#!/usr/bin/env python3
"""
Documentation resources for Sensor Tower MCP Server
"""

from fastmcp import FastMCP

def register_documentation(mcp: FastMCP):
    """Register documentation resources with FastMCP"""
    @mcp.resource("sensor-tower://info")
    def server_info() -> dict:
        """Basic server info for MCP clients."""
        from .config import API_BASE_URL
        return {
            "name": "Sensor Tower MCP Server",
            "version": "1.2.x",
            "transport": "stdio/http",
            "api_base_url": API_BASE_URL,
            "tool_count": 40,
        }
    
    @mcp.resource("sensor-tower://docs")
    def api_documentation() -> str:
        """Provides comprehensive documentation about available Sensor Tower API endpoints."""
        return """
        # Sensor Tower MCP Server Documentation
        
        ## Available Tools:
        
        ### App Intelligence API (16 endpoints)
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
        
        ### Store Intelligence API (6 endpoints)
        - **get_featured_apps**: Get apps featured on App Store's Apps & Games pages
        - **get_featured_today_stories**: Fetch App Store Today tab story metadata
        - **get_featured_creatives**: Get featured creatives and their positions in stores over time
        - **get_keywords**: Get keyword rankings for apps
        - **get_reviews**: Get app reviews and ratings data
        - **research_keyword**: Get detailed keyword information including traffic data and ranking difficulty
        
        ### Market Analysis API (12 endpoints)
        - **get_category_rankings**: Get top ranking apps by category and chart type
        - **get_top_and_trending**: Get top apps by downloads/revenue with growth metrics
        - **get_top_publishers**: Get top publishers by downloads/revenue with growth metrics  
        - **usage_top_apps**: Get top apps by active users (DAU/WAU/MAU) with growth metrics
        - **get_store_summary**: Get app store summary statistics
        - **search_entities**: Search for apps and publishers by name/description
        - **get_publisher_apps**: Get all apps for a specific publisher
        - **get_unified_publisher_apps**: Get unified publisher and all associated apps
        - **get_app_ids_by_category**: Get app IDs from a given category and date range
        - **top_apps**: Get top advertisers or publishers by ad impressions and spend
        - **top_apps_search**: Filter top advertisers by a specific app focus
        - **top_creatives**: Get top performing creatives across ad networks
        - **games_breakdown**: Get sub-category breakdowns within Games market segments
        
        ### Connected Apps API (5 endpoints) - Your Own Apps Only
        - **analytics_metrics**: Get detailed App Store analytics for your connected apps
        - **sources_metrics**: Get App Store traffic source metrics for your connected apps
        - **sales_reports**: Get downloads/revenue sales reports for your connected apps
        - **unified_sales_reports**: Get unified sales reports across iOS/Android for your connected apps
        
        ### Utility Tools (4 endpoints)
        - **get_country_codes**: Get available country codes
        - **get_category_ids**: Get category IDs for iOS/Android
        - **get_chart_types**: Get available chart types for rankings
        - **health_check**: Health check endpoint for monitoring
        
        ## Authentication:
        Set SENSOR_TOWER_API_TOKEN environment variable with your API token.
        Get your token from: https://app.sensortower.com/users/edit/api-settings
        
        ## Common Parameters:
        - **os**: "ios", "android", or "unified" 
        - **country/regions**: Country codes like "US", "GB", "JP" or comma-separated "US,GB,DE"
        - **app_ids**: Comma-separated app IDs (numbers for iOS, package names for Android)
        - **category**: Category ID (integer for iOS like 6005, string for Android like "business")
        - **chart_type**: "topfreeapplications", "toppaidapplications", "topgrossingapplications"
        - **comparison_attribute**: "absolute", "delta", or "transformed_delta" for growth analysis
        - **time_range**: "day", "week", "month", "quarter", "year" for aggregation periods
        - **measure**: "units" (downloads), "revenue", "DAU", "WAU", "MAU" depending on endpoint
        - **device_type**: "iphone", "ipad", "total" for iOS; leave blank for Android
        - **dates**: Format as YYYY-MM-DD
        - **data_model**: "DM_2025_Q2" (new model) or "DM_2025_Q1" (legacy)
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
        
        ## 4. Your App Analytics
        
        ```
        analytics_metrics(
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
