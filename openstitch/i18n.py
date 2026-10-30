"""Mehrsprachige Lokalisierung (DE, EN, FR, ES) für OpenStitch Studio."""
from __future__ import annotations

from PySide6.QtCore import QSettings

LANGUAGES: list[tuple[str, str]] = [
    ("de", "🇩🇪 Deutsch"),
    ("en", "🇬🇧 English"),
    ("fr", "🇫🇷 Français"),
    ("es", "🇪🇸 Español"),
]

_cur_lang = ["de"]


def init_lang() -> str:
    s = QSettings("OpenStitch", "OpenStitchStudio")
    lang = s.value("ui/lang", "de", type=str)
    if lang not in ("de", "en", "fr", "es"):
        lang = "de"
    _cur_lang[0] = lang
    return lang


def current_lang() -> str:
    return _cur_lang[0]


def set_lang(lang: str) -> None:
    if lang in ("de", "en", "fr", "es"):
        _cur_lang[0] = lang
        s = QSettings("OpenStitch", "OpenStitchStudio")
        s.setValue("ui/lang", lang)


# Übersetzungstabelle: Schlüssel -> (DE, EN, FR, ES)
_TABLE: dict[str, tuple[str, str, str, str]] = {
    # Menüs
    "menu_file": ("&Datei", "&File", "&Fichier", "&Archivo"),
    "menu_edit": ("&Bearbeiten", "&Edit", "&Édition", "&Editar"),
    "menu_view": ("&Ansicht", "&View", "&Affichage", "&Ver"),
    "menu_create": ("&Digitalisieren", "&Digitize", "&Numériser", "&Digitalizar"),
    "menu_machine": ("&Maschine && Export", "&Machine && Export", "&Machine && Export", "&Máquina && Exportar"),
    "menu_help": ("&Hilfe", "&Help", "&Aide", "A&yuda"),

    # Obere Toolbar (Kurzlabels)
    "tb_new": ("Neu", "New", "Nouveau", "Nuevo"),
    "tb_import": ("Import", "Import", "Importer", "Importar"),
    "tb_svg": ("SVG", "SVG", "SVG", "SVG"),
    "tb_export": ("Export", "Export", "Exporter", "Exportar"),
    "tb_pdf": ("PDF", "PDF", "PDF", "PDF"),
    "tb_auto": ("Auto-Digitizer", "Auto-Digitizer", "Auto-Numériseur", "Auto-Digitalizador"),
    "tb_photo": ("PhotoStitch", "PhotoStitch", "PhotoStitch", "PhotoStitch"),
    "tb_text": ("Schrift", "Lettering", "Lettrage", "Texto"),
    "tb_applique": ("Appliqué", "Appliqué", "Appliqué", "Aplique"),
    "tb_puff": ("3D-Puff", "3D-Puff", "3D-Puff", "3D-Puff"),
    "tb_transfer": ("Transfer", "Transfer", "Transfert", "Transferir"),
    "tb_doctor": ("Doktor", "Doctor", "Docteur", "Doctor"),
    "tb_tour": ("Rundgang", "Tour", "Visite", "Guía"),

    # Kontextleiste über der Leinwand
    "lbl_machine": ("Maschine:", "Machine:", "Machine :", "Máquina:"),
    "lbl_hoop": ("Stickrahmen:", "Hoop:", "Cadre :", "Bastidor:"),
    "btn_autofit": ("Auto-Fit", "Auto-Fit", "Ajuster", "Auto-Ajuste"),
    "fabric_slate": ("Stoff: Dunkel", "Fabric: Dark", "Tissu : Sombre", "Tela: Oscura"),
    "fabric_sand": ("Stoff: Sand", "Fabric: Sand", "Tissu : Sable", "Tela: Arena"),
    "fabric_light": ("Stoff: Hell", "Fabric: Light", "Tissu : Clair", "Tela: Clara"),
    "lbl_strategy": ("Strategie", "Strategy", "Stratégie", "Estrategia"),

    # Linke Werkzeugleiste (Tool-Rail)
    "tool_select": ("Auswahl (V)", "Select (V)", "Sélection (V)", "Selección (V)"),
    "tool_nodes": ("Knoten (N)", "Nodes (N)", "Nœuds (N)", "Nodos (N)"),
    "tool_fill": ("Tatami (F)", "Tatami (F)", "Tatami (F)", "Tatami (F)"),
    "tool_satin": ("Satin (S)", "Satin (S)", "Satin (S)", "Satén (S)"),
    "tool_run": ("Stepp (R)", "Run (R)", "Point droit (R)", "Pespunte (R)"),
    "tool_heatmap": ("Heatmap", "Heatmap", "Carte densité", "Mapa calor"),
    "tool_zoom": ("Rahmen einpassen", "Fit to hoop", "Ajuster au cadre", "Ajustar al bastidor"),

    # HUD auf der Leinwand
    "hud_select": (
        "Auswahl (V)  ·  Ziehen = Verschieben, Eckgriff = Skalieren, Mausrad = Zoom",
        "Select (V)  ·  Drag = Move, Corner handle = Scale, Wheel = Zoom",
        "Sélection (V)  ·  Glisser = Déplacer, Coin = Redimensionner, Molette = Zoom",
        "Selección (V)  ·  Arrastrar = Mover, Esquina = Escalar, Rueda = Zoom",
    ),
    "hud_nodes": (
        "Knoten & Stichwinkel (N)  ·  Weisse Knoten = Kontur ändern, Gelber Griff = Stichwinkel drehen",
        "Nodes & Stitch Angle (N)  ·  White nodes = Edit contour, Yellow handle = Rotate stitch angle",
        "Nœuds & Angle (N)  ·  Nœuds blancs = Contour, Poignée jaune = Angle de point",
        "Nodos y Ángulo (N)  ·  Nodos blancos = Contorno, Control amarillo = Ángulo de puntada",
    ),
    "hud_fill": (
        "Tatami-Fläche zeichnen (F)  ·  Klick = Punkt setzen, Doppelklick/Enter = Fertig",
        "Draw Tatami Fill (F)  ·  Click = Add point, Double-click/Enter = Finish",
        "Dessiner Tatami (F)  ·  Clic = Point, Double-clic/Entrée = Terminer",
        "Dibujar Tatami (F)  ·  Clic = Punto, Doble clic/Enter = Terminar",
    ),
    "hud_satin": (
        "Satin-Säule zeichnen (S)  ·  Klick = Punkt setzen, Doppelklick/Enter = Fertig",
        "Draw Satin Column (S)  ·  Click = Add point, Double-click/Enter = Finish",
        "Dessiner Colonne Satin (S)  ·  Clic = Point, Double-clic/Entrée = Terminer",
        "Dibujar Columna Satén (S)  ·  Clic = Punto, Doble clic/Enter = Terminar",
    ),
    "hud_run": (
        "Steppstich-Pfad zeichnen (R)  ·  Klick = Punkt setzen, Doppelklick/Enter = Fertig",
        "Draw Running Stitch (R)  ·  Click = Add point, Double-click/Enter = Finish",
        "Dessiner Point Droit (R)  ·  Clic = Point, Double-clic/Entrée = Terminer",
        "Dibujar Pespunte (R)  ·  Clic = Punto, Doble clic/Enter = Terminar",
    ),

    # Linkes Dock (Garnkatalog & Farben)
    "dock_palette": ("Garnfarben && Nadel-Sequenz", "Thread Catalog && Needle Sequence", "Catalogue Fils && Aiguilles", "Catálogo Hilos && Agujas"),
    "lbl_catalog": ("Garnkatalog:", "Thread Catalog:", "Catalogue :", "Catálogo:"),
    "lbl_seq": ("Farb- & Nadel-Sequenz im Design:", "Design Thread & Needle Sequence:", "Séquence de couleurs & aiguilles :", "Secuencia de colores y agujas:"),
    "needle": ("Nadel", "Needle", "Aiguille", "Aguja"),

    # Rechtes Dock (Ebenen & Inspektor)
    "dock_right": ("Ebenen && Objekt-Inspektor", "Layers && Object Inspector", "Calques && Inspecteur d'Objets", "Capas && Inspector de Objetos"),
    "btn_visible": ("👁 Sichtbar", "👁 Visible", "👁 Visible", "👁 Visible"),
    "btn_copy": ("⧉ Kopie", "⧉ Copy", "⧉ Copier", "⧉ Copiar"),
    "lbl_inspector": ("Objekt-Parameter (Live-Neuberechnung):", "Object Parameters (Live Recalculation):", "Paramètres de l'objet (Calcul en direct) :", "Parámetros del objeto (Cálculo en vivo):"),
    "lbl_no_sel": (
        "Kein Objekt ausgewählt.\nKlicke ein Element auf der Leinwand oder in der Ebenenliste an.",
        "No object selected.\nClick an element on the canvas or in the layer list.",
        "Aucun objet sélectionné.\nCliquez sur un élément du canevas ou de la liste.",
        "Ningún objeto seleccionado.\nHaz clic en un elemento del lienzo o de la lista.",
    ),
    "lbl_obj_name": ("Bezeichnung", "Name", "Nom", "Nombre"),

    # Unten: Simulator & Statusleiste
    "dock_bottom": ("Stich-Simulator && Näh-Player", "Stitch Simulator && Stitch Player", "Simulateur de Broderie", "Simulador de Bordado"),
    "btn_play": ("▶ Simulation", "▶ Simulate", "▶ Simulation", "▶ Simular"),
    "btn_pause": ("⏸ Pause", "⏸ Pause", "⏸ Pause", "⏸ Pausa"),
    "btn_show_all": ("⏭ Alle zeigen", "⏭ Show All", "⏭ Tout afficher", "⏭ Mostrar todo"),
    "lbl_progress": ("  Fortschritt:", "  Progress:", "  Progression :", "  Progreso:"),
    "lbl_speed": ("Tempo:", "Speed:", "Vitesse :", "Velocidad:"),
    "stats_stitches": ("Stiche", "Stitches", "Points", "Puntadas"),
    "stats_size": ("Mass", "Size", "Taille", "Tamaño"),
    "stats_avg": ("Ø Stichlänge", "Avg Len", "Long. moy.", "Long. med."),
    "stats_spm": ("Eff. Tempo", "Eff. Speed", "Vitesse eff.", "Vel. ef."),
    "stats_peak": ("Spitzendichte", "Peak Density", "Densité max", "Densidad máx."),
    "stats_colors": ("Farbwechsel", "Color Changes", "Changements", "Cambios color"),
    "stats_runtime": ("Laufzeit: ca.", "Runtime: ~", "Durée : env.", "Tiempo: aprox."),
    "stats_min": ("Min.", "min", "min", "min"),
}


