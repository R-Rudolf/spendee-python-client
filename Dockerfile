# syntax=docker/dockerfile:1
FROM python:3.11-slim

# example call to run the container:
# docker run --rm -it -p 8000:8000 spendee-mcp

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Entrypoint for MCP server (mock get_wallets, ready for spendee_firestore)
CMD ["python", "/app/spendee/spendee_mcp.py"]
