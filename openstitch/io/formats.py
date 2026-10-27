"""Lesen/Schreiben aller gängigen Stickformate (über pyembroidery) + eigener EXP-Writer."""
from __future__ import annotations

import os

import pyembroidery as pe

from ..core.design import Design, StitchesObject
from ..core.stitchplan import Cmd, StitchPlan, Thread
from .exp import write_exp

READ_EXT = ["exp", "dst", "pes", "pec", "jef", "vp3", "xxx", "hus", "vip", "sew", "u01", "pcs",
            "dsb", "dsz", "tbf", "shv", "10o", "100", "ksm", "max", "stx", "phb", "phc", "gt", "inb",
            "emd", "bro", "mit", "new", "zhs", "tap", "stc", "zxy", "pmv", "spx", "jpx", "csv", "json"]
WRITE_EXT = ["exp", "dst", "pes", "jef", "vp3", "xxx", "u01", "pec", "tbf", "csv", "svg", "png"]

FORMAT_NAMES = {
    "exp": "Melco Expanded (EXP) – empfohlen für EMT10/4",
    "dst": "Tajima (DST)",
    "pes": "Brother (PES)",
    "jef": "Janome (JEF)",
    "vp3": "Pfaff/Husqvarna (VP3)",
    "xxx": "Singer (XXX)",
    "u01": "Barudan (U01)",
    "pec": "Brother (PEC)",
    "tbf": "Tajima (TBF)",
    "csv": "CSV (Text, Debug)",
    "svg": "SVG (Vektorbild)",
    "png": "PNG (Bild)",
}


def plan_to_pattern(plan: StitchPlan) -> pe.EmbPattern:
    p = pe.EmbPattern()
    x0, y0, x1, y1 = plan.bounds()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for bi, block in enumerate(plan.blocks):
        t = pe.EmbThread()
        t.set_color(*block.thread.color)
        t.description = block.thread.name
        t.catalog_number = block.thread.code
        t.brand = block.thread.brand
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
    pe.write(pat, path)


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
