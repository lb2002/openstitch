"""Tests für den SVG-Importer (transform, Pfadbefehle, Stil-Vererbung, Füllregeln, Einheiten)."""
import math

import pytest
from shapely.ops import unary_union

from openstitch.auto.palette import nearest_thread
from openstitch.core.design import FillObject, RunObject, SatinObject
from openstitch.engine.pro_tools import _parse_svg_color, _parse_svg_path_d, import_svg

# 1 Benutzereinheit = 1 mm, damit Flächen/Grössen direkt prüfbar sind
MM_ROOT = 'width="200mm" height="200mm" viewBox="0 0 200 200"'


def _svg(tmp_path, body, root_attrs=MM_ROOT, name="t.svg"):
    p = tmp_path / name
    p.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" {root_attrs}>'
        f"{body}</svg>", encoding="utf-8")
    return str(p)


def _load(tmp_path, body, **kw):
    kw.setdefault("target_width_mm", None)
    return import_svg(_svg(tmp_path, body), **kw)


def _areas(d):
    return [o.geom for o in d.objects if isinstance(o, (FillObject, SatinObject))]


def _wh(g):
    x0, y0, x1, y1 = g.bounds
    return x1 - x0, y1 - y0


def test_translated_and_nested_groups(tmp_path):
    d = _load(tmp_path, '<rect width="10" height="10"/>'
                        '<g transform="translate(50,20)"><rect width="10" height="10"/></g>'
                        '<g transform="translate(0,60)"><g transform="scale(2)"><rect width="10" height="10"/></g></g>')
    a, b, c = _areas(d)
    assert b.centroid.x - a.centroid.x == pytest.approx(50, abs=1e-6)
    assert b.centroid.y - a.centroid.y == pytest.approx(20, abs=1e-6)
    assert _wh(c) == pytest.approx((20, 20), abs=1e-6)
    assert c.centroid.y - a.centroid.y == pytest.approx(65, abs=1e-6)


def test_rotated_rect_and_default_scaling(tmp_path):
    body = '<rect x="0" y="0" width="40" height="10" transform="rotate(90 20 5)"/>'
    (g,) = _areas(_load(tmp_path, body))
    assert _wh(g) == pytest.approx((10, 40), abs=1e-6)
    assert g.area == pytest.approx(400, rel=1e-6)
    # Standard: auf 95 mm Breite skaliert (bisheriges Verhalten)
    (g95,) = _areas(import_svg(_svg(tmp_path, body, name="d.svg")))
    assert _wh(g95) == pytest.approx((95, 380), rel=1e-6)


def test_arc_circle_area(tmp_path):
    d = _load(tmp_path, '<path d="M90,100 A10,10 0 0 1 110,100 A10,10 0 0 1 90,100 Z" fill="red"/>')
    (g,) = _areas(d)
    assert g.area == pytest.approx(math.pi * 100, rel=0.03)
    assert _wh(g) == pytest.approx((20, 20), abs=0.05)
    # kompakte Flags ohne Trenner + relative Bögen: Halbkreis-Paar
    subs = _parse_svg_path_d("M0 0a10 10 0 0120 0a10 10 0 01-20 0z")
    from shapely.geometry import Polygon
    assert Polygon(subs[0][0]).area == pytest.approx(math.pi * 100, rel=0.03)


def test_smooth_curves_s_and_t():
    s = _parse_svg_path_d("M0 0 C0 20 20 20 20 0 S40 -20 40 0")
    c = _parse_svg_path_d("M0 0 C0 20 20 20 20 0 C20 -20 40 -20 40 0")
    assert s[0][0] == pytest.approx(c[0][0])
    t = _parse_svg_path_d("M0 0 Q10 20 20 0 T40 0 t20 0")
    q = _parse_svg_path_d("M0 0 Q10 20 20 0 Q30 -20 40 0 Q50 20 60 0")
    assert t[0][0] == pytest.approx(q[0][0])
    # S ohne vorheriges C: erster Kontrollpunkt = aktueller Punkt
    s2 = _parse_svg_path_d("M0 0 S10 10 20 0")
    c2 = _parse_svg_path_d("M0 0 C0 0 10 10 20 0")
    assert s2[0][0] == pytest.approx(c2[0][0])


