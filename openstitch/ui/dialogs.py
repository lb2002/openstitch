"""Assistenten-Dialoge: Auto-Digitalisieren, Schrift/Monogramm, Melco EMT10/4 Disketten/USB-Manager."""
from __future__ import annotations

import os
import re

import numpy as np
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from ..auto.digitize import AutoParams, AutoResult, auto_digitize, load_image
from ..auto.photostitch import PhotoStitchParams, generate_photostitch
from ..core.design import Design
from ..core.stitchplan import StitchPlan, Thread
from ..io.exp import exp_bytes
from ..io.fat12 import Fat12Image, dos_name
from ..i18n import fmt_float, fmt_int, key_for, tr
from ..text import TextObject, default_font, list_fonts


def _np_to_pixmap(rgb: np.ndarray, max_side: int = 360) -> QPixmap:
    h, w = rgb.shape[:2]
    ch = rgb.shape[2] if rgb.ndim == 3 else 1
    if ch == 4:
        qimg = QImage(rgb.data, w, h, w * 4, QImage.Format_RGBA8888).copy()
    else:
        rgb_c = np.ascontiguousarray(rgb[:, :, :3])
        qimg = QImage(rgb_c.data, w, h, w * 3, QImage.Format_RGB888).copy()
    return QPixmap.fromImage(qimg).scaled(max_side, max_side, Qt.KeepAspectRatio, Qt.SmoothTransformation)


class _Cancelled(Exception):
    pass


_CLASSIFY_RE = re.compile(r"^Fläche (\d+)/(\d+) klassifizieren …$")


def _tr_progress(msg: str) -> str:
    """Übersetzt die (deutschen) Fortschrittsmeldungen der Auto-Digitizer-Engine in die UI-Sprache."""
    m = _CLASSIFY_RE.match(msg)
    if m:
        return tr("prog_classify").format(m.group(1), m.group(2))
    key = key_for(msg)
    return tr(key) if key else msg


def _image_filter(all_key: str = "filter_all_images") -> str:
    exts = "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff"
    return f"{tr(all_key)} ({exts});;{tr('filter_all_files')} (*.*)"


class _DigitizeWorker(QThread):
    progress = Signal(str, int)
    finished_ok = Signal(object, object)   # AutoResult, StitchPlan
    failed = Signal(str)

    def __init__(self, rgba: np.ndarray, params: AutoParams, hoop=None):
        super().__init__()
        self.rgba = rgba
        self.params = params
        self.hoop = hoop
        self.cancelled = False

    def _tick(self, msg: str, val: int):
        # Abbruch wird an jedem Fortschrittspunkt geprüft (Bildschritte bzw. je Objekt)
        if self.cancelled:
            raise _Cancelled()
        self.progress.emit(_tr_progress(msg), val)

    def run(self):
        try:
            res = auto_digitize(
                self.rgba,
                self.params,
                progress=lambda msg, v: self._tick(msg, int(v * 0.55)),
            )
            if self.hoop is not None:
                # Plan gleich für den Rahmen des Hauptfensters rechnen
                res.design.hoop = self.hoop
            plan = res.design.build_plan(
                progress=lambda i, n: self._tick(
                    tr("prog_computing_stitches").format(i, n), 55 + int(45 * i / max(1, n))
                )
            )
            if not self.cancelled:
                self.finished_ok.emit(res, plan)
        except _Cancelled:
            pass
        except Exception as exc:
            if not self.cancelled:
                self.failed.emit(str(exc))


