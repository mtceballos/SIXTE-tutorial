"""Check whether the Phase 1 simulation runtime and frozen inputs are ready."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from newathena_sixte_extended_sources import load_workspace

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = load_workspace(start=ROOT)
INSTALL = WORKSPACE.runtime / "install"
XIFU_ARCHIVE_SIZE = 2_948_575_012
XIFU_ARCHIVE_SHA256 = "8fe6c7cb54c04df447dacc4c03df62236ca15aed53400b1b5c4ae67abc9c997f"

EXPECTED = {
    "simput-v2.8.0.tar.gz": (
        "d41ee8152ff98b75ee5403ffe3ca328d3ee38c2c5e389151e1ff94e21c325179"
    ),
    "sixte-v3.4.0.tar.gz": (
        "4fc86d05466037a9572372b3d05e2e02e9fa2f432adbdaf8b8a1c0998236c224"
    ),
    "instruments_athena-wfi-1.12.1.tar.gz": (
        "5ed10e1d2612ead4371c175c9e35aa51c2cf3668cc6f997e87bd9d6cd525e256"
    ),
    "X-IFU_clusters_tutorial.tgz": (
        "89ee6a6833a5a17f8ab465d846ae3eee031abe89a9670dadb555fb100c91e541"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def version(binary: str) -> str:
    result = subprocess.run(
        [str(INSTALL / "bin" / binary)], check=True, capture_output=True, text=True
    )
    return result.stdout.splitlines()[0]


def main() -> None:
    downloads = WORKSPACE.inputs.parent / "downloads"
    checksums = {}
    failures = []
    for name, expected in EXPECTED.items():
        path = downloads / name
        actual = sha256(path) if path.is_file() else None
        checksums[name] = {
            "expected": expected,
            "actual": actual,
            "ok": actual == expected,
        }
        if actual != expected:
            failures.append(name)

    required = {
        "simputversion": INSTALL / "bin" / "simputversion",
        "sixteversion": INSTALL / "bin" / "sixteversion",
        "sixtesim": INSTALL / "bin" / "sixtesim",
        "wfi_instruments": (INSTALL / "share" / "sixte" / "instruments" / "athena-wfi"),
        "cluster_inputs": (WORKSPACE.inputs / "X-IFU_clusters_tutorial"),
        "xifu_baseline_xml": (
            INSTALL
            / "share"
            / "sixte"
            / "instruments"
            / "new-athena-xifu"
            / "baseline"
            / "xifu_nofilt_infoc.xml"
        ),
    }
    paths = {name: path.exists() for name, path in required.items()}
    failures.extend(name for name, exists in paths.items() if not exists)

    xifu_archive = downloads / "X-IFU-MISSION-ADOPTION-REVIEW-RELEASE-05-26.zip"
    xifu_size = xifu_archive.stat().st_size if xifu_archive.is_file() else 0
    xifu_checksum = sha256(xifu_archive) if xifu_size == XIFU_ARCHIVE_SIZE else None
    xifu_status = (
        "verified" if xifu_checksum == XIFU_ARCHIVE_SHA256 else "partial_or_pending"
    )

    manifest = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "versions": {
            "simput": version("simputversion"),
            "sixte": version("sixteversion"),
            "python": platform.python_version(),
        },
        "archive_checksums": checksums,
        "required_paths": paths,
        "core_runtime_ready": not failures,
        "xifu_instrument_bundle": {
            "status": xifu_status,
            "expected_size_bytes": XIFU_ARCHIVE_SIZE,
            "observed_size_bytes": xifu_size,
            "expected_sha256": XIFU_ARCHIVE_SHA256,
            "observed_sha256": xifu_checksum,
        },
    }
    output = WORKSPACE.runtime / "phase1-readiness.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    if failures:
        raise SystemExit("Phase 1 core readiness failures: " + ", ".join(failures))


if __name__ == "__main__":
    main()
