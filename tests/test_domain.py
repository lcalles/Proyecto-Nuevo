from src.domain.combinations import generate_row_combinations
from src.domain.modules_catalog import ModuleType
from src.domain.pattern_solver import SolvedRow, has_aligned_joints


def test_generate_row_combinations_exact_sum() -> None:
    modules = [
        ModuleType(id="A", name="A", length_links=2, description="", enabled=True),
        ModuleType(id="B", name="B", length_links=3, description="", enabled=True),
    ]
    combos = generate_row_combinations(5, modules)
    assert combos
    assert all(combo.total_length == 5 for combo in combos)


def test_has_aligned_joints_detection() -> None:
    a_combo = generate_row_combinations(
        6,
        [ModuleType(id="A", name="A", length_links=3, description="", enabled=True)],
    )[0]
    b_combo = generate_row_combinations(
        6,
        [
            ModuleType(id="A", name="A", length_links=2, description="", enabled=True),
            ModuleType(id="B", name="B", length_links=4, description="", enabled=True),
        ],
    )[0]
    row_a = SolvedRow(row_index=1, combination=a_combo, offset=0)
    row_b = SolvedRow(row_index=2, combination=b_combo, offset=0)
    assert has_aligned_joints(row_a, row_b) is False
