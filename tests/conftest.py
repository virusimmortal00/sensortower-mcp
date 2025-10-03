"""Shared test fixtures for Sensor Tower MCP test suite."""

import os
import sys
from pathlib import Path

import pytest

MCP_JSON_HEADERS = {"Accept": "application/json, text/event-stream"}
LEGACY_TOOL_ENDPOINT = os.getenv("MCP_TOOL_ENDPOINT", "/legacy/tools/invoke")


# Ensure the package under test can be imported without installing.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:  # pragma: no cover - optional dependency
    pass


@pytest.fixture(scope="session")
def token() -> str:
    """Sensor Tower API token loaded from environment or .env; skip if absent."""
    value = os.getenv("SENSOR_TOWER_API_TOKEN")
    if not value:
        pytest.skip("SENSOR_TOWER_API_TOKEN not configured; skipping token-dependent tests")
    return value


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the local MCP server under test."""
    return os.getenv("MCP_BASE_URL", "http://localhost:8666")


@pytest.fixture(scope="session")
def mcp_headers() -> dict[str, str]:
    """Default headers required for FastMCP HTTP transport."""
    return MCP_JSON_HEADERS.copy()


@pytest.fixture(scope="session")
def tool_endpoint() -> str:
    """HTTP path for legacy tool invocation endpoint."""
    return LEGACY_TOOL_ENDPOINT

pytest_plugins = ("tests.tool_manifest",)
