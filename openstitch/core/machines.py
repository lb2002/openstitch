"""Maschinen-Profile für ein universelles Open-Source-Stickprogramm.

Damit ist OpenStitch nicht nur auf die Melco EMT10/4 abgestimmt, sondern unterstützt
alle grossen Industrie- und Haushalts-Stickmaschinen mit ihren jeweiligen Eigenheiten
(Nadelanzahl, natives Format, max. Stichlänge, SPM, Trim-Verhalten, Standardrahmen).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MachineProfile:
    id: str
    name: str
    manufacturer: str
    needles: int
    native_ext: str
    max_stitch_mm: float
    default_spm: int
    trim_mode: str          # 'both' | 'code' | 'jumps'
    floppy_144mb: bool
    default_hoop_w: float
    default_hoop_h: float
    default_hoop_round: bool
    notes: str


MACHINE_PROFILES: list[MachineProfile] = [
    MachineProfile(
        id="universal_multi",
        name="Universal Standard (DST / PES / EXP · 15 Nadeln)",
        manufacturer="Universal",
        needles=15,
        native_ext="dst",
        max_stitch_mm=12.1,
        default_spm=950,
        trim_mode="both",
        floppy_144mb=True,
        default_hoop_w=180,
        default_hoop_h=180,
        default_hoop_round=True,
        notes="Herstellerneutrales Standardprofil für alle Industrie- und Mehrnadel-Stickmaschinen.",
    ),
    MachineProfile(
        id="tajima_tmez",
        name="Tajima TMEZ / TFMX / TMBR (15 Nadeln)",
        manufacturer="Tajima",
        needles=15,
        native_ext="dst",
        max_stitch_mm=12.1,
        default_spm=1000,
        trim_mode="jumps",
        floppy_144mb=True,
        default_hoop_w=200,
        default_hoop_h=200,
        default_hoop_round=True,
        notes="Industrie-Standard Tajima DST (Ternär-Codierung, Trim nach Sprungfolge).",
    ),
    MachineProfile(
        id="brother_pr",
        name="Brother PR-Serie / Persona (6–10 Nadeln)",
        manufacturer="Brother",
        needles=10,
        native_ext="pes",
        max_stitch_mm=12.1,
        default_spm=1000,
        trim_mode="code",
        floppy_144mb=False,
        default_hoop_w=200,
        default_hoop_h=300,
        default_hoop_round=False,
        notes="Brother PES mit eingebetteter RGB-Farbtabelle im Header.",
    ),
    MachineProfile(
        id="brother_home",
        name="Brother / Baby Lock Haushalt (1 Nadel · PES)",
        manufacturer="Brother",
        needles=1,
        native_ext="pes",
        max_stitch_mm=12.1,
        default_spm=650,
        trim_mode="code",
        floppy_144mb=False,
        default_hoop_w=130,
        default_hoop_h=180,
        default_hoop_round=False,
        notes="1-Nadel-Maschine: stoppt bei jedem Farbwechsel für manuellen Garnwechsel.",
    ),
    MachineProfile(
        id="barudan_bext",
        name="Barudan BEKT / BEXT (15 Nadeln)",
        manufacturer="Barudan",
        needles=15,
        native_ext="u01",
        max_stitch_mm=12.1,
        default_spm=1000,
        trim_mode="code",
        floppy_144mb=True,
        default_hoop_w=180,
        default_hoop_h=180,
        default_hoop_round=True,
        notes="Barudan U01 / DST mit explizitem Trim- & Nadelbefehl.",
    ),
    MachineProfile(
        id="ricoma_happy_zsk",
        name="Ricoma / HappyJapan / SWF / ZSK (12–15 Nadeln)",
        manufacturer="Universal Industrie",
        needles=15,
        native_ext="dst",
        max_stitch_mm=12.1,
        default_spm=950,
        trim_mode="both",
        floppy_144mb=False,
        default_hoop_w=200,
        default_hoop_h=200,
        default_hoop_round=True,
        notes="Universelles Industrie-DST/EXP-Profil für Mehrnadelmaschinen.",
    ),
    MachineProfile(
        id="janome_elna",
        name="Janome / Elna / Bernina Haushalt (JEF / EXP)",
        manufacturer="Janome / Bernina",
        needles=1,
        native_ext="jef",
        max_stitch_mm=12.1,
        default_spm=700,
        trim_mode="code",
        floppy_144mb=False,
        default_hoop_w=140,
        default_hoop_h=200,
        default_hoop_round=False,
        notes="Janome JEF bzw. Bernina USB-EXP.",
    ),
    MachineProfile(
        id="pfaff_husqvarna",
        name="Pfaff / Husqvarna Viking (VP3)",
        manufacturer="Husqvarna / Pfaff",
        needles=1,
        native_ext="vp3",
        max_stitch_mm=12.1,
        default_spm=700,
        trim_mode="code",
        floppy_144mb=False,
        default_hoop_w=180,
        default_hoop_h=130,
        default_hoop_round=False,
        notes="Hochauflösendes VP3-Format mit Garnfarben.",
    ),
    MachineProfile(
        id="melco_emt10_4",
        name="Melco EMT10/4 (4-Kopf / 10 Nadeln)",
        manufacturer="Melco",
        needles=10,
        native_ext="exp",
        max_stitch_mm=12.1,
        default_spm=850,
        trim_mode="both",
        floppy_144mb=True,
        default_hoop_w=180,
        default_hoop_h=180,
        default_hoop_round=True,
        notes="Natives EXP (0.1 mm), Kombi-Trim (80 80 07 00 + Sprünge), 1.44 MB FAT12 Diskette/GoTek.",
    ),
    MachineProfile(
        id="melco_amaya_bravo",
        name="Melco Amaya / EMT16X / Bravo (16 Nadeln)",
        manufacturer="Melco / Bernina",
        needles=16,
        native_ext="exp",
        max_stitch_mm=12.1,
        default_spm=1100,
        trim_mode="code",
        floppy_144mb=False,
        default_hoop_w=210,
        default_hoop_h=210,
        default_hoop_round=True,
        notes="Moderne 16-Nadel-Melco mit ActiFeed; nutzt EXP über Ethernet/USB.",
    ),
]


def get_machine_profile(profile_id: str) -> MachineProfile:
    for p in MACHINE_PROFILES:
        if p.id == profile_id:
            return p
    return MACHINE_PROFILES[0]
