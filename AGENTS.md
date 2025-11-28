# Agents Guide (Central)

## Overview
This document provides AI coding assistants with essential context for working with the spendee-python-client project.

**Project Purpose:** This is a Python client for the Spendee personal finance app. The original client was based on an undocumented REST API and has been deprecated. The current implementation uses Google Firestore, which is what the Spendee web application uses. The project is evolving to include an MCP (Multi-Agent Collaboration Protocol) server, which will allow AI agents to interact with the Spendee data for tasks like smart categorization and conversational data exploration.

**Core Components:**
- `SpendeeFirestore` class in `spendee/spendee_firestore.py` - main interface for Spendee data
- `FirebaseClient` class in `spendee/firebase_client.py` - handles authentication
- Methods decorated with `@mcp_tool` are exposed to the MCP server
- See `docs/firestore-schema.md` for Firestore schema information

## Directory-Specific Guides
- [agent-test/AGENTS.md](agent-test/AGENTS.md)
- [docs/AGENTS.md](docs/AGENTS.md)
- [spendee/AGENTS.md](spendee/AGENTS.md)
- [tests/AGENTS.md](tests/AGENTS.md)

## Development Environment Setup
This project uses [mise](https://mise.jdx.dev/) to manage the development environment and leverages python virtual environment by relying on the [requirements.txt](requirements.txt) file. For details how the environment set up works, look into the [setup.sh](setup.sh) file. Even after the setup with mise, you need to activate the python virtual environment as well.

**Setup Steps:**

***Non-interactive shells***
In non-interactive shells, tools managed by `mise` (like `bws`) are not in the PATH and must be executed with the `~/.local/bin/mise x --` prefix.

1. **Ensure wanted code state:**

Check if you are already on a feature branch, if not change to main, then pull, to work with the latest code version.
```bash
    git fetch --all
    git merge origin/main
```

2. **Run the setup script:**
For agents, it populates the .env file using the bitwarden credentials available in the enrivonment.
```bash
   ./setup.sh
```

3. **Activate the virtual environment:**
```bash
   source .venv/bin/activate
```

## Running the Application

**Manual Testing:**
The `run.py` script is used for manual testing and experimentation. You can modify it to call the methods you want to test.
```bash
./run.py
```

**Running the MCP Server:**
The `run-mcp.sh` script is used to run the MCP server. It activates the virtual environment and loads the environment variables from the `.env` file.
The MCP server uses bearer token authentication. The token is sourced from the `MCP_TOKEN` environment variable and should be included in the `Authorization` header of any requests.
```bash
./run-mcp.sh
```

**Debugging the MCP Server:**
The `inspect2.sh` script is used to run the MCP Inspector, a tool for debugging MCP servers. The script will clone the inspector repository and build the docker image if they don't exist.
```bash
./inspect2.sh
```

**Running Tests:**
See [tests/AGENTS.md](tests/AGENTS.md) and [agent-test/AGENTS.md](agent-test/AGENTS.md) for details on running tests.

**Building the MCP Server:**
The project includes a `Dockerfile` to build the MCP server.
```bash
./build.sh
```

This will build a Docker image named `spendee-mcp` and push it to a local registry.

## Secrets Management
We use Bitwarden for managing secrets. To access secrets, you will need the `BWS_ACCESS_TOKEN` environment variable set. You can then use the `bws` CLI to fetch secrets.

**Example: Get a specific secret by key**
```bash
bws secret list | jq -r '.[] | select(.key == "spendee-password") | .value'
```

**Example: List all secret keys**
```bash
bws secret list | jq -r '.[] | .key'
```

***`spendee-password` secret structure***
The `spendee-password` secret has a specific structure:
- The password is the `value` of the secret.
- The email is in the `note` field of the secret.

## Living Documentation
Important: The `AGENTS.md` files are living documentation that should be updated alongside code changes.

When implementing modifications:
*   **Update Relevant Agent Files:** Consider which `AGENTS.md` files need updates when making changes. Avoid adding to the root AGENTS.md file and use dedicated directory related AGENTS.md. Only add the the root, when it is really globally applicable, otherwise just reference there.
*   **Keep Implementation Details Current:** Ensure commands, file paths, and procedures reflect the current state
*   **Maintain Cross-References:** Update links between agent files and documentation
*   **File References Only:** Never quote file content in agent files - only reference files by path
*   **Consistency:** Ensure terminology and patterns remain consistent across all agent files

Even when doing development, testing and troubleshooting, take notes (docs/notes/) at least of the learnings to persist and be recallable later, mentioning them in related docs or AGENTS.md files. But surely high level findings should go to there, not just the links. The goal is to avoid the same mistakes happenning again.

Whatever you would put into "memory", put them into the docs and AGENTS.md files.

## Docs/Agents split policy
*   **Human docs (docs/**):** "What/Why"—architecture, domain flows, decisions, onboarding narratives, high-level troubleshooting flows.
*   **Agents (`AGENTS.md` files):** "How"—exact files to touch, commands, env/secrets guidance, gotchas, safe-change checklists, Cursor-ready prompts.

Each agent file starts with a "Read the overview" links block to the relevant `docs/**` pages.

Each relevant `docs/**` page gets a small footer: "For implementation details, see `<path>/AGENTS.md`".

Reduce code/text duplication as much as possible across twin docs and agents files.

## Guidance on development

### spendee_api.py is deprecated

It is left there if anytime a function would be needed from it, but all development happens on the firebase implementation, just as the core spendee developers did.

### Do not modify login flow or authentication

The authentication in the firebase_client.py is not intuitive, you may used to have more seamless firebase authentication, but THIS WORKS, DO NOT MODIFY. I was not able to make it work using the google.oauth2.credentials, do not try re-implementing that. Maybe because web page flow was only enabled by original authors and service owners, and python SDK based auth flow differs. Maybe because that library is intended for admin API access, not user-client access, I am not an expert in this, but did considerable trial-and-error on that front.

If you face authorization problems, troubleshoot what identities and wallets are used, or you may experiment with new firebase centric functions, but the authentication steps in the login flow should be only modified if user approved or explicitly asked.

### Development Workflow
See [spendee/AGENTS.md](spendee/AGENTS.md) for details on the development workflow.

### Logging

The project uses the `logging` module. A `debug.log` file is created with debug-level logs.

## AI Agent (Google Jules, Claude code, Gemini, Openai codex, etc...)

### Session Start Checklist
- `git fetch --all`
- `git merge origin/main`
- `./setup.sh`
- `source .venv/bin/activate`

### Session End Checklist
- All tests pass without errors.
- All learnings from the development process are documented in either the existing docs, `AGENTS.md`, or a new `docs/session-learnings-<date>-<topic>.md` file.

### Common troubleshooting steps:

Use `.venv/bin/python` instead of normal python if not found.

If `EMAIL` and `PASSWORD` environment variables are missing when running tests (e.g., "Failed: EMAIL and PASSWORD environment variables required"), ensure that the `.env` file exists and is sourced. The `setup.sh` script should create/update it. After running `setup.sh`, execute `source .venv/bin/activate && source .env`.

If .`env` file does not exists, or contains not valid fields (made up, like example, or dummy), delete it and re-execute the `setup.sh`. Never write to it, let only setup.sh populate it.


### In case of multiple problems

When facing repeated problems, challenges, start to write a troubleshooting document detailing all steps and trials, errors you faced, with insights into why you choosed a given resolution path. Only after such document return to the user.
