"""Design-Objekte (editierbar, parametrisch) und Aufbau des Stichplans."""
from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, field
from typing import Any

from shapely import affinity, wkt
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

from ..engine.fill import fill_runs, join_covered_runs
from ..engine.geom import Pt, clean, dist, lines_of, main_axis_angle, polygons_of, directional_grow
from ..engine.running import bean_stitch, running_stitch, tie_stitches
from ..engine.satin import UNDERLAY_STYLES, satin_runs
from .stitchplan import Cmd, ColorBlock, Stitch, StitchPlan, Thread

IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def compose(m2, m1):
    """m2 ∘ m1 (zuerst m1)."""
    a1, b1, d1, e1, x1, y1 = m1
    a2, b2, d2, e2, x2, y2 = m2
    return (a2 * a1 + b2 * d1, a2 * b1 + b2 * e1,
            d2 * a1 + e2 * d1, d2 * b1 + e2 * e1,
            a2 * x1 + b2 * y1 + x2, d2 * x1 + e2 * y1 + y2)


def apply_m(m, p: Pt) -> Pt:
    a, b, d, e, x, y = m
    return (a * p[0] + b * p[1] + x, d * p[0] + e * p[1] + y)


def m_scale(f: float) -> float:
    a, b, d, e, _, _ = f
    return math.sqrt(abs(a * e - b * d))


_next_id = [1]


def _new_id() -> int:
    _next_id[0] += 1
    return _next_id[0]


@dataclass
class EmbObject:
    thread: Thread
    name: str = ""
    transform: tuple = IDENTITY
    visible: bool = True
    id: int = field(default_factory=_new_id)
    kind: str = "base"

    # Parameter, die in der Eigenschaftsleiste erscheinen: (attr, Label, Typ, min, max, step)
    PARAMS = ()

    # --- Geometrie ---------------------------------------------------------
    def local_geom(self):
        raise NotImplementedError

    def world_geom(self):
        g = self.local_geom()
        if g is None or g.is_empty:
            return g
        return affinity.affine_transform(g, self.transform)

    def bounds(self):
        g = self.world_geom()
        if g is None or g.is_empty:
            return (0, 0, 0, 0)
        return g.bounds

    # --- Stiche ------------------------------------------------------------
    def runs(self, start: Pt | None = None) -> list[list[Pt]]:
        raise NotImplementedError

    def cache_key(self, start) -> str:
        d = self.to_dict()
        d.pop("name", None)
        d.pop("visible", None)
        s = None if start is None else (round(start[0], 1), round(start[1], 1))
        return json.dumps([d, s], sort_keys=True, default=str)

    # --- Serialisierung ----------------------------------------------------
    def base_dict(self) -> dict:
        return {"kind": self.kind, "thread": self.thread.to_dict(), "name": self.name,
                "transform": list(self.transform), "visible": self.visible}

    def to_dict(self) -> dict:
        d = self.base_dict()
        for attr, *_ in self.PARAMS:
            d[attr] = getattr(self, attr)
        return d

    def clone(self):
        c = copy.deepcopy(self)
        c.id = _new_id()
        return c

    def snapshot(self):
        """Kopie mit gleicher id (für Undo/Redo) – so bleibt der Stich-Cache gültig."""
        return copy.deepcopy(self)


