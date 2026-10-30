"""Startseite: führt in zwei Klicks zum ersten Design, auch ohne Stick-Vorwissen."""
from __future__ import annotations

import os

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..render import render_image
from ..samples import SAMPLES
from ..i18n import tr
from .onboarding import studio_icon


class _ThumbWorker(QThread):
    """Rendert die Beispiel-Vorschauen im Hintergrund: Der Start bleibt sofort bedienbar."""
    ready = Signal(str, QImage)

    def run(self):
        for sid, _key, factory in SAMPLES:
            if self.isInterruptionRequested():
                return
            try:
                plan = factory().build_plan()
                self.ready.emit(sid, render_image(plan, px_per_mm=4.0, margin_mm=4.0, background=None))
            except Exception:  # noqa: BLE001 - eine fehlende Vorschau darf den Start nicht stören
                continue


class StartPage(QWidget):
    """Kacheln für die häufigsten Wege, darunter Beispiele und zuletzt geöffnete Dateien."""
    chosen = Signal(str)            # "image" | "text" | "draw" | "open"
    sample_chosen = Signal(str)
    recent_chosen = Signal(str)
    tour_requested = Signal()

    def __init__(self, bind, icon, parent=None):
        super().__init__(parent)
        self.setObjectName("startPage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._bind = bind
        self._icon = icon
        self._thumbs: dict[str, QToolButton] = {}
        self._worker: _ThumbWorker | None = None

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        body = QWidget()
        body.setObjectName("startPage")
        scroll.setWidget(body)
        wrap = QHBoxLayout(body)
        wrap.addStretch(1)
        col = QVBoxLayout()
        col.setContentsMargins(24, 30, 24, 24)
        col.setSpacing(14)
        holder = QWidget()
        holder.setObjectName("startPage")
        holder.setMaximumWidth(920)
        holder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        holder.setLayout(col)
        wrap.addWidget(holder, 6)
        wrap.addStretch(1)

        title = QLabel()
        title.setProperty("role", "title")
        bind(title.setText, "start_title")
        sub = QLabel()
        sub.setProperty("role", "subtitle")
        sub.setWordWrap(True)
        bind(sub.setText, "start_subtitle")
        col.addWidget(title)
        col.addWidget(sub)
        col.addSpacing(8)

        cards = QGridLayout()
        cards.setSpacing(12)
        for i, (what, kind, key_t, key_d) in enumerate((
            ("image", "magic", "start_image", "start_image_d"),
            ("text", "text", "start_text", "start_text_d"),
            ("draw", "fill", "start_draw", "start_draw_d"),
            ("open", "open", "start_open", "start_open_d"),
        )):
            cards.addWidget(self._card(what, kind, key_t, key_d), i // 2, i % 2)
        col.addLayout(cards)
        col.addSpacing(10)

        lbl = QLabel()
        lbl.setProperty("role", "section")
        bind(lbl.setText, "start_samples")
        col.addWidget(lbl)
        row = QHBoxLayout()
        row.setSpacing(10)
        for sid, key, _factory in SAMPLES:
            b = QToolButton()
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            b.setIconSize(QSize(130, 110))
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setCursor(Qt.PointingHandCursor)
            bind(b.setText, key)
            b.clicked.connect(lambda _=False, s=sid: self.sample_chosen.emit(s))
            self._thumbs[sid] = b
            row.addWidget(b)
        col.addLayout(row)

        self.recent_title = QLabel()
        self.recent_title.setProperty("role", "section")
        bind(self.recent_title.setText, "start_recent")
        col.addWidget(self.recent_title)
        self.recent_box = QVBoxLayout()
        self.recent_box.setSpacing(0)
        col.addLayout(self.recent_box)

        tour = QPushButton()
        tour.setObjectName("linkBtn")
        tour.setCursor(Qt.PointingHandCursor)
        bind(tour.setText, "start_tour")
        tour.clicked.connect(self.tour_requested)
        col.addWidget(tour, 0, Qt.AlignLeft)
        col.addStretch(1)

    def _card(self, what: str, kind: str, key_t: str, key_d: str) -> QPushButton:
        """Kachel mit Symbol, Titel und einem Satz: Beschreibung im Button statt nur im Tooltip."""
        b = QPushButton()
        b.setObjectName("startCard")
        b.setCursor(Qt.PointingHandCursor)
        b.setMinimumHeight(86)
        b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        h = QHBoxLayout(b)
        h.setContentsMargins(14, 10, 14, 10)
        h.setSpacing(14)
        ic = QLabel()
        ic.setAttribute(Qt.WA_TransparentForMouseEvents)
        ic.setPixmap(studio_icon(kind, 30).pixmap(30, 30))
        self._icon(lambda i, l=ic: l.setPixmap(i.pixmap(30, 30)), kind, 30)
        h.addWidget(ic, 0, Qt.AlignVCenter)
        v = QVBoxLayout()
        v.setSpacing(2)
        t = QLabel()
        t.setProperty("role", "strong")
        t.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._bind(t.setText, key_t)
        self._bind(b.setAccessibleName, key_t)
        d = QLabel()
        d.setProperty("role", "cardText")
        d.setWordWrap(True)
        d.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._bind(d.setText, key_d)
        self._bind(b.setAccessibleDescription, key_d)
        v.addWidget(t)
        v.addWidget(d)
        h.addLayout(v, 1)
        b.clicked.connect(lambda _=False, w=what: self.chosen.emit(w))
        return b

    def load_thumbnails(self):
        if self._worker is not None:
            return
        self._worker = _ThumbWorker(self)
        self._worker.ready.connect(self._set_thumb)
        self._worker.start()

    def _set_thumb(self, sid: str, img: QImage):
        b = self._thumbs.get(sid)
        if b is not None:
            # Auf feste Fläche zentrieren, damit alle Beschriftungen auf einer Linie stehen
            pix = QPixmap.fromImage(img).scaled(b.iconSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            canvas = QPixmap(b.iconSize())
            canvas.fill(Qt.transparent)
            p = QPainter(canvas)
            p.drawPixmap((canvas.width() - pix.width()) // 2, (canvas.height() - pix.height()) // 2, pix)
            p.end()
            b.setIcon(QIcon(canvas))

    def set_recent(self, paths: list[str]):
        while self.recent_box.count():
            w = self.recent_box.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        self.recent_title.setVisible(bool(paths))
        for path in paths[:5]:
            b = QPushButton(os.path.basename(path))
            b.setObjectName("linkBtn")
            b.setToolTip(path)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, p=path: self.recent_chosen.emit(p))
            self.recent_box.addWidget(b, 0, Qt.AlignLeft)

    def stop(self):
        if self._worker is not None:
            self._worker.requestInterruption()
            self._worker.wait(4000)