def tr(key: str) -> str:
    row = _TABLE.get(key)
    if not row:
        return key
    idx = {"de": 0, "en": 1, "fr": 2, "es": 3}.get(_cur_lang[0], 0)
    return row[idx]


_TABLE.update({
    # Menüeinträge
    "m_new": ("Neues Design", "New design", "Nouveau design", "Nuevo diseño"),
    "m_open": ("Projekt öffnen (.ostitch) …", "Open project (.ostitch) …", "Ouvrir un projet (.ostitch) …", "Abrir proyecto (.ostitch) …"),
    "m_save": ("Projekt speichern (.ostitch) …", "Save project (.ostitch) …", "Enregistrer le projet (.ostitch) …", "Guardar proyecto (.ostitch) …"),
    "m_import": ("Stickdatei importieren (EXP, DST, PES, JEF …) …", "Import embroidery file (EXP, DST, PES, JEF …) …", "Importer un fichier de broderie (EXP, DST, PES, JEF …) …", "Importar archivo de bordado (EXP, DST, PES, JEF …) …"),
    "m_import_svg": ("SVG-Vektorgrafik importieren (.svg) …", "Import SVG vector graphic (.svg) …", "Importer un graphique vectoriel SVG …", "Importar gráfico vectorial SVG …"),
    "m_export": ("Stickdatei exportieren (EXP, DST, PES, JEF …) …", "Export embroidery file (EXP, DST, PES, JEF …) …", "Exporter le fichier de broderie (EXP, DST, PES, JEF …) …", "Exportar archivo de bordado (EXP, DST, PES, JEF …) …"),
    "m_export_pdf": ("Produktionsblatt als PDF speichern …", "Save production sheet as PDF …", "Enregistrer la fiche de production en PDF …", "Guardar hoja de producción como PDF …"),
    "m_export_png": ("Realistische 3D-Vorschau als PNG speichern …", "Save realistic 3D preview as PNG …", "Enregistrer l'aperçu 3D réaliste en PNG …", "Guardar vista previa 3D realista como PNG …"),
    "m_quit": ("Beenden", "Quit", "Quitter", "Salir"),
    "m_auto": ("Bild automatisch digitalisieren (Auto-Digitizer) …", "Auto-digitize image (Auto-Digitizer) …", "Numériser automatiquement une image …", "Digitalizar imagen automáticamente …"),
    "m_photo": ("PhotoStitch (Porträtfoto → Stickerei) …", "PhotoStitch (portrait photo → embroidery) …", "PhotoStitch (photo portrait → broderie) …", "PhotoStitch (foto retrato → bordado) …"),
    "m_text": ("Schrift / Monogramm einfügen …", "Insert lettering / monogram …", "Insérer lettrage / monogramme …", "Insertar texto / monograma …"),
    "m_applique": ("Aus Fläche Applikation (Appliqué) erzeugen", "Create appliqué from shape", "Créer un appliqué depuis la forme", "Crear aplique desde la forma"),
    "m_puff": ("3D-Puff-Schaumstoff-Modus für Satin umschalten", "Toggle 3D puff foam mode for satin", "Activer le mode mousse 3D pour le satin", "Activar modo espuma 3D para satén"),
    "m_transfer": ("Maschinen-Transfer / Diskette / USB / NetBridge …", "Machine transfer / floppy / USB / NetBridge …", "Transfert machine / disquette / USB / NetBridge …", "Transferencia a máquina / disquete / USB / NetBridge …"),
    "m_doctor": ("Qualitäts- & Maschinen-Doktor (Prüfung)", "Quality & Machine Doctor (check)", "Docteur qualité & machine (contrôle)", "Doctor de calidad y máquina (revisión)"),
    "m_optimize": ("Farben minimieren (Nadelwechsel sparen)", "Minimize colors (save needle changes)", "Minimiser les couleurs (moins de changements)", "Minimizar colores (menos cambios de aguja)"),
    "m_tour": ("Interaktiver Studio-Rundgang (Onboarding) …", "Interactive studio tour (onboarding) …", "Visite interactive du studio …", "Guía interactiva del estudio …"),
    "m_restore_logo": ("Offizielles OpenStitch-Logo wiederherstellen", "Restore official OpenStitch logo", "Restaurer le logo officiel OpenStitch", "Restaurar el logotipo oficial de OpenStitch"),
    "m_undo": ("Rückgängig", "Undo", "Annuler", "Deshacer"),
    "m_redo": ("Wiederherstellen", "Redo", "Rétablir", "Rehacer"),
    "m_duplicate": ("Ausgewähltes Objekt duplizieren", "Duplicate selected object", "Dupliquer l'objet sélectionné", "Duplicar objeto seleccionado"),
    "m_delete": ("Ausgewähltes Objekt löschen", "Delete selected object", "Supprimer l'objet sélectionné", "Eliminar objeto seleccionado"),
    "m_center": ("Design im Rahmen zentrieren", "Center design in hoop", "Centrer le design dans le cadre", "Centrar diseño en el bastidor"),
    "m_fit": ("Optimal in aktuellen Rahmen einpassen (Auto-Fit)", "Fit optimally into current hoop (Auto-Fit)", "Ajuster au cadre actuel (Auto-Fit)", "Ajustar al bastidor actual (Auto-Ajuste)"),
    "m_pick_hoop": ("Kleinsten passenden Rahmen automatisch wählen", "Automatically pick smallest fitting hoop", "Choisir automatiquement le plus petit cadre", "Elegir automáticamente el bastidor más pequeño"),
    "m_scale": ("Design skalieren (% / mm) …", "Scale design (% / mm) …", "Redimensionner le design (% / mm) …", "Escalar diseño (% / mm) …"),
    "m_3d": ("3D-Fadendarstellung", "3D thread rendering", "Rendu 3D des fils", "Renderizado 3D de hilos"),
    "m_jumps": ("Sprungstiche anzeigen", "Show jump stitches", "Afficher les sauts", "Mostrar saltos"),
    "m_grid": ("Millimeter-Raster anzeigen", "Show millimeter grid", "Afficher la grille millimétrique", "Mostrar cuadrícula milimétrica"),
    "m_heatmap": ("Stichdichte-Heatmap (Stoffbelastung)", "Stitch density heatmap (fabric stress)", "Carte de densité (contrainte du tissu)", "Mapa de densidad (tensión de la tela)"),
    "m_zoom": ("Auf Rahmengrösse zoomen", "Zoom to hoop", "Zoom sur le cadre", "Zoom al bastidor"),
    "lbl_lang": ("Sprache:", "Language:", "Langue :", "Idioma:"),
})


def key_for(german_text: str) -> str | None:
    """Findet den Übersetzungsschlüssel anhand des deutschen Originaltexts."""
    for k, row in _TABLE.items():
        if row[0] == german_text:
            return k
    return None


_TABLE.update({
    "status_computing": ("Stiche werden berechnet …", "Computing stitches …", "Calcul des points …",
                         "Calculando puntadas …"),
    "dlg_unsaved_title": ("Ungespeicherte Änderungen", "Unsaved changes", "Modifications non enregistrées",
                          "Cambios sin guardar"),
    "dlg_unsaved_text": ("Das aktuelle Design hat ungespeicherte Änderungen. Jetzt speichern?",
                         "The current design has unsaved changes. Save them now?",
                         "Le motif actuel contient des modifications non enregistrées. Les enregistrer ?",
                         "El diseño actual tiene cambios sin guardar. ¿Guardarlos ahora?"),
    "status_plan_error": ("Fehler bei der Stichberechnung", "Stitch generation failed",
                          "Erreur lors du calcul des points", "Error al calcular las puntadas"),
})


# Satinsäule & Diskette
_TABLE.update({
    "kind_column": ("Satinsäule", "Satin column", "Colonne satin", "Columna satén"),
    "param_column_width": ("Säulenbreite (mm)", "Column width (mm)", "Largeur de colonne (mm)",
                           "Ancho de columna (mm)"),
    "msg_overwrite_title": ("Datei ersetzen?", "Replace file?", "Remplacer le fichier ?", "¿Reemplazar archivo?"),
    "msg_overwrite_text": ("Auf der Diskette gibt es bereits {name}. Ersetzen?",
                           "{name} already exists on the floppy image. Replace it?",
                           "{name} existe déjà sur la disquette. Le remplacer ?",
                           "{name} ya existe en el disquete. ¿Reemplazarlo?"),
})


# Fehlermeldungen beim Laden
_TABLE.update({
    "err_project_damaged": (
        "„{name}“ ist beschädigt oder keine OpenStitch-Projektdatei.",
        "“{name}” is damaged or not an OpenStitch project file.",
        "« {name} » est endommagé ou n'est pas un fichier de projet OpenStitch.",
        "«{name}» está dañado o no es un archivo de proyecto de OpenStitch."),
})

