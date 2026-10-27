# Contributing to OpenStitch Studio

Vielen Dank für dein Interesse, an **OpenStitch Studio** mitzuarbeiten! Every contribution — whether bug reports, embroidery machine tests, algorithm improvements, UI polish, or translations — is highly welcome.

---

## 1. Wie du beitragen kannst (Ways to Contribute)

1. **Maschinen-Feedback & Praxistests:**
   Teste exportierte Stickdateien (`.DST`, `.PES`, `.EXP`, `.JEF`, `.VP3`, `.U01`) auf deiner Maschine (Tajima, Brother, Barudan, Ricoma, ZSK, Janome, Bernina, Melco u. a.) und teile deine Erfahrungen in den GitHub Issues / Discussions.
2. **Neue Features & Stich-Algorithmen:**
   - Verbesserungen an Auto-Digitizer, Satin-Säulen, Tatami-Füllungen, Unterlagen oder PhotoStitch.
   - Neue Schriftarten, Rahmenprofile oder Garn-Farbkarten (Madeira, Isacord, Gunold, Brother).
3. **Bugfixes & UI-Verbesserungen:**
   - Öffne einen Pull Request mit einer kurzen Beschreibung und führe vorab `pytest` aus.

---

## 2. Lokales Entwickler-Setup

```bash
git clone https://github.com/lb2002/openstitch.git
cd openstitch
python -m venv .venv
# Windows:
.venv\Scripts\pip install -e .
.venv\Scripts\pip install pytest
# macOS / Linux:
.venv/bin/pip install -e .
.venv/bin/pip install pytest
```

Tests ausführen:
```bash
pytest -q
```

---

## 3. Contributor License Agreement (CLA) & Lizenzierung

**OpenStitch Studio** steht unter der **GNU Affero General Public License v3.0 (AGPL-3.0-or-later)**, damit die Community-Version dauerhaft frei und quelloffen bleibt und niemand das Projekt als proprietären Closed-Source-Klon verkaufen kann.

Mit dem Einreichen eines Pull Requests oder Beitrags (Contribution) erklärst du dich mit folgenden Bedingungen einverstanden:

1. Du bestätigst, dass du der Urheber deines Beitrags bist und das Recht hast, ihn einzureichen.
2. Du räumst dem Projektgründer und Haupturheber **Linus Baumberger (`@lb2002`)** ein unwiderrufliches, weltweites, gebührenfreies, nicht-exklusives und unterlizenzierbares Recht ein, deinen Beitrag zusammen mit OpenStitch Studio sowohl unter der **GNU AGPL-3.0-or-later** als auch unter beliebigen anderen (einschließlich kommerziellen / proprietären Dual-Licensing-) Lizenzen zu nutzen, zu verändern und zu verbreiten.
3. Du behältst selbstverständlich das Urheberrecht an deinem eigenen Beitrag.
