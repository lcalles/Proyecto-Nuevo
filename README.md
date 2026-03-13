# Calculadora de Banda

Aplicación de escritorio en Python/PySide6 para diseñar un patrón de armado de bandas modulares tipo Intralox.

## Características
- Cálculo de longitud por links y ancho por filas.
- Carga de catálogo de módulos desde `modules.json`.
- Generación de combinaciones de fila que suman exactamente la longitud.
- Solución de patrón por filas evitando alineación de juntas adyacentes.
- Soporte opcional para patrón tipo ladrillo (offset horizontal).
- Resumen numérico, tabla de armado y diagrama visual.
- Exportación de resultados a CSV, diagrama a PNG y guardado/carga de proyecto JSON.

## Estructura
```text
calculadora_banda/
  src/
    config/settings.py
    domain/modules_catalog.py
    domain/combinations.py
    domain/pattern_solver.py
    ui/main_window.py
    ui/results_view.py
    ui/diagram_view.py
    export/csv_exporter.py
    export/image_exporter.py
    export/project_io.py
  tests/
  modules.json
  main.py
  requirements.txt
```

## Instalación
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución en desarrollo
```bash
python main.py
```

## Ejecutar tests
```bash
pytest -q
```

## Empaquetado a `.exe` con PyInstaller
```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "CalculadoraBanda" --add-data "modules.json;." main.py
```

El ejecutable quedará en `dist/CalculadoraBanda/CalculadoraBanda.exe`.

## Notas de uso
- Si no existen combinaciones exactas para la longitud solicitada, la app mostrará un mensaje claro.
- Si el catálogo JSON está mal formado, la app reportará el error al iniciar.