# Qualitäts-Doktor
_TABLE.update({
    "doc_empty": ("Das Design enthält noch keine Stiche.", "The design has no stitches yet.",
                  "Le motif ne contient encore aucun point.", "El diseño aún no tiene puntadas."),
    "doc_hoop_round": (
        "⚠ RAHMEN-KOLLISIONSGEFAHR: Das Motiv (Radius {r} mm) reicht an den Rand des Rundrahmens ({hoop}, Radius {hr} mm). "
        "Wähle einen grösseren Rahmen oder zentriere/verkleinere das Motiv.",
        "⚠ HOOP COLLISION RISK: the design (radius {r} mm) reaches the edge of the round hoop ({hoop}, radius {hr} mm). "
        "Pick a larger hoop or centre/shrink the design.",
        "⚠ RISQUE DE COLLISION AVEC LE CADRE : le motif (rayon {r} mm) atteint le bord du cadre rond ({hoop}, rayon {hr} mm). "
        "Choisissez un cadre plus grand ou centrez/réduisez le motif.",
        "⚠ RIESGO DE CHOQUE CON EL BASTIDOR: el diseño (radio {r} mm) llega al borde del bastidor redondo ({hoop}, radio {hr} mm). "
        "Elige un bastidor mayor o centra/reduce el diseño."),
    "doc_hoop_rect": (
        "⚠ RAHMEN-KOLLISIONSGEFAHR: Das Motiv ({w}×{h} mm) überschreitet das sichere Stickfeld des Rahmens ({hw}×{hh} mm).",
        "⚠ HOOP COLLISION RISK: the design ({w}×{h} mm) exceeds the hoop's safe sewing field ({hw}×{hh} mm).",
        "⚠ RISQUE DE COLLISION AVEC LE CADRE : le motif ({w}×{h} mm) dépasse la zone de broderie sûre du cadre ({hw}×{hh} mm).",
        "⚠ RIESGO DE CHOQUE CON EL BASTIDOR: el diseño ({w}×{h} mm) supera el área segura del bastidor ({hw}×{hh} mm)."),
    "doc_colors": (
        "⚠ ZU VIELE FARBEN: Das Design verwendet {n} Garnfarben, die Maschine hat {needles} Nadeln. "
        "Reduziere die Farben oder plane einen manuellen Garnwechsel ein.",
        "⚠ TOO MANY COLOURS: the design uses {n} thread colours but the machine has {needles} needles. "
        "Reduce colours or plan a manual thread change.",
        "⚠ TROP DE COULEURS : le motif utilise {n} couleurs de fil, la machine a {needles} aiguilles. "
        "Réduisez les couleurs ou prévoyez un changement de fil manuel.",
        "⚠ DEMASIADOS COLORES: el diseño usa {n} colores de hilo y la máquina tiene {needles} agujas. "
        "Reduce los colores o planifica un cambio de hilo manual."),
    "doc_small_text": (
        "⚠ KLEINE SCHRIFT ({name}, {h} mm): Umriss-Schriften unter 4.5 mm laufen auf Stoff oft zu. "
        "Tipp: Für kleine Schrift die Schriftart „OpenStitch Micro“ verwenden.",
        "⚠ SMALL LETTERING ({name}, {h} mm): outline fonts below 4.5 mm tend to fill in on fabric. "
        "Tip: use the “OpenStitch Micro” font for small lettering.",
        "⚠ PETIT TEXTE ({name}, {h} mm) : sous 4,5 mm, les polices à contour se bouchent souvent sur le tissu. "
        "Astuce : utilisez la police « OpenStitch Micro » pour les petits textes.",
        "⚠ TEXTO PEQUEÑO ({name}, {h} mm): las fuentes de contorno por debajo de 4,5 mm suelen cerrarse en la tela. "
        "Consejo: usa la fuente «OpenStitch Micro» para texto pequeño."),
    "doc_satin_density": (
        "⚠ HOHE SATIN-DICHTE ({name}, {sp} mm): Dichte unter 0.28 mm kann zu Fadenbruch führen (empfohlen: 0.36–0.42 mm).",
        "⚠ HIGH SATIN DENSITY ({name}, {sp} mm): spacing below 0.28 mm can break threads (recommended: 0.36–0.42 mm).",
        "⚠ DENSITÉ SATIN ÉLEVÉE ({name}, {sp} mm) : un espacement sous 0,28 mm peut casser le fil (conseillé : 0,36–0,42 mm).",
        "⚠ DENSIDAD DE SATÉN ALTA ({name}, {sp} mm): un espaciado inferior a 0,28 mm puede romper el hilo "
        "(recomendado: 0,36–0,42 mm)."),
    "doc_density": (
        "⚠ DICHTE-SPITZEN: An {n} Stellen (1×1 mm) liegen mehr als 14 Stiche übereinander "
        "(Strg+H zeigt die Heatmap).",
        "⚠ DENSITY HOT SPOTS: {n} places (1×1 mm) have more than 14 stitches on top of each other "
        "(Ctrl+H shows the heatmap).",
        "⚠ PICS DE DENSITÉ : {n} zones (1×1 mm) comptent plus de 14 points superposés "
        "(Ctrl+H affiche la carte de densité).",
        "⚠ PICOS DE DENSIDAD: en {n} puntos (1×1 mm) hay más de 14 puntadas superpuestas "
        "(Ctrl+H muestra el mapa de calor)."),
    "doc_ok": (
        "✅ Keine Probleme gefunden ({st} Stiche, {n} von {needles} Nadeln, sicher im Rahmen {hoop}).",
        "✅ No problems found ({st} stitches, {n} of {needles} needles, safely inside {hoop}).",
        "✅ Aucun problème détecté ({st} points, {n} aiguilles sur {needles}, bien dans le cadre {hoop}).",
        "✅ No se encontraron problemas ({st} puntadas, {n} de {needles} agujas, dentro del bastidor {hoop})."),
})


def tr_all(key: str) -> list[str]:
    return list(_TABLE.get(key, (key,) * 4))


def tr_opt(key: str, fallback: str) -> str:
    """Wie tr(), aber mit eigenem Rückfallwert, falls der Schlüssel fehlt."""
    return tr(key) if key in _TABLE else fallback


# Zahlenformat je Sprache: Tausendertrennzeichen und Dezimalzeichen
# (de: Schweizer Apostroph, fr: schmales geschütztes Leerzeichen)
_GROUP_SEP = {"de": "’", "en": ",", "fr": " ", "es": "."}
_DEC_SEP = {"de": ".", "en": ".", "fr": ",", "es": ","}


def fmt_int(n) -> str:
    """Ganzzahl mit sprachüblichem Tausendertrennzeichen (de 1’234, en 1,234, fr 1 234, es 1.234)."""
    return f"{int(round(n)):,}".replace(",", _GROUP_SEP.get(_cur_lang[0], ","))


def fmt_float(x: float, decimals: int = 1) -> str:
    """Dezimalzahl mit sprachüblichen Trennzeichen (z. B. fr 1 423,5)."""
    int_part, _, frac = f"{x:,.{decimals}f}".partition(".")
    lang = _cur_lang[0]
    out = int_part.replace(",", _GROUP_SEP.get(lang, ","))
    return out + _DEC_SEP.get(lang, ".") + frac if frac else out


# ---------------------------------------------------------------------------
# Allgemeine Schaltflächen, Dateifilter & Fehlertitel
# ---------------------------------------------------------------------------
_TABLE.update({
    "label_colon": (":", ":", " :", ":"),
    "btn_cancel": ("Abbrechen", "Cancel", "Annuler", "Cancelar"),
    "btn_close": ("Schliessen", "Close", "Fermer", "Cerrar"),
    "btn_apply": ("Übernehmen", "Apply", "Appliquer", "Aplicar"),
    "btn_save": ("Speichern", "Save", "Enregistrer", "Guardar"),
    "btn_discard": ("Verwerfen", "Discard", "Ne pas enregistrer", "Descartar"),
    "dlg_error": ("Fehler", "Error", "Erreur", "Error"),
    "dlg_notice": ("Hinweis", "Notice", "Remarque", "Aviso"),
    "filter_all_files": ("Alle Dateien", "All files", "Tous les fichiers", "Todos los archivos"),
    "filter_all_images": ("Alle Bilder", "All images", "Toutes les images", "Todas las imágenes"),
    "filter_images": ("Bilder", "Images", "Images", "Imágenes"),
    "filter_all_img_vec": ("Alle Bild- & Vektordateien", "All image & vector files",
                           "Tous les fichiers image et vectoriels", "Todos los archivos de imagen y vectoriales"),
    "filter_raster": ("Rasterbilder", "Raster images", "Images matricielles", "Imágenes de mapa de bits"),
    "filter_svg": ("SVG-Vektorgrafik", "SVG vector graphic", "Graphique vectoriel SVG", "Gráfico vectorial SVG"),
    "filter_photos": ("Fotos & Bilder", "Photos & images", "Photos et images", "Fotos e imágenes"),
    "filter_project": ("OpenStitch-Projekt", "OpenStitch project", "Projet OpenStitch", "Proyecto OpenStitch"),
    "filter_emb": ("Stickdateien", "Embroidery files", "Fichiers de broderie", "Archivos de bordado"),
    "filter_png": ("PNG-Bild", "PNG image", "Image PNG", "Imagen PNG"),
    "filter_floppy": ("Diskettenabbild", "Floppy image", "Image de disquette", "Imagen de disquete"),
    "err_open_title": ("Fehler beim Öffnen", "Error opening file", "Erreur d'ouverture", "Error al abrir"),
    "err_load_title": ("Fehler beim Laden", "Error loading file", "Erreur de chargement", "Error al cargar"),
    "err_svg_title": ("SVG-Import-Fehler", "SVG import error", "Erreur d'import SVG", "Error al importar SVG"),
    "err_import_title": ("Import-Fehler", "Import error", "Erreur d'importation", "Error de importación"),
    "err_save_title": ("Speicherfehler", "Save error", "Erreur d'enregistrement", "Error al guardar"),
    "err_export_title": ("Export-Fehler", "Export error", "Erreur d'exportation", "Error de exportación"),
    "err_pdf_title": ("PDF-Fehler", "PDF error", "Erreur PDF", "Error de PDF"),
    "err_png_title": ("PNG-Fehler", "PNG error", "Erreur PNG", "Error de PNG"),
    "err_png_text": ("Bild konnte nicht gespeichert werden:\n{}", "Could not save the image:\n{}",
                     "Impossible d'enregistrer l'image :\n{}", "No se pudo guardar la imagen:\n{}"),
    "err_image_title": ("Bild-Fehler", "Image error", "Erreur d'image", "Error de imagen"),
})


