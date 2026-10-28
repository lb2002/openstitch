"""Garnfarben-Paletten und Farbzuordnung (ΔE im CIE-Lab-Raum).

Enthält echte Industrie- und Haushalts-Garnkataloge mit offiziellen Farbnummern:
1. Madeira Polyneon No. 40 (Industrie-Standard)
2. Isacord Polyester No. 40 (Amann Group Industrie-Standard)
3. Gunold POLY 40 (Industrie-Stickgarn)
4. Brother Embroidery / Country (Haushalt & PR-Serie)
5. OpenStitch Universal Standard
Zusätzlich können eigene CSV-Farbkarten (`code;name;#rrggbb`) geladen werden.
"""
from __future__ import annotations

import csv
import math
import os

from ..core.stitchplan import Thread

_GENERIC = [
    ("001", "Weiss", "#ffffff"), ("002", "Naturweiss", "#f4efe1"), ("003", "Creme", "#efe2b8"),
    ("010", "Hellgrau", "#c8c8c8"), ("011", "Silbergrau", "#a3a6a8"), ("012", "Grau", "#7d7f80"),
    ("013", "Dunkelgrau", "#4a4c4e"), ("014", "Anthrazit", "#2e3033"), ("015", "Schwarz", "#111111"),
    ("020", "Zitronengelb", "#fff23a"), ("021", "Gelb", "#ffd500"), ("022", "Sonnengelb", "#ffb800"),
    ("023", "Goldgelb", "#e8a317"), ("024", "Ocker", "#c58b1d"), ("030", "Hellorange", "#ffa94d"),
    ("031", "Orange", "#ff7a00"), ("032", "Dunkelorange", "#e2561b"), ("040", "Lachs", "#ff9a8a"),
    ("041", "Koralle", "#ff6f61"), ("042", "Hellrot", "#ee3a32"), ("043", "Rot", "#d0121b"),
    ("044", "Kirschrot", "#b0101e"), ("045", "Weinrot", "#7c1022"), ("046", "Bordeaux", "#5a0f1e"),
    ("050", "Rosa", "#f9b6c8"), ("051", "Pink", "#f05a9a"), ("052", "Magenta", "#cc1f7a"),
    ("053", "Fuchsia", "#a0136b"), ("060", "Flieder", "#c8a8dc"), ("061", "Lila", "#8e5bb5"),
    ("062", "Violett", "#5e2d8c"), ("063", "Aubergine", "#3d1a4f"), ("070", "Babyblau", "#b4d7f0"),
    ("071", "Himmelblau", "#6fb4e6"), ("072", "Azurblau", "#1f8ad6"), ("073", "Königsblau", "#1846a8"),
    ("074", "Kobaltblau", "#123b8a"), ("075", "Marine", "#14244d"), ("076", "Nachtblau", "#0e1730"),
    ("080", "Türkis", "#27c3c8"), ("081", "Petrol", "#0f7a84"), ("082", "Aqua", "#7fe0d8"),
    ("090", "Mint", "#a7e3b5"), ("091", "Hellgrün", "#7ccf4f"), ("092", "Grasgrün", "#3fa33a"),
    ("093", "Grün", "#1c8a3e"), ("094", "Smaragd", "#0f6e47"), ("095", "Tannengrün", "#16432c"),
    ("096", "Oliv", "#6b7a2a"), ("097", "Khaki", "#a49a64"), ("098", "Limette", "#bfe01f"),
    ("100", "Beige", "#d9c29a"), ("101", "Sand", "#c8a874"), ("102", "Hellbraun", "#a5713d"),
    ("103", "Braun", "#7a4a24"), ("104", "Schokobraun", "#4e2d17"), ("105", "Dunkelbraun", "#33200f"),
    ("110", "Hautton hell", "#f6d3b8"), ("111", "Hautton", "#e6b08a"), ("112", "Hautton dunkel", "#b57a52"),
    ("120", "Gold (Metallic)", "#c9a43b"), ("121", "Silber (Metallic)", "#bfc3c7"),
]

