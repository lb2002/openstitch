"""Maschinen- und Nadelregeln: alles, was sich direkt aus den Stichen ablesen lässt."""
from __future__ import annotations

import numpy as np

from ..core.stitchplan import Cmd
from .stitches import Trace, layers_map

THREAD_W = 0.27          # mm, wirksame Breite von Stickgarn No. 40 (flach aufliegend)
SHORT_STITCH = 0.30      # darunter trifft die Nadel praktisch dasselbe Loch
FLOAT_WARN = 7.5         # längere Stiche bleiben leicht hängen und liegen lose auf
PILEUP_CELL = 0.25       # mm
PILEUP_LIMIT = 7         # Einstiche in einer Zelle: darüber wird der Stoff perforiert
MIN_RUN = 3              # kürzere Läufe halten nach dem Schnitt nicht


def _spots(xy: np.ndarray, limit: int = 12) -> list[tuple[float, float]]:
    """Wenige repräsentative Positionen (Fehler liegen oft gehäuft dicht beieinander)."""
    out: list[tuple[float, float]] = []
    for x, y in xy:
        if all(abs(x - a) + abs(y - b) > 3.0 for a, b in out):
            out.append((float(x), float(y)))
            if len(out) >= limit:
                break
    return out


def check_stitch_lengths(t: Trace, max_stitch: float) -> list[dict]:
    seg, _ = t.sewn_segments()
    if len(seg) == 0:
        return []
    length = np.hypot(seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1])
    out: list[dict] = []
    short = (length < SHORT_STITCH) & (length > 0.0)
    if short.any():
        out.append({"code": "short_stitch", "severity": "warning" if short.mean() > 0.002 else "info",
                    "count": int(short.sum()), "share": float(short.mean()),
                    "where": _spots(seg[short, 2:4])})
    too_long = length > max_stitch + 0.05
    if too_long.any():
        out.append({"code": "over_max_stitch", "severity": "error", "count": int(too_long.sum()),
                    "max_mm": float(length.max()), "where": _spots(seg[too_long, 2:4])})
    floats = (length > FLOAT_WARN) & ~too_long
    if floats.any():
        out.append({"code": "long_float", "severity": "warning", "count": int(floats.sum()),
                    "max_mm": float(length[floats].max()), "where": _spots(seg[floats, 2:4])})
    return out


def _has_lock(x: np.ndarray, y: np.ndarray) -> bool:
    """Vernähung: die ersten Stiche laufen auf engem Raum vor und zurück."""
    if len(x) < 4:
        return False
    if max(np.ptp(x[:4]), np.ptp(y[:4])) < 1.5:
        return True
    # Rückkehr nahe an den Anfang wirkt auch mit grösserem Stich wie ein Knoten
    return bool(np.hypot(x[2:4] - x[0], y[2:4] - y[0]).min() < 0.35)


def check_runs(t: Trace) -> list[dict]:
    out: list[dict] = []
    loose, orphans = [], []
    for r in t.runs():
        x, y = t.x[r], t.y[r]
        if len(r) - 1 < MIN_RUN:
            orphans.append((x[0], y[0]))
            continue
        if not _has_lock(x, y):
            loose.append((x[0], y[0]))
        if not _has_lock(x[::-1], y[::-1]):
            loose.append((x[-1], y[-1]))
    if loose:
        out.append({"code": "no_lock", "severity": "warning", "count": len(loose),
                    "where": _spots(np.array(loose))})
    if orphans:
        out.append({"code": "orphan_run", "severity": "warning", "count": len(orphans),
                    "where": _spots(np.array(orphans))})
    # Sprünge ohne Schnitt legen einen Faden quer über das Motiv
    untrimmed = []
    for i in np.nonzero(t.cmd == Cmd.JUMP)[0]:
        p = i - 1
        if p >= 0 and t.cmd[p] == Cmd.STITCH and t.block[p] == t.block[i]:
            if float(np.hypot(t.x[i] - t.x[p], t.y[i] - t.y[p])) > 2.0:
                untrimmed.append((t.x[i], t.y[i]))
    if untrimmed:
        out.append({"code": "untrimmed_jump", "severity": "warning", "count": len(untrimmed),
                    "where": _spots(np.array(untrimmed))})
    return out


def check_needle_pileup(t: Trace) -> list[dict]:
    m = t.cmd == Cmd.STITCH
    if not m.any():
        return []
    ix = np.floor(t.x[m] / PILEUP_CELL).astype(np.int64)
    iy = np.floor(t.y[m] / PILEUP_CELL).astype(np.int64)
    uniq, inv, cnt = np.unique(ix * 1_000_003 + iy, return_inverse=True, return_counts=True)
    hot = cnt > PILEUP_LIMIT
    if not hot.any():
        return []
    mask = hot[inv]
    return [{"code": "needle_pileup", "severity": "warning", "count": int(hot.sum()), "max_hits": int(cnt.max()),
             "where": _spots(np.column_stack((t.x[m][mask], t.y[m][mask])))}]


def check_density(t: Trace, max_layers: float) -> tuple[list[dict], float]:
    seg, _ = t.sewn_segments()
    if len(seg) == 0:
        return [], 0.0
    cell = 1.0
    x0, y0 = seg[:, [0, 2]].min() - 1, seg[:, [1, 3]].min() - 1
    w = int(np.ceil((seg[:, [0, 2]].max() - x0) / cell)) + 2
    h = int(np.ceil((seg[:, [1, 3]].max() - y0) / cell)) + 2
    grid = layers_map(seg, x0, y0, w, h, cell, THREAD_W)
    peak = float(grid.max())
    over = grid > max_layers
    if not over.any():
        return [], peak
    ys, xs = np.nonzero(over)
    pts = np.column_stack((x0 + (xs + 0.5) * cell, y0 + (ys + 0.5) * cell))
    sev = "error" if peak > max_layers * 1.6 else "warning"
    return [{"code": "too_dense", "severity": sev, "count": int(over.sum()), "peak": peak,
             "limit": max_layers, "where": _spots(pts)}], peak
