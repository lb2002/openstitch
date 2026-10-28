"""Text & Monogramme aus System-Schriften (TTF/OTF) – inkl. Bogentext.

Die Glyphen-Umrisse werden mit fontTools gelesen, Kurven geglättet und je Buchstabe
automatisch als Satin (schmale Striche) oder Tatami (breite Striche) gestickt.

Zusätzlich gibt es die eingebaute Einstrich-Kleinschrift „OpenStitch Micro“
(Spezifikation ``builtin:micro``, siehe ``fonts_micro``): Mittellinien-Glyphen, die als
schmale Satinsäulen bzw. Dreifachstich gestickt werden. Empfehlung: unter ~6 mm
Versalhöhe liefert sie deutlich lesbarere Schrift als TrueType-Umrisse (die Standard-
Schrift bleibt trotzdem die System-Schrift – die Micro-Schrift wird nur angeboten).
"""
from __future__ import annotations

import glob
import math
import os
import sys
from dataclasses import dataclass, field
from functools import lru_cache

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTCollection, TTFont
from shapely import affinity
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Point, Polygon
from shapely.ops import unary_union

from .core.design import OBJECT_TYPES, EmbObject, FillObject, SatinObject, m_scale
from .core.stitchplan import Thread
from .engine.geom import clean, dist, main_axis_angle, polygons_of
from .fonts_micro import MICRO_NAME, MICRO_SPEC
from .fonts_micro import layout as micro_layout
from .fonts_micro import mark_strokes as micro_mark_strokes
from .fonts_micro import pull_comp_for as micro_pull_comp
from .fonts_micro import text_runs as micro_text_runs
from .fonts_micro import run_length as micro_run_length
from .fonts_micro import stroke_width as micro_stroke_width


def is_builtin_font(spec: str | None) -> bool:
    """Eingebaute Schrift (kein TTF-Pfad), z. B. ``builtin:micro``."""
    return bool(spec) and str(spec).startswith("builtin:")


class _FlattenPen(BasePen):
    def __init__(self, glyphset, steps=10):
        super().__init__(glyphset)
        self.contours: list[list[tuple[float, float]]] = []
        self.cur: list[tuple[float, float]] = []
        self.steps = steps

    def _moveTo(self, pt):
        self.cur = [pt]

    def _lineTo(self, pt):
        self.cur.append(pt)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self.cur.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                             mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self.cur.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                             mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        if len(self.cur) >= 3:
            self.contours.append(self.cur)
        self.cur = []

    _endPath = _closePath