# 1. Madeira Polyneon No. 40 (Offizielle Farbnummern 1800–1999)
_MADEIRA_POLYNEON_40 = [
    ("1801", "Super White", "#ffffff"), ("1802", "Natural White", "#f7f3e6"), ("1803", "Ivory Cream", "#efe4c2"),
    ("1811", "Pearl Grey", "#d2d4d6"), ("1812", "Silver Grey", "#a6aaae"), ("1840", "Steel Grey", "#7a7e82"),
    ("1841", "Charcoal", "#494c50"), ("1918", "Anthracite", "#2d3034"), ("1800", "Emerald Black", "#111214"),
    ("1924", "Lemon Tart", "#fff042"), ("1825", "Canary Yellow", "#ffda00"), ("1980", "Sunflower", "#ffc000"),
    ("1824", "Golden Rod", "#ea9e15"), ("1972", "Amber Gold", "#cc8218"), ("1955", "Mandarin", "#ff9e3d"),
    ("1865", "Bright Orange", "#ff6d00"), ("1965", "Flame Orange", "#e04c19"), ("1839", "Coral Peach", "#ff8e7a"),
    ("1838", "Tangerine Red", "#f2483b"), ("1837", "Scarlet Red", "#e31e24"), ("1838", "Fire Engine Red", "#cc111b"),
    ("1981", "Crimson Red", "#a80f1d"), ("1835", "Burgundy Wine", "#781122"), ("1985", "Dark Maroon", "#540e1c"),
    ("1815", "Baby Pink", "#f8b8cb"), ("1990", "Hot Pink", "#ef5293"), ("1810", "Magenta Rose", "#c91c76"),
    ("1991", "Deep Fuchsia", "#9b1267"), ("1921", "Lavender", "#c6a6db"), ("1832", "Royal Purple", "#844eb0"),
    ("1922", "Deep Violet", "#572886"), ("1834", "Plum Aubergine", "#3a184c"), ("1874", "Sky Blue", "#aed5ef"),
    ("1875", "Cornflower Blue", "#63aee4"), ("1842", "Azure Blue", "#1c85d4"), ("1934", "Royal Blue", "#1648ad"),
    ("1843", "Cobalt Blue", "#113987"), ("1943", "Navy Blue", "#15254f"), ("1844", "Midnight Navy", "#0d162e"),
    ("1890", "Turquoise", "#22bfc4"), ("1892", "Teal Petrol", "#0e7680"), ("1989", "Aqua Mint", "#7cdcd4"),
    ("1849", "Soft Mint", "#a3e0b2"), ("1950", "Lime Green", "#77cb4a"), ("1850", "Kelly Green", "#3aa036"),
    ("1851", "Emerald Green", "#19853b"), ("1970", "Forest Green", "#106943"), ("1853", "Hunter Green", "#15402a"),
    ("1904", "Olive Drab", "#687628"), ("1956", "Desert Sand", "#d5be94"), ("1855", "Camel Tan", "#c29e68"),
    ("1856", "Cinnamon Brown", "#9e6b38"), ("1858", "Chestnut Brown", "#744520"), ("1859", "Espresso", "#482914"),
]

