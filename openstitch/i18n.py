"""Mehrsprachige Lokalisierung für OpenStitch Studio.

DE, EN, FR und ES stehen in `_TABLE`. Weitere Sprachen liegen je als eigene Datei in `locales/` und
werden erst geladen, wenn man sie wählt; fehlende Texte fallen auf Englisch zurück."""
from __future__ import annotations

from PySide6.QtCore import QLocale, QSettings

LANGUAGES: list[tuple[str, str]] = [
    ("de", "🇩🇪 Deutsch"),
    ("en", "🇬🇧 English"),
    ("fr", "🇫🇷 Français"),
    ("es", "🇪🇸 Español"),
    ("it", "🇮🇹 Italiano"),
    ("pt", "🇵🇹 Português"),
    ("nl", "🇳🇱 Nederlands"),
    ("pl", "🇵🇱 Polski"),
    ("tr", "🇹🇷 Türkçe"),
]
_SUPPORTED = {code for code, _ in LANGUAGES}
_COLUMN = {"de": 0, "en": 1, "fr": 2, "es": 3}
_extra_cache: dict[str, dict[str, str]] = {}

_cur_lang = ["de"]


def extra_table(lang: str) -> dict[str, str]:
    """Texte einer Sprache aus `locales/`, geladen erst beim ersten Gebrauch."""
    if lang not in _extra_cache:
        from .locales import TABLES
        _extra_cache[lang] = TABLES.get(lang, {})
    return _extra_cache[lang]


def init_lang() -> str:
    s = QSettings("OpenStitch", "OpenStitchStudio")
    lang = s.value("ui/lang", "", type=str) or QLocale.system().name()[:2]
    if lang not in _SUPPORTED:
        lang = "en"     # Beim ersten Start die Sprache des Systems, sonst Englisch
    _cur_lang[0] = lang
    return lang


def current_lang() -> str:
    return _cur_lang[0]


def set_lang(lang: str) -> None:
    if lang in _SUPPORTED:
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
    "tb_auto": ("Bild → Stiche", "Image to stitches", "Image → points", "Imagen a puntadas"),
    "tb_photo": ("PhotoStitch", "PhotoStitch", "PhotoStitch", "PhotoStitch"),
    "tb_text": ("Schrift", "Lettering", "Lettrage", "Texto"),
    "tb_applique": ("Appliqué", "Appliqué", "Appliqué", "Aplique"),
    "tb_puff": ("3D-Puff", "3D-Puff", "3D-Puff", "3D-Puff"),
    "tb_transfer": ("Transfer", "Transfer", "Transfert", "Transferir"),
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
    "dock_palette": ("Garne && Farben", "Threads && Colors", "Fils && couleurs", "Hilos y colores"),
    "lbl_catalog": ("Garnkatalog:", "Thread Catalog:", "Catalogue :", "Catálogo:"),
    "lbl_seq": ("Farb- & Nadel-Sequenz im Design:", "Design Thread & Needle Sequence:", "Séquence de couleurs & aiguilles :", "Secuencia de colores y agujas:"),
    "needle": ("Nadel", "Needle", "Aiguille", "Aguja"),

    # Rechtes Dock (Ebenen & Inspektor)
    "dock_right": ("Ebenen && Einstellungen", "Layers && Settings", "Calques && réglages", "Capas y ajustes"),
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
    lang = _cur_lang[0]
    if lang in _COLUMN:
        return row[_COLUMN[lang]]
    return extra_table(lang).get(key, row[1])


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
    "m_doctor": ("Design prüfen (virtueller Probestick)", "Check design (virtual stitch-out)",
                 "Vérifier le motif (essai virtuel)", "Revisar diseño (prueba virtual)"),
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


_TABLE.update({
    "ph_text": ("Dein Text", "Your text", "Votre texte", "Tu texto"),
    "tip_use_micro": ("Für so kleine Schrift besser „OpenStitch Micro“ verwenden (ein Klick hier)",
                      "For lettering this small, use “OpenStitch Micro” (click here)",
                      "Pour un texte aussi petit, utilisez « OpenStitch Micro » (cliquez ici)",
                      "Para un texto tan pequeño, usa «OpenStitch Micro» (haz clic aquí)"),
})

