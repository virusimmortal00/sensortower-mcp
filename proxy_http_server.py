#!/usr/bin/env python3
"""
HTTP Proxy server for connecting Claude Desktop to remote Sensor Tower MCP server
This runs as an HTTP server and forwards requests to the remote HTTP server
"""

from fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.requests import Request

# Create a proxy to your remote server that runs via HTTP
proxy = FastMCP.as_proxy(
    "https://sensortowermcp.sa.appsflyer.com/mcp/", 
    name="Sensor Tower HTTP Proxy"
)

# Add a health endpoint for the proxy
@proxy.custom_route("/health", methods=["GET"])
async def health_endpoint(request: Request) -> JSONResponse:
    """Health check endpoint for the proxy"""
    return JSONResponse({
        "status": "healthy",
        "service": "Sensor Tower HTTP Proxy", 
        "proxy_target": "https://sensortowermcp.sa.appsflyer.com/mcp/",
        "transport": "http"
    })

if __name__ == "__main__":
    # Run the proxy as an HTTP server instead of STDIO
    proxy.run(transport="http", port=8666)