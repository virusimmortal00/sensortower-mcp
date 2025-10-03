# Sensor Tower MCP Server

An MCP server that lets agents use Sensor Tower APIs for ads, market, and utility data—no custom HTTP clients needed.

## Features
- FastMCP-based MCP server with structured tool registration.
- Coverage for App Analysis, Market Analysis, Store Marketing, Usage Intelligence, and utility endpoints.
- Built-in input normalization for common parameter issues (e.g., ad network aliases).
- Bundled OpenAPI specifications (`swaggerdocs/`) for reference and validation.

## Requirements
- Python 3.10+
- Sensor Tower API token (`SENSOR_TOWER_API_TOKEN` environment variable)
- (Optional) Docker for container-based deployment

## Quick Start
1. Install dependencies and the package:
   ```bash
   uv sync  # or: pip install -e .[test]
   ```
2. Export your API token:
   ```bash
   export SENSOR_TOWER_API_TOKEN="st_xxxxxxxxx"
   ```
3. Launch the MCP server:
   ```bash
   python -m sensortower_mcp.server
   ```
   The FastMCP CLI will expose the registered tools to your orchestrator.

## Client setup (Cursor, Claude, Docker)

### Cursor
- Settings → MCP → Add Server → Command:
  - Command: `python`
  - Arguments: `-m sensortower_mcp.server`
  - Env: set `SENSOR_TOWER_API_TOKEN`

Example JSON (if Cursor asks for a block):
```json
{
  "name": "sensortower",
  "command": "python",
  "args": ["-m", "sensortower_mcp.server"],
  "env": { "SENSOR_TOWER_API_TOKEN": "st_xxxxxxxxx" }
}
```

### Claude (Desktop/Web with MCP)
- Add a custom MCP server in Settings → Integrations → Model Context Protocol.
- Use the same command/args/env as above.

Minimal config snippet some clients accept:
```json
{
  "mcpServers": {
    "sensortower": {
      "command": "python",
      "args": ["-m", "sensortower_mcp.server"],
      "env": { "SENSOR_TOWER_API_TOKEN": "st_xxxxxxxxx" }
    }
  }
}
```

### Docker
Build and run the server container locally:
```bash
docker build -t sensortower-mcp .
docker run --rm \
  -e SENSOR_TOWER_API_TOKEN=st_xxxxxxxxx \
  -p 8666:8666 \
  sensortower-mcp
```

Or with Compose (uses `docker-compose.yml`):
```bash
docker compose up -d
```

Then point your MCP client at the local command as usual, or at `http://localhost:8666` if your client supports HTTP MCP transport.

### HTTP Invocation Shortcut
When exercising the server over HTTP without a JSON-RPC session, target the legacy gateway exposed at `/legacy/tools/invoke`:

```bash
curl \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -X POST "http://localhost:8666/legacy/tools/invoke" \
  -d '{
        "tool": "get_creatives",
        "arguments": {
          "os": "ios",
          "app_ids": "835599320",
          "start_date": "2023-01-01",
          "end_date": "2023-01-31",
          "countries": "US",
          "networks": "Instagram,Unity",
          "ad_types": "video"
        }
      }'
```

The endpoint always responds with `{ "tool": "<name>", "result": <structured payload> }`. The combined `Accept` header is mandatory because FastMCP's HTTP transport performs content negotiation that requires both `application/json` and `text/event-stream` to be present; omitting it can yield 406 errors in some clients. The server automatically widens overly strict `Accept` values from known MCP clients, but external tooling should set the header explicitly to avoid regression issues.

## Usage Example
Calling the creatives tool from FastMCP requires the `ad_types` parameter, which Sensor Tower marks as mandatory:
```python
from fastmcp import FastMCP
from sensortower_mcp.server import build_server

mcp = FastMCP("sensortower")
server = build_server(api_token="st_xxxxxxxxx")
server.register(mcp)

result = mcp.invoke_tool(
    "get_creatives",
    {
        "os": "ios",
        "app_ids": "284882215",
        "start_date": "2024-01-01",
        "countries": "US",
        "networks": "Instagram",
        "ad_types": "video"
    }
)
```

## Testing
Install the testing extras and exercise the suites using `uv` (preferred) or the active virtualenv:
```bash
uv sync --extra test
uv run pytest tests/test_result_normalization.py  # fast structural sanity check
uv run pytest                                     # full offline suite
```

Live API exercises are marked with `@pytest.mark.live_api` and require a valid `SENSOR_TOWER_API_TOKEN`. Execute only that suite with:
```bash
uv run pytest -m live_api
```
The MCP server must be running locally (see Quick Start), and HTTP callers should send `Accept: application/json, text/event-stream`—or use the legacy gateway, which automatically normalizes the header when known MCP clients connect.

Manual smoke scripts that hit the deployed package or raw MCP transports have been moved to `manual/`. They are not part of automated CI but remain available for ad-hoc verification:
- `manual/search_entities_fix.py` – verifies the published package’s `search_entities` helper.
- `manual/search_entities_mcp.py` – end-to-end JSON-RPC smoke test for `search_entities`.

Run them with `python manual/<script>.py`; each script prints a summary and exits 0/1 accordingly.

See `docs/testing.md` for the full test matrix, CI recommendations, and troubleshooting tips.

## Release Highlights
- **1.2.10**: Expands tool docstrings with metadata-driven usage hints so MCP clients surface examples and notes without extra manual edits.
- **1.2.1**: Ensures `get_creatives` forwards the required `ad_types` query parameter, preventing 422 responses from Sensor Tower. Adds regression coverage so missing parameters are detected before release.

## Contributing
Issues and merge requests are welcome. Please include tests for bug fixes and keep API examples in the README and `README-pypi.md` synchronized.
