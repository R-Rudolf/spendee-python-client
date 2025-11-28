# Agent-Based Testing Guide

For general setup and project overview, see the [root AGENTS.md](../AGENTS.md).

## Running Agent-Based Tests

The agent-based tests are located in the `agent-test/` directory.

You can run them using `pytest`:
```bash
# For agent based MCP testing
.venv/bin/python -m pytest agent-test/ -v --tb=short
```

## Testing LLMs
When writing tests for services like LLMs, do not use mocks. Tests should rely on real API calls.
When testing non-deterministic LLM responses, if a specific term is required for an assertion, make the test prompt more specific to guide the LLM into using that term, which makes the test more reliable.
