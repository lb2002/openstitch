"""Beispiel-Designs für die Startseite: fertige Motive zum Ausprobieren und Abwandeln."""
from __future__ import annotations

import math

from shapely.geometry import LineString, Point, Polygon, box

from .core.design import ColumnObject, Design, FillObject, HOOPS, RunObject, SatinObject
from .core.stitchplan import Thread
from .text import TextObject

NAVY = Thread((24, 42, 92), "Navy")
GOLD = Thread((232, 176, 40), "Gold")
RED = Thread((205, 38, 52), "Red")
GREEN = Thread((44, 138, 84), "Green")
WHITE = Thread((245, 245, 245), "White")
ROSE = Thread((232, 120, 150), "Pink")
LEAF = Thread((88, 150, 70), "Leaf")
YELLOW = Thread((248, 205, 70), "Yellow")


def _heart(size: float) -> Polygon:
    pts = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * size / 32, -y * size / 32))
    return Polygon(pts)


def name_patch() -> Design:
    """Namensschild: Rand als Satin, Name in der Kleinschrift-tauglichen Einstrich-Schrift."""
    outer = box(-40, -14, 40, 14).buffer(6, join_style=1).buffer(-3)
    inner = outer.buffer(-3.2)
    d = Design(name="Name_Patch", hoop=HOOPS[2])
    d.objects.append(FillObject(NAVY, name="Background", geom=inner.buffer(0.4), angle=20))
    d.objects.append(SatinObject(GOLD, name="Border", geom=outer.difference(inner)))
    d.objects.append(TextObject(WHITE, name="Name", text="Your Name", height=9.0, font="builtin:micro"))
    return d


def heart() -> Design:
    d = Design(name="Heart", hoop=HOOPS[1])
    shape = _heart(62)
    d.objects.append(FillObject(RED, name="Heart", geom=shape, angle=35, pattern="ziegel"))
    d.objects.append(SatinObject(ROSE, name="Outline", geom=shape.buffer(1.4).difference(shape.buffer(-1.6))))
    return d


def flower() -> Design:
    d = Design(name="Flower", hoop=HOOPS[1])
    stem = LineString([(0, 6), (3, 24), (-1, 42)])
    d.objects.append(ColumnObject(LEAF, name="Stem", geom=stem, width=2.6))
    leaf = Polygon([(2, 30), (12, 21), (22, 22), (13, 31)]).buffer(1.2, join_style=1)
    d.objects.append(FillObject(LEAF, name="Leaf", geom=leaf, angle=-30))
    for i in range(6):
        a = i * math.pi / 3
        petal = Point(13 * math.cos(a), -8 + 13 * math.sin(a)).buffer(7.5)
        d.objects.append(SatinObject(ROSE, name=f"Petal {i + 1}", geom=petal))
    d.objects.append(FillObject(YELLOW, name="Center", geom=Point(0, -8).buffer(7), angle=60))
    return d


def monogram() -> Design:
    d = Design(name="Monogram", hoop=HOOPS[1])
    d.objects.append(SatinObject(GREEN, name="Ring", geom=Point(0, 0).buffer(32).difference(Point(0, 0).buffer(29))))
    d.objects.append(RunObject(GREEN, name="Inner ring", geom=Point(0, 0).buffer(26).exterior, repeats=1))
    d.objects.append(TextObject(GOLD, name="Monogram", text="AB", height=26.0))
    return d


SAMPLES = (
    ("patch", "sample_patch", name_patch),
    ("heart", "sample_heart", heart),
    ("flower", "sample_flower", flower),
    ("monogram", "sample_monogram", monogram),
)
