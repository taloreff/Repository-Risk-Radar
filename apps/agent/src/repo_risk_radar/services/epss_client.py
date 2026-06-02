from __future__ import annotations

import httpx

from repo_risk_radar.models import CveEnrichment, ExternalServiceError

EPSS_API_URL = "https://api.first.org/data/v1/epss"


class EPSSClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> EPSSClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def enrich_many(self, cve_ids: list[str]) -> dict[str, CveEnrichment]:
        enrichments: dict[str, CveEnrichment] = {}
        for chunk in _chunks(sorted(set(cve_ids)), max_chars=1900):
            if not chunk:
                continue
            response = await self._client.get(EPSS_API_URL, params={"cve": ",".join(chunk)})
            if response.status_code in {403, 429}:
                raise ExternalServiceError("FIRST EPSS rate limit reached. Try again later.")
            if response.status_code >= 400:
                raise ExternalServiceError(f"FIRST EPSS returned HTTP {response.status_code}.")

            data = response.json()
            for item in data.get("data", []) or []:
                if not isinstance(item, dict) or not item.get("cve"):
                    continue
                cve_id = str(item["cve"])
                enrichments[cve_id] = CveEnrichment(
                    cve_id=cve_id,
                    epss_score=_float_or_none(item.get("epss")),
                    epss_percentile=_float_or_none(item.get("percentile")),
                    epss_date=str(item["date"]) if item.get("date") else None,
                )
        return enrichments


def merge_epss(
    nvd_enrichments: dict[str, CveEnrichment],
    epss_enrichments: dict[str, CveEnrichment],
) -> dict[str, CveEnrichment]:
    merged = dict(nvd_enrichments)
    for cve_id, epss in epss_enrichments.items():
        current = merged.get(cve_id, CveEnrichment(cve_id=cve_id))
        merged[cve_id] = current.model_copy(
            update={
                "epss_score": epss.epss_score,
                "epss_percentile": epss.epss_percentile,
                "epss_date": epss.epss_date,
            }
        )
    return merged


def _float_or_none(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _chunks(values: list[str], max_chars: int) -> list[list[str]]:
    chunks: list[list[str]] = []
    current: list[str] = []
    current_length = 0
    for value in values:
        extra = len(value) + (1 if current else 0)
        if current and current_length + extra > max_chars:
            chunks.append(current)
            current = [value]
            current_length = len(value)
        else:
            current.append(value)
            current_length += extra
    if current:
        chunks.append(current)
    return chunks
