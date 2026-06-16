(function () {
  "use strict";

  var root = document.documentElement;
  var THEME_KEY = "mdbook-theme";

  // --- Tema (recuerda la preferencia) -----------------------------------
  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    var btn = document.querySelector(".theme-btn");
    if (btn) btn.innerHTML = theme === "dark" ? "&#9728;" : "&#9789;";
  }
  var saved = null;
  try { saved = localStorage.getItem(THEME_KEY); } catch (e) {}
  applyTheme(saved || root.getAttribute("data-default-theme") || "light");

  var themeBtn = document.querySelector(".theme-btn");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
    });
  }

  // --- Menú lateral (celular) -------------------------------------------
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

  // --- Copiar código -----------------------------------------------------
  document.querySelectorAll(".copy-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var block = btn.closest(".code-block");
      var pre = block ? block.querySelector("pre") : null;
      if (!pre) return;
      var text = pre.innerText;
      function done() {
        btn.textContent = "Copiado";
        btn.classList.add("done");
        setTimeout(function () {
          btn.textContent = "Copiar";
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

  // --- Agrupar contenido por sección (para filtrar en la búsqueda) ------
  document.querySelectorAll(".doc").forEach(function (doc) {
    var current = doc.id;
    Array.prototype.forEach.call(doc.children, function (el) {
      if (/^H[1-6]$/.test(el.tagName) && el.id) current = el.id;
      el.dataset.sec = current;
    });
  });

  // --- Búsqueda instantánea (filtra y resalta) --------------------------
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

  // --- Scrollspy: marca la sección activa en el índice ------------------
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
