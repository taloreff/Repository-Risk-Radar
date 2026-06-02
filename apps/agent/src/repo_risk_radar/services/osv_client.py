from __future__ import annotations

from collections import defaultdict

import httpx

from repo_risk_radar.models import (
    Dependency,
    ExternalServiceError,
    Vulnerability,
    VulnerabilityReference,
)

OSV_API_BASE = "https://api.osv.dev"


class OSVClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self._client = httpx.AsyncClient(base_url=OSV_API_BASE, timeout=timeout)
        self._vulnerability_cache: dict[str, Vulnerability] = {}

    async def __aenter__(self) -> OSVClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def query_dependencies(
        self, dependencies: list[Dependency]
    ) -> list[tuple[Dependency, Vulnerability]]:
        query_dependencies = [
            dependency for dependency in dependencies if dependency.resolved_version
        ]
        if not query_dependencies:
            return []

        results: list[tuple[Dependency, Vulnerability]] = []
        for chunk in _chunks(query_dependencies, 100):
            payload = {
                "queries": [
                    {
                        "version": dependency.resolved_version,
                        "package": {
                            "name": dependency.name,
                            "ecosystem": dependency.ecosystem,
                        },
                    }
                    for dependency in chunk
                ]
            }
            response = await self._client.post("/v1/querybatch", json=payload)
            if response.status_code in {429, 503}:
                raise ExternalServiceError(
                    "OSV.dev rate limit or service limit reached. Try again later."
                )
            if response.status_code >= 400:
                raise ExternalServiceError(f"OSV.dev returned HTTP {response.status_code}.")
            data = response.json()
            for dependency, result in zip(chunk, data.get("results", []), strict=False):
                for vuln_data in result.get("vulns", []) or []:
                    results.append((dependency, await self._full_vulnerability(vuln_data)))
        return _dedupe_results(results)

    async def _full_vulnerability(self, vuln_data: dict) -> Vulnerability:
        vuln_id = vuln_data.get("id")
        if not isinstance(vuln_id, str) or not vuln_id:
            return _parse_vulnerability(vuln_data)
        if vuln_id in self._vulnerability_cache:
            return self._vulnerability_cache[vuln_id]

        response = await self._client.get(f"/v1/vulns/{vuln_id}")
        if response.status_code == 404:
            vulnerability = _parse_vulnerability(vuln_data)
        elif response.status_code in {429, 503}:
            raise ExternalServiceError(
                "OSV.dev rate limit or service limit reached. Try again later."
            )
        elif response.status_code >= 400:
            raise ExternalServiceError(
                f"OSV.dev returned HTTP {response.status_code} for {vuln_id}."
            )
        else:
            vulnerability = _parse_vulnerability(response.json())

        self._vulnerability_cache[vuln_id] = vulnerability
        return vulnerability


def _parse_vulnerability(data: dict) -> Vulnerability:
    references = [
        VulnerabilityReference(type=ref.get("type"), url=ref["url"])
        for ref in data.get("references", [])
        if isinstance(ref, dict) and ref.get("url")
    ]
    vulnerability = Vulnerability(
        id=data.get("id", "UNKNOWN"),
        summary=data.get("summary"),
        details=data.get("details"),
        aliases=list(data.get("aliases", []) or []),
        modified=data.get("modified"),
        published=data.get("published"),
        database_specific=data.get("database_specific", {}) or {},
        affected=data.get("affected", []) or [],
        references=references,
        severity=data.get("severity", []) or [],
    )
    return vulnerability.model_copy(
        update={"fixed_versions": _extract_fixed_versions(vulnerability)}
    )


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


def _dedupe_results(
    results: list[tuple[Dependency, Vulnerability]],
) -> list[tuple[Dependency, Vulnerability]]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[tuple[Dependency, Vulnerability]] = []
    for dependency, vulnerability in results:
        key = (dependency.ecosystem, dependency.name.lower(), vulnerability.id)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((dependency, vulnerability))
    return deduped


def _chunks(values: list[Dependency], size: int) -> list[list[Dependency]]:
    grouped: defaultdict[int, list[Dependency]] = defaultdict(list)
    for index, value in enumerate(values):
        grouped[index // size].append(value)
    return list(grouped.values())
