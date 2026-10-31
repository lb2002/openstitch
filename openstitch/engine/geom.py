"""Geometrie-Hilfsfunktionen (Shapely-basiert)."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from shapely import affinity
from shapely.geometry import (GeometryCollection, LinearRing, LineString, MultiLineString,
                              MultiPolygon, Point, Polygon)
from shapely.ops import unary_union

Pt = tuple[float, float]


def polygons_of(geom) -> list[Polygon]:
    """Liefert alle Polygone einer beliebigen Geometrie."""
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, (MultiPolygon, GeometryCollection)):
        out = []
        for g in geom.geoms:
            out.extend(polygons_of(g))
        return out
    return []


def lines_of(geom) -> list[LineString]:
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, LineString):
        return [geom]
    if isinstance(geom, LinearRing):
        return [LineString(geom.coords)]
    if isinstance(geom, (MultiLineString, GeometryCollection)):
        out = []
        for g in geom.geoms:
            out.extend(lines_of(g))
        return out
    return []


def clean(geom, min_area: float = 0.0):
    """Repariert ungültige Geometrie und entfernt Kleinstteile."""
    if geom is None or geom.is_empty:
        return MultiPolygon()
    if not geom.is_valid:
        geom = geom.buffer(0)
    polys = [p for p in polygons_of(geom) if p.area > min_area]
    if not polys:
        return MultiPolygon()
    return unary_union(polys)


def dist(a: Pt, b: Pt) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def subdivide(a: Pt, b: Pt, max_len: float, include_start: bool = False) -> list[Pt]:
    """Punkte auf der Strecke a→b mit Abstand ≤ max_len (ohne a, mit b)."""
    d = dist(a, b)
    n = max(1, int(math.ceil(d / max_len - 1e-9)))
    pts = [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]
    return ([a] if include_start else []) + pts


def resample_path(coords: Iterable[Pt], step: float, closed: bool = False) -> list[Pt]:
    """Gleichmässige Punkte entlang eines Pfades, Ecken bleiben erhalten."""
    coords = [tuple(c) for c in coords]
    if closed and coords and coords[0] != coords[-1]:
        coords.append(coords[0])
    if len(coords) < 2:
        return coords
    out = [coords[0]]
    for a, b in zip(coords, coords[1:]):
        if dist(a, b) < 1e-6:
            continue
        # Ecke beibehalten: jedes Segment für sich unterteilen
        out.extend(subdivide(a, b, step))
    return merge_short(out, step * 0.35)


def resample_uniform(coords: Iterable[Pt], step: float, closed: bool = False) -> list[Pt]:
    """Exakt gleiche Abstände entlang des Pfades, unabhängig von der Dichte der Stützpunkte.

    Für Satin-Querschnitte: `resample_path` unterteilt jedes Segment für sich und kann dadurch den
    Abstand nie über den der Stützpunkte hinaus vergrössern (Skelette liegen dicht)."""
    arr = np.array([tuple(c) for c in coords], float)
    if closed and len(arr) and tuple(arr[0]) != tuple(arr[-1]):
        arr = np.vstack((arr, arr[0]))
    if len(arr) < 2:
        return [tuple(p) for p in arr]
    seg = np.hypot(*np.diff(arr, axis=0).T)
    keep = np.concatenate(([True], seg > 1e-9))
    arr = arr[keep]
    cum = np.concatenate(([0.0], np.cumsum(np.hypot(*np.diff(arr, axis=0).T))))
    total = float(cum[-1])
    if total < 1e-9:
        return [tuple(arr[0])]
    n = max(1, int(round(total / step)))
    s = np.linspace(0.0, total, n + 1)
    return list(zip(np.interp(s, cum, arr[:, 0]).tolist(), np.interp(s, cum, arr[:, 1]).tolist()))


def merge_short(pts: list[Pt], min_len: float) -> list[Pt]:
    """Entfernt sehr kurze Stiche (Fadenbruch-Gefahr) ohne Endpunkt zu verlieren."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:-1]:
        if dist(out[-1], p) >= min_len:
            out.append(p)
    if dist(out[-1], pts[-1]) < min_len and len(out) > 1:
        out[-1] = pts[-1]
    else:
        out.append(pts[-1])
    return out


def rotate_geom(geom, angle_deg: float, origin=(0, 0)):
    return affinity.rotate(geom, angle_deg, origin=origin, use_radians=False)


def rotate_pt(p: Pt, angle_deg: float, origin=(0.0, 0.0)) -> Pt:
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    x, y = p[0] - origin[0], p[1] - origin[1]
    return (origin[0] + x * c - y * s, origin[1] + x * s + y * c)


def directional_grow(geom, amount: float, angle_deg: float):
    """Zugkompensation: dehnt die Form entlang der Stichrichtung (angle_deg) um `amount` je Seite.

    Faden zieht den Stoff in Stichrichtung zusammen – darum wird nur in dieser
    Richtung verbreitert (wie bei kommerziellen Programmen)."""
    if amount <= 0 or geom.is_empty:
        return geom
    dx = math.cos(math.radians(angle_deg)) * amount
    dy = math.sin(math.radians(angle_deg)) * amount
    parts = [affinity.translate(geom, dx * t, dy * t) for t in np.linspace(-1, 1, 7)]
    return unary_union(parts).buffer(0.01).buffer(-0.01)


def nearest_point_on_ring(ring: LinearRing, p: Pt) -> float:
    return ring.project(Point(p))


def path_along_ring(ring, p: Pt, q: Pt) -> list[Pt]:
    """Kürzester Weg von p nach q entlang eines Rings (für unsichtbare Verbindungsstiche)."""
    line = LineString(ring.coords)
    L = line.length
    if L == 0:
        return [p, q]
    a = line.project(Point(p))
    b = line.project(Point(q))
    coords = list(line.coords)
    # kumulierte Längen
    cum = [0.0]
    for u, v in zip(coords, coords[1:]):
        cum.append(cum[-1] + dist(u, v))

    def walk(s0: float, s1: float, forward: bool) -> list[Pt]:
        pts = [tuple(line.interpolate(s0).coords[0])]
        if forward:
            if s1 < s0:
                s1 += L
            # Auch der Startpunkt des Rings ist eine Ecke: Ohne ihn schneidet der Weg dort ab
            idx = [c for c in cum[:-1]] + [c + L for c in cum[:-1]]
            for c in idx:
                if s0 < c < s1:
                    pts.append(tuple(line.interpolate(c % L).coords[0]))
        else:
            if s1 > s0:
                s1 -= L
            idx = sorted([c for c in cum[:-1]] + [c - L for c in cum[:-1]], reverse=True)
            for c in idx:
                if s1 < c < s0:
                    pts.append(tuple(line.interpolate(c % L).coords[0]))
        pts.append(tuple(line.interpolate(s1 % L).coords[0]))
        return pts

    fwd_len = (b - a) % L
    if fwd_len <= L / 2:
        return walk(a, b, True)
    return walk(a, b, False)


def main_axis_angle(geom) -> float:
    """Winkel (Grad) der Längsachse der minimal umschliessenden Box."""
    if geom.is_empty:
        return 0.0
    rect = geom.minimum_rotated_rectangle
    if not isinstance(rect, Polygon):
        return 0.0
    c = list(rect.exterior.coords)
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    e = e1 if math.hypot(*e1) >= math.hypot(*e2) else e2
    return math.degrees(math.atan2(e[1], e[0]))
