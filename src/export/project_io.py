from __future__ import annotations

import json
from pathlib import Path


class ProjectIOError(Exception):
    """Raised when project file cannot be read/written."""


def save_project(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        raise ProjectIOError(f"No se pudo guardar el proyecto: {exc}") from exc


def load_project(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectIOError(f"No se pudo cargar el proyecto: {exc}") from exc
