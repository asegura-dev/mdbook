# When not to add structure

Every pattern in this guide has a cost. The mistake that follows reading about
architecture is applying all of it to a script that didn't need any.

## 1. Structure has a cost

An interface, a layer, an abstraction — each one is a thing to name, navigate and
keep in your head. That cost is worth paying when it buys you something:
independent testing, a swappable detail, a boundary that stops a mess from
spreading. When it buys nothing, it's just indirection.

```python
# over-engineered for a one-off
class GreeterFactory:
    def create(self) -> "Greeter": ...

# fine
def greet(name: str) -> str:
    return f"Hello, {name}"
```

## 2. Signs you went too far

> If you have to open four files to follow one request, the structure is working
> against you.

- An interface with exactly one implementation and no plan for a second.
- Wrappers that only forward calls.
- A layer every change has to pass through untouched.
- More test scaffolding than code under test.

## 3. A checklist

The patterns in T2 §2 and T3 §3 are tools, not goals. Reach for them when the
pain they remove is real, not before. And when in doubt, optimize for cohesion
first (T1 §2) — a small, focused module is easy to split later; a premature
abstraction is hard to take back.

| Question                                  | If "no"…              |
| ----------------------------------------- | --------------------- |
| Is there a second implementation, or soon?| Skip the interface    |
| Does the layer catch a real failure?      | Drop the layer        |
| Would a junior find this faster?          | Reconsider the split  |
