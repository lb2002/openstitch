"""Tatami-Füllstich mit Abschnittszerlegung, Musterversatz und unsichtbaren Wegen.

Arbeitsweise:
1. Polygon so drehen, dass die Stichrichtung horizontal liegt.
2. Reihen im Abstand `spacing` mit dem Polygon schneiden.
3. Reihensegmente zu Abschnitten verketten (Boustrophedon-Zerlegung), sodass jeder
   Abschnitt in einem Zug hin und her gestickt werden kann.
4. Abschnitte nach dem nächstgelegenen Einstieg ordnen; Wege dazwischen laufen entlang
   der Kontur (verdeckt) statt mit Sprungstichen.
5. Stichpunkte liegen auf einem globalen Raster mit Musterversatz pro Reihe. Das ergibt
   die gleichmässige, „gewebte“ Optik von professionellem Tatami ohne sichtbare Linien.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from shapely.geometry import LineString, Point, Polygon
from shapely.prepared import prep

from .geom import (Pt, clean, dist, path_along_ring, polygons_of, resample_path, rotate_geom,
                   rotate_pt, subdivide)

PATTERNS: dict[str, list[float]] = {
    # Versatz je Reihe als Bruchteil der Stichlänge
    "standard": [0.0, 0.4, 0.8, 0.2, 0.6],     # kaum sichtbare Diagonalen
    "diagonal": [0.0, 1 / 3, 2 / 3],          # klassisches Tatami mit leichter Diagonale
    "ziegel": [0.0, 0.5],                     # Ziegelmuster
    "wellen": [0.0, 0.25, 0.5, 0.75, 0.5, 0.25],
    "kontur": [0.0],                          # Organischer Kontur-Füllstich (folgt der Form!)
}


def contour_fill_runs(geom, spacing: float = 0.45, stitch_len: float = 2.8,
                      start: Pt | None = None) -> list[list[Pt]]:
    """Organischer Kontur-Füllstich (Contour / Spiral Fill):
    Stiche folgen konzentrischen Offset-Ringen von aussen nach innen – ideal für
    Tierfell, Blätter, Flammen und geschwungene Formen."""
    runs: list[list[Pt]] = []
    for poly in polygons_of(clean(geom, 0.1)):
        cur_geom = poly
        pts: list[Pt] = []
        depth = 0
        while not cur_geom.is_empty and depth < 250:
            depth += 1
            sub_polys = polygons_of(cur_geom)
            if not sub_polys:
                break
            # Hauptring dieses Offset-Schritts
            for sp in sub_polys:
                ring = list(sp.exterior.coords)
                if len(ring) < 3:
                    continue
                if pts:
                    k = min(range(len(ring) - 1), key=lambda i: dist(ring[i], pts[-1]))
                    ring = ring[k:-1] + ring[:k + 1]
                    if dist(pts[-1], ring[0]) <= spacing * 4.0:
                        pts.extend(resample_path([pts[-1]] + ring, stitch_len)[1:])
                    else:
                        if len(pts) >= 2:
                            runs.append(pts)
                        pts = resample_path(ring, stitch_len)
                else:
                    pts = resample_path(ring, stitch_len)
            cur_geom = cur_geom.buffer(-spacing * 1.15, join_style=1)
        if len(pts) >= 2:
            runs.append(pts)
    return runs


@dataclass
class _Seg:
    row: int
    y: float
    x0: float
    x1: float


def _row_segments(poly: Polygon, spacing: float, min_seg: float) -> list[list[_Seg]]:
    minx, miny, maxx, maxy = poly.bounds
    k0 = math.floor(miny / spacing)
    k1 = math.ceil(maxy / spacing)
    rows: list[list[_Seg]] = []
    for k in range(k0, k1 + 1):
        y = (k + 0.5) * spacing
        if y <= miny or y >= maxy:
            continue
        line = LineString([(minx - 1, y), (maxx + 1, y)])
        inter = poly.intersection(line)
        segs = []
        for g in getattr(inter, "geoms", [inter]):
            if isinstance(g, LineString) and not g.is_empty:
                xs = [c[0] for c in g.coords]
                x0, x1 = min(xs), max(xs)
                if x1 - x0 >= min_seg:
                    segs.append(_Seg(k, y, x0, x1))
        segs.sort(key=lambda s: s.x0)
        if segs:
            rows.append(segs)
    return rows


def _sections(rows: list[list[_Seg]], spacing: float) -> list[list[_Seg]]:
    done: list[list[_Seg]] = []
    open_secs: list[list[_Seg]] = []
    prev_row_k = None
    for segs in rows:
        k = segs[0].row
        if prev_row_k is not None and k - prev_row_k > 1:
            done.extend(open_secs)
            open_secs = []
        prev_row_k = k

        def ov(a: _Seg, b: _Seg) -> bool:
            return a.x0 < b.x1 and b.x0 < a.x1

        links_sec = {i: [j for j, s in enumerate(segs) if ov(sec[-1], s)] for i, sec in enumerate(open_secs)}
        links_seg = {j: [i for i, sec in enumerate(open_secs) if ov(sec[-1], s)] for j, s in enumerate(segs)}
        new_open = []
        used = set()
        for i, sec in enumerate(open_secs):
            js = links_sec[i]
            if len(js) == 1 and len(links_seg[js[0]]) == 1:
                sec.append(segs[js[0]])
                new_open.append(sec)
                used.add(js[0])
            else:
                done.append(sec)
        for j, s in enumerate(segs):
            if j not in used:
                new_open.append([s])
        open_secs = new_open
    done.extend(open_secs)
    return done


def _row_points(y: float, xa: float, xb: float, stitch_len: float, offset: float,
                min_len: float) -> list[Pt]:
    """Stichpunkte einer Reihe von xa nach xb (Richtung beliebig), inkl. Endpunkt, ohne Start."""
    lo, hi = min(xa, xb), max(xa, xb)
    n0 = math.ceil((lo - offset * stitch_len) / stitch_len)
    xs = []
    n = n0
    while True:
        x = (n + offset) * stitch_len
        if x >= hi:
            break
        if x - lo >= min_len and hi - x >= min_len:
            xs.append(x)
        n += 1
    if xa > xb:
        xs.reverse()
    return [(x, y) for x in xs] + [(xb, y)]


def _stitch_section(sec: list[_Seg], reverse_rows: bool, start_left: bool, stitch_len: float,
                    pattern: list[float], min_len: float, spacing: float) -> list[Pt]:
    rows = list(reversed(sec)) if reverse_rows else list(sec)
    pts: list[Pt] = []
    left = start_left
    for i, s in enumerate(rows):
        xa, xb = (s.x0, s.x1) if left else (s.x1, s.x0)
        start = (xa, s.y)
        if pts:
            # Verbindung entlang der Kante, ggf. unterteilt
            pts.extend(subdivide(pts[-1], start, stitch_len))
        else:
            pts.append(start)
        off = pattern[s.row % len(pattern)]
        pts.extend(_row_points(s.y, xa, xb, stitch_len, off, min_len))
        left = not left
    return pts


def _section_entries(sec: list[_Seg]):
    """Vier Einstiegsvarianten: (reverse_rows, start_left, entry, exit)."""
    out = []
    for rev in (False, True):
        rows = list(reversed(sec)) if rev else sec
        for sl in (True, False):
            first = rows[0]
            entry = (first.x0, first.y) if sl else (first.x1, first.y)
            # Ausgang: Seite hängt von Reihenanzahl ab
            last = rows[-1]
            ends_left = (sl if len(rows) % 2 == 0 else not sl)
            exit_ = (last.x0, last.y) if ends_left else (last.x1, last.y)
            out.append((rev, sl, entry, exit_))
    return out


def _travel(poly: Polygon, prepared, rings, a: Pt, b: Pt, stitch_len: float) -> list[Pt] | None:
    """Unsichtbarer Weg von a nach b innerhalb der Form oder None (→ Sprung)."""
    d_ab = dist(a, b)
    if d_ab < 0.01:
        return []
    line = LineString([a, b])
    if d_ab <= 1.2 or (d_ab <= 4.0 and prepared.contains(line)):
        return subdivide(a, b, stitch_len)
    best = None
    for ring in rings:
        da = ring.distance(Point(a))
        db = ring.distance(Point(b))
        if da < 1.2 and db < 1.2:
            path = path_along_ring(ring, a, b)
            L = sum(dist(p, q) for p, q in zip(path, path[1:]))
            if L <= max(18.0, d_ab * 2.2) and (best is None or L < best[0]):
                best = (L, path)
    if best is None:
        return None
    path = [a] + best[1] + [b]
    return resample_path(path, stitch_len)[1:]


def join_covered_runs(runs: list[list[Pt]], geom, stitch_len: float = 2.5) -> list[list[Pt]]:
    """Verbindet aufeinanderfolgende Läufe mit Laufstichen innerhalb von `geom` statt Trim + Sprung.

    Nur für Läufe, die anschliessend noch überstickt werden (Unterlage → Deckstich,
    Satin-Endkappen → Satinsäule): die Wege liegen dann verdeckt unter dem Deckstich."""
    if len(runs) < 2 or geom is None or geom.is_empty:
        return runs
    area = geom.buffer(0.05)
    prepared = prep(area)
    rings = []
    for p in polygons_of(geom.buffer(-0.3)) or polygons_of(geom):
        rings.append(p.exterior)
        rings.extend(p.interiors)
    out = [list(runs[0])]
    for r in runs[1:]:
        a, b = out[-1][-1], r[0]
        if dist(a, b) < 1e-6 or prepared.contains(LineString([a, b])):
            tr = subdivide(a, b, stitch_len)
        else:
            tr = _travel(area, prepared, rings, a, b, stitch_len)
        if tr is None:
            out.append(list(r))
        else:
            out[-1].extend(tr)
            out[-1].extend(r[1:])
    return out


def fill_runs(geom, angle: float = 45.0, spacing: float = 0.4, stitch_len: float = 3.5,
              pattern: str = "standard", start: Pt | None = None,
              min_len: float = 0.6) -> list[list[Pt]]:
    """Erzeugt Füllstich-Läufe. Jeder Lauf ist zusammenhängend; zwischen Läufen wird gesprungen."""
    if pattern == "kontur":
        return contour_fill_runs(geom, spacing=spacing, stitch_len=min(stitch_len, 2.8), start=start)
    pat = PATTERNS.get(pattern, PATTERNS["standard"])
    runs: list[list[Pt]] = []
    cur = start
    polys = polygons_of(clean(geom, 0.05))
    # Teilflächen nach Nähe zum aktuellen Punkt sortieren
    remaining = list(polys)
    while remaining:
        if cur is not None:
            remaining.sort(key=lambda p: p.exterior.distance(Point(cur)))
        poly = remaining.pop(0)
        rpoly = rotate_geom(poly, -angle, origin=(0, 0))
        rcur = rotate_pt(cur, -angle) if cur is not None else None
        rows = _row_segments(rpoly, spacing, min_seg=min(0.3, spacing))
        secs = _sections(rows, spacing)
        if not secs:
            continue
        prepared = prep(rpoly.buffer(0.05))
        inset = rpoly.buffer(-0.25)
        rings = []
        for ip in polygons_of(inset):
            rings.append(ip.exterior)
            rings.extend(ip.interiors)
        if not rings:
            rings = [rpoly.exterior] + list(rpoly.interiors)

        pts_run: list[Pt] = []
        todo = list(range(len(secs)))
        while todo:
            ref = pts_run[-1] if pts_run else rcur
            best = None
            for si in todo:
                for rev, sl, entry, exit_ in _section_entries(secs[si]):
                    d = dist(ref, entry) if ref is not None else 0.0
                    if best is None or d < best[0]:
                        best = (d, si, rev, sl, entry)
            _, si, rev, sl, entry = best
            todo.remove(si)
            sec_pts = _stitch_section(secs[si], rev, sl, stitch_len, pat, min_len, spacing)
            if pts_run:
                tr = _travel(rpoly, prepared, rings, pts_run[-1], sec_pts[0], stitch_len)
                if tr is None:
                    runs.append([rotate_pt(p, angle) for p in pts_run])
                    pts_run = list(sec_pts)
                else:
                    pts_run.extend(tr)
                    pts_run.extend(sec_pts[1:])
            else:
                pts_run = list(sec_pts)
        if pts_run:
            runs.append([rotate_pt(p, angle) for p in pts_run])
            cur = runs[-1][-1]
    return runs
