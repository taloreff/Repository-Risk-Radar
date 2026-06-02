from __future__ import annotations

from urllib.parse import urlparse

from repo_risk_radar.models import RepoIdentifier, RepoRiskRadarError

SUPPORTED_MANIFEST_NAMES = {
    "package.json",
    "package-lock.json",
    "requirements.txt",
    "pyproject.toml",
}


def parse_github_url(repo_url: str) -> RepoIdentifier:
    parsed = urlparse(repo_url.strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        raise RepoRiskRadarError("Please provide a public GitHub URL like https://github.com/owner/repo.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise RepoRiskRadarError("GitHub URL must include both owner and repository name.")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise RepoRiskRadarError("GitHub URL must include both owner and repository name.")

    ref = None
    if len(parts) >= 4 and parts[2] == "tree":
        ref = "/".join(parts[3:])

    return RepoIdentifier(owner=owner, name=repo, ref=ref)


def detect_manifest_paths(paths: list[str]) -> list[str]:
    manifests = []
    for path in paths:
        name = path.rsplit("/", maxsplit=1)[-1]
        if name in SUPPORTED_MANIFEST_NAMES:
            manifests.append(path)
    return sorted(manifests)