# 2. Isacord Polyester No. 40 (Amann Group — Offizielle 4-stellige Farbnummern)
_ISACORD_40 = [
    ("0010", "Silky White", "#ffffff"), ("0015", "White", "#f9f8f4"), ("0017", "Paper White", "#f0e8d0"),
    ("0142", "Sterling Grey", "#cccccc"), ("0108", "Cobblestone", "#a2a5a8"), ("0111", "Whale Grey", "#787a7d"),
    ("0131", "Smoke", "#4b4d50"), ("0132", "Gunmetal", "#2e3033"), ("0020", "Black", "#101113"),
    ("0600", "Citrus", "#fff238"), ("0501", "Lemon Drop", "#ffd800"), ("0605", "Daisy", "#ffbe00"),
    ("0702", "Papaya", "#e89f16"), ("0822", "Nugget Gold", "#c68419"), ("0904", "Melon", "#ffa444"),
    ("1102", "Pumpkin", "#ff7200"), ("1300", "Tangerine", "#e2501a"), ("1521", "French Rose", "#ff9484"),
    ("1701", "Poppy Red", "#ee362e"), ("1902", "Poinsettia", "#d4141d"), ("1904", "Cardinal", "#b20f1e"),
    ("2101", "Country Red", "#801022"), ("2222", "Burgundy", "#580e1d"), ("2320", "Raspberry", "#c61b74"),
    ("2520", "Garden Rose", "#f25898"), ("2550", "Soft Pink", "#f8b8cb"), ("2920", "Purple", "#8854b2"),
    ("3040", "Pansy Violet", "#5a2b88"), ("3333", "Deep Navy", "#14234c"), ("3543", "Royal Blue", "#1747a9"),
    ("3622", "Imperial Blue", "#1d86d4"), ("3732", "Sky Blue", "#6ab0e5"), ("3910", "Crystal Blue", "#b2d6f0"),
    ("4103", "Tropical Teal", "#24c0c5"), ("4421", "Ocean Petrol", "#0e7882"), ("5101", "Bright Mint", "#7eddd5"),
    ("5422", "Swiss Green", "#1b883d"), ("5510", "Emerald", "#3ca138"), ("5613", "Lime", "#78cd4c"),
    ("5833", "Jalapeno", "#15422b"), ("5934", "Moss Olive", "#697829"), ("0761", "Oatmeal", "#d8c198"),
    ("0941", "Golden Tan", "#c5a46e"), ("1055", "Bark Brown", "#a16e3b"), ("1115", "Chestnut", "#774822"),
    ("1346", "Cinnamon", "#4c2b16"), ("1874", "Espresso Dark", "#311e0e"),
]

# 3. Gunold POLY 40 (Offizielle 5-stellige 6xxxx Nummern)
_GUNOLD_POLY_40 = [
    ("61001", "Snow White", "#ffffff"), ("61003", "Ecru", "#f3ece0"), ("61005", "Champagne", "#ece0b6"),
    ("61214", "Light Grey", "#c6c8ca"), ("61216", "Medium Grey", "#9ea1a4"), ("61218", "Slate Grey", "#76787a"),
    ("61189", "Anthracite", "#46484b"), ("61002", "Jet Black", "#111112"), ("61062", "Lemon", "#fff036"),
    ("61066", "Sun Yellow", "#ffd200"), ("61023", "Corn Gold", "#e8a116"), ("61147", "Bright Orange", "#ff7600"),
    ("61134", "Flame Red", "#e04e18"), ("61142", "Signal Red", "#d2131c"), ("61036", "Cherry Red", "#b00f1d"),
    ("61046", "Bordeaux", "#761020"), ("61115", "Rose Pink", "#f6b4c6"), ("61120", "Magenta", "#ca1d78"),
    ("61296", "Violet", "#5c2c8a"), ("61108", "Ice Blue", "#b0d4ee"), ("61082", "Azure", "#1e88d5"),
    ("61085", "Royal Blue", "#1846a8"), ("61042", "Dark Navy", "#13234b"), ("61270", "Turquoise", "#26c2c7"),
    ("61174", "Apple Green", "#7ace4e"), ("61051", "Grass Green", "#3ea239"), ("61169", "Emerald", "#1a883c"),
    ("61057", "Bottle Green", "#15422b"), ("61195", "Sand Beige", "#d6bf96"), ("61202", "Cognac", "#a26f3b"),
    ("61039", "Chocolate", "#4d2c16"), ("61199", "Dark Mocha", "#321f0f"),
]

