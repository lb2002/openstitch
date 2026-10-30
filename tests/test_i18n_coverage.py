"""Prüft, dass die Oberfläche vollständig übersetzbar ist (DE/EN/FR/ES)."""
from __future__ import annotations

import re
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QAbstractButton, QApplication, QComboBox, QDockWidget, QGroupBox, QLabel
from shapely.geometry import LineString, box

from openstitch import i18n
from openstitch.core.design import HOOP_NAME_KEYS, HOOPS, FillObject, Hoop, RunObject, SatinObject
from openstitch.core.stitchplan import Thread
from openstitch.i18n import _TABLE, fmt_int, set_lang, tr
from openstitch.text import TextObject
from openstitch.ui.main_window import MainWindow

_app = QApplication.instance() or QApplication(sys.argv)

SRC = Path(__file__).resolve().parent.parent / "openstitch"

# Wörter, die nur im deutschen UI vorkommen dürfen (keine Fremd-/Fachwörter, die auch englisch sind)
GERMAN_ONLY = (
    "Stichwinkel", "Unterlage", "Abbrechen", "Rahmen", "Speichern", "Fehler", "Füllung", "Zugkompensation",
    "Reihenabstand", "Stichlänge", "Muster", "Dichte", "Bezeichnung", "Buchstabenhöhe", "Zeichenabstand",
    "Bogenradius", "Stichart", "Wiederholungen", "Schriftart", "Strategie", "Ausgewogen", "Stiche",
    "Fadenschnitte", "Sichtbar", "Kopie", "Fortschritt", "Tempo", "Garnkatalog", "Nadel", "Maschine",
    "Stickrahmen", "Sprache", "Auswahl", "Knoten", "Stepp", "Ebenen", "Objekt", "Mittellauf", "Kantenlauf",
    "Ziegel", "Wellen", "Automatisch", "Rund ", "Schliessen", "Übernehmen", "Taste",
)


def _source_files():
    return [p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts]


def test_all_literal_tr_keys_exist():
    tr_re = re.compile(r"""\btr\(\s*(['"])([A-Za-z0-9_+]+)\1\s*\)""")
    bind_re = re.compile(r"""\._bind\(\s*[\w.]+\s*,\s*(['"])([A-Za-z0-9_+]+)\1""")
    missing = []
    for path in _source_files():
        src = path.read_text(encoding="utf-8")
        for rx in (tr_re, bind_re):
            for m in rx.finditer(src):
                if m.group(2) not in _TABLE:
                    missing.append(f"{path.relative_to(SRC.parent)}: {m.group(2)}")
    assert not missing, "Fehlende Übersetzungsschlüssel:\n" + "\n".join(missing)


def test_table_rows_complete_and_consistent():
    fmt = string.Formatter()
    for key, row in _TABLE.items():
        assert isinstance(row, tuple) and len(row) == 4, key
        assert all(isinstance(s, str) and s.strip() for s in row), key
        if key == "pdf_date_fmt":
            continue
        # Platzhalter müssen in allen Sprachen identisch sein, sonst schlägt .format() fehl
        fields = [sorted((f or "#") for _, f, _, _ in fmt.parse(s) if f is not None) for s in row]
        assert all(f == fields[0] for f in fields), f"{key}: {fields}"


def test_dynamic_keys_exist():
    # Inspektor-Labels & Optionswerte
    for cls in (FillObject, SatinObject, RunObject, TextObject):
        kind = cls.kind
        for attr, _label, typ, *_ in cls.PARAMS:
            assert f"param_{kind}_{attr}" in _TABLE or f"param_{attr}" in _TABLE, (cls.__name__, attr)
            if isinstance(typ, list):
                for opt in typ:
                    assert f"opt_{opt}" in _TABLE, (cls.__name__, attr, opt)
    for kind in ("fill", "satin", "run", "text", "stitches"):
        assert f"kind_{kind}" in _TABLE
    # Rahmen: jeder Name hat eine Übersetzung, jede Strategie eine Beschreibung
    assert {h.name for h in HOOPS} == set(HOOP_NAME_KEYS)
    for key in HOOP_NAME_KEYS.values():
        assert key in _TABLE
    for h in HOOPS:
        assert _TABLE[HOOP_NAME_KEYS[h.name]][0] == h.name  # deutscher Anzeigename == gespeicherter Name
        assert f"hoop_strat_{h.mode}" in _TABLE
    from openstitch.core.machines import MACHINE_PROFILES
    for mp in MACHINE_PROFILES:
        assert _TABLE[f"machine_{mp.id}"][0] == mp.name
    # Fortschrittsmeldungen der Auto-Digitizer-Engine werden im Dialog übersetzt
    engine_src = (SRC / "auto" / "digitize.py").read_text(encoding="utf-8")
    for msg in re.findall(r'step\("([^"]+)"', engine_src):
        assert i18n.key_for(msg) is not None, msg


def test_hoop_strategy_and_names_follow_language():
    h = HOOPS[2]
    try:
        set_lang("en")
        assert "pull compensation" in h.strategy_description
        assert h.display_name == "Round 15 cm (standard)"
        assert Hoop("Eigener Rahmen", 100, 100).display_name == "Eigener Rahmen"
        assert Hoop("x", 100, 100, mode="unknown").strategy_description == "Standard"
        set_lang("fr")
        assert "compensation de traction" in h.strategy_description
    finally:
        set_lang("de")
    assert h.name == "Rund 15 cm (Standard)"
    assert "Zugkompensation" in h.strategy_description


def test_fmt_int_per_language():
    expected = {"de": "1’234’567", "en": "1,234,567", "fr": "1 234 567", "es": "1.234.567"}
    try:
        for lang, exp in expected.items():
            set_lang(lang)
            assert fmt_int(1234567) == exp
            assert fmt_int(999) == "999"
    finally:
        set_lang("de")


