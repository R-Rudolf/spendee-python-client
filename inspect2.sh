#!/bin/bash
set -euo pipefail

REGISTRY="127.0.0.1:5555"

INSPECTOR_DIR="$(dirname "$0")/../inspector"
if [ ! -d "$INSPECTOR_DIR" ]; then
    git clone https://github.com/modelcontextprotocol/inspector.git "$INSPECTOR_DIR"
fi

if ! docker image inspect inspector:latest >/dev/null 2>&1; then
    echo "Local 'inspector' Docker image not found. Building image..."
    docker build -t inspector -t ${REGISTRY}/inspector "$INSPECTOR_DIR"
fi

if [ "${1:-}" == "build" ]; then
    docker build -t inspector -t ${REGISTRY}/inspector "$(dirname "$0")/../inspector"
    docker push ${REGISTRY}/inspector
fi

if [ -z "${1:-}" ] || [ $1 == "run" ]; then
    docker run -it --rm --name inspector \
        -p 6274:6274 \
        -p 6277:6277 \
        -e BASE_URL="http://0.0.0.0:6274" \
        -e HOST=0.0.0.0 \
        -e 'ALLOWED_ORIGINS=*' \
        -e 'DEBUG=*' \
        -e LOG_LEVEL=debug \
        -e DANGEROUSLY_OMIT_AUTH=true \
        inspector "$@"
fi
