"""Fasst alle Prüfungen zu einem Bericht mit Punktzahl zusammen."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..core.design import Design
from ..core.fabric import DEFAULT_FABRIC, Fabric, fabric_by_id
from ..core.stitchplan import Cmd, StitchPlan
from .checks import check_density, check_needle_pileup, check_runs, check_stitch_lengths
from .coverage import check_coverage
from .pull import PullResult, simulate_pull
from .stitches import Trace

_PENALTY = {"error": 22.0, "warning": 7.0, "info": 1.0}
_ORDER = {"error": 0, "warning": 1, "info": 2}
SMALL_TEXT_MM = 4.5
PUCKER_MM = 0.7         # so weit zieht sich der Stoff zusammen, bevor man Wellen sieht


@dataclass
class Finding:
    code: str
    severity: str
    count: int = 1
    where: list[tuple[float, float]] = field(default_factory=list)
    data: dict = field(default_factory=dict)


@dataclass
class Report:
    score: int
    findings: list[Finding]
    metrics: dict
    pull: PullResult | None = None

    @property
    def ok(self) -> bool:
        return not any(f.severity == "error" for f in self.findings)


def _finding(d: dict) -> Finding:
    d = dict(d)
    return Finding(d.pop("code"), d.pop("severity"), d.pop("count", 1), d.pop("where", []), d)


def _hoop_findings(design: Design, t: Trace) -> list[dict]:
    m = (t.cmd == Cmd.STITCH) | (t.cmd == Cmd.JUMP)
    if not m.any():
        return []
    hoop = design.hoop
    x, y = t.x[m], t.y[m]
    if hoop.round:
        over = (x * x + y * y) ** 0.5 > hoop.width / 2 - hoop.margin_mm
    else:
        over = (abs(x) > hoop.width / 2 - hoop.margin_mm) | (abs(y) > hoop.height / 2 - hoop.margin_mm)
    if over.any():
        k = int(over.argmax())
        return [{"code": "outside_hoop", "severity": "error", "count": 1, "where": [(float(x[k]), float(y[k]))]}]
    return []


def _small_text_findings(design: Design) -> list[dict]:
    """Umriss-Schriften laufen unter 4.5 mm zu; die Einstrich-Schrift ist genau dafür gemacht."""
    out = []
    for o in design.objects:
        if o.visible and o.kind == "text" and o.height < SMALL_TEXT_MM and not o.is_micro:
            x0, y0, x1, y1 = o.bounds()
            out.append({"code": "small_text", "severity": "warning", "object": o.name or o.text,
                        "mm": float(o.height), "where": [((x0 + x1) / 2, (y0 + y1) / 2)]})
    return out


def simulate_stitchout(design: Design | None, plan: StitchPlan, fabric: Fabric | None = None,
                       needles: int | None = None, physics: bool = True) -> Report:
    """Virtueller Probestick. `design` darf None sein (dann nur stichbasierte Prüfungen).

    Ohne `fabric` gilt der im Design gewählte Stoff."""
    if fabric is None:
        fabric = fabric_by_id(design.fabric) if design is not None else DEFAULT_FABRIC
    t = Trace.of(plan)
    raw: list[dict] = []
    max_stitch = design.settings.max_stitch if design is not None else 12.1
    raw += check_stitch_lengths(t, max_stitch)
    raw += check_runs(t)
    raw += check_needle_pileup(t)
    dens, peak = check_density(t, fabric.max_layers)
    raw += dens
    metrics: dict = {"stitches": plan.stitch_count, "trims": plan.trim_count, "colors": len(plan.blocks),
                     "peak_layers": peak}
    if design is not None:
        raw += _hoop_findings(design, t)
        raw += _small_text_findings(design)
        cov, per_obj = check_coverage(design, t)
        raw += cov
        metrics["coverage"] = per_obj
    if needles is not None:
        unique = len({b.thread.hex for b in plan.blocks})
        if unique > needles:
            raw.append({"code": "too_many_colors", "severity": "info" if needles == 1 else "warning",
                        "count": unique, "needles": needles})
    pull = simulate_pull(t, fabric) if physics else None
    if pull is not None:
        metrics.update(max_shift=pull.max_shift, p95_shift=pull.p95_shift, misregistration=pull.misregistration)
        if pull.gaps:
            raw.append({"code": "registration_gap", "severity": "warning", "count": len(pull.gaps),
                        "mm": pull.misregistration, "where": pull.gaps})
        if pull.p95_shift > PUCKER_MM:
            raw.append({"code": "puckering", "severity": "warning", "count": 1, "mm": pull.p95_shift})
    findings = sorted((_finding(d) for d in raw), key=lambda f: (_ORDER[f.severity], f.code))
    score = 100.0 - sum(_PENALTY[f.severity] * (1 + min(math.log10(max(f.count, 1)), 2) / 4) for f in findings)
    return Report(int(round(max(0.0, score))), findings, metrics, pull)
