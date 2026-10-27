"""Steppstich, Dreifachstich (Bean) und Motivstich entlang von Pfaden."""
from __future__ import annotations

from .geom import Pt, resample_path


def running_stitch(coords: list[Pt], stitch_len: float = 2.5, closed: bool = False) -> list[Pt]:
    return resample_path(coords, stitch_len, closed=closed)


def bean_stitch(coords: list[Pt], stitch_len: float = 2.5, repeats: int = 1,
                closed: bool = False) -> list[Pt]:
    """Dreifachstich: jeder Stich wird vor-zurück-vor genäht (repeats=1 → 3-fach)."""
    pts = running_stitch(coords, stitch_len, closed)
    if repeats <= 0 or len(pts) < 2:
        return pts
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        out.append(b)
        for _ in range(repeats):
            out.append(a)
            out.append(b)
    return out


def tie_stitches(p: Pt, toward: Pt | None, length: float = 0.6) -> list[Pt]:
    """Vernähstiche (Lock) – kleine Hin-und-her-Stiche, damit sich der Faden nicht löst."""
    if toward is None:
        return [p, (p[0] + length, p[1]), p, (p[0] + length, p[1]), p]
    dx, dy = toward[0] - p[0], toward[1] - p[1]
    d = max((dx * dx + dy * dy) ** 0.5, 1e-9)
    ux, uy = dx / d * length, dy / d * length
    q = (p[0] + ux, p[1] + uy)
    return [p, q, p, q, p]
