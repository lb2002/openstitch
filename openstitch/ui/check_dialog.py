"""Design-Prüfung: virtueller Probestick mit Punktzahl, Befunden in Klartext und Stoffvorschau."""
from __future__ import annotations

import copy

from PySide6.QtCore import QPointF, QRectF, Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..analysis import Report, simulate_stitchout
from ..analysis.roundtrip import RoundTrip, check_format
from ..core.design import Design
from ..core.stitchplan import Cmd, ColorBlock, Stitch, StitchPlan
from ..i18n import fmt_float, fmt_int, tr
from ..render import render_image
from . import theme

CANVAS_COLOR = {"slate": (52, 58, 72), "sand": (188, 182, 170), "light": (226, 222, 214)}
SEVERITY_KEY = {"error": "chk_sev_error", "warning": "chk_sev_warning", "info": "chk_sev_info"}


class _CheckWorker(QThread):
    done = Signal(object, object)      # Report, RoundTrip
    failed = Signal(str)

    def __init__(self, design: Design, plan: StitchPlan, needles: int, ext: str, parent=None):
        super().__init__(parent)
        self.design, self.plan, self.needles, self.ext = design, plan, needles, ext

    def run(self):
        try:
            report = simulate_stitchout(self.design, self.plan, needles=self.needles)
            export = check_format(self.plan, self.ext) if self.plan.stitch_count else None
            self.done.emit(report, export)
        except Exception as exc:  # noqa: BLE001 - die Prüfung soll das Programm nie mitreissen
            self.failed.emit(str(exc))


