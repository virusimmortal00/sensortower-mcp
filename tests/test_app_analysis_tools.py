"""Unit tests for app analysis tools specific behaviors."""

import inspect

import pytest

from src.sensortower_mcp.tools.app_analysis import AppAnalysisTools


class _RecordingAppAnalysisTools(AppAnalysisTools):
    """Capture outgoing requests for assertion without hitting the API."""

    def __init__(self):
        super().__init__(client=None, token="dummy-token")
        self.last_request: tuple[str, dict] | None = None

    async def make_request(self, endpoint: str, params: dict):  # type: ignore[override]
        self.last_request = (endpoint, params)
        return {"ok": True}


class _RegisteredTool:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class _MockFastMCP:
    """Collect tools registered via the helper decorator."""

    def __init__(self):
        self.tools = {}

    def tool(self, *, name, description=None, annotations=None, meta=None):
        def decorator(fn):
            registered = _RegisteredTool(fn)
            self.tools[name] = registered
            return registered

        return decorator


@pytest.mark.asyncio
async def test_get_creatives_forwards_ad_types():
    mock_mcp = _MockFastMCP()
    tools = _RecordingAppAnalysisTools()
    tools.register_tools(mock_mcp)

    result = await mock_mcp.tools["get_creatives"](
        os="ios",
        app_ids="123",
        start_date="2024-01-01",
        countries="US",
        networks="Instagram",
        ad_types="video",
    )

    assert tools.last_request is not None
    endpoint, params = tools.last_request
    assert endpoint.endswith("/ad_intel/creatives")
    assert params["ad_types"] == "video"
    assert result == {"ok": True}


def test_get_creatives_requires_ad_types():
    mock_mcp = _MockFastMCP()
    tools = _RecordingAppAnalysisTools()
    tools.register_tools(mock_mcp)

    signature = inspect.signature(mock_mcp.tools["get_creatives"].fn)
    param = signature.parameters["ad_types"]
    assert param.default is inspect._empty


@pytest.mark.asyncio
async def test_get_category_history_normalizes_chart_types():
    mock_mcp = _MockFastMCP()
    tools = _RecordingAppAnalysisTools()
    tools.register_tools(mock_mcp)

    await mock_mcp.tools["get_category_history"](
        os="ios",
        app_ids="284882215",
        category="6005",
        chart_type_ids=" topfreeapplications , topgrossingapplications ",
        start_date="2024-01-01",
        end_date="2024-01-07",
        countries="US",
    )

    assert tools.last_request is not None
    endpoint, params = tools.last_request
    assert endpoint.endswith("/category/category_history")
    assert params["category"] == "6005"
    assert params["chart_type_ids"] == "topfreeapplications,topgrossingapplications"
