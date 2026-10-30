"""Stoffverzug als Federgitter.

Jeder Einstich wird vom Faden zu seinen beiden Nachbar-Einstichen gezogen. Bei geraden Steppstichen
heben sich die Kräfte auf, bei Satin und Tatami ziehen sie die Kanten nach innen: genau der Effekt,
den die Zugkompensation ausgleicht. Das Gitter wird Abschnitt für Abschnitt belastet; bereits
gestickte Flächen versteifen den Stoff. Was zuerst gestickt wurde, wandert mit dem Stoff mit, wenn
später daneben gestickt wird. Daraus entstehen die Lücken zwischen Füllung und Kontur.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu

from ..core.stitchplan import Cmd
from .fabric import Fabric
from .stitches import Trace, layers_map

# Kalibriert: 4 mm Satin ohne Kompensation auf gewebter Baumwolle zieht sich um ~0.3 mm zusammen
TENSION = 0.055
THREAD_W = 0.27
MARGIN = 12.0
STIFFEN = 1.6            # je Fadenlage steigt die lokale Steifigkeit um diesen Faktor
MAX_NODES = 14_000
MAX_CHUNKS = 8


@dataclass
class PullResult:
    x0: float
    y0: float
    h: float
    dx: np.ndarray               # Abweichung je Einstich von der gewollten Position
    dy: np.ndarray
    idx: np.ndarray              # Index der Einstiche im Trace
    chunk: np.ndarray            # Abschnitt je Einstich
    max_shift: float
    p95_shift: float
    misregistration: float       # grösster Versatz zwischen Objekten am selben Ort
    gaps: list[tuple[float, float]]


def _forces(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fadenzug je Einstich (Summe der Einheitsvektoren zu den Nachbar-Einstichen)."""
    dx, dy = np.diff(x), np.diff(y)
    length = np.hypot(dx, dy)
    ok = length > 1e-6
    ux, uy = np.zeros_like(dx), np.zeros_like(dy)
    ux[ok], uy[ok] = dx[ok] / length[ok], dy[ok] / length[ok]
    fx, fy = np.zeros_like(x), np.zeros_like(y)
    fx[:-1] += ux
    fy[:-1] += uy
    fx[1:] -= ux
    fy[1:] -= uy
    return fx, fy


