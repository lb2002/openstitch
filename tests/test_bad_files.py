"""Beschädigte Dateien: Lesen darf scheitern, aber nie hängen, abstürzen oder Unsinn laden."""
from __future__ import annotations

import json
import math
import os
import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from PySide6.QtWidgets import QApplication

from openstitch.analysis import corpus
from openstitch.core.stitchplan import Cmd
from openstitch.engine.pro_tools import import_svg
from openstitch.io.fat12 import Fat12Image
from openstitch.io.formats import export_plan, import_file
from openstitch.io.project import load_project, save_project

_app = QApplication.instance() or QApplication(sys.argv)
ROUNDS = int(os.environ.get("OPENSTITCH_BADFILE_ROUNDS", "12"))
FORMATS = ("dst", "exp", "pes", "pec", "jef", "vp3", "xxx", "u01", "tbf")


def _mutate(data: bytes, rng: random.Random) -> bytes:
    b = bytearray(data)
    style = rng.randrange(4)
    if style == 0:
        return bytes(b[: rng.randrange(len(b) + 1)])                # abgeschnitten
    if style == 1:
        for _ in range(max(1, len(b) // 50)):                       # verstreute Bitfehler
            b[rng.randrange(len(b))] = rng.randrange(256)
        return bytes(b)
    if style == 2:
        k = rng.randrange(max(len(b) - 64, 1))                      # zerstörter Block
        b[k:k + 64] = bytes(rng.randrange(256) for _ in range(64))
        return bytes(b)
    return bytes(b[: min(512, len(b))]) * rng.randrange(1, 4) + bytes(rng.randrange(256) for _ in range(64))


@pytest.mark.parametrize("ext", FORMATS)
def test_damaged_embroidery_files(ext, tmp_path):
    plan = corpus.build("fill_islands").build_plan()
    good = tmp_path / f"good.{ext}"
    export_plan(plan, str(good))
    data = good.read_bytes()
    rng = random.Random(ext)
    for i in range(ROUNDS):
        bad = tmp_path / f"bad{i}.{ext}"
        bad.write_bytes(_mutate(data, rng))
        try:
            d = import_file(str(bad))
        except Exception:  # noqa: BLE001 - die Oberfläche fängt das ab und zeigt eine Meldung
            continue
        p = d.build_plan()
        for b in p.blocks:
            for s in b.stitches:
                assert math.isfinite(s.x) and math.isfinite(s.y)


def test_damaged_project_files(tmp_path):
    good = tmp_path / "good.ostitch"
    save_project(corpus.build("stack_badge"), str(good))
    data = good.read_bytes()
    rng = random.Random(7)
    for i in range(ROUNDS * 4):
        bad = tmp_path / f"bad{i}.ostitch"
        bad.write_bytes(_mutate(data, rng))
        try:
            load_project(str(bad)).build_plan()
        except ValueError:
            continue


@pytest.mark.parametrize("patch", [
    {"objects": [{"kind": "unknown"}]},
    {"objects": [{"kind": "fill", "thread": {"hex": "#zzzzzz"}, "geom": "POLYGON ((0 0, 1 0, 1 1, 0 0))"}]},
    {"objects": [{"kind": "fill", "thread": {"hex": "#ff0000"}, "geom": "not wkt"}]},
    {"objects": [{"kind": "fill", "thread": {"hex": "#ff0000"}, "geom": "POLYGON ((0 0, 1 0, 1 1, 0 0))", "spacing": 0}]},
    {"objects": "nope"},
    {"hoop": None},
])
def test_hostile_project_values_are_refused_cleanly(tmp_path, patch):
    good = tmp_path / "good.ostitch"
    save_project(corpus.build("fill_circle"), str(good))
    doc = json.loads(good.read_text(encoding="utf-8"))
    doc.update(patch)
    bad = tmp_path / "bad.ostitch"
    bad.write_text(json.dumps(doc), encoding="utf-8")
    try:
        load_project(str(bad)).build_plan()
    except ValueError as exc:
        assert "bad.ostitch" in str(exc)


def test_damaged_svg(tmp_path):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><linearGradient id="g">'
           '<stop stop-color="#f00"/></linearGradient></defs><g transform="scale(2)"><path fill="url(#g)" '
           'd="M10 10 C 20 20 40 20 50 10 A 5 5 0 0 1 60 60 Z"/><rect x="1" y="1" width="9" height="9" rx="2"/>'
           '<text>x</text></g></svg>').encode()
    rng = random.Random(3)
    for i in range(ROUNDS * 6):
        bad = tmp_path / f"bad{i}.svg"
        bad.write_bytes(_mutate(svg, rng))
        try:
            import_svg(str(bad)).build_plan()
        except (ValueError, ET.ParseError, KeyError, IndexError, TypeError, OverflowError, ZeroDivisionError):
            continue


def test_damaged_floppy_images():
    img = Fat12Image()
    img.add_file("TEST.EXP", b"x" * 2000)
    data = img.to_bytes()
    rng = random.Random(5)
    for _ in range(ROUNDS * 3):
        b = bytearray(data)
        for _ in range(200):
            b[rng.randrange(0, 40_000)] = rng.randrange(256)
        try:
            im = Fat12Image(bytes(b))
            for name, _size in im.list_files():
                im.read_file(name)
            im.add_file("NEW.DST", b"y" * 700)
        except (ValueError, IndexError, KeyError, OSError):
            continue


def test_import_centres_stitches_and_keeps_cmds(tmp_path):
    plan = corpus.build("fill_islands").build_plan()
    path = tmp_path / "a.dst"
    export_plan(plan, str(path))
    d = import_file(str(path))
    p2 = d.build_plan()
    x0, y0, x1, y1 = p2.bounds()
    assert abs(x0 + x1) < 0.5 and abs(y0 + y1) < 0.5
    assert sum(1 for b in p2.blocks for s in b.stitches if s.cmd == Cmd.TRIM) >= plan.trim_count - 1
