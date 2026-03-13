from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def export_rows_to_csv(path: Path, rows: Iterable[dict]) -> None:
    rows_list = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        if not rows_list:
            f.write("")
            return
        writer = csv.DictWriter(f, fieldnames=list(rows_list[0].keys()))
        writer.writeheader()
        writer.writerows(rows_list)
