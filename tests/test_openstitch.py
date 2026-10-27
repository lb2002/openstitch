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
from openstitch.io.formats import export_plan, import_file
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
