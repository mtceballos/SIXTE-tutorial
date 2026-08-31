"""Validate the required upstream tutorial contribution structure."""

from pathlib import Path

REQUIRED_PATHS = (
    "README.md",
    "config",
    "inputs/phase2/xifu_cen.reg",
    "inputs/phase2/xifu_out.reg",
    "inputs/phase3/east.reg",
    "inputs/phase3/west.reg",
    "inputs/phase3/model_soft.xcm",
    "inputs/phase3/model_hard.xcm",
    "notebooks/README.md",
    "src/newathena_sixte_extended_sources/__init__.py",
    "tests/test_package.py",
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise SystemExit(f"Missing required workspace paths:\n{formatted}")
    print(f"Workspace structure valid: {root}")


if __name__ == "__main__":
    main()
