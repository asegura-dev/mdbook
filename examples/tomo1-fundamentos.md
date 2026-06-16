# Tomo 1: Fundamentos de Python

Este tomo cubre las bases del lenguaje. Las **referencias cruzadas** como
`T2 §1` se convierten en enlaces si compilas con la opción activada.

## 1. Variables y tipos

Una variable es un nombre que apunta a un valor. Python infiere el tipo:

```python
nombre = "Ada"      # str
edad = 36           # int
activo = True       # bool
```

Tipos básicos más usados:

| Tipo    | Ejemplo     | Mutable |
| ------- | ----------- | ------- |
| `int`   | `42`        | No      |
| `str`   | `"hola"`    | No      |
| `list`  | `[1, 2, 3]` | Sí      |
| `dict`  | `{"a": 1}`  | Sí      |

## 2. Estructuras de control

El flujo se controla con `if`, `for` y `while`.

> Recuerda: en Python la **indentación** define los bloques, no las llaves.

```python
for i in range(3):
    if i % 2 == 0:
        print(f"{i} es par")
    else:
        print(f"{i} es impar")
```

## 3. Funciones

Las funciones se definen con `def` y pueden tener *valores por defecto*:

```python
def saluda(nombre: str, mayus: bool = False) -> str:
    saludo = f"Hola, {nombre}"
    return saludo.upper() if mayus else saludo
```

Cuando una función recibe o devuelve otra función, entramos en el terreno de
los decoradores: para eso, ver **T2 §1**.

## 4. Colecciones

Listas, tuplas, conjuntos y diccionarios:

- **Listas**: ordenadas y mutables.
- **Tuplas**: ordenadas e inmutables.
- **Conjuntos**: sin duplicados.
  - Útiles para pertenencia rápida.
- **Diccionarios**: pares clave-valor.

La iteración perezosa sobre colecciones se trata en **T2 §2**.
