"""Garnfarben-Paletten und Farbzuordnung (ΔE im Lab-Raum).

Die mitgelieferte Palette ist herstellerneutral. Eigene Hersteller-Tabellen
(Madeira, Isacord, Gunold …) lassen sich als CSV laden: `code;name;#rrggbb`.
"""
from __future__ import annotations

import csv
import math
import os

from ..core.stitchplan import Thread

_GENERIC = [
    ("001", "Weiss", "#ffffff"), ("002", "Naturweiss", "#f4efe1"), ("003", "Creme", "#efe2b8"),
    ("010", "Hellgrau", "#c8c8c8"), ("011", "Silbergrau", "#a3a6a8"), ("012", "Grau", "#7d7f80"),
    ("013", "Dunkelgrau", "#4a4c4e"), ("014", "Anthrazit", "#2e3033"), ("015", "Schwarz", "#111111"),
    ("020", "Zitronengelb", "#fff23a"), ("021", "Gelb", "#ffd500"), ("022", "Sonnengelb", "#ffb800"),
    ("023", "Goldgelb", "#e8a317"), ("024", "Ocker", "#c58b1d"), ("030", "Hellorange", "#ffa94d"),
    ("031", "Orange", "#ff7a00"), ("032", "Dunkelorange", "#e2561b"), ("040", "Lachs", "#ff9a8a"),
    ("041", "Koralle", "#ff6f61"), ("042", "Hellrot", "#ee3a32"), ("043", "Rot", "#d0121b"),
    ("044", "Kirschrot", "#b0101e"), ("045", "Weinrot", "#7c1022"), ("046", "Bordeaux", "#5a0f1e"),
    ("050", "Rosa", "#f9b6c8"), ("051", "Pink", "#f05a9a"), ("052", "Magenta", "#cc1f7a"),
    ("053", "Fuchsia", "#a0136b"), ("060", "Flieder", "#c8a8dc"), ("061", "Lila", "#8e5bb5"),
    ("062", "Violett", "#5e2d8c"), ("063", "Aubergine", "#3d1a4f"), ("070", "Babyblau", "#b4d7f0"),
    ("071", "Himmelblau", "#6fb4e6"), ("072", "Azurblau", "#1f8ad6"), ("073", "Königsblau", "#1846a8"),
    ("074", "Kobaltblau", "#123b8a"), ("075", "Marine", "#14244d"), ("076", "Nachtblau", "#0e1730"),
    ("080", "Türkis", "#27c3c8"), ("081", "Petrol", "#0f7a84"), ("082", "Aqua", "#7fe0d8"),
    ("090", "Mint", "#a7e3b5"), ("091", "Hellgrün", "#7ccf4f"), ("092", "Grasgrün", "#3fa33a"),
    ("093", "Grün", "#1c8a3e"), ("094", "Smaragd", "#0f6e47"), ("095", "Tannengrün", "#16432c"),
    ("096", "Oliv", "#6b7a2a"), ("097", "Khaki", "#a49a64"), ("098", "Limette", "#bfe01f"),
    ("100", "Beige", "#d9c29a"), ("101", "Sand", "#c8a874"), ("102", "Hellbraun", "#a5713d"),
    ("103", "Braun", "#7a4a24"), ("104", "Schokobraun", "#4e2d17"), ("105", "Dunkelbraun", "#33200f"),
    ("110", "Hautton hell", "#f6d3b8"), ("111", "Hautton", "#e6b08a"), ("112", "Hautton dunkel", "#b57a52"),
    ("120", "Gold (Metallic)", "#c9a43b"), ("121", "Silber (Metallic)", "#bfc3c7"),
]


def _srgb_to_lab(c):
    def lin(v):
        v /= 255.0
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92
    r, g, b = (lin(float(x)) for x in c)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(c1, c2) -> float:
    a, b = _srgb_to_lab(c1), _srgb_to_lab(c2)
    return math.dist(a, b)


class Palette:
    def __init__(self, name: str, threads: list[Thread]):
        self.name = name
        self.threads = threads
        self._lab = [_srgb_to_lab(t.color) for t in threads]

    def nearest(self, rgb) -> Thread:
        lab = _srgb_to_lab(rgb)
        i = min(range(len(self.threads)), key=lambda k: math.dist(lab, self._lab[k]))
        t = self.threads[i]
        return Thread(t.color, t.name, t.code, t.brand)

    @staticmethod
    def from_csv(path: str) -> "Palette":
        threads = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            sample = f.read(2048)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
            for row in csv.reader(f, dialect):
                if len(row) < 3 or not row[2].strip().startswith("#"):
                    continue
                threads.append(Thread.from_hex(row[2].strip(), row[1].strip(), row[0].strip(),
                                               os.path.splitext(os.path.basename(path))[0]))
        return Palette(os.path.splitext(os.path.basename(path))[0], threads)


GENERIC = Palette("OpenStitch Standard", [Thread.from_hex(h, n, c, "Standard") for c, n, h in _GENERIC])
_active = [GENERIC]


def set_active_palette(p: Palette):
    _active[0] = p


def active_palette() -> Palette:
    return _active[0]


def nearest_thread(rgb) -> Thread:
    return _active[0].nearest(rgb)
