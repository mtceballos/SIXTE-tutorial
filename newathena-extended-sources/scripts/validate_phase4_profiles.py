"""Validate teaching-profile behavior against the science reference profile."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PHASE2 = ROOT / "runtime" / "phase2-baseline"
PHASE3 = ROOT / "runtime" / "phase3-mixing"
OUTPUT = ROOT / "runtime" / "phase4-portability"


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def main() -> None:
    phase2_teaching = load(PHASE2 / "phase2_1000s_truth_summary.json")
    phase2_reference = load(PHASE2 / "phase2_100000s_truth_summary.json")
    phase3_mixing = load(PHASE3 / "phase3_mixing_summary.json")
    phase3_naive_teaching = load(PHASE3 / "phase3_1000s_naive_fit_results.json")
    phase3_mixed_teaching = load(PHASE3 / "phase3_1000s_n10000_mixed_fit_results.json")
    phase3_mixed_reference = load(
        PHASE3 / "phase3_100000s_n100000_mixed_fit_results.json"
    )

    phase2_counts: dict[str, dict[str, int]] = {}
    for region in ("cen", "out"):
        teaching_region = phase2_teaching["regions"][region]
        reference_region = phase2_reference["regions"][region]
        assert teaching_region["pha_count_reconciliation"]
        assert reference_region["pha_count_reconciliation"]
        phase2_counts[region] = {
            "teaching_pha_counts": teaching_region["pha_counts"],
            "reference_pha_counts": reference_region["pha_counts"],
        }

    mixing_differences: dict[str, float] = {}
    for region in ("east", "west"):
        teaching_fraction = phase3_mixing["exposures"]["1000"]["regions"][region][
            "source_fractions"
        ]
        reference_fraction = phase3_mixing["exposures"]["100000"]["regions"][region][
            "source_fractions"
        ]
        maximum = max(
            abs(teaching_fraction[source] - reference_fraction[source])
            for source in teaching_fraction
        )
        assert maximum < 0.002
        mixing_differences[region] = maximum

    naive_west = next(
        item for item in phase3_naive_teaching if item["region"] == "west"
    )
    mixed_hard = next(
        item for item in phase3_mixed_teaching["models"] if item["source"] == "hard"
    )
    assert abs(mixed_hard["bias_vs_truth"]) < abs(naive_west["bias_vs_local_truth"])
    assert all(
        abs(item["fractional_bias_vs_truth"]) < 0.001
        for item in phase3_mixed_reference["models"]
    )

    report = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "profiles": {
            "teaching": "demonstration_only",
            "reference": "validated_reference",
        },
        "phase2_pha_counts": phase2_counts,
        "phase3_teaching_vs_reference_maximum_mixing_fraction_difference": (
            mixing_differences
        ),
        "phase3_teaching_west_absolute_naive_bias": abs(
            naive_west["bias_vs_local_truth"]
        ),
        "phase3_teaching_hard_absolute_mixed_bias": abs(mixed_hard["bias_vs_truth"]),
        "reference_truth_recovery_within_0.1_percent": True,
        "status": "PASS",
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "profile_validation.json"
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
