"""Virtueller Probestick: Jeder Detektor muss absichtlich kaputte Stiche finden und gute in Ruhe lassen."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication
from shapely.geometry import LineString, Point, box

from openstitch.analysis import DEFAULT_FABRIC, fabric_by_id, simulate_stitchout
from openstitch.analysis import corpus
from openstitch.analysis.legibility import measure
from openstitch.analysis.roundtrip import MACHINE_FORMATS, check_format
from openstitch.analysis.stitches import Trace
from openstitch.core.design import Design, FillObject, SatinObject
from openstitch.core.stitchplan import Cmd, ColorBlock, Stitch, StitchPlan, Thread
from openstitch.io.formats import export_plan
from openstitch.engine.density_guard import optimize_stitches_for_melco
from openstitch.engine.satin import _zigzag

_app = QApplication.instance() or QApplication(sys.argv)
RED = Thread((200, 30, 30), "r")


def _plan(*coords, cmds=None) -> StitchPlan:
    st = [Stitch(x, y, Cmd.JUMP if i == 0 else Cmd.STITCH) for i, (x, y) in enumerate(coords)]
    for i, c in (cmds or {}).items():
        st[i].cmd = c
    return StitchPlan([ColorBlock(RED, st)])


def _locked_line(n=30, step=2.0):
    """Sauberer Lauf mit Vernähung an beiden Enden."""
    pts = [(0, 0), (0.6, 0), (0, 0), (0.6, 0), (0, 0)]
    pts += [(step * i, 0) for i in range(1, n)]
    e = pts[-1]
    pts += [(e[0] - 0.6, 0), e, (e[0] - 0.6, 0), e]
    return pts


def _codes(plan, **kw):
    return {f.code for f in simulate_stitchout(None, plan, physics=False, **kw).findings}


def test_clean_run_has_no_findings():
    assert _codes(_plan(*_locked_line())) == set()


def test_detects_short_stitches():
    pts = _locked_line()
    pts[8:8] = [(pts[7][0] + 0.1 * i, 0) for i in range(1, 12)]
    assert "short_stitch" in _codes(_plan(*pts))


def test_detects_stitch_over_machine_limit():
    assert "over_max_stitch" in _codes(_plan(*_locked_line(step=13.0)))


def test_detects_long_floats():
    assert "long_float" in _codes(_plan(*_locked_line(step=9.0)))


def test_detects_missing_lock_stitches():
    assert "no_lock" in _codes(_plan(*[(i * 2.0, 0) for i in range(20)]))


def test_detects_runs_too_short_to_hold():
    plan = _plan((0, 0), (1, 0), (2, 0))
    assert "orphan_run" in _codes(plan)


def test_detects_jump_without_trim():
    pts = _locked_line(10)
    n = len(pts)
    pts += [(40, 0)] + [(40 + i * 2.0, 0) for i in range(1, 8)]
    assert "untrimmed_jump" in _codes(_plan(*pts, cmds={n: Cmd.JUMP}))


def test_detects_needle_pileup():
    pts = _locked_line()
    pts[8:8] = [(pts[7][0] + (i % 2) * 0.05, 0.03) for i in range(14)]
    assert "needle_pileup" in _codes(_plan(*pts))


def test_detects_overdense_area():
    d = Design(objects=[FillObject(RED, geom=box(-8, -8, 8, 8), spacing=0.25, underlay=True) for _ in range(5)])
    r = simulate_stitchout(d, d.build_plan(), physics=False)
    assert "too_dense" in {f.code for f in r.findings}


def test_detects_design_outside_hoop():
    d = Design(objects=[FillObject(RED, geom=box(-90, -20, 90, 20))])
    r = simulate_stitchout(d, d.build_plan(), physics=False)
    assert "outside_hoop" in {f.code for f in r.findings} and not r.ok


def test_detects_uncovered_area():
    d = Design(objects=[FillObject(RED, geom=box(-20, -20, 20, 20), spacing=0.4)])
    plan = d.build_plan()
    # Die Form ist nachträglich gewachsen: ein grosser Teil davon hat keine Stiche
    d.objects[0].geom = box(-30, -30, 30, 30)
    r = simulate_stitchout(d, plan, physics=False)
    assert "low_coverage" in {f.code for f in r.findings}


def test_pull_shrinks_satin_more_on_stretchy_fabric():
    d = Design(objects=[SatinObject(RED, geom=LineString([(-15, 0), (15, 0)]).buffer(2.0, cap_style=2),
                                    pull_comp=0.0, underlay=False)])
    plan = d.build_plan()
    t = Trace.of(plan)

    def width(fabric):
        p = simulate_stitchout(None, plan, fabric).pull
        y, x = t.y[p.idx] + p.dy, t.x[p.idx]
        m = np.abs(x) < 8
        return np.percentile(y[m], 99) - np.percentile(y[m], 1)

    woven, jersey, denim = width(fabric_by_id("woven")), width(fabric_by_id("jersey")), width(fabric_by_id("denim"))
    assert 3.55 < woven < 3.85          # Erfahrungswert: ca. 0.3 mm Einzug bei 4 mm Satin
    assert jersey < woven < denim


def test_pull_comp_counteracts_pull():
    def edge_error(pc):
        d = Design(objects=[SatinObject(RED, geom=LineString([(-15, 0), (15, 0)]).buffer(2.0, cap_style=2),
                                        pull_comp=pc, underlay=False)])
        plan = d.build_plan()
        t = Trace.of(plan)
        p = simulate_stitchout(None, plan).pull
        y = t.y[p.idx] + p.dy
        m = np.abs(t.x[p.idx]) < 8
        return abs((np.percentile(y[m], 99) - np.percentile(y[m], 1)) - 4.0)

    assert edge_error(0.15) < edge_error(0.0)


def test_later_stitching_shifts_earlier_objects():
    """Füllung zuerst, Kontur danach: die Füllung wandert, die Kontur trifft sie nicht mehr exakt."""
    f = FillObject(RED, geom=box(-30, -30, 30, 30), pull_comp=0.0)
    s = SatinObject(Thread((20, 20, 200), "b"), geom=box(-31.5, -31.5, 31.5, 31.5).difference(box(-28.5, -28.5, 28.5, 28.5)))
    d = Design(objects=[f, s])
    r = simulate_stitchout(d, d.build_plan(), fabric_by_id("jersey"))
    assert r.metrics["misregistration"] > 0.1


def test_every_corpus_design_builds_and_exports_cleanly():
    for name in ("stack_badge", "text_micro_25", "fill_islands", "satin_curve", "many_colors"):
        plan = corpus.build(name).build_plan()
        for ext in MACHINE_FORMATS:
            r = check_format(plan, ext)
            assert r.ok, (name, ext, r.problems)


@pytest.mark.parametrize("name", ["fill_circle", "satin_straight", "column_arc", "text_micro_25", "run_triple"])
def test_corpus_scores_stay_high(name):
    d = corpus.build(name)
    r = simulate_stitchout(d, d.build_plan(), needles=d.settings.needles)
    assert r.ok and r.score >= 90, [(f.code, f.count) for f in r.findings]


def test_split_satin_respects_max_stitch():
    d = corpus.build("satin_wide")
    plan = d.build_plan()
    seg, _ = Trace.of(plan).sewn_segments()
    assert np.hypot(seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1]).max() <= 7.05


def test_density_guard_never_creates_long_stitches():
    """Mehrfach abgefahrene Linie: Überspringen gesättigter Zellen darf keinen Riesenstich erzeugen."""
    pts = [Stitch(0, 0.25 + i * 1.0, Cmd.STITCH) for i in range(13)] * 3
    st = [Stitch(0, 0, Cmd.JUMP)] + pts
    out = [s for s in optimize_stitches_for_melco(st) if s.cmd == Cmd.STITCH]
    assert max(abs(a.y - b.y) for a, b in zip(out, out[1:])) < 13.0


@pytest.mark.parametrize("name", ["Grün", "Weiß", "Çelik ı", "Żółty", "緑"])
def test_accented_thread_names_do_not_corrupt_files(name):
    """VP3: pyembroidery zählt Zeichen statt Bytes, ein einziges ü machte die Datei unlesbar."""
    d = Design(objects=[FillObject(Thread((30, 150, 70), name, name, name), geom=box(-10, -10, 10, 10))])
    plan = d.build_plan()
    for ext in MACHINE_FORMATS:
        r = check_format(plan, ext)
        assert r.ok, (ext, r.problems)


def test_hidden_travel_keeps_the_corner_at_the_ring_start():
    """Der Weg entlang einer Kante darf die Ecke am Ringanfang nicht abschneiden (Stich quer durchs Loch)."""
    from shapely.geometry import LinearRing, Point as P
    from openstitch.engine.geom import path_along_ring
    ring = LinearRing([(0, 0), (20, 0), (20, 20), (0, 20)])     # Start in der Ecke (0, 0)
    for a, b in (((0, 5), (5, 0)), ((5, 0), (0, 5))):
        path = path_along_ring(ring, a, b)
        assert (0.0, 0.0) in [tuple(p) for p in path]
        assert all(ring.distance(P(p)) < 1e-6 for p in path)


def test_fill_on_thin_triangle_ring_does_not_cross_the_hole():
    from shapely.geometry import MultiPoint, Point as P
    g = MultiPoint([(11.0, 0.0), (16.0, 16.0), (-27.0, 0.0)]).convex_hull
    g = g.difference(g.buffer(-1.5))
    d = Design(objects=[FillObject(RED, geom=g, angle=0)])
    t = Trace.of(d.build_plan())
    pts = [P(x, y) for x, y, c in zip(t.x, t.y, t.cmd) if c == Cmd.STITCH]
    assert max(g.distance(p) for p in pts) < 1.0


def test_calibration_makes_the_model_match_the_measurement():
    from openstitch.analysis.calibrate import BAR_WIDTH, calibration_design, fit_scale, predicted_shrink
    from openstitch.core.fabric import set_pull_scale, pull_scale
    fab = fabric_by_id("jersey")
    measured_shrink = 0.9
    scale = fit_scale("jersey", BAR_WIDTH - measured_shrink)
    assert abs(scale * predicted_shrink(fab) - measured_shrink) < 0.01
    plan = calibration_design("jersey").build_plan()
    t = Trace.of(plan)
    set_pull_scale("jersey", scale)
    try:
        p = simulate_stitchout(None, plan, fab).pull
        y = t.y[p.idx] + p.dy
        m = np.abs(t.x[p.idx]) < 10
        width = np.percentile(y[m], 99) - np.percentile(y[m], 1)
        assert abs(width - (BAR_WIDTH - measured_shrink)) < 0.1      # Modell trifft jetzt den Messwert
    finally:
        set_pull_scale("jersey", None)
    assert pull_scale("jersey") == 1.0


def test_calibration_scales_pull_compensation():
    from openstitch.core.fabric import set_pull_scale
    def height(scale):
        d = Design(fabric="jersey", objects=[SatinObject(RED, geom=LineString([(-9, 0), (9, 0)]).buffer(2, cap_style=2), pull_comp=0.2, underlay=False)])
        set_pull_scale("jersey", scale)
        try:
            b = d.build_plan().bounds()
        finally:
            set_pull_scale("jersey", None)
        return b[3] - b[1]
    assert height(2.0) > height(None) + 0.5


def test_fixed_rules_and_estimates_are_labelled():
    from openstitch.analysis.report import Finding
    assert Finding("registration_gap", "warning").is_estimate
    assert not Finding("over_max_stitch", "error").is_estimate


def test_legibility_measure_separates_distinct_letters():
    m = measure("OIX", 6.0, "builtin:micro")
    assert m.worst_pairs and m.worst_pairs[0][2] < 0.95


def test_analysis_runs_on_imported_files(tmp_path):
    from openstitch.io.formats import import_file
    plan = corpus.build("stack_badge").build_plan()
    path = tmp_path / "x.dst"
    export_plan(plan, str(path))
    d = import_file(str(path))
    r = simulate_stitchout(d, d.build_plan())
    assert r.score > 0 and r.metrics["stitches"] > 1000