class ScoreRing(QWidget):
    """Punktzahl als Ring: auf einen Blick sichtbar, auch ohne die Zahl zu lesen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.score: int | None = None
        self.setFixedSize(78, 78)

    def set_score(self, score: int | None):
        self.score = score
        self.update()

    def paintEvent(self, _ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = QRectF(7, 7, self.width() - 14, self.height() - 14)
        p.setPen(QPen(theme.color("surface_top"), 8))
        p.drawEllipse(r)
        if self.score is None:
            return
        name = "ok" if self.score >= 85 else "warn" if self.score >= 60 else "err"
        p.setPen(QPen(theme.color(name), 8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 90 * 16, -int(self.score / 100 * 360 * 16))
        p.setPen(theme.color("text"))
        f = QFont(self.font())
        f.setPointSizeF(15)
        f.setBold(True)
        p.setFont(f)
        p.drawText(self.rect(), Qt.AlignCenter, str(self.score))


def distorted_plan(plan: StitchPlan, report: Report, factor: float) -> StitchPlan:
    """Stichplan so, wie er nach dem Fadenzug auf dem Stoff liegt (zur Sicht verstärkt um `factor`)."""
    pull = report.pull
    if pull is None:
        return plan
    shift = {int(i): (float(dx), float(dy)) for i, dx, dy in zip(pull.idx, pull.dx, pull.dy)}
    out = StitchPlan()
    n = 0
    for b in plan.blocks:
        nb = ColorBlock(b.thread, object_ids=b.object_ids)
        for s in b.stitches:
            dx, dy = shift.get(n, (0.0, 0.0))
            if s.cmd == Cmd.STITCH:
                nb.stitches.append(Stitch(s.x + dx * factor, s.y + dy * factor, s.cmd))
            else:
                nb.stitches.append(Stitch(s.x, s.y, s.cmd))
            n += 1
        out.blocks.append(nb)
    return out


class DesignCheckDialog(QDialog):
    """Nicht modal: Über „Zeigen“ soll man die Stelle auf der Leinwand ansehen können."""

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self._worker: _CheckWorker | None = None
        self._report: Report | None = None
        self._plan: StitchPlan | None = None
        self.setWindowTitle(tr("chk_title"))
        self.resize(900, 620)
        self.setModal(False)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(16)
        self.ring = ScoreRing()
        head.addWidget(self.ring)
        col = QVBoxLayout()
        col.setSpacing(2)
        self.lbl_verdict = QLabel(tr("chk_running"))
        self.lbl_verdict.setProperty("role", "title")
        self.lbl_facts = QLabel()
        self.lbl_facts.setProperty("role", "subtitle")
        self.lbl_facts.setWordWrap(True)
        col.addStretch(1)
        col.addWidget(self.lbl_verdict)
        col.addWidget(self.lbl_facts)
        col.addStretch(1)
        head.addLayout(col, 1)
        self.btn_again = QPushButton(tr("chk_again"))
        self.btn_again.clicked.connect(self.start)
        head.addWidget(self.btn_again, 0, Qt.AlignTop)
        root.addLayout(head)

        body = QHBoxLayout()
        body.setSpacing(14)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_host = QWidget()
        self.list_lay = QVBoxLayout(self.list_host)
        self.list_lay.setContentsMargins(0, 0, 6, 0)
        self.list_lay.setSpacing(8)
        self.list_lay.addStretch(1)
        scroll.setWidget(self.list_host)
        body.addWidget(scroll, 5)

        right = QVBoxLayout()
        right.setSpacing(6)
        cap = QLabel(tr("chk_preview"))
        cap.setProperty("role", "section")
        right.addWidget(cap)
        self.lbl_preview = QLabel()
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setMinimumSize(320, 300)
        self.lbl_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right.addWidget(self.lbl_preview, 1)
        row = QHBoxLayout()
        lbl = QLabel(tr("chk_boost"))
        lbl.setProperty("role", "caption")
        self.lbl_boost = QLabel("×1")
        self.lbl_boost.setProperty("role", "caption")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 6)
        self.slider.setValue(3)
        self.slider.valueChanged.connect(self._update_preview)
        row.addWidget(lbl)
        row.addWidget(self.slider, 1)
        row.addWidget(self.lbl_boost)
        right.addLayout(row)
        body.addLayout(right, 4)
        root.addLayout(body, 1)

        self.lbl_foot = QLabel(tr("chk_disclaimer"))
        self.lbl_foot.setProperty("role", "caption")
        self.lbl_foot.setWordWrap(True)
        root.addWidget(self.lbl_foot)

    # ---------------------------------------------------------------- Ablauf
    def showEvent(self, ev):
        super().showEvent(ev)
        self.start()

    def start(self):
        if self._worker is not None and self._worker.isRunning():
            return
        win = self.win
        win.wait_for_plan()
        d = win.canvas.design
        # Eigene Kopie: Das Fenster bleibt bedienbar, während im Hintergrund geprüft wird
        design = copy.copy(d)
        design.objects = [o.snapshot() for o in d.objects]
        design._cache = {}
        self._plan = win.canvas.plan
        mp = win.cmb_machine.currentData()
        self.btn_again.setEnabled(False)
        self.ring.set_score(None)
        self.lbl_verdict.setText(tr("chk_running"))
        self.lbl_facts.clear()
        self._clear_list()
        self._worker = _CheckWorker(design, self._plan, d.settings.needles, mp.native_ext if mp else "dst", self)
        self._worker.done.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def closeEvent(self, ev):
        if self._worker is not None:
            self._worker.wait(15000)
        super().closeEvent(ev)

    def _on_failed(self, msg: str):
        self.btn_again.setEnabled(True)
        self.lbl_verdict.setText(tr("chk_failed"))
        self.lbl_facts.setText(msg)

    def _on_done(self, report: Report, export: RoundTrip | None):
        self._report = report
        self.btn_again.setEnabled(True)
        plan = self._plan
        if plan.stitch_count == 0:
            self.lbl_verdict.setText(tr("chk_empty"))
            return
        self.ring.set_score(report.score)
        key = "chk_good" if report.score >= 85 and report.ok else "chk_ok" if report.score >= 60 and report.ok else "chk_bad"
        self.lbl_verdict.setText(tr(key))
        self.lbl_facts.setText(tr("chk_facts").format(
            st=fmt_int(plan.stitch_count), colors=len(plan.blocks), trims=plan.trim_count,
            min=fmt_float(plan.estimated_minutes(self.win.canvas.design.settings.machine_spm), 0),
            thread=fmt_float(plan.thread_length_m(), 0)))
        for f in report.findings:
            self._add_row(f)
        if export is not None:
            self._add_export_row(export)
        if not report.findings:
            none = QLabel(tr("chk_none"))
            none.setProperty("severity", "ok")
            self.list_lay.insertWidget(self.list_lay.count() - 1, none)
        self._update_preview()

    # ---------------------------------------------------------------- Befunde
    def _clear_list(self):
        while self.list_lay.count() > 1:
            w = self.list_lay.takeAt(0).widget()
            if w is not None:
                w.deleteLater()

    def _card(self, severity: str, title: str, text: str) -> tuple[QFrame, QHBoxLayout]:
        card = QFrame()
        card.setObjectName("card")
        v = QVBoxLayout(card)
        v.setContentsMargins(12, 9, 12, 9)
        v.setSpacing(3)
        t = QLabel(title)
        t.setProperty("severity", severity)
        t.setWordWrap(True)
        d = QLabel(text)
        d.setProperty("role", "cardText")
        d.setWordWrap(True)
        v.addWidget(t)
        v.addWidget(d)
        row = QHBoxLayout()
        row.setSpacing(6)
        row.addStretch(1)
        v.addLayout(row)
        self.list_lay.insertWidget(self.list_lay.count() - 1, card)
        return card, row

    def _add_row(self, f):
        data = dict(f.data)
        data.setdefault("count", f.count)
        fmt = {k: (fmt_float(v, 1) if isinstance(v, float) else v) for k, v in data.items()}
        fmt["count"] = fmt_int(f.count)
        _card, row = self._card(f.severity, tr(f"chk_{f.code}_t"), tr(f"chk_{f.code}_d").format(**fmt))
        if f.where:
            b = QPushButton(tr("chk_show"))
            b.clicked.connect(lambda _=False, pts=f.where: self.win.canvas.show_spots(pts))
            row.addWidget(b)
        fix = self.win.fix_for(f.code)
        if fix is not None:
            b = QPushButton(tr("chk_fix"))
            b.setObjectName("primaryBtn")
            b.clicked.connect(lambda _=False, fn=fix: self._apply_fix(fn))
            row.addWidget(b)

    def _add_export_row(self, r: RoundTrip):
        ext = r.ext.upper()
        if r.ok:
            self._card("ok", tr("chk_export_ok_t").format(ext=ext),
                       tr("chk_export_ok_d").format(st=fmt_int(r.stitches), err=fmt_float(r.max_error_mm, 2)))
        else:
            self._card("error", tr("chk_export_bad_t").format(ext=ext), "; ".join(r.problems))

    def _apply_fix(self, fn):
        fn()
        self.start()

    # --------------------------------------------------------------- Vorschau
    def _update_preview(self):
        factor = self.slider.value()
        self.lbl_boost.setText(f"×{factor}")
        if self._report is None or self._plan is None or self._plan.stitch_count == 0:
            return
        bg = CANVAS_COLOR.get(self.win.canvas.fabric_theme, CANVAS_COLOR["slate"])
        plan = distorted_plan(self._plan, self._report, float(factor))
        x0, y0, x1, y1 = plan.bounds()
        size = max(x1 - x0, y1 - y0, 10.0)
        img: QImage = render_image(plan, px_per_mm=min(620.0 / size, 12.0), margin_mm=3.0, background=bg)
        pix = QPixmap.fromImage(img)
        self.lbl_preview.setPixmap(pix.scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
