"""Virtueller Probestick auf der Kommandozeile.

    python -m openstitch.analysis datei.dst [--fabric jersey] [--needles 1] [--image bericht.png]
    python -m openstitch.analysis --corpus

Beendet sich mit Code 1, wenn ein Fehler gefunden wurde (nützlich in Skripten und CI)."""
from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _load(path: str):
    from ..engine.pro_tools import import_svg
    from ..io.formats import import_file
    from ..io.project import load_project
    ext = os.path.splitext(path)[1].lower()
    if ext == ".ostitch":
        return load_project(path)
    if ext == ".svg":
        return import_svg(path)
    return import_file(path)


def _print_report(name: str, design, fabric, needles, formats: bool) -> bool:
    from ..analysis import simulate_stitchout
    from ..analysis.roundtrip import check_all
    plan = design.build_plan()
    r = simulate_stitchout(design, plan, fabric, needles=needles)
    m = r.metrics
    print(f"{name}: score {r.score}/100, {plan.stitch_count} stitches, {len(plan.blocks)} colors, "
          f"{plan.trim_count} trims, about {plan.estimated_minutes():.0f} min")
    if r.pull is not None:
        print(f"  fabric pull: {m['p95_shift']:.2f} mm typical, {m['max_shift']:.2f} mm max, "
              f"misregistration {m['misregistration']:.2f} mm; peak {m['peak_layers']:.1f} thread layers")
    for f in r.findings:
        where = f" near {f.where[0][0]:.1f}, {f.where[0][1]:.1f} mm" if f.where else ""
        extra = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in f.data.items()}
        print(f"  [{f.severity}] {f.code} x{f.count}{where} {extra if extra else ''}".rstrip())
    ok = r.ok
    if formats:
        for rt in check_all(plan):
            state = "ok" if rt.ok else "FAIL " + "; ".join(rt.problems)
            print(f"  {rt.ext:4} {rt.bytes:8} bytes, max error {rt.max_error_mm:.2f} mm: {state}")
            ok = ok and rt.ok
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m openstitch.analysis", description="Virtual stitch-out for embroidery designs")
    ap.add_argument("file", nargs="?", help="project, embroidery file or SVG")
    ap.add_argument("--fabric", help="woven, denim, twill_cap, pique, jersey, fleece, towel, leather, silk")
    ap.add_argument("--needles", type=int, help="needles on your machine")
    ap.add_argument("--formats", action="store_true", help="also test export to every machine format")
    ap.add_argument("--corpus", action="store_true", help="check the built-in test designs")
    args = ap.parse_args(argv)
    if not args.file and not args.corpus:
        ap.error("give a file or --corpus")

    from PySide6.QtCore import QCoreApplication
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)  # noqa: F841 - Qt braucht eine Instanz
    from ..core.fabric import fabric_by_id
    fabric = fabric_by_id(args.fabric) if args.fabric else None
    ok = True
    if args.corpus:
        from . import corpus
        for name in corpus.designs():
            ok = _print_report(name, corpus.build(name), fabric, args.needles, args.formats) and ok
    else:
        ok = _print_report(os.path.basename(args.file), _load(args.file), fabric, args.needles, args.formats)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