# Hilfe, Fehlerbericht
_TABLE.update({
    "act_shortcuts": ("Tastenkürzel …", "Keyboard shortcuts …", "Raccourcis clavier …", "Atajos de teclado …"),
    "act_report": ("Problem melden …", "Report a problem …", "Signaler un problème …", "Informar de un problema …"),
    "act_about": ("Über OpenStitch …", "About OpenStitch …", "À propos d'OpenStitch …", "Acerca de OpenStitch …"),
    "about_text": ("Freie Stick- und Digitalisier-Software. Lizenz: AGPL-3.0, der Quellcode ist frei verfügbar.",
                   "Free embroidery and digitizing software. License: AGPL-3.0, the source code is freely available.",
                   "Logiciel libre de broderie et de numérisation. Licence : AGPL-3.0, le code source est librement disponible.",
                   "Software libre de bordado y digitalización. Licencia: AGPL-3.0, el código fuente está disponible."),
    "keys_title": ("Tastenkürzel", "Keyboard shortcuts", "Raccourcis clavier", "Atajos de teclado"),
    "key_select": ("Auswählen und verschieben", "Select and move", "Sélectionner et déplacer", "Seleccionar y mover"),
    "key_nodes": ("Knoten bearbeiten", "Edit nodes", "Modifier les nœuds", "Editar nodos"),
    "key_fill": ("Fläche zeichnen", "Draw fill", "Dessiner un remplissage", "Dibujar relleno"),
    "key_satin": ("Satinsäule zeichnen", "Draw satin column", "Dessiner une colonne satin", "Dibujar columna de satén"),
    "key_run": ("Steppstich zeichnen", "Draw running stitch", "Dessiner un point droit", "Dibujar puntada recta"),
    "key_finish": ("Zeichnen beenden", "Finish drawing", "Terminer le dessin", "Terminar el dibujo"),
    "key_cancel": ("Zeichnen abbrechen", "Cancel drawing", "Annuler le dessin", "Cancelar el dibujo"),
    "key_zoom": ("Zoomen", "Zoom", "Zoomer", "Ampliar"),
    "key_pan": ("Ansicht verschieben", "Pan the view", "Déplacer la vue", "Desplazar la vista"),
    "key_wheel": ("Mausrad", "Mouse wheel", "Molette", "Rueda del ratón"),
    "key_middle": ("Mittlere Maustaste", "Middle mouse button", "Bouton central", "Botón central"),
    "crash_title": ("Das hätte nicht passieren dürfen", "That should not have happened", "Cela n'aurait pas dû arriver",
                    "Esto no debería haber pasado"),
    "crash_text": ("OpenStitch hat einen Fehler bemerkt. Deine Arbeit wurde gesichert und du kannst weitermachen.\n\n"
                   "Wenn du das Problem melden möchtest, hänge bitte diese Datei an:\n{}",
                   "OpenStitch ran into an error. Your work was saved and you can carry on.\n\n"
                   "If you would like to report it, please attach this file:\n{}",
                   "OpenStitch a rencontré une erreur. Votre travail a été sauvegardé et vous pouvez continuer.\n\n"
                   "Pour la signaler, joignez ce fichier :\n{}",
                   "OpenStitch encontró un error. Tu trabajo se guardó y puedes continuar.\n\n"
                   "Si quieres informar del problema, adjunta este archivo:\n{}"),
})

