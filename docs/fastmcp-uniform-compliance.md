## FastMCP Uniform Compliance Plan

### Scope
- **Goal**: Make all Sensor Tower MCP tools uniformly adhere to FastMCP guidelines: async-first tools, strong parameter schemas, structured outputs, rich annotations/metadata, clean error reporting.

### Current State (Summary)
- **Strengths**: Tools grouped by category; registered with `@mcp.tool`; object-like returns ensure structured content; list responses normalized.
- **Gaps**:
  - Inconsistent param metadata (missing `Annotated`/`Field`, `Literal`/Enum in places).
  - Non-idiomatic async (sync wrappers returning `asyncio.create_task`).
  - Missing decorator-level `annotations` and `meta` (using post-hoc attribute mutation instead).
  - Output schemas are vague (`Dict[str, Any]` everywhere).
  - Validation errors use generic exceptions; no `ToolError` for user-facing input issues.
  - Server not hardened for duplicates or error masking.

### Conventions To Apply Everywhere
- **Async-first**: Define tools as `async def`; `await` HTTP calls; remove `create_task` pattern from tool defs.
- **Parameter schemas**:
  - Use `Literal`/Enum for enumerations (e.g., `os`, `time_range`, `measure`, `date_granularity`).
  - Use `Annotated[..., Field(...)]` for per-parameter descriptions and constraints.
  - Apply uniform constraints for common params (`os`, dates, time ranges, measures, device types).
- **Decorator metadata**:
  - Provide `annotations={"title", "readOnlyHint", "idempotentHint", "openWorldHint"}`.
  - Provide `meta={...}` at decorator time; do not mutate `tool.meta` after registration.
- **Structured outputs**: Keep list normalization to `{ items, total_count }` or adopt Pydantic models for strong schemas.
- **Error handling**: Use `ToolError` for user-facing validation issues; keep native exceptions for internal failures; consider `mask_error_details=True`.

### Phase 1 — Server + Conventions
1. Harden `FastMCP` init in `src/sensortower_mcp/server.py`:
   - `on_duplicate_tools="error"` to prevent silent replacement.
   - `mask_error_details=True` for safer client error surfaces.
2. Document and adopt the conventions above as code review gates.

Example (server init):
```python
self.mcp = FastMCP(
    "Sensor Tower",
    on_duplicate_tools="error",
    mask_error_details=True,
)
```

### Phase 2 — Tools Refactor (Module Pass)
Apply the following to each module: `app_analysis.py`, `market_analysis.py`, `store_marketing.py`, `your_metrics.py`, `search_discovery.py`, `utilities.py`.
- Convert all tools to `async def`; directly `await` HTTP calls.
- Replace `Dict[str, Any]` input/return types with:
  - Constrained params via `Literal`/Enum.
  - `Annotated[..., Field(...)]` for descriptions and validation.
  - Keep object-like returns; normalize lists.
- Add `@mcp.tool(..., annotations={...}, meta={...})` on every tool.
- Use `ToolError` for input validation failures.
- Keep behavior the same; no API path changes.

Example (signature refactor sketch):
```python
@mcp.tool(
    name="get_impressions",
    description="Get advertising impressions data for apps.",
    annotations={
        "title": "Get Impressions",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
    meta={"category": "AppAnalysis", "version": "1.0"},
)
async def get_impressions(
    os: Literal["ios", "android", "unified"],
    app_ids: Annotated[str, Field(description="Comma-separated app IDs (max 5)")],
    start_date: Annotated[str, Field(description="YYYY-MM-DD")],
    end_date: Annotated[str, Field(description="YYYY-MM-DD")],
    countries: Annotated[str, Field(description="Comma-separated country codes")],
    networks: Annotated[str, Field(description="Comma-separated ad networks")],
    date_granularity: Literal["daily", "weekly", "monthly"] = "daily",
) -> dict:
    # validate with existing helpers, convert ValueError -> ToolError
    ...
```

### Phase 3 — Output Schemas (Pilot)
- Introduce Pydantic output models for 2–3 high-traffic endpoints (e.g., `get_impressions`, `get_top_and_trending`).
- Verify clients/tests accept structured content and that schemas reflect the payload precisely.
- Decide on broader rollout after pilot.

Example (model sketch):
```python
class ImpressionsResponse(BaseModel):
    items: list[dict]
    total_count: int
```

### Phase 4 — Cleanup + Tests
- Replace `apply_tool_metadata` with decorator `meta=` where possible; remove legacy metadata mutation.
- Ensure param constraints uniform across modules (`os`, `time_range`, `measure`, `date`, `device_type`).
- Update tests to:
  - Expect decorator-provided `_meta` and `annotations`.
  - Use async tools (no `Task`-return assumptions).
- Run full test suite; fix regressions and lints.

### Work Items (Trackable)
- Harden FastMCP init in `server.py`.
- Convert all tool functions to `async def`; remove `create_task` usage in tool defs.
- Standardize parameter types with `Literal`/Enum and `Annotated Field` across tools.
- Add decorator `annotations` for each tool.
- Migrate metadata into decorator `meta=`; minimize/remove post-hoc mutations.
- Use `ToolError` for user-facing validation.
- Keep explicit normalized list responses after requests.
- Pilot Pydantic output models for select endpoints.
- Uniform common param constraints across modules.
- Update tests for new metadata/annotations and async.
- Run full test suite; fix regressions/lints.

### Notes
- No endpoint URLs or behavior change; this is a presentation/compliance refactor.
- Start with modules easiest to convert (e.g., `utilities.py`) to de-risk patterns.


