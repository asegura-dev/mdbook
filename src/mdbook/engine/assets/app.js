(function () {
  "use strict";

  var root = document.documentElement;
  var THEME_KEY = "mdbook-theme";

  // --- Theme (remembers the preference) ---------------------------------
  // The <select> is rendered server-side, one option per theme the contract
  // declares, so this script never holds its own copy of the theme list.
  var themeSelect = document.querySelector(".theme-select");

  function isKnownTheme(theme) {
    if (!theme || !themeSelect) return false;
    return Array.prototype.some.call(themeSelect.options, function (opt) {
      return opt.value === theme;
    });
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    // Keep the control honest: a theme restored from localStorage must show up
    // as the selected option, or the box says one thing and the page another.
    if (themeSelect) themeSelect.value = theme;
  }

  var saved = null;
  try { saved = localStorage.getItem(THEME_KEY); } catch (e) {}
  // A stale localStorage value (a theme that was renamed or removed) would
  // otherwise leave the page on an undefined palette.
  applyTheme(
    isKnownTheme(saved) ? saved : root.getAttribute("data-default-theme") || "light"
  );

  if (themeSelect) {
    themeSelect.addEventListener("change", function () {
      var next = themeSelect.value;
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
    });
  }

  // --- Export to PDF -----------------------------------------------------
  // The browser's own print pipeline; everything that makes the result look
  // like a document lives in the @media print rules, not here.
  var printBtn = document.querySelector(".print-btn");
  if (printBtn) {
    printBtn.addEventListener("click", function () {
      window.print();
    });
  }

  // --- Sidebar menu (mobile) --------------------------------------------
  var menuBtn = document.querySelector(".menu-btn");
  var backdrop = document.querySelector(".backdrop");
  function closeSidebar() { document.body.classList.remove("sidebar-open"); }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      document.body.classList.toggle("sidebar-open");
    });
  }
  if (backdrop) backdrop.addEventListener("click", closeSidebar);
  document.querySelectorAll(".toc a").forEach(function (a) {
    a.addEventListener("click", closeSidebar);
  });

  // --- Copy code ---------------------------------------------------------
  document.querySelectorAll(".copy-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var block = btn.closest(".code-block");
      var pre = block ? block.querySelector("pre") : null;
      if (!pre) return;
      var text = pre.innerText;
      function done() {
        btn.textContent = "Copied";
        btn.classList.add("done");
        setTimeout(function () {
          btn.textContent = "Copy";
          btn.classList.remove("done");
        }, 1500);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
      }
      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta);
        done();
      }
    });
  });

  // =======================================================================
  // Reader annotations: highlights and notes
  //
  // Anchoring is the whole problem here. The book gets recompiled while the
  // reader keeps annotating it, so an annotation cannot be stored as a
  // position: any edit earlier in the file would shift it. Each one stores the
  // text it covers plus the text around it, and is located again by searching.
  // The full model, and what it survives, is in T3 §6.
  // =======================================================================

  var ANN_VERSION = 1;
  var CONTEXT = 48; // characters of prefix/suffix kept for disambiguation

  function normalizeText(value) {
    // Collapsing whitespace is what makes an anchor survive reflowed Markdown,
    // re-indentation and a changed line width.
    return String(value).replace(/\s+/g, " ").trim();
  }

  function bookKey(title) {
    var slug = normalizeText(title)
      .normalize("NFD")
      .replace(/\p{Diacritic}/gu, "")
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/[\s_]+/g, "-")
      .replace(/^-+|-+$/g, "");
    // Local files share one localStorage origin, so two books would overwrite
    // each other without this namespace. Keyed by title, not by path, because
    // the point is to survive the file being rewritten.
    return "mdbook:notes:" + (slug || "untitled");
  }

  function commonHeadLength(a, b) {
    var limit = Math.min(a.length, b.length);
    var i = 0;
    while (i < limit && a.charAt(i) === b.charAt(i)) i++;
    return i;
  }

  function commonTailLength(a, b) {
    var limit = Math.min(a.length, b.length);
    var i = 0;
    while (i < limit && a.charAt(a.length - 1 - i) === b.charAt(b.length - 1 - i)) i++;
    return i;
  }

  /**
   * Where does `anchor.exact` sit in `haystack`? Returns the start index, or
   * -1 when the text is gone — in which case the annotation is orphaned rather
   * than guessed at. There is deliberately no fuzzy matching: a wrong anchor
   * silently highlights the wrong sentence, which is worse for study than an
   * honest orphan.
   */
  function locateQuote(haystack, anchor) {
    var quote = anchor.exact;
    if (!quote) return -1;

    var hits = [];
    var from = 0;
    var at;
    while ((at = haystack.indexOf(quote, from)) !== -1) {
      hits.push(at);
      from = at + 1;
    }
    if (hits.length === 0) return -1;
    if (hits.length === 1) return hits[0];

    var prefix = anchor.prefix || "";
    var suffix = anchor.suffix || "";
    var best = -1;
    var bestScore = -Infinity;
    for (var i = 0; i < hits.length; i++) {
      var start = hits[i];
      var before = haystack.slice(Math.max(0, start - prefix.length), start);
      var after = haystack.slice(start + quote.length, start + quote.length + suffix.length);
      var score = commonTailLength(before, prefix) + commonHeadLength(after, suffix);
      // A hit inside the section the annotation came from outranks context:
      // the same sentence quoted in two chapters is a real case.
      if (inPreferredRange(anchor, start)) score += 1000;
      if (score > bestScore || (score === bestScore && isCloser(anchor, start, best))) {
        best = start;
        bestScore = score;
      }
    }
    return best;
  }

  function inPreferredRange(anchor, start) {
    return (
      typeof anchor.preferFrom === "number" &&
      typeof anchor.preferTo === "number" &&
      start >= anchor.preferFrom &&
      start < anchor.preferTo
    );
  }

  function isCloser(anchor, candidate, current) {
    if (typeof anchor.offsetHint !== "number" || current < 0) return false;
    return Math.abs(candidate - anchor.offsetHint) < Math.abs(current - anchor.offsetHint);
  }

  function stripLeadingNumber(title) {
    return title.replace(/^\d+\.\s*/, "");
  }

  // --- Bridge between the DOM and the normalized text --------------------

  /**
   * The normalized text of an element plus, for every character, the text node
   * and offset it came from. That map is what lets a match found in a plain
   * string be painted back onto the DOM.
   */
  // Controls are not prose. Excluding them keeps the language label and the
  // "Copy" caption of a code block — and the note buttons this file injects —
  // out of the text an anchor is matched against.
  var NOT_PROSE = ".code-head, .sec-note, .ann-bar, .ann-pop, .review";

  function buildTextMap(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var parent = node.parentElement;
        if (parent && parent.closest(NOT_PROSE)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var chars = [];
    var map = [];
    var indexOfNode = new Map();
    var spaceAt = null;
    var node;
    while ((node = walker.nextNode())) {
      var value = node.nodeValue;
      for (var i = 0; i < value.length; i++) {
        var ch = value.charAt(i);
        if (ch === " " || ch === "\n" || ch === "\t" || ch === "\r") {
          // Remember where the run of whitespace started: mapping the collapsed
          // space to a real position keeps a painted highlight contiguous
          // instead of leaving a gap at every word break.
          if (chars.length > 0 && spaceAt === null) spaceAt = { node: node, offset: i };
          continue;
        }
        if (spaceAt !== null) {
          chars.push(" ");
          map.push(spaceAt);
          spaceAt = null;
        }
        if (!indexOfNode.has(node)) indexOfNode.set(node, chars.length);
        chars.push(ch);
        map.push({ node: node, offset: i });
      }
    }
    return { text: chars.join(""), map: map, indexOfNode: indexOfNode };
  }

  function firstIndexOf(textMap, element) {
    var walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null);
    var node = walker.nextNode();
    while (node) {
      if (textMap.indexOfNode.has(node)) return textMap.indexOfNode.get(node);
      node = walker.nextNode();
    }
    return -1;
  }

  /**
   * A heading's own words. Read from data-title because this file appends a
   * note button inside the heading, and textContent would otherwise include it.
   */
  function headingTitle(heading) {
    var stored = heading.getAttribute("data-title");
    if (stored !== null) return stored;
    var title = normalizeText(heading.textContent);
    heading.setAttribute("data-title", title);
    return title;
  }

  function matchesSection(heading, ann) {
    if (ann.sectionId && heading.id === ann.sectionId) return true;
    if (!ann.sectionTitle) return false;
    var title = headingTitle(heading);
    // Renumbering "## 3. Sampling" to "## 4." changes the id *and* the title,
    // so the number is dropped before comparing.
    return title === ann.sectionTitle ||
      stripLeadingNumber(title) === stripLeadingNumber(ann.sectionTitle);
  }

  function preferredRange(scope, textMap, ann) {
    var headings = scope.querySelectorAll("h1, h2, h3, h4, h5, h6");
    for (var i = 0; i < headings.length; i++) {
      if (!matchesSection(headings[i], ann)) continue;
      var from = firstIndexOf(textMap, headings[i]);
      if (from < 0) return null;
      var to = i + 1 < headings.length ? firstIndexOf(textMap, headings[i + 1]) : -1;
      return { from: from, to: to < 0 ? textMap.text.length : to };
    }
    return null;
  }

  function documentTitleOf(element) {
    var heading = element.querySelector("h1");
    return heading ? headingTitle(heading) : "";
  }

  function scopesFor(ann) {
    var scopes = [];
    var docs = document.querySelectorAll(".doc");
    var byTitle = null;
    for (var i = 0; i < docs.length && ann.docTitle; i++) {
      if (documentTitleOf(docs[i]) === ann.docTitle) {
        byTitle = docs[i];
        break;
      }
    }
    // Title before id: doc ids are positional, so inserting or reordering a
    // chapter silently points doc3 at different prose.
    if (byTitle) scopes.push(byTitle);
    var byId = ann.docId ? document.getElementById(ann.docId) : null;
    if (byId && byId !== byTitle && byId.classList.contains("doc")) scopes.push(byId);
    var content = document.querySelector(".content");
    if (content) scopes.push(content);
    return scopes;
  }

  // --- Painting ----------------------------------------------------------

  function wrapRun(run, ann) {
    var node = run.node;
    if (!node.parentNode) return;
    var target = run.start > 0 ? node.splitText(run.start) : node;
    if (target.nodeValue.length > run.end - run.start) {
      target.splitText(run.end - run.start);
    }
    var span = document.createElement("span");
    span.className = "hl";
    span.setAttribute("data-ann", ann.id);
    span.setAttribute("data-color", ann.color || "yellow");
    if (ann.note) span.setAttribute("data-note", "1");
    target.parentNode.insertBefore(span, target);
    span.appendChild(target);
  }

  function paintRange(textMap, start, end, ann) {
    var runs = [];
    for (var i = start; i < end && i < textMap.map.length; i++) {
      var entry = textMap.map[i];
      var last = runs[runs.length - 1];
      if (last && last.node === entry.node && entry.offset === last.end) {
        last.end = entry.offset + 1;
      } else {
        runs.push({ node: entry.node, start: entry.offset, end: entry.offset + 1 });
      }
    }
    // A highlight can cross <strong> or <code>, so each text node is wrapped
    // separately; back to front, because splitting invalidates later offsets.
    for (var r = runs.length - 1; r >= 0; r--) wrapRun(runs[r], ann);
    return runs.length > 0;
  }

  // --- Storage -----------------------------------------------------------

  var ANN_KEY = bookKey(document.title);
  var annotations = [];

  function loadAnnotations() {
    try {
      var raw = localStorage.getItem(ANN_KEY);
      if (!raw) return [];
      var data = JSON.parse(raw);
      return Array.isArray(data.items) ? data.items : [];
    } catch (e) {
      return [];
    }
  }

  function saveAnnotations(items) {
    try {
      localStorage.setItem(ANN_KEY, JSON.stringify({ version: ANN_VERSION, items: items }));
      return true;
    } catch (e) {
      // Quota exhausted or storage blocked. Reported rather than swallowed:
      // the reader has to know an annotation did not survive the click.
      return false;
    }
  }

  function placeAnnotation(ann) {
    var scopes = scopesFor(ann);
    for (var i = 0; i < scopes.length; i++) {
      var textMap = buildTextMap(scopes[i]);
      var range = preferredRange(scopes[i], textMap, ann);
      var at = locateQuote(textMap.text, {
        exact: ann.exact,
        prefix: ann.prefix,
        suffix: ann.suffix,
        offsetHint: ann.offsetHint,
        preferFrom: range ? range.from : undefined,
        preferTo: range ? range.to : undefined
      });
      if (at >= 0) return paintRange(textMap, at, at + ann.exact.length, ann);
    }
    return false;
  }

  function sectionHeadingFor(ann) {
    var headings = document.querySelectorAll(".content h1, .content h2, .content h3, .content h4");
    for (var i = 0; i < headings.length; i++) {
      if (matchesSection(headings[i], ann)) return headings[i];
    }
    return null;
  }

  /**
   * Paint the in-memory annotations and refresh their orphan flags. Returns
   * whether any flag changed, so the caller knows if storage is now stale.
   */
  function renderAnnotations() {
    var changed = false;
    annotations.forEach(function (ann) {
      var placed = ann.exact ? placeAnnotation(ann) : Boolean(sectionHeadingFor(ann));
      if (Boolean(ann.orphan) !== !placed) {
        ann.orphan = !placed;
        changed = true;
      }
    });
    return changed;
  }

  function applyAnnotations() {
    annotations = loadAnnotations();
    // Orphan state is recomputed on every load, so an annotation heals itself
    // when a later build brings its text back. Nothing is ever deleted here.
    if (renderAnnotations()) saveAnnotations(annotations);
    return annotations;
  }

  // --- Capture -----------------------------------------------------------

  function anchorFromRange(range) {
    var host = range.startContainer.parentElement;
    var doc = host ? host.closest(".doc") : null;
    if (!doc) return null;
    var exact = normalizeText(range.toString());
    if (!exact) return null;

    var textMap = buildTextMap(doc);
    var start = textMap.text.indexOf(exact);
    if (start < 0) return null;

    var heading = null;
    var headings = doc.querySelectorAll("h1, h2, h3, h4, h5, h6");
    for (var i = 0; i < headings.length; i++) {
      var at = firstIndexOf(textMap, headings[i]);
      if (at >= 0 && at <= start) heading = headings[i];
    }

    return {
      id: "a" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
      docId: doc.id,
      docTitle: documentTitleOf(doc),
      sectionId: heading ? heading.id : "",
      sectionTitle: heading ? headingTitle(heading) : "",
      exact: exact,
      prefix: textMap.text.slice(Math.max(0, start - CONTEXT), start),
      suffix: textMap.text.slice(start + exact.length, start + exact.length + CONTEXT),
      offsetHint: start,
      color: "yellow",
      note: "",
      orphan: false,
      created: Date.now()
    };
  }

  // --- Annotation UI -----------------------------------------------------

  var annBar = document.querySelector(".ann-bar");
  var annPop = document.querySelector(".ann-pop");
  var review = document.querySelector(".review");
  var notesBtn = document.querySelector(".notes-btn");
  var editingId = null;

  function byId(id) {
    for (var i = 0; i < annotations.length; i++) {
      if (annotations[i].id === id) return annotations[i];
    }
    return null;
  }

  function unpaintAll() {
    document.querySelectorAll(".hl").forEach(function (span) {
      var parent = span.parentNode;
      while (span.firstChild) parent.insertBefore(span.firstChild, span);
      parent.removeChild(span);
      parent.normalize();
    });
  }

  function persist() {
    unpaintAll();
    renderAnnotations();
    if (!saveAnnotations(annotations)) {
      // Never pretend a click was saved: storage can be full or blocked, and
      // the reader would keep annotating into a void.
      window.alert(
        "Could not save. Browser storage is full or blocked — export your notes " +
          "from the Notes panel before continuing."
      );
    }
    renderReview();
  }

  function place(element) {
    var rect = element.getBoundingClientRect();
    return { top: window.scrollY + rect.bottom + 8, left: window.scrollX + rect.left };
  }

  // --- Creating from a selection -----------------------------------------

  function currentRange() {
    var selection = window.getSelection();
    if (!selection || selection.isCollapsed || selection.rangeCount === 0) return null;
    var range = selection.getRangeAt(0);
    if (!normalizeText(range.toString())) return null;
    var host = range.commonAncestorContainer;
    host = host.nodeType === 1 ? host : host.parentElement;
    return host && host.closest(".doc") ? range : null;
  }

  // The range the toolbar is currently offering to highlight. Kept, rather than
  // read back on click, because pressing a button collapses the selection: by
  // the time the click handler runs there is nothing left to anchor to.
  var pendingRange = null;

  function closeBar() {
    pendingRange = null;
    if (annBar) annBar.hidden = true;
  }

  function closePopover() {
    editingId = null;
    if (annPop) annPop.hidden = true;
  }

  function closeOverlays() {
    closeBar();
    closePopover();
  }

  function showBar() {
    var range = currentRange();
    if (!range || !annBar) {
      closeBar();
      return;
    }
    pendingRange = range.cloneRange();
    var rect = range.getBoundingClientRect();
    annBar.hidden = false;
    annBar.style.top = window.scrollY + rect.top - annBar.offsetHeight - 8 + "px";
    annBar.style.left = window.scrollX + rect.left + "px";
  }

  /** The first existing highlight the range runs into, if any. */
  function overlappingHighlight(range) {
    var spans = document.querySelectorAll(".hl");
    for (var i = 0; i < spans.length; i++) {
      if (range.intersectsNode(spans[i])) return spans[i];
    }
    return null;
  }

  function createFromSelection(color, withNote) {
    var range = pendingRange || currentRange();
    closeBar();
    if (!range) return;

    // Highlights must not overlap. Nested spans paint unpredictably and a quote
    // could then contain another annotation's text, so a selection that runs
    // into an existing highlight edits that one instead of stacking on it.
    var existing = overlappingHighlight(range);
    if (existing) {
      window.getSelection().removeAllRanges();
      openPopover(existing.getAttribute("data-ann"), existing);
      return;
    }

    var ann = anchorFromRange(range);
    if (!ann) return;
    ann.color = color;
    annotations.push(ann);
    window.getSelection().removeAllRanges();
    persist();
    if (withNote) openPopover(ann.id);
  }

  if (annBar) {
    // Keep the selection alive: without this the browser collapses it the
    // instant the button takes the press, and there is nothing to highlight.
    annBar.addEventListener("mousedown", function (event) {
      event.preventDefault();
    });
    annBar.querySelectorAll(".ann-color").forEach(function (btn) {
      btn.addEventListener("click", function () {
        createFromSelection(btn.getAttribute("data-color"), false);
      });
    });
    var noteBtn = annBar.querySelector(".ann-note-btn");
    if (noteBtn) {
      noteBtn.addEventListener("click", function () {
        createFromSelection("yellow", true);
      });
    }
  }

  document.addEventListener("mouseup", function (event) {
    if (annBar && annBar.contains(event.target)) return;
    if (annPop && annPop.contains(event.target)) return;
    // After the browser has settled the selection.
    window.setTimeout(showBar, 0);
  });

  // Dismissal, on every route a reader would expect: pressing elsewhere,
  // scrolling away, or Escape. Relying on the click handler alone left both
  // overlays sitting on the page.
  document.addEventListener("mousedown", function (event) {
    if (annBar && annBar.contains(event.target)) return;
    if (annPop && annPop.contains(event.target)) return;
    closeBar();
    if (!event.target.closest(".hl") && !event.target.closest(".review-item")) {
      closePopover();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeOverlays();
  });

  window.addEventListener("scroll", closeBar, { passive: true });

  // --- Editing an existing annotation ------------------------------------

  function openPopover(id, element) {
    var ann = byId(id);
    if (!ann || !annPop) return;
    editingId = id;
    annPop.querySelector(".ann-pop-note").value = ann.note || "";
    annPop.querySelectorAll(".ann-color").forEach(function (btn) {
      btn.classList.toggle("on", btn.getAttribute("data-color") === ann.color);
    });
    annPop.hidden = false;
    var target = element || document.querySelector('[data-ann="' + id + '"]');
    if (target) {
      var at = place(target);
      annPop.style.top = at.top + "px";
      annPop.style.left = at.left + "px";
    }
  }

  if (annPop) {
    annPop.querySelectorAll(".ann-color").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var ann = byId(editingId);
        if (!ann) return;
        ann.color = btn.getAttribute("data-color");
        annPop.querySelectorAll(".ann-color").forEach(function (other) {
          other.classList.toggle("on", other === btn);
        });
        persist();
      });
    });
    annPop.querySelector(".ann-pop-save").addEventListener("click", function () {
      var ann = byId(editingId);
      if (!ann) return;
      ann.note = annPop.querySelector(".ann-pop-note").value.trim();
      closePopover();
      persist();
    });
    annPop.querySelector(".ann-pop-delete").addEventListener("click", function () {
      var id = editingId;
      annotations = annotations.filter(function (ann) {
        return ann.id !== id;
      });
      closePopover();
      persist();
    });
  }

  document.addEventListener("click", function (event) {
    var span = event.target.closest ? event.target.closest(".hl") : null;
    if (span) openPopover(span.getAttribute("data-ann"), span);
  });

  // --- Section notes ------------------------------------------------------

  function createSectionNote(heading) {
    var doc = heading.closest(".doc");
    var existing = null;
    for (var i = 0; i < annotations.length; i++) {
      if (!annotations[i].exact && annotations[i].sectionId === heading.id) {
        existing = annotations[i];
        break;
      }
    }
    if (!existing) {
      existing = {
        id: "s" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
        docId: doc ? doc.id : "",
        docTitle: doc ? documentTitleOf(doc) : "",
        sectionId: heading.id,
        sectionTitle: headingTitle(heading),
        exact: "",
        prefix: "",
        suffix: "",
        color: "yellow",
        note: "",
        orphan: false,
        created: Date.now()
      };
      annotations.push(existing);
      persist();
    }
    openPopover(existing.id, heading);
  }

  document.querySelectorAll(".content .doc h2, .content .doc h3").forEach(function (heading) {
    headingTitle(heading); // freeze the title before the button joins the DOM
    var btn = document.createElement("button");
    btn.className = "sec-note";
    btn.type = "button";
    btn.setAttribute("aria-label", "Note on this section");
    btn.textContent = "✎";
    btn.addEventListener("click", function (event) {
      event.stopPropagation();
      createSectionNote(heading);
    });
    heading.appendChild(btn);
  });

  // --- Review panel -------------------------------------------------------

  function inDocumentOrder(list) {
    var positions = {};
    document.querySelectorAll(".hl").forEach(function (span, index) {
      var id = span.getAttribute("data-ann");
      if (!(id in positions)) positions[id] = index;
    });
    return list.slice().sort(function (a, b) {
      var pa = a.id in positions ? positions[a.id] : Number.MAX_SAFE_INTEGER;
      var pb = b.id in positions ? positions[b.id] : Number.MAX_SAFE_INTEGER;
      return pa - pb || (a.created || 0) - (b.created || 0);
    });
  }

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function renderItem(ann) {
    var item = element("div", "review-item");
    item.setAttribute("data-ann", ann.id);
    if (ann.orphan) item.classList.add("orphan");
    item.appendChild(element("div", "review-where", ann.sectionTitle || ann.docTitle || ""));
    if (ann.exact) {
      var quote = element("blockquote", "review-quote", ann.exact);
      quote.setAttribute("data-color", ann.color || "yellow");
      item.appendChild(quote);
    }
    if (ann.note) item.appendChild(element("p", "review-note", ann.note));
    item.addEventListener("click", function () {
      var span = document.querySelector('[data-ann="' + ann.id + '"]');
      if (span) {
        span.scrollIntoView({ block: "center" });
        openPopover(ann.id, span);
      } else {
        openPopover(ann.id, item);
      }
    });
    return item;
  }

  function renderReview() {
    if (!review) return;
    var list = review.querySelector(".review-list");
    list.textContent = "";

    var live = inDocumentOrder(
      annotations.filter(function (ann) {
        return !ann.orphan;
      })
    );
    var orphans = annotations.filter(function (ann) {
      return ann.orphan;
    });

    if (!annotations.length) {
      list.appendChild(
        element("p", "review-empty", "Select text in the book to highlight it.")
      );
    }

    var lastGroup = null;
    live.forEach(function (ann) {
      if (ann.docTitle !== lastGroup) {
        list.appendChild(element("h3", "review-group", ann.docTitle || "Untitled"));
        lastGroup = ann.docTitle;
      }
      list.appendChild(renderItem(ann));
    });

    if (orphans.length) {
      // Kept, never deleted: the text they were attached to changed, but the
      // reader's own words are still theirs.
      list.appendChild(element("h3", "review-group orphan", "Orphaned (" + orphans.length + ")"));
      list.appendChild(
        element(
          "p",
          "review-hint",
          "The text these were on has changed. They are kept here, and reattach on their own if it comes back."
        )
      );
      orphans.forEach(function (ann) {
        list.appendChild(renderItem(ann));
      });
    }

    var count = annotations.length;
    var badge = document.querySelector(".notes-count");
    if (badge) badge.textContent = count ? String(count) : "";
    // Drives the print appendix: with nothing to say it must not claim a page.
    review.setAttribute("data-count", String(count));
  }

  if (notesBtn && review) {
    notesBtn.addEventListener("click", function () {
      review.hidden = !review.hidden;
    });
    review.querySelector(".review-close").addEventListener("click", function () {
      review.hidden = true;
    });
  }

  // --- Export -------------------------------------------------------------

  function toMarkdown() {
    var lines = ["# Notes — " + document.title, ""];
    var lastGroup = null;
    var live = inDocumentOrder(
      annotations.filter(function (ann) {
        return !ann.orphan;
      })
    );
    live.concat(annotations.filter(function (a) { return a.orphan; })).forEach(function (ann) {
      var group = ann.orphan ? "Orphaned" : ann.docTitle || "Untitled";
      if (group !== lastGroup) {
        lines.push("## " + group, "");
        lastGroup = group;
      }
      if (ann.sectionTitle) lines.push("### " + ann.sectionTitle, "");
      if (ann.exact) lines.push("> " + ann.exact, "");
      if (ann.note) lines.push(ann.note, "");
    });
    return lines.join("\n");
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(null, fallbackCopy);
    } else {
      fallbackCopy();
    }
    function fallbackCopy() {
      var area = document.createElement("textarea");
      area.value = text;
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      try { document.execCommand("copy"); } catch (e) {}
      document.body.removeChild(area);
    }
  }

  if (review) {
    var copyBtn = review.querySelector(".review-copy");
    copyBtn.addEventListener("click", function () {
      copyText(toMarkdown());
      copyBtn.textContent = "Copied";
      window.setTimeout(function () { copyBtn.textContent = "Copy as Markdown"; }, 1500);
    });
    review.querySelector(".review-download").addEventListener("click", function () {
      var blob = new Blob([toMarkdown()], { type: "text/markdown;charset=utf-8" });
      var url = URL.createObjectURL(blob);
      var link = document.createElement("a");
      link.href = url;
      link.download = bookKey(document.title).replace("mdbook:notes:", "") + "-notes.md";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
  }

  applyAnnotations();
  renderReview();

  // Exposed for the Node tests of the anchor resolver (T3 §6). `module` does
  // not exist in a browser, so this is a no-op there.
  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      normalizeText: normalizeText,
      bookKey: bookKey,
      locateQuote: locateQuote,
      stripLeadingNumber: stripLeadingNumber
    };
  }

  // --- Group content by section (so search can filter) ------------------
  document.querySelectorAll(".doc").forEach(function (doc) {
    var current = doc.id;
    Array.prototype.forEach.call(doc.children, function (el) {
      if (/^H[1-6]$/.test(el.tagName) && el.id) current = el.id;
      el.dataset.sec = current;
    });
  });

  // --- Instant search (filter and highlight) ----------------------------
  var content = document.querySelector(".content");
  var cover = document.querySelector(".cover");
  var searchInput = document.querySelector(".search");

  function clearHighlights() {
    document.querySelectorAll("mark.hit").forEach(function (m) {
      var parent = m.parentNode;
      parent.replaceChild(document.createTextNode(m.textContent), m);
      parent.normalize();
    });
  }

  function highlight(query) {
    var walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue.toLowerCase().includes(query)) return NodeFilter.FILTER_REJECT;
        var p = node.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        if (p.closest("pre")) return NodeFilter.FILTER_REJECT;
        var sec = p.closest("[data-sec]");
        if (sec && sec.style.display === "none") return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(function (node) {
      var text = node.nodeValue;
      var lower = text.toLowerCase();
      var frag = document.createDocumentFragment();
      var i = 0, idx, last = 0;
      while ((idx = lower.indexOf(query, i)) !== -1) {
        frag.appendChild(document.createTextNode(text.slice(last, idx)));
        var mark = document.createElement("mark");
        mark.className = "hit";
        mark.textContent = text.slice(idx, idx + query.length);
        frag.appendChild(mark);
        i = idx + query.length;
        last = i;
      }
      frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    });
  }

  function resetSearch() {
    document.querySelectorAll("[data-sec]").forEach(function (e) { e.style.display = ""; });
    document.querySelectorAll(".doc").forEach(function (e) { e.style.display = ""; });
    document.querySelectorAll(".toc-doc, .toc-sec").forEach(function (e) { e.style.display = ""; });
    if (cover) cover.style.display = "";
  }

  function runSearch(rawQuery) {
    clearHighlights();
    var query = rawQuery.trim().toLowerCase();
    if (!query) { resetSearch(); return; }

    var matched = {};
    document.querySelectorAll(".content [data-sec]").forEach(function (el) {
      if (el.textContent.toLowerCase().includes(query)) matched[el.dataset.sec] = true;
    });

    document.querySelectorAll(".content [data-sec]").forEach(function (el) {
      el.style.display = matched[el.dataset.sec] ? "" : "none";
    });
    document.querySelectorAll(".doc").forEach(function (doc) {
      var visible = Array.prototype.some.call(doc.children, function (c) {
        return c.style.display !== "none";
      });
      doc.style.display = visible ? "" : "none";
    });
    if (cover) cover.style.display = "none";

    document.querySelectorAll(".toc-doc").forEach(function (li) {
      var docEl = document.getElementById(li.dataset.doc);
      var docVisible = docEl && docEl.style.display !== "none";
      li.style.display = docVisible ? "" : "none";
      li.querySelectorAll(".toc-sec").forEach(function (s) {
        s.style.display = matched[s.dataset.target] ? "" : "none";
      });
    });

    highlight(query);
  }

  if (searchInput) {
    searchInput.addEventListener("input", function () { runSearch(searchInput.value); });
  }

  // --- Scrollspy: mark the active section in the table of contents -------
  var tocLinks = {};
  document.querySelectorAll(".toc a").forEach(function (a) {
    tocLinks[a.getAttribute("href").slice(1)] = a;
  });
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var link = tocLinks[entry.target.id];
          if (!link) return;
          if (entry.isIntersecting) {
            Object.keys(tocLinks).forEach(function (k) { tocLinks[k].classList.remove("active"); });
            link.classList.add("active");
          }
        });
      },
      { rootMargin: "-10% 0px -80% 0px", threshold: 0 }
    );
    document.querySelectorAll(".doc [id], .doc").forEach(function (el) {
      if (el.id && tocLinks[el.id]) observer.observe(el);
    });
  }
})();
