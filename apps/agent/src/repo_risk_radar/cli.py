from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from repo_risk_radar.agent import (
    deterministic_narrative,
    generate_ai_narrative,
    generate_ai_release_gate,
)
from repo_risk_radar.analyzers.dependency_parser import extract_dependencies
from repo_risk_radar.analyzers.repo_detector import detect_manifest_paths, parse_github_url
from repo_risk_radar.analyzers.risk_ranker import rank_findings
from repo_risk_radar.config import load_settings
from repo_risk_radar.models import (
    Dependency,
    ExternalServiceError,
    RepoRiskRadarError,
    ScanResult,
    ScanStats,
)
from repo_risk_radar.release_policy import evaluate_release_gate
from repo_risk_radar.reporting.json_report import render_json_report
from repo_risk_radar.reporting.markdown_report import render_markdown_report
from repo_risk_radar.services.epss_client import EPSSClient, merge_epss
from repo_risk_radar.services.github_client import GitHubClient
from repo_risk_radar.services.nvd_client import NVDClient
from repo_risk_radar.services.osv_client import OSVClient

app = typer.Typer(no_args_is_help=True, help="Analyze GitHub repositories for dependency risk.")
console = Console()
error_console = Console(stderr=True)


@app.callback()
def main() -> None:
    """Analyze GitHub repositories for dependency risk."""


@app.command()
def analyze(
    repo_url: Annotated[str, typer.Argument(help="Public GitHub repository URL.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print the full JSON report to stdout."),
    ] = False,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write a Markdown or JSON report."),
    ] = None,
    no_ai: Annotated[
        bool,
        typer.Option("--no-ai", help="Disable OpenAI narrative generation."),
    ] = False,
    release_gate: Annotated[
        bool,
        typer.Option("--release-gate", help="Print detailed PASS/WARN/BLOCK release gate output."),
    ] = False,
    ticket: Annotated[
        bool,
        typer.Option("--ticket", help="Print the release gate developer ticket."),
    ] = False,
) -> None:
    """Analyze a public GitHub repository."""
    try:
        scan = asyncio.run(_analyze(repo_url=repo_url, no_ai=no_ai))
    except RepoRiskRadarError as exc:
        error_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from None
    except KeyboardInterrupt:
        error_console.print("[yellow]Scan cancelled.[/yellow]")
        raise typer.Exit(130) from None
    except Exception as exc:
        error_console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
        raise typer.Exit(1) from None

    if output:
        if output.suffix.lower() == ".json":
            report = render_json_report(scan)
        else:
            report = render_markdown_report(scan)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        destination_console = error_console if json_output else console
        destination_console.print(f"[green]Wrote report to[/green] {output}")

    if json_output:
        typer.echo(render_json_report(scan))
    else:
        _print_summary(scan, show_release_gate=release_gate, show_ticket=ticket)


@app.command("self-test")
def self_test() -> None:
    """Verify OSV/NVD/ranking with a known vulnerable package."""
    try:
        finding_count = asyncio.run(_self_test())
    except RepoRiskRadarError as exc:
        error_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from None

    if finding_count == 0:
        error_console.print("[bold red]Self-test failed:[/bold red] OSV returned no findings.")
        raise typer.Exit(1) from None


