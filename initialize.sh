#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$ROOT_DIR/launcher.py"

if [[ ! -f "$LAUNCHER" ]]; then
  echo "Error: launcher.py not found in $ROOT_DIR"
  exit 1
fi

# Find python3 or python
if command -v python3 >/dev/null 2>&1; then
  PYBIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYBIN="python"
else
  echo "Error: Python 3 could not be found. Please install Python 3.11 or newer."
  exit 1
fi

exec "$PYBIN" "$LAUNCHER" "$@"