@dataclass
class FillObject(EmbObject):
    geom: Any = None
    angle: float = 45.0
    spacing: float = 0.42
    stitch_len: float = 4.0
    pattern: str = "standard"
    underlay: bool = True
    pull_comp: float = 0.20
    kind: str = "fill"

    PARAMS = (("angle", "Stichwinkel (°)", float, -180, 180, 5),
              ("spacing", "Reihenabstand (mm)", float, 0.25, 1.5, 0.05),
              ("stitch_len", "Stichlänge (mm)", float, 1.5, 7.0, 0.1),
              ("pattern", "Muster", ["standard", "diagonal", "ziegel", "wellen", "kontur"], 0, 0, 0),
              ("underlay", "Unterlage", bool, 0, 0, 0),
              ("pull_comp", "Zugkompensation (mm)", float, 0.0, 1.0, 0.05))

    def local_geom(self):
        return self.geom

    def runs(self, start=None):
        g = self.world_geom()
        if g is None or g.is_empty:
            return []
        # Winkel mit Objekt-Rotation mitdrehen
        a, b, d, e, _, _ = self.transform
        rot = math.degrees(math.atan2(d, a))
        ang = self.angle + rot
        out: list[list[Pt]] = []
        cur = start
        if self.underlay:
            # Rahmen-abhängige Unterlage: Grosse Rahmen ("large"/"jacket") und Kappen ("cap")
            # federn stärker ("Trampolin-Effekt") -> dichtere Gitter-Unterlage schon ab kleinen Flächen!
            hoop_mode = getattr(self, "_hoop_mode", "medium")
            min_ul_area = 2.0 if hoop_mode in ("large", "jacket", "cap") else 4.0
            lat_mult = 5.0 if hoop_mode in ("large", "jacket", "cap") else 7.0
            for poly in polygons_of(g):
                ins = poly.buffer(-0.45, join_style=2)
                for ip in polygons_of(ins):
                    if ip.area < min_ul_area:
                        continue
                    ring = list(ip.exterior.coords)
                    if cur is not None:  # am nächsten Punkt beginnen
                        k = min(range(len(ring) - 1), key=lambda i: dist(ring[i], cur))
                        ring = ring[k:-1] + ring[:k + 1]
                    edge = running_stitch(ring, 3.2)
                    lat = fill_runs(ip.buffer(-0.25), ang + 90, spacing=max(2.2, self.spacing * lat_mult),
                                    stitch_len=4.2, pattern="ziegel", start=edge[-1] if edge else cur)
                    out.append(edge)
                    out.extend(lat)
                    # Bei sehr grossen Rahmen (>200 mm) zweite gekreuzte Stabilisierungsschicht bei grossen Flächen
                    if hoop_mode in ("large", "jacket") and ip.area > 350.0:
                        lat2 = fill_runs(ip.buffer(-0.35), ang + 45, spacing=4.5,
                                         stitch_len=4.8, pattern="ziegel", start=out[-1][-1] if out and out[-1] else cur)
                        out.extend(lat2)
                    if out and out[-1]:
                        cur = out[-1][-1]
        # Rahmen-abhängiger Zuschlag auf die Zugkompensation ("Trampolin-Effekt" in grossen Rahmen / Kappen)
        hoop_pc_boost = getattr(self, "_hoop_pc_boost", 1.0)
        top_geom = directional_grow(g, self.pull_comp * hoop_pc_boost, ang)
        top = fill_runs(top_geom, ang, self.spacing, self.stitch_len, self.pattern, start=cur)
        # Unterlage und Weg zum Deckstich-Einstieg liegen unter dem Deckstich → verbinden statt trimmen
        under = [r for r in out if len(r) >= 2]
        if under and top:
            out = join_covered_runs(under + top[:1], g) + top[1:]
        else:
            out = under + top
        return [r for r in out if len(r) >= 2]


@dataclass
class SatinObject(EmbObject):
    geom: Any = None
    spacing: float = 0.4
    pull_comp: float = 0.15
    max_stitch: float = 7.0
    underlay: bool = True
    puff_3d: bool = False
    underlay_style: str = "auto"
    kind: str = "satin"

    PARAMS = (("spacing", "Dichte (mm)", float, 0.2, 1.2, 0.05),
              ("pull_comp", "Zugkompensation (mm)", float, 0.0, 0.8, 0.05),
              ("max_stitch", "Max. Stich / Split (mm)", float, 4.0, 12.0, 0.5),
              ("underlay", "Unterlage", bool, 0, 0, 0),
              ("underlay_style", "Unterlage-Art", UNDERLAY_STYLES, 0, 0, 0),
              ("puff_3d", "3D-Puff (Cap-Modus)", bool, 0, 0, 0))

    def local_geom(self):
        return self.geom

    def runs(self, start=None):
        g = self.world_geom()
        if g is None or g.is_empty:
            return []
        eff_spacing = min(self.spacing, 0.25) if self.puff_3d else self.spacing
        eff_pc = max(self.pull_comp, 0.32) if self.puff_3d else self.pull_comp
        res = satin_runs(
            g, eff_spacing, eff_pc, self.max_stitch, self.underlay, start, puff_3d=self.puff_3d,
            underlay_style=self.underlay_style,
        )
        out = []
        if not self.puff_3d and res.leftover is not None and not res.leftover.is_empty:
            ang = main_axis_angle(res.leftover) + 90
            out.extend(fill_runs(res.leftover.buffer(0.15), ang, 0.42, 3.0, "standard", start=start))
        n_left = len(out)
        out.extend(res.runs)
        out = [r for r in out if len(r) >= 2]
        if n_left and len(out) > n_left:
            # Wege zwischen Füll-Resten (z. B. Säulen-Enden) und Satinstart werden vom Satin verdeckt
            out = join_covered_runs(out[:n_left + 1], g) + out[n_left + 1:]
        return out


