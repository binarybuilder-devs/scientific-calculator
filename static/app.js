// app.js - builds the UI from the backend's operation list and talks to /api/calculate.
(() => {
  const menu = document.getElementById("menu");
  const form = document.getElementById("form");
  const panel = document.getElementById("panel");
  const icon = document.getElementById("op-icon");
  const title = document.getElementById("op-title");
  const desc = document.getElementById("op-desc");
  const empty = document.getElementById("empty");
  const workspace = document.getElementById("workspace");
  const calcBtn = document.getElementById("calc-btn");
  const clearBtn = document.getElementById("clear-btn");
  const resultBox = document.getElementById("result");
  const resultOut = document.getElementById("result-value");
  const errorBox = document.getElementById("error");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let operations = [];
  let current = null;
  let listValues = [];       // for "list" fields
  let tileEls = new Map();
  let indicator = null;
  let indicatorReady = false;

  // ---------- helpers ----------
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function animate(el, keyframes, options) {
    if (reduceMotion || !el.animate) return null;
    return el.animate(keyframes, { duration: 400, easing: "cubic-bezier(0.22,1,0.36,1)", ...options });
  }

  // Move the sliding highlight to a tile.
  function moveIndicator(el) {
    if (!el || !indicator) return;
    if (!indicatorReady) {
      indicator.classList.add("instant");
      indicatorReady = true;
    } else {
      indicator.classList.remove("instant");
    }
    indicator.style.width = el.offsetWidth + "px";
    indicator.style.height = el.offsetHeight + "px";
    indicator.style.transform = `translate(${el.offsetLeft}px, ${el.offsetTop}px)`;
    indicator.style.opacity = "1";
    requestAnimationFrame(() => indicator.classList.remove("instant"));
  }
  window.addEventListener("resize", () => {
    if (current) moveIndicator(tileEls.get(current.key));
  });

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.hidden = false;
    errorBox.style.animation = "none";
    void errorBox.offsetWidth;                    // restart shake
    errorBox.style.animation = "";
  }
  function hideError() { errorBox.hidden = true; errorBox.textContent = ""; }

  // Count up the number so the result feels like it is being worked out.
  function showResult(text) {
    resultBox.hidden = false;
    resultBox.style.animation = "none";
    void resultBox.offsetWidth;
    resultBox.style.animation = "";
    const num = Number(text);
    if (reduceMotion || !Number.isFinite(num) || !/^-?\d+(\.\d+)?(e[+-]?\d+)?$/i.test(text)) {
      resultOut.textContent = text;
      return;
    }
    const start = performance.now(), dur = 600;
    const decimals = (text.split(".")[1] || "").length;
    const step = (now) => {
      const t = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      resultOut.textContent = (num * eased).toFixed(t < 1 ? decimals : decimals);
      if (t < 1) requestAnimationFrame(step); else resultOut.textContent = text;
    };
    requestAnimationFrame(step);
  }

  // ---------- menu ----------
  function buildMenu() {
    menu.innerHTML = "";
    tileEls = new Map();
    indicator = document.createElement("span");
    indicator.className = "indicator instant";
    menu.appendChild(indicator);
    indicatorReady = false;
    operations.forEach((op, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "tile";
      b.style.setProperty("--i", i);
      b.innerHTML = `<span class="glyph">${escapeHtml(op.icon)}</span>
                     <span class="name">${escapeHtml(op.label)}</span>
                     <span class="cat">${escapeHtml(op.category)}</span>`;
      b.addEventListener("click", () => selectOp(op.key));
      menu.appendChild(b);
      tileEls.set(op.key, b);
    });
  }

  // ---------- form ----------
  function renderField(f) {
    if (f.type === "choice") {
      const wrap = document.createElement("div");
      wrap.className = "field";
      const name = `choice-${f.name}`;
      wrap.innerHTML = `<span>${escapeHtml(f.label)}</span>`;
      const seg = document.createElement("div");
      seg.className = "seg";
      seg.dataset.field = f.name;
      seg.innerHTML = `<div class="thumb"></div>` + f.options.map((o, idx) =>
        `<label><input type="radio" name="${name}" value="${escapeHtml(o.value)}" ${idx === 0 ? "checked" : ""}>
         <span>${escapeHtml(o.label)}</span></label>`).join("");
      wrap.appendChild(seg);
      // move the sliding thumb to the checked option
      const moveThumb = (animated) => {
        const thumb = seg.querySelector(".thumb");
        const checked = seg.querySelector("input:checked");
        const label = checked.closest("label");
        const sr = seg.getBoundingClientRect(), lr = label.getBoundingClientRect();
        const x = lr.left - sr.left - 4;
        thumb.style.transition = animated ? "" : "none";
        thumb.style.width = lr.width + "px";
        thumb.style.transform = `translateX(${x}px)`;
        if (!animated) requestAnimationFrame(() => (thumb.style.transition = ""));
      };
      seg.addEventListener("change", () => { moveThumb(true); animate(seg, [{ transform: "scale(.98)" }, { transform: "none" }], { duration: 300 }); });
      requestAnimationFrame(() => moveThumb(false));
      return wrap;
    }

    if (f.type === "list") {
      const wrap = document.createElement("div");
      wrap.className = "field";
      wrap.innerHTML = `<span>${escapeHtml(f.label)} (add at least 2)</span>
        <div class="chips" id="chips"></div>
        <div class="add-row">
          <input type="number" id="list-input" inputmode="numeric" step="1" placeholder="Type a number">
          <button type="button" class="btn ghost" id="list-add">Add</button>
        </div>`;
      const addValue = () => {
        const input = wrap.querySelector("#list-input");
        const v = input.value.trim();
        if (v === "") return;
        listValues.push(v);
        input.value = "";
        renderChips(wrap);
        input.focus();
      };
      wrap.querySelector("#list-add").addEventListener("click", addValue);
      wrap.querySelector("#list-input").addEventListener("keydown", (e) => {
        if (e.key === "Enter") { e.preventDefault(); addValue(); }
      });
      renderChips(wrap);
      return wrap;
    }

    // int / num
    const wrap = document.createElement("label");
    wrap.className = "field";
    const step = f.type === "int" ? "1" : "any";
    wrap.innerHTML = `<span>${escapeHtml(f.label)}</span>
      <input type="number" name="${escapeHtml(f.name)}" step="${step}" inputmode="decimal" required>`;
    return wrap;
  }

  function renderChips(wrap) {
    const chips = wrap.querySelector("#chips");
    chips.innerHTML = "";
    listValues.forEach((v, idx) => {
      const c = document.createElement("span");
      c.className = "chip";
      c.innerHTML = `${escapeHtml(v)} <button type="button" aria-label="Remove ${escapeHtml(v)}">×</button>`;
      c.querySelector("button").addEventListener("click", () => {
        const done = () => { listValues.splice(idx, 1); renderChips(wrap); };
        const anim = animate(c, [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "scale(.8)" }], { duration: 220 });
        anim ? (anim.onfinish = done) : done();
      });
      chips.appendChild(c);
    });
    if (listValues.length === 0) chips.innerHTML = `<span class="muted">No numbers yet</span>`;
  }

  // Fade the old panel out, then render the new calculation and fade it in.
  function selectOp(key) {
    const op = operations.find((o) => o.key === key);
    if (!op) return;
    if (!workspace.hidden && !reduceMotion && workspace.animate) {
      const out = workspace.animate(
        [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(-8px)" }],
        { duration: 160, easing: "ease-in" });
      out.onfinish = () => renderOp(op);
    } else {
      renderOp(op);
    }
  }

  function renderOp(op) {
    current = op;
    listValues = [];
    hideError();
    resultBox.hidden = true;

    tileEls.forEach((el, k) => el.classList.toggle("active", k === op.key));
    moveIndicator(tileEls.get(op.key));
    animate(workspace, [{ opacity: 0, transform: "translateY(12px)" }, { opacity: 1, transform: "none" }], { duration: 420 });
    icon.textContent = op.icon;
    title.textContent = op.label;
    desc.textContent = op.desc;

    form.innerHTML = "";
    op.fields.forEach((f) => {
      const el = renderField(f);
      if (f.type === "list" || f.type === "choice") el.classList.add("wide");
      form.appendChild(el);
    });
    empty.hidden = true;
    workspace.hidden = false;

    // staggered field entrance
    [...form.children].forEach((el, i) =>
      animate(el, [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }],
        { duration: 420, delay: i * 70, fill: "backwards" }));
    const firstInput = form.querySelector("input");
    if (firstInput) setTimeout(() => firstInput.focus({ preventScroll: true }), 120);
  }

  // ---------- submit ----------
  function collectValues() {
    const values = {};
    const data = new FormData(form);
    for (const f of current.fields) {
      if (f.type === "list") values[f.name] = listValues.slice();
      else if (f.type === "choice") values[f.name] = data.get(`choice-${f.name}`);
      else {
        const raw = data.get(f.name);
        if (raw === null || String(raw).trim() === "") throw new Error(`Please fill in "${f.label}".`);
        values[f.name] = String(raw);
      }
    }
    return values;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    let values;
    try { values = collectValues(); }
    catch (err) { showError(err.message); return; }

    calcBtn.classList.add("loading");
    calcBtn.textContent = "Calculating…";
    try {
      const res = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: current.key, values }),
      });
      const data = await res.json();
      if (!data.ok) { resultBox.hidden = true; showError(data.error); return; }
      showResult(data.result);
    } catch {
      showError("Could not reach the server. Is app.py running?");
    } finally {
      calcBtn.classList.remove("loading");
      calcBtn.textContent = "Calculate";
    }
  });

  clearBtn.addEventListener("click", () => {
    if (!current) return;
    form.querySelectorAll("input").forEach((i) => { if (i.type !== "radio") i.value = ""; });
    listValues = [];
    const listWrap = form.querySelector("#chips")?.closest(".field");
    if (listWrap) renderChips(listWrap);
    resultBox.hidden = true;
    hideError();
  });

  // ---------- start ----------
  fetch("/api/operations")
    .then((r) => r.json())
    .then((ops) => { operations = ops; buildMenu(); })
    .catch(() => showError("Could not load calculations. Is app.py running?"));
})();
