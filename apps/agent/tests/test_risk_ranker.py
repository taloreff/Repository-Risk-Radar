from repo_risk_radar.analyzers.risk_ranker import rank_findings
from repo_risk_radar.models import CveEnrichment, Dependency, Vulnerability


def test_rank_findings_prioritizes_high_cvss_kev_direct_dependency() -> None:
    dependency = Dependency(
        name="danger-lib",
        ecosystem="npm",
        source_file="package-lock.json",
        resolved_version="1.0.0",
        dependency_type="direct",
    )
    vulnerability = Vulnerability(
        id="GHSA-1234",
        aliases=["CVE-2024-0001"],
        affected=[{"ranges": [{"events": [{"introduced": "0"}, {"fixed": "1.0.1"}]}]}],
    )
    cve = CveEnrichment(
        cve_id="CVE-2024-0001",
        cvss_score=9.8,
        severity="CRITICAL",
        cisa_known_exploited=True,
    )

    findings = rank_findings([(dependency, vulnerability)], {"CVE-2024-0001": cve})

    assert len(findings) == 1
    assert findings[0].risk_level == "critical"
    assert findings[0].risk_score == 100.0
    assert findings[0].fix_available is True
    assert "1.0.1" in findings[0].fixed_versions


def test_rank_findings_adds_uncertainty_when_no_fix_is_known() -> None:
    dependency = Dependency(
        name="maybe-risky",
        ecosystem="PyPI",
        source_file="requirements.txt",
        resolved_version="2.0.0",
        dependency_type="unknown",
    )
    vulnerability = Vulnerability(id="PYSEC-1", aliases=["CVE-2024-0002"])
    cve = CveEnrichment(cve_id="CVE-2024-0002", cvss_score=5.0, severity="MEDIUM")

    findings = rank_findings([(dependency, vulnerability)], {"CVE-2024-0002": cve})

    assert findings[0].risk_level == "medium"
    assert findings[0].fix_available is False
    assert any("uncertainty" in reason for reason in findings[0].reasons)


def test_rank_findings_uses_epss_signal() -> None:
    dependency = Dependency(
        name="active-risk",
        ecosystem="npm",
        source_file="package-lock.json",
        resolved_version="1.0.0",
        dependency_type="direct",
    )
    vulnerability = Vulnerability(id="GHSA-2", aliases=["CVE-2024-0003"])
    cve = CveEnrichment(
        cve_id="CVE-2024-0003",
        cvss_score=6.0,
        severity="MEDIUM",
        epss_score=0.62,
        epss_percentile=0.99,
    )

    findings = rank_findings([(dependency, vulnerability)], {"CVE-2024-0003": cve})

    assert findings[0].highest_epss == 0.62
    assert any("EPSS" in reason for reason in findings[0].reasons)
