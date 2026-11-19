/* ================= System Design section (separate group from DSA) ================= */
const SDX = PLAN.sdx;
const SD_TABS = [[20, "Start here"], ...SDX.tabs.map((t, i) => [21 + i, t.label]), [28, "Interactive labs"], [29, "HLD questions"], [30, "LLD questions (Java)"], [33, "Questions by company"], [31, "Interview Q&A"], [32, "Cheat sheet"], [7, "30-day plan: SD days"], [34, "✎ My notes & bookmarks"]];
const SD_TAB_OF = {};               // concept id -> filter number
SDX.tabs.forEach((t, i) => t.sections.forEach(s => s.ids.forEach(id => SD_TAB_OF[id] = 21 + i)));
SDX.hld.forEach(h => SD_TAB_OF[h.id] = 29); SDX.lld.forEach(l => SD_TAB_OF[l.id] = 30);
SD_TAB_OF["hld-framework"] = 32;
const SD_TITLE = id => (SDX.concepts[id] || SDX.hld.find(h => h.id === id) || SDX.lld.find(l => l.id === id) || {title: id === "hld-framework" ? "HLD interview framework" : id}).title;
if (!state.sd) state.sd = {c: {}, h: {}, l: {}};
let SDV = {level: "All", q: "", open: new Set(), practice: false, qaTopic: "All", qaShowAll: false, company: "All", coPick: "Amazon", freq: "All"};
try { const g = localStorage.getItem("dsa30-group"); if (g === "sd") { SDV.group = "sd"; GROUP = "sd"; } } catch (e) {}
let GROUP = "dsa";
const isSD = f => f === 34 ? GROUP === "sd" : (f >= 20 || f === 7);

