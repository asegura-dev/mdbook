# mdbook

> Convierte varios archivos Markdown (`.md`) en **un único HTML de estudio**:
> autocontenido, navegable, con búsqueda instantánea, tema claro/oscuro y botón
> de copiar en cada bloque de código.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Type-checked](https://img.shields.io/badge/mypy-strict-2a6db2)
![Lint](https://img.shields.io/badge/ruff-passing-success)

Pensado para **leer documentación cómodamente en el celular** y **enriquecer
repos de GitHub**: compilas tus apuntes o manuales en un solo `.html` que se
abre en cualquier navegador, sin servidor ni dependencias externas.

![La aplicación de escritorio](docs/img/gui.png)

## Características

- 📄 **Uno o varios `.md`** en un solo HTML; el primer `#` de cada archivo es su
  título en la navegación.
- 🧭 **Portada + índice + barra lateral** con secciones y subsecciones.
- 🔎 **Búsqueda instantánea** que filtra y **resalta** coincidencias.
- 🌗 **Tema claro/oscuro** que **recuerda** tu preferencia.
- 📋 **Botón "Copiar"** en cada bloque de código (con su lenguaje).
- 🔗 **Referencias cruzadas** opcionales: `T1 §3` se vuelve un enlace interno.
- 📦 **Autocontenido**: CSS y JS embebidos, **cero URLs externas**. Ideal para
  abrir desde el celular o servir desde un repo.
- 🖥️ **Dos interfaces sobre el mismo motor**: app de escritorio (CustomTkinter)
  y línea de comandos (Typer).

Markdown soportado: encabezados (`#`..`######`), párrafos, listas (anidadas),
tablas, bloques de código con ` ``` ` (preservando el lenguaje), citas (`>`),
**negrita**, *cursiva* e `inline code`.

## Demo

En [`examples/`](examples/) hay dos tomos de ejemplo con secciones numeradas y
referencias cruzadas. El resultado ya compilado está en
[`examples/demo.html`](examples/demo.html): descárgalo y ábrelo en tu navegador.

![El HTML resultante en tema oscuro](docs/img/demo-oscuro.png)

Para regenerarlo:

```bash
uv run mdbook build --input examples --title "Curso de Python — Demo mdbook" \
  --theme oscuro --cross-refs --output examples/demo.html
```

## Instalación

Requiere [uv](https://docs.astral.sh/uv/) y Python 3.12+.

```bash
git clone <url-del-repo>
cd mdbook
uv sync          # crea el entorno e instala todo
```

## Uso

### App de escritorio (GUI)

```bash
uv run mdbook-gui
```

1. **Agregar carpeta…** (toma todos los `.md`) o **Agregar archivos…** (sueltos).
2. Reordena la lista con **▲ Subir / ▼ Bajar** (el orden define el del HTML).
3. Escribe el **título**, elige **tema** y, si quieres, marca **referencias
   cruzadas**.
4. **Compilar** → te dice dónde quedó el HTML.
5. **Abrir en navegador** → lo abre con el navegador del sistema.

### Línea de comandos (CLI)

```bash
# Una carpeta: toma todos los .md (orden alfabético)
uv run mdbook build --input docs --title "Mi Obra" --theme oscuro --output libro.html

# Archivos sueltos: el orden de los -f define el orden del HTML
uv run mdbook build -f intro.md -f cap1.md -t "Curso" --cross-refs -o curso.html
```

| Opción | Descripción |
| ------ | ----------- |
| `--input/-i` | Carpeta: toma todos los `.md` (orden alfabético). |
| `--file/-f` | Archivo `.md` suelto (repetible; define el orden). |
| `--title/-t` | Título de la obra. |
| `--theme` | `claro` o `oscuro` (por defecto `claro`). |
| `--cross-refs / --no-cross-refs` | Activa/desactiva las referencias cruzadas. |
| `--output/-o` | Ruta del HTML de salida (`.html`). |

### Referencias cruzadas

Con las referencias activadas, patrones como `T1 §3` se convierten en enlaces
internos:

- `T<n>` = el documento número `n` (1-based, según el orden de la obra).
- `§<m>` = la **sección numerada `m`**: el encabezado cuyo texto empieza con
  `m.` (p. ej. `## 3. Funciones` es §3). Los subencabezados sin número **no**
  cuentan.

Si el destino no existe, el texto se deja tal cual.

## Ejecutable (.exe)

Para generar un único ejecutable de escritorio (Windows) con PyInstaller:

```bash
uv run pyinstaller packaging/mdbook.spec
```

El binario queda en `dist/mdbook.exe`: una sola ventana, sin consola, con los
assets embebidos. No requiere Python instalado para usarse.

## Arquitectura

La lógica **no depende de la interfaz**; es la decisión de diseño central.

```
src/mdbook/
├── config.py        # Frontera de validación: BuildOptions (Pydantic)
├── engine/          # MOTOR puro (no importa GUI ni CLI)
│   ├── parser.py    #   Markdown -> tokens (markdown-it-py) + secciones
│   ├── model.py     #   modelo interno (Book, Document, Section)
│   ├── crossref.py  #   referencias "T1 §3"
│   ├── renderer.py  #   modelo -> HTML autocontenido
│   ├── compiler.py  #   orquestación
│   └── assets/      #   template.html, style.css, app.js (se embeben)
├── cli.py           # Interfaz: Typer + Rich
└── gui/app.py       # Interfaz: CustomTkinter
```

- **`config.py`** es la única frontera de validación: tanto la GUI como la CLI
  construyen el mismo `BuildOptions` validado y se lo pasan al motor, que confía
  en él.
- El motor se puede probar y ejecutar **sin la interfaz**.
- [`tests/unit/test_architecture.py`](tests/unit/test_architecture.py) hace
  **verificable** esta separación: falla si el motor importa una interfaz o si
  la GUI toca el parseo/render.

## Desarrollo

```bash
uv run pytest            # todas las pruebas
uv run pytest -m unit    # markers: unit | smoke | regression
uv run ruff check .      # lint
uv run ruff format .     # formato
uv run mypy              # tipos (estricto)
```

> **Nota:** clona y trabaja el repo **fuera** de carpetas sincronizadas
> (OneDrive, Dropbox, Google Drive). El cliente de sincronización bloquea
> archivos dentro de `.venv` y provoca fallos intermitentes al instalar o
> reinstalar dependencias con `uv`.

## Licencia

[MIT](LICENSE) © 2026 Alejandro Segura.
