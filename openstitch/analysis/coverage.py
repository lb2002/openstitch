"""Rastert Stiche und vergleicht sie mit den Objektformen: Deckt der Faden die Fläche?"""
from __future__ import annotations

import cv2
import numpy as np

from ..core.design import Design
from ..engine.geom import polygons_of
from .stitches import Trace

PX_PER_MM = 12.0
THREAD_W = 0.38


def _to_px(pts, x0, y0) -> np.ndarray:
    return np.round((np.asarray(pts, float)[:, :2] - (x0, y0)) * PX_PER_MM * 16).astype(np.int32)


def thread_mask(seg: np.ndarray, x0, y0, w, h) -> np.ndarray:
    img = np.zeros((h, w), np.uint8)
    t = max(1, int(round(THREAD_W * PX_PER_MM)))
    a, b = _to_px(seg[:, :2], x0, y0), _to_px(seg[:, 2:], x0, y0)
    for p, q in zip(a.tolist(), b.tolist()):
        cv2.line(img, p, q, 255, t, cv2.LINE_8, 4)
    return img


def polygon_mask(geom, x0, y0, w, h) -> np.ndarray:
    img = np.zeros((h, w), np.uint8)
    for poly in polygons_of(geom):
        rings = [_to_px(poly.exterior.coords, x0, y0)] + [_to_px(r.coords, x0, y0) for r in poly.interiors]
        cv2.fillPoly(img, rings, 255, cv2.LINE_8, 4)
    return img


def check_coverage(design: Design, t: Trace) -> tuple[list[dict], dict]:
    """Deckung je Füll-/Satinobjekt. Die Form wird mit allem verglichen, was darauf liegt."""
    seg, _ = t.sewn_segments()
    out: list[dict] = []
    per_obj: dict[int, float] = {}
    objs = [o for o in design.objects if o.visible and o.kind in ("fill", "satin")]
    if len(seg) == 0 or not objs:
        return out, per_obj
    x0, y0 = seg[:, [0, 2]].min() - 2, seg[:, [1, 3]].min() - 2
    w = int((seg[:, [0, 2]].max() + 2 - x0) * PX_PER_MM) + 1
    h = int((seg[:, [1, 3]].max() + 2 - y0) * PX_PER_MM) + 1
    if w * h > 40_000_000:
        return out, per_obj
    mask = thread_mask(seg, x0, y0, w, h) > 0
    for o in objs:
        g = o.world_geom()
        if g is None or g.is_empty:
            continue
        # Kantenbereich ausklammern: dort dürfen einzelne Pixel fehlen, das sieht man nicht
        core = g.buffer(-0.35)
        if core.is_empty or core.area < 1.0:
            continue
        pm = polygon_mask(core, x0, y0, w, h) > 0
        area = int(np.count_nonzero(pm))
        if area == 0:
            continue
        cov = int(np.count_nonzero(mask & pm)) / area
        per_obj[o.id] = cov
        # Gewollt lockere Füllungen (grosser Reihenabstand) nicht bemängeln
        expected = min(0.97, THREAD_W / max(getattr(o, "spacing", 0.4), 1e-3) * 0.97)
        if cov < expected - 0.12:
            cx, cy = g.representative_point().coords[0]
            out.append({"code": "low_coverage", "severity": "warning", "object": o.name or o.kind,
                        "percent": cov * 100.0, "count": 1, "where": [(cx, cy)]})
    return out, per_obj