async def _analyze(repo_url: str, no_ai: bool) -> ScanResult:
    settings = load_settings()
    repo = parse_github_url(repo_url)
    scanned_ref = repo.ref

    async with GitHubClient(
        token=settings.github_token,
        timeout=settings.request_timeout_seconds,
    ) as github:
        metadata = await github.get_repo_metadata(repo)
        scanned_ref = scanned_ref or metadata.default_branch
        paths = await github.get_tree_paths(repo, scanned_ref)
        manifest_paths = detect_manifest_paths(paths)
        manifests = await github.get_manifests(repo, manifest_paths, scanned_ref)

    dependencies = extract_dependencies(manifests)
    resolved_dependency_count = sum(1 for dependency in dependencies if dependency.resolved_version)
    vulnerability_pairs = []
    if dependencies:
        async with OSVClient(timeout=settings.request_timeout_seconds) as osv:
            vulnerability_pairs = await osv.query_dependencies(dependencies)

    cve_ids = sorted(
        {
            cve_id
            for _dependency, vulnerability in vulnerability_pairs
            for cve_id in vulnerability.cve_aliases
        }
    )
    nvd_enrichments = {}
    cve_enrichments = {}
    epss_enrichments = {}
    if cve_ids:
        async with NVDClient(
            api_key=settings.nvd_api_key,
            timeout=settings.request_timeout_seconds,
        ) as nvd:
            nvd_enrichments = await nvd.enrich_many(cve_ids)
        async with EPSSClient(timeout=settings.request_timeout_seconds) as epss:
            epss_enrichments = await epss.enrich_many(cve_ids)
        cve_enrichments = merge_epss(nvd_enrichments, epss_enrichments)

    findings = rank_findings(vulnerability_pairs, cve_enrichments)
    scan = ScanResult(
        repo=metadata,
        scanned_ref=scanned_ref,
        manifests=manifest_paths,
        dependencies=dependencies,
        findings=findings,
        stats=ScanStats(
            dependencies_with_resolved_versions=resolved_dependency_count,
            dependencies_without_resolved_versions=len(dependencies) - resolved_dependency_count,
            osv_queries=resolved_dependency_count,
            osv_vulnerabilities=len(vulnerability_pairs),
            cves_enriched=len(nvd_enrichments),
            epss_enriched=len(epss_enrichments),
        ),
    )
    scan.release_gate = evaluate_release_gate(scan)

    if no_ai:
        scan.narrative = deterministic_narrative(scan)
        return scan

    try:
        scan.narrative = await generate_ai_narrative(scan, settings)
    except ExternalServiceError:
        raise
    except Exception:
        scan.narrative = None

    try:
        ai_release_gate = await generate_ai_release_gate(scan, settings)
        if ai_release_gate and scan.release_gate:
            scan.release_gate.explanation = ai_release_gate
            scan.release_gate.developer_ticket = ai_release_gate.developer_ticket
    except ExternalServiceError:
        raise
    except Exception:
        pass

    if scan.narrative is None:
        scan.narrative = deterministic_narrative(scan)
    return scan


async def _self_test() -> int:
    settings = load_settings()
    dependency = Dependency(
        name="minimist",
        ecosystem="npm",
        source_file="self-test",
        resolved_version="0.0.8",
        dependency_type="direct",
    )

    async with OSVClient(timeout=settings.request_timeout_seconds) as osv:
        vulnerability_pairs = await osv.query_dependencies([dependency])

    cve_ids = sorted(
        {
            cve_id
            for _dependency, vulnerability in vulnerability_pairs
            for cve_id in vulnerability.cve_aliases
        }
    )
    nvd_enrichments = {}
    cve_enrichments = {}
    epss_enrichments = {}
    if cve_ids:
        async with NVDClient(
            api_key=settings.nvd_api_key,
            timeout=settings.request_timeout_seconds,
        ) as nvd:
            nvd_enrichments = await nvd.enrich_many(cve_ids)
        async with EPSSClient(timeout=settings.request_timeout_seconds) as epss:
            epss_enrichments = await epss.enrich_many(cve_ids)
        cve_enrichments = merge_epss(nvd_enrichments, epss_enrichments)

    findings = rank_findings(vulnerability_pairs, cve_enrichments)
    console.print("[bold]Repo Risk Radar self-test[/bold]")
    console.print("Package: minimist@0.0.8")
    console.print(f"OSV findings: {len(vulnerability_pairs)}")
    console.print(f"NVD CVEs enriched: {len(nvd_enrichments)}")
    console.print(f"EPSS CVEs enriched: {len(epss_enrichments)}")
    if findings:
        top = findings[0]
        console.print(
            f"Top risk: {top.vulnerability.id} "
            f"({top.risk_level}, score {top.risk_score:.1f})"
        )
        console.print("[green]Self-test passed: OSV, NVD, and ranking are working.[/green]")
    return len(findings)


