#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib/runtime_env.sh"
output_dir="${runtime_dir}/phase2-baseline"
cluster_input_dir="${input_dir}/X-IFU_clusters_tutorial"

exposure="${EXPOSURE:-1000}"
seed="${SEED:-20260721}"
simput="${output_dir}/clusterA2146_arf_padded.simput"
prefix="${output_dir}/multispec_${exposure}s_"
xml="${SIXTE_INSTRUMENTS}/new-athena-xifu/baseline/xifu_nofilt_infoc.xml"
instrument_path="${SIXTE_INSTRUMENTS}/new-athena-xifu/baseline"
region_dir="${project_dir}/inputs/phase2"

mkdir -p "${output_dir}"

if [[ ! -f "${simput}" || "${REBUILD_SIMPUT:-no}" == "yes" ]]; then
  simputmultispec \
    Simput="${simput}" \
    XSPECFile="${cluster_input_dir}/xifu_point_source.xcm" \
    ImageFile="${cluster_input_dir}/A2146_SXB_russel_coord_cal.fits" \
    ParamFiles="${cluster_input_dir}/A2146_kt_russel_coord_cal.fits;${cluster_input_dir}/A2146_ab_russel_coord_cal.fits" \
    ParamNames="2;3" \
    ParamsLogScale="yes;no" \
    ParamsNumValues="8;8" \
    Emin=0.5 Emax=10.0 \
    srcFlux=7.995076796356145e-12 \
    RA=239.064583333 Dec=66.3470277776 \
    Elow=0.1495 Eup=12.101 Nbins=47806 \
    clobber=yes
fi

simputverify Simput="${simput}"

sixtesim \
  RA=239.04 Dec=66.36 \
  Simput="${simput}" \
  Exposure="${exposure}" \
  XMLFile="${xml}" \
  Prefix="${prefix}" \
  Background=no \
  Seed="${seed}" \
  history=yes progressbar=no clobber=yes

radec2xy \
  EvtFile="${prefix}evt.fits" \
  Projection=TAN \
  RefRA=239.04 RefDec=66.36

imgev \
  NAXIS1=151 NAXIS2=151 \
  CUNIT1=deg CUNIT2=deg \
  CDELT1=-0.000495 CDELT2=0.000495 \
  CRPIX1=76 CRPIX2=76 \
  CRVAL1=239.04 CRVAL2=66.36 \
  Projection=TAN CoordinateSystem=0 \
  EvtFile="${prefix}evt.fits[EVENTS]" \
  Image="${output_dir}/multispec_${exposure}s.img" \
  clobber=yes

for region in cen out; do
  region_file="${region_dir}/xifu_${region}.reg"
  ftcopy \
    "${prefix}evt.fits[EVENTS][regfilter('${region_file}')]" \
    "${output_dir}/multispec_${exposure}s_${region}_evt.fits" \
    copyall=yes clobber=yes

  makespec \
    EvtFile="${prefix}evt.fits" \
    RSPPATH="${instrument_path}" \
    regfile="${region_file}" \
    Spectrum="${output_dir}/multispec_${exposure}s_${region}.pha" \
    clobber=yes
done
