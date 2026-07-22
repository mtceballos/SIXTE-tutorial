#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Source scripts/lib/runtime_env.sh; do not execute it directly." >&2
  exit 2
fi

project_dir="${NEWATHENA_PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
runtime_dir="${NEWATHENA_RUNTIME_DIR:-${project_dir}/runtime}"
input_dir="${NEWATHENA_INPUT_DIR:-${project_dir}/data/external/inputs}"

: "${HEADAS:?Source the HEASoft initialization script before this workflow.}"

export SIXTE="${SIXTE:-${runtime_dir}/install}"
export SIMPUT="${SIMPUT:-${SIXTE}}"
export SIXTE_INSTRUMENTS="${SIXTE_INSTRUMENTS:-${SIXTE}/share/sixte/instruments}"

mkdir -p "${runtime_dir}/pfiles"
set +u
source "${SIXTE}/bin/sixte-install.sh"
set -u
export PFILES="${runtime_dir}/pfiles;${SIXTE}/share/simput/pfiles:${SIXTE}/share/sixte/pfiles:${HEADAS}/syspfiles"
