#!/usr/bin/env python3
"""
Main server module for Sensor Tower MCP Server
"""

import sys
from fastmcp import FastMCP
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import (
    parse_args, validate_token, create_http_client, 
    print_startup_info, print_token_error, get_auth_token
)
from .tools import (
    AppAnalysisTools, StoreMarketingTools, MarketAnalysisTools,
    YourMetricsTools, SearchDiscoveryTools, UtilityTools
)
from .documentation import register_documentation
from .prompts import register_prompts

# Global variables for deferred initialization
sensor_tower_client = None

class SensorTowerMCPServer:
    """Main MCP Server class for Sensor Tower"""
    
    def __init__(self):
        self.args = parse_args()
        self.mcp = FastMCP(
            "Sensor Tower",
            on_duplicate_tools="error",
            mask_error_details=True,
        )
        self.client = None
        self.tools_registered = False
        
    def setup_client(self):
        """Initialize HTTP client and validate token"""
        if not validate_token(self.args.token):
            print_token_error()
            sys.exit(1)
            
        token = get_auth_token(self.args.token)
        self.client = create_http_client(token)
        
        # Set global client for backward compatibility
        global sensor_tower_client
        sensor_tower_client = self.client
        
        return token
    
    def register_all_tools(self, token: str):
        """Register all MCP tools and resources"""
        if self.tools_registered:
            return
            
        # Initialize all tool classes
        app_analysis = AppAnalysisTools(self.client, token)
        store_marketing = StoreMarketingTools(self.client, token)
        market_analysis = MarketAnalysisTools(self.client, token)
        your_metrics = YourMetricsTools(self.client, token)
        search_discovery = SearchDiscoveryTools(self.client, token)
        utilities = UtilityTools()
        
        # Register tools with FastMCP
        app_analysis.register_tools(self.mcp)
        store_marketing.register_tools(self.mcp)
        market_analysis.register_tools(self.mcp)
        your_metrics.register_tools(self.mcp)
        search_discovery.register_tools(self.mcp)
        utilities.register_tools(self.mcp)
        
        # Register documentation resources
        register_documentation(self.mcp)
        # Register prompt templates
        register_prompts(self.mcp)

        # Add HTTP health check endpoint
        self.add_health_endpoint()
        self.add_json_tool_endpoint()

        # Fix FastMCP HTTP transport parameter validation bug
        if self.args.transport == "http":
            self.patch_fastmcp_http_transport()
        
        self.tools_registered = True
    
    def patch_fastmcp_http_transport(self):
        """Add middleware to fix Claude Desktop Accept header compatibility"""
        # FastMCP 2.11.1 HTTP transport is too strict about Accept headers
        # This middleware fixes the issue before requests reach FastMCP
        
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.requests import Request
        
        class ClaudeDesktopFixMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # Only process MCP endpoint requests (e.g. /mcp, /mcp/tools/invoke)
                if request.url.path.startswith('/mcp'):
                    # Fix Accept header for Claude Desktop compatibility
                    headers = dict(request.headers)
                    accept_header = headers.get('accept', '')
                    
                    # If clients only send application/json (or */*) add text/event-stream
                    if accept_header in {'application/json', '*/*', ''}:
                        # Create new headers with both mime types
                        new_headers = []
                        accept_set = False
                        for name, value in request.headers.items():
                            if name.lower() == 'accept':
                                new_headers.append((name.encode(), b"application/json, text/event-stream"))
                                accept_set = True
                            else:
                                new_headers.append((name.encode(), value.encode()))
                        
                        if not accept_set:
                            new_headers.append((b"accept", b"application/json, text/event-stream"))

                        # Create new scope with fixed headers
                        scope = request.scope.copy()
                        scope['headers'] = new_headers
                        
                        # Create new request with fixed headers
                        from starlette.requests import Request as NewRequest
                        fixed_request = NewRequest(scope, request.receive)
                        
                        return await call_next(fixed_request)
                
                return await call_next(request)
        
        # Add the middleware to FastMCP's FastAPI app
        if hasattr(self.mcp, '_app'):
            self.mcp._app.add_middleware(ClaudeDesktopFixMiddleware)
            try:
                from starlette.middleware.cors import CORSMiddleware
                self.mcp._app.add_middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_methods=["*"],
                    allow_headers=["*"]
                )
            except Exception:
                # CORS is best-effort and only relevant for browser-based callers
                pass

    def add_health_endpoint(self):
        """Add HTTP health check endpoint"""
        @self.mcp.custom_route("/health", methods=["GET"])
        async def health_endpoint(request: Request) -> JSONResponse:
            """HTTP health check endpoint"""
            from .config import API_BASE_URL
            return JSONResponse({
                "status": "healthy",
                "service": "Sensor Tower MCP Server", 
                "transport": self.args.transport,
                "api_base_url": API_BASE_URL,
                "tools_available": 40
            })

    def add_json_tool_endpoint(self):
        """Add legacy JSON endpoint that bypasses JSON-RPC session handling."""

        from fastmcp.exceptions import NotFoundError

        @self.mcp.custom_route("/legacy/tools/invoke", methods=["POST"])
        async def invoke_tool(request: Request) -> JSONResponse:
            payload = await request.json()
            tool_name = payload.get("tool")
            arguments = payload.get("arguments") or {}

            if not isinstance(tool_name, str):
                raise HTTPException(status_code=400, detail="Missing or invalid tool name")
            if not isinstance(arguments, dict):
                raise HTTPException(status_code=400, detail="Tool arguments must be an object")

            try:
                tool = await self.mcp.get_tool(tool_name)
            except NotFoundError as exc:  # pragma: no cover - runtime check
                raise HTTPException(status_code=404, detail=str(exc)) from exc

            try:
                result = await tool.run(arguments)
            except Exception as exc:  # pragma: no cover - runtime failure
                raise HTTPException(status_code=500, detail=f"Tool execution failed: {exc}") from exc

            structured = getattr(result, "structured_content", None)
            if structured is None:
                content = getattr(result, "content", [])

                def serialize(block):
                    if hasattr(block, "model_dump"):
                        return block.model_dump(mode="json")
                    return block

                structured = [serialize(block) for block in content]

            response_body = {
                "tool": tool_name,
                "result": structured,
            }

            return JSONResponse(response_body)
    
    async def run_async(self):
        """Run server in async mode"""
        # Setup client and register tools
        token = self.setup_client()
        self.register_all_tools(token)
        
        # Display startup information
        print_startup_info(self.args, 40)
        
        try:
            if self.args.transport == "stdio":
                # Run in stdio mode for MCP clients
                await self.mcp.run_async()
            elif self.args.transport == "http":
                # Run in HTTP mode using FastMCP's built-in HTTP server
                print(f"🌐 Starting HTTP server on http://localhost:{self.args.port}")
                print(f"🔍 Health check: http://localhost:{self.args.port}/health")
                
                await self.mcp.run_async(
                    transport="http",
                    host="0.0.0.0",
                    port=self.args.port
                )
        except KeyboardInterrupt:
            print("\n👋 Shutting down Sensor Tower MCP Server")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
    
    def run_sync(self):
        """Run server in sync mode"""
        # Setup client and register tools
        token = self.setup_client()
        self.register_all_tools(token)
        
        # Display startup information
        print_startup_info(self.args, 40)
        
        try:
            if self.args.transport == "stdio":
                # Run in stdio mode for MCP clients - use synchronous run
                self.mcp.run()
            else:
                # For HTTP mode, use FastMCP's built-in HTTP server
                print(f"🌐 Starting HTTP server on http://localhost:{self.args.port}")
                print(f"🔍 Health check: http://localhost:{self.args.port}/health")
                
                self.mcp.run(
                    transport="http",
                    host="0.0.0.0",
                    port=self.args.port
                )
        except KeyboardInterrupt:
            print("\n👋 Shutting down Sensor Tower MCP Server")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)

# Main entry points
async def main():
    """Main async entry point"""
    server = SensorTowerMCPServer()
    await server.run_async()

def cli():
    """CLI entry point for uvx/pip install"""
    server = SensorTowerMCPServer()
    server.run_sync()

if __name__ == "__main__":
    cli()
