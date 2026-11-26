/* ---------- System design: detailed explanations with diagrams (UML, state, step-through sequence, ER, estimates) ---------- */
const VX = {W: 760};
const vEsc = s => esc(String(s == null ? "" : s));
function vText(x, y, t, cls = "sdnt", anchor = "middle"){ return `<text class="${cls}" x="${x}" y="${y}" text-anchor="${anchor}">${vEsc(t)}</text>`; }
function vClip(c, dx, dy){                       // point where a ray from the box centre leaves the box
  const hw = c.w / 2, hh = c.h / 2; if (!dx && !dy) return [c.cx, c.cy];
  const t = Math.min(dx ? hw / Math.abs(dx) : Infinity, dy ? hh / Math.abs(dy) : Infinity);
  return [c.cx + dx * t, c.cy + dy * t];
}
function vLabel(x, y, t){ if (!t) return ""; const w = String(t).length * 6.3 + 10; return `<rect class="sdlb" x="${x - w / 2}" y="${y - 9}" width="${w}" height="17" rx="4"/>${vText(x, y + 4, t, "sdlt")}`; }
const vDefs = `<defs>
  <marker id="vxArr" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="sdah"/></marker>
  <marker id="vxOpen" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10" class="vxopen"/></marker>
  <marker id="vxTri" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="13" markerHeight="13" orient="auto-start-reverse"><path d="M0 0 L12 6 L0 12 z" class="vxhollow"/></marker>
  <marker id="vxDia" viewBox="0 0 16 10" refX="1" refY="5" markerWidth="15" markerHeight="10" orient="auto"><path d="M0 5 L8 0 L16 5 L8 10 z" class="sdah"/></marker>
  <marker id="vxDiaO" viewBox="0 0 16 10" refX="1" refY="5" markerWidth="15" markerHeight="10" orient="auto"><path d="M0 5 L8 0 L16 5 L8 10 z" class="vxhollow"/></marker>
</defs>`;

/* UML class diagram. spec: {rows:[[names]], classes:{Name:{k, f:[], m:[]}}, rels:[[from, to, type, label]]}
   type: inh (from extends to) · impl (from implements to) · comp (from owns to, filled diamond at from) · agg · assoc · dep */
