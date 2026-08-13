/**
 * Tests for the anchor resolver in engine/assets/app.js.
 *
 * This is the one piece of the annotation feature where a bug loses a reader's
 * work silently: a highlight that anchors to the wrong sentence, or fails to
 * anchor at all, looks like the feature "just lost" a note. Python cannot
 * exercise it, so it runs under Node's built-in test runner — no package.json,
 * no dependencies. Everything else in the feature is covered by the acceptance
 * procedure in T3 §6.
 *
 * app.js is loaded as-is, with a minimal browser stub, so the code under test
 * is exactly the code that ships.
 */

const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const APP = path.join(
  __dirname, "..", "..", "src", "mdbook", "engine", "assets", "app.js"
);

// A page-shaped stub, not a DOM: every query comes back empty, so the UI wiring
// in app.js finds nothing to attach to and only the pure functions are left to
// test. It grows when app.js starts touching a new browser API — which is the
// point of loading the real file rather than a copy of it.
function loadApp() {
  const noElement = { getAttribute: () => null, setAttribute: () => {}, options: [] };
  const sandbox = {
    module: { exports: {} },
    Map,
    Math,
    Date,
    JSON,
    String,
    Number,
    navigator: {},
    window: { print: () => {}, setTimeout: () => 0, alert: () => {}, getSelection: () => null },
    localStorage: { getItem: () => null, setItem: () => {} },
    document: {
      title: "Test Book",
      documentElement: noElement,
      body: { classList: { remove: () => {}, toggle: () => {} } },
      addEventListener: () => {},
      createElement: () => ({ style: {}, classList: { toggle: () => {} } }),
      querySelector: () => null,
      querySelectorAll: () => [],
      createTreeWalker: () => ({ nextNode: () => null }),
    },
  };
  vm.runInNewContext(fs.readFileSync(APP, "utf8"), sandbox, { filename: APP });
  return sandbox.module.exports;
}

const app = loadApp();

test("app.js exposes the resolver", () => {
  assert.ok(typeof app.locateQuote === "function");
  assert.ok(typeof app.normalizeText === "function");
  assert.ok(typeof app.bookKey === "function");
});

test("normalizeText collapses the whitespace a recompile changes", () => {
  assert.strictEqual(app.normalizeText("  two   words\n\tagain "), "two words again");
  assert.strictEqual(app.normalizeText("same"), "same");
});

test("bookKey namespaces by title, since local files share one origin", () => {
  assert.strictEqual(app.bookKey("My Thesis"), "mdbook:notes:my-thesis");
  // Accents must not change the key between builds.
  assert.strictEqual(app.bookKey("Análisis Numérico"), "mdbook:notes:analisis-numerico");
  assert.strictEqual(app.bookKey("   "), "mdbook:notes:untitled");
  // Two books cannot collide.
  assert.notStrictEqual(app.bookKey("Book A"), app.bookKey("Book B"));
});

test("a unique quote is found wherever it moved to", () => {
  const hay = "intro text. the sampling frame was small. more text.";
  const at = app.locateQuote(hay, { exact: "the sampling frame was small" });
  assert.strictEqual(hay.slice(at, at + 28), "the sampling frame was small");
});

test("missing text orphans instead of guessing", () => {
  // The quote was edited: no fuzzy fallback, on purpose. A wrong anchor
  // contaminates a review; an orphan is honest.
  const hay = "the sampling frame was tiny";
  assert.strictEqual(app.locateQuote(hay, { exact: "the sampling frame was small" }), -1);
  assert.strictEqual(app.locateQuote(hay, { exact: "" }), -1);
});

test("context picks the right copy of a repeated sentence", () => {
  const hay =
    "chapter one says see the results below and continues. " +
    "chapter two says see the results below and ends.";
  const second = hay.lastIndexOf("see the results below");

  const at = app.locateQuote(hay, {
    exact: "see the results below",
    prefix: "chapter two says ",
    suffix: " and ends.",
  });
  assert.strictEqual(at, second);

  const first = hay.indexOf("see the results below");
  assert.strictEqual(
    app.locateQuote(hay, {
      exact: "see the results below",
      prefix: "chapter one says ",
      suffix: " and continues.",
    }),
    first
  );
});

test("the annotation's own section outranks context", () => {
  const hay = "aaa the method bbb the method ccc";
  const second = hay.lastIndexOf("the method");
  // Context points at the first copy, but the preferred range covers only the
  // second: a quote lives in the section it was made in.
  const at = app.locateQuote(hay, {
    exact: "the method",
    prefix: "aaa ",
    suffix: " bbb",
    preferFrom: second - 4,
    preferTo: hay.length,
  });
  assert.strictEqual(at, second);
});

test("the old offset only breaks ties between equal contexts", () => {
  const hay = "xx term yy term zz";
  const first = hay.indexOf("term");
  const last = hay.lastIndexOf("term");
  assert.strictEqual(
    app.locateQuote(hay, { exact: "term", prefix: "", suffix: "", offsetHint: last }),
    last
  );
  assert.strictEqual(
    app.locateQuote(hay, { exact: "term", prefix: "", suffix: "", offsetHint: first }),
    first
  );
});

test("editing elsewhere does not move the anchor", () => {
  const before = "old opening. the key claim holds. tail.";
  const after = "a much longer rewritten opening paragraph. the key claim holds. tail.";
  const anchor = { exact: "the key claim holds", prefix: "old opening. ", suffix: ". tail." };

  const found = app.locateQuote(after, anchor);
  assert.ok(found > 0);
  assert.strictEqual(after.slice(found, found + anchor.exact.length), anchor.exact);
  assert.notStrictEqual(found, app.locateQuote(before, anchor));
});

test("renumbering a section is invisible to the comparison", () => {
  assert.strictEqual(app.stripLeadingNumber("3. Sampling"), "Sampling");
  assert.strictEqual(app.stripLeadingNumber("12. Results and discussion"), "Results and discussion");
  assert.strictEqual(app.stripLeadingNumber("Introduction"), "Introduction");
});
