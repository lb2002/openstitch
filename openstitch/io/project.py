"""Speichern/Laden von editierbaren OpenStitch-Projekten (.ostitch) und Produktionsblatt-Export."""
from __future__ import annotations

import datetime as _dt
import json

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPageLayout, QPageSize, QPainter, QPdfWriter, QPen

from .. import APP_NAME, __version__
from ..core.design import HOOPS, Design, Hoop, Settings, object_from_dict
from ..core.stitchplan import StitchPlan
from ..render import render_image


def save_project(design: Design, path: str) -> None:
    data = {
        "app": APP_NAME,
        "version": __version__,
        "name": design.name,
        "hoop": {
            "name": design.hoop.name,
            "width": design.hoop.width,
            "height": design.hoop.height,
            "round": design.hoop.round,
            "mode": design.hoop.mode,
            "margin_mm": design.hoop.margin_mm,
        },
        "settings": design.settings.__dict__,
        "objects": [o.to_dict() for o in design.objects],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_project(path: str) -> Design:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    h = data.get("hoop", {})
    hoop = Hoop(
        h.get("name", "Rahmen"),
        h.get("width", 150),
        h.get("height", 150),
        h.get("round", True),
        h.get("mode", "medium"),
        h.get("margin_mm", 4.5),
    )
    st = Settings(**{k: v for k, v in data.get("settings", {}).items() if k in Settings.__annotations__})
    objs = [object_from_dict(od) for od in data.get("objects", [])]
    return Design(objects=objs, hoop=hoop, settings=st, name=data.get("name", "Projekt"))


def export_worksheet_pdf(design: Design, plan: StitchPlan, path: str, machine_name: str | None = None) -> None:
    """Erzeugt ein druckfertiges Produktionsblatt (PDF) für alle Stickmaschinen."""
    mach_str = machine_name or getattr(design.settings, "machine_name", "Universal Standard (15 Nadeln)")
    max_nd = max(1, getattr(design.settings, "needles", 15))
    pdf = QPdfWriter(path)
    pdf.setPageSize(QPageSize(QPageSize.A4))
    pdf.setResolution(300)
    p = QPainter(pdf)
    W, H = pdf.width(), pdf.height()
    m = int(W * 0.06)

    # Titelzeile
    p.setPen(QColor(25, 28, 34))
    p.setFont(QFont("Segoe UI", 16, QFont.Bold))
    p.drawText(m, m + 60, f"{design.name}  —  Produktions- & Einrichteblatt")
    p.setFont(QFont("Segoe UI", 9))
    p.setPen(QColor(100, 105, 115))
    now_str = _dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    p.drawText(m, m + 115, f"Erstellt mit {APP_NAME} Studio {__version__} am {now_str}")

    # Kennzahlen-Box
    x0, y0, x1, y1 = plan.bounds()
    bw, bh = x1 - x0, y1 - y0
    box_y = m + 150
    box_h = 260
    p.setPen(QPen(QColor(210, 215, 222), 3))
    p.setBrush(QColor(248, 249, 251))
    p.drawRoundedRect(m, box_y, W - 2 * m, box_h, 18, 18)

    stats = [
        ("Stiche gesamt", f"{plan.stitch_count:,}".replace(",", "'")),
        ("Grösse (B × H)", f"{bw:.1f} × {bh:.1f} mm"),
        ("Farbwechsel / Blöcke", f"{plan.color_changes} ({len(plan.blocks)} Blöcke)"),
        ("Fadenschnitte (Trims)", f"{plan.trim_count}"),
        ("Stickrahmen", f"{design.hoop.name} ({design.hoop.width:.0f}×{design.hoop.height:.0f} mm)"),
        (f"Laufzeit (ca. {design.settings.machine_spm} SPM)", f"{plan.estimated_minutes(design.settings.machine_spm):.1f} Min."),
        ("Oberfadenbedarf", f"{plan.thread_length_m():.1f} m"),
        ("Maschinenprofil", mach_str[:28]),
    ]
    col_w = (W - 2 * m - 60) // 4
    for idx, (k, v) in enumerate(stats):
        r, c = divmod(idx, 4)
        cx = m + 30 + c * col_w
        cy = box_y + 65 + r * 110
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(110, 115, 125))
        p.drawText(cx, cy, k)
        p.setFont(QFont("Segoe UI", 11, QFont.Bold))
        p.setPen(QColor(25, 28, 34))
        p.drawText(cx, cy + 45, v)

    # Vorschau-Bild links
    prev_y = box_y + box_h + 60
    prev_size = int((W - 2 * m) * 0.48)
    p.setPen(QPen(QColor(210, 215, 222), 3))
    p.setBrush(QColor(245, 243, 238))
    p.drawRoundedRect(m, prev_y, prev_size, prev_size, 18, 18)
    img: QImage = render_image(plan, px_per_mm=10.0, margin_mm=4.0)
    scaled = img.scaled(prev_size - 40, prev_size - 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    ix = m + (prev_size - scaled.width()) // 2
    iy = prev_y + (prev_size - scaled.height()) // 2
    p.drawImage(ix, iy, scaled)

    # Nadel-/Farbsequenz-Tabelle rechts
    tx = m + prev_size + 50
    tw = W - m - tx
    p.setFont(QFont("Segoe UI", 11, QFont.Bold))
    p.setPen(QColor(25, 28, 34))
    p.drawText(tx, prev_y + 40, f"Farbfolge & Nadelzuordnung ({max_nd} Nadeln)")

    # eindeutige Farben → Nadeln 1..max_nd
    needle_map: dict[str, int] = {}
    for b in plan.blocks:
        if b.thread.hex not in needle_map:
            needle_map[b.thread.hex] = (len(needle_map) % max_nd) + 1

    ry = prev_y + 80
    row_h = 72
    for bi, b in enumerate(plan.blocks[:22]):
        n_st = sum(1 for s in b.stitches if s.cmd == 0)
        needle = needle_map[b.thread.hex]
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(*b.thread.color))
        p.drawRoundedRect(tx, ry, 52, 48, 8, 8)
        p.setPen(QPen(QColor(180, 180, 180), 2))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(tx, ry, 52, 48, 8, 8)

        p.setPen(QColor(25, 28, 34))
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        label = b.thread.name or b.thread.hex
        code = f" ({b.thread.code})" if b.thread.code else ""
        p.drawText(tx + 70, ry + 24, f"{bi + 1}. Nadel {needle}: {label}{code}")
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(100, 105, 115))
        p.drawText(tx + 70, ry + 50, f"{n_st} Stiche   ·   {b.thread.hex.upper()}")
        ry += row_h

    p.end()
