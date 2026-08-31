# Validation evidence

## Reference runtime

- macOS arm64
- Python 3.12.13
- HEASoft 6.35.2
- XSPEC/PyXspec 12.15.0d
- SIMPUT 2.8.0
- SIXTE 3.4.0
- NewAthena X-IFU instrument package 1.11.1
- X-IFU response release 1.4.1, ESA baseline 4 eV configuration

## Executed profiles

Notebooks 00, 02, and 03 execute from clean kernels under both profiles. The
upstream export was also executed from this directory while the runtime and
external-input locations were supplied only through `NEWATHENA_RUNTIME_DIR`
and `NEWATHENA_INPUT_DIR`.

| Profile | Phase 2 exposure | Phase 3 exposure | Phase 3 ARF sampling | Status |
| --- | ---: | ---: | ---: | --- |
| teaching | 1 ks | 1 ks | 10,000 photons | demonstration only |
| reference | 100 ks | 100 ks | 100,000 photons | validated reference |

## Scientific checks

- Phase 2 reference PHA counts: 46,725 central and 47,350 outer; both reconcile
  with positive-signal event rows.
- Phase 3 reference events: 3,325,142.
- Phase 3 reference mixing: east is 98.5455% soft; west is 92.7311% hard.
- Naive west fit: photon index 1.57082 versus input 1.5.
- Mixed fit: soft index 2.50131 versus 2.5; hard index 1.49924 versus 1.5.
- Dominant 50k-to-100k ARF changes are about 0.11% at the median. Weak
  cross-region paths retain 1.65--1.69% median Monte Carlo changes and are a
  documented limitation.
- Teaching/reference Phase 3 mixing fractions agree within 0.062 percentage
  points. Teaching mixed responses reduce the hard-index absolute offset from
  0.0926 to 0.0204 without claiming reference precision.
- The contributed Phase 3 morphology generator reproduces the validated FITS
  masks exactly: 7,825 combined nonzero pixels and 3,863 per hemisphere.

## Repository checks

- Python unit tests
- strict package type checking
- Ruff lint and format checks
- shell syntax checks
- source-clean notebook inspection
- executed-cell error inspection
- package source and wheel build
- contribution workspace validation
- generated-file and Git ignore audit

## Known limits

- The notebooks have not yet been executed inside an actual SciServer session.
- Instrument-response FITS metadata emit known `FILTER` and `TELESCOP`
  capitalization warnings.
- Instrument bundles, external cluster maps, and generated science products are
  intentionally not committed.