def test_path_number_syntax_and_unknown_command():
    (pts, closed), = _parse_svg_path_d("M1.5.5L-1-2 3e1,0z")
    assert closed and pts == pytest.approx([(1.5, 0.5), (-1, -2), (30, 0)])
    # implizit wiederholte Koordinaten bei allen Befehlen
    (pts, _), = _parse_svg_path_d("m0 0 10 0 0 10 h5 5 v5 5")
    assert pts == pytest.approx([(0, 0), (10, 0), (10, 10), (15, 10), (20, 10), (20, 15), (20, 20)])
    # unbekannter Befehl beendet den Pfad statt den Token-Strom zu verschieben
    (pts, _), = _parse_svg_path_d("M0 0 L10 0 X 99 99 L5 5")
    assert pts == pytest.approx([(0, 0), (10, 0)])


def test_fill_none_with_stroke_run_and_satin(tmp_path):
    d = _load(tmp_path, '<path d="M0 0 H50 V50 H0 Z M100 0 H150 V50 H100 Z" fill="none" stroke="red" stroke-width="0.5"/>')
    assert len(d.objects) == 1
    run = d.objects[0]
    assert isinstance(run, RunObject)
    assert run.geom.length == pytest.approx(400, rel=1e-6)  # beide Teilpfade, nicht nur der erste
    assert d.build_plan().stitch_count > 100
    d2 = _load(tmp_path, '<path d="M0 0 H50" fill="none" stroke="blue" stroke-width="4" stroke-linecap="butt"/>')
    (sat,) = d2.objects
    assert isinstance(sat, SatinObject)
    assert _wh(sat.geom) == pytest.approx((50, 4), abs=1e-6)
    assert d2.build_plan().stitch_count > 50


def test_display_none_and_visibility(tmp_path):
    d = _load(tmp_path, '<g style="display:none"><rect width="50" height="50"/></g>'
                        '<rect display="none" width="50" height="50"/>'
                        '<g visibility="hidden"><rect width="50" height="50"/>'
                        '<rect x="100" width="10" height="10" visibility="visible"/></g>'
                        '<rect x="0" y="100" width="20" height="20" opacity="0"/>')
    (g,) = _areas(d)
    assert _wh(g) == pytest.approx((10, 10))


def test_defs_and_non_rendered_containers_skipped(tmp_path):
    hidden = ('<defs><rect width="50" height="50"/></defs><clipPath><circle r="9"/></clipPath>'
              '<mask><rect width="5" height="5"/></mask><symbol><rect width="5" height="5"/></symbol>'
              '<marker><path d="M0 0 L5 5 L0 5z"/></marker><pattern><rect width="3" height="3"/></pattern>'
              '<metadata><rect width="3" height="3"/></metadata>')
    with pytest.raises(ValueError):
        _load(tmp_path, hidden)
    d = _load(tmp_path, hidden + '<circle cx="100" cy="100" r="15"/>')
    (g,) = _areas(d)
    assert g.area == pytest.approx(math.pi * 225, rel=0.02)


def test_use_href_and_symbol(tmp_path):
    d = _load(tmp_path, '<defs><rect id="r" width="10" height="10" fill="green"/>'
                        '<symbol id="s"><circle cx="5" cy="5" r="5"/></symbol></defs>'
                        '<use href="#r" x="30" y="0"/>'
                        '<use xlink:href="#r" x="0" y="0" transform="translate(0,40)"/>'
                        '<use href="#s" x="60" y="0"/>')
    a, b, c = _areas(d)
    assert _wh(a) == pytest.approx((10, 10)) and _wh(b) == pytest.approx((10, 10))
    assert b.centroid.x - a.centroid.x == pytest.approx(-30)
    assert b.centroid.y - a.centroid.y == pytest.approx(40)
    assert c.centroid.x - a.centroid.x == pytest.approx(30, abs=0.05)
    assert d.objects[0].thread == nearest_thread((0, 128, 0))


def test_fill_rules(tmp_path):
    outer = "M0 0 H40 V40 H0 Z"
    inner_same = "M10 10 H30 V30 H10 Z"
    inner_rev = "M10 10 V30 H30 V10 Z"
    # evenodd: gleicher Umlaufsinn -> Loch
    (g,) = _areas(_load(tmp_path, f'<path d="{outer} {inner_same}" fill-rule="evenodd"/>'))
    assert g.area == pytest.approx(1200)
    # nonzero, gleicher Umlaufsinn -> kein Loch
    (g,) = _areas(_load(tmp_path, f'<path d="{outer} {inner_same}"/>'))
    assert g.area == pytest.approx(1600)
    # nonzero, entgegengesetzter Umlaufsinn -> Loch; Insel im Loch wieder gefüllt
    (g,) = _areas(_load(tmp_path, f'<path d="{outer} {inner_rev}" style="fill-rule:nonzero"/>'))
    assert g.area == pytest.approx(1200)
    assert len(g.interiors) == 1
    gs = _areas(_load(tmp_path, f'<path d="{outer} {inner_rev} M15 15 H25 V25 H15 Z"/>'))
    assert sum(x.area for x in gs) == pytest.approx(1300)
    # nonzero: überlappende Teilpfade werden vereinigt (nicht XOR)
    (g,) = _areas(_load(tmp_path, '<path d="M0 0 H20 V20 H0 Z M10 0 H30 V20 H10 Z"/>'))
    assert g.area == pytest.approx(600)


