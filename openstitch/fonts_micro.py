"""OpenStitch Micro – eingebaute Einstrich-Kleinschrift (2.5 – 12 mm Versalhöhe).

TrueType-Umrisse sind unter ~6 mm zu dünn für Satin, die Buchstaben laufen zu. Wie die
Kleinschriften kommerzieller Programme ist „OpenStitch Micro“ deshalb als *Mittellinien*
digitalisiert: jedes Zeichen besteht aus wenigen Strichen (Polylinien), die als schmale
Satinsäule (``engine.column.column_runs``) oder – ganz klein – als Dreifachstich gestickt
werden.

Datenformat (Einheits-Box): Versalhöhe = 1.0, Grundlinie y = 0, y zeigt nach OBEN,
x-Höhe 0.70, Unterlänge −0.27. Je Zeichen: (Vorschub, [Strich, Strich, …]); ein Strich
ist eine Liste von Punkten in Stickreihenfolge, ein Strich mit nur einem Punkt ist ein
Punkt (i-Punkt, Satzzeichen). Die Reihenfolge der Striche ist so gewählt, dass möglichst
ohne Sprung gestickt werden kann; Lücken innerhalb eines Zeichens werden – wenn möglich –
mit einem Verbindungslauf entlang der Mittellinien überbrückt (bevorzugt unter noch nicht
gestickten Strichen, wie die „Unterlauf“-Verbindungen kommerzieller Schriften).
"""
from __future__ import annotations

import heapq
import math
import unicodedata

from .engine.column import MIN_SATIN_W, _even, bean_run, column_runs
from .engine.geom import Pt, dist

MICRO_SPEC = "builtin:micro"
MICRO_NAME = "OpenStitch Micro"

XH = 0.70     # x-Höhe
DESC = -0.27  # Unterlänge


# ---------------------------------------------------------------------------
# Zeichen-Hilfen (Einheits-Box, y nach oben)
# ---------------------------------------------------------------------------
def _arc(cx, cy, rx, ry, a0, a1, step=10.0):
    """Ellipsenbogen von Winkel a0 nach a1 (Grad, mathematisch positiv = gegen Uhrzeiger)."""
    n = max(2, int(math.ceil(abs(a1 - a0) / step)) + 1)
    out = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / (n - 1))
        out.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return out


def _cat(*parts):
    out = []
    for part in parts:
        for p in part:
            p = (round(p[0], 4), round(p[1], 4))
            if out and abs(out[-1][0] - p[0]) < 1e-4 and abs(out[-1][1] - p[1]) < 1e-4:
                continue
            out.append(p)
    return out


def _mirror_x(strokes, adv):
    return [[(adv - x, y) for x, y in s] for s in strokes]


def _rot180(strokes, adv, cy):
    """180°-Drehung um (adv/2, cy) – z. B. ? → ¿ und ! → ¡."""
    return [[(adv - x, 2 * cy - y) for x, y in s] for s in strokes]


def _shift(strokes, dx=0.0, dy=0.0):
    return [[(x + dx, y + dy) for x, y in s] for s in strokes]


