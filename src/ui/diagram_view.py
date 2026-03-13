from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from src.config.settings import COLOR_PALETTE
from src.domain.pattern_solver import SolveResult


class DiagramView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._result: SolveResult | None = None
        self._length_links: int = 0
        self._color_map: dict[str, QColor] = {}
        self.setMinimumHeight(260)

    def set_result(self, result: SolveResult, length_links: int) -> None:
        self._result = result
        self._length_links = max(length_links, 1)
        module_ids = []
        for row in result.rows:
            for piece in row.combination.pieces:
                if piece.module_id not in module_ids:
                    module_ids.append(piece.module_id)
        self._color_map = {
            module_id: QColor(COLOR_PALETTE[i % len(COLOR_PALETTE)])
            for i, module_id in enumerate(module_ids)
        }
        self.update()

    def clear(self) -> None:
        self._result = None
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("white"))

        if not self._result:
            painter.drawText(self.rect(), Qt.AlignCenter, "Sin diagrama")
            return

        margin = 20
        row_h = max((self.height() - margin * 2) // max(len(self._result.rows), 1), 28)
        usable_w = self.width() - margin * 2

        pen = QPen(QColor("#333333"))
        painter.setPen(pen)

        for idx, solved_row in enumerate(self._result.rows):
            y = margin + idx * row_h
            x_cursor = margin + int((solved_row.offset / self._length_links) * usable_w)

            for piece in solved_row.combination.pieces:
                w = max(int((piece.length_links / self._length_links) * usable_w), 2)
                color = self._color_map.get(piece.module_id, QColor("#DDDDDD"))
                painter.fillRect(x_cursor, y, w, row_h - 4, color)
                painter.drawRect(x_cursor, y, w, row_h - 4)
                painter.drawText(x_cursor + 3, y + (row_h // 2), piece.module_id)
                x_cursor += w

            painter.drawText(4, y + (row_h // 2), f"F{solved_row.row_index}")
