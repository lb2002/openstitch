"""Hauptfenster von OpenStitch Studio (Modernes Dark-Studio-UI, herstellerneutral)."""
from __future__ import annotations

import math
import os
from pathlib import Path

from PySide6.QtCore import QSettings, QSize, QStandardPaths, Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QColor, QDragEnterEvent, QDropEvent, QFont, QIcon, QKeySequence, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from shapely.geometry import LineString, Point

from .. import APP_NAME, __version__
from ..auto.palette import CATALOG_PALETTES, active_palette, nearest_thread, set_active_palette
from ..i18n import (
    LANGUAGES, current_lang, fmt_int, init_lang, key_for, machine_display_name, set_lang, tr, tr_opt,
)
from ..core.design import HOOPS, Design, EmbObject, FillObject, Hoop, RunObject, SatinObject, color_sorted
from ..core.machines import MACHINE_PROFILES, MachineProfile
from ..core.stitchplan import Thread
from ..engine.pro_tools import create_applique_objects, import_svg, run_quality_doctor
from ..io.formats import FORMAT_NAMES, READ_EXT, WRITE_EXT, export_plan, import_file, verify_exported_file
from ..io.project import export_worksheet_pdf, load_project, save_project
from ..render import render_image
from ..text import TextObject
from .canvas import StitchCanvas
from .dialogs import AutoDigitizeDialog, MelcoDiskDialog, PhotoStitchDialog, TextDialog
from .onboarding import InAppTourOverlay, OnboardingTourDialog, create_openstitch_logo_design, studio_icon
from .plan_worker import PlanBuilder

STUDIO_STYLE = """
QMainWindow, QDialog, QDockWidget, QWidget {
    background-color: #1f232b;
    color: #dfe3ec;
    font-family: "Segoe UI", "SF Pro Text", sans-serif;
    font-size: 9.5pt;
}
QLabel, QCheckBox {
    background: transparent;
}
QMenuBar {
    background-color: #1a1d24;
    color: #c9d0de;
    border-bottom: 1px solid #2d3340;
    padding: 3px 6px;
}
QMenuBar::item:selected {
    background-color: #2c3342;
    border-radius: 4px;
}
QMenu {
    background-color: #242934;
    border: 1px solid #363e4f;
    padding: 4px;
}
QMenu::item:selected {
    background-color: #3f6ec7;
    border-radius: 4px;
}
QToolBar {
    background-color: #232832;
    border-bottom: 1px solid #303644;
    border-right: 1px solid #303644;
    spacing: 5px;
    padding: 5px 8px;
}
QToolButton {
    background-color: #2b313d;
    border: 1px solid #394152;
    border-radius: 6px;
    padding: 4px 8px;
    color: #e1e5ef;
    font-weight: 500;
}
QToolButton:hover, QPushButton:hover {
    background-color: #343c4b;
    border-color: #6b99f0;
}
QToolButton:checked, QPushButton:checked {
    background-color: rgba(138, 180, 248, 0.24);
    border-color: #7cacf8;
    color: #e8f0fe;
}
QPushButton {
    background-color: #2b313d;
    border: 1px solid #3a4253;
    border-radius: 6px;
    padding: 5px 10px;
    color: #e1e5ef;
}
QPushButton#primaryBtn {
    background-color: #4678d8;
    border: 1px solid #6b99f0;
    color: #f8f9fc;
    font-weight: 600;
}
QPushButton#primaryBtn:hover {
    background-color: #5486e6;
}
QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    font-weight: 600;
    color: #9ba4b8;
}
QDockWidget::title {
    background-color: #232832;
    border-top: 1px solid #303644;
    border-bottom: 1px solid #303644;
    padding: 6px 10px;
    text-transform: uppercase;
    font-size: 8.5pt;
    letter-spacing: 0.6px;
}
QFrame#card {
    background-color: #262b35;
    border: 1px solid #343b49;
    border-radius: 8px;
    padding: 6px;
}
QListWidget, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #1a1e25;
    border: 1px solid #323947;
    border-radius: 6px;
    padding: 4px 7px;
    color: #e1e5ef;
}
QListWidget::item {
    padding: 5px 6px;
    border-radius: 5px;
    margin: 1px 2px;
}
QListWidget::item:selected {
    background-color: rgba(138, 180, 248, 0.25);
    border: 1px solid rgba(138, 180, 248, 0.45);
    color: #f0f4fc;
}
QListWidget::item:hover:!selected {
    background-color: #282e3b;
}
QScrollBar:vertical {
    background: #1c2028;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #384050;
    min-height: 24px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #4e586e;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #2c3240;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #5b8def;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #eef2fa;
    border: 2px solid #5b8def;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QStatusBar {
    background-color: #191c23;
    color: #9ba5b9;
    border-top: 1px solid #2d3340;
    font-size: 9pt;
}
"""


def _color_icon(rgb: tuple[int, int, int], size: int = 16) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setBrush(QColor(*rgb))
    p.setPen(QPen(QColor(255, 255, 255, 150), 1.2))
    p.drawRoundedRect(1, 1, size - 2, size - 2, 4, 4)
    p.end()
    return QIcon(pix)


