"""Stoff-Profile für den Probestick und die Auto-Einstellungen.

`stiffness`: Dehnwiderstand relativ zu gewebter Baumwolle (1.0).
`pull_factor`: Faktor auf die Zugkompensation. `density_factor`: Faktor auf den Reihenabstand
(> 1 = lockerer). `max_layers`: ab wie vielen Fadenlagen der Stoff leidet."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fabric:
    id: str
    stiffness: float
    pull_factor: float
    density_factor: float
    max_layers: float
    topping: bool = False        # wasserlösliche Folie empfohlen (hoher Flor)
    stabilizer: str = "cutaway"  # 'cutaway' | 'tearaway' | 'none'
    needle: str = "75/11"


FABRICS: list[Fabric] = [
    Fabric("woven", 1.0, 1.0, 1.0, 4.5, stabilizer="tearaway"),
    Fabric("denim", 1.8, 0.8, 1.0, 5.5, stabilizer="tearaway", needle="90/14"),
    Fabric("twill_cap", 1.4, 1.1, 1.0, 5.0, stabilizer="tearaway", needle="80/12"),
    Fabric("pique", 0.65, 1.5, 1.05, 4.0),
    Fabric("jersey", 0.45, 2.0, 1.15, 3.2),
    Fabric("fleece", 0.55, 1.8, 1.1, 3.8, topping=True),
    Fabric("towel", 0.6, 1.6, 0.95, 4.5, topping=True, needle="80/12"),
    Fabric("leather", 1.6, 0.7, 1.3, 2.6, stabilizer="none"),
    Fabric("silk", 0.7, 1.3, 1.2, 2.8, stabilizer="tearaway", needle="65/9"),
]

DEFAULT_FABRIC = FABRICS[0]


# Gemessener Faktor je Stoff (siehe analysis.calibrate); 1.0 = noch nicht gemessen
_pull_scale: dict[str, float] = {}


def pull_scale(fid: str) -> float:
    return _pull_scale.get(fid, 1.0)


def set_pull_scale(fid: str, value: float | None) -> None:
    if value is None:
        _pull_scale.pop(fid, None)
    else:
        _pull_scale[fid] = float(value)


def fabric_by_id(fid: str | None) -> Fabric:
    return next((f for f in FABRICS if f.id == fid), DEFAULT_FABRIC)
