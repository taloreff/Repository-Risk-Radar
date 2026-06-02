from __future__ import annotations

from typing import Any

import httpx

from repo_risk_radar.models import CveEnrichment, ExternalServiceError

NVD_CVE_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class NVDClient:
    def __init__(self, api_key: str | None = None, timeout: float = 30.0) -> None:
        headers = {"User-Agent": "repo-risk-radar"}
        if api_key:
            headers["apiKey"] = api_key
        self._client = httpx.AsyncClient(headers=headers, timeout=timeout)

    async def __aenter__(self) -> NVDClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def enrich_many(self, cve_ids: list[str]) -> dict[str, CveEnrichment]:
        enrichments: dict[str, CveEnrichment] = {}
        for cve_id in sorted(set(cve_ids)):
            enrichments[cve_id] = await self.enrich(cve_id)
        return enrichments

    async def enrich(self, cve_id: str) -> CveEnrichment:
        response = await self._client.get(NVD_CVE_API_URL, params={"cveId": cve_id})
        if response.status_code in {403, 429}:
            raise ExternalServiceError(
                "NVD rate limit reached. Try again later or set NVD_API_KEY in .env."
            )
        if response.status_code >= 400:
            raise ExternalServiceError(f"NVD returned HTTP {response.status_code} for {cve_id}.")
        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])
        if not vulnerabilities:
            return CveEnrichment(cve_id=cve_id)
        cve = vulnerabilities[0].get("cve", {})
        metrics = _extract_metrics(cve.get("metrics", {}))
        return CveEnrichment(
            cve_id=cve_id,
            cvss_score=metrics[0],
            severity=metrics[1],
            cwe_ids=_extract_cwes(cve),
            cisa_known_exploited=bool(cve.get("cisaExploitAdd")),
            cisa_due_date=cve.get("cisaActionDue"),
            published=cve.get("published"),
            last_modified=cve.get("lastModified"),
            references=_extract_references(cve),
        )


def _extract_metrics(metrics: dict[str, Any]) -> tuple[float | None, str | None]:
    for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        values = metrics.get(key, [])
        if not values:
            continue
        metric = values[0]
        cvss_data = metric.get("cvssData", {}) if isinstance(metric, dict) else {}
        score = cvss_data.get("baseScore")
        severity = cvss_data.get("baseSeverity") or metric.get("baseSeverity")
        return (float(score) if score is not None else None, str(severity) if severity else None)
    return None, None


def _extract_cwes(cve: dict[str, Any]) -> list[str]:
    cwes: set[str] = set()
    for weakness in cve.get("weaknesses", []) or []:
        for description in weakness.get("description", []) if isinstance(weakness, dict) else []:
            value = description.get("value") if isinstance(description, dict) else None
            if value and value.startswith("CWE-"):
                cwes.add(value)
    return sorted(cwes)


def _extract_references(cve: dict[str, Any]) -> list[str]:
    references = cve.get("references", {})
    values = references.get("referenceData", []) if isinstance(references, dict) else []
    urls = [item.get("url") for item in values if isinstance(item, dict) and item.get("url")]
    return list(dict.fromkeys(urls))
