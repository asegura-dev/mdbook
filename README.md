# mdbook

Convierte archivos Markdown (`.md`) en **un único HTML de estudio**:
autocontenido (CSS y JS embebidos), navegable, con búsqueda instantánea,
tema claro/oscuro recordado y botón de copiar en cada bloque de código.
Pensado para leer documentación cómodamente en el celular y enriquecer repos.

## Arquitectura

- **Motor puro** (`mdbook.engine`): recibe opciones validadas y produce el
  HTML. No depende de la GUI ni de la CLI; se prueba y ejecuta solo.
- **Frontera de validación** (`mdbook.config`): el contrato Pydantic
  `BuildOptions` que comparten ambas interfaces.
- **Interfaces**: la **CLI** (`mdbook.cli`, Typer + Rich) y, más adelante, la
  **GUI** (CustomTkinter). Ambas construyen el mismo `BuildOptions` y llaman al
  motor.

## Uso (CLI)

```bash
# Una carpeta: toma todos los .md (orden alfabético)
uv run mdbook build --input docs --title "Mi Obra" --theme oscuro --output libro.html

# Archivos sueltos (el orden define el orden del HTML)
uv run mdbook build -f intro.md -f cap1.md -t "Curso" --cross-refs -o curso.html
```

Opciones: `--input/-i` (carpeta), `--file/-f` (archivo, repetible),
`--title/-t`, `--theme` (`claro`|`oscuro`), `--cross-refs/--no-cross-refs`,
`--output/-o`.

### Referencias cruzadas

Con `--cross-refs`, patrones como `T1 §6` se convierten en enlaces internos.
Convención: `T<n>` = documento `n` (1-based, según el orden); `§<m>` = la
**sección numerada `m`**, es decir el encabezado cuyo texto empieza con `m.`
(por ejemplo `## 6. Validar la configuración` es §6). Los subencabezados sin
número **no** cuentan. Si el destino no existe, el texto se deja igual.

## Desarrollo

```bash
uv sync                 # instala runtime + dev
uv run pytest           # todas las pruebas
uv run pytest -m unit   # solo unitarias (markers: unit, smoke, regression)
uv run ruff check .     # lint
uv run ruff format .    # formato
uv run mypy             # tipos (estricto)
```

## Estado

- [x] **Fase 1**: contrato Pydantic + motor + CLI + pruebas.
- [ ] Fase 2: GUI mínima (elegir archivos, título, compilar, abrir).
- [ ] Fase 3: opciones (tema, referencias cruzadas, reordenar).
- [ ] Fase 4: empaquetado con PyInstaller.
