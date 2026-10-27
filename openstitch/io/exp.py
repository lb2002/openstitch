"""Melco EXP (Expanded) – natives Format der Melco EMT-Serie.

Aufbau: Folge von 2-Byte-Datensätzen (dx, dy) in 0.1 mm, vorzeichenbehaftet (±127),
Y-Achse nach oben. Steuercodes beginnen mit 0x80:
    80 01 00 00   Farbwechsel / Stopp
    80 04 dx dy   Sprung
    80 80 07 00   Fadenschnitt (Trim)

Ältere Melco-Firmware schneidet den Faden nicht über den Trim-Code, sondern nach einer
Folge von Sprüngen. Mit `trim_mode` lässt sich das Verhalten wählen.
"""
from __future__ import annotations

import io
import math

from ..core.stitchplan import Cmd, StitchPlan

MAX = 127


def _deltas(dx: int, dy: int, maxd: int = MAX, min_n: int = 1):
    n = max(min_n, math.ceil(max(abs(dx), abs(dy)) / maxd))
    xs = [round(dx * k / n) for k in range(n + 1)]
    ys = [round(dy * k / n) for k in range(n + 1)]
    return [(xs[k + 1] - xs[k], ys[k + 1] - ys[k]) for k in range(n)]


def write_exp(plan: StitchPlan, f, trim_mode: str = "code", min_jumps_for_trim: int = 3) -> None:
    """trim_mode: 'code' (80 80 07 00), 'jumps' (Sprungfolge) oder 'both'."""
    out = bytearray()
    # Ursprung = Mitte des Designs (Melco-Konvention: Start im Rahmenzentrum)
    x0, y0, x1, y1 = plan.bounds()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    xx = yy = 0  # aktuelle Position in 0.1 mm
    pending_trim = False

    def emit_move(tx, ty, jump: bool, force_jumps: int = 0):
        nonlocal xx, yy
        dx, dy = tx - xx, ty - yy
        parts = _deltas(dx, dy, MAX, force_jumps if jump else 1)
        for ddx, ddy in parts:
            if jump:
                out.extend(b"\x80\x04")
            out.extend(bytes([ddx & 0xFF, (-ddy) & 0xFF]))
        xx, yy = tx, ty

    first_block = True
    for bi, block in enumerate(plan.blocks):
        if not first_block:
            out.extend(b"\x80\x01\x00\x00")
        first_block = False
        for s in block.stitches:
            tx = int(round((s.x - cx) * 10))
            ty = int(round((s.y - cy) * 10))
            if s.cmd == Cmd.STITCH:
                if tx == xx and ty == yy:
                    continue
                emit_move(tx, ty, False)
            elif s.cmd == Cmd.JUMP:
                force = min_jumps_for_trim if pending_trim and trim_mode in ("jumps", "both") else 0
                emit_move(tx, ty, True, force)
                pending_trim = False
            elif s.cmd == Cmd.TRIM:
                if trim_mode in ("code", "both"):
                    out.extend(b"\x80\x80\x07\x00")
                pending_trim = True
            elif s.cmd in (Cmd.COLOR_CHANGE, Cmd.STOP):
                out.extend(b"\x80\x01\x00\x00")
    f.write(bytes(out))


def exp_bytes(plan: StitchPlan, **kw) -> bytes:
    b = io.BytesIO()
    write_exp(plan, b, **kw)
    return b.getvalue()
