from __future__ import annotations

from repo_risk_radar.models import Finding, ScanResult


def render_markdown_report(scan: ScanResult) -> str:
    lines = [
        f"# Repo Risk Radar: {scan.repo.full_name}",
        "",
        f"- Repository: [{scan.repo.html_url}]({scan.repo.html_url})",
        f"- Default branch: `{scan.repo.default_branch}`",
        f"- Scanned ref: `{scan.scanned_ref}`",
        f"- Generated: `{scan.generated_at.isoformat()}`",
        f"- Manifests found: `{len(scan.manifests)}`",
        f"- Dependencies extracted: `{len(scan.dependencies)}`",
        f"- Dependencies checked with OSV: `{scan.stats.osv_queries}`",
        f"- Dependencies skipped without exact versions: "
        f"`{scan.stats.dependencies_without_resolved_versions}`",
        f"- CVEs enriched with NVD: `{scan.stats.cves_enriched}`",
        f"- CVEs enriched with EPSS: `{scan.stats.epss_enriched}`",
        f"- Vulnerability findings: `{len(scan.findings)}`",
        "",
    ]

    if not scan.manifests:
        lines.extend(
            [
                "## No Dependency Manifests Found",
                "",
                "Repo Risk Radar did not find supported dependency manifests in this repository. "
                "The MVP currently supports `package.json`, `package-lock.json`, "
                "`requirements.txt`, and `pyproject.toml`.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(["## Manifests", ""])
    lines.extend(f"- `{path}`" for path in scan.manifests)
    lines.append("")

    narrative = scan.narrative
    if narrative:
        lines.extend(
            [
                "## Executive Summary",
                "",
                narrative.executive_summary,
                "",
                "## Technical Summary",
                "",
                narrative.technical_summary,
                "",
                "## Prioritized Remediation Plan",
                "",
            ]
        )
        if narrative.remediation_plan:
            lines.extend(
                f"{index}. {item}"
                for index, item in enumerate(narrative.remediation_plan, 1)
            )
        else:
            lines.append("No immediate remediation steps were identified.")
        lines.append("")
        if narrative.questions:
            lines.extend(["## Questions and Unknowns", ""])
            lines.extend(f"- {item}" for item in narrative.questions)
            lines.append("")

    gate = scan.release_gate
    if gate:
        lines.extend(
            [
                "## AI Release Gate",
                "",
                f"- Decision: `{gate.decision}`",
                f"- Confidence: `{gate.confidence}`",
                f"- Risk score: `{gate.risk_score:.1f}`",
                "",
            ]
        )
        reasons = gate.blocking_reasons or gate.warning_reasons
        if reasons:
            lines.extend(["### Why This Decision?", ""])
            lines.extend(f"- {reason}" for reason in reasons)
            lines.append("")
        if gate.required_actions:
            lines.extend(["### Required Before Release", ""])
            lines.extend(
                f"{index}. {action}" for index, action in enumerate(gate.required_actions, 1)
            )
            lines.append("")
        if gate.pass_conditions:
            lines.extend(["### What Would Make This Pass?", ""])
            lines.extend(f"- {condition}" for condition in gate.pass_conditions)
            lines.append("")
        if gate.unknowns:
            lines.extend(["### Release Gate Unknowns", ""])
            lines.extend(f"- {unknown}" for unknown in gate.unknowns)
            lines.append("")

    lines.extend(["## Findings", ""])
    if not scan.findings:
        lines.extend(
            [
                "No vulnerabilities were found for dependencies with exact resolved versions. "
                "Dependencies without lockfile or pinned versions may need a follow-up scan after "
                "install resolution.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "| Risk | Dependency | Source | Version | Vulnerability | Severity | CVSS | "
                "EPSS | KEV | Fixed Version |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for finding in scan.findings:
            lines.append(_finding_row(finding))
        lines.append("")
        lines.extend(["## Safe Remediation Commands", ""])
        commands = _safe_commands(scan.findings)
        if commands:
            lines.extend(f"- `{command}`" for command in commands)
        else:
            lines.append(
                "No fixed versions were available, so no package update commands were suggested."
            )
        lines.append("")
        lines.extend(["## Finding Details", ""])
        for finding in scan.findings:
            lines.append(f"### {finding.dependency.name} - {finding.vulnerability.id}")
            if finding.vulnerability.summary:
                lines.append("")
                lines.append(finding.vulnerability.summary)
                lines.append("")
            lines.extend(f"- {reason}" for reason in finding.reasons)
            references = _finding_references(finding)
            if references:
                lines.append("")
                lines.append("References:")
                lines.extend(f"- {url}" for url in references[:8])
            lines.append("")

    lines.extend(["## Safety Note", ""])
    lines.append(
        "This report is defensive and remediation-focused. It intentionally excludes exploit code, "
        "attack payloads, and offensive instructions."
    )
    lines.append("")
    return "\n".join(lines)


def _finding_row(finding: Finding) -> str:
    severity = finding.highest_severity or "unknown"
    cvss = f"{finding.highest_cvss:.1f}" if finding.highest_cvss is not None else "unknown"
    epss = f"{finding.highest_epss:.1%}" if finding.highest_epss is not None else "unknown"
    kev = "yes" if any(cve.cisa_known_exploited for cve in finding.cves) else "no"
    fixed = ", ".join(finding.fixed_versions) if finding.fixed_versions else "unknown"
    summary = finding.vulnerability.id
    return (
        f"| {finding.risk_level} ({finding.risk_score:.1f}) "
        f"| `{finding.dependency.name}` "
        f"| `{finding.dependency.source_file}` "
        f"| `{finding.dependency.display_version}` "
        f"| `{summary}` "
        f"| {severity} "
        f"| {cvss} "
        f"| {epss} "
        f"| {kev} "
        f"| `{fixed}` |"
    )


def _safe_commands(findings: list[Finding]) -> list[str]:
    commands: list[str] = []
    seen: set[str] = set()
    for finding in findings:
        if not finding.fixed_versions:
            continue
        version = finding.fixed_versions[-1]
        dependency = finding.dependency
        if dependency.ecosystem == "npm":
            command = f"npm install {dependency.name}@{version}"
        else:
            command = f"python -m pip install '{dependency.name}=={version}'"
        if command not in seen:
            seen.add(command)
            commands.append(command)
    return commands


def _finding_references(finding: Finding) -> list[str]:
    urls = [reference.url for reference in finding.vulnerability.references]
    for cve in finding.cves:
        urls.extend(cve.references)
    return list(dict.fromkeys(urls))
