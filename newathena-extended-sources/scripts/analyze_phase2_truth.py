"""Build truth and region-mixing products for the Phase 2 Abell 2146 baseline."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from regions import Regions

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "external" / "inputs" / "X-IFU_clusters_tutorial"
OUTPUT = ROOT / "runtime" / "phase2-baseline"
REGIONS = (
    ROOT
    / "references"
    / "upstream"
    / "sixte_workshop_2026"
    / "extended_sources"
    / "multispec"
    / "input"
)
EXPOSURE = int(os.environ.get("EXPOSURE", "100000"))


def load_primary(name: str) -> tuple[np.ndarray, fits.Header]:
    with fits.open(INPUT / name) as hdus:
        return np.asarray(hdus[0].data, dtype=float), hdus[0].header.copy()


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.average(values, weights=weights))


def main() -> None:
    brightness, header = load_primary("A2146_SXB_russel_coord_cal.fits")
    temperature, _ = load_primary("A2146_kt_russel_coord_cal.fits")
    abundance, _ = load_primary("A2146_ab_russel_coord_cal.fits")
    wcs = WCS(header)

    temperature_grid = np.geomspace(temperature.min(), temperature.max(), 8)
    abundance_grid = np.linspace(abundance.min(), abundance.max(), 8)
    temperature_index = np.abs(
        np.log(temperature[..., None]) - np.log(temperature_grid)
    ).argmin(axis=-1)
    abundance_index = np.abs(abundance[..., None] - abundance_grid).argmin(axis=-1)
    quantized_temperature = temperature_grid[temperature_index]
    quantized_abundance = abundance_grid[abundance_index]

    with fits.open(OUTPUT / "clusterA2146_arf_padded.simput") as hdus:
        catalog = hdus["SRC_CAT"].data
        source_rows = {
            int(row["SRC_ID"]): {
                "source_name": str(row["SRC_NAME"]),
                "flux_erg_s_cm2": float(row["FLUX"]),
            }
            for row in catalog
        }

    for row in source_rows.values():
        _, temperature_bin, abundance_bin = row["source_name"].split("_")
        row["temperature_bin"] = int(temperature_bin)
        row["abundance_bin"] = int(abundance_bin)
        row["temperature_keV"] = float(temperature_grid[int(temperature_bin)])
        row["abundance_solar"] = float(abundance_grid[int(abundance_bin)])

    summaries: dict[str, object] = {
        "temperature_grid_keV": temperature_grid.tolist(),
        "abundance_grid_solar": abundance_grid.tolist(),
        "regions": {},
    }
    mixing_rows: list[dict[str, object]] = []

    for region_name in ("cen", "out"):
        region_path = REGIONS / f"xifu_{region_name}.reg"
        sky_region = Regions.read(region_path, format="ds9")[0]
        pixel_region = sky_region.to_pixel(wcs)
        mask_image = pixel_region.to_mask(mode="center").to_image(brightness.shape)
        mask = np.asarray(mask_image) > 0
        weights = brightness[mask]
        positive = weights > 0
        weights = weights[positive]

        event_path = OUTPUT / f"multispec_{EXPOSURE}s_{region_name}_evt.fits"
        with fits.open(event_path) as hdus:
            events = hdus[1].data
            source_ids, detected_counts = np.unique(
                events["SRC_ID"], return_counts=True
            )
            zero_signal = int(np.count_nonzero(events["SIGNAL"] <= 0))

        detected_total = int(detected_counts.sum())
        detected_temperature = 0.0
        detected_abundance = 0.0
        for source_id, count in zip(source_ids, detected_counts, strict=True):
            source = source_rows[int(source_id)]
            fraction = float(count / detected_total)
            detected_temperature += fraction * float(source["temperature_keV"])
            detected_abundance += fraction * float(source["abundance_solar"])
            mixing_rows.append(
                {
                    "region": region_name,
                    "source_id": int(source_id),
                    **source,
                    "detected_counts": int(count),
                    "detected_fraction": fraction,
                }
            )

        with fits.open(OUTPUT / f"multispec_{EXPOSURE}s_{region_name}.pha") as hdus:
            pha_counts = int(np.sum(hdus["SPECTRUM"].data["COUNTS"]))

        summaries["regions"][region_name] = {
            "map_pixels": int(mask.sum()),
            "positive_brightness_pixels": int(positive.sum()),
            "continuous_brightness_weighted_temperature_keV": weighted_mean(
                temperature[mask][positive], weights
            ),
            "continuous_brightness_weighted_abundance_solar": weighted_mean(
                abundance[mask][positive], weights
            ),
            "quantized_brightness_weighted_temperature_keV": weighted_mean(
                quantized_temperature[mask][positive], weights
            ),
            "quantized_brightness_weighted_abundance_solar": weighted_mean(
                quantized_abundance[mask][positive], weights
            ),
            "detected_count_weighted_temperature_keV": detected_temperature,
            "detected_count_weighted_abundance_solar": detected_abundance,
            "region_event_rows": detected_total,
            "zero_signal_events": zero_signal,
            "pha_counts": pha_counts,
            "pha_count_reconciliation": detected_total - zero_signal == pha_counts,
            "detected_source_components": int(len(source_ids)),
        }

    summary_path = OUTPUT / f"phase2_{EXPOSURE}s_truth_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2) + "\n")

    mixing_path = OUTPUT / f"phase2_{EXPOSURE}s_region_source_mixing.csv"
    with mixing_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(mixing_rows[0]))
        writer.writeheader()
        writer.writerows(mixing_rows)

    print(json.dumps(summaries, indent=2))
    print(f"Wrote {mixing_path}")


if __name__ == "__main__":
    main()
