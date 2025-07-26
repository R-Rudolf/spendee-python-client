#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
DANGEROUSLY_OMIT_AUTH=true mcp dev spendee/spendee_mcp.py
