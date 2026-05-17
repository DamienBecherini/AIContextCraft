#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SEQUENCES_DIR="${ROOT_DIR}/docs/architecture/sequences"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

if [[ ! -d "${SEQUENCES_DIR}" ]]; then
  echo "Mermaid sequences directory not found: ${SEQUENCES_DIR}" >&2
  exit 1
fi

if ! command -v mmdc >/dev/null 2>&1; then
  echo "mermaid-cli (mmdc) is not available; skipping Mermaid syntax validation." >&2
  exit 0
fi

shopt -s nullglob
files=("${SEQUENCES_DIR}"/*.md)
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No sequence markdown files found in ${SEQUENCES_DIR}."
  exit 0
fi

for file in "${files[@]}"; do
  graph_file="${TMP_DIR}/$(basename "${file}" .md).mmd"
  output_file="${TMP_DIR}/$(basename "${file}" .md).svg"

  awk '
    /^```mermaid$/ {in_block=1; next}
    /^```$/ && in_block {in_block=0; exit}
    in_block {print}
  ' "${file}" > "${graph_file}"

  if [[ ! -s "${graph_file}" ]]; then
    echo "No Mermaid block found in ${file}" >&2
    exit 1
  fi

  mmdc \
    -q \
    -i "${graph_file}" \
    -o "${output_file}" >/dev/null || {
      echo "Mermaid CLI execution failed for ${file}; verify your Node/npm environment." >&2
      exit 1
    }
done

echo "Mermaid validation completed for ${#files[@]} file(s)."
