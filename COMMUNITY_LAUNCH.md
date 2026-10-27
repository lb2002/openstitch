# Community Launch & Ankündigungs-Vorlagen für OpenStitch Studio v0.1.0

Hier sind fertige, auf die jeweiligen Plattformen abgestimmte Posts, mit denen du **OpenStitch Studio** heute direkt auf **Reddit (`r/MachineEmbroidery`, `r/opensource`)** und **Hacker News (`Show HN`)** vorstellen kannst.

---

## 1. Reddit: `r/MachineEmbroidery` (Englisch – grösste Stickmaschinen-Community)

**Title:**
> I built a free, open-source embroidery digitizing suite with 3D preview, Auto-Digitizer, 3D-Puff & native DST/PES/EXP/JEF/VP3/U01 support — OpenStitch Studio v0.1.0 (Windows & macOS)

**Body:**
```markdown
Hi everyone!

Like many of you, I was frustrated that embroidery digitizing software either costs $1,000–$3,000+ with hardware dongles or feels super dated and complex to learn.

So I started building **OpenStitch Studio** — a free, open-source, manufacturer-neutral embroidery & digitizing suite with a modern Dark Studio interface and real-time 3D thread rendering.

🔗 **GitHub Repository & Free Download (v0.1.0):** https://github.com/lb2002/openstitch  
📦 **1-Click Windows Portable Release (.zip):** https://github.com/lb2002/openstitch/releases/tag/v0.1.0

### What it can do right now (v0.1.0):
* **Smart Auto-Digitizer (Image/Logo → Stitches):**
  * CIE-Lab perceptual color quantization + automatic thread palette matching
  * Edge flood-fill background removal (keeps inner details like white text intact!)
  * Medial-axis skeleton & distance-transform stroke classification: automatically turns thin lines into Bean/Triple-Run, columns & lettering into auto-rotating **Satin columns** (with short-stitches on tight inner curves), and large areas into **Tatami** or **Contour Fill** with Boustrophedon region splitting and edge travel routing.
  * **Color-Trap vs. Smart Knockdown + 0.7 mm Overlap Lip:** Prevents bulletproof stacking under large shapes while eliminating fabric gaps between adjacent colors.
  * Fabric presets for Cotton/Twill, Piqué/Polo/Knit, Terry Cloth/Towel, Caps, and Lightweight fabrics.
* **Manual Digitizing & Parametric Inspector:**
  * Draw Tatami fills (`F`), Satin columns (`S`), Running/Bean stitches (`R`), and edit contour nodes & stitch angles directly on the canvas (`N`).
  * True parametric scaling (resizing recalculates stitch density automatically).
* **Pro Tools Built-In:**
  * **3D-Puff Foam Mode (for Caps):** High-density satin (0.24 mm) with perforated pinch end-caps that cleanly cut 2–3 mm foam.
  * **1-Click Appliqué Generator:** Automatically creates placement line (with stop), tack-down run, and satin cover border.
  * **PhotoStitch:** Turns portrait photos into Monochrome, Sepia, or 4-color CMYK wave embroidery.
  * **Quality & Machine Doctor (`F7`) + Live Stitch Density Heatmap (`Ctrl+H`):** Catches needle/hoop collisions, density hotspots, and micro-stitches before you stitch.
* **Universal Machine Support & Binary Verification:**
  * Built-in profiles & hoop strategies (including Cap Center-Out / Bottom-Up and Jacket Back anti-trampoline underlay) for **Tajima (`.DST`), Brother (`.PES`/`.PEC`), Barudan (`.U01`), Ricoma/Happy/ZSK (`.DST`), Janome/Bernina (`.JEF`/`.EXP`), Pfaff/Husqvarna (`.VP3`), and Melco (`.EXP` + built-in 1.44 MB FAT12 `.IMG` GoTek floppy manager)**.
  * Includes an interactive **7-step in-app onboarding tour** on first launch.

### Looking for your feedback!
This is `v0.1.0` and I would love your feedback, bug reports, and test results on your specific embroidery machines! What features or hoop sizes are you missing most?

Links:
* GitHub: https://github.com/lb2002/openstitch
* Windows Portable Download: https://github.com/lb2002/openstitch/releases/tag/v0.1.0
```

