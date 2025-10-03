"""Validation for the generated documentation resources."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from sensortower_mcp.tool_examples import TOOL_ARGUMENT_EXAMPLES
from tests.tool_manifest import build_tool_manifest
from tests.tool_registry import load_openapi_required_query_params

DOC_PATH = Path("src/sensortower_mcp/documentation.py")


def _extract_resource_text(function_name: str) -> str:
    module = ast.parse(DOC_PATH.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == "register_documentation":
            for inner in node.body:
                if isinstance(inner, ast.FunctionDef) and inner.name == function_name:
                    for stmt in inner.body:
                        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                            value = stmt.value.value
                            if isinstance(value, str):
                                return value
    raise RuntimeError(f"Unable to locate resource text for {function_name}")


API_DOC_TEXT = _extract_resource_text("api_documentation")
MANIFEST = build_tool_manifest()
REQUIRED_QUERY_PARAMS = load_openapi_required_query_params()
PARAM_ALIASES = {
    "period": {"period", "date_granularity"},
    "time_period": {"time_period", "date_granularity"},
    "category": {"category", "categories"},
    "chart_type_ids": {"chart_type_ids"},
}
EXAMPLE_GAPS = {
    "impressions_rank": {"period"},
}


@pytest.mark.parametrize("entry", MANIFEST, ids=lambda e: e.name)
def test_api_documentation_mentions_every_tool(entry):
    assert f"**{entry.name}**" in API_DOC_TEXT, f"Documentation missing entry for {entry.name}"


@pytest.mark.parametrize("parameter", ["os", "country", "app_ids", "category", "chart_type"])
def test_common_parameters_section_mentions_core_parameter(parameter):
    assert parameter in API_DOC_TEXT, f"Common parameters section missing '{parameter}'"


@pytest.mark.parametrize(
    "entry",
    [e for e in MANIFEST if not TOOL_ARGUMENT_EXAMPLES.get(e.name, {}).get("skip_reason")],
    ids=lambda e: e.name,
)
def test_usage_examples_cover_required_parameters(entry):
    example_args = TOOL_ARGUMENT_EXAMPLES.get(entry.name, {}).get("arguments", {})
    endpoint_path = entry.endpoint_path
    if not endpoint_path:
        pytest.skip(f"No endpoint extraction for {entry.name}")

    candidate_paths = [endpoint_path]
    if "{os}" in endpoint_path:
        candidate_paths.extend(endpoint_path.replace("{os}", variant) for variant in ("ios", "android", "unified"))

    required_params = None
    for candidate in candidate_paths:
        params = REQUIRED_QUERY_PARAMS.get(candidate)
        if params is not None:
            required_params = params
            break

    if required_params is None or not required_params:
        pytest.skip(f"No required query params documented for {endpoint_path}")

    present_args = set(example_args.keys())

    def satisfies(param: str) -> bool:
        if param in present_args:
            return True
        aliases = PARAM_ALIASES.get(param)
        if aliases and aliases & present_args:
            return True
        return False

    missing = {param for param in required_params if not satisfies(param)}
    missing -= EXAMPLE_GAPS.get(entry.name, set())
    assert not missing, f"Usage example for {entry.name} missing required params {sorted(missing)}"
