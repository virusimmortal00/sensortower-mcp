"""Shared manifest fixture for Sensor Tower MCP tools."""

from __future__ import annotations

import asyncio
import inspect
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import pytest

from sensortower_mcp.base import SensorTowerTool
from sensortower_mcp.tool_examples import TOOL_ARGUMENT_EXAMPLES
from sensortower_mcp.tools import (
    AppAnalysisTools,
    MarketAnalysisTools,
    SearchDiscoveryTools,
    StoreMarketingTools,
    UtilityTools,
    YourMetricsTools,
)


class _MockResponse:
    """Lightweight stand-in for httpx.Response used in manifest tests."""

    def __init__(self, endpoint: str, params: Dict[str, Any]) -> None:
        self._payload = {"endpoint": endpoint, "params": params}

    def raise_for_status(self) -> None:  # pragma: no cover - no-op
        return None

    def json(self) -> Dict[str, Any]:
        return self._payload


class _MockAsyncClient:
    """Minimal async client matching the interface expected by SensorTowerTool."""

    async def get(self, endpoint: str, params: Dict[str, Any]) -> _MockResponse:
        await asyncio.sleep(0)
        return _MockResponse(endpoint, params)


class _RegisteredTool:
    def __init__(
        self,
        name: str,
        fn: Any,
        *,
        description: str | None = None,
        annotations: Dict[str, Any] | None = None,
        meta: Dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.fn = fn
        self.description = description or ""
        self.annotations: Dict[str, Any] = annotations or {}
        self.meta: Dict[str, Any] = meta or {}

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


class _MockMCP:
    """Simplified FastMCP substitute capturing registered tools."""

    def __init__(self) -> None:
        self.tools: Dict[str, _RegisteredTool] = {}

    def tool(
        self,
        func: Any | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        annotations: Dict[str, Any] | None = None,
        meta: Dict[str, Any] | None = None,
    ):
        if func is not None:
            resolved_name = name or func.__name__
            tool = _RegisteredTool(
                resolved_name,
                func,
                description=description,
                annotations=annotations,
                meta=meta,
            )
            self.tools[resolved_name] = tool
            return tool

        if name is None:
            raise ValueError("MockMCP.tool requires a tool name when used as a decorator factory")

        def decorator(fn: Any) -> _RegisteredTool:
            return self.tool(
                fn,
                name=name,
                description=description,
                annotations=annotations,
                meta=meta,
            )

        return decorator

    def resource(self, *_args: Any, **_kwargs: Any):  # pragma: no cover - unused in tests
        def decorator(fn: Any) -> Any:
            return fn

        return decorator

    def custom_route(self, *_args: Any, **_kwargs: Any):  # pragma: no cover - unused in tests
        def decorator(fn: Any) -> Any:
            return fn

        return decorator


@dataclass(frozen=True)
class ToolManifestEntry:
    """Captured metadata for a registered MCP tool."""

    category: str
    name: str
    tool: Any
    function: Any
    signature: inspect.Signature
    doc: str
    metadata: Dict[str, Any]
    example: Dict[str, Any] | None
    endpoint_path: str | None

    @property
    def example_arguments(self) -> Dict[str, Any]:
        return (self.example or {}).get("arguments", {})


_TOOL_CLASSES: List[type] = [
    AppAnalysisTools,
    StoreMarketingTools,
    MarketAnalysisTools,
    YourMetricsTools,
    SearchDiscoveryTools,
    UtilityTools,
]


def build_tool_manifest() -> List[ToolManifestEntry]:
    """Register all tools on a FastMCP instance and capture callable metadata."""
    mcp = _MockMCP()
    client = _MockAsyncClient()
    token = "dummy-token"

    entries: List[ToolManifestEntry] = []
    endpoint_pattern = re.compile(r"self\.(?:make_request|client\.(?:get|post))\(f?\"([^\"]+)\"")

    for tool_cls in _TOOL_CLASSES:
        before = set(mcp.tools.keys())
        if issubclass(tool_cls, SensorTowerTool):
            instance = tool_cls(client, token)  # type: ignore[misc]
        else:
            instance = tool_cls()  # type: ignore[call-arg]
        instance.register_tools(mcp)  # type: ignore[attr-defined]
        after = set(mcp.tools.keys())
        new_names = sorted(after - before)
        category = tool_cls.__name__.replace("Tools", "")
        for name in new_names:
            tool = mcp.tools[name]
            doc = inspect.getdoc(tool.fn) or ""
            signature = inspect.signature(tool.fn)
            metadata = tool.meta or {}
            example = TOOL_ARGUMENT_EXAMPLES.get(name)
            endpoint_path = None
            try:
                source = inspect.getsource(tool.fn)
                match = endpoint_pattern.search(source)
                if match:
                    endpoint_path = match.group(1)
            except (OSError, TypeError):  # pragma: no cover
                endpoint_path = None
            entries.append(
                ToolManifestEntry(
                    category=category,
                    name=name,
                    tool=tool,
                    function=tool.fn,
                    signature=signature,
                    doc=doc,
                    metadata=metadata,
                    example=example,
                    endpoint_path=endpoint_path,
                )
            )

    entries.sort(key=lambda item: item.name)
    return entries


_MANIFEST_ENTRIES = build_tool_manifest()


@pytest.fixture(scope="session")
def tool_manifest() -> List[ToolManifestEntry]:
    return _MANIFEST_ENTRIES


@pytest.fixture(scope="session", params=_MANIFEST_ENTRIES, ids=lambda entry: entry.name)
def tool_entry(request) -> ToolManifestEntry:
    """Parametrized fixture yielding each tool entry once."""
    return request.param


@pytest.fixture(scope="session")
def tool_manifest_by_name(tool_manifest: List[ToolManifestEntry]) -> Dict[str, ToolManifestEntry]:
    return {entry.name: entry for entry in tool_manifest}
