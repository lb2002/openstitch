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
# 2. SVG-Vektor-Importer (ohne Zusatzabhängigkeiten)
#    path/rect/circle/ellipse/line/polyline/polygon/use, transform=, Stil-Vererbung, Einheiten
# ===========================================================================
# Vollständige CSS-Farbnamen (CSS Color Module Level 4)
_CSS_COLORS = {k: (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)) for k, v in (p.split(":") for p in """
aliceblue:f0f8ff antiquewhite:faebd7 aqua:00ffff aquamarine:7fffd4 azure:f0ffff beige:f5f5dc bisque:ffe4c4
black:000000 blanchedalmond:ffebcd blue:0000ff blueviolet:8a2be2 brown:a52a2a burlywood:deb887 cadetblue:5f9ea0
chartreuse:7fff00 chocolate:d2691e coral:ff7f50 cornflowerblue:6495ed cornsilk:fff8dc crimson:dc143c cyan:00ffff
darkblue:00008b darkcyan:008b8b darkgoldenrod:b8860b darkgray:a9a9a9 darkgreen:006400 darkgrey:a9a9a9
darkkhaki:bdb76b darkmagenta:8b008b darkolivegreen:556b2f darkorange:ff8c00 darkorchid:9932cc darkred:8b0000
darksalmon:e9967a darkseagreen:8fbc8f darkslateblue:483d8b darkslategray:2f4f4f darkslategrey:2f4f4f
darkturquoise:00ced1 darkviolet:9400d3 deeppink:ff1493 deepskyblue:00bfff dimgray:696969 dimgrey:696969
dodgerblue:1e90ff firebrick:b22222 floralwhite:fffaf0 forestgreen:228b22 fuchsia:ff00ff gainsboro:dcdcdc
ghostwhite:f8f8ff gold:ffd700 goldenrod:daa520 gray:808080 green:008000 greenyellow:adff2f grey:808080
honeydew:f0fff0 hotpink:ff69b4 indianred:cd5c5c indigo:4b0082 ivory:fffff0 khaki:f0e68c lavender:e6e6fa
lavenderblush:fff0f5 lawngreen:7cfc00 lemonchiffon:fffacd lightblue:add8e6 lightcoral:f08080 lightcyan:e0ffff
lightgoldenrodyellow:fafad2 lightgray:d3d3d3 lightgreen:90ee90 lightgrey:d3d3d3 lightpink:ffb6c1
lightsalmon:ffa07a lightseagreen:20b2aa lightskyblue:87cefa lightslategray:778899 lightslategrey:778899
lightsteelblue:b0c4de lightyellow:ffffe0 lime:00ff00 limegreen:32cd32 linen:faf0e6 magenta:ff00ff maroon:800000
mediumaquamarine:66cdaa mediumblue:0000cd mediumorchid:ba55d3 mediumpurple:9370db mediumseagreen:3cb371
mediumslateblue:7b68ee mediumspringgreen:00fa9a mediumturquoise:48d1cc mediumvioletred:c71585
midnightblue:191970 mintcream:f5fffa mistyrose:ffe4e1 moccasin:ffe4b5 navajowhite:ffdead navy:000080
oldlace:fdf5e6 olive:808000 olivedrab:6b8e23 orange:ffa500 orangered:ff4500 orchid:da70d6 palegoldenrod:eee8aa
palegreen:98fb98 paleturquoise:afeeee palevioletred:db7093 papayawhip:ffefd5 peachpuff:ffdab9 peru:cd853f
pink:ffc0cb plum:dda0dd powderblue:b0e0e6 purple:800080 rebeccapurple:663399 red:ff0000 rosybrown:bc8f8f
royalblue:4169e1 saddlebrown:8b4513 salmon:fa8072 sandybrown:f4a460 seagreen:2e8b57 seashell:fff5ee
sienna:a0522d silver:c0c0c0 skyblue:87ceeb slateblue:6a5acd slategray:708090 slategrey:708090 snow:fffafa
springgreen:00ff7f steelblue:4682b4 tan:d2b48c teal:008080 thistle:d8bfd8 tomato:ff6347 turquoise:40e0d0
violet:ee82ee wheat:f5deb3 white:ffffff whitesmoke:f5f5f5 yellow:ffff00 yellowgreen:9acd32
""".split())}

