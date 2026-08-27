(function () {
  "use strict";

  var $ = function (sel, scope) { return (scope || document).querySelector(sel); };
  var $$ = function (sel, scope) { return Array.prototype.slice.call((scope || document).querySelectorAll(sel)); };
  function safe(fn, name) { try { return fn(); } catch (e) { console.warn("[" + name + "]", e); } }
  function escHTML(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  var DB = window.__DB__ || { productos: [], scoreAxes: {} };
  var STORAGE_KEY = "g3d_compare_ids";

  function getSelection() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) { return []; }
  }
  function setSelection(ids) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(ids)); } catch (e) {}
  }
  function findProduct(id) {
    for (var i = 0; i < DB.productos.length; i++) if (DB.productos[i].id === id) return DB.productos[i];
    return null;
  }

  // ---------------------------------------------------------------- nav

  function initNavToggle() {
    var btn = $("#navToggle"), nav = $("#mobileNav");
    if (!btn || !nav) return;
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // ---------------------------------------------------------------- gallery

  function initGallery() {
    var wrap = $("[data-galeria]");
    if (!wrap) return;
    var main = $(".ficha-img-main", wrap);
    var thumbs = $$(".ficha-thumbs img", wrap);
    if (!main || !thumbs.length) return;
    thumbs.forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        main.src = thumb.src;
        thumbs.forEach(function (t) { t.classList.remove("is-active"); });
        thumb.classList.add("is-active");
      });
    });
  }

  // ---------------------------------------------------------------- radar chart (hand-drawn canvas)

  function drawRadar(canvas, series, opts) {
    if (!canvas || !canvas.getContext) return;
    opts = opts || {};
    var labels = series[0] ? series[0].labels : [];
    var n = labels.length;
    if (n < 3) return;
    var dpr = window.devicePixelRatio || 1;
    var w = canvas.width, h = canvas.height;
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    var cx = w / 2, cy = h / 2 - 6, radius = Math.min(w, h) / 2 - 46;
    var rings = 5;

    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = "#e2dcd3";
    ctx.lineWidth = 1;

    // rings
    for (var r = 1; r <= rings; r++) {
      var rr = (radius * r) / rings;
      ctx.beginPath();
      for (var i = 0; i <= n; i++) {
        var ang = (Math.PI * 2 * i) / n - Math.PI / 2;
        var px = cx + rr * Math.cos(ang), py = cy + rr * Math.sin(ang);
        if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      }
      ctx.stroke();
    }
    // spokes + labels
    ctx.fillStyle = "#6b6155";
    ctx.font = "11px Inter, sans-serif";
    for (i = 0; i < n; i++) {
      ang = (Math.PI * 2 * i) / n - Math.PI / 2;
      px = cx + radius * Math.cos(ang);
      py = cy + radius * Math.sin(ang);
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(px, py);
      ctx.stroke();
      var lx = cx + (radius + 14) * Math.cos(ang);
      var ly = cy + (radius + 14) * Math.sin(ang);
      ctx.textAlign = Math.cos(ang) > 0.3 ? "left" : (Math.cos(ang) < -0.3 ? "right" : "center");
      ctx.textBaseline = Math.sin(ang) > 0.3 ? "top" : (Math.sin(ang) < -0.3 ? "bottom" : "middle");
      ctx.fillText(labels[i], lx, ly);
    }

    // series polygons
    series.forEach(function (s) {
      ctx.beginPath();
      for (var i = 0; i <= n; i++) {
        var idx = i % n;
        var v = Math.max(0, Math.min(10, s.values[idx] || 0));
        var rr = (radius * v) / 10;
        var ang = (Math.PI * 2 * idx) / n - Math.PI / 2;
        var px = cx + rr * Math.cos(ang), py = cy + rr * Math.sin(ang);
        if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      }
      ctx.closePath();
      ctx.fillStyle = s.color + "33";
      ctx.strokeStyle = s.color;
      ctx.lineWidth = 2;
      ctx.fill();
      ctx.stroke();
    });
  }

  var RADAR_COLORS = ["#c2540c", "#0f6b5c", "#1f5fa8", "#a83f8f"];

  function initFichaRadar() {
    var wrap = $("[data-radar]");
    if (!wrap) return;
    var canvas = $("canvas", wrap);
    if (!canvas) return;
    var data;
    try { data = JSON.parse(wrap.getAttribute("data-radar")); } catch (e) { return; }
    drawRadar(canvas, [{ labels: data.labels, values: data.values, color: RADAR_COLORS[0] }]);
  }

  // ---------------------------------------------------------------- add-to-comparator button (ficha pages)

  function initComparadorAddButtons() {
    var btns = $$("[data-add-comparador]");
    if (!btns.length) return;
    var selection = getSelection();
    btns.forEach(function (btn) {
      var id = btn.getAttribute("data-add-comparador");
      function refresh() {
        var active = selection.indexOf(id) > -1;
        btn.classList.toggle("is-active", active);
        btn.textContent = active ? "✓ En el comparador" : "+ Añadir al comparador";
      }
      refresh();
      btn.addEventListener("click", function () {
        var i = selection.indexOf(id);
        if (i > -1) selection.splice(i, 1); else selection.push(id);
        setSelection(selection);
        refresh();
      });
    });
  }

  // ---------------------------------------------------------------- comparador page

  function initComparadorPage() {
    var root = $("[data-comparador-root]");
    if (!root) return;

    var tabs = $$("[data-nicho-tab]");
    var panels = $$("[data-nicho-panel]");
    var activeNicho = (tabs[0] && tabs[0].getAttribute("data-nicho-tab")) || "impresora";

    function setActiveTab(nicho) {
      activeNicho = nicho;
      tabs.forEach(function (t) { t.classList.toggle("is-active", t.getAttribute("data-nicho-tab") === nicho); });
      panels.forEach(function (p) { p.hidden = p.getAttribute("data-nicho-panel") !== nicho; });
      render();
    }

    tabs.forEach(function (t) {
      t.addEventListener("click", function () { setActiveTab(t.getAttribute("data-nicho-tab")); });
    });

    var MAX_COMPARE = RADAR_COLORS.length;
    var limitMsg = $("[data-compare-limit-msg]");

    $$("[data-compare-check]").forEach(function (chk) {
      chk.addEventListener("change", function () {
        var selection = getSelection();
        var id = chk.value;
        var i = selection.indexOf(id);
        var panel = chk.closest("[data-nicho-panel]");
        var nicho = panel ? panel.getAttribute("data-nicho-panel") : activeNicho;
        var countInNicho = selection.filter(function (pid) {
          var p = findProduct(pid);
          return p && p.nicho === nicho;
        }).length;
        if (chk.checked && i === -1 && countInNicho >= MAX_COMPARE) {
          chk.checked = false;
          if (limitMsg) {
            limitMsg.textContent = "Puedes comparar un máximo de " + MAX_COMPARE + " productos a la vez. Quita alguno para añadir este.";
            limitMsg.hidden = false;
          }
          return;
        }
        if (limitMsg) limitMsg.hidden = true;
        if (chk.checked && i === -1) selection.push(id);
        if (!chk.checked && i > -1) selection.splice(i, 1);
        setSelection(selection);
        render();
      });
    });

    function restoreChecks() {
      var selection = getSelection();
      $$("[data-compare-check]").forEach(function (chk) {
        chk.checked = selection.indexOf(chk.value) > -1;
      });
    }

    function bestClass(field, values, better) {
      if (!better) return values.map(function () { return false; });
      var nums = values.map(function (v) { return typeof v === "number" ? v : null; });
      var valid = nums.filter(function (v) { return v !== null; });
      if (!valid.length) return values.map(function () { return false; });
      var target = better === "max" ? Math.max.apply(null, valid) : Math.min.apply(null, valid);
      return nums.map(function (v) { return v !== null && v === target; });
    }

    function fmtEUR(v) {
      if (v == null) return "—";
      var parts = v.toFixed(2).split(".");
      var intPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
      return (parts[1] === "00" ? intPart : intPart + "," + parts[1]) + " €";
    }

    function render() {
      var selection = getSelection();
      var productos = selection.map(findProduct).filter(function (p) { return p && p.nicho === activeNicho; }).slice(0, MAX_COMPARE);
      if (productos.length < 2) {
        root.innerHTML = '<div class="comparador-empty empty-state"><div class="empty-icon">⚖️</div><p>Selecciona al menos 2 productos de "' + escHTML(activeNicho) + '" para ver la comparativa.</p></div>';
        return;
      }

      var axes = (DB.scoreAxes && DB.scoreAxes[activeNicho]) || [];
      var series = productos.map(function (p, i) {
        return {
          labels: axes.map(function (a) { return a[1]; }),
          values: axes.map(function (a) { return p[a[0]] != null ? p[a[0]] : 0; }),
          color: RADAR_COLORS[i % RADAR_COLORS.length]
        };
      });

      var legend = productos.map(function (p, i) {
        return '<span><span class="dot" style="background:' + RADAR_COLORS[i % RADAR_COLORS.length] + '"></span>' + escHTML(p.name) + '</span>';
      }).join("");

      var head = '<tr><th>Especificación</th>' + productos.map(function (p) {
        var ficha = "producto-" + p.id + ".html";
        return '<th class="compare-col-head">' +
          '<a class="compare-name-link" href="' + escHTML(ficha) + '">' +
          (p.images && p.images[0] ? '<img src="' + escHTML(p.images[0]) + '" alt="">' : '') +
          '<div>' + escHTML(p.name) + '</div>' +
          '</a>' +
          '<a class="compare-ver-ficha" href="' + escHTML(ficha) + '">Ver análisis completo →</a>' +
          '<a class="btn-comprar" style="padding:.5rem .9rem;font-size:.78rem;" href="' + escHTML(p.affiliate_url) + '" target="_blank" rel="sponsored nofollow noopener">' + (p.isDemo ? "Ver opciones" : "Ver en Amazon") + '</a>' +
          '</th>';
      }).join("") + "</tr>";

      var specFields = (DB.specFields && DB.specFields[activeNicho]) || [];
      var rows = specFields.map(function (f) {
        var values = productos.map(function (p) { return p[f.field]; });
        var best = bestClass(f.field, values, f.better);
        var cells = values.map(function (v, i) {
          var display;
          if (v === null || v === undefined || v === "") display = "—";
          else if (f.field === "discountedPrice") display = fmtEUR(v);
          else if (typeof v === "boolean") display = v ? "Sí" : "No";
          else display = f.unit ? v + " " + f.unit : v;
          return '<td class="' + (best[i] ? "is-best" : "") + '">' + escHTML(display) + '</td>';
        }).join("");
        return '<tr><th scope="row">' + escHTML(f.label) + '</th>' + cells + '</tr>';
      }).join("");

      var extraRows =
        '<tr><th scope="row">Ventajas</th>' + productos.map(function (p) {
          return '<td class="compare-list-cell"><ul>' + (p.pros || []).slice(0, 3).map(function (x) { return '<li>' + escHTML(x) + '</li>'; }).join("") + '</ul></td>';
        }).join("") + '</tr>' +
        '<tr><th scope="row">Inconvenientes</th>' + productos.map(function (p) {
          return '<td class="compare-list-cell"><ul>' + (p.contras || []).slice(0, 3).map(function (x) { return '<li>' + escHTML(x) + '</li>'; }).join("") + '</ul></td>';
        }).join("") + '</tr>' +
        '<tr><th scope="row">Mejor para...</th>' + productos.map(function (p) {
          return '<td class="compare-text-cell">' + escHTML(p.ideal_para || "—") + '</td>';
        }).join("") + '</tr>';
      rows = rows + extraRows;

      root.innerHTML =
        '<div class="comparador-result-inner">' +
        '<div class="comparador-radar-overlay">' +
        '<canvas id="radarCompare" width="340" height="300"></canvas>' +
        '<div class="radar-legend">' + legend + '</div>' +
        '</div>' +
        '<div class="compare-table-wrap"><table class="compare-table">' +
        '<thead>' + head + '</thead><tbody>' + rows + '</tbody>' +
        '</table></div>' +
        '</div>';

      drawRadar($("#radarCompare"), series);
    }

    restoreChecks();
    setActiveTab(activeNicho);
  }

  // ---------------------------------------------------------------- boot

  function boot() {
    safe(initNavToggle, "initNavToggle");
    safe(initGallery, "initGallery");
    safe(initFichaRadar, "initFichaRadar");
    safe(initComparadorAddButtons, "initComparadorAddButtons");
    safe(initComparadorPage, "initComparadorPage");
    document.documentElement.classList.add("is-ready");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
