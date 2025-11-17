# MCP (Master Control Program)

## High-Level Overview
MCP is the central orchestration component of this project. It is responsible for coordinating data flows between different services.

## Focused Examples
MCP is primarily configured through YAML files. Here's a conceptual example of a task definition:

```yaml
tasks:
  - name: sync-spendee-to-firestore
    source: spendee
    destination: firestore
    schedule: "0 * * * *"
```

---
For implementation details, see `mcp/agents.md`.