_NUM_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_GRADIENT_GREY = (128, 128, 128)  # Verlauf ohne lesbare Stopp-Farbe -> neutrales Grau
_IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)  # SVG-Matrix (a, b, c, d, e, f)


def _parse_svg_color(val: str | None, gradients: dict | None = None,
                     current: tuple[int, int, int] | None = None) -> tuple[int, int, int] | None:
    """Liest eine SVG/CSS-Farbe. None = keine Farbe ("none", "transparent").
    url(#verlauf) -> erste Stopp-Farbe des Verlaufs (sonst Grau), currentColor -> `current`."""
    if val is None:
        return None
    raw = val.replace("!important", "").strip()
    v = raw.lower()
    if not v or v in ("none", "transparent"):
        return None
    if v.startswith("url("):
        m = re.match(r"url\(\s*['\"]?#?([^)'\"]*)['\"]?\s*\)\s*(.*)", raw)
        if m and gradients and m.group(1) in gradients:
            return gradients[m.group(1)]
        if m and m.group(2).strip():  # Fallback-Farbe hinter url(...)
            return _parse_svg_color(m.group(2), None, current)
        return _GRADIENT_GREY
    if v == "currentcolor":
        return current if current is not None else (0, 0, 0)
    if v in _CSS_COLORS:
        return _CSS_COLORS[v]
    if v.startswith("#"):
        h = v[1:]
        if len(h) in (3, 4) and all(c in "0123456789abcdef" for c in h):
            h = "".join(c * 2 for c in h[:3])
        if len(h) in (6, 8) and all(c in "0123456789abcdef" for c in h):
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    m = re.match(r"rgba?\(([^)]*)\)", v)
    if m:
        parts = [p for p in re.split(r"[\s,/]+", m.group(1).strip()) if p][:3]
        if len(parts) == 3:
            try:
                comps = [float(p[:-1]) * 255.0 / 100.0 if p.endswith("%") else float(p) for p in parts]
                return tuple(int(round(max(0.0, min(255.0, c)))) for c in comps)
            except ValueError:
                pass
    m = re.match(r"hsla?\(([^)]*)\)", v)
    if m:
        nums = [float(x) for x in _NUM_RE.findall(m.group(1))[:3]]
        if len(nums) == 3:
            import colorsys
            r, g, b = colorsys.hls_to_rgb((nums[0] % 360) / 360.0, nums[2] / 100.0, nums[1] / 100.0)
            return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))
    return (30, 30, 30)  # unbekannte Angabe -> dunkelgrau statt Abbruch


# --------------------------------------------------------------- Transformationen
def _mat_mul(m, n):
    """Matrixprodukt m·n (SVG-Reihenfolge: n wird zuerst angewendet)."""
    a1, b1, c1, d1, e1, f1 = m
    a2, b2, c2, d2, e2, f2 = n
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def _parse_transform(s: str | None):
    """transform="…" -> Matrix; matrix/translate/scale/rotate(a [cx cy])/skewX/skewY, auch mehrere."""
    m = _IDENT
    for name, args in re.findall(r"([A-Za-z]+)\s*\(([^)]*)\)", s or ""):
        v = [float(x) for x in _NUM_RE.findall(args)]
        name = name.lower()
        if not v:
            continue
        if name == "matrix" and len(v) >= 6:
            t = tuple(v[:6])
        elif name == "translate":
            t = (1.0, 0.0, 0.0, 1.0, v[0], v[1] if len(v) > 1 else 0.0)
        elif name == "scale":
            t = (v[0], 0.0, 0.0, v[1] if len(v) > 1 else v[0], 0.0, 0.0)
        elif name == "rotate":
            a = math.radians(v[0])
            t = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0.0, 0.0)
            if len(v) >= 3:  # um (cx, cy) drehen
                t = _mat_mul(_mat_mul((1.0, 0.0, 0.0, 1.0, v[1], v[2]), t), (1.0, 0.0, 0.0, 1.0, -v[1], -v[2]))
        elif name == "skewx":
            t = (1.0, 0.0, math.tan(math.radians(v[0])), 1.0, 0.0, 0.0)
        elif name == "skewy":
            t = (1.0, math.tan(math.radians(v[0])), 0.0, 1.0, 0.0, 0.0)
        else:
            continue
        m = _mat_mul(m, t)
    return m


