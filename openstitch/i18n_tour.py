"""Übersetzungen des Studio-Rundgangs (DE, EN, FR, ES).

Eigene Datei, damit die langen Rundgang-Texte i18n.py nicht aufblähen. Die Tabelle wird am Ende von
i18n.py in `_TABLE` übernommen. Die Texte sind Rich Text: `<b>` & Co. sind erlaubt, ein `&` im Fliesstext
wird als `&amp;` geschrieben. Bezeichnungen wie "Prüfen" müssen zu den Knöpfen der Oberfläche passen.
"""
from __future__ import annotations

TOUR_TABLE: dict[str, tuple[str, str, str, str]] = {
    # Gemeinsame Bedienelemente
    "tour_next": ("Weiter →", "Next →", "Suivant →", "Siguiente →"),
    "tour_prev_tip": ("Vorheriger Schritt", "Previous step", "Étape précédente", "Paso anterior"),
    "tour_close_tip": ("Rundgang schliessen (Esc)", "Close the tour (Esc)", "Fermer la visite (Échap)",
                       "Cerrar la guía (Esc)"),
    "tour_on_start": ("Beim Start", "At startup", "Au démarrage", "Al iniciar"),
    "tour_done": ("Fertig ✓", "Done ✓", "Terminé ✓", "Listo ✓"),

    # Rundgang als eigenes Fenster






    # Rundgang direkt im Hauptfenster
    "tour_app_1_badge": ("WILLKOMMEN · 1 / 7", "WELCOME · 1 / 7", "BIENVENUE · 1 / 7", "BIENVENIDA · 1 / 7"),
    "tour_app_1_title": ("Die Leinwand: dein Design in 3D", "The canvas: your design in 3D",
                         "Le canevas : votre motif en 3D", "El lienzo: tu diseño en 3D"),
    "tour_app_1_body": (
        "In der Mitte liegt dein Design im Stickrahmen, zum Start unser <b>OpenStitch-Wappen</b>.<br><br>"
        "• <b>Klicken und ziehen:</b> Objekte auswählen, verschieben oder am Eckgriff skalieren.<br>"
        "• <b>Mausrad:</b> Stufenlos bis auf einzelne Einstiche hineinzoomen.",
        "Your design sits in the hoop in the middle. To start with, that is our "
        "<b>OpenStitch crest</b>.<br><br>"
        "• <b>Click and drag:</b> select parts, move them, or resize them with the corner handle.<br>"
        "• <b>Mouse wheel:</b> zoom in smoothly, right down to single stitches.",
        "Votre motif apparaît au centre, dans le cadre. Pour commencer, c'est notre "
        "<b>blason OpenStitch</b>.<br><br>"
        "• <b>Cliquer et glisser :</b> sélectionnez des éléments, déplacez-les ou redimensionnez-les avec "
        "la poignée d'angle.<br>"
        "• <b>Molette de la souris :</b> zoomez en douceur jusqu'à voir chaque point.",
        "Tu diseño aparece en el centro, dentro del bastidor. Para empezar, es nuestro "
        "<b>escudo de OpenStitch</b>.<br><br>"
        "• <b>Clic y arrastrar:</b> selecciona partes, muévelas o cambia su tamaño con el tirador de la "
        "esquina.<br>"
        "• <b>Rueda del ratón:</b> acerca la vista poco a poco hasta ver cada puntada.",
    ),
    "tour_app_1_action": ("🎨 Stofffarbe im Rahmen testen (Dunkel / Sand / Hell)",
                          "🎨 Try a fabric color in the hoop (dark / sand / light)",
                          "🎨 Essayer une couleur de tissu (sombre / sable / clair)",
                          "🎨 Probar un color de tela (oscuro / arena / claro)"),

    "tour_app_2_badge": ("ÜBER DER LEINWAND · 2 / 7", "ABOVE THE CANVAS · 2 / 7", "AU-DESSUS DU CANEVAS · 2 / 7",
                         "ENCIMA DEL LIENZO · 2 / 7"),
    "tour_app_2_title": ("Maschine, Stickrahmen und Stoff", "Machine, hoop and fabric", "Machine, cadre et tissu",
                         "Máquina, bastidor y tela"),
    "tour_app_2_body": (
        "Direkt über der Leinwand sagst du OpenStitch, worauf gestickt wird:<br><br>"
        "• <b>Maschine:</b> Universal, Tajima, Brother, Barudan, Melco …<br>"
        "• <b>Stickrahmen:</b> Je nach Grösse passt OpenStitch Unterlage und Zugkompensation automatisch an, "
        "z. B. <i>Anti-Trampolin</i> bei grossen Rahmen oder <i>Center-Out und Bottom-Up</i> bei Kappen.<br>"
        "• <b>Stoff:</b> Passt Dichte und Zugausgleich an und empfiehlt dir Vlies und Nadel.",
        "Right above the canvas you tell OpenStitch what you are stitching on:<br><br>"
        "• <b>Machine:</b> Universal, Tajima, Brother, Barudan, Melco …<br>"
        "• <b>Hoop:</b> OpenStitch adjusts the underlay and pull compensation to the size. Large hoops get "
        "extra support against bouncing, and caps are stitched from the center outward and from the "
        "brim upward.<br>"
        "• <b>Fabric:</b> adjusts density and pull compensation, and recommends a stabilizer and needle.",
        "Juste au-dessus du canevas, indiquez à OpenStitch sur quoi vous brodez :<br><br>"
        "• <b>Machine :</b> Universal, Tajima, Brother, Barudan, Melco …<br>"
        "• <b>Cadre :</b> OpenStitch adapte la sous-couche et la compensation de traction à la taille. Les "
        "grands cadres sont renforcés contre l'effet trampoline, et les casquettes sont brodées du centre "
        "vers l'extérieur et de la visière vers le haut.<br>"
        "• <b>Tissu :</b> ajuste la densité et la compensation de traction, et vous conseille un "
        "stabilisateur et une aiguille.",
        "Justo encima del lienzo le indicas a OpenStitch sobre qué vas a bordar:<br><br>"
        "• <b>Máquina:</b> Universal, Tajima, Brother, Barudan, Melco …<br>"
        "• <b>Bastidor:</b> OpenStitch ajusta el refuerzo y la compensación de tirón según el tamaño. Los "
        "bastidores grandes llevan más sujeción contra el efecto trampolín, y las gorras se bordan del "
        "centro hacia fuera y desde la visera hacia arriba.<br>"
        "• <b>Tela:</b> ajusta la densidad y la compensación de tirón, y te recomienda estabilizador y aguja.",
    ),
    "tour_app_2_action": ("⛶ Design optimal in den Rahmen einpassen (Auto-Fit)",
                          "⛶ Fit the design to the hoop (Auto-Fit)",
                          "⛶ Ajuster le motif au cadre",
                          "⛶ Ajustar el diseño al bastidor (Auto-Ajuste)"),

    "tour_app_3_badge": ("OBERE LEISTE · 3 / 7", "TOP TOOLBAR · 3 / 7", "BARRE SUPÉRIEURE · 3 / 7",
                         "BARRA SUPERIOR · 3 / 7"),
    "tour_app_3_title": ("Bild, Schrift, Prüfen und Export", "Image, lettering, check and export",
                         "Image, lettrage, vérification et export", "Imagen, texto, revisión y exportación"),
    "tour_app_3_body": (
        "Neben den Datei-Knöpfen und Rückgängig findest du hier die wichtigsten Schritte:<br><br>"
        "• <b>Bild → Stiche (Ctrl+D):</b> Bild wählen, OpenStitch stellt es frei und erzeugt die "
        "Stickflächen.<br>"
        "• <b>Schrift (Ctrl+T):</b> Text und Monogramme einfügen.<br>"
        "• <b>Prüfen (F7):</b> Testet dein Design und gibt ihm eine Punktzahl bis 100.<br>"
        "• <b>Export (Ctrl+E):</b> Speichert die Datei für deine Maschine.<br><br>"
        "PhotoStitch, Appliqué und 3D-Puff sind im Menü <b>Digitalisieren</b>, SVG in <b>Datei</b>, "
        "Transfer in <b>Maschine &amp; Export</b>.",
        "Next to the file buttons and Undo you find the main steps:<br><br>"
        "• <b>Image to stitches (Ctrl+D):</b> pick an image, and OpenStitch removes the background and "
        "creates the stitch areas.<br>"
        "• <b>Lettering (Ctrl+T):</b> add text and monograms.<br>"
        "• <b>Check (F7):</b> tests your design and gives it a score out of 100.<br>"
        "• <b>Export (Ctrl+E):</b> saves the file for your machine.<br><br>"
        "PhotoStitch, Appliqué and 3D-Puff are in the <b>Digitize</b> menu, SVG is in <b>File</b>, and "
        "Transfer is in <b>Machine &amp; Export</b>.",
        "À côté des boutons de fichier et d'annulation se trouvent les étapes principales :<br><br>"
        "• <b>Image → points (Ctrl+D) :</b> choisissez une image, OpenStitch retire le fond et crée les "
        "zones de broderie.<br>"
        "• <b>Lettrage (Ctrl+T) :</b> ajoutez du texte et des monogrammes.<br>"
        "• <b>Vérifier (F7) :</b> teste votre motif et lui donne une note sur 100.<br>"
        "• <b>Exporter (Ctrl+E) :</b> enregistre le fichier pour votre machine.<br><br>"
        "PhotoStitch, Appliqué et 3D-Puff sont dans le menu <b>Numériser</b>, SVG dans <b>Fichier</b> et "
        "Transfert dans <b>Machine &amp; Export</b>.",
        "Junto a los botones de archivo y de deshacer están los pasos principales:<br><br>"
        "• <b>Imagen a puntadas (Ctrl+D):</b> elige una imagen y OpenStitch quita el fondo y crea las "
        "zonas de bordado.<br>"
        "• <b>Texto (Ctrl+T):</b> añade texto y monogramas.<br>"
        "• <b>Revisar (F7):</b> prueba tu diseño y le da una puntuación sobre 100.<br>"
        "• <b>Exportar (Ctrl+E):</b> guarda el archivo para tu máquina.<br><br>"
        "PhotoStitch, Aplique y 3D-Puff están en el menú <b>Digitalizar</b>, SVG en <b>Archivo</b> y "
        "Transferir en <b>Máquina &amp; Exportar</b>.",
    ),
    "tour_app_3_action": ("✨ Bild → Stiche öffnen …", "✨ Open Image to stitches …", "✨ Ouvrir Image → points …",
                          "✨ Abrir Imagen a puntadas …"),

    "tour_app_4_badge": ("WERKZEUGE · 4 / 7", "TOOLS · 4 / 7", "OUTILS · 4 / 7", "HERRAMIENTAS · 4 / 7"),
    "tour_app_4_title": ("Selbst zeichnen und Knoten bearbeiten (N)", "Draw by hand and edit nodes (N)",
                         "Dessiner à la main et modifier les nœuds (N)", "Dibujar a mano y editar nodos (N)"),
    "tour_app_4_body": (
        "Die schmale Leiste links zeigt nur Symbole. Zeige mit der Maus darauf, dann erscheint der "
        "Name:<br><br>"
        "• <b>Tatami (F) / Satin (S) / Stepp (R):</b> Eigene Formen frei auf der Leinwand zeichnen.<br>"
        "• <b>Knoten (N):</b> Konturpunkte einzeln verschieben und an der <b>gelben Achse</b> den "
        "Stichwinkel drehen.",
        "The narrow bar on the left shows icons only. Point the mouse at one to see its name:<br><br>"
        "• <b>Tatami (F) / Satin (S) / Run (R):</b> draw your own shapes on the canvas.<br>"
        "• <b>Nodes (N):</b> move outline points one by one, and drag the <b>yellow axis</b> to turn the "
        "stitch angle.",
        "La barre étroite à gauche n'affiche que des icônes. Pointez-en une avec la souris pour voir son "
        "nom :<br><br>"
        "• <b>Tatami (F) / Satin (S) / Point droit (R) :</b> dessinez vos propres formes sur le canevas.<br>"
        "• <b>Nœuds (N) :</b> déplacez les points du contour un par un et tirez l'<b>axe jaune</b> pour "
        "tourner l'angle de point.",
        "La barra estrecha de la izquierda solo muestra iconos. Pasa el ratón sobre uno para ver su "
        "nombre:<br><br>"
        "• <b>Tatami (F) / Satén (S) / Pespunte (R):</b> dibuja tus propias formas en el lienzo.<br>"
        "• <b>Nodos (N):</b> mueve los puntos del contorno uno a uno y arrastra el <b>eje amarillo</b> para "
        "girar el ángulo de puntada.",
    ),
    "tour_app_4_action": ("❖ Knoten- und Stichwinkel-Editor (N) einschalten",
                          "❖ Turn on the node and stitch angle editor (N)",
                          "❖ Activer l'éditeur de nœuds et d'angle (N)",
                          "❖ Activar el editor de nodos y ángulo (N)"),

    "tour_app_5_badge": ("GARNFARBEN · 5 / 7", "THREAD COLORS · 5 / 7", "COULEURS DE FIL · 5 / 7",
                         "COLORES DE HILO · 5 / 7"),
    "tour_app_5_title": ("Farben und Nadel-Reihenfolge", "Colors and needle order", "Couleurs et ordre des aiguilles",
                         "Colores y orden de agujas"),
    "tour_app_5_body": (
        "Links wählst du mit einem Klick eine Farbe aus dem <b>Garnkatalog</b> (Madeira, Isacord, Gunold, "
        "Brother …) oder über <b>RGB</b> einen eigenen Ton.<br><br>"
        "• Darunter siehst du die <b>Reihenfolge der Farben und Nadeln</b> in deinem Design, mit der "
        "Stichanzahl pro Farbe.",
        "On the left you pick a color from the <b>thread catalog</b> (Madeira, Isacord, Gunold, "
        "Brother …) with one click, or mix your own with <b>RGB</b>.<br><br>"
        "• Below that you see the <b>order of colors and needles</b> in your design, with the number of "
        "stitches per color.",
        "À gauche, choisissez en un clic une couleur du <b>catalogue de fils</b> (Madeira, Isacord, Gunold, "
        "Brother …) ou créez votre propre teinte avec <b>RGB</b>.<br><br>"
        "• En dessous, vous voyez l'<b>ordre des couleurs et des aiguilles</b> de votre motif, avec le "
        "nombre de points par couleur.",
        "A la izquierda eliges con un clic un color del <b>catálogo de hilos</b> (Madeira, Isacord, Gunold, "
        "Brother …) o creas tu propio tono con <b>RGB</b>.<br><br>"
        "• Debajo ves el <b>orden de colores y agujas</b> de tu diseño, con el número de puntadas por "
        "color.",
    ),

    "tour_app_6_badge": ("EBENEN UND EINSTELLUNGEN · 6 / 7", "LAYERS AND SETTINGS · 6 / 7",
                         "CALQUES ET RÉGLAGES · 6 / 7", "CAPAS Y AJUSTES · 6 / 7"),
    "tour_app_6_title": ("Ebenen und Objekt-Einstellungen", "Layers and object settings",
                         "Calques et réglages de l'objet", "Capas y ajustes del objeto"),
    "tour_app_6_body": (
        "Rechts legst du die <b>Stickreihenfolge</b> fest. Darunter stellst du für das gewählte Objekt "
        "Reihenabstand, Muster (z. B. <i>Kontur</i>), Zugkompensation oder bei Satin <b>3D-Puff</b> ein."
        "<br><br>"
        "• Jede Änderung berechnet die Stiche <b>sofort</b> auf der Leinwand neu.",
        "On the right you set the <b>stitching order</b>. Below it you adjust the selected object: row "
        "spacing, pattern (for example <i>Contour</i>), pull compensation, or <b>3D puff</b> for satin."
        "<br><br>"
        "• Every change recalculates the stitches on the canvas <b>right away</b>.",
        "À droite, vous définissez l'<b>ordre de broderie</b>. En dessous, réglez l'objet sélectionné : "
        "espacement des rangs, motif de remplissage (par exemple <i>Contour</i>), compensation de traction "
        "ou <b>Puff 3D</b> pour le satin.<br><br>"
        "• Chaque modification recalcule les points sur le canevas <b>aussitôt</b>.",
        "A la derecha fijas el <b>orden de bordado</b>. Debajo ajustas el objeto seleccionado: separación "
        "de filas, patrón (por ejemplo <i>Contorno</i>), compensación de tirón o <b>Puff 3D</b> para el "
        "satén.<br><br>"
        "• Cada cambio recalcula las puntadas en el lienzo <b>al instante</b>.",
    ),

    "tour_app_7_badge": ("SIMULATOR UND STATUS · 7 / 7", "SIMULATOR AND STATUS · 7 / 7",
                         "SIMULATEUR ET ÉTAT · 7 / 7", "SIMULADOR Y ESTADO · 7 / 7"),
    "tour_app_7_title": ("Stich-Simulator und Statusleiste", "Stitch simulator and status bar",
                         "Simulateur de points et barre d'état", "Simulador de puntadas y barra de estado"),
    "tour_app_7_body": (
        "Unter der Leinwand spielst du den kompletten Stickablauf <b>Stich für Stich</b> ab.<br><br>"
        "• In der Statusleiste ganz unten siehst du Stiche, Grösse, Farbwechsel, Fadenschnitte und die "
        "geschätzte Laufzeit. Zeige mit der Maus darauf für <b>Tempo</b> und <b>Spitzendichte</b>.<br>"
        "• Die <b>Sprache</b> stellst du unten rechts um.",
        "Below the canvas you can play the whole design <b>stitch by stitch</b>.<br><br>"
        "• The status bar at the very bottom shows stitches, size, color changes, trims and the "
        "estimated runtime. Point the mouse at it for <b>speed</b> and <b>peak density</b>.<br>"
        "• You change the <b>language</b> at the bottom right.",
        "Sous le canevas, vous pouvez rejouer tout le motif <b>point par point</b>.<br><br>"
        "• La barre d'état tout en bas indique les points, la taille, les changements de couleur, les "
        "coupes et la durée estimée. Pointez-la avec la souris pour voir la <b>vitesse</b> et la "
        "<b>densité maximale</b>.<br>"
        "• La <b>langue</b> se change en bas à droite.",
        "Debajo del lienzo puedes reproducir todo el diseño <b>puntada a puntada</b>.<br><br>"
        "• La barra de estado, abajo del todo, muestra las puntadas, el tamaño, los cambios de color, los "
        "cortes y el tiempo estimado. Pasa el ratón por encima para ver la <b>velocidad</b> y la "
        "<b>densidad máxima</b>.<br>"
        "• El <b>idioma</b> se cambia abajo a la derecha.",
    ),
    "tour_app_7_action": ("▶ Simulation starten / stoppen", "▶ Start / stop the simulation",
                          "▶ Lancer / arrêter la simulation", "▶ Iniciar / detener la simulación"),
}
