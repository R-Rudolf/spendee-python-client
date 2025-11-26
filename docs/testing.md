# Testing

## Overview
This project uses a combination of unit tests and integration tests to ensure code quality. We use `pytest` as our primary testing framework.

## MCP Testing
MCP tests are located in the `tests/mcp` directory. These tests focus on verifying the logic of the orchestration tasks.

## Spendee Firestore Testing
Spendee Firestore tests are located in the `tests/spendee` directory. These tests focus on verifying the interaction between the Spendee client and the Firestore database.

## Agent Testing
Agent tests are located in the `agent-test` directory. These tests focus on verifying the end-to-end functionality of the agent, including its interaction with the MCP server.

---
For implementation details, see `tests/agents.md`.
