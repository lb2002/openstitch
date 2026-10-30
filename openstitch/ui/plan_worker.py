"""Stichplan-Berechnung im Hintergrund-Thread, damit die Oberfläche beim Editieren flüssig bleibt.

Es läuft höchstens ein Rechen-Thread gleichzeitig (der Objekt-Cache des Designs wird so nie
parallel benutzt). Kommen während einer Berechnung neue Änderungen, wird danach genau einmal
mit dem neuesten Stand nachgerechnet – Zwischenstände werden übersprungen.
"""
from __future__ import annotations

import copy
import threading

from PySide6.QtCore import QObject, Signal

from ..core.design import Design


class PlanBuilder(QObject):
    # (Generation, StitchPlan | None, Fehlertext)
    finished = Signal(int, object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._pending: tuple[int, Design] | None = None
        self._result: tuple[int, object, str] | None = None
        self.generation = 0

    @staticmethod
    def _detach(design: Design) -> Design:
        """Flache Kopien der Objekte: Parameter/Geometrien sind unveränderlich bzw. werden nur
        ersetzt, so kann der Haupt-Thread weiter editieren, ohne die Berechnung zu stören."""
        d = copy.copy(design)       # so kommen auch künftige Felder (z. B. der Stoff) mit
        d.objects = [copy.copy(o) for o in design.objects]
        d.settings = copy.copy(design.settings)
        return d

    def request(self, design: Design) -> int:
        with self._lock:
            self.generation += 1
            self._pending = (self.generation, self._detach(design))
            if self._thread is None:
                self._start_locked()
            return self.generation

    def supersede(self) -> int:
        """Markiert alle laufenden/angeforderten Berechnungen als veraltet."""
        with self._lock:
            self.generation += 1
            self._pending = None
            return self.generation

    def busy(self) -> bool:
        with self._lock:
            return self._thread is not None

    def _start_locked(self):
        gen, d = self._pending
        self._pending = None
        self._thread = threading.Thread(target=self._run, args=(gen, d), daemon=True,
                                        name="openstitch-plan")
        self._thread.start()

    def _run(self, gen: int, d: Design):
        try:
            plan, err = d.build_plan(), ""
        except Exception as exc:  # Fehler im Stichgenerator dürfen die App nicht abstürzen lassen
            plan, err = None, f"{type(exc).__name__}: {exc}"
        with self._lock:
            self._result = (gen, plan, err)
            self._thread = None
            if self._pending is not None:
                self._start_locked()
        self.finished.emit(gen, plan, err)

    def wait(self, timeout: float | None = None) -> tuple[int, object, str] | None:
        """Blockiert, bis alle angeforderten Berechnungen fertig sind (für Export & Tests)."""
        while True:
            with self._lock:
                t = self._thread
                if t is None and self._pending is None:
                    return self._result
            if t is not None:
                t.join(timeout)
                if timeout is not None and t.is_alive():
                    return None
