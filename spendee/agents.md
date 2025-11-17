# Spendee Agent Guide

This document provides AI coding assistants with essential context for working with the Spendee client and MCP server.

## Spendee Client

### Key Files
*   **`spendee/spendee_api.py`**: This file contains the original REST API client. It is not actively used but is kept for reference.
*   **`spendee/spendee_firestore.py`**: This is the main file for interacting with Spendee's Firestore backend. It contains the `SpendeeFirestore` class, which is used to perform all data operations.
*   **`spendee/firebase_client.py`**: This file contains the `FirebaseClient` class, which is a generic client for interacting with Firebase services. It is used by `SpendeeFirestore`.
*   **`run.py`**: This is a script for manual testing and experimentation. You can modify this file to test new features or debug existing ones.

### How to Work with the Spendee Client
When working with the Spendee client, you will primarily be interacting with the `SpendeeFirestore` class. Here are some common tasks:
*   **Listing Wallets**: Use the `get_wallets()` method to get a list of all wallets.
*   **Listing Transactions**: Use the `list_transactions()` method to get a list of transactions for a specific wallet.
*   **Editing Transactions**: Use the `edit_transaction()` method to modify a transaction.

For more examples, please refer to the `run.py` script.

## MCP Server

### Key Files
*   **`spendee/spendee_mcp.py`**: This file contains the implementation of the MCP server. It uses the `SpendeeFirestore` class to interact with Spendee.
*   **`run-mcp.sh`**: This script is used to run the MCP server.
*   **`inspect.sh`**: This script is a development script that sets up a Python virtual environment and executes the `spendee_mcp.py` script.
*   **`inspect2.sh`**: This script is used to run the MCP Inspector, which is a tool for debugging MCP servers.

### How to Work with the MCP Server
When working with the MCP server, you will primarily be modifying the `spendee/spendee_mcp.py` file. Here are some common tasks:
*   **Adding New Endpoints**: Add new methods to the `SpendeeMcp` class to expose new functionality.
*   **Modifying Existing Endpoints**: Modify the existing methods in the `SpendeeMcp` class to change their behavior.
*   **Running the Server**: Use the `run-mcp.sh` script to run the MCP server.
*   **Debugging the Server**: Use the `inspect2.sh` script to run the MCP Inspector and debug the server.