# An die Maschine senden
_TABLE.update({
    "exp_title": ("An die Maschine senden", "Send to machine", "Envoyer à la machine", "Enviar a la máquina"),
    "exp_heading": ("Fertig zum Sticken?", "Ready to stitch?", "Prêt à broder ?", "¿Listo para bordar?"),
    "exp_facts": ("{st} Stiche · {colors} Farben · {w} × {h} mm", "{st} stitches · {colors} colors · {w} × {h} mm",
                  "{st} points · {colors} couleurs · {w} × {h} mm", "{st} puntadas · {colors} colores · {w} × {h} mm"),
    "exp_format": ("Dateiformat:", "File format:", "Format de fichier :", "Formato de archivo:"),
    "exp_recommended": ("{} (empfohlen)", "{} (recommended)", "{} (recommandé)", "{} (recomendado)"),
    "exp_name": ("Dateiname:", "File name:", "Nom du fichier :", "Nombre de archivo:"),
    "exp_short": ("Kurzer Name für ältere Maschinen", "Short name for older machines",
                  "Nom court pour machines anciennes", "Nombre corto para máquinas antiguas"),
    "exp_short_tip": ("Viele ältere Maschinen zeigen nur 8 Zeichen ohne Umlaute an.",
                      "Many older machines only show 8 plain characters.",
                      "Beaucoup de machines anciennes n'affichent que 8 caractères simples.",
                      "Muchas máquinas antiguas solo muestran 8 caracteres simples."),
    "exp_where": ("Speichern auf:", "Save to:", "Enregistrer sur :", "Guardar en:"),
    "exp_usb": ("USB-Stick: {}", "USB stick: {}", "Clé USB : {}", "Memoria USB: {}"),
    "exp_browse": ("Ordner …", "Folder …", "Dossier …", "Carpeta …"),
    "exp_refresh": ("Aktualisieren", "Refresh", "Actualiser", "Actualizar"),
    "exp_threads": ("Garnfolge für die Maschine", "Thread order for the machine", "Ordre des fils pour la machine",
                    "Orden de hilos para la máquina"),
    "exp_save": ("Speichern", "Save", "Enregistrer", "Guardar"),
    "exp_done": ("„{name}“ gespeichert und geprüft: {st} Stiche korrekt gelesen. Jetzt den Stick an die Maschine stecken.",
                 "“{name}” saved and verified: {st} stitches read back correctly. Now plug the stick into your machine.",
                 "« {name} » enregistré et vérifié : {st} points relus correctement. Branchez la clé sur la machine.",
                 "«{name}» guardado y verificado: {st} puntadas leídas correctamente. Conecta la memoria a la máquina."),
    "exp_overwrite": ("„{}“ gibt es dort schon. Ersetzen?", "“{}” already exists there. Replace it?",
                      "« {} » existe déjà à cet endroit. Le remplacer ?", "«{}» ya existe ahí. ¿Reemplazarlo?"),
    "exp_done_plain": ("„{name}“ gespeichert.", "“{name}” saved.", "« {name} » enregistré.", "«{name}» guardado."),
    "exp_failed": ("Speichern fehlgeschlagen: {}", "Could not save: {}", "Échec de l'enregistrement : {}",
                   "No se pudo guardar: {}"),
    "btn_close": ("Schliessen", "Close", "Fermer", "Cerrar"),
})

# Feste Regeln, Schätzungen und Kalibrierung
_TABLE.update({
    'chk_tag_rule': ('Feste Regel',
        'Fixed rule',
        'Règle fixe',
        'Regla fija'),
    'chk_tag_model': ('Schätzung',
        'Estimate',
        'Estimation',
        'Estimación'),
    'cal_open': ('Mit echtem Stoff kalibrieren …',
        'Calibrate with real fabric …',
        'Calibrer avec du vrai tissu …',
        'Calibrar con tela real …'),
    'cal_title': ('Stoff kalibrieren',
        'Calibrate fabric',
        'Calibrer le tissu',
        'Calibrar tela'),
    'cal_intro': ('1. Testbalken laden und mit Stoff, Vlies und Fadenspannung sticken, die du wirklich verwendest.\n2. Breite in der Mitte des Balkens messen. Geplant sind {width} mm.\n3. Messwert eintragen. Simulation und Zugausgleich rechnen dann mit deinem echten Wert.',
        '1. Load the test bar and stitch it with the fabric, stabilizer and tension you really use.\n2. Measure the width in the middle of the bar. It is planned at {width} mm.\n3. Enter the measurement. The simulation and pull compensation then use your real value.',
        '1. Chargez la barre de test et brodez-la avec le tissu, le stabilisateur et la tension que vous utilisez vraiment.\n2. Mesurez la largeur au milieu de la barre. Elle est prévue à {width} mm.\n3. Saisissez la mesure. La simulation et la compensation utilisent alors votre valeur réelle.',
        '1. Carga la barra de prueba y bórdala con la tela, el estabilizador y la tensión que usas de verdad.\n2. Mide el ancho en el centro de la barra. Está prevista de {width} mm.\n3. Introduce la medida. La simulación y la compensación usarán tu valor real.'),
    'cal_load': ('Testbalken laden',
        'Load test bar',
        'Charger la barre de test',
        'Cargar barra de prueba'),
    'cal_measured': ('Gemessene Breite:',
        'Measured width:',
        'Largeur mesurée :',
        'Ancho medido:'),
    'cal_apply': ('Übernehmen',
        'Apply',
        'Appliquer',
        'Aplicar'),
    'cal_reset': ('Zurücksetzen',
        'Reset',
        'Réinitialiser',
        'Restablecer'),
    'cal_state_estimate': ('Dieser Stoff ist noch nicht gemessen: Der Stoffzug ist eine Schätzung.',
        'This fabric has not been measured yet: fabric pull is an estimate.',
        "Ce tissu n'a pas encore été mesuré : la traction est une estimation.",
        'Esta tela aún no se ha medido: el tiro es una estimación.'),
    'cal_state_measured': ('Gemessen: Der Stoffzug ist das {factor}-Fache der Schätzung.',
        'Measured: fabric pull is {factor} times the estimate.',
        "Mesuré : la traction vaut {factor} fois l'estimation.",
        'Medido: el tiro es {factor} veces la estimación.'),
    'chk_disclaimer': ('Feste Regeln folgen exakt aus den Stichen. Schätzungen zum Stoffzug werden genau, wenn du den Stoff kalibrierst.',
        'Fixed rules follow exactly from the stitches. Fabric pull estimates become accurate once you calibrate the fabric.',
        'Les règles fixes découlent exactement des points. Les estimations de traction deviennent précises une fois le tissu calibré.',
        'Las reglas fijas se derivan exactamente de las puntadas. Las estimaciones del tiro son precisas al calibrar la tela.'),
})

