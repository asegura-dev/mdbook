# Coupling and cohesion

Two words that get repeated until they stop meaning anything. They're worth
pinning down, because most "clean architecture" advice is just a consequence of
getting these two right.

## 1. What coupling is

Coupling is how much one piece of code needs to know about another. If changing
module A forces you to open module B, they're coupled. Some coupling is
unavoidable — code has to call other code — but the kind that hurts is the
hidden kind: shared globals, reaching into another module's internals, depending
on the order things run in.

A quick way to feel it: count what breaks when you rename something.

| Signal                         | Coupling |
| ------------------------------ | -------- |
| Call a documented function     | Low      |
| Pass a shared mutable object   | Medium   |
| Read another module's globals  | High     |
| Depend on import side effects  | High     |

## 2. What cohesion is

Cohesion is the opposite question: do the things inside one module belong
together? A module with high cohesion does one job. A `utils.py` that holds date
math, HTTP retries and a CSV parser has low cohesion — three jobs sharing a file
for no reason.

> Aim for high cohesion inside a module and low coupling between modules. The
> second tends to follow from the first.

## 3. The rule of thumb

You usually can't remove coupling, only aim it. Where the dependencies point
matters more than how many there are; that direction is the whole topic of
T2 §1. And the cheapest way to keep modules from leaking into each other is to
stop validating the same data everywhere and do it once at the edge — see T3 §1.
