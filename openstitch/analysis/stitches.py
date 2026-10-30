"""Stichplan als Numpy-Arrays für die Analysen."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..core.stitchplan import Cmd, StitchPlan


@dataclass
class Trace:
    x: np.ndarray
    y: np.ndarray
    cmd: np.ndarray
    block: np.ndarray

    @staticmethod
    def of(plan: StitchPlan) -> "Trace":
        xs, ys, cs, bs = [], [], [], []
        for bi, b in enumerate(plan.blocks):
            for s in b.stitches:
                xs.append(s.x)
                ys.append(s.y)
                cs.append(int(s.cmd))
                bs.append(bi)
        return Trace(np.array(xs, float), np.array(ys, float), np.array(cs, int), np.array(bs, int))

    def sewn_segments(self) -> tuple[np.ndarray, np.ndarray]:
        """(N×4-Array x0,y0,x1,y1; Block je Segment): alle Stiche, die Faden auf den Stoff legen."""
        idx = np.nonzero(self.cmd == Cmd.STITCH)[0]
        idx = idx[idx > 0]
        prev = idx - 1
        # Nur Stiche, deren Vorgänger eine Nadelposition ist (STITCH oder JUMP), und im selben Block
        keep = np.isin(self.cmd[prev], (Cmd.STITCH, Cmd.JUMP)) & (self.block[prev] == self.block[idx])
        i, p = idx[keep], prev[keep]
        seg = np.column_stack((self.x[p], self.y[p], self.x[i], self.y[i]))
        return seg, self.block[i]

    def runs(self) -> list[np.ndarray]:
        """Zusammenhängende Nähläufe als Index-Arrays (Ende an Trim, Sprung oder Blockwechsel)."""
        out: list[list[int]] = []
        cur: list[int] = []
        last_block = None
        for i, (c, b) in enumerate(zip(self.cmd, self.block)):
            if b != last_block:
                if cur:
                    out.append(cur)
                cur = []
                last_block = b
            if c == Cmd.STITCH:
                cur.append(i)
            elif c == Cmd.JUMP:
                if cur:
                    out.append(cur)
                cur = [i]
            elif c == Cmd.TRIM:
                if cur:
                    out.append(cur)
                cur = []
        if cur:
            out.append(cur)
        return [np.array(r) for r in out if len(r) >= 2]


def layers_map(seg: np.ndarray, x0: float, y0: float, w: int, h: int, cell: float,
               thread_w: float) -> np.ndarray:
    """Fadenlagen je Zelle: abgelegte Fadenfläche / Zellenfläche (1.0 = Stoff gerade bedeckt)."""
    out = np.zeros((h, w), float)
    if len(seg) == 0:
        return out
    dx, dy = seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1]
    length = np.hypot(dx, dy)
    n = np.maximum(np.ceil(length / (cell * 0.5)).astype(int), 1)
    rep = np.repeat(np.arange(len(seg)), n)
    # Abtastpunkte je Segment gleichmässig verteilt
    k = np.concatenate([(np.arange(m) + 0.5) / m for m in n])
    px = seg[rep, 0] + dx[rep] * k
    py = seg[rep, 1] + dy[rep] * k
    ix = np.clip(((px - x0) / cell).astype(int), 0, w - 1)
    iy = np.clip(((py - y0) / cell).astype(int), 0, h - 1)
    np.add.at(out, (iy, ix), (length / n)[rep])
    return out * thread_w / (cell * cell)