# ---------------------------------------------------------------------------
# Hauptfenster: Tooltips, Objektliste, Statusleiste, Datei-Dialoge, Meldungen
# ---------------------------------------------------------------------------
_TABLE.update({
    "app_tagline": ("Universelle Open-Source-Stick- & Digitalisier-Suite",
                    "Universal Open-Source Embroidery & Digitizing Suite",
                    "Suite universelle open source de broderie et de numérisation",
                    "Suite universal de bordado y digitalización de código abierto"),
    "tb_title_studio": ("Studio-Leiste", "Studio toolbar", "Barre du studio", "Barra del estudio"),
    "tb_title_tools": ("Zeichenwerkzeuge", "Drawing tools", "Outils de dessin", "Herramientas de dibujo"),
    "tip_autofit": ("Design optimal in den gewählten Rahmen einpassen (Ctrl+F)",
                    "Fit the design optimally into the selected hoop (Ctrl+F)",
                    "Ajuster le motif de façon optimale au cadre choisi (Ctrl+F)",
                    "Ajustar el diseño de forma óptima al bastidor elegido (Ctrl+F)"),
    "tip_fabric": ("Stoffhintergrund im Stickrahmen umschalten (Dunkel-Schiefer / Warm-Sand / Hell)",
                   "Switch the fabric background in the hoop (dark slate / warm sand / light)",
                   "Changer le fond de tissu dans le cadre (ardoise sombre / sable chaud / clair)",
                   "Cambiar el fondo de tela en el bastidor (pizarra oscura / arena cálida / clara)"),
    "tip_tool_select": ("Objekte auswählen, verschieben & skalieren (Taste V)",
                        "Select, move & scale objects (key V)",
                        "Sélectionner, déplacer et redimensionner des objets (touche V)",
                        "Seleccionar, mover y escalar objetos (tecla V)"),
    "tip_tool_nodes": ("Konturknoten & Stichwinkel-Achse direkt ziehen (Taste N)",
                       "Drag contour nodes & the stitch angle axis directly (key N)",
                       "Déplacer directement les nœuds du contour et l'axe d'angle de point (touche N)",
                       "Arrastrar directamente los nodos del contorno y el eje del ángulo de puntada (tecla N)"),
    "tip_tool_fill": ("Neue Tatami-Füllfläche auf der Leinwand zeichnen (Taste F)",
                      "Draw a new tatami fill area on the canvas (key F)",
                      "Dessiner une nouvelle zone de remplissage tatami sur le canevas (touche F)",
                      "Dibujar una nueva área de relleno tatami en el lienzo (tecla F)"),
    "tip_tool_satin": ("Neue Satin-Säule auf der Leinwand zeichnen (Taste S)",
                       "Draw a new satin column on the canvas (key S)",
                       "Dessiner une nouvelle colonne de point satin sur le canevas (touche S)",
                       "Dibujar una nueva columna de puntada satén en el lienzo (tecla S)"),
    "tip_tool_run": ("Neuen Steppstich-Pfad zeichnen (Taste R)",
                     "Draw a new running stitch path (key R)",
                     "Dessiner un nouveau tracé au point droit (touche R)",
                     "Dibujar un nuevo trazado de puntada recta (tecla R)"),
    "tip_tool_heatmap": ("Stichdichte-Heatmap (Grün/Gelb/Rot) ein-/ausblenden (Ctrl+H)",
                         "Show/hide the stitch density heatmap (green/yellow/red) (Ctrl+H)",
                         "Afficher/masquer la carte de densité (vert/jaune/rouge) (Ctrl+H)",
                         "Mostrar/ocultar el mapa de densidad (verde/amarillo/rojo) (Ctrl+H)"),
    "tip_tool_zoom": ("Ansicht in den Stickrahmen einpassen (Ctrl+0)", "Fit the view to the hoop (Ctrl+0)",
                      "Ajuster la vue au cadre (Ctrl+0)", "Ajustar la vista al bastidor (Ctrl+0)"),
    "tip_obj_up": ("Objekt in der Stickreihenfolge nach oben", "Move object up in the stitch order",
                   "Monter l'objet dans l'ordre de broderie", "Subir el objeto en el orden de bordado"),
    "tip_obj_down": ("Objekt in der Stickreihenfolge nach unten", "Move object down in the stitch order",
                     "Descendre l'objet dans l'ordre de broderie", "Bajar el objeto en el orden de bordado"),
    "tip_obj_delete": ("Ausgewähltes Objekt löschen (Entf)", "Delete selected object (Del)",
                       "Supprimer l'objet sélectionné (Suppr)", "Eliminar el objeto seleccionado (Supr)"),
    "sim_all": ("Alle", "All", "Tout", "Todo"),
    "sim_speed_suffix": (" St./Tick", " st./tick", " pts/tick", " punt./tick"),
    "abbr_stitches": ("St.", "st.", "pts", "punt."),
    "stats_trims": ("Fadenschnitte", "Trims", "Coupes", "Cortes"),
    "kind_fill": ("Tatami", "Fill", "Remplissage", "Relleno"),
    "kind_satin": ("Satin", "Satin", "Satin", "Satén"),
    "kind_run": ("Stepp", "Running stitch", "Point droit", "Pespunte"),
    "kind_text": ("Schrift", "Lettering", "Lettrage", "Texto"),
    "kind_stitches": ("Stiche", "Stitches", "Points", "Puntadas"),
    "obj_hidden": ("[Aus]", "[Hidden]", "[Masqué]", "[Oculto]"),
    "btn_font_arc": ("Schriftart & Bogen anpassen …", "Adjust font & arc …",
                     "Modifier la police et l'arc …", "Ajustar fuente y arco …"),
    "status_hoop_strategy": ("Rahmen-Strategie aktiv: {}", "Hoop strategy active: {}",
                             "Stratégie de cadre active : {}", "Estrategia de bastidor activa: {}"),
    "status_saved": ("Gespeichert: {}", "Saved: {}", "Enregistré : {}", "Guardado: {}"),
    "color_dialog_title": ("Garnfarbe wählen", "Choose thread color", "Choisir la couleur du fil",
                           "Elegir color de hilo"),
    "default_design_name": ("Neues_Design", "New_Design", "Nouveau_motif", "Nuevo_diseño"),
    "fd_open_project": ("Projekt öffnen", "Open project", "Ouvrir un projet", "Abrir proyecto"),
    "fd_save_project": ("Projekt speichern", "Save project", "Enregistrer le projet", "Guardar proyecto"),
    "fd_import_emb": ("Stickdatei importieren", "Import embroidery file", "Importer un fichier de broderie",
                      "Importar archivo de bordado"),
    "fd_import_svg": ("SVG-Vektorgrafik importieren", "Import SVG vector graphic",
                      "Importer un graphique vectoriel SVG", "Importar gráfico vectorial SVG"),
    "fd_export_emb": ("Stickdatei exportieren", "Export embroidery file", "Exporter le fichier de broderie",
                      "Exportar archivo de bordado"),
    "fd_save_pdf": ("Produktionsblatt (PDF) speichern", "Save production sheet (PDF)",
                    "Enregistrer la fiche de production (PDF)", "Guardar hoja de producción (PDF)"),
    "pdf_file_suffix": ("Produktionsblatt", "production_sheet", "fiche_production", "hoja_produccion"),
    "fd_save_png": ("3D-Stichvorschau speichern", "Save 3D stitch preview", "Enregistrer l'aperçu 3D des points",
                    "Guardar vista previa 3D de puntadas"),
    "fd_pick_image": ("Bild, Grafik oder Logo wählen (Downloads / Bilder / Desktop)",
                      "Choose an image, graphic or logo (Downloads / Pictures / Desktop)",
                      "Choisir une image, un graphique ou un logo (Téléchargements / Images / Bureau)",
                      "Elegir una imagen, gráfico o logotipo (Descargas / Imágenes / Escritorio)"),
    "fd_pick_photo": ("Porträt- oder Landschaftsfoto wählen (Downloads / Bilder / Desktop)",
                      "Choose a portrait or landscape photo (Downloads / Pictures / Desktop)",
                      "Choisir une photo de portrait ou de paysage (Téléchargements / Images / Bureau)",
                      "Elegir una foto de retrato o paisaje (Descargas / Imágenes / Escritorio)"),
    "msg_applique_title": ("Applikation (Appliqué)", "Appliqué", "Appliqué", "Aplique"),
    "msg_applique_text": ("Bitte zuerst eine Fläche auf der Leinwand auswählen.",
                          "Please select a fill or satin shape on the canvas first.",
                          "Veuillez d'abord sélectionner une forme sur le canevas.",
                          "Primero selecciona una forma en el lienzo."),
    "msg_doctor_title": ("Qualitäts- & Maschinen-Doktor", "Quality & Machine Doctor",
                         "Docteur qualité & machine", "Doctor de calidad y máquina"),
    "msg_export_verified_title": ("Export & Binär-Verifikation erfolgreich", "Export & binary verification successful",
                                  "Export et vérification binaire réussis",
                                  "Exportación y verificación binaria correctas"),
    "msg_export_verified_text": (
        "✅ Stickdatei gespeichert und im Simulator verifiziert:\n{path}\n\n"
        "• Dateigrösse: {size} Bytes\n• Verifizierte Nähstiche: {stitches}\n"
        "• Abmessung: {w:.1f} × {h:.1f} mm\n• Max. Schrittweite: {step:.1f} mm\n"
        "• Farbwechsel: {colors}   ·   Sprünge: {jumps}",
        "✅ Embroidery file saved and verified in the simulator:\n{path}\n\n"
        "• File size: {size} bytes\n• Verified stitches: {stitches}\n"
        "• Dimensions: {w:.1f} × {h:.1f} mm\n• Max. step length: {step:.1f} mm\n"
        "• Color changes: {colors}   ·   Jumps: {jumps}",
        "✅ Fichier de broderie enregistré et vérifié dans le simulateur :\n{path}\n\n"
        "• Taille du fichier : {size} octets\n• Points vérifiés : {stitches}\n"
        "• Dimensions : {w:.1f} × {h:.1f} mm\n• Pas max. : {step:.1f} mm\n"
        "• Changements de couleur : {colors}   ·   Sauts : {jumps}",
        "✅ Archivo de bordado guardado y verificado en el simulador:\n{path}\n\n"
        "• Tamaño del archivo: {size} bytes\n• Puntadas verificadas: {stitches}\n"
        "• Dimensiones: {w:.1f} × {h:.1f} mm\n• Paso máx.: {step:.1f} mm\n"
        "• Cambios de color: {colors}   ·   Saltos: {jumps}",
    ),
    "msg_export_ok_title": ("Export erfolgreich", "Export successful", "Export réussi", "Exportación correcta"),
    "msg_export_ok_text": ("Datei wurde gespeichert:\n{}", "File saved:\n{}", "Fichier enregistré :\n{}",
                           "Archivo guardado:\n{}"),
    "msg_pdf_ok_title": ("PDF erstellt", "PDF created", "PDF créé", "PDF creado"),
    "msg_pdf_ok_text": ("Produktionsblatt gespeichert:\n{}", "Production sheet saved:\n{}",
                        "Fiche de production enregistrée :\n{}", "Hoja de producción guardada:\n{}"),
    "msg_puff_title": ("3D-Puff-Schaumstoff", "3D puff foam", "Mousse 3D (puff)", "Espuma 3D (puff)"),
    "msg_puff_text": ("Bitte wähle ein Satin-Objekt aus.", "Please select a satin object.",
                      "Veuillez sélectionner un objet en point satin.", "Selecciona un objeto de puntada satén."),
    "dlg_scale_title": ("Design skalieren (Stiche werden neu berechnet!)",
                        "Scale design (stitches will be recalculated!)",
                        "Redimensionner le motif (les points seront recalculés !)",
                        "Escalar diseño (¡las puntadas se recalcularán!)"),
    "dlg_scale_label": ("Skalierungsfaktor (%):", "Scale factor (%):", "Facteur d'échelle (%) :",
                        "Factor de escala (%):"),
})