---

## 2. Hacker News (`Show HN` auf news.ycombinator.com/submit)

**Title:**
> Show HN: OpenStitch Studio – Open-source embroidery digitizing CAD/CAM in Python

**URL:**
> https://github.com/lb2002/openstitch

**First Comment (Text):**
```text
Hi HN! I built OpenStitch Studio, an open-source (AGPLv3) CAD/CAM digitizing suite for घरेलू (home) and industrial multi-needle embroidery machines (Tajima, Brother, Barudan, ZSK, Janome, Melco, etc.).

Industrial embroidery software has historically been locked behind $2,000+ dongles and legacy Windows UIs. Stitching is actually a fascinating computational geometry and kinematics problem:
- If two needle penetrations are < 0.45 mm apart, a 75/11 needle (0.75 mm diameter) shreds the thread or causes birdnesting.
- Fabric stretches anisotropically under thread tension ("pull effect"), requiring directional pull compensation perpendicular to the stitch angle and Boustrophedon underlay lattices.
- Narrow shapes (< 6.5 mm) need satin columns where the stitch angle rotates continuously along the medial axis skeleton, with short-stitching on tight inner curves so the thread doesn't pile up.

Under the hood, OpenStitch uses Shapely 2.0, SciPy (Euclidean distance transforms & medial axis skeletons), scikit-image (CIE-Lab color quantization), and PySide6 with a cached 3D thread renderer and an independent binary verifier for .DST, .PES, .EXP, .JEF, .VP3, and .U01 files. It even includes a pure-Python FAT12 1.44 MB floppy image generator for older industrial machines using GoTek USB emulators, plus a Raspberry Pi Zero W Wi-Fi USB gadget bridge.

I'd love any feedback on the computational geometry pipeline, UI, or from anyone here who runs embroidery machines!
```

---

## 3. Deutschsprachige Foren / Maker-Communities / LinkedIn

**Titel:**
> OpenStitch Studio v0.1.0 — Freie Open-Source Stick- & Digitalisiersoftware (Windows & macOS)

**Text:**
```markdown
Hallo zusammen! 👋

Ich habe heute **OpenStitch Studio v0.1.0** als Open-Source-Projekt auf GitHub veröffentlicht: eine moderne, herstellerneutrale Stick- und Digitalisiersoftware für Windows und macOS!

🔗 **GitHub & Kostenloser Download:** https://github.com/lb2002/openstitch  
📦 **Direkt-Download für Windows (.exe im .zip, ohne Installation):** https://github.com/lb2002/openstitch/releases/tag/v0.1.0

**Was steckt drin?**
- 🪄 **Auto-Digitizer:** Wandelt Logos und Grafiken per CIE-Lab-Farberkennung und Skelett-Analyse automatisch in Satin-Säulen, Tatami-Füllungen (inkl. Kontur-Füllstich) und Dreifachstiche um – mit automatischer Zugkompensation, Unterlage und Hintergrund-Entfernung.
- 🎨 **Manuelles Digitalisieren & Knoten-Editor:** Flächen, Satin-Säulen, Steppstiche, Schriften (TTF/OTF inkl. Bogentext), **3D-Puff-Cap-Modus**, **1-Klick-Applikationen (Appliqué)** und **PhotoStitch**.
- 🩺 **Qualitäts-Doktor & Live-Heatmap:** Prüft vor dem Export automatisch auf Fadenbruch-Gefahren, Dichtespitzen und Rahmenkollisionen.
- 🏭 **Alle wichtigen Maschinenformate:** Unterstützt Tajima (`.DST`), Brother (`.PES`), Barudan (`.U01`), Ricoma/ZSK, Janome/Bernina (`.JEF`/`.EXP`), Pfaff/Husqvarna (`.VP3`) und Melco (inkl. GoTek FAT12 `.IMG`-Generator).

Ich freue mich riesig über jedes Feedback, Tests an euren Stickmaschinen, Ideen und Mitarbeit auf GitHub!
```
