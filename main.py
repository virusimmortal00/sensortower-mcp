#!/usr/bin/env python3
"""
Sensor Tower MCP Server using FastMCP

This MCP server provides access to Sensor Tower's comprehensive mobile app intelligence APIs
using the FastMCP package with OpenAPI integration for streamlined implementation.
"""

import argparse
import asyncio
import os
import sys
import httpx
from fastmcp import FastMCP
from typing import Dict, List, Optional, Any

# Base configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.sensortower.com")

def parse_args():
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

# Parse arguments first
args = parse_args()

# Initialize FastMCP server
mcp = FastMCP("Sensor Tower")

def get_auth_token() -> str:
    """Get authentication token for Sensor Tower API"""
    auth_token = args.token
    if not auth_token:
        raise ValueError("SENSOR_TOWER_API_TOKEN environment variable or --token argument is required")
    return auth_token

# Create HTTP client for Sensor Tower API - defer creation until we have token
sensor_tower_client = None

# Global variables for deferred initialization
api_mcp = None

# Simple @mcp.tool decorators - using sync functions that handle async internally
@mcp.tool
def get_app_metadata(
    os: str,
    app_ids: str,
    country: str = "US",
    include_sdk_data: bool = False
) -> Dict[str, Any]:
    """Get app metadata such as name, publisher, categories, description, screenshots, rating, etc."""
    import asyncio
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "country": country,
            "include_sdk_data": include_sdk_data,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/apps", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_category_rankings(
    os: str,
    category: str,
    chart_type: str,
    country: str,
    date: str
) -> Dict[str, Any]:
    """Get top ranking apps of a particular category and chart type."""
    import asyncio
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "category": category,
            "chart_type": chart_type,
            "country": country,
            "date": date,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/ranking", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_download_estimates(
    os: str,
    app_ids: str,
    countries: str = None,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Fetch download estimates for apps by country and date."""
    import asyncio
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {"app_ids": app_ids, "auth_token": get_auth_token()}
        if countries:
            params["countries"] = countries
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get(f"/v1/{os}/downloads", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_revenue_estimates(
    os: str,
    app_ids: str,
    countries: str = None,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Fetch revenue estimates for apps by country and date."""
    import asyncio
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {"app_ids": app_ids, "auth_token": get_auth_token()}
        if countries:
            params["countries"] = countries
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get(f"/v1/{os}/revenue", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def search_entities(
    os: str,
    entity_type: str,
    term: str,
    limit: int = 100
) -> Dict[str, Any]:
    """Search for apps and publishers by name, description, or other metadata."""
    import asyncio
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "entity_type": entity_type,
            "term": term,
            "limit": limit,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/search_entities", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

# Add utility tools that aren't part of the OpenAPI spec
@mcp.tool
def get_country_codes() -> Dict[str, Any]:
    """Get available country codes for Sensor Tower APIs."""
    common_countries = {
        "US": "United States",
        "GB": "United Kingdom", 
        "DE": "Germany",
        "FR": "France",
        "JP": "Japan",
        "CN": "China",
        "KR": "South Korea",
        "CA": "Canada",
        "AU": "Australia",
        "BR": "Brazil",
        "IN": "India",
        "RU": "Russia",
        "ES": "Spain",
        "IT": "Italy",
        "NL": "Netherlands",
        "SE": "Sweden",
        "MX": "Mexico"
    }
    return {"countries": common_countries}

@mcp.tool
def get_category_ids(os: str) -> Dict[str, Any]:
    """
    Get available category IDs for the specified platform.
    
    Args:
        os: Operating system ("ios" or "android")
    """
    if os.lower() == "ios":
        categories = {
            "6005": "Social Networking",
            "6020": "Entertainment", 
            "6002": "Utilities",
            "6006": "Medical",
            "6007": "Music",
            "6012": "Lifestyle",
            "6014": "Games",
            "6015": "Finance",
            "6016": "Travel",
            "6017": "Sports",
            "6018": "Business",
            "6021": "Education",
            "6022": "Catalogs",
            "6023": "Food & Drink",
            "6024": "Shopping",
            "6001": "Productivity",
            "6003": "Health & Fitness",
            "6004": "Photo & Video",
            "6008": "Navigation",
            "6009": "Reference",
            "6010": "News",
            "6011": "Weather"
        }
    else:  # android
        categories = {
            "business": "Business",
            "entertainment": "Entertainment",
            "finance": "Finance", 
            "games": "Games",
            "lifestyle": "Lifestyle",
            "music": "Music & Audio",
            "social": "Social",
            "sports": "Sports",
            "travel": "Travel & Local",
            "utilities": "Tools",
            "productivity": "Productivity",
            "health": "Health & Fitness",
            "photography": "Photography",
            "maps": "Maps & Navigation",
            "education": "Education",
            "news": "News & Magazines",
            "weather": "Weather",
            "shopping": "Shopping",
            "food": "Food & Drink"
        }
    
    return {"categories": categories}

@mcp.tool 
def get_chart_types() -> Dict[str, Any]:
    """Get available chart types for ranking endpoints."""
    chart_types = {
        "topfreeapplications": "Top Free Apps",
        "toppaidapplications": "Top Paid Apps",
        "topgrossingapplications": "Top Grossing Apps",
        "topfreeipadapplications": "Top Free iPad Apps (iOS only)",
        "toppaidipadadapplications": "Top Paid iPad Apps (iOS only)",
        "topgrossingipadadapplications": "Top Grossing iPad Apps (iOS only)"
    }
    return {"chart_types": chart_types}

# Add resources for documentation and metadata
@mcp.resource("sensor-tower://docs")
def api_documentation() -> str:
    """Provides comprehensive documentation about available Sensor Tower API endpoints."""
    return """
    # Sensor Tower MCP Server Documentation
    
    ## Available Tools:
    
    ### App Intelligence API
    - **get_app_metadata**: Get app details like name, publisher, categories, descriptions, ratings
    - **get_category_rankings**: Get top ranking apps by category and chart type  
    - **get_download_estimates**: Retrieve download estimates by country and date
    - **get_revenue_estimates**: Get revenue estimates and trends
    
    ### Store Intelligence API  
    - **get_featured_apps**: Get apps featured on App Store's Apps & Games pages
    - **get_featured_today_stories**: Fetch App Store Today tab story metadata
    
    ### Usage Intelligence API
    - **search_entities**: Search for apps and publishers by name/description
    - **get_app_ids_by_category**: Get app IDs from specific categories and date ranges
    
    ### Connected Apps API
    - **get_analytics_metrics**: Access your own apps' analytics data
    
    ### Ad Intelligence API
    - **get_advertising_creatives**: Get advertising creative data for competitor analysis
    
    ### Utility Tools
    - **get_country_codes**: Get available country codes
    - **get_category_ids**: Get category IDs for iOS/Android
    - **get_chart_types**: Get available chart types for rankings
    
    ## Authentication:
    Set SENSOR_TOWER_API_TOKEN environment variable with your API token.
    Get your token from: https://app.sensortower.com/users/edit/api-settings
    
    ## Common Parameters:
    - **os**: "ios" or "android" 
    - **country**: Country code like "US", "GB", "JP"
    - **app_ids**: Comma-separated app IDs
    - **category**: Category ID (numeric for iOS, string for Android)
    - **chart_type**: "topfreeapplications", "toppaidapplications", "topgrossingapplications"
    - **dates**: Format as YYYY-MM-DD
    
    ## Example Usage:
    
    ```
    # Search for apps
    search_entities(os="ios", entity_type="app", term="social media", limit=10)
    
    # Get app metadata  
    get_app_metadata(os="ios", app_ids="284882215", country="US")
    
    # Get top rankings
    get_category_rankings(os="ios", category="6005", chart_type="topfreeapplications", country="US", date="2024-01-15")
    ```
    """

@mcp.resource("sensor-tower://examples")
def usage_examples() -> str:
    """Provides practical usage examples for common Sensor Tower API scenarios."""
    return """
    # Sensor Tower API Usage Examples
    
    ## 1. App Research Workflow
    
    ### Step 1: Search for apps
    ```
    search_entities(
        os="unified",
        entity_type="app", 
        term="fitness tracker",
        limit=20
    )
    ```
    
    ### Step 2: Get detailed metadata
    ```
    get_app_metadata(
        os="ios",
        app_ids="284882215,1262148500",  # Facebook, Lyft
        country="US",
        include_sdk_data=True
    )
    ```
    
    ### Step 3: Analyze market position
    ```
    get_category_rankings(
        os="ios",
        category="6023",  # Health & Fitness
        chart_type="topfreeapplications",
        country="US", 
        date="2024-01-15"
    )
    ```
    
    ## 2. Competitor Analysis
    
    ### Download trends
    ```
    get_download_estimates(
        os="android",
        app_ids="com.facebook.katana,com.instagram.android",
        countries="US,GB,DE",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    ```
    
    ### Revenue analysis
    ```
    get_revenue_estimates(
        os="ios", 
        app_ids="284882215",
        countries="US,JP,GB",
        start_date="2023-12-01",
        end_date="2023-12-31"
    )
    ```
    
    ### Advertising intelligence
    ```
    get_advertising_creatives(
        os="ios",
        app_ids="284882215",
        countries="US",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    ```
    
    ## 3. Market Discovery
    
    ### Find new apps in category
    ```
    get_app_ids_by_category(
        os="android",
        category="games",
        start_date="2024-01-01",
        limit=100
    )
    ```
    
    ### Check featured placement
    ```
    get_featured_apps(
        category="6014",  # Games
        country="US",
        start_date="2024-01-10",
        end_date="2024-01-15"
    )
    ```
    
    ### Monitor Today stories
    ```
    get_featured_today_stories(
        country="US",
        start_date="2024-01-10", 
        end_date="2024-01-15"
    )
    ```
    
    ## 4. Your App Analytics
    
    ```
    get_analytics_metrics(
        app_ids="1234567890",  # Your app ID
        start_date="2024-01-01",
        end_date="2024-01-31",
        countries="US,CA,GB"
    )
    ```
    
    ## Tips:
    - Use get_country_codes() to see available countries
    - Use get_category_ids(os="ios") for iOS categories
    - Use get_chart_types() for ranking chart options
    - Dates must be in YYYY-MM-DD format
    - App IDs: iOS uses numbers, Android uses package names
    """

# Add health check endpoint for Docker
@mcp.tool
def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring and Docker"""
    return {
        "status": "healthy",
        "service": "Sensor Tower MCP Server", 
        "transport": args.transport,
        "api_base_url": API_BASE_URL,
        "tools_available": 9  # 5 API tools + 4 utility tools
    }

# Separate function for HTTP health endpoint (not a tool)
def get_health_data() -> Dict[str, Any]:
    """Get health check data for HTTP endpoint"""
    return {
        "status": "healthy",
        "service": "Sensor Tower MCP Server", 
        "transport": args.transport,
        "api_base_url": API_BASE_URL,
        "tools_available": 9  # 5 API tools + 4 utility tools
    }

# Add HTTP health check endpoint using custom route
from starlette.requests import Request
from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_endpoint(request: Request) -> JSONResponse:
    """HTTP health check endpoint"""
    return JSONResponse(get_health_data())

async def main():
    """Main entry point"""
    global sensor_tower_client, api_mcp
    
    # Check for required token
    if not args.token:
        print("❌ Error: SENSOR_TOWER_API_TOKEN environment variable or --token argument is required")
        print("🔑 Get your API token from: https://app.sensortower.com/users/edit/api-settings")
        sys.exit(1)
    
    # Initialize HTTP client now that we have the token
    sensor_tower_client = httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=httpx.Timeout(30.0)
    )
    
    # Display startup information
    print("🚀 Starting Sensor Tower MCP Server (FastMCP)")
    print(f"📡 API Base URL: {API_BASE_URL}")
    print(f"🚌 Transport: {args.transport}")
    if args.transport == "http":
        print(f"🌐 Port: {args.port}")
    print(f"🔧 Available tools: 9")  # 5 API tools + 4 utility tools
    
    try:
        if args.transport == "stdio":
            # Run in stdio mode for MCP clients
            await mcp.run_async()
        elif args.transport == "http":
            # Run in HTTP mode using FastMCP's built-in HTTP server
            print(f"🌐 Starting HTTP server on http://localhost:{args.port}")
            print(f"🔍 Health check: http://localhost:{args.port}/health")
            
            await mcp.run_async(
                transport="http",
                host="0.0.0.0",
                port=args.port
            )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Sensor Tower MCP Server")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def cli():
    """CLI entry point for uvx/pip install"""
    global sensor_tower_client, api_mcp
    
    # Check for required token
    if not args.token:
        print("❌ Error: SENSOR_TOWER_API_TOKEN environment variable or --token argument is required")
        print("🔑 Get your API token from: https://app.sensortower.com/users/edit/api-settings")
        sys.exit(1)
    
    # Initialize HTTP client now that we have the token
    sensor_tower_client = httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=httpx.Timeout(30.0)
    )
    
    # Display startup information
    print("🚀 Starting Sensor Tower MCP Server (FastMCP)")
    print(f"📡 API Base URL: {API_BASE_URL}")
    print(f"🚌 Transport: {args.transport}")
    if args.transport == "http":
        print(f"🌐 Port: {args.port}")
    print(f"🔧 Available tools: 9")  # 5 API tools + 4 utility tools
    
    try:
        if args.transport == "stdio":
            # Run in stdio mode for MCP clients - use synchronous run
            mcp.run()
        else:
            # For HTTP mode, use FastMCP's built-in HTTP server
            mcp.run(
                transport="http",
                host="0.0.0.0",
                port=args.port
            )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Sensor Tower MCP Server")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
