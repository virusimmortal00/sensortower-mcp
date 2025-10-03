#!/usr/bin/env python3
"""
Base classes and utilities for Sensor Tower MCP tools
"""

import asyncio
import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional

import httpx

from fastmcp.exceptions import ToolError
from fastmcp import FastMCP

from .tool_examples import TOOL_ARGUMENT_EXAMPLES

DEFAULT_TOOL_VERSION = "1.0"


def _to_title(name: str) -> str:
    """Convert snake_case identifiers into title case."""

    if not name:
        return ""
    return " ".join(part.capitalize() for part in name.split("_"))


def build_tool_annotations(
    *,
    title: str,
    read_only: bool = True,
    idempotent: bool = True,
    open_world: bool = True,
) -> Dict[str, Any]:
    """Create a consistent annotations payload for tool decorators."""

    return {
        "title": title,
        "readOnlyHint": read_only,
        "idempotentHint": idempotent,
        "openWorldHint": open_world,
    }


def build_decorator_meta(
    tool_name: str,
    *,
    category: Optional[str] = None,
    version: str = DEFAULT_TOOL_VERSION,
    **extra: Any,
) -> Dict[str, Any]:
    """Construct metadata for tool decorators including docs examples."""

    meta: Dict[str, Any] = {}
    if category:
        meta["category"] = category
    if version:
        meta["version"] = version

    docs_meta = build_tool_metadata(tool_name)
    if docs_meta:
        meta.update(docs_meta)

    if extra:
        meta.update(extra)

    return meta

