"""Assistenten-Dialoge: Auto-Digitalisieren, Schrift/Monogramm, Melco EMT10/4 Disketten/USB-Manager."""
from __future__ import annotations

import os

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


class _DigitizeWorker(QThread):
    progress = Signal(str, int)
    finished_ok = Signal(object, object)   # AutoResult, StitchPlan
    failed = Signal(str)

    def __init__(self, rgba: np.ndarray, params: AutoParams):
        super().__init__()
        self.rgba = rgba
        self.params = params

    def run(self):
        try:
            res = auto_digitize(
                self.rgba,
                self.params,
                progress=lambda msg, v: self.progress.emit(msg, int(v * 0.55)),
            )
            total = max(1, len(res.design.objects))
            plan = res.design.build_plan(
                progress=lambda i, n: self.progress.emit(
                    f"Stiche berechnen ({i}/{n}) …", 55 + int(45 * i / max(1, n))
                )
            )
            self.finished_ok.emit(res, plan)
        except Exception as exc:
            self.failed.emit(str(exc))


# ===========================================================================
# 1. Auto-Digitalisieren (Bild → Stickdatei)
# ===========================================================================
class AutoDigitizeDialog(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bild automatisch digitalisieren (Auto-Digitizer)")
        self.resize(860, 560)
        self.rgba = load_image(image_path)
        self.result_data: AutoResult | None = None
        self.result_plan: StitchPlan | None = None
        self._worker: _DigitizeWorker | None = None

        root = QVBoxLayout(self)

        top = QHBoxLayout()
        # Vorschau Original
        v1 = QVBoxLayout()
        lbl_t1 = QLabel(f"Originalbild ({os.path.basename(image_path)})")
        lbl_t1.setAlignment(Qt.AlignCenter)
        self.lbl_orig_title = lbl_t1
        self.lbl_orig = QLabel()
        self.lbl_orig.setAlignment(Qt.AlignCenter)
        self.lbl_orig.setMinimumSize(320, 320)
        self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 340))
        btn_change_img = QPushButton("📂 Anderes Bild wählen (Downloads / Desktop / Bilder …)")
        btn_change_img.clicked.connect(self._choose_other_image)
        v1.addWidget(lbl_t1)
        v1.addWidget(self.lbl_orig, 1)
        v1.addWidget(btn_change_img)
        top.addLayout(v1, 1)

        # Einstellungen rechts
        grp = QGroupBox("Stick-Einstellungen & Automatik")
        form = QFormLayout(grp)

        self.sp_width = QDoubleSpinBox()
        self.sp_width.setRange(15.0, 350.0)
        self.sp_width.setValue(95.0)
        self.sp_width.setSuffix(" mm")
        form.addRow("Zielbreite des Motivs:", self.sp_width)

        self.sp_colors = QSpinBox()
        self.sp_colors.setRange(1, 16)
        self.sp_colors.setValue(6)
        form.addRow("Max. Garnfarben (Nadeln):", self.sp_colors)

        self.cb_bg = QCheckBox("Bildhintergrund automatisch entfernen")
        self.cb_bg.setChecked(True)
        form.addRow("", self.cb_bg)

        self.cmb_fabric = QComboBox()
        self.cmb_fabric.addItem("Standard (Baumwolle / Twill / Universal)", "normal")
        self.cmb_fabric.addItem("Piqué / Polo / Strick (mehr Zugkompensation)", "strick")
        self.cmb_fabric.addItem("Frottee / Handtuch (dichter + starke Unterlage)", "frottee")
        self.cmb_fabric.addItem("Kappe / Cap (hohe Zugkompensation)", "cap")
        self.cmb_fabric.addItem("Leichter Stoff / Hemd (geringere Dichte)", "leicht")
        form.addRow("Stoffart / Material:", self.cmb_fabric)

        self.sp_density = QDoubleSpinBox()
        self.sp_density.setRange(0.28, 1.0)
        self.sp_density.setSingleStep(0.02)
        self.sp_density.setValue(0.40)
        self.sp_density.setSuffix(" mm")
        form.addRow("Stichdichte (Reihenabstand):", self.sp_density)

        self.sp_satin = QDoubleSpinBox()
        self.sp_satin.setRange(2.0, 10.0)
        self.sp_satin.setSingleStep(0.5)
        self.sp_satin.setValue(6.5)
        self.sp_satin.setSuffix(" mm")
        form.addRow("Satin-Grenze (schmaler = Satin):", self.sp_satin)

        self.sp_min_area = QDoubleSpinBox()
        self.sp_min_area.setRange(0.3, 15.0)
        self.sp_min_area.setSingleStep(0.5)
        self.sp_min_area.setValue(1.5)
        self.sp_min_area.setSuffix(" mm²")
        form.addRow("Kleinstteile filtern unter:", self.sp_min_area)

        self.cb_outline = QCheckBox("Zusätzliche Satinkontur um das Motiv legen")
        form.addRow("", self.cb_outline)

        self.cb_palette = QCheckBox("Farben an Stickgarn-Palette anpassen")
        self.cb_palette.setChecked(True)
        form.addRow("", self.cb_palette)

        top.addWidget(grp, 1)
        root.addLayout(top, 1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.lbl_status = QLabel("Bereit.")
        root.addWidget(self.lbl_status)
        root.addWidget(self.progress)

        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btn_ok = self.btns.button(QDialogButtonBox.Ok)
        self.btn_ok.setText("Jetzt digitalisieren && übernehmen")
        self.btns.button(QDialogButtonBox.Cancel).setText("Abbrechen")
        self.btns.accepted.connect(self._run)
        self.btns.rejected.connect(self.reject)
        root.addWidget(self.btns)

    def _choose_other_image(self):
        p = self.parent()
        if p is not None and hasattr(p, "_ask_open_file"):
            path = p._ask_open_file(
                "Bild oder Logo wählen (Downloads / Bilder / Desktop)",
                "Alle Bilder (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff);;Alle Dateien (*.*)",
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Bild oder Logo wählen", "", "Bilder (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff)"
            )
        if not path:
            return
        try:
            self.rgba = load_image(path)
            self.lbl_orig_title.setText(f"Originalbild ({os.path.basename(path)})")
            self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 340))
        except Exception as exc:
            QMessageBox.critical(self, "Fehler beim Laden", str(exc))

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
        self._worker = _DigitizeWorker(self.rgba, p)
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
        QMessageBox.critical(self, "Fehler beim Digitalisieren", err)


