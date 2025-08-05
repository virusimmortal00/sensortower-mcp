#!/usr/bin/env python3
"""
Your Metrics API tools for Sensor Tower MCP Server (Connected Apps)
"""

from typing import Dict, Any, Optional
from fastmcp import FastMCP
from ..base import SensorTowerTool

class YourMetricsTools(SensorTowerTool):
    """Tools for Your Metrics API endpoints (Connected Apps)"""
    
    def register_tools(self, mcp: FastMCP):
        """Register all your metrics tools with FastMCP"""
        
        @mcp.tool 
        def analytics_metrics(
            app_ids: str,
            countries: str,
            start_date: str,
            end_date: str
        ) -> Dict[str, Any]:
            """
            Get detailed App Store analytics report for your connected apps.
            
            Parameters:
            - app_ids: Comma-separated app IDs of apps you manage
            - countries: Comma-separated iTunes country codes
            - start_date: Start date in YYYY-MM-DD format
            - end_date: End date in YYYY-MM-DD format
            
            Examples:
            - Get analytics for your iOS app: app_ids="1234567890", countries="US,CA", start_date="2024-01-01", end_date="2024-01-31"
            
            Note: Provides app impressions, store views, in-app purchases, sessions, and active devices.
            This is ONLY for your own connected apps via iTunes Connect.
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "countries": countries,
                    "start_date": start_date,
                    "end_date": end_date
                }
                return await self.make_request("/v1/ios/sales_reports/analytics_metrics", params)
            
            return self.create_task(_get_data())

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
            
            Parameters:
            - app_ids: Comma-separated app IDs of apps you manage
            - countries: Comma-separated iTunes country codes
            - start_date: Start date in YYYY-MM-DD format  
            - end_date: End date in YYYY-MM-DD format
            - limit: Max reports to retrieve (max 6000, optional)
            - offset: Offset for pagination (optional)
            
            Examples:
            - Get search traffic for your app: app_ids="1234567890", countries="US", start_date="2024-01-01", end_date="2024-01-31"
            
            Note: Currently provides Search source type metrics (app units and impressions).
            This is ONLY for your own connected apps via iTunes Connect.
            """
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "countries": countries,
                    "start_date": start_date,
                    "end_date": end_date
                }
                
                if limit is not None:
                    params["limit"] = limit
                if offset is not None:
                    params["offset"] = offset
                
                return await self.make_request("/v1/ios/sales_reports/sources_metrics", params)
            
            return self.create_task(_get_data())

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
            async def _get_data():
                params = {
                    "app_ids": app_ids,
                    "countries": countries,
                    "date_granularity": date_granularity,
                    "start_date": start_date,
                    "end_date": end_date
                }
                return await self.make_request(f"/v1/{os}/sales_reports", params)
            
            return self.create_task(_get_data())

        @mcp.tool
        def unified_sales_reports(
            start_date: str,
            end_date: str,
            date_granularity: str,
            unified_app_ids: str = None,
            itunes_app_ids: str = None,
            android_app_ids: str = None,
            countries: str = None
        ) -> Dict[str, Any]:
            """
            Get unified downloads and revenue sales report for your connected apps.
            
            Parameters:
            - start_date: Start date in YYYY-MM-DD format (required)
            - end_date: End date in YYYY-MM-DD format (required)
            - date_granularity: "daily", "weekly", "monthly", or "quarterly" (required)
            - unified_app_ids: Comma-separated unified app IDs you manage (optional)
            - itunes_app_ids: Comma-separated iTunes app IDs you manage (optional)
            - android_app_ids: Comma-separated Android app IDs you manage (optional)
            - countries: Comma-separated country codes (use "WW" for all countries, optional)
            
            Examples:
            - Unified app data: start_date="2024-01-01", end_date="2024-12-31", date_granularity="monthly", unified_app_ids="61c25dc864df7d6b51498ab9", countries="US,GB"
            - Cross-platform via iTunes ID: start_date="2024-01-01", end_date="2024-01-31", date_granularity="weekly", itunes_app_ids="1234567890", countries="WW"
            
            Note: Groups data by unified apps. Must specify at least one app_ids parameter.
            This is ONLY for your own connected apps via iTunes Connect/Google Play.
            All revenue is Net and returned in cents.
            """
            async def _get_data():
                params = {"date_granularity": date_granularity}
                
                # Must specify at least one app_ids parameter
                app_id_params = {
                    "unified_app_ids": unified_app_ids,
                    "itunes_app_ids": itunes_app_ids,
                    "android_app_ids": android_app_ids
                }
                
                for key, value in app_id_params.items():
                    if value:
                        params[key] = value
                
                params["start_date"] = start_date
                params["end_date"] = end_date
                
                if countries:
                    params["countries"] = countries
                
                return await self.make_request("/v1/unified/sales_reports", params)
            
            return self.create_task(_get_data())