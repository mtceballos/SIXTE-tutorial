# Notebook sequence

- `00_environment_and_input_readiness.ipynb` validates frozen software,
  archive checksums, instrument configuration, and the seed policy.
- `02_spatially_varying_cluster_plasma.ipynb` presents the validated Abell 2146
  X-IFU baseline, truth definitions, source mixing, and recovery bias.
- `03_spatial_spectral_mixing.ipynb` measures region contamination and compares
  naive and explicit mixed-response spectral inference.

All notebooks call the shared workspace loader. Select the full science
reference with `NEWATHENA_PROFILE=reference` (the default), or the reduced-cost
classroom path with `NEWATHENA_PROFILE=teaching`. Hosted environments set
`NEWATHENA_RUNTIME_DIR` and `NEWATHENA_INPUT_DIR` to mounted locations; the
notebook science cells remain unchanged.

Teaching outputs demonstrate the workflow but do not inherit reference status.
Each notebook includes an exercise, a collapsible solution, interpretation,
and actionable missing-product guidance.

Generated products remain outside version control under `runtime/`. Notebook
sources are output-free; clean-kernel executed copies are written under
`runtime/executed-notebooks/<profile>/` for validation.