def test_colours_and_style_inheritance(tmp_path):
    assert _parse_svg_color("cornflowerblue") == (100, 149, 237)
    assert _parse_svg_color("RebeccaPurple") == (102, 51, 153)
    assert _parse_svg_color("darkslategrey") == (47, 79, 79)
    assert _parse_svg_color("#0f0") == (0, 255, 0)
    assert _parse_svg_color("#11223380") == (0x11, 0x22, 0x33)
    assert _parse_svg_color("rgb(100%, 50%, 0%)") == (255, 128, 0)
    assert _parse_svg_color("rgb(10 20 30)") == (10, 20, 30)
    assert _parse_svg_color("none") is None
    assert _parse_svg_color("url(#nix)") == (128, 128, 128)
    d = _load(tmp_path,
              '<linearGradient id="gr"><stop offset="0" style="stop-color:#ff0000"/><stop offset="1" stop-color="blue"/></linearGradient>'
              '<g fill="orange" stroke="none"><rect width="10" height="10"/>'
              '<rect x="20" width="10" height="10" fill="red" style="fill:navy"/>'
              '<g style="fill:teal"><rect x="40" width="10" height="10"/></g></g>'
              '<rect x="60" width="10" height="10"/>'
              '<rect x="80" width="10" height="10" fill="url(#gr)"/>'
              '<rect x="100" width="10" height="10" fill="none"/>')
    cols = [o.thread for o in d.objects]
    assert cols == [nearest_thread(c) for c in [(255, 165, 0), (0, 0, 128), (0, 128, 128), (0, 0, 0), (255, 0, 0)]]


def test_more_shapes(tmp_path):
    d = _load(tmp_path, '<ellipse cx="50" cy="50" rx="30" ry="10"/>'
                        '<rect x="0" y="100" width="40" height="30" rx="5"/>'
                        '<polyline points="100,100 140,100 140,140" fill="none" stroke="black" stroke-width="0.3"/>'
                        '<line x1="0" y1="190" x2="60" y2="190" stroke="black"/>')
    ell, rr = _areas(d)
    assert ell.area == pytest.approx(math.pi * 300, rel=0.01)
    assert rr.area == pytest.approx(40 * 30 - (4 - math.pi) * 25, rel=0.01)
    runs = [o for o in d.objects if isinstance(o, RunObject)]
    assert [r.geom.length for r in runs] == pytest.approx([80, 60])


def test_physical_size_and_document_order(tmp_path):
    body = '<rect width="250" height="100" fill="red"/><circle cx="125" cy="50" r="40" fill="blue"/>'
    p = _svg(tmp_path, body, root_attrs='width="50mm" height="20mm" viewBox="0 0 250 100"')
    d = import_svg(p, target_width_mm=None)
    g = unary_union(_areas(d))
    assert _wh(g) == pytest.approx((50, 20), rel=1e-6)
    assert [o.thread for o in d.objects][0] == nearest_thread((255, 0, 0))
    assert d.objects[-1].thread == nearest_thread((0, 0, 255))  # später = obenauf
    assert _wh(unary_union(_areas(import_svg(p)))) == pytest.approx((95, 38), rel=1e-6)
    # Zoll / Pixel ohne viewBox
    p2 = _svg(tmp_path, '<rect width="96" height="48"/>', root_attrs='width="96" height="96"', name="px.svg")
    assert _wh(unary_union(_areas(import_svg(p2, target_width_mm=None)))) == pytest.approx((25.4, 12.7), rel=1e-6)
    p3 = _svg(tmp_path, '<rect width="2" height="1"/>', root_attrs='width="2in" height="1in" viewBox="0 0 2 1"', name="in.svg")
    assert _wh(unary_union(_areas(import_svg(p3, target_width_mm=None)))) == pytest.approx((50.8, 25.4), rel=1e-6)
