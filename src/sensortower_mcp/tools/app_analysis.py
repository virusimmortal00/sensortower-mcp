#!/usr/bin/env python3
"""App Analysis API tools for Sensor Tower MCP Server."""

from typing import Annotated, Literal, Optional, Union

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from ..base import SensorTowerTool, validate_date_format, validate_os_parameter


class AppAnalysisTools(SensorTowerTool):
    """Tools for App Analysis API endpoints."""

    category = "AppAnalysis"

    def register_tools(self, mcp: FastMCP) -> None:
        """Register all app analysis tools with FastMCP."""
        
        @self.tool(
            mcp,
            name="top_in_app_purchases",
            title="Top In-App Purchases",
        )
        async def top_in_app_purchases(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system for the requested apps"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs (max 100 per call)", min_length=1),
            ],
            country: Annotated[
                str,
                Field(description="ISO 3166-1 alpha-2 country code", min_length=2, max_length=2),
            ] = "US",
        ) -> dict:
            """Retrieve top in-app purchases for the requested app IDs."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            params = {
                "app_ids": app_ids,
                "country": country,
            }
            return await self.make_request(
                f"/v1/{os_value}/apps/top_in_app_purchases",
                params,
            )

        @self.tool(
            mcp,
            name="get_creatives",
            title="Get Creatives",
        )
        async def get_creatives(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system context for the creatives request"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs to return creatives for", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            countries: Annotated[
                str,
                Field(description="Comma-separated ISO country codes"),
            ],
            networks: Annotated[
                str,
                Field(description="Comma-separated ad networks"),
            ],
            ad_types: Annotated[
                str,
                Field(description="Comma-separated ad types such as video,image,playable"),
            ],
            end_date: Annotated[
                Optional[str],
                Field(description="Optional end date in YYYY-MM-DD format"),
            ] = None,
        ) -> dict:
            """Fetch advertising creatives for apps with Share of Voice and publisher data."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date) if end_date else None

            valid_networks = {
                "Adcolony",
                "Admob",
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
                "adcolony": "Adcolony",
                "supersonic": "Supersonic",
            }

            normalized_networks: list[str] = []
            for network in (value.strip() for value in networks.split(",") if value.strip()):
                normalized = None
                if network in valid_networks:
                    normalized = network
                elif network.lower() in network_mapping:
                    normalized = network_mapping[network.lower()]

                if normalized and normalized in valid_networks:
                    normalized_networks.append(normalized)
                elif network.lower() != "facebook":
                    normalized_networks.append(network)

            params = {
                "app_ids": app_ids,
                "start_date": start_value,
                "countries": countries,
                "networks": ",".join(normalized_networks),
                "ad_types": ad_types,
            }
            if end_value:
                params["end_date"] = end_value

            return await self.make_request(
                f"/v1/{os_value}/ad_intel/creatives",
                params,
            )

        @self.tool(
            mcp,
            name="get_impressions",
            title="Get Impressions",
        )
        async def get_impressions(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system context for impressions data"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs (max 5 per call)", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            countries: Annotated[
                str,
                Field(description="Comma-separated ISO country codes"),
            ],
            networks: Annotated[
                str,
                Field(description="Comma-separated ad networks"),
            ],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly"],
                Field(description="Granularity for the impressions data"),
            ] = "daily",
        ) -> dict:
            """Get advertising impressions data for apps."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)
            period = {
                "daily": "day",
                "weekly": "week",
                "monthly": "month",
            }[date_granularity]

            valid_networks = {
                "Adcolony",
                "Admob",
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
                "adcolony": "Adcolony",
                "supersonic": "Supersonic",
            }

            normalized_networks: list[str] = []
            for network in (value.strip() for value in networks.split(',') if value.strip()):
                normalized = None
                if network in valid_networks:
                    normalized = network
                elif network.lower() in network_mapping:
                    normalized = network_mapping[network.lower()]

                if normalized and normalized in valid_networks:
                    normalized_networks.append(normalized)
                elif network.lower() != "facebook":
                    normalized_networks.append(network)

            params = {
                "app_ids": app_ids,
                "start_date": start_value,
                "end_date": end_value,
                "period": period,
                "countries": countries,
                "networks": ','.join(normalized_networks),
            }

            return await self.make_request(
                f"/v1/{os_value}/ad_intel/network_analysis",
                params,
            )


        @self.tool(
            mcp,
            name="get_usage_active_users",
            title="Get Usage Active Users",
        )
        async def get_usage_active_users(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system for usage metrics"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs (max 500 per call)", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            countries: Annotated[
                str,
                Field(description="Comma-separated ISO country codes (use WW for worldwide)"),
            ] = "US",
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly"],
                Field(description="Granularity for usage metrics"),
            ] = "monthly",
            data_model: Annotated[
                Literal["DM_2025_Q2", "DM_2025_Q1"],
                Field(description="Usage intelligence data model version"),
            ] = "DM_2025_Q2",
        ) -> dict:
            """Get usage intelligence active users data."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            time_period = {
                "daily": "day",
                "weekly": "week",
                "monthly": "month",
            }[date_granularity]

            params = {
                "app_ids": app_ids,
                "start_date": start_value,
                "end_date": end_value,
                "countries": countries,
                "time_period": time_period,
                "data_model": data_model,
            }

            return await self.make_request(
                f"/v1/{os_value}/usage/active_users",
                params,
            )

        @self.tool(
            mcp,
            name="get_category_history",
            title="Get Category History",
        )
        async def get_category_history(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system for category rankings"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs", min_length=1),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            chart_type_ids: Annotated[
                str,
                Field(description="Comma-separated chart type identifiers", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            countries: Annotated[
                str,
                Field(description="Comma-separated ISO country codes"),
            ] = "US",
        ) -> dict:
            """Get category ranking history for apps."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            normalized_chart_types = ",".join(
                value.strip()
                for value in chart_type_ids.split(",")
                if value.strip()
            )
            if not normalized_chart_types:
                raise ToolError("chart_type_ids must include at least one chart type identifier")

            params = {
                "app_ids": app_ids,
                "category": category,
                "chart_type_ids": normalized_chart_types,
                "start_date": start_value,
                "end_date": end_value,
                "countries": countries,
            }

            return await self.make_request(
                f"/v1/{os_value}/category/category_history",
                params,
            )

        @self.tool(
            mcp,
            name="compact_sales_report_estimates",
            title="Compact Sales Report Estimates",
        )
        async def compact_sales_report_estimates(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system for the compact sales report"),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            app_ids: Annotated[
                Optional[str],
                Field(description="Comma-separated app IDs", default=None),
            ] = None,
            publisher_ids: Annotated[
                Optional[str],
                Field(description="Comma-separated publisher IDs", default=None),
            ] = None,
            unified_app_ids: Annotated[
                Optional[str],
                Field(description="Comma-separated unified app IDs", default=None),
            ] = None,
            unified_publisher_ids: Annotated[
                Optional[str],
                Field(description="Comma-separated unified publisher IDs", default=None),
            ] = None,
            categories: Annotated[
                Optional[str],
                Field(description="Comma-separated category IDs", default=None),
            ] = None,
            countries: Annotated[
                str,
                Field(description="Comma-separated ISO country codes"),
            ] = "US",
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity for the report"),
            ] = "daily",
            data_model: Annotated[
                Literal["DM_2025_Q2", "DM_2025_Q1"],
                Field(description="Data model version"),
            ] = "DM_2025_Q2",
        ) -> dict:
            """Get download and revenue estimates in compact format."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            params = {
                "start_date": start_value,
                "end_date": end_value,
                "countries": countries,
                "date_granularity": date_granularity,
                "data_model": data_model,
            }

            optional_params = {
                "app_ids": app_ids,
                "publisher_ids": publisher_ids,
                "unified_app_ids": unified_app_ids,
                "unified_publisher_ids": unified_publisher_ids,
                "categories": categories,
            }

            for key, value in optional_params.items():
                if value:
                    params[key] = value

            return await self.make_request(
                f"/v1/{os_value}/compact_sales_report_estimates",
                params,
            )

        @self.tool(
            mcp,
            name="category_ranking_summary",
            title="Category Ranking Summary",
        )
        async def category_ranking_summary(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system for category summary"),
            ],
            app_id: Annotated[str, Field(description="Single app identifier", min_length=1)],
            country: Annotated[
                str,
                Field(description="ISO 3166-1 alpha-2 country code", min_length=2, max_length=2),
            ],
        ) -> dict:
            """Get today's category ranking summary for a particular app."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            params = {
                "app_id": app_id,
                "country": country,
            }

            return await self.make_request(
                f"/v1/{os_value}/category/category_ranking_summary",
                params,
            )

        @self.tool(
            mcp,
            name="impressions_rank",
            title="Impressions Rank",
        )
        async def impressions_rank(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope for impressions rank"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            countries: Annotated[
                str,
                Field(description="Comma-separated ISO country codes"),
            ],
            networks: Annotated[
                Optional[str],
                Field(description="Comma-separated ad networks", default=None),
            ] = None,
        ) -> dict:
            """Get advertising impressions rank data for apps."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            params = {
                "app_ids": app_ids,
                "start_date": start_value,
                "end_date": end_value,
                "countries": countries,
                "period": "day",
            }
            if networks:
                params["networks"] = networks

            response = await self.make_request(
                f"/v1/{os_value}/ad_intel/network_analysis/rank",
                params,
            )

            metadata = {}
            if isinstance(response, list):
                metadata["summary"] = f"Retrieved {len(response)} rank data points"

            return self.normalize_result(response, metadata)

        @self.tool(
            mcp,
            name="app_analysis_retention",
            title="App Retention",
        )
        async def app_analysis_retention(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system for retention data"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs", min_length=1),
            ],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly"],
                Field(description="Time granularity for retention metrics"),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[
                Optional[str],
                Field(description="End date in YYYY-MM-DD format", default=None),
            ] = None,
            country: Annotated[
                Optional[str],
                Field(description="Optional ISO country code", default=None),
            ] = None,
        ) -> dict:
            """Get retention analysis data for apps."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            actual_end_value = validate_date_format(end_date) if end_date else "2024-01-31"

            params = {
                "app_ids": app_ids,
                "date_granularity": date_granularity,
                "start_date": start_value,
                "end_date": actual_end_value,
            }
            if country:
                params["country"] = country

            return await self.make_request(
                f"/v1/{os_value}/usage/retention",
                params,
            )

        @self.tool(
            mcp,
            name="downloads_by_sources",
            title="Downloads By Sources",
        )
        async def downloads_by_sources(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system filter for downloads"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated unified app IDs", min_length=1),
            ],
            countries: Annotated[
                str,
                Field(description="Comma-separated ISO country codes"),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity for download sources"),
            ] = "monthly",
        ) -> dict:
            """Get app downloads by sources (organic, paid, browser)."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            params = {
                "app_ids": app_ids,
                "countries": countries,
                "start_date": start_value,
                "end_date": end_value,
                "date_granularity": date_granularity,
            }

            return await self.make_request(
                f"/v1/{os_value}/downloads_by_sources",
                params,
            )

        @self.tool(
            mcp,
            name="app_analysis_demographics",
            title="App Demographics",
        )
        async def app_analysis_demographics(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system for demographics"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs", min_length=1),
            ],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly"],
                Field(description="Granularity for demographic aggregation"),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[
                Optional[str],
                Field(description="End date in YYYY-MM-DD format", default=None),
            ] = None,
            country: Annotated[
                Optional[str],
                Field(description="Optional ISO country code", default=None),
            ] = None,
        ) -> dict:
            """Get demographic analysis data for apps."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            actual_end_value = validate_date_format(end_date) if end_date else "2024-01-31"

            params = {
                "app_ids": app_ids,
                "date_granularity": date_granularity,
                "start_date": start_value,
                "end_date": actual_end_value,
            }
            if country:
                params["country"] = country

            return await self.make_request(
                f"/v1/{os_value}/usage/demographics",
                params,
            )

        @self.tool(
            mcp,
            name="app_update_timeline",
            title="App Update Timeline",
        )
        async def app_update_timeline(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system for the app"),
            ],
            app_id: Annotated[str, Field(description="Single app identifier", min_length=1)],
            country: Annotated[
                str,
                Field(description="ISO 3166-1 alpha-2 country code", min_length=2, max_length=2),
            ] = "US",
            date_limit: Annotated[
                int,
                Field(description="Number of updates to retrieve", ge=1, le=100),
            ] = 10,
        ) -> dict:
            """Get app update history timeline."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            params = {
                "app_id": app_id,
                "country": country,
                "date_limit": date_limit,
            }

            return await self.make_request(
                f"/v1/{os_value}/app_update/get_app_update_history",
                params,
            )

        @self.tool(
            mcp,
            name="version_history",
            title="Version History",
        )
        async def version_history(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system for the app"),
            ],
            app_id: Annotated[str, Field(description="Single app identifier", min_length=1)],
            country: Annotated[
                str,
                Field(description="ISO 3166-1 alpha-2 country code", min_length=2, max_length=2),
            ] = "US",
        ) -> dict:
            """Get version history for a particular app."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            params = {
                "app_id": app_id,
                "country": country,
            }

            return await self.make_request(
                f"/v1/{os_value}/apps/version_history",
                params,
            )

        @self.tool(
            mcp,
            name="get_app_metadata",
            title="Get App Metadata",
        )
        async def get_app_metadata(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system for the requested apps"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs (max 100 per call)", min_length=1),
            ],
            country: Annotated[
                str,
                Field(description="ISO 3166-1 alpha-2 country code", min_length=2, max_length=2),
            ] = "US",
            include_sdk_data: Annotated[
                bool,
                Field(description="Include SDK insights data (requires subscription)"),
            ] = False,
        ) -> dict:
            """Get comprehensive app metadata including descriptions, ratings, and more."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            params = {
                "app_ids": app_ids,
                "country": country,
                "include_sdk_data": include_sdk_data,
            }

            return await self.make_request(
                f"/v1/{os_value}/apps",
                params,
            )

        @self.tool(
            mcp,
            name="get_download_estimates",
            title="Get Download Estimates",
        )
        async def get_download_estimates(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope for download estimates"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            countries: Annotated[
                Optional[str],
                Field(description="Comma-separated ISO country codes", default=None),
            ] = None,
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity for download estimates"),
            ] = "daily",
            data_model: Annotated[
                Literal["DM_2025_Q2", "DM_2025_Q1"],
                Field(description="Data model version"),
            ] = "DM_2025_Q2",
        ) -> dict:
            """Fetch download estimates for apps by country and date."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            params = {
                "app_ids": app_ids,
                "start_date": start_value,
                "end_date": end_value,
                "date_granularity": date_granularity,
                "data_model": data_model,
            }
            if countries:
                params["countries"] = countries

            return await self.make_request(
                f"/v1/{os_value}/sales_report_estimates",
                params,
            )

        @self.tool(
            mcp,
            name="get_revenue_estimates",
            title="Get Revenue Estimates",
        )
        async def get_revenue_estimates(
            os: Annotated[
                Literal["ios", "android", "unified"],
                Field(description="Operating system scope for revenue estimates"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs", min_length=1),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            countries: Annotated[
                Optional[str],
                Field(description="Comma-separated ISO country codes", default=None),
            ] = None,
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity for revenue estimates"),
            ] = "daily",
            data_model: Annotated[
                Literal["DM_2025_Q2", "DM_2025_Q1"],
                Field(description="Data model version"),
            ] = "DM_2025_Q2",
        ) -> dict:
            """Fetch revenue estimates for apps by country and date."""

            os_value = validate_os_parameter(os, ["ios", "android", "unified"])
            start_value = validate_date_format(start_date)
            end_value = validate_date_format(end_date)

            params = {
                "app_ids": app_ids,
                "start_date": start_value,
                "end_date": end_value,
                "date_granularity": date_granularity,
                "data_model": data_model,
            }
            if countries:
                params["countries"] = countries

            return await self.make_request(
                f"/v1/{os_value}/sales_report_estimates",
                params,
            )