# Design-Prüfung (virtueller Probestick)
_TABLE.update({
    "chk_title": ("Design prüfen", "Check design", "Vérifier le motif", "Revisar diseño"),
    "chk_running": ("Wird geprüft …", "Checking …", "Vérification …", "Revisando …"),
    "chk_failed": ("Prüfung fehlgeschlagen", "Check failed", "Échec de la vérification", "Falló la revisión"),
    "chk_empty": ("Noch keine Stiche", "No stitches yet", "Aucun point pour l'instant", "Aún no hay puntadas"),
    "chk_again": ("Erneut prüfen", "Check again", "Vérifier à nouveau", "Revisar de nuevo"),
    "chk_good": ("Bereit zum Sticken", "Ready to stitch", "Prêt à broder", "Listo para bordar"),
    "chk_ok": ("Stickbar, mit kleinen Risiken", "Stitchable, with small risks", "Brodable, avec de petits risques",
               "Bordable, con pequeños riesgos"),
    "chk_bad": ("Besser zuerst überarbeiten", "Better fix this first", "À corriger d'abord", "Mejor corregirlo antes"),
    "chk_none": ("Keine Probleme gefunden.", "No problems found.", "Aucun problème détecté.",
                 "No se encontraron problemas."),
    "chk_facts": ("{st} Stiche · {colors} Farben · {trims} Fadenschnitte · ca. {min} Min. · {thread} m Garn",
                  "{st} stitches · {colors} colors · {trims} trims · about {min} min · {thread} m thread",
                  "{st} points · {colors} couleurs · {trims} coupes · env. {min} min · {thread} m de fil",
                  "{st} puntadas · {colors} colores · {trims} cortes · aprox. {min} min · {thread} m de hilo"),
    "chk_preview": ("So zieht sich der Stoff zusammen", "How the fabric will pull in",
                    "Comment le tissu va se resserrer", "Cómo se encogerá la tela"),
    "chk_boost": ("Effekt verstärken", "Exaggerate effect", "Amplifier l'effet", "Exagerar el efecto"),
    "chk_show": ("Zeigen", "Show", "Afficher", "Mostrar"),
    "chk_fix": ("Beheben", "Fix", "Corriger", "Corregir"),
    "undo_fix": ("Automatische Korrektur", "Automatic fix", "Correction automatique", "Corrección automática"),
    "chk_sev_error": ("Problem", "Problem", "Problème", "Problema"),
    "chk_sev_warning": ("Warnung", "Warning", "Avertissement", "Aviso"),
    "chk_sev_info": ("Hinweis", "Note", "Remarque", "Nota"),
    "chk_short_stitch_t": ("Sehr kurze Stiche", "Very short stitches", "Points très courts", "Puntadas muy cortas"),
    "chk_short_stitch_d": ("Anzahl unter 0,3 mm: {count}. Die Nadel trifft fast dasselbe Loch, der Faden kann reissen.",
                           "Stitches under 0.3 mm: {count}. The needle nearly hits the same hole and the thread can break.",
                           "Points de moins de 0,3 mm : {count}. L'aiguille repique presque au même endroit et le fil peut casser.",
                           "Puntadas de menos de 0,3 mm: {count}. La aguja casi repite el agujero y el hilo puede romperse."),
    "chk_over_max_stitch_t": ("Stiche zu lang für die Maschine", "Stitches too long for the machine",
                              "Points trop longs pour la machine", "Puntadas demasiado largas para la máquina"),
    "chk_over_max_stitch_d": ("{count} Stiche überschreiten die Maschinengrenze (längster: {max_mm} mm).",
                              "{count} stitches exceed the machine limit (longest: {max_mm} mm).",
                              "{count} points dépassent la limite de la machine (le plus long : {max_mm} mm).",
                              "{count} puntadas superan el límite de la máquina (la más larga: {max_mm} mm)."),
    "chk_long_float_t": ("Lange lose Stiche", "Long loose stitches", "Longs points lâches", "Puntadas largas y sueltas"),
    "chk_long_float_d": ("{count} Stiche sind länger als 7,5 mm (bis {max_mm} mm). Sie bleiben im Alltag leicht hängen.",
                         "{count} stitches are longer than 7.5 mm (up to {max_mm} mm). They snag easily in daily use.",
                         "{count} points dépassent 7,5 mm (jusqu'à {max_mm} mm). Ils s'accrochent facilement à l'usage.",
                         "{count} puntadas superan 7,5 mm (hasta {max_mm} mm). Se enganchan fácilmente con el uso."),
    "chk_no_lock_t": ("Fadenenden nicht vernäht", "Thread ends not locked", "Extrémités de fil non arrêtées",
                      "Extremos de hilo sin rematar"),
    "chk_no_lock_d": ("An {count} Stellen fehlen Vernähstiche. Dort kann sich die Stickerei beim Waschen lösen.",
                      "{count} places have no lock stitches. The embroidery can come loose there when washed.",
                      "{count} endroits sans points d'arrêt. La broderie peut s'y défaire au lavage.",
                      "{count} lugares sin puntadas de remate. El bordado puede soltarse ahí al lavarlo."),
    "chk_orphan_run_t": ("Zu kurze Abschnitte", "Sections too short", "Sections trop courtes", "Secciones demasiado cortas"),
    "chk_orphan_run_d": ("{count} Abschnitte haben weniger als 3 Stiche und halten nach dem Fadenschnitt kaum.",
                         "{count} sections have fewer than 3 stitches and barely hold after the thread is cut.",
                         "{count} sections ont moins de 3 points et tiennent mal après la coupe du fil.",
                         "{count} secciones tienen menos de 3 puntadas y apenas aguantan tras cortar el hilo."),
    "chk_untrimmed_jump_t": ("Sprünge ohne Fadenschnitt", "Jumps without a trim", "Sauts sans coupe de fil",
                             "Saltos sin corte de hilo"),
    "chk_untrimmed_jump_d": ("{count} Sprünge lassen einen Faden quer über dem Motiv liegen.",
                             "{count} jumps leave a thread lying across the design.",
                             "{count} sauts laissent un fil en travers du motif.",
                             "{count} saltos dejan un hilo cruzando el diseño."),
    "chk_needle_pileup_t": ("Zu viele Einstiche an einem Punkt", "Too many needle hits in one spot",
                            "Trop de piqûres au même endroit", "Demasiadas puntadas en un punto"),
    "chk_needle_pileup_d": ("An {count} Stellen sticht die Nadel bis zu {max_hits}-mal ein. Das kann Stoff und Nadel beschädigen.",
                            "In {count} places the needle hits up to {max_hits} times. This can damage fabric and needle.",
                            "À {count} endroits l'aiguille pique jusqu'à {max_hits} fois. Cela peut abîmer le tissu et l'aiguille.",
                            "En {count} lugares la aguja entra hasta {max_hits} veces. Puede dañar la tela y la aguja."),
    "chk_too_dense_t": ("Zu dicht gestickt", "Stitched too densely", "Broderie trop dense", "Bordado demasiado denso"),
    "chk_too_dense_d": ("An {count} mm² liegen bis zu {peak} Fadenlagen (Grenze für diesen Stoff: {limit}). Die Stelle wird brettartig.",
                        "{count} mm² carry up to {peak} thread layers (limit for this fabric: {limit}). The area turns board-stiff.",
                        "{count} mm² portent jusqu'à {peak} couches de fil (limite pour ce tissu : {limit}). La zone devient rigide.",
                        "{count} mm² llevan hasta {peak} capas de hilo (límite de esta tela: {limit}). La zona queda rígida."),
    "chk_outside_hoop_t": ("Motiv passt nicht in den Rahmen", "Design does not fit the hoop",
                           "Le motif ne tient pas dans le cadre", "El diseño no cabe en el bastidor"),
    "chk_outside_hoop_d": ("Stiche liegen im Randbereich des Rahmens. Die Nadel kann den Rahmen treffen.",
                           "Stitches lie in the edge zone of the hoop. The needle could hit the hoop.",
                           "Des points se trouvent en bordure du cadre. L'aiguille pourrait le toucher.",
                           "Hay puntadas en el borde del bastidor. La aguja podría golpearlo."),
    "chk_low_coverage_t": ("Stoff scheint durch", "Fabric shows through", "Le tissu transparaît", "Se ve la tela"),
    "chk_low_coverage_d": ("„{object}“ ist nur zu {percent} % bedeckt.", "“{object}” is only {percent}% covered.",
                           "« {object} » n'est couvert qu'à {percent} %.", "«{object}» solo está cubierto al {percent} %."),
    "chk_too_many_colors_t": ("Mehr Farben als Nadeln", "More colors than needles", "Plus de couleurs que d'aiguilles",
                              "Más colores que agujas"),
    "chk_too_many_colors_d": ("{count} Farben bei {needles} Nadeln: Du musst unterwegs den Faden wechseln.",
                              "{count} colors on {needles} needles: you will change thread along the way.",
                              "{count} couleurs pour {needles} aiguilles : il faudra changer de fil en cours de route.",
                              "{count} colores con {needles} agujas: tendrás que cambiar de hilo durante el bordado."),
    "chk_registration_gap_t": ("Lücken zwischen Objekten möglich", "Gaps between objects are likely",
                               "Risque d'espaces entre les objets", "Posibles huecos entre objetos"),
    "chk_registration_gap_d": ("Der Stoffzug verschiebt Teile um bis zu {mm} mm gegeneinander. Mehr Zugausgleich hilft.",
                               "Fabric pull shifts parts by up to {mm} mm against each other. More pull compensation helps.",
                               "La traction du tissu décale des parties jusqu'à {mm} mm. Plus de compensation aide.",
                               "El tiro de la tela desplaza partes hasta {mm} mm. Más compensación ayuda."),
    "chk_puckering_t": ("Stoff kann Wellen werfen", "Fabric may pucker", "Le tissu peut godailler", "La tela puede fruncirse"),
    "chk_puckering_d": ("Die Stickerei zieht den Stoff um rund {mm} mm zusammen. Verwende ein festeres Vlies.",
                        "The embroidery pulls the fabric in by about {mm} mm. Use a firmer stabilizer.",
                        "La broderie resserre le tissu d'environ {mm} mm. Utilisez un stabilisateur plus ferme.",
                        "El bordado encoge la tela unos {mm} mm. Usa un estabilizador más firme."),
    "chk_small_text_t": ("Schrift zu klein für diese Schriftart", "Lettering too small for this font",
                         "Texte trop petit pour cette police", "Texto demasiado pequeño para esta fuente"),
    "chk_small_text_d": ("„{object}“ ist {mm} mm hoch. Umriss-Schriften laufen so klein zu. Nimm „OpenStitch Micro“.",
                         "“{object}” is {mm} mm tall. Outline fonts fill in at this size. Use “OpenStitch Micro”.",
                         "« {object} » mesure {mm} mm. Les polices à contour se bouchent à cette taille. Utilisez « OpenStitch Micro ».",
                         "«{object}» mide {mm} mm. Las fuentes de contorno se cierran a este tamaño. Usa «OpenStitch Micro»."),
    "chk_export_ok_t": ("{ext}-Datei geprüft", "{ext} file verified", "Fichier {ext} vérifié", "Archivo {ext} verificado"),
    "chk_export_ok_d": ("{st} Stiche neu eingelesen, grösste Abweichung {err} mm.",
                        "{st} stitches read back, largest error {err} mm.",
                        "{st} points relus, écart maximal {err} mm.",
                        "{st} puntadas releídas, desviación máxima {err} mm."),
    "chk_export_bad_t": ("Problem in der {ext}-Datei", "Problem in the {ext} file", "Problème dans le fichier {ext}",
                         "Problema en el archivo {ext}"),
})

