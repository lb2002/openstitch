"""Sofortiger Splash-Screen & schneller Startpunkt für OpenStitch."""
from __future__ import annotations

import sys

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from . import APP_NAME, __version__


def _create_splash_pixmap() -> QPixmap:
    w, h = 560, 320
    pix = QPixmap(w, h)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)

    # Hintergrund mit abgerundeten Ecken & feinem Farbverlauf
    grad = QLinearGradient(0, 0, w, h)
    grad.setColorAt(0.0, QColor(24, 28, 38))
    grad.setColorAt(1.0, QColor(38, 45, 62))
    p.setBrush(grad)
    p.setPen(QPen(QColor(85, 130, 235), 2))
    p.drawRoundedRect(QRectF(2, 2, w - 4, h - 4), 18, 18)

    # Gesticktes Logo-Emblem links (stilisierter Stickrahmen + Nadel + Goldkranz)
    cx, cy = 115, 150
    p.setPen(QPen(QColor(232, 163, 23), 5, Qt.DashLine, Qt.RoundCap))
    p.setBrush(QColor(20, 36, 77))
    p.drawEllipse(QRectF(cx - 64, cy - 64, 128, 128))
    p.setPen(QPen(QColor(95, 155, 255), 2.5))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QRectF(cx - 52, cy - 52, 104, 104))

    # Nadel-Ikone im Emblem
    p.setPen(QPen(QColor(240, 244, 255), 3.2, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(cx - 22, cy - 34, cx + 22, cy + 34)
    p.setPen(QPen(QColor(238, 58, 50), 3.0, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(QRectF(cx - 38, cy - 12, 76, 44), 0, -180 * 16)

    # Titel & Untertitel rechts
    p.setPen(QColor(245, 247, 252))
    p.setFont(QFont("Segoe UI", 28, QFont.Bold))
    p.drawText(210, 118, APP_NAME)

    p.setPen(QColor(232, 163, 23))
    p.setFont(QFont("Segoe UI", 11, QFont.Bold))
    p.drawText(212, 148, f"Studio {__version__}  ·  Universal Open-Source Embroidery Suite")

    p.setPen(QColor(175, 185, 205))
    p.setFont(QFont("Segoe UI", 9))
    p.drawText(212, 182, "Auto-Digitizer · 3D-Satin/Tatami · PhotoStitch · Appliqué")
    p.drawText(212, 202, "Tajima · Brother · Barudan · Melco · Bernina · Janome · Ricoma")

    p.end()
    return pix


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # 1. Splash-Screen SOFORT (< 150 ms) zeigen, bevor schwere Module geladen werden!
    splash = QSplashScreen(_create_splash_pixmap(), Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.show()
    splash.showMessage(
        "  Lade Geometrie- & Stich-Engine …",
        Qt.AlignBottom | Qt.AlignLeft,
        QColor(140, 185, 255),
    )
    app.processEvents()

    # 2. Erst jetzt die Hauptmodule importieren
    from .ui.crash import install as install_crash_handler
    from .ui.main_window import MainWindow

    splash.showMessage(
        "  Initialisiere Studio-Leinwand & Digitalisierungs-Werkzeuge …",
        Qt.AlignBottom | Qt.AlignLeft,
        QColor(140, 185, 255),
    )
    app.processEvents()

    win = MainWindow(defer_starter=True)
    install_crash_handler(win)
    win.show()
    app.processEvents()

    def _finish_startup():
        win.startup()
        splash.finish(win)
        win.setWindowState((win.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        win.raise_()
        win.activateWindow()

    QTimer.singleShot(50, _finish_startup)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
