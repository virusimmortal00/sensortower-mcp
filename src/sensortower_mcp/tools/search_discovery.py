#!/usr/bin/env python3
"""Search and Discovery API tools for Sensor Tower MCP Server."""

from typing import Annotated, Literal, Optional, Union

from fastmcp import FastMCP
from pydantic import Field

from ..base import SensorTowerTool, validate_date_format, validate_os_parameter


class SearchDiscoveryTools(SensorTowerTool):
    """Tools for Search and Discovery API endpoints."""

    category = "SearchDiscovery"

    def register_tools(self, mcp: FastMCP) -> None:
        """Register all search and discovery tools with FastMCP."""

        @self.tool(
            mcp,
            name="search_entities",
            title="Search Entities",
        )
        async def search_entities(
            os: Annotated[
                Literal["ios", "android", "both_stores", "unified"],
                Field(description="Platform scope"),
            ],
            entity_type: Annotated[
                Literal["app", "publisher"],
                Field(description="Type of entity to search"),
            ],
            term: Annotated[
                str,
                Field(description="Search term"),
            ],
            limit: Annotated[
                int,
                Field(description="Maximum results", ge=1, le=250),
            ] = 100,
        ) -> dict:
            """Search for apps or publishers by name and metadata."""

            params = {
                "entity_type": entity_type,
                "term": term,
                "limit": limit,
            }
            raw_data = await self.make_request(
                f"/v1/{os}/search_entities",
                params,
            )

            return self.normalize_result(
                raw_data,
                {
                    "query_term": term,
                    "entity_type": entity_type,
                    "platform": os,
                },
            )

        @self.tool(
            mcp,
            name="get_publisher_apps",
            title="Get Publisher Apps",
        )
        async def get_publisher_apps(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system"),
            ],
            publisher_id: Annotated[str, Field(description="Publisher identifier", min_length=1)],
            limit: Annotated[
                int,
                Field(description="Maximum results", ge=1, le=250),
            ] = 20,
            offset: Annotated[
                int,
                Field(description="Pagination offset", ge=0),
            ] = 0,
            include_count: Annotated[
                bool,
                Field(description="Include total count"),
            ] = False,
        ) -> dict:
            """Retrieve apps for the specified publisher."""

            params = {
                "publisher_id": publisher_id,
                "limit": limit,
                "offset": offset,
                "include_count": include_count,
            }
            raw_data = await self.make_request(
                f"/v1/{os}/publisher/publisher_apps",
                params,
            )

            return self.normalize_result(
                raw_data,
                {
                    "publisher_id": publisher_id,
                    "limit": limit,
                    "offset": offset,
                    "platform": os,
                },
            )

        @self.tool(
            mcp,
            name="get_unified_publisher_apps",
            title="Get Unified Publisher Apps",
        )
        async def get_unified_publisher_apps(
            unified_id: Annotated[str, Field(description="Unified publisher identifier", min_length=1)],
        ) -> dict:
            """Retrieve unified publisher details and associated apps."""

            params = {"unified_id": unified_id}
            data = await self.make_request(
                "/v1/unified/publishers/apps",
                params,
            )
            return self.normalize_result(data, {"unified_id": unified_id})

        @self.tool(
            mcp,
            name="get_app_ids_by_category",
            title="Get App IDs By Category",
        )
        async def get_app_ids_by_category(
            os: Annotated[
                Literal["ios", "android"],
                Field(description="Operating system"),
            ],
            category: Annotated[
                Union[int, str],
                Field(description="Category identifier"),
            ],
            start_date: Annotated[
                Optional[str],
                Field(description="Minimum start date in YYYY-MM-DD format", default=None),
            ] = None,
            updated_date: Annotated[
                Optional[str],
                Field(description="Updated date in YYYY-MM-DD format", default=None),
            ] = None,
            offset: Annotated[
                Optional[int],
                Field(description="Offset for pagination", ge=0, default=None),
            ] = None,
            limit: Annotated[
                int,
                Field(description="Maximum app IDs returned", ge=1, le=10000),
            ] = 1000,
        ) -> dict:
            """Retrieve app IDs by category and release/update date filters."""

            os_value = validate_os_parameter(os, ["ios", "android"])
            params = {
                "category": category,
                "limit": limit,
            }

            if start_date:
                params["start_date"] = validate_date_format(start_date)
            if updated_date:
                params["updated_date"] = validate_date_format(updated_date)
            if offset is not None:
                params["offset"] = offset

            raw_data = await self.make_request(
                f"/v1/{os_value}/apps/app_ids",
                params,
            )

            metadata = {
                "category": category,
                "platform": os_value,
                "limit": limit,
            }
            if offset is not None:
                metadata["offset"] = offset

            return self.normalize_result(raw_data, metadata)
