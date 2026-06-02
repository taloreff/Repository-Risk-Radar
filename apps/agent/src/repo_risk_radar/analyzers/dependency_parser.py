from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Iterable
from typing import Any

from packaging.requirements import InvalidRequirement, Requirement

from repo_risk_radar.models import Dependency, ManifestFile, RepoRiskRadarError

_COMMENT_RE = re.compile(r"\s+#.*$")
_EXACT_PYTHON_RE = re.compile(r"==\s*([A-Za-z0-9_.!+\-]+)")
_EXACT_NPM_RE = re.compile(r"^v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$")


def extract_dependencies(manifests: Iterable[ManifestFile]) -> list[Dependency]:
    dependencies: list[Dependency] = []
    for manifest in manifests:
        filename = manifest.path.rsplit("/", maxsplit=1)[-1]
        try:
            if filename == "package.json":
                dependencies.extend(parse_package_json(manifest.content, manifest.path))
            elif filename == "package-lock.json":
                dependencies.extend(parse_package_lock(manifest.content, manifest.path))
            elif filename == "requirements.txt":
                dependencies.extend(parse_requirements_txt(manifest.content, manifest.path))
            elif filename == "pyproject.toml":
                dependencies.extend(parse_pyproject_toml(manifest.content, manifest.path))
        except (json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
            raise RepoRiskRadarError(f"Could not parse {manifest.path}: {exc}") from exc
    return _merge_dependencies(dependencies)


def parse_package_json(content: str, source_file: str = "package.json") -> list[Dependency]:
    data = json.loads(content)
    dependencies: list[Dependency] = []
    for section, dependency_type in (("dependencies", "direct"), ("devDependencies", "dev")):
        values = data.get(section, {})
        if not isinstance(values, dict):
            continue
        for name, constraint in sorted(values.items()):
            dependencies.append(
                Dependency(
                    name=name,
                    ecosystem="npm",
                    source_file=source_file,
                    version_constraint=str(constraint),
                    resolved_version=_exact_npm_version(str(constraint)),
                    dependency_type=dependency_type,
                )
            )
    return dependencies


def parse_package_lock(content: str, source_file: str = "package-lock.json") -> list[Dependency]:
    data = json.loads(content)
    dependencies: list[Dependency] = []

    packages = data.get("packages")
    if isinstance(packages, dict):
        root = packages.get("", {})
        direct_names = _package_lock_root_names(root)
        installed = _package_lock_installed_versions(packages)
        for name, dependency_type in sorted(direct_names.items()):
            dependencies.append(
                Dependency(
                    name=name,
                    ecosystem="npm",
                    source_file=source_file,
                    version_constraint=None,
                    resolved_version=installed.get(name),
                    dependency_type=dependency_type,
                )
            )
        return dependencies

    legacy_dependencies = data.get("dependencies", {})
    if isinstance(legacy_dependencies, dict):
        for name, details in sorted(legacy_dependencies.items()):
            version = details.get("version") if isinstance(details, dict) else None
            dependencies.append(
                Dependency(
                    name=name,
                    ecosystem="npm",
                    source_file=source_file,
                    resolved_version=str(version) if version else None,
                    dependency_type="unknown",
                )
            )
    return dependencies


def parse_requirements_txt(content: str, source_file: str = "requirements.txt") -> list[Dependency]:
    dependencies: list[Dependency] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(("-", "--")):
            continue
        line = _strip_inline_comment(line)
        if not line:
            continue
        try:
            requirement = Requirement(line)
        except InvalidRequirement:
            continue
        constraint = str(requirement.specifier) or None
        dependencies.append(
            Dependency(
                name=requirement.name,
                ecosystem="PyPI",
                source_file=source_file,
                version_constraint=constraint,
                resolved_version=_exact_python_version(constraint),
                dependency_type="direct",
            )
        )
    return dependencies


def parse_pyproject_toml(content: str, source_file: str = "pyproject.toml") -> list[Dependency]:
    data = tomllib.loads(content)
    dependencies: list[Dependency] = []

    project = data.get("project", {})
    if isinstance(project, dict):
        dependencies.extend(
            _parse_pep508_dependencies(project.get("dependencies", []), source_file, "direct")
        )
        optional = project.get("optional-dependencies", {})
        if isinstance(optional, dict):
            for values in optional.values():
                dependencies.extend(_parse_pep508_dependencies(values, source_file, "optional"))

    poetry = data.get("tool", {}).get("poetry", {}) if isinstance(data.get("tool"), dict) else {}
    if isinstance(poetry, dict):
        poetry_dependencies = poetry.get("dependencies", {})
        dependencies.extend(_parse_poetry_dependencies(poetry_dependencies, source_file, "direct"))
        poetry_groups = poetry.get("group", {})
        if isinstance(poetry_groups, dict):
            for group in poetry_groups.values():
                group_dependencies = (
                    group.get("dependencies", {}) if isinstance(group, dict) else {}
                )
                dependencies.extend(
                    _parse_poetry_dependencies(group_dependencies, source_file, "dev")
                )

    return dependencies


def _parse_pep508_dependencies(
    values: Any, source_file: str, dependency_type: str
) -> list[Dependency]:
    dependencies: list[Dependency] = []
    if not isinstance(values, list):
        return dependencies
    for value in values:
        if not isinstance(value, str):
            continue
        try:
            requirement = Requirement(value)
        except InvalidRequirement:
            continue
        constraint = str(requirement.specifier) or None
        dependencies.append(
            Dependency(
                name=requirement.name,
                ecosystem="PyPI",
                source_file=source_file,
                version_constraint=constraint,
                resolved_version=_exact_python_version(constraint),
                dependency_type=dependency_type,
            )
        )
    return dependencies


def _parse_poetry_dependencies(
    values: Any, source_file: str, dependency_type: str
) -> list[Dependency]:
    dependencies: list[Dependency] = []
    if not isinstance(values, dict):
        return dependencies
    for name, raw_constraint in sorted(values.items()):
        if name.lower() == "python":
            continue
        constraint = _poetry_constraint_to_string(raw_constraint)
        dependencies.append(
            Dependency(
                name=name,
                ecosystem="PyPI",
                source_file=source_file,
                version_constraint=constraint,
                resolved_version=_exact_python_version(constraint),
                dependency_type=dependency_type,
            )
        )
    return dependencies


def _poetry_constraint_to_string(raw_constraint: Any) -> str | None:
    if isinstance(raw_constraint, str):
        return raw_constraint
    if isinstance(raw_constraint, dict):
        version = raw_constraint.get("version")
        return str(version) if version else None
    return str(raw_constraint) if raw_constraint is not None else None


def _strip_inline_comment(line: str) -> str:
    if " #" not in line:
        return line
    return _COMMENT_RE.sub("", line).strip()


def _exact_python_version(constraint: str | None) -> str | None:
    if not constraint:
        return None
    match = _EXACT_PYTHON_RE.search(constraint)
    return match.group(1) if match else None


def _exact_npm_version(constraint: str | None) -> str | None:
    if not constraint:
        return None
    match = _EXACT_NPM_RE.match(constraint.strip())
    return match.group(1) if match else None


def _package_lock_root_names(root: Any) -> dict[str, str]:
    names: dict[str, str] = {}
    if not isinstance(root, dict):
        return names
    for section, dependency_type in (("dependencies", "direct"), ("devDependencies", "dev")):
        values = root.get(section, {})
        if not isinstance(values, dict):
            continue
        for name in values:
            names[str(name)] = dependency_type
    return names


def _package_lock_installed_versions(packages: dict[str, Any]) -> dict[str, str]:
    installed: dict[str, str] = {}
    for path, details in packages.items():
        if not path.startswith("node_modules/") or not isinstance(details, dict):
            continue
        name = path.removeprefix("node_modules/")
        version = details.get("version")
        if version:
            installed[name] = str(version)
    return installed


def _merge_dependencies(dependencies: list[Dependency]) -> list[Dependency]:
    merged: dict[tuple[str, str], Dependency] = {}
    for dependency in dependencies:
        key = (dependency.ecosystem.lower(), dependency.name.lower())
        existing = merged.get(key)
        if existing is None:
            merged[key] = dependency
            continue

        source_files = sorted(set(existing.source_file.split(", ") + [dependency.source_file]))
        existing.source_file = ", ".join(source_files)
        if not existing.resolved_version and dependency.resolved_version:
            existing.resolved_version = dependency.resolved_version
        if not existing.version_constraint and dependency.version_constraint:
            existing.version_constraint = dependency.version_constraint
        if (
            existing.dependency_type in {"unknown", "optional"}
            and dependency.dependency_type != "unknown"
        ):
            existing.dependency_type = dependency.dependency_type

    return sorted(merged.values(), key=lambda item: (item.ecosystem, item.name.lower()))
