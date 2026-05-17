#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STRUCTURIZR_OUT_DIR="${ROOT_DIR}/docs/architecture/structurizr/out"
SEQUENCES_DIR="${ROOT_DIR}/docs/architecture/sequences"
ASSETS_DIR="${ROOT_DIR}/docs/architecture/assets"
TMP_DIR="${ROOT_DIR}/.tmp-diagram-assets"

resolve_docker_cmd() {
  if command -v docker >/dev/null 2>&1; then
    echo "docker"
    return 0
  fi

  if command -v docker.exe >/dev/null 2>&1; then
    echo "docker.exe"
    return 0
  fi

  return 1
}

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

mkdir -p "${ASSETS_DIR}" "${TMP_DIR}"

context_puml="${STRUCTURIZR_OUT_DIR}/structurizr-systemContext.puml"
container_puml="${STRUCTURIZR_OUT_DIR}/structurizr-containerView.puml"
processing_flow_puml="${STRUCTURIZR_OUT_DIR}/structurizr-processingFlowView.puml"

if [[ ! -f "${context_puml}" || ! -f "${container_puml}" || ! -f "${processing_flow_puml}" ]]; then
  echo "Missing Structurizr .puml files. Run render-structurizr.sh first." >&2
  exit 1
fi

DOCKER_CMD="$(resolve_docker_cmd || true)"

if command -v plantuml >/dev/null 2>&1; then
  plantuml -tsvg "${context_puml}" "${container_puml}" "${processing_flow_puml}"
elif [[ -n "${DOCKER_CMD}" ]] && "${DOCKER_CMD}" info >/dev/null 2>&1; then
  "${DOCKER_CMD}" run --rm \
    --user "$(id -u):$(id -g)" \
    -v "${ROOT_DIR}:/workspace" \
    plantuml/plantuml:latest \
    -tsvg \
    /workspace/docs/architecture/structurizr/out/structurizr-systemContext.puml \
    /workspace/docs/architecture/structurizr/out/structurizr-containerView.puml \
    /workspace/docs/architecture/structurizr/out/structurizr-processingFlowView.puml
else
  echo "PlantUML renderer unavailable. Install plantuml or enable Docker daemon." >&2
  exit 1
fi

if [[ ! -f "${STRUCTURIZR_OUT_DIR}/structurizr-systemContext.svg" || ! -f "${STRUCTURIZR_OUT_DIR}/structurizr-containerView.svg" || ! -f "${STRUCTURIZR_OUT_DIR}/structurizr-processingFlowView.svg" ]]; then
  echo "Structurizr SVG conversion failed." >&2
  exit 1
fi

cp "${STRUCTURIZR_OUT_DIR}/structurizr-systemContext.svg" "${ASSETS_DIR}/system-context.svg"
cp "${STRUCTURIZR_OUT_DIR}/structurizr-containerView.svg" "${ASSETS_DIR}/container-view.svg"
cp "${STRUCTURIZR_OUT_DIR}/structurizr-processingFlowView.svg" "${ASSETS_DIR}/processing-flow-view.svg"

extract_mermaid() {
  local source_md="$1"
  local target_mmd="$2"
  awk '
    /^```mermaid$/ {in_block=1; next}
    /^```$/ && in_block {in_block=0; exit}
    in_block {print}
  ' "${source_md}" > "${target_mmd}"
}

render_mermaid_svg() {
  local source_mmd="$1"
  local target_svg="$2"

  if command -v mmdc >/dev/null 2>&1; then
    mmdc -q -i "${source_mmd}" -o "${target_svg}" >/dev/null
    return
  fi

  if [[ -n "${DOCKER_CMD}" ]] && "${DOCKER_CMD}" info >/dev/null 2>&1; then
    "${DOCKER_CMD}" run --rm \
      --user "$(id -u):$(id -g)" \
      -v "${ROOT_DIR}:/workspace" \
      -v "${TMP_DIR}:/tmp/mermaid" \
      minlag/mermaid-cli:latest \
      -i "/tmp/mermaid/$(basename "${source_mmd}")" \
      -o "/workspace/docs/architecture/assets/$(basename "${target_svg}")" >/dev/null
    return
  fi

  echo "Mermaid renderer unavailable. Install mmdc or enable Docker daemon." >&2
  exit 1
}

run_standard_md="${SEQUENCES_DIR}/run-standard-flow.md"
git_diff_md="${SEQUENCES_DIR}/git-diff-flow.md"

if [[ ! -f "${run_standard_md}" || ! -f "${git_diff_md}" ]]; then
  echo "Missing Mermaid sequence source files." >&2
  exit 1
fi

run_standard_mmd="${TMP_DIR}/run-standard-flow.mmd"
git_diff_mmd="${TMP_DIR}/git-diff-flow.mmd"

extract_mermaid "${run_standard_md}" "${run_standard_mmd}"
extract_mermaid "${git_diff_md}" "${git_diff_mmd}"

if [[ ! -s "${run_standard_mmd}" || ! -s "${git_diff_mmd}" ]]; then
  echo "Failed to extract Mermaid blocks from sequence files." >&2
  exit 1
fi

render_mermaid_svg "${run_standard_mmd}" "${ASSETS_DIR}/run-standard-flow.svg"
render_mermaid_svg "${git_diff_mmd}" "${ASSETS_DIR}/git-diff-flow.svg"

echo "Diagram assets generated in ${ASSETS_DIR}."
