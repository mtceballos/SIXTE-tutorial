"""Fit both Phase 3 regions with explicit two-source response mixing."""

from __future__ import annotations

import json
import os
from pathlib import Path

from xspec import AllData, AllModels, Fit, Model, Xset

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "runtime" / "phase3-mixing"
EXPOSURE = int(os.environ.get("EXPOSURE", "100000"))
ARF_PHOTONS = int(os.environ.get("ARF_PHOTONS", "100000"))
ARFS = OUTPUT / "arf_trials" / f"n{ARF_PHOTONS}"
RMF = (
    ROOT
    / "runtime"
    / "install"
    / "share"
    / "sixte"
    / "instruments"
    / "new-athena-xifu"
    / "baseline"
    / "instdata"
    / "new_athena_xifu_mar_v2_4eV_gaussian.rmf"
)
TRUTH = {"soft": 2.5, "hard": 1.5}


def link_group_models(model_name: str) -> None:
    first = AllModels(1, model_name)
    second = AllModels(2, model_name)
    for parameter_index in range(1, first.nParameters + 1):
        second(parameter_index).link = first(parameter_index)


def configure_model(model_name: str, source_number: int, photon_index: float) -> None:
    model = Model("phabs*powerlaw", model_name, source_number)
    model(1).values = 1.0
    model(1).frozen = True
    model(2).values = photon_index
    model(2).frozen = False
    model(3).frozen = False
    link_group_models(model_name)


def main() -> None:
    AllData.clear()
    AllModels.clear()
    east = OUTPUT / f"mixing_{EXPOSURE}s_east.pha"
    west = OUTPUT / f"mixing_{EXPOSURE}s_west.pha"
    AllData(f"1:1 {east} 2:2 {west}")
    AllData.ignore("bad")
    AllData.ignore("**-1.0 12.0-**")

    arf_paths = {
        (1, 0): ARFS / "mixing_soft_in_east.arf",
        (1, 1): ARFS / "mixing_hard_in_east.arf",
        (2, 0): ARFS / "mixing_soft_in_west.arf",
        (2, 1): ARFS / "mixing_hard_in_west.arf",
    }
    for group in (1, 2):
        spectrum = AllData(group)
        for source_index in (0, 1):
            spectrum.multiresponse[source_index] = str(RMF)
            spectrum.multiresponse[source_index].arf = str(
                arf_paths[(group, source_index)]
            )

    Xset.abund = "angr"
    Xset.xsect = "vern"
    Xset.chatter = 5
    Xset.logChatter = 10
    configure_model("soft", 1, TRUTH["soft"])
    configure_model("hard", 2, TRUTH["hard"])

    Fit.statMethod = "cstat"
    Fit.method = "leven 1000 0.01"
    Fit.query = "yes"
    Fit.perform()

    soft = AllModels(1, "soft")
    hard = AllModels(1, "hard")
    Fit.error("1.0 soft:2 hard:2")

    models = []
    for name, model in (("soft", soft), ("hard", hard)):
        photon_index = float(model(2).values[0])
        models.append(
            {
                "source": name,
                "photon_index": photon_index,
                "photon_index_error_1sigma": [
                    float(value) for value in model(2).error[:2]
                ],
                "photon_index_error_status": str(model(2).error[2]),
                "truth": TRUTH[name],
                "bias_vs_truth": photon_index - TRUTH[name],
                "fractional_bias_vs_truth": photon_index / TRUTH[name] - 1.0,
                "normalization": float(model(3).values[0]),
            }
        )

    results = {
        "model": "two linked phabs*powerlaw source models",
        "fit_band_keV": [1.0, 12.0],
        "statistic": "cstat",
        "statistic_value": float(Fit.statistic),
        "degrees_of_freedom": int(Fit.dof),
        "exposure_s": EXPOSURE,
        "arf_photon_trial": ARF_PHOTONS,
        "models": models,
    }
    destination = OUTPUT / (f"phase3_{EXPOSURE}s_n{ARF_PHOTONS}_mixed_fit_results.json")
    destination.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