# ---------------------------------------------------------------------------
# Glyphen
# ---------------------------------------------------------------------------
def _build() -> dict[str, tuple[float, list[list[Pt]]]]:
    G: dict[str, tuple[float, list]] = {}

    def g(ch, adv, *strokes):
        G[ch] = (adv, [_cat(s) for s in strokes])

    # --- Versalien -----------------------------------------------------------
    # Querstrich tief: Das obere Dreieck muss bei 2.5 mm offen bleiben
    g("A", 0.80, [(0.05, 0), (0.40, 1), (0.75, 0)], [(0.662, 0.25), (0.138, 0.25)])
    g("B", 0.66, _cat([(0.10, 0), (0.10, 1), (0.33, 1)], _arc(0.33, 0.765, 0.235, 0.235, 90, -90)),
      _cat([(0.10, 0.53), (0.36, 0.53)], _arc(0.36, 0.265, 0.265, 0.265, 90, -90), [(0.10, 0)]))
    g("C", 0.72, _arc(0.40, 0.5, 0.31, 0.5, 45, 315))
    g("D", 0.74, _cat([(0.10, 0), (0.10, 1), (0.30, 1)], _arc(0.30, 0.5, 0.34, 0.5, 90, -90), [(0.10, 0)]))
    g("E", 0.62, [(0.54, 1), (0.10, 1), (0.10, 0.52)], [(0.47, 0.52), (0.10, 0.52), (0.10, 0), (0.54, 0)])
    g("F", 0.58, [(0.52, 1), (0.10, 1), (0.10, 0.52)], [(0.45, 0.52), (0.10, 0.52), (0.10, 0)])
    g("G", 0.76, _cat(_arc(0.41, 0.5, 0.33, 0.5, 45, 360), [(0.46, 0.5)]))
    g("H", 0.74, [(0.10, 0), (0.10, 1)], [(0.10, 0.52), (0.64, 0.52)], [(0.64, 1), (0.64, 0)])
    g("I", 0.26, [(0.13, 1), (0.13, 0)])
    g("J", 0.52, _cat([(0.42, 1), (0.42, 0.28)], _arc(0.25, 0.28, 0.17, 0.28, 0, -165)))
    g("K", 0.68, [(0.10, 0), (0.10, 1)], [(0.60, 1), (0.11, 0.40), (0.62, 0)])
    g("L", 0.56, [(0.10, 1), (0.10, 0), (0.52, 0)])
    g("M", 0.88, [(0.10, 0), (0.10, 1), (0.44, 0.28), (0.78, 1), (0.78, 0)])
    g("N", 0.76, [(0.10, 0), (0.10, 1), (0.66, 0), (0.66, 1)])
    g("O", 0.82, _arc(0.41, 0.5, 0.33, 0.5, 180, 540))
    g("P", 0.64, _cat([(0.10, 0), (0.10, 1), (0.34, 1)], _arc(0.34, 0.75, 0.25, 0.25, 90, -90), [(0.10, 0.5)]))
    g("Q", 0.86, _arc(0.41, 0.5, 0.33, 0.5, 180, 540), [(0.44, 0.30), (0.82, -0.14)])
    g("R", 0.66, _cat([(0.10, 0), (0.10, 1), (0.34, 1)], _arc(0.34, 0.755, 0.245, 0.245, 90, -90),
                      [(0.10, 0.51)]), [(0.32, 0.51), (0.62, 0)])
    g("S", 0.66, _cat(_arc(0.33, 0.75, 0.22, 0.25, 25, 270), _arc(0.33, 0.25, 0.25, 0.25, 90, -155)))
    g("T", 0.66, [(0.33, 0), (0.33, 1)], [(0.05, 1), (0.61, 1)])
    g("U", 0.74, _cat([(0.10, 1), (0.10, 0.32)], _arc(0.37, 0.32, 0.27, 0.32, 180, 360), [(0.64, 1)]))
    g("V", 0.72, [(0.06, 1), (0.36, 0), (0.66, 1)])
    g("W", 1.00, [(0.05, 1), (0.27, 0), (0.50, 0.72), (0.73, 0), (0.95, 1)])
    g("X", 0.70, [(0.06, 0), (0.64, 1)], [(0.06, 1), (0.64, 0)])
    g("Y", 0.70, [(0.06, 1), (0.35, 0.48), (0.64, 1)], [(0.35, 0.48), (0.35, 0)])
    g("Z", 0.66, [(0.08, 1), (0.58, 1), (0.08, 0), (0.60, 0)])

    # --- Gemeine (x-Höhe 0.70) -----------------------------------------------
    bowl_r = _cat([(0.54, 0.56)], _arc(0.31, 0.35, 0.23, 0.35, 40, 320), [(0.54, 0.14)])   # Bauch links vom Stamm
    bowl_l = _cat([(0.10, 0.14)], _arc(0.33, 0.35, 0.23, 0.35, 220, 500), [(0.10, 0.56)])  # Bauch rechts vom Stamm
    # Stamm mit Fuss: unterscheidet das a im Kleinen vom o
    g("a", 0.70, _cat([(0.54, XH), (0.54, 0.10)], _arc(0.64, 0.10, 0.10, 0.10, 180, 300)), bowl_r)
    g("b", 0.64, [(0.10, 1), (0.10, 0)], bowl_l)
    g("c", 0.58, _arc(0.32, 0.35, 0.24, 0.35, 42, 318))
    g("d", 0.64, bowl_r, [(0.54, 1), (0.54, 0)])
    # Querstrich tief: gibt dem Auge des e Platz
    g("e", 0.64, _cat([(0.10, 0.31), (0.56, 0.31)], _arc(0.33, 0.35, 0.23, 0.35, -8, 318)))
    g("f", 0.42, _cat([(0.20, 0), (0.20, 0.78)], _arc(0.34, 0.78, 0.14, 0.20, 180, 40)),
      [(0.04, 0.66), (0.38, 0.66)])
    g("g", 0.64, bowl_r, _cat([(0.54, XH), (0.54, -0.06)], _arc(0.32, -0.06, 0.22, 0.21, 0, -160)))
    g("h", 0.64, [(0.10, 0), (0.10, 1)], _cat([(0.10, 0.47)], _arc(0.31, 0.47, 0.21, 0.23, 180, 0), [(0.52, 0)]))
    g("i", 0.26, [(0.13, XH), (0.13, 0)], [(0.13, 1.0)])
    g("j", 0.32, _cat([(0.20, XH), (0.20, -0.10)], _arc(0.07, -0.10, 0.13, 0.16, 0, -160)), [(0.20, 1.0)])
    g("k", 0.60, [(0.10, 0), (0.10, 1)], [(0.50, XH), (0.11, 0.30), (0.53, 0)])
    # Mit Bogen unten: sonst ist l nicht von I zu unterscheiden
    g("l", 0.32, _cat([(0.13, 1), (0.13, 0.13)], _arc(0.25, 0.13, 0.12, 0.13, 180, 300)))
    g("m", 0.92, _cat([(0.10, 0), (0.10, 0.47)], _arc(0.255, 0.47, 0.155, 0.23, 180, 0)),
      _cat([(0.41, 0), (0.41, 0.47)], _arc(0.565, 0.47, 0.155, 0.23, 180, 0), [(0.72, 0)]))
    g("n", 0.62, _cat([(0.10, 0), (0.10, 0.47)], _arc(0.31, 0.47, 0.21, 0.23, 180, 0), [(0.52, 0)]))
    g("o", 0.64, _arc(0.32, 0.35, 0.23, 0.355, 180, 540))
    g("p", 0.64, [(0.10, DESC), (0.10, XH)], _cat([(0.10, 0.56)], _arc(0.33, 0.35, 0.23, 0.35, 140, -140), [(0.10, 0.14)]))
    g("q", 0.64, bowl_r, [(0.54, XH), (0.54, DESC)])
    g("r", 0.44, _cat([(0.10, 0), (0.10, 0.45)], _arc(0.30, 0.45, 0.20, 0.25, 180, 50)))
    g("s", 0.56, _cat(_arc(0.28, 0.525, 0.18, 0.175, 25, 270), _arc(0.28, 0.175, 0.20, 0.175, 90, -155)))
    g("t", 0.40, [(0.04, 0.68), (0.36, 0.68)], _cat([(0.18, 0.92), (0.18, 0.12)], _arc(0.30, 0.12, 0.12, 0.12, 180, 310)))
    g("u", 0.62, _cat([(0.10, XH), (0.10, 0.23)], _arc(0.31, 0.23, 0.21, 0.23, 180, 360), [(0.52, XH)]))
    g("v", 0.58, [(0.06, XH), (0.29, 0), (0.52, XH)])
    g("w", 0.84, [(0.05, XH), (0.22, 0), (0.42, 0.55), (0.62, 0), (0.79, XH)])
    g("x", 0.58, [(0.07, 0), (0.51, XH)], [(0.07, XH), (0.51, 0)])
    g("y", 0.58, [(0.06, XH), (0.29, 0.05)], [(0.52, XH), (0.18, DESC)])
    g("z", 0.56, [(0.08, XH), (0.48, XH), (0.08, 0), (0.50, 0)])

    # --- Ziffern (Tabellenziffern, Breite 0.62) ------------------------------
    six = _cat(_arc(0.33, 0.31, 0.25, 0.69, 70, 180), _arc(0.31, 0.31, 0.23, 0.31, 180, 540))
    g("0", 0.62, _arc(0.31, 0.5, 0.23, 0.5, 90, 450))
    g("1", 0.62, [(0.12, 0.78), (0.36, 1), (0.36, 0)])
    g("2", 0.62, _cat(_arc(0.31, 0.72, 0.23, 0.26, 155, -35), [(0.08, 0), (0.56, 0)]))
    g("3", 0.62, _cat(_arc(0.30, 0.76, 0.21, 0.24, 150, -90), _arc(0.30, 0.26, 0.25, 0.26, 90, -150)))
    g("4", 0.66, [(0.47, 0), (0.47, 1), (0.03, 0.24), (0.62, 0.24)])
    g("5", 0.62, _cat([(0.53, 1), (0.13, 1), (0.12, 0.56)], _arc(0.31, 0.33, 0.25, 0.33, 135, -150)))
    g("6", 0.62, six)
    g("7", 0.62, [(0.06, 1), (0.56, 1), (0.24, 0)])
    g("8", 0.62, _cat(_arc(0.31, 0.765, 0.19, 0.235, 270, 630), _arc(0.31, 0.265, 0.235, 0.265, 90, -270)))
    g("9", 0.62, *_rot180([six], 0.62, 0.5))

    # --- Satz- und Sonderzeichen ---------------------------------------------
    G[" "] = (0.30, [])
    g(".", 0.24, [(0.12, 0.06)])
    g(",", 0.24, [(0.14, 0.08), (0.08, -0.15)])
    g(":", 0.24, [(0.12, 0.60)], [(0.12, 0.06)])
    g(";", 0.24, [(0.12, 0.60)], [(0.14, 0.08), (0.08, -0.15)])
    g("!", 0.26, [(0.13, 1), (0.13, 0.36)], [(0.13, 0.06)])
    qm = [_cat(_arc(0.28, 0.74, 0.21, 0.24, 155, -70), [(0.28, 0.44), (0.28, 0.36)]), [(0.28, 0.06)]]
    g("?", 0.56, *qm)
    g("-", 0.44, [(0.08, 0.38), (0.36, 0.38)])
    g("_", 0.58, [(0.04, -0.12), (0.54, -0.12)])
    g("'", 0.20, [(0.10, 1), (0.10, 0.72)])
    g('"', 0.36, [(0.10, 1), (0.10, 0.72)], [(0.26, 1), (0.26, 0.72)])
    paren = _arc(0.46, 0.42, 0.30, 0.66, 118, 242)
    g("(", 0.38, paren)
    g(")", 0.38, *_mirror_x([list(reversed(paren))], 0.38))
    g("/", 0.46, [(0.06, -0.05), (0.40, 1.0)])
    g("&", 0.74, _cat([(0.66, 0), (0.24, 0.58)], _arc(0.31, 0.80, 0.14, 0.19, 215, -40),
                      _arc(0.30, 0.24, 0.20, 0.24, 160, 380), [(0.66, 0.44)]))
    g("+", 0.58, [(0.29, 0.14), (0.29, 0.62)], [(0.06, 0.38), (0.52, 0.38)])
    g("@", 1.00, _arc(0.46, 0.40, 0.15, 0.20, 0, 360),
      _cat([(0.61, 0.60), (0.61, 0.28)], _arc(0.71, 0.30, 0.10, 0.10, 180, 360), _arc(0.48, 0.42, 0.38, 0.53, 10, 300)))
    g("#", 0.70, [(0.22, 0), (0.30, 0.92)], [(0.06, 0.62), (0.64, 0.62)], [(0.52, 0.92), (0.44, 0)],
      [(0.62, 0.32), (0.04, 0.32)])
    g("%", 0.80, _arc(0.18, 0.78, 0.12, 0.18, 270, 630), [(0.66, 1.0), (0.14, 0)],
      _arc(0.62, 0.22, 0.12, 0.18, 90, 450))
    g("*", 0.56, [(0.28, 0.94), (0.28, 0.50)], [(0.09, 0.83), (0.47, 0.61)], [(0.09, 0.61), (0.47, 0.83)])
    g("¿", 0.56, *_rot180(qm, 0.56, 0.40))
    g("¡", 0.26, *_rot180([[(0.13, 1), (0.13, 0.36)], [(0.13, 0.06)]], 0.26, 0.46))
    g("ß", 0.66, _cat([(0.10, 0), (0.10, 0.76)], _arc(0.29, 0.76, 0.19, 0.24, 180, -60),
                      _arc(0.33, 0.28, 0.24, 0.28, 80, -125)))
    # punktloses i als Basis für î ï
    g("ı", 0.26, [(0.13, XH), (0.13, 0)])

    # --- Akzente (aus Grundzeichen + Zeichen zusammengesetzt) -----------------
    def acute(cx, y0):
        return [[(cx - 0.05, y0), (cx + 0.08, y0 + 0.15)]]

    def grave(cx, y0):
        return [[(cx - 0.08, y0 + 0.15), (cx + 0.05, y0)]]

    def circ(cx, y0):
        return [[(cx - 0.12, y0), (cx, y0 + 0.14), (cx + 0.12, y0)]]

    def tilde(cx, y0):
        return [[(cx + 0.18 * t / 4, y0 + 0.065 + 0.055 * math.sin(math.pi * t / 4)) for t in range(-4, 5)]]

    def cedilla(cx, y0):
        return [_cat([(cx, 0.0), (cx, -0.07)], _arc(cx, -0.14, 0.07, 0.07, 90, -150))]

    def compose(ch, base, mark, *, cx=None, upper=None, adv=None, dots=False):
        b_adv, b_strokes = G[base]
        if upper is None:
            upper = base.isupper()
        y0 = 1.15 if upper else 0.82
        if cx is None:
            cx = b_adv / 2
        if dots:   # Trema: ein Punkt vor, einer nach dem Grundzeichen → lange, getrimmte Wege
            d, yd = 0.14, (1.28 if upper else 0.99)   # hoch genug für Kleinstgrössen
            strokes = [[(cx - d, yd)]] + b_strokes + [[(cx + d, yd)]]
        else:
            strokes = b_strokes + mark(cx, y0)
            MARKS[ch] = set(range(len(b_strokes), len(strokes)))
        G[ch] = (adv or b_adv, strokes)

    compose("Ä", "A", None, dots=True)
    compose("Ö", "O", None, dots=True)
    compose("Ü", "U", None, dots=True)
    compose("ä", "a", None, dots=True, cx=0.32)
    compose("ö", "o", None, dots=True)
    compose("ü", "u", None, dots=True, cx=0.31)
    compose("É", "E", acute, cx=0.32)
    compose("È", "E", grave, cx=0.32)
    compose("Ê", "E", circ, cx=0.32)
    compose("À", "A", grave)
    compose("Ç", "C", cedilla, cx=0.40)
    compose("Ñ", "N", tilde)
    compose("é", "e", acute, cx=0.32)
    compose("è", "e", grave, cx=0.32)
    compose("ê", "e", circ, cx=0.32)
    compose("à", "a", grave, cx=0.32)
    compose("â", "a", circ, cx=0.32)
    compose("ç", "c", cedilla, cx=0.32)
    compose("ô", "o", circ)
    compose("î", "ı", circ, adv=0.34, cx=0.13)
    compose("ï", "ı", None, dots=True, adv=0.34, cx=0.13)
    compose("ñ", "n", tilde, cx=0.31)
    # î / ï etwas breiter: Grundstrich mittig setzen
    for ch in ("î", "ï"):
        adv, st = G[ch]
        G[ch] = (adv, _shift(st, 0.04))
    # Kleinschrift braucht mehr Luft: Vorbreite/Nachbreite je +SIDE
    return {ch: (adv + 2 * SIDE, _shift(st, SIDE)) for ch, (adv, st) in G.items()}


