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

## 6. Reader annotations

Highlights and notes live in the reader's browser, in `localStorage`, and never
leave the machine. The interesting problem is not storing them but finding them
again: the book gets recompiled while the reader keeps annotating it.

### The anchor

An annotation cannot be a position — any edit earlier in the file would shift
it. Each one stores the text it covers, 48 characters of context on each side,
and the titles of the chapter and section it came from. Whitespace is collapsed
before storing and before searching, which is what carries an anchor across
reflowed Markdown and re-indentation.

Resolution walks from the most stable identifier to the least. The chapter is
found by title before id, because ids are positional: `doc3` is whatever the
third file happens to be, so inserting a chapter would silently point it at
different prose. The section is matched by id, then by title, then by title with
its leading number removed, because renumbering `## 3.` to `## 4.` changes both
the id and the title. The quote is then searched inside that section, widening
to the chapter and then to the whole book. Where a phrase occurs more than once,
the stored context decides between the copies.

There is deliberately no fuzzy matching. Editing the highlighted words orphans
the annotation instead of relocating it. A wrong anchor highlights the wrong
sentence without saying so and quietly corrupts a review; an orphan is visible
and can be dealt with. Orphans are kept, listed in their own group in the review
panel, and never deleted — and because orphan state is recomputed on every load,
an annotation reattaches by itself when a later build brings its text back.

Storage is namespaced by book title. That is not a precaution: every local file
shares one `localStorage` origin, so without the namespace two books would
overwrite each other. Keying by title rather than by path is what lets
annotations survive the file being rewritten — and means renaming the book
starts a fresh set. The 5 MB quota is shared across every local file the browser
has open, and the export exists so nothing here is the only copy.

Highlights may not overlap. Nested spans paint unpredictably, and once nested,
one annotation's stored quote can contain another's text, which corrupts both
the export and the review list. Selecting over an existing highlight edits it.

### Acceptance procedure

The resolver has tests (`tests/js`, run under Node). The rest of the feature —
selection, painting, the panel, the export — is checked by hand, with these
steps, which are written down so they are repeated the same way each time:

1. Compile a book, highlight three passages in different chapters, attach a note
   to one, and add a section note. Reload: all four come back.
2. Edit a chapter — rewrite an earlier paragraph, renumber a section, and insert
   a new chapter before the others. Recompile and reload: all four still come
   back, with the section note attached to the renumbered heading.
3. Edit the words inside one highlight. Recompile and reload: that one appears
   under "Orphaned" with its text and note intact, and the others are untouched.
4. Undo that edit, recompile, reload: the orphan reattaches on its own.
5. Export to Markdown and check every annotation is present, orphans included.
6. Print: highlights appear as coloured underlines, note markers do not, and the
   panel prints as an appendix at the end.

Step 6 is the one that catches a stale artifact: the samples and the executable
embed these assets, so both must be rebuilt before they can show any of this —
see T7 §3.
