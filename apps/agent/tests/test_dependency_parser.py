from repo_risk_radar.analyzers.dependency_parser import (
    extract_dependencies,
    parse_package_json,
    parse_package_lock,
    parse_pyproject_toml,
    parse_requirements_txt,
)
from repo_risk_radar.models import ManifestFile


def test_parse_package_json_dependencies_and_dev_dependencies() -> None:
    content = """
    {
      "dependencies": {"express": "^4.18.2", "left-pad": "1.3.0"},
      "devDependencies": {"vitest": "1.2.3"}
    }
    """

    dependencies = parse_package_json(content)

    assert {dependency.name for dependency in dependencies} == {"express", "left-pad", "vitest"}
    left_pad = next(dependency for dependency in dependencies if dependency.name == "left-pad")
    vitest = next(dependency for dependency in dependencies if dependency.name == "vitest")
    assert left_pad.resolved_version == "1.3.0"
    assert vitest.dependency_type == "dev"


def test_parse_package_lock_v3_direct_versions() -> None:
    content = """
    {
      "lockfileVersion": 3,
      "packages": {
        "": {
          "dependencies": {"express": "^4.18.2"},
          "devDependencies": {"vitest": "^1.2.3"}
        },
        "node_modules/express": {"version": "4.18.2"},
        "node_modules/vitest": {"version": "1.2.3"}
      }
    }
    """

    dependencies = parse_package_lock(content)

    assert {dependency.name: dependency.resolved_version for dependency in dependencies} == {
        "express": "4.18.2",
        "vitest": "1.2.3",
    }


def test_parse_requirements_txt_skips_options_and_extracts_pinned_versions() -> None:
    content = """
    --index-url https://example.invalid/simple
    requests==2.31.0  # keep pinned
    django>=4.2
    # comment
    """

    dependencies = parse_requirements_txt(content)

    assert {dependency.name for dependency in dependencies} == {"requests", "django"}
    requests = next(dependency for dependency in dependencies if dependency.name == "requests")
    django = next(dependency for dependency in dependencies if dependency.name == "django")
    assert requests.resolved_version == "2.31.0"
    assert django.resolved_version is None


def test_parse_pyproject_project_and_poetry_dependencies() -> None:
    content = """
    [project]
    dependencies = ["httpx==0.27.0"]

    [project.optional-dependencies]
    dev = ["pytest>=8"]

    [tool.poetry.dependencies]
    python = "^3.11"
    typer = "^0.12"
    """

    dependencies = parse_pyproject_toml(content)

    assert {dependency.name.lower() for dependency in dependencies} == {"httpx", "pytest", "typer"}
    httpx = next(dependency for dependency in dependencies if dependency.name == "httpx")
    assert httpx.resolved_version == "0.27.0"


def test_extract_dependencies_merges_lockfile_resolution() -> None:
    manifests = [
        ManifestFile(
            path="package.json",
            content='{"dependencies": {"express": "^4.18.0"}}',
        ),
        ManifestFile(
            path="package-lock.json",
            content="""
            {
              "packages": {
                "": {"dependencies": {"express": "^4.18.0"}},
                "node_modules/express": {"version": "4.18.2"}
              }
            }
            """,
        ),
    ]

    dependencies = extract_dependencies(manifests)

    assert len(dependencies) == 1
    assert dependencies[0].name == "express"
    assert dependencies[0].version_constraint == "^4.18.0"
    assert dependencies[0].resolved_version == "4.18.2"
