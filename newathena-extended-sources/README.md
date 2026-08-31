# NewAthena SIXTE Extended-Source Notebooks

Validated, science-driven NewAthena X-IFU notebooks extending the SIXTE
extended-source tutorials.

## Project status

Notebooks 00, 02, and 03 have been executed locally under both the 1 ks
teaching profile and the 100 ks reference profile. Actual SciServer execution
remains to be validated.

## Scientific objective

Develop a tutorial workflow that constructs a spatially and spectrally
structured extended X-ray source, simulates a NewAthena observation with
SIXTE, produces standard analysis products, and quantitatively compares the
recovered measurements with the known simulation truth.

## Curriculum

- `00_environment_and_input_readiness.ipynb`: software, calibration, input,
  checksum, and seed readiness.
- `02_spatially_varying_cluster_plasma.ipynb`: Abell 2146 temperature and
  abundance structure with regional truth recovery.
- `03_spatial_spectral_mixing.ipynb`: source-to-region contamination, naive
  bias, ARF convergence, and simultaneous mixed-response inference.

## Directory layout

- `notebooks/`: output-free teaching notebooks.
- `src/`: reusable Python code extracted from validated notebook workflows.
- `tests/`: unit and scientific-contract tests.
- `scripts/`: reproducible acquisition, execution, and validation entrypoints.
- `config/`: versioned simulation and analysis configuration.
- `inputs/`: small versioned region and spectral-model definitions.

Downloaded inputs and generated products belong beneath `data/external/` and
`runtime/`; the repository excludes them.

## Development environment

Python 3.12 is the canonical development version. `pyproject.toml` is the
source of truth for Python dependencies; `environment.yml` supplies the Conda
scientific runtime. SIXTE, SIMPUT, HEASoft, and PyXspec are external runtime
dependencies and are recorded separately because they are not ordinary PyPI
packages.

The external Abell 2146 workshop input archive and official X-IFU response
release must be acquired before reference execution. Notebook 00 fails early
and reports missing products rather than silently substituting data.

Set `NEWATHENA_PROFILE=teaching` for the reduced 1 ks/10k-ARF path or
`NEWATHENA_PROFILE=reference` for the validated 100 ks/100k-ARF path. Hosted
environments may set `NEWATHENA_RUNTIME_DIR` and `NEWATHENA_INPUT_DIR` without
changing notebook science cells.

Before Phase 3 simulation, generate the two-component morphology:

```bash
python scripts/build_phase3_images.py
```

## Validation

```bash
make check
make quality
```

`make check` is the release-facing validation path. `make quality` exposes
lint, formatting, and typing work separately so scientific results are not
rewritten merely to satisfy style tooling.

Scientific reference evidence: X-IFU instrument package 1.11.1, response
release 1.4.1, SIMPUT 2.8.0, SIXTE 3.4.0, HEASoft 6.35.2, and XSPEC 12.15.0d.
The 100 ks mixing fit recovered photon indices 2.50131 and 1.49924 from truths
2.5 and 1.5. Weak cross-region ARFs retain percent-level Monte Carlo sampling
uncertainty, documented in notebook 03.
