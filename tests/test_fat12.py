"""Tests für das FAT12-Diskettenabbild (8.3-Namen, Transaktionen, defekte Abbilder)."""
import struct

import pytest

from openstitch.io.fat12 import CLUSTERS, IMAGE_SIZE, ROOT_ENTRIES, ROOT_START, SECTOR, Fat12Image, dos_name


def test_dos_name_extension_and_chars():
    assert dos_name("mein_logo.exp") == "MEIN_LOG.EXP"
    assert dos_name("Logo v1.5") == "LOGOV15.EXP"          # ".5" ist keine Endung
    assert dos_name("Logo v1.5.dst") == "LOGOV15.DST"      # nur der letzte Punkt zählt
    assert dos_name("Größe:*?.exp") == "GROESSE.EXP"
    assert dos_name("design") == "DESIGN.EXP"
    assert dos_name("x.pes", "DST") == "X.PES"
    assert dos_name("noext", "DST") == "NOEXT.DST"
    assert dos_name("???.exp") == "DESIGN.EXP"


def test_unique_short_names_and_replace():
    img = Fat12Image()
    a = img.add_file("Logo_Front_A.exp", b"A" * 700)
    b = img.add_file("Logo_Front_B.exp", b"B" * 700)
    c = img.add_file("Logo_Front_C.exp", b"C" * 10)
    assert (a, b, c) == ("LOGO_FRO.EXP", "LOGO_F~1.EXP", "LOGO_F~2.EXP")
    assert [n for n, _ in img.list_files()] == ["LOGO_FRO.EXP", "LOGO_F~1.EXP", "LOGO_F~2.EXP"]
    # gleicher Langname ersetzt (auch nach Neuladen des Abbilds)
    img = Fat12Image(img.to_bytes())
    free_before = img.free_bytes()
    assert img.add_file("Logo_Front_B.exp", b"b" * 100) == "LOGO_F~1.EXP"
    assert len(img.list_files()) == 3
    assert img.free_bytes() == free_before + SECTOR  # 2 Cluster -> 1 Cluster
    assert img.read_file("Logo_Front_B.exp") == b"b" * 100
    assert img.read_file("LOGO_F~1.EXP") == b"b" * 100
    assert img.read_file("Logo_Front_A.exp") == b"A" * 700
    # gleicher 8.3-Name ersetzt ebenfalls
    assert img.add_file("LOGO_FRO.EXP", b"x") == "LOGO_FRO.EXP"
    assert img.read_file("LOGO_FRO.EXP") == b"x"
    assert len(img.list_files()) == 3


def test_delete_accepts_listed_names():
    img = Fat12Image()
    img.add_file("Logo_Front_A.exp", b"1")
    img.add_file("Logo_Front_B.exp", b"2")
    # Eintrag ohne Endung (z. B. von anderem Gerät geschrieben) direkt anlegen
    e = bytearray(32)
    e[0:11] = b"README     "
    e[11] = 0x20
    slot = next(i for i in range(ROOT_ENTRIES) if img.data[ROOT_START * SECTOR + 32 * i] == 0)
    off = ROOT_START * SECTOR + 32 * slot
    img.data[off:off + 32] = e
    names = [n for n, _ in img.list_files()]
    assert "README" in names
    for n in names:
        assert img.delete_file(n) is True, n
    assert img.list_files() == []
    assert img.free_bytes() == CLUSTERS * SECTOR
    # Langname funktioniert weiterhin
    img.add_file("Mein langer Name.exp", b"z")
    assert img.delete_file("Mein langer Name.exp") is True
    assert img.delete_file("gibts_nicht.exp") is False


def test_add_file_is_transactional_when_full():
    img = Fat12Image()
    img.add_file("keep.exp", b"K" * 1000)
    big = b"\x00" * (CLUSTERS * SECTOR + 1)
    snap = img.to_bytes()
    with pytest.raises(ValueError, match="Nicht genug Platz"):
        img.add_file("keep.exp", big)  # Ersetzen scheitert -> alte Datei bleibt
    assert img.to_bytes() == snap
    assert img.read_file("KEEP.EXP") == b"K" * 1000

    # Verzeichnis voll: 222 weitere Einträge (Slot 0 = Volume-Label, 1 = KEEP.EXP)
    for i in range(ROOT_ENTRIES - 2):
        img.add_file(f"F{i}.EXP", b"")
    snap = img.to_bytes()
    with pytest.raises(ValueError, match="Stammverzeichnis voll"):
        img.add_file("NEU.EXP", b"neu")
    assert img.to_bytes() == snap
    # Ersetzen derselben Datei geht weiter (Slot wird wiederverwendet)
    img.add_file("F5.EXP", b"neu")
    assert img.read_file("F5.EXP") == b"neu"


def test_zero_byte_file_allocates_no_cluster():
    img = Fat12Image()
    free = img.free_bytes()
    assert img.add_file("leer.exp", b"") == "LEER.EXP"
    assert img.free_bytes() == free
    e = img.data[ROOT_START * SECTOR + 32:ROOT_START * SECTOR + 64]
    assert struct.unpack_from("<H", e, 26)[0] == 0
    assert img.read_file("LEER.EXP") == b""
    assert img.list_files() == [("LEER.EXP", 0)]
    assert img.delete_file("LEER.EXP") and img.free_bytes() == free


def test_cyclic_fat_chain_raises():
    img = Fat12Image()
    img.add_file("loop.exp", b"L" * (3 * SECTOR))
    img2 = Fat12Image(img.to_bytes())
    img2._set_fat(4, 2)  # Cluster 2 -> 3 -> 4 -> 2 …
    with pytest.raises(ValueError, match="Schleife"):
        img2.read_file("LOOP.EXP")
    img2._set_fat(4, 0xEEE)  # ungültiger Cluster ausserhalb des Datenbereichs
    with pytest.raises(ValueError):
        img2.read_file("LOOP.EXP")
    assert img2.delete_file("LOOP.EXP") is True  # Löschen bleibt robust
    assert len(img2.to_bytes()) == IMAGE_SIZE


def test_lfn_entries_are_hidden_from_listing():
    img = Fat12Image()
    img.add_file("ein sehr langer Dateiname für die Stickmaschine.exp", b"data")
    assert img.list_files() == [("EINSEHRL.EXP", 4)]
    # Langname-Einträge tragen Attribut 0x0F (für DOS/Melco unsichtbar)
    first = ROOT_START * SECTOR + 32
    assert img.data[first + 11] == 0x0F
