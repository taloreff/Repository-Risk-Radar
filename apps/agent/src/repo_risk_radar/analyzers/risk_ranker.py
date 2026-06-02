from __future__ import annotations

from repo_risk_radar.models import CveEnrichment, Dependency, Finding, Vulnerability

_SEVERITY_POINTS = {
    "CRITICAL": 40.0,
    "HIGH": 30.0,
    "MEDIUM": 18.0,
    "LOW": 8.0,
}

VulnerabilityPairs = list[tuple[Dependency, Vulnerability]]
VulnerabilityInput = dict[Dependency, list[Vulnerability]] | VulnerabilityPairs


def rank_findings(
    vulnerability_map: VulnerabilityInput,
    cve_enrichments: dict[str, CveEnrichment] | None = None,
) -> list[Finding]:
    cve_enrichments = cve_enrichments or {}
    pairs = _iter_pairs(vulnerability_map)
    findings = [
        _score_finding(dependency, vulnerability, cve_enrichments)
        for dependency, vulnerability in pairs
    ]
    return sorted(findings, key=lambda finding: finding.risk_score, reverse=True)


def _iter_pairs(vulnerability_map: VulnerabilityInput) -> VulnerabilityPairs:
    if isinstance(vulnerability_map, list):
        return vulnerability_map
    pairs: list[tuple[Dependency, Vulnerability]] = []
    for dependency, vulnerabilities in vulnerability_map.items():
        for vulnerability in vulnerabilities:
            pairs.append((dependency, vulnerability))
    return pairs


def _score_finding(
    dependency: Dependency,
    vulnerability: Vulnerability,
    cve_enrichments: dict[str, CveEnrichment],
) -> Finding:
    cves = [
        cve_enrichments[cve_id]
        for cve_id in vulnerability.cve_aliases
        if cve_id in cve_enrichments
    ]
    fixed_versions = vulnerability.fixed_versions or _extract_fixed_versions(vulnerability)
    fix_available = bool(fixed_versions)

    score = 10.0
    reasons = ["Base score for a dependency vulnerability."]

    severity = _highest_severity(cves) or _osv_severity(vulnerability)
    if severity:
        points = _SEVERITY_POINTS.get(severity.upper(), 0.0)
        score += points
        reasons.append(f"{severity.upper()} severity adds {points:.0f} points.")

    cvss = _highest_cvss(cves)
    if cvss is not None:
        points = min(40.0, cvss * 4.0)
        score += points
        reasons.append(f"CVSS {cvss:.1f} adds {points:.1f} points.")

    if any(cve.cisa_known_exploited for cve in cves):
        score += 35.0
        reasons.append("CISA KEV known-exploited status adds 35 points.")

    epss = _highest_epss(cves)
    if epss is not None:
        if epss >= 0.5:
            points = 20.0
        elif epss >= 0.1:
            points = 10.0
        elif epss >= 0.01:
            points = 5.0
        else:
            points = 0.0
        if points:
            score += points
            reasons.append(f"EPSS {epss:.3f} adds {points:.0f} exploit-likelihood points.")
        else:
            reasons.append(f"EPSS {epss:.3f} indicates low observed exploitation likelihood.")

    if dependency.dependency_type == "direct":
        score += 10.0
        reasons.append("Direct dependency adds 10 points.")
    elif dependency.dependency_type == "dev":
        score += 4.0
        reasons.append("Development dependency adds 4 points.")
    else:
        reasons.append("Dependency relationship is unknown, so no directness boost was applied.")

    if fix_available:
        reasons.append("A fixed version is known, lowering remediation uncertainty.")
    else:
        score += 5.0
        reasons.append("No fixed version was found, adding 5 uncertainty points.")

    score = min(round(score, 1), 100.0)
    return Finding(
        dependency=dependency,
        vulnerability=vulnerability.model_copy(update={"fixed_versions": fixed_versions}),
        cves=cves,
        risk_score=score,
        risk_level=_risk_level(score),
        reasons=reasons,
        fix_available=fix_available,
        fixed_versions=fixed_versions,
    )


def _highest_cvss(cves: list[CveEnrichment]) -> float | None:
    scores = [cve.cvss_score for cve in cves if cve.cvss_score is not None]
    return max(scores) if scores else None


def _highest_epss(cves: list[CveEnrichment]) -> float | None:
    scores = [cve.epss_score for cve in cves if cve.epss_score is not None]
    return max(scores) if scores else None


def _highest_severity(cves: list[CveEnrichment]) -> str | None:
    severities = [cve.severity for cve in cves if cve.severity]
    if not severities:
        return None
    return max(severities, key=lambda value: _SEVERITY_POINTS.get(value.upper(), 0.0))


def _osv_severity(vulnerability: Vulnerability) -> str | None:
    severity = vulnerability.database_specific.get("severity")
    if isinstance(severity, str) and severity.upper() in _SEVERITY_POINTS:
        return severity
    return None


def _risk_level(score: float) -> str:
    if score >= 85:
        return "critical"
    if score >= 65:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _extract_fixed_versions(vulnerability: Vulnerability) -> list[str]:
    fixed_versions: set[str] = set()
    for affected in vulnerability.affected:
        ranges = affected.get("ranges", []) if isinstance(affected, dict) else []
        for range_data in ranges:
            events = range_data.get("events", []) if isinstance(range_data, dict) else []
            for event in events:
                if isinstance(event, dict) and event.get("fixed"):
                    fixed_versions.add(str(event["fixed"]))
    return sorted(fixed_versions)
