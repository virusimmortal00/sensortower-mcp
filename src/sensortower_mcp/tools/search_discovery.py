#!/usr/bin/env python3
"""
Search and Discovery API tools for Sensor Tower MCP Server
"""

from typing import Dict, Any, Union, Optional
from fastmcp import FastMCP
from ..base import SensorTowerTool, wrap_list_response

class SearchDiscoveryTools(SensorTowerTool):
    """Tools for Search and Discovery API endpoints"""
    
    def register_tools(self, mcp: FastMCP):
        """Register all search and discovery tools with FastMCP"""
        
        @mcp.tool
        async def search_entities(
            os: str,
            entity_type: str,
            term: str,
            limit: int = 100
        ) -> Dict[str, Any]:
            """
            Search for apps and publishers by name, description, or other metadata.
            
            Parameters:
            - os: Platform - "ios", "android", "both_stores", or "unified"
            - entity_type: "app" or "publisher" (required)
            - term: Search term (min 2 non-Latin or 3 Latin characters, required)
            - limit: Max apps returned per call (max 250, default 100)
            
            Examples:
            - Search iOS apps: os="ios", entity_type="app", term="Lyft", limit=50
            - Find publishers: os="android", entity_type="publisher", term="Facebook"
            - Unified search: os="unified", entity_type="app", term="social media"
            
            Note: Returns wrapped response for MCP compliance.
            """
            params = {
                "entity_type": entity_type,
                "term": term,
                "limit": limit
            }
            raw_data = await self.make_request(f"/v1/{os}/search_entities", params)
            
            # Wrap raw list response in dictionary structure for MCP compliance
            return wrap_list_response(raw_data, {
                "query_term": term,
                "entity_type": entity_type,
                "platform": os
            })

        @mcp.tool
        def get_publisher_apps(
            os: str,
            publisher_id: str,
            limit: int = 20,
            offset: int = 0,
            include_count: bool = False
        ) -> Dict[str, Any]:
            """
            Retrieve a collection of apps for the specified publisher.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - publisher_id: Publisher ID (required)
            - limit: Max apps returned (default 20)
            - offset: Number of apps to skip for pagination (default 0)
            - include_count: Include total count in response (default False)
            
            Examples:
            - iOS publisher apps: os="ios", publisher_id="284882218", limit=50
            - Android with count: os="android", publisher_id="com.facebook", include_count=True
            - Paginated results: os="ios", publisher_id="284882218", limit=20, offset=40
            
            Note: Returns wrapped response for MCP compliance.
            """
            async def _get_data():
                params = {
                    "publisher_id": publisher_id,
                    "limit": limit,
                    "offset": offset,
                    "include_count": include_count
                }
                raw_data = await self.make_request(f"/v1/{os}/publisher/publisher_apps", params)
                
                # Wrap raw list response in dictionary structure for MCP compliance
                return wrap_list_response(raw_data, {
                    "publisher_id": publisher_id,
                    "limit": limit,
                    "offset": offset,
                    "platform": os
                })
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_unified_publisher_apps(
            unified_id: str
        ) -> Dict[str, Any]:
            """
            Retrieve unified publisher and all of its unified apps together with platform-specific apps.
            
            Parameters:
            - unified_id: Unified publisher ID (required)
            
            Examples:
            - Unified publisher data: unified_id="5a1b2c3d4e5f6789abcdef12"
            
            Note: Returns both unified apps and platform-specific apps for the publisher.
            """
            async def _get_data():
                params = {"unified_id": unified_id}
                return await self.make_request("/v1/unified/publishers/apps", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_app_ids_by_category(
            os: str,
            category: Union[int, str],
            start_date: str = None,
            updated_date: str = None,
            offset: int = None,
            limit: int = 1000
        ) -> Dict[str, Any]:
            """
            Retrieve a list of app IDs from a given release/updated date in a particular category.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - category: Category ID (integer for iOS like 6005, string for Android like "business")
            - start_date: Minimum start date in YYYY-MM-DD format (optional)
            - updated_date: App updated date in YYYY-MM-DD format (optional)
            - offset: Number of app IDs to skip (optional)
            - limit: Max app IDs returned (default 1000, max 10000)
            
            Examples:
            - iOS social apps: os="ios", category="6005", start_date="2024-01-01", limit=500
            - Android business apps: os="android", category="business", updated_date="2024-01-01"
            - Paginated results: os="ios", category="6014", offset=1000, limit=1000
            
            Note: As offset gets large, response time increases. Consider using start_date parameter instead.
            """
            async def _get_data():
                params = {
                    "category": category,
                    "limit": limit
                }
                
                optional_params = {
                    "start_date": start_date,
                    "updated_date": updated_date,
                    "offset": offset
                }
                
                for key, value in optional_params.items():
                    if value is not None:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/apps/app_ids", params)
            
            return self.create_task(_get_data())