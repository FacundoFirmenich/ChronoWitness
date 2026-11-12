#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Install Python 3.12 from python.org, then run this launcher again." >&2
  exit 1
fi
exec python3 workbench.py --menu "$@"
