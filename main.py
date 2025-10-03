#!/usr/bin/env python3
"""
Sensor Tower MCP Server Entry Point

This is a simplified entry point that uses the modular server implementation.
"""

from src.sensortower_mcp.server import cli

if __name__ == "__main__":
    cli()