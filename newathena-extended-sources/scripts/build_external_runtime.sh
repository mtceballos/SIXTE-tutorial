#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
env_dir="${project_dir}/.venv"
runtime_dir="${project_dir}/runtime"
install_dir="${runtime_dir}/install"
conda_bin="${CONDA_EXE:-}"

if [[ -z "${conda_bin}" ]]; then
  conda_bin="$(command -v conda || true)"
fi

simput_src="${runtime_dir}/src/simput-v2.8.0"
sixte_src="${runtime_dir}/src/sixte-v3.4.0"

if [[ ! -d "${env_dir}" ]]; then
  echo "Missing project environment: ${env_dir}" >&2
  exit 1
fi

if [[ -z "${conda_bin}" || ! -x "${conda_bin}" ]]; then
  echo "Conda executable not found. Activate Conda or set CONDA_EXE." >&2
  exit 1
fi

if [[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
  config_sub=""
  for candidate in \
    /opt/local/share/automake-1.18/config.sub \
    /opt/local/share/libtool/build-aux/config.sub \
    /opt/local/share/autoconf/build-aux/config.sub; do
    if [[ -f "${candidate}" ]]; then
      config_sub="${candidate}"
      break
    fi
  done

  if [[ -z "${config_sub}" ]]; then
    echo "A current config.sub is required to build bundled WCSLIB on Apple Silicon." >&2
    exit 1
  fi

  cp "${config_sub}" "${simput_src}/extlib/wcslib/config/config.sub"
fi

mkdir -p "${runtime_dir}/build/simput" "${runtime_dir}/build/sixte" "${install_dir}"

"${conda_bin}" run -p "${env_dir}" cmake \
  -S "${simput_src}" \
  -B "${runtime_dir}/build/simput" \
  -G Ninja \
  -DCMAKE_INSTALL_PREFIX="${install_dir}" \
  -DCMAKE_PREFIX_PATH="${env_dir}" \
  -DCMAKE_BUILD_TYPE=Release

"${conda_bin}" run -p "${env_dir}" cmake --build "${runtime_dir}/build/simput" --parallel 8
"${conda_bin}" run -p "${env_dir}" cmake --install "${runtime_dir}/build/simput"

"${conda_bin}" run -p "${env_dir}" cmake \
  -S "${sixte_src}" \
  -B "${runtime_dir}/build/sixte" \
  -G Ninja \
  -DCMAKE_INSTALL_PREFIX="${install_dir}" \
  -DSIMPUT_ROOT="${install_dir}" \
  -DCMAKE_PREFIX_PATH="${env_dir}" \
  -DCMAKE_BUILD_TYPE=Release

"${conda_bin}" run -p "${env_dir}" cmake --build "${runtime_dir}/build/sixte" --parallel 8
"${conda_bin}" run -p "${env_dir}" cmake --install "${runtime_dir}/build/sixte"