@dataclass
class RunObject(EmbObject):
    geom: Any = None  # LineString / MultiLineString
    stitch_len: float = 2.5
    repeats: int = 0  # 0 = einfach, 1 = Dreifachstich, 2 = Fünffach
    kind: str = "run"

    PARAMS = (("stitch_len", "Stichlänge (mm)", float, 1.0, 6.0, 0.1),
              ("repeats", "Wiederholungen (0=einfach, 1=dreifach)", int, 0, 3, 1))

    def local_geom(self):
        return self.geom

    def runs(self, start=None):
        g = self.world_geom()
        out = []
        lines = lines_of(g)
        if not lines:
            for p in polygons_of(g):
                lines.append(LineString(p.exterior.coords))
        cur = start
        while lines:
            if cur is not None:
                lines.sort(key=lambda l: min(dist(cur, l.coords[0]), dist(cur, l.coords[-1])))
            l = lines.pop(0)
            coords = list(l.coords)
            closed = dist(coords[0], coords[-1]) < 1e-6
            if cur is not None:
                if closed:
                    k = min(range(len(coords) - 1), key=lambda i: dist(coords[i], cur))
                    coords = coords[k:-1] + coords[:k + 1]
                elif dist(cur, coords[-1]) < dist(cur, coords[0]):
                    coords.reverse()
            pts = bean_stitch(coords, self.stitch_len, self.repeats) if self.repeats else \
                running_stitch(coords, self.stitch_len)
            out.append(pts)
            cur = pts[-1]
        return out


@dataclass
class ColumnObject(EmbObject):
    """Manuelle Satinsäule: gezeichnete Mittellinie + Breite.

    Die Stiche stehen exakt senkrecht zur gezeichneten Linie (wie „Column A/B“ in kommerziellen
    Programmen) – kein Rückraten der Mittellinie per Skelett wie beim Flächen-Satin."""
    geom: Any = None  # LineString / MultiLineString (Mittellinie)
    width: float = 3.0
    spacing: float = 0.4
    pull_comp: float = 0.15
    underlay: bool = True
    kind: str = "column"

    PARAMS = (("width", "Säulenbreite (mm)", float, 0.6, 12.0, 0.1),
              ("spacing", "Dichte (mm)", float, 0.2, 1.2, 0.05),
              ("pull_comp", "Zugkompensation (mm)", float, 0.0, 0.8, 0.05),
              ("underlay", "Unterlage", bool, 0, 0, 0))

    def local_geom(self):
        return self.geom

    def bounds(self):
        g = self.world_geom()
        if g is None or g.is_empty:
            return (0, 0, 0, 0)
        return g.buffer(self.width * m_scale(self.transform) / 2.0).bounds

    def runs(self, start=None):
        from ..engine.column import column_runs
        g = self.world_geom()
        w = self.width * m_scale(self.transform)
        out: list[list[Pt]] = []
        cur = start
        lines = lines_of(g)
        while lines:
            if cur is not None:
                lines.sort(key=lambda l: min(dist(cur, l.coords[0]), dist(cur, l.coords[-1])))
            l = lines.pop(0)
            rs = column_runs(list(l.coords), w, spacing=self.spacing, pull_comp=self.pull_comp,
                             underlay="center" if self.underlay else "none", start=cur)
            rs = [r for r in rs if len(r) >= 2]
            if rs:
                out.extend(rs)
                cur = rs[-1][-1]
        return out


@dataclass
class StitchesObject(EmbObject):
    """Importierte Stiche (z. B. aus DST/EXP). Stiche sind fix, können aber transformiert werden."""
    stitch_runs: list = field(default_factory=list)  # list[list[Pt]] lokal
    kind: str = "stitches"

    def local_geom(self):
        lines = [LineString(r) for r in self.stitch_runs if len(r) >= 2]
        return MultiLineString(lines) if lines else MultiLineString()

    def runs(self, start=None):
        return [[apply_m(self.transform, p) for p in r] for r in self.stitch_runs if len(r) >= 2]

    def to_dict(self):
        d = self.base_dict()
        d["stitch_runs"] = [[[round(x, 3), round(y, 3)] for x, y in r] for r in self.stitch_runs]
        return d