# ===========================================================================
# 1. Auto-Digitalisieren (Bild → Stickdatei)
# ===========================================================================
class AutoDigitizeDialog(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dlg_auto_title"))
        self.resize(860, 560)
        self.rgba = load_image(image_path)
        self.result_data: AutoResult | None = None
        self.result_plan: StitchPlan | None = None
        self._worker: _DigitizeWorker | None = None

        root = QVBoxLayout(self)

        top = QHBoxLayout()
        # Vorschau Original
        v1 = QVBoxLayout()
        lbl_t1 = QLabel(tr("lbl_orig_image").format(os.path.basename(image_path)))
        lbl_t1.setAlignment(Qt.AlignCenter)
        self.lbl_orig_title = lbl_t1
        self.lbl_orig = QLabel()
        self.lbl_orig.setAlignment(Qt.AlignCenter)
        self.lbl_orig.setMinimumSize(320, 320)
        self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 340))
        btn_change_img = QPushButton(tr("btn_other_image"))
        btn_change_img.clicked.connect(self._choose_other_image)
        v1.addWidget(lbl_t1)
        v1.addWidget(self.lbl_orig, 1)
        v1.addWidget(btn_change_img)
        top.addLayout(v1, 1)

        # Einstellungen rechts
        grp = QGroupBox(tr("grp_auto_settings"))
        form = QFormLayout(grp)

        self.sp_width = QDoubleSpinBox()
        self.sp_width.setRange(15.0, 350.0)
        self.sp_width.setValue(95.0)
        self.sp_width.setSuffix(" mm")
        form.addRow(tr("lbl_target_width_motif"), self.sp_width)

        self.sp_colors = QSpinBox()
        self.sp_colors.setRange(1, 16)
        self.sp_colors.setValue(6)
        form.addRow(tr("lbl_max_colors"), self.sp_colors)

        self.cb_bg = QCheckBox(tr("cb_remove_bg"))
        self.cb_bg.setChecked(True)
        form.addRow("", self.cb_bg)

        self.cmb_fabric = QComboBox()
        for fab in ("normal", "strick", "frottee", "cap", "leicht"):
            self.cmb_fabric.addItem(tr(f"fabric_opt_{fab}"), fab)
        form.addRow(tr("lbl_fabric_type"), self.cmb_fabric)

        self.sp_density = QDoubleSpinBox()
        self.sp_density.setRange(0.28, 1.0)
        self.sp_density.setSingleStep(0.02)
        self.sp_density.setValue(0.40)
        self.sp_density.setSuffix(" mm")
        form.addRow(tr("lbl_density_row"), self.sp_density)

        self.sp_satin = QDoubleSpinBox()
        self.sp_satin.setRange(2.0, 10.0)
        self.sp_satin.setSingleStep(0.5)
        self.sp_satin.setValue(6.5)
        self.sp_satin.setSuffix(" mm")
        form.addRow(tr("lbl_satin_limit"), self.sp_satin)

        self.sp_min_area = QDoubleSpinBox()
        self.sp_min_area.setRange(0.3, 15.0)
        self.sp_min_area.setSingleStep(0.5)
        self.sp_min_area.setValue(1.5)
        self.sp_min_area.setSuffix(" mm²")
        form.addRow(tr("lbl_min_area"), self.sp_min_area)

        self.cb_outline = QCheckBox(tr("cb_outline"))
        form.addRow("", self.cb_outline)

        self.cb_palette = QCheckBox(tr("cb_palette"))
        self.cb_palette.setChecked(True)
        form.addRow("", self.cb_palette)

        top.addWidget(grp, 1)
        root.addLayout(top, 1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.lbl_status = QLabel(tr("status_ready"))
        root.addWidget(self.lbl_status)
        root.addWidget(self.progress)

        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_ok = self.btns.button(QDialogButtonBox.Ok)
        self.btn_ok.setText(tr("btn_digitize_apply"))
        self.btns.button(QDialogButtonBox.Cancel).setText(tr("btn_cancel"))
        self.btns.accepted.connect(self._run)
        self.btns.rejected.connect(self.reject)
        root.addWidget(self.btns)

    def _choose_other_image(self):
        p = self.parent()
        if p is not None and hasattr(p, "_ask_open_file"):
            path = p._ask_open_file(tr("fd_pick_logo"), _image_filter())
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, tr("fd_pick_logo_short"), "",
                f"{tr('filter_images')} (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff)",
            )
        if not path:
            return
        try:
            self.rgba = load_image(path)
            self.lbl_orig_title.setText(tr("lbl_orig_image").format(os.path.basename(path)))
            self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 340))
        except Exception as exc:
            QMessageBox.critical(self, tr("err_load_title"), str(exc))

    def _run(self):
        if self._worker is not None and self._worker.isRunning():
            return
        p = AutoParams(
            width_mm=self.sp_width.value(),
            colors=self.sp_colors.value(),
            remove_background=self.cb_bg.isChecked(),
            fabric=self.cmb_fabric.currentData(),
            density=self.sp_density.value(),
            satin_max_mm=self.sp_satin.value(),
            min_area_mm2=self.sp_min_area.value(),
            outline=self.cb_outline.isChecked(),
            use_palette=self.cb_palette.isChecked(),
        )
        self.btn_ok.setEnabled(False)
        parent = self.parent()
        hoop = parent.canvas.design.hoop if parent is not None and hasattr(parent, "canvas") else None
        self._worker = _DigitizeWorker(self.rgba, p, hoop)
        self._worker.progress.connect(self._on_prog)
        self._worker.finished_ok.connect(self._on_done)
        self._worker.failed.connect(self._on_fail)
        self._worker.start()

    def _on_prog(self, msg: str, val: int):
        self.lbl_status.setText(msg)
        self.progress.setValue(val)

    def _on_done(self, res: AutoResult, plan: StitchPlan):
        self.result_data = res
        self.result_plan = plan
        self.btn_ok.setEnabled(True)
        self.accept()

    def _on_fail(self, err: str):
        self.btn_ok.setEnabled(True)
        QMessageBox.critical(self, tr("err_digitize_title"), err)

    def reject(self):
        # Abbrechen/Esc/Schliessen stoppt auch die laufende Berechnung
        w = self._worker
        if w is not None and w.isRunning():
            w.cancelled = True
            for sig in (w.progress, w.finished_ok, w.failed):
                try:
                    sig.disconnect()
                except (RuntimeError, TypeError):
                    pass
            w.wait(15000)
        self._worker = None
        super().reject()


