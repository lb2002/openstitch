"""Satinsäule entlang einer Mittellinie (wiederverwendbarer Säulen-Generator).

Wird von der Kleinschrift „OpenStitch Micro“ benutzt und ist als Grundlage für ein
manuelles Satinsäulen-Werkzeug gedacht: aus einer Mittellinie und einer (optional
variablen) Breite entsteht ein echter Satin-Zickzack mit

* Querschnitten im Abstand spacing/2 (Einstiche auf derselben Kante → exakt `spacing`,
  gleiche Konvention wie ``satin._zigzag``),
* geglätteter Stichrichtung (senkrecht zur lokalen Tangente),
* Kurzstichen auf der Innenseite enger Kurven,
* Eckbehandlung wie in kommerziellen Programmen: Gehrung (Mitre) mit weich drehenden
  Querschnitten bei mittleren Ecken, beschnittene Gehrung bei sehr spitzen Ecken
  (beide Schenkel werden senkrecht gestickt und an der Winkelhalbierenden abgeschnitten,
  Spitze auf MITRE_LIMIT gekappt) – nie hunderte Einstiche in ein Loch,
* Mittellauf-Unterlage (hin), Satin zurück,
* Rückfall auf Dreifachstich (Bean) bei sehr schmalen Säulen.

Koordinaten in mm, Y zeigt nach unten (Bildschirm-Konvention); die Geometrie selbst ist
orientierungsunabhängig.
"""
from __future__ import annotations

import math

from .geom import Pt, dist, resample_path
from .running import bean_stitch

CORNER_DEG = 40.0        # ab dieser Richtungsänderung gilt ein Stützpunkt als Ecke
                         # (Gehrung schon ab 40° – sauberer als reine Glättung)
MITRE_MAX_DEG = 130.0    # bis hierhin weiche Gehrung, darüber beschnittene Gehrung
MITRE_LIMIT = 1.45       # max. Gehrungslänge (× halbe Breite) auf der Aussenseite
MIN_SATIN_W = 0.7        # schmaler → Dreifachstich statt Satin
UNDERLAY_MIN_W = 1.0     # schmaler → keine Unterlage (würde nur auftragen)
FINE = 0.04              # Feinraster der Mittellinie (mm)
SAME_HOLE = 0.12         # Einstiche näher als das gelten als „selbes Loch“


# ---------------------------------------------------------------------------
# Öffentliche API
# ---------------------------------------------------------------------------
def column_runs(centerline: list[Pt], width: float | list[float], spacing: float = 0.4,
                pull_comp: float = 0.1, underlay: str = "center", start: Pt | None = None,
                max_stitch: float = 7.0, run_len: float = 1.0) -> list[list[Pt]]:
    """Satinsäule entlang `centerline` (Polylinie in mm).

    width      Säulenbreite (mm) – Zahl oder Liste je Stützpunkt der Mittellinie.
    spacing    Abstand zweier Einstiche auf derselben Kante (Dichte).
    pull_comp  Zugkompensation je Seite (mm).
    underlay   "center" (Mittellauf hin, Satin zurück) oder "none"; unter 1.0 mm Breite
               wird automatisch keine Unterlage genäht.
    start      Nadelposition davor – die Säule beginnt am näheren Ende (bei geschlossenen
               Linien am nächsten Stützpunkt).
    max_stitch längere Satinstiche werden geteilt (Split-Satin).
    run_len    Stichlänge des Dreifachstichs, falls die Säule schmaler als 0.7 mm ist.

    Liefert eine Liste zusammenhängender Läufe (normalerweise genau einen)."""
    pts, ws = _prepare(centerline, width)
    if len(pts) < 2:
        return []
    closed = len(pts) > 3 and dist(pts[0], pts[-1]) < 1e-6
    if start is not None:
        if closed:
            k = min(range(len(pts) - 1), key=lambda i: dist(pts[i], start))
            pts = pts[k:-1] + pts[:k + 1]
            ws = ws[k:-1] + ws[:k + 1]
        elif dist(start, pts[-1]) < dist(start, pts[0]):
            pts.reverse()
            ws.reverse()
    if max(ws) < MIN_SATIN_W:
        return [bean_run(pts, run_len, closed)]
    cross = _cross_sections(pts, ws, spacing, pull_comp, closed)
    if len(cross) < 2:
        return [bean_run(pts, run_len, closed)]
    wavg = sum(ws) / len(ws)
    if underlay == "center" and wavg >= UNDERLAY_MIN_W:
        hw0 = wavg / 2
        walk = _even(_trim_ends(pts, 0.0 if closed else min(0.4, hw0)), 1.6)
        zz = _zigzag(list(reversed(cross)), spacing, max_stitch)
        run = walk + zz
    else:
        run = _zigzag(cross, spacing, max_stitch)
    return [run] if len(run) >= 2 else []


