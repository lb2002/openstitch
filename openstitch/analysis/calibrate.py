"""Vom Schätzwert zum Messwert: Testfleck sticken, ausmessen, Stoffzug daran anpassen.

Der Fadenzug hängt von Stoff, Vlies, Spannung und Maschine ab, das lässt sich nicht aus Tabellen
ablesen. Wie weit sich aber eine Satinsäule ohne Zugkompensation zusammenzieht, misst man in einer
Minute mit Lineal oder Messschieber. Aus diesem einen Wert wird der Faktor für Simulation und
Zugkompensation dieses Stoffs."""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString

from ..core.design import Design, SatinObject
from ..core.fabric import Fabric, fabric_by_id, pull_scale
from ..core.stitchplan import Thread
from .pull import simulate_pull
from .stitches import Trace

BAR_WIDTH = 5.0
BAR_LENGTH = 40.0
SCALE_MIN, SCALE_MAX = 0.1, 4.0


def calibration_design(fabric_id: str) -> Design:
    """Satinbalken ohne Zugkompensation: Seine Breite zeigt den Einzug ohne jede Korrektur."""
    bar = LineString([(-BAR_LENGTH / 2, 0), (BAR_LENGTH / 2, 0)]).buffer(BAR_WIDTH / 2, cap_style=2)
    return Design(name="Calibration", fabric=fabric_id,
                  objects=[SatinObject(Thread((30, 30, 30), "Black"), name="Measure this bar", geom=bar, pull_comp=0.0)])


def predicted_shrink(fabric: Fabric) -> float:
    """Einzug des Balkens in mm laut Modell (ohne Kalibrierung)."""
    plan = calibration_design(fabric.id).build_plan()
    t = Trace.of(plan)
    pull = simulate_pull(t, fabric, scale=1.0)
    x, y = t.x[pull.idx], t.y[pull.idx]
    mid = np.abs(x) < BAR_LENGTH / 4
    before = np.percentile(y[mid], 99) - np.percentile(y[mid], 1)
    moved = y[mid] + pull.dy[mid]
    return float(before - (np.percentile(moved, 99) - np.percentile(moved, 1)))


def fit_scale(fabric_id: str, measured_width_mm: float) -> float:
    """Faktor, mit dem das Modell den gemessenen Einzug trifft."""
    fabric = fabric_by_id(fabric_id)
    shrink = BAR_WIDTH - measured_width_mm
    return min(max(shrink / max(predicted_shrink(fabric), 1e-3), SCALE_MIN), SCALE_MAX)


def is_measured(fabric_id: str) -> bool:
    return pull_scale(fabric_id) != 1.0
