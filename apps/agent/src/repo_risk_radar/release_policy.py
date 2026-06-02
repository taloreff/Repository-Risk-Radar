from __future__ import annotations

from repo_risk_radar.models import (
    Finding,
    ReleaseGateExplanation,
    ReleaseGateResult,
    ReleaseGateTicket,
    ScanResult,
)


def evaluate_release_gate(scan: ScanResult) -> ReleaseGateResult:
    """Evaluate whether the scanned repository is ready for release."""
    risk_score = _overall_risk_score(scan.findings)
    blocking_reasons: list[str] = []
    warning_reasons: list[str] = []
    evidence: list[str] = []
    unknowns: list[str] = []

    kev_findings = [finding for finding in scan.findings if _has_kev(finding)]
    if kev_findings:
        blocking_reasons.append("Known exploited vulnerability found in dependency findings.")
        evidence.extend(_finding_evidence(finding) for finding in kev_findings[:3])

    direct_critical_with_fix = [
        finding
        for finding in scan.findings
        if _is_direct(finding) and _is_critical(finding) and finding.fix_available
    ]
    if direct_critical_with_fix:
        blocking_reasons.append("Critical direct dependency has a known fixed version.")
        evidence.extend(_finding_evidence(finding) for finding in direct_critical_with_fix[:3])

    direct_cvss_nines = [
        finding
        for finding in scan.findings
        if _is_direct(finding)
        and finding.highest_cvss is not None
        and finding.highest_cvss >= 9.0
    ]
    if direct_cvss_nines:
        blocking_reasons.append("Direct dependency has CVSS >= 9.0.")
        evidence.extend(_finding_evidence(finding) for finding in direct_cvss_nines[:3])

    if risk_score >= 85:
        blocking_reasons.append(
            f"Overall risk score is {risk_score:.1f}, meeting the BLOCK threshold."
        )

    critical_findings = [finding for finding in scan.findings if _is_critical(finding)]
    if len(critical_findings) > 2:
        blocking_reasons.append(
            f"{len(critical_findings)} critical findings exceed the release policy limit."
        )
        evidence.extend(_finding_evidence(finding) for finding in critical_findings[:3])

    high_findings = [finding for finding in scan.findings if _is_high(finding)]
    if high_findings:
        warning_reasons.append("High severity finding exists.")
        evidence.extend(_finding_evidence(finding) for finding in high_findings[:3])

    critical_without_fix = [
        finding for finding in critical_findings if not finding.fix_available
    ]
    if critical_without_fix:
        warning_reasons.append("Critical finding exists without a known fixed version.")
        evidence.extend(_finding_evidence(finding) for finding in critical_without_fix[:3])

    if 50 <= risk_score < 85:
        warning_reasons.append(f"Overall risk score is {risk_score:.1f}, which is in WARN range.")

    runtime_medium_findings = [
        finding
        for finding in scan.findings
        if finding.risk_level == "medium"
        and finding.dependency.dependency_type in {"direct", "unknown"}
    ]
    if len(runtime_medium_findings) > 1:
        warning_reasons.append(
            "Multiple medium findings affect runtime or unresolved dependency relationships."
        )
        evidence.extend(_finding_evidence(finding) for finding in runtime_medium_findings[:3])

    important_with_incomplete_enrichment = [
        finding
        for finding in scan.findings
        if _is_important(finding) and _enrichment_incomplete(finding)
    ]
    if important_with_incomplete_enrichment:
        warning_reasons.append("NVD/OSV enrichment is incomplete for important findings.")
        unknowns.extend(
            (
                f"{finding.dependency.name} {finding.vulnerability.id} is missing "
                "CVE, CVSS, or severity enrichment."
            )
            for finding in important_with_incomplete_enrichment[:5]
        )

    if scan.stats.dependencies_without_resolved_versions:
        unknowns.append(
            f"{scan.stats.dependencies_without_resolved_versions} dependencies were "
            "skipped because exact versions were unavailable."
        )

    if blocking_reasons:
        decision = "BLOCK"
    elif warning_reasons:
        decision = "WARN"
    else:
        decision = "PASS"

    required_actions = _required_actions(scan.findings, decision)
    pass_conditions = _pass_conditions(scan, decision, required_actions, unknowns)
    confidence = _confidence(decision, unknowns, scan)
    evidence = list(dict.fromkeys(evidence)) or _pass_evidence(scan)

    ticket = _developer_ticket(
        scan=scan,
        decision=decision,
        risk_score=risk_score,
        reasons=blocking_reasons or warning_reasons,
        required_actions=required_actions,
        evidence=evidence,
    )

    gate = ReleaseGateResult(
        decision=decision,
        confidence=confidence,
        risk_score=risk_score,
        blocking_reasons=list(dict.fromkeys(blocking_reasons)),
        warning_reasons=list(dict.fromkeys(warning_reasons)),
        required_actions=required_actions,
        evidence=evidence,
        unknowns=list(dict.fromkeys(unknowns)),
        pass_conditions=pass_conditions,
        developer_ticket=ticket,
    )
    gate.explanation = deterministic_release_gate_explanation(scan, gate)
    return gate