# Textobjekt ist in text.py definiert (benötigt Font-Engine), Registrierung dort.
OBJECT_TYPES: dict[str, type] = {"fill": FillObject, "satin": SatinObject, "run": RunObject, "column": ColumnObject,
                                 "stitches": StitchesObject}


def _checked_param(typ, lo, hi, val):
    """Wert aus einer Projektdatei prüfen: Zahlen in den erlaubten Bereich holen, Unsinn ablehnen."""
    if typ is bool:
        return bool(val)
    if typ in (int, float):
        v = float(val)
        if not math.isfinite(v):
            raise ValueError(f"invalid number: {val!r}")
        v = min(max(v, lo), hi) if hi > lo else v
        return typ(v)
    if isinstance(typ, (list, tuple)):
        if val not in typ:
            raise ValueError(f"unknown option: {val!r}")
        return val
    return str(val)


def object_from_dict(d: dict) -> EmbObject:
    cls = OBJECT_TYPES[d["kind"]]
    transform = tuple(float(v) for v in d.get("transform", IDENTITY))
    if len(transform) != 6 or not all(math.isfinite(v) for v in transform):
        raise ValueError("invalid transform")
    kw = {"thread": Thread.from_dict(d["thread"]), "name": str(d.get("name", "")),
          "transform": transform, "visible": bool(d.get("visible", True))}
    if "geom" in d:
        kw["geom"] = wkt.loads(d["geom"]) if d["geom"] else None
    if "stitch_runs" in d:
        kw["stitch_runs"] = [[tuple(p) for p in r] for r in d["stitch_runs"]]
    for attr, _label, typ, lo, hi, _step in getattr(cls, "PARAMS", ()):
        if attr in d:
            kw[attr] = _checked_param(typ, lo, hi, d[attr])
    for extra in getattr(cls, "EXTRA_FIELDS", ()):
        if extra in d:
            kw[extra] = d[extra]
    return cls(**kw)


def _geom_dict(obj: EmbObject, d: dict) -> dict:
    g = getattr(obj, "geom", None)
    if g is not None:
        d["geom"] = g.wkt
    return d


for _cls in (FillObject, SatinObject, RunObject, ColumnObject):
    _orig = _cls.to_dict

    def _to_dict(self, _orig=_orig):
        return _geom_dict(self, _orig(self))
    _cls.to_dict = _to_dict


def color_sorted(objects: list[EmbObject]) -> list[EmbObject]:
    """Farbwechsel minimieren, ohne die Überdeckung zu verändern.

    Ein Objekt darf nur dann nach vorne zu einem früheren Block gleicher Farbe rutschen, wenn es
    keines der übersprungenen Objekte berührt – sonst würde es plötzlich darunter statt darüber
    gestickt (das naive Gruppieren nach Farbe zerstört genau das)."""
    geoms = {}

    def footprint(o):
        if o.id not in geoms:
            g = o.world_geom()
            geoms[o.id] = None if g is None or g.is_empty else g.buffer(0.3)
        return geoms[o.id]

    out: list[EmbObject] = []
    for o in objects:
        pos = len(out)
        # rückwärts nach dem letzten Objekt gleicher Farbe suchen, solange nichts überlappt
        for k in range(len(out) - 1, -1, -1):
            prev = out[k]
            if prev.thread.hex == o.thread.hex:
                pos = k + 1
                break
            fo, fp = footprint(o), footprint(prev)
            if fo is None or fp is None or fo.intersects(fp):
                break
        out.insert(pos, o)
    return out