# ---------------------------------------------------------------------------
# Stickrahmen: Namen (nur Anzeige – Hoop.name bleibt unverändert) & Strategien
# ---------------------------------------------------------------------------
_TABLE.update({
    "hoop_round9": ("Rund 9 cm (Klein/Brust)", "Round 9 cm (small/chest)", "Rond 9 cm (petit/poitrine)",
                    "Redondo 9 cm (pequeño/pecho)"),
    "hoop_round12": ("Rund 12 cm (Brustlogo)", "Round 12 cm (chest logo)", "Rond 12 cm (logo poitrine)",
                     "Redondo 12 cm (logo de pecho)"),
    "hoop_round15": ("Rund 15 cm (Standard)", "Round 15 cm (standard)", "Rond 15 cm (standard)",
                     "Redondo 15 cm (estándar)"),
    "hoop_round18": ("Rund 18 cm (Gross)", "Round 18 cm (large)", "Rond 18 cm (grand)", "Redondo 18 cm (grande)"),
    "hoop_round21": ("Rund 21 cm (XL)", "Round 21 cm (XL)", "Rond 21 cm (XL)", "Redondo 21 cm (XL)"),
    "hoop_cap": ("Kappe / Cap 13 × 5 cm", "Cap 13 × 5 cm", "Casquette 13 × 5 cm", "Gorra 13 × 5 cm"),
    "hoop_widecap": ("Wide-Cap 30 × 7 cm", "Wide cap 30 × 7 cm", "Casquette large 30 × 7 cm", "Gorra ancha 30 × 7 cm"),
    "hoop_rect13x18": ("Rechteck 13 × 18 cm (Haushalt)", "Rectangle 13 × 18 cm (home)",
                       "Rectangle 13 × 18 cm (domestique)", "Rectangular 13 × 18 cm (doméstico)"),
    "hoop_jacket": ("Jackenrücken 30 × 30 cm", "Jacket back 30 × 30 cm", "Dos de veste 30 × 30 cm",
                    "Espalda de chaqueta 30 × 30 cm"),
    "hoop_field40x30": ("Grossfeld 40 × 30 cm (Industrie)", "Large field 40 × 30 cm (industrial)",
                        "Grand champ 40 × 30 cm (industriel)", "Campo grande 40 × 30 cm (industrial)"),
    "hoop_strat_small": (
        "Straffe Spannung · feine Details (-10% Zugkompensation, Standard-Unterlage)",
        "Firm tension · fine details (-10% pull compensation, standard underlay)",
        "Tension ferme · détails fins (-10 % de compensation de traction, sous-couche standard)",
        "Tensión firme · detalles finos (-10 % de compensación de tirón, refuerzo estándar)",
    ),
    "hoop_strat_medium": (
        "Ausgewogen · Standard-Brust-/Ärmelrahmen (100% Zugkompensation)",
        "Balanced · standard chest/sleeve hoop (100% pull compensation)",
        "Équilibré · cadre standard poitrine/manche (100 % de compensation de traction)",
        "Equilibrado · bastidor estándar de pecho/manga (100 % de compensación de tirón)",
    ),
    "hoop_strat_large": (
        "Anti-Trampolin · verstärkte Unterlage (+20% Zugkompensation + Kreuz-Gitter bei grossen Flächen)",
        "Anti-trampoline · reinforced underlay (+20% pull compensation + cross grid on large areas)",
        "Anti-trampoline · sous-couche renforcée (+20 % de compensation de traction + grille croisée "
        "sur les grandes surfaces)",
        "Antitrampolín · refuerzo reforzado (+20 % de compensación de tirón + rejilla cruzada en áreas grandes)",
    ),
    "hoop_strat_jacket": (
        "Jackenrücken-Stabilisierung (+35% Zugkompensation, Doppel-Gitter-Unterlage, max. 750 SPM)",
        "Jacket-back stabilization (+35% pull compensation, double grid underlay, max. 750 SPM)",
        "Stabilisation dos de veste (+35 % de compensation de traction, sous-couche en double grille, max. 750 SPM)",
        "Estabilización para espalda de chaqueta (+35 % de compensación de tirón, refuerzo de doble rejilla, "
        "máx. 750 SPM)",
    ),
    "hoop_strat_cap": (
        "Kappen-Modus (Center-Out & Bottom-Up vom Schirm nach oben, +30% Zugkompensation)",
        "Cap mode (center-out & bottom-up from the brim upward, +30% pull compensation)",
        "Mode casquette (du centre vers l'extérieur et de la visière vers le haut, +30 % de compensation de traction)",
        "Modo gorra (del centro hacia fuera y desde la visera hacia arriba, +30 % de compensación de tirón)",
    ),
    "hoop_strat_default": ("Standard", "Standard", "Standard", "Estándar"),
})