def _apply_mat(m, pts):
    a, b, c, d, e, f = m
    return [(a * x + c * y + e, b * x + d * y + f) for x, y in pts]


# --------------------------------------------------------------- Pfad-Parser
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


def _sample_quad(p0, p1, p2, steps=12):
    out = []
    for k in range(1, steps + 1):
        t = k / steps
        mt = 1.0 - t
        out.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                    mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))
    return out


def _sample_arc(x1, y1, rx, ry, phi_deg, large, sweep, x2, y2):
    """Elliptischer Bogen (SVG-Endpunkt-Form) -> Punkte; Umrechnung in Mittelpunkt-Form nach SVG F.6.5/F.6.6."""
    if abs(x1 - x2) < 1e-12 and abs(y1 - y2) < 1e-12:
        return []
    rx, ry = abs(rx), abs(ry)
    if rx < 1e-12 or ry < 1e-12:
        return [(x2, y2)]  # Radius 0 -> gerade Linie
    phi = math.radians(phi_deg % 360.0)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if lam > 1.0:  # Radien zu klein -> hochskalieren
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) if den > 0 else 0.0
    if bool(large) == bool(sweep):
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    ccx = cp * cxp - sp * cyp + (x1 + x2) / 2.0
    ccy = sp * cxp + cp * cyp + (y1 + y2) / 2.0
    ux, uy = (x1p - cxp) / rx, (y1p - cyp) / ry
    vx, vy = (-x1p - cxp) / rx, (-y1p - cyp) / ry
    th1 = math.atan2(uy, ux)
    dth = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi
    n = max(2, int(math.ceil(abs(dth) / (2 * math.pi / 72))))  # 5°-Schritte
    out = []
    for k in range(1, n + 1):
        t = th1 + dth * k / n
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        out.append((cp * ex - sp * ey + ccx, sp * ex + cp * ey + ccy))
    out[-1] = (x2, y2)
    return out


