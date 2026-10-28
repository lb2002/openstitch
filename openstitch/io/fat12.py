"""FAT12-Diskettenabbild (1.44 MB), wie es die Melco EMT10/4 erwartet.

Damit lassen sich .IMG-Dateien für USB-Disketten-Emulatoren (GoTek mit FlashFloppy,
HxC) erzeugen oder bestehende Abbilder ergänzen, ohne Admin-Rechte oder Zusatztools.
Lange Dateinamen werden wie unter Windows als 8.3-Name (ggf. NAME~1.EXT) plus
VFAT-Langname abgelegt; die Maschine sieht nur den 8.3-Namen.
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

_REAL_EXT = re.compile(r"(?=.*[A-Za-z])[A-Za-z0-9]{1,3}")  # "exp", "u01" – aber nicht "5" aus "v1.5"
_LFN_BAD = re.compile(r'[\x00-\x1f\\/:*?"<>|]')


def _split_name(name: str, default_ext: str) -> tuple[str, str]:
    """Trennt Basis und Endung: nur der LETZTE Punkt zählt, und nur bei einer echten Endung."""
    name = name.strip()
    base, dot, ext = name.rpartition(".")
    if not dot or not base.strip(". ") or not _REAL_EXT.fullmatch(ext):
        return name, default_ext
    return base, ext


def _clean83(s: str) -> str:
    s = s.upper()
    for k, v in {"Ä": "AE", "Ö": "OE", "Ü": "UE", "ß": "SS", "ẞ": "SS"}.items():
        s = s.replace(k, v)
    return re.sub(r"[^A-Z0-9_\-]", "", s)


def dos_name(name: str, default_ext: str = "EXP") -> str:
    """Erzeugt einen gültigen 8.3-Namen (Grossbuchstaben, nur A-Z 0-9 _ -)."""
    base, ext = _split_name(name, default_ext)
    base = _clean83(base)[:8] or "DESIGN"
    ext = _clean83(ext)[:3] or _clean83(default_ext)[:3]
    return f"{base}.{ext}" if ext else base


def _long_name(name: str, default_ext: str = "EXP") -> str:
    """Langer (VFAT-)Name wie vom Aufrufer gemeint; ohne echte Endung wird die Standardendung angehängt."""
    n = _LFN_BAD.sub("", name).strip().rstrip(". ")
    base, _ = _split_name(n, default_ext)
    if base == n and default_ext:
        n = f"{n}.{default_ext.lower()}"
    return n[:255] or dos_name(name, default_ext)


def _83(name: str) -> bytes:
    b, _, e = name.partition(".")
    return (b.ljust(8)[:8] + e.ljust(3)[:3]).encode("ascii")


def _lfn_checksum(short11: bytes) -> int:
    s = 0
    for c in short11:
        s = (((s & 1) << 7) + (s >> 1) + c) & 0xFF
    return s


def _lfn_entries(long: str, short11: bytes) -> list[bytes]:
    """VFAT-Langnamen-Einträge in Disk-Reihenfolge (letzter Teil zuerst), wie Windows sie schreibt."""
    raw = long.encode("utf-16-le")
    units = [raw[i:i + 2] for i in range(0, len(raw), 2)]
    n = -(-len(units) // 13)
    if len(units) % 13:
        units.append(b"\x00\x00")
    units += [b"\xFF\xFF"] * (n * 13 - len(units))
    chk = _lfn_checksum(short11)
    out = []
    for seq in range(n, 0, -1):
        part = units[(seq - 1) * 13:seq * 13]
        e = bytearray(32)
        e[0] = seq | (0x40 if seq == n else 0)
        e[1:11] = b"".join(part[0:5])
        e[11] = 0x0F
        e[13] = chk
        e[14:26] = b"".join(part[5:11])
        e[28:32] = b"".join(part[11:13])
        out.append(bytes(e))
    return out


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

    def _chain(self, start: int, strict: bool = True) -> list[int]:
        """Clusterkette ab `start`; begrenzt gegen Schleifen/ungültige Cluster aus fremden .IMG-Dateien."""
        out, seen, cl = [], set(), start
        while 2 <= cl < 0xFF8:
            if cl >= CLUSTERS + 2 or cl in seen:
                if strict:
                    raise ValueError("Beschädigtes Abbild: FAT-Kette enthält eine Schleife oder einen ungültigen Cluster.")
                break
            seen.add(cl)
            out.append(cl)
            cl = self._get_fat(cl)
        return out

    def free_bytes(self) -> int:
        return sum(1 for c in range(2, CLUSTERS + 2) if self._get_fat(c) == 0) * SECTOR

    # -------------------------------------------------------------- Einträge
    def _entries(self):
        base = ROOT_START * SECTOR
        for i in range(ROOT_ENTRIES):
            off = base + i * 32
            yield i, off, self.data[off:off + 32]

    def _scan(self) -> list[dict]:
        """Alle Dateieinträge des Stammverzeichnisses inkl. VFAT-Langname und belegter Slots."""
        files, parts, lfn_slots, chk = [], {}, [], None
        for i, off, e in self._entries():
            if e[0] == 0:
                break
            if e[0] == 0xE5:
                parts, lfn_slots = {}, []
                continue
            if e[11] == 0x0F:  # Langnamen-Teil
                if e[0] & 0x40:
                    parts, lfn_slots = {}, []
                parts[e[0] & 0x1F] = bytes(e[1:11] + e[14:26] + e[28:32])
                lfn_slots.append(i)
                chk = e[13]
                continue
            if not e[11] & 0x18:  # kein Volume-Label, kein Verzeichnis
                long = None
                if parts and chk == _lfn_checksum(bytes(e[0:11])) and sorted(parts) == list(range(1, len(parts) + 1)):
                    raw = b"".join(parts[k] for k in sorted(parts))
                    long = raw.decode("utf-16-le", "replace").split("\x00")[0]
                name = e[0:8].decode("ascii", "replace").rstrip()
                ext = e[8:11].decode("ascii", "replace").rstrip()
                files.append({"slots": lfn_slots + [i], "short": f"{name}.{ext}" if ext else name, "long": long,
                              "cluster": struct.unpack_from("<H", e, 26)[0],
                              "size": struct.unpack_from("<I", e, 28)[0]})
            parts, lfn_slots = {}, []
        return files

    def list_files(self) -> list[tuple[str, int]]:
        """(8.3-Name, Grösse) – genau diese Namen akzeptieren read_file/delete_file unverändert."""
        return [(f["short"], f["size"]) for f in self._scan()]

    def _lookup(self, name: str, default_ext: str = "EXP", legacy: bool = True, files=None):
        """Sucht einen Eintrag: 1. exakter 8.3-Name wie gelistet, 2. Langname (VFAT),
        3. (legacy) umgewandelter 8.3-Name bei Einträgen ohne Langname. -> (Eintrag, exakt?)"""
        files = self._scan() if files is None else files
        up = name.strip().upper()
        for f in files:
            if f["short"] == up:
                return f, True
        lng = _long_name(name, default_ext).casefold()
        for f in files:
            if f["long"] and f["long"].casefold() == lng:
                return f, False
        if legacy:
            short = dos_name(name, default_ext)
            for f in files:
                if f["short"] == short and not f["long"]:
                    return f, False
        return None, False

    def read_file(self, name: str) -> bytes:
        f, _ = self._lookup(name)
        if f is None:
            raise FileNotFoundError(name)
        out = bytearray()
        for cl in self._chain(f["cluster"]):
            s = (DATA_START + cl - 2) * SECTOR
            out += self.data[s:s + SECTOR]
        if len(out) < f["size"]:
            raise ValueError(f"Beschädigtes Abbild: {f['short']} ist kürzer als im Verzeichnis angegeben.")
        return bytes(out[:f["size"]])

    def _remove(self, f: dict):
        for cl in self._chain(f["cluster"], strict=False):
            self._set_fat(cl, 0)
        base = ROOT_START * SECTOR
        for i in f["slots"]:
            self.data[base + i * 32] = 0xE5

    def delete_file(self, name: str) -> bool:
        """Löscht per 8.3-Name (wie von list_files geliefert) oder per Langname."""
        f, _ = self._lookup(name)
        if f is None:
            return False
        self._remove(f)
        return True

    def _unique_short(self, long: str, default_ext: str, files: list[dict]) -> str:
        """8.3-Name wie bei Windows: gekürzter Name, bei Kollision NAME~1.EXT, ~2, …"""
        taken = {f["short"] for f in files}
        short = dos_name(long, default_ext)
        if short not in taken:
            return short
        base, ext = _split_name(long, default_ext)
        base = _clean83(base) or "DESIGN"
        ext = _clean83(ext)[:3]
        for n in range(1, 100000):
            tail = f"~{n}"
            cand = base[:8 - len(tail)] + tail + (f".{ext}" if ext else "")
            if cand not in taken:
                return cand
        raise ValueError("Kein freier 8.3-Name mehr verfügbar.")

    def add_file(self, name: str, content: bytes, default_ext: str = "EXP") -> str:
        """Legt eine Datei an (gleicher Name ersetzt die alte Datei) und liefert den 8.3-Namen.
        Transaktional: reicht Platz oder Verzeichnis nicht, bleibt das Abbild unverändert (ValueError)."""
        content = bytes(content)
        files = self._scan()
        old, exact = self._lookup(name, default_ext, legacy=False, files=files)
        if old is not None:
            short = old["short"]
            long = short if exact else old["long"]
        else:
            long = _long_name(name, default_ext)
            short = self._unique_short(long, default_ext, files)
        lfn = _lfn_entries(long, _83(short)) if long.upper() != short else []

        # 1. Platz prüfen (Cluster der ersetzten Datei zählen als frei)
        old_chain = self._chain(old["cluster"], strict=False) if old else []
        free = sorted({c for c in range(2, CLUSTERS + 2) if self._get_fat(c) == 0} | set(old_chain))
        need = -(-len(content) // SECTOR)
        if need > len(free):
            raise ValueError(f"Nicht genug Platz auf der Diskette: {short} braucht {need * SECTOR:,} Bytes, "
                             f"frei sind nur {len(free) * SECTOR:,} Bytes.".replace(",", "'"))
        # 2. zusammenhängende freie Verzeichnis-Slots suchen (Langname-Teile + 8.3-Eintrag)
        old_slots = set(old["slots"]) if old else set()
        usable, ended = [], False
        for i, _, e in self._entries():
            ended = ended or e[0] == 0
            usable.append(ended or e[0] == 0xE5 or i in old_slots)
        want = len(lfn) + 1
        first = next((i for i in range(ROOT_ENTRIES - want + 1) if all(usable[i:i + want])), None)
        if first is None:
            raise ValueError(f"Stammverzeichnis voll (max. {ROOT_ENTRIES} Einträge): {short} wurde nicht gespeichert.")

        # 3. ab hier kann nichts mehr scheitern: alte Datei entfernen, Daten schreiben
        if old:
            self._remove(old)
        chain = free[:need]
        for i, c in enumerate(chain):
            self._set_fat(c, chain[i + 1] if i + 1 < len(chain) else 0xFFF)
            s = (DATA_START + c - 2) * SECTOR
            self.data[s:s + SECTOR] = content[i * SECTOR:(i + 1) * SECTOR].ljust(SECTOR, b"\x00")
        e = bytearray(32)
        e[0:11] = _83(short)
        e[11] = 0x20  # Archiv
        date, time = _dos_datetime(_dt.datetime.now())
        struct.pack_into("<HHHHHHH", e, 14, time, date, date, 0, time, date, chain[0] if chain else 0)
        struct.pack_into("<I", e, 28, len(content))
        base = ROOT_START * SECTOR
        for k, ent in enumerate(lfn + [bytes(e)]):
            off = base + (first + k) * 32
            self.data[off:off + 32] = ent
        return short

    def to_bytes(self) -> bytes:
        return bytes(self.data)