SIDE = 0.04   # zusätzliche Vor-/Nachbreite (Einheiten der Versalhöhe)


MARKS: dict[str, set[int]] = {}   # Akzent-Striche je Zeichen (werden schmaler gestickt)
GLYPHS: dict[str, tuple[float, list[list[Pt]]]] = _build()


def mark_strokes(ch: str) -> set[int]:
    """Indizes der Akzent-Striche eines Zeichens (Strich-Reihenfolge wie in ``glyph``)."""
    return MARKS.get(ch, set()) if ch in GLYPHS else set()

#: Alle Zeichen, die die Schrift garantiert enthält
CHARSET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:;!?-_'\"()/&+@#%*"
           "ÄÖÜäöüßÉÈÊÀÇéèêàâçôîïñÑ¿¡")


def glyph(ch: str):
    """(Vorschub, Striche) eines Zeichens; unbekannte Akzentbuchstaben fallen auf den
    Grundbuchstaben zurück, sonst auf '?'."""
    if ch in GLYPHS:
        return GLYPHS[ch]
    base = unicodedata.normalize("NFD", ch)[:1]
    if base and base in GLYPHS:
        return GLYPHS[base]
    return GLYPHS["?"]


# ---------------------------------------------------------------------------
# Satz
# ---------------------------------------------------------------------------
BEAN_BELOW_MM = 5.5   # unter dieser Versalhöhe: Dreifachstich statt Satin


