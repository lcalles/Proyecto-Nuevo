from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.config.settings import MODULES_JSON_PATH
from src.domain.combinations import NoCombinationsError, RowCombination, generate_row_combinations
from src.domain.modules_catalog import ModulesCatalog, ModulesCatalogError
from src.domain.pattern_solver import PatternSolverError, SolveResult, solve_rows_pattern
from src.export.csv_exporter import export_rows_to_csv
from src.export.image_exporter import export_widget_to_png
from src.export.project_io import load_project, save_project
from src.ui.diagram_view import DiagramView
from src.ui.results_view import ResultsView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Calculadora de Banda")
        self.resize(1200, 760)

        self.catalog = self._load_catalog(MODULES_JSON_PATH)
        self._current_result: SolveResult | None = None
        self._length_links: int = 0
        self._rows_count: int = 0

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.params_tab = QWidget()
        self.results_view = ResultsView()
        self.diagram_view = DiagramView()

        self.tabs.addTab(self.params_tab, "Parámetros")
        self.tabs.addTab(self.results_view, "Resultados")
        self.tabs.addTab(self.diagram_view, "Diagrama")

        self._build_params_tab()

    def _build_params_tab(self) -> None:
        root = QVBoxLayout(self.params_tab)

        length_group = QGroupBox("Longitud")
        length_form = QFormLayout(length_group)
        self.length_mm_input = QLineEdit("1000")
        self.pitch_input = QLineEdit("25")
        self.length_links_input = QSpinBox()
        self.length_links_input.setMaximum(100000)
        self.length_links_input.setValue(40)
        length_form.addRow(QLabel("Longitud (mm)"), self.length_mm_input)
        length_form.addRow(QLabel("Pitch (mm)"), self.pitch_input)
        length_form.addRow(QLabel("O longitud directa (links)"), self.length_links_input)

        width_group = QGroupBox("Ancho")
        width_form = QFormLayout(width_group)
        self.width_mm_input = QLineEdit("500")
        self.row_width_input = QLineEdit("25")
        self.rows_input = QSpinBox()
        self.rows_input.setMaximum(10000)
        self.rows_input.setValue(20)
        width_form.addRow(QLabel("Ancho (mm)"), self.width_mm_input)
        width_form.addRow(QLabel("Ancho por fila (mm)"), self.row_width_input)
        width_form.addRow(QLabel("O filas directas"), self.rows_input)

        config_group = QGroupBox("Parámetros de armado")
        config_form = QFormLayout(config_group)
        self.tolerance_input = QLineEdit("0.5")
        self.allow_brick_checkbox = QCheckBox("Permitir patrón ladrillo")
        self.allow_brick_checkbox.setChecked(True)
        config_form.addRow(QLabel("Tolerancia de redondeo (links)"), self.tolerance_input)
        config_form.addRow(self.allow_brick_checkbox)

        modules_group = QGroupBox("Catálogo de módulos")
        modules_layout = QVBoxLayout(modules_group)
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(4)
        self.modules_table.setHorizontalHeaderLabels(["Usar", "ID", "Nombre", "Links"])
        self._refresh_modules_table()
        modules_layout.addWidget(self.modules_table)

        root.addWidget(length_group)
        root.addWidget(width_group)
        root.addWidget(config_group)
        root.addWidget(modules_group)

        actions = QHBoxLayout()
        calc_button = QPushButton("Calcular")
        calc_button.clicked.connect(self.calculate)
        export_csv_btn = QPushButton("Exportar CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        export_png_btn = QPushButton("Exportar PNG")
        export_png_btn.clicked.connect(self.export_png)
        save_project_btn = QPushButton("Guardar proyecto")
        save_project_btn.clicked.connect(self.save_project_dialog)
        load_project_btn = QPushButton("Cargar proyecto")
        load_project_btn.clicked.connect(self.load_project_dialog)
        for btn in [calc_button, export_csv_btn, export_png_btn, save_project_btn, load_project_btn]:
            actions.addWidget(btn)
        root.addLayout(actions)

    def _load_catalog(self, path: Path) -> ModulesCatalog:
        try:
            return ModulesCatalog.from_json(path)
        except ModulesCatalogError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            raise

    def _refresh_modules_table(self) -> None:
        modules = self.catalog.modules
        self.modules_table.setRowCount(len(modules))
        for row, module in enumerate(modules):
            check = QTableWidgetItem()
            check.setCheckState(2 if module.enabled else 0)
            self.modules_table.setItem(row, 0, check)
            self.modules_table.setItem(row, 1, QTableWidgetItem(module.id))
            self.modules_table.setItem(row, 2, QTableWidgetItem(module.name))
            self.modules_table.setItem(row, 3, QTableWidgetItem(str(module.length_links)))
        self.modules_table.resizeColumnsToContents()

    def _sync_enabled_modules_from_table(self) -> None:
        for row, module in enumerate(self.catalog.modules):
            checked = self.modules_table.item(row, 0).checkState() == 2
            self.catalog.set_enabled(module.id, checked)

    def _compute_length_links(self) -> int:
        direct = self.length_links_input.value()
        if direct > 0:
            return direct
        length_mm = float(self.length_mm_input.text())
        pitch = float(self.pitch_input.text())
        tolerance = float(self.tolerance_input.text())
        raw = length_mm / pitch
        rounded = round(raw)
        if abs(raw - rounded) > tolerance:
            raise ValueError(
                f"Longitud no compatible con pitch. valor={raw:.3f}, redondeado={rounded}, tolerancia={tolerance}"
            )
        return int(rounded)

    def _compute_rows_count(self) -> int:
        direct = self.rows_input.value()
        if direct > 0:
            return direct
        width_mm = float(self.width_mm_input.text())
        row_width = float(self.row_width_input.text())
        if row_width <= 0:
            raise ValueError("Ancho por fila debe ser > 0")
        return int(round(width_mm / row_width))

    def calculate(self) -> None:
        try:
            self._sync_enabled_modules_from_table()
            self._length_links = self._compute_length_links()
            self._rows_count = self._compute_rows_count()
            combinations = generate_row_combinations(self._length_links, self.catalog.modules)
            self._current_result = solve_rows_pattern(
                rows_count=self._rows_count,
                combinations=combinations,
                allow_brick_pattern=self.allow_brick_checkbox.isChecked(),
            )
            self.results_view.set_result(self._current_result, self._length_links, self._rows_count)
            self.diagram_view.set_result(self._current_result, self._length_links)
            self.tabs.setCurrentWidget(self.results_view)
        except (ValueError, NoCombinationsError, PatternSolverError, ModulesCatalogError) as exc:
            self._current_result = None
            self.results_view.clear()
            self.diagram_view.clear()
            QMessageBox.warning(self, "No se pudo calcular", str(exc))

    def _rows_for_export(self) -> list[dict]:
        if not self._current_result:
            raise ValueError("No hay resultados para exportar")
        rows: list[dict] = []
        for solved_row in self._current_result.rows:
            cursor = solved_row.offset
            for seq, piece in enumerate(solved_row.combination.pieces, start=1):
                start = cursor
                end = cursor + piece.length_links
                rows.append(
                    {
                        "fila": solved_row.row_index,
                        "secuencia": seq,
                        "modulo_id": piece.module_id,
                        "inicio": start,
                        "fin": end,
                    }
                )
                cursor = end
        return rows

    def export_csv(self) -> None:
        if not self._current_result:
            QMessageBox.information(self, "Exportar", "Primero debe calcular un resultado.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "armado.csv", "CSV (*.csv)")
        if not path:
            return
        export_rows_to_csv(Path(path), self._rows_for_export())
        QMessageBox.information(self, "Exportar", f"CSV generado en {path}")

    def export_png(self) -> None:
        if not self._current_result:
            QMessageBox.information(self, "Exportar", "Primero debe calcular un resultado.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar PNG", "diagrama.png", "PNG (*.png)")
        if not path:
            return
        export_widget_to_png(self.diagram_view, Path(path))
        QMessageBox.information(self, "Exportar", f"Imagen generada en {path}")

    def save_project_dialog(self) -> None:
        if not self._current_result:
            QMessageBox.information(self, "Guardar", "No hay resultado para guardar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar proyecto", "proyecto.json", "JSON (*.json)")
        if not path:
            return

        payload = {
            "inputs": {
                "length_mm": self.length_mm_input.text(),
                "pitch_mm": self.pitch_input.text(),
                "length_links_direct": self.length_links_input.value(),
                "width_mm": self.width_mm_input.text(),
                "row_width_mm": self.row_width_input.text(),
                "rows_direct": self.rows_input.value(),
                "tolerance": self.tolerance_input.text(),
                "allow_brick_pattern": self.allow_brick_checkbox.isChecked(),
                "enabled_modules": [
                    {"id": m.id, "enabled": m.enabled, "length_links": m.length_links}
                    for m in self.catalog.modules
                ],
            },
            "result": {
                "length_links": self._length_links,
                "rows_count": self._rows_count,
                "used_brick_pattern": self._current_result.used_brick_pattern,
                "rows": [
                    {
                        "row_index": row.row_index,
                        "offset": row.offset,
                        "pieces": [asdict(piece) for piece in row.combination.pieces],
                    }
                    for row in self._current_result.rows
                ],
            },
        }
        save_project(Path(path), payload)
        QMessageBox.information(self, "Guardar", f"Proyecto guardado en {path}")

    def load_project_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Cargar proyecto", "", "JSON (*.json)")
        if not path:
            return
        payload = load_project(Path(path))
        inputs = payload.get("inputs", {})
        self.length_mm_input.setText(str(inputs.get("length_mm", self.length_mm_input.text())))
        self.pitch_input.setText(str(inputs.get("pitch_mm", self.pitch_input.text())))
        self.length_links_input.setValue(int(inputs.get("length_links_direct", self.length_links_input.value())))
        self.width_mm_input.setText(str(inputs.get("width_mm", self.width_mm_input.text())))
        self.row_width_input.setText(str(inputs.get("row_width_mm", self.row_width_input.text())))
        self.rows_input.setValue(int(inputs.get("rows_direct", self.rows_input.value())))
        self.tolerance_input.setText(str(inputs.get("tolerance", self.tolerance_input.text())))
        self.allow_brick_checkbox.setChecked(bool(inputs.get("allow_brick_pattern", True)))

        enabled_map = {m.get("id"): bool(m.get("enabled", True)) for m in inputs.get("enabled_modules", [])}
        for module in self.catalog.modules:
            if module.id in enabled_map:
                self.catalog.set_enabled(module.id, enabled_map[module.id])
        self._refresh_modules_table()
        QMessageBox.information(self, "Cargar", "Proyecto cargado. Presione Calcular para regenerar resultados.")
