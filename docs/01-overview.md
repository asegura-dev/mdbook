# Overview

mdbook takes a set of Markdown files and produces one HTML file you can open
anywhere. This manual is itself built with mdbook, so it doubles as a working
sample of the cross-references and navigation.

## 1. What it does

You give it an ordered list of `.md` files and a few options. It parses a fixed
subset of Markdown, builds a table of contents from the headings, and writes a
single self-contained `.html`: styles and scripts are inlined, so there are no
external requests. The output has a cover, a sidebar, instant search, a
light/dark toggle, and a copy button on each code block.

There is no project config file and no plugin system. The feature set is fixed
on purpose.

## 2. When to use it

It fits two cases. The first is reading long documentation on a phone: one file,
no server, search built in. The second is shipping browsable docs inside a repo
without a static-site toolchain.

If you need themes beyond light/dark, embedded images, or PDF export, this isn't
the tool — and adding them is out of scope.

## 3. How the pieces fit

There are three parts: a pure engine, a validation boundary, and two interfaces
on top. The engine is described in T2 §1, the boundary in T2 §2. The step from
Markdown files to HTML is the compilation flow in T3 §1. Cross-references — the
`T1 §3` style links you're reading now — are covered in T4 §1.