def stroke_width(cap_mm: float) -> float:
    """Säulenbreite (mm) für eine Versalhöhe. Unter 5.5 mm wird mit Dreifachstich gestickt
    (Rückgabe < 0.7 mm → ``column_runs`` fällt auf Bean zurück), darüber Satin mit
    0.7 – 2.2 mm (≈ 11 % der Versalhöhe). Nach Augenmass abgestimmt: schmalere Satinsäulen
    sind nicht stickbar, breitere lassen die Innenräume bei 6 mm zulaufen."""
    if cap_mm < BEAN_BELOW_MM:
        return min(0.6, 0.12 * cap_mm)
    return min(2.2, max(0.7, 0.11 * cap_mm))


def pull_comp_for(width: float, pull_comp: float) -> float:
    """Schmale Säulen ziehen kaum ein → Zugkompensation höchstens 8 % der Breite je Seite."""
    return min(pull_comp, 0.08 * width)


def auto_tracking(cap_mm: float) -> float:
    """Zusätzlicher Zeichenabstand (mm), damit kräftige Satinsäulen nicht zusammenlaufen."""
    w = stroke_width(cap_mm)
    vis = 0.45 if w < MIN_SATIN_W else w * 1.16 + 0.35   # sichtbare Strichbreite inkl. Faden
    return max(0.0, 0.6 * (vis - 0.12 * cap_mm))


