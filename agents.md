# Agents Guide (Central)

## Overview
This document provides AI coding assistants with essential context for working with the spendee-python-client project.

## Development Environment Setup
Please refer to the README.md for instructions on setting up the development environment.

## Secrets Management
We use Bitwarden for managing secrets. To access secrets, you will need the `BWS_ACCESS_TOKEN` environment variable set (possibly already set). You can then use the `bws` CLI to fetch secrets.
Sometimes the 'note' field contains useful information about the secret, how to use it, or for which account/project it belongs to.
,
**Example: Get a specific secret by key**
```bash
bws secret list | jq -r '.[] | select(.key == "spendee-password") | .value'
```

**Example: List all secret keys**
```bash
bws secret list | jq -r '.[] | .key'
```

## Living Documentation
Important: The `agents.md` files are living documentation that should be updated alongside code changes. When implementing modifications:

*   **Update Relevant Agent Files:** Consider which `agents.md` files need updates when making changes. Avoid adding to the root agents.md file and use dedicated directory related agents.md. Only add the the root, when it is really globally applicable, otherwise just reference there.
*   **Keep Implementation Details Current:** Ensure commands, file paths, and procedures reflect the current state
*   **Maintain Cross-References:** Update links between agent files and documentation
*   **File References Only:** Never quote file content in agent files - only reference files by path
*   **Consistency:** Ensure terminology and patterns remain consistent across all agent files

## Docs/Agents split policy
*   **Human docs (docs/**):** "What/Why"—architecture, domain flows, decisions, onboarding narratives, high-level troubleshooting flows.
*   **Agents (`agents.md` files):** "How"—exact files to touch, commands, env/secrets guidance, gotchas, safe-change checklists, Cursor-ready prompts.

Each agent file starts with a "Read the overview" links block to the relevant `docs/**` pages.

Each relevant `docs/**` page gets a small footer: "For implementation details, see `<path>/agents.md`".

Reduce code/text duplication as much as possible across twin docs and agents files.

# Subordinate pages

Update this file if new agents.md is created.

Currently there are no further agents.md's in this project.
