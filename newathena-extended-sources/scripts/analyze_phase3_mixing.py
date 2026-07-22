"""Measure Phase 3 source-to-region mixing and validate spectral counts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from astropy.io import fits

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runtime" / "phase3-mixing"
SOURCE_LABELS = {1: "east_soft", 2: "west_hard"}


def main() -> None:
    summaries: dict[str, object] = {"exposures": {}}
    mixing_rows: list[dict[str, object]] = []

    for exposure in (1000, 100000):
        with fits.open(OUTPUT / f"mixing_{exposure}s_evt.fits") as hdus:
            total_events = len(hdus["EVENTS"].data)

        exposure_summary: dict[str, object] = {
            "total_event_rows": total_events,
            "regions": {},
        }
        for region in ("east", "west"):
            with fits.open(OUTPUT / f"mixing_{exposure}s_{region}_evt.fits") as hdus:
                events = hdus["EVENTS"].data
                source_ids, counts = np.unique(events["SRC_ID"], return_counts=True)
                zero_signal = int(np.count_nonzero(events["SIGNAL"] <= 0))

            region_total = int(counts.sum())
            source_counts = {
                SOURCE_LABELS[int(source_id)]: int(count)
                for source_id, count in zip(source_ids, counts, strict=True)
            }
            source_fractions = {
                SOURCE_LABELS[int(source_id)]: float(count / region_total)
                for source_id, count in zip(source_ids, counts, strict=True)
            }
            for source_id, count in zip(source_ids, counts, strict=True):
                mixing_rows.append(
                    {
                        "exposure_s": exposure,
                        "region": region,
                        "source_id": int(source_id),
                        "source": SOURCE_LABELS[int(source_id)],
                        "detected_counts": int(count),
                        "detected_fraction": float(count / region_total),
                    }
                )

            with fits.open(OUTPUT / f"mixing_{exposure}s_{region}.pha") as hdus:
                pha_counts = int(np.sum(hdus["SPECTRUM"].data["COUNTS"]))

            exposure_summary["regions"][region] = {
                "event_rows": region_total,
                "zero_signal_events": zero_signal,
                "pha_counts": pha_counts,
                "pha_count_reconciliation": region_total - zero_signal == pha_counts,
                "source_counts": source_counts,
                "source_fractions": source_fractions,
            }
        summaries["exposures"][str(exposure)] = exposure_summary

    summary_path = OUTPUT / "phase3_mixing_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2) + "\n")

    mixing_path = OUTPUT / "phase3_region_source_mixing.csv"
    with mixing_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(mixing_rows[0]))
        writer.writeheader()
        writer.writerows(mixing_rows)

    print(json.dumps(summaries, indent=2))
    print(f"Wrote {mixing_path}")


if __name__ == "__main__":
    main()
