# MCP Agent Guide

This document provides AI coding assistants with essential context for working with the MCP server.

## Key Files
*   **`spendee/spendee_mcp.py`**: This file contains the implementation of the MCP server. It uses the `SpendeeFirestore` class to interact with Spendee.
*   **`run-mcp.sh`**: This script is used to run the MCP server.
*   **`inspect.sh`**: This script is a development script that sets up a Python virtual environment and executes the `spendee_mcp.py` script.
*   **`inspect2.sh`**: This script is used to run the MCP Inspector, which is a tool for debugging MCP servers.

## How to Work with the MCP Server
When working with the MCP server, you will primarily be modifying the `spendee/spendee_mcp.py` file. Here are some common tasks:
*   **Adding New Endpoints**: Add new methods to the `SpendeeMcp` class to expose new functionality.
*   **Modifying Existing Endpoints**: Modify the existing methods in the `SpendeeMcp` class to change their behavior.
*   **Running the Server**: Use the `run-mcp.sh` script to run the MCP server.
*   **Debugging the Server**: Use the `inspect2.sh` script to run the MCP Inspector and debug the server.
