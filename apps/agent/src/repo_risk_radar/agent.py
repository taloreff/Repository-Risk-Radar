from __future__ import annotations

import json
import os
from typing import Any

from repo_risk_radar.config import Settings
from repo_risk_radar.models import (
    ReleaseGateExplanation,
    ReleaseGateTicket,
    ReportNarrative,
    ScanResult,
)

AGENT_INSTRUCTIONS = """You generate defensive dependency security reports.

Use only the structured scan data provided by the application. Do not invent vulnerabilities,
exploitability, affected versions, or fixes. Do not provide exploit code, attack payloads,
or offensive instructions.

Return a compact JSON object with these keys:
- executive_summary: string
- technical_summary: string
- remediation_plan: array of strings
- questions: array of strings

Suggest safe developer commands only when the scan data includes a fixed version.
"""

RELEASE_GATE_INSTRUCTIONS = """You explain a defensive dependency security release gate.

The release decision is deterministic and already computed by the application. Do not override it.
Use only the structured scan data and policy result provided. Do not invent vulnerabilities, CVEs,
versions, affected packages, exploitability, or fixes. Do not provide exploit code, attack payloads,
or offensive instructions.

Only suggest exact upgrade commands when fixed version data exists. If data is missing, say what is
unknown. Keep the response remediation-focused and developer-friendly.

Return a compact JSON object with these keys:
- executive_summary: string
- technical_summary: string
- release_decision_explanation: string
- top_required_actions: array of strings
- safe_fix_plan: array of strings
- what_would_make_this_pass: array of strings
- developer_ticket: object with title, description, acceptance_criteria, evidence
- questions_for_developer: array of strings
"""


async def generate_ai_narrative(scan: ScanResult, settings: Settings) -> ReportNarrative | None:
    if not settings.openai_api_key:
        return None

    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    try:
        from agents import Agent, Runner
    except ImportError:
        return None

    agent = Agent(
        name="Repo Risk Radar Report Agent",
        instructions=AGENT_INSTRUCTIONS,
        model=settings.openai_model,
    )
    prompt = json.dumps(_scan_payload(scan), indent=2, sort_keys=True)
    result = await Runner.run(agent, prompt)
    return _parse_agent_output(str(result.final_output))


async def generate_ai_release_gate(
    scan: ScanResult,
    settings: Settings,
) -> ReleaseGateExplanation | None:
    if not settings.openai_api_key or not scan.release_gate or not scan.findings:
        return None

    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    try:
        from agents import Agent, Runner
    except ImportError:
        return None

    agent = Agent(
        name="Repo Risk Radar Release Gate Agent",
        instructions=RELEASE_GATE_INSTRUCTIONS,
        model=settings.openai_model,
    )
    prompt = json.dumps(_release_gate_payload(scan), indent=2, sort_keys=True)
    result = await Runner.run(agent, prompt)
    return _parse_release_gate_output(str(result.final_output), scan.release_gate.developer_ticket)


def deterministic_narrative(scan: ScanResult) -> ReportNarrative:
    if not scan.manifests:
        return ReportNarrative(
            executive_summary="No supported dependency manifests were found in the repository.",
            technical_summary=(
                "The scan fetched repository metadata and the file tree, but none of the MVP "
                "manifest types were present."
            ),
            remediation_plan=[
                "Confirm whether the project uses another dependency system.",
                "Add support for the missing manifest type before relying on this scan.",
            ],
            questions=[
                "Does this repository keep dependency manifests in a generated or private path?"
            ],
            ai_generated=False,
        )

    if not scan.findings:
        return ReportNarrative(
            executive_summary=(
                "No known vulnerabilities were found for dependencies with exact resolved versions."
            ),
            technical_summary=(
                f"The scan parsed {len(scan.dependencies)} dependencies from {len(scan.manifests)} "
                f"manifest file(s). OSV matching was performed for "
                f"{scan.stats.osv_queries} dependencies with resolved versions."
            ),
            remediation_plan=[
                "Keep lockfiles committed so future scans can match exact versions.",
                "Run dependency updates and tests regularly.",
            ],
            questions=[
                "Were all production dependency groups represented in the scanned manifests?",
                "Do unpinned constraints resolve to different versions in deployment?",
            ],
            ai_generated=False,
        )

    top = scan.findings[0]
    return ReportNarrative(
        executive_summary=(
            f"Repo Risk Radar found {len(scan.findings)} vulnerability finding(s). The highest "
            f"priority is {top.dependency.name} with risk score {top.risk_score:.1f}."
        ),
        technical_summary=(
            f"The scan parsed {len(scan.dependencies)} dependencies from {len(scan.manifests)} "
            f"manifest file(s), matched {scan.stats.osv_queries} exact versions through OSV.dev, "
            "enriched CVEs with "
            "NVD where available, and ranked findings with severity, CVSS, CISA KEV, "
            "directness, and fix data."
        ),
        remediation_plan=_deterministic_plan(scan),
        questions=[
            "Are dev dependencies deployed or bundled into production artifacts?",
            "Do package manager lockfiles reflect the currently deployed versions?",
        ],
        ai_generated=False,
    )


