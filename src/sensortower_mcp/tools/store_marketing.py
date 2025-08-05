#!/usr/bin/env python3
"""
Store Marketing API tools for Sensor Tower MCP Server
"""

from typing import Dict, Any, Optional, Union
from fastmcp import FastMCP
from ..base import SensorTowerTool

class StoreMarketingTools(SensorTowerTool):
    """Tools for Store Marketing API endpoints"""
    
    def register_tools(self, mcp: FastMCP):
        """Register all store marketing tools with FastMCP"""
        
        @mcp.tool
        def get_featured_today_stories(
            country: str = "US",
            start_date: str = None,
            end_date: str = None
        ) -> Dict[str, Any]:
            """
            Retrieve featured today story metadata from App Store.
            
            Parameters:
            - country: Country code (defaults to "US")
            - start_date: Start date in YYYY-MM-DD format (optional, defaults to 3 days ago)
            - end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
            Examples:
            - US featured stories: country="US", start_date="2024-01-01", end_date="2024-01-07"
            - UK recent stories: country="GB"
            
            Note: Non-App Intelligence users are limited to the last 3 days. App Intelligence users get all-time data including tomorrow's stories.
            """
            async def _get_data():
                params = {"country": country}
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date
                
                return await self.make_request("/v1/ios/featured/today/stories", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_featured_apps(
            category: Union[int, str],
            country: str = "US",
            start_date: str = None,
            end_date: str = None
        ) -> Dict[str, Any]:
            """
            Retrieve apps featured on the App Store's Apps & Games pages.
            
            Parameters:
            - category: Category ID (required)
            - country: Country code (defaults to "US")
            - start_date: Start date in YYYY-MM-DD format (optional, defaults to 3 days ago)
            - end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
            Examples:
            - Entertainment apps: category="6020", country="US", start_date="2024-01-01", end_date="2024-01-07"
            - French featured games: category="6014", country="FR"
            
            Note: Non-App Intelligence users are limited to the last 3 days. App Intelligence users get all-time data.
            """
            async def _get_data():
                params = {
                    "category": category,
                    "country": country
                }
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date
                
                return await self.make_request("/v1/ios/featured/apps", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_featured_creatives(
            os: str,
            app_id: str,
            countries: str = None,
            types: str = None,
            start_date: str = None,
            end_date: str = None
        ) -> Dict[str, Any]:
            """
            Retrieve the featured creatives and their positions within the App and Google Play store over time.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - app_id: Single app ID
            - countries: Comma-separated country codes (optional)
            - types: Comma-separated creative types (optional)
            - start_date: Start date in YYYY-MM-DD format (optional)
            - end_date: End date in YYYY-MM-DD format (optional)
            
            Examples:
            - iOS app creatives: os="ios", app_id="284882215", countries="US,GB", start_date="2024-01-01", end_date="2024-01-31"
            - Android featured content: os="android", app_id="com.facebook.katana", countries="US"
            """
            async def _get_data():
                params = {"app_id": app_id}
                
                optional_params = {
                    "countries": countries,
                    "types": types,
                    "start_date": start_date,
                    "end_date": end_date
                }
                
                for key, value in optional_params.items():
                    if value:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/featured/creatives", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_keywords(
            os: str,
            app_id: str,
            country: str = "US"
        ) -> Dict[str, Any]:
            """
            Get keyword rankings for apps.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - app_id: App ID (required)
            - country: Country code (defaults to "US")
            
            Examples:
            - iOS app keywords: os="ios", app_id="284882215", country="US"
            - Android app keywords: os="android", app_id="com.facebook.katana", country="GB"
            """
            async def _get_data():
                params = {
                    "app_id": app_id,
                    "country": country
                }
                
                return await self.make_request(f"/v1/{os}/keywords/get_current_keywords", params)
            
            return self.create_task(_get_data())

        @mcp.tool  
        def get_reviews(
            os: str,
            app_id: str,
            country: str,
            start_date: str = None,
            end_date: str = None,
            rating_filter: str = None,
            search_term: str = None,
            username: str = None,
            limit: int = None,
            page: int = None
        ) -> Dict[str, Any]:
            """
            Get app reviews and ratings data.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - app_id: App ID (required)
            - country: Country code (required)
            - start_date: Start date in YYYY-MM-DD format (optional)
            - end_date: End date in YYYY-MM-DD format (optional)
            - rating_filter: Filter by specific rating - "positive", "negative", or 1-5 (optional)
            - search_term: Filter reviews by content (optional)
            - username: Filter reviews by username (optional)
            - limit: Limit how many reviews per call (maximum: 200, optional)
            - page: Offset reviews by the limit for each page (optional)
            
            Examples:
            - iOS app reviews: os="ios", app_id="529479190", country="US", start_date="2024-01-01", end_date="2024-01-31"
            - High-rated Android reviews: os="android", app_id="com.facebook.katana", country="US", rating_filter="5"
            """
            async def _get_data():
                params = {
                    "app_id": app_id,
                    "country": country
                }
                
                optional_params = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "rating_filter": rating_filter,
                    "search_term": search_term,
                    "username": username,
                    "limit": limit,
                    "page": page
                }
                
                for key, value in optional_params.items():
                    if value is not None:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/review/get_reviews", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def research_keyword(
            os: str,
            term: str,
            country: str,
            app_id: int = None,
            page: int = None
        ) -> Dict[str, Any]:
            """
            Retrieve detailed information for any keyword, such as related search terms, traffic data, and ranking difficulty.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - term: Keyword term to research (required)
            - country: Country code (required)
            - app_id: App ID for keyword ranking prediction (iOS only, optional)
            - page: Page number to offset top ranking apps by 25 (optional)
            
            Examples:
            - iOS keyword research: os="ios", term="social", country="US", app_id=284882215
            - Android keyword analysis: os="android", term="business", country="US", page=2
            """
            async def _get_data():
                params = {
                    "term": term,
                    "country": country
                }
                if app_id:
                    params["app_id"] = app_id
                if page:
                    params["page"] = page
                
                return await self.make_request(f"/v1/{os}/keywords/research_keyword", params)
            
            return self.create_task(_get_data())