from __future__ import annotations

from collections import Counter

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from src.domain.pattern_solver import SolveResult


class ResultsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.summary_label = QLabel("Sin resultados.")
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Fila", "Secuencia", "Módulo", "Inicio", "Fin", "Junta"]
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.table)

    def set_result(self, solve_result: SolveResult, length_links: int, rows_count: int) -> None:
        counts: Counter[str] = Counter()
        rows_data: list[tuple[int, int, str, int, int, str]] = []
        for solved_row in solve_result.rows:
            cursor = solved_row.offset
            for seq, piece in enumerate(solved_row.combination.pieces, start=1):
                start = cursor
                end = cursor + piece.length_links
                cursor = end
                counts[piece.module_id] += 1
                rows_data.append(
                    (
                        solved_row.row_index,
                        seq,
                        piece.module_id,
                        start,
                        end,
                        "Sí" if end in solved_row.shifted_joints else "No",
                    )
                )

        summary_lines = [
            f"Longitud total: {length_links} links",
            f"Filas: {rows_count}",
            f"Total de módulos: {sum(counts.values())}",
            "Cantidad por tipo: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
            "Sin juntas alineadas entre filas adyacentes: "
            + ("Sí" if solve_result.no_aligned_adjacent_joints else "No"),
            "Patrón ladrillo utilizado: " + ("Sí" if solve_result.used_brick_pattern else "No"),
        ]
        self.summary_label.setText("\n".join(summary_lines))

        self.table.setRowCount(len(rows_data))
        for row_idx, data in enumerate(rows_data):
            for col_idx, value in enumerate(data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def clear(self) -> None:
        self.summary_label.setText("Sin resultados.")
        self.table.setRowCount(0)
