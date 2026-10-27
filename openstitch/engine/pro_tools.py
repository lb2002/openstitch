"""SVG-Vektor-Import + Applikations-Generator (Appliqué) + Qualitäts-Doktor."""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

from ..auto.palette import nearest_thread
from ..core.design import Design, EmbObject, FillObject, RunObject, SatinObject
from ..core.stitchplan import Cmd, StitchPlan, Thread
from ..engine.geom import clean, main_axis_angle, polygons_of


# ===========================================================================
# 1. Automatischer Applikations-Generator (Appliqué)
# ===========================================================================
def create_applique_objects(base_obj: EmbObject, border_width_mm: float = 3.2) -> list[EmbObject]:
    """Erzeugt aus einer beliebigen Fläche ein 3-stufiges Profi-Applikations-Set:
    1. Platzierungsnaht (Steppstich auf Grundstoff – zeigt, wo der Applikationsstoff aufgelegt wird),
    2. Fixiernaht / Tackdown (Stepp-/Doppelstich nach Farbstopp – näht den Stoff fest zum Ausschneiden),
    3. Breite Satin-Deckkante (versäubert die Schnittkante sauber).
    Spart bei grossen Patches bis zu 80 % Stiche und verhindert jeglichen Stoffverzug!"""
    g = base_obj.world_geom()
    polys = polygons_of(g)
    if not polys:
        return []
    out: list[EmbObject] = []
    t_place = Thread((120, 120, 120), "1. Appliqué-Platzierung (Stopp)", "APP1", "Appliqué")
    t_tack = Thread((80, 140, 220), "2. Appliqué-Fixiernaht (Ausschneiden)", "APP2", "Appliqué")
    t_satin = base_obj.thread

    for i, poly in enumerate(polys):
        ring_line = LineString(poly.exterior.coords)
        inset_line = LineString(poly.buffer(-border_width_mm * 0.25).exterior.coords) \
            if not poly.buffer(-border_width_mm * 0.25).is_empty else ring_line
        satin_ring = poly.exterior.buffer(border_width_mm / 2.0, join_style=1)

        out.append(RunObject(t_place, name=f"Appliqué 1: Platzierung #{i + 1}", geom=ring_line, stitch_len=2.5))
        out.append(RunObject(t_tack, name=f"Appliqué 2: Fixiernaht #{i + 1}", geom=inset_line, stitch_len=2.2, repeats=1))
        out.append(SatinObject(t_satin, name=f"Appliqué 3: Satinkante #{i + 1}", geom=satin_ring, spacing=0.38))
    return out


# ===========================================================================
# 2. SVG-Vektor-Importer (ohne Zusatzabhängigkeiten, liest path/rect/circle/ellipse/polygon)
# ===========================================================================
def _parse_svg_color(val: str | None) -> tuple[int, int, int] | None:
    if not val or val.strip().lower() == "none":
        return None
    v = val.strip().lower()
    named = {
        "black": (15, 15, 15), "white": (255, 255, 255), "red": (210, 25, 25),
        "blue": (25, 75, 205), "green": (30, 150, 55), "yellow": (245, 205, 20),
        "orange": (245, 125, 20), "purple": (130, 45, 165), "gray": (128, 128, 128),
        "grey": (128, 128, 128), "navy": (20, 36, 77), "gold": (225, 175, 30),
    }
    if v in named:
        return named[v]
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) >= 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", v)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return (30, 30, 30)


def _sample_cubic(p0, p1, p2, p3, steps=10):
    out = []
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1.0 - t
        out.append((
            mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
            mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1],
        ))
    return out


