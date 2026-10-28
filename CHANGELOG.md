# Changelog

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