def bean_run(pts: list[Pt], run_len: float = 1.0, closed: bool = False) -> list[Pt]:
    """Dreifachstich entlang einer Linie mit gleichmässigen Stichen (Ecken bleiben erhalten)."""
    ev = _even(pts, run_len)
    if len(ev) < 2:
        return ev
    # Stiche sind bereits ≤ run_len → bean_stitch unterteilt nicht erneut
    return bean_stitch(ev, stitch_len=run_len * 1.6, repeats=1)


# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------
def _prepare(centerline, width):
    pts = [(float(p[0]), float(p[1])) for p in centerline]
    if isinstance(width, (int, float)):
        ws = [float(width)] * len(pts)
    else:
        ws = [float(w) for w in width]
        if len(ws) != len(pts):
            raise ValueError("width-Liste muss so lang wie die Mittellinie sein")
    out_p, out_w = [], []
    for p, w in zip(pts, ws):
        if not (math.isfinite(p[0]) and math.isfinite(p[1])):
            continue
        if out_p and dist(out_p[-1], p) < 1e-6:
            continue
        out_p.append(p)
        out_w.append(max(0.0, w))
    # geschlossene Linie: Endpunkt exakt auf den Anfang legen
    if len(out_p) > 3 and dist(out_p[0], out_p[-1]) < 1e-4:
        out_p[-1] = out_p[0]
    return out_p, out_w


def _unit(dx, dy):
    L = math.hypot(dx, dy)
    if L < 1e-12:
        return (0.0, 0.0)
    return (dx / L, dy / L)


def _turn(a: Pt, b: Pt, c: Pt) -> float:
    """Vorzeichenbehaftete Richtungsänderung bei b (Grad, + = gegen den Uhrzeigersinn in x/y)."""
    u = _unit(b[0] - a[0], b[1] - a[1])
    v = _unit(c[0] - b[0], c[1] - b[1])
    cr = u[0] * v[1] - u[1] * v[0]
    dt = u[0] * v[0] + u[1] * v[1]
    return math.degrees(math.atan2(cr, dt))


def _cum(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + dist(a, b))
    return out


def _at(pts, cum, s):
    """Punkt bei Bogenlänge s (geklemmt)."""
    if s <= 0:
        return pts[0]
    if s >= cum[-1]:
        return pts[-1]
    lo, hi = 0, len(cum) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if cum[mid] <= s:
            lo = mid
        else:
            hi = mid
    seg = cum[hi] - cum[lo]
    t = 0.0 if seg < 1e-12 else (s - cum[lo]) / seg
    a, b = pts[lo], pts[hi]
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _interp_w(cum, ws, s):
    if s <= 0:
        return ws[0]
    if s >= cum[-1]:
        return ws[-1]
    for i in range(1, len(cum)):
        if cum[i] >= s:
            seg = cum[i] - cum[i - 1]
            t = 0.0 if seg < 1e-12 else (s - cum[i - 1]) / seg
            return ws[i - 1] + (ws[i] - ws[i - 1]) * t
    return ws[-1]


def _even(pts: list[Pt], step: float, corner_deg: float = 35.0) -> list[Pt]:
    """Gleichmässige Teilung je Abschnitt zwischen Ecken (ohne Mikrostiche an dichten Kurvenpunkten)."""
    if len(pts) < 2:
        return list(pts)
    parts, cur = [], [pts[0]]
    for i in range(1, len(pts) - 1):
        cur.append(pts[i])
        if abs(_turn(pts[i - 1], pts[i], pts[i + 1])) > corner_deg:
            parts.append(cur)
            cur = [pts[i]]
    cur.append(pts[-1])
    parts.append(cur)
    out = [pts[0]]
    for part in parts:
        cum = _cum(part)
        L = cum[-1]
        if L < 1e-9:
            continue
        n = max(1, int(math.ceil(L / step - 1e-9)))
        for k in range(1, n + 1):
            out.append(_at(part, cum, L * k / n))
    return out


