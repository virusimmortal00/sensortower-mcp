#!/usr/bin/env python3
"""Your Metrics API tools for Sensor Tower MCP Server (Connected Apps)."""

from typing import Annotated, Literal, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from ..base import SensorTowerTool, validate_date_format


class YourMetricsTools(SensorTowerTool):
    """Tools for Your Metrics API endpoints (Connected Apps)."""

    category = "YourMetrics"

    def register_tools(self, mcp: FastMCP) -> None:
        """Register all your metrics tools with FastMCP."""

        @self.tool(
            mcp,
            name="analytics_metrics",
            title="Analytics Metrics",
        )
        async def analytics_metrics(
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs you manage", min_length=1),
            ],
            countries: Annotated[
                str,
                Field(description="Comma-separated iTunes country codes", min_length=2),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
        ) -> dict:
            """Get detailed App Store analytics report for connected apps."""

            params = {
                "app_ids": app_ids,
                "countries": countries,
                "start_date": validate_date_format(start_date),
                "end_date": validate_date_format(end_date),
            }

            return await self.make_request(
                "/v1/ios/sales_reports/analytics_metrics",
                params,
            )

        @self.tool(
            mcp,
            name="sources_metrics",
            title="Sources Metrics",
        )
        async def sources_metrics(
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs you manage", min_length=1),
            ],
            countries: Annotated[
                str,
                Field(description="Comma-separated iTunes country codes", min_length=2),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            limit: Annotated[
                Optional[int],
                Field(description="Maximum reports to retrieve (max 6000)", ge=1, le=6000, default=None),
            ] = None,
            offset: Annotated[
                Optional[int],
                Field(description="Offset for pagination", ge=0, default=None),
            ] = None,
        ) -> dict:
            """Get App Store metrics by traffic source for connected apps."""

            params = {
                "app_ids": app_ids,
                "countries": countries,
                "start_date": validate_date_format(start_date),
                "end_date": validate_date_format(end_date),
            }
            if limit is not None:
                params["limit"] = limit
            if offset is not None:
                params["offset"] = offset

            return await self.make_request(
                "/v1/ios/sales_reports/sources_metrics",
                params,
            )

        @self.tool(
            mcp,
            name="sales_reports",
            title="Sales Reports",
        )
        async def sales_reports(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system for the report"),
            ],
            app_ids: Annotated[
                str,
                Field(description="Comma-separated app IDs you manage", min_length=1),
            ],
            countries: Annotated[
                str,
                Field(description="Comma-separated country codes", min_length=2),
            ],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity for aggregation"),
            ],
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
        ) -> dict:
            """Get downloads and revenue sales report for connected apps."""

            params = {
                "app_ids": app_ids,
                "countries": countries,
                "date_granularity": date_granularity,
                "start_date": validate_date_format(start_date),
                "end_date": validate_date_format(end_date),
            }

            return await self.make_request(
                f"/v1/{os}/sales_reports",
                params,
            )

        @self.tool(
            mcp,
            name="unified_sales_reports",
            title="Unified Sales Reports",
        )
        async def unified_sales_reports(
            start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
            end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
            date_granularity: Annotated[
                Literal["daily", "weekly", "monthly", "quarterly"],
                Field(description="Granularity for aggregation"),
            ],
            unified_app_ids: Annotated[
                Optional[str],
                Field(description="Comma-separated unified app IDs", default=None),
            ] = None,
            itunes_app_ids: Annotated[
                Optional[str],
                Field(description="Comma-separated iTunes app IDs", default=None),
            ] = None,
            android_app_ids: Annotated[
                Optional[str],
                Field(description="Comma-separated Android app IDs", default=None),
            ] = None,
            countries: Annotated[
                Optional[str],
                Field(description="Comma-separated country codes", default=None),
            ] = None,
        ) -> dict:
            """Get unified downloads and revenue sales report for connected apps."""

            params = {
                "date_granularity": date_granularity,
                "start_date": validate_date_format(start_date),
                "end_date": validate_date_format(end_date),
            }

            app_id_params = {
                "unified_app_ids": unified_app_ids,
                "itunes_app_ids": itunes_app_ids,
                "android_app_ids": android_app_ids,
            }

            if not any(value for value in app_id_params.values()):
                raise ToolError(
                    "Provide at least one of unified_app_ids, itunes_app_ids, or android_app_ids",
                )

            for key, value in app_id_params.items():
                if value:
                    params[key] = value

            if countries:
                params["countries"] = countries

            return await self.make_request(
                "/v1/unified/sales_reports",
                params,
            )
