"""Affentest: zufällige Klicks, Tasten und Mausgesten auf das echte Hauptfenster.

Keine Aktion darf eine Ausnahme auslösen, egal in welcher Reihenfolge sie kommt. Dialoge werden
gebaut, aber sofort geschlossen."""
from __future__ import annotations

import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QAction, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QSlider,
    QSpinBox,
    QToolButton,
)

from openstitch.analysis import corpus
from openstitch.io.formats import export_plan
from openstitch.io.project import save_project
from openstitch.ui.main_window import MainWindow

_app = QApplication.instance() or QApplication(sys.argv)
STEPS = int(os.environ.get("OPENSTITCH_MONKEY_STEPS", "400"))
SEEDS = [int(s) for s in os.environ.get("OPENSTITCH_MONKEY_SEEDS", "1,2,3").split(",")]

# Beenden und Fensterschliessen würden den Test beenden
SKIP_TEXT = ("beenden", "quit", "exit", "quitter", "salir")


class _Mouse:
    def __init__(self, canvas, rng):
        self.c, self.rng = canvas, rng

    def _send(self, kind, x, y, button, buttons):
        p = QPointF(x, y)
        ev = QMouseEvent(kind, p, self.c.mapToGlobal(p.toPoint()).toPointF(), button, buttons, Qt.NoModifier)
        QApplication.sendEvent(self.c, ev)

    def gesture(self):
        w, h = max(self.c.width(), 50), max(self.c.height(), 50)
        x, y = self.rng.randrange(w), self.rng.randrange(h)
        button = self.rng.choice((Qt.LeftButton, Qt.LeftButton, Qt.LeftButton, Qt.RightButton, Qt.MiddleButton))
        self._send(QEvent.MouseButtonPress, x, y, button, button)
        for _ in range(self.rng.randrange(0, 6)):
            x += self.rng.randrange(-80, 80)
            y += self.rng.randrange(-80, 80)
            self._send(QEvent.MouseMove, x, y, Qt.NoButton, button)
        self._send(QEvent.MouseButtonRelease, x, y, button, Qt.NoButton)
        if self.rng.random() < 0.3:
            self._send(QEvent.MouseButtonDblClick, x, y, Qt.LeftButton, Qt.LeftButton)
            self._send(QEvent.MouseButtonRelease, x, y, Qt.LeftButton, Qt.NoButton)

    def wheel(self):
        p = QPointF(self.rng.randrange(max(self.c.width(), 1)), self.rng.randrange(max(self.c.height(), 1)))
        ev = QWheelEvent(p, self.c.mapToGlobal(p.toPoint()).toPointF(), QPoint(0, 0),
                         QPoint(0, self.rng.choice((-240, -120, 120, 240))), Qt.NoButton, Qt.NoModifier,
                         Qt.NoScrollPhase, False)
        QApplication.sendEvent(self.c, ev)


def _safe_actions(win):
    out = []
    for a in win.findChildren(QAction):
        t = a.text().lower().replace("&", "")
        if a.menu() is not None or a.isSeparator() or not t or any(k in t for k in SKIP_TEXT):
            continue
        out.append(a)
    return out


