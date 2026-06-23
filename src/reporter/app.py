import os
from fastmcp import FastMCP

from reporter.instructions import load_server_instructions
from fastmcp.server.transforms.search import BM25SearchTransform

from reporter.tools import register_tools
from reporter.prompts import register_prompts
from reporter.routes import register_routes

# Initialize FastMCP server
mcp = FastMCP(
    "reporter",
    instructions=load_server_instructions(),
    transforms=[BM25SearchTransform()],
)

# Register custom tools
register_tools(mcp)

# Register custom prompts
register_prompts(mcp)

# Register custom routes
register_routes(mcp)

if __name__ == "__main__":
    # When run directly, check for a platform port env var.
    # If found, start an HTTP server (useful for Databricks local testing).
    # Otherwise fall back to stdio for local MCP clients (Claude Desktop, etc.).
    port_env = os.getenv("DATABRICKS_APP_PORT") or os.getenv("PORT")
    if port_env:
        mcp.run(transport="http", host="0.0.0.0", port=int(port_env))
    else:
        mcp.run(transport="stdio")




