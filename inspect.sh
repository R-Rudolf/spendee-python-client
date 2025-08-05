#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(which python)" != "$(pwd)/.venv/bin/python" ]]; then
    source .venv/bin/activate
fi
source .venv/bin/activate
mcp dev spendee/spendee_mcp.py $@
