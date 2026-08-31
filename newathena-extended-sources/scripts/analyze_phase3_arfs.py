"""Quantify convergence of the Phase 3 source-to-region ARFs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from astropy.io import fits

ROOT = Path(__file__).resolve().parents[1]
TRIALS = ROOT / "runtime" / "phase3-mixing" / "arf_trials"


def compare(low: int, high: int, name: str) -> dict[str, float | int | str]:
    low_path = TRIALS / f"n{low}" / name
    high_path = TRIALS / f"n{high}" / name
    with fits.open(low_path) as low_hdus, fits.open(high_path) as high_hdus:
        low_data = low_hdus["SPECRESP"].data
        high_data = high_hdus["SPECRESP"].data
        energy = (
            np.asarray(high_data["ENERG_LO"], dtype=float)
            + np.asarray(high_data["ENERG_HI"], dtype=float)
        ) / 2.0
        low_area = np.asarray(low_data["SPECRESP"], dtype=float)
        high_area = np.asarray(high_data["SPECRESP"], dtype=float)

    selected = (energy >= 1.0) & (energy <= 12.0) & (high_area > 0)
    difference = (low_area[selected] - high_area[selected]) / high_area[selected]
    absolute = np.abs(difference)
    return {
        "response": name,
        "lower_photon_trial": low,
        "higher_photon_trial": high,
        "fit_band_bins": int(selected.sum()),
        "median_absolute_fractional_change": float(np.median(absolute)),
        "p95_absolute_fractional_change": float(np.percentile(absolute, 95)),
        "rms_fractional_change": float(np.sqrt(np.mean(difference**2))),
        "maximum_absolute_fractional_change": float(np.max(absolute)),
    }


def main() -> None:
    names = sorted(path.name for path in (TRIALS / "n100000").glob("*.arf"))
    results = {
        "fit_band_keV": [1.0, 12.0],
        "comparisons": [
            compare(low, high, name)
            for low, high in ((10000, 50000), (50000, 100000))
            for name in names
        ],
        "production_trial_photons": 100000,
        "assessment": (
            "Dominant source-region paths are sub-percent stable; cross-region "
            "paths retain percent-level Monte Carlo uncertainty."
        ),
    }
    destination = TRIALS.parent / "phase3_arf_convergence.json"
    destination.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
