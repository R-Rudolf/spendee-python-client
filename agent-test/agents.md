
# Goal

The agent-test mini project shares the virtual environment from it the parent project via the 'spendee-python-client/requirements.txt'.

The goal is to create a chatbot which acts as an MCP client to the Spendee MCP server (spendee-python-client/spendee/spendee_mcp.py).

# Background

The first use case for the spendee-python-client was a discord chatbot via an N8N workflow containing an LLM agent connected to the spendee mcp server.

With this mini project we want to achieve an N8N independent self-contained python project to have both a Local testing environment to verify LLM behaviour with the MCP server, enabling improvements to it in a short iteration manner. An potential benefit could be in the future that an n8n independent discord chatbot could be achieved as well

### The flaw

The N8N's MCP server integration has an "unnecessary" translation layer, which loses important aspects of the schema. With that loss the LLM either throws an error that the function/tool call signature is flawed (claude, gemini) or it guesses (deepseek) the schema, but that results in recurring failure during the MCP server validation.

# Plan

The github repository of the MCP client framework is: https://github.com/lastmile-ai/mcp-agent

First goal: Get a wallet balance with it, using a Gemini flash 2.0 model.

Gemini access is set via the config.yaml file.

Discord integration may be established in a future milestone.


Roadmap:
 1. Make the simplest MCP tool call work (wallet balance)
 2. Create pytest cases for all MCP tool/function and verify them

Further ideation:
 1. Implement Discord integration
  - decide on monolythic or microservice approach (MCP server, Agent, Discord bot)
  - determine interface between agent/discord (channel/history/context handling)
 2. Deploy it as a service
  - logging
  - secret handling
 3. Observability
  - Tracing?
  - LLM token count for cost analysis
  - OpenRouter to try dynamically multiple LLMs


Deployment environment is a Kubernetes cluster. K3D on a homelab server, using Cloudflare tunnel as ingress. Bitwarden is used for secret handling. Secrets are populated into .secret.env files for local debugging and for deployment time secret creation.
