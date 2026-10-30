"""Export-Prüfung: Datei schreiben, unabhängig wieder einlesen und Stich für Stich vergleichen.

Zum Lesen dient pyembroidery. Damit wird geprüft, was tatsächlich in der Datei steht, nicht was der
Plan sagt. Das deckt verlorene Trims, Rundungsdrift und falsche Farben auf."""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field

import numpy as np
import pyembroidery as pe
from scipy.spatial import cKDTree

from ..core.stitchplan import Cmd, StitchPlan
from ..io.formats import export_plan

MACHINE_FORMATS = ("dst", "exp", "pes", "pec", "jef", "vp3", "xxx", "u01", "tbf")
# Formate ohne Farbtabelle (Farben legt die Maschine fest) oder nur mit fester Hersteller-Palette
NO_RGB = {"dst", "exp", "u01", "tbf"}
PALETTE_RGB = {"pes", "pec", "jef"}


@dataclass
class RoundTrip:
    ext: str
    bytes: int = 0
    stitches: int = 0
    expected: int = 0
    max_error_mm: float = 0.0
    drift_mm: float = 0.0
    trims: int = 0
    expected_trims: int = 0
    colors: int = 0
    expected_colors: int = 0
    color_error: float = 0.0
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def _plan_points(plan: StitchPlan) -> np.ndarray:
    pts = [(s.x, s.y) for b in plan.blocks for s in b.stitches if s.cmd == Cmd.STITCH]
    return np.array(pts, float).reshape(-1, 2)


def _read(path: str):
    # Der JEF-Leser erkennt die Trim-Sprungfolge nur auf Wunsch
    pat = pe.read(path, {"trims": True} if path.endswith(".jef") else None)
    if pat is None:
        raise ValueError("unreadable")
    pts, trims, jumps_in_row, trim_like, colors, needles = [], 0, 0, 0, 1, 0
    for x, y, cmd in pat.stitches:
        c = cmd & pe.COMMAND_MASK
        if c == pe.STITCH:
            if jumps_in_row >= 3:
                trim_like += 1
            jumps_in_row = 0
            pts.append((x / 10.0, y / 10.0))
        elif c == pe.JUMP:
            jumps_in_row += 1
        elif c == pe.TRIM:
            trims += 1
        elif c == pe.COLOR_CHANGE:
            colors += 1
        elif c == pe.NEEDLE_SET:
            needles += 1
    # U01/TBF wählen Nadeln statt Farbwechsel
    return np.array(pts, float).reshape(-1, 2), max(trims, trim_like), max(colors, needles), pat


def check_format(plan: StitchPlan, ext: str, folder: str | None = None) -> RoundTrip:
    r = RoundTrip(ext)
    expected = _plan_points(plan)
    r.expected = len(expected)
    r.expected_trims = plan.trim_count
    r.expected_colors = len(plan.blocks)
    own = folder is None
    tmp = tempfile.TemporaryDirectory() if own else None
    path = os.path.join(tmp.name if own else folder, f"roundtrip.{ext}")
    try:
        kw = {"trim_mode": "code"} if ext == "exp" else {}
        export_plan(plan, path, **kw)
        r.bytes = os.path.getsize(path)
        pts, trims, colors, pat = _read(path)
    except Exception as e:  # noqa: BLE001 - jedes Versagen eines Formats ist ein Befund, kein Absturz
        r.problems.append(f"export/read failed: {type(e).__name__}: {e}")
        return r
    finally:
        if tmp is not None:
            tmp.cleanup()
    r.stitches = len(pts)
    r.trims = trims
    r.colors = colors
    if len(pts) == 0:
        r.problems.append("no stitches in file")
        return r
    # Dateien sind auf die Motivmitte zentriert; Y-Richtung ist nach dem Lesen wieder Bildschirm-Y
    a = expected - (expected.min(axis=0) + expected.max(axis=0)) / 2
    b = pts - (pts.min(axis=0) + pts.max(axis=0)) / 2
    forward = cKDTree(b).query(a)[0]
    backward = cKDTree(a).query(b)[0]
    r.max_error_mm = float(max(forward.max(), backward.max()))
    if len(pts) == len(expected):
        # Laufende Summe gerundeter Deltas darf sich nicht aufaddieren
        n = min(len(a), len(b))
        r.drift_mm = float(np.hypot(*(a[:n] - b[:n]).T).max())
    if r.max_error_mm > 0.25:
        r.problems.append(f"position error {r.max_error_mm:.2f} mm")
    if r.drift_mm > 0.25:
        r.problems.append(f"sequence drift {r.drift_mm:.2f} mm")
    if abs(r.stitches - r.expected) > max(3, r.expected * 0.01):
        r.problems.append(f"stitch count {r.stitches} != {r.expected}")
    if r.trims < r.expected_trims - 1:
        r.problems.append(f"trims lost: {r.trims} of {r.expected_trims}")
    if r.expected_colors > 1 and r.colors != r.expected_colors:
        r.problems.append(f"color changes {r.colors} != {r.expected_colors}")
    if ext not in NO_RGB and len(pat.threadlist) >= len(plan.blocks):
        errs = []
        for block, th in zip(plan.blocks, pat.threadlist):
            got = np.array((th.get_red(), th.get_green(), th.get_blue()), float)
            errs.append(float(np.linalg.norm(got - np.array(block.thread.color, float))))
        r.color_error = max(errs, default=0.0)
        # Feste Paletten treffen seltene Farben nur grob; RGB-Formate müssen exakt sein
        if r.color_error > (160 if ext in PALETTE_RGB else 3):
            r.problems.append(f"color off by {r.color_error:.0f}")
    return r


def check_all(plan: StitchPlan, formats=MACHINE_FORMATS) -> list[RoundTrip]:
    return [check_format(plan, ext) for ext in formats]