def deterministic_release_gate_explanation(
    scan: ScanResult,
    gate: ReleaseGateResult,
) -> ReleaseGateExplanation:
    reasons = gate.blocking_reasons or gate.warning_reasons
    if gate.decision == "PASS":
        executive = (
            f"{scan.repo.full_name} passes the dependency release gate. No critical, high, "
            "or known exploited dependency findings were detected in the scanned exact versions."
        )
        decision_text = (
            "The deterministic policy returned PASS because no blocking or warning "
            "thresholds fired."
        )
    elif gate.decision == "WARN":
        executive = (
            f"{scan.repo.full_name} can continue with caution, but release owners should review "
            "the dependency warnings before production."
        )
        decision_text = (
            "The deterministic policy returned WARN because at least one caution "
            "threshold fired."
        )
    else:
        executive = (
            f"{scan.repo.full_name} should not be released to production until dependency security "
            "blocking items are remediated."
        )
        decision_text = (
            "The deterministic policy returned BLOCK because at least one blocking "
            "threshold fired."
        )

    technical = (
        f"Release gate evaluated {len(scan.findings)} finding(s), "
        f"{len(scan.dependencies)} dependencies, and {len(scan.manifests)} manifest(s). "
        f"The computed release risk score is {gate.risk_score:.1f}."
    )
    if reasons:
        technical = f"{technical} Primary policy signals: {'; '.join(reasons[:4])}"

    return ReleaseGateExplanation(
        executive_summary=executive,
        technical_summary=technical,
        release_decision_explanation=decision_text,
        top_required_actions=gate.required_actions,
        safe_fix_plan=gate.required_actions,
        what_would_make_this_pass=gate.pass_conditions,
        developer_ticket=gate.developer_ticket,
        questions_for_developer=gate.unknowns,
        ai_generated=False,
    )


def _overall_risk_score(findings: list[Finding]) -> float:
    return round(max((finding.risk_score for finding in findings), default=0.0), 1)


def _has_kev(finding: Finding) -> bool:
    return any(cve.cisa_known_exploited for cve in finding.cves)


def _is_direct(finding: Finding) -> bool:
    return finding.dependency.dependency_type == "direct"


def _is_critical(finding: Finding) -> bool:
    return (
        finding.risk_level == "critical"
        or (finding.highest_severity or "").upper() == "CRITICAL"
    )


def _is_high(finding: Finding) -> bool:
    return finding.risk_level == "high" or (finding.highest_severity or "").upper() == "HIGH"


def _is_important(finding: Finding) -> bool:
    return _is_critical(finding) or _is_high(finding) or finding.risk_score >= 65


def _enrichment_incomplete(finding: Finding) -> bool:
    if not finding.vulnerability.cve_aliases:
        return True
    if not finding.cves:
        return True
    return any(cve.cvss_score is None or cve.severity is None for cve in finding.cves)


def _required_actions(findings: list[Finding], decision: str) -> list[str]:
    if decision == "PASS":
        return ["Keep lockfiles committed and re-scan before production release."]

    actions: list[str] = []
    for finding in findings[:8]:
        dependency = finding.dependency
        if finding.fixed_versions:
            version = finding.fixed_versions[-1]
            actions.append(
                f"Upgrade {dependency.name} from {dependency.display_version} to at "
                f"least {version}, regenerate lockfiles, and run tests."
            )
        else:
            actions.append(
                f"Review or replace {dependency.name}; {finding.vulnerability.id} "
                "has no fixed version in OSV data."
            )
    actions.append("Re-run Repo Risk Radar and verify the release gate no longer returns BLOCK.")
    return list(dict.fromkeys(actions))


