#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

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
~/.local/bin/mise trust .mise.toml
# Detect user shell for Mise activation
if [ -n "${BASH_VERSION:-}" ]; then
  SHELL_TYPE="bash"
elif [ -n "${ZSH_VERSION:-}" ]; then
  SHELL_TYPE="zsh"
elif [ -n "${FISH_VERSION:-}" ]; then
  SHELL_TYPE="fish"
else
  SHELL_TYPE="sh"
fi

if [[ $- == *i* ]]; then
  #Shell is interactive
  eval "$(~/.local/bin/mise activate "$SHELL_TYPE")"
else
  echo "Shell is not interactive, mise env setup may not fully function, see https://mise.jdx.dev/dev-tools/shims.html#shims-vs-path"
  eval "$(~/.local/bin/mise activate --shims)"
fi

mise install


# --- Bitwarden credential setup ---

function load_spendee_env() {
  REQUIRED_PASSWORD="spendee-password"
  if ! bws secret list | jq -r '.[] | .key' | grep -qx "$REQUIRED_PASSWORD"; then
    echo "Secret key '$REQUIRED_PASSWORD' not found in Bitwarden secrets. Verify if access key is right, or access to the project/key was set."
    exit 1
  fi
  PASSWORD=$(bws secret list  | jq -r '.[] | select(.key == "'$REQUIRED_PASSWORD'") | .value')
  EMAIL_LINE=$(bws secret list  | jq -r '.[] | select(.key == "'$REQUIRED_PASSWORD'") | .note') # example value: EMAIL=lumi.8.lumiere@gmail.com

  echo "export PASSWORD='${PASSWORD}'" > .env
  echo "export ${EMAIL_LINE}" >> .env
}

function load_mcp_agent_env() {
  REQUIRED_API_KEY="GOOGLE_API_KEY"
  if ! bws secret list | jq -r '.[] | .key' | grep -qx "$REQUIRED_API_KEY"; then
    echo "Secret key '$REQUIRED_API_KEY' not found in Bitwarden secrets. Verify if access key is right, or access to the project/key was set."
    exit 1
  fi
  GOOGLE_API_KEY=$(bws secret list  | jq -r '.[] | select(.key == "'$REQUIRED_API_KEY'") | .value') 
  echo "GOOGLE_API_KEY='${GOOGLE_API_KEY}'" > agent-test/.env
  echo "GGOOGLE_API_KEY set in agent-test/.env"
}

if [ ! -f ".env" ]; then
  if [ -z "${BWS_ACCESS_TOKEN:-}" ]; then
    echo "Neither .env file is set, nor BWS_ACCESS_TOKEN environment variable is not set or empty. Setup can not be complete without them."
    exit 1
  fi
  echo ".env file does not exist, loading it via Bitwarden"
  load_spendee_env
fi

if [ ! -f "agent-test/.env" ]; then
  if [ -z "${BWS_ACCESS_TOKEN:-}" ]; then
    echo "Neither .env file is set, nor BWS_ACCESS_TOKEN environment variable is not set or empty. Setup can not be complete without them."
    exit 1
  fi
  echo "agent-test/.env file does not exist, loading it via Bitwarden"
  load_mcp_agent_env
fi


# --- Python virtual environment setup ---
echo "Create a virtual environment"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

echo  "Activate the python virtual environment"
source .venv/bin/activate

echo "Install dependencies"
pip install -r requirements.txt

echo "Setup completed!"
