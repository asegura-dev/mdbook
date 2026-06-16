# Volume 1: Python fundamentals

This volume covers the basics of the language. Cross-references like `T2 §1`
become links when you compile with that option on.

## 1. Variables and types

A variable is a name bound to a value. Python infers the type:

```python
name = "Ada"        # str
age = 36            # int
active = True       # bool
```

The types you reach for most often:

| Type   | Example     | Mutable |
| ------ | ----------- | ------- |
| `int`  | `42`        | No      |
| `str`  | `"hi"`      | No      |
| `list` | `[1, 2, 3]` | Yes     |
| `dict` | `{"a": 1}`  | Yes     |

## 2. Control flow

Flow is controlled with `if`, `for` and `while`.

> In Python, **indentation** defines blocks, not braces.

```python
for i in range(3):
    if i % 2 == 0:
        print(f"{i} is even")
    else:
        print(f"{i} is odd")
```

## 3. Functions

Functions are defined with `def` and can take *default values*:

```python
def greet(name: str, upper: bool = False) -> str:
    msg = f"Hello, {name}"
    return msg.upper() if upper else msg
```

When a function takes or returns another function, you are in decorator
territory: see T2 §1.

## 4. Collections

Lists, tuples, sets and dicts:

- **Lists**: ordered and mutable.
- **Tuples**: ordered and immutable.
- **Sets**: no duplicates.
  - Handy for fast membership tests.
- **Dicts**: key-value pairs.

Lazy iteration over collections is covered in T2 §2.
