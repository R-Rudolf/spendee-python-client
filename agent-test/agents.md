The agent-test mini project (dev-projects/spendee-python-client/agent-test) is part of the spendee-python-client.
It shares the virtual environment from it (dev-projects/spendee-python-client/requirements.txt, dev-projects/spendee-python-client/.venv, python 3.22).

The goal is to create a chatbot which acts as an MCP client to the Spendee MCP server (dev-projects/spendee-python-client/spendee/spendee_mcp.py).

For this first use-case it will be integrated to a Discord channel.

There is an existing n8n workflow which solves this, but that has unnecessary conversations in between the MCP server and the LLM API endpoint.
With this mini project we want to achieve an N8N independent self-contained python project to have both a Discord chatbot and a Local testing environment to verify LLM behaviour with the MCP server, enabling improvements to it in a short iteration manner.

The github repository of the MCP client framework is: https://github.com/lastmile-ai/mcp-agent

First goal: Get the Rafi wallet's balance with it, using a Gemini flash 2.0 model.

Gemini access is set via the config.yaml file.

Discord integration will be established in a future milestone.


Roadmap:
 1. Make the simplest MCP tool call work (Rafi wallet's balance)
 2. Create pytest cases for all MCP tool/function and verify them
 3. Implement Discord integration
  - decide on monolythic or microservice approach (MCP server, Agent, Discord bot)
  - determine interface between agent/discord (channel/history/context handling)
 4. Deploy it as a service
  - logging
  - secret handling
 5. Optional
  - Tracing?
  - LLM token count for cost analysis
  - OpenRouter to try dynamically multiple LLMs


Deployment environment is a Kubernetes cluster. K3D on a homelab server, using Cloudflare tunnel as ingress. Bitwarden is used for secret handling. Secrets are populated into .secret.env files for local debugging and for deployment time secret creation.
