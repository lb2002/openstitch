"""Virtueller Probestick: prüft einen Stichplan, ohne eine Maschine zu benötigen.

- `checks`: Maschinen- und Nadelregeln (Kurzstiche, lange Flottungen, Vernähen, Nadelhäufung, Dichte)
- `pull`: Stoffverzug als Federgitter (Zug des Fadens, Passgenauigkeit zwischen Objekten)
- `coverage`: deckt der Faden die Fläche?
- `roundtrip`: Export → unabhängig wieder einlesen → Stich für Stich vergleichen
- `legibility`: bleibt Schrift bei kleiner Höhe lesbar?

Die Physik ist ein Modell mit Erfahrungswerten: Es zeigt verlässlich Trends und Problemstellen,
ersetzt aber keinen echten Probestick.
"""
from .fabric import DEFAULT_FABRIC, FABRICS, Fabric, fabric_by_id
from .report import Finding, Report, simulate_stitchout

__all__ = ["DEFAULT_FABRIC", "FABRICS", "Fabric", "Finding", "Report", "fabric_by_id", "simulate_stitchout"]