# ===========================================================================
# 2. Schrift & Monogramme
# ===========================================================================
class TextDialog(QDialog):
    def __init__(self, thread: Thread, existing: TextObject | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Schrift / Monogramm erstellen")
        self.resize(520, 380)
        self.thread = thread
        self.existing = existing
        self.created_object: TextObject | None = None

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.ed_text = QLineEdit(existing.text if existing else "OPENSTITCH")
        form.addRow("Text:", self.ed_text)

        self.cmb_font = QComboBox()
        self._fonts = list_fonts()
        cur_font = existing.font if existing else default_font()
        cur_idx = 0
        for idx, (name, spec) in enumerate(self._fonts.items()):
            self.cmb_font.addItem(name, spec)
            if spec == cur_font:
                cur_idx = idx
        self.cmb_font.setCurrentIndex(cur_idx)
        form.addRow("Schriftart (TTF/OTF):", self.cmb_font)

        self.sp_height = QDoubleSpinBox()
        self.sp_height.setRange(4.0, 150.0)
        self.sp_height.setValue(existing.height if existing else 16.0)
        self.sp_height.setSuffix(" mm")
        form.addRow("Buchstabenhöhe (Versalhöhe):", self.sp_height)

        self.sp_spacing = QDoubleSpinBox()
        self.sp_spacing.setRange(-4.0, 20.0)
        self.sp_spacing.setSingleStep(0.2)
        self.sp_spacing.setValue(existing.letter_spacing if existing else 0.6)
        self.sp_spacing.setSuffix(" mm")
        form.addRow("Zeichenabstand:", self.sp_spacing)

        self.sp_arc = QDoubleSpinBox()
        self.sp_arc.setRange(-400.0, 400.0)
        self.sp_arc.setSingleStep(5.0)
        self.sp_arc.setValue(existing.arc_radius if existing else 0.0)
        self.sp_arc.setSuffix(" mm (0 = gerade)")
        form.addRow("Bogenradius:", self.sp_arc)

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItem("Automatisch (Satin bis 7 mm, darüber Tatami)", "auto")
        self.cmb_mode.addItem("Immer Satinstich (Glanz-Schrift)", "satin")
        self.cmb_mode.addItem("Immer Tatami-Füllstich", "fill")
        if existing:
            idx = self.cmb_mode.findData(existing.mode)
            if idx >= 0:
                self.cmb_mode.setCurrentIndex(idx)
        form.addRow("Stichart:", self.cmb_mode)

        self.sp_density = QDoubleSpinBox()
        self.sp_density.setRange(0.25, 0.9)
        self.sp_density.setSingleStep(0.02)
        self.sp_density.setValue(existing.density if existing else 0.38)
        self.sp_density.setSuffix(" mm")
        form.addRow("Stichdichte:", self.sp_density)

        root.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Übernehmen")
        btns.button(QDialogButtonBox.Cancel).setText("Abbrechen")
        btns.accepted.connect(self._apply)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _apply(self):
        txt = self.ed_text.text().strip()
        if not txt:
            QMessageBox.warning(self, "Hinweis", "Bitte einen Text eingeben.")
            return
        self.created_object = TextObject(
            thread=self.thread,
            name=f'Text „{txt[:18]}“',
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
        self.setWindowTitle("Maschinen-Transfer (USB / 1.44 MB Disketten-Emulator / WLAN NetBridge)")
        self.resize(680, 520)
        self.plan = plan
        self.image = Fat12Image()
        self.img_path: str | None = None

        root = QVBoxLayout(self)

        # Abschnitt 1: Dateiname & Trim-Modus
        g1 = QGroupBox("1. Maschinen- & Trim-Einstellungen (EXP / Industrie-Format)")
        f1 = QFormLayout(g1)
        self.ed_name = QLineEdit(dos_name(design_name, "EXP"))
        f1.addRow("DOS-Dateiname (8.3-Format):", self.ed_name)

        self.cmb_trim = QComboBox()
        self.cmb_trim.addItem("Kombi: EXP-Trim-Code + 3 Sprünge (höchste Kompatibilität)", "both")
        self.cmb_trim.addItem("Standard EXP-Trim-Code (80 80 07 00)", "code")
        self.cmb_trim.addItem("Nur Sprungfolge (für ältere EMT-Firmware)", "jumps")
        f1.addRow("Fadenschnitt (Trim)-Modus:", self.cmb_trim)
        root.addWidget(g1)

        # Abschnitt 2: Direkt auf USB-Stick / Diskettenlaufwerk oder per WLAN-NetBridge senden
        g2 = QGroupBox("2. Direkt auf USB-Stick / Laufwerk oder über WLAN-NetBridge senden")
        v2 = QVBoxLayout(g2)
        btn_folder = QPushButton("EXP direkt auf USB-Stick / Ordner speichern …")
        btn_folder.clicked.connect(self._save_direct_exp)
        v2.addWidget(btn_folder)

        hb_net = QHBoxLayout()
        hb_net.addWidget(QLabel("NetBridge-URL:"))
        self.ed_net_url = QLineEdit("http://raspberrypi.local:8070")
        hb_net.addWidget(self.ed_net_url, 1)
        btn_net = QPushButton("Über WLAN an Melco NetBridge senden")
        btn_net.clicked.connect(self._send_netbridge)
        hb_net.addWidget(btn_net)
        v2.addLayout(hb_net)
        root.addWidget(g2)

        # Abschnitt 3: 1.44 MB FAT12 Diskettenabbild (.IMG) für GoTek / FlashFloppy / HxC
        g3 = QGroupBox("3. 1.44 MB FAT12-Diskettenabbild (.IMG) für USB-Emulator (GoTek / HxC)")
        v3 = QVBoxLayout(g3)
        self.lbl_img = QLabel("Aktuelles Abbild: Neues leeres 1.44-MB-Abbild (FAT12)")
        v3.addWidget(self.lbl_img)
        self.list_files = QListWidget()
        v3.addWidget(self.list_files, 1)

        hb = QHBoxLayout()
        btn_open_img = QPushButton("Bestehendes .IMG öffnen …")
        btn_open_img.clicked.connect(self._open_img)
        btn_add_cur = QPushButton("Aktuelles Design ins Abbild einfügen")
        btn_add_cur.clicked.connect(self._add_current_to_img)
        btn_del = QPushButton("Ausgewählte Datei löschen")
        btn_del.clicked.connect(self._delete_selected)
        btn_save_img = QPushButton(".IMG-Datei speichern …")
        btn_save_img.clicked.connect(self._save_img)
        hb.addWidget(btn_open_img)
        hb.addWidget(btn_add_cur)
        hb.addWidget(btn_del)
        hb.addWidget(btn_save_img)
        v3.addLayout(hb)
        root.addWidget(g3, 1)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
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
            self.list_files.addItem(f"{fname:<14}   ({size:,} Bytes)".replace(",", "'"))
        free_kb = self.image.free_bytes() / 1024
        src = self.img_path or "Neues 1.44-MB-Abbild"
        self.lbl_img.setText(f"{src}  —  Freier Speicher: {free_kb:.1f} KB von 1'423.5 KB")

    def _save_direct_exp(self):
        name, data = self._current_exp_bytes()
        path, _ = QFileDialog.getSaveFileName(self, "Melco EXP speichern", name, "Melco EXP (*.EXP *.exp)")
        if not path:
            return
        with open(path, "wb") as f:
            f.write(data)
        QMessageBox.information(self, "Gespeichert", f"Melco-Stickdatei gespeichert:\n{path}\n({len(data)} Bytes)")

    def _send_netbridge(self):
        import urllib.request
        name, data = self._current_exp_bytes()
        url = self.ed_net_url.text().strip().rstrip("/") + "/upload"
        req = urllib.request.Request(url, data=data, method="POST", headers={"X-Filename": name})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode("utf-8", "replace")
            QMessageBox.information(self, "WLAN-Übertragung erfolgreich", f"Gesendet an {url}:\n{body}")
        except Exception as exc:
            QMessageBox.critical(self, "NetBridge nicht erreichbar", f"Konnte {url} nicht erreichen:\n{exc}")

    def _open_img(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "FAT12-Diskettenabbild öffnen", "", "Diskettenabbild (*.img *.IMG *.ima *.dsk)"
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                self.image = Fat12Image(f.read())
            self.img_path = path
            self._refresh_list()
        except Exception as exc:
            QMessageBox.critical(self, "Fehler", str(exc))

    def _add_current_to_img(self):
        try:
            name, data = self._current_exp_bytes()
            self.image.add_file(name, data)
            self._refresh_list()
        except Exception as exc:
            QMessageBox.critical(self, "Fehler", str(exc))

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
            self, "1.44 MB FAT12-Diskettenabbild speichern", default, "Diskettenabbild (*.IMG *.img *.ima)"
        )
        if not path:
            return
        with open(path, "wb") as f:
            f.write(self.image.to_bytes())
        self.img_path = path
        self._refresh_list()
        QMessageBox.information(
            self,
            "Diskettenabbild gespeichert",
            f"1.44-MB-FAT12-Abbild gespeichert:\n{path}\n\n"
            "Tipp für GoTek/FlashFloppy: Benenne die Bilder auf dem USB-Stick z. B. "
            "DSKA0000.IMG, DSKA0001.IMG oder kopiere die .EXP-Datei direkt, falls FlashFloppy "
            "im Direct-File-Modus läuft.",
        )


# ===========================================================================
# 4. PhotoStitch-Assistent (Porträtfoto → Gravur-/CMYK-Wellen-Stickerei)
# ===========================================================================
class PhotoStitchDialog(QDialog):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PhotoStitch — Porträt- & Foto-Stickerei erzeugen")
        self.resize(740, 440)
        self.rgba = load_image(image_path)
        self.result_design: Design | None = None

        root = QVBoxLayout(self)
        top = QHBoxLayout()

        v1 = QVBoxLayout()
        self.lbl_orig_title = QLabel(f"Originalfoto ({os.path.basename(image_path)})")
        self.lbl_orig_title.setAlignment(Qt.AlignCenter)
        self.lbl_orig = QLabel()
        self.lbl_orig.setAlignment(Qt.AlignCenter)
        self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 300))
        btn_change_img = QPushButton("📂 Anderes Foto wählen (Downloads / Desktop / Bilder …)")
        btn_change_img.clicked.connect(self._choose_other_image)
        v1.addWidget(self.lbl_orig_title)
        v1.addWidget(self.lbl_orig, 1)
        v1.addWidget(btn_change_img)
        top.addLayout(v1, 1)

        grp = QGroupBox("PhotoStitch-Einstellungen")
        form = QFormLayout(grp)

        self.sp_width = QDoubleSpinBox()
        self.sp_width.setRange(40.0, 280.0)
        self.sp_width.setValue(110.0)
        self.sp_width.setSuffix(" mm")
        form.addRow("Zielbreite:", self.sp_width)

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItem("Monochrom-Gravur (1 Garnfarbe auf hellem Stoff)", "mono")
        self.cmb_mode.addItem("Sepia-Porträt (2 Garnfarben: Hellbraun + Dunkelbraun)", "sepia")
        self.cmb_mode.addItem("4-Farb CMYK-Halbton (Gelb, Magenta, Cyan, Schwarz)", "color4")
        form.addRow("Farbmodus:", self.cmb_mode)

        self.sp_row = QDoubleSpinBox()
        self.sp_row.setRange(0.9, 3.0)
        self.sp_row.setSingleStep(0.1)
        self.sp_row.setValue(1.5)
        self.sp_row.setSuffix(" mm")
        form.addRow("Zeilenabstand (Feinheit):", self.sp_row)

        self.sp_contrast = QDoubleSpinBox()
        self.sp_contrast.setRange(0.7, 2.2)
        self.sp_contrast.setSingleStep(0.1)
        self.sp_contrast.setValue(1.25)
        form.addRow("Kontrast-Verstärkung:", self.sp_contrast)

        top.addWidget(grp, 1)
        root.addLayout(top, 1)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("PhotoStitch berechnen && übernehmen")
        btns.accepted.connect(self._run)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _choose_other_image(self):
        p = self.parent()
        if p is not None and hasattr(p, "_ask_open_file"):
            path = p._ask_open_file(
                "Bild oder Logo wählen (Downloads / Bilder / Desktop)",
                "Alle Bilder (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff);;Alle Dateien (*.*)",
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Bild oder Logo wählen", "", "Bilder (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff)"
            )
        if not path:
            return
        try:
            self.rgba = load_image(path)
            self.lbl_orig_title.setText(f"Originalbild ({os.path.basename(path)})")
            self.lbl_orig.setPixmap(_np_to_pixmap(self.rgba, 340))
        except Exception as exc:
            QMessageBox.critical(self, "Fehler beim Laden", str(exc))

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
            QMessageBox.critical(self, "Fehler", str(exc))

