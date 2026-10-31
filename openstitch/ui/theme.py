"""Farbtöne und Stylesheet (Material 3, dunkel und hell) an einer Stelle.

Widgets setzen keine Farben selbst, sondern eine Rolle: ``label.setProperty("role", "caption")``."""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QSettings, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class Theme:
    id: str
    window: str
    surface: str
    surface_high: str
    surface_top: str
    outline: str
    outline_soft: str
    text: str
    text_dim: str
    text_faint: str
    accent: str
    on_accent: str
    accent_fill: str
    accent_soft: str
    ok: str
    warn: str
    err: str
    canvas: str
    hud_bg: str
    hud_text: str
    # Akzentfarben der Symbole
    icon_light: str
    icon_blue: str
    icon_gold: str
    icon_green: str
    icon_red: str
    icon_purple: str
    icon_cyan: str


DARK = Theme(
    id="dark", window="#14171c", surface="#1b1f26", surface_high="#232833", surface_top="#2c323e",
    outline="#3a4250", outline_soft="#2a303b", text="#e6e9ef", text_dim="#a6afbe", text_faint="#7b8493",
    accent="#8ab4f8", on_accent="#0b1d3a", accent_fill="#4f86ee", accent_soft="rgba(138, 180, 248, 0.16)",
    ok="#7fd19b", warn="#f2c14e", err="#f28b82", canvas="#1a1d23",
    hud_bg="rgba(38, 43, 54, 0.85)", hud_text="#bac3d4",
    icon_light="#e8eaed", icon_blue="#8ab4f8", icon_gold="#fdd663", icon_green="#81c995",
    icon_red="#f28b82", icon_purple="#c58af9", icon_cyan="#78d9ec",
)

LIGHT = Theme(
    id="light", window="#eef0f4", surface="#ffffff", surface_high="#f4f5f8", surface_top="#e8ebf0",
    outline="#cdd3dc", outline_soft="#e1e4ea", text="#1c2028", text_dim="#4f5866", text_faint="#79828f",
    accent="#1a5fd0", on_accent="#ffffff", accent_fill="#1a5fd0", accent_soft="rgba(26, 95, 208, 0.12)",
    ok="#1e8e4e", warn="#a86f00", err="#c5362c", canvas="#dfe2e8",
    hud_bg="rgba(255, 255, 255, 0.88)", hud_text="#3d4552",
    icon_light="#3a4250", icon_blue="#1a5fd0", icon_gold="#b27a00", icon_green="#1e8e4e",
    icon_red="#c5362c", icon_purple="#7b3fc4", icon_cyan="#00798c",
)

_THEMES = {"dark": DARK, "light": LIGHT}
_current = [DARK]


def current() -> Theme:
    return _current[0]


def color(name: str) -> QColor:
    """Farbton als QColor (auch die rgba(...)-Werte)."""
    v = getattr(current(), name)
    if v.startswith("rgba("):
        r, g, b, a = (float(x) for x in v[5:-1].split(","))
        return QColor(int(r), int(g), int(b), int(a * 255))
    return QColor(v)