# ===========================================================================
# 2. Schrift & Monogramme
# ===========================================================================
class TextDialog(QDialog):
    def __init__(self, thread: Thread, existing: TextObject | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dlg_text_title"))
        self.resize(520, 380)
        self.thread = thread
        self.existing = existing
        self.created_object: TextObject | None = None

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.ed_text = QLineEdit(existing.text if existing else "OPENSTITCH")
        form.addRow(tr("lbl_text"), self.ed_text)

        self.cmb_font = QComboBox()
        self._fonts = list_fonts()
        cur_font = existing.font if existing else default_font()
        cur_idx = 0
        for idx, (name, spec) in enumerate(self._fonts.items()):
            self.cmb_font.addItem(name, spec)
            if spec == cur_font:
                cur_idx = idx
        self.cmb_font.setCurrentIndex(cur_idx)
        form.addRow(tr("lbl_font_file"), self.cmb_font)

        self.sp_height = QDoubleSpinBox()
        self.sp_height.setRange(4.0, 150.0)
        self.sp_height.setValue(existing.height if existing else 16.0)
        self.sp_height.setSuffix(" mm")
        form.addRow(tr("lbl_letter_height"), self.sp_height)

        self.sp_spacing = QDoubleSpinBox()
        self.sp_spacing.setRange(-4.0, 20.0)
        self.sp_spacing.setSingleStep(0.2)
        self.sp_spacing.setValue(existing.letter_spacing if existing else 0.6)
        self.sp_spacing.setSuffix(" mm")
        form.addRow(tr("lbl_letter_spacing"), self.sp_spacing)

        self.sp_arc = QDoubleSpinBox()
        self.sp_arc.setRange(-400.0, 400.0)
        self.sp_arc.setSingleStep(5.0)
        self.sp_arc.setValue(existing.arc_radius if existing else 0.0)
        self.sp_arc.setSuffix(tr("sfx_arc"))
        form.addRow(tr("lbl_arc_radius"), self.sp_arc)

        self.cmb_mode = QComboBox()
        for mode in ("auto", "satin", "fill"):
            self.cmb_mode.addItem(tr(f"text_mode_{mode}"), mode)
        if existing:
            idx = self.cmb_mode.findData(existing.mode)
            if idx >= 0:
                self.cmb_mode.setCurrentIndex(idx)
        form.addRow(tr("lbl_stitch_type"), self.cmb_mode)

        self.sp_density = QDoubleSpinBox()
        self.sp_density.setRange(0.25, 0.9)
        self.sp_density.setSingleStep(0.02)
        self.sp_density.setValue(existing.density if existing else 0.38)
        self.sp_density.setSuffix(" mm")
        form.addRow(tr("lbl_stitch_density"), self.sp_density)

        root.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText(tr("btn_apply"))
        btns.button(QDialogButtonBox.Cancel).setText(tr("btn_cancel"))
        btns.accepted.connect(self._apply)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _apply(self):
        txt = self.ed_text.text().strip()
        if not txt:
            QMessageBox.warning(self, tr("dlg_notice"), tr("msg_enter_text"))
            return
        self.created_object = TextObject(
            thread=self.thread,
            name=tr("text_obj_name").format(txt[:18]),
            text=txt,
            font=self.cmb_font.currentData(),
            height=self.sp_height.value(),
            letter_spacing=self.sp_spacing.value(),
            arc_radius=self.sp_arc.value(),
            mode=self.cmb_mode.currentData(),
            density=self.sp_density.value(),
        )
        self.accept()


# ===========================================================================
# 3. Melco EMT10/4 Disketten- & USB-Emulator-Manager
# ===========================================================================
class MelcoDiskDialog(QDialog):
    def __init__(self, plan: StitchPlan, design_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dlg_transfer_title"))
        self.resize(680, 520)
        self.plan = plan
        self.image = Fat12Image()
        self.img_path: str | None = None

        root = QVBoxLayout(self)

        # Abschnitt 1: Dateiname & Trim-Modus
        g1 = QGroupBox(tr("grp_transfer_1"))
        f1 = QFormLayout(g1)
        self.ed_name = QLineEdit(dos_name(design_name, "EXP"))
        f1.addRow(tr("lbl_dos_name"), self.ed_name)

        self.cmb_trim = QComboBox()
        for mode in ("both", "code", "jumps"):
            self.cmb_trim.addItem(tr(f"trim_{mode}"), mode)
        f1.addRow(tr("lbl_trim_mode"), self.cmb_trim)
        root.addWidget(g1)

        # Abschnitt 2: Direkt auf USB-Stick / Diskettenlaufwerk oder per WLAN-NetBridge senden
        g2 = QGroupBox(tr("grp_transfer_2"))
        v2 = QVBoxLayout(g2)
        btn_folder = QPushButton(tr("btn_save_exp_usb"))
        btn_folder.clicked.connect(self._save_direct_exp)
        v2.addWidget(btn_folder)

        hb_net = QHBoxLayout()
        hb_net.addWidget(QLabel(tr("lbl_netbridge_url")))
        self.ed_net_url = QLineEdit("http://raspberrypi.local:8070")
        hb_net.addWidget(self.ed_net_url, 1)
        btn_net = QPushButton(tr("btn_send_netbridge"))
        btn_net.clicked.connect(self._send_netbridge)
        hb_net.addWidget(btn_net)
        v2.addLayout(hb_net)
        root.addWidget(g2)

        # Abschnitt 3: 1.44 MB FAT12 Diskettenabbild (.IMG) für GoTek / FlashFloppy / HxC
        g3 = QGroupBox(tr("grp_transfer_3"))
        v3 = QVBoxLayout(g3)
        self.lbl_img = QLabel(tr("lbl_img_initial"))
        v3.addWidget(self.lbl_img)
        self.list_files = QListWidget()
        v3.addWidget(self.list_files, 1)

        hb = QHBoxLayout()
        btn_open_img = QPushButton(tr("btn_open_img"))
        btn_open_img.clicked.connect(self._open_img)
        btn_add_cur = QPushButton(tr("btn_add_cur_img"))
        btn_add_cur.clicked.connect(self._add_current_to_img)
        btn_del = QPushButton(tr("btn_del_file"))
        btn_del.clicked.connect(self._delete_selected)
        btn_save_img = QPushButton(tr("btn_save_img"))
        btn_save_img.clicked.connect(self._save_img)
        hb.addWidget(btn_open_img)
        hb.addWidget(btn_add_cur)
        hb.addWidget(btn_del)
        hb.addWidget(btn_save_img)
        v3.addLayout(hb)
        root.addWidget(g3, 1)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_box.button(QDialogButtonBox.Close).setText(tr("btn_close"))
        close_box.rejected.connect(self.reject)
        root.addWidget(close_box)

        # Aktuelles Design gleich ins neue Abbild legen
        self._add_current_to_img()

    def _current_exp_bytes(self) -> tuple[str, bytes]:
        name = dos_name(self.ed_name.text().strip() or "DESIGN.EXP", "EXP")
        self.ed_name.setText(name)
        data = exp_bytes(self.plan, trim_mode=self.cmb_trim.currentData())
        return name, data

    def _refresh_list(self):
        self.list_files.clear()
        for fname, size in self.image.list_files():
            self.list_files.addItem(f"{fname:<14}   ({fmt_int(size)} {tr('unit_bytes')})")
        free_kb = self.image.free_bytes() / 1024
        src = self.img_path or tr("img_new")
        self.lbl_img.setText(tr("img_free").format(src=src, free=fmt_float(free_kb), total=fmt_float(1423.5)))

    def _save_direct_exp(self):
        name, data = self._current_exp_bytes()
        path, _ = QFileDialog.getSaveFileName(self, tr("fd_save_exp"), name, "Melco EXP (*.EXP *.exp)")
        if not path:
            return
        with open(path, "wb") as f:
            f.write(data)
        QMessageBox.information(self, tr("msg_saved_title"),
                                tr("msg_exp_saved").format(path=path, size=fmt_int(len(data))))

    def _send_netbridge(self):
        import urllib.request
        name, data = self._current_exp_bytes()
        url = self.ed_net_url.text().strip().rstrip("/") + "/upload"
        req = urllib.request.Request(url, data=data, method="POST", headers={"X-Filename": name})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode("utf-8", "replace")
            QMessageBox.information(self, tr("msg_wifi_ok_title"), tr("msg_wifi_ok_text").format(url=url, body=body))
        except Exception as exc:
            QMessageBox.critical(self, tr("msg_netbridge_fail_title"),
                                 tr("msg_netbridge_fail_text").format(url=url, err=exc))

    def _open_img(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("fd_open_img"), "", f"{tr('filter_floppy')} (*.img *.IMG *.ima *.dsk)"
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                self.image = Fat12Image(f.read())
            self.img_path = path
            self._refresh_list()
        except Exception as exc:
            QMessageBox.critical(self, tr("dlg_error"), str(exc))

    def _add_current_to_img(self):
        try:
            name, data = self._current_exp_bytes()
            self.image.add_file(name, data)
            self._refresh_list()
        except Exception as exc:
            QMessageBox.critical(self, tr("dlg_error"), str(exc))

    def _delete_selected(self):
        item = self.list_files.currentItem()
        if not item:
            return
        fname = item.text().split()[0]
        self.image.delete_file(fname)
        self._refresh_list()

    def _save_img(self):
        default = self.img_path or "DSKA0000.IMG"
        path, _ = QFileDialog.getSaveFileName(
            self, tr("fd_save_img"), default, f"{tr('filter_floppy')} (*.IMG *.img *.ima)"
        )
        if not path:
            return
        with open(path, "wb") as f:
            f.write(self.image.to_bytes())
        self.img_path = path
        self._refresh_list()
        QMessageBox.information(
            self,
            tr("msg_img_saved_title"),
            tr("msg_img_saved_text").format(path=path),
        )


# ===========================================================================
# 4. PhotoStitch-Assistent (Porträtfoto → Gravur-/CMYK-Wellen-Stickerei)
# ===========================================================================
class PhotoStitchDialog(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dlg_photo_title"))
        self.resize(740, 440)
        self.rgba = load_image(image_path)
        self.result_design: Design | None = None

        root = QVBoxLayout(self)
        top = QHBoxLayout()

        v1 = QVBoxLayout()
        self.lbl_orig_title = QLabel(tr("lbl_orig_photo").format(os.path.basename(image_path)))
        self.lbl_orig_title.setAlignment(Qt.AlignCenter)
        self.lbl_orig = QLabel()
        self.lbl_orig.setAlignment(Qt.AlignCenter)
        self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 300))
        btn_change_img = QPushButton(tr("btn_other_photo"))
        btn_change_img.clicked.connect(self._choose_other_image)
        v1.addWidget(self.lbl_orig_title)
        v1.addWidget(self.lbl_orig, 1)
        v1.addWidget(btn_change_img)
        top.addLayout(v1, 1)

        grp = QGroupBox(tr("grp_photo_settings"))
        form = QFormLayout(grp)

        self.sp_width = QDoubleSpinBox()
        self.sp_width.setRange(40.0, 280.0)
        self.sp_width.setValue(110.0)
        self.sp_width.setSuffix(" mm")
        form.addRow(tr("lbl_target_width"), self.sp_width)

        self.cmb_mode = QComboBox()
        for mode in ("mono", "sepia", "color4"):
            self.cmb_mode.addItem(tr(f"photo_mode_{mode}"), mode)
        form.addRow(tr("lbl_color_mode"), self.cmb_mode)

        self.sp_row = QDoubleSpinBox()
        self.sp_row.setRange(0.9, 3.0)
        self.sp_row.setSingleStep(0.1)
        self.sp_row.setValue(1.5)
        self.sp_row.setSuffix(" mm")
        form.addRow(tr("lbl_row_spacing_fine"), self.sp_row)

        self.sp_contrast = QDoubleSpinBox()
        self.sp_contrast.setRange(0.7, 2.2)
        self.sp_contrast.setSingleStep(0.1)
        self.sp_contrast.setValue(1.25)
        form.addRow(tr("lbl_contrast"), self.sp_contrast)

        top.addWidget(grp, 1)
        root.addLayout(top, 1)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText(tr("btn_photo_apply"))
        btns.button(QDialogButtonBox.Cancel).setText(tr("btn_cancel"))
        btns.accepted.connect(self._run)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _choose_other_image(self):
        p = self.parent()
        if p is not None and hasattr(p, "_ask_open_file"):
            path = p._ask_open_file(tr("fd_pick_logo"), _image_filter())
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, tr("fd_pick_logo_short"), "",
                f"{tr('filter_images')} (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff)",
            )
        if not path:
            return
        try:
            self.rgba = load_image(path)
            self.lbl_orig_title.setText(tr("lbl_orig_photo").format(os.path.basename(path)))
            self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 340))
        except Exception as exc:
            QMessageBox.critical(self, tr("err_load_title"), str(exc))

    def _run(self):
        p = PhotoStitchParams(
            width_mm=self.sp_width.value(),
            row_spacing_mm=self.sp_row.value(),
            mode=self.cmb_mode.currentData(),
            contrast=self.sp_contrast.value(),
        )
        try:
            self.result_design = generate_photostitch(self.rgba, p)
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, tr("dlg_error"), str(exc))

