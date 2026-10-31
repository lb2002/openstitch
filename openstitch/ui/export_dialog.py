"""„An die Maschine senden“: passendes Format, USB-Stick, Prüfung der geschriebenen Datei."""
from __future__ import annotations

import os
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from ..core.machines import MachineProfile
from ..i18n import fmt_float, fmt_int, tr
from ..io.drives import removable_drives
from ..io.formats import FORMAT_NAMES, WRITE_EXT, export_plan, verify_exported_file
from ..render import render_image

MACHINE_EXT = ("exp", "dst", "pes", "jef", "vp3", "xxx", "u01", "pec", "tbf")


def short_name(name: str, limit: int = 8) -> str:
    """Name für ältere Maschinen: nur A–Z, 0–9, höchstens 8 Zeichen."""
    clean = re.sub(r"[^A-Za-z0-9]+", "", name).upper()
    return (clean or "DESIGN")[:limit]


def safe_name(name: str) -> str:
    """Zeichen entfernen, die Dateisysteme oder Maschinen nicht mögen."""
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", name).strip(" .")
    return clean or "design"


class ExportDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle(tr("exp_title"))
        self.resize(640, 560)
        self.saved_path: str | None = None
        design, plan = win.canvas.design, win.canvas.plan
        mp: MachineProfile | None = win.cmb_machine.currentData()

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(14)
        thumb = QLabel()
        thumb.setFixedSize(96, 96)
        thumb.setAlignment(Qt.AlignCenter)
        if plan.stitch_count:
            size = max(plan.bounds()[2] - plan.bounds()[0], plan.bounds()[3] - plan.bounds()[1], 10.0)
            img = render_image(plan, px_per_mm=min(190.0 / size, 8.0), margin_mm=2.0, background=None)
            thumb.setPixmap(QPixmap.fromImage(img).scaled(92, 92, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        head.addWidget(thumb)
        col = QVBoxLayout()
        col.setSpacing(2)
        title = QLabel(tr("exp_heading"))
        title.setProperty("role", "title")
        facts = QLabel(tr("exp_facts").format(
            st=fmt_int(plan.stitch_count), colors=len(plan.blocks),
            w=fmt_float(plan.bounds()[2] - plan.bounds()[0], 0), h=fmt_float(plan.bounds()[3] - plan.bounds()[1], 0)))
        facts.setProperty("role", "subtitle")
        facts.setWordWrap(True)
        col.addStretch(1)
        col.addWidget(title)
        col.addWidget(facts)
        col.addStretch(1)
        head.addLayout(col, 1)
        root.addLayout(head)

        form = QFormLayout()
        form.setVerticalSpacing(9)
        form.setHorizontalSpacing(12)

        self.cmb_format = QComboBox()
        native = mp.native_ext if mp else "dst"
        for ext in [native] + [e for e in WRITE_EXT if e != native]:
            label = FORMAT_NAMES.get(ext, ext.upper())
            if ext == native:
                label = tr("exp_recommended").format(label)
            self.cmb_format.addItem(label, ext)
        self.cmb_format.currentIndexChanged.connect(self._update_path)
        form.addRow(tr("exp_format"), self.cmb_format)

        self.ed_name = QLineEdit(safe_name(design.name))
        self.ed_name.textChanged.connect(self._update_path)
        form.addRow(tr("exp_name"), self.ed_name)

        self.cb_short = QCheckBox(tr("exp_short"))
        self.cb_short.setToolTip(tr("exp_short_tip"))
        self.cb_short.setChecked(bool(mp and mp.floppy_144mb))
        self.cb_short.toggled.connect(self._update_path)
        form.addRow("", self.cb_short)

        where = QHBoxLayout()
        self.cmb_where = QComboBox()
        self._fill_targets()
        self.cmb_where.currentIndexChanged.connect(self._update_path)
        btn_other = QPushButton(tr("exp_browse"))
        btn_other.clicked.connect(self._pick_folder)
        btn_refresh = QPushButton(tr("exp_refresh"))
        btn_refresh.clicked.connect(self._refresh_targets)
        where.addWidget(self.cmb_where, 1)
        where.addWidget(btn_refresh)
        where.addWidget(btn_other)
        form.addRow(tr("exp_where"), where)
        root.addLayout(form)

        self.lbl_path = QLabel()
        self.lbl_path.setProperty("role", "caption")
        self.lbl_path.setWordWrap(True)
        root.addWidget(self.lbl_path)

        cap = QLabel(tr("exp_threads"))
        cap.setProperty("role", "section")
        root.addWidget(cap)
        self.list_threads = QListWidget()
        for i, b in enumerate(plan.blocks, 1):
            icon = win.thread_icon(b.thread.color)
            self.list_threads.addItem(QListWidgetItem(icon, f"{i}. {b.thread.name or b.thread.hex}  {b.thread.code}".rstrip()))
        root.addWidget(self.list_threads, 1)

        self.lbl_result = QLabel()
        self.lbl_result.setWordWrap(True)
        root.addWidget(self.lbl_result)

        row = QHBoxLayout()
        row.addStretch(1)
        self.btn_close = QPushButton(tr("btn_close"))
        self.btn_close.clicked.connect(self.reject)
        self.btn_save = QPushButton(tr("exp_save"))
        self.btn_save.setObjectName("primaryBtn")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self.save)
        self.btn_save.setEnabled(plan.stitch_count > 0)
        row.addWidget(self.btn_close)
        row.addWidget(self.btn_save)
        root.addLayout(row)
        self._update_path()

    # ---------------------------------------------------------------- Zielort
    def _fill_targets(self):
        self.cmb_where.blockSignals(True)
        self.cmb_where.clear()
        for path, label in removable_drives():
            self.cmb_where.addItem(tr("exp_usb").format(label), path)
        docs = self.win._default_open_dir()
        self.cmb_where.addItem(docs, docs)
        self.cmb_where.blockSignals(False)

    def _refresh_targets(self):
        self._fill_targets()
        self._update_path()

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr("exp_where"), self.cmb_where.currentData() or "")
        if folder:
            self.cmb_where.insertItem(0, folder, folder)
            self.cmb_where.setCurrentIndex(0)

    def target_path(self) -> str:
        ext = self.cmb_format.currentData()
        name = safe_name(self.ed_name.text())
        if self.cb_short.isChecked():
            name, ext = short_name(name), ext.upper()
        return os.path.join(self.cmb_where.currentData() or ".", f"{name}.{ext}")

    def _update_path(self):
        self.lbl_path.setText(self.target_path())

    # -------------------------------------------------------------- Speichern
    def _may_replace(self, path: str) -> bool:
        """Kurze Namen kollidieren leicht: Eine vorhandene Datei wird nie stillschweigend ersetzt."""
        if not os.path.exists(path):
            return True
        ans = QMessageBox.question(self, tr("exp_title"), tr("exp_overwrite").format(os.path.basename(path)),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return ans == QMessageBox.Yes

    def save(self):
        path = self.target_path()
        if not self._may_replace(path):
            return
        plan = self.win.canvas.plan
        self.lbl_result.setProperty("severity", "ok")
        # Erst neben dem Ziel schreiben und prüfen: Ein Fehler lässt die alte Datei unberührt
        stem, ext = os.path.splitext(path)
        tmp = f"{stem}.partial{ext}"
        try:
            export_plan(plan, tmp)
            if self.cmb_format.currentData() in MACHINE_EXT:
                rep = verify_exported_file(tmp, plan)
                msg = tr("exp_done").format(st=fmt_int(rep["stitches"]), name=os.path.basename(path))
            else:
                msg = tr("exp_done_plain").format(name=os.path.basename(path))
            os.replace(tmp, path)
            self.saved_path = path
            self.btn_close.setDefault(True)
            self.lbl_result.setText(msg)
        except Exception as exc:  # noqa: BLE001 - Schreibschutz, voller Stick, ungültiger Pfad …
            self.lbl_result.setProperty("severity", "error")
            self.lbl_result.setText(tr("exp_failed").format(exc))
            try:
                os.remove(tmp)
            except OSError:
                pass
        self.lbl_result.style().unpolish(self.lbl_result)
        self.lbl_result.style().polish(self.lbl_result)
