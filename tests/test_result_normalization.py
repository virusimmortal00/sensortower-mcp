"""Tests for SensorTowerTool result normalization."""

import pytest

from sensortower_mcp.base import SensorTowerTool


class _RegisteredTool:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class _StubMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, *, name, description=None, annotations=None, meta=None):
        def decorator(fn):
            wrapped = _RegisteredTool(fn)
            self.tools[name] = wrapped
            return wrapped

        return decorator


class _DummyTool(SensorTowerTool):
    async def make_request(self, endpoint, params):  # pragma: no cover
        raise AssertionError("make_request should not be called in tests")

    def register_to_mcp(self, mcp):
        @self.tool(mcp, name="list_tool")
        async def list_tool() -> dict:
            return [1, 2, 3]

        @self.tool(mcp, name="scalar_tool")
        async def scalar_tool() -> dict:
            return 7


@pytest.mark.asyncio
async def test_list_result_wrapped_with_metadata():
    mcp = _StubMCP()
    tool = _DummyTool(client=None, token="token")
    tool.register_to_mcp(mcp)

    result = await mcp.tools["list_tool"]()
    assert isinstance(result, dict)
    assert result["items"] == [1, 2, 3]
    assert result["total_count"] == 3


@pytest.mark.asyncio
async def test_scalar_result_wrapped_with_value_key():
    mcp = _StubMCP()
    tool = _DummyTool(client=None, token="token")
    tool.register_to_mcp(mcp)

    result = await mcp.tools["scalar_tool"]()
    assert isinstance(result, dict)
    assert result["value"] == 7
