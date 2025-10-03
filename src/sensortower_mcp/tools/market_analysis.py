#!/usr/bin/env python3
"""Market Analysis API tools for Sensor Tower MCP Server."""

from typing import Annotated, Literal, Optional, Union

from fastmcp import FastMCP
from pydantic import Field

from ..base import SensorTowerTool, validate_date_format, validate_os_parameter


class MarketAnalysisTools(SensorTowerTool):
    """Tools for Market Analysis API endpoints."""

    category = "MarketAnalysis"

    def register_tools(self, mcp: FastMCP) -> None:
        """Register all market analysis tools with FastMCP."""

        @self.tool(
            mcp,
            name="get_top_and_trending",
            title="Get Top And Trending",
        )
        async def get_top_and_trending(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope"),
            ],
            comparison_attribute: Annotated[
                Literal["absolute", "delta", "transformed_delta"],
                Field(description="Comparison attribute to rank by"),
            ],
            time_range: Annotated[
                Literal["day", "week", "month", "quarter", "year"],
                Field(description="Time range for estimates"),
            ],
            measure: Annotated[
                Literal["units", "revenue"],
                Field(description="Metric type"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            date: Annotated[str, Field(description="Starting date in YYYY-MM-DD format")],
            regions: Annotated[
                str,
                Field(description="Comma-separated region codes"),
            ],
            device_type: Annotated[
                Optional[Literal["iphone", "ipad", "total"]],
                Field(description="Device filter", default=None),
            ] = None,
            end_date: Annotated[
                Optional[str],
                Field(description="Optional end date in YYYY-MM-DD format", default=None),
            ] = None,
            limit: Annotated[
                int,
                Field(description="Maximum number of apps", ge=1, le=2000),
            ] = 25,
            offset: Annotated[
                Optional[int],
                Field(description="Offset for pagination", ge=0, default=None),
            ] = None,
            custom_fields_filter_id: Annotated[
                Optional[str],
                Field(description="Optional custom fields filter ID", default=None),
            ] = None,
            custom_tags_mode: Annotated[
                Literal["include_unified_apps", "exclude_unified_apps"],
                Field(description="Custom tags mode"),
            ] = "include_unified_apps",
            data_model: Annotated[
                Literal["DM_2025_Q2", "DM_2025_Q1"],
                Field(description="Data model version"),
            ] = "DM_2025_Q2",
        ) -> dict:
            """Get top apps by download or revenue estimates with growth metrics."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(date)
            end_value = validate_date_format(end_date) if end_date else None

            params = {
                "comparison_attribute": comparison_attribute,
                "time_range": time_range,
                "measure": measure,
                "category": category,
                "date": start_value,
                "regions": regions,
                "limit": limit,
                "custom_tags_mode": custom_tags_mode,
                "data_model": data_model,
            }

            optional_params = {
                "device_type": device_type,
                "end_date": end_value,
                "offset": offset,
                "custom_fields_filter_id": custom_fields_filter_id,
            }

            for key, value in optional_params.items():
                if value is not None:
                    params[key] = value

            return await self.make_request(
                f"/v1/{os_value}/sales_report_estimates_comparison_attributes",
                params,
            )

        @self.tool(
            mcp,
            name="get_top_publishers",
            title="Get Top Publishers",
        )
        async def get_top_publishers(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope"),
            ],
            comparison_attribute: Annotated[
                Literal["absolute", "delta", "transformed_delta"],
                Field(description="Comparison attribute"),
            ],
            time_range: Annotated[
                Literal["day", "week", "month", "quarter", "year"],
                Field(description="Time range for estimates"),
            ],
            measure: Annotated[
                Literal["units", "revenue"],
                Field(description="Metric type"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            date: Annotated[str, Field(description="Starting date in YYYY-MM-DD format")],
            country: Annotated[
                Optional[str],
                Field(description="Optional country code", default=None),
            ] = None,
            device_type: Annotated[
                Optional[Literal["iphone", "ipad", "total"]],
                Field(description="Device filter", default=None),
            ] = None,
            end_date: Annotated[
                Optional[str],
                Field(description="Optional end date in YYYY-MM-DD format", default=None),
            ] = None,
            limit: Annotated[
                int,
                Field(description="Maximum number of publishers", ge=1, le=2000),
            ] = 25,
            offset: Annotated[
                Optional[int],
                Field(description="Offset for pagination", ge=0, default=None),
            ] = None,
        ) -> dict:
            """Get top publishers by download or revenue estimates."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(date)
            end_value = validate_date_format(end_date) if end_date else None

            params = {
                "comparison_attribute": comparison_attribute,
                "time_range": time_range,
                "measure": measure,
                "category": category,
                "date": start_value,
                "limit": limit,
            }

            optional_params = {
                "country": country,
                "device_type": device_type,
                "end_date": end_value,
                "offset": offset,
            }

            for key, value in optional_params.items():
                if value is not None:
                    params[key] = value

            return await self.make_request(
                f"/v1/{os_value}/top_and_trending/publishers",
                params,
            )

        @self.tool(
            mcp,
            name="get_store_summary",
            title="Get Store Summary",
        )
        async def get_store_summary(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system"),
            ],
            categories: Annotated[
                str,
                Field(description="Comma-separated category identifiers", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity of aggregated data"),
            ] = "daily",
            countries: Annotated[
                str,
                Field(description="Comma-separated country codes"),
            ] = "US",
        ) -> dict:
            """Get app store summary statistics."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            params = {
                "categories": categories,
                "start_date": start_value,
                "end_date": end_value,
                "date_granularity": date_granularity,
                "countries": countries,
            }

            return await self.make_request(
                f"/v1/{os_value}/store_summary",
                params,
            )

        @self.tool(
            mcp,
            name="usage_top_apps",
            title="Usage Top Apps",
        )
        async def usage_top_apps(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope"),
            ],
            comparison_attribute: Annotated[
                Literal["absolute", "delta", "transformed_delta"],
                Field(description="Comparison attribute"),
            ],
            time_range: Annotated[
                Literal["week", "month", "quarter"],
                Field(description="Time range for usage metrics"),
            ],
            measure: Annotated[
                Literal["DAU", "WAU", "MAU"],
                Field(description="Active user metric"),
            ],
            date: Annotated[str, Field(description="Starting date in YYYY-MM-DD format")],
            regions: Annotated[
                str,
                Field(description="Comma-separated region codes"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier", default="0"),
            ] = "0",
            device_type: Annotated[
                Optional[Literal["iphone", "ipad", "total"]],
                Field(description="Device filter", default=None),
            ] = None,
            limit: Annotated[
                int,
                Field(description="Maximum number of apps", ge=1, le=2000),
            ] = 25,
            offset: Annotated[
                Optional[int],
                Field(description="Offset for pagination", ge=0, default=None),
            ] = None,
            custom_fields_filter_id: Annotated[
                Optional[str],
                Field(description="Custom fields filter ID", default=None),
            ] = None,
            data_model: Annotated[
                Literal["DM_2025_Q2", "DM_2025_Q1"],
                Field(description="Data model version"),
            ] = "DM_2025_Q2",
        ) -> dict:
            """Get top apps by active users with growth metrics."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(date)

            params = {
                "comparison_attribute": comparison_attribute,
                "time_range": time_range,
                "measure": measure,
                "date": start_value,
                "regions": regions,
                "category": category,
                "limit": limit,
                "data_model": data_model,
            }

            optional_params = {
                "device_type": device_type,
                "offset": offset,
                "custom_fields_filter_id": custom_fields_filter_id,
            }

            for key, value in optional_params.items():
                if value is not None:
                    params[key] = value

            return await self.make_request(
                f"/v1/{os_value}/top_and_trending/active_users",
                params,
            )

        @self.tool(
            mcp,
            name="get_category_rankings",
            title="Get Category Rankings",
        )
        async def get_category_rankings(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            chart_type: Annotated[
                str,
                Field(description="Chart type identifier", min_length=1),
            ],
            country: Annotated[
                str,
                Field(description="ISO country code", min_length=2, max_length=2),
            ],
            date: Annotated[str, Field(description="Date in YYYY-MM-DD format")],
        ) -> dict:
            """Get top ranking apps for a category and chart type."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            date_value = validate_date_format(date)

            params = {
                "category": category,
                "chart_type": chart_type,
                "country": country,
                "date": date_value,
            }

            return await self.make_request(
                f"/v1/{os_value}/ranking",
                params,
            )

        @self.tool(
            mcp,
            name="top_apps",
            title="Top Apps",
        )
        async def top_apps(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope"),
            ],
            role: Annotated[
                Literal["advertisers", "publishers"],
                Field(description="Role to rank"),
            ],
            date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            period: Annotated[
                Literal["week", "month", "quarter"],
                Field(description="Aggregation period"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            country: Annotated[
                str,
                Field(description="ISO country code"),
            ],
            network: Annotated[
                str,
                Field(description="Ad network name"),
            ],
            custom_fields_filter_id: Annotated[
                Optional[str],
                Field(description="Optional custom fields filter", default=None),
            ] = None,
            limit: Annotated[
                int,
                Field(description="Maximum number of apps", ge=1, le=250),
            ] = 25,
            page: Annotated[
                int,
                Field(description="Page number", ge=1),
            ] = 1,
        ) -> dict:
            """Fetch Share of Voice for top advertisers or publishers."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            date_value = validate_date_format(date)

            params = {
                "role": role,
                "date": date_value,
                "period": period,
                "category": category,
                "country": country,
                "network": network,
                "limit": limit,
                "page": page,
            }
            if custom_fields_filter_id:
                params["custom_fields_filter_id"] = custom_fields_filter_id

            return await self.make_request(
                f"/v1/{os_value}/ad_intel/top_apps",
                params,
            )

        @self.tool(
            mcp,
            name="top_apps_search",
            title="Top Apps Search",
        )
        async def top_apps_search(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope"),
            ],
            app_id: Annotated[str, Field(description="App identifier to search", min_length=1)],
            role: Annotated[
                Literal["advertisers", "publishers"],
                Field(description="Role to rank"),
            ],
            date: Annotated[str, Field(description="Date in YYYY-MM-DD format")],
            period: Annotated[
                Literal["week", "month", "quarter"],
                Field(description="Aggregation period"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            country: Annotated[
                str,
                Field(description="ISO country code"),
            ],
            network: Annotated[
                str,
                Field(description="Ad network name"),
            ],
        ) -> dict:
            """Fetch the rank of a top advertiser or publisher for the given filters."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            date_value = validate_date_format(date)

            valid_networks = {
                "Adcolony",
                "Admob",
                "Apple Search Ads",
                "Applovin",
                "Chartboost",
                "Instagram",
                "Mopub",
                "Pinterest",
                "Snapchat",
                "Supersonic",
                "Tapjoy",
                "TikTok",
                "Unity",
                "Vungle",
                "Youtube",
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
                "supersonic": "Supersonic",
            }

            normalized_network = network
            if isinstance(network, str):
                if network in valid_networks:
                    normalized_network = network
                elif network.lower() in network_mapping:
                    normalized_network = network_mapping[network.lower()]
                elif network.lower() == "facebook":
                    normalized_network = "Instagram"

            params = {
                "app_id": app_id,
                "role": role,
                "date": date_value,
                "period": period,
                "category": str(category),
                "country": country,
                "network": normalized_network,
            }

            return await self.make_request(
                f"/v1/{os_value}/ad_intel/top_apps/search",
                params,
            )

        @self.tool(
            mcp,
            name="top_creatives",
            title="Top Creatives",
        )
        async def top_creatives(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope"),
            ],
            date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            period: Annotated[
                Literal["week", "month", "quarter"],
                Field(description="Aggregation period"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            country: Annotated[
                str,
                Field(description="ISO country code"),
            ],
            network: Annotated[
                str,
                Field(description="Ad network name"),
            ],
            ad_types: Annotated[
                str,
                Field(description="Comma-separated ad types"),
            ],
            limit: Annotated[
                int,
                Field(description="Maximum creatives", ge=1, le=250),
            ] = 25,
            page: Annotated[
                int,
                Field(description="Page number", ge=1),
            ] = 1,
            placements: Annotated[
                Optional[str],
                Field(description="Optional comma-separated placements", default=None),
            ] = None,
            video_durations: Annotated[
                Optional[str],
                Field(description="Optional comma-separated video durations", default=None),
            ] = None,
            aspect_ratios: Annotated[
                Optional[str],
                Field(description="Optional comma-separated aspect ratios", default=None),
            ] = None,
            banner_dimensions: Annotated[
                Optional[str],
                Field(description="Optional comma-separated banner dimensions", default=None),
            ] = None,
            new_creative: Annotated[
                bool,
                Field(description="Return only new creatives"),
            ] = False,
        ) -> dict:
            """Fetch top creatives over a given time period."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            date_value = validate_date_format(date)

            params = {
                "date": date_value,
                "period": period,
                "category": category,
                "country": country,
                "network": network,
                "ad_types": ad_types,
                "limit": limit,
                "page": page,
                "new_creative": new_creative,
            }

            optional_params = {
                "placements": placements,
                "video_durations": video_durations,
                "aspect_ratios": aspect_ratios,
                "banner_dimensions": banner_dimensions,
            }

            for key, value in optional_params.items():
                if value:
                    params[key] = value

            return await self.make_request(
                f"/v1/{os_value}/ad_intel/creatives/top",
                params,
            )

        @self.tool(
            mcp,
            name="games_breakdown",
            title="Games Breakdown",
        )
        async def games_breakdown(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system"),
            ],
            categories: Annotated[
                str,
                Field(description="Comma-separated game categories", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity for the estimates"),
            ] = "daily",
            countries: Annotated[
                Optional[str],
                Field(description="Comma-separated country codes", default=None),
            ] = None,
        ) -> dict:
            """Retrieve aggregated download and revenue estimates of game categories."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            params = {
                "categories": categories,
                "start_date": start_value,
                "end_date": end_value,
                "date_granularity": date_granularity,
            }
            if countries:
                params["countries"] = countries

            return await self.make_request(
                f"/v1/{os_value}/games_breakdown",
                params,
            )
