#!/usr/bin/env python3
"""
App Analysis API tools for Sensor Tower MCP Server
"""

import httpx
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from ..base import SensorTowerTool

class AppAnalysisTools(SensorTowerTool):
    """Tools for App Analysis API endpoints"""
    
    def register_tools(self, mcp: FastMCP):
        """Register all app analysis tools with FastMCP"""
        
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
            - app_ids: Comma-separated app IDs (max 100 per call)
            - country: Country code (defaults to "US")
            
            Examples:
            - iOS games: os="ios", app_ids="529479190,1262148500", country="US"
            - Android apps: os="android", app_ids="com.facebook.katana", country="US"
            
            Note: iOS uses integer app IDs, Android uses string package names.
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "country": country
                }
                return await self.make_request(f"/v1/{os}/apps/top_in_app_purchases", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_creatives(
            os: str,
            app_ids: str,
            start_date: str,
            countries: str,
            networks: str,
            ad_types: str,
            end_date: str = None
        ) -> Dict[str, Any]:
            """
            Fetch advertising creatives for apps with Share of Voice and publisher data.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs to return creatives for
            - start_date: Start date in YYYY-MM-DD format
            - countries: Comma-separated country codes (e.g. "US,GB,DE")
            - networks: Comma-separated ad networks (e.g. "Instagram,Admob,Unity")
            - ad_types: Comma-separated ad types (e.g. "video,image,playable")
            - end_date: Optional end date in YYYY-MM-DD format (defaults to today)
            
            Examples:
            - iOS app creatives: os="ios", app_ids="835599320", start_date="2023-01-01", countries="US", networks="Instagram", ad_types="video"
            - Android unified: os="android", app_ids="com.zhiliaoapp.musically", start_date="2023-01-01", countries="US,GB", networks="Admob,Instagram", ad_types="video,image"
            
            Note: Valid networks: Adcolony, Admob, Applovin, Chartboost, Instagram, Mopub, Pinterest, Snapchat, Supersonic, Tapjoy, TikTok, Unity, Vungle, Youtube.
            Facebook is NOT supported by this endpoint.
            """
            async def _get_data():
                # Valid networks for creatives endpoint (same as network_analysis)
                valid_networks = {
                    "Adcolony", "Admob", "Applovin", "Chartboost", "Instagram", 
                    "Mopub", "Pinterest", "Snapchat", "Supersonic", "Tapjoy", 
                    "TikTok", "Unity", "Vungle", "Youtube"
                }
                
                # Network normalization and filtering
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
                    "adcolony": "Adcolony",
                    "supersonic": "Supersonic"
                }
                
                # Filter and normalize networks
                normalized_networks = []
                if networks:
                    network_list = [n.strip() for n in networks.split(',')]
                    for network in network_list:
                        normalized_network = None
                        if network in valid_networks:
                            normalized_network = network
                        elif network.lower() in network_mapping:
                            normalized_network = network_mapping[network.lower()]
                        
                        if normalized_network and normalized_network in valid_networks:
                            normalized_networks.append(normalized_network)
                        elif network.lower() == "facebook":
                            # Skip Facebook - not supported
                            continue
                        else:
                            normalized_networks.append(network)
                
                params = {
                    "app_ids": app_ids,
                    "start_date": start_date,
                    "countries": countries,
                    "networks": ",".join(normalized_networks),
                    "ad_types": ad_types
                }
                if end_date:
                    params["end_date"] = end_date
                
                return await self.make_request(f"/v1/{os}/ad_intel/creatives", params)
            
            return self.create_task(_get_data())

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
            Get advertising impressions data for apps.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs (max 5 per call)
            - start_date: Start date in YYYY-MM-DD format (minimum: 2018-01-01)
            - end_date: End date in YYYY-MM-DD format
            - countries: Comma-separated country codes (required)
            - networks: Comma-separated ad networks (required)
            - date_granularity: "daily", "weekly", "monthly" (maps to API period parameter)
            
            Examples:
            - Daily iOS impressions: os="ios", app_ids="284882215", start_date="2023-01-01", end_date="2023-01-31", countries="US", networks="Instagram,Unity,Youtube"
            
            Note: Valid networks for this endpoint: Adcolony, Admob, Applovin, Chartboost, Instagram, Mopub, Pinterest, Snapchat, Supersonic, Tapjoy, TikTok, Unity, Vungle, Youtube.
            Facebook is NOT supported by the network_analysis endpoint.
            """
            async def _get_data():
                # Map period - API only supports day, week, month
                period_mapping = {
                    "daily": "day",
                    "weekly": "week", 
                    "monthly": "month"
                }
                period = period_mapping.get(date_granularity, "day")
                
                # Valid networks for network_analysis endpoint (from API error message)
                valid_networks = {
                    "Adcolony", "Admob", "Applovin", "Chartboost", "Instagram", 
                    "Mopub", "Pinterest", "Snapchat", "Supersonic", "Tapjoy", 
                    "TikTok", "Unity", "Vungle", "Youtube"
                }
                
                # Network mapping with endpoint-specific filtering
                network_mapping = {
                    "unity": "Unity", 
                    "google": "Youtube",  # Common alias
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
                    "adcolony": "Adcolony",
                    "supersonic": "Supersonic"
                    # Note: Facebook is NOT supported by network_analysis endpoint
                }
                
                # Normalize and filter network names
                normalized_networks = []
                if networks:
                    network_list = [n.strip() for n in networks.split(',')]
                    for network in network_list:
                        # Try exact match first, then lowercase match
                        normalized_network = None
                        if network in valid_networks:
                            normalized_network = network
                        elif network.lower() in network_mapping:
                            normalized_network = network_mapping[network.lower()]
                        
                        # Only add if it's in the valid networks list
                        if normalized_network and normalized_network in valid_networks:
                            normalized_networks.append(normalized_network)
                        elif network.lower() == "facebook":
                            # Skip Facebook with warning - not supported by this endpoint
                            continue
                        else:
                            # Keep original if no mapping found (let API validate)
                            normalized_networks.append(network)
                
                params = {
                    "app_ids": app_ids,
                    "start_date": start_date,
                    "end_date": end_date,
                    "period": period,
                    "countries": countries,
                    "networks": ",".join(normalized_networks)
                }
                
                response = await self.make_request(f"/v1/{os}/ad_intel/network_analysis", params)
                # Wrap list response in dictionary for MCP client compatibility
                return {
                    "data": response,
                    "total_records": len(response) if isinstance(response, list) else 0,
                    "summary": f"Retrieved {len(response) if isinstance(response, list) else 0} SOV data points"
                }
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_usage_active_users(
            os: str,
            app_ids: str,
            start_date: str,
            end_date: str,
            countries: str = "US",
            date_granularity: str = "monthly",
            data_model: str = "DM_2025_Q2"
        ) -> Dict[str, Any]:
            """
            Get usage intelligence active users data.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs (max 500 per call)
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - countries: Comma-separated country codes (defaults to "US", supports "WW" for worldwide)
            - date_granularity: "daily", "weekly", or "monthly" (maps to API time_period: day/week/month)
            - data_model: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
            
            Examples:
            - Monthly iOS active users: os="ios", app_ids="284882215", start_date="2024-01-01", end_date="2024-01-31", countries="US"
            - Daily Android users: os="android", app_ids="com.facebook.katana", start_date="2024-01-01", end_date="2024-01-07", date_granularity="daily"
            
            Note: date_granularity is automatically mapped to the API's 'time_period' parameter.
            """
            async def _get_data():
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
                    "time_period": time_period,
                    "data_model": data_model
                }
                return await self.make_request(f"/v1/{os}/usage/active_users", params)
            
            return self.create_task(_get_data())

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
            - categories: Comma-separated category IDs
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - countries: Comma-separated country codes (defaults to "US")
            
            Examples:
            - iOS social apps: os="ios", app_ids="284882215", categories="6005", start_date="2024-01-01", end_date="2024-01-31", countries="US"
            - Android business: os="android", app_ids="com.facebook.katana", categories="business", start_date="2024-01-01", end_date="2024-01-31"
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "categories": categories,
                    "start_date": start_date,
                    "end_date": end_date,
                    "countries": countries
                }
                return await self.make_request(f"/v1/{os}/category/category_history", params)
            
            return self.create_task(_get_data())

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
            date_granularity: str = "daily",
            data_model: str = "DM_2025_Q2"
        ) -> Dict[str, Any]:
            """
            Get download and revenue estimates in compact format.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - app_ids: Comma-separated app IDs (optional)
            - publisher_ids: Comma-separated publisher IDs (optional)
            - unified_app_ids: Comma-separated unified app IDs (optional)
            - unified_publisher_ids: Comma-separated unified publisher IDs (optional)
            - categories: Comma-separated category IDs (optional)
            - countries: Comma-separated country codes (defaults to "US")
            - date_granularity: "daily", "weekly", "monthly", or "quarterly"
            - data_model: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
            
            Examples:
            - App estimates: os="ios", app_ids="284882215", start_date="2024-01-01", end_date="2024-01-31", countries="US"
            - Category data: os="android", categories="business", start_date="2024-01-01", end_date="2024-01-31"
            
            Note: All revenues are returned in cents.
            """
            async def _get_data():
                params = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "countries": countries,
                    "date_granularity": date_granularity,
                    "data_model": data_model
                }
                
                optional_params = {
                    "app_ids": app_ids,
                    "publisher_ids": publisher_ids,
                    "unified_app_ids": unified_app_ids,
                    "unified_publisher_ids": unified_publisher_ids,
                    "categories": categories
                }
                
                for key, value in optional_params.items():
                    if value:
                        params[key] = value
                
                return await self.make_request(f"/v1/{os}/compact_sales_report_estimates", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def category_ranking_summary(
            os: str,
            app_id: str,
            country: str
        ) -> Dict[str, Any]:
            """
            Get today's category ranking summary for a particular app.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - app_id: Single app ID
            - country: Country code
            
            Examples:
            - iOS app ranking: os="ios", app_id="284882215", country="US"
            - Android app ranking: os="android", app_id="com.facebook.katana", country="US"
            """
            async def _get_data():
                params = {
                    "app_id": app_id,
                    "country": country
                }
                return await self.make_request(f"/v1/{os}/category/category_ranking_summary", params)
            
            return self.create_task(_get_data())

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
            Get advertising impressions rank data for apps.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - countries: Comma-separated country codes
            - networks: Comma-separated ad networks (optional)
            
            Examples:
            - iOS impressions rank: os="ios", app_ids="284882215", start_date="2024-01-01", end_date="2024-01-31", countries="US"
            - Multi-network rank: os="unified", app_ids="5823dd570211a6d33a0003a3", start_date="2024-01-01", end_date="2024-01-31", countries="US", networks="Facebook,Instagram,Admob"
            
            Note: This endpoint supports more networks than network_analysis, including Facebook, Meta Audience Network, Moloco, Digital Turbine, and others.
            Network support varies by endpoint - impressions_rank has broader network coverage than network_analysis.
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "start_date": start_date,
                    "end_date": end_date,
                    "countries": countries,
                    "period": "day"
                }
                if networks:
                    params["networks"] = networks
                
                response = await self.make_request(f"/v1/{os}/ad_intel/network_analysis/rank", params)
                # Wrap list response in dictionary for MCP client compatibility
                return {
                    "data": response,
                    "total_records": len(response) if isinstance(response, list) else 0,
                    "summary": f"Retrieved {len(response) if isinstance(response, list) else 0} rank data points"
                }
            
            return self.create_task(_get_data())

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
            Get retention analysis data for apps.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs
            - date_granularity: Time granularity for data aggregation
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format (optional, defaults to 2024-01-31)
            - country: Country code (optional)
            
            Examples:
            - iOS app retention: os="ios", app_ids="284882215", date_granularity="monthly", start_date="2024-01-01"
            - Android with country: os="android", app_ids="com.facebook.katana", date_granularity="weekly", start_date="2024-01-01", country="US"
            
            Note: Provides retention data from day 1 to day 90, along with baseline retention.
            """
            async def _get_data():
                actual_end_date = end_date or "2024-01-31"
                
                params = {
                    "app_ids": app_ids,
                    "date_granularity": date_granularity,
                    "start_date": start_date,
                    "end_date": actual_end_date
                }
                if country:
                    params["country"] = country
                
                return await self.make_request(f"/v1/{os}/usage/retention", params)
            
            return self.create_task(_get_data())

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
            Get app downloads by sources (organic, paid, browser).
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified" (filters data but always expects unified app IDs)
            - app_ids: Comma-separated UNIFIED app IDs (regardless of OS parameter)
            - countries: Comma-separated country codes
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - date_granularity: "daily", "weekly", "monthly", or "quarterly" (defaults to "monthly")
            
            Examples:
            - iOS data: os="ios", app_ids="55c530a702ac64f9c0002dff", countries="US", start_date="2024-01-01", end_date="2024-01-31"
            - Android data: os="android", app_ids="55c530a702ac64f9c0002dff", countries="US,GB,DE", start_date="2024-01-01", end_date="2024-01-31", date_granularity="weekly"
            
            Note: Always use unified app IDs regardless of OS parameter. Returns percentages and absolute values for organic, paid, and browser download sources.
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "countries": countries,
                    "start_date": start_date,
                    "end_date": end_date,
                    "date_granularity": date_granularity
                }
                return await self.make_request(f"/v1/{os}/downloads_by_sources", params)
            
            return self.create_task(_get_data())

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
            Get demographic analysis data for apps.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs
            - date_granularity: Time granularity for data aggregation
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format (optional, defaults to 2024-01-31)
            - country: Country code (optional)
            
            Examples:
            - iOS demographics: os="ios", app_ids="284882215", date_granularity="monthly", start_date="2024-01-01"
            - Android with country: os="android", app_ids="com.facebook.katana", date_granularity="weekly", start_date="2024-01-01", country="US"
            
            Note: Provides demographic breakdown by gender and age range.
            """
            async def _get_data():
                actual_end_date = end_date or "2024-01-31"
                
                params = {
                    "app_ids": app_ids,
                    "date_granularity": date_granularity,
                    "start_date": start_date,
                    "end_date": actual_end_date
                }
                if country:
                    params["country"] = country
                
                return await self.make_request(f"/v1/{os}/usage/demographics", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def app_update_timeline(
            os: str,
            app_id: str,
            country: str = "US",
            date_limit: str = "10"
        ) -> Dict[str, Any]:
            """
            Get app update history timeline.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - app_id: Single app ID
            - country: Country code (defaults to "US")
            - date_limit: Number of updates to retrieve (defaults to "10")
            
            Examples:
            - iOS app updates: os="ios", app_id="284882215", country="US", date_limit="20"
            - Android app history: os="android", app_id="com.facebook.katana", country="US"
            """
            async def _get_data():
                params = {
                    "app_id": app_id,
                    "country": country,
                    "date_limit": date_limit
                }
                return await self.make_request(f"/v1/{os}/app_update/get_app_update_history", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def version_history(
            os: str,
            app_id: str,
            country: str = "US"
        ) -> Dict[str, Any]:
            """
            Get version history for a particular app.
            
            Parameters:
            - os: Operating system - "ios" or "android"
            - app_id: Single app ID
            - country: Country code (defaults to "US")
            
            Examples:
            - iOS version history: os="ios", app_id="284882215", country="US"
            - Android versions: os="android", app_id="com.facebook.katana", country="GB"
            """
            async def _get_data():
                params = {
                    "app_id": app_id,
                    "country": country
                }
                return await self.make_request(f"/v1/{os}/apps/version_history", params)
            
            return self.create_task(_get_data())

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
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "country": country,
                    "include_sdk_data": include_sdk_data
                }
                return await self.make_request(f"/v1/{os}/apps", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_download_estimates(
            os: str,
            app_ids: str,
            start_date: str,
            end_date: str,
            countries: str = None,
            date_granularity: str = "daily",
            data_model: str = "DM_2025_Q2"
        ) -> Dict[str, Any]:
            """
            Fetch download estimates for apps by country and date.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - countries: Comma-separated country codes (optional)
            - date_granularity: "daily", "weekly", "monthly", or "quarterly"
            - data_model: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
            
            Examples:
            - iOS downloads: os="ios", app_ids="284882215", start_date="2024-01-01", end_date="2024-01-31"
            - Android downloads: os="android", app_ids="com.facebook.katana", start_date="2024-01-01", end_date="2024-01-31", countries="US,GB"
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "start_date": start_date,
                    "end_date": end_date,
                    "date_granularity": date_granularity,
                    "data_model": data_model
                }
                if countries:
                    params["countries"] = countries
                
                return await self.make_request(f"/v1/{os}/sales_report_estimates", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def get_revenue_estimates(
            os: str,
            app_ids: str,
            start_date: str,
            end_date: str,
            countries: str = None,
            date_granularity: str = "daily",
            data_model: str = "DM_2025_Q2"
        ) -> Dict[str, Any]:
            """
            Fetch revenue estimates for apps by country and date.
            
            Parameters:
            - os: Operating system - "ios", "android", or "unified"
            - app_ids: Comma-separated app IDs
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            - countries: Comma-separated country codes (optional)
            - date_granularity: "daily", "weekly", "monthly", or "quarterly"
            - data_model: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
            
            Examples:
            - iOS revenue: os="ios", app_ids="284882215", start_date="2024-01-01", end_date="2024-01-31"
            - Android revenue: os="android", app_ids="com.facebook.katana", start_date="2024-01-01", end_date="2024-01-31", countries="US,GB"
            
            Note: All revenues are returned in cents.
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "start_date": start_date,
                    "end_date": end_date,
                    "date_granularity": date_granularity,
                    "data_model": data_model
                }
                if countries:
                    params["countries"] = countries
                
                return await self.make_request(f"/v1/{os}/sales_report_estimates", params)
            
            return self.create_task(_get_data())


