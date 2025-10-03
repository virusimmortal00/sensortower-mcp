#!/usr/bin/env python3
"""
Configuration and setup for Sensor Tower MCP Server
"""

import argparse
import os
import httpx
from typing import Optional

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Base configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.sensortower.com")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Sensor Tower MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=os.getenv("TRANSPORT", "stdio"),
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8666")),
        help="HTTP server port (default: 8666)"
    )
    parser.add_argument(
        "--token",
        default=os.getenv("SENSOR_TOWER_API_TOKEN"),
        help="Sensor Tower API token"
    )
    return parser.parse_args()

def get_auth_token(token: Optional[str] = None) -> str:
    """Get authentication token for Sensor Tower API"""
    auth_token = token or os.getenv("SENSOR_TOWER_API_TOKEN")
    if not auth_token:
        raise ValueError("SENSOR_TOWER_API_TOKEN environment variable or --token argument is required")
    return auth_token

def create_http_client(token: str) -> httpx.AsyncClient:
    """Create HTTP client for Sensor Tower API"""
    return httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=httpx.Timeout(connect=5.0, read=45.0, write=45.0, pool=5.0)
    )

def validate_token(token: Optional[str] = None) -> bool:
    """Validate that we have a token available"""
    try:
        get_auth_token(token)
        return True
    except ValueError:
        return False

def print_startup_info(args: argparse.Namespace, tool_count: int = 40):
    """Print startup information"""
    print("🚀 Starting Sensor Tower MCP Server (FastMCP)")
    print(f"📡 API Base URL: {API_BASE_URL}")
    print(f"🚌 Transport: {args.transport}")
    if args.transport == "http":
        print(f"🌐 Port: {args.port}")
    print(f"🔧 Available tools: {tool_count}")

def print_token_error():
    """Print error message for missing token"""
    print("❌ Error: SENSOR_TOWER_API_TOKEN environment variable or --token argument is required")
    print("🔑 Get your API token from: https://app.sensortower.com/users/edit/api-settings")