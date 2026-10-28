"""Automatisierte Tests für OpenStitch."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np
from PySide6.QtWidgets import QApplication
from shapely.geometry import LineString, Point, box

from openstitch.auto.digitize import AutoParams, auto_digitize
from openstitch.core.design import Design, FillObject, RunObject, SatinObject
from openstitch.core.stitchplan import Thread
from openstitch.io.exp import exp_bytes
from openstitch.io.fat12 import IMAGE_SIZE, Fat12Image
from openstitch.io.formats import export_plan, import_file, verify_exported_file
from openstitch.io.project import export_worksheet_pdf, load_project, save_project
from openstitch.text import TextObject
from openstitch.ui.main_window import MainWindow
from openstitch.core.machines import MACHINE_PROFILES
from openstitch.engine.pro_tools import create_applique_objects, import_svg, run_quality_doctor
from openstitch.auto.photostitch import PhotoStitchParams, generate_photostitch

_app = QApplication.instance() or QApplication(sys.argv)


def test_engine_and_formats(tmp_path):
    d = Design(name="TestDesign")
    d.objects.append(FillObject(Thread((200, 20, 20), "Rot"), geom=Point(0, 0).buffer(18), angle=30))
    d.objects.append(SatinObject(Thread((20, 40, 200), "Blau"), geom=LineString([(-15, 0), (15, 0)]).buffer(2.2)))
    d.objects.append(RunObject(Thread((20, 20, 20), "Schwarz"), geom=box(-20, -20, 20, 20).exterior, repeats=1))
    d.objects.append(TextObject(Thread((240, 200, 20), "Gold"), text="AB", height=12.0))

    plan = d.build_plan()
    assert plan.stitch_count > 500
    assert len(plan.blocks) == 4

    # Projekt speichern & laden
    proj_file = str(tmp_path / "test.ostitch")
    save_project(d, proj_file)
    d2 = load_project(proj_file)
    assert len(d2.objects) == 4

    # Melco EXP & Tajima DST exportieren + wieder importieren
    exp_file = str(tmp_path / "TEST.EXP")
    dst_file = str(tmp_path / "TEST.DST")
    export_plan(plan, exp_file, trim_mode="both")
    export_plan(plan, dst_file)
    d_imp = import_file(exp_file)
    assert len(d_imp.objects) >= 1

    # PDF-Produktionsblatt
    pdf_file = str(tmp_path / "sheet.pdf")
    export_worksheet_pdf(d, plan, pdf_file)
    assert os.path.getsize(pdf_file) > 1000


def test_fat12_floppy_image():
    img = Fat12Image()
    raw = b"\x10\x10\x80\x80\x07\x00" * 50
    saved_name = img.add_file("mein_logo.exp", raw)
    assert saved_name == "MEIN_LOG.EXP"
    assert len(img.to_bytes()) == IMAGE_SIZE
    img2 = Fat12Image(img.to_bytes())
    assert img2.read_file("MEIN_LOG.EXP") == raw
    assert img2.delete_file("MEIN_LOG.EXP") is True
    assert img2.list_files() == []


def test_auto_digitizer_and_gui():
    rgba = np.full((240, 320, 4), 255, dtype=np.uint8)
    cv2.circle(rgba, (160, 120), 85, (210, 40, 40, 255), -1)
    cv2.putText(rgba, "OK", (110, 140), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255, 255), 8)
    res = auto_digitize(rgba, AutoParams(width_mm=60, colors=3))
    plan = res.design.build_plan()
    assert plan.stitch_count > 300
    assert len(exp_bytes(plan)) > 600

    win = MainWindow()
    win.wait_for_plan()
    assert win.canvas.plan.stitch_count > 500
    issues = run_quality_doctor(win.canvas.design, win.canvas.plan, max_needles=10)
    assert len(issues) >= 1
    app_objs = create_applique_objects(win.canvas.design.objects[0])
    assert len(app_objs) == 3
    assert len(MACHINE_PROFILES) >= 8

    # Contour-Fill + 3D-Puff-Foam + PhotoStitch testen
    c_fill = FillObject(Thread((30, 160, 60), "Grün"), geom=Point(0, 0).buffer(12), pattern="kontur")
    assert len(c_fill.runs()) >= 1
    puff_satin = SatinObject(Thread((200, 30, 30), "Rot"), geom=LineString([(-12, 0), (12, 0)]).buffer(2.2), puff_3d=True)
    assert len(puff_satin.runs()) >= 1
    ps_design = generate_photostitch(rgba, PhotoStitchParams(width_mm=60, mode="mono"))
    assert ps_design.build_plan().stitch_count > 100
    win.close()


def test_all_machine_formats_binary_verification(tmp_path):
    """Exportiert ein komplexes Design in alle wichtigen Binärformate und verifiziert sie unabhängig."""
    win = MainWindow(show_tour_on_init=False)
    plan = win.wait_for_plan()
    assert plan.stitch_count > 4000

    for ext in ("exp", "dst", "pes", "jef", "vp3", "xxx", "u01"):
        out_path = str(tmp_path / f"OpenStitch_Logo.{ext}")
        export_plan(plan, out_path)
        rep = verify_exported_file(out_path, plan)
        assert rep["stitches"] >= int(plan.stitch_count * 0.90)
        assert rep["bytes"] > 1000
        # Auch den vollständigen Re-Import in ein editierbares OpenStitch-Design prüfen:
        reimp = import_file(out_path)
        assert len(reimp.objects) >= 1
        assert reimp.build_plan().stitch_count >= int(plan.stitch_count * 0.85)
    win.close()


def test_interactive_gui_usage_and_undo_redo():
    """Simuliert echte Maus- und Tastaturbedienung auf der Leinwand inkl. Undo/Redo-Konsistenz."""
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QKeyEvent, QMouseEvent

    win = MainWindow(show_tour_on_init=False)
    canvas = win.canvas
    initial_count = len(canvas.design.objects)

    # 1. Tastenkürzel 'F' auf der Leinwand drücken → Werkzeug wechselt synchron zu Tatami-Fläche
    ev_f = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_F, Qt.NoModifier, "f")
    canvas.keyPressEvent(ev_f)
    assert canvas.tool == "draw_fill"
    assert win.act_tool_fill.isChecked() is True

    # 2. Ein Dreieck auf der Leinwand zeichnen und mit Enter abschließen
    canvas._draw_pts = [(-15.0, -15.0), (15.0, -15.0), (0.0, 15.0)]
    ev_enter = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Return, Qt.NoModifier, "\r")
    canvas.keyPressEvent(ev_enter)
    assert len(canvas.design.objects) == initial_count + 1
    assert canvas.tool == "select"
    assert win.act_tool_select.isChecked() is True

    # 3. Undo (Strg+Z) muss das gezeichnete Dreieck wieder entfernen!
    win.action_undo()
    assert len(canvas.design.objects) == initial_count

    # 4. Redo (Strg+Y) stellt es wieder her
    win.action_redo()
    assert len(canvas.design.objects) == initial_count + 1

    # 5. Entf-Taste auf der Leinwand löscht das ausgewählte Objekt (mit Undo-Snapshot)
    ev_del = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier, "")
    canvas.keyPressEvent(ev_del)
    assert len(canvas.design.objects) == initial_count
    win.action_undo()
    assert len(canvas.design.objects) == initial_count + 1
    win.close()



def test_language_switch_and_thread_catalogs():
    from openstitch.auto.palette import CATALOG_PALETTES, nearest_thread, set_active_palette
    from openstitch.i18n import set_lang, tr

    names = [p.name for p in CATALOG_PALETTES]
    assert any("Madeira" in n for n in names) and any("Isacord" in n for n in names)
    assert any("Gunold" in n for n in names) and any("Brother" in n for n in names)
    for pal in CATALOG_PALETTES:
        assert len(pal.threads) >= 25
        set_active_palette(pal)
        t = nearest_thread((200, 20, 30))
        assert t.code and t.brand

    win = MainWindow(show_tour_on_init=False)
    for lang, expected in (("en", "Machine:"), ("fr", "Machine :"), ("es", "Máquina:"), ("de", "Maschine:")):
        win.cmb_lang.setCurrentIndex(next(i for i in range(win.cmb_lang.count()) if win.cmb_lang.itemData(i) == lang))
        assert tr("lbl_machine") == expected
        assert win.btn_play.text() == tr("btn_play")
    # Katalogwechsel baut das Farbfeld neu auf
    win.cmb_catalog.setCurrentIndex(1)
    assert win.swatch_grid.count() >= 25
    set_lang("de")
    win.close()


def _max_stitch_len(plan):
    import math
    from openstitch.core.stitchplan import Cmd
    longest = 0.0
    for b in plan.blocks:
        prev = None
        for s in b.stitches:
            if s.cmd == Cmd.STITCH and prev is not None:
                longest = max(longest, math.hypot(s.x - prev[0], s.y - prev[1]))
            if s.cmd in (Cmd.STITCH, Cmd.JUMP):
                prev = (s.x, s.y)
    return longest


def test_no_stray_stitches_after_trim():
    """Nach Trim + Sprung darf die Nadel nicht von der alten Position aus weiternähen."""
    t = Thread((200, 30, 30), "Rot")
    for obj in (SatinObject(t, geom=LineString([(-30, 0), (30, 0)]).buffer(2.5)),
                FillObject(t, geom=Point(0, 0).buffer(30), angle=30)):
        d = Design()
        d.objects.append(obj)
        plan = d.build_plan()
        assert plan.trim_count >= 1
        assert _max_stitch_len(plan) <= d.settings.max_stitch + 1e-6


def test_undo_keeps_ids_and_coalesces_spinbox_edits():
    win = MainWindow(show_tour_on_init=False)
    d = win.canvas.design
    obj = next(o for o in d.objects if o.kind == "fill")
    win.canvas.selected = obj
    ids_before = [o.id for o in d.objects]
    depth = len(win._undo_stack)
    # Spinbox-Ziehen: viele valueChanged-Signale → genau ein Undo-Schritt
    for v in (0.45, 0.46, 0.47, 0.48):
        win._set_obj_attr(obj, "spacing", v)
    win._set_obj_attr(obj, "spacing", 0.48)  # unverändert → kein Snapshot
    assert len(win._undo_stack) == depth + 1
    win.action_undo()
    assert [o.id for o in d.objects] == ids_before
    assert win.canvas.selected.id == obj.id
    restored = next(o for o in d.objects if o.id == obj.id)
    assert restored.spacing != 0.48
    win.close()


def test_loaded_design_syncs_hoop_combo(tmp_path):
    from openstitch.core.design import HOOPS
    win = MainWindow(show_tour_on_init=False)
    d = Design(name="Jacke")
    d.hoop = HOOPS[8]
    d.objects.append(FillObject(Thread((10, 10, 10)), geom=Point(0, 0).buffer(10)))
    path = str(tmp_path / "jacke.ostitch")
    save_project(d, path)
    win.set_design(load_project(path), reset_undo=True)
    assert win.cmb_hoop.currentData() is win.canvas.design.hoop
    assert win.canvas.design.hoop.mode == "jacket"
    win.close()


def test_fit_to_hoop_keeps_text_scale():
    win = MainWindow(show_tour_on_init=False)
    t = TextObject(Thread((0, 0, 0)), text="AB", height=10.0)
    t.transform = (2.0, 0.0, 0.0, 2.0, 0.0, 0.0)  # per Griff auf 200 % gezogen
    win.set_design(Design(objects=[t]), reset_undo=True)
    from openstitch.core.design import m_scale
    h_before = t.height
    w_before = t.bounds()[2] - t.bounds()[0]
    win.action_fit_to_hoop()
    obj = win.canvas.design.objects[0]
    s = obj.height / h_before
    # Der Einpass-Faktor landet in height, die per Griff gezogenen 200 % bleiben im Transform
    assert abs(m_scale(obj.transform) - 2.0) < 1e-6
    w_after = obj.bounds()[2] - obj.bounds()[0]
    assert abs(w_after - w_before * s) < 0.05 * w_after
    win.close()


def test_single_objects_need_no_internal_trims():
    """Unterlage → Deckstich und Satin-Endkappen → Säule laufen verdeckt, ohne Trim."""
    t = Thread((200, 30, 30), "Rot")
    for obj in (FillObject(t, geom=Point(0, 0).buffer(30), angle=30),
                SatinObject(t, geom=LineString([(-30, 0), (30, 0)]).buffer(2.5))):
        d = Design()
        d.objects.append(obj)
        plan = d.build_plan()
        assert plan.trim_count == 1  # nur der Schlussschnitt
        assert _max_stitch_len(plan) <= d.settings.max_stitch + 1e-6


def test_plan_is_built_in_background():
    """Editieren blockiert nicht: der Plan wird im Hintergrund gerechnet und danach übernommen."""
    win = MainWindow(show_tour_on_init=False)
    win.wait_for_plan()
    before = win.canvas.plan
    obj = next(o for o in win.canvas.design.objects if o.kind == "fill")
    win._snapshot("test")
    obj.spacing = 0.8
    win.rebuild_plan()
    plan = win.wait_for_plan()
    assert plan is not before and plan.stitch_count < before.stitch_count
    # mehrere schnelle Änderungen: nur der neueste Stand wird übernommen
    for sp in (0.5, 0.6, 0.7):
        obj.spacing = sp
        win.rebuild_plan()
    final = win.wait_for_plan()
    d = Design(objects=[o.snapshot() for o in win.canvas.design.objects], hoop=win.canvas.design.hoop)
    assert final.stitch_count == d.build_plan().stitch_count
    win.close()


def test_density_guard_keeps_fill_turn_points():
    """Reihenwende-Punkte am Rand sind keine Mikrostiche – sonst franst die Kontur aus."""
    import math
    from openstitch.core.stitchplan import Cmd, Stitch
    from openstitch.engine.density_guard import optimize_stitches_for_melco
    zig = [Stitch(0, -1, Cmd.JUMP)]
    for k in range(20):  # Tatami-artige Reihen im Abstand 0.4 mm
        y = k * 0.4
        xs = (0.0, 10.0) if k % 2 == 0 else (10.0, 0.0)
        zig += [Stitch(xs[0], y), Stitch(5.0, y), Stitch(xs[1], y)]
    out = optimize_stitches_for_melco(zig)
    ends = [s for s in out if s.cmd == Cmd.STITCH and s.x in (0.0, 10.0)]
    assert len(ends) == 40
    # echte Mikrostiche auf gerader Strecke werden weiterhin entfernt
    line = [Stitch(0, 0, Cmd.JUMP), Stitch(1, 0), Stitch(1.1, 0), Stitch(2, 0), Stitch(3, 0)]
    assert len(optimize_stitches_for_melco(line)) == 4


def test_satin_underlay_styles():
    from openstitch.engine.satin import auto_underlay_style
    assert auto_underlay_style(1.5) == "mitte"
    assert auto_underlay_style(3.5) == "kante"
    assert auto_underlay_style(6.0) == "kante+zickzack"
    t = Thread((20, 40, 200), "Blau")
    counts = {}
    for style in ("mitte", "kante", "zickzack", "kante+zickzack"):
        o = SatinObject(t, geom=LineString([(-20, 0), (20, 0)]).buffer(3.0), underlay_style=style)
        d = Design(objects=[o])
        plan = d.build_plan()
        counts[style] = plan.stitch_count
        assert plan.trim_count == 1 and _max_stitch_len(plan) <= d.settings.max_stitch
    # Kantenlauf läuft hin und zurück → mehr Stiche als nur die Mitte
    assert counts["kante"] > counts["mitte"] and counts["kante+zickzack"] > counts["kante"]
    # alte Projekte ohne underlay_style laden weiter (Default "auto")
    from openstitch.core.design import object_from_dict
    dct = SatinObject(t, geom=Point(0, 0).buffer(2)).to_dict()
    dct.pop("underlay_style")
    assert object_from_dict(dct).underlay_style == "auto"


def test_jef_export_keeps_trims(tmp_path):
    import pyembroidery as pe
    d = Design()
    t = Thread((200, 30, 30), "Rot")
    for x in (-30, 0, 30):  # drei getrennte Flächen gleicher Farbe → Trims dazwischen
        d.objects.append(FillObject(t, geom=Point(x, 0).buffer(6)))
    plan = d.build_plan()
    path = str(tmp_path / "t.jef")
    export_plan(plan, path)
    raw = open(path, "rb").read()
    assert raw.count(b"\x80\x02\x00\x00\x80\x02\x00\x00\x80\x02\x00\x00") >= plan.trim_count - 1


def test_color_sort_respects_overlaps():
    from openstitch.core.design import color_sorted
    red, blue = Thread((200, 0, 0)), Thread((0, 0, 200))
    a = FillObject(red, geom=Point(-30, 0).buffer(5))
    b = FillObject(blue, geom=Point(0, 0).buffer(5))
    c = FillObject(red, geom=Point(30, 0).buffer(5))
    assert [o.id for o in color_sorted([a, b, c])] == [a.id, c.id, b.id]
    # c liegt jetzt auf b → darf nicht unter b rutschen
    c2 = FillObject(red, geom=Point(4, 0).buffer(5))
    assert [o.id for o in color_sorted([a, b, c2])] == [a.id, b.id, c2.id]


def test_quality_doctor_round_hoop_uses_real_radius():
    from openstitch.core.design import HOOPS
    d = Design(objects=[FillObject(Thread((1, 1, 1)), geom=Point(0, 0).buffer(64))])
    d.hoop = HOOPS[2]  # rund 15 cm → Radius 75 mm; Kreis r=64 passt (Bounding-Box-Ecke wäre 90 mm)
    issues = run_quality_doctor(d, d.build_plan(), max_needles=10)
    assert len(issues) == 1 and issues[0].startswith("✅")


def test_column_object_stitches_perpendicular_and_round_trips(tmp_path):
    import math
    from openstitch.core.design import ColumnObject
    from openstitch.core.stitchplan import Cmd
    line = LineString([(-20, 0), (0, 0), (15, 10)])
    col = ColumnObject(Thread((10, 120, 60), "Grün"), geom=line, width=3.0)
    d = Design(objects=[col])
    plan = d.build_plan()
    assert plan.stitch_count > 100 and _max_stitch_len(plan) <= d.settings.max_stitch + 1e-6
    # Auf dem geraden Stück (x < -3) stehen die Satinstiche senkrecht zur Linie (also vertikal)
    pts = [(s.x, s.y) for s in plan.blocks[0].stitches if s.cmd == Cmd.STITCH]
    vertical = [abs(b[1] - a[1]) / max(1e-9, math.dist(a, b)) for a, b in zip(pts, pts[1:])
                if -17 < a[0] < -3 and -17 < b[0] < -3 and math.dist(a, b) > 2.5]
    assert vertical and sum(vertical) / len(vertical) > 0.95
    assert col.bounds()[3] - col.bounds()[1] > 3.0 * 0.9 + 10  # Breite fliesst in die Bounds ein
    path = str(tmp_path / "col.ostitch")
    save_project(d, path)
    c2 = load_project(path).objects[0]
    assert c2.kind == "column" and abs(c2.width - 3.0) < 1e-9