# ---------------------------------------------------------------------------
# Maschinenprofile: Anzeigenamen (machine_<id>; MachineProfile.name bleibt der gespeicherte Wert)
# ---------------------------------------------------------------------------
_TABLE.update({
    "machine_universal_multi": ("Universal Standard (DST / PES / EXP · 15 Nadeln)",
                                "Universal standard (DST / PES / EXP · 15 needles)",
                                "Standard universel (DST / PES / EXP · 15 aiguilles)",
                                "Estándar universal (DST / PES / EXP · 15 agujas)"),
    "machine_tajima_tmez": ("Tajima TMEZ / TFMX / TMBR (15 Nadeln)", "Tajima TMEZ / TFMX / TMBR (15 needles)",
                            "Tajima TMEZ / TFMX / TMBR (15 aiguilles)", "Tajima TMEZ / TFMX / TMBR (15 agujas)"),
    "machine_brother_pr": ("Brother PR-Serie / Persona (6–10 Nadeln)", "Brother PR series / Persona (6–10 needles)",
                           "Brother série PR / Persona (6–10 aiguilles)", "Brother serie PR / Persona (6–10 agujas)"),
    "machine_brother_home": ("Brother / Baby Lock Haushalt (1 Nadel · PES)", "Brother / Baby Lock home (1 needle · PES)",
                             "Brother / Baby Lock domestique (1 aiguille · PES)",
                             "Brother / Baby Lock doméstica (1 aguja · PES)"),
    "machine_barudan_bext": ("Barudan BEKT / BEXT (15 Nadeln)", "Barudan BEKT / BEXT (15 needles)",
                             "Barudan BEKT / BEXT (15 aiguilles)", "Barudan BEKT / BEXT (15 agujas)"),
    "machine_ricoma_happy_zsk": ("Ricoma / HappyJapan / SWF / ZSK (12–15 Nadeln)",
                                 "Ricoma / HappyJapan / SWF / ZSK (12–15 needles)",
                                 "Ricoma / HappyJapan / SWF / ZSK (12–15 aiguilles)",
                                 "Ricoma / HappyJapan / SWF / ZSK (12–15 agujas)"),
    "machine_janome_elna": ("Janome / Elna / Bernina Haushalt (JEF / EXP)", "Janome / Elna / Bernina home (JEF / EXP)",
                            "Janome / Elna / Bernina domestique (JEF / EXP)",
                            "Janome / Elna / Bernina doméstica (JEF / EXP)"),
    "machine_pfaff_husqvarna": ("Pfaff / Husqvarna Viking (VP3)", "Pfaff / Husqvarna Viking (VP3)",
                                "Pfaff / Husqvarna Viking (VP3)", "Pfaff / Husqvarna Viking (VP3)"),
    "machine_melco_emt10_4": ("Melco EMT10/4 (4-Kopf / 10 Nadeln)", "Melco EMT10/4 (4-head / 10 needles)",
                              "Melco EMT10/4 (4 têtes / 10 aiguilles)", "Melco EMT10/4 (4 cabezales / 10 agujas)"),
    "machine_melco_amaya_bravo": ("Melco Amaya / EMT16X / Bravo (16 Nadeln)", "Melco Amaya / EMT16X / Bravo (16 needles)",
                                  "Melco Amaya / EMT16X / Bravo (16 aiguilles)",
                                  "Melco Amaya / EMT16X / Bravo (16 agujas)"),
})


def machine_display_name(name: str) -> str:
    """Übersetzter Anzeigename eines Maschinenprofils (anhand des gespeicherten deutschen Namens)."""
    from .core.machines import MACHINE_PROFILES  # spät importieren: vermeidet Import-Zyklen
    mp = next((m for m in MACHINE_PROFILES if m.name == name), None)
    return tr_opt(f"machine_{mp.id}", name) if mp else name


# ---------------------------------------------------------------------------
# Objekt-Inspektor: Parameter-Labels (param_<attr> bzw. param_<kind>_<attr>) & Optionswerte (opt_<wert>)
# ---------------------------------------------------------------------------
_TABLE.update({
    "param_angle": ("Stichwinkel (°)", "Stitch angle (°)", "Angle de point (°)", "Ángulo de puntada (°)"),
    "param_fill_spacing": ("Reihenabstand (mm)", "Row spacing (mm)", "Espacement des rangs (mm)",
                           "Separación de filas (mm)"),
    "param_satin_spacing": ("Dichte (mm)", "Density (mm)", "Densité (mm)", "Densidad (mm)"),
    "param_stitch_len": ("Stichlänge (mm)", "Stitch length (mm)", "Longueur de point (mm)",
                         "Longitud de puntada (mm)"),
    "param_pattern": ("Muster", "Pattern", "Motif de remplissage", "Patrón"),
    "param_underlay": ("Unterlage", "Underlay", "Sous-couche", "Refuerzo"),
    "param_pull_comp": ("Zugkompensation (mm)", "Pull compensation (mm)", "Compensation de traction (mm)",
                        "Compensación de tirón (mm)"),
    "param_max_stitch": ("Max. Stich / Split (mm)", "Max. stitch / split (mm)", "Point max. / division (mm)",
                         "Puntada máx. / división (mm)"),
    "param_underlay_style": ("Unterlage-Art", "Underlay type", "Type de sous-couche", "Tipo de refuerzo"),
    "param_puff_3d": ("3D-Puff (Cap-Modus)", "3D puff (cap mode)", "Puff 3D (mode casquette)", "Puff 3D (modo gorra)"),
    "param_repeats": ("Wiederholungen (0=einfach, 1=dreifach)", "Repeats (0 = single, 1 = triple)",
                      "Répétitions (0 = simple, 1 = triple)", "Repeticiones (0 = simple, 1 = triple)"),
    "param_text": ("Text", "Text", "Texte", "Texto"),
    "param_font": ("Schrift", "Font", "Police", "Fuente"),
    "param_height": ("Buchstabenhöhe (mm)", "Letter height (mm)", "Hauteur des lettres (mm)", "Altura de letra (mm)"),
    "param_letter_spacing": ("Zeichenabstand (mm)", "Letter spacing (mm)", "Espacement des lettres (mm)",
                             "Espaciado entre letras (mm)"),
    "param_arc_radius": ("Bogenradius (mm, 0 = gerade)", "Arc radius (mm, 0 = straight)",
                         "Rayon de l'arc (mm, 0 = droit)", "Radio del arco (mm, 0 = recto)"),
    "param_mode": ("Stichart", "Stitch type", "Type de point", "Tipo de puntada"),
    "param_density": ("Dichte (mm)", "Density (mm)", "Densité (mm)", "Densidad (mm)"),
    # Füllmuster
    "opt_standard": ("Standard", "Standard", "Standard", "Estándar"),
    "opt_diagonal": ("Diagonal", "Diagonal", "Diagonal", "Diagonal"),
    "opt_ziegel": ("Ziegel", "Brick", "Brique", "Ladrillo"),
    "opt_wellen": ("Wellen", "Waves", "Vagues", "Ondas"),
    "opt_kontur": ("Kontur", "Contour", "Contour", "Contorno"),
    # Satin-Unterlagen
    "opt_auto": ("Automatisch", "Automatic", "Automatique", "Automático"),
    "opt_mitte": ("Mittellauf", "Center walk", "Passage central", "Pasada central"),
    "opt_kante": ("Kantenlauf", "Edge walk", "Passage de bord", "Pasada de borde"),
    "opt_zickzack": ("Zickzack", "Zigzag", "Zigzag", "Zigzag"),
    "opt_kante+zickzack": ("Kantenlauf + Zickzack", "Edge walk + zigzag", "Passage de bord + zigzag",
                           "Pasada de borde + zigzag"),
    # Schrift-Stichart
    "opt_satin": ("Satinstich", "Satin stitch", "Point satin", "Puntada satén"),
    "opt_fill": ("Tatami-Füllstich", "Tatami fill", "Remplissage tatami", "Relleno tatami"),
})


