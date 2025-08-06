#!/usr/bin/env python3
"""
HTTP Proxy server for connecting Claude Desktop to remote Sensor Tower MCP server
This runs as an HTTP server and forwards requests to the remote HTTP server
"""

import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.requests import Request
from starlette.routing import Route
import uvicorn

# Define the upstream server (internal Docker hostname)
UPSTREAM_URL = "http://sensortowermcp:8666/mcp/"

async def health_endpoint(request: Request) -> JSONResponse:
    """Health check endpoint for the proxy"""
    return JSONResponse({
        "status": "healthy",
        "service": "Sensor Tower HTTP Proxy", 
        "proxy_target": UPSTREAM_URL,
        "transport": "http"
    })

async def proxy_mcp(request: Request) -> StreamingResponse:
    """Proxy MCP requests with fixed Accept headers"""
    
    # Get the original headers and fix the Accept header
    headers = dict(request.headers)
    
    # If only application/json is present, add text/event-stream
    accept_header = headers.get("accept", "")
    if "application/json" in accept_header and "text/event-stream" not in accept_header:
        headers["accept"] = "application/json, text/event-stream"
    
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    # Get request body
    body = await request.body()
    
    # Get the path after /mcp/
    path = request.path_params.get('path', '')
    
    # Forward the request to upstream with timeout handling
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            upstream_response = await client.request(
                method=request.method,
                url=f"{UPSTREAM_URL}{path}",
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # Return the response as a stream
            return StreamingResponse(
                iter([upstream_response.content]),
                status_code=upstream_response.status_code,
                headers=dict(upstream_response.headers),
                media_type=upstream_response.headers.get("content-type")
            )
    except httpx.ConnectTimeout:
        return JSONResponse(
            {"error": "Upstream server connection timeout", "upstream": UPSTREAM_URL},
            status_code=502
        )
    except httpx.RequestError as e:
        return JSONResponse(
            {"error": f"Upstream server error: {str(e)}", "upstream": UPSTREAM_URL},
            status_code=502
        )

# Create Starlette app
routes = [
    Route("/health", health_endpoint, methods=["GET"]),
    Route("/mcp/", proxy_mcp, methods=["GET", "POST", "PUT", "DELETE", "PATCH"]),
    Route("/mcp/{path:path}", proxy_mcp, methods=["GET", "POST", "PUT", "DELETE", "PATCH"]),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    # Run the proxy as an HTTP server
    uvicorn.run(app, host="0.0.0.0", port=8666)