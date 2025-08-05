#!/usr/bin/env python3
"""
Proxy server for connecting Claude Desktop to remote Sensor Tower MCP server
This runs locally via STDIO and forwards requests to the remote HTTP server
"""

from fastmcp import FastMCP

# Create a proxy to your remote server
mcp = FastMCP.as_proxy(
    "https://sensortowermcp.sa.appsflyer.com/mcp/", 
    name="Sensor Tower Remote Proxy"
)

if __name__ == "__main__":
    mcp.run()  # Runs via STDIO for Claude Desktop