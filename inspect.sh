#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ "$(which python)" != "$(pwd)/.venv/bin/python" ]]; then
    source .venv/bin/activate
fi

if [ ! -L ".venv/lib64/python3.11/site-packages/spendee" ]; then
    ln -s "$(pwd)/spendee" ".venv/lib64/python3.11/site-packages/spendee"
fi

source .env

mcp dev spendee/spendee_mcp.py $@
