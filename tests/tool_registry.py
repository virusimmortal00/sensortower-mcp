"""Helpers for introspecting registered Sensor Tower MCP tools."""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, get_args, get_origin

import yaml

from tests.tool_manifest import build_tool_manifest


@dataclass(frozen=True)
class ToolInfo:
    """Metadata captured for a registered MCP tool."""

    category: str
    name: str
    func: Callable[..., Any]
    doc: str
    signature: inspect.Signature
    param_docs: Dict[str, Optional[str]]
    endpoint_path: Optional[str]
    metadata: Dict[str, Any]


_DEF_ENDPOINT_PATTERN = re.compile(r"self\.(?:make_request|client\.(?:get|post))\(f?\"([^\"]+)\"")


def _extract_endpoint_path(func: Callable[..., Any]) -> Optional[str]:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):  # pragma: no cover - fallback when source missing
        return None
    match = _DEF_ENDPOINT_PATTERN.search(source)
    if match:
        return match.group(1)
    return None


def _parse_param_docs(func: Callable[..., Any]) -> Dict[str, Optional[str]]:
    docs: Dict[str, Optional[str]] = {}
    for param_name, annotation in getattr(func, "__annotations__", {}).items():
        if param_name == "return":
            continue
        doc_text: Optional[str] = None
        origin = get_origin(annotation)
        if origin is not None and origin.__qualname__ == "Annotated":  # type: ignore[attr-defined]
            args = get_args(annotation)
            for meta in args[1:]:
                if isinstance(meta, str):
                    doc_text = meta.strip()
                    break
        docs[param_name] = doc_text
    return docs


def collect_tool_infos() -> List[ToolInfo]:
    infos: List[ToolInfo] = []
    for entry in build_tool_manifest():
        func = entry.function
        doc = entry.doc
        signature = entry.signature
        param_docs = _parse_param_docs(func)
        endpoint_path = _extract_endpoint_path(func)
        infos.append(
            ToolInfo(
                category=entry.category,
                name=entry.name,
                func=func,
                doc=doc,
                signature=signature,
                param_docs=param_docs,
                endpoint_path=endpoint_path,
                metadata=entry.metadata,
            )
        )
    infos.sort(key=lambda info: info.name)
    return infos


def load_openapi_paths() -> List[str]:
    """Return a list of documented API paths from bundled swagger docs."""
    return list(load_openapi_required_query_params().keys())


def load_openapi_required_query_params() -> Dict[str, set[str]]:
    """Return mapping of documented API paths to their required query parameters."""
    swagger_dir = Path(__file__).resolve().parent.parent / "swaggerdocs"
    mapping: Dict[str, set[str]] = {}
    for path in swagger_dir.glob("*.yml"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        spec = yaml.safe_load(content)
        for api_path, methods in spec.get("paths", {}).items():
            required_params: set[str] = mapping.setdefault(api_path, set())
            for method_details in methods.values():
                for param in method_details.get("parameters", []):
                    if not param.get("required"):
                        continue
                    if param.get("in") != "query":
                        continue
                    name = param.get("name")
                    if name and name != "auth_token":
                        required_params.add(name)
    return mapping
