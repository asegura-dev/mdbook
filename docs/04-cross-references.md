# Cross-references

An optional feature that turns short references in the prose into internal
links. It's off by default; turn it on with `--cross-refs` or the GUI checkbox.

## 1. Syntax

A reference looks like `T1 §3`. `T<n>` is the document number in the order of
the work (1-based), and `§<m>` is a numbered section in that document. Spacing is
flexible: `T1§3`, `T1 §3` and `T1 § 3` all match. The regex only fires on this
shape, so ordinary prose isn't touched.

## 2. How section numbers are resolved

`§<m>` does not mean "the m-th heading". It means the heading whose text starts
with `m.` — so `## 3. Functions` is §3, and an unnumbered `### Notes` is skipped
entirely. The number comes straight from the text, which is why the count can
jump (a `## 10.` is §10 even if it's the third heading). Section numbers are
assigned during parsing; see T3 §2. If the same number appears twice, the first
one wins.

## 3. Behavior when a target is missing

If a reference points at a document or section that doesn't exist, nothing
happens to it — the text is left exactly as written, no broken link. That keeps
a typo from turning into a dead anchor. The rewriting runs on already-escaped
text, so references inside code spans are not affected.
