# Tomo 2: Temas avanzados

Una breve introducción al tomo avanzado.

## 1. Decoradores

Los decoradores envuelven funciones.

```python
import functools


def temporiza(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

## 2. Generadores

Los generadores producen valores de forma perezosa con `yield`.
