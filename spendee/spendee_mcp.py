from mcp.server.fastmcp import FastMCP
import logging

# to start (after .venv setup):
# python spendee/spendee_mcp.py

# to test:
# DANGEROUSLY_OMIT_AUTH=true mcp dev spendee/spendee_mcp.py
# Then on the url: http://localhost:6274/
# setup "Transport Type" to "Streamable HTTP"
# and "Server URL" to "http://localhost:8000/mcp"

logging.basicConfig(level=logging.DEBUG)
mcp = FastMCP("spendee", host="0.0.0.0", port=8000)

@mcp.tool()
def get_wallets():
    # Hardcoded example wallets
    example_wallets = [
        {"id": 1, "name": "Main Account", "currency": "USD", "balance": 1234.56},
        {"id": 2, "name": "Savings", "currency": "EUR", "balance": 7890.12},
    ]
    return example_wallets

if __name__ == "__main__":
    mcp.run(transport="streamable-http")

# relevant URLs for learning:
# - https://modelcontextprotocol.io/specification/2025-06-18/server/tools
# - https://www.aibootcamp.dev/blog/remote-mcp-servers
# - https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_configuration-format
# - https://docs.anthropic.com/en/docs/claude-code/mcp
# - https://modelcontextprotocol.io/docs/tools/debugging
# - https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#session-management
# - https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#authentication
