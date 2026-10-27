"""FAT12-Diskettenabbild (1.44 MB), wie es die Melco EMT10/4 erwartet.

Damit lassen sich .IMG-Dateien für USB-Disketten-Emulatoren (GoTek mit FlashFloppy,
HxC) erzeugen oder bestehende Abbilder ergänzen, ohne Admin-Rechte oder Zusatztools.
"""
from __future__ import annotations

import datetime as _dt
import re
import struct

SECTOR = 512
TOTAL_SECTORS = 2880
FAT_SECTORS = 9
ROOT_ENTRIES = 224
RESERVED = 1
NUM_FATS = 2
ROOT_START = RESERVED + NUM_FATS * FAT_SECTORS          # 19
ROOT_SECTORS = ROOT_ENTRIES * 32 // SECTOR              # 14
DATA_START = ROOT_START + ROOT_SECTORS                  # 33
CLUSTERS = TOTAL_SECTORS - DATA_START                   # 2847
IMAGE_SIZE = TOTAL_SECTORS * SECTOR                     # 1 474 560


def dos_name(name: str, default_ext: str = "EXP") -> str:
    """Erzeugt einen gültigen 8.3-Namen (Grossbuchstaben)."""
    base, _, ext = name.rpartition(".")
    if not base:
        base, ext = ext, default_ext
    repl = {"Ä": "AE", "Ö": "OE", "Ü": "UE", "ß": "SS"}
    base = base.upper()
    for k, v in repl.items():
        base = base.replace(k, v)
    base = re.sub(r"[^A-Z0-9_\-]", "", base)[:8] or "DESIGN"
    ext = re.sub(r"[^A-Z0-9]", "", ext.upper())[:3] or default_ext
    return f"{base}.{ext}"


def _83(name: str) -> bytes:
    b, _, e = name.partition(".")
    return (b.ljust(8)[:8] + e.ljust(3)[:3]).encode("ascii")


