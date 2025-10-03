"""Metadata validation for MCP tool registrations."""

from __future__ import annotations

import inspect
import textwrap
from typing import Optional

import pytest

from sensortower_mcp.tool_examples import TOOL_ARGUMENT_EXAMPLES

from .tool_registry import (
    collect_tool_infos,
    load_openapi_paths,
    load_openapi_required_query_params,
)

TOOL_INFOS = collect_tool_infos()
OPENAPI_PATHS = set(load_openapi_paths())
OPENAPI_REQUIRED_QUERY_PARAMS = load_openapi_required_query_params()
PARAM_ALIASES = {
    "period": {"period", "date_granularity"},
    "time_period": {"time_period", "date_granularity"},
    "category": {"category", "categories"},
    "chart_type_ids": {"chart_type_ids"},
}

KNOWN_SCHEMA_GAPS = {
    "impressions_rank": {"period"},
}


def _format_missing_docs(info_name: str, doc: str) -> str:
    preview = textwrap.shorten(doc.replace("\n", " "), width=120)
    return f"Tool '{info_name}' docstring insufficient (preview: {preview!r})"


def test_expected_tool_count():
    # SensorTower MCP currently exposes 43 tools across all modules.
    assert len(TOOL_INFOS) == 43, "Unexpected number of registered tools"


@pytest.mark.parametrize("info", TOOL_INFOS, ids=lambda i: i.name)
def test_tool_docstrings_include_guidance(info):
    doc = info.doc.strip()
    assert len(doc) >= 40, _format_missing_docs(info.name, doc)
    guidance_present = any(keyword in doc for keyword in ("Example", "Parameters", "Returns", "Note"))
    assert guidance_present, _format_missing_docs(info.name, doc)


@pytest.mark.parametrize("info", TOOL_INFOS, ids=lambda i: i.name)
def test_tool_metadata_includes_examples(info):
    docs_meta = info.metadata.get("docs") if isinstance(info.metadata, dict) else None
    assert docs_meta, f"Tool {info.name} missing docs metadata"
    assert docs_meta.get("hint"), f"Tool {info.name} metadata lacks usage hint"
    example_record = TOOL_ARGUMENT_EXAMPLES.get(info.name, {})
    if example_record.get("skip_reason"):
        pytest.skip("Credential-gated tool")
    if example_record.get("arguments"):
        assert docs_meta.get("example_snippet"), f"Tool {info.name} metadata lacks example snippet"


@pytest.mark.parametrize("info", TOOL_INFOS, ids=lambda i: i.name)
def test_tool_parameters_have_type_hints(info):
    for param in info.signature.parameters.values():
        assert param.annotation is not inspect._empty, f"Parameter '{param.name}' in {info.name} lacks a type hint"


@pytest.mark.parametrize("info", TOOL_INFOS, ids=lambda i: i.name)
def test_tool_parameter_annotations_carry_descriptions(info):
    annotated_params = {name: doc for name, doc in info.param_docs.items() if doc is not None}
    for name, doc in annotated_params.items():
        assert doc, f"Annotated parameter '{name}' in {info.name} missing inline documentation"


@pytest.mark.parametrize(
    "info",
    [i for i in TOOL_INFOS if i.endpoint_path],
    ids=lambda i: i.name,
)
def test_tool_endpoints_present_in_openapi(info):
    path = info.endpoint_path
    if "{os}" in path:
        candidates = [path] + [path.replace("{os}", os_variant) for os_variant in ("ios", "android")]
        assert any(candidate in OPENAPI_PATHS for candidate in candidates), (
            f"Endpoint {path!r} (any OS variant) used by {info.name} not found in swaggerdocs"
        )
    else:
        assert path in OPENAPI_PATHS, (
            f"Endpoint {path!r} used by {info.name} not found in swaggerdocs"
        )


@pytest.mark.parametrize(
    "info",
    [i for i in TOOL_INFOS if i.endpoint_path],
    ids=lambda i: i.name,
)
def test_required_parameters_match_openapi(info):
    path = info.endpoint_path
    candidate_paths = [path]
    if "{os}" in path:
        candidate_paths.extend(path.replace("{os}", variant) for variant in ("ios", "android", "unified"))

    required_params: Optional[set[str]] = None
    for candidate in candidate_paths:
        spec_required = OPENAPI_REQUIRED_QUERY_PARAMS.get(candidate)
        if spec_required is not None:
            required_params = spec_required
            break

    if required_params is None:
        pytest.skip(f"No query parameter spec found for {path}")

    signature = info.signature
    available_params = set(signature.parameters.keys())

    def satisfies(param: str) -> bool:
        if param in available_params:
            return True
        aliases = PARAM_ALIASES.get(param)
        if aliases and aliases & available_params:
            return True
        return False

    unresolved = {param for param in required_params if not satisfies(param)}
    unresolved -= KNOWN_SCHEMA_GAPS.get(info.name, set())

    assert not unresolved, (
        f"Tool {info.name} missing required params {sorted(unresolved)} for endpoint {path}"
    )
