# Compilation flow

This is what happens between a validated `BuildOptions` and the file on disk.
The entry points are `compile_html` (returns a string) and `compile_book`
(writes it and returns the path).

## 1. Two passes

The build runs in two passes over the documents. The reason is cross-references:
a link in document 1 can point to a section in document 3, so every section has
to be known before any text is rendered. Pass one indexes all documents; pass
two renders them.

## 2. Pass one: parse and index

For each file, `parse_document` parses the Markdown to tokens and walks the
headings. It takes the first `#` as the document title, slugifies every heading
into a unique `id`, and records each heading's numbered-section value — the
number is read from the heading text, not from its position. Those numbers are
what cross-references resolve against; the details are in T4 §2.

## 3. Pass two: render

With the full section index in hand, `build_crossref_map` builds the lookup
table and `render_document` turns each document's tokens into HTML. Custom
render rules handle two things: fenced code blocks get a header with the
language and a copy button, and text nodes get the `T1 §3` patterns rewritten
into links when cross-references are on.

## 4. Assembly and output

`renderer.build_html` reads the three assets, builds the sidebar and the cover
index from the model, and substitutes everything into the template. The result
is one HTML string. `compile_book` writes it where `BuildOptions.output` points.

## 5. Printing and PDF export

The "PDF" button calls `window.print()` and nothing else. There is no PDF
library, no server and no second output format: the page prints itself, so the
export cannot go stale relative to the HTML and adds no dependency to the
executable.

The work is in the `@media print` rules. Screen chrome is hidden, each document
starts on a fresh page, the cover and its contents list take a page of their
own, code blocks and quotes resist breaking, and tables become real tables again
(on screen they are `display: block` for horizontal scrolling, which stops them
paginating) so a long one repeats its header across pages. External links print
their URL after the text; internal cross-references do not, since the anchor
means nothing on paper.

Two decisions are worth knowing about. The palette is forced light — and the
typeface serif — by specificity: `:root:root` outweighs any `[data-theme="…"]`
block, so no JavaScript has to swap the theme and put it back. Swapping it would
leave the reader on the wrong theme if they cancelled the print dialog. And
because the rule names no theme, a theme added later is neutralised without
touching the print block. Second, browsers omit background fills unless the
reader enables "Background graphics", so anything that must be visible on paper
is drawn with borders and ink rather than with a fill.

What this approach cannot do, in exchange for costing nothing: there are no page
numbers of our own — `@page` margin boxes are CSS Paged Media, which browsers do
not implement, and the header and footer you see come from the print dialog and
are outside our control. Breaks are requests, not guarantees: an element taller
than a page still breaks. Output differs between browsers, so pick one for
reproducible drafts. If page-level typographic control ever matters more than
portability, that is the point to reconsider the approach — not before.
