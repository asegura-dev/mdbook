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
