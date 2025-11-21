
import os
import logging
import contextlib
import uvicorn
import hashlib
import secrets

from mcp.server.fastmcp import FastMCP
#from fastmcp import FastMCP
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.sse import SseServerTransport

from fastapi import FastAPI, HTTPException, Request

from starlette.routing import Route, Mount
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope, Receive, Send

from spendee.spendee_firestore import SpendeeFirestore, MCP_TOOLS


# to start (after .venv setup):
#   python spendee/spendee_mcp.py

# to test:
#   mcp dev spendee/spendee_mcp.py
# Then on the url: http://localhost:6274/
# setup for "Transport Type": "Streamable HTTP"
#    "Server URL" to "http://localhost:8000/mcp"
# setup for "Transport Type": "SSE"
#    "Server URL" to "http://localhost:8000/sse"


DEBUG_MODE = os.environ.get("DEBUG_MODE", "") != ""

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def run(email=None, password=None, port=8000, accepted_token="spendee-token", transfer_mode="sse"):
    
    if transfer_mode not in ["sse", "streamable-http"]:
        raise ValueError("TRANSFER_MODE must be either 'sse' or 'streamable-http'")

    if not email or not password:
        raise ValueError('Please set EMAIL and PASSWORD as an ENV variable.')

    mcp = FastMCP("spendee", host="0.0.0.0", port=port)

    spendee = SpendeeFirestore(EMAIL, PASSWORD)

    # Automatically register all MCP tools from the client
    for name, func in MCP_TOOLS.items():
        # Bind the method to the spendee instance if it's a class method
        bound_func = getattr(spendee, name)
        mcp.tool()(bound_func)
    
    async def check_bearer_auth(request, error_response=None):
        if accepted_token == "disabled":
            logger.info("Bearer token authentication is disabled.")
            return None

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
        if token != accepted_token:
            logger.warning("Invalid token.")
            if error_response:
                return await error_response("Invalid token.", 401)
            raise HTTPException(401, "Invalid token.")
        return None

    logger.info("Starting Spendee MCP Server")
    # I failed to unify both transfer modes, because of some lifecycle issues
    if transfer_mode == "streamable-http":
        logger.info("Using Streamable HTTP transport")
        streaming_server(mcp, port, check_bearer_auth)
    else:
        logger.info("Using SSE transport")
        sse_server(mcp, port, check_bearer_auth)

# Authentication middleware and server setup

def debug_secret(secret, name):
    salt = secrets.token_hex(5)
    token_hash = hashlib.sha256((salt + secret).encode()).hexdigest()
    logger.debug(f"sha256('{salt}' + token): {token_hash}")
    logger.debug(f"You can verify with: echo -n \"{salt}${name}\" | sha256sum")


def streaming_server(mcp, port, check_bearer_auth):
    # maybe this would be simpler: https://gofastmcp.com/deployment/self-hosted#environment-variables
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

    logger.info(f"Starting Spendee MCP Server with Bearer Token Authentication on port {port}")
    logger.info(f"Access the MCP endpoint at http://0.0.0.0:{port}/mcp")
    uvicorn.run(app, host="0.0.0.0", port=port)


def sse_server(mcp, port, check_bearer_auth):
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
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    ACCEPTED_TOKEN = os.environ.get("MCP_TOKEN", "spendee-token")
    PORT = int(os.environ.get("MCP_PORT", 8000))
    TRANSFER_MODE = os.environ.get("TRANSFER_MODE", "sse").lower()

    run(email=EMAIL, password=PASSWORD, port=PORT, accepted_token=ACCEPTED_TOKEN, transfer_mode=TRANSFER_MODE)
