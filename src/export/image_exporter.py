from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget


def export_widget_to_png(widget: QWidget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pixmap = widget.grab()
    pixmap.save(str(path), "PNG")
