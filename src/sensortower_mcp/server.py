#!/usr/bin/env python3
"""
Main server module for Sensor Tower MCP Server
"""

import sys
import asyncio
import httpx
from fastmcp import FastMCP
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

# Global variables for deferred initialization
sensor_tower_client = None

class SensorTowerMCPServer:
    """Main MCP Server class for Sensor Tower"""
    
    def __init__(self):
        self.args = parse_args()
        self.mcp = FastMCP("Sensor Tower")
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
        
        # Add HTTP health check endpoint
        self.add_health_endpoint()
        
        self.tools_registered = True
    
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