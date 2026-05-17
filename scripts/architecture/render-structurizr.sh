#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKSPACE_DSL="${ROOT_DIR}/docs/architecture/structurizr/workspace.dsl"
OUT_DIR="${ROOT_DIR}/docs/architecture/structurizr/out"

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

if [[ ! -f "${WORKSPACE_DSL}" ]]; then
  echo "Structurizr workspace not found: ${WORKSPACE_DSL}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

if command -v structurizr >/dev/null 2>&1; then
  structurizr export \
    -workspace "${WORKSPACE_DSL}" \
    -format "plantuml" \
    -output "${OUT_DIR}"
  echo "Structurizr export completed using local CLI."
  exit 0
fi

DOCKER_CMD="$(resolve_docker_cmd || true)"
if [[ -n "${DOCKER_CMD}" ]]; then
  if ! "${DOCKER_CMD}" info >/dev/null 2>&1; then
    echo "Docker CLI found (${DOCKER_CMD}) but daemon is not running; cannot run structurizr/structurizr container." >&2
    exit 1
  fi

  "${DOCKER_CMD}" run --rm \
    --user "$(id -u):$(id -g)" \
    -v "${ROOT_DIR}:/workspace" \
    structurizr/structurizr:latest \
    export \
    -workspace /workspace/docs/architecture/structurizr/workspace.dsl \
    -format "plantuml" \
    -output /workspace/docs/architecture/structurizr/out
  echo "Structurizr export completed using Docker image structurizr/structurizr."
  exit 0
fi

echo "Neither structurizr CLI nor Docker (docker or docker.exe) is available on this machine." >&2
exit 1
