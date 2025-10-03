"""Live API smoke tests grouped by tool families."""

from __future__ import annotations

import asyncio
import os
from collections import defaultdict
from typing import Dict, Tuple

import httpx
import pytest

from sensortower_mcp.tool_examples import TOOL_ARGUMENT_EXAMPLES
from tests.tool_manifest import build_tool_manifest, ToolManifestEntry

try:  # pragma: no cover - optional when running via pytest
    from tests.conftest import MCP_JSON_HEADERS  # type: ignore
except Exception:  # pragma: no cover - script execution fallback
    MCP_JSON_HEADERS = {"Accept": "application/json, text/event-stream"}

try:  # pragma: no cover - optional when running via pytest
    from tests.jsonrpc import build_tool_payload  # type: ignore
except Exception:  # pragma: no cover - script execution fallback
    def build_tool_payload(tool: str, arguments: dict | None = None, request_id: str | None = None) -> dict:
        if arguments is None:
            arguments = {}
        return {"tool": tool, "arguments": arguments}

TOOL_ENDPOINT = os.getenv("MCP_TOOL_ENDPOINT", "/legacy/tools/invoke")

MANIFEST = build_tool_manifest()
CATEGORY_TO_ENTRIES: Dict[str, list[ToolManifestEntry]] = defaultdict(list)
for entry in MANIFEST:
    CATEGORY_TO_ENTRIES[entry.category].append(entry)


@pytest.fixture(scope="session")
def live_api_cache() -> Dict[Tuple[str, Tuple[Tuple[str, str], ...]], httpx.Response]:
    return {}


async def _invoke_tool(
    entry: ToolManifestEntry,
    base_url: str,
    token: str,
    cache: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], httpx.Response],
) -> httpx.Response:
    record = TOOL_ARGUMENT_EXAMPLES.get(entry.name)
    if record is None:
        pytest.skip("No live payload defined")
    if "skip_reason" in record:
        pytest.skip(record["skip_reason"])

    arguments = record.get("arguments", {})
    cache_key = (entry.name, tuple(sorted(arguments.items())))
    if cache_key in cache:
        return cache[cache_key]

    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(45.0),
        headers=MCP_JSON_HEADERS,
    ) as client:
        response = await client.post(
            TOOL_ENDPOINT,
            json=build_tool_payload(entry.name, arguments),
        )
    cache[cache_key] = response
    await asyncio.sleep(0.25)
    return response


@pytest.mark.live_api
@pytest.mark.asyncio
@pytest.mark.parametrize("entry", CATEGORY_TO_ENTRIES.get("AppAnalysis", []), ids=lambda e: e.name)
async def test_live_app_analysis(entry, base_url: str, token: str, live_api_cache) -> None:
    response = await _invoke_tool(entry, base_url, token, live_api_cache)
    assert response.status_code < 500, (
        f"Tool {entry.name} responded with {response.status_code}: {response.text[:200]}"
    )


@pytest.mark.live_api
@pytest.mark.asyncio
@pytest.mark.parametrize("entry", CATEGORY_TO_ENTRIES.get("MarketAnalysis", []), ids=lambda e: e.name)
async def test_live_market_analysis(entry, base_url: str, token: str, live_api_cache) -> None:
    response = await _invoke_tool(entry, base_url, token, live_api_cache)
    assert response.status_code < 500, (
        f"Tool {entry.name} responded with {response.status_code}: {response.text[:200]}"
    )


@pytest.mark.live_api
@pytest.mark.asyncio
@pytest.mark.parametrize("entry", CATEGORY_TO_ENTRIES.get("StoreMarketing", []), ids=lambda e: e.name)
async def test_live_store_marketing(entry, base_url: str, token: str, live_api_cache) -> None:
    response = await _invoke_tool(entry, base_url, token, live_api_cache)
    assert response.status_code < 500, (
        f"Tool {entry.name} responded with {response.status_code}: {response.text[:200]}"
    )


@pytest.mark.live_api
@pytest.mark.asyncio
@pytest.mark.parametrize("entry", CATEGORY_TO_ENTRIES.get("SearchDiscovery", []), ids=lambda e: e.name)
async def test_live_search_discovery(entry, base_url: str, token: str, live_api_cache) -> None:
    response = await _invoke_tool(entry, base_url, token, live_api_cache)
    assert response.status_code < 500, (
        f"Tool {entry.name} responded with {response.status_code}: {response.text[:200]}"
    )


@pytest.mark.live_api
@pytest.mark.asyncio
@pytest.mark.parametrize("entry", CATEGORY_TO_ENTRIES.get("Utility", []), ids=lambda e: e.name)
async def test_live_utilities(entry, base_url: str, token: str, live_api_cache) -> None:
    response = await _invoke_tool(entry, base_url, token, live_api_cache)
    assert response.status_code < 500, (
        f"Tool {entry.name} responded with {response.status_code}: {response.text[:200]}"
    )
