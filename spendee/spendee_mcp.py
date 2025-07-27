
import os
import logging
import contextlib
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.routing import Route, Mount
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope, Receive, Send
from mcp.server.sse import SseServerTransport
import hashlib
import secrets

# to start (after .venv setup):
#   python spendee/spendee_mcp.py

# to test:
#   mcp dev spendee/spendee_mcp.py
# Then on the url: http://localhost:6274/
# setup for "Transport Type": "Streamable HTTP"
#    "Server URL" to "http://localhost:8000/mcp"
# setup for "Transport Type": "SSE"
#    "Server URL" to "http://localhost:8000/sse"

ACCEPTED_TOKEN = os.environ.get("MCP_TOKEN", "spendee-token")
PORT = int(os.environ.get("MCP_PORT", 8000))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "") != ""
TRANSFER_MODE = os.environ.get("TRANSFER_MODE", "sse").lower()

if TRANSFER_MODE not in ["sse", "streamable-http"]:
    raise ValueError("TRANSFER_MODE must be either 'sse' or 'streamable-http'")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mcp = FastMCP("spendee", host="0.0.0.0", port=PORT)

@mcp.tool()
def get_wallets():
    # Hardcoded example wallets
    return [
        {"id": 1, "name": "Main Account", "currency": "USD", "balance": 1234.56},
        {"id": 2, "name": "Savings", "currency": "EUR", "balance": 7890.12},
    ]

# Authentication middleware and server setup

async def check_bearer_auth(request, error_response=None):
    if DEBUG_MODE:
        logger.debug(f"Incoming request: method={request.method}, url={request.url}")
        logger.debug(f"Request headers: {dict(request.headers)}")

    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        logger.warning("Missing or invalid Authorization header.")
        if error_response:
            return await error_response("Missing or invalid Authorization header.", 401)
        raise HTTPException(401, "Missing or invalid Authorization header.")

    token = auth_header.split(" ", 1)[1]
    if token != ACCEPTED_TOKEN:
        logger.warning("Invalid token.")
        logger.debug(f"Expected token: '{ACCEPTED_TOKEN}', received token: '{token}'")
        if error_response:
            return await error_response("Invalid token.", 401)
        raise HTTPException(401, "Invalid token.")
    return None


def streaming_server():
    session_manager = StreamableHTTPSessionManager(
        app=mcp._mcp_server,
    )

    async def auth_middleware(scope, receive, send):
        request = Request(scope, receive)
        err = await check_bearer_auth(request)
        if err:
            return
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        async with session_manager.run():
            logger.info("StreamableHTTPSessionManager started.")
            yield
            logger.info("StreamableHTTPSessionManager stopped.")

    app = FastAPI(lifespan=lifespan)
    app.mount("/mcp", auth_middleware)

    logger.info(f"Starting Spendee MCP Server with Bearer Token Authentication on port {PORT}")
    logger.info(f"Access the MCP endpoint at http://0.0.0.0:{PORT}/mcp")
    uvicorn.run(app, host="0.0.0.0", port=PORT)


def sse_server():
    sse_transport = SseServerTransport("/messages/")

    async def error_response(msg, status):
        response = Response(msg, status_code=status)
        async def responder(scope, receive, send):
            await response(scope, receive, send)
        return responder

    async def handle_sse(request):
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp._mcp_server.run(streams[0], streams[1], mcp._mcp_server.create_initialization_options())
        return Response()

    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]
    starlette_sse_app = Starlette(routes=routes)

    async def sse_auth_middleware(scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive)
        err = await check_bearer_auth(request, error_response)
        if err:
            await err(scope, receive, send)
            return

        await starlette_sse_app(scope, receive, send)

    app = Starlette(
        routes=[
            Mount("/", sse_auth_middleware),
        ],
    )
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    logger.info("Starting Spendee MCP Server")
    salt = secrets.token_hex(5)
    token_hash = hashlib.sha256((salt + ACCEPTED_TOKEN).encode()).hexdigest()
    logger.debug(f"sha256('{salt}' + token): {token_hash}")
    logger.debug(f"You can verify with: echo -n \"{salt}$MCP_TOKEN\" | sha256sum")

    # I failed to unify both transfer modes, because of some lifecycle issues
    if TRANSFER_MODE == "streamable-http":
        logger.info("Using Streamable HTTP transport")
        streaming_server()
    else:
        logger.info("Using SSE transport")
        sse_server()


# relevant URLs for learning:
# - https://modelcontextprotocol.io/specification/2025-06-18/server/tools
# - https://www.aibootcamp.dev/blog/remote-mcp-servers
# - https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_configuration-format
# - https://docs.anthropic.com/en/docs/claude-code/mcp
# - https://modelcontextprotocol.io/docs/tools/debugging
# - https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#session-management
# - https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#authentication
# - auth inspiration: https://github.com/zahere-dev/mcp-labs/tree/main
