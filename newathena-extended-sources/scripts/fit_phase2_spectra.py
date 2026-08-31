"""Fit the Phase 2 regional spectra with the workshop phabs*apec model."""

from __future__ import annotations

import json
import os
from pathlib import Path

from xspec import AllData, AllModels, Fit, Model, Spectrum, Xset

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runtime" / "phase2-baseline"
EXPOSURE = int(os.environ.get("EXPOSURE", "100000"))


def fit_region(region: str, initial_temperature: float) -> dict[str, object]:
    AllData.clear()
    AllModels.clear()
    spectrum = Spectrum(str(OUTPUT / f"multispec_{EXPOSURE}s_{region}.pha"))
    AllData.ignore("bad")
    spectrum.ignore("**-0.2 12.0-**")

    model = Model("phabs*apec")
    model(1).values = 0.03
    model(1).frozen = True
    model(2).values = initial_temperature
    model(2).frozen = False
    model(3).values = 0.5
    model(3).frozen = False
    model(4).values = 0.0
    model(4).frozen = True
    model(5).frozen = False

    Fit.statMethod = "cstat"
    Fit.method = "leven 1000 0.01"
    Fit.query = "yes"
    Fit.perform()
    Fit.error("1.0 2 3")

    return {
        "region": region,
        "model": "phabs*apec",
        "fit_band_keV": [0.2, 12.0],
        "statistic": "cstat",
        "statistic_value": float(Fit.statistic),
        "degrees_of_freedom": int(Fit.dof),
        "nH_1e22_cm2": float(model(1).values[0]),
        "nH_frozen": bool(model(1).frozen),
        "temperature_keV": float(model(2).values[0]),
        "temperature_error_1sigma": [float(value) for value in model(2).error[:2]],
        "temperature_error_status": str(model(2).error[2]),
        "abundance_solar": float(model(3).values[0]),
        "abundance_error_1sigma": [float(value) for value in model(3).error[:2]],
        "abundance_error_status": str(model(3).error[2]),
        "redshift": float(model(4).values[0]),
        "redshift_frozen": bool(model(4).frozen),
        "normalization": float(model(5).values[0]),
    }


def main() -> None:
    Xset.abund = "angr"
    Xset.xsect = "vern"
    Xset.chatter = 5
    Xset.logChatter = 10

    results = [fit_region("cen", 3.6), fit_region("out", 10.5)]
    truth = json.loads((OUTPUT / f"phase2_{EXPOSURE}s_truth_summary.json").read_text())
    for result in results:
        region_truth = truth["regions"][str(result["region"])]
        for quantity, fit_key in (
            ("temperature", "temperature_keV"),
            ("abundance", "abundance_solar"),
        ):
            continuous_key = f"continuous_brightness_weighted_{quantity}" + (
                "_keV" if quantity == "temperature" else "_solar"
            )
            detected_key = f"detected_count_weighted_{quantity}" + (
                "_keV" if quantity == "temperature" else "_solar"
            )
            fitted = float(result[fit_key])
            continuous = float(region_truth[continuous_key])
            detected = float(region_truth[detected_key])
            result[f"{quantity}_continuous_truth"] = continuous
            result[f"{quantity}_detected_truth"] = detected
            result[f"{quantity}_bias_vs_continuous_fraction"] = (
                fitted / continuous - 1.0
            )
            result[f"{quantity}_bias_vs_detected_fraction"] = fitted / detected - 1.0
    destination = OUTPUT / f"phase2_{EXPOSURE}s_fit_results.json"
    destination.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