_PATH_ARGC = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def _path_tokens(d: str) -> list[tuple[str, list[float]]]:
    """Zerlegt path-d in (Befehl, Zahlen) inkl. impliziter Wiederholungen, '1.5.5', '-1-2' und
    Bogen-Flags ohne Trenner ('a1 1 0 011 1'). Bei einem Syntaxfehler endet der Pfad dort (wie im Browser)."""
    out: list[tuple[str, list[float]]] = []
    i, n = 0, len(d)
    cmd = None
    while True:
        while i < n and d[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        if d[i].isalpha():
            if d[i].upper() not in _PATH_ARGC:
                break  # unbekannter Befehl -> Rest verwerfen statt Token-Strom zu verschieben
            cmd = d[i]
            i += 1
            if cmd in "Zz":
                out.append((cmd, []))
                continue
        elif cmd is None or cmd in "Zz":
            break
        args: list[float] = []
        for k in range(_PATH_ARGC[cmd.upper()]):
            while i < n and d[i] in " \t\r\n,":
                i += 1
            if cmd in "Aa" and k in (3, 4):  # Flags: genau ein Zeichen 0/1
                if i < n and d[i] in "01":
                    args.append(float(d[i]))
                    i += 1
                    continue
                return out
            m = _NUM_RE.match(d, i)
            if not m:
                return out
            args.append(float(m.group()))
            i = m.end()
        out.append((cmd, args))
        if cmd in "Mm":  # weitere Koordinaten nach M sind implizite L
            cmd = "l" if cmd == "m" else "L"
    return out


def _parse_svg_path_d(d: str) -> list[tuple[list[tuple[float, float]], bool]]:
    """Parst SVG-Pfadbefehle (M L H V C S Q T A Z, absolut & relativ) in Punktlisten (Teilpfade)."""
    subpaths: list[tuple[list[tuple[float, float]], bool]] = []
    cur: list[tuple[float, float]] = []
    cx = cy = sx = sy = 0.0
    ctrl = (0.0, 0.0)  # letzter Kontrollpunkt (für S/T-Spiegelung)
    prev = ""
    for cmd, a in _path_tokens(d):
        up = cmd.upper()
        ox, oy = (cx, cy) if cmd != up else (0.0, 0.0)
        if up == "Z":
            if len(cur) >= 2:
                subpaths.append((cur, True))
            cur = []
            cx, cy = sx, sy
            prev = up
            continue
        if up == "M":
            if len(cur) >= 2:
                subpaths.append((cur, False))
            cx, cy = sx, sy = a[0] + ox, a[1] + oy
            cur = [(cx, cy)]
            prev = up
            continue
        if not cur:  # Zeichenbefehl direkt nach Z: neuer Teilpfad am Startpunkt
            cur = [(cx, cy)]
            sx, sy = cx, cy
        if up == "L":
            x, y = a[0] + ox, a[1] + oy
            cur.append((x, y))
        elif up == "H":
            x, y = a[0] + ox, cy
            cur.append((x, y))
        elif up == "V":
            x, y = cx, a[0] + oy
            cur.append((x, y))
        elif up in ("C", "S"):
            if up == "C":
                p1 = (a[0] + ox, a[1] + oy)
                a = a[2:]
            else:
                p1 = (2 * cx - ctrl[0], 2 * cy - ctrl[1]) if prev in ("C", "S") else (cx, cy)
            ctrl = (a[0] + ox, a[1] + oy)
            x, y = a[2] + ox, a[3] + oy
            cur.extend(_sample_cubic((cx, cy), p1, ctrl, (x, y), 16))
        elif up in ("Q", "T"):
            if up == "Q":
                ctrl = (a[0] + ox, a[1] + oy)
                a = a[2:]
            else:
                ctrl = (2 * cx - ctrl[0], 2 * cy - ctrl[1]) if prev in ("Q", "T") else (cx, cy)
            x, y = a[0] + ox, a[1] + oy
            cur.extend(_sample_quad((cx, cy), ctrl, (x, y)))
        else:  # A
            x, y = a[5] + ox, a[6] + oy
            cur.extend(_sample_arc(cx, cy, a[0], a[1], a[2], a[3], a[4], x, y))
        cx, cy = x, y
        prev = up
    if len(cur) >= 2:
        subpaths.append((cur, False))
    return subpaths


# --------------------------------------------------------------- Formen & Stil
_SVG_SKIP = {"defs", "clipPath", "mask", "symbol", "marker", "pattern", "style", "metadata", "title",
             "desc", "script", "linearGradient", "radialGradient", "filter", "font", "foreignObject"}
_SVG_INHERITED = ("fill", "stroke", "stroke-width", "fill-rule", "visibility", "color", "fill-opacity",
                  "stroke-opacity", "stroke-linejoin", "stroke-linecap")
_UNIT_PX = {"": 1.0, "px": 1.0, "mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96.0, "pt": 96 / 72, "pc": 16.0,
            "em": 16.0, "ex": 8.0}
_XLINK_HREF = "{http://www.w3.org/1999/xlink}href"


def _local(tag) -> str:
    return tag.split("}")[-1] if isinstance(tag, str) else ""


def _svg_len(val, default: float = 0.0) -> float:
    """Längenangabe in SVG-Benutzereinheiten (px@96 dpi); % wird ignoriert."""
    m = re.match(r"\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*([a-z%]*)", str(val or "").lower())
    if not m or m.group(2) not in _UNIT_PX:
        return default
    return float(m.group(1)) * _UNIT_PX[m.group(2)]


def _svg_style(el) -> dict:
    """Präsentationsattribute + style="…" eines Elements (style gewinnt)."""
    st = {k: el.attrib[k].strip() for k in (*_SVG_INHERITED, "display", "opacity") if k in el.attrib}
    for part in el.attrib.get("style", "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            st[k.strip().lower()] = v.replace("!important", "").strip()
    return st


def _shape_subpaths(tag: str, el):
    """Element -> (Teilpfade, füllbar) in lokalen Koordinaten."""
    g = lambda k, dflt=0.0: _svg_len(el.attrib.get(k), dflt)  # noqa: E731
    if tag == "path":
        return _parse_svg_path_d(el.attrib.get("d", "")), True
    if tag == "rect":
        x, y, w, h = g("x"), g("y"), g("width"), g("height")
        if w <= 0 or h <= 0:
            return [], True
        rx, ry = el.attrib.get("rx"), el.attrib.get("ry")
        rx = _svg_len(rx if rx not in (None, "auto") else ry)
        ry = _svg_len(ry if ry not in (None, "auto") else el.attrib.get("rx"))
        rx, ry = min(max(rx, 0.0), w / 2), min(max(ry, 0.0), h / 2)
        if rx <= 0 or ry <= 0:
            return [([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True)], True
        d = (f"M{x + rx},{y} H{x + w - rx} A{rx},{ry} 0 0 1 {x + w},{y + ry} V{y + h - ry} "
             f"A{rx},{ry} 0 0 1 {x + w - rx},{y + h} H{x + rx} A{rx},{ry} 0 0 1 {x},{y + h - ry} "
             f"V{y + ry} A{rx},{ry} 0 0 1 {x + rx},{y} Z")
        return _parse_svg_path_d(d), True
    if tag in ("circle", "ellipse"):
        cx, cy = g("cx"), g("cy")
        rx, ry = (g("r"), g("r")) if tag == "circle" else (g("rx"), g("ry"))
        if tag == "ellipse":  # fehlender Radius = der andere (SVG 2 "auto")
            rx, ry = rx or ry, ry or rx
        if rx <= 0 or ry <= 0:
            return [], True
        pts = [(cx + rx * math.cos(2 * math.pi * k / 72), cy + ry * math.sin(2 * math.pi * k / 72)) for k in range(72)]
        return [(pts, True)], True
    if tag == "line":
        return [([(g("x1"), g("y1")), (g("x2"), g("y2"))], False)], False
    if tag in ("polygon", "polyline"):
        nums = [float(v) for v in _NUM_RE.findall(el.attrib.get("points", ""))]
        pts = list(zip(nums[0::2], nums[1::2]))
        return ([(pts, tag == "polygon")] if len(pts) >= 2 else []), True
    return [], False


def _signed_area(pts) -> float:
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))


def _fill_geometry(rings: list, rule: str):
    """Füllfläche aus Teilpfaden. evenodd: XOR; nonzero: Vereinigung, aber ein vollständig enthaltener
    Teilpfad mit entgegengesetztem Umlaufsinn (Windungszahl 0) wird zum Loch."""
    polys = []
    for pts in rings:
        try:
            p = Polygon(pts)
            p = p if p.is_valid else p.buffer(0)
        except Exception:
            continue
        if not p.is_empty and p.area > 0:
            polys.append((p, 1 if _signed_area(pts) >= 0 else -1))
    if not polys:
        return None
    if rule == "evenodd":
        acc = polys[0][0]
        for p, _ in polys[1:]:
            acc = acc.symmetric_difference(p)
        return acc
    polys.sort(key=lambda t: -t[0].area)  # Eltern vor Kindern
    acc = None
    for i, (p, s) in enumerate(polys):
        w_out = sum(s2 for p2, s2 in polys[:i] if p2.covers(p))
        w_in = w_out + s
        if w_in != 0 and w_out == 0:
            acc = p if acc is None else acc.union(p)
        elif w_in == 0 and w_out != 0 and acc is not None:
            acc = acc.difference(p)
    return acc


def _svg_gradients(root) -> dict:
    """id -> erste Stopp-Farbe von linear-/radialGradient (folgt href auf andere Verläufe)."""
    by_id = {el.get("id"): el for el in root.iter() if _local(el.tag) in ("linearGradient", "radialGradient")
             and el.get("id")}
    out = {}
    for gid, el in by_id.items():
        seen = set()
        while el is not None and id(el) not in seen:
            seen.add(id(el))
            stops = [s for s in el if _local(s.tag) == "stop"]
            if stops:
                st = _svg_style(stops[0])
                st.setdefault("stop-color", stops[0].get("stop-color", "black"))
                col = _parse_svg_color(st["stop-color"])
                if col is not None:
                    out[gid] = col
                break
            ref = (el.get("href") or el.get(_XLINK_HREF) or "").lstrip("#")
            el = by_id.get(ref)
    return out


def _svg_mm_per_unit(root) -> float | None:
    """Physische Grösse einer Benutzereinheit in mm aus width/height (+ viewBox), sonst None."""
    def mm(val):
        m = re.match(r"\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*([a-z]*)\s*$", str(val or "").lower())
        if not m or m.group(2) not in _UNIT_PX or float(m.group(1)) <= 0:
            return None
        return float(m.group(1)) * _UNIT_PX[m.group(2)] * 25.4 / 96.0
    w_mm, h_mm = mm(root.get("width")), mm(root.get("height"))
    vb = [float(v) for v in _NUM_RE.findall(root.get("viewBox", ""))]
    if len(vb) == 4 and vb[2] > 0 and vb[3] > 0:
        if w_mm:
            return w_mm / vb[2]
        if h_mm:
            return h_mm / vb[3]
        return None
    return 25.4 / 96.0 if (w_mm or h_mm) else None


_CAPS = {"butt": 2, "square": 3, "round": 1}
_JOINS = {"miter": 2, "miter-clip": 2, "arcs": 1, "bevel": 3, "round": 1}


def import_svg(path: str, target_width_mm: float | None = 95.0) -> Design:
    """Importiert eine SVG-Vektordatei direkt als editierbare Stick-Objekte (Satin/Tatami/Run).
    target_width_mm=None: echte physische Grösse aus width/height/viewBox (falls angegeben, sonst 95 mm)."""
    tree = ET.parse(path)
    root = tree.getroot()
    ids = {el.get("id"): el for el in root.iter() if isinstance(el.tag, str) and el.get("id")}
    gradients = _svg_gradients(root)
    raw_items = []  # (fill_rgb, fill_geom, stroke_rgb, [LineString], stroke_w, cap, join) in Dokumentreihenfolge

    def emit(subs, fillable, m, style, opacity):
        a, b, c, dd, _, _ = m
        det = a * dd - b * c
        if abs(det) < 1e-12 or not subs:
            return
        tsubs = [(_apply_mat(m, pts), closed) for pts, closed in subs]
        current = _parse_svg_color(style.get("color", "black"))

        def op(key):
            try:
                return float(style.get(key, "1").rstrip("%")) / (100.0 if style.get(key, "").endswith("%") else 1.0)
            except ValueError:
                return 1.0
        fill_rgb = _parse_svg_color(style.get("fill", "black"), gradients, current) if fillable else None
        if opacity * op("fill-opacity") <= 0:
            fill_rgb = None
        stroke_rgb = _parse_svg_color(style.get("stroke", "none"), gradients, current)
        sw = _svg_len(style.get("stroke-width", "1"), 1.0) * math.sqrt(abs(det))
        if opacity * op("stroke-opacity") <= 0 or sw <= 0:
            stroke_rgb = None
        fill_geom = None
        if fill_rgb is not None:
            fill_geom = _fill_geometry([p for p, _ in tsubs if len(p) >= 3],
                                       style.get("fill-rule", "nonzero").strip().lower())
            if fill_geom is None or fill_geom.is_empty:
                fill_rgb, fill_geom = None, None
        lines = []
        if stroke_rgb is not None:
            for pts, closed in tsubs:
                pts = pts + [pts[0]] if closed and pts[0] != pts[-1] else pts
                if len(pts) >= 2 and LineString(pts).length > 0:
                    lines.append(LineString(pts))
        if fill_rgb is None and not lines:
            return
        raw_items.append((fill_rgb, fill_geom, stroke_rgb if lines else None, lines, sw,
                          _CAPS.get(style.get("stroke-linecap", "butt"), 2),
                          _JOINS.get(style.get("stroke-linejoin", "miter"), 2)))

    def walk(el, ctm, inherited, opacity, active, as_group=False):
        tag = _local(el.tag)
        if not tag or (tag in _SVG_SKIP and not as_group) or len(active) > 32:
            return
        st = _svg_style(el)
        if st.get("display", "").lower() == "none":
            return
        style = dict(inherited)
        style.update({k: v for k, v in st.items() if k in _SVG_INHERITED and v != "inherit"})
        try:
            opacity *= float(st.get("opacity", "1"))
        except ValueError:
            pass
        m = _mat_mul(ctm, _parse_transform(el.get("transform")))
        if tag == "use":
            ref = ids.get((el.get("href") or el.get(_XLINK_HREF) or "").strip().lstrip("#"))
            if ref is None or id(ref) in active:
                return
            m = _mat_mul(m, (1.0, 0.0, 0.0, 1.0, _svg_len(el.get("x")), _svg_len(el.get("y"))))
            walk(ref, m, style, opacity, active | {id(ref)}, as_group=_local(ref.tag) == "symbol")
            return
        if el is not root and tag == "svg":  # verschachteltes <svg>: nur x/y-Versatz
            m = _mat_mul(m, (1.0, 0.0, 0.0, 1.0, _svg_len(el.get("x")), _svg_len(el.get("y"))))
        if tag in ("svg", "g", "a", "switch", "symbol"):
            for ch in el:
                walk(ch, m, style, opacity, active)
            return
        if style.get("visibility", "visible").lower() in ("hidden", "collapse") or opacity <= 0:
            return
        subs, fillable = _shape_subpaths(tag, el)
        emit(subs, fillable, m, style, opacity)

    walk(root, _IDENT, {}, 1.0, frozenset())

    if not raw_items:
        raise ValueError("Keine unterstützten Vektorpfade in der SVG-Datei gefunden.")

    # Auf Zielbreite (mm) bzw. physische Grösse skalieren & zentrieren
    bnds = [g.bounds for it in raw_items for g in ([it[1]] if it[1] is not None else []) + it[3]]
    x0, y0 = min(b[0] for b in bnds), min(b[1] for b in bnds)
    x1, y1 = max(b[2] for b in bnds), max(b[3] for b in bnds)
    mpu = _svg_mm_per_unit(root) if target_width_mm is None else None
    scale = mpu if mpu else (target_width_mm or 95.0) / max(x1 - x0, 1e-3)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    from shapely import affinity
    from shapely.geometry import MultiLineString
    from ..auto.digitize import _fast_stroke_width

    def to_mm(geom):
        return affinity.scale(affinity.translate(geom, -cx, -cy), xfact=scale, yfact=scale, origin=(0, 0))

    d = Design(name="SVG_Import")
    for fill_rgb, fill_geom, stroke_rgb, lines, sw, cap, join in raw_items:
        if fill_rgb is not None:  # SVG malt erst die Füllung, dann die Kontur
            th = nearest_thread(fill_rgb)
            for pg in polygons_of(clean(to_mm(fill_geom), 0.2)):
                typ, maxw = _fast_stroke_width(pg)
                if maxw <= 6.2 and pg.area < 450.0:
                    d.objects.append(SatinObject(th, name="SVG-Satin", geom=pg))
                else:
                    ang = (main_axis_angle(pg) + 90) % 180 - 90
                    d.objects.append(FillObject(th, name="SVG-Fläche", geom=pg, angle=round(ang, 1)))
        if stroke_rgb is not None:
            th = nearest_thread(stroke_rgb)
            mm_lines = [to_mm(l) for l in lines]
            w_mm = sw * scale
            if w_mm < 1.2:  # dünne Kontur -> Bohnenstich
                geom = mm_lines[0] if len(mm_lines) == 1 else MultiLineString(mm_lines)
                if geom.length > 0.8:
                    d.objects.append(RunObject(th, name="SVG-Kontur", geom=geom, repeats=1))
            else:  # breite Kontur -> Satinband entlang der Linie
                band = clean(unary_union([l.buffer(w_mm / 2.0, cap_style=cap, join_style=join) for l in mm_lines]), 0.05)
                if not band.is_empty:
                    d.objects.append(SatinObject(th, name="SVG-Kontur (Satin)", geom=band))
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
