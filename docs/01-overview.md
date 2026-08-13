# Overview

mdbook takes a set of Markdown files and produces one HTML file you can open
anywhere. This manual is itself built with mdbook, so it doubles as a working
sample of the cross-references and navigation.

## 1. What it does

You give it an ordered list of `.md` files and a few options. It parses a fixed
subset of Markdown, builds a table of contents from the headings, and writes a
single self-contained `.html`: styles and scripts are inlined, so there are no
external requests. The output has a cover, a sidebar, instant search, a theme
picker, and a copy button on each code block.

Four themes ship: `light`, `dark`, `sepia` and `serif`. The first three differ
only in palette; `serif` also swaps the typeface for a system serif stack and
loosens the leading, for reading rather than reference. The reader can switch
between them in the page, and the choice is remembered.

A "PDF" button exports the page through the browser's own print pipeline. There
is no PDF library involved — the output is the same HTML with a print
stylesheet, described in T3 §5.

There is no project config file and no plugin system. The feature set is fixed
on purpose.

## 2. When to use it

It fits two cases. The first is reading long documentation on a phone: one file,
no server, search built in. The second is shipping browsable docs inside a repo
without a static-site toolchain.

If you need embedded images, PDF export or a custom palette of your own, this
isn't the tool — and adding them is out of scope.

## 3. How the pieces fit

There are three parts: a pure engine, a validation boundary, and two interfaces
on top. The engine is described in T2 §1, the boundary in T2 §2. The step from
Markdown files to HTML is the compilation flow in T3 §1. Cross-references — the
`T1 §3` style links you're reading now — are covered in T4 §1.
