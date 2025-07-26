#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(which python)" != "$(pwd)/.venv/bin/python" ]]; then
    source .venv/bin/activate
fi
source .venv/bin/activate
DANGEROUSLY_OMIT_AUTH=true mcp dev spendee/spendee_mcp.py $@
