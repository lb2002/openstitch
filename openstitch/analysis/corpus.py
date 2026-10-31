"""Testsammlung: typische und bösartige Designs für Simulator, Tests und Bewertung."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box

from ..auto.digitize import AutoParams, auto_digitize
from ..core.design import ColumnObject, Design, FillObject, HOOPS, RunObject, SatinObject
from ..core.stitchplan import Thread
from ..text import TextObject

RED = Thread((200, 30, 30), "Rot")
BLUE = Thread((30, 70, 200), "Blau")
GREEN = Thread((30, 150, 70), "Grün")
GOLD = Thread((235, 180, 30), "Gold")
WHITE = Thread((245, 245, 245), "Weiss")
BLACK = Thread((25, 25, 25), "Schwarz")


def _star(r1=30.0, r2=12.0, n=5):
    pts = []
    for i in range(2 * n):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / n - math.pi / 2
        pts.append((r * math.cos(a), r * math.sin(a)))
    return Polygon(pts)


def _d(*objs, hoop=None, name="corpus") -> Design:
    d = Design(name=name, objects=list(objs))
    if hoop is not None:
        d.hoop = hoop
    return d


def _sine(a=10.0, length=60.0, n=60):
    return LineString([(-length / 2 + length * i / n, a * math.sin(i / n * 2 * math.pi)) for i in range(n + 1)])


def _image_blobs(size=240):
    import cv2
    img = np.full((size, size, 4), 255, np.uint8)
    cv2.circle(img, (80, 90), 55, (220, 40, 40, 255), -1)
    cv2.rectangle(img, (120, 120), (215, 210), (20, 80, 200, 255), -1)
    cv2.ellipse(img, (70, 180), (50, 28), 25, 0, 360, (60, 170, 30, 255), -1)
    return img


def _image_logo(size=300):
    import cv2
    img = np.full((size, size, 4), 255, np.uint8)
    cv2.circle(img, (150, 150), 130, (20, 40, 120, 255), 12)
    cv2.putText(img, "OS", (60, 195), cv2.FONT_HERSHEY_DUPLEX, 4.0, (200, 20, 20, 255), 14, cv2.LINE_AA)
    return img


def _auto(img, width=80.0, colors=5) -> Design:
    return auto_digitize(img, AutoParams(width_mm=width, colors=colors)).design


def designs() -> dict[str, callable]:
    """Name → Fabrik (Fabriken, weil Bilder und Schriften erst bei Bedarf erzeugt werden sollen)."""
    return {
        "fill_circle": lambda: _d(FillObject(RED, geom=Point(0, 0).buffer(30), angle=30)),
        "fill_large": lambda: _d(FillObject(BLUE, geom=box(-55, -55, 55, 55), angle=45), hoop=HOOPS[4]),
        "fill_star": lambda: _d(FillObject(GREEN, geom=_star(), angle=10)),
        "fill_donut": lambda: _d(FillObject(RED, geom=Point(0, 0).buffer(30).difference(Point(0, 0).buffer(14)))),
        "fill_c_shape": lambda: _d(FillObject(BLUE, geom=box(-25, -25, 25, 25).difference(box(-10, -12, 30, 12)))),
        "fill_islands": lambda: _d(FillObject(GOLD, geom=MultiPolygon(
            [Point(-25, 0).buffer(10), Point(0, 18).buffer(8), Point(22, -5).buffer(12)]))),
        "fill_sliver": lambda: _d(FillObject(RED, geom=Polygon([(-30, 0), (30, -0.8), (30, 0.8)]))),
        "fill_tiny": lambda: _d(FillObject(RED, geom=Point(0, 0).buffer(1.2))),
        "fill_no_underlay": lambda: _d(FillObject(RED, geom=box(-20, -15, 20, 15), underlay=False)),
        "fill_patterns": lambda: _d(*[FillObject(c, geom=box(x, -14, x + 24, 14), pattern=p)
                                      for x, c, p in ((-44, RED, "diagonal"), (-14, BLUE, "ziegel"),
                                                      (16, GREEN, "wellen"))]),
        "fill_contour": lambda: _d(FillObject(GOLD, geom=Point(0, 0).buffer(25), pattern="kontur")),
        "satin_straight": lambda: _d(SatinObject(RED, geom=LineString([(-30, 0), (30, 0)]).buffer(2.0, cap_style=2))),
        "satin_curve": lambda: _d(SatinObject(BLUE, geom=_sine().buffer(2.5))),
        "satin_thin": lambda: _d(SatinObject(GREEN, geom=_sine().buffer(0.6))),
        "satin_wide": lambda: _d(SatinObject(GOLD, geom=LineString([(-30, 0), (30, 0)]).buffer(6.5, cap_style=2))),
        "satin_ring": lambda: _d(SatinObject(RED, geom=Point(0, 0).buffer(30).difference(Point(0, 0).buffer(25)))),
        "satin_cross": lambda: _d(SatinObject(BLUE, geom=LineString([(-25, 0), (25, 0)]).buffer(2.5, cap_style=2).union(
            LineString([(0, -25), (0, 25)]).buffer(2.5, cap_style=2)))),
        "column_arc": lambda: _d(ColumnObject(RED, geom=LineString(
            [(30 * math.cos(a / 30 * math.pi), 30 * math.sin(a / 30 * math.pi)) for a in range(31)]), width=4.0)),
        "column_corners": lambda: _d(ColumnObject(BLUE, geom=LineString([(-30, 15), (0, -15), (30, 15)]), width=3.0)),
        "column_tight": lambda: _d(ColumnObject(GREEN, geom=_sine(a=8, length=30), width=5.0)),
        "run_triple": lambda: _d(RunObject(BLACK, geom=box(-25, -25, 25, 25).exterior, repeats=1)),
        "run_spiral": lambda: _d(RunObject(RED, geom=LineString(
            [(a * 0.4 * math.cos(a), a * 0.4 * math.sin(a)) for a in np.arange(0.5, 60, 0.2)]))),
        "text_micro_25": lambda: _d(TextObject(BLACK, text="Hamburg 2.5", height=2.5, font="builtin:micro")),
        "text_micro_4": lambda: _d(TextObject(BLUE, text="OpenStitch Äöü", height=4.0, font="builtin:micro")),
        "text_micro_8": lambda: _d(TextObject(RED, text="Studio", height=8.0, font="builtin:micro")),
        "text_ttf_12": lambda: _d(TextObject(GOLD, text="Stitch", height=12.0)),
        "text_ttf_30": lambda: _d(TextObject(RED, text="AB", height=30.0)),
        "stack_badge": lambda: _d(
            FillObject(BLUE, geom=Point(0, 0).buffer(32)),
            SatinObject(GOLD, geom=Point(0, 0).buffer(33).difference(Point(0, 0).buffer(29))),
            FillObject(RED, geom=_star(20, 8)),
            TextObject(WHITE, text="OK", height=9.0)),
        "stack_overlap": lambda: _d(
            FillObject(RED, geom=box(-25, -25, 25, 25)),
            FillObject(BLUE, geom=box(-12, -12, 12, 12), angle=-45),
            FillObject(GREEN, geom=box(-6, -6, 6, 6), angle=0)),
        "many_colors": lambda: _d(*[FillObject(Thread((20 * i, 200 - 15 * i, 100)), geom=box(-40 + i * 8, -12, -33 + i * 8, 12))
                                    for i in range(11)], hoop=HOOPS[3]),
        "hoop_cap": lambda: _d(FillObject(BLUE, geom=box(-50, -15, 50, 15)), hoop=HOOPS[5]),
        "hoop_jacket": lambda: _d(FillObject(RED, geom=Point(0, 0).buffer(110)), hoop=HOOPS[8]),
        "auto_blobs": lambda: _auto(_image_blobs()),
        "auto_logo": lambda: _auto(_image_logo()),
    }


def build(name: str) -> Design:
    return designs()[name]()
