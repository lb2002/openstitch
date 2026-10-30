"""Neue Oberfläche: Startseite, Design-Prüfung, Stoff, Sicherung, Fenstergrösse."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QMessageBox
from shapely.geometry import LineString, box

from openstitch.analysis import FABRICS, corpus, simulate_stitchout
from openstitch.core.design import Design, FillObject, SatinObject
from openstitch.core.stitchplan import Cmd, Thread
from openstitch.io.project import load_project, save_project
from openstitch.samples import SAMPLES
from openstitch.ui import theme
from openstitch.ui.main_window import MainWindow

_app = QApplication.instance() or QApplication(sys.argv)
RED = Thread((200, 30, 30), "r")
BLUE = Thread((30, 30, 200), "b")


@pytest.fixture()
def win():
    w = MainWindow(defer_starter=False, show_tour_on_init=False)
    w.show()
    yield w
    w._dirty = False
    w.close()


def _pump(cond, timeout=30.0):
    end = time.time() + timeout
    while time.time() < end and not cond():
        QApplication.processEvents()
        time.sleep(0.01)
    assert cond()


def test_window_fits_small_laptops_in_every_language(win):
    from openstitch.i18n import LANGUAGES, set_lang
    try:
        for code, _ in LANGUAGES:
            win.cmb_lang.setCurrentIndex(win.cmb_lang.findData(code))
            QApplication.processEvents()
            hint = win.minimumSizeHint()
            assert hint.width() <= 1280, (code, hint.width())
            assert hint.height() <= 700, (code, hint.height())
    finally:
        win.cmb_lang.setCurrentIndex(win.cmb_lang.findData("de"))
        set_lang("de")


def test_start_page_offers_samples_and_hides_editor(win):
    win.show_start_page()
    assert win.stack.currentWidget() is win.start_page
    assert not win.left_dock.isVisible()
    win._open_sample("heart")
    assert win.stack.currentWidget() is win.editor_page
    assert win.left_dock.isVisible()
    win.wait_for_plan()
    assert win.canvas.plan.stitch_count > 500


@pytest.mark.parametrize("sid", [s for s, _k, _f in SAMPLES])
def test_samples_are_good_examples(sid):
    d = next(f for s, _k, f in SAMPLES if s == sid)()
    r = simulate_stitchout(d, d.build_plan(), needles=d.settings.needles)
    assert r.ok and r.score >= 70, [(f.code, f.count) for f in r.findings]


def test_recent_files_and_open_path(win, tmp_path):
    p = tmp_path / "a.ostitch"
    save_project(corpus.build("fill_circle"), str(p))
    win.open_path(str(p))
    assert win._recent_files()[0] == str(p)
    assert len(win.canvas.design.objects) == 1
    win._fill_recent_menu()
    assert win.m_recent.actions()


def test_missing_recent_file_is_forgotten(win, tmp_path, monkeypatch):
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *a, **k: QMessageBox.Ok))
    gone = str(tmp_path / "gone.ostitch")
    QSettings("OpenStitch", "OpenStitchStudio").setValue("recent/files", [gone])
    win.open_path(gone)
    assert gone not in win._recent_files()


def test_autosave_recovers_after_crash(win, monkeypatch):
    win._dirty = True
    win.canvas.design.name = "Rettung"
    win._autosave()
    assert os.path.isfile(win._autosave_path())
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    win._dirty = False
    assert win._offer_recovery()
    assert win.canvas.design.name == "Rettung"
    win._clear_autosave()
    assert not win._offer_recovery()


def test_clean_exit_leaves_no_autosave():
    w = MainWindow(defer_starter=False, show_tour_on_init=False)
    w.show()
    w._dirty = True
    w._autosave()
    w._dirty = False
    path = w._autosave_path()
    assert os.path.isfile(path)
    w.close()
    assert not os.path.isfile(path)


def test_fabric_changes_stitching_and_is_saved(win, tmp_path):
    d = Design(objects=[SatinObject(RED, geom=LineString([(-20, 0), (20, 0)]).buffer(2.5, cap_style=2))])
    win.set_design(d, reset_undo=True)
    win.wait_for_plan()
    woven = win.canvas.plan.stitch_count
    win.cmb_fabric.setCurrentIndex(win.cmb_fabric.findData("jersey"))
    win.wait_for_plan()
    assert d.fabric == "jersey"
    assert win.canvas.plan.stitch_count < woven     # lockerer auf dehnbarem Stoff
    path = tmp_path / "f.ostitch"
    save_project(d, str(path))
    assert load_project(str(path)).fabric == "jersey"


def test_every_fabric_builds():
    for fab in FABRICS:
        d = corpus.build("stack_badge")
        d.fabric = fab.id
        r = simulate_stitchout(d, d.build_plan())
        assert r.metrics["stitches"] > 1000
        assert fab.id == d.fabric


def test_hidden_stitches_are_removed_only_when_fully_covered():
    under = FillObject(RED, geom=box(-30, -30, 30, 30))
    over = FillObject(BLUE, geom=box(-15, -15, 15, 15), angle=0)
    d = Design(objects=[under, over])
    with_knockout = d.build_plan()
    pts = [(s.x, s.y) for s in with_knockout.blocks[0].stitches if s.cmd == Cmd.STITCH]
    # Mitte frei, aber der Rand läuft 1 mm unter das obere Objekt: sonst entstünden Lücken
    assert not any(abs(x) < 13.5 and abs(y) < 13.5 for x, y in pts)
    assert any(abs(x) < 14.8 and abs(y) < 14.8 for x, y in pts)
    under.knockout = False
    without = d.build_plan()
    assert without.stitch_count > with_knockout.stitch_count * 1.1


def test_thin_lettering_keeps_its_fill_underneath():
    from openstitch.text import TextObject
    fill = FillObject(RED, geom=box(-30, -10, 30, 10))
    d = Design(objects=[fill, TextObject(BLUE, text="ABC", height=7.0, font="builtin:micro")])
    d.build_plan()
    assert fill._hidden is None


def test_check_dialog_runs_and_fixes(win):
    d = Design(objects=[FillObject(RED, geom=box(-90, -20, 90, 20))])
    win.set_design(d, reset_undo=True)
    win.action_quality_doctor()
    dlg = win._check_dlg
    _pump(lambda: dlg._report is not None and not dlg._worker.isRunning())
    QApplication.processEvents()
    codes = {f.code for f in dlg._report.findings}
    assert "outside_hoop" in codes and not dlg._report.ok
    assert dlg.ring.score is not None
    assert win.fix_for("outside_hoop") is not None
    win.fix_for("outside_hoop")()
    win.wait_for_plan()
    dlg.start()
    _pump(lambda: not dlg._worker.isRunning())
    QApplication.processEvents()
    assert "outside_hoop" not in {f.code for f in dlg._report.findings}
    win.canvas.show_spots([(1.0, 2.0)])
    assert win.canvas._spots


def test_export_dialog_writes_and_verifies(win, tmp_path, monkeypatch):
    from openstitch.ui import export_dialog as ed
    monkeypatch.setattr(ed, "removable_drives", lambda: [(str(tmp_path), "STICK")])
    win.set_design(corpus.build("fill_islands"), reset_undo=True)
    win.wait_for_plan()
    dlg = ed.ExportDialog(win)
    assert dlg.cmb_where.currentData() == str(tmp_path)         # USB-Stick zuerst
    assert dlg.cmb_format.currentData() == win.cmb_machine.currentData().native_ext
    dlg.ed_name.setText("Müller: Logo/2")
    dlg.cb_short.setChecked(True)
    dlg.save()
    assert dlg.saved_path and os.path.isfile(dlg.saved_path)
    assert os.path.basename(dlg.saved_path) == "MLLERLOG." + dlg.cmb_format.currentData().upper()
    assert dlg.lbl_result.property("severity") == "ok"
    dlg.cb_short.setChecked(False)
    assert "Logo_2" in dlg.target_path().replace("Müller_ ", "")
    dlg.close()


def test_export_dialog_reports_write_errors(win, tmp_path, monkeypatch):
    from openstitch.ui import export_dialog as ed
    monkeypatch.setattr(ed, "removable_drives", lambda: [(str(tmp_path / "nicht-da"), "WEG")])
    win.set_design(corpus.build("fill_islands"), reset_undo=True)
    win.wait_for_plan()
    dlg = ed.ExportDialog(win)
    dlg.save()
    assert dlg.saved_path is None
    assert dlg.lbl_result.property("severity") == "error"
    dlg.close()


def test_text_dialog_allows_small_lettering_and_suggests_micro(win):
    from openstitch.fonts_micro import MICRO_SPEC
    from openstitch.ui.dialogs import TextDialog
    dlg = TextDialog(win.canvas.active_thread, parent=win)
    dlg.show()
    dlg.sp_height.setValue(2.5)
    assert dlg.sp_height.value() == 2.5         # 2.5 mm ist das Versprechen der Micro-Schrift
    dlg.cmb_font.setCurrentIndex(max(0, dlg.cmb_font.findText("Arial")))
    if dlg.cmb_font.currentData() != MICRO_SPEC:
        assert dlg.lbl_font_tip.isVisible()
    dlg._use_micro()
    assert dlg.cmb_font.currentData() == MICRO_SPEC and not dlg.lbl_font_tip.isVisible()
    dlg.ed_text.setText("Test")
    assert dlg.preview.obj is not None
    dlg.grab()
    dlg._apply()
    assert dlg.created_object.height == 2.5
    dlg.close()


def test_all_finding_codes_have_texts():
    from openstitch.i18n import _TABLE
    for code in ("short_stitch", "over_max_stitch", "long_float", "no_lock", "orphan_run", "untrimmed_jump",
                 "needle_pileup", "too_dense", "outside_hoop", "low_coverage", "too_many_colors",
                 "registration_gap", "puckering"):
        assert f"chk_{code}_t" in _TABLE and f"chk_{code}_d" in _TABLE


@pytest.mark.parametrize("tid", ["dark", "light"])
def test_themes_switch_and_stay_readable(win, tid):
    win.set_theme(tid)
    try:
        assert theme.current().id == tid
        assert "QMainWindow" in QApplication.instance().styleSheet()
        win.grab()
    finally:
        win.set_theme("dark")
