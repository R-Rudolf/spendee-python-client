# Agents Guide (Central)

## Overview
This document provides AI coding assistants with essential context for working with the spendee-python-client project.

## Development Environment Setup
This project uses [mise](https://mise.jdx.dev/) to manage the development environment and leverages python virtual environment by relying on the [requirements.txt](requirements.txt) file. For details how the environment set up works, look into the [setup.sh](setup.sh) file. Even after the setup with mise, you need to activate the python virtual environment as well.

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

## Jules Agent

### Session Start Checklist
- `git pull origin main`
- `./setup.sh`
- `source .venv/bin/activate`

### Session End Checklist
- All tests pass without errors.
- All learnings from the development process are documented in either the existing docs, `AGENTS.md`, or a new `docs/session-learnings-<date>-<topic>.md` file.

### In case of trouble

When facing repeated problems, challenges, start to write a troubleshooting document detailing all steps and trials, errors you faced, with insights into why you choosed a given resolution path. Only after such document return to the user.