function umlSVG(s){
  const boxes = {}, gapX = 34, gapY = 64; let y = 12, W = VX.W;
  const size = n => { const c = s.classes[n] || {}, k = c.k || "class", stereo = {interface: "«interface»", enum: "«enum»", abstract: "«abstract»", record: "«record»"}[k] || "";
    const lines = [...(c.f || []), ...(c.m || [])], wch = Math.max(n.length + 2, stereo.length, ...lines.map(l => l.length));
    return {n, k, stereo, f: c.f || [], m: c.m || [], w: Math.max(118, wch * 6.4 + 18), h: 26 + (stereo ? 13 : 0) + Math.max(1, (c.f || []).length) * 14 + 8 + Math.max(1, (c.m || []).length) * 14 + 6}; };
  const rows = s.rows.map(r => r.map(size));
  rows.forEach(r => { const need = r.reduce((a, b) => a + b.w, 0) + gapX * (r.length + 1); W = Math.max(W, need); });
  rows.forEach(r => { const total = r.reduce((a, b) => a + b.w, 0), gap = (W - total) / (r.length + 1); let x = gap; const hmax = Math.max(...r.map(b => b.h));
    r.forEach(b => { b.cx = x + b.w / 2; b.cy = y + hmax / 2; b.top = b.cy - b.h / 2; boxes[b.n] = b; x += b.w + gap; }); y += hmax + gapY; });
  const H = y - gapY + 14, place = vPlacer(Object.values(boxes).map(b => ({cx: b.cx, cy: b.cy, w: b.w, h: b.h})));
  let edges = "", labels = "";
  (s.rels || []).forEach(([a, b, t, lab]) => {
    const A = boxes[a], B = boxes[b]; if (!A || !B) return;
    if (a === b) { const x = A.cx + A.w / 2, y1 = A.cy - 14, y2 = A.cy + 14;
      edges += `<path class="sde" d="M ${x} ${y1} h 30 v ${y2 - y1} h -26" marker-end="url(#vxOpen)"/>`; if (lab) labels += vLabel(x + 30 + String(lab).length * 3.4 + 6, A.cy, lab); W = Math.max(W, x + 80); return; }
    const dx = B.cx - A.cx, dy = B.cy - A.cy, L = Math.hypot(dx, dy) || 1, [x1, y1] = vClip(A, dx / L, dy / L), [x2, y2] = vClip(B, -dx / L, -dy / L);
    const dash = t === "impl" || t === "dep" ? ' stroke-dasharray="6 4"' : "";
    const end = t === "inh" || t === "impl" ? ' marker-end="url(#vxTri)"' : t === "assoc" || t === "dep" ? ' marker-end="url(#vxOpen)"' : "";
    const start = t === "comp" ? ' marker-start="url(#vxDia)"' : t === "agg" ? ' marker-start="url(#vxDiaO)"' : "";
    edges += `<line class="sde vxrel" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"${dash}${end}${start}/>`;
    if (lab) labels += place((x1 + x2) / 2, (y1 + y2) / 2, lab);
  });
  const box = b => { const x = b.cx - b.w / 2; let yy = b.top, out = `<g class="vxcls ${b.k}"><rect x="${x}" y="${yy}" width="${b.w}" height="${b.h}" rx="4"/>`;
    if (b.stereo) { out += vText(b.cx, yy + 13, b.stereo, "vxst"); yy += 13; }
    out += vText(b.cx, yy + 17, b.n, "vxcn"); yy += 24; out += `<line x1="${x}" x2="${x + b.w}" y1="${yy}" y2="${yy}"/>`;
    (b.f.length ? b.f : [" "]).forEach((f, i) => out += vText(x + 8, yy + 13 + i * 14, f, "vxm", "start")); yy += Math.max(1, b.f.length) * 14 + 6;
    out += `<line x1="${x}" x2="${x + b.w}" y1="${yy}" y2="${yy}"/>`;
    (b.m.length ? b.m : [" "]).forEach((m, i) => out += vText(x + 8, yy + 13 + i * 14, m, "vxm", "start"));
    return out + "</g>"; };
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="UML class diagram">${vDefs}${edges}${Object.values(boxes).map(box).join("")}${labels}</svg>`;
}
const UML_LEGEND = `<span class="vxlg"><svg width="34" height="12"><line x1="2" y1="6" x2="22" y2="6" class="sde"/><path d="M22 1 L32 6 L22 11 z" class="vxhollow"/></svg>extends</span>
  <span class="vxlg"><svg width="34" height="12"><line x1="2" y1="6" x2="22" y2="6" class="sde" stroke-dasharray="4 3"/><path d="M22 1 L32 6 L22 11 z" class="vxhollow"/></svg>implements</span>
  <span class="vxlg"><svg width="34" height="12"><path d="M2 6 L9 2 L16 6 L9 10 z" class="sdah"/><line x1="16" y1="6" x2="32" y2="6" class="sde"/></svg>owns (composition)</span>
  <span class="vxlg"><svg width="34" height="12"><path d="M2 6 L9 2 L16 6 L9 10 z" class="vxhollow"/><line x1="16" y1="6" x2="32" y2="6" class="sde"/></svg>has (aggregation)</span>
  <span class="vxlg"><svg width="34" height="12"><line x1="2" y1="6" x2="30" y2="6" class="sde"/><path d="M24 1 L31 6 L24 11" class="vxopen"/></svg>uses / knows</span>
  <span class="vxlg"><svg width="34" height="12"><line x1="2" y1="6" x2="30" y2="6" class="sde" stroke-dasharray="4 3"/><path d="M24 1 L31 6 L24 11" class="vxopen"/></svg>depends on</span>`;

/* State machine / generic graph. spec: {rows:[[states]], edges:[[from, to, label]]}; "[*]" = start, "[end]" = end */
function vPlacer(obstacles){                      // places edge labels so they don't cover boxes or each other
  const taken = obstacles.map(o => ({x1: o.cx - o.w / 2 - 4, x2: o.cx + o.w / 2 + 4, y1: o.cy - o.h / 2 - 2, y2: o.cy + o.h / 2 + 2}));
  const hits = r => taken.some(t => r.x1 < t.x2 && r.x2 > t.x1 && r.y1 < t.y2 && r.y2 > t.y1);
  return (x, y, t, prefer = 1) => {
    if (!t) return ""; const w = String(t).length * 6.3 + 10;
    const cands = [];
    for (const d of [0, 1, -1, 2, -2, 3, -3, 4, -4, 6, -6, 8, -8, 11, -11]) for (const e of [0, -1, 1, -2, 2]) cands.push([d * 14 * prefer, e * 13]);
    cands.sort((a, b) => Math.hypot(a[0], a[1] * 1.6) - Math.hypot(b[0], b[1] * 1.6));
    for (const [dx, dy] of cands) {
      const r = {x1: x + dx - w / 2, x2: x + dx + w / 2, y1: y + dy - 10, y2: y + dy + 9};
      if (!hits(r)) { taken.push(r); return vLabel(x + dx, y + dy, t); }
    }
    return vLabel(x, y, t);
  };
}
function stateSVG(s){
  const nodes = {}, rowH = 104, top = 22, W = VX.W;
  s.rows.forEach((row, r) => row.forEach((n, j) => {
    const slot = W / row.length, pseudo = n === "[*]" || n === "[end]", lines = pseudo ? [] : wrapText(n, 20);
    nodes[n] = {n, r, pseudo, lines, cx: slot * (j + 0.5), cy: top + r * rowH + 26, w: pseudo ? 22 : Math.max(...lines.map(l => l.length)) * 7.2 + 30, h: pseudo ? 22 : 20 + lines.length * 15};
  }));
  const H = top + s.rows.length * rowH - 14, pairs = new Set((s.edges || []).map(([a, b]) => a + "→" + b)), place = vPlacer(Object.values(nodes));
  let edges = "", labels = "", loops = "";
  const ordered = [...(s.edges || []).filter(e => e[0] === e[1]), ...(s.edges || []).filter(e => e[0] !== e[1])];
  ordered.forEach(([a, b, lab]) => {
    const A = nodes[a], B = nodes[b]; if (!A || !B) return;
    if (a === b) { const x = A.cx + A.w / 2, y1 = A.cy - 8, y2 = A.cy + 8;
      edges += `<path class="sde" d="M ${x} ${y1} C ${x + 34} ${y1 - 22}, ${x + 34} ${y2 + 22}, ${x + 2} ${y2}" marker-end="url(#vxArr)"/>`;
      if (lab) { const w = String(lab).length * 6.3 + 10; loops += place(x + 36 + w / 2, A.cy, lab); } return; }
    const dx = B.cx - A.cx, dy = B.cy - A.cy, L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L;
    const twoWay = pairs.has(b + "→" + a);
    const between = Object.values(nodes).some(o => o !== A && o !== B && Math.abs((o.cx - A.cx) * ny * -1 + (o.cy - A.cy) * nx * -1) < 1e9 &&
      (() => { const t = ((o.cx - A.cx) * dx + (o.cy - A.cy) * dy) / (L * L); if (t <= 0.05 || t >= 0.95) return false;
               const px = A.cx + t * dx, py = A.cy + t * dy; return Math.abs(px - o.cx) < o.w / 2 + 8 && Math.abs(py - o.cy) < o.h / 2 + 8; })());
    let mx = (A.cx + B.cx) / 2, my = (A.cy + B.cy) / 2, curved = false, sx = 0, sy = 0;
    if (between) { const side = A.cx >= W / 2 ? 1 : -1, wmax = Math.max(A.w, B.w) / 2 + 70;
      // route around: control point well to the side so the curve's apex clears the boxes in between
      mx += Math.abs(dy) > Math.abs(dx) ? side * 2 * wmax : 0; my += Math.abs(dy) > Math.abs(dx) ? 0 : -2 * 60; curved = true; }
    else if (twoWay) { sx = nx * 11; sy = ny * 11; }
    const d1x = mx - A.cx, d1y = my - A.cy, l1 = Math.hypot(d1x, d1y) || 1, d2x = mx - B.cx, d2y = my - B.cy, l2 = Math.hypot(d2x, d2y) || 1;
    let [x1, y1] = curved ? vClip(A, d1x / l1, d1y / l1) : vClip(A, dx / L, dy / L), [x2, y2] = curved ? vClip(B, d2x / l2, d2y / l2) : vClip(B, -dx / L, -dy / L);
    x1 += sx; y1 += sy; x2 += sx; y2 += sy;
    edges += curved ? `<path class="sde" d="M ${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}" marker-end="url(#vxArr)"/>` : `<line class="sde" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#vxArr)"/>`;
    const lx = curved ? 0.25 * x1 + 0.5 * mx + 0.25 * x2 : (x1 + x2) / 2, ly = curved ? 0.25 * y1 + 0.5 * my + 0.25 * y2 : (y1 + y2) / 2;
    labels += place(lx, ly, lab, twoWay ? (nx * 11 >= 0 ? 1 : -1) || 1 : 1);
  });
  const shape = n => n.n === "[*]" ? `<circle class="vxstart" cx="${n.cx}" cy="${n.cy}" r="9"/>` : n.n === "[end]" ? `<circle class="vxend" cx="${n.cx}" cy="${n.cy}" r="11"/><circle class="vxstart" cx="${n.cx}" cy="${n.cy}" r="6"/>`
    : `<g class="vxstate"><rect x="${n.cx - n.w / 2}" y="${n.cy - n.h / 2}" width="${n.w}" height="${n.h}" rx="${Math.min(16, n.h / 2)}"/>${n.lines.map((l, i) => vText(n.cx, n.cy - (n.lines.length - 1) * 7.5 + i * 15 + 4, l)).join("")}</g>`;
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="State diagram">${vDefs}${edges}${Object.values(nodes).map(shape).join("")}${labels}${loops}</svg>`;
}

/* Sequence diagram with step-through. spec: {actors:[], msgs:[[from, to, label, type, explain] | {note:[actors], text}]}; type: "" call · "r" reply · "a" async */
function seqStepSVG(s){
  const n = s.actors.length, W = Math.max(VX.W, n * 128), colW = W / n, top = 12, boxH = 30, step = 36;
  const X = a => colW * (s.actors.indexOf(a) + 0.5);
  const hs = s.msgs.map(m => m.note ? 30 : m[0] === m[1] ? 44 : step);
  const H = top + boxH + 18 + hs.reduce((a, b) => a + b, 0) + 10;
  let out = s.actors.map(a => { const bw = Math.min(colW - 10, Math.max(80, a.length * 7.3 + 20));
    return `<rect class="sdsa" x="${X(a) - bw / 2}" y="${top}" width="${bw}" height="${boxH}" rx="6"/>${vText(X(a), top + 19, a)}<line class="sdll" x1="${X(a)}" x2="${X(a)}" y1="${top + boxH}" y2="${H - 4}"/>`; }).join("");
  let y = top + boxH + 24, k = 0;
  s.msgs.forEach((m, i) => {
    if (m.note) { const xs = m.note.map(X), x1 = Math.min(...xs) - 50, x2 = Math.max(...xs) + 50, w = Math.max(x2 - x1, m.text.length * 6.4 + 16), cx = (x1 + x2) / 2;
      out += `<g class="sm vxnote" data-i="${i}"><rect x="${cx - w / 2}" y="${y - 12}" width="${w}" height="22" rx="3"/>${vText(cx, y + 3, m.text, "sdlt seq")}</g>`; y += hs[i]; return; }
    const [a, b, lab, t] = m, x1 = X(a), x2 = X(b); k++;
    const cls = t === "r" ? "sde vxreply" : "sde", mk = t === "a" || t === "r" ? "vxOpen" : "vxArr";
    if (a === b) out += `<g class="sm" data-i="${i}"><path class="${cls}" d="M ${x1} ${y} h 36 v 18 h -32" marker-end="url(#${mk})"/>${vText(x1 + 42, y + 4, k + ". " + lab, "sdlt seq", "start")}</g>`;
    else { const dir = x2 > x1 ? 1 : -1; out += `<g class="sm" data-i="${i}"><line class="${cls}" x1="${x1}" x2="${x2 - dir * 3}" y1="${y}" y2="${y}" marker-end="url(#${mk})"/>${vText((x1 + x2) / 2, y - 6, k + ". " + lab, "sdlt seq")}</g>`; }
    y += hs[i];
  });
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Sequence diagram">${vDefs}${out}</svg>`;
}