# Startseite, Stoffe, neue Oberfläche
_TABLE.update({
    "tb_open": ("Öffnen", "Open", "Ouvrir", "Abrir"),
    "tb_save": ("Speichern", "Save", "Enregistrer", "Guardar"),
    "tb_check": ("Prüfen", "Check", "Vérifier", "Revisar"),
    "act_home": ("Startseite anzeigen", "Show start page", "Afficher la page d'accueil", "Mostrar página de inicio"),
    "act_theme_dark": ("Dunkles Design", "Dark theme", "Thème sombre", "Tema oscuro"),
    "act_theme_light": ("Helles Design", "Light theme", "Thème clair", "Tema claro"),
    "menu_recent": ("Zuletzt geöffnet", "Open recent", "Fichiers récents", "Abrir reciente"),
    "lbl_fabric": ("Stoff:", "Fabric:", "Tissu :", "Tela:"),
    "fab_woven": ("Baumwolle / Hemd (gewebt)", "Cotton / shirt (woven)", "Coton / chemise (tissé)",
                  "Algodón / camisa (tejido)"),
    "fab_denim": ("Jeans / Canvas", "Denim / canvas", "Denim / toile", "Vaquero / lona"),
    "fab_twill_cap": ("Kappe (Twill)", "Cap (twill)", "Casquette (sergé)", "Gorra (sarga)"),
    "fab_pique": ("Polo-Piqué", "Polo piqué", "Piqué polo", "Piqué de polo"),
    "fab_jersey": ("T-Shirt (Jersey)", "T-shirt (jersey)", "T-shirt (jersey)", "Camiseta (punto)"),
    "fab_fleece": ("Fleece / Sweatshirt", "Fleece / sweatshirt", "Polaire / sweat", "Polar / sudadera"),
    "fab_towel": ("Frottee / Handtuch", "Terry / towel", "Éponge / serviette", "Rizo / toalla"),
    "fab_leather": ("Leder", "Leather", "Cuir", "Cuero"),
    "fab_silk": ("Seide / feiner Stoff", "Silk / fine fabric", "Soie / tissu fin", "Seda / tela fina"),
    "stab_cutaway": ("Schneidvlies", "cut-away stabilizer", "stabilisateur à découper", "estabilizador recortable"),
    "stab_tearaway": ("Reissvlies", "tear-away stabilizer", "stabilisateur à déchirer", "estabilizador desprendible"),
    "stab_none": ("kein Vlies", "no stabilizer", "pas de stabilisateur", "sin estabilizador"),
    "fabric_advice": ("{fabric}: {stabilizer} verwenden, Nadel {needle}. Dichte und Zugausgleich sind angepasst.",
                      "{fabric}: use {stabilizer}, needle {needle}. Density and pull compensation are adjusted.",
                      "{fabric} : utilisez un {stabilizer}, aiguille {needle}. Densité et compensation ajustées.",
                      "{fabric}: usa {stabilizer}, aguja {needle}. Densidad y compensación ajustadas."),
    "fabric_topping": ("Obenauf wasserlösliche Folie legen, damit die Stiche nicht einsinken.",
                       "Put water-soluble topping on top so stitches do not sink in.",
                       "Posez un film soluble dessus pour que les points ne s'enfoncent pas.",
                       "Coloca film soluble encima para que las puntadas no se hundan."),
    "tip_obj_visible": ("Objekt ein- oder ausblenden", "Show or hide object", "Afficher ou masquer l'objet",
                        "Mostrar u ocultar objeto"),
    "tip_obj_copy": ("Objekt duplizieren", "Duplicate object", "Dupliquer l'objet", "Duplicar objeto"),
    "param_knockout": ("Verdecktes nicht sticken", "Skip hidden parts", "Ignorer les parties cachées",
                       "Omitir partes ocultas"),
    "canvas_empty_hint": ("Bild hierher ziehen oder links ein Zeichenwerkzeug wählen",
                          "Drop an image here or pick a drawing tool on the left",
                          "Déposez une image ici ou choisissez un outil de dessin à gauche",
                          "Suelta una imagen aquí o elige una herramienta de dibujo a la izquierda"),
    "start_title": ("Was möchtest du sticken?", "What would you like to embroider?",
                    "Que souhaitez-vous broder ?", "¿Qué te gustaría bordar?"),
    "start_subtitle": ("Wähle einen Einstieg. Du brauchst keine Vorkenntnisse.",
                       "Pick a starting point. No experience needed.",
                       "Choisissez un point de départ. Aucune expérience requise.",
                       "Elige un punto de partida. No necesitas experiencia."),
    "start_image": ("Bild in Stickerei umwandeln", "Turn an image into embroidery", "Transformer une image en broderie",
                    "Convertir una imagen en bordado"),
    "start_image_d": ("Logo oder Zeichnung wählen, den Rest erledigt OpenStitch.",
                      "Pick a logo or drawing and OpenStitch does the rest.",
                      "Choisissez un logo ou un dessin, OpenStitch fait le reste.",
                      "Elige un logotipo o dibujo y OpenStitch hará el resto."),
    "start_text": ("Text sticken", "Embroider text", "Broder du texte", "Bordar texto"),
    "start_text_d": ("Name oder Schriftzug, sauber lesbar ab 2,5 mm Höhe.",
                     "A name or slogan, cleanly readable from 2.5 mm tall.",
                     "Un nom ou un slogan, lisible dès 2,5 mm de haut.",
                     "Un nombre o lema, legible desde 2,5 mm de alto."),
    "start_draw": ("Selbst zeichnen", "Draw it yourself", "Dessiner vous-même", "Dibujar tú mismo"),
    "start_draw_d": ("Flächen, Satinsäulen und Linien mit der Maus zeichnen.",
                     "Draw fills, satin columns and lines with the mouse.",
                     "Dessinez des remplissages, colonnes satin et lignes à la souris.",
                     "Dibuja rellenos, columnas de satén y líneas con el ratón."),
    "start_open": ("Datei öffnen", "Open a file", "Ouvrir un fichier", "Abrir un archivo"),
    "start_open_d": ("Projekt, Stickdatei (DST, PES, JEF …), SVG oder Bild.",
                     "Project, embroidery file (DST, PES, JEF …), SVG or image.",
                     "Projet, fichier de broderie (DST, PES, JEF …), SVG ou image.",
                     "Proyecto, archivo de bordado (DST, PES, JEF …), SVG o imagen."),
    "start_samples": ("Oder mit einem Beispiel anfangen", "Or start from an example",
                      "Ou commencez par un exemple", "O empieza con un ejemplo"),
    "start_recent": ("Zuletzt geöffnet", "Recent files", "Fichiers récents", "Archivos recientes"),
    "start_tour": ("Kurze Einführung ansehen", "Take a short tour", "Suivre une courte visite",
                   "Ver una breve introducción"),
    "sample_patch": ("Namensschild", "Name patch", "Écusson prénom", "Parche con nombre"),
    "sample_heart": ("Herz", "Heart", "Cœur", "Corazón"),
    "sample_flower": ("Blume", "Flower", "Fleur", "Flor"),
    "sample_monogram": ("Monogramm", "Monogram", "Monogramme", "Monograma"),
    "fd_open_any": ("Datei öffnen", "Open file", "Ouvrir un fichier", "Abrir archivo"),
    "filter_supported": ("Alle unterstützten Dateien", "All supported files", "Tous les fichiers pris en charge",
                         "Todos los archivos compatibles"),
    "err_file_gone": ("Die Datei wurde nicht gefunden:\n{}", "The file was not found:\n{}",
                      "Fichier introuvable :\n{}", "No se encontró el archivo:\n{}"),
    "err_unknown_type": ("„{}“ hat einen Dateityp, den OpenStitch nicht kennt.",
                         "“{}” has a file type OpenStitch does not know.",
                         "« {} » a un type de fichier inconnu d'OpenStitch.",
                         "«{}» tiene un tipo de archivo que OpenStitch no conoce."),
    "dlg_recover_title": ("Arbeit wiederherstellen?", "Restore your work?", "Restaurer votre travail ?",
                          "¿Restaurar tu trabajo?"),
    "dlg_recover_text": ("OpenStitch wurde nicht sauber beendet. Möchtest du die letzte automatische Sicherung öffnen?",
                         "OpenStitch did not close properly. Open the last automatic backup?",
                         "OpenStitch ne s'est pas fermé correctement. Ouvrir la dernière sauvegarde automatique ?",
                         "OpenStitch no se cerró correctamente. ¿Abrir la última copia automática?"),
    "status_autosave_failed": ("Automatisches Speichern fehlgeschlagen: {}", "Autosave failed: {}",
                               "Échec de l'enregistrement automatique : {}", "Falló el guardado automático: {}"),
})