def _trim_ends(pts, d):
    """Kürzt eine offene Linie an beiden Enden um d (für versteckte Unterlage)."""
    cum = _cum(pts)
    L = cum[-1]
    if d <= 0 or L <= 2.5 * d:
        return pts
    a, b = d, L - d
    out = [_at(pts, cum, a)]
    out += [p for p, s in zip(pts, cum) if a < s < b]
    out.append(_at(pts, cum, b))
    return out


# ---------------------------------------------------------------------------
# Querschnitte
# ---------------------------------------------------------------------------
class _Corner:
    """Ecke der Mittellinie. kind: "mitre" (weich drehende Querschnitte) oder "clip"
    (senkrechte Querschnitte, an der Winkelhalbierenden beschnitten)."""
    __slots__ = ("idx", "theta", "sign", "kind", "lam", "r", "u", "m", "hw", "K")

    def __init__(self, idx, theta, sign):
        self.idx, self.theta, self.sign = idx, theta, sign
        self.kind, self.lam, self.r, self.m, self.hw = "clip", 0.0, (0.0, 0.0), 1.0, 0.0
        self.u, self.K = (1.0, 0.0), (0.0, 0.0)


def _dir_near(pts, cum, s, d, forward):
    """Mittlere Richtung der Linie über eine kurze Strecke d ab Bogenlänge s."""
    if forward:
        a, b = _at(pts, cum, s), _at(pts, cum, s + d)
    else:
        a, b = _at(pts, cum, s - d), _at(pts, cum, s)
    return _unit(b[0] - a[0], b[1] - a[1])


def _cross_sections(pts, ws, spacing, pc, closed):
    """Liste von (Mitte, L, R) im Abstand spacing/2 entlang der ganzen Säule."""
    cum = _cum(pts)
    hws = [w / 2 + pc for w in ws]
    n = len(pts)
    # --- Ecken finden --------------------------------------------------------
    corners = []
    for i in range(1, n - 1):
        t = _turn(pts[i - 1], pts[i], pts[i + 1])
        if abs(t) > CORNER_DEG:
            corners.append(_Corner(i, abs(t), 1 if t > 0 else -1))
    if closed:
        t = _turn(pts[-2], pts[0], pts[1])
        if abs(t) > CORNER_DEG:
            corners.insert(0, _Corner(0, abs(t), 1 if t > 0 else -1))
    if closed and corners:
        # Naht auf die erste Ecke legen → wie offene Linie mit Ecke am Anfang/Ende
        k = corners[0].idx
        pts = pts[k:-1] + pts[:k + 1]
        hws = hws[k:-1] + hws[:k + 1]
        for c in corners:
            c.idx = (c.idx - k) % (n - 1)
        seam = corners[0]
        corners = corners[1:]
        cum = _cum(pts)
        bounds = [0] + [c.idx for c in corners] + [len(pts) - 1]
        joints = [seam] + corners + [seam]
    else:
        bounds = [0] + [c.idx for c in corners] + [n - 1]
        joints = [None] + corners + [None]
    loop_smooth = closed and not corners

    # --- Eckart bestimmen (weiche oder beschnittene Gehrung) --------------------
    seg_len = [cum[bounds[k + 1]] - cum[bounds[k]] for k in range(len(bounds) - 1)]
    for j, c in enumerate(joints):
        if c is None:
            continue
        k_in = j - 1 if j > 0 else len(seg_len) - 1    # Abschnitt vor der Ecke
        k_out = j if j < len(seg_len) else 0           # Abschnitt nach der Ecke
        s_k = cum[bounds[j]]
        hw = hws[bounds[j]]
        half = math.radians(c.theta) / 2
        s_off = hw * math.tan(half)
        lam = min(2.0 * s_off + 0.5 * hw, 0.5 * min(seg_len[k_in], seg_len[k_out]))
        c.hw = hw
        c.K = pts[bounds[j]]
        d = max(1e-3, min(hw, 0.5 * seg_len[k_in], 0.5 * seg_len[k_out]))
        if j == 0 or j == len(joints) - 1:   # Naht einer geschlossenen Linie
            ta = _dir_near(pts, cum, cum[-1], d, False)
            tb = _dir_near(pts, cum, 0.0, d, True)
        else:
            ta = _dir_near(pts, cum, s_k, d, False)
            tb = _dir_near(pts, cum, s_k, d, True)
        na = (-ta[1], ta[0])
        nb = (-tb[1], tb[0])
        # Winkelhalbierende der Normalen (Gehrungslinie) und Normale dazu (Richtung a→b)
        r = _unit(na[0] + nb[0], na[1] + nb[1])
        c.r = r if r != (0.0, 0.0) else ta          # Haarnadel: Achse = Laufrichtung
        u = _unit(ta[0] + tb[0], ta[1] + tb[1])
        c.u = u if u != (0.0, 0.0) else na
        c.m = 1.0 / max(math.cos(half), 1e-3)
        if c.theta <= MITRE_MAX_DEG and lam >= 1.3 * s_off + 0.05:
            c.kind = "mitre"
            c.lam = lam
        else:
            c.kind = "clip"

    # --- Abschnitte ------------------------------------------------------------
    out = []
    for k in range(len(bounds) - 1):
        i0, i1 = bounds[k], bounds[k + 1]
        piece = pts[i0:i1 + 1]
        phw = hws[i0:i1 + 1]
        cs = joints[k]          # Ecke am Anfang
        ce = joints[k + 1]      # Ecke am Ende
        cross = _piece_cross(piece, phw, spacing, cs, ce, loop_smooth)
        if not cross:
            continue
        if cs is not None and cs.kind == "mitre" and out and k > 0:
            cross = cross[1:]   # gemeinsamer Gehrungs-Querschnitt nur einmal
        out.extend(cross)
    return out


