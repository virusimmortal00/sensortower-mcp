# MCP Tool Testing Roadmap

This plan describes everything required to verify that **every MCP tool** works end-to-end via HTTP and native JSON-RPC transports.

## 1. Normalize HTTP Access
- **Legacy Endpoint:** Keep (or rename) `/legacy/tools/invoke` as the documented HTTP gateway. It should accept `{"tool": "name", "arguments": {...}}` and return `{"tool": ..., "result": ...}` without requiring JSON-RPC session IDs.
- **Client Headers:** Document that all callers must send `Accept: application/json, text/event-stream`. Update scripts/README accordingly.
- **Smoke Test:** Add an automated suite that iterates all tools via this endpoint to catch regressions early.

## 2. Fix Tool Output Shapes
- **Structured Output:** Ensure each tool returns a dict (or explicitly populated `structured_content`) instead of raw lists to satisfy FastMCP expectations.
- **Unit Coverage:** Add tests per tool module asserting output structure so HTTP serialization never fails.

## 3. Resolve 4xx Live API Errors
- **Test Fixtures:** Update argument payloads in `tool_examples.py`/`tool_manifest.py` to match current API requirements (e.g., include `period`, valid networks, categories).
- **Documentation:** Record endpoints needing customer-owned app data and skip tests with clear reasons when real data is unavailable.

## 4. Strengthen Test Harness
- **Comprehensive Loop:** Extend `test_manual.py` (or create `test_all_tools.py`) to invoke every tool via HTTP; mark it with `pytest.mark.live_api`.
- **Schematics Check:** Where feasible, assert response matches the tool’s schema or stored sample to detect API drift.
- **Deployment Script:** After CLI/Docker checks, have `test_deployment.py` spin up the server once and run the same tool loop.

## 5. Client-Side Session Coverage
- **fastmcp.Client:** Add a test that connects via JSON-RPC `fastmcp.Client("http://localhost:8666")` and calls a handful of tools to verify the official transport still operates.
- **STDIO Mode:** Document how to run the server in stdio and exercise tools via an MCP client for agent integration confidence.

## 6. Continuous Verification
- **CI Pipeline:** Incorporate `ruff`, unit tests, and an optional live smoke job (requires `SENSOR_TOWER_API_TOKEN`) that runs the comprehensive tool suite.
- **Regression Fixtures:** Maintain redacted sample responses in `tests/fixtures/` and wrap them in regression tests to reduce reliance on live calls.
- **Dependency Hygiene:** Keep `uv.lock` current (fastmcp/httpx/aiohttp). Re-run the suite after updates to catch protocol/library changes.

## 7. Housekeeping & Documentation
- **README Updates:** Explain how to provision the token, install test extras (`uv sync --extra test`), start the server, and run the live suite.
- **Artifacts:** Persist `tests/test_report.txt` and `server.log` after runs (especially in CI) for debugging.
- **Skip Policy:** Clearly list tools or parameters that require special access so skipped tests are intentional, not surprises.

Following this roadmap ensures every MCP tool can be validated end-to-end, both manually and in automation, keeping the Sensor Tower integration reliable.
