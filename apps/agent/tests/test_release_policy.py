from repo_risk_radar.models import (
    CveEnrichment,
    Dependency,
    Finding,
    RepoMetadata,
    ScanResult,
    ScanStats,
    Vulnerability,
)
from repo_risk_radar.release_policy import evaluate_release_gate


def test_release_gate_passes_when_no_high_critical_or_kev_findings() -> None:
    scan = _scan(findings=[])

    gate = evaluate_release_gate(scan)

    assert gate.decision == "PASS"
    assert gate.risk_score == 0.0
    assert gate.blocking_reasons == []
    assert gate.developer_ticket.title.startswith("[PASS]")


def test_release_gate_warns_when_high_severity_exists_without_blocking_condition() -> None:
    finding = _finding(
        risk_score=70.0,
        risk_level="high",
        dependency_type="dev",
        cvss_score=7.5,
        severity="HIGH",
    )

    gate = evaluate_release_gate(_scan(findings=[finding]))

    assert gate.decision == "WARN"
    assert any("High severity" in reason for reason in gate.warning_reasons)
    assert gate.blocking_reasons == []


def test_release_gate_blocks_when_kev_exists() -> None:
    finding = _finding(
        risk_score=70.0,
        risk_level="high",
        dependency_type="dev",
        cvss_score=7.5,
        severity="HIGH",
        cisa_known_exploited=True,
    )

    gate = evaluate_release_gate(_scan(findings=[finding]))

    assert gate.decision == "BLOCK"
    assert any("Known exploited" in reason for reason in gate.blocking_reasons)


def test_release_gate_blocks_when_critical_direct_dependency_has_fix() -> None:
    finding = _finding(
        risk_score=80.0,
        risk_level="critical",
        dependency_type="direct",
        cvss_score=8.8,
        severity="CRITICAL",
        fixed_versions=["2.0.0"],
    )

    gate = evaluate_release_gate(_scan(findings=[finding]))

    assert gate.decision == "BLOCK"
    assert any("Critical direct dependency" in reason for reason in gate.blocking_reasons)


def test_release_gate_blocks_when_risk_score_crosses_threshold() -> None:
    finding = _finding(
        risk_score=86.0,
        risk_level="medium",
        dependency_type="dev",
        cvss_score=5.0,
        severity="MEDIUM",
    )

    gate = evaluate_release_gate(_scan(findings=[finding]))

    assert gate.decision == "BLOCK"
    assert any("Overall risk score" in reason for reason in gate.blocking_reasons)


def test_release_gate_warns_when_enrichment_is_incomplete() -> None:
    finding = _finding(
        risk_score=70.0,
        risk_level="high",
        dependency_type="dev",
        cvss_score=None,
        severity=None,
        include_cve=False,
    )

    gate = evaluate_release_gate(_scan(findings=[finding]))

    assert gate.decision == "WARN"
    assert any("enrichment is incomplete" in reason for reason in gate.warning_reasons)
    assert gate.unknowns


def test_release_gate_deterministic_ticket_fallback_without_openai() -> None:
    finding = _finding(
        risk_score=99.0,
        risk_level="critical",
        dependency_type="direct",
        cvss_score=9.8,
        severity="CRITICAL",
        fixed_versions=["2.0.0"],
    )

    gate = evaluate_release_gate(_scan(findings=[finding]))

    assert gate.developer_ticket.title == "[BLOCK] Dependency security release gate for owner/repo"
    assert "Required actions" in gate.developer_ticket.description
    assert gate.explanation is not None
    assert gate.explanation.ai_generated is False


def _scan(findings: list[Finding]) -> ScanResult:
    return ScanResult(
        repo=RepoMetadata(
            owner="owner",
            name="repo",
            full_name="owner/repo",
            html_url="https://github.com/owner/repo",
            default_branch="main",
        ),
        scanned_ref="main",
        manifests=["package.json"],
        dependencies=[finding.dependency for finding in findings],
        findings=findings,
        stats=ScanStats(
            dependencies_with_resolved_versions=len(findings),
            osv_queries=len(findings),
            osv_vulnerabilities=len(findings),
            cves_enriched=sum(1 for finding in findings if finding.cves),
            epss_enriched=0,
        ),
    )


def _finding(
    risk_score: float,
    risk_level: str,
    dependency_type: str,
    cvss_score: float | None,
    severity: str | None,
    fixed_versions: list[str] | None = None,
    cisa_known_exploited: bool = False,
    include_cve: bool = True,
) -> Finding:
    fixed_versions = fixed_versions or []
    dependency = Dependency(
        name="pkg",
        ecosystem="npm",
        source_file="package-lock.json",
        resolved_version="1.0.0",
        dependency_type=dependency_type,  # type: ignore[arg-type]
    )
    vulnerability = Vulnerability(
        id="GHSA-test",
        summary="test advisory",
        aliases=["CVE-2025-0001"],
        fixed_versions=fixed_versions,
    )
    cves = []
    if include_cve:
        cves.append(
            CveEnrichment(
                cve_id="CVE-2025-0001",
                cvss_score=cvss_score,
                severity=severity,
                cisa_known_exploited=cisa_known_exploited,
            )
        )
    return Finding(
        dependency=dependency,
        vulnerability=vulnerability,
        cves=cves,
        risk_score=risk_score,
        risk_level=risk_level,  # type: ignore[arg-type]
        reasons=["test"],
        fix_available=bool(fixed_versions),
        fixed_versions=fixed_versions,
    )