def _dos_datetime(t: _dt.datetime):
    date = ((t.year - 1980) << 9) | (t.month << 5) | t.day
    time = (t.hour << 11) | (t.minute << 5) | (t.second // 2)
    return date, time


class Fat12Image:
    def __init__(self, data: bytes | None = None, label: str = "OPENSTITCH"):
        if data is None:
            self.data = bytearray(IMAGE_SIZE)
            self._format(label)
        else:
            if len(data) != IMAGE_SIZE:
                raise ValueError("Nur 1.44-MB-Abbilder (1 474 560 Bytes) werden unterstützt.")
            self.data = bytearray(data)
            if struct.unpack_from("<H", self.data, 11)[0] != SECTOR:
                raise ValueError("Kein gültiges FAT12-Abbild.")

    # ---------------------------------------------------------------- Format
    def _format(self, label: str):
        bs = bytearray(SECTOR)
        bs[0:3] = b"\xEB\x3C\x90"
        bs[3:11] = b"OPENSTCH"
        struct.pack_into("<HBHBHHBHHHII", bs, 11, SECTOR, 1, RESERVED, NUM_FATS, ROOT_ENTRIES,
                         TOTAL_SECTORS, 0xF0, FAT_SECTORS, 18, 2, 0, 0)
        bs[36] = 0x00      # Laufwerksnummer
        bs[38] = 0x29      # erweiterte Boot-Signatur
        struct.pack_into("<I", bs, 39, int(_dt.datetime.now().timestamp()) & 0xFFFFFFFF)
        bs[43:54] = label.upper().ljust(11)[:11].encode("ascii")
        bs[54:62] = b"FAT12   "
        # minimaler Bootcode: "nicht bootfähig"-Schleife
        bs[62:64] = b"\xEB\xFE"
        bs[510:512] = b"\x55\xAA"
        self.data[0:SECTOR] = bs
        self._set_fat(0, 0xFF0)
        self._set_fat(1, 0xFFF)
        # Volume-Label-Eintrag
        e = bytearray(32)
        e[0:11] = label.upper().ljust(11)[:11].encode("ascii")
        e[11] = 0x08
        self.data[ROOT_START * SECTOR:ROOT_START * SECTOR + 32] = e

    # ------------------------------------------------------------------- FAT
    def _get_fat(self, n: int) -> int:
        off = RESERVED * SECTOR + (n * 3) // 2
        v = self.data[off] | (self.data[off + 1] << 8)
        return (v >> 4) if n & 1 else (v & 0xFFF)

    def _set_fat(self, n: int, val: int):
        for f in range(NUM_FATS):
            off = (RESERVED + f * FAT_SECTORS) * SECTOR + (n * 3) // 2
            v = self.data[off] | (self.data[off + 1] << 8)
            if n & 1:
                v = (v & 0x000F) | (val << 4)
            else:
                v = (v & 0xF000) | (val & 0xFFF)
            self.data[off] = v & 0xFF
            self.data[off + 1] = (v >> 8) & 0xFF

    def free_bytes(self) -> int:
        return sum(1 for c in range(2, CLUSTERS + 2) if self._get_fat(c) == 0) * SECTOR

    # -------------------------------------------------------------- Einträge
    def _entries(self):
        base = ROOT_START * SECTOR
        for i in range(ROOT_ENTRIES):
            off = base + i * 32
            yield i, off, self.data[off:off + 32]

    def list_files(self) -> list[tuple[str, int]]:
        out = []
        for _, _, e in self._entries():
            if e[0] == 0:
                break
            if e[0] == 0xE5 or e[11] & 0x08 or e[11] == 0x0F:
                continue
            name = e[0:8].decode("ascii", "replace").rstrip()
            ext = e[8:11].decode("ascii", "replace").rstrip()
            size = struct.unpack_from("<I", e, 28)[0]
            out.append((f"{name}.{ext}" if ext else name, size))
        return out

    def read_file(self, name: str) -> bytes:
        key = _83(dos_name(name))
        for _, _, e in self._entries():
            if e[0] == 0:
                break
            if bytes(e[0:11]) == key and e[0] != 0xE5:
                cl = struct.unpack_from("<H", e, 26)[0]
                size = struct.unpack_from("<I", e, 28)[0]
                out = bytearray()
                while 2 <= cl < 0xFF8:
                    s = (DATA_START + cl - 2) * SECTOR
                    out += self.data[s:s + SECTOR]
                    cl = self._get_fat(cl)
                return bytes(out[:size])
        raise FileNotFoundError(name)

    def delete_file(self, name: str) -> bool:
        key = _83(dos_name(name))
        for _, off, e in self._entries():
            if e[0] == 0:
                break
            if bytes(e[0:11]) == key:
                cl = struct.unpack_from("<H", e, 26)[0]
                while 2 <= cl < 0xFF8:
                    nxt = self._get_fat(cl)
                    self._set_fat(cl, 0)
                    cl = nxt
                self.data[off] = 0xE5
                return True
        return False

    def add_file(self, name: str, content: bytes) -> str:
        name = dos_name(name)
        self.delete_file(name)
        need = max(1, -(-len(content) // SECTOR))
        free = [c for c in range(2, CLUSTERS + 2) if self._get_fat(c) == 0]
        if len(free) < need:
            raise IOError("Nicht genug Platz auf der Diskette (1.44 MB).")
        chain = free[:need]
        for i, c in enumerate(chain):
            self._set_fat(c, chain[i + 1] if i + 1 < len(chain) else 0xFFF)
            s = (DATA_START + c - 2) * SECTOR
            chunk = content[i * SECTOR:(i + 1) * SECTOR]
            self.data[s:s + SECTOR] = chunk.ljust(SECTOR, b"\x00")
        slot = None
        for _, off, e in self._entries():
            if e[0] in (0x00, 0xE5):
                slot = off
                break
        if slot is None:
            raise IOError("Stammverzeichnis voll (max. 224 Dateien).")
        e = bytearray(32)
        e[0:11] = _83(name)
        e[11] = 0x20  # Archiv
        date, time = _dos_datetime(_dt.datetime.now())
        e[13] = 0
        struct.pack_into("<HHHHHHH", e, 14, time, date, date, 0, time, date, chain[0])
        struct.pack_into("<I", e, 28, len(content))
        self.data[slot:slot + 32] = e
        return name

    def to_bytes(self) -> bytes:
        return bytes(self.data)
