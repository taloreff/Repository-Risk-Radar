from repo_risk_radar.analyzers.repo_detector import parse_github_url


def test_parse_github_url_owner_repo() -> None:
    repo = parse_github_url("https://github.com/openai/openai-python")

    assert repo.owner == "openai"
    assert repo.name == "openai-python"
    assert repo.ref is None


def test_parse_github_url_tree_branch() -> None:
    repo = parse_github_url("https://github.com/taloreff/Tasker/tree/dev")

    assert repo.owner == "taloreff"
    assert repo.name == "Tasker"
    assert repo.ref == "dev"


def test_parse_github_url_tree_branch_with_slash() -> None:
    repo = parse_github_url("https://github.com/example/project/tree/feature/test-scan")

    assert repo.owner == "example"
    assert repo.name == "project"
    assert repo.ref == "feature/test-scan"
