import os
from fastmcp import FastMCP
from fastmcp.server.transforms.search import BM25SearchTransform
from reporter.tools import register_tools
from reporter.prompts import register_prompts
from reporter.routes import register_routes

# Initialize FastMCP server
mcp = FastMCP("reporter")

# Register custom tools
register_tools(mcp)
mcp.add_transform(BM25SearchTransform())

# Register custom prompts
register_prompts(mcp)

# Register custom routes
register_routes(mcp)

# ASGI app for HTTP deployments — imported by uvicorn in all remote environments:
#   cloud.gov:  Procfile/manifest.yaml  →  uvicorn ... --port $PORT
#   Databricks: app.yaml               →  uvicorn ... --port $DATABRICKS_APP_PORT
app = mcp.http_app(stateless_http=True)


if __name__ == "__main__":
    # When run directly, check for a platform port env var.
    # If found, start an HTTP server (useful for Databricks local testing).
    # Otherwise fall back to stdio for local MCP clients (Claude Desktop, etc.).
    port_env = os.getenv("DATABRICKS_APP_PORT") or os.getenv("PORT")
    if port_env:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(port_env))
    else:
        mcp.run(transport="stdio")




