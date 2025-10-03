#!/usr/bin/env python3
"""
Utility tools for Sensor Tower MCP Server
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from pydantic import Field

from ..base import build_decorator_meta, build_tool_annotations


def _titleize(name: str) -> str:
    """Convert snake_case helper names to Title Case for annotations."""

    return name.replace("_", " ").title()


class UtilityTools:
    """Utility tools that don't require API calls"""

    category = "Utilities"

    def __init__(self) -> None:
        pass

    def _meta(self, tool_name: str, **extra) -> dict:
        return build_decorator_meta(
            tool_name,
            category=self.category,
            **extra,
        )

    def _annotations(self, tool_name: str, *, title: str | None = None) -> dict:
        resolved_title = title or _titleize(tool_name)
        return build_tool_annotations(title=resolved_title)

    def register_tools(self, mcp: FastMCP) -> None:
        """Register all utility tools with FastMCP"""

        @mcp.tool(
            name="get_country_codes",
            description="Get available country codes for Sensor Tower APIs.",
            annotations=self._annotations("get_country_codes", title="Get Country Codes"),
            meta=self._meta("get_country_codes"),
        )
        async def get_country_codes() -> dict:
            """Return a mapping of common country codes to their names.\n\n            Note: Use alongside country filters to provide friendly labels in prompts.\n            Example: get_country_codes()."""

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
                "MX": "Mexico",
            }
            return {"countries": common_countries}

        @mcp.tool(
            name="get_category_ids",
            description="Get available category identifiers for App Store and Google Play.",
            annotations=self._annotations("get_category_ids", title="Get Category IDs"),
            meta=self._meta("get_category_ids"),
        )
        async def get_category_ids(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system to filter categories"),
            ]
        ) -> dict:
            """Return category mappings for the requested mobile platform.\n\n            Note: Pass ios or android to receive the correct category dictionary.\n            Example: get_category_ids(os='ios')."""

            if os == "ios":
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
                    "6011": "Weather",
                }
            else:
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
                    "food": "Food & Drink",
                }

            return {"categories": categories}

        @mcp.tool(
            name="get_chart_types",
            description="List available ranking chart identifiers used by Sensor Tower.",
            annotations=self._annotations("get_chart_types", title="Get Chart Types"),
            meta=self._meta("get_chart_types"),
        )
        async def get_chart_types() -> dict:
            """Return supported ranking chart identifiers and descriptions.\n\n            Note: Combine with category data to craft ranking queries.\n            Example: get_chart_types()."""

            chart_types = {
                "topfreeapplications": "Top Free Apps",
                "toppaidapplications": "Top Paid Apps",
                "topgrossingapplications": "Top Grossing Apps",
                "topfreeipadapplications": "Top Free iPad Apps (iOS only)",
                "toppaidipadadapplications": "Top Paid iPad Apps (iOS only)",
                "topgrossingipadadapplications": "Top Grossing iPad Apps (iOS only)",
            }
            return {"chart_types": chart_types}

        @mcp.tool(
            name="health_check",
            description="Lightweight status endpoint for monitoring and orchestration.",
            annotations=self._annotations("health_check", title="Health Check"),
            meta=self._meta("health_check"),
        )
        async def health_check() -> dict:
            """Return service health details for monitoring probes.\n\n            Note: Use before running live API tests to ensure the MCP proxy is online.\n            Example: health_check()."""

            from ..config import API_BASE_URL, parse_args

            args = parse_args()

            return {
                "status": "healthy",
                "service": "Sensor Tower MCP Server",
                "transport": args.transport,
                "api_base_url": API_BASE_URL,
                "tools_available": 40,
            }
