from spendee.spendee_firestore import SpendeeFirestore, MCP_TOOLS

from fastmcp import FastMCP

import pytest
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))


@pytest.fixture(scope="session")
def spendee_mcp_server():
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    
    if not email or not password:
        pytest.fail("EMAIL and PASSWORD environment variables required")
        return None
    
    spendee = SpendeeFirestore(email, password)
    mcp = FastMCP("spendee")

    # Automatically register all MCP tools from the client
    for name, func in MCP_TOOLS.items():
        # Bind the method to the spendee instance if it's a class method
        bound_func = getattr(spendee, name)
        mcp.tool()(bound_func)
    
    return mcp
