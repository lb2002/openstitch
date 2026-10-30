"""Lesbarkeit kleiner Schrift, ohne OCR-Abhängigkeit.

Jeder Buchstabe wird gestickt, mit Fadenbreite gerastert und unscharf gezeichnet (so sieht man ihn
aus Leseabstand). Lesbar ist er, wenn er sich von allen anderen Buchstaben klar unterscheidet und
Innenräume offen bleiben. Das Mass ist die Korrelation zum ähnlichsten anderen Buchstaben."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from ..core.design import Design
from ..core.stitchplan import Cmd, Thread
from ..text import TextObject

PX_PER_MM = 16
THREAD_W = 0.38


def _render(chars: str, height: float, font: str) -> np.ndarray | None:
    obj = TextObject(Thread((0, 0, 0)), text=chars, height=height, font=font)
    d = Design(objects=[obj])
    plan = d.build_plan()
    pts_runs: list[list[tuple[float, float]]] = []
    for b in plan.blocks:
        cur: list[tuple[float, float]] = []
        for s in b.stitches:
            if s.cmd == Cmd.STITCH:
                cur.append((s.x, s.y))
            elif s.cmd == Cmd.JUMP:
                if len(cur) > 1:
                    pts_runs.append(cur)
                cur = [(s.x, s.y)]
            elif s.cmd == Cmd.TRIM:
                if len(cur) > 1:
                    pts_runs.append(cur)
                cur = []
        if len(cur) > 1:
            pts_runs.append(cur)
    if not pts_runs:
        return None
    all_pts = np.array([p for r in pts_runs for p in r])
    x0, y0 = all_pts.min(axis=0)
    x1, y1 = all_pts.max(axis=0)
    # Einheitliche Leinwand, damit Buchstaben unterschiedlicher Breite vergleichbar bleiben
    w = int(max(x1 - x0, height) * PX_PER_MM) + 2 * PX_PER_MM
    h = int(max(y1 - y0, height) * PX_PER_MM) + 2 * PX_PER_MM
    img = np.zeros((h, w), np.uint8)
    t = max(1, int(round(THREAD_W * PX_PER_MM)))
    for r in pts_runs:
        arr = np.round((np.array(r) - (x0 - 1, y0 - 1)) * PX_PER_MM).astype(np.int32)
        cv2.polylines(img, [arr.reshape(-1, 1, 2)], False, 255, t, cv2.LINE_AA)
    return img


def _norm(img: np.ndarray, size: int = 64) -> np.ndarray:
    # Aus Leseabstand verschwimmt alles unter etwa einer Fadenbreite
    blur = cv2.GaussianBlur(img, (0, 0), THREAD_W * PX_PER_MM * 0.6)
    a = cv2.resize(blur, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32).ravel()
    a -= a.mean()
    return a / (np.linalg.norm(a) + 1e-6)


@dataclass
class Legibility:
    height: float
    font: str
    worst_pairs: list[tuple[str, str, float]]
    mean_nearest: float
    blocked_counters: list[str]


def _blocked(img: np.ndarray) -> bool:
    """Geschlossene Innenräume (a, e, o …) laufen zu, wenn sie kleiner als ~2 Fadenbreiten werden."""
    contours, hier = cv2.findContours((img > 127).astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hier is None:
        return False
    holes = [cv2.contourArea(c) for c, h in zip(contours, hier[0]) if h[3] >= 0]
    return bool(holes) and max(holes) < (0.5 * PX_PER_MM) ** 2


def measure(chars: str, height: float, font: str) -> Legibility:
    imgs = {c: _render(c, height, font) for c in chars}
    imgs = {c: i for c, i in imgs.items() if i is not None}
    keys = list(imgs)
    vecs = np.stack([_norm(imgs[c]) for c in keys])
    sim = vecs @ vecs.T
    np.fill_diagonal(sim, -1)
    nearest = sim.max(axis=1)
    order = np.dstack(np.unravel_index(np.argsort(-sim, axis=None), sim.shape))[0]
    worst: list[tuple[str, str, float]] = []
    for i, j in order:
        if i < j:
            worst.append((keys[i], keys[j], float(sim[i, j])))
        if len(worst) >= 8:
            break
    # Innenräume: nur Zeichen, die im Original einen haben
    probes = [c for c in "abdegopqABDOPQR04689" if c in imgs]
    blocked = [c for c in probes if _blocked(imgs[c])]
    return Legibility(height, font, worst, float(nearest.mean()), blocked)