def run_length(cap_mm: float) -> float:
    """Stichlänge für Dreifachstich/Verbindungsläufe – kurz genug für enge Bögen."""
    return min(1.2, max(0.55, 0.22 * cap_mm))


def layout(text: str, height: float, letter_spacing: float = 0.0, line_spacing: float = 1.25):
    """Liefert [(zeichen, [Striche in mm, Y nach unten], Mittelpunkt-x)] – Zeile zentriert,
    Grundlinie der ersten Zeile bei y = 0 (wie ``text.glyph_shapes``). Zum Zeichenabstand
    kommt die automatische Laufweite für kräftige Säulen (``auto_tracking``)."""
    letter_spacing = letter_spacing + auto_tracking(height)
    out = []
    for li, line in enumerate(text.split("\n")):
        x = 0.0
        y_off = li * height * line_spacing * 1.35
        row = []
        for ch in line:
            adv, strokes = glyph(ch)
            if strokes:
                st = [[(x + px * height, y_off - py * height) for px, py in s] for s in strokes]
                row.append((ch, st, x + adv * height / 2))
            x += adv * height + letter_spacing
        shift = -x / 2
        for ch, st, cx in row:
            out.append((ch, [[(px + shift, py) for px, py in s] for s in st], cx + shift))
    return out