# ---------------------------------------------------------------------------
def font_dirs() -> list[str]:
    if sys.platform.startswith("win"):
        return [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
    if sys.platform == "darwin":
        return ["/System/Library/Fonts", "/System/Library/Fonts/Supplemental", "/Library/Fonts",
                os.path.expanduser("~/Library/Fonts")]
    return ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts")]


@lru_cache(maxsize=1)
def list_fonts() -> dict[str, str]:
    """Anzeigename → Pfad (Index bei TTC: 'pfad#index').

    Die eingebaute Kleinschrift „OpenStitch Micro“ steht immer an erster Stelle
    (Spezifikation ``builtin:micro`` statt Dateipfad)."""
    out: dict[str, str] = {}
    bundled = os.path.join(os.path.dirname(__file__), "fonts")
    for d in [bundled] + font_dirs():
        if not os.path.isdir(d):
            continue
        for path in glob.glob(os.path.join(d, "**", "*.*"), recursive=True):
            ext = path.lower().rsplit(".", 1)[-1]
            try:
                if ext in ("ttf", "otf"):
                    f = TTFont(path, lazy=True, fontNumber=0)
                    out.setdefault(_font_name(f), path)
                elif ext == "ttc":
                    coll = TTCollection(path, lazy=True)
                    for i, f in enumerate(coll.fonts):
                        out.setdefault(_font_name(f), f"{path}#{i}")
            except Exception:
                continue
    out.pop(MICRO_NAME, None)
    return {MICRO_NAME: MICRO_SPEC, **dict(sorted(out.items(), key=lambda kv: kv[0].lower()))}


def _font_name(f: TTFont) -> str:
    name = f["name"]
    fam = name.getDebugName(16) or name.getDebugName(1) or "?"
    sub = name.getDebugName(17) or name.getDebugName(2) or ""
    return f"{fam} {sub}".strip() if sub and sub.lower() not in ("regular", "normal", "standard") else fam


@lru_cache(maxsize=16)
def _load_font(spec: str) -> TTFont:
    if is_builtin_font(spec):
        raise ValueError(f"{spec!r} ist eine eingebaute Schrift, keine TTF/OTF-Datei")
    if "#" in spec:
        p, i = spec.rsplit("#", 1)
        return TTFont(p, fontNumber=int(i))
    return TTFont(spec)


def default_font() -> str:
    # Schneller Direkt-Check für Standard-Systemschriften (0.1 ms statt Scan über 400 Dateien beim Start!)
    quick_candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for cand in quick_candidates:
        if os.path.isfile(cand):
            return cand
    fonts = list_fonts()
    for pref in ("Arial Black", "Arial Bold", "Arial Fett", "Helvetica Bold", "Segoe UI Bold",
                 "Verdana Bold", "Arial", "Helvetica", "DejaVu Sans Bold", "DejaVu Sans"):
        if pref in fonts:
            return fonts[pref]
    # Eingebaute Micro-Schrift nie stillschweigend zum Standard machen
    return next((v for v in fonts.values() if not is_builtin_font(v)), "")


def glyph_shapes(text: str, font_spec: str, height_mm: float, letter_spacing: float = 0.0,
                 line_spacing: float = 1.25):
    """Liefert Liste (zeichen, Polygon-Geometrie, Mittelpunkt-x) in mm; Grundlinie bei y=0."""
    if is_builtin_font(font_spec):
        # Micro-Schrift: Striche mit typischer Säulenbreite als Flächen
        hw = max(micro_stroke_width(height_mm), 0.4) / 2
        return [(ch, unary_union([_stroke_geom(s).buffer(hw) for s in st]), cx)
                for ch, st, cx in micro_layout(text, height_mm, letter_spacing, line_spacing)]
    font = _load_font(font_spec)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap() or {}
    upm = font["head"].unitsPerEm
    # Versalhöhe als Referenz für "height_mm"
    cap = None
    if "OS/2" in font and getattr(font["OS/2"], "sCapHeight", 0):
        cap = font["OS/2"].sCapHeight
    cap = cap or upm * 0.7
    s = height_mm / cap
    hmtx = font["hmtx"]
    kern = {}
    if "kern" in font:
        try:
            for t in font["kern"].kernTables:
                kern.update(t.kernTable)
        except Exception:
            pass
    out = []
    lines = text.split("\n")
    for li, line in enumerate(lines):
        x = 0.0
        y_off = li * height_mm * line_spacing / 0.7 * 0.7 * 1.0 + li * height_mm * (line_spacing - 1) * 0
        y_off = li * cap * s * line_spacing * 1.35
        prev = None
        row = []
        for ch in line:
            gname = cmap.get(ord(ch))
            if gname is None:
                gname = ".notdef"
            if prev is not None and (prev, gname) in kern:
                x += kern[(prev, gname)] * s
            adv = hmtx[gname][0] * s if gname in hmtx.metrics else upm * 0.5 * s
            if ch.strip():
                pen = _FlattenPen(gs, steps=8)
                gs[gname].draw(pen)
                geom = None
                for c in pen.contours:
                    pts = [(x + px * s, y_off - py * s) for px, py in c]
                    try:
                        poly = Polygon(pts).buffer(0)
                    except Exception:
                        continue
                    geom = poly if geom is None else geom.symmetric_difference(poly)
                if geom is not None and not geom.is_empty:
                    row.append((ch, clean(geom, 0.01), x + adv / 2))
            x += adv + letter_spacing
            prev = gname
        # Zeile zentrieren
        shift = -x / 2
        out.extend((ch, affinity.translate(g, shift, 0), cx + shift) for ch, g, cx in row)
    return out


def _stroke_geom(stroke):
    return Point(stroke[0]) if len(stroke) == 1 else LineString(stroke)


def micro_glyph_geoms(text: str, height_mm: float, letter_spacing: float = 0.0):
    """Micro-Schrift: Liste (zeichen, GeometryCollection der Striche in Stickreihenfolge, cx)."""
    return [(ch, GeometryCollection([_stroke_geom(s) for s in st]), cx)
            for ch, st, cx in micro_layout(text, height_mm, letter_spacing)]


def arc_layout(glyphs, radius: float):
    """Buchstaben entlang eines Bogens anordnen. radius>0: Bogen oben, <0: unten."""
    if not radius:
        return glyphs
    out = []
    r = abs(radius)
    for ch, g, cx in glyphs:
        ang = cx / r  # rad
        if radius > 0:
            # Grundlinie liegt auf Kreis mit Mittelpunkt (0, r)
            g2 = affinity.translate(g, -cx, 0)
            g2 = affinity.rotate(g2, math.degrees(ang), origin=(0, 0))
            px, py = r * math.sin(ang), r - r * math.cos(ang)
        else:
            g2 = affinity.translate(g, -cx, 0)
            g2 = affinity.rotate(g2, -math.degrees(ang), origin=(0, 0))
            px, py = r * math.sin(ang), -(r - r * math.cos(ang))
        out.append((ch, affinity.translate(g2, px, py), cx))
    return out


@dataclass
class TextObject(EmbObject):
    text: str = "Text"
    font: str = ""
    height: float = 10.0           # Versalhöhe mm
    letter_spacing: float = 0.5
    arc_radius: float = 0.0
    mode: str = "auto"             # auto | satin | fill
    density: float = 0.4
    pull_comp: float = 0.18
    kind: str = "text"

    PARAMS = (("text", "Text", str, 0, 0, 0),
              ("font", "Schrift", "font", 0, 0, 0),
              ("height", "Buchstabenhöhe (mm)", float, 2.0, 200.0, 0.5),
              ("letter_spacing", "Zeichenabstand (mm)", float, -5.0, 20.0, 0.1),
              ("arc_radius", "Bogenradius (mm, 0 = gerade)", float, -500.0, 500.0, 5.0),
              ("mode", "Stichart", ["auto", "satin", "fill"], 0, 0, 0),
              ("density", "Dichte (mm)", float, 0.25, 1.0, 0.05),
              ("pull_comp", "Zugkompensation (mm)", float, 0.0, 0.8, 0.05))

    def __post_init__(self):
        if not self.font:
            self.font = default_font()

    @property
    def is_micro(self) -> bool:
        return is_builtin_font(self.font)

    def _glyphs(self):
        key = (self.text, self.font, self.height, self.letter_spacing, self.arc_radius)
        if getattr(self, "_gkey", None) != key:
            if self.is_micro:
                g = micro_glyph_geoms(self.text, self.height, self.letter_spacing)
            else:
                g = glyph_shapes(self.text, self.font, self.height, self.letter_spacing) if self.font else []
            self._gcache = arc_layout(g, self.arc_radius)
            self._gkey = key
        return self._gcache

    def local_geom(self):
        if self.is_micro:
            # Striche mit Säulenbreite gepuffert → Auswahlrahmen & Trefferprüfung
            hw = max(micro_stroke_width(self.height), 0.4) / 2
            gs = [g.buffer(hw) for _, g, _ in self._glyphs() if not g.is_empty]
            return unary_union(gs) if gs else MultiPolygon()
        gs = [g for _, g, _ in self._glyphs()]
        return unary_union(gs) if gs else MultiPolygon()

    def _micro_runs(self, start=None):
        """Micro-Schrift: Mittellinien je Zeichen als schmale Satinsäulen / Dreifachstich."""
        cap = self.height * m_scale(self.transform)        # wirksame Versalhöhe in mm
        w = micro_stroke_width(cap)
        pc = micro_pull_comp(w, self.pull_comp)   # schmale Säulen: wenig Zugkompensation
        glyph_strokes, thin = [], []
        for ch, g, _ in self._glyphs():
            wg = affinity.affine_transform(g, self.transform)
            glyph_strokes.append([[tuple(c) for c in p.coords] for p in wg.geoms])
            thin.append(micro_mark_strokes(ch))
        return micro_text_runs(glyph_strokes, w, spacing=self.density, pull_comp=pc,
                               run_len=micro_run_length(cap), glyph_thin=thin)

    def runs(self, start=None):
        if self.is_micro:
            return self._micro_runs(start)
        out = []
        cur = start
        for ch, g, _ in self._glyphs():
            wg = affinity.affine_transform(g, self.transform)
            for part in polygons_of(wg):
                stroke = 2 * part.area / max(part.length, 1e-6) * 2  # ≈ mittlere Strichbreite
                use_satin = self.mode == "satin" or (self.mode == "auto" and stroke <= 7.0)
                if use_satin:
                    o = SatinObject(self.thread, geom=part, spacing=self.density, pull_comp=self.pull_comp)
                else:
                    ang = 45.0
                    o = FillObject(self.thread, geom=part, angle=ang, spacing=self.density,
                                   pull_comp=self.pull_comp)
                rs = o.runs(cur)
                if rs:
                    out.extend(rs)
                    cur = rs[-1][-1]
        return out

    def to_dict(self):
        d = self.base_dict()
        for attr, *_ in self.PARAMS:
            d[attr] = getattr(self, attr)
        return d

    def __getstate__(self):
        st = self.__dict__.copy()
        st.pop("_gcache", None)
        st.pop("_gkey", None)
        return st


OBJECT_TYPES["text"] = TextObject