def _deterministic_plan(scan: ScanResult) -> list[str]:
    plan: list[str] = []
    for finding in scan.findings[:5]:
        dependency = finding.dependency
        if finding.fixed_versions:
            version = finding.fixed_versions[-1]
            if dependency.ecosystem == "npm":
                plan.append(
                    f"Update {dependency.name} to {version} with `npm install "
                    f"{dependency.name}@{version}`, then run the project's test suite."
                )
            else:
                plan.append(
                    f"Update {dependency.name} to {version} with `python -m pip install "
                    f"'{dependency.name}=={version}'`, then run the project's test suite."
                )
        else:
            plan.append(
                f"Review {dependency.name} for {finding.vulnerability.id}; no fixed version was "
                "available in OSV data."
            )
    return plan


def _scan_payload(scan: ScanResult) -> dict[str, Any]:
    return {
        "repo": scan.repo.model_dump(mode="json"),
        "manifests": scan.manifests,
        "dependency_count": len(scan.dependencies),
        "stats": scan.stats.model_dump(mode="json"),
        "findings": [
            {
                "dependency": finding.dependency.model_dump(mode="json"),
                "vulnerability": {
                    "id": finding.vulnerability.id,
                    "summary": finding.vulnerability.summary,
                    "aliases": finding.vulnerability.aliases,
                    "fixed_versions": finding.fixed_versions,
                },
                "cves": [cve.model_dump(mode="json") for cve in finding.cves],
                "risk_score": finding.risk_score,
                "risk_level": finding.risk_level,
                "reasons": finding.reasons,
            }
            for finding in scan.findings[:20]
        ],
    }


def _release_gate_payload(scan: ScanResult) -> dict[str, Any]:
    release_gate = None
    if scan.release_gate:
        release_gate = scan.release_gate.model_dump(
            mode="json",
            exclude={"explanation"},
        )
    payload = _scan_payload(scan)
    payload["release_gate"] = release_gate
    return payload


def _parse_agent_output(output: str) -> ReportNarrative | None:
    cleaned = output.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return ReportNarrative(
            executive_summary="AI narrative was generated, but it did not return structured JSON.",
            technical_summary=output,
            remediation_plan=[],
            questions=[],
            ai_generated=True,
        )
    return ReportNarrative(
        executive_summary=str(data.get("executive_summary", "")).strip(),
        technical_summary=str(data.get("technical_summary", "")).strip(),
        remediation_plan=[str(item) for item in data.get("remediation_plan", [])],
        questions=[str(item) for item in data.get("questions", [])],
        ai_generated=True,
    )


def _parse_release_gate_output(
    output: str,
    fallback_ticket: ReleaseGateTicket,
) -> ReleaseGateExplanation | None:
    cleaned = output.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return ReleaseGateExplanation(
            executive_summary=(
                "AI release gate explanation was generated, but it did not return "
                "structured JSON."
            ),
            technical_summary=output,
            release_decision_explanation="The deterministic release decision remains unchanged.",
            top_required_actions=[],
            safe_fix_plan=[],
            what_would_make_this_pass=[],
            developer_ticket=fallback_ticket,
            questions_for_developer=[],
            ai_generated=True,
        )

    ticket_data = data.get("developer_ticket")
    ticket = fallback_ticket
    if isinstance(ticket_data, dict):
        ticket = ReleaseGateTicket(
            title=str(ticket_data.get("title") or fallback_ticket.title).strip(),
            description=str(ticket_data.get("description") or fallback_ticket.description).strip(),
            acceptance_criteria=[
                str(item) for item in ticket_data.get("acceptance_criteria", [])
            ]
            or fallback_ticket.acceptance_criteria,
            evidence=[str(item) for item in ticket_data.get("evidence", [])]
            or fallback_ticket.evidence,
        )

    return ReleaseGateExplanation(
        executive_summary=str(data.get("executive_summary", "")).strip(),
        technical_summary=str(data.get("technical_summary", "")).strip(),
        release_decision_explanation=str(
            data.get("release_decision_explanation", "")
        ).strip(),
        top_required_actions=[str(item) for item in data.get("top_required_actions", [])],
        safe_fix_plan=[str(item) for item in data.get("safe_fix_plan", [])],
        what_would_make_this_pass=[
            str(item) for item in data.get("what_would_make_this_pass", [])
        ],
        developer_ticket=ticket,
        questions_for_developer=[
            str(item) for item in data.get("questions_for_developer", [])
        ],
        ai_generated=True,
    )
