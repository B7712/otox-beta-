```markdown
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

```

---

## 🛠️ Tech Stack (El Arsenal)

* **Frontend:** HTML5 Semántico, CSS3 Neón Variables & Grid Layout, FontAwesome, Vanilla JS.


* **Backend:** Python 3.x, Flask Web Framework, Jinja2 Templating Engine.


* **Database:** Persistencia temporal en RAM (Listas/Diccionarios) ➔ Próxima migración a SQLite3.


* **Environment & Tools:** Android (Termux + Acode editor), Linux Mint (VS Code + Firefox Developer Tools), Git & GitHub.



---

## 🏁 Instalación & Ejecución Local (Local Deployment)

Si querés clonar este proyecto y probarlo en tu propia máquina (Linux, Windows, MacOS o Android Termux), seguí estos pasos:

### 1. Clonar el repositorio

```bash
git clone [https://github.com/tu-usuario/otox.git](https://github.com/tu-usuario/otox.git)
cd otox

```

### 2. Crear y activar entorno virtual (Opcional pero Recomendado)

```bash
python -m venv venv
# En Linux / Termux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

```

### 3. Instalar dependencias

```bash
pip install flask

```

### 4. Encender el servidor

```bash
python app.py

```

### 5. Abrir en el navegador

Visita en tu navegador favorito: `http://127.0.0.1:5000` o `http://localhost:5000` , dependiendo del link que le da a la hora de encender el app.py .
---

## 🛣️ Roadmap & Estado del Proyecto

* [x] **Fase 1: Structure & HTML5** (Layout 3 columnas, formularios, pestañas navegación).


* [x] **Fase 2: Dark Neon CSS3 Styling** (Diseño cyberpunk responsive y componentes neón).


* [x] **Fase 3: Python & Flask Core Backend** (Parser de YouTube/Spotify, motor Jinja2, lógica de perfil y lecciones).


* [ ] **Fase 4: Database Integration** (Migración de memoria a SQLite con SQLAlchemy/SQL crudo).


* [ ] **Fase 5: APK Build / Webview** (Empaquetamiento para dispositivos móviles).



---

## 📜 Licencia & Open Source

Este proyecto es software libre bajo la licencia **MIT License**. Podés clonarlo, modificarlo, redistribuirlo y aprender de él sin restricciones.

---