# Fehlermeldungen beim Laden
_TABLE.update({
    "err_project_damaged": (
        "„{name}“ ist beschädigt oder keine OpenStitch-Projektdatei.",
        "“{name}” is damaged or not an OpenStitch project file.",
        "« {name} » est endommagé ou n'est pas un fichier de projet OpenStitch.",
        "«{name}» está dañado o no es un archivo de proyecto de OpenStitch."),
})

def tr_all(key: str) -> list[str]:
    return list(_TABLE.get(key, (key,) * 4))


def tr_opt(key: str, fallback: str) -> str:
    """Wie tr(), aber mit eigenem Rückfallwert, falls der Schlüssel fehlt."""
    return tr(key) if key in _TABLE else fallback


# Zahlenformat je Sprache: Tausendertrennzeichen und Dezimalzeichen
# (de: Schweizer Apostroph, fr: schmales geschütztes Leerzeichen)
_GROUP_SEP = {"de": "’", "en": ",", "fr": " ", "es": ".", "it": ".", "pt": "\u00a0", "nl": ".", "pl": "\u00a0", "tr": "."}
_DEC_SEP = {"de": ".", "en": ".", "fr": ",", "es": ",", "it": ",", "pt": ",", "nl": ",", "pl": ",", "tr": ","}


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

from .i18n_tour import TOUR_TABLE  # noqa: E402
_TABLE.update(TOUR_TABLE)