# ---------------------------------------------------------------------------
# Sticken eines Zeichens
# ---------------------------------------------------------------------------
class _Network:
    """Graph aus den Mittellinien eines Zeichens für Verbindungsläufe."""

    def __init__(self, strokes: list[list[Pt]], step: float, tol: float):
        self.nodes: list[Pt] = []
        self.sid: list[int] = []
        self.adj: list[list[tuple[int, float]]] = []
        self.first: dict[int, int] = {}
        for si, s in enumerate(strokes):
            if len(s) < 2:
                continue
            pts = _even(s, step, corner_deg=20.0)
            base = len(self.nodes)
            self.first[si] = base
            for k, p in enumerate(pts):
                self.nodes.append(p)
                self.sid.append(si)
                self.adj.append([])
                if k:
                    i, j = base + k - 1, base + k
                    d = dist(self.nodes[i], self.nodes[j])
                    self.adj[i].append((j, d))
                    self.adj[j].append((i, d))
        n = len(self.nodes)
        for i in range(n):
            for j in range(i + 1, n):
                if self.sid[i] != self.sid[j]:
                    d = dist(self.nodes[i], self.nodes[j])
                    if d <= tol:
                        self.adj[i].append((j, d))
                        self.adj[j].append((i, d))

    def nearest(self, p: Pt, only: int | None = None):
        best, bi = None, -1
        for i, q in enumerate(self.nodes):
            if only is not None and self.sid[i] != only:
                continue
            d = dist(p, q)
            if best is None or d < best:
                best, bi = d, i
        return bi, (best if best is not None else 1e9)

    def path(self, a: int, b: int, done: set[int], over_w: float = 2.5):
        """Dijkstra; Wege über bereits gestickte Striche kosten `over_w`-fach."""
        INF = float("inf")
        cost = [INF] * len(self.nodes)
        prev = [-1] * len(self.nodes)
        cost[a] = 0.0
        pq = [(0.0, a)]
        while pq:
            c, i = heapq.heappop(pq)
            if c > cost[i]:
                continue
            if i == b:
                break
            for j, d in self.adj[i]:
                same = self.sid[i] == self.sid[j]
                w = d * (over_w if (same and self.sid[i] in done) else 1.0)
                if c + w < cost[j]:
                    cost[j] = c + w
                    prev[j] = i
                    heapq.heappush(pq, (c + w, j))
        if cost[b] == INF:
            return None, INF
        seq = [b]
        while seq[-1] != a:
            seq.append(prev[seq[-1]])
        seq.reverse()
        return [self.nodes[i] for i in seq], cost[b]