class MainWindow(QMainWindow):
    def __init__(self, defer_starter: bool = False, show_tour_on_init: bool = True):
        super().__init__()
        init_lang()
        self._tr_bindings: list[tuple] = []
        self._bind(self.setWindowTitle, "app_tagline", fmt=lambda s: f"{APP_NAME} Studio {__version__}  —  {s}")
        self.resize(1540, 920)
        self.setStyleSheet(STUDIO_STYLE)
        self.setAcceptDrops(True)
        self._show_tour_on_init = show_tour_on_init
        self._tour_overlay: InAppTourOverlay | None = None

        self.canvas = StitchCanvas(self)
        self._planner = PlanBuilder(self)
        self._planner.finished.connect(self._on_plan_finished)
        self._applied_gen = 0
        self._dirty = False
        central = QWidget(self)
        c_lay = QVBoxLayout(central)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(0)

        # Google-Studio Kontextleiste direkt über der Leinwand (Maschine, Rahmen, Auto-Fit, Stoff & Strategie)
        ctx_bar = QFrame(central)
        self.ctx_bar = ctx_bar
        ctx_bar.setStyleSheet(
            "QFrame { background-color: #1c2028; border-bottom: 1px solid #2e3442; }"
        )
        ctx_hb = QHBoxLayout(ctx_bar)
        ctx_hb.setContentsMargins(12, 5, 12, 5)
        ctx_hb.setSpacing(8)

        lbl_m = QLabel("Maschine:")
        lbl_m.setStyleSheet("color: #8ab4f8; font-weight: 600;")
        self._bind(lbl_m.setText, "lbl_machine")
        ctx_hb.addWidget(lbl_m)
        self.cmb_machine = QComboBox()
        self.cmb_machine.setMinimumWidth(225)
        for mp in MACHINE_PROFILES:
            self.cmb_machine.addItem(machine_display_name(mp.name), mp)
        self.cmb_machine.currentIndexChanged.connect(self._on_machine_changed)
        ctx_hb.addWidget(self.cmb_machine)

        ctx_hb.addSpacing(4)
        lbl_h = QLabel("Stickrahmen:")
        lbl_h.setStyleSheet("color: #8ab4f8; font-weight: 600;")
        self._bind(lbl_h.setText, "lbl_hoop")
        ctx_hb.addWidget(lbl_h)
        self.cmb_hoop = QComboBox()
        self.cmb_hoop.setMinimumWidth(200)
        for h in HOOPS:
            self.cmb_hoop.addItem(self._hoop_label(h), h)
        self.cmb_hoop.setCurrentIndex(2)  # Rund 15 cm Standard
        self.cmb_hoop.currentIndexChanged.connect(self._on_hoop_changed)
        ctx_hb.addWidget(self.cmb_hoop)

        btn_fit = QToolButton()
        btn_fit.setIcon(studio_icon("fit", 16))
        btn_fit.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn_fit.setText("Auto-Fit")
        self._bind(btn_fit.setText, "btn_autofit")
        self._bind(btn_fit.setToolTip, "tip_autofit")
        btn_fit.clicked.connect(self.action_fit_to_hoop)
        ctx_hb.addWidget(btn_fit)

        self.btn_fabric = QToolButton()
        self.btn_fabric.setText(tr("fabric_slate"))
        self._bind(self.btn_fabric.setToolTip, "tip_fabric")
        self.btn_fabric.clicked.connect(self.cycle_fabric_theme)
        ctx_hb.addWidget(self.btn_fabric)

        ctx_hb.addStretch(1)

        lbl_lang = QLabel("Sprache:")
        lbl_lang.setStyleSheet("color: #8ab4f8; font-weight: 600;")
        self._bind(lbl_lang.setText, "lbl_lang")
        ctx_hb.addWidget(lbl_lang)
        self.cmb_lang = QComboBox()
        for code, label in LANGUAGES:
            self.cmb_lang.addItem(label, code)
        self.cmb_lang.setCurrentIndex(max(0, next((i for i, (c, _) in enumerate(LANGUAGES) if c == current_lang()), 0)))
        self.cmb_lang.currentIndexChanged.connect(self._on_language_changed)
        ctx_hb.addWidget(self.cmb_lang)
        ctx_hb.addSpacing(6)
        self.lbl_hoop_strategy = QLabel()  # Text setzt retranslate_ui()
        self.lbl_hoop_strategy.setStyleSheet(
            "color: #81c995; background-color: rgba(129, 201, 149, 0.12); "
            "border: 1px solid rgba(129, 201, 149, 0.28); border-radius: 5px; padding: 3px 8px; font-size: 8.5pt;"
        )
        ctx_hb.addWidget(self.lbl_hoop_strategy)

        c_lay.addWidget(ctx_bar)
        c_lay.addWidget(self.canvas, 1)
        self.setCentralWidget(central)

        self._undo_stack: list[tuple[str, list[EmbObject]]] = []
        self._redo_stack: list[tuple[str, list[EmbObject]]] = []
        self._updating_props = False

        self._rebuild_timer = QTimer(self)
        self._rebuild_timer.setSingleShot(True)
        self._rebuild_timer.setInterval(120)
        self._rebuild_timer.timeout.connect(lambda: self.rebuild_plan(refresh_props=False))
        self._last_edit_key = None

        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(25)
        self.sim_timer.timeout.connect(self._sim_step)

        self._build_menus_and_header()
        self._build_left_tool_rail()
        self._build_left_palette_dock()
        self._build_right_dock()
        self._build_bottom_bar()

        self.canvas.selection_changed.connect(self._on_canvas_selection)
        self.canvas.about_to_modify.connect(self._snapshot)
        self.canvas.design_modified.connect(self._on_design_modified)
        self.canvas.tool_changed.connect(self._set_tool)
        self.canvas.cursor_moved.connect(self._on_cursor_moved)
        self.retranslate_ui()

        if not defer_starter:
            self._load_starter_design()

    # ------------------------------------------------------------ Mehrsprachigkeit
    def _bind(self, setter, key: str, escape: bool = False, fmt=None):
        """Bindet ein Widget-Textsetzer an einen i18n-Schlüssel und setzt den aktuellen Text sofort."""
        self._tr_bindings.append((setter, key, escape, fmt))
        self._apply_binding(setter, key, escape, fmt)

    @staticmethod
    def _apply_binding(setter, key, escape, fmt):
        txt = tr(key)
        if escape:
            txt = txt.replace("&", "&&")
        if fmt is not None:
            txt = fmt(txt)
        setter(txt)

    def _update_strategy_label(self):
        if hasattr(self, "lbl_hoop_strategy"):
            self.lbl_hoop_strategy.setText(
                f"{tr('lbl_strategy')}{tr('label_colon')} {self.canvas.design.hoop.strategy_description}"
            )

    @staticmethod
    def _hoop_label(h: Hoop) -> str:
        return f"{h.display_name} ({h.width:.0f}×{h.height:.0f} mm)"

    def retranslate_ui(self):
        for setter, key, escape, fmt in self._tr_bindings:
            self._apply_binding(setter, key, escape, fmt)
        for i in range(self.cmb_hoop.count()):
            self.cmb_hoop.setItemText(i, self._hoop_label(self.cmb_hoop.itemData(i)))
        for i in range(self.cmb_machine.count()):
            self.cmb_machine.setItemText(i, machine_display_name(self.cmb_machine.itemData(i).name))
        self._refresh_object_list()
        total = self.canvas.plan.stitch_count
        if total:  # Zahlenformat des Simulator-Zählers an die Sprache anpassen
            cur = total if self.canvas.sim_limit is None else self.canvas.sim_limit
            self.lbl_sim.setText(f"{fmt_int(cur)} / {fmt_int(total)}")
        lbl = {"slate": "fabric_slate", "sand": "fabric_sand", "light": "fabric_light"}
        self.btn_fabric.setText(tr(lbl.get(self.canvas.fabric_theme, "fabric_slate")))
        self._refresh_stats()
        self._refresh_needle_list()
        self._populate_properties(self.canvas.selected)
        self._update_strategy_label()
        self.btn_play.setText(tr("btn_pause") if self.btn_play.isChecked() else tr("btn_play"))
        self.canvas.update()

    def _on_language_changed(self):
        lang = self.cmb_lang.currentData()
        if lang and lang != current_lang():
            set_lang(lang)
            self.retranslate_ui()

    def _on_catalog_changed(self):
        pal = self.cmb_catalog.currentData()
        if pal is None:
            return
        set_active_palette(pal)
        self._rebuild_swatch_grid()
        self.status.showMessage(f"{tr('lbl_catalog')} {pal.name} ({len(pal.threads)})", 6000)

    def _rebuild_swatch_grid(self):
        grid = self.swatch_grid
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        cols = 7
        for idx, t in enumerate(active_palette().threads[:70]):
            btn = QToolButton()
            btn.setFixedSize(30, 24)
            btn.setToolTip(f"{t.brand} {t.code} {t.name} ({t.hex})")
            r, g, b = t.color
            btn.setStyleSheet(
                f"QToolButton {{ background-color: rgb({r},{g},{b}); border: 1px solid rgba(255,255,255,35); border-radius: 5px; }}"
                f"QToolButton:hover {{ border: 2px solid #a8c7fa; }}"
            )
            btn.clicked.connect(lambda _=False, th=t: self._apply_thread(th))
            grid.addWidget(btn, idx // cols, idx % cols)

    def cycle_fabric_theme(self):
        order = [("slate", "fabric_slate"), ("sand", "fabric_sand"), ("light", "fabric_light")]
        cur = self.canvas.fabric_theme
        idx = next((i for i, (k, _) in enumerate(order) if k == cur), 0)
        nxt_k, nxt_key = order[(idx + 1) % len(order)]
        self.canvas.fabric_theme = nxt_k
        self.btn_fabric.setText(tr(nxt_key))
        self.canvas.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._tour_overlay is not None and self._tour_overlay.isVisible():
            self._tour_overlay._refresh()

    # ======================================= 1. Menüs & Kompakte Header-Toolbar
    def _build_menus_and_header(self):
        mb = self.menuBar()
        m_file = mb.addMenu("")
        m_edit = mb.addMenu("")
        m_view = mb.addMenu("")
        m_create = mb.addMenu("")
        m_machine = mb.addMenu("")
        m_help = mb.addMenu("")
        for _m, _k in ((m_file, "menu_file"), (m_edit, "menu_edit"), (m_view, "menu_view"),
                       (m_create, "menu_create"), (m_machine, "menu_machine"), (m_help, "menu_help")):
            self._bind(_m.setTitle, _k, fmt=lambda s: s.replace("&&", "&&"))

        tb = QToolBar(tr("tb_title_studio"), self)
        self._bind(tb.setWindowTitle, "tb_title_studio")
        self.top_toolbar = tb
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(Qt.TopToolBarArea, tb)

        def add_act(menu, text, slot, shortcut=None, toolbar_label=None, icon_kind=None, checkable=False):
            ic = studio_icon(icon_kind, 16) if icon_kind else QIcon()
            act = QAction(ic, text, self)
            key = key_for(text)
            if key:
                self._bind(act.setText, key, escape=True)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            act.setCheckable(checkable)
            act.triggered.connect(slot)
            menu.addAction(act)
            if toolbar_label:
                tb_act = QAction(ic, toolbar_label, self)
                tb_key = key_for(toolbar_label)
                if tb_key:
                    self._bind(tb_act.setText, tb_key, escape=True)
                if key:
                    self._bind(
                        tb_act.setToolTip, key, escape=False,
                        fmt=(lambda s, sc=shortcut: f"{s} ({sc})" if sc else s),
                    )
                tb_act.setCheckable(checkable)
                tb_act.triggered.connect(slot)
                tb.addAction(tb_act)
                return tb_act
            return act

        # Datei
        add_act(m_file, "Neues Design", self.action_new, "Ctrl+N", "Neu", "new")
        add_act(m_file, "Projekt öffnen (.ostitch) …", self.action_open_project, "Ctrl+O")
        add_act(m_file, "Projekt speichern (.ostitch) …", self.action_save_project, "Ctrl+S")
        m_file.addSeparator()
        add_act(m_file, "Stickdatei importieren (EXP, DST, PES, JEF …) …", self.action_import_embroidery, "Ctrl+I", "Import", "import")
        add_act(m_file, "SVG-Vektorgrafik importieren (.svg) …", self.action_import_svg, None, "SVG", "svg")
        add_act(m_file, "Stickdatei exportieren (EXP, DST, PES, JEF …) …", self.action_export_embroidery, "Ctrl+E", "Export", "export")
        add_act(m_file, "Produktionsblatt als PDF speichern …", self.action_export_pdf, None, "PDF", "pdf")
        add_act(m_file, "Realistische 3D-Vorschau als PNG speichern …", self.action_export_png)
        m_file.addSeparator()
        add_act(m_file, "Beenden", self.close, "Ctrl+Q")

        tb.addSeparator()
        # Digitalisieren / Assistenten
        add_act(m_create, "Bild automatisch digitalisieren (Auto-Digitizer) …", self.action_auto_digitize, "Ctrl+D", "Auto-Digitizer", "magic")
        add_act(m_create, "PhotoStitch (Porträtfoto → Stickerei) …", self.action_photostitch, "Ctrl+P", "PhotoStitch", "photo")
        add_act(m_create, "Schrift / Monogramm einfügen …", self.action_add_text, "Ctrl+T", "Schrift", "text")
        add_act(m_create, "Aus Fläche Applikation (Appliqué) erzeugen", self.action_make_applique, None, "Appliqué", "applique")
        add_act(m_create, "3D-Puff-Schaumstoff-Modus für Satin umschalten", self.action_toggle_3d_puff, None, "3D-Puff", "puff")

        tb.addSeparator()
        # Maschine & Qualitätsprüfung
        add_act(m_machine, "Maschinen-Transfer / Diskette / USB / NetBridge …", self.action_melco_disk, "Ctrl+M", "Transfer", "transfer")
        add_act(m_machine, "Qualitäts- & Maschinen-Doktor (Prüfung)", self.action_quality_doctor, "F7", "Doktor", "doctor")
        add_act(m_machine, "Farben minimieren (Nadelwechsel sparen)", self.action_optimize_color_order)

        # Hilfe / Rundgang
        add_act(m_help, "Interaktiver Studio-Rundgang (Onboarding) …", self.action_show_tour, "F1", "Rundgang", "tour")
        add_act(m_help, "Offizielles OpenStitch-Logo wiederherstellen", self._load_starter_design)

        # Bearbeiten
        add_act(m_edit, "Rückgängig", self.action_undo, "Ctrl+Z")
        add_act(m_edit, "Wiederherstellen", self.action_redo, "Ctrl+Y")
        m_edit.addSeparator()
        add_act(m_edit, "Ausgewähltes Objekt duplizieren", self.action_duplicate_selected, "Ctrl+J")
        add_act(m_edit, "Ausgewähltes Objekt löschen", self.action_delete_selected, "Delete")
        add_act(m_edit, "Design im Rahmen zentrieren", self.action_center_design)
        add_act(m_edit, "Optimal in aktuellen Rahmen einpassen (Auto-Fit)", self.action_fit_to_hoop, "Ctrl+F")
        add_act(m_edit, "Kleinsten passenden Rahmen automatisch wählen", self.action_auto_select_hoop)
        add_act(m_edit, "Design skalieren (% / mm) …", self.action_scale_design)

        # Ansicht
        self.act_3d = add_act(m_view, "3D-Fadendarstellung", self._toggle_view, None, None, None, True)
        self.act_3d.setChecked(True)
        self.act_jumps = add_act(m_view, "Sprungstiche anzeigen", self._toggle_view, None, None, None, True)
        self.act_jumps.setChecked(True)
        self.act_grid = add_act(m_view, "Millimeter-Raster anzeigen", self._toggle_view, None, None, None, True)
        self.act_grid.setChecked(True)
        self.act_heatmap = add_act(m_view, "Stichdichte-Heatmap (Stoffbelastung)", self._toggle_view, "Ctrl+H", None, None, True)
        add_act(m_view, "Auf Rahmengrösse zoomen", self.canvas.zoom_to_fit, "Ctrl+0")

    # ================================= 2. Linke Vertikal-Werkzeugleiste (Tool-Rail)
    def _build_left_tool_rail(self):
        rail = QToolBar(tr("tb_title_tools"), self)
        self._bind(rail.setWindowTitle, "tb_title_tools")
        self.left_rail = rail
        rail.setMovable(False)
        rail.setOrientation(Qt.Vertical)
        rail.setIconSize(QSize(17, 17))
        rail.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(Qt.LeftToolBarArea, rail)

        def rail_btn(key: str, icon_kind: str, tip_key: str, slot, checkable: bool = True) -> QAction:
            a = QAction(studio_icon(icon_kind, 17), tr(key), self)
            self._bind(a.setText, key, escape=True)
            self._bind(a.setToolTip, tip_key)
            a.setCheckable(checkable)
            a.triggered.connect(slot)
            rail.addAction(a)
            w_btn = rail.widgetForAction(a)
            if w_btn is not None:
                w_btn.setMinimumWidth(116)
            return a

        self.act_tool_select = rail_btn("tool_select", "select", "tip_tool_select", lambda: self._set_tool("select"))
        self.act_tool_nodes = rail_btn("tool_nodes", "nodes", "tip_tool_nodes", lambda: self._set_tool("edit_nodes"))
        rail.addSeparator()
        self.act_tool_fill = rail_btn("tool_fill", "fill", "tip_tool_fill", lambda: self._set_tool("draw_fill"))
        self.act_tool_satin = rail_btn("tool_satin", "satin", "tip_tool_satin", lambda: self._set_tool("draw_satin"))
        self.act_tool_run = rail_btn("tool_run", "run", "tip_tool_run", lambda: self._set_tool("draw_run"))
        rail.addSeparator()
        self.act_rail_heatmap = rail_btn("tool_heatmap", "heatmap", "tip_tool_heatmap", self._toggle_heatmap_from_rail)
        rail_btn("tool_zoom", "zoom", "tip_tool_zoom", self.canvas.zoom_to_fit, checkable=False)
        self.act_tool_select.setChecked(True)

    def _toggle_heatmap_from_rail(self, checked: bool):
        self.act_heatmap.setChecked(checked)
        self._toggle_view()

    # =============================== 3. Linkes Dock: Kompaktes Farb-Grid & Sequenz
    def _build_left_palette_dock(self):
        dock = QDockWidget("Garnfarben && Nadel-Sequenz", self)
        self._bind(dock.setWindowTitle, "dock_palette")
        self.left_dock = dock
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        w = QWidget()
        w.setMaximumWidth(275)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # Aktive Farbe oben als elegante Karte
        card_cur = QFrame()
        card_cur.setObjectName("card")
        hc = QHBoxLayout(card_cur)
        hc.setContentsMargins(6, 4, 6, 4)
        self.lbl_active_swatch = QLabel()
        self.lbl_active_swatch.setFixedSize(26, 26)
        self.lbl_active_name = QLabel("043 Rot")
        self.lbl_active_name.setStyleSheet("font-weight: 600;")
        btn_rgb = QPushButton("RGB …")
        btn_rgb.setFixedWidth(64)
        btn_rgb.clicked.connect(self._pick_custom_color)
        hc.addWidget(self.lbl_active_swatch)
        hc.addWidget(self.lbl_active_name, 1)
        hc.addWidget(btn_rgb)
        lay.addWidget(card_cur)

        # Garnkatalog-Auswahl (Madeira, Isacord, Gunold, Brother, Universal)
        hb_cat = QHBoxLayout()
        lbl_cat = QLabel("Garnkatalog:")
        lbl_cat.setStyleSheet("color: #8ab4f8; font-weight: 600;")
        self._bind(lbl_cat.setText, "lbl_catalog")
        self.cmb_catalog = QComboBox()
        for pal in CATALOG_PALETTES:
            self.cmb_catalog.addItem(pal.name, pal)
        self.cmb_catalog.setCurrentIndex(0)
        hb_cat.addWidget(lbl_cat)
        hb_cat.addWidget(self.cmb_catalog, 1)
        lay.addLayout(hb_cat)

        # Kompaktes 7-spaltiges Farbfeld-Grid (statt klobiger langer Liste!)
        swatch_card = QFrame()
        swatch_card.setObjectName("card")
        self.swatch_grid = QGridLayout(swatch_card)
        self.swatch_grid.setContentsMargins(6, 6, 6, 6)
        self.swatch_grid.setSpacing(4)
        self._rebuild_swatch_grid()
        self.cmb_catalog.currentIndexChanged.connect(self._on_catalog_changed)
        lay.addWidget(swatch_card)

        lbl_seq = QLabel("Farb- & Nadel-Sequenz im Design:")
        self._bind(lbl_seq.setText, "lbl_seq")
        lbl_seq.setStyleSheet("color: #9ba4b8; font-weight: 600; margin-top: 4px;")
        lay.addWidget(lbl_seq)

        self.list_needles = QListWidget()
        self.list_needles.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lay.addWidget(self.list_needles, 1)

        dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self._update_active_swatch_ui()

    def _update_active_swatch_ui(self):
        t = self.canvas.active_thread
        r, g, b = t.color
        self.lbl_active_swatch.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); border: 1px solid rgba(255,255,255,90); border-radius: 5px;"
        )
        self.lbl_active_name.setText(f"{t.code}  {t.name}")

    # ======================================= 4. Rechtes Dock: Ebenen & Inspektor
    def _build_right_dock(self):
        dock = QDockWidget("Ebenen && Objekt-Inspektor", self)
        self._bind(dock.setWindowTitle, "dock_right")
        self.right_dock = dock
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        split = QSplitter(Qt.Vertical)
        split.setMinimumWidth(330)
        split.setMaximumWidth(370)

        w_top = QWidget()
        vt = QVBoxLayout(w_top)
        vt.setContentsMargins(8, 8, 8, 4)
        self.list_objects = QListWidget()
        self.list_objects.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_objects.currentRowChanged.connect(self._on_object_row_changed)
        vt.addWidget(self.list_objects, 1)

        hb = QHBoxLayout()
        btn_up = QPushButton("▲")
        self._bind(btn_up.setToolTip, "tip_obj_up")
        btn_up.clicked.connect(lambda: self._move_selected_object(-1))
        btn_dn = QPushButton("▼")
        self._bind(btn_dn.setToolTip, "tip_obj_down")
        btn_dn.clicked.connect(lambda: self._move_selected_object(1))
        btn_vis = QPushButton("👁 Sichtbar")
        self._bind(btn_vis.setText, "btn_visible")
        btn_vis.clicked.connect(self._toggle_selected_visibility)
        btn_dup = QPushButton("⧉ Kopie")
        self._bind(btn_dup.setText, "btn_copy")
        btn_dup.clicked.connect(self.action_duplicate_selected)
        btn_del = QPushButton("🗑")
        self._bind(btn_del.setToolTip, "tip_obj_delete")
        btn_del.clicked.connect(self.action_delete_selected)
        for b in (btn_up, btn_dn, btn_vis, btn_dup, btn_del):
            hb.addWidget(b)
        vt.addLayout(hb)
        split.addWidget(w_top)

        w_bot = QWidget()
        vb = QVBoxLayout(w_bot)
        vb.setContentsMargins(8, 4, 8, 8)
        lbl_insp = QLabel("Objekt-Parameter (Live-Neuberechnung):")
        self._bind(lbl_insp.setText, "lbl_inspector")
        lbl_insp.setStyleSheet("color: #8ab4f8; font-weight: 600;")
        vb.addWidget(lbl_insp)
        self.prop_container = QFrame()
        self.prop_container.setObjectName("card")
        self.prop_layout = QFormLayout(self.prop_container)
        self.prop_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.prop_layout.setVerticalSpacing(8)
        self.prop_layout.setHorizontalSpacing(10)
        vb.addWidget(self.prop_container, 1)
        split.addWidget(w_bot)
        split.setSizes([235, 485])

        dock.setWidget(split)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    # ========================================= 5. Unten: Simulator & Statusleiste
    def _build_bottom_bar(self):
        dock = QDockWidget("Stich-Simulator && Näh-Player", self)
        self._bind(dock.setWindowTitle, "dock_bottom")
        self.bottom_dock = dock
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        w = QWidget()
        hb = QHBoxLayout(w)
        hb.setContentsMargins(12, 6, 12, 6)

        self.btn_play = QPushButton(tr("btn_play"))
        self.btn_play.setObjectName("primaryBtn")
        self.btn_play.setCheckable(True)
        self.btn_play.toggled.connect(self._toggle_sim)
        hb.addWidget(self.btn_play)

        btn_reset_sim = QPushButton("⏭ Alle zeigen")
        self._bind(btn_reset_sim.setText, "btn_show_all")
        btn_reset_sim.clicked.connect(self._reset_sim)
        hb.addWidget(btn_reset_sim)

        lbl_prog = QLabel("  Fortschritt:")
        self._bind(lbl_prog.setText, "lbl_progress")
        hb.addWidget(lbl_prog)
        self.slider_sim = QSlider(Qt.Horizontal)
        self.slider_sim.setRange(0, 100)
        self.slider_sim.setValue(100)
        self.slider_sim.valueChanged.connect(self._on_sim_slider)
        hb.addWidget(self.slider_sim, 1)

        self.lbl_sim = QLabel(tr("sim_all"))
        self.lbl_sim.setMinimumWidth(115)
        hb.addWidget(self.lbl_sim)

        lbl_spd = QLabel("Tempo:")
        self._bind(lbl_spd.setText, "lbl_speed")
        hb.addWidget(lbl_spd)
        self.sp_sim_speed = QSpinBox()
        self.sp_sim_speed.setRange(5, 500)
        self.sp_sim_speed.setValue(45)
        self._bind(self.sp_sim_speed.setSuffix, "sim_speed_suffix")
        hb.addWidget(self.sp_sim_speed)

        dock.setWidget(w)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.lbl_stats = QLabel()
        self.lbl_cursor = QLabel("X: 0.0 mm, Y: 0.0 mm")
        self.status.addWidget(self.lbl_stats, 1)
        self.status.addPermanentWidget(self.lbl_cursor)

    # ============================================= Offizielles OpenStitch-Starter-Logo & In-App Rundgang
    def _load_starter_design(self):
        d = create_openstitch_logo_design()
        self.set_design(d, reset_undo=True)
        if d.objects:
            self.canvas.selected = d.objects[0]
            self._refresh_object_list()
            self._populate_properties(d.objects[0])
        QTimer.singleShot(60, self.canvas.zoom_to_fit)
        if self._show_tour_on_init:
            self._show_tour_on_init = False
            settings = QSettings("OpenStitch", "OpenStitchStudio")
            if settings.value("show_tour_on_startup", True, type=bool):
                QTimer.singleShot(280, self.action_show_tour)

    def action_show_tour(self):
        if self._tour_overlay is None:
            self._tour_overlay = InAppTourOverlay(self)
        self._tour_overlay.start_tour()

    # =================================================== Design-Rebuild & Sync
    def set_design(self, d: Design, reset_undo: bool = False, prebuilt_plan=None):
        self.canvas.design = d
        self.canvas.selected = d.objects[0] if d.objects else None
        self.canvas.sim_limit = None
        if hasattr(self, "btn_play"):
            self.btn_play.setChecked(False)
        if reset_undo:
            self._undo_stack.clear()
            self._redo_stack.clear()
            self._dirty = False
        else:
            self._dirty = True
        self._last_edit_key = None
        self._sync_hoop_machine_ui()
        self.rebuild_plan(prebuilt_plan=prebuilt_plan)

    def _sync_hoop_machine_ui(self):
        """Rahmen-/Maschinen-Auswahl an das (neu geladene) Design anpassen, ohne Signale auszulösen."""
        d = self.canvas.design
        if hasattr(self, "cmb_hoop"):
            idx = next((i for i in range(self.cmb_hoop.count())
                        if self.cmb_hoop.itemData(i).name == d.hoop.name), -1)
            if idx >= 0:
                # gleiche Instanz verwenden wie die Auswahlliste
                d.hoop = self.cmb_hoop.itemData(idx)
                self.cmb_hoop.blockSignals(True)
                self.cmb_hoop.setCurrentIndex(idx)
                self.cmb_hoop.blockSignals(False)
            self._update_strategy_label()
        if hasattr(self, "cmb_machine"):
            idx = next((i for i in range(self.cmb_machine.count())
                        if self.cmb_machine.itemData(i).name == d.settings.machine_name), -1)
            if idx >= 0:
                self.cmb_machine.blockSignals(True)
                self.cmb_machine.setCurrentIndex(idx)
                self.cmb_machine.blockSignals(False)

    def _snapshot(self, desc: str):
        self._dirty = True
        self._last_edit_key = None
        self._undo_stack.append((desc, [o.snapshot() for o in self.canvas.design.objects]))
        if len(self._undo_stack) > 30:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def rebuild_plan(self, prebuilt_plan=None, refresh_props: bool = True):
        """Objektliste/Inspektor sofort aktualisieren, Stiche im Hintergrund neu berechnen."""
        self._refresh_object_list()
        if refresh_props:
            self._populate_properties(self.canvas.selected)
        if prebuilt_plan is not None:
            # laufende Berechnungen sind damit überholt
            self._applied_gen = self._planner.supersede()
            self._apply_plan(prebuilt_plan)
            return
        self._planner.request(self.canvas.design)
        if hasattr(self, "status"):
            self.status.showMessage(tr("status_computing"))

    def _on_plan_finished(self, gen: int, plan, err: str):
        if gen != self._planner.generation or gen <= self._applied_gen:
            return  # veraltet – eine neuere Berechnung läuft schon
        self._applied_gen = gen
        if plan is None:
            self.status.showMessage(f"{tr('status_plan_error')}: {err}", 12000)
            return
        self.status.clearMessage()
        self._apply_plan(plan)

    def wait_for_plan(self):
        """Wartet auf die laufende Berechnung (vor Export, Prüfung & in Tests)."""
        res = self._planner.wait()
        if res is not None:
            self._on_plan_finished(*res)
        return self.canvas.plan

    def _apply_plan(self, plan):
        self.canvas.plan = plan
        n = max(1, self.canvas.plan.stitch_count)
        self.slider_sim.blockSignals(True)
        self.slider_sim.setRange(0, n)
        if self.canvas.sim_limit is None:
            self.slider_sim.setValue(n)
            self.lbl_sim.setText(f"{fmt_int(n)} / {fmt_int(n)}")
        self.slider_sim.blockSignals(False)

        self._refresh_needle_list()
        self._refresh_stats()
        self.canvas.invalidate_render_cache()

    def _refresh_stats(self):
        from ..engine.density_guard import analyze_kinematics
        p = self.canvas.plan
        x0, y0, x1, y1 = p.bounds()
        w, h = x1 - x0, y1 - y0
        kin = analyze_kinematics(p, self.canvas.design.settings.machine_spm)
        self.lbl_stats.setText(
            f"{tr('stats_stitches')}{tr('label_colon')} {fmt_int(p.stitch_count)}   ·   "
            f"{tr('stats_size')}{tr('label_colon')} {w:.1f} × {h:.1f} mm   ·   "
            f"{tr('stats_avg')}{tr('label_colon')} {kin['avg_len']:.1f} mm   ·   "
            f"{tr('stats_spm')}{tr('label_colon')} ~{kin['eff_spm']} SPM   ·   "
            f"{tr('stats_peak')}{tr('label_colon')} {kin['max_per_mm2']}/mm²   ·   "
            f"{tr('stats_colors')}{tr('label_colon')} {p.color_changes}   ·   "
            f"{tr('stats_trims')}{tr('label_colon')} {p.trim_count}   ·   "
            f"{tr('stats_runtime')} {kin['real_minutes']:.1f} {tr('stats_min')}"
        )

    def _refresh_object_list(self):
        self.list_objects.blockSignals(True)
        self.list_objects.clear()
        sel_row = -1
        for i, o in enumerate(self.canvas.design.objects):
            vis = "" if o.visible else f"{tr('obj_hidden')} "
            kl = tr_opt(f"kind_{o.kind}", o.kind)
            it = QListWidgetItem(_color_icon(o.thread.color), f"{i + 1}. {vis}{kl} · {o.name or o.thread.name}")
            self.list_objects.addItem(it)
            if o is self.canvas.selected:
                sel_row = i
        if sel_row >= 0:
            self.list_objects.setCurrentRow(sel_row)
        self.list_objects.blockSignals(False)

    def _refresh_needle_list(self):
        self.list_needles.clear()
        plan = self.canvas.plan
        needle_map: dict[str, int] = {}
        max_nd = self.canvas.design.settings.needles
        for bi, b in enumerate(plan.blocks):
            if b.thread.hex not in needle_map:
                needle_map[b.thread.hex] = len(needle_map) + 1
            nd = needle_map[b.thread.hex]
            warn = f" ⚠ (>{max_nd}!)" if nd > max_nd else ""
            cnt = sum(1 for s in b.stitches if s.cmd == 0)
            it = QListWidgetItem(
                _color_icon(b.thread.color),
                f"#{bi + 1} ({tr('needle')} {nd}): {b.thread.name or b.thread.hex} · "
                f"{fmt_int(cnt)} {tr('abbr_stitches')}{warn}",
            )
            self.list_needles.addItem(it)

    # ============================================= Eigenschafts-Inspektor
    def _populate_properties(self, obj: EmbObject | None):
        self._updating_props = True
        while self.prop_layout.rowCount() > 0:
            self.prop_layout.removeRow(0)

        if obj is None:
            lbl_empty = QLabel(tr("lbl_no_sel"))
            lbl_empty.setWordWrap(True)
            lbl_empty.setStyleSheet("color: #7c8599;")
            self.prop_layout.addRow(lbl_empty)
            self._updating_props = False
            return

        ed_name = QLineEdit(obj.name)
        ed_name.setCursorPosition(0)
        ed_name.editingFinished.connect(lambda: self._set_obj_attr(obj, "name", ed_name.text()))
        colon = tr("label_colon")  # fr: geschütztes Leerzeichen vor dem Doppelpunkt
        self.prop_layout.addRow(tr("lbl_obj_name") + colon, ed_name)

        kind = getattr(obj, "kind", "")
        for attr, label, typ, vmin, vmax, step in getattr(obj, "PARAMS", ()):
            val = getattr(obj, attr)
            # Labels werden erst bei der Anzeige übersetzt (PARAMS enthält das deutsche Original)
            label = tr_opt(f"param_{kind}_{attr}", tr_opt(f"param_{attr}", label))
            if typ is bool:
                cb = QCheckBox()
                cb.setChecked(bool(val))
                cb.toggled.connect(lambda v, a=attr: self._set_obj_attr(obj, a, v))
                self.prop_layout.addRow(label + colon, cb)
            elif typ is int:
                sp = QSpinBox()
                sp.setRange(int(vmin), int(vmax))
                sp.setSingleStep(int(step or 1))
                sp.setValue(int(val))
                sp.valueChanged.connect(lambda v, a=attr: self._set_obj_attr(obj, a, int(v)))
                self.prop_layout.addRow(label + colon, sp)
            elif typ is float:
                sp = QDoubleSpinBox()
                sp.setDecimals(2)
                sp.setRange(float(vmin), float(vmax))
                sp.setSingleStep(float(step or 0.1))
                sp.setValue(float(val))
                sp.valueChanged.connect(lambda v, a=attr: self._set_obj_attr(obj, a, float(v)))
                self.prop_layout.addRow(label + colon, sp)
            elif typ is str:
                ed = QLineEdit(str(val))
                ed.editingFinished.connect(lambda e=ed, a=attr: self._set_obj_attr(obj, a, e.text()))
                self.prop_layout.addRow(label + colon, ed)
            elif isinstance(typ, list):
                cmb = QComboBox()
                for opt in typ:
                    # Datenwert bleibt unverändert (wird gespeichert), nur der Anzeigetext ist übersetzt
                    cmb.addItem(tr_opt(f"opt_{opt}", str(opt)), opt)
                if val in typ:
                    cmb.setCurrentIndex(typ.index(val))
                cmb.currentIndexChanged.connect(lambda _, c=cmb, a=attr: self._set_obj_attr(obj, a, c.currentData()))
                self.prop_layout.addRow(label + colon, cmb)
            elif typ == "font":
                btn_font = QPushButton(tr("btn_font_arc"))
                btn_font.clicked.connect(lambda: self._edit_text_object(obj))
                self.prop_layout.addRow(label + colon, btn_font)

        self._updating_props = False

    def _set_obj_attr(self, obj: EmbObject, attr: str, value):
        if self._updating_props or getattr(obj, attr, None) == value:
            return
        key = (obj.id, attr)
        if self._last_edit_key != key:
            self._snapshot(f"{attr} ändern")
            self._last_edit_key = key
        setattr(obj, attr, value)
        self._rebuild_timer.start()

    def _edit_text_object(self, obj: TextObject):
        dlg = TextDialog(obj.thread, existing=obj, parent=self)
        if dlg.exec() == TextDialog.Accepted and dlg.created_object is not None:
            self._snapshot("Text bearbeiten")
            new_o = dlg.created_object
            new_o.transform = obj.transform
            new_o.name = obj.name or new_o.name
            new_o.visible = obj.visible
            if hasattr(obj, "pull_comp") and hasattr(new_o, "pull_comp"):
                new_o.pull_comp = obj.pull_comp
            idx = self.canvas.design.objects.index(obj)
            self.canvas.design.objects[idx] = new_o
            self.canvas.selected = new_o
            self.rebuild_plan()

    # ======================================================= Aktionen & Slots
    def _set_tool(self, tool: str):
        self.canvas.tool = tool
        self.canvas._draw_pts.clear()
        self.act_tool_select.setChecked(tool == "select")
        self.act_tool_nodes.setChecked(tool == "edit_nodes")
        self.act_tool_fill.setChecked(tool == "draw_fill")
        self.act_tool_satin.setChecked(tool == "draw_satin")
        self.act_tool_run.setChecked(tool == "draw_run")
        self.canvas.update()

    def _toggle_view(self):
        self.canvas.realistic = self.act_3d.isChecked()
        self.canvas.show_jumps = self.act_jumps.isChecked()
        self.canvas.show_grid = self.act_grid.isChecked()
        self.canvas.show_heatmap = self.act_heatmap.isChecked()
        self.act_rail_heatmap.setChecked(self.act_heatmap.isChecked())
        self.canvas.invalidate_render_cache()

    def _on_hoop_changed(self):
        self.canvas.design.hoop = self.cmb_hoop.currentData()
        if self.canvas.design.hoop.mode == "cap":
            self._apply_cap_center_out_order()
        self._update_strategy_label()
        self.rebuild_plan()
        self.canvas.zoom_to_fit()
        self.status.showMessage(
            tr("status_hoop_strategy").format(self.canvas.design.hoop.strategy_description), 7000
        )

    def _apply_cap_center_out_order(self):
        for o in self.canvas.design.objects:
            if hasattr(o, "angle") and o.kind == "fill":
                if abs(o.angle) < 15:
                    o.angle = 65.0

    def action_auto_select_hoop(self):
        x0, y0, x1, y1 = self.canvas.design.bounds()
        w, h = x1 - x0, y1 - y0
        # Rundrahmen: echter Radius der Nadelpositionen (Bounding-Box-Ecken überschätzen runde Motive)
        plan = self.wait_for_plan()
        r_need = max((math.hypot(s.x, s.y) for b in plan.blocks for s in b.stitches if s.cmd in (0, 1)),
                     default=max(math.hypot(x0, y0), math.hypot(x1, y1), math.hypot(x0, y1), math.hypot(x1, y0)))
        for idx, hp in enumerate(HOOPS):
            mg = hp.margin_mm
            if hp.round and r_need <= (hp.width / 2.0 - mg):
                self.cmb_hoop.setCurrentIndex(idx)
                return
            if not hp.round and hp.mode != "cap" and w <= (hp.width - 2 * mg) and h <= (hp.height - 2 * mg):
                self.cmb_hoop.setCurrentIndex(idx)
                return

    def action_fit_to_hoop(self):
        b = self.canvas.design.bounds()
        if b == (0, 0, 0, 0):
            return
        self._snapshot("In Rahmen einpassen")
        x0, y0, x1, y1 = b
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        w, h = max(x1 - x0, 1.0), max(y1 - y0, 1.0)
        hp = self.canvas.design.hoop
        mg = hp.margin_mm + 2.0
        if hp.round:
            avail_d = hp.width - 2 * mg
            diag = math.hypot(w, h)
            s = (avail_d * 0.92) / max(diag, 1.0)
        else:
            s = min((hp.width - 2 * mg) / w, (hp.height - 2 * mg) / h) * 0.92
        s = max(0.2, min(4.0, s))
        for o in self.canvas.design.objects:
            a, bb, d, e, x, y = o.transform
            nx, ny = (x - cx) * s, (y - cy) * s
            o.transform = (a * s, bb * s, d * s, e * s, nx, ny)
            if isinstance(o, TextObject):
                o.height *= s
                o.letter_spacing *= s
                o.arc_radius *= s
                o.transform = (a, bb, d, e, nx, ny)
        self.rebuild_plan()
        self.canvas.zoom_to_fit()

    def _on_machine_changed(self):
        mp: MachineProfile = self.cmb_machine.currentData()
        self.canvas.design.settings.needles = mp.needles
        self.canvas.design.settings.machine_spm = mp.default_spm
        self.canvas.design.settings.max_stitch = mp.max_stitch_mm
        self.canvas.design.settings.machine_name = mp.name
        self._refresh_needle_list()
        self._refresh_stats()

    def _apply_thread(self, t: Thread):
        self.canvas.active_thread = t
        self._update_active_swatch_ui()
        if self.canvas.selected is not None:
            self._snapshot("Farbe ändern")
            self.canvas.selected.thread = t
            self.rebuild_plan()

    def _pick_custom_color(self):
        col = QColorDialog.getColor(QColor(*self.canvas.active_thread.color), self, tr("color_dialog_title"))
        if not col.isValid():
            return
        t = nearest_thread((col.red(), col.green(), col.blue()))
        t = Thread((col.red(), col.green(), col.blue()), f"{t.name}", t.code, "Eigen")
        self._apply_thread(t)

    def _on_canvas_selection(self, obj: EmbObject | None):
        self._refresh_object_list()
        self._populate_properties(obj)

    def _on_object_row_changed(self, row: int):
        objs = self.canvas.design.objects
        self.canvas.selected = objs[row] if 0 <= row < len(objs) else None
        self._populate_properties(self.canvas.selected)
        self.canvas.update()

    def _on_design_modified(self, desc: str):
        self._dirty = True
        self.rebuild_plan()

    def _confirm_discard(self) -> bool:
        """Fragt nach, bevor ungespeicherte Änderungen verworfen werden. True = weitermachen."""
        if not self._dirty or not self.isVisible():
            return True
        box = QMessageBox(
            QMessageBox.Question, tr("dlg_unsaved_title"), tr("dlg_unsaved_text"),
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, self,
        )
        box.setDefaultButton(QMessageBox.Save)
        for std, key in ((QMessageBox.Save, "btn_save"), (QMessageBox.Discard, "btn_discard"),
                         (QMessageBox.Cancel, "btn_cancel")):
            box.button(std).setText(tr(key))
        box.exec()
        ans = box.standardButton(box.clickedButton())
        if ans == QMessageBox.Save:
            return self.action_save_project()
        return ans == QMessageBox.Discard

    def closeEvent(self, event):
        if not self._confirm_discard():
            event.ignore()
            return
        self._planner.wait(5.0)
        super().closeEvent(event)

    def _on_cursor_moved(self, x: float, y: float):
        self.lbl_cursor.setText(f"X: {x:6.1f} mm,  Y: {y:6.1f} mm")

    def _move_selected_object(self, delta: int):
        obj = self.canvas.selected
        objs = self.canvas.design.objects
        if obj not in objs:
            return
        i = objs.index(obj)
        j = i + delta
        if 0 <= j < len(objs):
            self._snapshot("Reihenfolge ändern")
            objs[i], objs[j] = objs[j], objs[i]
            self.rebuild_plan()

    def _toggle_selected_visibility(self):
        obj = self.canvas.selected
        if obj is not None:
            self._snapshot("Sichtbarkeit")
            obj.visible = not obj.visible
            self.rebuild_plan()

    # -------------------------------------------------------- Datei-Dialoge & Drag & Drop
    def _default_open_dir(self) -> str:
        settings = QSettings("OpenStitch", "OpenStitchStudio")
        last_dir = settings.value("io/last_dir", "", type=str)
        if last_dir and os.path.isdir(last_dir):
            return last_dir
        for loc in (
            QStandardPaths.DownloadLocation,
            QStandardPaths.PicturesLocation,
            QStandardPaths.DesktopLocation,
            QStandardPaths.DocumentsLocation,
            QStandardPaths.HomeLocation,
        ):
            p = QStandardPaths.writableLocation(loc)
            if p and os.path.isdir(p):
                return p
        return os.path.expanduser("~")

    def _remember_dir(self, file_path: str):
        if file_path:
            d = os.path.dirname(os.path.abspath(file_path))
            if os.path.isdir(d):
                settings = QSettings("OpenStitch", "OpenStitchStudio")
                settings.setValue("io/last_dir", d)

    def _sidebar_urls(self) -> list[QUrl]:
        urls: list[QUrl] = []
        seen: set[str] = set()
        candidates = [
            QStandardPaths.writableLocation(QStandardPaths.DownloadLocation),
            QStandardPaths.writableLocation(QStandardPaths.DesktopLocation),
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
            QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation),
            os.path.abspath(os.getcwd()),
        ]
        # Zusätzlich typische Windows-Pfade (auch OneDrive-Desktop/Bilder falls vorhanden)
        user_home = Path.home()
        for sub in ("Downloads", "Desktop", "Pictures", "Documents", "OneDrive/Desktop", "OneDrive/Pictures", "OneDrive/Bilder"):
            candidates.append(str(user_home / sub))
        for c in candidates:
            if c and os.path.isdir(c):
                norm = os.path.normcase(os.path.abspath(c))
                if norm not in seen:
                    seen.add(norm)
                    urls.append(QUrl.fromLocalFile(os.path.abspath(c)))
        return urls

    def _ask_open_file(self, title: str, name_filter: str) -> str:
        dlg = QFileDialog(self, title, self._default_open_dir(), name_filter)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setSidebarUrls(self._sidebar_urls())
        if dlg.exec() == QFileDialog.Accepted and dlg.selectedFiles():
            path = dlg.selectedFiles()[0]
            self._remember_dir(path)
            return path
        return ""

    def _ask_save_file(self, title: str, default_filename: str, name_filter: str) -> str:
        start_path = os.path.join(self._default_open_dir(), default_filename)
        dlg = QFileDialog(self, title, start_path, name_filter)
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setSidebarUrls(self._sidebar_urls())
        if dlg.exec() == QFileDialog.Accepted and dlg.selectedFiles():
            path = dlg.selectedFiles()[0]
            self._remember_dir(path)
            return path
        return ""

    # Drag & Drop direkt aus dem Windows Explorer / macOS Finder auf das Programmfenster
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if not path or not os.path.isfile(path):
            return
        self._remember_dir(path)
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if (ext == "ostitch" or ext == "svg" or ext in READ_EXT) and not self._confirm_discard():
            return
        if ext == "ostitch":
            try:
                self.set_design(load_project(path), reset_undo=True)
                self.canvas.zoom_to_fit()
            except Exception as exc:
                QMessageBox.critical(self, tr("err_open_title"), str(exc))
        elif ext == "svg":
            try:
                d = import_svg(path, target_width_mm=95.0)
                d.hoop = self.canvas.design.hoop
                self.set_design(d, reset_undo=True)
                self.canvas.zoom_to_fit()
            except Exception as exc:
                QMessageBox.critical(self, tr("err_svg_title"), str(exc))
        elif ext in READ_EXT:
            try:
                d = import_file(path)
                self.set_design(d, reset_undo=True)
                self.canvas.zoom_to_fit()
            except Exception as exc:
                QMessageBox.critical(self, tr("err_import_title"), str(exc))
        elif ext in ("png", "jpg", "jpeg", "bmp", "webp", "tif", "tiff", "gif"):
            self._open_auto_digitize_for_path(path)

    # -------------------------------------------------------- Datei-Aktionen
    def action_new(self):
        if not self._confirm_discard():
            return
        self.set_design(Design(name=tr("default_design_name")), reset_undo=True)

    def action_open_project(self):
        if not self._confirm_discard():
            return
        path = self._ask_open_file(
            tr("fd_open_project"), f"{tr('filter_project')} (*.ostitch);;{tr('filter_all_files')} (*.*)"
        )
        if not path:
            return
        try:
            self.set_design(load_project(path), reset_undo=True)
            self.canvas.zoom_to_fit()
        except Exception as exc:
            QMessageBox.critical(self, tr("err_open_title"), str(exc))

    def action_save_project(self):
        path = self._ask_save_file(
            tr("fd_save_project"), f"{self.canvas.design.name}.ostitch", f"{tr('filter_project')} (*.ostitch)"
        )
        if not path:
            return False
        try:
            save_project(self.canvas.design, path)
        except Exception as exc:
            QMessageBox.critical(self, tr("err_save_title"), str(exc))
            return False
        self._dirty = False
        self.status.showMessage(tr("status_saved").format(path), 5000)
        return True

    def action_import_embroidery(self):
        if not self._confirm_discard():
            return
        exts = " ".join(f"*.{e} *.{e.upper()}" for e in READ_EXT)
        path = self._ask_open_file(
            tr("fd_import_emb"), f"{tr('filter_emb')} ({exts});;{tr('filter_all_files')} (*.*)"
        )
        if not path:
            return
        try:
            d = import_file(path)
            self.set_design(d, reset_undo=True)
            self.canvas.zoom_to_fit()
        except Exception as exc:
            QMessageBox.critical(self, tr("err_import_title"), str(exc))

    def action_import_svg(self):
        if not self._confirm_discard():
            return
        path = self._ask_open_file(
            tr("fd_import_svg"), f"{tr('filter_svg')} (*.svg);;{tr('filter_all_files')} (*.*)"
        )
        if not path:
            return
        try:
            d = import_svg(path, target_width_mm=95.0)
            d.hoop = self.canvas.design.hoop
            self.set_design(d, reset_undo=True)
            self.canvas.zoom_to_fit()
        except Exception as exc:
            QMessageBox.critical(self, tr("err_svg_title"), str(exc))

    def action_make_applique(self):
        obj = self.canvas.selected
        if obj is None or obj.kind not in ("fill", "satin"):
            QMessageBox.information(self, tr("msg_applique_title"), tr("msg_applique_text"))
            return
        app_objs = create_applique_objects(obj)
        if not app_objs:
            return
        self._snapshot("Applikation erstellen")
        idx = self.canvas.design.objects.index(obj)
        self.canvas.design.objects[idx:idx + 1] = app_objs
        self.canvas.selected = app_objs[-1]
        self.rebuild_plan()

    def action_quality_doctor(self):
        self.wait_for_plan()
        issues = run_quality_doctor(
            self.canvas.design, self.canvas.plan, max_needles=self.canvas.design.settings.needles
        )
        QMessageBox.information(
            self,
            tr("msg_doctor_title"),
            "\n\n".join(issues),
        )

    def action_export_embroidery(self):
        mp: MachineProfile = self.cmb_machine.currentData()
        ext_default = mp.native_ext.upper() if mp else "EXP"
        filters = ";;".join(f"{FORMAT_NAMES.get(e, e.upper())} (*.{e})" for e in WRITE_EXT)
        path = self._ask_save_file(
            tr("fd_export_emb"), f"{self.canvas.design.name}.{ext_default}", filters
        )
        if not path:
            return
        self.wait_for_plan()
        try:
            export_plan(self.canvas.plan, path)
            ext = os.path.splitext(path)[1].lower().lstrip(".")
            if ext in ("exp", "dst", "pes", "jef", "vp3", "xxx", "u01", "pec", "tbf"):
                rep = verify_exported_file(path, self.canvas.plan)
                QMessageBox.information(
                    self,
                    tr("msg_export_verified_title"),
                    tr("msg_export_verified_text").format(
                        path=path, size=fmt_int(rep["bytes"]), stitches=fmt_int(rep["stitches"]),
                        w=rep["width_mm"], h=rep["height_mm"], step=rep["max_step_mm"],
                        colors=rep["color_changes"], jumps=rep["jumps"],
                    ),
                )
            else:
                QMessageBox.information(self, tr("msg_export_ok_title"), tr("msg_export_ok_text").format(path))
        except Exception as exc:
            QMessageBox.critical(self, tr("err_export_title"), str(exc))

    def action_export_pdf(self):
        path = self._ask_save_file(
            tr("fd_save_pdf"), f"{self.canvas.design.name}_{tr('pdf_file_suffix')}.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        self.wait_for_plan()
        try:
            export_worksheet_pdf(self.canvas.design, self.canvas.plan, path)
        except Exception as exc:
            QMessageBox.critical(self, tr("err_pdf_title"), str(exc))
            return
        QMessageBox.information(self, tr("msg_pdf_ok_title"), tr("msg_pdf_ok_text").format(path))

    def action_export_png(self):
        path = self._ask_save_file(
            tr("fd_save_png"), f"{self.canvas.design.name}.png", f"{tr('filter_png')} (*.png)"
        )
        if not path:
            return
        self.wait_for_plan()
        if not render_image(self.canvas.plan, px_per_mm=10.0).save(path):
            QMessageBox.critical(self, tr("err_png_title"), tr("err_png_text").format(path))

    # ---------------------------------------------- Digitalisier-Assistenten
    def action_auto_digitize(self):
        path = self._ask_open_file(
            tr("fd_pick_image"),
            f"{tr('filter_all_img_vec')} (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff *.svg);;"
            f"{tr('filter_raster')} (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff);;"
            f"{tr('filter_svg')} (*.svg);;"
            f"{tr('filter_all_files')} (*.*)",
        )
        if not path:
            return
        if path.lower().endswith(".svg"):
            try:
                d = import_svg(path, target_width_mm=95.0)
                d.hoop = self.canvas.design.hoop
                self.set_design(d, reset_undo=True)
                self.canvas.zoom_to_fit()
            except Exception as exc:
                QMessageBox.critical(self, tr("err_svg_title"), str(exc))
            return
        self._open_auto_digitize_for_path(path)

    def _open_auto_digitize_for_path(self, path: str):
        try:
            dlg = AutoDigitizeDialog(path, self)
        except Exception as exc:
            QMessageBox.critical(self, tr("err_image_title"), str(exc))
            return
        if dlg.exec() == AutoDigitizeDialog.Accepted and dlg.result_data is not None:
            self._snapshot("Auto-Digitalisieren")
            res_d = dlg.result_data.design
            same_mode = res_d.hoop.mode == self.canvas.design.hoop.mode
            res_d.hoop = self.canvas.design.hoop
            res_d.settings = self.canvas.design.settings
            # Vorberechneter Plan gilt nur, wenn die Rahmen-Strategie identisch ist
            self.set_design(res_d, prebuilt_plan=dlg.result_plan if same_mode else None)
            self.canvas.zoom_to_fit()

    def action_photostitch(self):
        path = self._ask_open_file(
            tr("fd_pick_photo"),
            f"{tr('filter_photos')} (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;{tr('filter_all_files')} (*.*)",
        )
        if not path:
            return
        try:
            dlg = PhotoStitchDialog(path, self)
        except Exception as exc:
            QMessageBox.critical(self, tr("err_image_title"), str(exc))
            return
        if dlg.exec() == PhotoStitchDialog.Accepted and dlg.result_design is not None:
            self._snapshot("PhotoStitch")
            res_d = dlg.result_design
            res_d.hoop = self.canvas.design.hoop
            res_d.settings = self.canvas.design.settings
            self.set_design(res_d)
            self.canvas.zoom_to_fit()

    def action_toggle_3d_puff(self):
        obj = self.canvas.selected
        if obj is not None and isinstance(obj, SatinObject):
            self._snapshot("3D-Puff umschalten")
            obj.puff_3d = not obj.puff_3d
            self.rebuild_plan()
            return
        satins = [o for o in self.canvas.design.objects if isinstance(o, SatinObject)]
        if not satins:
            QMessageBox.information(self, tr("msg_puff_title"), tr("msg_puff_text"))
            return
        self._snapshot("3D-Puff für alle Satin-Objekte")
        new_state = not satins[0].puff_3d
        for s in satins:
            s.puff_3d = new_state
        self.rebuild_plan()

    def action_add_text(self):
        dlg = TextDialog(self.canvas.active_thread, parent=self)
        if dlg.exec() == TextDialog.Accepted and dlg.created_object is not None:
            self._snapshot("Text einfügen")
            self.canvas.design.objects.append(dlg.created_object)
            self.canvas.selected = dlg.created_object
            self.rebuild_plan()

    def action_melco_disk(self):
        self.wait_for_plan()
        dlg = MelcoDiskDialog(self.canvas.plan, self.canvas.design.name, self)
        dlg.exec()

    def action_optimize_color_order(self):
        objs = self.canvas.design.objects
        # Nur umsortieren, wo sich nichts überdeckt – die Stapelreihenfolge bleibt sichtbar gleich
        grouped = color_sorted(objs)
        if [o.id for o in grouped] == [o.id for o in objs]:
            return
        self._snapshot("Farbwechsel optimieren")
        self.canvas.design.objects = grouped
        self.rebuild_plan()

    # ------------------------------------------------ Bearbeiten / Undo / Redo
    def action_undo(self):
        if not self._undo_stack:
            return
        desc, prev_objs = self._undo_stack.pop()
        self._redo_stack.append((desc, [o.snapshot() for o in self.canvas.design.objects]))
        self._last_edit_key = None
        sel_id = self.canvas.selected.id if self.canvas.selected is not None else None
        self.canvas.design.objects = prev_objs
        self.canvas.selected = next((o for o in prev_objs if o.id == sel_id), prev_objs[0] if prev_objs else None)
        self.rebuild_plan()

    def action_redo(self):
        if not self._redo_stack:
            return
        desc, next_objs = self._redo_stack.pop()
        self._undo_stack.append((desc, [o.snapshot() for o in self.canvas.design.objects]))
        self._last_edit_key = None
        sel_id = self.canvas.selected.id if self.canvas.selected is not None else None
        self.canvas.design.objects = next_objs
        self.canvas.selected = next((o for o in next_objs if o.id == sel_id), next_objs[0] if next_objs else None)
        self.rebuild_plan()

    def action_duplicate_selected(self):
        if self.canvas.selected is None:
            return
        self._snapshot("Duplizieren")
        clone = self.canvas.selected.clone()
        a, b, d, e, x, y = clone.transform
        clone.transform = (a, b, d, e, x + 5.0, y + 5.0)
        self.canvas.design.objects.append(clone)
        self.canvas.selected = clone
        self.rebuild_plan()

    def action_delete_selected(self):
        if self.canvas.selected in self.canvas.design.objects:
            self._snapshot("Löschen")
            self.canvas.design.objects.remove(self.canvas.selected)
            self.canvas.selected = self.canvas.design.objects[0] if self.canvas.design.objects else None
            self.rebuild_plan()

    def action_center_design(self):
        b = self.canvas.design.bounds()
        if b == (0, 0, 0, 0):
            return
        self._snapshot("Zentrieren")
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        for o in self.canvas.design.objects:
            a, bb, d, e, x, y = o.transform
            o.transform = (a, bb, d, e, x - cx, y - cy)
        self.rebuild_plan()

    def action_scale_design(self):
        from PySide6.QtWidgets import QInputDialog
        dlg = QInputDialog(self)
        dlg.setInputMode(QInputDialog.DoubleInput)
        dlg.setWindowTitle(tr("dlg_scale_title"))
        dlg.setLabelText(tr("dlg_scale_label"))
        dlg.setDoubleDecimals(1)
        dlg.setDoubleRange(20.0, 400.0)
        dlg.setDoubleValue(100.0)
        dlg.setCancelButtonText(tr("btn_cancel"))
        ok = dlg.exec() == QInputDialog.Accepted
        pct = dlg.doubleValue()
        if not ok or abs(pct - 100.0) < 1e-3:
            return
        self._snapshot("Design skalieren")
        s = pct / 100.0
        for o in self.canvas.design.objects:
            a, b, d, e, x, y = o.transform
            o.transform = (a * s, b * s, d * s, e * s, x * s, y * s)
            if isinstance(o, TextObject):
                o.height *= s
                o.letter_spacing *= s
                o.arc_radius *= s
                o.transform = (a, b, d, e, x * s, y * s)
        self.rebuild_plan()

    # ------------------------------------------------------------ Simulator
    def _toggle_sim(self, playing: bool):
        if playing:
            if self.canvas.sim_limit is None or self.canvas.sim_limit >= self.canvas.plan.stitch_count:
                self.canvas.sim_limit = 1
            self.btn_play.setText(tr("btn_pause"))
            self.sim_timer.start()
        else:
            self.btn_play.setText(tr("btn_play"))
            self.sim_timer.stop()

    def _sim_step(self):
        total = self.canvas.plan.stitch_count
        cur = (self.canvas.sim_limit or 0) + self.sp_sim_speed.value()
        if cur >= total:
            self.canvas.sim_limit = None
            self.btn_play.setChecked(False)
            self.slider_sim.setValue(total)
            return
        self.canvas.sim_limit = cur
        self.slider_sim.blockSignals(True)
        self.slider_sim.setValue(cur)
        self.slider_sim.blockSignals(False)
        self.lbl_sim.setText(f"{fmt_int(cur)} / {fmt_int(total)}")
        self.canvas.update()  # sim_limit ist Teil des Cache-Schlüssels

    def _on_sim_slider(self, val: int):
        total = self.canvas.plan.stitch_count
        if val >= total:
            self.canvas.sim_limit = None
            self.lbl_sim.setText(f"{fmt_int(total)} / {fmt_int(total)}")
        else:
            self.canvas.sim_limit = val
            self.lbl_sim.setText(f"{fmt_int(val)} / {fmt_int(total)}")
        self.canvas.update()  # sim_limit ist Teil des Cache-Schlüssels

    def _reset_sim(self):
        self.btn_play.setChecked(False)
        self.canvas.sim_limit = None
        self.slider_sim.setValue(self.canvas.plan.stitch_count)
        self.canvas.update()  # sim_limit ist Teil des Cache-Schlüssels