def _glyph(kind: str, col: str) -> str:
    """Kleine Pfeile und Haken als PNG: Stylesheets können Unterelemente nur aus Dateien zeichnen."""
    folder = os.path.join(tempfile.gettempdir(), "openstitch-ui")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{kind}-{col.strip('#')}.png")
    if not os.path.isfile(path):
        s = 28                      # doppelte Grösse: bleibt auf HiDPI-Bildschirmen scharf
        img = QImage(s, s, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(QPen(QColor(col), 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        pts = {"down": ((7, 10), (14, 18), (21, 10)), "up": ((7, 18), (14, 10), (21, 18)),
               "check": ((6, 15), (12, 21), (22, 8))}[kind]
        p.drawPolyline(QPolygonF([QPointF(*q) for q in pts]))
        p.end()
        img.save(path)
    return path.replace("\\", "/")


def stylesheet(t: Theme | None = None) -> str:
    t = t or current()
    down, up = _glyph("down", t.text_dim), _glyph("up", t.text_dim)
    check = _glyph("check", "#ffffff")
    return f"""
QMainWindow, QDialog, QDockWidget, QWidget {{
    background-color: {t.window};
    color: {t.text};
    font-family: "Segoe UI Variable Text", "Segoe UI", "SF Pro Text", "Cantarell", "Noto Sans", sans-serif;
    font-size: 9.5pt;
}}
QLabel, QCheckBox, QRadioButton {{ background: transparent; }}
QToolTip {{
    background-color: {t.surface_top};
    color: {t.text};
    border: 1px solid {t.outline};
    padding: 4px 6px;
}}
QMenuBar {{
    background-color: {t.surface};
    color: {t.text_dim};
    border-bottom: 1px solid {t.outline_soft};
    padding: 2px 6px;
}}
QMenuBar::item {{ background: transparent; padding: 4px 9px; border-radius: 6px; }}
QMenuBar::item:selected {{ background-color: {t.surface_top}; color: {t.text}; }}
QMenu {{
    background-color: {t.surface_high};
    border: 1px solid {t.outline};
    border-radius: 8px;
    padding: 5px;
}}
QMenu::item {{ padding: 6px 26px 6px 12px; border-radius: 6px; }}
QMenu::item:selected {{ background-color: {t.accent_soft}; color: {t.text}; }}
QMenu::separator {{ height: 1px; background: {t.outline_soft}; margin: 5px 8px; }}
QToolBar {{
    background-color: {t.surface};
    border: none;
    border-bottom: 1px solid {t.outline_soft};
    spacing: 3px;
    padding: 5px 8px;
}}
QToolBar#rail {{ border-bottom: none; border-right: 1px solid {t.outline_soft}; padding: 8px 6px; spacing: 4px; }}
QToolBar::separator {{ background: {t.outline_soft}; width: 1px; height: 1px; margin: 4px 6px; }}
QToolButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 5px 9px;
    color: {t.text};
}}
QToolBar#rail QToolButton {{ padding: 7px; }}
QToolButton:hover {{ background-color: {t.surface_top}; }}
QToolButton:pressed {{ background-color: {t.outline}; }}
QToolButton:checked {{ background-color: {t.accent_soft}; color: {t.accent}; }}
QToolButton:disabled {{ color: {t.text_faint}; }}
QToolButton#accentTool {{ background-color: {t.accent_fill}; color: #ffffff; font-weight: 600; padding: 5px 14px; }}
QToolButton#accentTool:hover {{ background-color: {t.accent}; color: {t.on_accent}; }}
QPushButton {{
    background-color: {t.surface_high};
    border: 1px solid {t.outline};
    border-radius: 8px;
    padding: 6px 12px;
    color: {t.text};
}}
QPushButton:hover {{ background-color: {t.surface_top}; border-color: {t.accent}; }}
QPushButton:pressed {{ background-color: {t.outline}; }}
QPushButton:checked {{ background-color: {t.accent_soft}; border-color: {t.accent}; color: {t.accent}; }}
QPushButton:disabled {{ color: {t.text_faint}; border-color: {t.outline_soft}; }}
QPushButton:focus, QToolButton:focus, QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QListWidget:focus {{ border-color: {t.accent}; }}
QPushButton#primaryBtn {{
    background-color: {t.accent_fill};
    border: 1px solid {t.accent_fill};
    color: #ffffff;
    font-weight: 600;
}}
QPushButton#primaryBtn:hover {{ background-color: {t.accent}; border-color: {t.accent}; color: {t.on_accent}; }}
QDialogButtonBox QPushButton:default {{
    background-color: {t.accent_fill};
    border: 1px solid {t.accent_fill};
    color: #ffffff;
    font-weight: 600;
}}
QDialogButtonBox QPushButton:default:hover {{ background-color: {t.accent}; border-color: {t.accent}; color: {t.on_accent}; }}
QPushButton#iconBtn {{ padding: 5px; min-width: 22px; }}
QPushButton#startCard {{
    background-color: {t.surface};
    border: 1px solid {t.outline_soft};
    border-radius: 14px;
    padding: 16px;
    text-align: left;
    font-size: 10.5pt;
    font-weight: 600;
}}
QPushButton#startCard:hover {{ border-color: {t.accent}; background-color: {t.surface_high}; }}
QPushButton#linkBtn {{
    background: transparent;
    border: none;
    color: {t.accent};
    padding: 3px 2px;
    text-align: left;
}}
QPushButton#linkBtn:hover {{ text-decoration: underline; }}
QDockWidget {{ font-weight: 600; color: {t.text_dim}; }}
QDockWidget::title {{
    background-color: {t.surface};
    border-bottom: 1px solid {t.outline_soft};
    padding: 7px 12px;
    text-align: left;
}}
QMainWindow::separator {{ background: {t.outline_soft}; width: 1px; height: 1px; }}
QMainWindow::separator:hover {{ background: {t.accent}; }}
QSplitter::handle {{ background: {t.outline_soft}; height: 1px; }}
QFrame#card {{
    background-color: {t.surface};
    border: 1px solid {t.outline_soft};
    border-radius: 10px;
}}
QFrame#ctxBar, QFrame#simBar {{ background-color: {t.surface}; border: none; }}
QFrame#ctxBar {{ border-bottom: 1px solid {t.outline_soft}; }}
QFrame#simBar {{ border-top: 1px solid {t.outline_soft}; }}
QFrame#ctxBar QLabel, QFrame#simBar QLabel {{ background: transparent; }}
QWidget#startPage {{ background-color: {t.window}; }}
QListWidget, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background-color: {t.surface_high};
    border: 1px solid {t.outline_soft};
    border-radius: 8px;
    padding: 4px 8px;
    color: {t.text};
    selection-background-color: {t.accent_fill};
    selection-color: #ffffff;
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox::down-arrow {{ image: url({down}); width: 13px; height: 13px; }}
QSpinBox, QDoubleSpinBox {{ padding-left: 8px; padding-right: 18px; }}
QSpinBox::up-button, QDoubleSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background: transparent;
    border: none;
    width: 16px;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{ background: {t.surface_top}; border-radius: 4px; }}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{ image: url({up}); width: 11px; height: 11px; }}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{ image: url({down}); width: 11px; height: 11px; }}
QCheckBox {{ spacing: 7px; }}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {t.outline};
    border-radius: 5px;
    background: {t.surface_high};
}}
QCheckBox::indicator:hover {{ border-color: {t.accent}; }}
QCheckBox::indicator:checked {{ background: {t.accent_fill}; border-color: {t.accent_fill}; image: url({check}); }}
QComboBox QAbstractItemView {{
    background-color: {t.surface_high};
    border: 1px solid {t.outline};
    selection-background-color: {t.accent_soft};
    selection-color: {t.text};
}}
QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {{ border-color: {t.outline}; }}
QListWidget {{ padding: 3px; outline: none; }}
QListWidget::item {{ padding: 5px 6px; border-radius: 6px; margin: 1px; }}
QListWidget::item:selected {{ background-color: {t.accent_soft}; color: {t.text}; }}
QListWidget::item:hover:!selected {{ background-color: {t.surface_top}; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {t.outline}; min-height: 24px; border-radius: 4px; }}
QScrollBar::handle:vertical:hover {{ background: {t.text_faint}; }}
QScrollBar:horizontal {{ background: transparent; height: 8px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {t.outline}; min-width: 24px; border-radius: 4px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QSlider::groove:horizontal {{ height: 4px; background: {t.surface_top}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {t.accent}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: {t.accent};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QGroupBox {{
    background-color: {t.surface};
    border: 1px solid {t.outline_soft};
    border-radius: 10px;
    margin-top: 12px;
    padding: 12px 10px 8px 10px;
    font-weight: 600;
}}
QGroupBox QLabel, QGroupBox QCheckBox {{ font-weight: 400; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 4px; color: {t.text_dim}; }}
QProgressBar {{
    background: {t.surface_top};
    border: none;
    border-radius: 3px;
    max-height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{ background: {t.accent}; border-radius: 3px; }}
QTabBar::tab {{
    background: transparent;
    padding: 7px 14px;
    color: {t.text_dim};
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{ color: {t.accent}; border-bottom-color: {t.accent}; }}
QTabWidget::pane {{ border: none; }}
QStatusBar {{
    background-color: {t.surface};
    color: {t.text_dim};
    border-top: 1px solid {t.outline_soft};
    font-size: 9pt;
}}
QStatusBar::item {{ border: none; }}
QLabel[role="caption"] {{ color: {t.text_faint}; font-size: 8pt; }}
QLabel[role="section"] {{ color: {t.text_dim}; font-weight: 600; }}
QLabel[role="muted"] {{ color: {t.text_faint}; }}
QLabel[role="title"] {{ font-size: 19pt; font-weight: 600; }}
QLabel[role="subtitle"] {{ color: {t.text_dim}; font-size: 10.5pt; }}
QLabel[role="cardText"] {{ color: {t.text_dim}; font-size: 9pt; }}
QLabel[role="strong"] {{ font-weight: 600; }}
QLabel[severity="error"] {{ color: {t.err}; font-weight: 600; }}
QLabel[severity="warning"] {{ color: {t.warn}; font-weight: 600; }}
QLabel[severity="info"] {{ color: {t.text_dim}; font-weight: 600; }}
QLabel[severity="ok"] {{ color: {t.ok}; font-weight: 600; }}
"""


def init_theme() -> Theme:
    tid = QSettings("OpenStitch", "OpenStitchStudio").value("ui/theme", "dark", type=str)
    _current[0] = _THEMES.get(tid, DARK)
    return _current[0]


def set_theme(tid: str) -> Theme:
    _current[0] = _THEMES.get(tid, DARK)
    QSettings("OpenStitch", "OpenStitchStudio").setValue("ui/theme", _current[0].id)
    apply_to_app()
    return _current[0]


def apply_to_app() -> None:
    app = QApplication.instance()
    if app is not None:
        app.setStyleSheet(stylesheet())
