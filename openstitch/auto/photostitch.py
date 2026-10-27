"""PhotoStitch-Engine: Porträt- & Landschaftsfotos in Halbton-Wellen-/Gravur-Stickerei umwandeln.

Wie funktioniert echtes PhotoStitch?
- Statt Farbflächen zu segmentieren, wird das Foto in leicht gewellte Scanlinien im Abstand
  `row_spacing_mm` (z. B. 1.3–1.8 mm) abgetastet.
- Entlang jeder Linie steuert die lokale Dunkelheit des Pixels die Zickzack-Amplitude:
  - Ganz helle Stellen (< Schwellwert): keine Stiche oder flacher Steppstich.
  - Mittlere & dunkle Töne: Zickzack-Ausschlag proportional zur Dunkelheit (0.4 mm bis row_spacing_mm * 0.95).
- Im 4-Farb-Modus (CMYK-Halbton: Cyan, Magenta, Gelb, Schwarz) erhält jede Farbschicht ihren
  eigenen klassischen Rasterwinkel (15°, 75°, 0°, 45°), damit kein Moiré entsteht und ein
  farbiges Stick-Gemälde auf hellem Stoff entsteht!
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import cv2
import numpy as np

from ..core.design import Design, StitchesObject
from ..core.stitchplan import Thread
from .digitize import load_image


@dataclass
class PhotoStitchParams:
    width_mm: float = 110.0
    row_spacing_mm: float = 1.5     # Abstand der Scanlinien (kleiner = feiner, mehr Stiche)
    step_mm: float = 0.65           # Abtastschritt entlang der Linie
    mode: str = "mono"              # 'mono' (1-Farb-Gravur) | 'sepia' (2-Farb) | 'color4' (4-Farb CMYK)
    contrast: float = 1.25


def _channel_to_runs(
    darkness: np.ndarray,
    alpha: np.ndarray,
    width_mm: float,
    height_mm: float,
    angle_deg: float,
    row_spacing_mm: float,
    step_mm: float,
    min_darkness: float = 0.14,
) -> list[list[tuple[float, float]]]:
    """Erzeugt modulierte Wellen-/Zickzack-Läufe für einen Helligkeitskanal (0.0 = weiss, 1.0 = dunkel)."""
    h, w = darkness.shape
    ox, oy = -width_mm / 2.0, -height_mm / 2.0
    diag = math.hypot(width_mm, height_mm) / 2.0
    ca, sa = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    nx, ny = -sa, ca  # Normalenvektor quer zur Zeilenrichtung

    n_rows = int(math.ceil((2 * diag) / row_spacing_mm))
    runs: list[list[tuple[float, float]]] = []
    cur_run: list[tuple[float, float]] = []

    for ri in range(n_rows):
        v_off = -diag + (ri + 0.5) * row_spacing_mm
        # Boustrophedon (abwechselnd hin und her)
        n_steps = int(math.ceil((2 * diag) / step_mm))
        u_vals = np.linspace(-diag, diag, n_steps)
        if ri % 2 == 1:
            u_vals = u_vals[::-1]

        toggle = 1
        for u in u_vals:
            cx = u * ca + v_off * nx
            cy = u * sa + v_off * ny
            # liegt der Punkt im Bild?
            px = int((cx - ox) / width_mm * w)
            py = int((cy - oy) / height_mm * h)
            if not (0 <= px < w and 0 <= py < h) or alpha[py, px] < 128:
                if len(cur_run) >= 2:
                    runs.append(cur_run)
                cur_run = []
                continue

            d = float(darkness[py, px])
            if d < min_darkness:
                if len(cur_run) >= 2:
                    runs.append(cur_run)
                cur_run = []
                continue

            amp = (d ** 1.1) * (row_spacing_mm * 0.52)
            sx = cx + nx * amp * toggle
            sy = cy + ny * amp * toggle
            toggle = -toggle
            if cur_run and math.hypot(sx - cur_run[-1][0], sy - cur_run[-1][1]) > row_spacing_mm * 3.2:
                if len(cur_run) >= 2:
                    runs.append(cur_run)
                cur_run = [(sx, sy)]
            else:
                cur_run.append((sx, sy))

    if len(cur_run) >= 2:
        runs.append(cur_run)
    return runs


def generate_photostitch(rgba: np.ndarray, p: PhotoStitchParams) -> Design:
    h, w = rgba.shape[:2]
    height_mm = p.width_mm * h / max(w, 1)
    rgb = rgba[:, :, :3].astype(np.float32) / 255.0
    alpha = rgba[:, :, 3]

    # Kontrast + CLAHE-Schärfung für klare Gesichtszüge
    gray_u8 = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray_u8).astype(np.float32) / 255.0
    dark = np.clip((1.0 - gray_eq) * p.contrast, 0.0, 1.0)

    d = Design(name="PhotoStitch_Portrait")
    if p.mode == "mono":
        runs = _channel_to_runs(dark, alpha, p.width_mm, height_mm, 12.0, p.row_spacing_mm, p.step_mm)
        d.objects.append(StitchesObject(
            Thread((22, 24, 30), "Anthrazit-Schwarz (PhotoStitch)", "015", "PhotoStitch"),
            name="PhotoStitch Monochrom",
            stitch_runs=runs,
        ))
    elif p.mode == "sepia":
        runs_mid = _channel_to_runs(
            np.clip(dark * 0.85, 0, 1), alpha, p.width_mm, height_mm, -20.0, p.row_spacing_mm * 1.15, p.step_mm
        )
        runs_dark = _channel_to_runs(
            np.clip((dark - 0.38) * 1.5, 0, 1), alpha, p.width_mm, height_mm, 25.0, p.row_spacing_mm * 1.15, p.step_mm
        )
        d.objects.append(StitchesObject(
            Thread((165, 113, 61), "Sepia-Hellbraun", "102", "PhotoStitch"),
            name="PhotoStitch Sepia-Mitteltöne",
            stitch_runs=runs_mid,
        ))
        d.objects.append(StitchesObject(
            Thread((51, 32, 15), "Dunkelbraun-Schatten", "105", "PhotoStitch"),
            name="PhotoStitch Dunkelschatten",
            stitch_runs=runs_dark,
        ))
    else:
        # 4-Farb CMYK-Halbton (Gelb -> Magenta -> Cyan -> Key/Schwarz mit gedrehten Winkeln)
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        k = np.minimum(np.minimum(1.0 - r, 1.0 - g), 1.0 - b)
        denom = np.maximum(1.0 - k, 1e-4)
        c = (1.0 - r - k) / denom
        m = (1.0 - g - k) / denom
        y = (1.0 - b - k) / denom
        layers = [
            (y * 0.85, 0.0, Thread((255, 213, 0), "Photo-Gelb (Y)", "021", "PhotoStitch")),
            (m * 0.85, 15.0, Thread((204, 31, 122), "Photo-Magenta (M)", "052", "PhotoStitch")),
            (c * 0.85, 75.0, Thread((31, 138, 214), "Photo-Cyan (C)", "072", "PhotoStitch")),
            (np.clip(k * 1.15, 0, 1), 45.0, Thread((20, 20, 24), "Photo-Schwarz (K)", "015", "PhotoStitch")),
        ]
        sp = p.row_spacing_mm * 1.35
        for chan, ang, th in layers:
            runs = _channel_to_runs(chan, alpha, p.width_mm, height_mm, ang, sp, p.step_mm * 1.15, min_darkness=0.22)
            if runs:
                d.objects.append(StitchesObject(th, name=f"PhotoStitch {th.name}", stitch_runs=runs))
    return d
