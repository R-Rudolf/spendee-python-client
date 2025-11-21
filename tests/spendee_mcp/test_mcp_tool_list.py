import pytest
from fastmcp import Client

@pytest.mark.asyncio
async def test_mcp_tool_list(spendee_mcp_server):
    """
    Test that the MCP server has the expected tools registered.
    """
    async with Client(spendee_mcp_server) as client:
        assert len(await client.list_tools()) > 0
