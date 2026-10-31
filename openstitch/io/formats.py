"""Lesen/Schreiben aller gängigen Stickformate (über pyembroidery) + eigener EXP-Writer."""
from __future__ import annotations

import os
import unicodedata

import pyembroidery as pe

from ..core.design import Design, StitchesObject
from ..core.stitchplan import Cmd, StitchPlan, Thread
from .exp import write_exp

_SPECIAL = str.maketrans({"ß": "ss", "ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "ı": "i", "æ": "ae", "œ": "oe"})

READ_EXT = ["exp", "dst", "pes", "pec", "jef", "vp3", "xxx", "hus", "vip", "sew", "u01", "pcs",
            "dsb", "dsz", "tbf", "shv", "10o", "100", "ksm", "max", "stx", "phb", "phc", "gt", "inb",
            "emd", "bro", "mit", "new", "zhs", "tap", "stc", "zxy", "pmv", "spx", "jpx", "csv", "json"]
WRITE_EXT = ["exp", "dst", "pes", "jef", "vp3", "xxx", "u01", "pec", "tbf", "csv", "svg", "png"]

FORMAT_NAMES = {
    "exp": "Melco / Bernina Expanded (EXP)",
    "dst": "Tajima / Universal Industrie (DST)",
    "pes": "Brother / Baby Lock (PES)",
    "jef": "Janome / Elna (JEF)",
    "vp3": "Pfaff / Husqvarna Viking (VP3)",
    "xxx": "Singer (XXX)",
    "u01": "Barudan (U01)",
    "pec": "Brother (PEC)",
    "tbf": "Tajima (TBF)",
    "csv": "CSV (Stichtabelle / Debug)",
    "svg": "SVG (Vektor-Stichvorschau)",
    "png": "PNG (Bildvorschau)",
}


def _ascii(text: str) -> str:
    """Garnnamen für Stickdateien: nur einfache Zeichen.

    Maschinen zeigen ohnehin keine Umlaute. Vor allem aber schreibt pyembroidery in VP3 die Länge
    in Zeichen statt Bytes: Schon ein „ü“ verschiebt den Rest und die Datei ist unlesbar."""
    text = text.translate(_SPECIAL)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def plan_to_pattern(plan: StitchPlan) -> pe.EmbPattern:
    p = pe.EmbPattern()
    x0, y0, x1, y1 = plan.bounds()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for bi, block in enumerate(plan.blocks):
        t = pe.EmbThread()
        t.set_color(*block.thread.color)
        t.description = _ascii(block.thread.name)
        t.catalog_number = _ascii(block.thread.code)
        t.brand = _ascii(block.thread.brand)
        p.add_thread(t)
        if bi > 0:
            p.add_command(pe.COLOR_CHANGE)
        for s in block.stitches:
            x, y = (s.x - cx) * 10, (s.y - cy) * 10
            if s.cmd == Cmd.STITCH:
                p.add_stitch_absolute(pe.STITCH, x, y)
            elif s.cmd == Cmd.JUMP:
                p.add_stitch_absolute(pe.JUMP, x, y)
            elif s.cmd == Cmd.TRIM:
                p.add_command(pe.TRIM)
    p.add_command(pe.END)
    return p


def export_plan(plan: StitchPlan, path: str, **kw) -> None:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if ext == "exp":
        with open(path, "wb") as f:
            write_exp(plan, f, **kw)
        return
    pat = plan_to_pattern(plan)
    # pyembroidery lässt Trims im JEF-Writer standardmässig weg → Janome würde keinen Faden schneiden.
    # Mit trims=True werden sie als 3 Null-Sprünge geschrieben (Janome-Konvention).
    settings = {"trims": True} if ext == "jef" else None
    pe.write(pat, path, settings)


def import_file(path: str) -> Design:
    """Öffnet eine Stickdatei als Design mit einem Stich-Objekt pro Farbe."""
    pat = pe.read(path)
    if pat is None:
        raise ValueError(f"Datei konnte nicht gelesen werden: {path}")
    d = Design(name=os.path.splitext(os.path.basename(path))[0])
    default_colors = [(30, 30, 30), (200, 30, 30), (30, 90, 200), (30, 160, 60), (240, 190, 20),
                      (140, 40, 160), (250, 120, 20), (90, 200, 220), (240, 240, 240), (120, 70, 30)]
    for i, (stitches, thread) in enumerate(pat.get_as_colorblocks()):
        if thread is not None:
            th = Thread((thread.get_red(), thread.get_green(), thread.get_blue()),
                        thread.description or "", thread.catalog_number or "", thread.brand or "")
        else:
            th = Thread(default_colors[i % len(default_colors)], f"Farbe {i + 1}")
        runs, cur = [], []
        for x, y, cmd in stitches:
            c = cmd & pe.COMMAND_MASK
            if c == pe.STITCH:
                cur.append((x / 10.0, y / 10.0))
            elif c in (pe.JUMP, pe.TRIM, pe.COLOR_CHANGE, pe.STOP, pe.END):
                if len(cur) >= 2:
                    runs.append(cur)
                cur = []
                if c == pe.JUMP:
                    cur = [(x / 10.0, y / 10.0)]
        if len(cur) >= 2:
            runs.append(cur)
        if runs:
            d.objects.append(StitchesObject(th, name=f"{th.name or 'Farbe'} {i + 1}", stitch_runs=runs))
    # Design in Rahmenmitte verschieben
    b = d.bounds()
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    for o in d.objects:
        a, bb, dd, e, x, y = o.transform
        o.transform = (a, bb, dd, e, x - cx, y - cy)
    return d


def verify_exported_file(path: str, expected_plan: StitchPlan | None = None) -> dict:
    """Liest eine exportierte Stickdatei unabhängig wieder ein und simuliert die Maschinen-Kinematik."""
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise ValueError(f"Exportierte Datei ist leer oder existiert nicht: {path}")
    pat = pe.read(path)
    if pat is None or not pat.stitches:
        raise ValueError(f"Stickdatei konnte vom unabhängigen Parser nicht gelesen werden: {path}")

    stitch_cnt = 0
    jump_cnt = 0
    trim_cnt = 0
    color_changes = 0
    max_step_mm = 0.0
    xs: list[float] = []
    ys: list[float] = []
    prev_xy: tuple[float, float] | None = None

    for x, y, cmd in pat.stitches:
        c = cmd & pe.COMMAND_MASK
        xmm, ymm = x / 10.0, y / 10.0
        if c == pe.STITCH:
            stitch_cnt += 1
            xs.append(xmm)
            ys.append(ymm)
            if prev_xy is not None:
                step = ((xmm - prev_xy[0]) ** 2 + (ymm - prev_xy[1]) ** 2) ** 0.5
                if step > max_step_mm:
                    max_step_mm = step
            prev_xy = (xmm, ymm)
        elif c == pe.JUMP:
            jump_cnt += 1
            prev_xy = (xmm, ymm)
        elif c == pe.TRIM:
            trim_cnt += 1
        elif c in (pe.COLOR_CHANGE, pe.STOP):
            color_changes += 1

    if stitch_cnt == 0:
        raise ValueError(f"Exportierte Datei enthält 0 Nähstiche: {path}")

    w_mm = (max(xs) - min(xs)) if xs else 0.0
    h_mm = (max(ys) - min(ys)) if ys else 0.0

    if expected_plan is not None and expected_plan.stitch_count > 0:
        exp_x0, exp_y0, exp_x1, exp_y1 = expected_plan.bounds()
        exp_w = exp_x1 - exp_x0
        exp_h = exp_y1 - exp_y0
        if abs(w_mm - exp_w) > 2.5 or abs(h_mm - exp_h) > 2.5:
            raise ValueError(
                f"Geometrie-Abweichung in {os.path.basename(path)}: "
                f"ist {w_mm:.1f}×{h_mm:.1f} mm, erwartet {exp_w:.1f}×{exp_h:.1f} mm"
            )

    return {
        "file": os.path.basename(path),
        "bytes": os.path.getsize(path),
        "stitches": stitch_cnt,
        "jumps": jump_cnt,
        "trims": trim_cnt,
        "color_changes": color_changes,
        "width_mm": round(w_mm, 2),
        "height_mm": round(h_mm, 2),
        "max_step_mm": round(max_step_mm, 2),
    }
