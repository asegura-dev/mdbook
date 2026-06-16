# Dependency direction

The single idea behind layered, hexagonal and "clean" architectures is the same:
control which way the arrows point. Everything else is naming.

## 1. Dependencies point inward

Put the rules that define what your program *is* — the domain logic — at the
center, and let everything else depend on it. The center depends on nothing
outward: not the database, not the web framework, not the CLI. This is just
cohesion (T1 §2) applied across modules instead of inside one.

Concretely: the core imports no I/O, and the I/O imports the core.

```python
# core.py  — knows nothing about storage or HTTP
def price_with_tax(amount: float, rate: float) -> float:
    return round(amount * (1 + rate), 2)

# api.py  — depends on core, never the other way around
from core import price_with_tax
```

## 2. The dependency inversion trick

When the center genuinely needs something from the outside — "save this" — it
declares an interface and lets the outer layer implement it. The arrow flips: the
detail now depends on the abstraction the core owns.

```python
from typing import Protocol

class Repository(Protocol):
    def save(self, order: "Order") -> None: ...

def checkout(order: "Order", repo: Repository) -> None:
    repo.save(order)            # core depends on the Protocol, not on a DB
```

## 3. A worked example

mdbook is a small instance of this. The engine is the center; it produces HTML
from a validated request and imports neither Typer nor Tkinter. The CLI and the
GUI sit on the outside and depend on the engine. The thing the core insists on —
valid input — is handled at the edge, which is T3 §2.
