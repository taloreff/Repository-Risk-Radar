from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    github_token: str | None
    nvd_api_key: str | None
    request_timeout_seconds: float = 30.0


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        openai_api_key=_blank_to_none(os.getenv("OPENAI_API_KEY")),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
        github_token=_blank_to_none(os.getenv("GITHUB_TOKEN")),
        nvd_api_key=_blank_to_none(os.getenv("NVD_API_KEY")),
    )