function erHTML(s){
  return `<div class="vxer">${s.tables.map(t => `<div class="vxtbl"><div class="vxth">${vEsc(t.name)}${t.store ? `<span>${vEsc(t.store)}</span>` : ""}</div><table>${t.cols.map(([c, ty, key]) => `<tr><td class="c">${vEsc(c)}</td><td class="t">${vEsc(ty || "")}</td><td>${key ? `<span class="vxkey ${key.toLowerCase().split(" ")[0]}">${vEsc(key)}</span>` : ""}</td></tr>`).join("")}</table>${t.note ? `<p>${mdInline(t.note)}</p>` : ""}</div>`).join("")}</div>
    ${s.links && s.links.length ? `<ul class="vxlinks">${s.links.map(l => `<li>${mdInline(l)}</li>`).join("")}</ul>` : ""}`;
}
function calcHTML(s){
  return `<table class="vxcalc"><thead><tr><th>Quantity</th><th>How it's computed</th><th>Result</th></tr></thead><tbody>${s.rows.map(([q, f, r, note]) => `<tr><td>${mdInline(q)}${note ? `<div class="vxnote2">${mdInline(note)}</div>` : ""}</td><td><code>${vEsc(f)}</code></td><td><b>${vEsc(r)}</b></td></tr>`).join("")}</tbody></table>`;
}
function barsHTML(s){
  const vals = s.items.map(i => i[1]), mx = Math.max(...vals), mn = Math.min(...vals.filter(v => v > 0));
  const pctOf = v => s.log ? (Math.log10(v) - Math.log10(mn) + 0.3) / (Math.log10(mx) - Math.log10(mn) + 0.3) * 100 : v / mx * 100;
  return `<div class="vxbars">${s.items.map(([l, v, disp]) => `<div class="vxbar"><span class="l">${mdInline(l)}</span><span class="b"><i style="width:${Math.max(1.5, pctOf(v)).toFixed(1)}%"></i></span><span class="v">${vEsc(disp || v)}</span></div>`).join("")}</div>${s.log ? `<p class="vxnote2">Bar length uses a logarithmic scale (each step is ×10).</p>` : ""}`;
}
function tblHTML(s){
  return `<div class="tscroll"><table class="vxt"><thead><tr>${s.head.map(h => `<th>${mdInline(h)}</th>`).join("")}</tr></thead><tbody>${s.rows.map(r => `<tr>${r.map(c => `<td>${mdInline(String(c))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function vFig(inner, b, extraCap = "", cls = ""){
  return `<figure class="sdfig vxfig ${cls}">${b.title ? `<div class="vxft">${mdInline(b.title)}</div>` : ""}${inner}${b.caption || extraCap ? `<figcaption>${extraCap}${b.caption ? `<span class="vxcap">${mdInline(b.caption)}</span>` : ""}</figcaption>` : ""}</figure>`;
}
function vBlock(b){
  switch (b.t) {
    case "md": return `<div class="sdmd">${md(b.md)}</div>`;
    case "analogy": return `<div class="sdbox an"><b>Picture it like this</b><p>${mdInline(b.md)}</p></div>`;
    case "key": return `<div class="sdbox tip vxkeypt"><b>${mdInline(b.title || "Key idea")}</b><p>${mdInline(b.md)}</p></div>`;
    case "flow": return vFig(diagramSVG(b.spec, b.title).replace(/^<figure class="sdfig">|<\/figure>$/g, ""), b);
    case "uml": return vFig(umlSVG(b.spec), b, UML_LEGEND);
    case "state": return vFig(stateSVG(b.spec), b);
    case "seq": { const ex = b.spec.msgs.map(m => m.note ? "" : (m[4] || ""));
      return `<figure class="sdfig vxfig vxseq" data-ex="${vEsc(JSON.stringify(ex))}">${b.title ? `<div class="vxft">${mdInline(b.title)}</div>` : ""}
        <div class="vxctl"><button type="button" data-sq="prev">◀ Back</button><button type="button" data-sq="next">Step ▶</button><button type="button" data-sq="all">Show all</button><span class="vxpos">Press Step to walk through the messages one by one</span></div>
        ${seqStepSVG(b.spec)}<div class="vxexp" hidden></div><figcaption><span class="vxlg">→ call</span><span class="vxlg">⇢ reply (dashed)</span><span class="vxlg">open arrow = async message</span>${b.caption ? `<span class="vxcap">${mdInline(b.caption)}</span>` : ""}</figcaption></figure>`; }
    case "er": return vFig(erHTML(b.spec), b, "", "vxhtml");
    case "calc": return vFig(calcHTML(b.spec), b, "", "vxhtml");
    case "bars": return vFig(barsHTML(b.spec), b, "", "vxhtml");
    case "table": return vFig(tblHTML(b.spec), b, "", "vxhtml");
    case "code": return `<div class="codewrap">${b.title ? `<div class="codebar"><span>${vEsc(b.title)}</span><span class="cbtns"><button type="button" class="copy sdcopy">Copy</button></span></div>` : ""}<pre class="code ${b.lang || "java"}">${vEsc(b.code)}</pre></div>`;
    case "out": return `<div class="vxout"><div class="vxoh">${vEsc(b.title || "Output when you run main()")}</div><pre>${vEsc(b.text)}</pre></div>`;
    case "h": return `<h5 class="vxh">${mdInline(b.md)}</h5>`;
    case "ba": return `<div class="vxba"><div class="vxbap bef"><div class="vxbal">✘ ${vEsc(b.bl)}</div>${vBlock(b.before)}</div><div class="vxbap aft"><div class="vxbal">✔ ${vEsc(b.al)}</div>${vBlock(b.after)}</div></div>`;
    default: return "";
  }
}
function sdxHTML(x, title){
  if (!x || !x.blocks || !x.blocks.length) return "";
  return `<section class="sdx"><div class="sdxt">${vEsc(title || "Explained step by step, with diagrams")}</div>${x.blocks.map(vBlock).join("")}</section>`;
}
document.addEventListener("click", e => {
  const btn = e.target.closest(".vxseq [data-sq]"); if (!btn) return;
  const fig = btn.closest(".vxseq"), ms = [...fig.querySelectorAll(".sm")], ex = JSON.parse(fig.dataset.ex || "[]"), box = fig.querySelector(".vxexp"), pos = fig.querySelector(".vxpos");
  let i = +(fig.dataset.cur ?? -1);
  if (btn.dataset.sq === "all") { fig.classList.remove("stepping"); ms.forEach(m => m.classList.remove("cur", "past")); fig.dataset.cur = -1; box.hidden = true; pos.textContent = "Press Step to walk through the messages one by one"; return; }
  i = btn.dataset.sq === "next" ? Math.min(ms.length - 1, i + 1) : Math.max(0, i - 1);
  fig.dataset.cur = i; fig.classList.add("stepping");
  ms.forEach((m, j) => { m.classList.toggle("cur", j === i); m.classList.toggle("past", j < i); });
  const di = +ms[i].dataset.i, txt = ex[di] || ms[i].textContent;
  box.hidden = false; box.innerHTML = `<b>Step ${i + 1} of ${ms.length}</b> ${mdInline(txt)}`; pos.textContent = `Step ${i + 1} / ${ms.length}`;
});