def _piece_cross(piece, phw, spacing, cs, ce, loop_smooth):
    cum = _cum(piece)
    Lp = cum[-1]
    if Lp < 1e-6:
        return []
    hwm = max(phw)
    win = min(0.8, max(0.2, 0.6 * hwm))
    # Feinraster der Mittellinie
    nfine = max(2, int(math.ceil(Lp / FINE)) + 1)
    ss = [Lp * j / (nfine - 1) for j in range(nfine)]
    C, Lr, Rr, T = [], [], [], []
    for s in ss:
        c = _at(piece, cum, s)
        if loop_smooth:
            a = _at(piece, cum, (s - win) % Lp)
            b = _at(piece, cum, (s + win) % Lp)
        else:
            a = _at(piece, cum, max(0.0, s - win))
            b = _at(piece, cum, min(Lp, s + win))
            # an Ecken nicht über die Ecke hinweg glätten: Richtung des eigenen Abschnitts
        t = _unit(b[0] - a[0], b[1] - a[1])
        if t == (0.0, 0.0):
            t = T[-1] if T else (1.0, 0.0)
        h = _interp_w(cum, phw, s)
        nx, ny = -t[1], t[0]
        C.append(c)
        T.append(t)
        Lr.append((c[0] + nx * h, c[1] + ny * h))
        Rr.append((c[0] - nx * h, c[1] - ny * h))

    # Beschnittene Gehrung: Säule geradlinig über die Ecke hinaus verlängern; die Querschnitte
    # werden danach an der Winkelhalbierenden (und der Spitzenkappung) abgeschnitten.
    if ce is not None and ce.kind == "clip":
        _extend(C, Lr, Rr, ss, T[-1], piece[-1], phw[-1], ce, at_end=True, Lp=Lp)
    if cs is not None and cs.kind == "clip":
        _extend(C, Lr, Rr, ss, T[0], piece[0], phw[0], cs, at_end=False, Lp=Lp)

    # Gehrung: Querschnitte drehen weich zur Winkelhalbierenden, Innenkante wird linear
    # auf den Gehrungspunkt geführt → keine Stichhäufung in der Ecke
    if ce is not None and ce.kind == "mitre":
        _blend(C, Lr, Rr, ss, ce, at_end=True, Lp=Lp)
    if cs is not None and cs.kind == "mitre":
        _blend(C, Lr, Rr, ss, cs, at_end=False, Lp=Lp)

    # Querschnitte nach Fortschritt der längeren Kante setzen (Aussenkante = spacing)
    prog = [0.0]
    for j in range(1, len(C)):
        prog.append(prog[-1] + max(dist(Lr[j - 1], Lr[j]), dist(Rr[j - 1], Rr[j]), 1e-9))
    M = prog[-1]
    step = spacing / 2.0
    N = max(1, int(round(M / step)))
    out = []
    j = 0
    last = N - 1 if loop_smooth else N
    for k in range(last + 1):
        m = M * k / N
        while j < len(prog) - 2 and prog[j + 1] < m:
            j += 1
        seg = prog[j + 1] - prog[j]
        t = 0.0 if seg < 1e-12 else min(1.0, max(0.0, (m - prog[j]) / seg))

        def lerp(A, B):
            return (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t)
        out.append((lerp(C[j], C[j + 1]), lerp(Lr[j], Lr[j + 1]), lerp(Rr[j], Rr[j + 1])))
    if ce is not None and ce.kind == "clip":
        out = _clip(out, ce, keep_before=True)
    if cs is not None and cs.kind == "clip":
        out = _clip(out, cs, keep_before=False)
    return out


