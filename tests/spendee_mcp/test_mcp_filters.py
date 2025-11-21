import pytest
from fastmcp import Client

@pytest.mark.asyncio
async def test_mcp_transaction_list(spendee_mcp_server):
    async with Client(spendee_mcp_server) as client:
        result = await client.call_tool("aggregate_transactions", \
            {
                "wallet_id": "5668018f-2c8d-41b0-9ef9-fbaa6518891d", \
                "start": "2025-11-17T00:00:00Z", \
                "end": '2025-11-17T23:59:59Z', \
                "filters": {"labels__contains": "Coffee ☕"}, \
            }
        )

        assert not result.is_error
        total = result.data
        assert isinstance(total, float)
        assert total == -4.0
