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
    "tool_zoom": ("Zoom 100%", "Zoom Fit", "Zoom 100%", "Zoom 100%"),

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


def tr_all(key: str) -> list[str]:
    return list(_TABLE.get(key, (key,) * 4))
