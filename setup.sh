#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

REQUIRED_PASSWORD="spendee-password"

# --- Mise environment setup ---
if ! command -v curl >/dev/null 2>&1; then
  echo "curl not found. Installing curl via apt..."
  sudo apt-get update
  sudo apt-get install -y curl
fi

if [ ! -x "$HOME/.local/bin/mise" ]; then
  echo "Mise not found in ~/.local/bin. Installing Mise..."
  curl https://mise.run | sh
fi

echo "Activate Mise environment and install"
eval "$(~/.local/bin/mise activate bash)"
mise install


# --- Python virtual environment setup ---
echo "Create a virtual environment"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

echo  "Activate the python virtual environment"
source .venv/bin/activate

echo "Install dependencies"
pip install -r requirements.txt


# --- Bitwarden credential setup ---
if [ ! -f ".env" ]; then
  if [ -z "${BWS_ACCESS_TOKEN:-}" ]; then
    echo "Neither .env file is set, nor BWS_ACCESS_TOKEN environment variable is not set or empty. Setup can not be complete without them."
    exit 1
  fi
  echo ".env file does not exist, loading it via Bitwarden"
  if ! bws secret list | jq -r '.[] | .key' | grep -qx "$REQUIRED_PASSWORD"; then
    echo "Secret key '$REQUIRED_PASSWORD' not found in Bitwarden secrets. Verify if access key is right, or access to the project/key was set."
    exit 1
  fi
  PASSWORD=$(bws secret list  | jq -r '.[] | select(.key == "'$REQUIRED_PASSWORD'") | .value')
  EMAIL_LINE=$(bws secret list  | jq -r '.[] | select(.key == "'$REQUIRED_PASSWORD'") | .note') # example value: EMAIL=lumi.8.lumiere@gmail.com

  echo "PASSWORD='${PASSWORD}'" > .env
  echo "${EMAIL_LINE}" >> .env
fi
