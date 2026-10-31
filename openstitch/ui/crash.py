"""Unerwartete Fehler: Arbeit sichern, Bericht ablegen, verständlich melden.

Im gepackten Programm gibt es keine Konsole. Ohne das hier würde ein Fehler spurlos verschwinden."""
from __future__ import annotations

import datetime as _dt
import os
import platform
import sys
import traceback

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QMessageBox

from .. import __version__
from ..i18n import tr


def log_path() -> str:
    folder = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "crash.log")


def write_report(tp, val, tb) -> str:
    path = log_path()
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n=== {_dt.datetime.now().isoformat(timespec='seconds')} OpenStitch {__version__} "
                f"on {platform.platform()}, Python {platform.python_version()}\n")
        f.write("".join(traceback.format_exception(tp, val, tb)))
    return path


def install(win) -> None:
    busy = [False]

    def hook(tp, val, tb):
        sys.__excepthook__(tp, val, tb)
        if busy[0] or issubclass(tp, KeyboardInterrupt):
            return
        busy[0] = True
        try:
            win._autosave()
            path = write_report(tp, val, tb)
            QMessageBox.critical(win, tr("crash_title"), tr("crash_text").format(path))
        except Exception:  # noqa: BLE001 - der Fehlerbericht selbst darf nie nachtreten
            pass
        finally:
            busy[0] = False

    sys.excepthook = hook
