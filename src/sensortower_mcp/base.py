#!/usr/bin/env python3
"""
Base classes and utilities for Sensor Tower MCP tools
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
from .config import get_auth_token

class SensorTowerTool:
    """Base class for Sensor Tower API tools"""
    
    def __init__(self, client: httpx.AsyncClient, token: str):
        self.client = client
        self.token = token
    
    def get_auth_token(self) -> str:
        """Get authentication token"""
        return self.token
    
    async def make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Sensor Tower API"""
        params["auth_token"] = self.get_auth_token()
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    
    def create_task(self, coro):
        """Create asyncio task for synchronous tool interface"""
        return asyncio.create_task(coro)

def wrap_list_response(data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap raw list responses in dictionary structure for MCP compliance"""
    if isinstance(data, list):
        return {
            "items": data,
            "total_count": len(data),
            **metadata
        }
    else:
        return data

def validate_os_parameter(os: str, allowed: list = None) -> str:
    """Validate operating system parameter"""
    if allowed is None:
        allowed = ["ios", "android", "unified"]
    
    if os.lower() not in allowed:
        raise ValueError(f"Invalid OS parameter: {os}. Must be one of: {', '.join(allowed)}")
    
    return os.lower()

def validate_date_format(date_str: str) -> str:
    """Validate date format (YYYY-MM-DD)"""
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Must be YYYY-MM-DD")