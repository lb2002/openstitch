# 🪡 OpenStitch Studio

🌐 **Idioma / Language:** [English](./README.md) · [Deutsch](./README.de.md) · [Français](./README.fr.md) · **Español**

**Suite universal de código abierto para digitalizar y bordar en Windows, macOS y Linux**

[![Licencia: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Plataforma](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-2ea44f.svg)](#-inicio-rápido--instalación)

**OpenStitch Studio** es un software moderno y de código abierto para digitalizar bordados, con una interfaz oscura cómoda para la vista, vista previa 3D de hilos en tiempo real, un **Auto-Digitalizador** inteligente, **PhotoStitch**, **catálogos de hilos** reales (Madeira, Isacord, Gunold, Brother) y una **interfaz en 4 idiomas** (English, Deutsch, Français, Español). Es compatible con las máquinas de bordar domésticas e industriales más comunes (**Tajima, Brother, Barudan, Ricoma, ZSK, Janome, Bernina, Pfaff/Husqvarna, Melco**).

> 💬 **¡Se agradecen comentarios y contribuciones!**
> ¿Encontraste un error, tienes una idea o quieres ayudar? Abre un [Issue](https://github.com/lb2002/openstitch/issues) o un [Pull Request](./CONTRIBUTING.md).

![OpenStitch Studio — interfaz oscura](./assets/screenshot_studio.png)

---

## ✨ Características

* 🪄 **Auto-Digitalizador (imagen / logotipo → archivo de bordado):** reducción de color en CIE-Lab, correspondencia con catálogos reales (**Madeira Polyneon 40, Isacord 40, Gunold Poly 40, Brother**), eliminación automática del fondo, detección del tipo de puntada (pespunte triple, **satén automático**, **tatami** / relleno de contorno), compensación de tirantez, entretela y solape de 0,7 mm entre colores.
* 🎨 **Digitalización manual:** herramientas Tatami (`F`), Satén (`S`), Pespunte (`R`), editor de nodos (`N`), inspector paramétrico en vivo, texto TTF/OTF con arco, importación SVG y arrastrar y soltar.
* 🧵 **Herramientas pro:** modo espuma 3D (gorras), **aplique en 1 clic**, **PhotoStitch** (foto → bordado monocromo, sepia o CMYK).
* 🩺 **Control de calidad:** filtro anti-rotura de hilo, mapa de densidad en vivo, **doctor de calidad (`F7`)** y **verificación binaria** de cada archivo exportado.
* 🏭 **Neutral respecto a fabricantes:** DST, PES, EXP, JEF, VP3, U01; perfiles para Tajima, Brother, Barudan, Ricoma/ZSK, Janome/Bernina, Pfaff/Husqvarna y Melco (gestor de disquete FAT12 `.IMG` incluido).
* 🌍 **4 idiomas** conmutables al instante: 🇬🇧 🇩🇪 🇫🇷 🇪🇸.
* 📄 **Hoja de producción PDF A4:** agujas, consumo de hilo, número de puntadas y tiempo estimado.

---

## 🚀 Inicio rápido & instalación

### Opción A: descarga con 1 clic (sin Python)
Desde la **[página de releases (v0.1.0)](https://github.com/lb2002/openstitch/releases/tag/v0.1.0)**:
* 🪟 **Windows (64 bits, archivo único):** [`OpenStitch-Studio-Windows-x64.exe`](https://github.com/lb2002/openstitch/releases/download/v0.1.0/OpenStitch-Studio-Windows-x64.exe)
* 🍏 **macOS (Apple Silicon M1–M4):** [`OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip`](https://github.com/lb2002/openstitch/releases/download/v0.1.0/OpenStitch-Studio-macOS-AppleSilicon-M-Chip-arm64.zip)
* 🍎 **macOS (Intel x64):** [`OpenStitch-Studio-macOS-Intel-x64.zip`](https://github.com/lb2002/openstitch/releases/download/v0.1.0/OpenStitch-Studio-macOS-Intel-x64.zip)

### Opción B: desde el código fuente
Requiere **Python 3.10+**.

```bash
git clone https://github.com/lb2002/openstitch.git
cd openstitch
python -m venv .venv
.venv/bin/pip install -e .      # Windows: .venv\Scripts\pip install -e .
.venv/bin/python main.py        # Windows: .venv\Scripts\python.exe main.py
```

---

## 🤝 Contribuir

* 🌟 ¡Dale una estrella al repositorio si te gusta!
* 🐛 Errores y pruebas en máquina: [GitHub Issues](https://github.com/lb2002/openstitch/issues).
* 🌐 Traducciones: [`openstitch/i18n.py`](./openstitch/i18n.py).
* 🔧 Pull requests: consulta [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📜 Licencia y derechos de autor

Copyright © 2026 **Linus Baumberger** ([@lb2002](https://github.com/lb2002)).

* **Copyleft de código abierto:** publicado bajo **[GNU AGPL-3.0-or-later](./LICENSE)**. Uso, estudio, mejora y distribución libres; las obras derivadas y los servicios de red deben mantenerse abiertos bajo la misma licencia.
* **Licencia comercial / doble licencia:** como autor original, **Linus Baumberger (`@lb2002`)** se reserva el derecho de ofrecer OpenStitch Studio también bajo licencias comerciales / OEM. Ver [LICENSE](./LICENSE).