class _Grid:
    def __init__(self, x0, y0, nx, ny, h):
        self.x0, self.y0, self.nx, self.ny, self.h = x0, y0, nx, ny, h

    def _weights(self, x, y):
        gx = np.clip((x - self.x0) / self.h, 0, self.nx - 1.001)
        gy = np.clip((y - self.y0) / self.h, 0, self.ny - 1.001)
        ix, iy = gx.astype(int), gy.astype(int)
        return ix, iy, gx - ix, gy - iy

    def sample(self, u, x, y):
        ix, iy, fx, fy = self._weights(x, y)
        a = u[iy, ix] * ((1 - fx) * (1 - fy))[..., None] + u[iy, ix + 1] * (fx * (1 - fy))[..., None]
        b = u[iy + 1, ix] * ((1 - fx) * fy)[..., None] + u[iy + 1, ix + 1] * (fx * fy)[..., None]
        return a + b

    def spread(self, x, y, fx_, fy_):
        f = np.zeros((self.ny, self.nx, 2))
        ix, iy, fx, fy = self._weights(x, y)
        for dix, diy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)),
                            (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
            np.add.at(f[..., 0], (iy + diy, ix + dix), fx_ * w)
            np.add.at(f[..., 1], (iy + diy, ix + dix), fy_ * w)
        return f


def _stiffness_matrix(grid: _Grid, s: np.ndarray):
    """Federgitter (Kanten + Diagonalen), Randknoten fest (eingespannter Stoff)."""
    nx, ny = grid.nx, grid.ny
    nid = np.arange(nx * ny).reshape(ny, nx)
    rows, cols, vals = [], [], []

    def add(a, b, k, ex, ey):
        # Feder zwischen a und b: k·(e eᵀ) auf die Freiheitsgrade 2·i, 2·i+1
        e = ((ex * ex, ex * ey), (ex * ey, ey * ey))
        for i in range(2):
            for j in range(2):
                w = k * e[i][j]
                ia, ib, ja, jb = 2 * a + i, 2 * b + i, 2 * a + j, 2 * b + j
                rows.extend((ia, ib, ia, ib))
                cols.extend((ja, jb, jb, ja))
                vals.extend((w, w, -w, -w))

    add(nid[:, :-1].ravel(), nid[:, 1:].ravel(), (0.5 * (s[:, :-1] + s[:, 1:])).ravel(), 1.0, 0.0)
    add(nid[:-1, :].ravel(), nid[1:, :].ravel(), (0.5 * (s[:-1, :] + s[1:, :])).ravel(), 0.0, 1.0)
    r = 0.7071
    add(nid[:-1, :-1].ravel(), nid[1:, 1:].ravel(), (0.25 * (s[:-1, :-1] + s[1:, 1:])).ravel(), r, r)
    add(nid[:-1, 1:].ravel(), nid[1:, :-1].ravel(), (0.25 * (s[:-1, 1:] + s[1:, :-1])).ravel(), r, -r)
    n = 2 * nx * ny
    K = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsc()
    free = np.ones(n, bool)
    edge = np.zeros((ny, nx), bool)
    edge[0, :] = edge[-1, :] = True
    edge[:, 0] = edge[:, -1] = True
    fixed = nid[edge]
    free[2 * fixed] = False
    free[2 * fixed + 1] = False
    return K[free][:, free], free


def _chunks(t: Trace, idx: np.ndarray) -> np.ndarray:
    """Teilt die Einstiche in Abschnitte (Farbblöcke; grosse Blöcke zusätzlich der Länge nach)."""
    n = len(idx)
    chunk = np.zeros(n, int)
    size = max(n // MAX_CHUNKS, 1)
    cur = start = 0
    for i in range(1, n):
        if t.block[idx[i]] != t.block[idx[i - 1]] or i - start >= size:
            cur += 1
            start = i
        chunk[i] = cur
    return chunk


def simulate_pull(t: Trace, fabric: Fabric) -> PullResult | None:
    idx = np.nonzero(t.cmd == Cmd.STITCH)[0]
    if len(idx) < 8:
        return None
    x, y = t.x[idx], t.y[idx]
    bx0, by0, bx1, by1 = x.min(), y.min(), x.max(), y.max()
    w, h = bx1 - bx0 + 2 * MARGIN, by1 - by0 + 2 * MARGIN
    cell = max(1.0, float(np.sqrt(w * h / MAX_NODES)))
    nx, ny = int(w / cell) + 2, int(h / cell) + 2
    grid = _Grid(bx0 - MARGIN, by0 - MARGIN, nx, ny, cell)

    stiff = np.full((ny, nx), float(fabric.stiffness))
    chunk = _chunks(t, idx)
    u = np.zeros((ny, nx, 2))
    mat_x, mat_y = np.zeros_like(x), np.zeros_like(y)

    for c in range(int(chunk.max()) + 1):
        m = chunk == c
        cx, cy = x[m], y[m]
        # Die Nadel trifft Rahmenkoordinaten; der Stoffpunkt darunter ist bereits verschoben
        offs = grid.sample(u, cx, cy)
        mat_x[m], mat_y[m] = cx - offs[:, 0], cy - offs[:, 1]

        K, free = _stiffness_matrix(grid, stiff)
        fx, fy = _forces(cx, cy)
        f = grid.spread(cx, cy, fx * TENSION, fy * TENSION)
        b = np.empty(2 * nx * ny)
        b[0::2], b[1::2] = f[..., 0].ravel(), f[..., 1].ravel()
        du = np.zeros(2 * nx * ny)
        du[free] = splu(K, permc_spec="MMD_AT_PLUS_A", options={"SymmetricMode": True}).solve(b[free])
        u[..., 0] += du[0::2].reshape(ny, nx)
        u[..., 1] += du[1::2].reshape(ny, nx)

        # Bestickte Fläche versteift den Stoff für alles Folgende
        seg = np.column_stack((cx[:-1], cy[:-1], cx[1:], cy[1:]))
        lay = layers_map(seg, grid.x0, grid.y0, nx, ny, cell, THREAD_W)
        stiff += fabric.stiffness * STIFFEN * np.minimum(lay, 3.0)

    final = grid.sample(u, mat_x, mat_y)
    dx, dy = mat_x + final[:, 0] - x, mat_y + final[:, 1] - y
    shift = np.hypot(dx, dy)
    mis, gaps = _misregistration(x, y, dx, dy, chunk)
    return PullResult(grid.x0, grid.y0, cell, dx, dy, idx, chunk, float(shift.max()),
                      float(np.percentile(shift, 95)), mis, gaps)


def _misregistration(x, y, dx, dy, chunk, cell: float = 1.0, min_points: int = 4):
    """Versatz zwischen verschiedenen Abschnitten am selben Ort (mittlere Abweichung je Zelle)."""
    ix = np.floor(x / cell).astype(np.int64)
    iy = np.floor(y / cell).astype(np.int64)
    key = (ix + 5000) * 10_007 + (iy + 5000) + (chunk.astype(np.int64)) * 200_000_000
    uniq, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    sx, sy = np.bincount(inv, dx) / cnt, np.bincount(inv, dy) / cnt
    first = np.zeros(len(uniq), int)
    first[inv[::-1]] = np.arange(len(x))[::-1]
    cells: dict[tuple[int, int], list[tuple[float, float]]] = {}
    for i in np.nonzero(cnt >= min_points)[0]:
        k = (int(ix[first[i]]), int(iy[first[i]]))
        cells.setdefault(k, []).append((float(sx[i]), float(sy[i])))
    worst = 0.0
    spots: list[tuple[float, float, float]] = []
    for (cx, cy), vecs in cells.items():
        if len(vecs) < 2:
            continue
        a = np.array(vecs)
        d = float(np.hypot(*(a.max(axis=0) - a.min(axis=0))))
        worst = max(worst, d)
        spots.append((d, (cx + 0.5) * cell, (cy + 0.5) * cell))
    spots.sort(reverse=True)
    return worst, [(s[1], s[2]) for s in spots[:12] if s[0] > 0.35]
