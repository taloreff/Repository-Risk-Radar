from __future__ import annotations

import base64

import httpx

from repo_risk_radar.models import ExternalServiceError, ManifestFile, RepoIdentifier, RepoMetadata

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: float = 30.0) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "repo-risk-radar",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(base_url=GITHUB_API_BASE, headers=headers, timeout=timeout)

    async def __aenter__(self) -> GitHubClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_repo_metadata(self, repo: RepoIdentifier) -> RepoMetadata:
        data = await self._get_json(f"/repos/{repo.owner}/{repo.name}")
        return RepoMetadata(
            owner=repo.owner,
            name=repo.name,
            full_name=data.get("full_name", repo.full_name),
            html_url=data.get("html_url", f"https://github.com/{repo.full_name}"),
            default_branch=data.get("default_branch", "main"),
            description=data.get("description"),
        )

    async def get_tree_paths(self, repo: RepoIdentifier, branch: str) -> list[str]:
        data = await self._get_json(
            f"/repos/{repo.owner}/{repo.name}/git/trees/{branch}",
            params={"recursive": "1"},
        )
        tree = data.get("tree", [])
        if not isinstance(tree, list):
            return []
        return [
            item["path"]
            for item in tree
            if isinstance(item, dict) and item.get("type") == "blob" and item.get("path")
        ]

    async def get_manifest(self, repo: RepoIdentifier, path: str, branch: str) -> ManifestFile:
        data = await self._get_json(
            f"/repos/{repo.owner}/{repo.name}/contents/{path}", params={"ref": branch}
        )
        content = data.get("content")
        encoding = data.get("encoding")
        if not isinstance(content, str) or encoding != "base64":
            raise ExternalServiceError(f"GitHub returned an unexpected content format for {path}.")
        decoded = base64.b64decode(content).decode("utf-8", errors="replace")
        return ManifestFile(path=path, content=decoded)

    async def get_manifests(
        self, repo: RepoIdentifier, paths: list[str], branch: str
    ) -> list[ManifestFile]:
        manifests: list[ManifestFile] = []
        for path in paths:
            manifests.append(await self.get_manifest(repo, path, branch))
        return manifests

    async def _get_json(self, path: str, params: dict[str, str] | None = None) -> dict:
        response = await self._client.get(path, params=params)
        if response.status_code in {403, 429}:
            raise ExternalServiceError(
                "GitHub rate limit reached. Try again later or set GITHUB_TOKEN in .env."
            )
        if response.status_code == 404:
            raise ExternalServiceError("GitHub repository or file was not found.")
        if response.status_code >= 400:
            raise ExternalServiceError(
                f"GitHub API returned HTTP {response.status_code}: {_short_response(response)}"
            )
        return response.json()


def _short_response(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text[:200]
    message = data.get("message") if isinstance(data, dict) else None
    return str(message or response.text[:200])