# ---------------------------------------------------------------------------
# Dialoge: Auto-Digitizer, Schrift, Maschinen-Transfer, PhotoStitch
# ---------------------------------------------------------------------------
_TABLE.update({
    # Auto-Digitizer
    "dlg_auto_title": ("Bild automatisch digitalisieren (Auto-Digitizer)", "Auto-digitize image (Auto-Digitizer)",
                       "Numériser automatiquement une image (Auto-Numériseur)",
                       "Digitalizar imagen automáticamente (Auto-Digitalizador)"),
    "lbl_orig_image": ("Originalbild ({})", "Original image ({})", "Image d'origine ({})", "Imagen original ({})"),
    "btn_other_image": ("📂 Anderes Bild wählen (Downloads / Desktop / Bilder …)",
                        "📂 Choose another image (Downloads / Desktop / Pictures …)",
                        "📂 Choisir une autre image (Téléchargements / Bureau / Images …)",
                        "📂 Elegir otra imagen (Descargas / Escritorio / Imágenes …)"),
    "grp_auto_settings": ("Stick-Einstellungen & Automatik", "Embroidery settings & automation",
                          "Réglages de broderie et automatisme", "Ajustes de bordado y automatización"),
    "lbl_target_width_motif": ("Zielbreite des Motivs:", "Target design width:", "Largeur cible du motif :",
                               "Ancho objetivo del diseño:"),
    "lbl_max_colors": ("Max. Garnfarben (Nadeln):", "Max. thread colors (needles):",
                       "Couleurs de fil max. (aiguilles) :", "Máx. colores de hilo (agujas):"),
    "cb_remove_bg": ("Bildhintergrund automatisch entfernen", "Remove image background automatically",
                     "Supprimer automatiquement l'arrière-plan", "Eliminar el fondo de la imagen automáticamente"),
    "fabric_opt_normal": ("Standard (Baumwolle / Twill / Universal)", "Standard (cotton / twill / universal)",
                          "Standard (coton / sergé / universel)", "Estándar (algodón / sarga / universal)"),
    "fabric_opt_strick": ("Piqué / Polo / Strick (mehr Zugkompensation)",
                          "Piqué / polo / knit (more pull compensation)",
                          "Piqué / polo / maille (plus de compensation de traction)",
                          "Piqué / polo / punto (más compensación de tirón)"),
    "fabric_opt_frottee": ("Frottee / Handtuch (dichter + starke Unterlage)",
                           "Terry / towel (denser + strong underlay)",
                           "Éponge / serviette (plus dense + sous-couche renforcée)",
                           "Rizo / toalla (más denso + refuerzo fuerte)"),
    "fabric_opt_cap": ("Kappe / Cap (hohe Zugkompensation)", "Cap (high pull compensation)",
                       "Casquette (forte compensation de traction)", "Gorra (alta compensación de tirón)"),
    "fabric_opt_leicht": ("Leichter Stoff / Hemd (geringere Dichte)", "Lightweight fabric / shirt (lower density)",
                          "Tissu léger / chemise (densité réduite)", "Tela ligera / camisa (menor densidad)"),
    "lbl_fabric_type": ("Stoffart / Material:", "Fabric / material:", "Type de tissu / matière :",
                        "Tipo de tela / material:"),
    "lbl_density_row": ("Stichdichte (Reihenabstand):", "Stitch density (row spacing):",
                        "Densité de points (espacement des rangs) :", "Densidad de puntada (separación de filas):"),
    "lbl_satin_limit": ("Satin-Grenze (schmaler = Satin):", "Satin limit (narrower = satin):",
                        "Limite satin (plus étroit = satin) :", "Límite satén (más estrecho = satén):"),
    "lbl_min_area": ("Kleinstteile filtern unter:", "Filter out tiny areas below:", "Filtrer les petites zones sous :",
                     "Filtrar zonas diminutas por debajo de:"),
    "cb_outline": ("Zusätzliche Satinkontur um das Motiv legen", "Add a satin outline around the design",
                   "Ajouter un contour en point satin autour du motif",
                   "Añadir un contorno de puntada satén alrededor del diseño"),
    "cb_palette": ("Farben an Stickgarn-Palette anpassen", "Match colors to the thread palette",
                   "Adapter les couleurs à la palette de fils", "Ajustar los colores a la paleta de hilos"),
    "status_ready": ("Bereit.", "Ready.", "Prêt.", "Listo."),
    "btn_digitize_apply": ("Jetzt digitalisieren && übernehmen", "Digitize && apply now",
                           "Numériser && appliquer", "Digitalizar && aplicar ahora"),
    "fd_pick_logo": ("Bild oder Logo wählen (Downloads / Bilder / Desktop)",
                     "Choose an image or logo (Downloads / Pictures / Desktop)",
                     "Choisir une image ou un logo (Téléchargements / Images / Bureau)",
                     "Elegir una imagen o logotipo (Descargas / Imágenes / Escritorio)"),
    "fd_pick_logo_short": ("Bild oder Logo wählen", "Choose an image or logo", "Choisir une image ou un logo",
                           "Elegir una imagen o logotipo"),
    "err_digitize_title": ("Fehler beim Digitalisieren", "Digitizing failed", "Échec de la numérisation",
                           "Error al digitalizar"),
    "prog_computing_stitches": ("Stiche berechnen ({}/{}) …", "Computing stitches ({}/{}) …",
                                "Calcul des points ({}/{}) …", "Calculando puntadas ({}/{}) …"),
    # Fortschrittsmeldungen des Auto-Digitizers (Engine meldet deutsch, Dialog übersetzt)
    "prog_prepare": ("Bild vorbereiten …", "Preparing image …", "Préparation de l'image …", "Preparando imagen …"),
    "prog_reduce": ("Farben reduzieren …", "Reducing colors …", "Réduction des couleurs …", "Reduciendo colores …"),
    "prog_clean": ("Flächen bereinigen …", "Cleaning up areas …", "Nettoyage des zones …", "Limpiando áreas …"),
    "prog_vectorize": ("Konturen vektorisieren …", "Vectorizing contours …", "Vectorisation des contours …",
                       "Vectorizando contornos …"),
    "prog_done": ("Fertig", "Done", "Terminé", "Listo"),
    "prog_classify": ("Fläche {}/{} klassifizieren …", "Classifying area {}/{} …",
                      "Classification de la zone {}/{} …", "Clasificando área {}/{} …"),
    # Schrift / Monogramm
    "dlg_text_title": ("Schrift / Monogramm erstellen", "Create lettering / monogram",
                       "Créer un lettrage / monogramme", "Crear texto / monograma"),
    "lbl_text": ("Text:", "Text:", "Texte :", "Texto:"),
    "lbl_font_file": ("Schriftart (TTF/OTF):", "Font (TTF/OTF):", "Police (TTF/OTF) :", "Fuente (TTF/OTF):"),
    "lbl_letter_height": ("Buchstabenhöhe (Versalhöhe):", "Letter height (cap height):",
                          "Hauteur des lettres (hauteur de capitale) :", "Altura de letra (altura de mayúscula):"),
    "lbl_letter_spacing": ("Zeichenabstand:", "Letter spacing:", "Espacement des lettres :",
                           "Espaciado entre letras:"),
    "sfx_arc": (" mm (0 = gerade)", " mm (0 = straight)", " mm (0 = droit)", " mm (0 = recto)"),
    "lbl_arc_radius": ("Bogenradius:", "Arc radius:", "Rayon de l'arc :", "Radio del arco:"),
    "text_mode_auto": ("Automatisch (Satin bis 7 mm, darüber Tatami)", "Automatic (satin up to 7 mm, tatami above)",
                       "Automatique (satin jusqu'à 7 mm, tatami au-delà)",
                       "Automático (satén hasta 7 mm, tatami por encima)"),
    "text_mode_satin": ("Immer Satinstich (Glanz-Schrift)", "Always satin stitch (glossy lettering)",
                        "Toujours point satin (lettrage brillant)", "Siempre puntada satén (texto brillante)"),
    "text_mode_fill": ("Immer Tatami-Füllstich", "Always tatami fill", "Toujours remplissage tatami",
                       "Siempre relleno tatami"),
    "lbl_stitch_type": ("Stichart:", "Stitch type:", "Type de point :", "Tipo de puntada:"),
    "lbl_stitch_density": ("Stichdichte:", "Stitch density:", "Densité de points :", "Densidad de puntada:"),
    "msg_enter_text": ("Bitte einen Text eingeben.", "Please enter some text.", "Veuillez saisir un texte.",
                       "Introduce un texto."),
    "text_obj_name": ("Text „{}“", "Text “{}”", "Texte « {} »", "Texto «{}»"),
    # Maschinen-Transfer
    "dlg_transfer_title": ("Maschinen-Transfer (USB / 1.44 MB Disketten-Emulator / WLAN NetBridge)",
                           "Machine transfer (USB / 1.44 MB floppy emulator / Wi-Fi NetBridge)",
                           "Transfert machine (USB / émulateur de disquette 1,44 Mo / NetBridge Wi-Fi)",
                           "Transferencia a máquina (USB / emulador de disquete de 1,44 MB / NetBridge Wi-Fi)"),
    "grp_transfer_1": ("1. Maschinen- & Trim-Einstellungen (EXP / Industrie-Format)",
                       "1. Machine & trim settings (EXP / industrial format)",
                       "1. Réglages machine et coupe de fil (EXP / format industriel)",
                       "1. Ajustes de máquina y corte (EXP / formato industrial)"),
    "lbl_dos_name": ("DOS-Dateiname (8.3-Format):", "DOS file name (8.3 format):", "Nom de fichier DOS (format 8.3) :",
                     "Nombre de archivo DOS (formato 8.3):"),
    "trim_both": ("Kombi: EXP-Trim-Code + 3 Sprünge (höchste Kompatibilität)",
                  "Combined: EXP trim code + 3 jumps (highest compatibility)",
                  "Combiné : code de coupe EXP + 3 sauts (compatibilité maximale)",
                  "Combinado: código de corte EXP + 3 saltos (máxima compatibilidad)"),
    "trim_code": ("Standard EXP-Trim-Code (80 80 07 00)", "Standard EXP trim code (80 80 07 00)",
                  "Code de coupe EXP standard (80 80 07 00)", "Código de corte EXP estándar (80 80 07 00)"),
    "trim_jumps": ("Nur Sprungfolge (für ältere EMT-Firmware)", "Jump sequence only (for older EMT firmware)",
                   "Séquence de sauts uniquement (anciens firmwares EMT)",
                   "Solo secuencia de saltos (para firmware EMT antiguo)"),
    "lbl_trim_mode": ("Fadenschnitt (Trim)-Modus:", "Trim mode:", "Mode de coupe de fil :", "Modo de corte:"),
    "grp_transfer_2": ("2. Direkt auf USB-Stick / Laufwerk oder über WLAN-NetBridge senden",
                       "2. Send directly to a USB stick / drive or via Wi-Fi NetBridge",
                       "2. Envoyer directement sur clé USB / lecteur ou via NetBridge Wi-Fi",
                       "2. Enviar directamente a memoria USB / unidad o mediante NetBridge Wi-Fi"),
    "btn_save_exp_usb": ("EXP direkt auf USB-Stick / Ordner speichern …", "Save EXP directly to USB stick / folder …",
                         "Enregistrer l'EXP directement sur clé USB / dossier …",
                         "Guardar EXP directamente en memoria USB / carpeta …"),
    "lbl_netbridge_url": ("NetBridge-URL:", "NetBridge URL:", "URL NetBridge :", "URL de NetBridge:"),
    "btn_send_netbridge": ("Über WLAN an Melco NetBridge senden", "Send to Melco NetBridge via Wi-Fi",
                           "Envoyer à Melco NetBridge via Wi-Fi", "Enviar a Melco NetBridge por Wi-Fi"),
    "grp_transfer_3": ("3. 1.44 MB FAT12-Diskettenabbild (.IMG) für USB-Emulator (GoTek / HxC)",
                       "3. 1.44 MB FAT12 floppy image (.IMG) for USB emulator (GoTek / HxC)",
                       "3. Image de disquette FAT12 1,44 Mo (.IMG) pour émulateur USB (GoTek / HxC)",
                       "3. Imagen de disquete FAT12 de 1,44 MB (.IMG) para emulador USB (GoTek / HxC)"),
    "lbl_img_initial": ("Aktuelles Abbild: Neues leeres 1.44-MB-Abbild (FAT12)",
                        "Current image: new empty 1.44 MB image (FAT12)",
                        "Image actuelle : nouvelle image vide de 1,44 Mo (FAT12)",
                        "Imagen actual: nueva imagen vacía de 1,44 MB (FAT12)"),
    "btn_open_img": ("Bestehendes .IMG öffnen …", "Open existing .IMG …", "Ouvrir un .IMG existant …",
                     "Abrir .IMG existente …"),
    "btn_add_cur_img": ("Aktuelles Design ins Abbild einfügen", "Add current design to image",
                        "Ajouter le motif actuel à l'image", "Añadir el diseño actual a la imagen"),
    "btn_del_file": ("Ausgewählte Datei löschen", "Delete selected file", "Supprimer le fichier sélectionné",
                     "Eliminar el archivo seleccionado"),
    "btn_save_img": (".IMG-Datei speichern …", "Save .IMG file …", "Enregistrer le fichier .IMG …",
                     "Guardar archivo .IMG …"),
    "unit_bytes": ("Bytes", "bytes", "octets", "bytes"),
    "img_new": ("Neues 1.44-MB-Abbild", "New 1.44 MB image", "Nouvelle image 1,44 Mo", "Nueva imagen de 1,44 MB"),
    "img_free": ("{src}  —  Freier Speicher: {free} KB von {total} KB", "{src}  —  Free space: {free} KB of {total} KB",
                 "{src}  —  Espace libre : {free} Ko sur {total} Ko",
                 "{src}  —  Espacio libre: {free} KB de {total} KB"),
    "fd_save_exp": ("Melco EXP speichern", "Save Melco EXP", "Enregistrer Melco EXP", "Guardar Melco EXP"),
    "msg_saved_title": ("Gespeichert", "Saved", "Enregistré", "Guardado"),
    "msg_exp_saved": ("Melco-Stickdatei gespeichert:\n{path}\n({size} Bytes)",
                      "Melco embroidery file saved:\n{path}\n({size} bytes)",
                      "Fichier de broderie Melco enregistré :\n{path}\n({size} octets)",
                      "Archivo de bordado Melco guardado:\n{path}\n({size} bytes)"),
    "msg_wifi_ok_title": ("WLAN-Übertragung erfolgreich", "Wi-Fi transfer successful", "Transfert Wi-Fi réussi",
                          "Transferencia Wi-Fi correcta"),
    "msg_wifi_ok_text": ("Gesendet an {url}:\n{body}", "Sent to {url}:\n{body}", "Envoyé à {url} :\n{body}",
                         "Enviado a {url}:\n{body}"),
    "msg_netbridge_fail_title": ("NetBridge nicht erreichbar", "NetBridge unreachable", "NetBridge injoignable",
                                 "NetBridge no accesible"),
    "msg_netbridge_fail_text": ("Konnte {url} nicht erreichen:\n{err}", "Could not reach {url}:\n{err}",
                                "Impossible de joindre {url} :\n{err}", "No se pudo acceder a {url}:\n{err}"),
    "fd_open_img": ("FAT12-Diskettenabbild öffnen", "Open FAT12 floppy image", "Ouvrir une image de disquette FAT12",
                    "Abrir imagen de disquete FAT12"),
    "fd_save_img": ("1.44 MB FAT12-Diskettenabbild speichern", "Save 1.44 MB FAT12 floppy image",
                    "Enregistrer l'image de disquette FAT12 1,44 Mo", "Guardar imagen de disquete FAT12 de 1,44 MB"),
    "msg_img_saved_title": ("Diskettenabbild gespeichert", "Floppy image saved", "Image de disquette enregistrée",
                            "Imagen de disquete guardada"),
    "msg_img_saved_text": (
        "1.44-MB-FAT12-Abbild gespeichert:\n{path}\n\n"
        "Tipp für GoTek/FlashFloppy: Benenne die Bilder auf dem USB-Stick z. B. DSKA0000.IMG, DSKA0001.IMG "
        "oder kopiere die .EXP-Datei direkt, falls FlashFloppy im Direct-File-Modus läuft.",
        "1.44 MB FAT12 image saved:\n{path}\n\n"
        "Tip for GoTek/FlashFloppy: name the images on the USB stick e.g. DSKA0000.IMG, DSKA0001.IMG, "
        "or copy the .EXP file directly if FlashFloppy runs in direct-file mode.",
        "Image FAT12 de 1,44 Mo enregistrée :\n{path}\n\n"
        "Astuce GoTek/FlashFloppy : nommez les images sur la clé USB p. ex. DSKA0000.IMG, DSKA0001.IMG, "
        "ou copiez directement le fichier .EXP si FlashFloppy fonctionne en mode fichier direct.",
        "Imagen FAT12 de 1,44 MB guardada:\n{path}\n\n"
        "Consejo para GoTek/FlashFloppy: nombra las imágenes en la memoria USB p. ej. DSKA0000.IMG, DSKA0001.IMG, "
        "o copia directamente el archivo .EXP si FlashFloppy funciona en modo de archivo directo.",
    ),
    # PhotoStitch
    "dlg_photo_title": ("PhotoStitch — Porträt- & Foto-Stickerei erzeugen",
                        "PhotoStitch — create portrait & photo embroidery",
                        "PhotoStitch — créer une broderie de portrait et de photo",
                        "PhotoStitch — crear bordado de retrato y foto"),
    "lbl_orig_photo": ("Originalfoto ({})", "Original photo ({})", "Photo d'origine ({})", "Foto original ({})"),
    "btn_other_photo": ("📂 Anderes Foto wählen (Downloads / Desktop / Bilder …)",
                        "📂 Choose another photo (Downloads / Desktop / Pictures …)",
                        "📂 Choisir une autre photo (Téléchargements / Bureau / Images …)",
                        "📂 Elegir otra foto (Descargas / Escritorio / Imágenes …)"),
    "grp_photo_settings": ("PhotoStitch-Einstellungen", "PhotoStitch settings", "Réglages PhotoStitch",
                           "Ajustes de PhotoStitch"),
    "lbl_target_width": ("Zielbreite:", "Target width:", "Largeur cible :", "Ancho objetivo:"),
    "photo_mode_mono": ("Monochrom-Gravur (1 Garnfarbe auf hellem Stoff)",
                        "Monochrome engraving (1 thread color on light fabric)",
                        "Gravure monochrome (1 couleur de fil sur tissu clair)",
                        "Grabado monocromo (1 color de hilo sobre tela clara)"),
    "photo_mode_sepia": ("Sepia-Porträt (2 Garnfarben: Hellbraun + Dunkelbraun)",
                         "Sepia portrait (2 thread colors: light brown + dark brown)",
                         "Portrait sépia (2 couleurs de fil : brun clair + brun foncé)",
                         "Retrato sepia (2 colores de hilo: marrón claro + marrón oscuro)"),
    "photo_mode_color4": ("4-Farb CMYK-Halbton (Gelb, Magenta, Cyan, Schwarz)",
                          "4-color CMYK halftone (yellow, magenta, cyan, black)",
                          "Demi-teinte CMJN 4 couleurs (jaune, magenta, cyan, noir)",
                          "Semitono CMYK de 4 colores (amarillo, magenta, cian, negro)"),
    "lbl_color_mode": ("Farbmodus:", "Color mode:", "Mode couleur :", "Modo de color:"),
    "lbl_row_spacing_fine": ("Zeilenabstand (Feinheit):", "Row spacing (fineness):",
                             "Espacement des lignes (finesse) :", "Separación de líneas (finura):"),
    "lbl_contrast": ("Kontrast-Verstärkung:", "Contrast boost:", "Renforcement du contraste :",
                     "Refuerzo de contraste:"),
    "btn_photo_apply": ("PhotoStitch berechnen && übernehmen", "Compute && apply PhotoStitch",
                        "Calculer && appliquer PhotoStitch", "Calcular && aplicar PhotoStitch"),
})


