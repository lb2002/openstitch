"""Google-Material-3 Vektor-Icons, offizielles OpenStitch-Starter-Logo & Interaktiver Studio-Rundgang."""
from __future__ import annotations

import math
from PySide6.QtCore import QPointF, QRectF, QSettings, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from shapely.geometry import LineString, Point, Polygon

from ..core.design import Design, FillObject, HOOPS, RunObject, SatinObject
from ..core.stitchplan import Thread
from ..text import TextObject


# ===========================================================================
# 1. Kristallklare Vektor-Icons (Google Material 3 Stil, kein Emoji-Clipping)
# ===========================================================================
def studio_icon(kind: str, size: int = 18) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    c_blue = QColor("#8ab4f8")
    c_gold = QColor("#fdd663")
    c_green = QColor("#81c995")
    c_red = QColor("#f28b82")
    c_purple = QColor("#c58af9")
    c_cyan = QColor("#78d9ec")
    c_light = QColor("#e8eaed")

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
            name="Wappen-Schild (Ziegel)",
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
            Thread.from_hex("#4285F4", "Studio Blau", "035", "OpenStitch"),
            name="Wappen-Satinrand",
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
            name="Goldene Fadenwelle",
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
            Thread.from_hex("#EA4335", "Korallenrot", "042", "OpenStitch"),
            name="Korallen-Fadenschlaufe",
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
            Thread.from_hex("#34A853", "Smaragd", "058", "OpenStitch"),
            name="Präzisions-Nadel",
            geom=needle_geom,
            spacing=0.36,
            pull_comp=0.16,
        )
    )

    # 6. Markenschriftzug „OPENSTITCH“ in Reinweiss (#FFFFFF)
    d.objects.append(
        TextObject(
            Thread.from_hex("#FFFFFF", "Reinweiss", "001", "OpenStitch"),
            name='Schriftzug „OPENSTITCH“',
            text="OPENSTITCH",
            height=5.6,
            letter_spacing=0.45,
            transform=(1.0, 0.0, 0.0, 1.0, 0.0, 13.0),
        )
    )

    return d