def _print_summary(
    scan: ScanResult,
    show_release_gate: bool = False,
    show_ticket: bool = False,
) -> None:
    console.print(f"[bold]Repo Risk Radar:[/bold] {scan.repo.full_name}")
    console.print(f"Scanned ref: {scan.scanned_ref}")
    console.print(f"Manifests: {len(scan.manifests)}")
    console.print(f"Dependencies: {len(scan.dependencies)}")
    console.print(
        "OSV checked: "
        f"{scan.stats.osv_queries}/{len(scan.dependencies)} dependencies with exact versions"
    )
    if scan.stats.dependencies_without_resolved_versions:
        console.print(
            "[yellow]Skipped without exact versions:[/yellow] "
            f"{scan.stats.dependencies_without_resolved_versions}"
        )
    console.print(f"Findings: {len(scan.findings)}")
    if scan.release_gate:
        console.print(
            f"Release gate: [bold]{scan.release_gate.decision}[/bold] "
            f"(risk {scan.release_gate.risk_score:.1f}, confidence {scan.release_gate.confidence})"
        )
        if show_release_gate:
            _print_release_gate(scan)
        if show_ticket:
            _print_release_gate_ticket(scan)

    if not scan.manifests:
        console.print(
            "[yellow]No supported dependency manifests were found. Supported files are "
            "package.json, package-lock.json, requirements.txt, and pyproject.toml.[/yellow]"
        )
        return

    if scan.narrative:
        source = "AI" if scan.narrative.ai_generated else "deterministic"
        console.print(f"\n[bold]Executive summary ({source}):[/bold]")
        console.print(scan.narrative.executive_summary)

    if not scan.findings:
        if scan.stats.osv_queries == 0 and scan.dependencies:
            console.print(
                "\n[yellow]No dependencies had exact resolved versions, so OSV version matching "
                "could not be performed. Commit lockfiles or pin versions for a stronger "
                "scan.[/yellow]"
            )
            return
        console.print(
            "\n[green]No vulnerabilities were found for dependencies with exact "
            "resolved versions.[/green]"
        )
        return

    table = Table(title="Top risks")
    table.add_column("Package")
    table.add_column("Vulnerability")
    table.add_column("Severity")
    table.add_column("Score", justify="right")
    table.add_column("Fix")

    for finding in scan.findings[:10]:
        severity = finding.highest_severity or "unknown"
        fix = ", ".join(finding.fixed_versions) if finding.fixed_versions else "unknown"
        table.add_row(
            finding.dependency.name,
            finding.vulnerability.id,
            severity,
            f"{finding.risk_score:.1f}",
            fix,
        )
    console.print(table)


def _print_release_gate(scan: ScanResult) -> None:
    gate = scan.release_gate
    if not gate:
        return
    console.print("\n[bold]Release Gate[/bold]")
    console.print(f"RELEASE DECISION: [bold]{gate.decision}[/bold]")
    console.print(f"Risk score: {gate.risk_score:.1f}")
    console.print(f"Confidence: {gate.confidence}")

    reasons = gate.blocking_reasons or gate.warning_reasons
    if reasons:
        console.print("\nReason:")
        for reason in reasons:
            console.print(f"- {reason}")

    if gate.required_actions:
        console.print("\nRequired before release:")
        for index, action in enumerate(gate.required_actions, 1):
            console.print(f"{index}. {action}")

    if gate.unknowns:
        console.print("\nUnknowns:")
        for unknown in gate.unknowns:
            console.print(f"- {unknown}")


def _print_release_gate_ticket(scan: ScanResult) -> None:
    gate = scan.release_gate
    if not gate:
        return
    ticket = gate.developer_ticket
    console.print("\n[bold]Developer Ticket[/bold]")
    console.print(f"Title: {ticket.title}")
    console.print("\nBody:")
    console.print(ticket.description)
    if ticket.acceptance_criteria:
        console.print("\nAcceptance criteria:")
        for item in ticket.acceptance_criteria:
            console.print(f"- {item}")
    if ticket.evidence:
        console.print("\nEvidence:")
        for item in ticket.evidence:
            console.print(f"- {item}")
