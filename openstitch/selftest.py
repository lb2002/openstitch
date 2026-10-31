"""Selbsttest für fertig gepackte Programme: `OpenStitch-Studio --selftest`.

Fehlt beim Packen eine Bibliothek oder Sprachdatei, startet das Fenster oft trotzdem, und der Fehler
zeigt sich erst bei der ersten echten Aktion. Der Test führt diese Aktionen einmal durch."""
from __future__ import annotations

import traceback

import numpy as np

REPORT_FILE = "openstitch-selftest.txt"


def _steps():
    from .analysis import simulate_stitchout
    from .analysis.roundtrip import MACHINE_FORMATS, check_format
    from .auto.digitize import AutoParams, auto_digitize
    from .i18n import LANGUAGES, extra_table
    from .render import render_image
    from .samples import SAMPLES

    design = SAMPLES[0][2]()
    plan = design.build_plan()
    assert plan.stitch_count > 100, "no stitches"
    yield "stitch engine"

    assert simulate_stitchout(design, plan, needles=15).pull is not None, "no fabric simulation"
    yield "virtual stitch-out"

    for ext in MACHINE_FORMATS:
        result = check_format(plan, ext)
        assert result.ok, (ext, result.problems)
    yield "machine formats"

    assert render_image(plan, px_per_mm=2.0).width() > 10, "no preview"
    yield "preview"

    img = np.full((120, 120, 4), 255, np.uint8)
    img[30:90, 30:90, :3] = (200, 30, 30)
    assert auto_digitize(img, AutoParams(width_mm=40.0, colors=2)).design.objects, "auto-digitizer found nothing"
    yield "auto-digitizer"

    for code, _label in LANGUAGES:
        assert code in ("de", "en", "fr", "es") or extra_table(code), f"language {code} missing"
    yield "languages"


def run() -> int:
    """0 = alles in Ordnung. Der Bericht landet in einer Datei, weil gepackte Programme keine Konsole haben."""
    lines: list[str] = []
    code = 0
    try:
        for name in _steps():
            lines.append(f"ok    {name}")
    except Exception:  # noqa: BLE001 - genau diese Fehler soll der Test sichtbar machen
        lines.append("FAIL\n" + traceback.format_exc())
        code = 1
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return code