# ===========================================================================
# 3. Interaktiver Studio-Rundgang (Google-Material-3 Onboarding-Tour)
# ===========================================================================
class _TourHeroBanner(QWidget):
    """Vektor-illustrierter Header für jeden Schritt des Studio-Rundgangs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(145)
        self.step_index = 0

    def set_step(self, idx: int):
        self.step_index = idx
        self.update()

    def paintEvent(self, _ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = float(self.width()), float(self.height())

        # Edler Google-AI-Studio Verlaufshintergrund
        grad = QLinearGradient(0, 0, w, h)
        palettes = [
            (QColor("#16233b"), QColor("#1f3763"), QColor("#4285F4")),
            (QColor("#142b29"), QColor("#1b433d"), QColor("#34A853")),
            (QColor("#2c2214"), QColor("#463316"), QColor("#FBBC04")),
            (QColor("#261a38"), QColor("#3c255c"), QColor("#c58af9")),
            (QColor("#2d1a1e"), QColor("#4a2229"), QColor("#EA4335")),
        ]
        c0, c1, accent = palettes[self.step_index % len(palettes)]
        grad.setColorAt(0.0, c0)
        grad.setColorAt(1.0, c1)

        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), 12, 12)
        p.fillPath(path, grad)

        # Dekoratives Millimeter-Grid im Hintergrund
        p.setPen(QPen(QColor(255, 255, 255, 16), 1))
        for x in range(24, int(w), 24):
            p.drawLine(x, 0, x, int(h))
        for y in range(24, int(h), 24):
            p.drawLine(0, y, int(w), y)

        # Schritt-spezifische Vektor-Grafik in der Mitte
        cx, cy = w * 0.5, h * 0.52
        p.setPen(QPen(accent, 2.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 42))

        if self.step_index == 0:
            # OpenStitch Hexagon + Fadenwelle
            pts = [
                QPointF(cx + 42 * math.cos(math.radians(i * 60 - 30)),
                        cy + 42 * math.sin(math.radians(i * 60 - 30)))
                for i in range(6)
            ]
            p.drawPolygon(QPolygonF(pts))
            p.setPen(QPen(QColor("#FBBC04"), 3.0, Qt.SolidLine, Qt.RoundCap))
            wave = QPainterPath()
            wave.moveTo(cx - 28, cy + 4)
            wave.cubicTo(QPointF(cx - 10, cy - 22), QPointF(cx + 10, cy + 28), QPointF(cx + 28, cy - 4))
            p.drawPath(wave)
        elif self.step_index == 1:
            # Stickrahmen + Cap Center-Out Pfeile
            p.drawEllipse(QPointF(cx, cy), 42, 42)
            p.setPen(QPen(QColor("#81c995"), 1.6, Qt.DashLine))
            p.drawEllipse(QPointF(cx, cy), 34, 34)
            p.setPen(QPen(QColor("#ffffff"), 2.0))
            p.drawLine(QPointF(cx, cy + 16), QPointF(cx, cy - 18))
            p.drawLine(QPointF(cx, cy + 4), QPointF(cx - 20, cy + 4))
            p.drawLine(QPointF(cx, cy + 4), QPointF(cx + 20, cy + 4))
        elif self.step_index == 2:
            # Bild -> Funken -> Stickerei
            p.drawRoundedRect(QRectF(cx - 65, cy - 28, 52, 56), 6, 6)
            p.setPen(QPen(QColor("#FBBC04"), 2.4))
            p.drawLine(QPointF(cx - 6, cy), QPointF(cx + 8, cy))
            p.drawRoundedRect(QRectF(cx + 16, cy - 28, 52, 56), 6, 6)
            for ry in range(-18, 22, 8):
                p.drawLine(QPointF(cx + 24, cy + ry), QPointF(cx + 60, cy + ry))
        elif self.step_index == 3:
            # Bezier-Knoten & Stichwinkel-Achse
            p.drawRoundedRect(QRectF(cx - 48, cy - 30, 96, 60), 10, 10)
            p.setPen(QPen(QColor("#FBBC04"), 2.2, Qt.DashLine))
            p.drawLine(QPointF(cx - 32, cy + 16), QPointF(cx + 32, cy - 16))
            p.setBrush(QColor("#ffffff"))
            p.drawEllipse(QPointF(cx - 32, cy + 16), 5, 5)
            p.drawEllipse(QPointF(cx + 32, cy - 16), 5, 5)
        else:
            # Qualitäts-Doktor Schild + Haken
            p.drawEllipse(QPointF(cx, cy), 40, 40)
            p.setPen(QPen(QColor("#81c995"), 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(QPointF(cx - 16, cy + 2), QPointF(cx - 4, cy + 15))
            p.drawLine(QPointF(cx - 4, cy + 15), QPointF(cx + 18, cy - 12))

        p.end()


class OnboardingTourDialog(QDialog):
    """Interaktiver 5-Schritte-Rundgang im Google-Studio-Look."""

    STEPS = [
        {
            "badge": "WILLKOMMEN · ÜBERBLICK",
            "title": "Willkommen bei OpenStitch Studio",
            "body": (
                "<b>OpenStitch</b> ist deine universelle, herstellerneutrale Open-Source-Suite für "
                "professionelles Digitalisieren und Sticken.<br><br>"
                "• <b>Universell kompatibel:</b> Unterstützt <b>Tajima (.DST)</b>, <b>Brother (.PES)</b>, "
                "<b>Melco/Bernina (.EXP)</b>, <b>Janome (.JEF)</b>, <b>Pfaff/Husqvarna (.VP3)</b> & <b>Barudan (.U01)</b>.<br>"
                "• <b>Starter-Design auf der Leinwand:</b> Wir haben für dich direkt das offizielle "
                "<b>OpenStitch-Wappen</b> geladen – klicke einzelne Elemente an, um sie live anzupassen!"
            ),
            "action_label": None,
            "action_key": None,
        },
        {
            "badge": "SCHRITT 1 VON 4 · OBEN RECHTS",
            "title": "Maschine & Intelligenter Stickrahmen",
            "body": (
                "Oben rechts in der Studio-Leiste wählst du deine <b>Maschine</b> und deinen <b>Stickrahmen</b>:<br><br>"
                "• <b>Automatische Rahmen-Physik:</b> Grosse Rahmen (18–30 cm) federn in der Mitte stärker "
                "(<i>Trampolin-Effekt</i>). OpenStitch verstärkt dort automatisch die Unterlage und Zugkompensation.<br>"
                "• <b>Kappen-Modus (Cap):</b> Sortiert Objekte automatisch <i>Center-Out & Bottom-Up</i> "
                "(vom Schirm nach oben und von der Mittelnaht nach aussen), damit sich auf Caps keine Falten bilden."
            ),
            "action_label": "⛶ Design jetzt optimal in Rahmen einpassen (Auto-Fit)",
            "action_key": "fit",
        },
        {
            "badge": "SCHRITT 2 VON 4 · OBEN MITTE",
            "title": "In Sekunden vom Bild oder Vektor zur Stickdatei",
            "body": (
                "Drei leistungsstarke Assistenten nehmen dir die Vorarbeit ab:<br><br>"
                "• <b>✨ Auto-Digitizer (Ctrl+D):</b> Entfernt den Bildhintergrund automatisch, trennt Farben per "
                "CIE-Lab und erzeugt saubere Tatami- & Satin-Objekte mit 0.7 mm Überlappung gegen Stoffblitzer.<br>"
                "• <b>🖼 PhotoStitch (Ctrl+P):</b> Verwandelt Porträtfotos in monochrome oder 4-farbige CMYK-Wellenstickerei.<br>"
                "• <b>✒ SVG & 🔤 Schrift (Ctrl+T):</b> Importiert Vektor-Logos oder setzt TrueType-Schriften auf Bogen."
            ),
            "action_label": "✨ Auto-Digitizer jetzt öffnen …",
            "action_key": "auto_digitize",
        },
        {
            "badge": "SCHRITT 3 VON 4 · LINKS & RECHTS",
            "title": "Profi-Werkzeuge, Knoten-Editor & Live-Inspektor",
            "body": (
                "Du hast jederzeit die volle manuelle Kontrolle:<br><br>"
                "• <b>Linke Werkzeugleiste:</b> Zeichne eigene <b>Tatami-Flächen (F)</b>, <b>Satin-Säulen (S)</b> oder "
                "<b>Steppstiche (R)</b>. Mit <b>Knoten (N)</b> ziehst du Konturpunkte und die gelbe Stichwinkel-Achse live.<br>"
                "• <b>Rechter Objekt-Inspektor:</b> Ändere Dichte, Muster (z. B. <i>Kontur-Fill</i>), Zugkompensation oder "
                "aktiviere den <b>3D-Puff-Schaumstoff-Modus</b> für erhabene 3D-Caps – alles berechnet sich sofort neu!"
            ),
            "action_label": "❖ Knoten- & Stichwinkel-Editor (Taste N) aktivieren",
            "action_key": "nodes_tool",
        },
        {
            "badge": "SCHRITT 4 VON 4 · PRÜFUNG & EXPORT",
            "title": "Qualitäts-Doktor (F7), Simulator & Export",
            "body": (
                "Bevor die Maschine startet, sorgt OpenStitch für maximale Produktionssicherheit:<br><br>"
                "• <b>🩺 Qualitäts-Doktor (F7):</b> Prüft dein Design auf Fadenriss-Risiken, Nadelbruch-Stellen "
                "(&gt;18 Stiche/mm²), Rahmen-Überschreitung und Nadelanzahl.<br>"
                "• <b>▶ Näh-Simulator (Unten):</b> Spiele den Stickverlauf Stich für Stich vor.<br>"
                "• <b>💾 Export (Ctrl+E) & 📄 PDF:</b> Exportiere für deine Maschine + drucke das A4-Produktionsblatt."
            ),
            "action_label": "🩺 Qualitäts-Doktor (F7) für das aktuelle Logo ausführen",
            "action_key": "doctor",
        },
    ]

    def __init__(self, main_win, parent=None):
        super().__init__(parent or main_win)
        self.main_win = main_win
        self.idx = 0
        self.setWindowTitle("OpenStitch Studio  —  Interaktiver Rundgang")
        self.setMinimumWidth(560)
        self.setMaximumWidth(600)
        self.setModal(False)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 18)
        lay.setSpacing(14)

        self.hero = _TourHeroBanner(self)
        lay.addWidget(self.hero)

        self.lbl_badge = QLabel()
        self.lbl_badge.setStyleSheet(
            "color: #8ab4f8; font-size: 8.5pt; font-weight: 700; letter-spacing: 1.1px;"
        )
        lay.addWidget(self.lbl_badge)

        self.lbl_title = QLabel()
        f = QFont("Segoe UI", 14, QFont.Bold)
        self.lbl_title.setFont(f)
        self.lbl_title.setStyleSheet("color: #f8f9fa;")
        lay.addWidget(self.lbl_title)

        card = QFrame()
        card.setObjectName("card")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(14, 12, 14, 12)
        self.lbl_body = QLabel()
        self.lbl_body.setWordWrap(True)
        self.lbl_body.setStyleSheet("color: #d2d8e6; font-size: 10pt; line-height: 1.45;")
        cv.addWidget(self.lbl_body)

        self.btn_try = QPushButton()
        self.btn_try.setCursor(Qt.PointingHandCursor)
        self.btn_try.setStyleSheet(
            "QPushButton { background-color: rgba(138, 180, 248, 0.14); border: 1px solid #4c8df6; "
            "color: #8ab4f8; font-weight: 600; padding: 7px 12px; border-radius: 7px; margin-top: 6px; }"
            "QPushButton:hover { background-color: rgba(138, 180, 248, 0.26); color: #ffffff; }"
        )
        self.btn_try.clicked.connect(self._on_try_action)
        cv.addWidget(self.btn_try)
        lay.addWidget(card)

        # Fusszeile mit Schritt-Punkten, Checkbox & Navigation
        foot = QHBoxLayout()
        self.cb_startup = QCheckBox("Beim Start zeigen")
        settings = QSettings("OpenStitch", "OpenStitchStudio")
        self.cb_startup.setChecked(settings.value("show_tour_on_startup", True, type=bool))
        self.cb_startup.toggled.connect(
            lambda v: QSettings("OpenStitch", "OpenStitchStudio").setValue("show_tour_on_startup", bool(v))
        )
        foot.addWidget(self.cb_startup)

        foot.addStretch(1)
        self.lbl_dots = QLabel()
        self.lbl_dots.setStyleSheet("color: #8ab4f8; font-size: 11pt; letter-spacing: 3px;")
        foot.addWidget(self.lbl_dots)
        foot.addStretch(1)

        self.btn_prev = QPushButton("← Zurück")
        self.btn_prev.clicked.connect(self._prev)
        foot.addWidget(self.btn_prev)

        self.btn_next = QPushButton("Weiter →")
        self.btn_next.setObjectName("primaryBtn")
        self.btn_next.clicked.connect(self._next)
        foot.addWidget(self.btn_next)

        lay.addLayout(foot)
        self._refresh()

    def _refresh(self):
        st = self.STEPS[self.idx]
        self.hero.set_step(self.idx)
        self.lbl_badge.setText(st["badge"])
        self.lbl_title.setText(st["title"])
        self.lbl_body.setText(st["body"])

        if st["action_label"]:
            self.btn_try.setText(st["action_label"])
            self.btn_try.show()
        else:
            self.btn_try.hide()

        dots = ["●" if i == self.idx else "○" for i in range(len(self.STEPS))]
        self.lbl_dots.setText(" ".join(dots))

        self.btn_prev.setEnabled(self.idx > 0)
        if self.idx == len(self.STEPS) - 1:
            self.btn_next.setText("Loslegen ✓")
        else:
            self.btn_next.setText("Weiter →")

    def _prev(self):
        if self.idx > 0:
            self.idx -= 1
            self._refresh()

    def _next(self):
        if self.idx < len(self.STEPS) - 1:
            self.idx += 1
            self._refresh()
        else:
            self.accept()

    def _on_try_action(self):
        key = self.STEPS[self.idx].get("action_key")
        if not self.main_win:
            return
        if key == "fit":
            self.main_win.action_fit_to_hoop()
        elif key == "auto_digitize":
            self.hide()
            self.main_win.action_auto_digitize()
        elif key == "nodes_tool":
            self.main_win._set_tool("edit_nodes")
        elif key == "doctor":
            self.main_win.action_quality_doctor()


# ===========================================================================
# 4. In-App Spotlight & Coach-Mark Popups (Direkt im Hauptfenster!)
# ===========================================================================
class InAppTourOverlay(QWidget):
    """Interaktives Spotlight-Overlay mit schwebenden Coach-Mark-Popups direkt über den UI-Bereichen."""

    STEPS = [
        {
            "target": "canvas_center",
            "place": "right",
            "badge": "WILLKOMMEN · 1 / 7",
            "title": "3D-Stickleinwand & OpenStitch-Wappen",
            "body": (
                "Hier in der Mitte siehst du unser offizielles <b>OpenStitch-Wappen</b> im Stickrahmen.<br><br>"
                "• <b>Klicken & Ziehen:</b> Objekte direkt auswählen, verschieben oder am Eckgriff skalieren.<br>"
                "• <b>Mausrad:</b> Stufenlos bis auf einzelne Einstiche hineinzoomen."
            ),
            "action_label": "🎨 Stofffarbe im Rahmen testen (Dunkel / Sand / Hell)",
            "action_key": "cycle_fabric",
        },
        {
            "target": "ctx_bar",
            "place": "below",
            "badge": "KONTEXTLEISTE · 2 / 7",
            "title": "Maschine, Stickrahmen & Rahmen-Physik",
            "body": (
                "Direkt über der Leinwand wählst du deine <b>Maschine</b> (Universal, Tajima, Brother, Barudan, Melco …) "
                "und den <b>Stickrahmen</b>:<br><br>"
                "• <b>Intelligente Strategie:</b> Je nach Rahmengrösse (z. B. <i>Anti-Trampolin</i> bei grossen Rahmen "
                "oder <i>Center-Out & Bottom-Up</i> bei Caps) passt OpenStitch Unterlage & Zugkompensation automatisch an!"
            ),
            "action_label": "⛶ Design optimal in den Rahmen einpassen (Auto-Fit)",
            "action_key": "fit",
        },
        {
            "target": "top_toolbar",
            "place": "below",
            "badge": "STUDIO-LEISTE · 3 / 7",
            "title": "Auto-Digitizer, PhotoStitch, SVG & Doktor",
            "body": (
                "Oben findest du alle Kreativ-Assistenten und Prüfwerkzeuge:<br><br>"
                "• <b>Auto-Digitizer (Ctrl+D):</b> Bild hochladen → automatische Hintergrund-Freistellung & Stickflächen.<br>"
                "• <b>PhotoStitch (Ctrl+P):</b> Porträtfotos als Wellen-/CMYK-Stickerei.<br>"
                "• <b>Doktor (F7):</b> Prüft dein Design vorab auf Fadenriss- & Nadelbruch-Risiken."
            ),
            "action_label": "✨ Auto-Digitizer direkt öffnen …",
            "action_key": "auto_digitize",
        },
        {
            "target": "left_rail",
            "place": "right",
            "badge": "WERKZEUGE · 4 / 7",
            "title": "Manuelles Zeichnen & Stichwinkel-Knoten (N)",
            "body": (
                "In der vertikalen Werkzeugleiste links wechselst du den Bearbeitungsmodus:<br><br>"
                "• <b>Tatami (F) / Satin (S) / Stepp (R):</b> Eigene Formen frei auf der Leinwand zeichnen.<br>"
                "• <b>Knoten (N):</b> Konturpunkte einzeln verschieben und an der <b>gelben Achse</b> den Stichwinkel live drehen!"
            ),
            "action_label": "❖ Knoten- && Stichwinkel-Editor (N) jetzt einschalten",
            "action_key": "nodes_tool",
        },
        {
            "target": "left_dock",
            "place": "right",
            "badge": "GARNFARBEN · 5 / 7",
            "title": "Farbpalette & Nadel-Sequenz",
            "body": (
                "Links wählst du mit einem Klick aus <b>49 Industriepaletten-Farben</b> oder einem eigenen RGB-Ton.<br><br>"
                "• Darunter siehst du live die <b>Nadel- & Farbwechsel-Sequenz</b> deiner Maschine inklusive Stichanzahl pro Farbe."
            ),
            "action_label": None,
            "action_key": None,
        },
        {
            "target": "right_dock",
            "place": "left",
            "badge": "INSPEKTOR · 6 / 7",
            "title": "Ebenen & Live-Objekt-Parameter",
            "body": (
                "Rechts steuerst du die <b>Stickreihenfolge</b> und stellst im <b>Objekt-Inspektor</b> "
                "Reihenabstand, Muster (z. B. <i>Kontur-Fill</i>), Zugkompensation oder <b>3D-Puff-Schaumstoff</b> ein.<br><br>"
                "• Jede Änderung berechnet die Stiche <b>sofort live</b> auf der Leinwand neu!"
            ),
            "action_label": None,
            "action_key": None,
        },
        {
            "target": "bottom_bar",
            "place": "above",
            "badge": "SIMULATOR & PRODUKTION · 7 / 7",
            "title": "Stich-Simulator & Echtzeit-Kinematik",
            "body": (
                "Unten spielst du den kompletten Nähvorgang <b>Stich für Stich</b> im Simulator vor.<br><br>"
                "• In der Statusleiste ganz unten siehst du live die <b>effektive Maschinengeschwindigkeit (SPM)</b>, "
                "Spitzendichte (St./mm²), Trims und die reale Produktionslaufzeit!"
            ),
            "action_label": "▶ Näh-Simulation unten starten / stoppen",
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
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setToolTip("Rundgang schliessen (Esc)")
        btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #9aa4b8; font-size: 10pt; padding: 0; }"
            "QPushButton:hover { color: #ffffff; background-color: #343b4a; border-radius: 12px; }"
        )
        btn_close.clicked.connect(self.close_tour)
        top_row.addWidget(btn_close)
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
        self.cb_startup = QCheckBox("Beim Start")
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
        self.btn_prev.setToolTip("Vorheriger Schritt")
        self.btn_prev.clicked.connect(self._prev)
        foot.addWidget(self.btn_prev)

        self.btn_next = QPushButton("Weiter →")
        self.btn_next.setObjectName("primaryBtn")
        self.btn_next.clicked.connect(self._next)
        foot.addWidget(self.btn_next)
        lay.addLayout(foot)

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
        self.lbl_badge.setText(st["badge"])
        self.lbl_title.setText(st["title"])
        self.lbl_body.setText(st["body"])

        if st["action_label"]:
            self.btn_try.setText(st["action_label"])
            self.btn_try.show()
        else:
            self.btn_try.hide()

        dots = ["●" if i == self.idx else "○" for i in range(len(self.STEPS))]
        self.lbl_dots.setText(" ".join(dots))

        self.btn_prev.setEnabled(self.idx > 0)
        self.btn_next.setText("Fertig ✓" if self.idx == len(self.STEPS) - 1 else "Weiter →")

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

