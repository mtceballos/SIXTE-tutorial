#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib/runtime_env.sh"
output_dir="${runtime_dir}/phase3-mixing"
region_dir="${project_dir}/inputs/phase3"

exposure="${EXPOSURE:-1000}"
seed="${SEED:-20260722}"
prefix="${output_dir}/mixing_${exposure}s_"
xml="${SIXTE_INSTRUMENTS}/new-athena-xifu/baseline/xifu_nofilt_infoc.xml"
instrument_path="${SIXTE_INSTRUMENTS}/new-athena-xifu/baseline"
simputs="${output_dir}/mixing_soft.simput,${output_dir}/mixing_hard.simput"

mkdir -p "${output_dir}"

sixtesim \
  RA=45.0 Dec=0.0 \
  Simput="${simputs}" \
  Exposure="${exposure}" \
  XMLFile="${xml}" \
  Prefix="${prefix}" \
  Background=no \
  Seed="${seed}" \
  history=yes progressbar=no clobber=yes

radec2xy \
  EvtFile="${prefix}evt.fits" \
  Projection=TAN \
  RefRA=45.0 RefDec=0.0

imgev \
  NAXIS1=151 NAXIS2=151 \
  CUNIT1=deg CUNIT2=deg \
  CDELT1=-0.000495 CDELT2=0.000495 \
  CRPIX1=76 CRPIX2=76 \
  CRVAL1=45.0 CRVAL2=0.0 \
  Projection=TAN CoordinateSystem=0 \
  EvtFile="${prefix}evt.fits[EVENTS]" \
  Image="${output_dir}/mixing_${exposure}s.img" \
  clobber=yes

for region in east west; do
  region_file="${region_dir}/${region}.reg"

  ftcopy \
    "${prefix}evt.fits[EVENTS][regfilter('${region_file}')]" \
    "${output_dir}/mixing_${exposure}s_${region}_evt.fits" \
    copyall=yes clobber=yes

  makespec \
    EvtFile="${prefix}evt.fits" \
    RSPPATH="${instrument_path}" \
    regfile="${region_file}" \
    Spectrum="${output_dir}/mixing_${exposure}s_${region}.pha" \
    clobber=yes
done