@pytest.fixture()
def dialogs_closed(monkeypatch, tmp_path):
    """Dialoge öffnen nicht wirklich; Dateiauswahl liefert abwechselnd echte Dateien oder Abbruch."""
    d = corpus.build("stack_badge")
    plan = d.build_plan()
    files = {".ostitch": str(tmp_path / "a.ostitch"), ".dst": str(tmp_path / "a.dst"), ".pes": str(tmp_path / "a.pes")}
    save_project(d, files[".ostitch"])
    export_plan(plan, files[".dst"])
    export_plan(plan, files[".pes"])
    svg = tmp_path / "a.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="15"/></svg>')
    png = tmp_path / "a.png"
    from PySide6.QtGui import QImage
    img = QImage(64, 64, QImage.Format_RGB32)
    img.fill(Qt.red)
    img.save(str(png))
    rng = random.Random(0)

    def pick_open(self, title, name_filter):
        f = name_filter.lower()
        for ext, path in ((".svg", str(svg)), (".png", str(png)), (".ostitch", files[".ostitch"]), (".dst", files[".dst"])):
            if ext[1:] in f and rng.random() < 0.8:
                return path
        return ""

    def pick_save(self, title, default_filename, name_filter):
        return "" if rng.random() < 0.4 else str(tmp_path / default_filename)

    monkeypatch.setattr(MainWindow, "_ask_open_file", pick_open)
    monkeypatch.setattr(MainWindow, "_ask_save_file", pick_save)
    monkeypatch.setattr(QDialog, "exec", lambda self: 0)
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: QMessageBox.Ok))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *a, **k: QMessageBox.Ok))
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a, **k: QMessageBox.Ok))
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    monkeypatch.setattr(QInputDialog, "getDouble", staticmethod(lambda *a, **k: (120.0, True)))
    monkeypatch.setattr(QInputDialog, "getItem", staticmethod(lambda *a, **k: ("100", True)))
    monkeypatch.setattr(QInputDialog, "getText", staticmethod(lambda *a, **k: ("Test", True)))
    return files


@pytest.mark.parametrize("seed", SEEDS)
def test_monkey(seed, dialogs_closed):
    errors: list[str] = []
    old_hook = sys.excepthook

    def hook(tp, val, tb):
        import traceback
        errors.append("".join(traceback.format_exception(tp, val, tb)))

    sys.excepthook = hook
    rng = random.Random(seed)
    win = MainWindow(defer_starter=False, show_tour_on_init=False)
    win.resize(1400, 860)
    win.show()
    log: list[str] = []
    try:
        mouse = _Mouse(win.canvas, rng)
        actions = _safe_actions(win)
        for step in range(STEPS):
            roll = rng.random()
            if roll < 0.40:
                mouse.gesture()
                log.append("gesture")
            elif roll < 0.45:
                mouse.wheel()
                log.append("wheel")
            elif roll < 0.72:
                a = rng.choice(actions)
                log.append(f"action:{a.text()}")
                a.trigger()
            elif roll < 0.82:
                key = rng.choice((Qt.Key_V, Qt.Key_N, Qt.Key_F, Qt.Key_S, Qt.Key_R, Qt.Key_Delete, Qt.Key_Escape,
                                  Qt.Key_Return, Qt.Key_Backspace, Qt.Key_Left, Qt.Key_Up))
                log.append(f"key:{key}")
                for kind in (QEvent.KeyPress, QEvent.KeyRelease):
                    QApplication.sendEvent(win.canvas, QKeyEvent(kind, key, Qt.NoModifier))
            else:
                widgets = [w for cls in (QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QListWidget, QSlider,
                                         QLineEdit, QToolButton) for w in win.findChildren(cls) if w.isEnabled()]
                w = rng.choice(widgets)
                log.append(f"widget:{type(w).__name__}:{w.objectName()}")
                if isinstance(w, QComboBox) and w.count():
                    w.setCurrentIndex(rng.randrange(w.count()))
                elif isinstance(w, (QSpinBox, QDoubleSpinBox, QSlider)):
                    w.setValue(rng.uniform(w.minimum(), w.maximum()))
                elif isinstance(w, QCheckBox):
                    w.toggle()
                elif isinstance(w, QListWidget) and w.count():
                    w.setCurrentRow(rng.randrange(w.count()))
                elif isinstance(w, QLineEdit):
                    w.setText(rng.choice(("", "x", "Hällo", "42", "‮abc")))
                elif isinstance(w, QToolButton) and w.isVisible():
                    w.click()
            QApplication.processEvents()
            if step % 40 == 0:
                win.wait_for_plan()
            assert not errors, "\n".join(log[-12:]) + "\n" + errors[0]
        win.wait_for_plan()
        QApplication.processEvents()
        assert not errors, "\n".join(log[-12:]) + "\n" + errors[0]
    finally:
        sys.excepthook = old_hook
        win._dirty = False
        win.close()