/* ---------- markdown-lite ---------- */
function mdInline(s){
  return esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
}
function md(src){
  if (!src) return "";
  const out = [], parts = src.split(/```(\w*)\n([\s\S]*?)```/);
  for (let p = 0; p < parts.length; p++) {
    if (p % 3 === 1) continue;
    if (p % 3 === 2) { out.push(`<pre class="code java sdcode">${esc(parts[p].replace(/\n$/, ""))}</pre>`); continue; }
    const lines = parts[p].split("\n"); let i = 0;
    while (i < lines.length) {
      const L = lines[i];
      if (!L.trim()) { i++; continue; }
      if (L.startsWith("### ")) { out.push(`<h4>${mdInline(L.slice(4))}</h4>`); i++; continue; }
      if (L.startsWith("|")) {
        const rows = []; while (i < lines.length && lines[i].startsWith("|")) rows.push(lines[i++].replace(/^\||\|$/g, "").split("|"));
        out.push(`<div class="tscroll"><table class="sdt"><thead><tr>${rows[0].map(c => `<th>${mdInline(c.trim())}</th>`).join("")}</tr></thead><tbody>${rows.slice(1).map(r => `<tr>${r.map(c => `<td>${mdInline(c.trim())}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
        continue;
      }
      if (/^- /.test(L)) { const it = []; while (i < lines.length && /^- /.test(lines[i])) it.push(lines[i++].slice(2)); out.push(`<ul>${it.map(x => `<li>${mdInline(x)}</li>`).join("")}</ul>`); continue; }
      if (/^\d+\. /.test(L)) { const it = []; while (i < lines.length && /^\d+\. /.test(lines[i])) it.push(lines[i++].replace(/^\d+\. /, "")); out.push(`<ol>${it.map(x => `<li>${mdInline(x)}</li>`).join("")}</ol>`); continue; }
      const para = []; while (i < lines.length && lines[i].trim() && !/^(### |\||- |\d+\. )/.test(lines[i])) para.push(lines[i++]);
      out.push(`<p>${mdInline(para.join(" "))}</p>`);
    }
  }
  return out.join("");
}

/* ---------- diagrams: boxes-and-arrows and sequence ---------- */
const KIND = n => { const m = /^(db|q|c|u|x):(.*)$/.exec(n); return m ? [m[1], m[2]] : ["box", n]; };
function wrapText(t, max){
  const w = t.split(" "), lines = [""];
  w.forEach(x => { const cur = lines[lines.length - 1]; if ((cur + " " + x).trim().length > max && cur) lines.push(x); else lines[lines.length - 1] = (cur + " " + x).trim(); });
  return lines.slice(0, 3);
}
function diagramSVG(d, label){
  if (!d) return "";
  if (d.seq) return seqSVG(d, label);
  const W = 760, rowH = 92, top = 16, nodes = {};
  d.rows.forEach((row, r) => row.forEach((n, j) => {
    const [k, t] = KIND(n), slot = W / row.length, maxc = Math.max(10, Math.floor((slot - 20) / 7.2));
    const lines = wrapText(t, Math.min(22, maxc)), bw = Math.min(slot - 14, Math.max(...lines.map(l => l.length)) * 7.2 + 26), bh = 22 + lines.length * 15;
    nodes[t] = {k, t, lines, cx: slot * (j + 0.5), cy: top + r * rowH + 30, w: bw, h: bh, r};
  }));
  const H = top + d.rows.length * rowH;
  let edges = "", labels = "";
  (d.edges || []).forEach(([a, b, lab]) => {
    const A = nodes[KIND(a)[1]], B = nodes[KIND(b)[1]]; if (!A || !B) return;
    let x1, y1, x2, y2;
    if (A.r === B.r) { const dir = B.cx > A.cx ? 1 : -1; x1 = A.cx + dir * A.w / 2; y1 = A.cy; x2 = B.cx - dir * B.w / 2; y2 = B.cy; }
    else if (B.r > A.r) { x1 = A.cx; y1 = A.cy + A.h / 2; x2 = B.cx; y2 = B.cy - B.h / 2 - 3; }
    else { x1 = A.cx; y1 = A.cy - A.h / 2; x2 = B.cx; y2 = B.cy + B.h / 2 + 3; }
    const far = A.r !== B.r && Math.abs(B.r - A.r) > 1, side = ((x1 + x2) / 2 >= W / 2 ? 1 : -1);
    const cx = (x1 + x2) / 2 + side * 70, cy = (y1 + y2) / 2;
    edges += `<path class="sde" d="M ${x1} ${y1}${far ? ` Q ${cx} ${cy} ${x2} ${y2}` : ` L ${x2} ${y2}`}" marker-end="url(#sdarrow)"/>`;
    if (lab) { const mx = far ? 0.25 * x1 + 0.5 * cx + 0.25 * x2 : (x1 + x2) / 2, my = far ? 0.25 * y1 + 0.5 * cy + 0.25 * y2 : (y1 + y2) / 2, lw = lab.length * 6.3 + 10;
      labels += `<rect class="sdlb" x="${mx - lw / 2}" y="${my - 9}" width="${lw}" height="17" rx="4"/><text class="sdlt" x="${mx}" y="${my + 4}" text-anchor="middle">${esc(lab)}</text>`; }
  });
  const shape = n => {
    const x = n.cx - n.w / 2, y = n.cy - n.h / 2;
    const txt = n.lines.map((l, i) => `<text class="sdnt" x="${n.cx}" y="${n.cy - (n.lines.length - 1) * 7.5 + i * 15 + 4 + (n.k === "db" ? 4 : 0)}" text-anchor="middle">${esc(l)}</text>`).join("");
    if (n.k === "db") return `<g class="sdn db"><path d="M${x} ${y + 7} v${n.h - 7} a${n.w / 2} 7 0 0 0 ${n.w} 0 v${-(n.h - 7)}"/><ellipse cx="${n.cx}" cy="${y + 7}" rx="${n.w / 2}" ry="7"/>${txt}</g>`;
    if (n.k === "q") return `<g class="sdn q"><rect x="${x}" y="${y}" width="${n.w}" height="${n.h}" rx="4"/>${[0.78, 0.86, 0.94].map(f => `<line x1="${x + n.w * f}" x2="${x + n.w * f}" y1="${y + 4}" y2="${y + n.h - 4}"/>`).join("")}${txt}</g>`;
    if (n.k === "u") return `<g class="sdn u"><rect x="${x}" y="${y}" width="${n.w}" height="${n.h}" rx="${n.h / 2}"/>${txt}</g>`;
    return `<g class="sdn ${n.k}"><rect x="${x}" y="${y}" width="${n.w}" height="${n.h}" rx="8"/>${txt}</g>`;
  };
  return `<figure class="sdfig"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label || "Architecture diagram")}"><defs><marker id="sdarrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="sdah"/></marker></defs>${edges}${Object.values(nodes).map(shape).join("")}${labels}</svg>
    <figcaption><span class="lg lgbox"></span>service <span class="lg db"></span>database/storage <span class="lg c"></span>cache <span class="lg q"></span>queue/stream <span class="lg u"></span>client <span class="lg x"></span>external</figcaption></figure>`;
}
function seqSVG(d, label){
  const W = 760, n = d.seq.length, colW = W / n, top = 14, boxH = 30, step = 34, H = top + boxH + 18 + d.msgs.length * step + 10;
  const X = a => colW * (d.seq.indexOf(a) + 0.5);
  let s = d.seq.map(a => `<rect class="sdsa" x="${X(a) - Math.min(colW - 12, 140) / 2}" y="${top}" width="${Math.min(colW - 12, 140)}" height="${boxH}" rx="6"/><text class="sdnt" x="${X(a)}" y="${top + 19}" text-anchor="middle">${esc(a)}</text><line class="sdll" x1="${X(a)}" x2="${X(a)}" y1="${top + boxH}" y2="${H - 6}"/>`).join("");
  d.msgs.forEach(([a, b, lab], i) => {
    const y = top + boxH + 26 + i * step, x1 = X(a), x2 = X(b), dir = x2 > x1 ? 1 : -1;
    s += `<line class="sde" x1="${x1}" x2="${x2 - dir * 4}" y1="${y}" y2="${y}" marker-end="url(#sdarrowS)"/><text class="sdlt seq" x="${(x1 + x2) / 2}" y="${y - 6}" text-anchor="middle">${i + 1}. ${esc(lab)}</text>`;
  });
  return `<figure class="sdfig"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label || "Sequence diagram")}"><defs><marker id="sdarrowS" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" class="sdah"/></marker></defs>${s}</svg><figcaption>Sequence: time flows downwards, numbered in order.</figcaption></figure>`;
}

/* ---------- shared bits ---------- */
const lvBadge = l => `<span class="sdlv ${l[0]}">${l}</span>`;
const FREQ_ICON = {"Very common": ["v", "★★★"], "Common": ["c", "★★"], "Sometimes": ["s", "★"], "Less common": ["l", "☆"]};
const freqBadge = f => f ? `<span class="sdfq ${FREQ_ICON[f][0]}" title="How often this question appears in interview reports and prep lists">${FREQ_ICON[f][1]} ${f}</span>` : "";
const SD_COMPANIES = (() => { const m = {}; [...SDX.hld, ...SDX.lld].forEach(q => q.companies.forEach(c => m[c] = (m[c] || 0) + 1));
  return Object.entries(m).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])); })();
const coOK = q => SDV.company === "All" || q.companies.includes(SDV.company);
const coSelect = () => `<label class="sdco-sel">Company <select id="sdCo"><option value="All">All companies</option>${SD_COMPANIES.map(([c, n]) => `<option value="${esc(c)}"${SDV.company === c ? " selected" : ""}>${esc(c)} (${n})</option>`).join("")}</select></label>`;
const qaCoSelect = () => { const m = {}; SDX.qa.forEach(q => q.companies.forEach(c => m[c] = (m[c] || 0) + 1));
  return `<label class="sdco-sel">Company <select id="sdCo"><option value="All">All companies</option>${Object.entries(m).sort((a, b) => b[1] - a[1]).map(([c, n]) => `<option value="${esc(c)}"${SDV.company === c ? " selected" : ""}>${esc(c)} (${n})</option>`).join("")}</select></label>`; };
const FREQ_ORDER = {"Very common": 0, "Common": 1, "Sometimes": 2, "Less common": 3, "": 4};
const doneMark = on => on ? `<span class="sddone" title="Learned">✓</span>` : "";
function sdCounts(){
  const c = Object.keys(SDX.concepts).length, cl = Object.keys(state.sd.c).filter(k => state.sd.c[k] && SDX.concepts[k]).length;
  const h = SDX.hld.length, hl = SDX.hld.filter(x => state.sd.h[x.id]).length, l = SDX.lld.length, ll = SDX.lld.filter(x => state.sd.l[x.id]).length;
  return {c, cl, h, hl, l, ll};
}
function sdToolbar(placeholder, extra = ""){
  return `<div class="sdbar">
    <label class="sdsearch"><span class="sr">Search system design</span><input type="search" id="sdQ" placeholder="${placeholder}" value="${esc(SDV.q)}" autocomplete="off"></label>
    <div class="sdlvls" role="group" aria-label="Level">${["All", "Basic", "Intermediate", "Advanced"].map(l => `<button type="button" data-lv="${l}" aria-pressed="${SDV.level === l}">${l === "All" ? "All levels" : l}</button>`).join("")}</div>${extra}</div>`;
}
function sdWireToolbar(root){
  const q = root.querySelector("#sdQ");
  if (q) { q.oninput = () => { SDV.q = q.value; const pos = q.selectionStart; renderSDX(); const n = document.getElementById("sdQ"); if (n) { n.focus(); n.setSelectionRange(pos, pos); } };
           q.onkeydown = e => { if (e.key === "Escape") { SDV.q = ""; renderSDX(); } }; }
  root.querySelectorAll(".sdlvls button").forEach(b => b.onclick = () => { SDV.level = b.dataset.lv; renderSDX(); });
}
function sdGo(id){
  const f = SD_TAB_OF[id]; if (!f) return;
  filter = f; GROUP = "sd"; SDV.q = ""; SDV.open.add(id); renderTabs(); renderBoard();
  requestAnimationFrame(() => { const el = document.getElementById("sdc-" + id); if (el) { el.scrollIntoView({block: "start"}); const h = el.querySelector(".sdch"); if (h) h.focus({preventScroll: true}); } });
}
const lvOK = l => SDV.level === "All" || l === SDV.level;
const hit = (q, ...xs) => !q || xs.some(x => x && String(x).toLowerCase().includes(q));

/* ---------- concept cards ---------- */
function conceptCard(c){
  const open = SDV.open.has(c.id), learned = !!state.sd.c[c.id];
  return `<article class="sdc${learned ? " learned" : ""}" id="sdc-${c.id}">
    <button type="button" class="sdch" aria-expanded="${open}" aria-controls="sdb-${c.id}" data-id="${c.id}">
      <span class="sdct"><b>${esc(c.title)}</b>${doneMark(learned)}</span>${lvBadge(c.level)}
      <span class="sdwhat">${mdInline(c.what)}</span></button>${tmActs("sd:" + c.id, c.title, "sd")}${state.tn["sd:" + c.id] ? tmNoteArea("sd:" + c.id) : ""}
    <div class="sdcb" id="sdb-${c.id}"${open ? "" : " hidden"}>${open ? conceptBody(c) : ""}</div></article>`;
}
function conceptBody(c){
  return `<div class="sdmd">${md(c.body)}</div>
    ${c.analogy ? `<div class="sdbox an"><b>Real-life analogy</b><p>${mdInline(c.analogy)}</p></div>` : ""}
    ${c.example ? `<div class="sdbox ex"><b>Real-world example</b><p>${mdInline(c.example)}</p></div>` : ""}
    ${c.diagram ? diagramSVG(c.diagram, c.title) : ""}
    ${c.lab ? `<div class="sdlabhost" data-lab="${c.lab}"><button type="button" class="sdlabbtn" data-lab="${c.lab}">▶ Try the interactive lab: ${esc(LAB_TITLES[c.lab])}</button></div>` : ""}
    ${c.tips.length ? `<div class="sdbox tip"><b>In the interview</b><ul>${c.tips.map(t => `<li>${mdInline(t)}</li>`).join("")}</ul></div>` : ""}
    ${c.see.length ? `<div class="sdsee"><span>Related:</span>${c.see.map(s => `<button type="button" class="sdlink" data-go="${s}">${esc(SD_TITLE(s))}</button>`).join("")}</div>` : ""}
    <label class="sdlearn"><input type="checkbox" data-learn="${c.id}"${state.sd.c[c.id] ? " checked" : ""}> I understand this concept</label>`;
}
function renderConceptTab(root, t){
  const q = SDV.q.trim().toLowerCase(), all = t.sections.flatMap(s => s.ids), learned = all.filter(id => state.sd.c[id]).length;
  const secs = t.sections.map(s => ({name: s.name, cs: s.ids.map(id => SDX.concepts[id]).filter(c => lvOK(c.level) && hit(q, c.title, c.what, c.body))})).filter(s => s.cs.length);
  root.innerHTML = `<div class="eyebrow">System design · ${esc(t.label)}</div><h2>${esc(t.label)}</h2><p class="lead">${esc(t.intro)}</p>
    <div class="sdprog"><div class="trbar"><i style="width:${learned / all.length * 100}%"></i></div><span><b>${learned}</b> of ${all.length} concepts learned in this tab</span></div>
    ${sdToolbar("Search this tab, e.g. cache, Kafka, CAP", `<button type="button" class="sdtog" id="sdExpand">${secs.every(s => s.cs.every(c => SDV.open.has(c.id))) ? "Collapse all" : "Expand all"}</button>`)}
    <div class="sdlayout">
      <nav class="sdtoc" aria-label="Concepts in this tab"><details open><summary>Contents</summary>${secs.map(s => `<div class="sdtocs"><b>${esc(s.name)}</b>${s.cs.map(c => `<a href="#sdc-${c.id}" data-toc="${c.id}"><span class="dot ${c.level[0]}" aria-hidden="true"></span>${esc(c.title)}${state.sd.c[c.id] ? " ✓" : ""}</a>`).join("")}</div>`).join("")}</details></nav>
      <div class="sdlist">${secs.length ? secs.map(s => `<h3 class="sdsec">${esc(s.name)}</h3>${s.cs.map(conceptCard).join("")}`).join("") : `<p class="qempty">No concepts match. Clear the search or choose another level.</p>`}</div>
    </div>`;
  sdWireToolbar(root);
  root.querySelector("#sdExpand").onclick = () => { const ids = secs.flatMap(s => s.cs.map(c => c.id)), allOpen = ids.every(id => SDV.open.has(id)); ids.forEach(id => allOpen ? SDV.open.delete(id) : SDV.open.add(id)); renderSDX(); };
  root.querySelectorAll("[data-toc]").forEach(a => a.onclick = e => { e.preventDefault(); SDV.open.add(a.dataset.toc); const card = document.getElementById("sdc-" + a.dataset.toc); openCard(card); card.scrollIntoView({block: "start"}); });
}
function openCard(card){
  if (!card) return;
  const id = card.id.slice(4), btn = card.querySelector(".sdch"), body = card.querySelector(".sdcb");
  if (!body.innerHTML) body.innerHTML = cardBodyFor(id);
  body.hidden = false; btn.setAttribute("aria-expanded", "true"); SDV.open.add(id);
}
function cardBodyFor(id){
  if (SDX.concepts[id]) return conceptBody(SDX.concepts[id]);
  const h = SDX.hld.find(x => x.id === id); if (h) return hldBody(h);
  const l = SDX.lld.find(x => x.id === id); if (l) return lldBody(l);
  return "";
}

/* ---------- HLD ---------- */
function hldCard(h){
  const open = SDV.open.has(h.id), done = !!state.sd.h[h.id];
  return `<article class="sdc${done ? " learned" : ""}" id="sdc-${h.id}">
    <button type="button" class="sdch" aria-expanded="${open}" aria-controls="sdb-${h.id}" data-id="${h.id}">
      <span class="sdct"><b>${esc(h.title)}</b>${doneMark(done)}</span><span class="sdbadges">${freqBadge(h.freq)}${lvBadge(h.level)}</span>
      <span class="sdwhat"><span class="sdco">Asked at ${h.companies.map(esc).join(" · ")}</span> — tests ${mdInline(h.tests)}</span></button>${tmActs("sd:" + h.id, h.title, "hld")}${state.tn["sd:" + h.id] ? tmNoteArea("sd:" + h.id) : ""}
    <div class="sdcb" id="sdb-${h.id}"${open ? "" : " hidden"}>${open ? hldBody(h) : ""}</div></article>`;
}
function hldBody(h){
  const ans = `
    <h4>2 · Back-of-the-envelope estimates</h4><div class="sdmd">${md(h.estimates)}</div>
    <h4>3 · API</h4><div class="sdmd">${md(h.api)}</div>
    <h4>4 · Data model</h4><div class="sdmd">${md(h.data)}</div>
    <h4>5 · High-level design</h4>${diagramSVG(h.design, h.title)}
    <ol class="sdflow">${h.flow.map(f => `<li>${mdInline(f)}</li>`).join("")}</ol>
    <h4>6 · Deep dives</h4><ul class="sddeep">${h.deep.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul>
    ${h.tradeoffs.length ? `<h4>7 · Trade-offs to say out loud</h4><ul>${h.tradeoffs.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul>` : ""}
    ${h.followups.length ? `<div class="sdbox tip"><b>Likely follow-up questions</b><ul>${h.followups.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul></div>` : ""}`;
  return `<h4>1 · Requirements</h4><div class="sdreq"><div><b>Functional</b><ul>${h.functional.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul></div>
      <div><b>Non-functional</b><ul>${h.nonfunctional.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul></div></div>
    ${SDV.practice ? `<details class="sdans"><summary>Try it yourself first: design it on paper for 30 minutes, then open the model answer</summary>${ans}</details>` : ans}
    <label class="sdlearn"><input type="checkbox" data-hld="${h.id}"${state.sd.h[h.id] ? " checked" : ""}> I have practised this design</label>`;
}
function renderHLD(root){
  const q = SDV.q.trim().toLowerCase(), list = SDX.hld.filter(h => lvOK(h.level) && coOK(h) && hit(q, h.title, h.tests, h.companies.join(" "), h.deep.join(" ")));
  const c = sdCounts();
  root.innerHTML = `<div class="eyebrow">System design · interview questions</div><h2>High-level design questions</h2>
    <p class="lead">${SDX.hld.length} design questions asked at Google, Amazon, Microsoft, Meta, Uber, Flipkart and other product companies, from basic to advanced. Each has a full model answer in the 7-step interview format with an architecture diagram.</p>
    <div class="sdprog"><div class="trbar"><i style="width:${c.hl / c.h * 100}%"></i></div><span><b>${c.hl}</b> of ${c.h} designs practised</span></div>
    ${sdToolbar("Search designs, e.g. chat, payment, Google", `${coSelect()}<label class="sdpract"><input type="checkbox" id="sdPractice"${SDV.practice ? " checked" : ""}> Practice mode (hide answers)</label>`)}
    <div class="sdlist wide">${list.length ? list.map(hldCard).join("") : `<p class="qempty">No designs match.</p>`}</div>`;
  sdWireToolbar(root);
  root.querySelector("#sdPractice").onchange = e => { SDV.practice = e.target.checked; renderSDX(); };
  root.querySelector("#sdCo").onchange = e => { SDV.company = e.target.value; renderSDX(); };
}

/* ---------- LLD ---------- */
function lldCard(l){
  const open = SDV.open.has(l.id), done = !!state.sd.l[l.id];
  return `<article class="sdc${done ? " learned" : ""}" id="sdc-${l.id}">
    <button type="button" class="sdch" aria-expanded="${open}" aria-controls="sdb-${l.id}" data-id="${l.id}">
      <span class="sdct"><b>${esc(l.title)}</b>${doneMark(done)}</span><span class="sdbadges">${freqBadge(l.freq)}${lvBadge(l.level)}</span>
      <span class="sdwhat"><span class="sdco">Asked at ${l.companies.map(esc).join(" · ")}</span> — patterns: ${esc(l.patterns.join(", "))}</span></button>${tmActs("sd:" + l.id, l.title, "lld")}${state.tn["sd:" + l.id] ? tmNoteArea("sd:" + l.id) : ""}
    <div class="sdcb" id="sdb-${l.id}"${open ? "" : " hidden"}>${open ? lldBody(l) : ""}</div></article>`;
}
function lldBody(l){
  const code = `<div class="codewrap"><div class="codebar"><span>Java · complete, compiles and runs (main() demo)</span><span class="cbtns"><button type="button" class="copy sdcopy">Copy</button></span></div><pre class="code java">${esc(l.code)}</pre></div>`;
  return `<div class="sdreq"><div><b>Requirements</b><ul>${l.requirements.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul></div>
      <div><b>Classes / entities</b><ul>${l.entities.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul><b>Patterns used</b><ul>${l.patterns.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul></div></div>
    ${SDV.practice ? `<details class="sdans"><summary>Try it yourself first: code it in 45 minutes, then open the solution</summary>${code}</details>` : code}
    ${l.extensions.length ? `<div class="sdbox tip"><b>Extensions interviewers ask for</b><ul>${l.extensions.map(f => `<li>${mdInline(f)}</li>`).join("")}</ul></div>` : ""}
    <label class="sdlearn"><input type="checkbox" data-lld="${l.id}"${state.sd.l[l.id] ? " checked" : ""}> I have coded this myself</label>`;
}
function renderLLD(root){
  const q = SDV.q.trim().toLowerCase(), list = SDX.lld.filter(l => lvOK(l.level) && coOK(l) && hit(q, l.title, l.patterns.join(" "), l.companies.join(" "), l.code));
  const c = sdCounts();
  root.innerHTML = `<div class="eyebrow">System design · machine coding</div><h2>Low-level design questions (Java)</h2>
    <p class="lead">${SDX.lld.length} object-oriented design / machine-coding problems. Every solution is complete Java that compiles and runs, applying SOLID and design patterns. Read the method in <button type="button" class="sdlink" data-go="lld-approach">How to answer an LLD round</button>.</p>
    <div class="sdprog"><div class="trbar"><i style="width:${c.ll / c.l * 100}%"></i></div><span><b>${c.ll}</b> of ${c.l} coded</span></div>
    ${sdToolbar("Search, e.g. parking, Strategy, Amazon", `${coSelect()}<label class="sdpract"><input type="checkbox" id="sdPractice"${SDV.practice ? " checked" : ""}> Practice mode (hide code)</label>`)}
    <div class="sdlist wide">${list.length ? list.map(lldCard).join("") : `<p class="qempty">No problems match.</p>`}</div>`;
  sdWireToolbar(root);
  root.querySelector("#sdPractice").onchange = e => { SDV.practice = e.target.checked; renderSDX(); };
  root.querySelector("#sdCo").onchange = e => { SDV.company = e.target.value; renderSDX(); };
}

/* ---------- Questions by company ---------- */
function renderCompanies(root){
  if (SDV.q.trim()) { renderSearch(root); return; }
  const pick = SDV.coPick, byF = (a, b) => FREQ_ORDER[a.freq] - FREQ_ORDER[b.freq] || "BIA".indexOf(a.level[0]) - "BIA".indexOf(b.level[0]);
  const hs = SDX.hld.filter(h => h.companies.includes(pick) && lvOK(h.level)).sort(byF), ls = SDX.lld.filter(l => l.companies.includes(pick) && lvOK(l.level)).sort(byF);
  const MAJOR = ["Google", "Amazon", "Microsoft", "Meta", "Uber", "Apple", "Flipkart", "Swiggy"];
  const row = (q, kind) => `<tr><th scope="row"><button type="button" class="sdlink" data-go="${q.id}">${esc((t => t[0].toUpperCase() + t.slice(1))(q.title.replace(/^Design (a |an )?/, "")))}</button></th><td>${kind}</td><td>${freqBadge(q.freq)}</td>${MAJOR.map(c => `<td class="mk">${q.companies.includes(c) ? '<span aria-label="yes">●</span>' : '<span class="no" aria-label="no">·</span>'}</td>`).join("")}<td class="oth">${esc(q.companies.filter(c => !MAJOR.includes(c)).join(", "))}</td></tr>`;
  const all = [...SDX.hld.map(q => [q, "HLD"]), ...SDX.lld.map(q => [q, "LLD"])].filter(([q]) => lvOK(q.level)).sort((a, b) => byF(a[0], b[0]));
  root.innerHTML = `<div class="eyebrow">System design · company-wise</div><h2>Which questions are asked at which company</h2>
    <p class="lead">Pick a company to see the HLD and LLD questions reported in its interviews, most frequently asked first. The table below shows every question against the big companies at a glance.</p>
    <div class="sdbox tip"><b>How to read this</b><p>Company tags come from public candidate reports (LeetCode Discuss, Glassdoor, Blind, GeeksforGeeks interview experiences) and prep lists. <b>★★★ Very common</b> = in the top 10 most-repeated design questions across prep sources (PracHub, Nov 2026); <b>★★ Common</b> = top 20; <b>★ Sometimes</b> = top 30; <b>☆ Less common</b> = asked, but outside the top 30. Q&amp;A frequency marks staple concept questions (CAP, SQL vs NoSQL, caching, sharding…) as ★★★. Companies change their question pools, so treat this as a strong guide, not a guarantee, and prepare the ★★★ ones first.</p></div>
    ${sdToolbar("Search all of system design", "")}
    <div class="sdcos" role="group" aria-label="Company">${SD_COMPANIES.map(([c, n]) => `<button type="button" data-co="${esc(c)}" aria-pressed="${pick === c}">${esc(c)} <small>${n}</small></button>`).join("")}</div>
    <h3 class="sdcoh">${esc(pick)}: ${hs.length} HLD · ${ls.length} LLD · ${SDX.qa.filter(x => x.companies.includes(pick)).length} Q&amp;A</h3>
    ${hs.length ? `<h3 class="sdsec">High-level design</h3><div class="sdlist wide">${hs.map(hldCard).join("")}</div>` : ""}
    ${ls.length ? `<h3 class="sdsec">Low-level design (Java)</h3><div class="sdlist wide">${ls.map(lldCard).join("")}</div>` : ""}
    ${(() => { const qs = SDX.qa.filter(x => x.companies.includes(pick) && lvOK(x.level)).sort((a, b) => FREQ_ORDER[a.freq] - FREQ_ORDER[b.freq]);
      return qs.length ? `<h3 class="sdsec">Conceptual Q&amp;A commonly asked at ${esc(pick)} (${qs.length})</h3><div class="sdqa">${qs.map(x => `<details class="sdq"><summary><span class="sdqq">${mdInline(x.q)}</span><span class="sdbadges">${freqBadge(x.freq)}${lvBadge(x.level)}</span></summary><div class="sdqa-a">${md(x.a)}</div></details>`).join("")}</div>` : ""; })()}
    <h3 class="sdsec">All questions × companies</h3>
    <div class="tscroll"><table class="sdt sdmatrix"><thead><tr><th scope="col">Question</th><th scope="col">Type</th><th scope="col">How often</th>${MAJOR.map(c => `<th scope="col">${c}</th>`).join("")}<th scope="col">Also asked at</th></tr></thead>
      <tbody>${all.map(([q, k]) => row(q, k)).join("")}</tbody></table></div>
    <p class="labnote">Sources: <a href="https://prachub.com/resources/top-30-system-design-questions-ranked-by-how-often-they-re-asked" target="_blank" rel="noopener">PracHub frequency ranking</a> · <a href="https://www.designgurus.io/blog/system-design-interviews-at-google-meta-amazon" target="_blank" rel="noopener">DesignGurus company guides</a> · <a href="https://leetcode.com/discuss/interview-experience/" target="_blank" rel="noopener">LeetCode Discuss interview experiences</a> · <a href="https://workat.tech/machine-coding" target="_blank" rel="noopener">workat.tech machine coding</a></p>`;
  sdWireToolbar(root);
  root.querySelectorAll(".sdcos button").forEach(b => b.onclick = () => { SDV.coPick = b.dataset.co; renderSDX(); });
}

/* ---------- Q&A ---------- */
function renderQA(root){
  const q = SDV.q.trim().toLowerCase(), topics = ["All", ...new Set(SDX.qa.map(x => x.topic))];
  const list = SDX.qa.filter(x => lvOK(x.level) && coOK(x) && (SDV.freq === "All" || x.freq === SDV.freq) && (SDV.qaTopic === "All" || x.topic === SDV.qaTopic) && hit(q, x.q, x.a, x.topic, x.companies.join(" ")))
    .sort((a, b) => SDV.freq === "All" && SDV.qaSort === "freq" ? FREQ_ORDER[a.freq] - FREQ_ORDER[b.freq] : 0);
  root.innerHTML = `<div class="eyebrow">System design · rapid fire</div><h2>Interview Q&amp;A</h2>
    <p class="lead">${SDX.qa.length} short conceptual questions interviewers fire between design steps, with crisp model answers. Each shows where it is commonly asked and how often (★★★ asked in almost every loop). Say your answer out loud first, then open it.</p>
    ${sdToolbar("Search questions or a company", `${qaCoSelect()}<label class="sdco-sel">How often <select id="sdFreq">${["All", "Very common", "Common", "Sometimes"].map(f => `<option${SDV.freq === f ? " selected" : ""}>${f}</option>`).join("")}</select></label><label class="sdpract"><input type="checkbox" id="sdSort"${SDV.qaSort === "freq" ? " checked" : ""}> Most asked first</label><button type="button" class="sdtog" id="sdShowAll">${SDV.qaShowAll ? "Hide all answers" : "Show all answers"}</button>`)}
    <div class="sdtopics" role="group" aria-label="Topic">${topics.map(t => `<button type="button" data-tp="${esc(t)}" aria-pressed="${SDV.qaTopic === t}">${esc(t)}</button>`).join("")}</div>
    <p class="sdcount">${list.length} questions</p>
    <div class="sdqa">${list.map((x, i) => `<details class="sdq" id="qa-${x.id}"${SDV.qaShowAll || state.tn["qa:" + x.id] ? " open" : ""}><summary><span class="sdqn">${i + 1}</span><span class="sdqq">${mdInline(x.q)}<span class="sdqco">Asked at ${x.companies.map(esc).join(" · ")}</span></span><span class="sdbadges">${freqBadge(x.freq)}${lvBadge(x.level)}<span class="sdqt">${esc(x.topic)}</span>${tmActs("qa:" + x.id, x.q, "qa")}</span></summary>${state.tn["qa:" + x.id] ? tmNoteArea("qa:" + x.id) : ""}<div class="sdqa-a">${md(x.a)}</div></details>`).join("") || `<p class="qempty">No questions match.</p>`}</div>`;
  sdWireToolbar(root);
  root.querySelector("#sdShowAll").onclick = () => { SDV.qaShowAll = !SDV.qaShowAll; renderSDX(); };
  root.querySelector("#sdCo").onchange = e => { SDV.company = e.target.value; renderSDX(); };
  root.querySelector("#sdFreq").onchange = e => { SDV.freq = e.target.value; renderSDX(); };
  root.querySelector("#sdSort").onchange = e => { SDV.qaSort = e.target.checked ? "freq" : ""; renderSDX(); };
  root.querySelectorAll(".sdtopics button").forEach(b => b.onclick = () => { SDV.qaTopic = b.dataset.tp; renderSDX(); });
}

/* ---------- Start here ---------- */
function renderStart(root){
  const c = sdCounts();
  const stage = s => { const n = s.ids.length, d = s.ids.filter(id => state.sd.c[id] || state.sd.h[id] || state.sd.l[id]).length;
    return `<div class="sdstage"><div class="sdsh"><h3>${esc(s.name)}</h3><span>${d}/${n}</span></div><p>${esc(s.why)}</p><div class="trbar"><i style="width:${d / n * 100}%"></i></div>
      <div class="sdchips">${s.ids.map(id => `<button type="button" class="sdchip${state.sd.c[id] ? " on" : ""}" data-go="${id}">${state.sd.c[id] ? "✓ " : ""}${esc(SD_TITLE(id))}</button>`).join("")}</div></div>`; };
  const byLv = arr => ["Basic", "Intermediate", "Advanced"].map(l => `<div><b>${l}</b><ul>${arr.filter(x => x.level === l).map(x => `<li><button type="button" class="sdlink" data-go="${x.id}">${esc(x.title)}</button></li>`).join("")}</ul></div>`).join("");
  root.innerHTML = `<div class="eyebrow">System design · start here</div><h2>System Design from zero to senior level</h2>
    ${sdToolbar("Search all of system design: concepts, HLD, LLD, Q&A")}
    <p class="lead">Everything you need for system design interviews at Google, Microsoft, Amazon and other product companies, explained for someone who has never designed a system. Read the concepts in order, try the interactive labs, then practise HLD and LLD questions out loud.</p>
    <div class="sdstats">
      <div><b>${c.cl}<span>/${c.c}</span></b>concepts learned</div><div><b>${c.hl}<span>/${c.h}</span></b>HLD designs practised</div>
      <div><b>${c.ll}<span>/${c.l}</span></b>LLD problems coded</div><div><b>${SDX.qa.length}</b>interview Q&amp;As</div><div><b>${SD_COMPANIES.length}</b>companies tagged</div></div>
    <div class="sdbox tip"><b>How to use this section</b><ol>
      <li><b>Learn</b>: work through Stages 1 → 3 below. Open each concept card, read the explanation, analogy and diagram, then tick <i>I understand this concept</i>.</li>
      <li><b>Play</b>: the Interactive labs let you see caching, rate limiting, consistent hashing, load balancing, quorums and feed fan-out working.</li>
      <li><b>Practise</b>: one HLD and one LLD question a day with <i>Practice mode</i> on: attempt first, then compare with the model answer.</li>
      <li><b>Revise</b>: the Interview Q&amp;A and Cheat sheet before every interview.</li></ol></div>
    ${SDX.roadmap.map(stage).join("")}
    <div class="sdstage"><div class="sdsh"><h3>Practice order for interview questions</h3></div><p>Start with the basic designs and move right as you get comfortable.</p>
      <h4>High-level design</h4><div class="sdcols">${byLv(SDX.hld)}</div><h4>Low-level design (Java)</h4><div class="sdcols">${byLv(SDX.lld)}</div></div>`;
  sdWireToolbar(root);
}

/* ---------- Cheat sheet ---------- */
function renderCheat(root){
  const tbl = (h, rows) => `<div class="tscroll"><table class="sdt"><thead><tr>${h.map(x => `<th>${x}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(x => `<td>${mdInline(x)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  root.innerHTML = `<div class="eyebrow">System design · revise before the interview</div><h2>Cheat sheet</h2>
    <p class="lead">The interview framework, the numbers to remember and quick 'if you hear X, use Y' mappings on one page.</p>
    <div class="sdstage" id="sdc-hld-framework"><h3>The 7-step HLD interview framework (45–60 min)</h3>
      <div class="sdsteps">${SDX.framework.map(([t, m, d]) => `<div class="sdstep"><b>${esc(t)}</b><em>${esc(m)}</em><span>${mdInline(d)}</span></div>`).join("")}</div>
      <p>For LLD rounds see <button type="button" class="sdlink" data-go="lld-approach">How to answer a low-level design round</button>.</p></div>
    <div class="sdstage"><h3>What interviewers expect at each level</h3>${tbl(["Level", "Expectation"], SDX.levels)}</div>
    <div class="sdstage"><h3>If you hear… think…</h3>${tbl(["Requirement", "Reach for"], SDX.think)}</div>
    <div class="sdstage"><h3>Which database?</h3>${tbl(["Store", "Use it for"], SDX.dbpick)}</div>
    <div class="sdstage"><h3>Numbers for estimation</h3>${tbl(["Quantity", "Value"], SDX.numbers)}${tbl(["Power of 2", "≈", "Bytes"], SDX.powers)}
      <p>Full latency table and worked example: <button type="button" class="sdlink" data-go="latency-numbers">Latency numbers</button> · <button type="button" class="sdlink" data-go="estimation">Back-of-the-envelope estimation</button> · <button type="button" class="sdlink" data-golab="estimator">Estimation calculator lab</button></p></div>
    <div class="sdstage"><h3>Common mistakes that fail candidates</h3><ul>${SDX.mistakes.map(m => `<li>${mdInline(m)}</li>`).join("")}</ul></div>
    <div class="sdstage"><h3>What different companies tend to focus on</h3>${tbl(["Company", "Focus (general patterns, not guarantees)"], SDX.companies)}</div>`;
}

/* ---------- search across everything ---------- */
function renderSearch(root){
  const q = SDV.q.trim().toLowerCase();
  const cs = Object.values(SDX.concepts).filter(c => lvOK(c.level) && hit(q, c.title, c.what, c.body));
  const hs = SDX.hld.filter(h => lvOK(h.level) && hit(q, h.title, h.tests, h.deep.join(" "))), ls = SDX.lld.filter(l => lvOK(l.level) && hit(q, l.title, l.patterns.join(" ")));
  const qs = SDX.qa.filter(x => lvOK(x.level) && hit(q, x.q, x.a));
  const item = (id, t, type, lv, sub) => `<li><button type="button" class="sdres" data-go="${id}"><span class="sdrt">${type}</span><b>${esc(t)}</b>${lvBadge(lv)}<span class="sdrs">${sub}</span></button></li>`;
  root.innerHTML = `<div class="eyebrow">System design · search</div><h2>Results for “${esc(SDV.q)}”</h2>${sdToolbar("Search all of system design")}
    <p class="sdcount">${cs.length} concepts · ${hs.length} HLD · ${ls.length} LLD · ${qs.length} Q&amp;A</p>
    <ul class="sdresults">${cs.map(c => item(c.id, c.title, "Concept", c.level, mdInline(c.what))).join("")}${hs.map(h => item(h.id, h.title, "HLD", h.level, esc(h.tests))).join("")}${ls.map(l => item(l.id, l.title, "LLD", l.level, esc(l.patterns.join(", ")))).join("")}</ul>
    ${qs.length ? `<h3>Interview Q&amp;A</h3><div class="sdqa">${qs.map(x => `<details class="sdq"><summary><span class="sdqq">${mdInline(x.q)}</span>${lvBadge(x.level)}</summary><div class="sdqa-a">${md(x.a)}</div></details>`).join("")}</div>` : ""}`;
  sdWireToolbar(root);
}

/* ---------- main render + delegated events ---------- */
function renderSDX(){
  const root = document.getElementById("sdx");
  if (SDV.lastTab !== filter) { SDV.company = "All"; SDV.freq = "All"; SDV.lastTab = filter; }   // filters are per tab
  if (filter === 20 && SDV.q.trim()) renderSearch(root);
  else if (filter === 20) renderStart(root);
  else if (filter >= 21 && filter <= 27) renderConceptTab(root, SDX.tabs[filter - 21]);
  else if (filter === 28) renderLabs(root);
  else if (filter === 29) renderHLD(root);
  else if (filter === 30) renderLLD(root);
  else if (filter === 31) renderQA(root);
  else if (filter === 32) renderCheat(root);
  else if (filter === 33) renderCompanies(root);
  else if (filter === 34) renderNotes(root);
}
document.addEventListener("click", e => {
  const root = document.getElementById("sdx"); if (!root || root.hidden || !root.contains(e.target)) return;
  const head = e.target.closest(".sdch");
  if (head) {
    const card = head.closest(".sdc"), body = card.querySelector(".sdcb"), id = head.dataset.id, open = head.getAttribute("aria-expanded") !== "true";
    if (open) openCard(card); else { body.hidden = true; head.setAttribute("aria-expanded", "false"); SDV.open.delete(id); }
    return;
  }
  const go = e.target.closest("[data-go]"); if (go) { sdGo(go.dataset.go); return; }
  const gl = e.target.closest("[data-golab]"); if (gl) { filter = 28; renderTabs(); renderBoard(); requestAnimationFrame(() => { const el = document.getElementById("lab-" + gl.dataset.golab); if (el) el.scrollIntoView({block: "start"}); }); return; }
  const lb = e.target.closest(".sdlabbtn"); if (lb) { const host = lb.parentElement; host.innerHTML = labHTML(lb.dataset.lab, "in"); LABS[lb.dataset.lab](host.querySelector(".lab")); return; }
  const cp = e.target.closest(".sdcopy");
  if (cp) { const pre = cp.closest(".codewrap").querySelector("pre"); const done = () => { cp.textContent = "Copied"; setTimeout(() => cp.textContent = "Copy", 1500); };
    try { navigator.clipboard.writeText(pre.textContent).then(done, () => selectCode(cp)); } catch (er) { selectCode(cp); } }
});
document.addEventListener("change", e => {
  const t = e.target; if (!t.dataset) return;
  const set = (bucket, id) => { if (t.checked) state.sd[bucket][id] = Date.now(); else delete state.sd[bucket][id]; save();
    const card = t.closest(".sdc"); if (card) { card.classList.toggle("learned", t.checked); const tt = card.querySelector(".sdct"); const m = tt.querySelector(".sddone"); if (t.checked && !m) tt.insertAdjacentHTML("beforeend", doneMark(true)); if (!t.checked && m) m.remove(); }
    if (t.checked) SDV.open.delete(id);                                  // done: fold the card up
    const prog = document.querySelector("#sdx .sdprog");
    if (prog && filter >= 21 && filter <= 30) { const y = window.scrollY; renderSDX(); window.scrollTo(0, y); }
    else if (t.checked && card) { const b = card.querySelector(".sdcb"), h = card.querySelector(".sdch"); b.hidden = true; h.setAttribute("aria-expanded", "false"); }
    if (t.checked) { const c2 = document.getElementById("sdc-" + id); if (c2) { const r = c2.getBoundingClientRect(); if (r.top < 0 || r.top > innerHeight) c2.scrollIntoView({block: "start"}); c2.querySelector(".sdch").focus({preventScroll: true}); } } };
  if (t.dataset.learn) set("c", t.dataset.learn); else if (t.dataset.hld) set("h", t.dataset.hld); else if (t.dataset.lld) set("l", t.dataset.lld);
});

/* ================= Interactive labs ================= */
const LAB_TITLES = {estimator: "Back-of-the-envelope calculator", ratelimit: "Rate limiter playground", lb: "Load balancer simulator", cache: "Cache eviction (LRU / LFU / FIFO)", ring: "Consistent hashing ring", quorum: "Quorum replication (N, R, W)", fanout: "Feed fan-out: push vs pull vs hybrid"};
const LAB_DESC = {
  estimator: "Type your assumptions; it computes QPS, peak, storage and bandwidth the way you should in an interview.",
  ratelimit: "Fire requests at a token bucket, fixed window or sliding log and watch which get rejected.",
  lb: "Send requests of different lengths to four servers (one is slow) and compare algorithms.",
  cache: "Feed an access sequence into a small cache and watch hits, misses and evictions.",
  ring: "Add and remove servers on a hash ring and see how few keys move compared with hash % N.",
  quorum: "Turn replicas off and change R and W to see when reads are guaranteed fresh and when writes fail.",
  fanout: "Compare the work a post creates for normal users and celebrities under each feed strategy."};
function labHTML(k, mode){ return `<section class="lab" id="${mode === "in" ? "" : "lab-" + k}" data-lab="${k}"><h3>${esc(LAB_TITLES[k])}</h3><p class="labd">${esc(LAB_DESC[k])}</p><div class="labbody"></div></section>`; }
function renderLabs(root){
  root.innerHTML = `<div class="eyebrow">System design · learn by playing</div><h2>Interactive labs</h2>
    <p class="lead">Seven small simulations of the ideas interviewers ask about most. Change the inputs and watch what happens.</p>
    <div class="labgrid">${Object.keys(LAB_TITLES).map(k => labHTML(k)).join("")}</div>`;
  root.querySelectorAll(".lab").forEach(el => LABS[el.dataset.lab](el));
}
const fmtN = n => n >= 1e15 ? (n / 1e15).toFixed(1) + " P" : n >= 1e12 ? (n / 1e12).toFixed(1) + " T" : n >= 1e9 ? (n / 1e9).toFixed(1) + " G" : n >= 1e6 ? (n / 1e6).toFixed(1) + " M" : n >= 1e3 ? (n / 1e3).toFixed(1) + " K" : n.toFixed(n < 10 ? 1 : 0);
const LABS = {
  estimator(el){
    const b = el.querySelector(".labbody");
    const f = [["dau", "Daily active users", 100e6], ["reads", "Reads per user per day", 50], ["writes", "Writes per user per day", 2], ["size", "Size of one write (KB)", 1], ["resp", "Size of one read response (KB)", 10], ["years", "Retention (years)", 5], ["repl", "Replication factor", 3], ["perServer", "Requests/s one server handles", 2000]];
    b.innerHTML = `<div class="labform">${f.map(([k, l, v]) => `<label>${l}<input type="number" min="0" step="any" data-k="${k}" value="${v}"></label>`).join("")}</div><div class="labout" aria-live="polite"></div>`;
    const calc = () => {
      const v = {}; b.querySelectorAll("input").forEach(i => v[i.dataset.k] = Math.max(0, +i.value || 0));
      const rq = v.dau * v.reads / 86400, wq = v.dau * v.writes / 86400, st = v.dau * v.writes * v.size * 1e3 * 365 * v.years * v.repl;
      const bw = rq * v.resp * 1e3 * 8, srv = Math.ceil((rq + wq) * 3 / Math.max(1, v.perServer));
      b.querySelector(".labout").innerHTML = `<div class="labkpis">
        <div><b>${fmtN(rq)}</b>read QPS avg</div><div><b>${fmtN(rq * 3)}</b>read QPS peak (×3)</div><div><b>${fmtN(wq)}</b>write QPS avg</div><div><b>${fmtN(wq * 3)}</b>write QPS peak</div>
        <div><b>${fmtN(st)}B</b>storage over ${v.years} yrs (×${v.repl})</div><div><b>${fmtN(bw)}bps</b>read bandwidth</div><div><b>${srv}</b>servers at peak</div><div><b>${wq ? fmtN(rq / wq) : "∞"} : 1</b>read : write</div></div>
        <p class="labnote">${rq / Math.max(wq, 1e-9) >= 10 ? "Read-heavy: add caching, CDN and read replicas." : "Write-heavy: think about queues, batching, LSM-based stores and sharding."} Formula: QPS = users × actions ÷ 86,400; peak ≈ 3 × average.</p>`;
    };
    b.querySelectorAll("input").forEach(i => i.oninput = calc); calc();
  },
  ratelimit(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = `<div class="labctl"><label>Algorithm <select data-a><option value="tb">Token bucket (capacity 5, refill 1/s)</option><option value="fw">Fixed window (5 per 5 s)</option><option value="sl">Sliding log (5 per 5 s)</option></select></label>
      <button type="button" data-one>Send 1 request</button><button type="button" data-burst>Burst of 8</button><label class="chk"><input type="checkbox" data-auto> Random traffic</label><button type="button" data-reset>Reset</button></div>
      <div class="labstate" aria-live="polite"></div><svg class="labtl" viewBox="0 0 700 80" role="img" aria-label="Request timeline: accepted and rejected"></svg>
      <p class="labnote"><span class="lgd ok"></span> accepted · <span class="lgd no"></span> rejected (429). Timeline shows the last 20 seconds.</p>`;
    let t0 = performance.now(), algo = "tb", tokens = 5, last = 0, win = 0, cnt = 0, log = [], evts = [];
    const now = () => (performance.now() - t0) / 1000;
    const allow = t => {
      if (algo === "tb") { tokens = Math.min(5, tokens + (t - last) * 1); last = t; if (tokens >= 1) { tokens -= 1; return true; } return false; }
      if (algo === "fw") { const w = Math.floor(t / 5); if (w !== win) { win = w; cnt = 0; } if (cnt < 5) { cnt++; return true; } return false; }
      log = log.filter(x => t - x < 5); if (log.length < 5) { log.push(t); return true; } return false;
    };
    const send = () => { const t = now(); evts.push([t, allow(t)]); draw(); };
    const draw = () => {
      if (!el.isConnected) return;
      const t = now(); evts = evts.filter(e => t - e[0] < 20);
      const st = algo === "tb" ? `Tokens in bucket: <b>${Math.min(5, tokens + (t - last)).toFixed(1)}</b> / 5` : algo === "fw" ? `Window ${Math.floor(t / 5)}: <b>${Math.floor(t / 5) === win ? cnt : 0}</b> / 5 used · resets in ${(5 - t % 5).toFixed(1)} s` : `Requests in the last 5 s: <b>${log.filter(x => t - x < 5).length}</b> / 5`;
      const ok = evts.filter(e => e[1]).length;
      b.querySelector(".labstate").innerHTML = `${st} · accepted <b>${ok}</b>, rejected <b>${evts.length - ok}</b>`;
      let s = `<line x1="0" x2="700" y1="40" y2="40" class="labaxis"/>`;
      if (algo === "fw") for (let w = Math.ceil((t - 20) / 5) * 5; w <= t; w += 5) { const x = 700 - (t - w) * 35; s += `<line x1="${x}" x2="${x}" y1="8" y2="72" class="labwin"/>`; }
      evts.forEach(([et, a], i) => { const x = 700 - (t - et) * 35; s += `<circle cx="${x}" cy="${a ? 30 : 52}" r="5" class="${a ? "lok" : "lno"}"/>`; });
      s += `<text x="4" y="14" class="labtx">20 s ago</text><text x="696" y="14" text-anchor="end" class="labtx">now</text>`;
      b.querySelector(".labtl").innerHTML = s;
    };
    b.querySelector("[data-a]").onchange = e => { algo = e.target.value; b.querySelector("[data-reset]").click(); };
    b.querySelector("[data-one]").onclick = send;
    b.querySelector("[data-burst]").onclick = () => { for (let i = 0; i < 8; i++) send(); };
    b.querySelector("[data-reset]").onclick = () => { t0 = performance.now(); tokens = 5; last = 0; win = 0; cnt = 0; log = []; evts = []; draw(); };
    const tick = setInterval(() => { if (!el.isConnected) { clearInterval(tick); return; } if (b.querySelector("[data-auto]").checked && Math.random() < 0.35) send(); else draw(); }, 250);
    draw();
  },
  lb(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = `<div class="labctl"><label>Algorithm <select data-a><option value="rr">Round robin</option><option value="lc">Least connections</option><option value="rnd">Random</option><option value="p2">Power of two choices</option><option value="ip">IP hash (sticky)</option></select></label>
      <button type="button" data-send>Send 20 requests</button><label class="chk"><input type="checkbox" data-auto> Continuous traffic</label><button type="button" data-reset>Reset</button></div>
      <div class="labsrv" aria-live="polite"></div><p class="labnote">Server C is 3× slower. Requests take 1–6 s (long ones are like uploads/WebSockets). Watch how each algorithm piles work onto the slow server or not.</p>`;
    const names = ["A", "B", "C", "D"], speed = [1, 1, 3, 1];
    let srv, rr, algo = "rr", clients = 0;
    const reset = () => { srv = names.map(() => ({active: [], done: 0, total: 0})); rr = 0; draw(); };
    const pick = ip => {
      const L = i => srv[i].active.length;
      if (algo === "rr") return rr++ % 4;
      if (algo === "lc") return [0, 1, 2, 3].sort((x, y) => L(x) - L(y))[0];
      if (algo === "rnd") return Math.floor(Math.random() * 4);
      if (algo === "p2") { const a = Math.floor(Math.random() * 4), c = (a + 1 + Math.floor(Math.random() * 3)) % 4; return L(a) <= L(c) ? a : c; }
      return ip % 4;
    };
    const send = n => { const t = performance.now(); for (let k = 0; k < n; k++) { const ip = clients++ % 6, i = pick(ip), dur = (1 + Math.random() * 5) * speed[i] * 1000; srv[i].active.push(t + dur); srv[i].total++; } draw(); };
    const draw = () => {
      if (!el.isConnected) return;
      const t = performance.now();
      srv.forEach(s => { const before = s.active.length; s.active = s.active.filter(e => e > t); s.done += before - s.active.length; });
      const max = Math.max(8, ...srv.map(s => s.active.length));
      b.querySelector(".labsrv").innerHTML = srv.map((s, i) => `<div class="labsrow"><span class="labsn">Server ${names[i]}${speed[i] > 1 ? " (slow)" : ""}</span><div class="labbar"><i style="width:${s.active.length / max * 100}%"></i></div><span class="labsv"><b>${s.active.length}</b> active · ${s.total} total</span></div>`).join("");
    };
    b.querySelector("[data-a]").onchange = e => { algo = e.target.value; reset(); };
    b.querySelector("[data-send]").onclick = () => send(20);
    b.querySelector("[data-reset]").onclick = reset;
    const tick = setInterval(() => { if (!el.isConnected) { clearInterval(tick); return; } if (b.querySelector("[data-auto]").checked) send(2); else draw(); }, 400);
    reset();
  },
  cache(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = `<div class="labctl"><label>Policy <select data-p><option>LRU</option><option>LFU</option><option>FIFO</option></select></label><label>Capacity <input type="number" min="1" max="8" value="3" data-c></label>
      <label class="grow">Access sequence <input type="text" data-s value="A B C A D A B E A C B"></label><button type="button" data-step>Step</button><button type="button" data-run>Run all</button><button type="button" data-reset>Reset</button></div>
      <div class="labcache" aria-live="polite"></div>`;
    let i, cache, log, hits;
    const seq = () => b.querySelector("[data-s]").value.trim().split(/[\s,]+/).filter(Boolean);
    const reset = () => { i = 0; cache = []; log = []; hits = 0; draw(); };
    const step = () => {
      const s = seq(); if (i >= s.length) return;
      const k = s[i++], P = b.querySelector("[data-p]").value, cap = Math.max(1, +b.querySelector("[data-c]").value || 1), t = i;
      const e = cache.find(x => x.k === k);
      if (e) { hits++; e.last = t; e.freq++; log.push([k, "hit", ""]); }
      else {
        let ev = "";
        if (cache.length >= cap) {
          const victim = P === "LRU" ? cache.reduce((a, x) => x.last < a.last ? x : a) : P === "LFU" ? cache.reduce((a, x) => x.freq < a.freq || (x.freq === a.freq && x.last < a.last) ? x : a) : cache.reduce((a, x) => x.ins < a.ins ? x : a);
          cache = cache.filter(x => x !== victim); ev = victim.k;
        }
        cache.push({k, last: t, freq: 1, ins: t}); log.push([k, "miss", ev]);
      }
      draw();
    };
    const draw = () => {
      const s = seq(), P = b.querySelector("[data-p]").value;
      const order = P === "LRU" ? [...cache].sort((a, c) => c.last - a.last) : P === "LFU" ? [...cache].sort((a, c) => c.freq - a.freq || c.last - a.last) : [...cache].sort((a, c) => c.ins - a.ins);
      b.querySelector(".labcache").innerHTML = `<div class="labseq">${s.map((k, j) => `<span class="${j < i ? (log[j][1] === "hit" ? "h" : "m") : j === i ? "nx" : ""}">${esc(k)}</span>`).join("")}</div>
        <div class="labslots"><span class="labsl">Cache (${P === "LRU" ? "most recent first" : P === "LFU" ? "most used first" : "newest first"}):</span>${order.map(x => `<span class="slot">${esc(x.k)}${P === "LFU" ? `<small>×${x.freq}</small>` : ""}</span>`).join("") || "<em>empty</em>"}</div>
        <p>${log.length ? `Last access <b>${esc(log[log.length - 1][0])}</b>: ${log[log.length - 1][1] === "hit" ? "<b>hit</b>" : "<b>miss</b>" + (log[log.length - 1][2] ? `, evicted <b>${esc(log[log.length - 1][2])}</b>` : "")}. ` : ""}Hits <b>${hits}</b> / ${log.length} · hit ratio <b>${log.length ? Math.round(hits / log.length * 100) : 0}%</b></p>
        <p class="labnote"><span class="lgd ok"></span> hit · <span class="lgd no"></span> miss. Try the same sequence with each policy to compare.</p>`;
    };
    b.querySelector("[data-step]").onclick = step;
    b.querySelector("[data-run]").onclick = () => { reset(); seq().forEach(step); };
    b.querySelector("[data-reset]").onclick = reset;
    ["[data-p]", "[data-c]", "[data-s]"].forEach(q => b.querySelector(q).onchange = reset);
    reset();
  },
  ring(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = `<div class="labctl"><button type="button" data-add>Add server</button><button type="button" data-rm>Remove a server</button><label>Virtual nodes per server <input type="range" min="1" max="40" value="1" data-v><span data-vv>1</span></label></div>
      <div class="labring"><svg viewBox="0 0 320 320" role="img" aria-label="Consistent hashing ring"></svg><div class="labringinfo" aria-live="polite"></div></div>`;
    const H = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
      h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b); h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35); h ^= h >>> 16;   // murmur finaliser for even spread
      return (h >>> 0) / 4294967296; };
    const keys = Array.from({length: 60}, (_, i) => "user" + i);
    let servers = ["S1", "S2", "S3"], next = 4, vn = 1, prevOwner = null, prevMod = null;
    const ownerOf = (k, ring) => { const h = H(k); const e = ring.find(p => p.h >= h) || ring[0]; return e.s; };
    const draw = msg => {
      const ring = servers.flatMap(s => Array.from({length: vn}, (_, v) => ({s, h: H(s + "#" + v)}))).sort((a, c) => a.h - c.h);
      const owner = Object.fromEntries(keys.map(k => [k, ownerOf(k, ring)]));
      const mod = Object.fromEntries(keys.map(k => [k, servers[Math.floor(H(k) * 1e6) % servers.length]]));
      const col = s => "var(--lab" + ((+s.slice(1) - 1) % 6) + ")";
      const P = (h, r) => [160 + r * Math.sin(h * 2 * Math.PI), 160 - r * Math.cos(h * 2 * Math.PI)];
      let svg = `<circle cx="160" cy="160" r="120" class="labringc"/>`;
      keys.forEach(k => { const [x, y] = P(H(k), 132); svg += `<circle cx="${x}" cy="${y}" r="3.5" fill="${col(owner[k])}"/>`; });
      ring.forEach(p => { const [x, y] = P(p.h, 120); svg += `<rect x="${x - 5}" y="${y - 5}" width="10" height="10" rx="2" fill="${col(p.s)}" class="labvn"/>`; });
      servers.forEach(s => { const [x, y] = P(H(s + "#0"), 96); svg += `<text x="${x}" y="${y + 4}" text-anchor="middle" class="labtx b">${s}</text>`; });
      b.querySelector("svg").innerHTML = svg;
      const counts = servers.map(s => [s, keys.filter(k => owner[k] === s).length]);
      let moved = "";
      if (prevOwner && msg) { const m = keys.filter(k => prevOwner[k] !== owner[k]).length, mm = keys.filter(k => prevMod[k] !== mod[k]).length;
        moved = `<p class="labmoved">${esc(msg)}: <b>${m}</b> of 60 keys moved on the ring, vs <b>${mm}</b> with <code>hash % N</code>.</p>`; }
      prevOwner = owner; prevMod = mod;
      b.querySelector(".labringinfo").innerHTML = `${moved}<p>Keys per server (ideal ${(60 / servers.length).toFixed(0)}):</p>${counts.map(([s, n]) => `<div class="labsrow"><span class="labsn"><span class="lgd" style="background:${col(s)}"></span>${s}</span><div class="labbar"><i style="width:${n / 60 * 100}%;background:${col(s)}"></i></div><span class="labsv"><b>${n}</b></span></div>`).join("")}
        <p class="labnote">Squares are server positions (virtual nodes), dots are keys coloured by the server that owns them (next server clockwise). More virtual nodes → more even load.</p>`;
    };
    b.querySelector("[data-add]").onclick = () => { if (servers.length >= 6) return; const s = "S" + next++; servers.push(s); draw("Added " + s); };
    b.querySelector("[data-rm]").onclick = () => { if (servers.length <= 1) return; const s = servers.splice(Math.floor(servers.length / 2), 1)[0]; draw("Removed " + s); };
    b.querySelector("[data-v]").oninput = e => { vn = +e.target.value; b.querySelector("[data-vv]").textContent = vn; prevOwner = null; draw(); };
    draw();
  },
  quorum(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = `<div class="labctl"><label>N replicas <select data-n><option>3</option><option>5</option></select></label><label>W (write acks) <input type="number" min="1" value="2" data-w></label><label>R (read replicas) <input type="number" min="1" value="2" data-r></label>
      <button type="button" data-write>Write new value</button><button type="button" data-read>Read</button><button type="button" data-reset>Reset</button></div>
      <div class="labnodes" aria-live="polite"></div><div class="labqout" aria-live="polite"></div>`;
    let n = 3, nodes, ver, msg;
    const reset = () => { n = +b.querySelector("[data-n]").value; nodes = Array.from({length: n}, () => ({up: true, v: 1})); ver = 1; msg = "All replicas hold version 1. Click a replica to take it down or bring it back."; draw(); };
    const W = () => Math.min(n, Math.max(1, +b.querySelector("[data-w]").value || 1)), R = () => Math.min(n, Math.max(1, +b.querySelector("[data-r]").value || 1));
    const draw = () => {
      b.querySelector(".labnodes").innerHTML = nodes.map((x, i) => `<button type="button" class="labnode${x.up ? "" : " down"}" data-i="${i}" aria-pressed="${!x.up}">Replica ${i + 1}<b>v${x.v}</b><small>${x.up ? "up" : "down"}</small></button>`).join("");
      b.querySelectorAll(".labnode").forEach(bt => bt.onclick = () => { const x = nodes[+bt.dataset.i]; x.up = !x.up; msg = `Replica ${+bt.dataset.i + 1} is now ${x.up ? "up" : "down"}.`; draw(); });
      const strong = R() + W() > n;
      b.querySelector(".labqout").innerHTML = `<p class="labrule ${strong ? "ok" : "no"}">R + W = ${R() + W()} ${strong ? ">" : "≤"} N = ${n}: ${strong ? "every read overlaps the latest write (strong reads)." : "a read may miss the latest write (eventual consistency)."}</p><p>${msg}</p>`;
    };
    b.querySelector("[data-write]").onclick = () => {
      const live = nodes.map((x, i) => i).filter(i => nodes[i].up);
      if (live.length < W()) { msg = `<b>Write failed</b>: only ${live.length} replicas up but W = ${W()}. The system chooses consistency over availability.`; draw(); return; }
      ver++; live.slice(0, W()).forEach(i => nodes[i].v = ver);
      msg = `Wrote version <b>${ver}</b> to replicas ${live.slice(0, W()).map(i => i + 1).join(", ")} (the others are now stale).`; draw();
    };
    b.querySelector("[data-read]").onclick = () => {
      const live = nodes.map((x, i) => i).filter(i => nodes[i].up).reverse();   // read from the "other end" to show overlap
      if (live.length < R()) { msg = `<b>Read failed</b>: only ${live.length} replicas up but R = ${R()}.`; draw(); return; }
      const asked = live.slice(0, R()), got = Math.max(...asked.map(i => nodes[i].v));
      asked.forEach(i => nodes[i].v = got);   // read repair
      msg = `Asked replicas ${asked.map(i => i + 1).join(", ")} → newest is <b>v${got}</b> ${got === ver ? "✓ latest" : `✗ stale (latest is v${ver})`}. Stale replicas that answered were repaired.`; draw();
    };
    b.querySelector("[data-reset]").onclick = reset; b.querySelector("[data-n]").onchange = reset;
    ["[data-w]", "[data-r]"].forEach(q => b.querySelector(q).oninput = draw);
    reset();
  },
  fanout(el){
    const b = el.querySelector(".labbody");
    b.innerHTML = `<div class="labform"><label>Followers of a normal user<input type="number" min="0" value="300" data-k="nf"></label><label>Followers of a celebrity<input type="number" min="0" value="50000000" data-k="cf"></label>
      <label>Accounts a reader follows<input type="number" min="1" value="400" data-k="fol"></label><label>…of which celebrities<input type="number" min="0" value="20" data-k="cel"></label></div><div class="labout" aria-live="polite"></div>`;
    const calc = () => {
      const v = {}; b.querySelectorAll("input").forEach(i => v[i.dataset.k] = Math.max(0, +i.value || 0));
      const rows = [["Push (fan-out on write)", v.nf, v.cf, 1], ["Pull (fan-out on read)", 1, 1, v.fol], ["Hybrid (push normal, pull celebrities)", v.nf, 1, 1 + v.cel]];
      const max = Math.max(...rows.flatMap(r => [r[1], r[2], r[3]]), 1), bar = x => `<div class="labbar log"><i style="width:${Math.log10(x + 1) / Math.log10(max + 1) * 100}%"></i></div>`;
      b.querySelector(".labout").innerHTML = `<div class="tscroll"><table class="sdt"><thead><tr><th>Strategy</th><th>Writes when a normal user posts</th><th>Writes when a celebrity posts</th><th>Reads to load one feed</th></tr></thead><tbody>
        ${rows.map(r => `<tr><td><b>${r[0]}</b></td><td>${fmtN(r[1])}${bar(r[1])}</td><td>${fmtN(r[2])}${bar(r[2])}</td><td>${fmtN(r[3])}${bar(r[3])}</td></tr>`).join("")}</tbody></table></div>
        <p class="labnote">Bars use a log scale. Push makes reads cheap but one celebrity post costs ${fmtN(v.cf)} writes; pull makes every feed load query ${fmtN(v.fol)} timelines; hybrid keeps both small, which is why Twitter and Instagram use it.</p>`;
    };
    b.querySelectorAll("input").forEach(i => i.oninput = calc); calc();
  },
};
