#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

render_status=0
validate_status=0
assets_status=0

"${ROOT_DIR}/scripts/architecture/render-structurizr.sh" || render_status=$?
"${ROOT_DIR}/scripts/architecture/validate-mermaid.sh" || validate_status=$?
"${ROOT_DIR}/scripts/architecture/render-diagram-assets.sh" || assets_status=$?

if [[ ${render_status} -ne 0 ]]; then
  echo "Structurizr export failed (exit: ${render_status})." >&2
fi

if [[ ${validate_status} -ne 0 ]]; then
  echo "Mermaid validation failed (exit: ${validate_status})." >&2
fi

if [[ ${assets_status} -ne 0 ]]; then
  echo "Diagram assets generation failed (exit: ${assets_status})." >&2
fi

if [[ ${render_status} -ne 0 || ${validate_status} -ne 0 || ${assets_status} -ne 0 ]]; then
  exit 1
fi

echo "Architecture artifacts generation finished."
