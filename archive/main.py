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
from typing import Any, Dict

import httpx
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

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

# App Analysis API endpoints
@mcp.tool
def top_in_app_purchases(
    os: str,
    app_ids: str,
    country: str = "US"
) -> Dict[str, Any]:
    """
    Retrieve top in-app purchases for the requested app IDs.

    Parameters:
    - os: Operating system - "ios" or "android"
    - app_ids: App IDs of apps, separated by commas (limited to 100)
    - country: Country code (defaults to "US")

    Example:
    - Get IAP for iOS games: os="ios", app_ids="529479190,1262148500", country="US"
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "country": country,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/apps/top_in_app_purchases", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_creatives(
    os: str,
    app_ids: str,
    start_date: str,
    countries: str,
    networks: str,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Fetches creatives for an advertising app and includes Share of Voice and top publishers for each creative.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - app_ids: Apps to return creatives for, separated by commas
    - start_date: Start date for creatives, YYYY-MM-DD format
    - countries: Countries to return results for, separated by commas
    - networks: Networks to return results for, separated by commas
    - end_date: End date for creatives, YYYY-MM-DD format (defaults to today)
    
    Example:
    - get_creatives(os="ios", app_ids="835599320", start_date="2023-01-01", countries="US", networks="Admob")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "start_date": start_date,
            "countries": countries,
            "networks": networks,
            "auth_token": get_auth_token()
        }
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get(f"/v1/{os}/ad_intel/creatives", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_impressions(
    os: str,
    app_ids: str,
    start_date: str,
    end_date: str,
    countries: str,
    networks: str,
    date_granularity: str = "daily"
) -> Dict[str, Any]:
    """
    Fetches the impressions share of voice (SOV) time series of the requested apps.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - app_ids: Apps to return SOV for, separated by commas (max 5 apps)
    - start_date: Start date for the impressions share of voice data, YYYY-MM-DD format (minimum 2018-01-01)
    - end_date: End date for the impressions share of voice data, YYYY-MM-DD format
    - countries: Countries to return results for, separated by commas
    - networks: Networks to return results for, separated by commas
    - date_granularity: Time period to calculate Share of Voice for - "daily", "weekly", "monthly" (default "daily")
    
    Example:
    - get_impressions(os="ios", app_ids="284882215,1262148500", start_date="2023-01-01", end_date="2023-01-31", countries="US", networks="Facebook")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        # Map date_granularity to period for network_analysis endpoint
        period_mapping = {
            "daily": "day",
            "weekly": "week", 
            "monthly": "month",
            "quarterly": "quarter",
            "yearly": "year"
        }
        period = period_mapping.get(date_granularity, "day")
        
        params = {
            "app_ids": app_ids,
            "start_date": start_date,
            "end_date": end_date,
            "countries": countries,
            "networks": networks,
            "period": period,  # Required parameter for network_analysis
            "auth_token": get_auth_token()
        }
        # Fixed: Use correct network_analysis endpoint with required period parameter
        response = await sensor_tower_client.get(f"/v1/{os}/ad_intel/network_analysis", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_usage_active_users(
    os: str,
    app_ids: str,
    start_date: str,
    end_date: str,
    countries: str = "US",
    date_granularity: str = "monthly"  # Fixed: Valid options are monthly, quarterly, all_time
) -> Dict[str, Any]:
    """
    Retrieve active user estimates of apps per country by date and time period.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - app_ids: IDs of apps, separated by commas (maximum 500 app ids, use Unified App IDs for "unified" os)
    - start_date: Start Date, YYYY-MM-DD format (auto-changes to beginning of time_period, weeks begin on Monday)
    - end_date: End Date, YYYY-MM-DD format (auto-changes to end of specified time_period)
    - countries: Countries to return results for, separated by commas (supports 'WW' for Worldwide, default "US")
    - date_granularity: Aggregate estimates by time period - "daily" for DAU, "weekly" for WAU, "monthly" for MAU (default "monthly")
    
    Example:
    - get_usage_active_users(os="ios", app_ids="284882215,310633997", start_date="2021-01-01", end_date="2021-01-31", countries="US")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        # Map date_granularity to time_period for active_users endpoint
        time_period_mapping = {
            "daily": "day",
            "weekly": "week", 
            "monthly": "month"
        }
        time_period = time_period_mapping.get(date_granularity, "month")
        
        params = {
            "app_ids": app_ids,
            "start_date": start_date,
            "end_date": end_date,
            "countries": countries,
            "time_period": time_period,  # Fixed: Use correct parameter name
            "auth_token": get_auth_token()
        }
        # Fixed: Use correct /usage/ endpoint instead of /usage_intelligence/
        response = await sensor_tower_client.get(f"/v1/{os}/usage/active_users", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_category_history(
    os: str,
    app_ids: str,
    categories: str,
    start_date: str,
    end_date: str,
    countries: str = "US"
) -> Dict[str, Any]:
    """
    Get category ranking history for apps.
    
    Parameters:
    - os: Operating system - "ios" or "android"
    - app_ids: Comma-separated app IDs
    - categories: Comma-separated category IDs (numeric for iOS, string for Android)
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - countries: Comma-separated country codes (default "US")
    
    Example:
    - get_category_history(os="ios", app_ids="284882215", categories="6005", start_date="2024-01-01", end_date="2024-01-31")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "categories": categories,
            "start_date": start_date,
            "end_date": end_date,
            "countries": countries,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/category_history", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def compact_sales_report_estimates(
    os: str,
    start_date: str,
    end_date: str,
    app_ids: str = None,
    publisher_ids: str = None,
    unified_app_ids: str = None,
    unified_publisher_ids: str = None,
    categories: str = None,
    countries: str = "US",
    date_granularity: str = "daily"
) -> Dict[str, Any]:
    """
    Get download and revenue estimates in compact format.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - app_ids: Optional comma-separated app IDs
    - publisher_ids: Optional comma-separated publisher IDs
    - unified_app_ids: Optional comma-separated unified app IDs
    - unified_publisher_ids: Optional comma-separated unified publisher IDs
    - categories: Optional comma-separated category IDs
    - countries: Comma-separated country codes (default "US")
    - date_granularity: "daily", "weekly", "monthly", or "quarterly" (default "daily")
    
    Example:
    - compact_sales_report_estimates(os="ios", start_date="2024-01-01", end_date="2024-01-31", app_ids="284882215")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "countries": countries,
            "date_granularity": date_granularity,
            "auth_token": get_auth_token()
        }
        if app_ids:
            params["app_ids"] = app_ids
        if publisher_ids:
            params["publisher_ids"] = publisher_ids
        if unified_app_ids:
            params["unified_app_ids"] = unified_app_ids
        if unified_publisher_ids:
            params["unified_publisher_ids"] = unified_publisher_ids
        if categories:
            params["categories"] = categories
        
        response = await sensor_tower_client.get(f"/v1/{os}/compact_sales_report_estimates", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def category_ranking_summary(
    os: str,
    app_id: str,
    country: str
) -> Dict[str, Any]:
    """
    Retrieve today's category ranking summary for a particular app with data on chart type, category, and rank.
    
    Parameters:
    - os: Operating system - "ios" or "android"
    - app_id: ID of App
    - country: Country you want download rankings for (Country Codes)
    
    Example:
    - category_ranking_summary(os="ios", app_id="284882215", country="US")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_id": app_id,
            "country": country,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/category/category_ranking_summary", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def impressions_rank(
    os: str,
    app_ids: str,
    start_date: str,
    end_date: str,
    countries: str,
    networks: str = None
) -> Dict[str, Any]:
    """
    Fetches the ranks for the countries, networks and dates of the requested apps.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - app_ids: Apps to return SOV for, separated by commas (max 5 apps)
    - start_date: Start date for the rank data, YYYY-MM-DD format (minimum 2018-01-01)
    - end_date: End date for the rank data, YYYY-MM-DD format
    - countries: Countries to return results for, separated by commas
    - networks: Networks to return results for, separated by commas (optional)
    
    Example:
    - impressions_rank(os="ios", app_ids="284882215,1262148500", start_date="2023-01-01", end_date="2023-01-31", countries="US", networks="Facebook")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "start_date": start_date,
            "end_date": end_date,
            "countries": countries,
            "period": "day",  # Required parameter for network_analysis endpoints
            "auth_token": get_auth_token()
        }
        if networks:
            params["networks"] = networks
        
        response = await sensor_tower_client.get(f"/v1/{os}/ad_intel/network_analysis/rank", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def app_analysis_retention(
    os: str,
    app_ids: str,
    date_granularity: str,
    start_date: str,
    end_date: str = None,
    country: str = None
) -> Dict[str, Any]:
    """
    Retrieve retention of apps (from day 1 to day 90), along with the baseline retention.
    
    Parameters:
    - os: Operating system - "ios" or "android"
    - app_ids: IDs of apps, separated by commas (maximum 500 app ids)
    - date_granularity: Aggregate estimates by granularity - "all_time" or "quarterly"
    - start_date: Start Date, YYYY-MM-DD format
    - end_date: End Date, YYYY-MM-DD format (if date_granularity is "all_time", this parameter is ignored)
    - country: Country codes or region codes to return results for (leave blank for Worldwide)
    
    Note: Quarterly regional and country data begins in Q1 2021. Worldwide and All Time data goes back to Q4 2015.
    
    Example:
    - app_analysis_retention(os="ios", app_ids="284882215,310633997", date_granularity="all_time", start_date="2021-01-01")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        # end_date is required for usage endpoints, provide default if not specified
        actual_end_date = end_date or "2024-01-31"  # Default end_date if not provided
        
        params = {
            "app_ids": app_ids,
            "date_granularity": date_granularity,
            "start_date": start_date,
            "end_date": actual_end_date,  # Required parameter
            "auth_token": get_auth_token()
        }
        if country:
            params["country"] = country
        
        # Fixed: Use correct /usage/ endpoint instead of /usage_intelligence/
        response = await sensor_tower_client.get(f"/v1/{os}/usage/retention", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def downloads_by_sources(
    os: str,
    app_ids: str,
    countries: str,
    start_date: str,
    end_date: str,
    date_granularity: str = "monthly"
) -> Dict[str, Any]:
    """
    Fetch percentages and absolute values for all three download sources: organic, paid, and browser.
    
    Note: Regardless of the OS parameter, this endpoint only accepts Unified app IDs and returns data grouped by Unified app IDs.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified" (only affects platform filtering, always expects Unified app IDs)
    - app_ids: Unified app IDs, separated by commas
    - countries: Country codes, separated by commas (use 'WW' for worldwide, excludes China per Google Play)
    - start_date: Start Date, YYYY-MM-DD format
    - end_date: End Date, YYYY-MM-DD format
    - date_granularity: Aggregate estimates by granularity - "daily" or "monthly" (default "monthly")
    
    Example:
    - downloads_by_sources(os="unified", app_ids="55c5027502ac64f9c0001fa6", countries="WW", start_date="2023-01-01", end_date="2023-02-28")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "countries": countries,
            "start_date": start_date,
            "end_date": end_date,
            "date_granularity": date_granularity,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/downloads_by_sources", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def app_analysis_demographics(
    os: str,
    app_ids: str,
    date_granularity: str,
    start_date: str,
    end_date: str = None,
    country: str = None
) -> Dict[str, Any]:
    """
    Retrieve demographic breakdown of apps (by gender and age range), along with the baseline demographic.
    
    Parameters:
    - os: Operating system - "ios" or "android"
    - app_ids: IDs of apps, separated by commas (maximum 500 app ids)
    - date_granularity: Aggregate estimates by granularity - "all_time" or "quarterly"
    - start_date: Start Date, YYYY-MM-DD format
    - end_date: End Date, YYYY-MM-DD format (if date_granularity is "all_time", this parameter is ignored)
    - country: Country codes or region codes to return results for (leave blank for Worldwide)
    
    Note: Quarterly regional and country data begins in Q1 2021. Worldwide and All Time data goes back to Q4 2015.
    
    Example:
    - app_analysis_demographics(os="ios", app_ids="284882215,310633997", date_granularity="quarterly", start_date="2021-01-01", end_date="2021-08-01")
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        # end_date is required for usage endpoints, provide default if not specified
        actual_end_date = end_date or "2024-01-31"  # Default end_date if not provided
        
        params = {
            "app_ids": app_ids,
            "date_granularity": date_granularity,
            "start_date": start_date,
            "end_date": actual_end_date,  # Required parameter
            "auth_token": get_auth_token()
        }
        if country:
            params["country"] = country
        
        # Fixed: Use correct /usage/ endpoint instead of /usage_intelligence/
        response = await sensor_tower_client.get(f"/v1/{os}/usage/demographics", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def app_update_timeline(
    os: str,
    app_id: str,
    country: str = "US",
    date_limit: str = "10"
) -> Dict[str, Any]:
    """Get app update history timeline."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_id": app_id,
            "country": country,
            "date_limit": date_limit,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/app_update/get_app_update_history", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def version_history(
    os: str,
    app_id: str,
    country: str = "US"
) -> Dict[str, Any]:
    """Get version history for a particular app."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_id": app_id,
            "country": country,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/apps/version_history", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())


# Store Marketing API endpoints  
@mcp.tool
def get_featured_today_stories(
    country: str = "US",
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Retrieve featured today story metadata from App Store."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {"country": country, "auth_token": get_auth_token()}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get("/v1/ios/featured/today/stories", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_featured_apps(
    category: str,
    country: str = "US",
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Retrieve apps featured on the App Store's Apps & Games pages."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "category": category,
            "country": country,
            "auth_token": get_auth_token()
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get("/v1/ios/featured/apps", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_featured_creatives(
    os: str,
    app_id: str,
    countries: str = None,
    types: str = None,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Retrieve the featured creatives and their positions within the App and Google Play store over time."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_id": app_id,
            "auth_token": get_auth_token()
        }
        if countries:
            params["countries"] = countries
        if types:
            params["types"] = types
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get(f"/v1/{os}/featured/creatives", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_keywords(
    os: str,
    app_ids: str,
    countries: str = "US",
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """Get keyword rankings for apps."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "countries": countries,
            "auth_token": get_auth_token()
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get(f"/v1/{os}/keywords", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool  
def get_reviews(
    os: str,
    app_ids: str,
    countries: str = "US",
    start_date: str = None,
    end_date: str = None,
    rating: str = None
) -> Dict[str, Any]:
    """Get app reviews and ratings data."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "countries": countries,
            "auth_token": get_auth_token()
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if rating:
            params["rating"] = rating
        
        response = await sensor_tower_client.get(f"/v1/{os}/reviews", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def research_keyword(
    os: str,
    term: str,
    country: str,
    app_id: int = None,
    page: int = None
) -> Dict[str, Any]:
    """Retrieve detailed information for any keyword, such as related search terms, traffic data, and ranking difficulty."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "term": term,
            "country": country,
            "auth_token": get_auth_token()
        }
        if app_id:
            params["app_id"] = app_id
        if page:
            params["page"] = page
        
        response = await sensor_tower_client.get(f"/v1/{os}/keywords/research_keyword", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

# Market Analysis API endpoints
@mcp.tool
def get_top_and_trending(
    os: str,
    comparison_attribute: str,
    time_range: str,
    measure: str,
    category: str,
    date: str,
    regions: str,
    device_type: str = None,
    end_date: str = None,
    limit: int = 25,
    offset: int = None,
    custom_fields_filter_id: str = None,
    custom_tags_mode: str = "include_unified_apps",
    data_model: str = "DM_2025_Q2"
) -> Dict[str, Any]:
    """
    Get top apps by download and revenue estimates with growth metrics.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - comparison_attribute: "absolute", "delta", or "transformed_delta" 
    - time_range: "day", "week", "month", "quarter", or "year"
    - measure: "units" (downloads) or "revenue"
    - category: Category ID (numeric for iOS like "6005", string for Android like "business")
    - date: Start date in YYYY-MM-DD format (auto-adjusts to beginning of time_range)
    - regions: Comma-separated region codes (e.g. "US,GB,DE")
    - device_type: "iphone", "ipad", "total" for iOS; leave blank for Android; "total" for unified
    - end_date: Optional end date for aggregating multiple periods
    - limit: Max apps per call (default 25, max 2000)
    - offset: Number of apps to offset results by
    - custom_fields_filter_id: Custom fields filter ID
    - custom_tags_mode: "include_unified_apps" or "exclude_unified_apps" (required for unified with custom fields)
    - data_model: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
    
    Examples:
    - Top iOS games by downloads: os="ios", comparison_attribute="absolute", time_range="week", measure="units", category="6014", date="2024-01-01", regions="US"
    - Growing Android business apps: os="android", comparison_attribute="delta", time_range="month", measure="units", category="business", date="2024-01-01", regions="US,GB"
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "comparison_attribute": comparison_attribute,
            "time_range": time_range,
            "measure": measure,
            "category": category,
            "date": date,
            "regions": regions,
            "limit": limit,
            "custom_tags_mode": custom_tags_mode,
            "data_model": data_model,
            "auth_token": get_auth_token()
        }
        
        # Add optional parameters
        if device_type:
            params["device_type"] = device_type
        if end_date:
            params["end_date"] = end_date
        if offset is not None:
            params["offset"] = offset
        if custom_fields_filter_id:
            params["custom_fields_filter_id"] = custom_fields_filter_id
        
        response = await sensor_tower_client.get(f"/v1/{os}/sales_report_estimates_comparison_attributes", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_top_publishers(
    os: str,
    comparison_attribute: str,
    time_range: str,
    measure: str,
    category: str,
    date: str,
    country: str = None,
    device_type: str = None,
    end_date: str = None,
    limit: int = 25,
    offset: int = None
) -> Dict[str, Any]:
    """
    Get top publishers by download and revenue estimates with growth metrics.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - comparison_attribute: "absolute", "delta", or "transformed_delta"
    - time_range: "day", "week", "month", "quarter", or "year"
    - measure: "units" (downloads) or "revenue"
    - category: Category ID (numeric for iOS like "6005", string for Android like "business") 
    - date: Start date in YYYY-MM-DD format (auto-adjusts to beginning of time_range)
    - country: Country or region code (e.g. "US", "GB")
    - device_type: "iphone", "ipad", "total" for iOS; leave blank for Android; "total" for unified
    - end_date: Optional end date for aggregating multiple periods
    - limit: Max publishers per call (default 25)
    - offset: Number of publishers to offset results by
    
    Examples:
    - Top iOS game publishers by revenue: os="ios", comparison_attribute="absolute", time_range="month", measure="revenue", category="6014", date="2024-01-01", country="US"
    - Growing Android productivity publishers: os="android", comparison_attribute="delta", time_range="quarter", measure="units", category="productivity", date="2024-01-01"
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "comparison_attribute": comparison_attribute,
            "time_range": time_range,
            "measure": measure,
            "category": category,
            "date": date,
            "limit": limit,
            "auth_token": get_auth_token()
        }
        
        # Add optional parameters
        if country:
            params["country"] = country
        if device_type:
            params["device_type"] = device_type
        if end_date:
            params["end_date"] = end_date
        if offset is not None:
            params["offset"] = offset
        
        response = await sensor_tower_client.get(f"/v1/{os}/top_and_trending/publishers", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_store_summary(
    os: str,
    start_date: str,
    end_date: str,
    countries: str = "US"
) -> Dict[str, Any]:
    """Get app store summary statistics."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "countries": countries,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/store_summary", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

# Your Metrics API endpoints (Connected Apps)
@mcp.tool 
def analytics_metrics(
    app_ids: str,
    countries: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Get detailed App Store analytics report for your connected apps.
    
    Provides app impressions, store views, in-app purchases, sessions, and active devices.
    
    Parameters:
    - app_ids: Comma-separated app IDs of apps you manage 
    - countries: Comma-separated country codes (e.g. "US,GB,DE")
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Example:
    - Get analytics for your iOS app: app_ids="1234567890", countries="US,CA", start_date="2024-01-01", end_date="2024-01-31"
    
    Note: This is ONLY for your own connected apps via iTunes Connect.
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "countries": countries,
            "start_date": start_date,
            "end_date": end_date,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get("/v1/ios/sales_reports/analytics_metrics", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def sources_metrics(
    app_ids: str,
    countries: str,
    start_date: str,
    end_date: str,
    limit: int = None,
    offset: int = None
) -> Dict[str, Any]:
    """
    Get App Store metrics by traffic source type for your connected apps.
    
    Currently provides Search source type metrics (app units and impressions).
    
    Parameters:
    - app_ids: Comma-separated app IDs of apps you manage
    - countries: Comma-separated iTunes country codes
    - start_date: Start date in YYYY-MM-DD format  
    - end_date: End date in YYYY-MM-DD format
    - limit: Max reports to retrieve (max 6000)
    - offset: Offset for pagination
    
    Example:
    - Get search traffic for your app: app_ids="1234567890", countries="US", start_date="2024-01-01", end_date="2024-01-31"
    
    Note: This is ONLY for your own connected apps via iTunes Connect.
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "countries": countries,
            "start_date": start_date,
            "end_date": end_date,
            "auth_token": get_auth_token()
        }
        
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        
        response = await sensor_tower_client.get("/v1/ios/sales_reports/sources_metrics", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def sales_reports(
    os: str,
    app_ids: str,
    countries: str,
    date_granularity: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Get downloads and revenue sales report for your connected apps.
    
    Parameters:
    - os: Operating system - "ios" or "android"
    - app_ids: Comma-separated app IDs of apps you manage
    - countries: Comma-separated country codes (use "WW" for worldwide)
    - date_granularity: "daily", "weekly", "monthly", or "quarterly"
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Examples:
    - iOS daily sales: os="ios", app_ids="1234567890", countries="US,CA", date_granularity="daily", start_date="2024-01-01", end_date="2024-01-31"
    - Android monthly worldwide: os="android", app_ids="com.example.app", countries="WW", date_granularity="monthly", start_date="2024-01-01", end_date="2024-12-31"
    
    Note: This is ONLY for your own connected apps via iTunes Connect/Google Play.
    All revenue is Net and returned in cents.
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "app_ids": app_ids,
            "countries": countries,
            "date_granularity": date_granularity,
            "start_date": start_date,
            "end_date": end_date,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/sales_reports", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def unified_sales_reports(
    unified_app_ids: str = None,
    itunes_app_ids: str = None,
    android_app_ids: str = None,
    countries: str = None,
    date_granularity: str = "daily",
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Get unified downloads and revenue sales report for your connected apps.
    
    Groups data by unified apps. Must specify at least one app_ids parameter.
    
    Parameters:
    - unified_app_ids: Comma-separated unified app IDs you manage
    - itunes_app_ids: Comma-separated iTunes app IDs you manage
    - android_app_ids: Comma-separated Android app IDs you manage
    - countries: Comma-separated country codes (use "WW" for all countries)
    - date_granularity: "daily", "weekly", "monthly", or "quarterly"
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Examples:
    - Unified app data: unified_app_ids="61c25dc864df7d6b51498ab9", countries="US,GB", date_granularity="monthly", start_date="2024-01-01", end_date="2024-12-31"
    - Cross-platform via iTunes ID: itunes_app_ids="1234567890", countries="WW", date_granularity="weekly", start_date="2024-01-01", end_date="2024-01-31"
    
    Note: This is ONLY for your own connected apps via iTunes Connect/Google Play.
    All revenue is Net and returned in cents.
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "date_granularity": date_granularity,
            "auth_token": get_auth_token()
        }
        
        # Must specify at least one app_ids parameter
        if unified_app_ids:
            params["unified_app_ids"] = unified_app_ids
        if itunes_app_ids:
            params["itunes_app_ids"] = itunes_app_ids
        if android_app_ids:
            params["android_app_ids"] = android_app_ids
        if countries:
            params["countries"] = countries
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = await sensor_tower_client.get("/v1/unified/sales_reports", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def usage_top_apps(
    os: str,
    comparison_attribute: str,
    time_range: str,
    measure: str,
    date: str,
    regions: str,
    category: str = "0",
    device_type: str = None,
    limit: int = 25,
    offset: int = None,
    custom_fields_filter_id: str = None,
    data_model: str = "DM_2025_Q2"
) -> Dict[str, Any]:
    """
    Get top apps by active users with growth metrics.
    
    Parameters:
    - os: Operating system - "ios", "android", or "unified"
    - comparison_attribute: "absolute", "delta", or "transformed_delta"
    - time_range: "week", "month", or "quarter" (week not available for MAU)
    - measure: "DAU" (daily), "WAU" (weekly), or "MAU" (monthly active users)
    - date: Start date in YYYY-MM-DD format (must match beginning of range)
    - regions: Comma-separated region codes (e.g. "US,GB,DE")
    - category: Category ID (default "0" for all, numeric for iOS, string for Android)
    - device_type: "iphone", "ipad", "total" for iOS; leave blank for Android; "total" for unified
    - limit: Max apps per call (default 25)
    - offset: Number of apps to offset results by
    - custom_fields_filter_id: Custom fields filter ID
    - data_model: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
    
    Examples:
    - Top iOS apps by daily active users: os="ios", comparison_attribute="absolute", time_range="month", measure="DAU", date="2024-01-01", regions="US"
    - Growing Android social apps by MAU: os="android", comparison_attribute="delta", time_range="quarter", measure="MAU", date="2024-01-01", regions="US,GB", category="social"
    """
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "comparison_attribute": comparison_attribute,
            "time_range": time_range,
            "measure": measure,
            "date": date,
            "regions": regions,
            "category": category,
            "limit": limit,
            "data_model": data_model,
            "auth_token": get_auth_token()
        }
        
        # Add optional parameters
        if device_type:
            params["device_type"] = device_type
        if offset is not None:
            params["offset"] = offset
        if custom_fields_filter_id:
            params["custom_fields_filter_id"] = custom_fields_filter_id
        
        response = await sensor_tower_client.get(f"/v1/{os}/top_and_trending/active_users", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

# Simple @mcp.tool decorators - using sync functions that handle async internally
@mcp.tool
def get_app_metadata(
    os: str,
    app_ids: str,
    country: str = "US",
    include_sdk_data: bool = False
) -> Dict[str, Any]:
    """
    Get comprehensive app metadata including name, publisher, categories, description, screenshots, ratings, etc.
    
    Parameters:
    - os: Operating system - "ios" or "android"
    - app_ids: Comma-separated app IDs (max 100 per call)
    - country: Country code for localized data (default "US")
    - include_sdk_data: Include SDK insights data (requires subscription)
    
    Examples:
    - Get iOS app details: os="ios", app_ids="284882215,1262148500", country="US"
    - Get Android app with SDK data: os="android", app_ids="com.facebook.katana", include_sdk_data=True
    """
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
        
        # Fixed: Use correct sales_report_estimates endpoint instead of downloads
        response = await sensor_tower_client.get(f"/v1/{os}/sales_report_estimates", params=params)
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
        
        # Fixed: Use correct sales_report_estimates endpoint instead of revenue  
        response = await sensor_tower_client.get(f"/v1/{os}/sales_report_estimates", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
async def search_entities(
    os: str,
    entity_type: str,
    term: str,
    limit: int = 100
) -> Dict[str, Any]:
    """Search for apps and publishers by name, description, or other metadata."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    params = {
        "entity_type": entity_type,
        "term": term,
        "limit": limit,
        "auth_token": get_auth_token()
    }
    response = await sensor_tower_client.get(f"/v1/{os}/search_entities", params=params)
    response.raise_for_status()
    raw_data = response.json()
    
    # Wrap raw list response in dictionary structure for MCP compliance
    if isinstance(raw_data, list):
        return {
            f"{entity_type}s": raw_data,
            "total_count": len(raw_data),
            "query_term": term,
            "entity_type": entity_type,
            "platform": os
        }
    else:
        # In case API already returns dictionary structure
        return raw_data

@mcp.tool
def get_publisher_apps(
    os: str,
    publisher_id: str,
    limit: int = 20,
    offset: int = 0,
    include_count: bool = False
) -> Dict[str, Any]:
    """Retrieve a collection of apps for the specified publisher."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "publisher_id": publisher_id,
            "limit": limit,
            "offset": offset,
            "include_count": include_count,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get(f"/v1/{os}/publisher/publisher_apps", params=params)
        response.raise_for_status()
        raw_data = response.json()
        
        # Wrap raw list response in dictionary structure for MCP compliance
        if isinstance(raw_data, list):
            return {
                "apps": raw_data,
                "total_count": len(raw_data),
                "publisher_id": publisher_id,
                "limit": limit,
                "offset": offset,
                "platform": os
            }
        else:
            # In case API already returns dictionary structure
            return raw_data
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_unified_publisher_apps(
    unified_id: str
) -> Dict[str, Any]:
    """Retrieve unified publisher and all of its unified apps together with platform-specific apps."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "unified_id": unified_id,
            "auth_token": get_auth_token()
        }
        response = await sensor_tower_client.get("/v1/unified/publishers/apps", params=params)
        response.raise_for_status()
        return response.json()
    
    return asyncio.create_task(_get_data())

@mcp.tool
def get_app_ids_by_category(
    os: str,
    category: str,
    start_date: str = None,
    updated_date: str = None,
    offset: int = None,
    limit: int = 1000
) -> Dict[str, Any]:
    """Retrieve a list of app IDs from a given release/updated date in a particular category."""
    if not sensor_tower_client:
        raise ValueError("Sensor Tower client not initialized")
    
    async def _get_data():
        params = {
            "category": category,
            "limit": limit,
            "auth_token": get_auth_token()
        }
        if start_date:
            params["start_date"] = start_date
        if updated_date:
            params["updated_date"] = updated_date
        if offset is not None:
            params["offset"] = offset
        
        response = await sensor_tower_client.get(f"/v1/{os}/apps/app_ids", params=params)
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
    
    ### App Intelligence API (19 endpoints)
    - **get_app_metadata**: Get app details like name, publisher, categories, descriptions, ratings
    - **get_download_estimates**: Retrieve download estimates by country and date
    - **get_revenue_estimates**: Get revenue estimates and trends
    - **top_in_app_purchases**: Get top in-app purchases for apps
    - **compact_sales_report_estimates**: Get sales estimates in compact format
    - **category_ranking_summary**: Get today's category ranking summary for an app
    - **get_creatives**: Get advertising creatives with Share of Voice data
    - **get_impressions**: Get advertising impressions data
    - **impressions_rank**: Get advertising impressions rank data
    - **get_usage_active_users**: Get usage intelligence active users data
    - **get_category_history**: Get category ranking history for apps
    - **app_analysis_retention**: Get retention analysis data for apps
    - **downloads_by_sources**: Get downloads by organic/paid/browser sources
    - **app_analysis_demographics**: Get demographic analysis data for apps
    - **app_update_timeline**: Get app update history timeline
    - **version_history**: Get app version history
    - **search_entities**: Search for apps and publishers by name/description
    - **get_publisher_apps**: Get all apps for a specific publisher
    - **get_unified_publisher_apps**: Get unified publisher and all associated apps
    - **get_app_ids_by_category**: Get app IDs from a given category and date range
    
    ### Store Intelligence API (6 endpoints)
    - **get_featured_apps**: Get apps featured on App Store's Apps & Games pages
    - **get_featured_today_stories**: Fetch App Store Today tab story metadata
    - **get_featured_creatives**: Get featured creatives and their positions in stores over time
    - **get_keywords**: Get keyword rankings for apps
    - **get_reviews**: Get app reviews and ratings data
    - **research_keyword**: Get detailed keyword information including traffic data and ranking difficulty
    
    ### Market Analysis API (5 endpoints)
    - **get_category_rankings**: Get top ranking apps by category and chart type
    - **get_top_and_trending**: Get top apps by downloads/revenue with growth metrics
    - **get_top_publishers**: Get top publishers by downloads/revenue with growth metrics  
    - **usage_top_apps**: Get top apps by active users (DAU/WAU/MAU) with growth metrics
    - **get_store_summary**: Get app store summary statistics
    
    ### Connected Apps API (5 endpoints) - Your Own Apps Only
    - **analytics_metrics**: Get detailed App Store analytics for your connected apps
    - **sources_metrics**: Get App Store traffic source metrics for your connected apps
    - **sales_reports**: Get downloads/revenue sales reports for your connected apps
    - **unified_sales_reports**: Get unified sales reports across iOS/Android for your connected apps
    - **api_usage**: Get your API usage statistics
    

    
    ### Utility Tools
    - **get_country_codes**: Get available country codes
    - **get_category_ids**: Get category IDs for iOS/Android
    - **get_chart_types**: Get available chart types for rankings
    
    ## Authentication:
    Set SENSOR_TOWER_API_TOKEN environment variable with your API token.
    Get your token from: https://app.sensortower.com/users/edit/api-settings
    
    ## Common Parameters:
    - **os**: "ios", "android", or "unified" 
    - **country/regions**: Country codes like "US", "GB", "JP" or comma-separated "US,GB,DE"
    - **app_ids**: Comma-separated app IDs (numbers for iOS, package names for Android)
    - **category**: Category ID (numeric for iOS like "6005", string for Android like "business")
    - **chart_type**: "topfreeapplications", "toppaidapplications", "topgrossingapplications"
    - **comparison_attribute**: "absolute", "delta", or "transformed_delta" for growth analysis
    - **time_range**: "day", "week", "month", "quarter", "year" for aggregation periods
    - **measure**: "units" (downloads), "revenue", "DAU", "WAU", "MAU" depending on endpoint
    - **device_type**: "iphone", "ipad", "total" for iOS; leave blank for Android
    - **dates**: Format as YYYY-MM-DD
    - **data_model**: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
    
    ## Example Usage:
    
    ```
    # Search for apps
    search_entities(os="ios", entity_type="app", term="social media", limit=10)
    
    # Get app metadata  
    get_app_metadata(os="ios", app_ids="284882215", country="US")
    
    # Get top rankings
    get_category_rankings(os="ios", category="6005", chart_type="topfreeapplications", country="US", date="2024-01-15")
    
    # Top trending games by downloads with growth
    get_top_and_trending(os="ios", comparison_attribute="delta", time_range="week", 
                        measure="units", category="6014", date="2024-01-01", regions="US")
    
    # Top publishers by revenue in business category
    get_top_publishers(os="android", comparison_attribute="absolute", time_range="month",
                      measure="revenue", category="business", date="2024-01-01", country="US")
    
    # Top apps by monthly active users
    usage_top_apps(os="unified", comparison_attribute="absolute", time_range="month",
                  measure="MAU", date="2024-01-01", regions="US,GB,DE")
    
    # Get apps for a publisher
    get_publisher_apps(os="ios", publisher_id="368677371", limit=50)
    
    # Get unified publisher data
    get_unified_publisher_apps(unified_id="560c48b48ac350643900b82d")
    
    # Get app IDs by category
    get_app_ids_by_category(os="android", category="business", start_date="2024-01-01", limit=100)
    
    # Research a keyword
    research_keyword(os="ios", term="fitness", country="US")
    
    # Connected apps analytics (your own apps only)
    analytics_metrics(app_ids="1234567890", countries="US,CA", 
                     start_date="2024-01-01", end_date="2024-01-31")
    
    # Your app sales reports
    sales_reports(os="ios", app_ids="1234567890", countries="US,GB", 
                 date_granularity="daily", start_date="2024-01-01", end_date="2024-01-31")
    

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
        "tools_available": 40  # All available MCP tools including this health check
    }

# Separate function for HTTP health endpoint (not a tool)
def get_health_data() -> Dict[str, Any]:
    """Get health check data for HTTP endpoint"""
    return {
        "status": "healthy",
        "service": "Sensor Tower MCP Server", 
        "transport": args.transport,
        "api_base_url": API_BASE_URL,
        "tools_available": 40  # All available MCP tools including health check
    }

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
    print("🔧 Available tools: 40")  # All MCP tools including health check
    
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
    print("🔧 Available tools: 40")  # All MCP tools including health check
    
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
