from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .modules_catalog import ModuleType


@dataclass(frozen=True)
class RowPiece:
    module_id: str
    module_name: str
    length_links: int


@dataclass(frozen=True)
class RowCombination:
    pieces: tuple[RowPiece, ...]

    @property
    def total_length(self) -> int:
        return sum(piece.length_links for piece in self.pieces)

    @property
    def piece_count(self) -> int:
        return len(self.pieces)

    @property
    def joints(self) -> tuple[int, ...]:
        # Joints are internal boundaries; exclude start (0) and end (total length).
        points: list[int] = []
        acc = 0
        for piece in self.pieces[:-1]:
            acc += piece.length_links
            points.append(acc)
        return tuple(points)

    @property
    def longness_score(self) -> int:
        # Tie-breaker: maximize larger modules.
        return sum(piece.length_links * piece.length_links for piece in self.pieces)


class NoCombinationsError(Exception):
    """Raised when no exact row combinations exist for a requested length."""


def generate_row_combinations(length_links: int, modules: list[ModuleType]) -> list[RowCombination]:
    if length_links <= 0:
        raise ValueError("La longitud de fila debe ser mayor a cero.")

    enabled_modules = [m for m in modules if m.enabled]
    if not enabled_modules:
        raise NoCombinationsError("No hay módulos habilitados para calcular combinaciones.")

    # Ordered combinations: sequence matters, hence we branch on every module option.
    @lru_cache(maxsize=None)
    def build(remaining: int) -> tuple[tuple[RowPiece, ...], ...]:
        if remaining == 0:
            return (tuple(),)
        solutions: list[tuple[RowPiece, ...]] = []
        for module in enabled_modules:
            if module.length_links <= remaining:
                head = RowPiece(module.id, module.name, module.length_links)
                for tail in build(remaining - module.length_links):
                    solutions.append((head, *tail))
        return tuple(solutions)

    result = [RowCombination(pieces=s) for s in build(length_links)]
    if not result:
        raise NoCombinationsError(
            f"No existen combinaciones exactas para {length_links} links con los módulos seleccionados."
        )

    # Primary criterion: fewer pieces. Secondary criterion: use longer modules.
    result.sort(key=lambda combo: (combo.piece_count, -combo.longness_score))
    return result
