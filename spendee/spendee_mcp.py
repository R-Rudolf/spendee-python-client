
import os
import logging
import contextlib
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

# to start (after .venv setup):
#   python spendee/spendee_mcp.py

# to test:
#   mcp dev spendee/spendee_mcp.py
# Then on the url: http://localhost:6274/
# setup "Transport Type" to "Streamable HTTP"
# and "Server URL" to "http://localhost:8000/mcp"

ACCEPTED_TOKEN = os.environ.get("MCP_TOKEN", "spendee-token")
PORT = int(os.environ.get("MCP_PORT", 8000))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "") != ""
DISABLE_AUTH = os.environ.get("DISABLE_AUTH", "") != ""

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


# def server_with_authentication():
#     session_manager = StreamableHTTPSessionManager(
#         app=mcp._mcp_server,  # Use the underlying MCPServer instance
#     )

#     async def auth_middleware(scope, receive, send):
#         request = Request(scope, receive)
#         # Log request method, url, and headers for troubleshooting
#         if DEBUG_MODE:
#             logger.debug(f"Incoming request: method={request.method}, url={request.url}")
#             logger.debug(f"Request headers: {dict(request.headers)}")

#         auth_header = request.headers.get("authorization")

#         if not auth_header or not auth_header.lower().startswith("bearer "):
#             logger.warning("Missing or invalid Authorization header.")
#             raise HTTPException(401, "Missing or invalid Authorization header.")

#         token = auth_header.split(" ", 1)[1]
#         if token != ACCEPTED_TOKEN:
#             logger.warning("Invalid or expired token.")
#             raise HTTPException(401, "Invalid or expired token.")

#         await session_manager.handle_request(scope, receive, send)

#     @contextlib.asynccontextmanager
#     async def lifespan(app: FastAPI):
#         async with session_manager.run():
#             logger.info("StreamableHTTPSessionManager started.")
#             yield
#             logger.info("StreamableHTTPSessionManager stopped.")

#     app = FastAPI(lifespan=lifespan)
#     app.mount("/mcp", auth_middleware)

#     logger.info(f"Starting Spendee MCP Server with Bearer Token Authentication on port {PORT}")
#     logger.info(f"Access the MCP endpoint at http://0.0.0.0:{PORT}/mcp")
#     uvicorn.run(app, host="0.0.0.0", port=PORT)

def server_with_sse():
    app = FastAPI()
    @app.get("/")
    def read_root():
        return {"Hello": "World"}
    #from app.sse import create_sse_server
    app.mount("/", app.sse.create_sse_server(mcp))

if __name__ == "__main__":
    logger.info("Starting Spendee MCP Server as SSE without authentication")
    mcp.run(transport="sse") # for n8n compatibility, authentication implemented on cloudflare level
    #server_with_sse()

    # if DISABLE_AUTH:
    #     logger.warning("Running without authentication! This is insecure and should only be used for local testing.")
    #     #mcp.run(transport="streamable-http")
    #     mcp.run(transport="sse")
    # else:
    #     server_with_authentication()


# relevant URLs for learning:
# - https://modelcontextprotocol.io/specification/2025-06-18/server/tools
# - https://www.aibootcamp.dev/blog/remote-mcp-servers
# - https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_configuration-format
# - https://docs.anthropic.com/en/docs/claude-code/mcp
# - https://modelcontextprotocol.io/docs/tools/debugging
# - https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#session-management
# - https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#authentication
# - auth inspiration: https://github.com/zahere-dev/mcp-labs/tree/main
