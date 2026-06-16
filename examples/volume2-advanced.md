# Volume 2: Advanced Python

A follow-up to the fundamentals. This one references the first volume, like
`T1 §3`.

## 1. Decorators

A decorator wraps a function to add behavior without touching its body. Part of
T1 §3 (functions) is a prerequisite.

```python
import functools


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__} took {perf_counter() - start:.4f}s")

    return wrapper
```

> Use `functools.wraps` to keep the original name and docstring.

## 2. Generators

Generators produce values *lazily* with `yield`, without materializing the
whole collection (see T1 §4):

```python
def naturals():
    n = 1
    while True:
        yield n
        n += 1
```

This lets you work with potentially infinite sequences using little memory.

## 3. Context managers

The `with` block guarantees cleanup:

```python
with open("data.txt", encoding="utf-8") as f:
    content = f.read()
```

You can write your own with `contextlib.contextmanager`, which is itself a
**decorator** (T1 §3 and T2 §1).
