"""USB-Sticks finden, damit das Speichern für die Maschine ohne Ordnersuche geht."""
from __future__ import annotations

import os
import sys

from PySide6.QtCore import QStorageInfo


def _is_removable_windows(root: str) -> bool:
    import ctypes
    DRIVE_REMOVABLE = 2
    return ctypes.windll.kernel32.GetDriveTypeW(root) == DRIVE_REMOVABLE


def removable_drives() -> list[tuple[str, str]]:
    """(Pfad, Anzeigename) aller beschreibbaren Wechseldatenträger."""
    out: list[tuple[str, str]] = []
    for vol in QStorageInfo.mountedVolumes():
        if not vol.isValid() or not vol.isReady() or vol.isReadOnly() or vol.isRoot():
            continue
        root = vol.rootPath()
        if sys.platform == "win32":
            ok = _is_removable_windows(os.path.join(root, ""))
        elif sys.platform == "darwin":
            ok = root.startswith("/Volumes/")
        else:
            ok = root.startswith(("/media/", "/run/media/", "/mnt/"))
        if ok:
            name = vol.displayName() or root
            free = vol.bytesAvailable() / 1e9
            out.append((root, f"{name} ({root}, {free:.1f} GB)"))
    return out
