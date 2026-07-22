#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib/runtime_env.sh"
output_dir="${runtime_dir}/phase3-mixing"
input_model_dir="${project_dir}/inputs/phase3"

mkdir -p "${output_dir}"

sides=(east west)
spectra=(soft hard)
source_ids=(1 2)

for index in "${!sides[@]}"; do
  side="${sides[$index]}"
  spectrum="${spectra[$index]}"
  simput="${output_dir}/mixing_${spectrum}.simput"

  simputfile \
    Simput="${simput}" \
    Src_ID="${source_ids[$index]}" \
    RA=45.0 Dec=0.0 \
    srcFlux=2e-11 Emin=2.0 Emax=10.0 \
    Elow=0.1495 Eup=12.101 Nbins=47806 \
    XSPECFile="${input_model_dir}/model_${spectrum}.xcm" \
    ImageFile="${output_dir}/mixing_simput_img_${side}.fits" \
    clobber=yes

  simputverify Simput="${simput}"
done
