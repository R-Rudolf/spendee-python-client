#!/usr/bin/env python3
"""
Simple MCP server that returns Alice's favorite food.

To run:
    python alice_mcp.py

To test:
    mcp dev alice_mcp.py
"""

import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("alice-food", host="0.0.0.0", port=8000, transport="http")


@mcp.tool()
def get_alices_favorite_food() -> str:
    """Get Alice's favorite food."""
    return "macaron"


if __name__ == "__main__":
    logger.info("Starting Alice's MCP Server")
    logger.info("Access the server at http://0.0.0.0:8000")
    mcp.run()
