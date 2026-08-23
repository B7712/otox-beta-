# ⚡ OTOX (BETA) — CYBERPUNK MUSIC NETWORK & INTERACTIVE LABS 🎵🤖

> **"El código no duerme y el arte tampoco. Otox es el bastión cibernético para la creación, aprendizaje y difusión musical independiente."**

---

## 🚀 ¿Qué carajos es Otox?

**Otox** es una plataforma social y educativa interactiva enfocada en la música, con una estética **Cyberpunk / Dark Anime Neón** desarrollada con pura *Main Character Energy*[cite: 1, 4]. Combina un feed dinámico tipo Twitter/X para compartir producciones musicales y tutoriales (mediante parser e integración directa de iFrames de **YouTube** y **Spotify**)[cite: 1, 4], junto con un módulo educativo interactivo único inspirado en *Lichess.org* denominado **"Estudios Otox"** (teoría musical, armonía cyberpunk, acordes complejos, tablaturas y práctica en línea)[cite: 1, 4].

Diseñado y construido desde cero en modo **Solo Dev / Guerrero** utilizando un stack ultraligero y portable (**Android Termux + Acode + PC Linux Mint + VS Code + Firefox**)[cite: 1, 3].

---

## 🔥 Features Principales (God Level Capabilities)

* **💻 Feed Dinámico & Parser de Media Embed:** Transforma dinámicamente enlaces crudos de YouTube (`watch`, `youtu.be`) y Spotify (`track`) en reproductores integrados e iFrames optimizados sin romper el layout[cite: 1, 4].
* **🎓 Estudios Otox (Lichess-style Music Lab):** Módulo de lecciones interactivas comunitarias para aprender armonía, escalas neón y progresión de acordes[cite: 1, 4].
* **🛡️ Perfil & Bóveda Personal:** Gestión de bio, alias, métricas de usuario, personalización de avatar/banner y guardado de tracks favoritos en la bóveda personal[cite: 1, 4].
* **🎛️ Dark/Neon Aesthetic UI:** Layout responsive de 3 columnas (Sidebar, Feed Principal, Panel de Estudios / Perfil) maquetado con variables CSS neón, animaciones fluidas y adaptabilidad total[cite: 1, 4].
* **⚡ Flask Micro-Backend:** Arquitectura orientada a rendimiento en Python con Jinja2 para renderizado dinámico de templates[cite: 1, 2].

---

## 📁 Estructura del Proyecto (Project Architecture)

```text
Otox/
├── static/
│   ├── images/
│   │   └── otox.jpeg      # Logo oficial e identidad visual
│   └── style.css          # Estilos
├── templates/
│   └── index.html         # Maquetación principal 3 Columnas (Feed, Estudios, Perfil, Ajustes)
├── app.py                 # Core Backend (Flask Router + Parser Media + Lógica de Datos)
└── README.md              # Documentación del repositorio
├── database.py            # La forma en la que se almacena datos y cuentas
└── otox.db                # Base de datos
