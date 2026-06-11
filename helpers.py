"""Parameter normalization and naming helpers (pure, stdlib-only)."""

import json
import pathlib


def _params(params, kwargs):
    merged = _coerce_mapping(params)
    merged.update(_coerce_mapping(kwargs))

    for key in ("arguments", "args", "input", "parameters", "params"):
        nested = _coerce_mapping(merged.get(key))
        if nested:
            merged.update(nested)

    return merged


def _coerce_mapping(value):
    if isinstance(value, dict):
        return dict(value)

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}

        if isinstance(parsed, dict):
            return dict(parsed)

    return {}


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    return parsed if parsed > 0 else default


def _repo_name(params):
    explicit = str(params.get("repo_name") or params.get("repo") or "").strip()
    if explicit:
        return explicit

    path = str(params.get("repo_path") or params.get("path") or "").strip()
    if not path:
        return ""

    return pathlib.PurePosixPath(path).name


def _clean_repo_name(value):
    return "".join(
        char for char in str(value or "").strip()
        if char.isalnum() or char in {".", "_", "-"}
    )[:120]


def _relative_path(params, repo_name):
    explicit = str(
        params.get("relative_path")
        or params.get("relativePath")
        or params.get("file_path")
        or params.get("filepath")
        or params.get("file")
        or params.get("filename")
        or ""
    ).strip()
    if explicit:
        return explicit

    path = str(params.get("path") or "").strip()
    if not path:
        return ""

    pure_path = pathlib.PurePosixPath(path)
    parts = pure_path.parts
    if repo_name in parts:
        repo_index = parts.index(repo_name)
        relative_parts = parts[repo_index + 1 :]
        if relative_parts:
            return str(pathlib.PurePosixPath(*relative_parts))

    return pure_path.name
