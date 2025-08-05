#!/usr/bin/env python3
"""
Utility tools for Sensor Tower MCP Server
"""

from typing import Dict, Any
from fastmcp import FastMCP

class UtilityTools:
    """Utility tools that don't require API calls"""
    
    def register_tools(self, mcp: FastMCP):
        """Register all utility tools with FastMCP"""
        
        @mcp.tool
        def get_country_codes() -> Dict[str, Any]:
            """
            Get available country codes for Sensor Tower APIs.
            
            Returns:
            Dictionary containing common country codes and their names.
            
            Examples:
            - US: United States
            - GB: United Kingdom
            - DE: Germany
            - JP: Japan
            
            Note: This is a utility function that returns static country code mappings.
            """
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
            
            Parameters:
            - os: Operating system - "ios" or "android"
            
            Returns:
            Dictionary containing category IDs and names for the specified platform.
            
            Examples:
            - iOS categories: os="ios" returns numeric IDs like "6005": "Social Networking"
            - Android categories: os="android" returns string IDs like "business": "Business"
            
            Note: iOS uses numeric category IDs, Android uses string category names.
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
            """
            Get available chart types for ranking endpoints.
            
            Returns:
            Dictionary containing chart type IDs and descriptions.
            
            Available chart types:
            - topfreeapplications: Top Free Apps
            - toppaidapplications: Top Paid Apps  
            - topgrossingapplications: Top Grossing Apps
            - topfreeipadapplications: Top Free iPad Apps (iOS only)
            - toppaidipadadapplications: Top Paid iPad Apps (iOS only)
            - topgrossingipadadapplications: Top Grossing iPad Apps (iOS only)
            
            Note: iPad-specific chart types are only available for iOS platform.
            """
            chart_types = {
                "topfreeapplications": "Top Free Apps",
                "toppaidapplications": "Top Paid Apps",
                "topgrossingapplications": "Top Grossing Apps",
                "topfreeipadapplications": "Top Free iPad Apps (iOS only)",
                "toppaidipadadapplications": "Top Paid iPad Apps (iOS only)",
                "topgrossingipadadapplications": "Top Grossing iPad Apps (iOS only)"
            }
            return {"chart_types": chart_types}

        @mcp.tool
        def health_check() -> Dict[str, Any]:
            """
            Health check endpoint for monitoring and Docker.
            
            Returns:
            Service status information including:
            - Service status and name
            - Transport method
            - API base URL
            - Number of available tools
            
            Examples:
            - Status: "healthy"
            - Service: "Sensor Tower MCP Server"
            - Tools available: 40
            
            Note: Used for monitoring service health and configuration validation.
            """
            from ..config import API_BASE_URL, parse_args
            args = parse_args()
            
            return {
                "status": "healthy",
                "service": "Sensor Tower MCP Server", 
                "transport": args.transport,
                "api_base_url": API_BASE_URL,
                "tools_available": 40  # All available MCP tools including this health check
            }