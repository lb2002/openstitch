# 🪡 OpenStitch Studio

🌐 **Langue / Language :** [English](./README.md) · [Deutsch](./README.de.md) · **Français** · [Español](./README.es.md)

**Suite open source universelle de numérisation et de broderie pour Windows, macOS et Linux**

[![Licence : AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Plateforme](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-2ea44f.svg)](#-démarrage-rapide--installation)

**OpenStitch Studio** est un logiciel moderne et open source de numérisation de broderie, avec une interface sombre reposante, un aperçu 3D des fils en temps réel, un **Auto-Numériseur** intelligent, **PhotoStitch**, de vrais **nuanciers de fils** (Madeira, Isacord, Gunold, Brother) et une **interface en 4 langues** (English, Deutsch, Français, Español). Il prend en charge les machines à broder domestiques et industrielles courantes (**Tajima, Brother, Barudan, Ricoma, ZSK, Janome, Bernina, Pfaff/Husqvarna, Melco**).

> 💬 **Retours et contributions bienvenus !**
> Signalez un bug, proposez une idée ou aidez au développement : ouvrez une [Issue](https://github.com/lb2002/openstitch/issues) ou une [Pull Request](./CONTRIBUTING.md).

![OpenStitch Studio — interface sombre](./assets/screenshot_studio.png)

---

## ✨ Fonctionnalités

* 🪄 **Auto-Numériseur (image / logo → fichier de broderie) :** réduction des couleurs en CIE-Lab, correspondance avec de vrais nuanciers (**Madeira Polyneon 40, Isacord 40, Gunold Poly 40, Brother**), suppression automatique du fond, détection du type de point (point droit triple, **satin automatique**, **tatami** / remplissage de contour), compensation de tirage, sous-couche et recouvrement de 0,7 mm entre couleurs.
* 🎨 **Numérisation manuelle :** outils Tatami (`F`), Satin (`S`), Point droit (`R`), éditeur de nœuds (`N`), inspecteur paramétrique en direct, colonnes satin le long de la ligne centrale dessinée, police de broderie **OpenStitch Micro** lisible dès 2,5 mm, lettrage TTF/OTF avec texte en arc, import SVG, glisser-déposer.
* 🧵 **Outils pro :** mode mousse 3D (casquettes), **appliqué en 1 clic**, **PhotoStitch** (photo → broderie monochrome, sépia ou CMJN).
* 🩺 **Contrôle qualité :** filtre anti-casse de fil, carte de densité en direct, **docteur qualité (`F7`)** et **vérification binaire** de chaque fichier exporté.
* 🏭 **Neutre vis-à-vis des fabricants :** DST, PES, EXP, JEF, VP3, U01 ; profils pour Tajima, Brother, Barudan, Ricoma/ZSK, Janome/Bernina, Pfaff/Husqvarna et Melco (gestionnaire de disquette FAT12 `.IMG` inclus).
* 🌍 **4 langues** commutables à chaud : 🇬🇧 🇩🇪 🇫🇷 🇪🇸.
* 📄 **Fiche de production PDF A4** : aiguilles, consommation de fil, nombre de points, durée estimée.

---

## 🚀 Démarrage rapide & installation

### Option A : téléchargement en 1 clic (sans Python)
Depuis la **[page des releases (latest)](https://github.com/lb2002/openstitch/releases/latest)** :
* 🪟 **Windows (64 bits, fichier unique) :** [`OpenStitch-Studio-Windows-x64.exe`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-Windows-x64.exe)
* 🍏 **macOS (Apple Silicon M1–M4) :** [`OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip)
* 🍎 **macOS (Intel x64) :** [`OpenStitch-Studio-macOS-Intel-x64.zip`](https://github.com/lb2002/openstitch/releases/latest/download/OpenStitch-Studio-macOS-Intel-x64.zip)

### Option B : depuis les sources
Nécessite **Python 3.10+**.

```bash
git clone https://github.com/lb2002/openstitch.git
cd openstitch
python -m venv .venv
.venv/bin/pip install -e .      # Windows : .venv\Scripts\pip install -e .
.venv/bin/python main.py        # Windows : .venv\Scripts\python.exe main.py
```

---

## 🤝 Contribuer

* 🌟 Mettez une étoile au dépôt si le projet vous plaît !
* 🐛 Bugs et tests sur machine : [GitHub Issues](https://github.com/lb2002/openstitch/issues).
* 🌐 Traductions : [`openstitch/i18n.py`](./openstitch/i18n.py).
* 🔧 Pull requests : voir [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📜 Licence & droits d'auteur

Copyright © 2026 **Linus Baumberger** ([@lb2002](https://github.com/lb2002)).

* **Copyleft open source :** publié sous **[GNU AGPL-3.0-or-later](./LICENSE)**. Utilisation, étude, amélioration et partage libres ; les œuvres dérivées et services réseau doivent rester ouverts sous la même licence.
* **Licence commerciale / double licence :** en tant qu'auteur d'origine, **Linus Baumberger (`@lb2002`)** se réserve le droit de proposer OpenStitch Studio sous licences commerciales / OEM. Voir [LICENSE](./LICENSE).
