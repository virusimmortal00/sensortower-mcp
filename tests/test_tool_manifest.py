"""Unit coverage derived from the shared tool manifest."""

from __future__ import annotations

import asyncio

import pytest

from tests.tool_manifest import ToolManifestEntry


@pytest.mark.asyncio
async def test_tool_invokes_with_example(tool_entry: ToolManifestEntry) -> None:
    if tool_entry.name == "health_check":
        pytest.skip("health_check relies on CLI arguments")

    example = tool_entry.example or {}
    if "skip_reason" in example:
        pytest.skip(example["skip_reason"])

    arguments = dict(tool_entry.example_arguments)
    result = tool_entry.function(**arguments)

    if asyncio.iscoroutine(result) or isinstance(result, asyncio.Task):
        result = await result
    elif isinstance(result, asyncio.Future):
        result = await result

    assert result is not None
    assert isinstance(result, dict), "Tool results should always be dictionary payloads"
    if tool_entry.endpoint_path:
        endpoint = result.get("endpoint") or result.get("data", {}).get("endpoint")
        assert endpoint, "Mock response should include requested endpoint"
