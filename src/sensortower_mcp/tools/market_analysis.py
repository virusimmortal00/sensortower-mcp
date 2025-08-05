#!/usr/bin/env python3
"""
Market Analysis API tools for Sensor Tower MCP Server
"""

from typing import Dict, Any, Union, Optional
from fastmcp import FastMCP
from ..base import SensorTowerTool

class MarketAnalysisTools(SensorTowerTool):
    """Tools for Market Analysis API endpoints"""
    
    def register_tools(self, mcp: FastMCP):
        """Register all market analysis tools with FastMCP"""
        
        @mcp.tool
        def get_top_and_trending(
            os: str,
            comparison_attribute: str,
            time_range: str,
            measure: str,
            category: Union[int, str],
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
            - category: Category ID (integer for iOS like 6005, string for Android like "business")
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
            - Top iOS games by downloads: os="ios", comparison_attribute="absolute", time_range="week", measure="units", category=6014, date="2024-01-01", regions="US"
            - Growing Android business apps: os="android", comparison_attribute="delta", time_range="month", measure="units", category="business", date="2024-01-01", regions="US,GB"
            """
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
                    "data_model": data_model
                }
                
                optional_params = {
                    "device_type": device_type,
                    "end_date": end_date,
                    "offset": offset,
                    "custom_fields_filter_id": custom_fields_filter_id
                }
                
                for key, value in optional_params.items():
                    if value is not None:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/sales_report_estimates_comparison_attributes", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_top_publishers(
            os: str,
            comparison_attribute: str,
            time_range: str,
            measure: str,
            category: Union[int, str],
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
            - category: Category ID (integer for iOS like 6005, string for Android like "business") 
            - date: Start date in YYYY-MM-DD format (auto-adjusts to beginning of time_range)
            - country: Country or region code (e.g. "US", "GB")
            - device_type: "iphone", "ipad", "total" for iOS; leave blank for Android; "total" for unified
            - end_date: Optional end date for aggregating multiple periods
            - limit: Max publishers per call (default 25)
            - offset: Number of publishers to offset results by
            
            Examples:
            - Top iOS game publishers by revenue: os="ios", comparison_attribute="absolute", time_range="month", measure="revenue", category=6014, date="2024-01-01", country="US"
            - Growing Android productivity publishers: os="android", comparison_attribute="delta", time_range="quarter", measure="units", category="productivity", date="2024-01-01"
            """
            async def _get_data():
                params = {
                    "comparison_attribute": comparison_attribute,
                    "time_range": time_range,
                    "measure": measure,
                    "category": category,
                    "date": date,
                    "limit": limit
                }
                
                optional_params = {
                    "country": country,
                    "device_type": device_type,
                    "end_date": end_date,
                    "offset": offset
                }
                
                for key, value in optional_params.items():
                    if value is not None:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/top_and_trending/publishers", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_store_summary(
            os: str,
            categories: str,
            start_date: str,
            end_date: str,
            date_granularity: str = "daily",
            countries: str = "US"
        ) -> Dict[str, Any]:
            """
            Get app store summary statistics.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - categories: Comma-separated category IDs (required)
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - date_granularity: Aggregate estimates by granularity ("daily", "weekly", "monthly", or "quarterly")
            - countries: Comma-separated country codes (defaults to "US")
            
            Examples:
            - iOS store summary: os="ios", categories="6012", start_date="2024-01-01", end_date="2024-01-31", date_granularity="daily", countries="US"
            - Multi-country Android: os="android", categories="lifestyle", start_date="2024-01-01", end_date="2024-01-31", date_granularity="monthly", countries="US,GB,DE"
            """
            async def _get_data():
                params = {
                    "categories": categories,
                    "start_date": start_date,
                    "end_date": end_date,
                    "date_granularity": date_granularity,
                    "countries": countries
                }
                return await self.make_request(f"/v1/{os}/store_summary", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def usage_top_apps(
            os: str,
            comparison_attribute: str,
            time_range: str,
            measure: str,
            date: str,
            regions: str,
            category: Union[int, str] = "0",
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
            - category: Category ID (default "0" for all, integer for iOS, string for Android)
            - device_type: "iphone", "ipad", "total" for iOS; leave blank for Android; "total" for unified
            - limit: Max apps per call (default 25)
            - offset: Number of apps to offset results by
            - custom_fields_filter_id: Custom fields filter ID
            - data_model: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
            
            Examples:
            - Top iOS apps by daily active users: os="ios", comparison_attribute="absolute", time_range="month", measure="DAU", date="2024-01-01", regions="US"
            - Growing Android social apps by MAU: os="android", comparison_attribute="delta", time_range="quarter", measure="MAU", date="2024-01-01", regions="US,GB", category="social"
            """
            async def _get_data():
                params = {
                    "comparison_attribute": comparison_attribute,
                    "time_range": time_range,
                    "measure": measure,
                    "date": date,
                    "regions": regions,
                    "category": category,
                    "limit": limit,
                    "data_model": data_model
                }
                
                optional_params = {
                    "device_type": device_type,
                    "offset": offset,
                    "custom_fields_filter_id": custom_fields_filter_id
                }
                
                for key, value in optional_params.items():
                    if value is not None:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/top_and_trending/active_users", params)
            
            return self.create_task(_get_data())



        @mcp.tool
        def get_category_rankings(
            os: str,
            category: Union[int, str],
            chart_type: str,
            country: str,
            date: str
        ) -> Dict[str, Any]:
            """
            Get top ranking apps of a particular category and chart type.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - category: Category ID (integer for iOS like 6005, string for Android like "business")
            - chart_type: Chart type (e.g. "topfreeapplications", "toppaidapplications", "topgrossingapplications")
            - country: Country code (e.g. "US", "GB")
            - date: Date in YYYY-MM-DD format (defaults to latest rankings)
            
            Examples:
            - iOS top free social apps: os="ios", category="6005", chart_type="topfreeapplications", country="US", date="2024-01-01"
            - Android top grossing business: os="android", category="business", chart_type="topgrossingapplications", country="US", date="2024-01-01"
            """
            async def _get_data():
                params = {
                    "category": category,
                    "chart_type": chart_type,
                    "country": country,
                    "date": date
                }
                return await self.make_request(f"/v1/{os}/ranking", params)
            
            return self.create_task(_get_data())





        @mcp.tool
        def top_apps(
            os: str,
            role: str,
            date: str,
            period: str,
            category: Union[int, str],
            country: str,
            network: str,
            custom_fields_filter_id: str = None,
            limit: int = 25,
            page: int = 1
        ) -> Dict[str, Any]:
            """
            Fetches the current and prior Share of Voice for the top advertisers or publishers over a given time period.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - role: "advertisers" or "publishers"
            - date: Start date for impression data, YYYY-MM-DD format
            - period: Time period - "week", "month", or "quarter"
            - category: Category ID (use iOS categories for unified)
            - country: Country code (default "US")
            - network: Network name (e.g. "Admob", "Facebook", "All Networks")
            - custom_fields_filter_id: Custom fields filter ID (optional)
            - limit: Max apps returned (25, 100, or 250, default 25)
            - page: Page number (default 1)
            
            Examples:
            - Top iOS advertisers: os="ios", role="advertisers", date="2024-01-01", period="month", category="6005", country="US", network="Admob"
            - Top Android publishers: os="android", role="publishers", date="2024-01-01", period="week", category="social", country="US", network="Facebook"
            """
            async def _get_data():
                params = {
                    "role": role,
                    "date": date,
                    "period": period,
                    "category": category,
                    "country": country,
                    "network": network,
                    "limit": limit,
                    "page": page
                }
                
                if custom_fields_filter_id:
                    params["custom_fields_filter_id"] = custom_fields_filter_id
                
                return await self.make_request(f"/v1/{os}/ad_intel/top_apps", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def top_apps_search(
            os: str,
            app_id: str,
            role: str,
            date: str,
            period: str,
            category: Union[int, str],
            country: str,
            network: str
        ) -> Dict[str, Any]:
            """
            Fetches the rank of a top advertiser or top publisher in apps matching the provided filters.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_id: App to search for
            - role: "advertisers" or "publishers"
            - date: Date to search, YYYY-MM-DD format
            - period: Time period - "week", "month", or "quarter"
            - category: Category to search (use iOS categories for unified)
            - country: Country code (default "US")
            - network: Network name (e.g. "Admob", "Instagram")
            
            Examples:
            - Search iOS app rank: os="ios", app_id="284882215", role="advertisers", date="2024-01-01", period="month", category="6005", country="US", network="Admob"
            - Search Android app: os="android", app_id="com.zhiliaoapp.musically", role="publishers", date="2024-01-01", period="week", category="social", country="US", network="Instagram"
            
            Note: Valid networks: Adcolony, Admob, Apple Search Ads, Applovin, Chartboost, Instagram, Mopub, Pinterest, Snapchat, Supersonic, Tapjoy, TikTok, Unity, Vungle, Youtube.
            Facebook is NOT supported. Network names are case-sensitive.
            """
            async def _get_data():
                # Normalize network names similar to get_impressions
                # Valid networks for top_apps endpoints (includes Apple Search Ads)
                valid_networks = {
                    "Adcolony", "Admob", "Apple Search Ads", "Applovin", "Chartboost", 
                    "Instagram", "Mopub", "Pinterest", "Snapchat", "Supersonic", 
                    "Tapjoy", "TikTok", "Unity", "Vungle", "Youtube"
                }
                
                network_mapping = {
                    "unity": "Unity", 
                    "google": "Youtube",
                    "youtube": "Youtube",
                    "admob": "Admob",
                    "applovin": "Applovin",
                    "chartboost": "Chartboost",
                    "instagram": "Instagram",
                    "snapchat": "Snapchat",
                    "tiktok": "TikTok",
                    "mopub": "Mopub",
                    "tapjoy": "Tapjoy",
                    "vungle": "Vungle",
                    "pinterest": "Pinterest",
                    "apple search ads": "Apple Search Ads",
                    "adcolony": "Adcolony",
                    "supersonic": "Supersonic"
                    # Note: Facebook is NOT supported by ad_intel endpoints
                }
                
                # Normalize and validate network name
                normalized_network = network
                if network in valid_networks:
                    normalized_network = network
                elif network.lower() in network_mapping:
                    candidate = network_mapping[network.lower()]
                    if candidate in valid_networks:
                        normalized_network = candidate
                elif network.lower() == "facebook":
                    # Facebook not supported - use Instagram instead
                    normalized_network = "Instagram"
                
                params = {
                    "app_id": app_id,
                    "role": role,
                    "date": date,
                    "period": period,
                    "category": str(category),  # Ensure category is string
                    "country": country,
                    "network": normalized_network
                }
                
                return await self.make_request(f"/v1/{os}/ad_intel/top_apps/search", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def top_creatives(
            os: str,
            date: str,
            period: str,
            category: Union[int, str],
            country: str,
            network: str,
            ad_types: str,
            limit: int = 25,
            page: int = 1,
            placements: str = None,
            video_durations: str = None,
            aspect_ratios: str = None,
            banner_dimensions: str = None,
            new_creative: bool = False
        ) -> Dict[str, Any]:
            """
            Fetches the top creatives over a given time period.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - date: Start date for creatives data, YYYY-MM-DD format
            - period: Time period - "week", "month", or "quarter"
            - category: Category ID (use iOS categories for unified)
            - country: Country code (default "US")
            - network: Network name (e.g. "Youtube", "Facebook", "Admob")
            - ad_types: Comma-separated ad types (e.g. "video", "image", "playable")
            - limit: Max creatives returned (25, 100, or 250, default 25)
            - page: Page number (default 1)
            - placements: Comma-separated ad placements (optional)
            - video_durations: Comma-separated video duration ranges (optional)
            - aspect_ratios: Comma-separated aspect ratios (optional)
            - banner_dimensions: Comma-separated banner dimensions (optional)
            - new_creative: If true, return only new creatives (default false)
            
            Examples:
            - Top video creatives: os="ios", date="2024-01-01", period="month", category="6005", country="US", network="Youtube", ad_types="video"
            - Top image ads: os="android", date="2024-01-01", period="week", category="social", country="US", network="Facebook", ad_types="image,banner"
            """
            async def _get_data():
                params = {
                    "date": date,
                    "period": period,
                    "category": category,
                    "country": country,
                    "network": network,
                    "ad_types": ad_types,
                    "limit": limit,
                    "page": page,
                    "new_creative": new_creative
                }
                
                optional_params = {
                    "placements": placements,
                    "video_durations": video_durations,
                    "aspect_ratios": aspect_ratios,
                    "banner_dimensions": banner_dimensions
                }
                
                for key, value in optional_params.items():
                    if value:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/ad_intel/creatives/top", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def games_breakdown(
            os: str,
            categories: str,
            start_date: str,
            end_date: str,
            date_granularity: str = "daily",
            countries: str = None
        ) -> Dict[str, Any]:
            """
            Retrieve aggregated download and revenue estimates of game categories by country and date.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - categories: Comma-separated game category IDs (required)
            - start_date: Start date, YYYY-MM-DD format (data before 2016-01-01 not supported)
            - end_date: End date, YYYY-MM-DD format
            - date_granularity: Aggregate estimates by granularity ("daily", "weekly", "monthly", or "quarterly")
            - countries: Comma-separated country codes (use "WW" for worldwide)
            
            Examples:
            - iOS game breakdown: os="ios", categories="7001", start_date="2024-01-01", end_date="2024-01-07", date_granularity="daily", countries="US"
            - Android games worldwide: os="android", categories="game_action", start_date="2024-01-01", end_date="2024-01-31", date_granularity="monthly", countries="WW"
            
            Note: All revenues are returned in cents.
            """
            async def _get_data():
                params = {
                    "categories": categories,
                    "start_date": start_date,
                    "end_date": end_date,
                    "date_granularity": date_granularity
                }
                
                if countries:
                    params["countries"] = countries
                
                return await self.make_request(f"/v1/{os}/games_breakdown", params)
            
            return self.create_task(_get_data())