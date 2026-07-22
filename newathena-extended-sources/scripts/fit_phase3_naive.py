"""Fit Phase 3 regional spectra while ignoring spatial-spectral mixing."""

from __future__ import annotations

import json
import os
from pathlib import Path

from xspec import AllData, AllModels, Fit, Model, Spectrum, Xset

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runtime" / "phase3-mixing"
LOCAL_TRUTH = {"east": 2.5, "west": 1.5}
EXPOSURE = int(os.environ.get("EXPOSURE", "100000"))


def fit_region(region: str) -> dict[str, object]:
    AllData.clear()
    AllModels.clear()
    spectrum = Spectrum(str(OUTPUT / f"mixing_{EXPOSURE}s_{region}.pha"))
    AllData.ignore("bad")
    spectrum.ignore("**-1.0 12.0-**")

    model = Model("phabs*powerlaw")
    model(1).values = 1.0
    model(1).frozen = True
    model(2).values = LOCAL_TRUTH[region]
    model(2).frozen = False
    model(3).frozen = False

    Fit.statMethod = "cstat"
    Fit.method = "leven 1000 0.01"
    Fit.query = "yes"
    Fit.perform()
    Fit.error("1.0 2")

    photon_index = float(model(2).values[0])
    truth = LOCAL_TRUTH[region]
    return {
        "region": region,
        "model": "phabs*powerlaw",
        "fit_band_keV": [1.0, 12.0],
        "statistic": "cstat",
        "statistic_value": float(Fit.statistic),
        "degrees_of_freedom": int(Fit.dof),
        "nH_1e22_cm2": float(model(1).values[0]),
        "nH_frozen": bool(model(1).frozen),
        "photon_index": photon_index,
        "photon_index_error_1sigma": [float(value) for value in model(2).error[:2]],
        "photon_index_error_status": str(model(2).error[2]),
        "local_source_truth": truth,
        "bias_vs_local_truth": photon_index - truth,
        "fractional_bias_vs_local_truth": photon_index / truth - 1.0,
        "normalization": float(model(3).values[0]),
    }


def main() -> None:
    Xset.abund = "angr"
    Xset.xsect = "vern"
    Xset.chatter = 5
    Xset.logChatter = 10

    results = [fit_region(region) for region in ("east", "west")]
    destination = OUTPUT / f"phase3_{EXPOSURE}s_naive_fit_results.json"
    destination.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