def _dot_run(p: Pt, width: float, spacing: float, pull_comp: float, upright: bool = False) -> list[Pt]:
    """Punkt (i-Punkt, Trema, Satzzeichen). Klein: Stiche ≥ 0.48 mm (kürzere filtert der
    Dichte-Wächter) – als runder Sternchen-Punkt bzw. als senkrechter Mini-Dreifachstich
    (upright), wenn ein Nachbarpunkt daneben liegt (Trema bleibt so zweigeteilt)."""
    if width < MIN_SATIN_W:
        if upright:
            h = 0.24
            a, b = (p[0], p[1] - h), (p[0], p[1] + h)
            return [a, b, a, b]
        # Sternchen aus drei Durchmessern (alle Stiche ≥ 0.47 mm) → gefüllter, runder Punkt
        r = 0.27
        return [(p[0] + r * math.cos(math.radians(a)), p[1] + r * math.sin(math.radians(a)))
                for a in (90, 270, 150, 330, 30, 210)]
    h = max(0.5, 0.85 * width) / 2
    rs = column_runs([(p[0], p[1] - h), (p[0], p[1] + h)], width, spacing, pull_comp, underlay="none")
    return rs[0] if rs else [p]


def glyph_runs(strokes: list[list[Pt]], width: float, spacing: float = 0.4, pull_comp: float = 0.08,
               run_len: float = 0.8, min_trim: float = 1.6, thin: set[int] | None = None) -> list[list[Pt]]:
    """Stickt die Striche eines Zeichens (Welt-Koordinaten, mm) in Datenreihenfolge.

    Zwischen zwei Strichen wird – falls die Striche über das Zeichen verbunden sind – ein
    Verbindungslauf entlang der Mittellinien genäht (bevorzugt unter noch nicht gestickten
    Strichen, die ihn danach verdecken); sonst beginnt ein neuer Lauf (Sprung/Trim macht
    ``Design``). Striche mit Index in `thin` (Akzente) werden schmaler gestickt – kurze
    Akzente als volle Satinsäule wären nur ein Klumpen."""
    thin = thin or set()
    keep = [i for i, s in enumerate(strokes) if s]
    thin = {k for k, i in enumerate(keep) if i in thin}
    strokes = [strokes[i] for i in keep]
    if not strokes:
        return []
    net = _Network(strokes, step=max(0.25, min(0.6, width * 0.6)), tol=max(0.3, 0.6 * max(width, 0.5)))
    travel_len = max(0.6, min(1.6, run_len * 1.4))
    runs: list[list[Pt]] = []
    run: list[Pt] = []
    done: set[int] = set()
    for si, s in enumerate(strokes):
        if len(s) == 1:
            p = s[0]
            twin = any(len(o) == 1 and o is not s and abs(o[0][1] - p[1]) < 0.3 and abs(o[0][0] - p[0]) < 1.6
                       for o in strokes)
            seq = _dot_run(p, width, spacing, pull_comp, upright=twin)
        else:
            w, rl = (width * 0.75, min(run_len, 0.6)) if si in thin else (width, run_len)
            rs = column_runs(s, w, spacing, pull_comp, underlay="center", run_len=rl)
            seq = [p for r in rs for p in r]
        if not seq:
            continue
        if not run:
            run = list(seq)
        else:
            cur = run[-1]
            gap = dist(cur, seq[0])
            joined = False
            if gap <= 0.35:
                run.extend(seq)
                joined = True
            elif len(s) >= 2 and si in net.first and si > 0 and len(strokes[si - 1]) >= 2:
                a, da = net.nearest(cur)
                b = net.first[si]
                if a >= 0 and da <= max(0.35, 0.75 * width):
                    path, cost = net.path(a, b, done)
                    if path is not None:
                        plen = sum(dist(p, q) for p, q in zip(path, path[1:]))
                        ok = cost <= 1.8 * gap + 0.4 or (gap <= min_trim + 0.2 and plen <= 4 * gap + 1.0)
                        if ok:
                            tr = _even([cur] + path, travel_len)[1:]
                            run.extend(tr)
                            run.extend(seq)
                            joined = True
            if not joined:
                runs.append(run)
                run = list(seq)
        done.add(si)
    if run:
        runs.append(run)
    return [r for r in runs if len(r) >= 2]


