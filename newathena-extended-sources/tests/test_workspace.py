from __future__ import annotations

from pathlib import Path

import pytest

from newathena_sixte_extended_sources.workspace import (
    INPUT_ENV,
    PROFILE_ENV,
    ROOT_ENV,
    RUNTIME_ENV,
    find_project_root,
    load_workspace,
)


def test_find_project_root_from_nested_directory() -> None:
    root = Path(__file__).resolve().parents[1]
    assert find_project_root(root / "notebooks") == root


def test_workspace_honors_portable_overrides(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = Path(__file__).resolve().parents[1]
    runtime = tmp_path / "runtime"
    inputs = tmp_path / "inputs"
    monkeypatch.setenv(ROOT_ENV, str(root))
    monkeypatch.setenv(RUNTIME_ENV, str(runtime))
    monkeypatch.setenv(INPUT_ENV, str(inputs))
    monkeypatch.setenv(PROFILE_ENV, "teaching")

    workspace = load_workspace()

    assert workspace.root == root
    assert workspace.runtime == runtime
    assert workspace.inputs == inputs
    assert workspace.profile == "teaching"
    assert workspace.profile_values["phase3_exposure_s"] == 1000
    assert workspace.profile_values["science_status"] == "demonstration_only"


def test_unknown_profile_fails_with_choices(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(PROFILE_ENV, "fast-but-ambiguous")
    with pytest.raises(ValueError, match="reference, teaching"):
        load_workspace()


def test_require_has_actionable_failure(tmp_path: Path) -> None:
    workspace = load_workspace()
    with pytest.raises(FileNotFoundError, match="NEWATHENA_.*notebook 00"):
        workspace.require(tmp_path / "missing.fits", "test input")
