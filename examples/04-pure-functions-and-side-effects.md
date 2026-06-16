# Pure functions and side effects

A pure function is the easiest thing to test, read and move. The trick isn't
making everything pure — you can't — it's keeping the impure parts in as few
places as possible.

## 1. What makes a function pure

A function is pure when its output depends only on its arguments and it changes
nothing outside itself: no globals, no disk, no clock, no network. Same input,
same output, every time.

```python
# pure: depends only on its args
def slugify(text: str) -> str:
    return "-".join(text.lower().split())

# impure: reads the clock and writes a file
def write_log(msg: str) -> None:
    with open("log.txt", "a") as f:
        f.write(f"{now()} {msg}\n")
```

## 2. Push side effects to the edges

You can't avoid I/O, but you can corner it. Keep a pure core that computes
results, and a thin shell that reads inputs and writes outputs. This is the same
arrow from T2 §1, seen from a different angle: the impure shell depends on the
pure center.

> Functional core, imperative shell. Decide in the core, act in the shell.

## 3. Why this helps testing

Pure functions need no mocks — you call them and assert on the return value. The
impure shell shrinks to a few functions you can check with one integration test.
Boundary validation (T3 §1) is one of those edges: parse at the door, compute in
the middle, write at the other door.
