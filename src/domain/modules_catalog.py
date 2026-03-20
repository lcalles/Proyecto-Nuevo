from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ModuleType:
    id: str
    name: str
    length_links: int
    description: str
    enabled: bool = True


class ModulesCatalogError(Exception):
    """Raised when module catalog cannot be loaded or validated."""


class ModulesCatalog:
    def __init__(self, modules: list[ModuleType]):
        if not modules:
            raise ModulesCatalogError("El catálogo de módulos está vacío.")
        self._modules = modules

    @property
    def modules(self) -> list[ModuleType]:
        return list(self._modules)

    def enabled_modules(self) -> list[ModuleType]:
        return [m for m in self._modules if m.enabled]

    def set_enabled(self, module_id: str, enabled: bool) -> None:
        updated: list[ModuleType] = []
        found = False
        for module in self._modules:
            if module.id == module_id:
                found = True
                updated.append(
                    ModuleType(
                        id=module.id,
                        name=module.name,
                        length_links=module.length_links,
                        description=module.description,
                        enabled=enabled,
                    )
                )
            else:
                updated.append(module)
        if not found:
            raise ModulesCatalogError(f"No se encontró módulo con id '{module_id}'.")
        self._modules = updated

    @classmethod
    def from_json(cls, path: Path) -> "ModulesCatalog":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ModulesCatalogError(f"JSON inválido en {path}: {exc}") from exc
        except OSError as exc:
            raise ModulesCatalogError(f"No se pudo leer {path}: {exc}") from exc

        if not isinstance(payload, list):
            raise ModulesCatalogError("El catálogo debe ser una lista JSON.")

        modules: list[ModuleType] = []
        for idx, item in enumerate(payload, start=1):
            try:
                modules.append(_parse_module(item))
            except (KeyError, TypeError, ValueError) as exc:
                raise ModulesCatalogError(f"Módulo inválido en posición {idx}: {exc}") from exc
        return cls(modules)

    def lengths_of_enabled(self) -> list[int]:
        return [m.length_links for m in self.enabled_modules()]

    def by_id(self) -> dict[str, ModuleType]:
        return {m.id: m for m in self._modules}


def _parse_module(item: dict) -> ModuleType:
    if not isinstance(item, dict):
        raise TypeError("cada módulo debe ser un objeto")
    if int(item["length_links"]) <= 0:
        raise ValueError("length_links debe ser mayor a 0")

    return ModuleType(
        id=str(item["id"]),
        name=str(item.get("name", item["id"])),
        length_links=int(item["length_links"]),
        description=str(item.get("description", "")),
        enabled=bool(item.get("enabled", True)),
    )


def module_ids(modules: Iterable[ModuleType]) -> list[str]:
    return [m.id for m in modules]
