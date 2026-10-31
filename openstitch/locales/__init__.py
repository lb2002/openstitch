"""Weitere Sprachen, je eine Datei mit `TABLE: dict[str, str]` (Schlüssel wie in i18n._TABLE).

Bewusst feste Importe: So erkennt PyInstaller die Dateien und packt sie in die fertigen Programme."""
from . import it, nl, pl, pt, tr

TABLES: dict[str, dict[str, str]] = {"it": it.TABLE, "nl": nl.TABLE, "pl": pl.TABLE, "pt": pt.TABLE, "tr": tr.TABLE}
