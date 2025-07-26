#!/bin/bash
set -euo pipefail

IMAGE_NAME="spendee-mcp"
REGISTRY="127.0.0.1:5555"
TAG="latest"

NO_PUSH=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t)
            TAG="$2"
            shift 2
            ;;
        --no-push)
            NO_PUSH=1
            shift
            ;;
        *)
            echo "Usage: $0 [-t tag] [--no-push]"
            exit 1
            ;;
    esac
done

REGISTRY_TAG="$REGISTRY/$IMAGE_NAME:$TAG"

cd "$(dirname "$0")"

echo "Building Docker image..."
docker build -t "$IMAGE_NAME:$TAG" -t "$REGISTRY_TAG" .

if [[ "$NO_PUSH" -eq 0 ]]; then
    echo "Pushing Docker image to local registry..."
    docker push "$REGISTRY_TAG"
else
    echo "Skipping push to local registry (--no-push specified)."
fi

echo "Done."
