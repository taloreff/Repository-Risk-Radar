from __future__ import annotations

import json

from repo_risk_radar.models import ScanResult


def render_json_report(scan: ScanResult) -> str:
    return json.dumps(scan.model_dump(mode="json"), indent=2, sort_keys=True)
