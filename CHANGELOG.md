# Changelog

## v0.4.0

### Virtual stitch-out
- **Check design (`F7`) replaces the old Doctor.** You get a score out of 100, findings in plain language, a Show button that jumps to the spot and a Fix button where a one-click fix exists.
- **Fabric pull simulation.** A spring model shows how thread tension pulls the fabric in, with a preview you can exaggerate. Earlier objects move when later ones are stitched, so it can warn about gaps between a fill and its outline. It is a model built on rules of thumb, not a replacement for a test stitch-out.
- **Export check.** Every machine format is written, read back with an independent parser and compared stitch by stitch.
- **Command line:** `python -m openstitch.analysis design.dst --fabric jersey --formats`.

### Stitch quality fixes found by the simulator
- **Satin density now works.** Spacing above about 0.4 mm had no effect, and needle holes along satin edges were uneven.
- Split satin no longer exceeds the maximum stitch length (it could by 17 %).
- The density guard can no longer turn repeated lines into 13 mm stitches, and it keeps lock stitches at run ends.
- Degenerate column lines can no longer throw stitches far off the shape.
- Hidden travel along a shape's edge no longer cuts across holes at the ring's start corner.
- **VP3 files with an accented thread name (such as Grün) were corrupted** and could not be read back. Thread names are now written in plain characters in all formats.
- Damaged project files give a clear message instead of crashing plan building.

### New
- **Real fabric choice** (cotton, denim, cap, piqué, T-shirt, fleece, towel, leather, silk). It sets pull compensation and density, and tells you which stabilizer and needle to use.
- **Hidden stitches are skipped.** A fill no longer stitches under a later object that fully covers it, which saves stitches and avoids board-stiff spots. It keeps running 1 mm under the edge so no gaps open, and thin objects such as lettering keep their fill.
- **Send to machine.** Picks the right format for your machine, finds USB sticks, offers short names for older machines, lists the thread order, verifies the saved file and never overwrites silently.
- **Micro font tuned with a legibility measure.** `l` and `I` now differ, `A`, `e`, `4` have more open counters and `a` is easier to tell from `o`. From 3 mm every counter stays open; at 2.5 mm `e` and `4` are tight.
- Fixed: the text dialog refused heights under 4 mm, so 2.5 mm lettering could only be set afterwards. It now has a live preview and suggests the Micro font for small text.

### Easier to use
- **Start page** with four clear ways in, sample designs and recent files.
- **The window fits a laptop.** It needed 2212 px of width and now fits 1280 px.
- **Light theme** next to the dark one, and a redesigned layout with a shorter toolbar.
- **One Open dialog** for projects, embroidery files, SVG and images.
- **Autosave with crash recovery**, and a crash report instead of a silent exit.
- **Five more languages:** Italian, Portuguese, Dutch, Polish and Turkish. These are machine translations, so corrections from native speakers are very welcome.
- The app starts in your system language, otherwise English. The tour is translated.
- Help menu: keyboard shortcuts, report a problem, about.
- Your machine choice is remembered.

### Project
- Random shape tests, damaged file tests and a monkey test that clicks through the real window. Long versions run weekly.
- Linux download in releases.

## v0.3.0 (2026-10-28)

### New
- **OpenStitch Micro: an embroidery font for small lettering from 2.5 mm.** Single-stroke glyphs are stitched as a triple run below 5.5 mm and as narrow satin columns above, the way commercial small-text fonts work. Outline fonts converted from TrueType fill in below about 4.5 mm. It covers A–Z, a–z, 0–9, punctuation and German/French/Spanish accents. Pick it in the text dialog; it is listed first.
- **Real satin columns.** The satin tool (`S`) now stitches exactly perpendicular to the line you draw, with adjustable width, density, pull compensation and underlay. Short stitches on tight curves and corner handling are built in. Previously the line was thickened to a fixed 3.2 mm polygon and its centre line re-guessed from pixels.

### Stitch quality fixes
- **No more stray stitches across the design.** After a trim inside one colour, the next run was split from the *old* needle position, which sewed stitches of up to 50 mm straight across finished areas. This affected every export with more than one run per colour.
- **Far fewer trims.** Underlay, the travel to the top-fill entry point, and satin end caps are now joined with running stitches hidden under the later stitching. A single fill or satin object needs 1 trim instead of 3.
- **Clean fill edges.** The density guard removed tatami row-turn points as "micro-stitches", which made fill outlines ragged. Turn points are now always kept.
- **JEF (Janome) export now cuts threads.** pyembroidery drops trims in JEF files by default; they are now written as three zero-length jumps (the Janome convention).
- **Satin underlay types**, chosen automatically by column width like commercial software: centre walk (≤ 2 mm), edge walk (≤ 4.5 mm), edge walk + zigzag (wider). Each style can be picked per object.

### Editor
- Stitch plans are built in a **background thread**, so editing stays responsive on large designs.
- The simulator draws only new stitches each frame (about 7× faster), and the heatmap is cached.
- Undo/redo keeps object identity and selection, so undo no longer regenerates the whole design. Dragging a spin box counts as one undo step, and show/hide can be undone.
- The inspector no longer loses your input while you type.
- Node editing no longer jumps between nodes, drops parts of multi-part shapes, or moves text to the origin.
- Fit-to-hoop and Scale keep text rotation and size.
- Hoop and machine selection follow the loaded design. Auto-digitize uses the current hoop and can be cancelled.
- Unsaved-changes prompt on New/Open/Import/Drop/Close. Project saves are atomic, and save/export errors are reported.

- **Colour sort that respects stacking:** "Optimise colour order" only moves an object to an earlier block of the same colour when nothing it skips overlaps it.
- **Round-hoop checks use the real stitch radius.** Bounding-box corners overestimated round designs by up to 41 %.

### SVG import (rewritten)
- `transform` on elements and groups (matrix, translate, scale, rotate, skew).
- Full path syntax, including arcs (`A`), smooth curves (`S`/`T`) and compact number notation.
- Style inheritance, `fill="none"`, gradients (first stop colour), the full CSS colour-name list, `display:none`.
- `<use>`/`<symbol>`, ellipse, line, rounded rect and polyline. `<defs>`, `<clipPath>` and `<mask>` content is no longer stitched.
- evenodd and nonzero fill rules. Strokes become a bean run (< 1.2 mm) or a satin outline (wider).
- Optional real-world size from width/height/viewBox. Protection against `<use>` expansion bombs.

### Melco floppy images (FAT12)
- Adding a file is transactional: if it fails, the image is left unchanged.
- Long names get Windows-style `~1` short names with VFAT long-name entries.
- Zero-byte files work, and corrupt or cyclic FAT chains are detected.
- The floppy dialog asks before replacing a file with the same 8.3 name.

### Languages
- All dialogs, message boxes, inspector parameters, hoop and machine names, the Quality Doctor and the PDF production sheet are now translated (DE/EN/FR/ES).
- Numbers use each language's own thousands separator.

### Project
- CI tests on Python 3.10 and 3.12.
