"""Google-Material-3 Vektor-Icons, offizielles OpenStitch-Starter-Logo & Interaktiver Studio-Rundgang."""
from __future__ import annotations

import math
from PySide6.QtCore import QPointF, QRectF, QSettings, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from shapely.geometry import LineString, Polygon

from ..core.design import Design, FillObject, HOOPS, SatinObject
from ..core.stitchplan import Thread
from ..i18n import tr
from ..text import TextObject
from . import theme


# ===========================================================================
# 1. Kristallklare Vektor-Icons (Google Material 3 Stil, kein Emoji-Clipping)
# ===========================================================================
def studio_icon(kind: str, size: int = 18) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    th = theme.current()
    c_blue = QColor(th.icon_blue)
    c_gold = QColor(th.icon_gold)
    c_green = QColor(th.icon_green)
    c_red = QColor(th.icon_red)
    c_purple = QColor(th.icon_purple)
    c_cyan = QColor(th.icon_cyan)
    c_light = QColor(th.icon_light)

    s = float(size)
    m = s * 0.16

    if kind == "new":
        p.setPen(QPen(c_light, 1.7, Qt.SolidLine, Qt.RoundCap))
        p.drawRoundedRect(QRectF(m, m, s - 2 * m, s - 2 * m), 3, 3)
        p.setPen(QPen(c_blue, 1.8, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(s * 0.5, s * 0.32), QPointF(s * 0.5, s * 0.68))
        p.drawLine(QPointF(s * 0.32, s * 0.5), QPointF(s * 0.68, s * 0.5))

    elif kind == "import":
        p.setPen(QPen(c_gold, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QColor(253, 214, 99, 40))
        path = QPainterPath()
        path.moveTo(m, s * 0.30)
        path.lineTo(s * 0.42, s * 0.30)
        path.lineTo(s * 0.50, s * 0.40)
        path.lineTo(s - m, s * 0.40)
        path.lineTo(s - m, s * 0.80)
        path.lineTo(m, s * 0.80)
        path.closeSubpath()
        p.drawPath(path)

    elif kind == "svg":
        p.setPen(QPen(c_purple, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path = QPainterPath()
        path.moveTo(m, s - m)
        path.cubicTo(QPointF(m, s * 0.2), QPointF(s - m, s * 0.8), QPointF(s - m, m))
        p.drawPath(path)
        p.setBrush(c_purple)
        p.drawEllipse(QPointF(m, s - m), 2.2, 2.2)
        p.drawEllipse(QPointF(s - m, m), 2.2, 2.2)

    elif kind == "export":
        p.setPen(QPen(c_green, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(QPointF(s * 0.5, s * 0.22), QPointF(s * 0.5, s * 0.68))
        p.drawLine(QPointF(s * 0.32, s * 0.50), QPointF(s * 0.5, s * 0.68))
        p.drawLine(QPointF(s * 0.68, s * 0.50), QPointF(s * 0.5, s * 0.68))
        p.drawLine(QPointF(m, s * 0.82), QPointF(s - m, s * 0.82))

    elif kind == "pdf":
        p.setPen(QPen(c_red, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawRoundedRect(QRectF(s * 0.22, m, s * 0.56, s - 2 * m), 2.5, 2.5)
        p.drawLine(QPointF(s * 0.34, s * 0.42), QPointF(s * 0.66, s * 0.42))
        p.drawLine(QPointF(s * 0.34, s * 0.58), QPointF(s * 0.66, s * 0.58))
        p.drawLine(QPointF(s * 0.34, s * 0.72), QPointF(s * 0.54, s * 0.72))

    elif kind == "magic":
        # Google AI Sparkle Stern
        p.setPen(Qt.NoPen)
        p.setBrush(c_gold)
        cx, cy = s * 0.48, s * 0.50
        r_out, r_in = s * 0.38, s * 0.12
        pts = []
        for i in range(8):
            ang = i * math.pi / 4.0
            r = r_out if i % 2 == 0 else r_in
            pts.append(QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang)))
        p.drawPolygon(QPolygonF(pts))
        p.setBrush(c_blue)
        p.drawEllipse(QPointF(s * 0.78, s * 0.24), 2.0, 2.0)

    elif kind == "photo":
        p.setPen(QPen(c_cyan, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawRoundedRect(QRectF(m, s * 0.20, s - 2 * m, s * 0.62), 3, 3)
        p.setBrush(c_gold)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(s * 0.35, s * 0.38), 2.0, 2.0)
        p.setPen(QPen(c_green, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path = QPainterPath()
        path.moveTo(s * 0.22, s * 0.74)
        path.lineTo(s * 0.45, s * 0.50)
        path.lineTo(s * 0.62, s * 0.65)
        path.lineTo(s * 0.76, s * 0.46)
        p.drawPath(path)

    elif kind == "text":
        p.setPen(QPen(c_blue, 2.0, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(s * 0.24, s * 0.24), QPointF(s * 0.76, s * 0.24))
        p.drawLine(QPointF(s * 0.50, s * 0.24), QPointF(s * 0.50, s * 0.80))
        p.drawLine(QPointF(s * 0.36, s * 0.80), QPointF(s * 0.64, s * 0.80))

    elif kind == "applique":
        p.setPen(QPen(c_green, 1.6, Qt.DashLine, Qt.RoundCap))
        p.setBrush(QColor(129, 201, 149, 45))
        p.drawEllipse(QRectF(m, m, s - 2 * m, s - 2 * m))

    elif kind == "puff":
        p.setPen(QPen(c_purple, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QColor(197, 138, 249, 45))
        p.drawRoundedRect(QRectF(s * 0.22, s * 0.28, s * 0.56, s * 0.52), 4, 4)
        p.drawLine(QPointF(s * 0.30, s * 0.20), QPointF(s * 0.70, s * 0.20))

    elif kind == "transfer":
        p.setPen(QPen(c_cyan, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawRoundedRect(QRectF(s * 0.22, s * 0.18, s * 0.56, s * 0.64), 2.5, 2.5)
        p.setBrush(c_cyan)
        p.drawRect(QRectF(s * 0.36, s * 0.18, s * 0.28, s * 0.20))

    elif kind == "doctor":
        p.setPen(QPen(c_green, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawEllipse(QRectF(m, m, s - 2 * m, s - 2 * m))
        p.drawLine(QPointF(s * 0.33, s * 0.52), QPointF(s * 0.46, s * 0.66))
        p.drawLine(QPointF(s * 0.46, s * 0.66), QPointF(s * 0.70, s * 0.36))

    elif kind == "tour":
        p.setPen(QPen(c_gold, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QColor(253, 214, 99, 35))
        p.drawEllipse(QRectF(m, m, s - 2 * m, s - 2 * m))
        p.setBrush(c_gold)
        pts = [
            QPointF(s * 0.65, s * 0.35),
            QPointF(s * 0.54, s * 0.54),
            QPointF(s * 0.35, s * 0.65),
            QPointF(s * 0.46, s * 0.46),
        ]
        p.drawPolygon(QPolygonF(pts))

    elif kind == "fit":
        p.setPen(QPen(c_blue, 1.7, Qt.SolidLine, Qt.RoundCap))
        d = s * 0.22
        p.drawLine(QPointF(m, m), QPointF(m + d, m))
        p.drawLine(QPointF(m, m), QPointF(m, m + d))
        p.drawLine(QPointF(s - m, m), QPointF(s - m - d, m))
        p.drawLine(QPointF(s - m, m), QPointF(s - m, m + d))
        p.drawLine(QPointF(m, s - m), QPointF(m + d, s - m))
        p.drawLine(QPointF(m, s - m), QPointF(m, s - m - d))
        p.drawLine(QPointF(s - m, s - m), QPointF(s - m - d, s - m))
        p.drawLine(QPointF(s - m, s - m), QPointF(s - m, s - m - d))

    elif kind == "select":
        p.setPen(QPen(c_light, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(c_blue)
        pts = [
            QPointF(s * 0.26, s * 0.18),
            QPointF(s * 0.26, s * 0.78),
            QPointF(s * 0.44, s * 0.62),
            QPointF(s * 0.58, s * 0.84),
            QPointF(s * 0.68, s * 0.78),
            QPointF(s * 0.54, s * 0.56),
            QPointF(s * 0.76, s * 0.56),
        ]
        p.drawPolygon(QPolygonF(pts))

    elif kind == "nodes":
        p.setPen(QPen(c_gold, 1.6))
        p.drawLine(QPointF(s * 0.22, s * 0.75), QPointF(s * 0.50, s * 0.25))
        p.drawLine(QPointF(s * 0.50, s * 0.25), QPointF(s * 0.78, s * 0.70))
        p.setBrush(c_blue)
        for pt in (QPointF(s * 0.22, s * 0.75), QPointF(s * 0.50, s * 0.25), QPointF(s * 0.78, s * 0.70)):
            p.drawRect(QRectF(pt.x() - 2.5, pt.y() - 2.5, 5, 5))

    elif kind == "fill":
        p.setPen(QPen(c_blue, 1.5))
        p.setBrush(QColor(138, 180, 248, 55))
        p.drawRoundedRect(QRectF(m, m, s - 2 * m, s - 2 * m), 3, 3)
        for k in (0.35, 0.52, 0.69):
            p.drawLine(QPointF(m + 2, s * k), QPointF(s - m - 2, s * k))

    elif kind == "satin":
        p.setPen(QPen(c_gold, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path = QPainterPath()
        for idx, y in enumerate([0.22, 0.36, 0.50, 0.64, 0.78]):
            x = s * (0.24 if idx % 2 == 0 else 0.76)
            if idx == 0:
                path.moveTo(x, s * y)
            else:
                path.lineTo(x, s * y)
        p.drawPath(path)

    elif kind == "run":
        p.setPen(QPen(c_green, 1.9, Qt.DashLine, Qt.RoundCap))
        p.drawLine(QPointF(m, s - m), QPointF(s - m, m))

    elif kind == "heatmap":
        p.setPen(Qt.NoPen)
        p.setBrush(c_red)
        p.drawEllipse(QPointF(s * 0.5, s * 0.52), s * 0.34, s * 0.34)
        p.setBrush(c_gold)
        p.drawEllipse(QPointF(s * 0.5, s * 0.55), s * 0.21, s * 0.21)

    elif kind == "zoom":
        p.setPen(QPen(c_light, 1.7, Qt.SolidLine, Qt.RoundCap))
        p.drawEllipse(QPointF(s * 0.44, s * 0.44), s * 0.24, s * 0.24)
        p.drawLine(QPointF(s * 0.62, s * 0.62), QPointF(s * 0.82, s * 0.82))

    elif kind == "home":
        p.setPen(QPen(c_light, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPolyline(QPolygonF([QPointF(m, s * 0.5), QPointF(s * 0.5, m), QPointF(s - m, s * 0.5)]))
        p.drawPolyline(QPolygonF([QPointF(s * 0.26, s * 0.46), QPointF(s * 0.26, s - m),
                                  QPointF(s * 0.74, s - m), QPointF(s * 0.74, s * 0.46)]))

    elif kind == "open":
        p.setPen(QPen(c_gold, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path = QPainterPath()
        path.moveTo(m, s * 0.8)
        path.lineTo(m, s * 0.24)
        path.lineTo(s * 0.4, s * 0.24)
        path.lineTo(s * 0.5, s * 0.36)
        path.lineTo(s * 0.8, s * 0.36)
        path.lineTo(s * 0.8, s * 0.48)
        path.moveTo(m, s * 0.8)
        path.lineTo(s * 0.3, s * 0.48)
        path.lineTo(s - m * 0.6, s * 0.48)
        path.lineTo(s * 0.72, s * 0.8)
        path.closeSubpath()
        p.drawPath(path)

    elif kind == "save":
        p.setPen(QPen(c_blue, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawRoundedRect(QRectF(m, m, s - 2 * m, s - 2 * m), 2.5, 2.5)
        p.drawRect(QRectF(s * 0.32, m, s * 0.36, s * 0.24))
        p.drawRect(QRectF(s * 0.28, s * 0.58, s * 0.44, s - m - s * 0.58))

    elif kind in ("undo", "redo"):
        p.save()
        if kind == "redo":
            p.translate(s, 0)
            p.scale(-1, 1)
        p.setPen(QPen(c_light, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path = QPainterPath()
        path.moveTo(s * 0.26, s * 0.42)
        path.lineTo(s * 0.62, s * 0.42)
        path.cubicTo(s * 0.92, s * 0.42, s * 0.92, s * 0.8, s * 0.6, s * 0.8)
        path.lineTo(s * 0.42, s * 0.8)
        p.drawPath(path)
        p.drawPolyline(QPolygonF([QPointF(s * 0.42, s * 0.24), QPointF(s * 0.24, s * 0.42), QPointF(s * 0.42, s * 0.6)]))
        p.restore()

    elif kind == "palette":
        p.setPen(QPen(c_light, 1.6, Qt.SolidLine, Qt.RoundCap))
        p.drawEllipse(QPointF(s * 0.5, s * 0.5), s * 0.36, s * 0.36)
        p.setPen(Qt.NoPen)
        for (dx, dy), col in (((0.36, 0.38), c_red), ((0.6, 0.34), c_gold), ((0.68, 0.56), c_green), ((0.42, 0.64), c_blue)):
            p.setBrush(col)
            p.drawEllipse(QPointF(s * dx, s * dy), s * 0.075, s * 0.075)

    elif kind in ("up", "down"):
        p.setPen(QPen(c_light, 1.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        a, b = (0.62, 0.38) if kind == "up" else (0.38, 0.62)
        p.drawPolyline(QPolygonF([QPointF(s * 0.26, s * a), QPointF(s * 0.5, s * b), QPointF(s * 0.74, s * a)]))

    elif kind == "eye":
        p.setPen(QPen(c_light, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        path = QPainterPath()
        path.moveTo(m * 0.7, s * 0.5)
        path.quadTo(s * 0.5, s * 0.14, s - m * 0.7, s * 0.5)
        path.quadTo(s * 0.5, s * 0.86, m * 0.7, s * 0.5)
        p.drawPath(path)
        p.setBrush(c_light)
        p.drawEllipse(QPointF(s * 0.5, s * 0.5), s * 0.11, s * 0.11)

    elif kind == "copy":
        p.setPen(QPen(c_light, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawRoundedRect(QRectF(s * 0.36, s * 0.36, s * 0.46, s * 0.46), 2, 2)
        p.drawPolyline(QPolygonF([QPointF(s * 0.24, s * 0.64), QPointF(s * 0.18, s * 0.64), QPointF(s * 0.18, s * 0.18),
                                  QPointF(s * 0.64, s * 0.18), QPointF(s * 0.64, s * 0.24)]))

    elif kind == "trash":
        p.setPen(QPen(c_red, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(QPointF(s * 0.2, s * 0.28), QPointF(s * 0.8, s * 0.28))
        p.drawLine(QPointF(s * 0.4, s * 0.28), QPointF(s * 0.42, s * 0.16))
        p.drawLine(QPointF(s * 0.6, s * 0.28), QPointF(s * 0.58, s * 0.16))
        p.drawPolyline(QPolygonF([QPointF(s * 0.27, s * 0.28), QPointF(s * 0.32, s * 0.84),
                                  QPointF(s * 0.68, s * 0.84), QPointF(s * 0.73, s * 0.28)]))

    elif kind == "usb":
        p.setPen(QPen(c_blue, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawRoundedRect(QRectF(s * 0.28, s * 0.36, s * 0.44, s * 0.48), 3, 3)
        p.drawRect(QRectF(s * 0.38, s * 0.14, s * 0.24, s * 0.22))

    p.end()
    return QIcon(pix)


# ===========================================================================
# 2. Offizielles OpenStitch-Emblem als erste Stickdatei (Herstellerneutral)
# ===========================================================================
def create_openstitch_logo_design() -> Design:
    """Erzeugt das offizielle OpenStitch-Studio-Wappen als parametrische Stickdatei."""
    d = Design(name="OpenStitch_Official_Logo", hoop=HOOPS[2])  # Rund 15 cm Standard

    # 1. Abgerundetes Hexagon-Wappen (Tatami-Hintergrund in Deep Space Indigo)
    hex_pts = []
    radius = 37.0
    for i in range(6):
        ang = math.radians(i * 60 - 30)
        hex_pts.append((radius * math.cos(ang), radius * math.sin(ang)))
    hex_poly = Polygon(hex_pts).buffer(3.5, join_style=1)

    d.objects.append(
        FillObject(
            Thread.from_hex("#162847", "Space Indigo", "075", "OpenStitch"),
            name="Shield",
            geom=hex_poly.buffer(-2.6),
            angle=30.0,
            spacing=0.44,
            pattern="ziegel",
            pull_comp=0.20,
        )
    )

    # 2. Äusserer Satin-Rahmen in Google-Blau (#4285F4)
    outer_ring = hex_poly.difference(hex_poly.buffer(-3.2))
    d.objects.append(
        SatinObject(
            Thread.from_hex("#4285F4", "Studio Blue", "035", "OpenStitch"),
            name="Shield border",
            geom=outer_ring,
            spacing=0.38,
            pull_comp=0.18,
        )
    )

    # 3. Geschwungene Fadenwelle durch das Wappen (Gold-Gelb #FBBC04)
    wave_pts = []
    for k in range(-24, 25, 2):
        x = float(k)
        y = -6.0 + 7.5 * math.sin(k / 7.8)
        wave_pts.append((x, y))
    wave_ribbon = LineString(wave_pts).buffer(2.2, cap_style=1, join_style=1)
    d.objects.append(
        SatinObject(
            Thread.from_hex("#FBBC04", "Solar Gold", "023", "OpenStitch"),
            name="Golden thread",
            geom=wave_ribbon,
            spacing=0.36,
            pull_comp=0.18,
        )
    )

    # 4. Korallenrote Satin-Fadenschlaufe (#EA4335) als harmonischer Oberbogen
    arc_pts = [
        (20.0 * math.cos(math.radians(a)), -5.5 + 13.5 * math.sin(math.radians(a)))
        for a in range(-150, -30, 8)
    ]
    arc_ribbon = LineString(arc_pts).buffer(1.45, cap_style=1, join_style=1)
    d.objects.append(
        SatinObject(
            Thread.from_hex("#EA4335", "Coral Red", "042", "OpenStitch"),
            name="Coral loop",
            geom=arc_ribbon,
            spacing=0.36,
            pull_comp=0.16,
        )
    )

    # 5. Stilisierte Sticknadel-Silhouette (Smaragdgrün #34A853)
    needle_line = LineString([(-15.0, -21.0), (15.0, 4.0)])
    needle_geom = needle_line.buffer(1.8, cap_style=1)
    d.objects.append(
        SatinObject(
            Thread.from_hex("#34A853", "Emerald", "058", "OpenStitch"),
            name="Needle",
            geom=needle_geom,
            spacing=0.36,
            pull_comp=0.16,
        )
    )

    # 6. Markenschriftzug „OPENSTITCH“ in Reinweiss (#FFFFFF)
    d.objects.append(
        TextObject(
            Thread.from_hex("#FFFFFF", "Pure White", "001", "OpenStitch"),
            name="Lettering",
            text="OPENSTITCH",
            height=5.6,
            letter_spacing=0.45,
            transform=(1.0, 0.0, 0.0, 1.0, 0.0, 13.0),
        )
    )

    return d


# ===========================================================================
# 3. In-App Spotlight & Coach-Mark Popups (Direkt im Hauptfenster!)
# ===========================================================================
class InAppTourOverlay(QWidget):
    """Interaktives Spotlight-Overlay mit schwebenden Coach-Mark-Popups direkt über den UI-Bereichen."""

    # Enthält i18n-Schlüssel: Übersetzt wird erst in _refresh, damit der Rundgang der Sprache folgt.
    STEPS = [
        {
            "target": "canvas_center",
            "place": "right",
            "badge": "tour_app_1_badge",
            "title": "tour_app_1_title",
            "body": "tour_app_1_body",
            "action_label": "tour_app_1_action",
            "action_key": "cycle_fabric",
        },
        {
            "target": "ctx_bar",
            "place": "below",
            "badge": "tour_app_2_badge",
            "title": "tour_app_2_title",
            "body": "tour_app_2_body",
            "action_label": "tour_app_2_action",
            "action_key": "fit",
        },
        {
            "target": "top_toolbar",
            "place": "below",
            "badge": "tour_app_3_badge",
            "title": "tour_app_3_title",
            "body": "tour_app_3_body",
            "action_label": "tour_app_3_action",
            "action_key": "auto_digitize",
        },
        {
            "target": "left_rail",
            "place": "right",
            "badge": "tour_app_4_badge",
            "title": "tour_app_4_title",
            "body": "tour_app_4_body",
            "action_label": "tour_app_4_action",
            "action_key": "nodes_tool",
        },
        {
            "target": "left_dock",
            "place": "right",
            "badge": "tour_app_5_badge",
            "title": "tour_app_5_title",
            "body": "tour_app_5_body",
            "action_label": None,
            "action_key": None,
        },
        {
            "target": "right_dock",
            "place": "left",
            "badge": "tour_app_6_badge",
            "title": "tour_app_6_title",
            "body": "tour_app_6_body",
            "action_label": None,
            "action_key": None,
        },
        {
            "target": "bottom_bar",
            "place": "above",
            "badge": "tour_app_7_badge",
            "title": "tour_app_7_title",
            "body": "tour_app_7_body",
            "action_label": "tour_app_7_action",
            "action_key": "play_sim",
        },
    ]

    def __init__(self, main_win):
        super().__init__(main_win)
        self.main_win = main_win
        self.idx = 0
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)

        # Schwebende Coach-Mark Popup-Karte
        self.card = QFrame(self)
        self.card.setFixedWidth(410)
        self.card.setStyleSheet(
            "QFrame {"
            "  background-color: #262b36;"
            "  border: 1.5px solid #5b8def;"
            "  border-radius: 12px;"
            "}"
            "QLabel { border: none; background: transparent; }"
        )
        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        top_row = QHBoxLayout()
        self.lbl_badge = QLabel()
        self.lbl_badge.setStyleSheet(
            "color: #8ab4f8; font-size: 8.5pt; font-weight: 700; letter-spacing: 1px;"
        )
        top_row.addWidget(self.lbl_badge)
        top_row.addStretch(1)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #9aa4b8; font-size: 10pt; padding: 0; }"
            "QPushButton:hover { color: #ffffff; background-color: #343b4a; border-radius: 12px; }"
        )
        self.btn_close.clicked.connect(self.close_tour)
        top_row.addWidget(self.btn_close)
        lay.addLayout(top_row)

        self.lbl_title = QLabel()
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet("color: #f1f3f9; font-size: 12pt; font-weight: 700;")
        lay.addWidget(self.lbl_title)

        self.lbl_body = QLabel()
        self.lbl_body.setWordWrap(True)
        self.lbl_body.setStyleSheet("color: #cfd5e2; font-size: 9.5pt; line-height: 1.4;")
        lay.addWidget(self.lbl_body)

        self.btn_try = QPushButton()
        self.btn_try.setCursor(Qt.PointingHandCursor)
        self.btn_try.setStyleSheet(
            "QPushButton { background-color: rgba(138, 180, 248, 0.15); border: 1px solid #5b8def; "
            "color: #a8c7fa; font-weight: 600; padding: 6px 10px; border-radius: 7px; }"
            "QPushButton:hover { background-color: rgba(138, 180, 248, 0.28); color: #ffffff; }"
        )
        self.btn_try.clicked.connect(self._on_try_action)
        lay.addWidget(self.btn_try)

        foot = QHBoxLayout()
        self.cb_startup = QCheckBox()
        self.cb_startup.setStyleSheet("color: #9aa4b8; font-size: 8.5pt;")
        settings = QSettings("OpenStitch", "OpenStitchStudio")
        self.cb_startup.setChecked(settings.value("show_tour_on_startup", True, type=bool))
        self.cb_startup.toggled.connect(
            lambda v: QSettings("OpenStitch", "OpenStitchStudio").setValue("show_tour_on_startup", bool(v))
        )
        foot.addWidget(self.cb_startup)

        foot.addStretch(1)
        self.lbl_dots = QLabel()
        self.lbl_dots.setStyleSheet("color: #8ab4f8; font-size: 10pt; letter-spacing: 2px;")
        foot.addWidget(self.lbl_dots)
        foot.addStretch(1)

        self.btn_prev = QPushButton("←")
        self.btn_prev.setFixedWidth(34)
        self.btn_prev.clicked.connect(self._prev)
        foot.addWidget(self.btn_prev)

        self.btn_next = QPushButton()
        self.btn_next.setObjectName("primaryBtn")
        self.btn_next.clicked.connect(self._next)
        foot.addWidget(self.btn_next)
        lay.addLayout(foot)

        main_win.cmb_lang.currentIndexChanged.connect(self._on_language_changed)

    def _on_language_changed(self):
        if self.isVisible():
            self._refresh()

    def start_tour(self):
        self.idx = 0
        self.setGeometry(self.main_win.rect())
        self.show()
        self.raise_()
        self.setFocus()
        self._refresh()

    def close_tour(self):
        self.hide()

    def _target_rect(self) -> QRectF:
        target = self.STEPS[self.idx]["target"]
        mw = self.main_win
        w = None
        if target == "canvas_center":
            cv = mw.canvas
            tl = cv.mapTo(mw, cv.rect().topLeft())
            # Fokus-Rechteck rund um das Wappen in der Mitte der Leinwand
            cx = tl.x() + cv.width() * 0.5
            cy = tl.y() + cv.height() * 0.5
            r = min(cv.width(), cv.height()) * 0.36
            return QRectF(cx - r, cy - r, r * 2, r * 2)
        elif target == "ctx_bar":
            w = getattr(mw, "ctx_bar", None)
        elif target == "top_toolbar":
            w = getattr(mw, "top_toolbar", None)
        elif target == "left_rail":
            w = getattr(mw, "left_rail", None)
        elif target == "left_dock":
            w = getattr(mw, "left_dock", None)
        elif target == "right_dock":
            w = getattr(mw, "right_dock", None)
        elif target == "bottom_bar":
            w = getattr(mw, "bottom_dock", None)

        if w is not None and w.isVisible():
            tl = w.mapTo(mw, w.rect().topLeft())
            return QRectF(tl.x(), tl.y(), w.width(), w.height()).adjusted(2, 2, -2, -2)
        return QRectF(mw.width() * 0.3, mw.height() * 0.3, 300, 200)

    def _refresh(self):
        self.setGeometry(self.main_win.rect())
        st = self.STEPS[self.idx]
        self.btn_close.setToolTip(tr("tour_close_tip"))
        self.cb_startup.setText(tr("tour_on_start"))
        self.btn_prev.setToolTip(tr("tour_prev_tip"))
        self.lbl_badge.setText(tr(st["badge"]))
        self.lbl_title.setText(tr(st["title"]))
        self.lbl_body.setText(tr(st["body"]))

        if st["action_label"]:
            self.btn_try.setText(tr(st["action_label"]))
            self.btn_try.show()
        else:
            self.btn_try.hide()

        dots = ["●" if i == self.idx else "○" for i in range(len(self.STEPS))]
        self.lbl_dots.setText(" ".join(dots))

        self.btn_prev.setEnabled(self.idx > 0)
        self.btn_next.setText(tr("tour_done") if self.idx == len(self.STEPS) - 1 else tr("tour_next"))

        self.card.adjustSize()
        spot = self._target_rect()
        cw, ch = self.card.width(), self.card.sizeHint().height()
        self.card.setFixedHeight(ch)

        place = st["place"]
        gap = 22
        if place == "below":
            cx = max(20, min(self.width() - cw - 20, spot.center().x() - cw * 0.5))
            cy = spot.bottom() + gap
        elif place == "above":
            cx = max(20, min(self.width() - cw - 20, spot.center().x() - cw * 0.5))
            cy = max(60, spot.top() - ch - gap)
        elif place == "right":
            cx = min(self.width() - cw - 20, spot.right() + gap)
            cy = max(60, min(self.height() - ch - 30, spot.center().y() - ch * 0.5))
        elif place == "left":
            cx = max(20, spot.left() - cw - gap)
            cy = max(60, min(self.height() - ch - 30, spot.center().y() - ch * 0.5))
        else:
            cx = (self.width() - cw) * 0.5
            cy = (self.height() - ch) * 0.5

        self.card.move(int(cx), int(cy))
        self.update()

    def _prev(self):
        if self.idx > 0:
            self.idx -= 1
            self._refresh()

    def _next(self):
        if self.idx < len(self.STEPS) - 1:
            self.idx += 1
            self._refresh()
        else:
            self.close_tour()

    def _on_try_action(self):
        key = self.STEPS[self.idx].get("action_key")
        mw = self.main_win
        if key == "cycle_fabric":
            mw.cycle_fabric_theme()
            self.update()
        elif key == "fit":
            mw.action_fit_to_hoop()
            self.update()
        elif key == "auto_digitize":
            self.close_tour()
            mw.action_auto_digitize()
        elif key == "nodes_tool":
            mw._set_tool("edit_nodes")
            self.update()
        elif key == "play_sim":
            mw.btn_play.setChecked(not mw.btn_play.isChecked())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_tour()
        elif event.key() in (Qt.Key_Right, Qt.Key_Return, Qt.Key_Space):
            self._next()
        elif event.key() == Qt.Key_Left:
            self._prev()

    def mousePressEvent(self, event):
        # Klick ins Spotlight-Feld erlaubt direkte Bedienung oder Weiterklicken
        if not self.card.geometry().contains(event.position().toPoint()):
            spot = self._target_rect()
            if spot.contains(event.position()):
                self.close_tour()

    def paintEvent(self, _ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        spot = self._target_rect()
        outer = QPainterPath()
        outer.addRect(QRectF(self.rect()))
        hole = QPainterPath()
        hole.addRoundedRect(spot, 12, 12)
        scrim = outer.subtracted(hole)

        # Sanfte Abdunkelung rund um das hervorgehobene UI-Element
        p.fillPath(scrim, QColor(16, 19, 25, 130))

        # Weicher Google-Blau Spotlight-Schein & Rahmen um das Ziel-Widget
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(138, 180, 248, 65), 6))
        p.drawRoundedRect(spot.adjusted(-2, -2, 2, 2), 14, 14)
        p.setPen(QPen(QColor(138, 180, 248, 230), 2))
        p.drawRoundedRect(spot, 12, 12)

        # Verbindungslinie (Pointer) zwischen Spotlight und Popup-Karte
        crect = QRectF(self.card.geometry())
        place = self.STEPS[self.idx]["place"]
        if place == "below":
            p0 = QPointF(crect.center().x(), spot.bottom())
            p1 = QPointF(crect.center().x(), crect.top())
        elif place == "above":
            p0 = QPointF(crect.center().x(), spot.top())
            p1 = QPointF(crect.center().x(), crect.bottom())
        elif place == "right":
            p0 = QPointF(spot.right(), crect.center().y())
            p1 = QPointF(crect.left(), crect.center().y())
        else:
            p0 = QPointF(spot.left(), crect.center().y())
            p1 = QPointF(crect.right(), crect.center().y())

        p.setPen(QPen(QColor(138, 180, 248, 220), 2, Qt.DashLine))
        p.drawLine(p0, p1)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(138, 180, 248))
        p.drawEllipse(p0, 4.5, 4.5)
        p.end()