def _pass_conditions(
    scan: ScanResult,
    decision: str,
    required_actions: list[str],
    unknowns: list[str],
) -> list[str]:
    if decision == "PASS":
        conditions = [
            (
                "Continue to keep exact dependency versions available through lockfiles "
                "or pinned requirements."
            ),
            "Re-scan when dependency manifests or lockfiles change.",
        ]
    else:
        conditions = [
            "No known exploited dependency findings remain.",
            "No direct dependency has critical severity with a known fix still unapplied.",
            "No direct dependency finding has CVSS >= 9.0.",
            "Overall release gate risk score is below 50.",
        ]
        conditions.extend(required_actions[:5])
    if unknowns and scan.stats.dependencies_without_resolved_versions:
        conditions.append("Resolve unpinned dependencies so OSV can match exact deployed versions.")
    return list(dict.fromkeys(conditions))


def _confidence(decision: str, unknowns: list[str], scan: ScanResult) -> str:
    if not scan.manifests or scan.stats.osv_queries == 0:
        return "low"
    if unknowns:
        return "medium" if decision != "PASS" else "low"
    return "high"


def _finding_evidence(finding: Finding) -> str:
    cves = ", ".join(cve.cve_id for cve in finding.cves) or "no CVE alias enriched"
    fix = ", ".join(finding.fixed_versions) if finding.fixed_versions else "no fixed version"
    cvss = f"{finding.highest_cvss:.1f}" if finding.highest_cvss is not None else "unknown"
    return (
        f"{finding.dependency.name}@{finding.dependency.display_version} "
        f"({finding.dependency.dependency_type}) -> {finding.vulnerability.id}; "
        f"CVEs: {cves}; CVSS: {cvss}; fix: {fix}; risk: {finding.risk_score:.1f}"
    )


def _pass_evidence(scan: ScanResult) -> list[str]:
    if scan.findings:
        return [
            f"{len(scan.findings)} finding(s) remained below BLOCK/WARN policy thresholds."
        ]
    return [
        "No vulnerabilities were found for dependencies with exact resolved versions.",
        f"OSV checked {scan.stats.osv_queries}/{len(scan.dependencies)} dependencies.",
    ]


def _developer_ticket(
    scan: ScanResult,
    decision: str,
    risk_score: float,
    reasons: list[str],
    required_actions: list[str],
    evidence: list[str],
) -> ReleaseGateTicket:
    summary = (
        f"Repo Risk Radar release gate returned {decision} for {scan.repo.full_name} "
        f"with risk score {risk_score:.1f}."
    )
    if reasons:
        summary = f"{summary}\n\nPolicy reasons:\n" + "\n".join(f"- {reason}" for reason in reasons)

    affected_packages = list(dict.fromkeys(finding.dependency.name for finding in scan.findings))
    cves = list(
        dict.fromkeys(
            cve.cve_id for finding in scan.findings for cve in finding.cves
        )
    )
    body = "\n".join(
        [
            summary,
            "",
            "Affected packages:",
            "\n".join(f"- {package}" for package in affected_packages) or "- None",
            "",
            "CVEs:",
            "\n".join(f"- {cve}" for cve in cves) or "- None",
            "",
            "Required actions:",
            "\n".join(f"- {action}" for action in required_actions) or "- None",
        ]
    )
    acceptance = [
        (
            "Vulnerable direct dependencies are upgraded to non-vulnerable versions "
            "where fixes are available."
        ),
        "Lockfiles are regenerated and committed.",
        "Project tests pass.",
        f"Repo Risk Radar re-scan no longer returns {decision} for unresolved dependency risk.",
        "Any remaining risk is documented and accepted by the release owner.",
    ]
    return ReleaseGateTicket(
        title=f"[{decision}] Dependency security release gate for {scan.repo.full_name}",
        description=body,
        acceptance_criteria=acceptance,
        evidence=evidence,
    )