# 4. Brother Embroidery (PR-Serie & Innov-is Nummern)
_BROTHER = [
    ("001", "White", "#ffffff"), ("010", "Cream Brown", "#f2ead8"), ("005", "Silver", "#c4c6c8"),
    ("707", "Dark Grey", "#56585b"), ("900", "Black", "#111111"), ("202", "Lemon Yellow", "#fff138"),
    ("205", "Yellow", "#ffd400"), ("206", "Harvest Gold", "#e69f16"), ("208", "Orange", "#ff7800"),
    ("800", "Red", "#d4141c"), ("807", "Carmine", "#aa101d"), ("107", "Dark Fuchsia", "#781021"),
    ("085", "Pink", "#f7b4c7"), ("620", "Magenta", "#cb1e78"), ("614", "Purple", "#5e2d8c"),
    ("403", "Light Blue", "#6db2e5"), ("405", "Blue", "#1846a8"), ("419", "Peacock Blue", "#25c1c6"),
    ("406", "Navy Blue", "#14244d"), ("502", "Mint Green", "#7ccf4f"), ("513", "Lime Green", "#3fa33a"),
    ("507", "Emerald Green", "#1c8a3e"), ("509", "Moss Green", "#16432c"), ("339", "Clay Brown", "#a5713d"),
    ("323", "Light Brown", "#7a4a24"), ("330", "Russet Brown", "#4e2d17"),
]


def _srgb_to_lab(c):
    def lin(v):
        v /= 255.0
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92
    r, g, b = (lin(float(x)) for x in c)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(c1, c2) -> float:
    a, b = _srgb_to_lab(c1), _srgb_to_lab(c2)
    return math.dist(a, b)


class Palette:
    def __init__(self, name: str, brand: str, threads: list[Thread]):
        self.name = name
        self.brand = brand
        self.threads = threads
        self._lab = [_srgb_to_lab(t.color) for t in threads]

    def nearest(self, rgb) -> Thread:
        lab = _srgb_to_lab(rgb)
        i = min(range(len(self.threads)), key=lambda k: math.dist(lab, self._lab[k]))
        t = self.threads[i]
        return Thread(t.color, t.name, t.code, t.brand)

    @staticmethod
    def from_csv(path: str) -> "Palette":
        threads = []
        brand = os.path.splitext(os.path.basename(path))[0]
        with open(path, newline="", encoding="utf-8-sig") as f:
            sample = f.read(2048)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
            for row in csv.reader(f, dialect):
                if len(row) < 3 or not row[2].strip().startswith("#"):
                    continue
                threads.append(Thread.from_hex(row[2].strip(), row[1].strip(), row[0].strip(), brand))
        return Palette(brand, brand, threads)


GENERIC = Palette(
    "OpenStitch Universal",
    "Universal",
    [Thread.from_hex(h, n, c, "Universal") for c, n, h in _GENERIC],
)
MADEIRA_POLYNEON = Palette(
    "Madeira Polyneon No. 40",
    "Madeira Polyneon 40",
    [Thread.from_hex(h, n, c, "Madeira 40") for c, n, h in _MADEIRA_POLYNEON_40],
)
ISACORD_40 = Palette(
    "Isacord Polyester No. 40",
    "Isacord 40",
    [Thread.from_hex(h, n, c, "Isacord 40") for c, n, h in _ISACORD_40],
)
GUNOLD_POLY = Palette(
    "Gunold POLY 40",
    "Gunold 40",
    [Thread.from_hex(h, n, c, "Gunold 40") for c, n, h in _GUNOLD_POLY_40],
)
BROTHER_EMB = Palette(
    "Brother Embroidery / PR",
    "Brother",
    [Thread.from_hex(h, n, c, "Brother") for c, n, h in _BROTHER],
)

CATALOG_PALETTES: list[Palette] = [
    MADEIRA_POLYNEON,
    ISACORD_40,
    GUNOLD_POLY,
    BROTHER_EMB,
    GENERIC,
]

_active = [MADEIRA_POLYNEON]


def set_active_palette(p: Palette):
    _active[0] = p


def active_palette() -> Palette:
    return _active[0]


def nearest_thread(rgb) -> Thread:
    return _active[0].nearest(rgb)
