"""Jeder Regler muss wirken: Mehr Dichte heisst mehr Stiche, mehr Zugausgleich heisst breiter.

Solche Fehler sieht kein normaler Test: Die Stiche sind gültig, nur die Einstellung ist wirkungslos."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication
from shapely.geometry import LineString, Point, box

from openstitch.analysis.stitches import Trace
from openstitch.core.design import ColumnObject, Design, FillObject, RunObject, SatinObject
from openstitch.core.stitchplan import Thread
from openstitch.text import TextObject

_app = QApplication.instance() or QApplication(sys.argv)
R = Thread((200, 30, 30), "r")
BAR = LineString([(-20, 0), (20, 0)])
RING = Point(0, 0).buffer(30).difference(Point(0, 0).buffer(25))


def _count(obj) -> int:
    return Design(objects=[obj]).build_plan().stitch_count


def _falls(values: list[int], min_drop: float = 0.05):
    """Jeder Schritt muss spürbar weniger Stiche ergeben."""
    for a, b in zip(values, values[1:]):
        assert b < a * (1 - min_drop), values


def test_fill_spacing_controls_density():
    _falls([_count(FillObject(R, geom=box(-20, -20, 20, 20), spacing=s, underlay=False)) for s in (0.3, 0.4, 0.5, 0.6, 0.8)])


def test_fill_stitch_length_controls_count():
    _falls([_count(FillObject(R, geom=box(-20, -20, 20, 20), stitch_len=s, underlay=False)) for s in (2, 3, 4, 5, 6)])


@pytest.mark.parametrize("geom", [BAR.buffer(2.5, cap_style=2), RING], ids=["straight", "ring"])
def test_satin_density_controls_stitches(geom):
    """Lief lange Zeit ins Leere: Abstände über ~0.4 mm änderten bei Satin gar nichts."""
    _falls([_count(SatinObject(R, geom=geom, spacing=s, underlay=False)) for s in (0.3, 0.4, 0.5, 0.6, 0.8)])


def test_satin_edge_spacing_is_even():
    d = Design(objects=[SatinObject(R, geom=BAR.buffer(2.0, cap_style=2), spacing=0.5, underlay=False, pull_comp=0.0)])
    t = Trace.of(d.build_plan())
    mid = np.abs(t.x) < 12
    edge = np.sort(t.x[mid & (t.y > 1.5)])
    gaps = np.diff(edge)
    gaps = gaps[gaps > 0.02]
    assert abs(np.median(gaps) - 0.5) < 0.06
    assert gaps.std() < 0.08


def test_column_density_controls_stitches():
    _falls([_count(ColumnObject(R, geom=BAR, width=4, spacing=s, underlay=False)) for s in (0.3, 0.4, 0.5, 0.6, 0.8)])


def test_run_stitch_length_controls_count():
    _falls([_count(RunObject(R, geom=BAR, stitch_len=s)) for s in (1, 2, 3, 4)])


@pytest.mark.parametrize("font", ["builtin:micro", None], ids=["micro", "truetype"])
def test_text_density_controls_stitches(font):
    kw = {"font": font} if font else {}
    _falls([_count(TextObject(R, text="AB", height=12, density=s, **kw)) for s in (0.3, 0.4, 0.5, 0.6)])


@pytest.mark.parametrize("obj", [
    lambda pc: FillObject(R, geom=box(-20, -20, 20, 20), pull_comp=pc, angle=0, underlay=False),
    lambda pc: SatinObject(R, geom=BAR.buffer(2.0, cap_style=2), pull_comp=pc, underlay=False),
    lambda pc: ColumnObject(R, geom=BAR, width=4, pull_comp=pc, underlay=False),
], ids=["fill", "satin", "column"])
def test_pull_compensation_widens_the_stitched_shape(obj):
    sizes = []
    for pc in (0.0, 0.3, 0.6):
        x0, y0, x1, y1 = Design(objects=[obj(pc)]).build_plan().bounds()
        # Füllung wächst in Stichrichtung (Winkel 0 = x), Satin quer zur Säule
        sizes.append(x1 - x0 if isinstance(obj(0.0), FillObject) else y1 - y0)
    assert sizes[0] < sizes[1] < sizes[2]


def test_column_width_is_what_was_asked_for():
    for w in (1.0, 2.0, 4.0, 8.0):
        x0, y0, x1, y1 = Design(objects=[ColumnObject(R, geom=BAR, width=w, underlay=False, pull_comp=0)]).build_plan().bounds()
        assert abs((y1 - y0) - w) < 0.05


def test_angle_turns_fill_rows():
    def direction(angle):
        d = Design(objects=[FillObject(R, geom=box(-20, -20, 20, 20), angle=angle, underlay=False, pull_comp=0)])
        seg, _ = Trace.of(d.build_plan()).sewn_segments()
        dx, dy = seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1]
        long_ = np.hypot(dx, dy) > 2
        return np.median(np.degrees(np.arctan2(dy[long_], dx[long_])) % 180)
    assert abs(direction(0) - 0) < 3 or abs(direction(0) - 180) < 3
    assert abs(direction(90) - 90) < 3


def test_underlay_adds_stitches_everywhere():
    for mk in (lambda u: FillObject(R, geom=box(-15, -15, 15, 15), underlay=u),
               lambda u: SatinObject(R, geom=BAR.buffer(2.5, cap_style=2), underlay=u),
               lambda u: ColumnObject(R, geom=BAR, width=4, underlay=u)):
        assert _count(mk(True)) > _count(mk(False))


def test_triple_run_sews_each_stitch_three_times():
    locks = 8   # Vernähstiche an beiden Enden werden nicht verdreifacht
    assert 2.7 < (_count(RunObject(R, geom=BAR, repeats=1)) - locks) / (_count(RunObject(R, geom=BAR, repeats=0)) - locks) < 3.3
