"""GPU-beschleunigte Stick-Leinwand (QOpenGLWidget + 3D-Layer-Cache + Stichdichte-Heatmap)."""
from __future__ import annotations

import math
import os
from collections import defaultdict

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
    QSurfaceFormat,
    QWheelEvent,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget
from shapely.geometry import LineString, Point, Polygon

from ..core.design import Design, EmbObject, FillObject, RunObject, SatinObject, compose
from ..core.stitchplan import Cmd, StitchPlan, Thread
from ..render import draw_plan


class StitchCanvas(QWidget):
    selection_changed = Signal(object)       # EmbObject | None
    design_modified = Signal(str)            # Beschreibung für Undo
    about_to_modify = Signal(str)            # Snapshot vor interaktiver Änderung
    tool_changed = Signal(str)               # Synchronisiert Toolbar-Buttons
    cursor_moved = Signal(float, float)      # x_mm, y_mm

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.design: Design = Design()
        self.plan: StitchPlan = StitchPlan()
        self.selected: EmbObject | None = None

        # Ansicht
        self.px_per_mm: float = 3.8
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self.realistic: bool = True
        self.show_jumps: bool = True
        self.show_grid: bool = True
        self.show_hoop: bool = True
        self.show_heatmap: bool = False
        self.fabric_theme: str = "slate"  # 'slate' | 'sand' | 'light'
        self.sim_limit: int | None = None

        # 3D-Render-Cache (verhindert Neuberechnung von 100k Linien bei jedem Maus-Event!)
        self._cache_img: QImage | None = None
        self._cache_key: tuple | None = None
        self._cache_origin_mm: tuple[float, float] = (0.0, 0.0)
        self._cache_px_per_mm: float = 1.0
        self._last_sim_pt: tuple[float, float] | None = None
        self._plan_version: int = 0

        # Werkzeug
        self.tool: str = "select"
        self.active_thread: Thread = Thread((208, 18, 27), "Rot", "043", "Standard")
        self._draw_pts: list[tuple[float, float]] = []
        self._hover_mm: tuple[float, float] = (0.0, 0.0)

        # Maus-Interaktion
        self._panning = False
        self._pan_start = QPointF()
        self._dragging_obj = False
        self._drag_mode = "move"
        self._drag_start_mm = (0.0, 0.0)
        self._orig_transform = None
        self._orig_bounds = None
        self._dragging_node_idx: int | None = None
        self._dragging_angle: bool = False

    def invalidate_render_cache(self):
        self._plan_version += 1
        self._cache_key = None
        self.update()

    # -------------------------------------------------------- Koordinaten
    def mm_to_screen(self, x: float, y: float) -> QPointF:
        cx = self.width() / 2.0 + self.pan_x
        cy = self.height() / 2.0 + self.pan_y
        return QPointF(cx + x * self.px_per_mm, cy + y * self.px_per_mm)

    def screen_to_mm(self, pt: QPointF) -> tuple[float, float]:
        cx = self.width() / 2.0 + self.pan_x
        cy = self.height() / 2.0 + self.pan_y
        return ((pt.x() - cx) / self.px_per_mm, (pt.y() - cy) / self.px_per_mm)

    def zoom_to_fit(self):
        w_mm = max(self.design.hoop.width * 1.15, 60.0)
        h_mm = max(self.design.hoop.height * 1.15, 60.0)
        if self.width() > 50 and self.height() > 50:
            self.px_per_mm = min(self.width() / w_mm, self.height() / h_mm)
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.update()

    # ------------------------------------------------- Schneller Layer-Cache
    def _ensure_stitch_cache(self):
        q_ppm = round(min(self.px_per_mm, 14.0), 1)
        key = (self._plan_version, q_ppm, self.realistic, self.show_jumps, self.sim_limit)
        if self._cache_key == key and self._cache_img is not None:
            return
        x0, y0, x1, y1 = self.plan.bounds()
        pad = 6.0
        w_mm = max(10.0, (x1 - x0) + 2 * pad)
        h_mm = max(10.0, (y1 - y0) + 2 * pad)
        eff_ppm = min(q_ppm, 2800.0 / max(w_mm, h_mm))
        eff_ppm = max(1.5, eff_ppm)
        iw = max(1, int(math.ceil(w_mm * eff_ppm)))
        ih = max(1, int(math.ceil(h_mm * eff_ppm)))

        img = QImage(iw, ih, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        sp = QPainter(img)
        sp.scale(eff_ppm, eff_ppm)
        ox, oy = x0 - pad, y0 - pad
        sp.translate(-ox, -oy)
        self._last_sim_pt = draw_plan(
            sp, self.plan, upto=self.sim_limit, realistic=self.realistic,
            show_jumps=self.show_jumps, px_per_mm=eff_ppm,
        )
        sp.end()

        self._cache_img = img
        self._cache_origin_mm = (ox, oy)
        self._cache_px_per_mm = eff_ppm
        self._cache_key = key

    def _draw_heatmap(self, p: QPainter):
        counts: dict[tuple[int, int], int] = defaultdict(int)
        for b in self.plan.blocks:
            for s in b.stitches:
                if s.cmd == Cmd.STITCH:
                    counts[(int(math.floor(s.x)), int(math.floor(s.y)))] += 1
        p.setPen(Qt.NoPen)
        for (gx, gy), c in counts.items():
            if c <= 6:
                col = QColor(40, 200, 90, 95)
            elif c <= 12:
                col = QColor(255, 195, 0, 145)
            else:
                col = QColor(255, 35, 35, 190)
            p.setBrush(col)
            p.drawRect(QRectF(gx, gy, 1.0, 1.0))

    # ----------------------------------------------------------- Zeichnen
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Weicher, augenfreundlicher Studio-Hintergrund (kein hartes Schwarz)
        p.fillRect(self.rect(), QColor(34, 38, 47))

        p.save()
        p.translate(self.width() / 2.0 + self.pan_x, self.height() / 2.0 + self.pan_y)
        p.scale(self.px_per_mm, self.px_per_mm)

        hw, hh = self.design.hoop.width, self.design.hoop.height
        hoop_rect = QRectF(-hw / 2, -hh / 2, hw, hh)
        hoop_path = QPainterPath()
        if self.design.hoop.round:
            hoop_path.addEllipse(hoop_rect)
        else:
            hoop_path.addRoundedRect(hoop_rect, 8, 8)

        # Harmonischer Stoffhintergrund im Rahmen (ohne blendenden Hell/Dunkel-Schock)
        rad = QRadialGradient(QPointF(0, 0), max(hw, hh) * 0.55)
        if self.fabric_theme == "light":
            rad.setColorAt(0.0, QColor(232, 228, 220))
            rad.setColorAt(1.0, QColor(218, 213, 204))
            grid_col = QColor(195, 190, 180, 140)
            axis_col = QColor(160, 155, 145, 180)
        elif self.fabric_theme == "sand":
            rad.setColorAt(0.0, QColor(196, 190, 178))
            rad.setColorAt(1.0, QColor(180, 174, 162))
            grid_col = QColor(158, 152, 142, 130)
            axis_col = QColor(125, 120, 110, 170)
        else:  # 'slate' (Standard: edles Dark-Studio-Tuch, sanfter Kontrast)
            rad.setColorAt(0.0, QColor(58, 65, 80))
            rad.setColorAt(1.0, QColor(47, 53, 66))
            grid_col = QColor(255, 255, 255, 22)
            axis_col = QColor(160, 185, 230, 65)

        p.setPen(Qt.NoPen)
        p.fillPath(hoop_path, rad)

        if self.show_grid:
            p.save()
            p.setClipPath(hoop_path)
            pen_grid = QPen(grid_col, 0)
            pen_grid.setCosmetic(True)
            p.setPen(pen_grid)
            gx0 = int(-hw // 2 // 10) * 10
            gx1 = int(hw // 2 // 10) * 10
            gy0 = int(-hh // 2 // 10) * 10
            gy1 = int(hh // 2 // 10) * 10
            for x in range(gx0, gx1 + 1, 10):
                p.drawLine(QPointF(x, -hh / 2), QPointF(x, hh / 2))
            for y in range(gy0, gy1 + 1, 10):
                p.drawLine(QPointF(-hw / 2, y), QPointF(hw / 2, y))
            pen_axis = QPen(axis_col, 0, Qt.DashLine)
            pen_axis.setCosmetic(True)
            p.setPen(pen_axis)
            p.drawLine(QPointF(-hw / 2, 0), QPointF(hw / 2, 0))
            p.drawLine(QPointF(0, -hh / 2), QPointF(0, hh / 2))
            p.restore()

        if self.show_hoop:
            # Sanfter Doppelring für den Stickrahmen
            pen_outer = QPen(QColor(95, 140, 215, 190), 2.2)
            pen_outer.setCosmetic(True)
            p.setPen(pen_outer)
            p.setBrush(Qt.NoBrush)
            p.drawPath(hoop_path)
            # Gestrichelte innere Sicherheitsgrenze (Presserfuss-Abstand zum Rahmen)
            mg = getattr(self.design.hoop, "margin_mm", 4.0)
            safe_rect = QRectF(-hw / 2 + mg, -hh / 2 + mg, hw - 2 * mg, hh - 2 * mg)
            pen_safe = QPen(QColor(235, 175, 85, 110), 1.0, Qt.DashLine)
            pen_safe.setCosmetic(True)
            p.setPen(pen_safe)
            if self.design.hoop.round:
                p.drawEllipse(safe_rect)
            else:
                p.drawRoundedRect(safe_rect, 6, 6)
            # Bei Kappenrahmen: rote Mittennaht-Hilfslinie & Schirm-Markierung unten anzeigen
            if getattr(self.design.hoop, "mode", "") == "cap":
                pen_cap = QPen(QColor(230, 105, 105, 140), 1.2, Qt.DotLine)
                pen_cap.setCosmetic(True)
                p.setPen(pen_cap)
                p.drawLine(QPointF(0, -hh / 2), QPointF(0, hh / 2))

        if self.plan.blocks:
            self._ensure_stitch_cache()
            if self._cache_img is not None:
                ox, oy = self._cache_origin_mm
                w_mm = self._cache_img.width() / self._cache_px_per_mm
                h_mm = self._cache_img.height() / self._cache_px_per_mm
                p.drawImage(QRectF(ox, oy, w_mm, h_mm), self._cache_img)

        if self.show_heatmap:
            self._draw_heatmap(p)

        if self.sim_limit is not None and self._last_sim_pt is not None:
            nx, ny = self._last_sim_pt
            pen_n = QPen(QColor(242, 139, 130), 2.0)
            pen_n.setCosmetic(True)
            p.setPen(pen_n)
            r = 6.0 / self.px_per_mm
            p.drawEllipse(QPointF(nx, ny), r, r)
            p.drawLine(QPointF(nx - r * 1.6, ny), QPointF(nx + r * 1.6, ny))
            p.drawLine(QPointF(nx, ny - r * 1.6), QPointF(nx, ny + r * 1.6))

        if self.selected is not None and self.selected in self.design.objects:
            b = self.selected.bounds()
            if b != (0, 0, 0, 0):
                pen_sel = QPen(QColor(138, 180, 248, 210), 1.5, Qt.DashLine)
                pen_sel.setCosmetic(True)
                p.setPen(pen_sel)
                p.setBrush(Qt.NoBrush)
                rect = QRectF(b[0] - 1.0, b[1] - 1.0, (b[2] - b[0]) + 2.0, (b[3] - b[1]) + 2.0)
                p.drawRect(rect)
                hr = 4.5 / self.px_per_mm
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(138, 180, 248))
                p.drawRoundedRect(QRectF(rect.right() - hr, rect.bottom() - hr, hr * 2, hr * 2), hr * 0.4, hr * 0.4)

                # Im Knoten- & Stichwinkel-Editor ("edit_nodes"):
                if self.tool == "edit_nodes":
                    nodes = self._get_editable_nodes(self.selected)
                    nr = 4.2 / self.px_per_mm
                    pen_poly = QPen(QColor(138, 180, 248, 200), 1.5)
                    pen_poly.setCosmetic(True)
                    p.setPen(pen_poly)
                    for a, b_pt in zip(nodes, nodes[1:]):
                        p.drawLine(QPointF(*a), QPointF(*b_pt))
                    p.setBrush(QColor(240, 244, 250))
                    for nx, ny in nodes:
                        p.drawRect(QRectF(nx - nr, ny - nr, nr * 2, nr * 2))

                    if hasattr(self.selected, "angle"):
                        cx, cy = (b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0
                        arm = max(14.0, min(b[2] - b[0], b[3] - b[1]) * 0.45)
                        ang_rad = math.radians(self.selected.angle)
                        ax = cx + math.cos(ang_rad) * arm
                        ay = cy + math.sin(ang_rad) * arm
                        bx = cx - math.cos(ang_rad) * arm
                        by = cy - math.sin(ang_rad) * arm
                        pen_ang = QPen(QColor(253, 214, 99), 2.4)
                        pen_ang.setCosmetic(True)
                        p.setPen(pen_ang)
                        p.drawLine(QPointF(bx, by), QPointF(ax, ay))
                        p.setBrush(QColor(253, 214, 99))
                        p.drawEllipse(QPointF(ax, ay), nr * 1.4, nr * 1.4)

        if self._draw_pts:
            pen_d = QPen(QColor(253, 214, 99), 2.0)
            pen_d.setCosmetic(True)
            p.setPen(pen_d)
            pts_all = self._draw_pts + [self._hover_mm]
            for a, b in zip(pts_all, pts_all[1:]):
                p.drawLine(QPointF(*a), QPointF(*b))
            r = 3.5 / self.px_per_mm
            p.setBrush(QColor(253, 214, 99))
            for x, y in self._draw_pts:
                p.drawEllipse(QPointF(x, y), r, r)

        p.restore()

        # Dezentes HUD-Pill-Badge oben links auf der Leinwand
        tool_names = {
            "select": "Auswahl (V)  ·  Ziehen = Verschieben, Eckgriff = Skalieren, Mausrad = Zoom",
            "edit_nodes": "Knoten & Stichwinkel (N)  ·  Weisse Knoten = Kontur ändern, Gelber Griff = Stichwinkel drehen",
            "draw_fill": "Tatami-Fläche zeichnen (F)  ·  Klick = Punkt setzen, Doppelklick/Enter = Fertig",
            "draw_satin": "Satin-Säule zeichnen (S)  ·  Klick = Punkt setzen, Doppelklick/Enter = Fertig",
            "draw_run": "Steppstich-Pfad zeichnen (R)  ·  Klick = Punkt setzen, Doppelklick/Enter = Fertig",
        }
        hud_text = tool_names.get(self.tool, "")
        p.setFont(QFont("Segoe UI", 8.5))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(hud_text) + 22
        hud_rect = QRectF(12, 10, tw, 24)
        p.setPen(QPen(QColor(68, 76, 94, 150), 1))
        p.setBrush(QColor(38, 43, 54, 210))
        p.drawRoundedRect(hud_rect, 12, 12)
        p.setPen(QColor(186, 195, 212))
        p.drawText(hud_rect, Qt.AlignCenter, hud_text)

    # --------------------------------------------------------- Maus / Key
    def wheelEvent(self, event: QWheelEvent):
        before = self.screen_to_mm(event.position())
        factor = 1.18 if event.angleDelta().y() > 0 else 1 / 1.18
        self.px_per_mm = max(0.5, min(60.0, self.px_per_mm * factor))
        after = self.screen_to_mm(event.position())
        self.pan_x += (after[0] - before[0]) * self.px_per_mm
        self.pan_y += (after[1] - before[1]) * self.px_per_mm
        self.update()

    def mousePressEvent(self, event):
        mm = self.screen_to_mm(event.position())
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier):
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            return

        if event.button() == Qt.RightButton and self._draw_pts:
            self._finish_drawing()
            return

        if event.button() == Qt.LeftButton:
            if self.tool == "edit_nodes" and self.selected is not None:
                # 1. Prüfen ob gelber Stichwinkel-Griff getroffen wurde
                b = self.selected.bounds()
                if hasattr(self.selected, "angle") and b != (0, 0, 0, 0):
                    cx, cy = (b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0
                    arm = max(14.0, min(b[2] - b[0], b[3] - b[1]) * 0.45)
                    ang_rad = math.radians(self.selected.angle)
                    ax = cx + math.cos(ang_rad) * arm
                    ay = cy + math.sin(ang_rad) * arm
                    if math.hypot(mm[0] - ax, mm[1] - ay) <= 9.0 / self.px_per_mm:
                        self.about_to_modify.emit("Stichwinkel drehen")
                        self._dragging_angle = True
                        return
                # 2. Prüfen ob ein Konturknoten getroffen wurde
                nodes = self._get_editable_nodes(self.selected)
                for idx, (nx, ny) in enumerate(nodes):
                    if math.hypot(mm[0] - nx, mm[1] - ny) <= 8.0 / self.px_per_mm:
                        self.about_to_modify.emit("Knoten verschieben")
                        self._dragging_node_idx = idx
                        return

            if self.tool not in ("select", "edit_nodes"):
                self._draw_pts.append(mm)
                self.update()
                return

            if self.selected is not None and self.selected in self.design.objects:
                b = self.selected.bounds()
                if b != (0, 0, 0, 0):
                    hx, hy = b[2] + 1.0, b[3] + 1.0
                    if math.hypot(mm[0] - hx, mm[1] - hy) <= 8.0 / self.px_per_mm:
                        self.about_to_modify.emit("Objekt skalieren")
                        self._dragging_obj = True
                        self._drag_mode = "scale"
                        self._drag_start_mm = mm
                        self._orig_transform = self.selected.transform
                        self._orig_bounds = b
                        return

            pt = Point(mm)
            hit = None
            for obj in reversed(self.design.objects):
                if not obj.visible:
                    continue
                g = obj.world_geom()
                if g is not None and not g.is_empty and g.distance(pt) <= max(1.5, 5.0 / self.px_per_mm):
                    hit = obj
                    break
            self.selected = hit
            self.selection_changed.emit(hit)
            if hit is not None:
                self._dragging_obj = True
                self._drag_mode = "move"
                self._drag_start_mm = mm
                self._orig_transform = hit.transform
                self._orig_bounds = hit.bounds()
                self._move_snapshot_taken = False
            self.update()

    def mouseDoubleClickEvent(self, event):
        if self.tool != "select" and self._draw_pts:
            self._finish_drawing()

    def mouseMoveEvent(self, event):
        mm = self.screen_to_mm(event.position())
        self._hover_mm = mm
        self.cursor_moved.emit(mm[0], mm[1])
        if self._panning:
            d = event.position() - self._pan_start
            self._pan_start = event.position()
            self.pan_x += d.x()
            self.pan_y += d.y()
            self.update()
            return
        if self._dragging_angle and self.selected is not None and hasattr(self.selected, "angle"):
            b = self.selected.bounds()
            cx, cy = (b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0
            self.selected.angle = round(math.degrees(math.atan2(mm[1] - cy, mm[0] - cx)), 1)
            self.update()
            return
        if self._dragging_node_idx is not None and self.selected is not None:
            self._move_editable_node(self.selected, self._dragging_node_idx, mm)
            self.update()
            return
        if self._dragging_obj and self.selected is not None:
            dx = mm[0] - self._drag_start_mm[0]
            dy = mm[1] - self._drag_start_mm[1]
            if self._drag_mode == "move":
                if not getattr(self, "_move_snapshot_taken", False) and math.hypot(dx, dy) > 0.2:
                    self._move_snapshot_taken = True
                    self.about_to_modify.emit("Objekt verschieben")
                self.selected.transform = compose((1, 0, 0, 1, dx, dy), self._orig_transform)
            elif self._drag_mode == "scale":
                b = self._orig_bounds
                cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
                w0 = max(b[2] - b[0], 1.0)
                h0 = max(b[3] - b[1], 1.0)
                s = max(0.15, min(8.0, 1.0 + max(dx / w0, dy / h0) * 2.0))
                t1 = (1, 0, 0, 1, -cx, -cy)
                ts = (s, 0, 0, s, 0, 0)
                t2 = (1, 0, 0, 1, cx, cy)
                self.selected.transform = compose(t2, compose(ts, compose(t1, self._orig_transform)))
            self.update()
            return
        if self._draw_pts:
            self.update()

    def mouseReleaseEvent(self, event):
        if self._panning:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
        if self._dragging_angle:
            self._dragging_angle = False
            self.design_modified.emit("Stichwinkel drehen")
        if self._dragging_node_idx is not None:
            self._dragging_node_idx = None
            self.design_modified.emit("Knoten verschieben")
        if self._dragging_obj:
            self._dragging_obj = False
            if self.selected is not None and self.selected.transform != self._orig_transform:
                self.design_modified.emit("Objekt transformieren")

    def _get_editable_nodes(self, obj: EmbObject) -> list[tuple[float, float]]:
        g = obj.world_geom()
        if g is None or g.is_empty:
            return []
        from ..engine.geom import polygons_of, lines_of
        polys = polygons_of(g)
        if polys:
            # Vereinfachte Konturknoten des Hauptpolygons
            simp = polys[0].simplify(0.45, preserve_topology=True)
            if isinstance(simp, Polygon) and not simp.is_empty:
                return [(float(x), float(y)) for x, y in simp.exterior.coords]
            return [(float(x), float(y)) for x, y in polys[0].exterior.coords]
        lns = lines_of(g)
        if lns:
            return [(float(x), float(y)) for x, y in lns[0].coords]
        return []

    def _move_editable_node(self, obj: EmbObject, idx: int, new_mm: tuple[float, float]):
        from ..core.design import IDENTITY
        from ..engine.geom import polygons_of, lines_of
        g = obj.world_geom()
        polys = polygons_of(g)
        if polys:
            simp = polys[0].simplify(0.45, preserve_topology=True)
            base_poly = simp if (isinstance(simp, Polygon) and not simp.is_empty) else polys[0]
            coords = list(base_poly.exterior.coords)
            if 0 <= idx < len(coords):
                coords[idx] = new_mm
                if idx == 0 or idx == len(coords) - 1:
                    coords[0] = coords[-1] = new_mm
                try:
                    new_p = Polygon(coords, list(base_poly.interiors)).buffer(0)
                    if not new_p.is_empty:
                        obj.geom = new_p
                        obj.transform = IDENTITY
                except Exception:
                    pass
            return
        lns = lines_of(g)
        if lns:
            coords = list(lns[0].coords)
            if 0 <= idx < len(coords):
                coords[idx] = new_mm
                obj.geom = LineString(coords)
                obj.transform = IDENTITY

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and self._draw_pts:
            self._finish_drawing()
        elif event.key() == Qt.Key_Escape and self._draw_pts:
            self._draw_pts.clear()
            self.tool = "select"
            self.tool_changed.emit("select")
            self.update()
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace) and self.selected is not None:
            if self.selected in self.design.objects:
                self.about_to_modify.emit("Objekt löschen")
                self.design.objects.remove(self.selected)
                self.selected = None
                self.selection_changed.emit(None)
                self.design_modified.emit("Objekt löschen")
        elif not self._draw_pts and event.modifiers() == Qt.NoModifier:
            key_tool = {
                Qt.Key_V: "select",
                Qt.Key_N: "edit_nodes",
                Qt.Key_F: "draw_fill",
                Qt.Key_S: "draw_satin",
                Qt.Key_R: "draw_run",
            }.get(event.key())
            if key_tool:
                self.tool = key_tool
                self.tool_changed.emit(key_tool)
                self.update()

    def _finish_drawing(self):
        pts = list(self._draw_pts)
        self._draw_pts.clear()
        t = self.tool
        self.tool = "select"
        self.tool_changed.emit("select")
        if t == "draw_fill" and len(pts) >= 3:
            poly = Polygon(pts).buffer(0)
            if not poly.is_empty and poly.area >= 1.0:
                self.about_to_modify.emit("Fläche zeichnen")
                obj = FillObject(self.active_thread, name="Freihand-Fläche", geom=poly)
                self.design.objects.append(obj)
                self.selected = obj
                self.selection_changed.emit(obj)
                self.design_modified.emit("Fläche zeichnen")
        elif t == "draw_satin" and len(pts) >= 2:
            line = LineString(pts)
            if line.length >= 1.0:
                self.about_to_modify.emit("Satin zeichnen")
                obj = SatinObject(self.active_thread, name="Freihand-Satin", geom=line.buffer(1.6, cap_style=2))
                self.design.objects.append(obj)
                self.selected = obj
                self.selection_changed.emit(obj)
                self.design_modified.emit("Satin zeichnen")
        elif t == "draw_run" and len(pts) >= 2:
            line = LineString(pts)
            if line.length >= 1.0:
                self.about_to_modify.emit("Steppstich zeichnen")
                obj = RunObject(self.active_thread, name="Steppstich-Pfad", geom=line, repeats=1)
                self.design.objects.append(obj)
                self.selected = obj
                self.selection_changed.emit(obj)
                self.design_modified.emit("Steppstich zeichnen")
        self.update()
