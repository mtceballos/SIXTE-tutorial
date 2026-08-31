#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib/runtime_env.sh"
output_dir="${runtime_dir}/phase3-mixing"
region_dir="${project_dir}/inputs/phase3"

photon_trials="${PHOTON_TRIALS:-10000 50000 100000}"
max_jobs="${MAX_JOBS:-1}"
xml="${SIXTE_INSTRUMENTS}/new-athena-xifu/baseline/xifu_nofilt_infoc.xml"

mkdir -p "${output_dir}"

for n_photons in ${photon_trials}; do
  trial_dir="${output_dir}/arf_trials/n${n_photons}"
  mkdir -p "${trial_dir}"
  path_index=0
  pids=()
  for region in east west; do
    for source in soft hard; do
      seed=$((2026072200 + path_index))
      sixte_arfgen \
        XMLFile="${xml}" \
        Simput="${output_dir}/mixing_${source}.simput" \
        regfile="${region_dir}/${region}.reg" \
        ARFCorr="${trial_dir}/mixing_${source}_in_${region}.arf" \
        RA=45.0 Dec=0.0 \
        RefRA=45.0 RefDec=0.0 \
        sampling_factor=100 \
        n_photons="${n_photons}" \
        Exposure=100000 \
        Seed="${seed}" \
        progressbar=no history=yes clobber=yes &
      pids+=("$!")
      path_index=$((path_index + 1))
      if (( ${#pids[@]} == max_jobs )); then
        for pid in "${pids[@]}"; do
          wait "${pid}"
        done
        pids=()
      fi
    done
  done
  if (( ${#pids[@]} > 0 )); then
    for pid in "${pids[@]}"; do
      wait "${pid}"
    done
  fi
done