# ---------------------------------------------------------------------------
# PDF-Produktionsblatt
# ---------------------------------------------------------------------------
_TABLE.update({
    "pdf_title": ("{}  —  Produktions- & Einrichteblatt", "{}  —  Production & setup sheet",
                  "{}  —  Fiche de production et de réglage", "{}  —  Hoja de producción y preparación"),
    "pdf_created": ("Erstellt mit {app} am {date}", "Created with {app} on {date}", "Créé avec {app} le {date}",
                    "Creado con {app} el {date}"),
    "pdf_date_fmt": ("%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M"),
    "pdf_total_stitches": ("Stiche gesamt", "Total stitches", "Points au total", "Puntadas totales"),
    "pdf_size": ("Grösse (B × H)", "Size (W × H)", "Taille (L × H)", "Tamaño (an. × al.)"),
    "pdf_color_changes": ("Farbwechsel / Blöcke", "Color changes / blocks", "Changements de couleur / blocs",
                          "Cambios de color / bloques"),
    "pdf_blocks_val": ("{} ({} Blöcke)", "{} ({} blocks)", "{} ({} blocs)", "{} ({} bloques)"),
    "pdf_trims": ("Fadenschnitte (Trims)", "Thread trims", "Coupes de fil", "Cortes de hilo"),
    "pdf_hoop": ("Stickrahmen", "Hoop", "Cadre", "Bastidor"),
    "pdf_runtime": ("Laufzeit (ca. {} SPM)", "Run time (approx. {} SPM)", "Durée (env. {} SPM)",
                    "Duración (aprox. {} SPM)"),
    "pdf_thread_usage": ("Oberfadenbedarf", "Top thread usage", "Consommation de fil supérieur",
                         "Consumo de hilo superior"),
    "pdf_machine": ("Maschinenprofil", "Machine profile", "Profil machine", "Perfil de máquina"),
    "pdf_sequence": ("Farbfolge & Nadelzuordnung ({} Nadeln)", "Color sequence & needle assignment ({} needles)",
                     "Séquence de couleurs et attribution des aiguilles ({} aiguilles)",
                     "Secuencia de colores y asignación de agujas ({} agujas)"),
})
