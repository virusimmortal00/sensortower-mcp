"""Helpers for constructing payloads for legacy MCP tool invocations."""

from __future__ import annotations

from typing import Any, Dict


def build_tool_payload(
    tool: str,
    arguments: Dict[str, Any] | None = None,
    request_id: str | None = None,
) -> Dict[str, Any]:
    """Return the simplified JSON body accepted by the legacy tool endpoint."""
    if arguments is None:
        arguments = {}
    return {"tool": tool, "arguments": arguments, "request_id": request_id}
