from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Ecosystem = Literal["npm", "PyPI"]
DependencyType = Literal["direct", "dev", "optional", "unknown"]
ReleaseDecision = Literal["PASS", "WARN", "BLOCK"]
ReleaseConfidence = Literal["high", "medium", "low"]


class RepoRiskRadarError(Exception):
    """Base class for expected application errors."""


class ExternalServiceError(RepoRiskRadarError):
    """Raised when an external API returns an expected failure."""


class RepoIdentifier(BaseModel):
    owner: str
    name: str
    ref: str | None = None

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


class RepoMetadata(BaseModel):
    owner: str
    name: str
    full_name: str
    html_url: str
    default_branch: str
    description: str | None = None


class ManifestFile(BaseModel):
    path: str
    content: str


class Dependency(BaseModel):
    name: str
    ecosystem: Ecosystem
    source_file: str
    version_constraint: str | None = None
    resolved_version: str | None = None
    dependency_type: DependencyType = "unknown"

    @property
    def display_version(self) -> str:
        return self.resolved_version or self.version_constraint or "unknown"


class VulnerabilityReference(BaseModel):
    type: str | None = None
    url: str


class Vulnerability(BaseModel):
    id: str
    summary: str | None = None
    details: str | None = None
    aliases: list[str] = Field(default_factory=list)
    modified: str | None = None
    published: str | None = None
    database_specific: dict[str, Any] = Field(default_factory=dict)
    affected: list[dict[str, Any]] = Field(default_factory=list)
    references: list[VulnerabilityReference] = Field(default_factory=list)
    severity: list[dict[str, Any]] = Field(default_factory=list)
    fixed_versions: list[str] = Field(default_factory=list)

    @property
    def cve_aliases(self) -> list[str]:
        return [alias for alias in self.aliases if alias.upper().startswith("CVE-")]


class CveEnrichment(BaseModel):
    cve_id: str
    cvss_score: float | None = None
    severity: str | None = None
    epss_score: float | None = None
    epss_percentile: float | None = None
    epss_date: str | None = None
    cwe_ids: list[str] = Field(default_factory=list)
    cisa_known_exploited: bool = False
    cisa_due_date: str | None = None
    published: str | None = None
    last_modified: str | None = None
    references: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    dependency: Dependency
    vulnerability: Vulnerability
    cves: list[CveEnrichment] = Field(default_factory=list)
    risk_score: float
    risk_level: Literal["critical", "high", "medium", "low"]
    reasons: list[str] = Field(default_factory=list)
    fix_available: bool = False
    fixed_versions: list[str] = Field(default_factory=list)

    @property
    def highest_cvss(self) -> float | None:
        scores = [cve.cvss_score for cve in self.cves if cve.cvss_score is not None]
        return max(scores) if scores else None

    @property
    def highest_epss(self) -> float | None:
        scores = [cve.epss_score for cve in self.cves if cve.epss_score is not None]
        return max(scores) if scores else None

    @property
    def highest_severity(self) -> str | None:
        order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        severities = [cve.severity for cve in self.cves if cve.severity]
        osv_severity = self.vulnerability.database_specific.get("severity")
        if isinstance(osv_severity, str):
            severities.append(osv_severity)
        if not severities:
            return None
        return max(severities, key=lambda value: order.get(value.upper(), 0))


class ReportNarrative(BaseModel):
    executive_summary: str
    technical_summary: str
    remediation_plan: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    ai_generated: bool = False


class ReleaseGateTicket(BaseModel):
    title: str
    description: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class ReleaseGateExplanation(BaseModel):
    executive_summary: str
    technical_summary: str
    release_decision_explanation: str
    top_required_actions: list[str] = Field(default_factory=list)
    safe_fix_plan: list[str] = Field(default_factory=list)
    what_would_make_this_pass: list[str] = Field(default_factory=list)
    developer_ticket: ReleaseGateTicket
    questions_for_developer: list[str] = Field(default_factory=list)
    ai_generated: bool = False


class ReleaseGateResult(BaseModel):
    decision: ReleaseDecision
    confidence: ReleaseConfidence
    risk_score: float
    blocking_reasons: list[str] = Field(default_factory=list)
    warning_reasons: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    pass_conditions: list[str] = Field(default_factory=list)
    developer_ticket: ReleaseGateTicket
    explanation: ReleaseGateExplanation | None = None


class ScanStats(BaseModel):
    dependencies_with_resolved_versions: int = 0
    dependencies_without_resolved_versions: int = 0
    osv_queries: int = 0
    osv_vulnerabilities: int = 0
    cves_enriched: int = 0
    epss_enriched: int = 0


class ScanResult(BaseModel):
    repo: RepoMetadata
    scanned_ref: str
    manifests: list[str] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    stats: ScanStats = Field(default_factory=ScanStats)
    narrative: ReportNarrative | None = None
    release_gate: ReleaseGateResult | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
