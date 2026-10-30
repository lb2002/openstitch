"""Physik- & Kinematik-Optimierer für die Melco EMT10/4 (Nadelstärke, Fadenspannung, Pantograph-Latenz).

Warum ist das entscheidend?
1. Nadel-Geometrie: Eine typische Sticknadel (75/11 oder 80/12) hat einen Durchmesser von 0.75–0.80 mm.
   Stiche, die kürzer als ~0.45 mm sind, stechen in dasselbe Loch → das Garn franst aus, der Greifer
   verfehlt die Schlinge (Fehlstich) oder der Stoff wird perforiert.
2. Lokale Stichhäufung („Bulletproof Embroidery“): Wenn sich in einer 0.5 × 0.5 mm Zelle mehr als
   5 Einstiche sammeln, steigt die Reibung am Oberfaden massiv → Fadenspannung schiesst hoch →
   Fadenbruch oder Stoffwellen (Puckering).
3. Pantograph-Latenz (X/Y-Trägheit der EMT10/4): Der Rahmen kann nur verfahren, während die Nadel
   oberhalb des Stoffes ist (~40 % des Zyklus). Bei Sprüngen/langen Stichen > 5.5 mm muss die
   Maschine abbremsen. Gleichmässige Stichlängen (1.2–4.2 mm) halten die Maschine im ruhigen,
   schnellen Lauf (750–1000 SPM).
"""
from __future__ import annotations

import math
from collections import defaultdict

from ..core.stitchplan import Cmd, Stitch, StitchPlan


MAX_BRIDGE_MM = 2.5     # so lang darf ein Stich werden, der einen gesättigten Einstich überbrückt


def _is_turn(a: tuple[float, float], s: Stitch, nxt: Stitch) -> bool:
    """Wendepunkt (> 60° Richtungswechsel), z. B. Reihenwechsel im Tatami oder Satin-Kante.

    Solche Einstiche definieren die Kontur – wer sie als „Mikrostich“ entfernt, franst die Kante aus."""
    ux, uy = s.x - a[0], s.y - a[1]
    vx, vy = nxt.x - s.x, nxt.y - s.y
    return ux * vx + uy * vy < 0.5 * math.hypot(ux, uy) * math.hypot(vx, vy)


def optimize_stitches_for_melco(
    stitches: list[Stitch],
    min_stitch_mm: float = 0.45,
    cell_size_mm: float = 0.5,
    max_punctures_per_cell: int = 5,
) -> list[Stitch]:
    """Filtert Mikrostiche (< min_stitch_mm) und verhindert lokale Nadel-Klumpen."""
    if len(stitches) < 3:
        return stitches

    grid: dict[tuple[int, int], int] = defaultdict(int)
    out: list[Stitch] = []
    last_xy: tuple[float, float] | None = None

    for i, s in enumerate(stitches):
        if s.cmd != Cmd.STITCH:
            out.append(s)
            if s.cmd in (Cmd.JUMP, Cmd.TRIM):
                last_xy = (s.x, s.y)
            continue

        # Letzten Stich eines Laufs (vor Trim/Jump/Ende) immer behalten für exakte Kontur
        is_last_of_run = (i + 1 == len(stitches)) or (stitches[i + 1].cmd != Cmd.STITCH)

        if last_xy is not None:
            d = math.hypot(s.x - last_xy[0], s.y - last_xy[1])
            if d < min_stitch_mm and not is_last_of_run and not _is_turn(last_xy, s, stitches[i + 1]):
                continue

        cell = (int(math.floor(s.x / cell_size_mm)), int(math.floor(s.y / cell_size_mm)))
        if grid[cell] >= max_punctures_per_cell and not is_last_of_run:
            # Zelle ist bereits gesättigt → Einstich überspringen, schont Stoff & Faden.
            # Aber nur, wenn der nächste Stich dadurch nicht lang wird: sonst entsteht auf
            # mehrfach abgefahrenen Linien ein Riesenstich quer über das Motiv.
            nxt = stitches[i + 1]
            if last_xy is None or math.hypot(nxt.x - last_xy[0], nxt.y - last_xy[1]) <= MAX_BRIDGE_MM:
                continue

        grid[cell] += 1
        out.append(s)
        last_xy = (s.x, s.y)

    return out


def analyze_kinematics(plan: StitchPlan, max_spm: int = 850) -> dict:
    """Berechnet reale Maschinen-Metriken für die EMT10/4 (effektive SPM, Dichte-Spitzen, Kurzstich-Anteil)."""
    lengths = []
    cell_counts: dict[tuple[int, int], int] = defaultdict(int)
    for b in plan.blocks:
        prev = None
        for s in b.stitches:
            if s.cmd == Cmd.STITCH:
                if prev is not None:
                    lengths.append(math.hypot(s.x - prev[0], s.y - prev[1]))
                prev = (s.x, s.y)
                cell_counts[(int(s.x // 1.0), int(s.y // 1.0))] += 1
            elif s.cmd == Cmd.JUMP:
                prev = (s.x, s.y)

    if not lengths:
        return {"avg_len": 0.0, "eff_spm": max_spm, "max_per_mm2": 0, "real_minutes": 0.0}

    # Pantograph-Abbremsmodell: bis 3.5 mm volle Drehzahl, darüber sinkt SPM wegen Rahmenträgheit
    total_sec = 0.0
    for L in lengths:
        if L <= 3.5:
            spm = max_spm
        elif L <= 7.0:
            spm = max_spm * (1.0 - 0.08 * (L - 3.5))
        else:
            spm = max_spm * 0.58
        total_sec += 60.0 / max(300.0, spm)

    eff_spm = int(round(len(lengths) / (total_sec / 60.0))) if total_sec > 0 else max_spm
    total_sec += plan.color_changes * 6.0 + plan.trim_count * 2.5
    return {
        "avg_len": sum(lengths) / len(lengths),
        "eff_spm": eff_spm,
        "max_per_mm2": max(cell_counts.values(), default=0),
        "real_minutes": total_sec / 60.0,
    }
