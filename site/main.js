// Sprache, passender Download und aktuelle Version: alles ohne Server, die Seite bleibt statisch.
const T = {
  de: {
    nav_download: "Download", nav_source: "Quellcode", nav_lang: "Sprache",
    nav_feedback: "Feedback",
    fb_d: "Fehler gefunden, fehlt dir etwas oder kommst du nicht weiter?",
    fb_bug: "Problem melden", fb_wish: "Idee vorschlagen", fb_question: "Frage stellen",
    fb_note: "Rückmeldungen laufen über GitHub, dafür brauchst du ein kostenloses GitHub-Konto.",
    lede: "Kostenlose Sticksoftware, die dein Design prüft, bevor du stickst.",
    sub: "Mach aus einem Logo Stiche, sticke Namen ab 3 mm und speichere direkt auf den USB-Stick für deine Maschine. Für Windows, Mac und Linux. Ohne Konto, ohne Abo.",
    cta: "Kostenlos herunterladen", hero_caption: "Der Schriftzug oben wurde von OpenStitch selbst gestickt.",
    f1_t: "Dein Bild, umgewandelt in Stiche",
    f1_d: "Zieh ein Logo oder eine Zeichnung hinein. OpenStitch wählt Garnfarben aus echten Katalogen wie Madeira und Isacord, entscheidet für jede Fläche zwischen Satin und Füllstich und setzt die Unterlage. Alles bleibt bearbeitbar.",
    f2_t: "Probleme finden, bevor sie Faden kosten",
    f2_d: "F7 gibt dir eine Punktzahl bis 100 und klare Erklärungen: hier zu dicht, dieser Stich zu lang, das Motiv berührt den Rahmen. Zeigen führt dich zur Stelle, Beheben repariert es.",
    f2_d2: "Dazu siehst du, wie sich dein Stoff zusammenzieht, vom T-Shirt bis zur Jeans. Stick einen kleinen Testbalken, miss ihn, und die Vorschau rechnet mit deinem echten Stoff.",
    f3_t: "Kleine Schrift, die lesbar bleibt",
    f3_d: "Normale Schriften laufen unter etwa 5 mm zu. Die eingebaute Schrift OpenStitch Micro ist als Einzelstrich gezeichnet, wie kommerzielle Kleinschriften. So bleiben Namen und Daten ab etwa 3 mm lesbar.",
    fmt_t: "Passt zu deiner Maschine",
    fmt_d: "Speichert DST, PES, JEF, EXP, VP3, U01 und XXX für Tajima, Brother, Janome, Melco, Bernina, Pfaff, Husqvarna, Barudan, Singer und mehr. Jede Datei wird nach dem Speichern neu eingelesen und geprüft.",
    dl_t: "Download", dl_d: "Kostenlos und quelloffen unter AGPL-3.0.",
    dl_win: "64 Bit, eine Datei, ohne Installation", dl_mac_arm: "Apple-Chip (M1 bis M4)", dl_mac_intel: "Intel-Chip",
    dl_linux: "64 Bit, entpacken und starten", dl_btn: "Herunterladen",
    mac_t: "macOS lässt die App nicht öffnen",
    mac_d: "OpenStitch ist kostenlos und nicht mit einem bezahlten Apple-Zertifikat signiert, deshalb blockiert macOS es beim ersten Mal. Verschiebe die App nach Programme, versuche einmal sie zu öffnen, gehe dann zu Systemeinstellungen, Datenschutz & Sicherheit, und klicke Trotzdem öffnen. Meldet macOS, die App sei beschädigt, führe einmal im Terminal aus:",
    help_t: "Hilf mit, auf echten Maschinen zu testen",
    help_d: "OpenStitch wird am Computer gründlich getestet, braucht aber echte Probestickereien. Wenn du ein Design auf deiner Maschine stickst, hilft ein Foto und ein Satz dazu, was gut oder schlecht lief, mehr als alles andere.",
    help_btn: "Probestick teilen", foot: "OpenStitch Studio ist freie Software unter der Lizenz AGPL-3.0.",
    version: "Version {v}",
  },
  fr: {
    nav_download: "Télécharger", nav_source: "Code source", nav_lang: "Langue",
    nav_feedback: "Retours",
    fb_d: "Un bug, une fonction qui manque, ou vous êtes bloqué ?",
    fb_bug: "Signaler un problème", fb_wish: "Proposer une idée", fb_question: "Poser une question",
    fb_note: "Les retours passent par GitHub, il faut donc un compte GitHub gratuit.",
    lede: "Un logiciel de broderie gratuit qui vérifie votre motif avant que vous brodiez.",
    sub: "Transformez un logo en points, brodez des prénoms dès 3 mm et enregistrez directement sur la clé USB de votre machine. Pour Windows, Mac et Linux. Sans compte ni abonnement.",
    cta: "Télécharger gratuitement", hero_caption: "Le texte ci-dessus a été brodé par OpenStitch lui-même.",
    f1_t: "Votre image transformée en points",
    f1_d: "Déposez un logo ou un dessin. OpenStitch choisit les couleurs de fil dans de vrais nuanciers comme Madeira et Isacord, décide entre satin et remplissage pour chaque zone et ajoute la sous-couche. Tout reste modifiable.",
    f2_t: "Repérez les problèmes avant de gaspiller du fil",
    f2_d: "F7 donne une note sur 100 et des explications claires : trop dense ici, ce point est trop long, le motif touche le cadre. Afficher vous mène à l'endroit, Corriger le répare.",
    f2_d2: "Vous voyez aussi comment votre tissu va se resserrer, du t-shirt au denim. Brodez une petite barre de test, mesurez-la, et l'aperçu utilise votre vrai tissu.",
    f3_t: "Des petits textes qui restent lisibles",
    f3_d: "Les polices normales se bouchent sous 5 mm environ. La police intégrée OpenStitch Micro est dessinée en un seul trait, comme les polices commerciales pour petits textes, et reste lisible dès 3 mm environ.",
    fmt_t: "Compatible avec votre machine",
    fmt_d: "Enregistre en DST, PES, JEF, EXP, VP3, U01 et XXX pour Tajima, Brother, Janome, Melco, Bernina, Pfaff, Husqvarna, Barudan, Singer et d'autres. Chaque fichier est relu et vérifié après l'enregistrement.",
    dl_t: "Télécharger", dl_d: "Gratuit et open source sous licence AGPL-3.0.",
    dl_win: "64 bits, un seul fichier, sans installation", dl_mac_arm: "Puce Apple (M1 à M4)", dl_mac_intel: "Puce Intel",
    dl_linux: "64 bits, décompresser et lancer", dl_btn: "Télécharger",
    mac_t: "macOS refuse d'ouvrir l'app",
    mac_d: "OpenStitch est gratuit et n'est pas signé avec un certificat Apple payant, macOS le bloque donc la première fois. Déplacez l'app dans Applications, essayez de l'ouvrir une fois, puis allez dans Réglages Système, Confidentialité et sécurité, et cliquez sur Ouvrir quand même. Si macOS indique que l'app est endommagée, exécutez une fois dans le Terminal :",
    help_t: "Aidez-nous à tester sur de vraies machines",
    help_d: "OpenStitch est testé en profondeur sur ordinateur, mais il lui faut de vrais essais de broderie. Si vous brodez un motif sur votre machine, une photo et une phrase sur ce qui a marché ou non aident plus que tout.",
    help_btn: "Partager un essai", foot: "OpenStitch Studio est un logiciel libre sous licence AGPL-3.0.",
    version: "Version {v}",
  },
  es: {
    nav_download: "Descargar", nav_source: "Código fuente", nav_lang: "Idioma",
    nav_feedback: "Opiniones",
    fb_d: "¿Encontraste un error, te falta algo o no sabes seguir?",
    fb_bug: "Informar de un problema", fb_wish: "Proponer una idea", fb_question: "Hacer una pregunta",
    fb_note: "Las opiniones se envían por GitHub, así que necesitas una cuenta gratuita de GitHub.",
    lede: "Software de bordado gratuito que revisa tu diseño antes de que bordes.",
    sub: "Convierte un logotipo en puntadas, borda nombres desde 3 mm y guarda directamente en la memoria USB de tu máquina. Para Windows, Mac y Linux. Sin cuenta ni suscripción.",
    cta: "Descargar gratis", hero_caption: "El texto de arriba lo bordó el propio OpenStitch.",
    f1_t: "Tu imagen convertida en puntadas",
    f1_d: "Arrastra un logotipo o un dibujo. OpenStitch elige colores de hilo de catálogos reales como Madeira e Isacord, decide entre satén y relleno para cada zona y añade la base. Todo sigue siendo editable.",
    f2_t: "Encuentra problemas antes de gastar hilo",
    f2_d: "F7 te da una nota sobre 100 y explicaciones claras: demasiado denso aquí, esta puntada es demasiado larga, el diseño toca el bastidor. Mostrar te lleva al lugar y Corregir lo arregla.",
    f2_d2: "También ves cómo se encogerá tu tela, de la camiseta al vaquero. Borda una pequeña barra de prueba, mídela y la vista previa usa tu tela real.",
    f3_t: "Letras pequeñas que siguen siendo legibles",
    f3_d: "Las fuentes normales se cierran por debajo de unos 5 mm. La fuente integrada OpenStitch Micro está dibujada en un solo trazo, como las fuentes comerciales para texto pequeño, y sigue siendo legible desde unos 3 mm.",
    fmt_t: "Funciona con tu máquina",
    fmt_d: "Guarda DST, PES, JEF, EXP, VP3, U01 y XXX para Tajima, Brother, Janome, Melco, Bernina, Pfaff, Husqvarna, Barudan, Singer y más. Cada archivo se vuelve a leer y se comprueba al guardarlo.",
    dl_t: "Descargar", dl_d: "Gratis y de código abierto con licencia AGPL-3.0.",
    dl_win: "64 bits, un solo archivo, sin instalación", dl_mac_arm: "Chip de Apple (M1 a M4)", dl_mac_intel: "Chip Intel",
    dl_linux: "64 bits, descomprimir y ejecutar", dl_btn: "Descargar",
    mac_t: "macOS no deja abrir la app",
    mac_d: "OpenStitch es gratuito y no está firmado con un certificado de pago de Apple, por lo que macOS lo bloquea la primera vez. Mueve la app a Aplicaciones, intenta abrirla una vez, ve a Ajustes del Sistema, Privacidad y seguridad, y pulsa Abrir igualmente. Si macOS dice que la app está dañada, ejecuta una vez en Terminal:",
    help_t: "Ayúdanos a probarlo en máquinas reales",
    help_d: "OpenStitch se prueba a fondo en el ordenador, pero necesita bordados reales. Si bordas un diseño en tu máquina, una foto y una frase sobre lo que salió bien o mal ayudan más que nada.",
    help_btn: "Compartir una prueba", foot: "OpenStitch Studio es software libre con licencia AGPL-3.0.",
    version: "Versión {v}",
  },
};

