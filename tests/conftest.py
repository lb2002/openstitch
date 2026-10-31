"""Tests dürfen die echten Benutzereinstellungen nicht berühren."""
import os
import sys
import tempfile

from PySide6.QtCore import QSettings

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if sys.platform == "win32":     # die Offscreen-Ausgabe findet Windows-Schriften nicht von selbst
    os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")

_tmp = tempfile.TemporaryDirectory(prefix="openstitch-tests-")
QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, _tmp.name)
QSettings("OpenStitch", "OpenStitchStudio").setValue("ui/lang", "de")
