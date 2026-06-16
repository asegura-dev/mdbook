# Volume 2: Advanced topics

A short intro to the advanced volume.

## 1. Decorators

Decorators wrap functions.

```python
import functools


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

## 2. Generators

Generators yield values lazily with `yield`.
