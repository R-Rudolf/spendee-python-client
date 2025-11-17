# MCP (Model Context Protocol)

## High-Level Overview
MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems. Think of it like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect electronic devices, MCP provides a standardized way to connect AI applications to external systems like data sources, tools, and workflows.

## Key Concepts
*   **Servers:** Expose data and tools to AI applications.
*   **Clients:** Connect to MCP servers to access data and tools.
*   **Transports:** The underlying communication mechanism between clients and servers.

## MCP Inspector
The [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) is an interactive developer tool for testing and debugging MCP servers. It allows you to:
*   Inspect available resources, prompts, and tools.
*   Test prompt generation and tool execution.
*   View server logs and notifications.

The `inspect2.sh` script in this repository is designed to help you run the MCP Inspector.

## Further Reading
For a deeper understanding of MCP, please refer to the [official documentation](https://modelcontextprotocol.io/docs/getting-started/intro).

---
For implementation details, see `mcp/agents.md`.
