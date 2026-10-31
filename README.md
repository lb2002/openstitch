# 🪡 OpenStitch Studio

🌐 **Language / Sprache:** **English** · [Deutsch](./README.de.md) · [Français](./README.fr.md) · [Español](./README.es.md)

**Universal Open-Source Embroidery & Digitizing Suite for Windows, macOS & Linux**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-2ea44f.svg)](#-quickstart--installation)
[![PRs Welcome](https://img.shields.io/badge/PRs%20%26%20Feedback-welcome-brightgreen.svg)](./CONTRIBUTING.md)

**OpenStitch Studio** is a modern, open-source embroidery digitizing suite with an eye-friendly **dark studio interface**, real-time 3D thread preview, a smart **Auto-Digitizer**, **PhotoStitch**, real **thread catalogs** (Madeira, Isacord, Gunold, Brother) and a **UI in 4 languages** (English, Deutsch, Français, Español). It supports all common home and industrial embroidery machines (**Tajima, Brother, Barudan, Ricoma, ZSK, Janome, Bernina, Pfaff/Husqvarna, Melco**).

> 💬 **Feedback & contributions welcome!**
> This project thrives on real-world feedback from many different embroidery machines and on community contributions. Found a bug, have an idea, or want to help build it? Open an [Issue](https://github.com/lb2002/openstitch/issues) or a [Pull Request](./CONTRIBUTING.md)!

![OpenStitch Studio — Dark Studio Interface](./assets/screenshot_studio.png)

<table><tr><td><img src="./assets/screenshot_start.png" alt="Start page"></td><td><img src="./assets/screenshot_check.png" alt="Design check with fabric preview"></td></tr></table>

<details>
<summary><b>🔍 Preview: interactive in-app studio tour (spotlight & coach marks)</b></summary>
<br>

![OpenStitch Studio — Interactive Onboarding Tour](./assets/screenshot_tour.png)

</details>

---

## ✨ Highlights & Features

### 1. 🪄 Smart Auto-Digitizer (image / logo → embroidery file)
* **Perceptual colour reduction in CIE-Lab** + automatic matching to real thread catalogs (**Madeira Polyneon 40, Isacord 40, Gunold Poly 40, Brother, Universal**).
* **Edge flood-fill background removal:** removes the background but keeps same-coloured inner details (e.g. white lettering in a logo).
* **Automatic stitch-type classification** via medial-axis skeleton & distance transform:
  * thin lines → **triple / bean run**
  * lettering & columns → **auto satin** with smoothly rotating stitch angle, short-stitching on tight inner curves, split satin for wide columns and automatic underlay
  * large areas → **tatami fill** or curved **contour fill** with boustrophedon region splitting, hidden travel routing along the outline, edge/lattice underlay and directional pull compensation
* **Hidden stitches are skipped:** fills do not stitch under objects that fully cover them, while a small overlap keeps gaps from opening.
* **Real fabric choice:** cotton, denim, cap, piqué, T-shirt, fleece, towel, leather, silk. It sets density and pull compensation, and tells you which stabilizer and needle to use.
* **Drag & drop:** drop images (`.png`, `.jpg`, `.webp`), `.svg` vectors or embroidery files straight onto the window.

### 2. 🎨 Manual digitizing, node editor & pro tools
* **Direct tools:** tatami (`F`), satin (`S`), running/bean stitch (`R`) and an interactive **node editor (`N`)**.
* **Parametric live inspector:** every object stays fully editable; scaling recalculates stitch density.
* **3D puff foam mode (caps):** dense satin (0.24 mm) with perforating pinch end-caps for 2–3 mm foam.
* **1-click appliqué:** placement line (with stop), tack-down and satin cover border.
* **PhotoStitch:** portrait/landscape photos → monochrome, sepia or 4-colour CMYK wave embroidery.
* **Satin columns along your drawn centre line** (`S`): stitches stay perpendicular to the line, with adjustable width, short stitches on tight curves, corner handling and automatic underlay (centre walk / edge walk / zigzag, chosen by column width).
* **OpenStitch Micro: small lettering from 2.5 mm.** A built-in single-stroke embroidery font, stitched like commercial small-text fonts. TrueType outlines fill in below ~4.5 mm; Micro stays readable:

  ![OpenStitch Micro vs. TrueType at 2.5 and 3 mm](./assets/micro_font_comparison.png)
* **SVG import** (transforms, arcs, styles, `<use>`, fill rules) & **TTF/OTF lettering** (arc text, automatic satin/tatami choice).

### 3. 🧪 Virtual stitch-out (`F7`)
* **Check design:** a score out of 100, findings in plain language, a **Show** button that jumps to the spot and a **Fix** button where one click solves it.
* **Fixed rules and estimates, clearly labelled:** stitch lengths, hoop limits, thread layers, lock stitches and the exported file follow exactly from the stitches. Only fabric pull is an estimate.
* **Fabric pull simulation:** see how thread tension pulls your chosen fabric in, and where outline and fill may no longer meet.
* **Calibration with real fabric:** stitch one small test bar, measure its width and enter it. The simulation and pull compensation then use your measured value for that fabric.
* **Machine rules:** stitches too short or too long, loose floats, missing lock stitches, needle pile-ups, too many thread layers, hoop collisions.
* **Export check:** files are read back with an independent parser and compared stitch by stitch.
* **Command line:** `python -m openstitch.analysis design.dst --fabric jersey --formats`

### 4. 🌍 Languages & real thread catalogs
* **UI languages:** 🇬🇧 English · 🇩🇪 Deutsch · 🇫🇷 Français · 🇪🇸 Español · 🇮🇹 Italiano · 🇵🇹 Português · 🇳🇱 Nederlands · 🇵🇱 Polski · 🇹🇷 Türkçe — the app starts in your system language; switch any time at the bottom right.
* **Thread catalogs with official colour numbers:** Madeira Polyneon No. 40, Isacord Polyester No. 40, Gunold POLY 40, Brother Embroidery and a universal palette; custom CSV palettes can be loaded too.

### 5. 🏭 Manufacturer-neutral & all major machine formats
* **Built-in machine profiles & hoop strategies:** Universal (`.DST` / `.PES` / `.EXP`), **Tajima** (`.DST`), **Brother** (`.PES` / `.PEC`), **Barudan** (`.U01` / `.DST`), **Ricoma / HappyJapan / ZSK** (`.DST`), **Janome / Elna / Bernina** (`.JEF` / `.EXP`), **Pfaff / Husqvarna Viking** (`.VP3`), **Melco** (native `.EXP`, built-in 1.44 MB FAT12 `.IMG` GoTek/FlashFloppy manager and an optional Raspberry Pi Wi-Fi bridge in `melco_netbridge/`).
* **Smart hoop strategies:** underlay, pull compensation and stitch order adapt to small hoops, standard hoops, jacket backs and curved cap frames (*centre-out & bottom-up*).
* **A4 PDF production sheet:** needle assignment, thread usage, stitch count and runtime estimate.

---

## 🔬 How it is tested

Nothing here has been proven on every real machine yet, so the project tests as much as it can without one:

* **Virtual stitch-out:** machine rules, fabric pull and coverage on a set of 34 test designs (`python -m openstitch.analysis --corpus --formats`).
* **Export round trip:** every machine format is written, re-read by an independent parser and compared stitch by stitch.
* **Random shape tests:** thousands of odd shapes must never crash the engine or put stitches outside the shape.
* **Damaged files:** broken embroidery, project, SVG and floppy files must fail cleanly.
* **Monkey test:** thousands of random clicks and keys on the real window.
* **Every setting must have an effect:** this found that satin density did nothing above about 0.4 mm.

Test stitch-outs on real machines are still the most useful contribution you can make.

## 🚀 Quickstart & Installation

### Option A: 1-click download (no Python required)
Get the ready-made app from the **[GitHub release page (latest)](https://github.com/lb2002/openstitch/releases/latest)**:
* 🪟 **Windows (64-bit, single file):** [`OpenStitch-Studio-Windows-x64.exe`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-Windows-x64.exe) *(download & double-click, nothing to unpack)*
* 🍏 **macOS (Apple Silicon M1 / M2 / M3 / M4):** [`OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip)
* 🍎 **macOS (Intel x64):** [`OpenStitch-Studio-macOS-Intel-x64.zip`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-macOS-Intel-x64.zip)
* 🐧 **Linux (64-bit):** **[`OpenStitch-Studio-Linux-x64.tar.gz`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-Linux-x64.tar.gz)** *(unpack, then run `OpenStitch-Studio`)*

> 🍏 **Opening on a Mac:** OpenStitch is free and not signed with a paid Apple certificate, so macOS blocks it the first time. Move the app to *Applications*, try to open it once, then go to *System Settings → Privacy & Security* and click **Open Anyway**. If macOS says the app is damaged, run this once in Terminal:
> ```bash
> xattr -cr "/Applications/OpenStitch Studio.app"
> ```

### Option B: run from source (Windows, macOS & Linux)
Requires **Python 3.10+**.

```bash
git clone https://github.com/lb2002/openstitch.git
cd openstitch
python -m venv .venv
# Windows:  .venv\Scripts\pip install -e .   &&   .venv\Scripts\python.exe main.py
# macOS/Linux:
.venv/bin/pip install -e .
.venv/bin/python main.py
```

On first launch you are greeted by the official **OpenStitch emblem** in the hoop and an interactive **7-step in-app tour** (reopen any time with `F1`).

---

## 🗂️ Project layout

```text
openstitch/
├── openstitch/
│   ├── auto/          # CIE-Lab colour reduction, Auto-Digitizer, PhotoStitch & thread catalogs
│   ├── core/          # design model, stitch plan, hoop & machine profiles
│   ├── engine/        # geometry, tatami/contour fill, satin, 3D puff, appliqué, density guard
│   ├── io/            # DST, PES, EXP, JEF, VP3, U01 import/export, FAT12 generator, PDF report
│   ├── text/          # TTF/OTF vector lettering engine & arc text
│   ├── ui/            # Material 3 dark studio GUI, 3D canvas, dialogs & onboarding
│   └── i18n.py        # UI translations (EN / DE / FR / ES)
├── melco_netbridge/   # optional Wi-Fi USB-emulator server (e.g. Raspberry Pi Zero 2 W)
└── tests/             # automated pytest suite
```

---

## 🤝 Contributing & feedback

* 🌟 **Star the repo** if you like OpenStitch Studio!
* 🐛 **Bug reports & machine tests:** open a [GitHub Issue](https://github.com/lb2002/openstitch/issues) and tell us which machine you use.
* 🌐 **Translations:** add or improve a language in [`openstitch/i18n.py`](./openstitch/i18n.py).
* 🔧 **Pull requests:** see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📜 License & copyright

Copyright © 2026 **Linus Baumberger** ([@lb2002](https://github.com/lb2002)).

* **Open-source copyleft:** released under the **[GNU AGPL-3.0-or-later](./LICENSE)**. Anyone may use, study, improve and share the software for free; derivative works and network/cloud services must stay open under the same licence.
* **Commercial / dual licensing:** as original author and copyright holder, **Linus Baumberger (`@lb2002`)** reserves the right to additionally offer OpenStitch Studio under commercial / OEM licences. See [LICENSE](./LICENSE).
