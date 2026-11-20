/* ================= ML & AI live demos (run in the browser) ================= */
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || "#888";
const PAL = () => [cssv("--lab0"), cssv("--lab1"), cssv("--lab2"), cssv("--lab3"), cssv("--lab4"), cssv("--lab5")];
function mkCanvas(host, w, h, label){
  const c = document.createElement("canvas"); c.width = w * 2; c.height = h * 2; c.className = "mlcv"; c.style.aspectRatio = w + " / " + h;
  c.setAttribute("role", "img"); c.setAttribute("aria-label", label || "demo plot"); host.appendChild(c);
  const ctx = c.getContext("2d"); ctx.scale(2, 2); ctx.W = w; ctx.H = h; return ctx;
}
const clear = ctx => { ctx.clearRect(0, 0, ctx.W, ctx.H); ctx.fillStyle = cssv("--panel"); ctx.fillRect(0, 0, ctx.W, ctx.H); };
const dot = (ctx, x, y, r, fill, stroke) => { ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = fill; ctx.fill(); if (stroke) { ctx.lineWidth = 1.5; ctx.strokeStyle = stroke; ctx.stroke(); } };
const ctl = html => `<div class="labctl">${html}</div>`;
const outBox = () => `<div class="labout" aria-live="polite"></div>`;
const cvPos = (ctx, e) => { const r = ctx.canvas.getBoundingClientRect(); return [(e.clientX - r.left) / r.width * ctx.W, (e.clientY - r.top) / r.height * ctx.H]; };
function rng(seed){ let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const gauss = r => { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
function bars(ctx, vals, x0, y0, w, h, color, labels){
  const mx = Math.max(...vals, 1e-9), bw = w / vals.length;
  vals.forEach((v, i) => { const bh = v / mx * h; ctx.fillStyle = color; ctx.fillRect(x0 + i * bw + 1, y0 + h - bh, bw - 2, bh); });
  if (labels) { ctx.fillStyle = cssv("--muted"); ctx.font = "10px " + cssv("--mono"); ctx.textAlign = "center"; labels.forEach((l, i) => ctx.fillText(l, x0 + (i + 0.5) * bw, y0 + h + 12)); }
}
function twoClass(seed, kind, n = 120){
  const r = rng(seed), pts = [];
  for (let i = 0; i < n; i++) {
    let x, y, c = i % 2;
    if (kind === "moons") { const t = r() * Math.PI; x = c ? 1 - Math.cos(t) : Math.cos(t); y = c ? 0.5 - Math.sin(t) : Math.sin(t); x = (x + 1.2) / 3.4; y = (y + 0.9) / 2.1; x += gauss(r) * 0.05; y += gauss(r) * 0.06; }
    else if (kind === "circles") { const a = r() * 7, rad = c ? 0.13 + r() * 0.07 : 0.32 + r() * 0.08; x = 0.5 + rad * Math.cos(a); y = 0.5 + rad * Math.sin(a); }
    else if (kind === "xor") { x = r(); y = r(); c = (x > 0.5) !== (y > 0.5) ? 1 : 0; }
    else if (kind === "spiral") { const t = (i >> 1) / (n / 2) * 3.2; const s = c ? Math.PI : 0; x = 0.5 + 0.42 * (t / 3.2) * Math.cos(t * 1.6 + s) + gauss(r) * 0.015; y = 0.5 + 0.42 * (t / 3.2) * Math.sin(t * 1.6 + s) + gauss(r) * 0.015; }
    else { x = (c ? 0.62 : 0.38) + gauss(r) * 0.12; y = (c ? 0.6 : 0.4) + gauss(r) * 0.12; }
    pts.push([x, y, c]);
  }
  return pts;
}

const ML_DEMOS = {
  clt(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Source <select data-d><option value="exp">Exponential (skewed)</option><option value="uni">Uniform</option><option value="bi">Two humps</option></select></label><label>Sample size n <input type="range" min="1" max="60" value="1" data-n><span data-nv>1</span></label><button type="button" data-go>Draw 500 sample means</button><button type="button" data-reset>Reset</button>`) + outBox();
    const ctx = mkCanvas(b, 520, 220, "Histogram of sample means"); const r = rng(7); let means = [];
    const draw1 = d => d === "exp" ? -Math.log(1 - r()) : d === "uni" ? r() * 2 : (r() < 0.5 ? 0.3 : 1.7) + gauss(r) * 0.15;
    const sd = {exp: 1, uni: 2 / Math.sqrt(12), bi: Math.sqrt(0.49 + 0.0225)};
    const render = () => {
      clear(ctx); const d = b.querySelector("[data-d]").value, n = +b.querySelector("[data-n]").value;
      if (!means.length) { ctx.fillStyle = cssv("--muted"); ctx.font = "13px " + cssv("--sans"); ctx.fillText("Press 'Draw' to collect means of n samples each.", 20, 110); }
      else { const lo = 0, hi = 3, B = 40, h = Array(B).fill(0); means.forEach(m => { const k = Math.floor((m - lo) / (hi - lo) * B); if (k >= 0 && k < B) h[k]++; });
        bars(ctx, h, 10, 10, 500, 185, cssv("--lab0")); ctx.fillStyle = cssv("--muted"); ctx.font = "10px " + cssv("--mono"); [0, 1, 2, 3].forEach(v => ctx.fillText(v, 10 + v / 3 * 500, 210)); }
      const mu = means.reduce((a, x) => a + x, 0) / (means.length || 1), s = Math.sqrt(means.reduce((a, x) => a + (x - mu) ** 2, 0) / Math.max(1, means.length - 1));
      b.querySelector(".labout").innerHTML = `<p>${means.length} means · average ${mu.toFixed(3)} · spread (std) ${s.toFixed(3)} vs theory σ/√n = ${(sd[d] / Math.sqrt(n)).toFixed(3)}. ${n >= 20 ? "The shape is now close to a normal bell curve, even though the source isn't." : "Increase n: the histogram of means becomes bell-shaped and narrower."}</p>`;
    };
    b.querySelector("[data-go]").onclick = () => { const d = b.querySelector("[data-d]").value, n = +b.querySelector("[data-n]").value; for (let i = 0; i < 500; i++) { let s = 0; for (let j = 0; j < n; j++) s += draw1(d); means.push(s / n); } render(); };
    b.querySelector("[data-reset]").onclick = () => { means = []; render(); };
    b.querySelector("[data-n]").oninput = e => { b.querySelector("[data-nv]").textContent = e.target.value; means = []; render(); };
    b.querySelector("[data-d]").onchange = () => { means = []; render(); }; render();
  },

  gd(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Surface <select data-f><option value="bowl">Round bowl</option><option value="valley" selected>Narrow valley</option><option value="two">Two minima</option></select></label><label>Optimiser <select data-o><option>Gradient descent</option><option>Momentum</option><option>Adam</option></select></label><label>Learning rate <input type="range" min="-3" max="0" step="0.05" value="-1.3" data-lr><span data-lrv></span></label><button type="button" data-run>Run 80 steps</button>`) + `<p class="labnote">Click anywhere on the surface to choose the starting point. Darker = lower loss.</p>` + outBox();
    const ctx = mkCanvas(b, 340, 340, "Loss surface with optimisation path"); let start = [-1.6, 1.6], path = [];
    const F = {bowl: [(x, y) => x * x + y * y, (x, y) => [2 * x, 2 * y]], valley: [(x, y) => 0.5 * x * x + 8 * y * y, (x, y) => [x, 16 * y]],
               two: [(x, y) => (x * x - 1) ** 2 + 0.8 * y * y + 0.3 * x, (x, y) => [4 * x * (x * x - 1) + 0.3, 1.6 * y]]};
    const toPx = v => (v + 2) / 4 * 340, toV = p => p / 340 * 4 - 2;
    let bg = null, bgKey = "";
    const render = () => {
      const f = F[b.querySelector("[data-f]").value][0], key = b.querySelector("[data-f]").value + document.documentElement.dataset.theme;
      if (bgKey !== key) { const off = document.createElement("canvas"); off.width = off.height = 170; const o = off.getContext("2d"), img = o.createImageData(170, 170);
        let mx = 0; const vals = []; for (let j = 0; j < 170; j++) for (let i = 0; i < 170; i++) { const v = Math.log(1 + f(i / 170 * 4 - 2, j / 170 * 4 - 2)); vals.push(v); mx = Math.max(mx, v); }
        const dark = matchMedia("(prefers-color-scheme: dark)").matches && document.documentElement.dataset.theme !== "light" || document.documentElement.dataset.theme === "dark";
        vals.forEach((v, k) => { const t = v / mx, band = Math.floor(t * 14) % 2 ? 0.92 : 1; const c = dark ? [30 + 120 * t, 50 + 110 * t, 90 + 120 * t] : [40 + 200 * t, 90 + 150 * t, 160 + 90 * t];
          img.data.set([c[0] * band, c[1] * band, c[2] * band, 255], k * 4); });
        o.putImageData(img, 0, 0); bg = off; bgKey = key; }
      ctx.drawImage(bg, 0, 0, 340, 340);
      ctx.strokeStyle = cssv("--lab1"); ctx.lineWidth = 2; ctx.beginPath(); path.forEach(([x, y], i) => i ? ctx.lineTo(toPx(x), toPx(y)) : ctx.moveTo(toPx(x), toPx(y))); ctx.stroke();
      path.forEach(([x, y], i) => dot(ctx, toPx(x), toPx(y), i ? 2.5 : 5, cssv("--lab1")));
      if (!path.length) dot(ctx, toPx(start[0]), toPx(start[1]), 5, cssv("--lab1"));
    };
    const run = () => {
      const [f, g] = F[b.querySelector("[data-f]").value], opt = b.querySelector("[data-o]").value, lr = 10 ** +b.querySelector("[data-lr]").value;
      let [x, y] = start, v = [0, 0], m = [0, 0], s = [0, 0]; path = [[x, y]]; let diverged = false;
      for (let t = 1; t <= 80; t++) { const gr = g(x, y);
        if (opt === "Momentum") { v = [0.9 * v[0] + gr[0], 0.9 * v[1] + gr[1]]; x -= lr * v[0]; y -= lr * v[1]; }
        else if (opt === "Adam") { m = m.map((a, i) => 0.9 * a + 0.1 * gr[i]); s = s.map((a, i) => 0.999 * a + 0.001 * gr[i] ** 2);
          const mh = m.map(a => a / (1 - 0.9 ** t)), sh = s.map(a => a / (1 - 0.999 ** t)); x -= lr * mh[0] / (Math.sqrt(sh[0]) + 1e-8); y -= lr * mh[1] / (Math.sqrt(sh[1]) + 1e-8); }
        else { x -= lr * gr[0]; y -= lr * gr[1]; }
        if (!isFinite(x) || Math.abs(x) > 50 || Math.abs(y) > 50) { diverged = true; break; } path.push([x, y]); }
      render(); const [lx, ly] = path[path.length - 1];
      b.querySelector(".labout").innerHTML = diverged ? `<p class="labrule no"><b>Diverged!</b> The learning rate ${lr.toFixed(3)} is too large: each step overshoots and the loss explodes.</p>`
        : `<p>After ${path.length - 1} steps: position (${lx.toFixed(2)}, ${ly.toFixed(2)}), loss ${f(lx, ly).toFixed(4)}. ${opt === "Gradient descent" && b.querySelector("[data-f]").value === "valley" ? "Notice the zig-zag across the narrow valley — momentum and Adam fix this." : ""}</p>`;
    };
    const lrv = () => b.querySelector("[data-lrv]").textContent = (10 ** +b.querySelector("[data-lr]").value).toFixed(3);
    ctx.canvas.onclick = e => { const [px, py] = cvPos(ctx, e); start = [toV(px), toV(py)]; run(); };
    b.querySelector("[data-run]").onclick = run; b.querySelector("[data-lr]").oninput = () => { lrv(); run(); };
    b.querySelector("[data-f]").onchange = run; b.querySelector("[data-o]").onchange = run; lrv(); run();
  },

  linreg(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<button type="button" data-rand>Random data</button><button type="button" data-out>Add an outlier</button><button type="button" data-clear>Clear</button><label class="sdpract"><input type="checkbox" data-res checked> Show residuals</label>`) + `<p class="labnote">Click to add points. The line minimises the sum of squared residuals.</p>` + outBox();
    const ctx = mkCanvas(b, 520, 300, "Scatter plot with least-squares line"); let pts = []; const r = rng(3);
    const rand = () => { pts = []; for (let i = 0; i < 25; i++) { const x = r(); pts.push([x, 0.2 + 0.6 * x + gauss(r) * 0.07]); } };
    const render = () => {
      clear(ctx); const n = pts.length;
      pts.forEach(([x, y]) => dot(ctx, x * 520, (1 - y) * 300, 4.5, cssv("--lab0")));
      if (n < 2) { b.querySelector(".labout").innerHTML = "<p>Add at least two points.</p>"; return; }
      const mx = pts.reduce((a, p) => a + p[0], 0) / n, my = pts.reduce((a, p) => a + p[1], 0) / n;
      const sxy = pts.reduce((a, p) => a + (p[0] - mx) * (p[1] - my), 0), sxx = pts.reduce((a, p) => a + (p[0] - mx) ** 2, 0);
      const w = sxx ? sxy / sxx : 0, c = my - w * mx, pred = x => w * x + c;
      if (b.querySelector("[data-res]").checked) { ctx.strokeStyle = cssv("--muted"); ctx.lineWidth = 1; pts.forEach(([x, y]) => { ctx.beginPath(); ctx.moveTo(x * 520, (1 - y) * 300); ctx.lineTo(x * 520, (1 - pred(x)) * 300); ctx.stroke(); }); }
      ctx.strokeStyle = cssv("--lab1"); ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(0, (1 - pred(0)) * 300); ctx.lineTo(520, (1 - pred(1)) * 300); ctx.stroke();
      const sse = pts.reduce((a, p) => a + (p[1] - pred(p[0])) ** 2, 0), sst = pts.reduce((a, p) => a + (p[1] - my) ** 2, 0);
      b.querySelector(".labout").innerHTML = `<p><b>ŷ = ${w.toFixed(3)}·x ${c >= 0 ? "+" : "−"} ${Math.abs(c).toFixed(3)}</b> · MSE ${(sse / n).toFixed(4)} · R² ${sst ? (1 - sse / sst).toFixed(3) : "—"} · ${n} points. Add an outlier and watch the squared loss drag the line toward it.</p>`;
    };
    ctx.canvas.onclick = e => { const [x, y] = cvPos(ctx, e); pts.push([x / 520, 1 - y / 300]); render(); };
    b.querySelector("[data-rand]").onclick = () => { rand(); render(); }; b.querySelector("[data-clear]").onclick = () => { pts = []; render(); };
    b.querySelector("[data-out]").onclick = () => { pts.push([0.9, 0.05]); render(); }; b.querySelector("[data-res]").onchange = render; rand(); render();
  },

  knn(el){
    const b = el.querySelector(".labbody"), rn = "knnc" + Math.random().toString(36).slice(2, 7);
    b.innerHTML = ctl(`<label>Data <select data-d><option value="moons">Two moons</option><option value="blobs">Blobs</option><option value="circles">Circles</option><option value="xor">XOR</option></select></label><label>k <input type="range" min="1" max="51" step="2" value="1" data-k><span data-kv>1</span></label>`) + `<p class="labnote">Click to add a point of the class chosen below. Shaded regions show what kNN would predict.</p>` + ctl(`<label class="sdpract"><input type="radio" name="${rn}" value="0" checked> class A</label><label class="sdpract"><input type="radio" name="${rn}" value="1"> class B</label>`) + outBox();
    const ctx = mkCanvas(b, 360, 360, "kNN decision regions"); let pts = twoClass(11, "moons");
    const predict = (x, y, k, skip = -1) => { const d = []; pts.forEach((p, i) => { if (i !== skip) d.push([(p[0] - x) ** 2 + (p[1] - y) ** 2, p[2]]); }); d.sort((a, c) => a[0] - c[0]);
      let v = 0; for (let i = 0; i < Math.min(k, d.length); i++) v += d[i][1]; return v * 2 > Math.min(k, d.length) ? 1 : 0; };
    const render = () => {
      clear(ctx); const k = +b.querySelector("[data-k]").value, P = PAL(), G = 60;
      for (let i = 0; i < G; i++) for (let j = 0; j < G; j++) { ctx.fillStyle = P[predict((i + 0.5) / G, (j + 0.5) / G, k)]; ctx.globalAlpha = 0.18; ctx.fillRect(i * 6, j * 6, 6, 6); }
      ctx.globalAlpha = 1; pts.forEach(p => dot(ctx, p[0] * 360, p[1] * 360, 4, P[p[2]], cssv("--panel")));
      const tr = pts.filter(p => predict(p[0], p[1], k) === p[2]).length / pts.length, loo = pts.filter((p, i) => predict(p[0], p[1], k, i) === p[2]).length / pts.length;
      b.querySelector(".labout").innerHTML = `<p>k = ${k}: training accuracy ${(tr * 100).toFixed(0)}%, leave-one-out (validation) accuracy <b>${(loo * 100).toFixed(0)}%</b>. ${k === 1 ? "k = 1 memorises every point (100% training accuracy) — a jagged, overfit boundary." : k > 25 ? "Large k smooths too much and starts to underfit." : ""}</p>`;
    };
    ctx.canvas.onclick = e => { const [x, y] = cvPos(ctx, e); pts.push([x / 360, y / 360, +b.querySelector(`input[name="${rn}"]:checked`).value]); render(); };
    b.querySelector("[data-k]").oninput = e => { b.querySelector("[data-kv]").textContent = e.target.value; render(); };
    b.querySelector("[data-d]").onchange = e => { pts = twoClass(11, e.target.value); render(); }; render();
  },

  tree(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Threshold <input type="range" min="0" max="100" value="30" data-t><span data-tv></span></label><button type="button" data-best>Find best split</button><button type="button" data-new>New data</button>`) + outBox();
    const ctx = mkCanvas(b, 520, 170, "Points on a line split by a threshold"); let pts;
    const gen = s => { const r = rng(s); pts = Array.from({length: 24}, () => { const x = r(); return [x, r() < (x > 0.55 ? 0.85 : 0.15) ? 1 : 0]; }); };
    const gini = arr => { if (!arr.length) return 0; const p = arr.filter(c => c).length / arr.length; return 1 - p * p - (1 - p) * (1 - p); };
    const stats = t => { const L = pts.filter(p => p[0] <= t).map(p => p[1]), R = pts.filter(p => p[0] > t).map(p => p[1]), n = pts.length;
      const w = (L.length * gini(L) + R.length * gini(R)) / n; return {L, R, gL: gini(L), gR: gini(R), w, gain: gini(pts.map(p => p[1])) - w}; };
    const render = () => {
      const t = +b.querySelector("[data-t]").value / 100, s = stats(t), P = PAL(); b.querySelector("[data-tv]").textContent = t.toFixed(2); clear(ctx);
      ctx.strokeStyle = cssv("--line"); ctx.beginPath(); ctx.moveTo(10, 80); ctx.lineTo(510, 80); ctx.stroke();
      pts.forEach(p => dot(ctx, 10 + p[0] * 500, p[1] ? 66 : 94, 7, P[p[1] ? 1 : 0], cssv("--panel")));
      ctx.strokeStyle = cssv("--ink"); ctx.setLineDash([5, 4]); ctx.beginPath(); ctx.moveTo(10 + t * 500, 20); ctx.lineTo(10 + t * 500, 140); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = cssv("--muted"); ctx.font = "12px " + cssv("--sans"); ctx.fillText(`left: ${s.L.length} pts, Gini ${s.gL.toFixed(3)}`, 14, 160); ctx.textAlign = "right"; ctx.fillText(`right: ${s.R.length} pts, Gini ${s.gR.toFixed(3)}`, 506, 160); ctx.textAlign = "left";
      b.querySelector(".labout").innerHTML = `<p>Parent Gini ${gini(pts.map(p => p[1])).toFixed(3)} → weighted children ${s.w.toFixed(3)} · <b>information gain (Gini decrease) ${s.gain.toFixed(3)}</b>. A tree tries every threshold of every feature and keeps the one with the biggest decrease.</p>`;
    };
    b.querySelector("[data-t]").oninput = render;
    b.querySelector("[data-best]").onclick = () => { let best = 0, bt = 0; for (let i = 0; i <= 100; i++) { const g = stats(i / 100).gain; if (g > best) { best = g; bt = i; } } b.querySelector("[data-t]").value = bt; render(); };
    let seed = 5; b.querySelector("[data-new]").onclick = () => { gen(++seed); render(); }; gen(seed); render();
  },

  kmeans(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>k <input type="range" min="1" max="7" value="3" data-k><span data-kv>3</span></label><button type="button" data-step>Step</button><button type="button" data-run>Run to convergence</button><button type="button" data-reset>New data + reset</button>`) + outBox();
    const ctx = mkCanvas(b, 360, 360, "k-means clustering"); let pts, cents, lab, phase, it, seed = 2;
    const reset = () => { const r = rng(seed++); pts = []; const C = [[0.25, 0.3], [0.7, 0.25], [0.5, 0.72], [0.2, 0.75]]; for (let i = 0; i < 160; i++) { const c = C[i % 4]; pts.push([c[0] + gauss(r) * 0.07, c[1] + gauss(r) * 0.07]); }
      const k = +b.querySelector("[data-k]").value; cents = Array.from({length: k}, () => [0.1 + r() * 0.8, 0.1 + r() * 0.8]); lab = pts.map(() => -1); phase = "assign"; it = 0; render("Random centroids placed. Press Step."); };
    const inertia = () => pts.reduce((a, p, i) => a + (lab[i] < 0 ? 0 : (p[0] - cents[lab[i]][0]) ** 2 + (p[1] - cents[lab[i]][1]) ** 2), 0);
    const step = () => { let moved = 0;
      if (phase === "assign") { lab = pts.map(p => { let bi = 0, bd = 1e9; cents.forEach((c, j) => { const d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2; if (d < bd) { bd = d; bi = j; } }); return bi; }); phase = "update"; render("Assigned every point to its nearest centroid."); return 1; }
      cents = cents.map((c, j) => { const m = pts.filter((p, i) => lab[i] === j); if (!m.length) return c; const n = [m.reduce((a, p) => a + p[0], 0) / m.length, m.reduce((a, p) => a + p[1], 0) / m.length]; moved += Math.hypot(n[0] - c[0], n[1] - c[1]); return n; });
      phase = "assign"; it++; render(moved < 1e-4 ? `Converged after ${it} iterations.` : "Moved each centroid to the mean of its points."); return moved; };
    const render = msg => { clear(ctx); const P = PAL();
      pts.forEach((p, i) => dot(ctx, p[0] * 360, p[1] * 360, 3.5, lab[i] < 0 ? cssv("--muted") : P[lab[i] % 6]));
      cents.forEach((c, j) => { ctx.fillStyle = P[j % 6]; ctx.strokeStyle = cssv("--ink"); ctx.lineWidth = 2; ctx.beginPath(); ctx.rect(c[0] * 360 - 7, c[1] * 360 - 7, 14, 14); ctx.fill(); ctx.stroke(); });
      b.querySelector(".labout").innerHTML = `<p>${msg || ""} Iteration ${it} · inertia (within-cluster squared distance) ${inertia().toFixed(3)}. Data has 4 real groups — try k = 2…6.</p>`; };
    b.querySelector("[data-step]").onclick = step;
    b.querySelector("[data-run]").onclick = () => { let g = 0; while (g++ < 60) { step(); if (phase === "assign" && step() < 1e-4) break; } };
    b.querySelector("[data-reset]").onclick = reset; b.querySelector("[data-k]").oninput = e => { b.querySelector("[data-kv]").textContent = e.target.value; reset(); }; reset();
  },

  overfit(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Polynomial degree <input type="range" min="0" max="15" value="1" data-d><span data-dv>1</span></label><button type="button" data-new>New sample</button>`) + outBox();
    const ctx = mkCanvas(b, 520, 260, "Polynomial fit to noisy data"); const ectx = mkCanvas(b, 520, 140, "Training and validation error by degree"); let tr, va, seed = 4;
    const truth = x => Math.sin(2 * Math.PI * x);
    const gen = () => { const r = rng(seed++); tr = Array.from({length: 14}, () => { const x = r(); return [x, truth(x) + gauss(r) * 0.25]; }); va = Array.from({length: 60}, () => { const x = r(); return [x, truth(x) + gauss(r) * 0.25]; }); };
    const fit = d => { const n = d + 1, A = Array.from({length: n}, () => Array(n + 1).fill(0));
      tr.forEach(([x, y]) => { const z = 2 * x - 1, pw = Array.from({length: n}, (_, i) => z ** i); for (let i = 0; i < n; i++) { for (let j = 0; j < n; j++) A[i][j] += pw[i] * pw[j]; A[i][n] += pw[i] * y; } });
      for (let i = 0; i < n; i++) A[i][i] += 1e-9;
      for (let i = 0; i < n; i++) { let p = i; for (let k = i + 1; k < n; k++) if (Math.abs(A[k][i]) > Math.abs(A[p][i])) p = k; [A[i], A[p]] = [A[p], A[i]];
        for (let k = 0; k < n; k++) if (k !== i) { const f = A[k][i] / A[i][i]; for (let j = i; j <= n; j++) A[k][j] -= f * A[i][j]; } }
      const w = A.map((row, i) => row[n] / row[i]); return x => w.reduce((a, c, i) => a + c * (2 * x - 1) ** i, 0); };
    const mse = (f, D) => D.reduce((a, [x, y]) => a + (f(x) - y) ** 2, 0) / D.length;
    const render = () => {
      const d = +b.querySelector("[data-d]").value, f = fit(d), P = PAL(); b.querySelector("[data-dv]").textContent = d; clear(ctx);
      const Y = y => 130 - y * 80;
      ctx.strokeStyle = cssv("--muted"); ctx.setLineDash([4, 4]); ctx.beginPath(); for (let i = 0; i <= 200; i++) { const x = i / 200; i ? ctx.lineTo(x * 520, Y(truth(x))) : ctx.moveTo(0, Y(truth(x))); } ctx.stroke(); ctx.setLineDash([]);
      va.forEach(([x, y]) => dot(ctx, x * 520, Y(y), 2.5, P[2])); tr.forEach(([x, y]) => dot(ctx, x * 520, Y(y), 5, P[0], cssv("--panel")));
      ctx.strokeStyle = P[1]; ctx.lineWidth = 2.5; ctx.beginPath(); for (let i = 0; i <= 260; i++) { const x = i / 260, y = Math.max(-2, Math.min(2, f(x))); i ? ctx.lineTo(x * 520, Y(y)) : ctx.moveTo(0, Y(y)); } ctx.stroke();
      const errs = Array.from({length: 16}, (_, k) => { const g = fit(k); return [mse(g, tr), mse(g, va)]; }); clear(ectx);
      const mx = Math.min(1.5, Math.max(...errs.flat())); const X = k => 30 + k / 15 * 470, EY = v => 120 - Math.min(v, mx) / mx * 105;
      [[0, P[0], "training"], [1, P[2], "validation"]].forEach(([j, c, name], q) => { ectx.strokeStyle = c; ectx.lineWidth = 2; ectx.beginPath(); errs.forEach((e, k) => k ? ectx.lineTo(X(k), EY(e[j])) : ectx.moveTo(X(k), EY(e[j]))); ectx.stroke(); ectx.fillStyle = c; ectx.font = "11px " + cssv("--sans"); ectx.fillText(name + " error", 380, 18 + q * 14); });
      ectx.strokeStyle = cssv("--ink"); ectx.setLineDash([3, 3]); ectx.beginPath(); ectx.moveTo(X(d), 10); ectx.lineTo(X(d), 125); ectx.stroke(); ectx.setLineDash([]);
      ectx.fillStyle = cssv("--muted"); ectx.font = "10px " + cssv("--mono"); [0, 5, 10, 15].forEach(k => ectx.fillText(k, X(k) - 3, 137));
      const [te, ve] = errs[d]; const best = errs.reduce((bi, e, k) => e[1] < errs[bi][1] ? k : bi, 0);
      b.querySelector(".labout").innerHTML = `<p>Degree ${d}: training MSE <b>${te.toFixed(3)}</b>, validation MSE <b>${ve.toFixed(3)}</b> → ${d <= 1 ? "underfitting (high bias)" : ve > 2 * Math.max(te, 0.05) && d > best ? "overfitting (high variance): it chases the 14 training points" : "a good fit"}. Best validation degree here: ${best}. Blue = training points, green = validation, dashed = true curve.</p>`;
    };
    b.querySelector("[data-d]").oninput = render; b.querySelector("[data-new]").onclick = () => { gen(); render(); }; gen(); render();
  },

  roc(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Class separation <input type="range" min="0" max="30" value="15" data-s></label><label>Decision threshold <input type="range" min="0" max="100" value="50" data-t><span data-tv></span></label><label>Positives % <input type="range" min="2" max="50" value="30" data-p><span data-pv></span></label>`) + `<div class="mlroc"></div>` + outBox();
    const host = b.querySelector(".mlroc"), dctx = mkCanvas(host, 330, 200, "Score distributions"), rctx = mkCanvas(host, 200, 200, "ROC curve");
    const render = () => {
      const sep = +b.querySelector("[data-s]").value / 10, t = +b.querySelector("[data-t]").value / 100 * 6 - 3, pr = +b.querySelector("[data-p]").value / 100, P = PAL();
      b.querySelector("[data-tv]").textContent = t.toFixed(2); b.querySelector("[data-pv]").textContent = Math.round(pr * 100) + "%";
      const pdf = (x, m) => Math.exp(-((x - m) ** 2) / 2) / Math.sqrt(2 * Math.PI), cdf = x => 0.5 * (1 + Math.tanh(0.7978845608 * (x + 0.044715 * x ** 3)));
      const mN = -sep / 2, mP = sep / 2; clear(dctx);
      [[mN, P[0], 1 - pr], [mP, P[1], pr]].forEach(([m, c, w]) => { dctx.fillStyle = c; dctx.globalAlpha = 0.35; dctx.beginPath(); dctx.moveTo(0, 185);
        for (let i = 0; i <= 330; i++) { const x = i / 330 * 8 - 4; dctx.lineTo(i, 185 - pdf(x, m) * w * 380); } dctx.lineTo(330, 185); dctx.fill(); dctx.globalAlpha = 1; });
      const tx = (t + 4) / 8 * 330; dctx.strokeStyle = cssv("--ink"); dctx.setLineDash([5, 4]); dctx.beginPath(); dctx.moveTo(tx, 10); dctx.lineTo(tx, 190); dctx.stroke(); dctx.setLineDash([]);
      dctx.fillStyle = cssv("--muted"); dctx.font = "11px " + cssv("--sans"); dctx.fillText("negatives", 8, 14); dctx.fillText("positives", 260, 14);
      const tpr = 1 - cdf(t - mP), fpr = 1 - cdf(t - mN), N = 1000, TP = tpr * pr * N, FP = fpr * (1 - pr) * N, FN = pr * N - TP, TN = (1 - pr) * N - FP;
      const prec = TP / (TP + FP || 1), f1 = 2 * prec * tpr / (prec + tpr || 1);
      clear(rctx); rctx.strokeStyle = cssv("--line"); rctx.strokeRect(10, 10, 180, 180); rctx.beginPath(); rctx.moveTo(10, 190); rctx.lineTo(190, 10); rctx.setLineDash([3, 3]); rctx.stroke(); rctx.setLineDash([]);
      rctx.strokeStyle = P[1]; rctx.lineWidth = 2.5; rctx.beginPath(); let auc = 0, px = 0, py = 0;
      for (let i = 0; i <= 120; i++) { const th = 4 - i / 120 * 8, x = 1 - cdf(th - mN), y = 1 - cdf(th - mP); auc += (x - px) * (y + py) / 2; px = x; py = y; i ? rctx.lineTo(10 + x * 180, 190 - y * 180) : rctx.moveTo(10 + x * 180, 190 - y * 180); }
      rctx.stroke(); dot(rctx, 10 + fpr * 180, 190 - tpr * 180, 6, cssv("--ink"));
      b.querySelector(".labout").innerHTML = `<div class="tscroll"><table class="sdt mlcm"><tr><th></th><th>Predicted +</th><th>Predicted −</th></tr><tr><th>Actual +</th><td>TP ${TP.toFixed(0)}</td><td>FN ${FN.toFixed(0)}</td></tr><tr><th>Actual −</th><td>FP ${FP.toFixed(0)}</td><td>TN ${TN.toFixed(0)}</td></tr></table></div>
        <p>Per 1,000 cases: precision <b>${(prec * 100).toFixed(1)}%</b> · recall (TPR) <b>${(tpr * 100).toFixed(1)}%</b> · FPR ${(fpr * 100).toFixed(1)}% · F1 ${f1.toFixed(3)} · accuracy ${((TP + TN) / N * 100).toFixed(1)}% · ROC-AUC ${auc.toFixed(3)} (threshold-free). Lower the threshold → recall up, precision down. Shrink the positive % → precision falls even though ROC doesn't change.</p>`;
    };
    ["[data-s]", "[data-t]", "[data-p]"].forEach(q => b.querySelector(q).oninput = render); render();
  },

  perceptron(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Problem <select data-d><option>AND</option><option>OR</option><option>XOR</option></select></label><button type="button" data-step>One update</button><button type="button" data-epoch>One epoch</button><button type="button" data-reset>Reset</button>`) + outBox();
    const ctx = mkCanvas(b, 300, 300, "Perceptron decision line"); const X = [[0, 0], [0, 1], [1, 0], [1, 1]]; let w, bias, i, epoch, errs, log;
    const Y = () => ({AND: [-1, -1, -1, 1], OR: [-1, 1, 1, 1], XOR: [-1, 1, 1, -1]})[b.querySelector("[data-d]").value];
    const reset = () => { w = [0, 0]; bias = 0; i = 0; epoch = 0; errs = 0; log = []; render(); };
    const one = () => { const y = Y()[i], x = X[i], out = w[0] * x[0] + w[1] * x[1] + bias > 0 ? 1 : -1;
      if (out !== y) { w = [w[0] + 0.5 * y * x[0], w[1] + 0.5 * y * x[1]]; bias += 0.5 * y; errs++; log.unshift(`point (${x}) was wrong → w = [${w}], b = ${bias}`); } else log.unshift(`point (${x}) correct`);
      i = (i + 1) % 4; if (!i) { epoch++; log.unshift(`— epoch ${epoch} done with ${errs} mistakes${errs ? "" : ": converged!"}`); errs = 0; } };
    const render = () => { clear(ctx); const P = PAL(), S = v => 40 + v * 220;
      if (w[1] !== 0 || w[0] !== 0) { ctx.strokeStyle = cssv("--ink"); ctx.lineWidth = 2; ctx.beginPath();
        if (Math.abs(w[1]) > 1e-9) { const yAt = x => -(w[0] * x + bias) / w[1]; ctx.moveTo(S(-0.2), 300 - S(yAt(-0.2))); ctx.lineTo(S(1.2), 300 - S(yAt(1.2))); } else { const x0 = -bias / w[0]; ctx.moveTo(S(x0), 0); ctx.lineTo(S(x0), 300); } ctx.stroke(); }
      X.forEach((x, k) => dot(ctx, S(x[0]), 300 - S(x[1]), 12, P[Y()[k] > 0 ? 1 : 0], k === i ? cssv("--ink") : null));
      b.querySelector(".labout").innerHTML = `<p>w = [${w.join(", ")}], b = ${bias}, epoch ${epoch}. ${b.querySelector("[data-d]").value === "XOR" && epoch > 3 ? "<b>XOR never converges</b>: no single straight line separates it — you need a hidden layer." : "Orange = positive, blue = negative."}</p><ul class="mllog">${log.slice(0, 6).map(l => `<li>${esc(l)}</li>`).join("")}</ul>`; };
    b.querySelector("[data-step]").onclick = () => { one(); render(); }; b.querySelector("[data-epoch]").onclick = () => { for (let k = 0; k < 4; k++) one(); render(); };
    b.querySelector("[data-reset]").onclick = reset; b.querySelector("[data-d]").onchange = reset; reset();
  },

  nn(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Data <select data-d><option value="circles">Circles</option><option value="xor">XOR</option><option value="moons">Moons</option><option value="spiral">Spiral</option></select></label><label>Hidden layers <select data-h><option value="0">none (logistic regression)</option><option value="8" selected>1 × 8</option><option value="16,16">2 × 16</option></select></label><label>Activation <select data-a><option>tanh</option><option>relu</option></select></label><label>Learning rate <select data-lr><option>0.003</option><option selected>0.01</option><option>0.03</option></select></label><button type="button" data-train>▶ Train</button><button type="button" data-reset>Reset weights</button>`) + outBox();
    const ctx = mkCanvas(b, 360, 360, "Neural network decision regions"); let data, net, timer = null, steps = 0;
    const init = () => { const hs = b.querySelector("[data-h]").value === "0" ? [] : b.querySelector("[data-h]").value.split(",").map(Number), sizes = [2, ...hs, 1], r = rng(9);
      net = sizes.slice(1).map((n, l) => ({W: Array.from({length: n}, () => Array.from({length: sizes[l]}, () => gauss(r) * Math.sqrt(2 / (sizes[l] + n)))), b: Array(n).fill(0), mW: null, vW: null}));
      net.forEach(L => { L.mW = L.W.map(r => r.map(() => 0)); L.vW = L.W.map(r => r.map(() => 0)); L.mb = L.b.map(() => 0); L.vb = L.b.map(() => 0); }); steps = 0; };
    const act = () => b.querySelector("[data-a]").value;
    const f = z => act() === "relu" ? Math.max(0, z) : Math.tanh(z), df = (z, a) => act() === "relu" ? (z > 0 ? 1 : 0) : 1 - a * a;
    const forward = x => { const zs = [], as = [x]; let a = x; net.forEach((L, l) => { const z = L.W.map((row, i) => row.reduce((s, w, j) => s + w * a[j], L.b[i])); zs.push(z);
      a = l === net.length - 1 ? z.map(v => 1 / (1 + Math.exp(-v))) : z.map(f); as.push(a); }); return {zs, as}; };
    const trainStep = () => { const lr = +b.querySelector("[data-lr]").value, gW = net.map(L => L.W.map(r => r.map(() => 0))), gb = net.map(L => L.b.map(() => 0)), r = rng(steps + 1); let loss = 0;
      for (let s = 0; s < 32; s++) { const [x0, y0, c] = data[Math.floor(r() * data.length)], x = [(x0 - 0.5) * 4, (y0 - 0.5) * 4], {zs, as} = forward(x), p = as[as.length - 1][0];
        loss += -(c * Math.log(p + 1e-9) + (1 - c) * Math.log(1 - p + 1e-9)); let delta = [p - c];
        for (let l = net.length - 1; l >= 0; l--) { const a = as[l]; delta.forEach((d, i) => { gb[l][i] += d; a.forEach((av, j) => gW[l][i][j] += d * av); });
          if (l) delta = a.map((av, j) => delta.reduce((s2, d, i) => s2 + d * net[l].W[i][j], 0) * df(zs[l - 1][j], av)); } }
      steps++; const t = steps;
      net.forEach((L, l) => { L.W.forEach((row, i) => row.forEach((w, j) => { const g = gW[l][i][j] / 32; L.mW[i][j] = 0.9 * L.mW[i][j] + 0.1 * g; L.vW[i][j] = 0.999 * L.vW[i][j] + 0.001 * g * g;
        row[j] -= lr * (L.mW[i][j] / (1 - 0.9 ** t)) / (Math.sqrt(L.vW[i][j] / (1 - 0.999 ** t)) + 1e-8); }));
        L.b.forEach((bv, i) => { const g = gb[l][i] / 32; L.mb[i] = 0.9 * L.mb[i] + 0.1 * g; L.vb[i] = 0.999 * L.vb[i] + 0.001 * g * g; L.b[i] -= lr * (L.mb[i] / (1 - 0.9 ** t)) / (Math.sqrt(L.vb[i] / (1 - 0.999 ** t)) + 1e-8); }); });
      return loss / 32; };
    const render = loss => { clear(ctx); const P = PAL(), G = 45, s = 360 / G;
      for (let i = 0; i < G; i++) for (let j = 0; j < G; j++) { const p = forward([((i + 0.5) / G - 0.5) * 4, ((j + 0.5) / G - 0.5) * 4]).as.slice(-1)[0][0];
        ctx.fillStyle = p > 0.5 ? P[1] : P[0]; ctx.globalAlpha = 0.08 + Math.abs(p - 0.5) * 0.45; ctx.fillRect(Math.floor(i * s), Math.floor(j * s), Math.ceil(s) + 1, Math.ceil(s) + 1); }
      ctx.globalAlpha = 1; data.forEach(p => dot(ctx, p[0] * 360, p[1] * 360, 3.5, P[p[2] ? 1 : 0], cssv("--panel")));
      const acc = data.filter(p => (forward([(p[0] - 0.5) * 4, (p[1] - 0.5) * 4]).as.slice(-1)[0][0] > 0.5 ? 1 : 0) === p[2]).length / data.length;
      b.querySelector(".labout").innerHTML = `<p>${steps} training steps (Adam, batch 32) · ${loss !== undefined ? "loss " + loss.toFixed(3) + " · " : ""}accuracy <b>${(acc * 100).toFixed(0)}%</b>. ${b.querySelector("[data-h]").value === "0" ? "With no hidden layer the boundary must be a straight line — add a hidden layer." : ""}</p>`; };
    const stop = () => { clearInterval(timer); timer = null; b.querySelector("[data-train]").textContent = "▶ Train"; };
    b.querySelector("[data-train]").onclick = () => { if (timer) { stop(); return; } b.querySelector("[data-train]").textContent = "❚❚ Pause";
      timer = setInterval(() => { if (!el.isConnected) { stop(); return; } let L = 0; for (let k = 0; k < 25; k++) L = trainStep(); render(L); if (steps > 4000) stop(); }, 60); };
    const restart = () => { stop(); data = twoClass(5, b.querySelector("[data-d]").value, 200); init(); render(); };
    b.querySelector("[data-reset]").onclick = restart; ["[data-d]", "[data-h]", "[data-a]"].forEach(q => b.querySelector(q).onchange = restart); restart();
  },

  pca(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = ctl(`<label>Correlation <input type="range" min="-95" max="95" value="80" data-c><span data-cv></span></label><label class="sdpract"><input type="checkbox" data-proj> Project onto PC1</label><button type="button" data-new>New sample</button>`) + outBox();
    const ctx = mkCanvas(b, 360, 360, "PCA of a 2-D point cloud"); let base, seed = 1;
    const gen = () => { const r = rng(seed++); base = Array.from({length: 200}, () => [gauss(r), gauss(r)]); };
    const render = () => { const rho = +b.querySelector("[data-c]").value / 100; b.querySelector("[data-cv]").textContent = rho.toFixed(2);
      const pts = base.map(([u, v]) => [u, rho * u + Math.sqrt(1 - rho * rho) * v]).map(([x, y]) => [x * 0.9, y * 0.6]);
      const n = pts.length, mx = pts.reduce((a, p) => a + p[0], 0) / n, my = pts.reduce((a, p) => a + p[1], 0) / n;
      let sxx = 0, syy = 0, sxy = 0; pts.forEach(([x, y]) => { sxx += (x - mx) ** 2; syy += (y - my) ** 2; sxy += (x - mx) * (y - my); }); sxx /= n - 1; syy /= n - 1; sxy /= n - 1;
      const tr = sxx + syy, det = sxx * syy - sxy * sxy, l1 = tr / 2 + Math.sqrt(tr * tr / 4 - det), l2 = tr / 2 - Math.sqrt(Math.max(0, tr * tr / 4 - det));
      let v1 = Math.abs(sxy) > 1e-12 ? [l1 - syy, sxy] : sxx >= syy ? [1, 0] : [0, 1]; const nv = Math.hypot(...v1); v1 = [v1[0] / nv, v1[1] / nv]; const v2 = [-v1[1], v1[0]];
      const S = 60, X = x => 180 + x * S, Y = y => 180 - y * S, P = PAL(), proj = b.querySelector("[data-proj]").checked; clear(ctx);
      pts.forEach(([x, y]) => { if (proj) { const t = (x - mx) * v1[0] + (y - my) * v1[1], px = mx + t * v1[0], py = my + t * v1[1];
        ctx.strokeStyle = cssv("--line"); ctx.beginPath(); ctx.moveTo(X(x), Y(y)); ctx.lineTo(X(px), Y(py)); ctx.stroke(); dot(ctx, X(px), Y(py), 2.8, P[1]); } else dot(ctx, X(x), Y(y), 3, P[0]); });
      [[v1, l1, P[1], "PC1"], [v2, l2, P[2], "PC2"]].forEach(([v, l, c, name]) => { const L = Math.sqrt(l) * 2; ctx.strokeStyle = c; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(X(mx - v[0] * L), Y(my - v[1] * L)); ctx.lineTo(X(mx + v[0] * L), Y(my + v[1] * L)); ctx.stroke();
        ctx.fillStyle = c; ctx.font = "bold 12px " + cssv("--sans"); ctx.fillText(name, X(mx + v[0] * L) + 4, Y(my + v[1] * L)); });
      b.querySelector(".labout").innerHTML = `<p>PC1 explains <b>${(l1 / (l1 + l2) * 100).toFixed(1)}%</b> of the variance, PC2 ${(l2 / (l1 + l2) * 100).toFixed(1)}%. ${proj ? "Projecting onto PC1 keeps each point's position along the main direction and drops the rest — 2 numbers become 1." : "Tick 'Project onto PC1' to see dimensionality reduction."} Higher |correlation| → PC1 captures more.</p>`; };
    b.querySelector("[data-c]").oninput = render; b.querySelector("[data-proj]").onchange = render; b.querySelector("[data-new]").onclick = () => { gen(); render(); }; gen(); render();
  },

  conv(el){
    const b = el.querySelector(".labbody");
    const K = {"Identity": [0, 0, 0, 0, 1, 0, 0, 0, 0], "Vertical edges (Sobel x)": [-1, 0, 1, -2, 0, 2, -1, 0, 1], "Horizontal edges (Sobel y)": [-1, -2, -1, 0, 0, 0, 1, 2, 1],
      "All edges (Laplacian)": [0, 1, 0, 1, -4, 1, 0, 1, 0], "Blur (box)": [1, 1, 1, 1, 1, 1, 1, 1, 1].map(v => v / 9), "Sharpen": [0, -1, 0, -1, 5, -1, 0, -1, 0], "Emboss": [-2, -1, 0, -1, 1, 1, 0, 1, 2]};
    b.innerHTML = ctl(`<label>Filter <select data-k>${Object.keys(K).map(k => `<option>${k}</option>`).join("")}</select></label><label class="sdpract"><input type="checkbox" data-relu> Apply ReLU</label>`) + `<div class="mlconv"><div><b>Input image</b></div><div class="mlkern"></div><div><b>Feature map</b></div></div>` + outBox();
    const cols = b.querySelectorAll(".mlconv > div"), N = 96, ia = mkCanvas(cols[0], 192, 192, "Input image"), oa = mkCanvas(cols[2], 192, 192, "Feature map");
    const img = new Float32Array(N * N); for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) { let v = 0.15;
      if (x > 12 && x < 44 && y > 12 && y < 44) v = 0.85; if ((x - 66) ** 2 + (y - 30) ** 2 < 300) v = 0.6; if (y > 60 && y < 84 && x > 10 + (y - 60) && x < 86 - (y - 60) * 0.2) v = 0.95; if (y > 52 && y < 56) v = 0.4; img[y * N + x] = v; }
    const paint = (ctx, arr, signed) => { const off = document.createElement("canvas"); off.width = off.height = N; const o = off.getContext("2d"), d = o.createImageData(N, N);
      let mx = 1e-9; arr.forEach(v => mx = Math.max(mx, Math.abs(v)));
      arr.forEach((v, i) => { const t = signed ? 0.5 + v / mx / 2 : Math.max(0, Math.min(1, v / (signed === false ? mx : 1))); const g = Math.round(t * 255); d.data.set([g, g, g, 255], i * 4); });
      o.putImageData(d, 0, 0); ctx.imageSmoothingEnabled = false; ctx.drawImage(off, 0, 0, 192, 192); };
    const render = () => { const name = b.querySelector("[data-k]").value, k = K[name], relu = b.querySelector("[data-relu]").checked, out = new Float32Array(N * N);
      for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) { let s = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const yy = Math.min(N - 1, Math.max(0, y + dy)), xx = Math.min(N - 1, Math.max(0, x + dx)); s += img[yy * N + xx] * k[(dy + 1) * 3 + dx + 1]; } out[y * N + x] = relu ? Math.max(0, s) : s; }
      paint(ia, img); const signed = !relu && k.some(v => v < 0) && !["Sharpen", "Identity"].includes(name); paint(oa, out, signed ? true : false);
      b.querySelector(".mlkern").innerHTML = `<b>3×3 kernel</b><div class="mlkgrid">${k.map(v => `<span>${+v.toFixed(2)}</span>`).join("")}</div>`;
      b.querySelector(".labout").innerHTML = `<p>Each output pixel = sum of (kernel × the 3×3 patch under it). ${signed ? "Grey = 0, white = positive, black = negative response." : ""} A CNN <b>learns</b> the numbers in kernels like these — early layers end up looking like edge detectors.</p>`; };
    b.querySelector("[data-k]").onchange = render; b.querySelector("[data-relu]").onchange = render; render();
  },

  attention(el){
    const b = el.querySelector(".labbody");
    const toks = ["The", "animal", "didn't", "cross", "the", "street", "because", "it", "was", "too", "tired"];
    const E = {The: [0, 0, 0, 1, 0], animal: [1, 0, 0, 0, .6], "didn't": [0, 0, 1, .3, 0], cross: [0, .5, 1, 0, 0], the: [0, 0, 0, 1, 0], street: [0, 1, 0, 0, 0], because: [0, 0, .3, 1, 0], it: [.9, .2, 0, .2, .5], was: [0, 0, .8, .4, .2], too: [0, 0, 0, .6, .4], tired: [.6, 0, .2, 0, 1]};
    b.innerHTML = ctl(`<label>Sharpness (1/temperature) <input type="range" min="1" max="12" value="5" data-s></label><label class="sdpract"><input type="checkbox" data-mask> Causal mask (GPT-style)</label>`) + `<p class="labnote">Click a word to see where it looks. Rows of the matrix are queries, columns are keys.</p><div class="mlatt"></div>` + outBox();
    let q = 7;
    const render = () => { const s = +b.querySelector("[data-s]").value, mask = b.querySelector("[data-mask]").checked;
      const W = toks.map((a, i) => { const sc = toks.map((c, j) => mask && j > i ? -Infinity : E[a].reduce((t, v, k) => t + v * E[c][k], 0) * s), m = Math.max(...sc), ex = sc.map(v => Math.exp(v - m)), z = ex.reduce((x, y) => x + y, 0); return ex.map(v => v / z); });
      b.querySelector(".mlatt").innerHTML = `<div class="mlattw">${toks.map((t, j) => `<button type="button" data-q="${j}" class="${j === q ? "q" : ""}" style="--w:${(W[q][j]).toFixed(3)}">${esc(t)}<small>${(W[q][j] * 100).toFixed(0)}%</small></button>`).join("")}</div>
        <div class="tscroll"><table class="mlattm"><tr><th></th>${toks.map(t => `<th>${esc(t)}</th>`).join("")}</tr>${W.map((row, i) => `<tr${i === q ? ' class="q"' : ""}><th>${esc(toks[i])}</th>${row.map(v => `<td style="--w:${v.toFixed(3)}" title="${(v * 100).toFixed(1)}%"></td>`).join("")}</tr>`).join("")}</table></div>`;
      b.querySelectorAll("[data-q]").forEach(x => x.onclick = () => { q = +x.dataset.q; render(); });
      const top = W[q].map((v, j) => [v, toks[j]]).sort((a, c) => c[0] - a[0]).slice(0, 3);
      b.querySelector(".labout").innerHTML = `<p>“${esc(toks[q])}” attends most to ${top.map(([v, t]) => `<b>${esc(t)}</b> (${(v * 100).toFixed(0)}%)`).join(", ")}. ${toks[q] === "it" ? "A trained transformer learns that “it” refers to the animal — the toy vectors here encode that." : ""} Weights in each row sum to 100% (softmax).</p>`; };
    b.querySelector("[data-s]").oninput = render; b.querySelector("[data-mask]").onchange = render; render();
  },

  sampling(el){
    const b = el.querySelector(".labbody");
    const cand = [["mat", 3.2], ["sofa", 2.6], ["floor", 2.4], ["bed", 2.0], ["roof", 1.2], ["chair", 1.1], ["windowsill", 0.8], ["keyboard", 0.3], ["moon", -0.8], ["banana", -2.0]];
    b.innerHTML = ctl(`<label>Temperature <input type="range" min="0" max="200" value="100" data-t><span data-tv></span></label><label>Top-k <input type="range" min="1" max="10" value="10" data-k><span data-kv></span></label><label>Top-p <input type="range" min="10" max="100" value="100" data-p><span data-pv></span></label><button type="button" data-s>Sample 12 sentences</button>`) + `<p class="labnote">Prompt: “The cat sat on the …”</p>` + outBox();
    const ctx = mkCanvas(b, 520, 210, "Next-token probabilities"); let samples = [];
    const probs = () => { const T = +b.querySelector("[data-t]").value / 100, k = +b.querySelector("[data-k]").value, p = +b.querySelector("[data-p]").value / 100;
      let pr; if (T < 0.01) pr = cand.map((c, i) => i === 0 ? 1 : 0); else { const z = cand.map(c => c[1] / T), m = Math.max(...z), e = z.map(v => Math.exp(v - m)), s = e.reduce((a, c) => a + c, 0); pr = e.map(v => v / s); }
      const order = pr.map((v, i) => [v, i]).sort((a, c) => c[0] - a[0]); const keep = new Set(); let cum = 0;
      for (const [v, i] of order) { if (keep.size >= k) break; keep.add(i); cum += v; if (cum >= p) break; }
      const kept = pr.map((v, i) => keep.has(i) ? v : 0), s = kept.reduce((a, c) => a + c, 0); return kept.map(v => v / s); };
    const render = () => { const pr = probs(), P = PAL(); ["t", "k", "p"].forEach(x => b.querySelector(`[data-${x}v]`).textContent = x === "t" ? (+b.querySelector("[data-t]").value / 100).toFixed(2) : x === "p" ? (+b.querySelector("[data-p]").value / 100).toFixed(2) : b.querySelector("[data-k]").value);
      clear(ctx); bars(ctx, pr, 10, 10, 500, 170, P[0], cand.map(c => c[0]));
      ctx.fillStyle = cssv("--ink"); ctx.font = "10px " + cssv("--mono"); ctx.textAlign = "center"; pr.forEach((v, i) => v > 0.004 && ctx.fillText((v * 100).toFixed(0) + "%", 10 + (i + 0.5) * 50, 175 - v / Math.max(...pr) * 170)); ctx.textAlign = "left";
      b.querySelector(".labout").innerHTML = `<p>${pr.filter(v => v > 0).length} candidate words allowed. Temperature 0 = greedy (always “mat”); higher = flatter and more random; top-k / top-p cut off the unlikely tail (no “banana”).</p>${samples.length ? `<p class="mlsamples">${samples.map(s => `<span>…on the <b>${esc(s)}</b></span>`).join("")}</p>` : ""}`; };
    b.querySelector("[data-s]").onclick = () => { const pr = probs(); samples = Array.from({length: 12}, () => { let r = Math.random(), i = 0; while (i < pr.length - 1 && (r -= pr[i]) > 0) i++; return cand[i][0]; }); render(); };
    ["[data-t]", "[data-k]", "[data-p]"].forEach(q => b.querySelector(q).oninput = () => { samples = []; render(); }); render();
  },

  embed(el){
    const b = el.querySelector(".labbody");
    const W = {king: [0.8, 0.8], queen: [0.8, 0.2], man: [0.3, 0.8], woman: [0.3, 0.2], prince: [0.62, 0.86], princess: [0.62, 0.14], boy: [0.14, 0.86], girl: [0.14, 0.14],
      apple: [-0.6, 0.55], mango: [-0.7, 0.45], banana: [-0.62, 0.36], car: [-0.3, -0.6], bus: [-0.4, -0.7], train: [-0.22, -0.72], delhi: [0.55, -0.55], india: [0.85, -0.5], paris: [0.4, -0.85], france: [0.7, -0.8]};
    const words = Object.keys(W);
    b.innerHTML = ctl(`<label>Analogy <select data-a>${words.map(w => `<option${w === "king" ? " selected" : ""}>${w}</option>`).join("")}</select> − <select data-b>${words.map(w => `<option${w === "man" ? " selected" : ""}>${w}</option>`).join("")}</select> + <select data-c>${words.map(w => `<option${w === "woman" ? " selected" : ""}>${w}</option>`).join("")}</select></label>`) + `<p class="labnote">Click a word to list its nearest neighbours. Try india − delhi + paris.</p>` + outBox();
    const ctx = mkCanvas(b, 420, 380, "2-D word embedding space"); let sel = "king";
    const X = v => 210 + v[0] * 210 * 0.95, Y = v => 190 - v[1] * 190 * 0.95;
    const render = () => { const P = PAL(), a = b.querySelector("[data-a]").value, bb = b.querySelector("[data-b]").value, c = b.querySelector("[data-c]").value;
      const t = [W[a][0] - W[bb][0] + W[c][0], W[a][1] - W[bb][1] + W[c][1]], best = words.filter(w => ![a, bb, c].includes(w)).map(w => [Math.hypot(W[w][0] - t[0], W[w][1] - t[1]), w]).sort((x, y) => x[0] - y[0])[0][1];
      clear(ctx); ctx.strokeStyle = cssv("--line"); ctx.beginPath(); ctx.moveTo(0, 190); ctx.lineTo(420, 190); ctx.moveTo(210, 0); ctx.lineTo(210, 380); ctx.stroke();
      const arrow = (p, q, col) => { ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(X(p), Y(p)); ctx.lineTo(X(q), Y(q)); ctx.stroke(); };
      arrow(W[bb], W[a], P[3]); arrow(W[c], t, P[3]); dot(ctx, X(t), Y(t), 7, "transparent", P[1]);
      words.forEach(w => { dot(ctx, X(W[w]), Y(W[w]), w === sel ? 6 : 4, w === best ? P[1] : w === sel ? P[2] : P[0]); ctx.fillStyle = cssv("--ink"); ctx.font = (w === sel || w === best ? "bold " : "") + "12px " + cssv("--sans"); ctx.fillText(w, X(W[w]) + 7, Y(W[w]) + 4); });
      const nn = words.filter(w => w !== sel).map(w => [Math.hypot(W[sel][0] - W[w][0], W[sel][1] - W[w][1]), w]).sort((x, y) => x[0] - y[0]).slice(0, 4);
      b.querySelector(".labout").innerHTML = `<p><b>${a} − ${bb} + ${c} ≈ ${best}</b> (orange ring = the computed point; parallel arrows = the same 'direction' of meaning). Closest to <b>${sel}</b>: ${nn.map(([s, w]) => `${w} (distance ${s.toFixed(2)})`).join(", ")}. Real embeddings have hundreds of dimensions learned from text.</p>`; };
    ctx.canvas.onclick = e => { const [px, py] = cvPos(ctx, e); sel = words.map(w => [Math.hypot(X(W[w]) - px, Y(W[w]) - py), w]).sort((x, y) => x[0] - y[0])[0][1]; render(); };
    ["[data-a]", "[data-b]", "[data-c]"].forEach(q => b.querySelector(q).onchange = render); render();
  },
};
