# Validation at the boundary

If the core trusts its inputs, something else has to make them trustworthy. That
job lives at the boundary — the thin layer where external data becomes internal
data.

## 1. Validate once, at the edge

Pick the line where untrusted input crosses into your program and validate there,
once. Past that line, every function can assume the data is well-formed. The
alternative — re-checking the same fields in every function "to be safe" — spreads
the same knowledge everywhere and is exactly the coupling T1 §1 warns about.

## 2. The core trusts its inputs

A validated value should be a *type*, not a convention. Parse into something the
core can rely on, and the checks disappear from the inner functions.

```python
from pydantic import BaseModel, field_validator

class BuildRequest(BaseModel):
    title: str
    theme: str

    @field_validator("theme")
    @classmethod
    def known_theme(cls, v: str) -> str:
        if v not in ("light", "dark"):
            raise ValueError("theme must be light or dark")
        return v
```

> "Parse, don't validate": turn the input into a type that can't hold a bad
> value, instead of checking a bag of strings over and over.

## 3. Where to put the contract

Keep the contract in its own module, between the outside and the core, so both
the CLI and the GUI build the same object. The boundary is also where side
effects gather, which is the subject of T4 §2.

| Layer      | Responsibility            | Trusts input? |
| ---------- | ------------------------- | ------------- |
| Interface  | Collect raw input         | No            |
| Boundary   | Validate, build the type  | Turns No→Yes  |
| Core       | Apply the rules           | Yes           |
