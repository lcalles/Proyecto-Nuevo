from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODULES_JSON_PATH = BASE_DIR / "modules.json"
PROJECTS_DIR = BASE_DIR / "projects"
EXPORTS_DIR = BASE_DIR / "exports"

DEFAULT_TOLERANCE_LINKS = 0.5
DEFAULT_ALLOW_BRICK_PATTERN = True

COLOR_PALETTE = [
    "#4E79A7",
    "#F28E2B",
    "#E15759",
    "#76B7B2",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7",
    "#9C755F",
    "#BAB0AC",
]
