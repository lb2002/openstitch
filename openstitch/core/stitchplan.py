"""Maschinenunabhängiger Stichplan.

Alle Koordinaten sind in Millimetern, Y-Achse zeigt nach unten (wie am Bildschirm).
Die Exporter konvertieren in die jeweiligen Maschineneinheiten (meist 0.1 mm).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
import math


class Cmd(IntEnum):
    STITCH = 0
    JUMP = 1
    TRIM = 2
    COLOR_CHANGE = 3
    STOP = 4
    END = 5


@dataclass
class Stitch:
    x: float
    y: float
    cmd: Cmd = Cmd.STITCH


@dataclass
class Thread:
    color: tuple[int, int, int]
    name: str = ""
    code: str = ""
    brand: str = ""

    @property
    def hex(self) -> str:
        r, g, b = self.color
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def from_hex(h: str, name: str = "", code: str = "", brand: str = "") -> "Thread":
        h = h.lstrip("#")
        if len(h) != 6:
            raise ValueError(f"invalid colour: {h!r}")
        return Thread((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), name, code, brand)

    def to_dict(self) -> dict:
        return {"hex": self.hex, "name": self.name, "code": self.code, "brand": self.brand}

    @staticmethod
    def from_dict(d: dict) -> "Thread":
        return Thread.from_hex(d["hex"], d.get("name", ""), d.get("code", ""), d.get("brand", ""))


@dataclass
class ColorBlock:
    """Zusammenhängende Stiche einer Farbe (ein Nadelwechsel-Abschnitt)."""
    thread: Thread
    stitches: list[Stitch] = field(default_factory=list)
    object_ids: list[int] = field(default_factory=list)


@dataclass
class StitchPlan:
    blocks: list[ColorBlock] = field(default_factory=list)

    # ---- Statistik ---------------------------------------------------------
    def all_stitches(self):
        """Iteriert über (block_index, stitch)."""
        for bi, b in enumerate(self.blocks):
            for s in b.stitches:
                yield bi, s

    @property
    def stitch_count(self) -> int:
        return sum(1 for b in self.blocks for s in b.stitches if s.cmd == Cmd.STITCH)

    @property
    def trim_count(self) -> int:
        return sum(1 for b in self.blocks for s in b.stitches if s.cmd == Cmd.TRIM)

    @property
    def color_changes(self) -> int:
        return max(0, len(self.blocks) - 1)

    def bounds(self) -> tuple[float, float, float, float]:
        xs, ys = [], []
        for b in self.blocks:
            for s in b.stitches:
                if s.cmd in (Cmd.STITCH, Cmd.JUMP):
                    xs.append(s.x)
                    ys.append(s.y)
        if not xs:
            return (0.0, 0.0, 0.0, 0.0)
        return (min(xs), min(ys), max(xs), max(ys))

    def thread_length_m(self) -> float:
        total = 0.0
        for b in self.blocks:
            prev = None
            for s in b.stitches:
                if s.cmd == Cmd.STITCH and prev is not None:
                    total += math.hypot(s.x - prev[0], s.y - prev[1])
                if s.cmd in (Cmd.STITCH, Cmd.JUMP):
                    prev = (s.x, s.y)
        # Oberfaden + ca. 30 % Einbindung
        return total * 1.3 / 1000.0

    def estimated_minutes(self, spm: int = 800, color_change_s: float = 6.0,
                          trim_s: float = 2.5) -> float:
        return (self.stitch_count / spm
                + (self.color_changes * color_change_s + self.trim_count * trim_s) / 60.0)