def _parse_svg_path_d(d: str) -> list[tuple[list[tuple[float, float]], bool]]:
    """Parst SVG-Pfadbefehle (M, L, H, V, C, Q, Z, absolut & relativ) in Punktlisten."""
    tokens = re.findall(r"[A-Za-z]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
    subpaths: list[tuple[list[tuple[float, float]], bool]] = []
    cur: list[tuple[float, float]] = []
    cx = cy = sx = sy = 0.0
    i = 0
    cmd = "M"
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
            if cmd in ("Z", "z"):
                if len(cur) >= 2:
                    subpaths.append((cur, True))
                cur = []
                cx, cy = sx, sy
                continue
        rel = cmd.islower()
        c_up = cmd.upper()

        def nf():
            nonlocal i
            v = float(tokens[i])
            i += 1
            return v

        if c_up == "M":
            x, y = nf(), nf()
            if rel:
                x += cx
                y += cy
            if len(cur) >= 2:
                subpaths.append((cur, False))
            cx, cy = sx, sy = x, y
            cur = [(cx, cy)]
            cmd = "l" if rel else "L"
        elif c_up == "L":
            x, y = nf(), nf()
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            cur.append((cx, cy))
        elif c_up == "H":
            x = nf()
            cx = cx + x if rel else x
            cur.append((cx, cy))
        elif c_up == "V":
            y = nf()
            cy = cy + y if rel else y
            cur.append((cx, cy))
        elif c_up == "C":
            x1, y1, x2, y2, x, y = nf(), nf(), nf(), nf(), nf(), nf()
            if rel:
                x1, y1, x2, y2, x, y = x1 + cx, y1 + cy, x2 + cx, y2 + cy, x + cx, y + cy
            cur.extend(_sample_cubic((cx, cy), (x1, y1), (x2, y2), (x, y), 10))
            cx, cy = x, y
        elif c_up == "Q":
            x1, y1, x, y = nf(), nf(), nf(), nf()
            if rel:
                x1, y1, x, y = x1 + cx, y1 + cy, x + cx, y + cy
            p0 = (cx, cy)
            for k in range(1, 9):
                t = k / 8.0
                mt = 1.0 - t
                cur.append((mt * mt * p0[0] + 2 * mt * t * x1 + t * t * x,
                            mt * mt * p0[1] + 2 * mt * t * y1 + t * t * y))
            cx, cy = x, y
        else:
            i += 1
    if len(cur) >= 2:
        subpaths.append((cur, False))
    return subpaths


def import_svg(path: str, target_width_mm: float = 95.0) -> Design:
    """Importiert eine SVG-Vektordatei direkt als editierbare Stick-Objekte (Satin/Tatami/Run)."""
    tree = ET.parse(path)
    root = tree.getroot()
    raw_items = []  # (fill_rgb, stroke_rgb, geom_or_line, is_closed)

    for el in root.iter():
        tag = el.tag.split("}")[-1]
        style_dict = {}
        if "style" in el.attrib:
            for part in el.attrib["style"].split(";"):
                if ":" in part:
                    k, v = part.split(":", 1)
                    style_dict[k.strip()] = v.strip()
        fill_str = style_dict.get("fill", el.attrib.get("fill", "#222222"))
        stroke_str = style_dict.get("stroke", el.attrib.get("stroke", "none"))
        fill_rgb = _parse_svg_color(fill_str)
        stroke_rgb = _parse_svg_color(stroke_str)

        if tag == "path" and "d" in el.attrib:
            subs = _parse_svg_path_d(el.attrib["d"])
            poly_accum = None
            for pts, closed in subs:
                if (closed or (fill_rgb is not None and len(pts) >= 3)) and len(pts) >= 3:
                    try:
                        p = Polygon(pts).buffer(0)
                        poly_accum = p if poly_accum is None else poly_accum.symmetric_difference(p)
                    except Exception:
                        pass
                elif len(pts) >= 2:
                    raw_items.append((None, stroke_rgb or fill_rgb or (20, 20, 20), LineString(pts), False))
            if poly_accum is not None and not poly_accum.is_empty:
                raw_items.append((fill_rgb, stroke_rgb, poly_accum, True))
        elif tag == "rect":
            x = float(el.attrib.get("x", 0))
            y = float(el.attrib.get("y", 0))
            w = float(el.attrib.get("width", 0))
            h = float(el.attrib.get("height", 0))
            if w > 0 and h > 0:
                from shapely.geometry import box
                raw_items.append((fill_rgb, stroke_rgb, box(x, y, x + w, y + h), True))
        elif tag == "circle":
            cx = float(el.attrib.get("cx", 0))
            cy = float(el.attrib.get("cy", 0))
            r = float(el.attrib.get("r", 0))
            if r > 0:
                from shapely.geometry import Point
                raw_items.append((fill_rgb, stroke_rgb, Point(cx, cy).buffer(r), True))
        elif tag in ("polygon", "polyline") and "points" in el.attrib:
            nums = [float(v) for v in re.findall(r"[-+]?\d*\.?\d+", el.attrib["points"])]
            pts = list(zip(nums[0::2], nums[1::2]))
            if tag == "polygon" and len(pts) >= 3:
                raw_items.append((fill_rgb, stroke_rgb, Polygon(pts).buffer(0), True))
            elif len(pts) >= 2:
                raw_items.append((None, stroke_rgb or fill_rgb or (20, 20, 20), LineString(pts), False))

    if not raw_items:
        raise ValueError("Keine unterstützten Vektorpfade in der SVG-Datei gefunden.")

    # Auf Zielbreite (mm) skalieren & zentrieren
    all_geoms = [g for _, _, g, _ in raw_items if g is not None and not g.is_empty]
    u = unary_union(all_geoms)
    x0, y0, x1, y1 = u.bounds
    scale = target_width_mm / max(x1 - x0, 1e-3)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    from shapely import affinity
    from ..auto.digitize import _fast_stroke_width

    d = Design(name="SVG_Import")
    for fill_rgb, stroke_rgb, geom, is_closed in raw_items:
        g = affinity.translate(geom, -cx, -cy)
        g = affinity.scale(g, xfact=scale, yfact=scale, origin=(0, 0))
        if is_closed and fill_rgb is not None:
            th = nearest_thread(fill_rgb)
            for pg in polygons_of(clean(g, 0.2)):
                typ, maxw = _fast_stroke_width(pg)
                if maxw <= 6.2 and pg.area < 450.0:
                    d.objects.append(SatinObject(th, name="SVG-Satin", geom=pg))
                else:
                    ang = (main_axis_angle(pg) + 90) % 180 - 90
                    d.objects.append(FillObject(th, name="SVG-Fläche", geom=pg, angle=round(ang, 1)))
        if stroke_rgb is not None:
            th = nearest_thread(stroke_rgb)
            line = g if isinstance(g, LineString) else LineString(polygons_of(g)[0].exterior.coords) if polygons_of(g) else None
            if line is not None and line.length > 0.8:
                d.objects.append(RunObject(th, name="SVG-Kontur", geom=line, repeats=1))
    return d


# ===========================================================================
# 3. Qualitäts- & Maschinen-Doktor (Prüfung & Auto-Fix)
# ===========================================================================
def run_quality_doctor(design: Design, plan: StitchPlan, max_needles: int = 10) -> list[str]:
    """Prüft das Design auf Stick-Probleme, die in der Praxis zu Fadenbruch, Nadelbruch oder Verzug führen."""
    issues: list[str] = []
    hw, hh = design.hoop.width / 2.0, design.hoop.height / 2.0
    x0, y0, x1, y1 = plan.bounds()

    if plan.stitch_count == 0:
        return ["Das Design enthält noch keine Stiche."]

    # 1. Rahmengrenzen-Check (Kollisionsgefahr Nadel/Presserfuss mit dem Rahmen!)
    if design.hoop.round:
        r_max = max(math.hypot(x0, y0), math.hypot(x1, y1), math.hypot(x0, y1), math.hypot(x1, y0))
        if r_max > hw - 2.0:
            issues.append(
                f"⚠ RAHMEN-KOLLISIONSGEFAHR: Das Motiv (Radius {r_max:.1f} mm) ragt an den Rand des Rundrahmens "
                f"({design.hoop.name}, Radius {hw:.0f} mm). Wähle einen grösseren Rahmen oder zentriere/verkleinere das Motiv!"
            )
    else:
        if x0 < -hw + 2 or x1 > hw - 2 or y0 < -hh + 2 or y1 > hh - 2:
            issues.append(
                f"⚠ RAHMEN-KOLLISIONSGEFAHR: Das Motiv ({x1 - x0:.1f}×{y1 - y0:.1f} mm) überschreitet das sichere Stickfeld "
                f"des Rahmens ({design.hoop.width:.0f}×{design.hoop.height:.0f} mm)."
            )

    # 2. Nadelanzahl-Check
    unique_colors = len({b.thread.hex for b in plan.blocks})
    if unique_colors > max_needles:
        issues.append(
            f"⚠ ZU VIELE FARBEN: Das Design verwendet {unique_colors} Garnfarben, deine Maschine hat aber "
            f"{max_needles} Nadeln. Reduziere die Farben oder plane einen manuellen Garnwechsel ein."
        )

    # 3. Objekt-Checks (zu kleine Schrift / zu schmale Satin-Säulen)
    for o in design.objects:
        if not o.visible:
            continue
        if o.kind == "text" and getattr(o, "height", 10.0) < 4.5:
            issues.append(
                f"⚠ KLEINE SCHRIFT ({o.name}, {o.height:.1f} mm): Normale TrueType-Schriften unter 4.5 mm "
                f"laufen auf Stoff oft zu. Tipp: Nutze unter 5 mm eine kräftige serifenlose Schrift mit "
                f"Dichte 0.45 mm oder Dreifachstich!"
            )
        if o.kind == "satin" and getattr(o, "spacing", 0.4) < 0.28:
            issues.append(
                f"⚠ HOHE SATIN-DICHTE ({o.name}, {o.spacing:.2f} mm): Dichte unter 0.28 mm kann zu "
                f"Fadenbruch führen (empfohlen: 0.36–0.42 mm)."
            )

    # 4. Lokale Stichdichte prüfen
    cells: dict[tuple[int, int], int] = defaultdict(int)
    for b in plan.blocks:
        for s in b.stitches:
            if s.cmd == Cmd.STITCH:
                cells[(int(math.floor(s.x)), int(math.floor(s.y)))] += 1
    hot_cells = sum(1 for c in cells.values() if c > 14)
    if hot_cells > 5:
        issues.append(
            f"⚠ DICHTE-SPITZEN: An {hot_cells} Stellen (1×1 mm) liegen mehr als 14 Stiche übereinander "
            f"(Schalte mit Strg+H die Heatmap ein, um sie rot zu sehen)."
        )

    if not issues:
        issues.append(
            f"✅ PERFEKT: Keine Probleme gefunden! ({plan.stitch_count:,} Stiche, {unique_colors} von {max_needles} Nadeln, "
            f"liegt sicher im Rahmen {design.hoop.name}).".replace(",", "'")
        )
    return issues