def _gap_cost(g: float, min_trim: float) -> float:
    """Kosten einer Verbindung: sichtbarer Verbindungsstich (zwischen ~0.35 mm und der
    Trimm-Schwelle) ist am schlechtesten, ein Trim kostet nur Zeit."""
    if g <= 0.35:
        return 0.0
    if g <= min_trim + 0.15:
        return 5.0 + g
    # Trim: kürzere Sprünge bevorzugen; über ~12 mm teilt Design._connect den Sprung zudem
    # in Stiche auf (Maschinengrenze) → deutlich teurer
    return 2.5 + 0.02 * g + (4.0 if g > 11.5 else 0.0)


def _variants(strokes, thin: set[int]):
    """Alternative Stickreihenfolgen eines Zeichens: Datenreihenfolge, komplett rückwärts,
    und bei Trema (Punkt zuerst und zuletzt) mit vertauschten Punkten.
    Liefert [(Striche, Indizes der schmalen Striche)]."""
    n = len(strokes)
    fwd = list(range(n))
    orders = [(fwd, False), (fwd[::-1], True)]
    if n >= 3 and len(strokes[0]) == 1 and len(strokes[-1]) == 1:
        sw = [n - 1] + fwd[1:-1] + [0]
        orders += [(sw, False), (sw[::-1], True)]
    out = []
    for order, rev in orders:
        st = [list(reversed(strokes[i])) if rev else strokes[i] for i in order]
        out.append((st, {k for k, i in enumerate(order) if i in thin}))
    return out


def text_runs(glyph_strokes: list[list[list[Pt]]], width: float, spacing: float = 0.4,
              pull_comp: float = 0.08, run_len: float = 0.8, min_trim: float = 1.6,
              glyph_thin: list[set[int]] | None = None) -> list[list[Pt]]:
    """Stickt eine ganze Zeichenfolge (je Zeichen die Striche in Welt-Koordinaten).

    Je Zeichen wird die Reihenfolge (vorwärts/rückwärts, Trema-Punkte vertauscht) so
    gewählt, dass möglichst keine kurzen, sichtbaren Verbindungsstiche entstehen – weder
    innerhalb des Zeichens noch zum vorigen/nächsten Zeichen (Ausblick ein Zeichen).
    `glyph_thin`: je Zeichen die Indizes schmal zu stickender Striche (siehe ``mark_strokes``)."""
    out: list[list[Pt]] = []
    thins = glyph_thin or [set()] * len(glyph_strokes)
    pairs = [(st, th) for st, th in zip(glyph_strokes, thins) if any(st)]
    glyphs = [st for st, _ in pairs]
    for gi, (strokes, thin) in enumerate(pairs):
        cur = out[-1][-1] if out else None
        nxt = glyphs[gi + 1] if gi + 1 < len(glyphs) else None
        best = None
        for cand, cthin in _variants(strokes, thin):
            rs = glyph_runs(cand, width, spacing, pull_comp, run_len, min_trim, thin=cthin)
            if not rs:
                continue
            cost = 0.0 if cur is None else _gap_cost(dist(cur, rs[0][0]), min_trim)
            for a, b in zip(rs, rs[1:]):
                cost += _gap_cost(dist(a[-1], b[0]), min_trim)
            if nxt is not None:
                end = rs[-1][-1]
                cost += 0.8 * min(_gap_cost(dist(end, nxt[0][0]), min_trim),
                                  _gap_cost(dist(end, nxt[-1][-1]), min_trim))
            if best is None or cost < best[0] - 1e-9:
                best = (cost, rs)
        if best is None:
            continue
        for r in best[1]:
            if out and dist(out[-1][-1], r[0]) <= 0.35:
                out[-1].extend(r[1:])
            else:
                out.append(r)
    return out