def _visible_texts(win: MainWindow) -> list[str]:
    texts = [win.windowTitle()]
    for w in win.findChildren(QLabel):
        texts.append(w.text())
    for w in win.findChildren(QAbstractButton):  # QPushButton, QCheckBox, QToolButton
        texts.append(w.text())
        texts.append(w.toolTip())
    for w in win.findChildren(QComboBox):
        texts.extend(w.itemText(i) for i in range(w.count()))
    for w in win.findChildren(QDockWidget):
        texts.append(w.windowTitle())
    for a in win.findChildren(QAction):
        texts.append(a.text())
        texts.append(a.toolTip())
    for m in win.menuBar().actions():
        texts.append(m.text())
    texts.append(win.sp_sim_speed.suffix())
    texts.extend(win.list_objects.item(i).text() for i in range(win.list_objects.count()))
    texts.extend(win.list_needles.item(i).text() for i in range(win.list_needles.count()))
    return [t for t in texts if t]


def _assert_no_german(texts: list[str], where: str):
    hits = sorted({f"{w!r} in {t!r}" for t in texts for w in GERMAN_ONLY if w in t})
    assert not hits, f"Deutscher Text in {where}:\n" + "\n".join(hits)


def test_main_window_and_inspector_fully_translated():
    win = MainWindow(show_tour_on_init=False, defer_starter=True)
    th = Thread((200, 30, 40), "Red", "1147", "Madeira")
    fill = FillObject(thread=th, name="F1", geom=box(-20, -20, 20, 20))
    satin = SatinObject(thread=th, name="S1", geom=LineString([(-20, 30), (20, 30)]).buffer(2.0))
    run = RunObject(thread=th, name="R1", geom=LineString([(-20, -30), (20, -30)]))
    text = TextObject(thread=th, name="T1", text="AB", height=12.0)
    run.visible = False  # "[Aus]"-Markierung in der Objektliste prüfen
    win.canvas.design.objects[:] = [fill, satin, run, text]
    win.rebuild_plan()
    win.wait_for_plan()
    try:
        idx = next(i for i in range(win.cmb_lang.count()) if win.cmb_lang.itemData(i) == "en")
        win.cmb_lang.setCurrentIndex(idx)
        assert i18n.current_lang() == "en"
        assert win.cmb_hoop.toolTip().startswith("Strategy: ")
        assert "Fit to hoop" in [a.text() for a in win.left_rail.actions()]
        for obj in (fill, satin, run, text, None):
            win.canvas.selected = obj
            win._populate_properties(obj)
            _assert_no_german(_visible_texts(win), f"Inspektor ({type(obj).__name__})")
        # Optionswerte: Anzeige übersetzt, Daten unverändert
        win._populate_properties(satin)
        combos = win.prop_container.findChildren(QComboBox)
        assert combos and combos[0].itemData(1) == "mitte" and combos[0].itemText(1) == "Center walk"
        assert not any("Stitch angle" in t for t in _visible_texts(win))  # Satin hat keinen Stichwinkel
        win._populate_properties(fill)
        assert any(t.startswith("Stitch angle") for t in _visible_texts(win))
        # Zurück auf Deutsch: Texte wechseln zurück
        idx = next(i for i in range(win.cmb_lang.count()) if win.cmb_lang.itemData(i) == "de")
        win.cmb_lang.setCurrentIndex(idx)
        win._populate_properties(fill)
        assert any(t.startswith("Stichwinkel") for t in _visible_texts(win))
        assert win.cmb_hoop.currentText().startswith("Rund 15 cm")
    finally:
        set_lang("de")
        win._dirty = False
        win.close()


def _dialog_texts(dlg) -> list[str]:
    texts = [dlg.windowTitle()]
    texts += [w.text() for w in dlg.findChildren(QLabel)]
    texts += [w.text() for w in dlg.findChildren(QAbstractButton)]
    texts += [w.title() for w in dlg.findChildren(QGroupBox)]
    for c in dlg.findChildren(QComboBox):
        texts += [c.itemText(i) for i in range(c.count())]
    return [t for t in texts if t]


def test_dialogs_and_pdf_translated(tmp_path):
    import cv2
    import numpy as np

    from openstitch.core.design import Design
    from openstitch.io.project import export_worksheet_pdf
    from openstitch.ui.dialogs import AutoDigitizeDialog, MelcoDiskDialog, PhotoStitchDialog, TextDialog, _tr_progress

    img = np.full((80, 100, 3), 255, dtype=np.uint8)
    cv2.circle(img, (50, 40), 30, (40, 40, 210), -1)
    img_path = str(tmp_path / "logo.png")
    cv2.imwrite(img_path, img)
    th = Thread((200, 30, 40), "Red")
    d = Design(objects=[FillObject(thread=th, geom=box(-10, -10, 10, 10))])
    plan = d.build_plan()
    try:
        for lang in ("en", "fr", "es"):
            set_lang(lang)
            for dlg in (AutoDigitizeDialog(img_path), PhotoStitchDialog(img_path), TextDialog(th),
                        MelcoDiskDialog(plan, "TEST")):
                _assert_no_german(_dialog_texts(dlg), f"{type(dlg).__name__} ({lang})")
                dlg.deleteLater()
            # Fortschrittsmeldungen der Engine werden übersetzt
            assert _tr_progress("Fläche 3/7 klassifizieren …") == tr("prog_classify").format(3, 7)
            assert _tr_progress("Farben reduzieren …") == tr("prog_reduce")
            out = tmp_path / f"sheet_{lang}.pdf"
            export_worksheet_pdf(d, plan, str(out))
            assert out.stat().st_size > 1000
    finally:
        set_lang("de")
