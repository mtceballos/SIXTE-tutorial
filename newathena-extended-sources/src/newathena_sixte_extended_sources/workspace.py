"""Portable workspace and teaching-profile discovery."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import yaml

ProfileName = Literal["reference", "teaching"]
ROOT_ENV = "NEWATHENA_PROJECT_ROOT"
RUNTIME_ENV = "NEWATHENA_RUNTIME_DIR"
INPUT_ENV = "NEWATHENA_INPUT_DIR"
PROFILE_ENV = "NEWATHENA_PROFILE"


@dataclass(frozen=True)
class Workspace:
    """Resolved project paths and compute profile."""

    root: Path
    runtime: Path
    inputs: Path
    config: Path
    notebooks: Path
    profile: ProfileName
    profile_values: dict[str, object]

    def require(self, path: Path, purpose: str) -> Path:
        """Return an existing path or raise an actionable error."""
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {purpose}: {path}. Set the appropriate NEWATHENA_* "
                "environment variable or complete notebook 00 readiness first."
            )
        return path


def find_project_root(start: Path | None = None) -> Path:
    """Find the repository root without assuming notebook launch location."""
    override = os.environ.get(ROOT_ENV)
    if override:
        root = Path(override).expanduser().resolve()
        if not (root / "pyproject.toml").is_file():
            raise FileNotFoundError(f"{ROOT_ENV} is not a project root: {root}")
        return root

    candidate = (start or Path.cwd()).expanduser().resolve()
    for directory in (candidate, *candidate.parents):
        if (directory / "pyproject.toml").is_file() and (
            directory / "config" / "portability.yml"
        ).is_file():
            return directory
    raise FileNotFoundError(
        f"Could not locate the project from {candidate}. Set {ROOT_ENV}."
    )


def load_workspace(
    profile: ProfileName | None = None, start: Path | None = None
) -> Workspace:
    """Resolve local or SciServer paths through environment overrides."""
    root = find_project_root(start)
    config_path = root / "config" / "portability.yml"
    configuration = yaml.safe_load(config_path.read_text())
    selected = profile or os.environ.get(PROFILE_ENV, "reference")
    profiles = configuration["profiles"]
    if selected not in profiles:
        choices = ", ".join(sorted(profiles))
        raise ValueError(f"Unknown {PROFILE_ENV}={selected!r}; choose {choices}")
    profile_name = cast(ProfileName, selected)

    runtime = Path(os.environ.get(RUNTIME_ENV, root / "runtime")).expanduser().resolve()
    inputs = (
        Path(os.environ.get(INPUT_ENV, root / "data" / "external" / "inputs"))
        .expanduser()
        .resolve()
    )
    return Workspace(
        root=root,
        runtime=runtime,
        inputs=inputs,
        config=root / "config",
        notebooks=root / "notebooks",
        profile=profile_name,
        profile_values=dict(profiles[profile_name]),
    )