const EN = {};
document.querySelectorAll("[data-i18n]").forEach((el) => { EN[el.dataset.i18n] = el.textContent; });
EN.version = "Version {v}";

let release = null;

function setLang(lang) {
  const table = T[lang] || {};
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = table[el.dataset.i18n] || EN[el.dataset.i18n];
  });
  showVersion();
  try { localStorage.setItem("lang", lang); } catch (e) { /* privater Modus */ }
}

function showVersion() {
  if (!release) return;
  const lang = document.documentElement.lang;
  document.getElementById("version").textContent = ((T[lang] || {}).version || EN.version).replace("{v}", release);
}

// Eigenes System hervorheben; bei Mac lässt sich der Chip nicht sicher erkennen, beide bleiben sichtbar
function markOwnSystem() {
  const ua = navigator.userAgent;
  const os = /Windows/.test(ua) ? "windows" : /Mac/.test(ua) ? "mac" : /Linux|X11/.test(ua) && !/Android/.test(ua) ? "linux" : null;
  if (!os) return;
  const rows = document.querySelectorAll(`.dl-list li[data-os="${os}"]`);
  rows.forEach((li) => li.classList.add("mine"));
  if (rows.length === 1) {
    document.getElementById("primary-download").href = rows[0].querySelector("a").href;
  }
}

async function loadRelease() {
  try {
    const r = await fetch("https://api.github.com/repos/lb2002/openstitch/releases/latest");
    if (!r.ok) return;
    release = (await r.json()).tag_name.replace(/^v/, "");
    showVersion();
  } catch (e) { /* ohne Netz bleibt die Version einfach weg */ }
}

const select = document.getElementById("lang");
let start = "en";
try { start = localStorage.getItem("lang") || ""; } catch (e) { start = ""; }
if (!start) start = (navigator.language || "en").slice(0, 2);
if (!T[start] && start !== "en") start = "en";
select.value = start;
select.addEventListener("change", () => setLang(select.value));
setLang(start);
markOwnSystem();
loadRelease();
