#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
input_dir="${NEWATHENA_INPUT_DIR:-${project_dir}/data/external/inputs}"
destination="$(dirname "${input_dir}")/downloads/X-IFU-MISSION-ADOPTION-REVIEW-RELEASE-05-26.zip"
url="https://sdrive.cnrs.fr/public.php/dav/files/mBLrAMCkFYGcB7o"

mkdir -p "$(dirname "${destination}")"
curl --fail --location --show-error --continue-at - \
  --user mBLrAMCkFYGcB7o: \
  --output "${destination}" \
  "${url}"

actual_size="$(stat -f '%z' "${destination}")"
expected_size="2948575012"
if [[ "${actual_size}" != "${expected_size}" ]]; then
  echo "Unexpected archive size: ${actual_size} bytes (expected ${expected_size})" >&2
  exit 1
fi

shasum -a 256 "${destination}"
unzip -tq "${destination}"