# ---------------------------------------------------------------------------
# Design
# ---------------------------------------------------------------------------
@dataclass
class Hoop:
    name: str
    width: float          # mm
    height: float         # mm
    round: bool = False
    mode: str = "medium"  # 'small' | 'medium' | 'large' | 'cap' | 'jacket'
    margin_mm: float = 4.0  # Sicherheitsabstand für den Presserfuss zum Rahmenrand

    @property
    def pc_boost(self) -> float:
        """Multiplikator für Zugkompensation je nach Rahmengrösse / Einspannung."""
        return {
            "small": 0.90,   # straff gespannt, wenig Nachgeben
            "medium": 1.00,  # Standard (15 cm)
            "large": 1.20,   # 18–21 cm: stärkerer Trampolin-Effekt in der Mitte
            "jacket": 1.35,  # 30×30 cm Jackenrücken: starker Stoffzug
            "cap": 1.30,     # Kappe: gebogene Front + Mittelnaht
        }.get(self.mode, 1.0)

    @property
    def strategy_description(self) -> str:
        """Beschreibung der Rahmen-Strategie in der aktuellen UI-Sprache."""
        from ..i18n import tr  # spät importieren: vermeidet Import-Zyklen
        if self.mode in ("small", "medium", "large", "jacket", "cap"):
            return tr(f"hoop_strat_{self.mode}")
        return tr("hoop_strat_default")

    @property
    def display_name(self) -> str:
        """Übersetzter Anzeigename. `name` selbst bleibt unverändert (Projektdateien & Abgleich)."""
        key = HOOP_NAME_KEYS.get(self.name)
        if key is None:
            return self.name
        from ..i18n import tr
        return tr(key)


HOOPS = [
    Hoop("Rund 9 cm (Klein/Brust)", 90, 90, True, "small", 3.5),
    Hoop("Rund 12 cm (Brustlogo)", 120, 120, True, "small", 4.0),
    Hoop("Rund 15 cm (Standard)", 150, 150, True, "medium", 4.5),
    Hoop("Rund 18 cm (Gross)", 180, 180, True, "large", 5.0),
    Hoop("Rund 21 cm (XL)", 210, 210, True, "large", 5.0),
    Hoop("Kappe / Cap 13 × 5 cm", 130, 50, False, "cap", 3.5),
    Hoop("Wide-Cap 30 × 7 cm", 300, 70, False, "cap", 4.0),
    Hoop("Rechteck 13 × 18 cm (Haushalt)", 130, 180, False, "medium", 4.0),
    Hoop("Jackenrücken 30 × 30 cm", 300, 300, False, "jacket", 6.0),
    Hoop("Grossfeld 40 × 30 cm (Industrie)", 400, 300, False, "jacket", 6.0),
]

# Übersetzungsschlüssel für die Anzeige der Rahmennamen (Hoop.name ist der gespeicherte Schlüssel)
HOOP_NAME_KEYS: dict[str, str] = {
    "Rund 9 cm (Klein/Brust)": "hoop_round9",
    "Rund 12 cm (Brustlogo)": "hoop_round12",
    "Rund 15 cm (Standard)": "hoop_round15",
    "Rund 18 cm (Gross)": "hoop_round18",
    "Rund 21 cm (XL)": "hoop_round21",
    "Kappe / Cap 13 × 5 cm": "hoop_cap",
    "Wide-Cap 30 × 7 cm": "hoop_widecap",
    "Rechteck 13 × 18 cm (Haushalt)": "hoop_rect13x18",
    "Jackenrücken 30 × 30 cm": "hoop_jacket",
    "Grossfeld 40 × 30 cm (Industrie)": "hoop_field40x30",
}


@dataclass
class Settings:
    min_trim: float = 1.6       # Verbindungen länger als das → Trim
    tie_in: bool = True
    tie_off: bool = True
    max_stitch: float = 12.1    # mm (Maschinengrenze)
    machine_spm: int = 850
    needles: int = 15           # Universal Standard: 15 Nadeln
    machine_name: str = "Universal Standard (DST / PES / EXP · 15 Nadeln)"


