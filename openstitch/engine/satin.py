"""Satinstich mit automatischer Mittellinie (Skelett), drehender Stichrichtung,
Kurzstich in Innenkurven, Split-Satin für breite Säulen und Unterlage.

Die Mittellinie wird aus einem Rasterbild der Form per Skelettierung gewonnen und in
Äste zerlegt. Für jeden Ast werden die Stiche senkrecht zur lokalen Richtung gelegt.
So drehen sich die Stiche fliessend um Kurven wie bei handdigitalisierten Buchstaben.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np
from scipy import ndimage
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
from skimage.morphology import skeletonize

from .geom import Pt, clean, dist, polygons_of, resample_path, resample_uniform, subdivide

RES = 0.16  # mm pro Pixel (2.5x schneller bei identischer Stickgenauigkeit)


@dataclass
class Branch:
    pts: list[Pt]            # Mittellinie in mm
    hw: list[float]          # halbe Breite je Punkt
    leaf_start: bool = False
    leaf_end: bool = False


@dataclass
class SatinResult:
    runs: list[list[Pt]] = field(default_factory=list)
    leftover: object = None   # nicht abgedeckte Fläche (→ Füllstich)


# ---------------------------------------------------------------------------
# Skelett
# ---------------------------------------------------------------------------
def _rasterize(poly, res: float):
    minx, miny, maxx, maxy = poly.bounds
    pad = 3
    w = int(math.ceil((maxx - minx) / res)) + 2 * pad
    h = int(math.ceil((maxy - miny) / res)) + 2 * pad
    img = np.zeros((h, w), np.uint8)
    ox, oy = minx - pad * res, miny - pad * res

    def to_px(coords):
        return np.array([[(x - ox) / res, (y - oy) / res] for x, y in coords], np.int32)

    for p in polygons_of(poly):
        cv2.fillPoly(img, [to_px(p.exterior.coords)], 1)
        for hole in p.interiors:
            cv2.fillPoly(img, [to_px(hole.coords)], 0)
    return img, ox, oy


_NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def _trace_branches(sk: np.ndarray) -> list[list[tuple[int, int]]]:
    pix = set(zip(*np.nonzero(sk)))

    def nbrs(p):
        r, c = p
        return [(r + dr, c + dc) for dr, dc in _NB if (r + dr, c + dc) in pix]

    deg = {p: len(nbrs(p)) for p in pix}
    nodes = {p for p, d in deg.items() if d != 2}
    visited_edges = set()
    branches = []
    for n in nodes:
        for nb in nbrs(n):
            if (n, nb) in visited_edges:
                continue
            path = [n, nb]
            visited_edges.add((n, nb))
            visited_edges.add((nb, n))
            prev, cur = n, nb
            while cur not in nodes:
                nxt = [q for q in nbrs(cur) if q != prev and (cur, q) not in visited_edges]
                if not nxt:
                    break
                # bevorzugt 4-Nachbarn (glatterer Pfad)
                nxt.sort(key=lambda q: abs(q[0] - cur[0]) + abs(q[1] - cur[1]))
                q = nxt[0]
                visited_edges.add((cur, q))
                visited_edges.add((q, cur))
                path.append(q)
                prev, cur = cur, q
            branches.append(path)
    # Reine Schleifen (z. B. Buchstabe O) ohne Knoten
    seen = {p for b in branches for p in b}
    for p in pix:
        if p in seen or deg[p] != 2:
            continue
        loop = [p]
        seen.add(p)
        prev, cur = None, p
        while True:
            nxt = [q for q in nbrs(cur) if q != prev and q not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            loop.append(cur)
            seen.add(cur)
        if len(loop) > 3:
            loop.append(loop[0])
            branches.append(loop)
    return branches, deg


def skeleton_branches(poly, res: float = RES, prune_factor: float = 1.6) -> list[Branch]:
    img, ox, oy = _rasterize(poly, res)
    dt = ndimage.distance_transform_edt(img) * res
    sk = skeletonize(img > 0)
    for _ in range(3):
        branches, deg = _trace_branches(sk)
        changed = False
        for b in branches:
            a, z = b[0], b[-1]
            leaf = (deg.get(a, 0) == 1) != (deg.get(z, 0) == 1)  # genau ein Blatt-Ende
            if not leaf:
                continue
            junction = z if deg.get(a, 0) == 1 else a
            length = len(b) * res
            if length < prune_factor * dt[junction] and len(branches) > 1:
                for p in b:
                    if p != junction:
                        sk[p] = False
                changed = True
        if not changed:
            break
        sk = skeletonize(sk)
    branches, deg = _trace_branches(sk)
    out = []
    for b in branches:
        if len(b) < 3:
            continue
        pts = [(ox + c * res, oy + r * res) for r, c in b]
        hw = [float(dt[r, c]) for r, c in b]
        out.append(Branch(pts, hw, deg.get(b[0], 0) == 1, deg.get(b[-1], 0) == 1))
    return out


def _smooth(pts: list[Pt], win: int) -> list[Pt]:
    if len(pts) < 3 or win < 2:
        return pts
    a = np.array(pts, float)
    closed = dist(pts[0], pts[-1]) < 1e-6
    k = np.ones(win) / win
    if closed:
        ext = np.concatenate([a[-win:-1], a, a[1:win]])
        xs = np.convolve(ext[:, 0], k, "same")[win - 1:win - 1 + len(a)]
        ys = np.convolve(ext[:, 1], k, "same")[win - 1:win - 1 + len(a)]
    else:
        pad = win
        ext = np.concatenate([np.repeat(a[:1], pad, 0), a, np.repeat(a[-1:], pad, 0)])
        xs = np.convolve(ext[:, 0], k, "same")[pad:pad + len(a)]
        ys = np.convolve(ext[:, 1], k, "same")[pad:pad + len(a)]
        xs[0], ys[0], xs[-1], ys[-1] = a[0, 0], a[0, 1], a[-1, 0], a[-1, 1]
    return list(zip(xs.tolist(), ys.tolist()))


# ---------------------------------------------------------------------------
# Satin entlang eines Asts
# ---------------------------------------------------------------------------
def _rails_for_branch(poly, prepared_poly, br: Branch, spacing: float, pull_comp: float,
                      covered=None):
    """Liefert Liste von (center, left, right) Querschnitten."""
    pts = _smooth(br.pts, 9)
    # Enden bis zum Rand verlängern (innerhalb des Polygons)
    def extend(p, q, hw):
        d = dist(q, p)
        if d < 1e-9:
            return []
        ux, uy = (p[0] - q[0]) / d, (p[1] - q[1]) / d
        out_ext = []
        for t in (0.3, 0.6, 0.85):
            cand = (p[0] + ux * hw * t, p[1] + uy * hw * t)
            if prepared_poly.contains(Point(cand)):
                out_ext.append(cand)
        return out_ext

    closed = dist(pts[0], pts[-1]) < 0.35
    if closed:
        pts[-1] = pts[0]
    else:
        step_k = min(4, len(pts) - 1)
        if br.leaf_start and step_k >= 1:
            pts = list(reversed(extend(pts[0], pts[step_k], min(br.hw[0], 2.5)))) + pts
        if br.leaf_end and step_k >= 1:
            pts = pts + extend(pts[-1], pts[-1 - step_k], min(br.hw[-1], 2.5))
    path = resample_uniform(pts, spacing / 2.0, closed=closed)
    if len(path) < 2:
        return []
    arr = np.array(path)
    # Tangenten über ein breiteres Fenster → ruhige Stichrichtung
    n = len(arr)
    out = []
    win = max(2, int(round(0.8 / (spacing / 2))))
    hw_line = LineString(br.pts) if len(br.pts) > 1 else None
    bp = np.array(br.pts, float)
    for i in range(n):
        if closed:
            a = arr[(i - win) % (n - 1)]
            b = arr[(i + win) % (n - 1)]
        else:
            a = arr[max(0, i - win)]
            b = arr[min(n - 1, i + win)]
        t = b - a
        tl = math.hypot(*t)
        if tl < 1e-9:
            continue
        nx, ny = -t[1] / tl, t[0] / tl
        c = tuple(arr[i])
        if covered is not None and covered.contains(Point(c)):
            out.append(None)
            continue
        # lokale halbe Breite aus dem Skelett
        if hw_line is not None:
            d2 = (bp[:, 0] - c[0]) ** 2 + (bp[:, 1] - c[1]) ** 2
            hw = br.hw[int(np.argmin(d2))]
        else:
            hw = 1.0
        reach = hw * 1.6 + 0.6
        ray = LineString([(c[0] - nx * reach, c[1] - ny * reach), (c[0] + nx * reach, c[1] + ny * reach)])
        inter = poly.intersection(ray)
        seg = None
        for g in getattr(inter, "geoms", [inter]):
            if isinstance(g, LineString) and g.distance(Point(c)) < 0.15:
                seg = g
                break
        if seg is None:
            continue
        p0, p1 = seg.coords[0], seg.coords[-1]
        # Seiten zuordnen und begrenzen
        def side_dist(p):
            return (p[0] - c[0]) * nx + (p[1] - c[1]) * ny
        dl, dr = side_dist(p0), side_dist(p1)
        if dl > dr:
            dl, dr = dr, dl
        lim = hw * 1.3 + 0.25
        dl = max(dl, -lim) - pull_comp
        dr = min(dr, lim) + pull_comp
        if dr - dl < 0.3:
            continue
        L = (c[0] + nx * dl, c[1] + ny * dl)
        R = (c[0] + nx * dr, c[1] + ny * dr)
        out.append((c, L, R))
    return out


def _split_runs(cross):
    runs, cur = [], []
    for x in cross:
        if x is None:
            if len(cur) >= 2:
                runs.append(cur)
            cur = []
        else:
            cur.append(x)
    if len(cur) >= 2:
        runs.append(cur)
    return runs


def _zigzag(cross, max_stitch: float, short_stitch: bool = True) -> list[Pt]:
    """Echter Satin-Zickzack: jeder Querschnitt (im Abstand spacing/2) wechselt die Seite L ↔ R.

    Damit beträgt der Abstand zweier Einstiche auf derselben Kante exakt `spacing` (z. B. 0.40 mm).
    In engen Innenkurven verkürzt Short-Stitching jeden zweiten Einstich auf der Innenseite,
    damit keine Fadenknäuel (Stichhäufung) entstehen."""
    pts: list[Pt] = []
    for i, (c, L, R) in enumerate(cross):
        target = L if (i % 2 == 0) else R
        # Kurzstich: wenn auf derselben Seite der Abstand zum vorletzten Einstich sehr klein ist (< 0.22 mm)
        if short_stitch and i >= 2 and (i // 2) % 2 == 1:
            prev_same_side = cross[i - 2][1 if (i % 2 == 0) else 2]
            if dist(prev_same_side, target) < 0.22:
                target = (target[0] * 0.68 + c[0] * 0.32, target[1] * 0.68 + c[1] * 0.32)
        if not pts:
            pts.append(target)
            continue
        prev = pts[-1]
        w = dist(prev, target)
        # Split-Satin bei breiten Säulen (> max_stitch): versetzte Zwischenstiche
        if w > max_stitch:
            # Der Versatz verlängert ein Teilstück um 17.5 % → auch das muss unter max_stitch bleiben
            nseg = int(math.ceil(w * 1.175 / max_stitch))
            shift = 0.35 if (i % 2) else -0.35
            for k in range(1, nseg):
                t = max(0.15, min(0.85, (k + shift * 0.5) / nseg))
                pts.append((prev[0] + (target[0] - prev[0]) * t, prev[1] + (target[1] - prev[1]) * t))
        pts.append(target)
    return pts


UNDERLAY_STYLES = ["auto", "mitte", "kante", "zickzack", "kante+zickzack"]


def auto_underlay_style(width_avg: float) -> str:
    """Wie kommerzielle Software: schmal → Mittellauf, mittel → Kantenlauf, breit → Kante + Zickzack."""
    if width_avg <= 2.0:
        return "mitte"
    if width_avg <= 4.5:
        return "kante"
    return "kante+zickzack"


def _edge_walk(cross, inset: float = 0.45) -> list[Pt]:
    """Kantenlauf: entlang der linken Kante hin, entlang der rechten zurück (stabilisiert beide Ränder)."""
    def ins(c, p):
        d = dist(c, p)
        if d < inset * 2:
            return c
        return (c[0] + (p[0] - c[0]) * (d - inset) / d, c[1] + (p[1] - c[1]) * (d - inset) / d)
    left = [ins(c, L) for c, L, _ in cross]
    right = [ins(c, R) for c, _, R in reversed(cross)]
    return resample_path(left + right, 2.0)


def _underlay(cross, width_avg: float, spacing: float, style: str = "auto") -> list[Pt]:
    """Unterlage je nach Stil: Mittellauf, Kantenlauf, Zickzack oder Kante + Zickzack."""
    if style == "auto":
        style = auto_underlay_style(width_avg)
    if style == "kante":
        return _edge_walk(cross)
    centers = [c for c, _, _ in cross]
    out = _edge_walk(cross) if style == "kante+zickzack" else resample_path(centers, 2.0)
    if style == "kante+zickzack":
        # Kantenlauf endet am Start → Zickzack läuft hin (Satin kommt dann zurück)
        cross = list(reversed(cross))
    if style in ("zickzack", "kante+zickzack"):
        back = list(reversed(cross))
        zz = []
        step = max(1, int(round(2.2 / (spacing / 2))))
        for i, (c, L, R) in enumerate(back[::step]):
            inset = 0.45
            def ins(p):
                d = dist(c, p)
                if d < inset * 2:
                    return c
                return (c[0] + (p[0] - c[0]) * (d - inset) / d, c[1] + (p[1] - c[1]) * (d - inset) / d)
            zz.append(ins(L) if i % 2 == 0 else ins(R))
        if zz:
            out.extend(subdivide(out[-1], zz[0], 3.0))
            for p in zz[1:]:
                out.extend(subdivide(out[-1], p, 7.0))
    return out


def _pinch_end_caps(cross, n_taper: int = 5):
    """Für 3D-Puff-Foam: Verjüngt die ersten und letzten Querschnitte einer offenen Satinsäule
    keilförmig zur Mitte hin ('Pinch-Cap'), damit der 3D-Schaumstoff an den Säulenenden komplett
    eingeschlossen und sauber perforiert wird."""
    if len(cross) < 4:
        return cross
    c0, c_last = cross[0][0], cross[-1][0]
    if dist(c0, c_last) < 0.6:
        return cross  # geschlossener Ring braucht keine End-Caps
    out = list(cross)
    # Zusätzliche dichte Perforations-Stiche am Start- und Endrand
    for end_idx, direction in ((0, 1), (-1, -1)):
        c, L, R = out[end_idx]
        cap_steps = []
        for k in range(1, n_taper + 1):
            t = k / (n_taper + 1)  # von Spitze (schmal) zu voller Breite
            Lk = (c[0] + (L[0] - c[0]) * t, c[1] + (L[1] - c[1]) * t)
            Rk = (c[0] + (R[0] - c[0]) * t, c[1] + (R[1] - c[1]) * t)
            cap_steps.append((c, Lk, Rk))
        if end_idx == 0:
            out = cap_steps + out
        else:
            out = out + list(reversed(cap_steps))
    return out


def _puff_perforation_underlay(cross) -> list[Pt]:
    """Spezielle 3D-Puff-Unterlage: Läuft mit kurzen, scharfen Perforationsstichen (1.2 mm)
    entlang beider Säulenkanten (L und R), um den Schaumstoff vor dem Satin-Deckstich anzuritzen."""
    left_rail = [L for _, L, _ in cross]
    right_rail = [R for _, _, R in reversed(cross)]
    return resample_path(left_rail + right_rail, 1.2)


def satin_runs(geom, spacing: float = 0.4, pull_comp: float = 0.15, max_stitch: float = 7.0,
               underlay: bool = True, start: Pt | None = None, puff_3d: bool = False,
               underlay_style: str = "auto") -> SatinResult:
    res = SatinResult()
    leftovers = []
    from .fill import _travel  # lokale Abhängigkeit vermeiden
    for poly in polygons_of(clean(geom, 0.05)):
        branches = skeleton_branches(poly)
        prepared_poly = prep(poly.buffer(0.05))
        rings = [poly.buffer(-0.2).exterior] if not poly.buffer(-0.2).is_empty and isinstance(poly.buffer(-0.2), Polygon) else [poly.exterior]
        covered_parts = []
        covered = None
        # längste Äste zuerst (Hauptstriche), winzige Nebenäste begrenzen
        branches.sort(key=lambda b: -len(b.pts))
        branches = branches[:18]
        segments = []
        for br in branches:
            cross_all = _rails_for_branch(poly, prepared_poly, br, spacing, pull_comp, covered)
            for cross in _split_runs(cross_all):
                quads = []
                for (c0, L0, R0), (c1, L1, R1) in zip(cross, cross[1:]):
                    q = Polygon([L0, R0, R1, L1])
                    if q.is_valid and q.area > 0:
                        quads.append(q)
                if not quads:
                    continue
                cov = unary_union(quads).buffer(0.05)
                covered_parts.append(cov)
                segments.append(cross)
            if covered_parts:
                covered = prep(unary_union(covered_parts).buffer(-0.25)) if covered_parts else None
                covered = _PreparedWrap(covered)
        # Reihenfolge: nächster Einstieg
        cur = start if not res.runs else res.runs[-1][-1]
        run: list[Pt] = []
        while segments:
            if cur is None:
                idx, rev = 0, False
            else:
                best = None
                for i, s in enumerate(segments):
                    for rv in (False, True):
                        e = s[-1][0] if rv else s[0][0]
                        d = dist(cur, e)
                        if best is None or d < best[0]:
                            best = (d, i, rv)
                _, idx, rev = best
            cross = segments.pop(idx)
            if rev:
                cross = list(reversed(cross))
            widths = [dist(L, R) for _, L, R in cross]
            wavg = sum(widths) / len(widths)
            seq: list[Pt] = []
            if puff_3d:
                cross = _pinch_end_caps(cross, n_taper=5)
                seq.extend(_puff_perforation_underlay(cross))
                seq.extend(_zigzag(cross, max_stitch=max(max_stitch, 10.0), short_stitch=False))
            else:
                if underlay and wavg > 1.2:
                    ul = _underlay(cross, wavg, spacing, underlay_style)
                    seq.extend(ul)
                    # Satin startet dort, wo die Unterlage endet
                    if dist(ul[-1], cross[0][0]) > dist(ul[-1], cross[-1][0]):
                        cross = list(reversed(cross))
                seq.extend(_zigzag(cross, max_stitch))
            if run:
                tr = _travel(poly, prepared_poly, rings, run[-1], seq[0], 2.5)
                if tr is None:
                    res.runs.append(run)
                    run = list(seq)
                else:
                    run.extend(tr)
                    run.extend(seq[1:] if tr else seq)
            else:
                run = list(seq)
            cur = run[-1]
        if run:
            res.runs.append(run)
        if covered_parts:
            left = poly.difference(unary_union(covered_parts).buffer(0.1))
            left = clean(left, 0.8)
            # nur nennenswerte Teile (keine Splitter)
            left = clean(left.buffer(-0.25).buffer(0.35), 0.8)
            if not left.is_empty:
                leftovers.append(left)
        else:
            leftovers.append(poly)
    res.leftover = unary_union(leftovers) if leftovers else None
    return res


class _PreparedWrap:
    def __init__(self, prepared):
        self.p = prepared

    def contains(self, pt):
        return self.p is not None and self.p.contains(pt)
