"""Tests für die Einstrich-Kleinschrift „OpenStitch Micro“ und den Säulen-Generator."""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from openstitch.core.design import Design, object_from_dict
from openstitch.core.stitchplan import Cmd, Thread
from openstitch.engine.column import column_runs
from openstitch.fonts_micro import CHARSET, GLYPHS, MICRO_SPEC, glyph
from openstitch.text import TextObject, default_font, list_fonts

SAMPLE = "Micro 2.5: Äpfel & Öl für 12 € – ß?"


def _plan_stats(plan):
    longest, nan, prev = 0.0, 0, None
    for b in plan.blocks:
        prev = None
        for s in b.stitches:
            if not (math.isfinite(s.x) and math.isfinite(s.y)):
                nan += 1
                continue
            if s.cmd == Cmd.STITCH:
                if prev is not None:
                    longest = max(longest, math.hypot(s.x - prev[0], s.y - prev[1]))
                prev = (s.x, s.y)
            elif s.cmd == Cmd.JUMP:
                prev = (s.x, s.y)
    return longest, nan


def test_every_listed_character_has_glyph_data():
    required = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
                " .,:;!?-_'\"()/&+@#%*ÄÖÜäöüßÉÈÊÀÇéèêàâçôîïñÑ¿¡")
    for ch in required:
        assert ch in CHARSET
        assert ch in GLYPHS, f"Glyphe fehlt: {ch!r}"
        adv, strokes = GLYPHS[ch]
        assert adv > 0
        if ch != " ":
            assert strokes, f"keine Striche: {ch!r}"
        for s in strokes:
            assert s and all(math.isfinite(x) and math.isfinite(y) for x, y in s)
            # Einheits-Box: Versalhöhe 1.0, kleine Über-/Unterlängen erlaubt
            assert all(-0.45 <= y <= 1.45 and -0.2 <= x <= adv + 0.2 for x, y in s), ch
    # unbekannte Akzentbuchstaben fallen auf den Grundbuchstaben zurück
    assert glyph("ú") is GLYPHS["u"]


def test_micro_font_listed_first_and_not_default():
    fonts = list_fonts()
    first_name, first_spec = next(iter(fonts.items()))
    assert first_name == "OpenStitch Micro" and first_spec == MICRO_SPEC
    assert default_font() != MICRO_SPEC


@pytest.mark.parametrize("height", [2.5, 8.0])
def test_micro_text_builds_clean_plan(height):
    d = Design()
    t = TextObject(Thread((20, 30, 90), "Blau"), text=SAMPLE.replace("€", "EUR"), font=MICRO_SPEC,
                   height=height, letter_spacing=0.0)
    d.objects.append(t)
    plan = d.build_plan()
    longest, nan = _plan_stats(plan)
    assert nan == 0
    assert longest <= 7.0, f"Stich zu lang: {longest:.2f} mm"
    n = plan.stitch_count
    n_chars = len(SAMPLE.replace(" ", ""))
    # grob: 20 – 400 Stiche je Zeichen (Dreifachstich klein, Satin gross)
    assert 20 * n_chars < n < 400 * n_chars
    # Auswahlrahmen/Trefferprüfung: Geometrie deckt die Schrift ab
    x0, y0, x1, y1 = t.bounds()
    assert x1 - x0 > height * 5 and y1 - y0 >= height * 0.9


def test_micro_text_respects_transform_and_arc():
    t = TextObject(Thread((0, 0, 0)), text="ARC", font=MICRO_SPEC, height=6.0, arc_radius=30.0)
    runs = t.runs()
    assert runs and all(len(r) >= 2 for r in runs)
    w0 = max(p[0] for r in runs for p in r) - min(p[0] for r in runs for p in r)
    t.transform = (2.0, 0.0, 0.0, 2.0, 10.0, 5.0)
    xs = [p[0] for r in t.runs() for p in r]
    assert abs((max(xs) + min(xs)) / 2 - 10.0) < 1.5          # zentriert um die Verschiebung
    assert 1.8 * w0 < max(xs) - min(xs) < 2.3 * w0           # skaliert (inkl. breiterer Säule)


def test_column_straight_line_rail_spacing():
    run = column_runs([(0.0, 0.0), (10.0, 0.0)], 1.0, spacing=0.4, pull_comp=0.1, underlay="none")[0]
    # Einstiche wechseln die Seite; auf derselben Kante liegen sie `spacing` auseinander
    left = [p for p in run if p[1] > 0]
    right = [p for p in run if p[1] < 0]
    assert abs(len(left) - len(right)) <= 1
    for rail in (left, right):
        gaps = [b[0] - a[0] for a, b in zip(rail, rail[1:])]
        assert all(abs(g - 0.4) < 0.02 for g in gaps)
    # Breite inkl. Zugkompensation
    assert all(abs(abs(p[1]) - 0.6) < 1e-6 for p in run)


def test_column_underlay_and_bean_fallback():
    with_ul = column_runs([(0, 0), (8, 0)], 1.6, underlay="center")[0]
    no_ul = column_runs([(0, 0), (8, 0)], 1.6, underlay="none")[0]
    assert len(with_ul) > len(no_ul)
    # Unterlage = Mittellauf: beginnt auf der Mittellinie
    assert abs(with_ul[0][1]) < 1e-6
    narrow = column_runs([(0, 0), (8, 0)], 0.9, underlay="center")[0]
    assert all(abs(abs(p[1]) - 0.55) < 1e-6 for p in narrow)   # < 1.0 mm: keine Unterlage
    bean = column_runs([(0, 0), (8, 0)], 0.5)[0]
    assert all(abs(p[1]) < 1e-9 for p in bean)                    # < 0.7 mm: Dreifachstich
    assert len(bean) > 3 * 8 / 1.0


def test_column_start_chooses_direction():
    run = column_runs([(0, 0), (8, 0)], 1.0, underlay="none", start=(9, 0))[0]
    assert run[0][0] > 7.5 and run[-1][0] < 0.5


@pytest.mark.parametrize("opening", [30, 50, 70, 100])
@pytest.mark.parametrize("width", [0.8, 1.5])
def test_sharp_v_corner_has_no_needle_pileup(opening, width):
    a = math.radians(opening / 2)
    V = [(-5 * math.sin(a), -5 * math.cos(a)), (0.0, 0.0), (5 * math.sin(a), -5 * math.cos(a))]
    pts = [p for r in column_runs(V, width, 0.4, 0.1, "center") for p in r]
    assert pts
    # in keinem Kreis von 0.5 mm Durchmesser mehr als 6 Einstiche
    worst = max(sum(1 for q in pts if math.dist(p, q) <= 0.25) for p in pts)
    assert worst <= 6
    # und die Spitze ist überhaupt gestickt
    assert min(math.dist(p, (0, 0)) for p in pts) < width


def test_micro_text_save_load_roundtrip():
    t = TextObject(Thread((200, 10, 10), "Rot"), text="Grüße", font=MICRO_SPEC, height=4.0,
                   letter_spacing=0.2, arc_radius=-40.0, density=0.38)
    d = t.to_dict()
    assert d["font"] == MICRO_SPEC
    t2 = object_from_dict(d)
    assert isinstance(t2, TextObject)
    assert (t2.text, t2.font, t2.height, t2.letter_spacing, t2.arc_radius, t2.density) == \
        ("Grüße", MICRO_SPEC, 4.0, 0.2, -40.0, 0.38)
    assert t2.runs() == t.runs()