def _extend(C, Lr, Rr, ss, t, P, h, corner, at_end, Lp):
    """Verlängert die Feinpunkte geradlinig über die Ecke hinaus (bzw. vor den Anfang)."""
    ext = corner.hw * min(4.0, math.tan(math.radians(corner.theta) / 2)) + 0.1
    nx, ny = -t[1], t[0]
    steps = max(1, int(math.ceil(ext / FINE)))
    sg = 1.0 if at_end else -1.0
    add = []
    for j in range(1, steps + 1):
        e = ext * j / steps
        c = (P[0] + sg * t[0] * e, P[1] + sg * t[1] * e)
        add.append((c, (c[0] + nx * h, c[1] + ny * h), (c[0] - nx * h, c[1] - ny * h),
                    Lp + e if at_end else -e))
    if not at_end:
        add.reverse()
    cs_, ls_, rs_, ss_ = (list(v) for v in zip(*add))
    if at_end:
        C.extend(cs_)
        Lr.extend(ls_)
        Rr.extend(rs_)
        ss.extend(ss_)
    else:
        C[:0] = cs_
        Lr[:0] = ls_
        Rr[:0] = rs_
        ss[:0] = ss_


def _clip(cross, corner, keep_before: bool):
    """Querschnitte auf die eigene Seite der Winkelhalbierenden beschneiden und die
    Aussenspitze auf MITRE_LIMIT × halbe Breite kappen. Zu kurze Reste entfallen."""
    K, (ux, uy), (rx, ry) = corner.K, corner.u, corner.r
    ox, oy = -corner.sign * rx, -corner.sign * ry      # Aussenrichtung der Ecke
    lim = corner.hw * MITRE_LIMIT
    min_len = max(0.3, 0.35 * corner.hw)
    planes = ((ux, uy, 0.0, 1.0 if keep_before else -1.0), (ox, oy, lim, 1.0))
    # nur lokal an der Ecke beschneiden (Halbebenen sind unendlich – ein Bogen, der später
    # wieder nahe an die Ecke kommt, darf nicht mitbeschnitten werden)
    reach = corner.hw * (min(4.0, math.tan(math.radians(corner.theta) / 2)) + 2.0) + 0.2
    seq = list(reversed(cross)) if keep_before else list(cross)
    n_local = 0
    for c, _, _ in seq:
        if dist(c, K) > reach:
            break
        n_local += 1
    rest = seq[n_local:]
    out = []
    for c, L, R in seq[:n_local]:
        lo, hi = 0.0, 1.0
        ok = True
        for ax, ay, bound, sgn in planes:
            # Bedingung: sgn · (p − K)·a ≤ bound für p = L + t (R − L)
            f0 = sgn * ((L[0] - K[0]) * ax + (L[1] - K[1]) * ay) - bound
            f1 = sgn * ((R[0] - K[0]) * ax + (R[1] - K[1]) * ay) - bound
            if f0 <= 0 and f1 <= 0:
                continue
            if f0 > 0 and f1 > 0:
                ok = False
                break
            tz = f0 / (f0 - f1)
            if f0 > 0:
                lo = max(lo, tz)
            else:
                hi = min(hi, tz)
        if not ok or hi - lo <= 1e-9:
            continue
        L2 = (L[0] + (R[0] - L[0]) * lo, L[1] + (R[1] - L[1]) * lo)
        R2 = (L[0] + (R[0] - L[0]) * hi, L[1] + (R[1] - L[1]) * hi)
        if dist(L2, R2) < min_len:
            continue
        out.append(((0.5 * (L2[0] + R2[0]), 0.5 * (L2[1] + R2[1])), L2, R2))
    out += rest
    return list(reversed(out)) if keep_before else out