class SensorTowerTool:
    """Base class for Sensor Tower API tools"""
    
    def __init__(self, client: httpx.AsyncClient, token: str):
        self.client = client
        self.token = token
    
    def get_auth_token(self) -> str:
        """Get authentication token"""
        return self.token
    
    async def make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Make authenticated request to Sensor Tower API with retries and backoff."""
        params["auth_token"] = self.get_auth_token()
        backoff_seconds = 0.5
        max_attempts = 5
        for attempt_index in range(max_attempts):
            try:
                response = await self.client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as status_error:
                status_code = status_error.response.status_code
                if status_code in {429, 500, 502, 503, 504} and attempt_index < (max_attempts - 1):
                    await asyncio.sleep(backoff_seconds)
                    backoff_seconds = min(backoff_seconds * 2.0, 8.0)
                    continue
                raise
            except (httpx.ReadTimeout, httpx.ConnectError):
                if attempt_index < (max_attempts - 1):
                    await asyncio.sleep(backoff_seconds)
                    backoff_seconds = min(backoff_seconds * 2.0, 8.0)
                    continue
                raise

    def build_meta(
        self,
        tool_name: str,
        *,
        category: Optional[str] = None,
        version: str = DEFAULT_TOOL_VERSION,
        **extra: Any,
    ) -> Dict[str, Any]:
        """Create decorator metadata with optional category and docs examples."""

        return build_decorator_meta(
            tool_name,
            category=category,
            version=version,
            **extra,
        )

    def build_annotations(
        self,
        tool_name: str,
        *,
        title: Optional[str] = None,
        **hints: Any,
    ) -> Dict[str, Any]:
        """Create standardized annotations for a tool decorator."""

        resolved_title = title or _to_title(tool_name)
        return build_tool_annotations(title=resolved_title, **hints)

    def create_task(self, coro, *, list_metadata: Optional[Dict[str, Any]] = None):
        """Create asyncio task for synchronous tool interface.

        FastMCP tools expect structured (dict-like) payloads. Wrapping the coroutine
        allows us to normalize list responses across every tool without changing
        the individual implementations.
        """

        async def _runner():
            try:
                raw_result = await coro
                return self.normalize_result(raw_result, list_metadata)
            except asyncio.CancelledError:
                # Allow upstream to handle cancellation cleanly
                raise

        return asyncio.create_task(_runner())

    def normalize_result(
        self, result: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Coerce tool results into dictionaries compatible with MCP clients."""

        if isinstance(result, dict):
            if metadata:
                # Metadata keys should not overwrite the main payload.
                merged = {**result}
                for key, value in metadata.items():
                    merged.setdefault(key, value)
                return merged
            return result

        if isinstance(result, list):
            payload: Dict[str, Any] = {
                "items": result,
                "total_count": len(result),
            }
            if metadata:
                payload.update({k: v for k, v in metadata.items() if k not in payload})
            return payload

        # Fallback for primitives/None – wrap so FastMCP receives a mapping.
        wrapped: Dict[str, Any] = {"value": result}
        if metadata:
            wrapped.update({k: v for k, v in metadata.items() if k not in wrapped})
        return wrapped

    def _attach_metadata(self, tool: Any, tool_name: str) -> None:
        """Enrich a registered tool with example metadata for downstream tests."""
        apply_tool_metadata(tool, tool_name)

    def tool(
        self,
        mcp: FastMCP,
        *,
        name: str,
        description: Optional[str] = None,
        title: Optional[str] = None,
        category: Optional[str] = None,
        annotations: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Callable[[Callable[..., Awaitable[Any]]], Any]:
        """Helper that registers an async tool with consistent metadata handling."""

        def decorator(func: Callable[..., Awaitable[Any]]):
            base_description = description or (inspect.getdoc(func) or name)
            resolved_annotations = annotations or self.build_annotations(
                name,
                title=title,
            )
            resolved_meta = meta or self.build_meta(
                name,
                category=category or getattr(self, "category", None),
            )

            # Enrich the description with metadata guidance so tooling consumers
            # always see an example or usage note alongside the terse docstring.
            doc_parts = [base_description.strip()]
            if isinstance(resolved_meta, dict):
                docs_meta = resolved_meta.get("docs")
                if isinstance(docs_meta, dict):
                    hint = docs_meta.get("hint")
                    if hint:
                        normalized_hint = hint.strip()
                        if not normalized_hint.lower().startswith("note:"):
                            normalized_hint = f"Note: {normalized_hint}"
                        doc_parts.append(normalized_hint)
                    example = docs_meta.get("example_snippet")
                    if example:
                        doc_parts.append(f"Example: {example}")

            func_description = "\n\n".join(part for part in doc_parts if part)

            @wraps(func)
            async def runner(*args: Any, **kwargs: Any) -> Dict[str, Any]:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result  # type: ignore[assignment]
                return self.normalize_result(result)

            runner.__doc__ = func_description

            return mcp.tool(
                name=name,
                description=func_description,
                annotations=resolved_annotations,
                meta=resolved_meta,
            )(runner)

        return decorator


def build_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """Create structured metadata with example arguments for the given tool."""
    record = TOOL_ARGUMENT_EXAMPLES.get(tool_name)
    if not record:
        return {}

    if record.get("skip_reason"):
        # Skip entries that are intentionally disabled (e.g., connected apps).
        return {"docs": {"hint": record["skip_reason"]}}

    arguments = record.get("arguments", {})
    example_snippet = format_example_snippet(tool_name, arguments)
    hint = record.get("hint") or (
        "Invoke with representative arguments shown below; see documentation for other options."
    )

    return {
        "docs": {
            "hint": hint,
            "example_arguments": arguments,
            "example_snippet": example_snippet,
        }
    }


def apply_tool_metadata(tool: Any, tool_name: str) -> None:
    """Attach generated metadata to the given FastMCP tool."""
    metadata = build_tool_metadata(tool_name)
    if not metadata:
        return

    existing_meta = getattr(tool, "meta", {}) or {}
    setattr(tool, "meta", {**existing_meta, **metadata})


def format_example_snippet(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Format a concise example call snippet for metadata and documentation."""
    if not arguments:
        return f"{tool_name}()"

    formatted_args = ", ".join(f"{key}={value!r}" for key, value in arguments.items())
    return f"{tool_name}({formatted_args})"

def wrap_list_response(data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap raw list responses in dictionary structure for MCP compliance"""
    if isinstance(data, list):
        return {
            "items": data,
            "total_count": len(data),
            **metadata
        }
    else:
        return data

def validate_os_parameter(os: str, allowed: list = None) -> str:
    """Validate operating system parameter"""
    if allowed is None:
        allowed = ["ios", "android", "unified"]
    
    normalized = os.lower()
    if normalized not in allowed:
        raise ToolError(f"Invalid OS parameter: {os}. Must be one of: {', '.join(allowed)}")

    return normalized

def validate_date_format(date_str: str) -> str:
    """Validate date format (YYYY-MM-DD)"""
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError as exc:
        raise ToolError(f"Invalid date format: {date_str}. Must be YYYY-MM-DD") from exc
