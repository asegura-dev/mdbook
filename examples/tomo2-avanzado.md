# Tomo 2: Python avanzado

Continuación de los fundamentos. Aquí encontrarás referencias de vuelta al
primer tomo, como `T1 §3`.

## 1. Decoradores

Un decorador envuelve una función para añadirle comportamiento sin tocar su
cuerpo. Parte de lo visto en **T1 §3** (funciones) es prerrequisito.

```python
import functools


def temporiza(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__} tardó {perf_counter() - inicio:.4f}s")

    return wrapper
```

> Usa `functools.wraps` para conservar el nombre y la documentación originales.

## 2. Generadores

Los generadores producen valores de forma *perezosa* con `yield`, sin
materializar toda la colección (ver **T1 §4**):

```python
def naturales():
    n = 1
    while True:
        yield n
        n += 1
```

Esto permite trabajar con secuencias potencialmente infinitas usando poca
memoria.

## 3. Manejo de contexto

El bloque `with` garantiza la liberación de recursos:

```python
with open("datos.txt", encoding="utf-8") as f:
    contenido = f.read()
```

Puedes crear tus propios gestores con `contextlib.contextmanager`, que a su
vez es un **decorador** (T1 §3 y T2 §1).