def _blend(C, Lr, Rr, ss, corner, at_end, Lp):
    lam = corner.lam
    K = C[-1] if at_end else C[0]
    h = corner.hw
    rx, ry = corner.r
    inner = h * corner.m
    outer = h * min(corner.m, MITRE_LIMIT)
    # r zeigt in Richtung der Normalen (+n = L-Seite); Innenseite = Seite der Drehung
    if corner.sign > 0:
        L_end = (K[0] + rx * inner, K[1] + ry * inner)
        R_end = (K[0] - rx * outer, K[1] - ry * outer)
    else:
        L_end = (K[0] + rx * outer, K[1] + ry * outer)
        R_end = (K[0] - rx * inner, K[1] - ry * inner)
    if at_end:
        idx = [j for j, s in enumerate(ss) if s >= Lp - lam]
        if not idx:
            return
        j0 = max(0, idx[0] - 1)
        L0, R0, s0 = Lr[j0], Rr[j0], ss[j0]
        span = max(Lp - s0, 1e-9)
        for j in idx:
            u = min(1.0, (ss[j] - s0) / span)
            Lr[j] = (L0[0] + (L_end[0] - L0[0]) * u, L0[1] + (L_end[1] - L0[1]) * u)
            Rr[j] = (R0[0] + (R_end[0] - R0[0]) * u, R0[1] + (R_end[1] - R0[1]) * u)
    else:
        idx = [j for j, s in enumerate(ss) if s <= lam]
        if not idx:
            return
        j1 = min(len(ss) - 1, idx[-1] + 1)
        L1, R1, s1 = Lr[j1], Rr[j1], ss[j1]
        span = max(s1, 1e-9)
        for j in idx:
            u = min(1.0, (s1 - ss[j]) / span)
            Lr[j] = (L1[0] + (L_end[0] - L1[0]) * u, L1[1] + (L_end[1] - L1[1]) * u)
            Rr[j] = (R1[0] + (R_end[0] - R1[0]) * u, R1[1] + (R_end[1] - R1[1]) * u)


# ---------------------------------------------------------------------------
# Zickzack mit Kurzstichen
# ---------------------------------------------------------------------------
def _zigzag(cross, spacing: float, max_stitch: float) -> list[Pt]:
    """Wechselt je Querschnitt die Seite L ↔ R. Ist der Abstand zum letzten vollen Einstich
    derselben Kante kleiner als spacing/2 (Innenseite enger Kurven/Ecken), wird der Einstich
    Richtung Mitte gezogen (Kurzstich). Einstiche ins selbe Loch werden ausgelassen."""
    pts: list[Pt] = []
    last_full: list[Pt | None] = [None, None]
    last_any: list[Pt | None] = [None, None]
    for i, (c, L, R) in enumerate(cross):
        side = i % 2
        tgt, opp = (L, R) if side == 0 else (R, L)
        lf = last_full[side]
        if lf is not None and dist(lf, tgt) < 0.5 * spacing:
            tgt = (tgt[0] + (opp[0] - tgt[0]) * 0.45, tgt[1] + (opp[1] - tgt[1]) * 0.45)
        else:
            last_full[side] = tgt
        la = last_any[side]
        if la is not None and dist(la, tgt) < SAME_HOLE:
            continue
        last_any[side] = tgt
        if pts:
            prev = pts[-1]
            w = dist(prev, tgt)
            if w > max_stitch:
                nseg = int(math.ceil(w / max_stitch))
                shift = 0.35 if (i % 2) else -0.35
                for k in range(1, nseg):
                    t = max(0.15, min(0.85, (k + shift * 0.5) / nseg))
                    pts.append((prev[0] + (tgt[0] - prev[0]) * t, prev[1] + (tgt[1] - prev[1]) * t))
        pts.append(tgt)
    return pts