@dataclass
class Design:
    objects: list[EmbObject] = field(default_factory=list)
    hoop: Hoop = field(default_factory=lambda: HOOPS[2])
    settings: Settings = field(default_factory=Settings)
    name: str = "Unbenannt"
    _cache: dict = field(default_factory=dict, repr=False)

    def bounds(self):
        bs = [o.bounds() for o in self.objects if o.visible]
        bs = [b for b in bs if b != (0, 0, 0, 0)]
        if not bs:
            return (0, 0, 0, 0)
        return (min(b[0] for b in bs), min(b[1] for b in bs),
                max(b[2] for b in bs), max(b[3] for b in bs))

    def object_runs(self, obj: EmbObject, start) -> list[list[Pt]]:
        # Rahmen-Modus und Zugkompensations-Boost an das Objekt übergeben
        obj._hoop_mode = self.hoop.mode
        obj._hoop_pc_boost = self.hoop.pc_boost
        key = obj.cache_key(start) + f"|{self.hoop.mode}"
        r = self._cache.get((obj.id, key))
        if r is None:
            r = obj.runs(start)
            # Im Kappen-Modus ("cap"): Läufe innerhalb eines Objekts von der Mitte (x=0) nach aussen
            # und von unten (grosse y = nah am Schirm) nach oben sortieren!
            if self.hoop.mode == "cap" and len(r) > 1:
                r = sorted(r, key=lambda run: (abs(run[0][0]) * 0.7 - run[0][1] * 0.3))
            # Cache klein halten
            for k in [k for k in self._cache if k[0] == obj.id]:
                del self._cache[k]
            self._cache[(obj.id, key)] = r
        return r

    def build_plan(self, progress=None) -> StitchPlan:
        plan = StitchPlan()
        cur: Pt | None = None
        block: ColorBlock | None = None
        s = self.settings
        vis = [o for o in self.objects if o.visible]
        # Cache-Einträge gelöschter/ersetzter Objekte verwerfen (sonst wächst er mit jedem Undo)
        live = {o.id for o in self.objects}
        for k in [k for k in self._cache if k[0] not in live]:
            del self._cache[k]
        for i, obj in enumerate(vis):
            if progress:
                progress(i, len(vis))
            runs = self.object_runs(obj, cur)
            if not runs:
                continue
            if block is None or block.thread.hex != obj.thread.hex:
                if block is not None and block.stitches:
                    self._end_block(block, cur)
                block = ColorBlock(obj.thread)
                plan.blocks.append(block)
                cur_in_block = None
            else:
                cur_in_block = cur
            block.object_ids.append(obj.id)
            for run in runs:
                cur_in_block = self._connect(block, cur_in_block, run)
                cur = cur_in_block
        if block is not None and block.stitches:
            self._end_block(block, cur)
        # Kinematik- & Stichdichten-Optimierung (verhindert Mikrostiche & Fadenklumpen)
        from ..engine.density_guard import optimize_stitches_for_melco
        for b in plan.blocks:
            b.stitches = optimize_stitches_for_melco(b.stitches)
        if progress:
            progress(len(vis), len(vis))
        return plan

    def _connect(self, block: ColorBlock, cur: Pt | None, run: list[Pt]) -> Pt:
        s = self.settings
        st = block.stitches
        joined = cur is not None and dist(cur, run[0]) <= s.min_trim
        if cur is None:
            st.append(Stitch(run[0][0], run[0][1], Cmd.JUMP))
            if s.tie_in:
                for p in tie_stitches(run[0], run[1] if len(run) > 1 else None)[1:]:
                    st.append(Stitch(p[0], p[1]))
        else:
            if joined:
                pass  # direkt weitersticken
            else:
                if s.tie_off and len(st) > 2:
                    prev = (st[-2].x, st[-2].y)
                    for p in tie_stitches(cur, prev)[1:]:
                        st.append(Stitch(p[0], p[1]))
                st.append(Stitch(cur[0], cur[1], Cmd.TRIM))
                st.append(Stitch(run[0][0], run[0][1], Cmd.JUMP))
                if s.tie_in:
                    for p in tie_stitches(run[0], run[1] if len(run) > 1 else None)[1:]:
                        st.append(Stitch(p[0], p[1]))
        # Nach Trim + Sprung steht die Nadel auf run[0], nicht mehr auf `cur`
        prev = cur if joined else run[0]
        for p in run[(0 if joined else 1):]:
            # Stiche länger als Maschinengrenze teilen
            dd = dist(prev, p)
            if dd > s.max_stitch:
                n = int(math.ceil(dd / s.max_stitch))
                for k in range(1, n):
                    st.append(Stitch(prev[0] + (p[0] - prev[0]) * k / n, prev[1] + (p[1] - prev[1]) * k / n))
            if dd > 0.05:
                st.append(Stitch(p[0], p[1]))
                prev = p
        return prev

    def _end_block(self, block: ColorBlock, cur):
        st = block.stitches
        if self.settings.tie_off and cur is not None and len(st) > 2:
            prev = (st[-2].x, st[-2].y)
            for p in tie_stitches(cur, prev)[1:]:
                st.append(Stitch(p[0], p[1]))
        if cur is not None:
            st.append(Stitch(cur[0], cur[1], Cmd.TRIM))

    # --- Farben ------------------------------------------------------------
    def threads_in_order(self) -> list[Thread]:
        out = []
        last = None
        for o in self.objects:
            if o.visible and o.thread.hex != last:
                out.append(o.thread)
                last = o.thread.hex
        return out

    def invalidate(self):
        self._cache.clear()
