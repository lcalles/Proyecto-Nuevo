from __future__ import annotations

from dataclasses import dataclass

from .combinations import RowCombination


@dataclass(frozen=True)
class SolvedRow:
    row_index: int
    combination: RowCombination
    offset: int = 0

    @property
    def shifted_joints(self) -> tuple[int, ...]:
        return tuple(j + self.offset for j in self.combination.joints)


@dataclass(frozen=True)
class SolveResult:
    rows: list[SolvedRow]
    used_brick_pattern: bool
    no_aligned_adjacent_joints: bool


class PatternSolverError(Exception):
    """Raised when row pattern cannot be solved under given constraints."""


def has_aligned_joints(row_a: SolvedRow, row_b: SolvedRow) -> bool:
    return not set(row_a.shifted_joints).isdisjoint(row_b.shifted_joints)


def solve_rows_pattern(
    rows_count: int,
    combinations: list[RowCombination],
    allow_brick_pattern: bool = True,
) -> SolveResult:
    if rows_count <= 0:
        raise ValueError("rows_count debe ser mayor a cero")
    if not combinations:
        raise PatternSolverError("No hay combinaciones de filas para resolver el patrón")

    offsets = [0, 1] if allow_brick_pattern else [0]
    current: list[SolvedRow] = []

    def backtrack(row_idx: int) -> bool:
        if row_idx == rows_count:
            return True
        for combo in combinations:
            for offset in offsets:
                candidate = SolvedRow(row_index=row_idx + 1, combination=combo, offset=offset)
                if current and has_aligned_joints(current[-1], candidate):
                    continue
                current.append(candidate)
                if backtrack(row_idx + 1):
                    return True
                current.pop()
        return False

    if not backtrack(0):
        raise PatternSolverError(
            "No fue posible generar un patrón sin alineación de juntas entre filas adyacentes."
        )

    used_brick = any(row.offset != 0 for row in current)
    no_alignment = all(
        not has_aligned_joints(current[i], current[i + 1]) for i in range(len(current) - 1)
    )
    return SolveResult(rows=list(current), used_brick_pattern=used_brick, no_aligned_adjacent_joints=no_alignment)
