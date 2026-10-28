"""Realistische Stichdarstellung mit QPainter (3D-Fadenoptik)."""
from __future__ import annotations

import math

from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen

from .core.stitchplan import Cmd, StitchPlan


def _shade(c: QColor, f: float) -> QColor:
    if f < 1:
        return QColor(int(c.red() * f), int(c.green() * f), int(c.blue() * f))
    t = f - 1
    return QColor(int(c.red() + (255 - c.red()) * t), int(c.green() + (255 - c.green()) * t),
                  int(c.blue() + (255 - c.blue()) * t))


def iter_segments(plan: StitchPlan, upto: int | None = None, start: int = 0):
    """Liefert je Farbblock die genähten Segmente: (block, [(x0,y0,x1,y1), ...], jumps).

    `start`: nur Segmente nach dem start-ten Stich (für inkrementelles Weiterzeichnen im Simulator)."""
    n = 0
    for block in plan.blocks:
        segs, jumps = [], []
        prev = None
        for s in block.stitches:
            if upto is not None and n >= upto:
                break
            if s.cmd == Cmd.STITCH:
                n += 1
                if prev is not None and n > start:
                    segs.append((prev[0], prev[1], s.x, s.y))
                prev = (s.x, s.y)
            elif s.cmd == Cmd.JUMP:
                if prev is not None and n >= start:
                    jumps.append((prev[0], prev[1], s.x, s.y))
                prev = (s.x, s.y)
        yield block, segs, jumps
        if upto is not None and n >= upto:
            return


def draw_plan(p: QPainter, plan: StitchPlan, upto: int | None = None, realistic: bool = True,
              thread_w: float = 0.38, show_jumps: bool = False, px_per_mm: float = 4.0, start: int = 0):
    """Zeichnet in mm-Koordinaten (Painter muss bereits skaliert sein)."""
    p.setRenderHint(QPainter.Antialiasing, True)
    last_pt = None
    for block, segs, jumps in iter_segments(plan, upto, start):
        if not segs:
            continue
        col = QColor(*block.thread.color)
        lines = [QLineF(a, b, c, d) for a, b, c, d in segs]
        if realistic and px_per_mm >= 2.0:
            # 1) Schatten
            pen = QPen(_shade(col, 0.42), thread_w * 1.25, Qt.SolidLine, Qt.RoundCap)
            sh = QColor(pen.color())
            sh.setAlpha(170)
            pen.setColor(sh)
            p.setPen(pen)
            p.drawLines(lines)
            # 2) Fadenkörper
            p.setPen(QPen(_shade(col, 0.92), thread_w, Qt.SolidLine, Qt.RoundCap))
            p.drawLines(lines)
            # 3) Glanzlicht (verkürzt, leicht versetzt → Seidenglanz)
            hl = []
            off = thread_w * 0.16
            for a, b, c, d in segs:
                dx, dy = c - a, d - b
                L = math.hypot(dx, dy)
                if L < 0.25:
                    continue
                nx, ny = -dy / L * off, dx / L * off
                if ny > 0:  # Licht kommt von oben links
                    nx, ny = -nx, -ny
                k = min(0.3, 0.12 / L * 2)
                hl.append(QLineF(a + dx * k + nx, b + dy * k + ny, c - dx * k + nx, d - dy * k + ny))
            hc = _shade(col, 1.55)
            hc.setAlpha(150)
            p.setPen(QPen(hc, thread_w * 0.28, Qt.SolidLine, Qt.RoundCap))
            p.drawLines(hl)
        else:
            p.setPen(QPen(col, max(thread_w * 0.6, 0.6 / px_per_mm), Qt.SolidLine, Qt.RoundCap))
            p.drawLines(lines)
        if show_jumps and jumps:
            pen = QPen(QColor(120, 120, 120, 160), 0, Qt.DashLine)
            pen.setCosmetic(True)
            p.setPen(pen)
            p.drawLines([QLineF(a, b, c, d) for a, b, c, d in jumps])
        last_pt = segs[-1][2:]
    return last_pt


def render_image(plan: StitchPlan, px_per_mm: float = 8.0, margin_mm: float = 3.0,
                 background=(245, 243, 238), realistic: bool = True, upto=None) -> QImage:
    x0, y0, x1, y1 = plan.bounds()
    w = int((x1 - x0 + 2 * margin_mm) * px_per_mm) + 1
    h = int((y1 - y0 + 2 * margin_mm) * px_per_mm) + 1
    img = QImage(max(w, 1), max(h, 1), QImage.Format_ARGB32_Premultiplied)
    if background is None:
        img.fill(Qt.transparent)
    else:
        img.fill(QColor(*background))
    p = QPainter(img)
    p.scale(px_per_mm, px_per_mm)
    p.translate(-x0 + margin_mm, -y0 + margin_mm)
    draw_plan(p, plan, upto=upto, realistic=realistic, px_per_mm=px_per_mm)
    p.end()
    return img
