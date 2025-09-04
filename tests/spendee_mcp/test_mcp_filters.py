import pytest
from fastmcp import Client

@pytest.mark.asyncio
async def test_mcp_transaction_list(spendee_mcp_server):
    async with Client(spendee_mcp_server) as client:
        result = await client.call_tool("aggregate_transactions", \
            {
                "wallet_id": "b368c5c2-68fe-4f98-9d4f-08e0cdca57a7", \
                "start": "2025-08-01T00:00:00Z", \
                "end": '2025-08-31T23:59:59Z', \
                "filters": {"labels__contains": "szigetspicc"}, \
            }
        )

        assert not result.is_error
        total = result.data
        assert isinstance(total, float)
        assert total > -80000
        assert total < -5000
