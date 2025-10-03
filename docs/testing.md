# Testing Guide

This repository ships multiple test layers so contributors can validate changes quickly and with confidence.  The table below shows which suites require a live Sensor Tower token and which ones are safe to run offline.

| Suite | Command | Live Token Required? | Purpose |
| --- | --- | --- | --- |
| Unit & metadata checks | `uv run pytest` | No | Validates tool registration, structured output, and helper modules without hitting the live API. |
| Quick structural check | `uv run pytest tests/test_result_normalization.py` | No | Fast sanity test while iterating on tool logic. |
| Live MCP smoke | `uv run pytest -m live_api` | Yes (`SENSOR_TOWER_API_TOKEN`) | Calls every registered MCP tool via the HTTP gateway to confirm live API compatibility. |
| Individual live shard | `uv run pytest tests/test_live_api_tools.py -k get_creatives` | Yes | Diagnose a single tool while developing parameters. |

## Prerequisites

1. Install dependencies with the testing extras:
   ```bash
   uv sync --extra test
   ```
2. Export a token when running live suites:
   ```bash
   export SENSOR_TOWER_API_TOKEN="st_xxxxxxxxx"
   ```
3. Start the MCP server locally before invoking `-m live_api` suites.  The HTTP transport listens on `http://localhost:8666` by default:
   ```bash
   uv run python -m sensortower_mcp.server --transport http --port 8666
   ```

## Marker Usage

- `@pytest.mark.live_api` wraps tests that make real HTTP requests.  Use `-m live_api` to run only those tests or `-m "not live_api"` to exclude them.
- Pytest is configured with `asyncio_mode=auto`, so asynchronous fixtures default to function scope.

## Manual Smoke Scripts

Manual helpers live in the `manual/` directory.  They are not part of continuous integration but remain useful when verifying a released package:

- `manual/search_entities_fix.py` – executes the schema transformation sample and optionally exercises the published PyPI package’s `search_entities` tool when a token is available.
- `manual/search_entities_mcp.py` – spins up the server in stdio mode and issues JSON-RPC requests against the MCP entry point.

Run them directly with `python manual/<script>.py`; each exits with `0` on success.

## Legacy Scripts

Any previous top-level `test_*.py` files have been moved under `manual/` (or removed if empty) to keep pytest discovery focused on `tests/`.  If you need to create new manual harnesses, place them alongside the existing scripts and document their usage here.

## CI Recommendations

A typical pipeline can stage the suites as follows:

1. `ruff check --fix` (already part of the developer workflow)
2. `uv run pytest` (offline, fast)
3. `uv run pytest -m live_api` (optional nightly/approved job; requires `SENSOR_TOWER_API_TOKEN` and a running MCP server)

Logging artefacts (e.g., `server.log`, `tests/test_report.txt`) should be uploaded when live jobs run to aid debugging.

## Troubleshooting

| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| Live tests return `401 Unauthorized` | Missing or invalid token | Re-export `SENSOR_TOWER_API_TOKEN` and ensure it belongs to an account with API access. |
| Live tests return `422 Validation Error` | Arguments drifted from API expectations | Adjust payloads in `src/sensortower_mcp/tool_examples.py` and sync fixtures/tests. |
| `pytest` warns about skipped manual scripts | You invoked scripts in `manual/` via pytest | Run manual smoke tests directly with `python manual/<script>.py`. |

Following this checklist keeps the repository predictable for collaborators and external contributors alike.
