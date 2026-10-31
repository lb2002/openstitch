# 🪡 OpenStitch Studio

🌐 **Sprache / Language:** [English](./README.md) · **Deutsch** · [Français](./README.fr.md) · [Español](./README.es.md)

**Universal Open-Source Embroidery & Digitizing Suite for Windows, macOS & Linux**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-2ea44f.svg)](#quickstart--installation)
[![PRs Welcome](https://img.shields.io/badge/PRs%20%26%20Feedback-welcome-brightgreen.svg)](./CONTRIBUTING.md)

**OpenStitch Studio** ist eine moderne, quelloffene Stick- und Digitalisiersoftware (Digitizing Suite) mit einem augenschonenden **Dark-Studio-Interface**, Echtzeit-3D-Seidenglanz-Vorschau, intelligentem **Auto-Digitizer**, **PhotoStitch** und nativer Unterstützung für alle gängigen Haushalts- und Industrie-Stickmaschinen (**Tajima, Brother, Barudan, Ricoma, ZSK, Janome, Bernina, Pfaff/Husqvarna, Melco**).

> 💬 **Feedback & Mitarbeit erwünscht!**  
> Dieses Projekt lebt von echtem Praxis-Feedback an verschiedensten Stickmaschinen und von Community-Beiträgen. Wenn du Ideen, Wünsche oder Bugs findest oder selbst mitentwickeln möchtest: Erstelle gerne ein [Issue](https://github.com/lb2002/openstitch/issues) oder einen [Pull Request](./CONTRIBUTING.md)!

![OpenStitch Studio — Dark Studio Interface](./assets/screenshot_studio.png)

<details>
<summary><b>🔍 Vorschau: Interaktiver In-App Studio-Rundgang (Spotlight & Coach-Marks)</b></summary>
<br>

![OpenStitch Studio — Interactive Onboarding Tour](./assets/screenshot_tour.png)

</details>

---

## ✨ Highlights & Features

### 1. 🪄 Intelligenter Auto-Digitizer (Bild / Logo → Stickdatei)
* **Wahrnehmungstreue Farbreduktion im CIE-Lab-Farbraum** + automatisches Matching auf echte Stickgarn-Paletten (Madeira / Isacord / Universal).
* **Rand-Flood-Fill Hintergrund-Erkennung:** Entfernt den Bildhintergrund automatisch, lässt aber gleichfarbige Innendetails (z. B. weiße Schrift im Logo) unangetastet.
* **Automatische Stichart-Klassifikation per Medial-Axis-Skelett & Distanztransformation:**
  * Feine Konturen → **Dreifach-/Beanstich**
  * Schriften & Säulen → **Auto-Satinstich** mit fließend mitdrehendem Stichwinkel, Kurzstichen (Short-Stitches) in engen Innenkurven, Split-Satin bei breiten Säulen und automatischer Unterlage
  * Große Flächen → **Tatami-Füllstich** oder **gebogener Kontur-Füllstich (Contour Fill)** mit Boustrophedon-Abschnittszerlegung, unsichtbarem Travel-Routing entlang der Außenkante, Kanten-/Gitter-Unterlage und richtungsabhängiger Zugkompensation (Pull Compensation)
* **Verdecktes wird nicht gestickt:** Füllungen laufen nicht unter Objekten weiter, die sie ganz zudecken. Eine kleine Überlappung verhindert Lücken.
* **Stoffprofile:** Standard (Baumwolle/Twill), Piqué/Polo/Strick, Frottee/Handtuch, Kappe/Cap, Leichter Stoff.
* **Drag & Drop:** Ziehe Bilder (`.png`, `.jpg`, `.webp`), `.svg`-Vektorgrafiken oder Stickdateien direkt aus dem Explorer/Finder ins Programmfenster.

### 2. 🎨 Manuelles Digitalisieren, Knoten-Editor & Pro-Werkzeuge
* **Direkt-Werkzeuge:** Tatami-Fläche (`F`), Satin-Säule (`S`), Lauf-/Dreifachstich (`R`) und **Interaktiver Knoten-Editor (`N`)** direkt auf der Leinwand.
* **Parametrischer Live-Inspektor:** Jedes Objekt bleibt vollständig editierbar (Reihenabstand, Stichlänge, Winkel, Kontur-Füllung, Zugkompensation, Unterlage, Ein-/Ausstich-Einkürzung). Beim Skalieren wird die Stichdichte automatisch neu berechnet.
* **3D-Puff-Schaumstoff-Modus (für Caps):** Erzeugt hochdichte Satin-Säulen (0.24 mm) mit speziell perforierenden **Pinch-End-Caps** zum sauberen Durchtrennen von 2–3 mm 3D-Stick-Schaumstoff.
* **1-Klick Applikation (Appliqué):** Erzeugt automatisch Platzierungslinie (mit Maschinen-Stopp), Stoff-Fixiernaht (Tack-Down) und breite Satin-Deckkante.
* **PhotoStitch:** Verwandelt Porträt- und Landschaftsfotos in Monochrom-, Sepia- oder 4-Farb-CMYK-Wellenstickerei.
* **Satinsäulen entlang der gezeichneten Mittellinie** (`S`): Stiche stehen senkrecht zur Linie, mit einstellbarer Breite, Kurzstich in engen Kurven, Eckenbehandlung und automatischer Unterlage (Mittellauf / Kantenlauf / Zickzack je nach Säulenbreite).
* **OpenStitch Micro – kleine Schrift ab 2.5 mm:** Eingebaute Einlinien-Stickschrift, gestickt wie die Kleinschriften kommerzieller Programme. TrueType-Umrisse laufen unter ~4.5 mm zu, Micro bleibt lesbar:

  ![OpenStitch Micro vs. TrueType bei 2.5 und 3 mm](./assets/micro_font_comparison.png)
* **SVG-Vektor-Import** (Transformationen, Bögen, Stile, `<use>`, Füllregeln) & **TTF/OTF-Schrift-Generator** (inkl. Bogentext & automatischer Satin/Tatami-Wahl).

### 3. 🧪 Virtueller Probestick (`F7`)
* **Design prüfen:** Punktzahl bis 100, Befunde in Klartext, **Zeigen** springt zur Stelle, **Beheben** löst es mit einem Klick, wo das möglich ist.
* **Stoffzug-Simulation:** zeigt, wie der Faden den gewählten Stoff zusammenzieht und wo Kontur und Füllung auseinanderlaufen können. Das ist ein Modell mit Erfahrungswerten und ersetzt keinen echten Probestick.
* **Maschinenregeln:** zu kurze und zu lange Stiche, lose Flottungen, fehlende Vernähstiche, Nadelhäufungen, zu viele Fadenlagen, Rahmenkollision.
* **Export-Prüfung:** Dateien werden mit einem unabhängigen Parser neu eingelesen und Stich für Stich verglichen.
* **Kommandozeile:** `python -m openstitch.analysis design.dst --fabric jersey --formats`

### 4. 🏭 Herstellerneutral & Alle wichtigen Maschinenformate
* **Integrierte Maschinenprofile & Rahmen-Strategien:**
  * Universal Standard (`.DST` / `.PES` / `.EXP`)
  * **Tajima** (TME / TMF / TMFD / TMBP — `.DST`)
  * **Brother** (PR-Serie Mehrnadel & Innov-is Haushalt — `.PES` / `.PEC`)
  * **Barudan** (BEMR / BEXY / BEKT — `.U01` / `.DST`)
  * **Ricoma / HappyJapan / ZSK** (`.DST`)
  * **Janome / Elna / Bernina** (`.JEF` / `.EXP`)
  * **Pfaff / Husqvarna Viking** (`.VP3`)
  * **Melco** (EMT10/4, Amaya, Bravo — nativer `.EXP`-Generator + eingebauter 1.44 MB FAT12 `.IMG` GoTek/FlashFloppy-Diskettenmanager & optionales Raspberry-Pi WLAN-NetBridge-Modul in `melco_netbridge/`).
* **Intelligente Rahmen-Strategien:** Passt Unterlage, Zugkompensation und Stickreihenfolge automatisch an kleine Hemdrahmen, Standardrahmen, Jackenrücken oder gebogene Kappenrahmen (*Center-Out & Bottom-Up*) an.
* **A4-PDF-Produktionsblatt:** Exportiert ein druckfertiges Produktions- & Einrichteblatt mit Nadelbelegung, Garnverbrauch, Stichzahl und Laufzeitschätzung.

---

## 🚀 Quickstart & Installation

### Option A: 1-Klick Direkt-Download (ohne Python-Installation!)
Lade dir auf der **[GitHub Release-Seite (latest)](https://github.com/lb2002/openstitch/releases/latest)** direkt die fertige Anwendung für dein System herunter:
* 🪟 **Windows (64-Bit Einzeldatei):** **[`OpenStitch-Studio-Windows-x64.exe`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-Windows-x64.exe)** *(einfach herunterladen & doppelklicken, kein Entpacken nötig!)*
* 🍏 **macOS (Apple Silicon M1 / M2 / M3 / M4):** **[`OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip)** *(`OpenStitch Studio.app`)*
* 🍎 **macOS (Intel x64):** **[`OpenStitch-Studio-macOS-Intel-x64.zip`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-macOS-Intel-x64.zip)** *(`OpenStitch Studio.app`)*
* 🐧 **Linux (64-Bit):** **[`OpenStitch-Studio-Linux-x64.tar.gz`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-Linux-x64.tar.gz)** *(entpacken, dann `OpenStitch-Studio` starten)*

---

### Option B: Aus dem Quellcode starten (Windows, macOS & Linux)
* Voraussetzung: **Python 3.10+**

### 1. Repository klonen & starten

#### Windows
Doppelklicke auf **`start_windows.bat`** (richtet beim ersten Start automatisch die virtuelle Umgebung `.venv` ein) — oder im Terminal:
```powershell
git clone https://github.com/lb2002/openstitch.git
cd openstitch
python -m venv .venv
.venv\Scripts\pip install -e .
.venv\Scripts\python.exe main.py
```

#### macOS / Linux
Doppelklicke auf **`start_macos.command`** (`chmod +x start_macos.command`) — oder im Terminal:
```bash
git clone https://github.com/lb2002/openstitch.git
cd openstitch
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python main.py
```

Beim ersten Start begrüßt dich **OpenStitch Studio** mit dem offiziellen **OpenStitch-Emblem** im Stickrahmen und einem interaktiven **7-Schritte In-App Studio-Rundgang** (jederzeit wieder aufrufbar über `Hilfe` → `Interaktiven Studio-Rundgang starten (F1)`).

---

## 🗂️ Projekt-Architektur

```text
openstitch/
├── openstitch/
│   ├── auto/          # CIE-Lab Farbreduktion, Auto-Digitizer, PhotoStitch & Garnpaletten
│   ├── core/          # Design-Datenmodell, Stichplan, Rahmenprofile & Maschinenprofile
│   ├── engine/        # Geometrie, Tatami/Contour-Fill, Satin-Säulen, 3D-Puff, Appliqué, Density-Guard
│   ├── io/            # Exporter/Importer (DST, PES, EXP, JEF, VP3, U01), FAT12-Generator, PDF-Report
│   ├── text/          # TTF/OTF Vektor-Schrift-Engine & Bogentext
│   └── ui/            # Google Material 3 Dark-Studio GUI, 3D-Canvas, Dialoge & In-App-Onboarding
├── melco_netbridge/   # Optionaler WLAN-USB-Emulator-Server (z. B. für Raspberry Pi Zero 2 W)
└── tests/             # Automatisierte Pytest-Testsuite
```

---

## 🤝 Mitmachen & Feedback (Contributing)

Wir freuen uns riesig über jedes Feedback aus der Stick- und Maker-Community:
* 🌟 **Gib dem Repo einen Star**, wenn dir OpenStitch Studio gefällt!
* 🐛 **Bug-Reports & Maschinen-Tests:** Öffne ein [GitHub Issue](https://github.com/lb2002/openstitch/issues) und schreib gern dazu, mit welcher Stickmaschine du arbeitest.
* 🔧 **Pull Requests:** Lies unsere [CONTRIBUTING.md](./CONTRIBUTING.md) für Details zum Setup und zur Beitragsvereinbarung.

---

## 📜 Lizenz & Urheberrecht (License)

Copyright © 2026 **Linus Baumberger** ([@lb2002](https://github.com/lb2002)).

* **Open-Source Copyleft Lizenz:** Dieses Projekt ist unter der **[GNU Affero General Public License v3.0 (AGPL-3.0-or-later)](./LICENSE)** veröffentlicht. Jeder darf die Software kostenlos nutzen, studieren, verbessern und teilen. Jegliche Weiterentwicklungen, abgeleitete Werke oder Netzwerk-/Cloud-Dienste müssen unter derselben Lizenz quelloffen bleiben – ein unbefugtes Verkaufen als geschlossene/proprietäre Software durch Dritte ist ausgeschlossen.
* **Kommerzielle / Dual-Lizenzierung:** Als ursprünglicher Erfinder und Urheberrechtsinhaber behält sich **Linus Baumberger (`@lb2002`)** das Recht vor, OpenStitch Studio (oder Teile davon) zusätzlich unter kommerziellen / OEM-Lizenzen anzubieten. Für kommerzielle Anfragen oder Partnerschaften siehe [LICENSE](./LICENSE).
