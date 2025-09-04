#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
source .venv/bin/activate
source .env

python -m spendee.spendee_mcp "$@"
