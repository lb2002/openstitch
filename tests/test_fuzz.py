"""Zufallstests: Der Stich-Motor muss jede Form überstehen und dabei seine Grundregeln einhalten."""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from PySide6.QtWidgets import QApplication
from shapely import affinity
from shapely.geometry import LineString, MultiPoint, Point, Polygon, box
from shapely.ops import unary_union

from openstitch.core.design import ColumnObject, Design, FillObject, RunObject, SatinObject
from openstitch.core.stitchplan import Cmd, Thread
from openstitch.engine.geom import polygons_of
from openstitch.text import TextObject

_app = QApplication.instance() or QApplication(sys.argv)
RUNS = int(os.environ.get("OPENSTITCH_FUZZ_RUNS", "60"))
RED = Thread((200, 30, 30), "r")

coord = st.floats(min_value=-45, max_value=45, allow_nan=False)
points = st.lists(st.tuples(coord, coord), min_size=3, max_size=14, unique=True)


def _shape(pts, kind: int, r: float):
    """Gültige, oft unangenehme Formen: Hüllen, Blobs, gepufferte Linien, Ringe."""
    if kind == 0:
        g = MultiPoint(pts).convex_hull
    elif kind == 1:
        g = unary_union([Point(p).buffer(r) for p in pts])
    elif kind == 2:
        g = LineString(pts).buffer(r)
    else:
        g = MultiPoint(pts).convex_hull
        g = g.difference(g.buffer(-r))
    return g if not g.is_empty and g.is_valid else None


def _check_plan(d: Design, geom=None):
    plan = d.build_plan()
    max_stitch = d.settings.max_stitch
    for b in plan.blocks:
        prev = None
        for s in b.stitches:
            assert math.isfinite(s.x) and math.isfinite(s.y)
            if s.cmd == Cmd.STITCH and prev is not None:
                assert math.hypot(s.x - prev[0], s.y - prev[1]) <= max_stitch + 1e-6
            if s.cmd in (Cmd.STITCH, Cmd.JUMP):
                prev = (s.x, s.y)
            if geom is not None and s.cmd == Cmd.STITCH:
                # Niemals ausserhalb der Form sticken (Zugkompensation + Vernähen als Zugabe)
                assert geom.distance(Point(s.x, s.y)) < 3.0
    return plan


@settings(max_examples=RUNS, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(points, st.integers(0, 3), st.floats(0.4, 12), st.floats(-180, 180),
       st.sampled_from(["standard", "diagonal", "ziegel", "wellen", "kontur"]), st.booleans())
def test_fill_never_escapes(pts, kind, r, angle, pattern, underlay):
    g = _shape(pts, kind, r)
    if g is None or not polygons_of(g):
        return
    d = Design(objects=[FillObject(RED, geom=g, angle=angle, pattern=pattern, underlay=underlay)])
    _check_plan(d, g)


@settings(max_examples=RUNS, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(points, st.integers(0, 3), st.floats(0.3, 8), st.booleans(), st.sampled_from(
    ["auto", "mitte", "kante", "zickzack", "kante+zickzack"]))
def test_satin_never_escapes(pts, kind, r, underlay, style):
    g = _shape(pts, kind, r)
    if g is None or not polygons_of(g):
        return
    d = Design(objects=[SatinObject(RED, geom=g, underlay=underlay, underlay_style=style)])
    _check_plan(d, g)


@settings(max_examples=RUNS, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.lists(st.tuples(coord, coord), min_size=2, max_size=14, unique=True), st.floats(0.6, 12),
       st.floats(0.2, 1.2), st.booleans())
def test_column_on_any_line(pts, width, spacing, underlay):
    line = LineString(pts)
    if line.length < 0.1:
        return
    d = Design(objects=[ColumnObject(RED, geom=line, width=width, spacing=spacing, underlay=underlay)])
    # Gehrungen dürfen an spitzen Ecken bis 2.5 × halbe Breite hinausragen (siehe column.MAX_REACH)
    _check_plan(d, line.buffer(width * 1.25))


@settings(max_examples=RUNS, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.lists(st.tuples(coord, coord), min_size=2, max_size=14, unique=True), st.integers(0, 3),
       st.floats(1.0, 6.0))
def test_run_on_any_line(pts, repeats, stitch_len):
    line = LineString(pts)
    if line.length < 0.1:
        return
    _check_plan(Design(objects=[RunObject(RED, geom=line, repeats=repeats, stitch_len=stitch_len)]), line)


@settings(max_examples=RUNS, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.text(st.characters(codec="utf-8", exclude_categories=("Cs", "Cc")), min_size=0, max_size=12),
       st.floats(1.0, 40.0))
def test_micro_text_handles_any_string(text, height):
    _check_plan(Design(objects=[TextObject(RED, text=text, height=height, font="builtin:micro")]))


@settings(max_examples=RUNS, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(points, st.floats(0.5, 2.0), st.floats(-180, 180), st.floats(-30, 30), st.floats(-30, 30), st.booleans())
def test_transforms_keep_stitches_on_shape(pts, scale, rot, dx, dy, mirror):
    g = MultiPoint(pts).convex_hull
    if g.is_empty or not polygons_of(g):
        return
    o = FillObject(RED, geom=g)
    a = math.radians(rot)
    sx = -scale if mirror else scale
    o.transform = (sx * math.cos(a), -scale * math.sin(a), sx * math.sin(a), scale * math.cos(a), dx, dy)
    _check_plan(Design(objects=[o]), o.world_geom())
