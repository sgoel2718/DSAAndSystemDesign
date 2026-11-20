/* ================= Highlights: mark text for future reference; re-applied whenever the topic is shown ================= */
if (!Array.isArray(state.hl)) state.hl = [];      // [{id, key, title, text, color, at}]
const HL_SKIP = "svg, textarea, input, select, script, style, .tmacts, .seltool, .exppop, .codebar";
/* where a piece of text lives: a stable key for the card / question / lesson it belongs to */
function hlUnitOf(node){
  const el = node.nodeType === 1 ? node : node.parentElement;
  const sheet = el.closest("#sheet");
  if (sheet) { const h = sheet.querySelector("#sheetTitle"), eb = sheet.querySelector(".eyebrow");
    const m = eb && /Day (\d+)/.exec(eb.textContent); return {unit: sheet, key: m ? "day:" + m[1] : "pat:" + (h ? h.textContent : ""), title: (m ? "Day " + m[1] + ": " : "Pattern: ") + (h ? h.textContent : "")}; }
  const card = el.closest(".sdc[id], .sdq[id]");
  if (card) { const t = card.querySelector(".sdct b, .sdqq"); return {unit: card, key: card.id, title: t ? t.firstChild.textContent || t.textContent : card.id}; }
  const other = el.closest(".sdstage, .lab[id], .nvsec, section[id], main[id]");
  if (other) { const t = other.querySelector("h2, h3"); return {unit: other, key: "sec:" + (other.id || (t && t.textContent) || ""), title: t ? t.textContent : "Section"}; }
  return null;
}
function hlTextMap(unit){
  const map = [], walker = document.createTreeWalker(unit, NodeFilter.SHOW_TEXT, {acceptNode: n => n.parentElement && n.parentElement.closest(HL_SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT});
  let norm = "", n, lastSpace = true;
  while ((n = walker.nextNode())) {
    const v = n.nodeValue;
    for (let i = 0; i < v.length; i++) {
      const ws = /\s/.test(v[i]);
      if (ws) { if (lastSpace) continue; norm += " "; map.push([n, i]); lastSpace = true; }
      else { norm += v[i]; map.push([n, i]); lastSpace = false; }
    }
  }
  return {norm, map};
}
const hlNorm = t => t.replace(/\s+/g, " ").trim();
function hlWrap(unit, h){
  if (unit.querySelector(`mark[data-hl="${h.id}"]`)) return true;
  const {norm, map} = hlTextMap(unit), q = hlNorm(h.text), at = norm.indexOf(q);
  if (at < 0 || !q) return false;
  const pieces = [];                                       // group consecutive chars by text node
  for (let i = at; i < at + q.length; i++) { const [node, off] = map[i]; const last = pieces[pieces.length - 1];
    if (last && last.node === node) last.end = off + 1; else pieces.push({node, start: off, end: off + 1}); }
  pieces.reverse().forEach(({node, start, end}) => {
    const r = document.createRange(); r.setStart(node, start); r.setEnd(node, end);
    const m = document.createElement("mark"); m.className = "hl hl-" + h.color; m.dataset.hl = h.id; m.title = "Highlighted · click to remove";
    try { r.surroundContents(m); } catch (e) {}
  });
  return true;
}
function applyHighlights(root){
  if (!state.hl.length) return;
  const units = new Map();
  (root.querySelectorAll ? [root, ...root.querySelectorAll(".sdc[id], .sdq[id]")] : []).forEach(el => {
    const u = el.matches && (el.matches(".sdc[id], .sdq[id]") || el.id === "sheet") ? hlUnitOf(el) : null; if (u) units.set(u.key, u.unit); });
  const sheet = document.getElementById("sheet"); if (sheet && !sheet.hidden && root.contains && (root === sheet || sheet.contains(root) || root.contains(sheet))) { const u = hlUnitOf(sheet); if (u) units.set(u.key, u.unit); }
  state.hl.forEach(h => { const u = units.get(h.key) || (h.key.startsWith("sdc-") || h.key.startsWith("qa-") || h.key.startsWith("mqa-") ? document.getElementById(h.key) : null);
    if (u && root.contains && (root.contains(u) || u.contains(root))) hlWrap(u, h); });
}
function addHighlight(color){
  const sel = getSelection(); if (!sel || sel.isCollapsed) return;
  const range = sel.getRangeAt(0), u = hlUnitOf(range.commonAncestorContainer);
  const text = hlNorm(sel.toString());
  if (!u || text.length < 2) return;
  const h = {id: "h" + Date.now().toString(36), key: u.key, title: hlNorm(u.title).slice(0, 160), text: text.slice(0, 1500), color, at: Date.now()};
  if (!hlWrap(u.unit, h)) return;
  state.hl.push(h); save(); sel.removeAllRanges();
  if (filter === 34) renderSDX();
}
/* click a highlight: small menu to remove or explain */
const hlMenu = document.createElement("div"); hlMenu.className = "hlmenu"; hlMenu.hidden = true;
hlMenu.innerHTML = `<button type="button" data-hlact="explain">Explain</button><button type="button" data-hlact="remove">Remove highlight</button>`;
document.body.append(hlMenu);
let hlCur = null;
document.addEventListener("click", e => {
  const m = e.target.closest && e.target.closest("mark[data-hl]");
  if (m && getSelection().isCollapsed) { hlCur = m.dataset.hl; const r = m.getBoundingClientRect();
    hlMenu.style.left = (window.scrollX + Math.max(8, Math.min(r.left, document.documentElement.clientWidth - 220))) + "px"; hlMenu.style.top = (window.scrollY + r.bottom + 6) + "px"; hlMenu.hidden = false; e.stopPropagation(); return; }
  if (!hlMenu.contains(e.target)) hlMenu.hidden = true;
}, true);
hlMenu.addEventListener("click", e => {
  const b = e.target.closest("[data-hlact]"); if (!b || !hlCur) return;
  const h = state.hl.find(x => x.id === hlCur); hlMenu.hidden = true;
  if (b.dataset.hlact === "remove") { removeHighlight(hlCur); return; }
  const m = document.querySelector(`mark[data-hl="${hlCur}"]`); if (!m || !h) return;
  const r = m.getBoundingClientRect(); const unit = hlUnitOf(m);
  explain({text: h.text.slice(0, 400), rect: r, context: (m.closest("li, p, td, .sayit") || m.parentElement).textContent.slice(0, 1500), title: unit ? unit.title : ""});
});
function removeHighlight(id){
  document.querySelectorAll(`mark[data-hl="${id}"]`).forEach(m => { const p = m.parentNode; while (m.firstChild) p.insertBefore(m.firstChild, m); p.removeChild(m); p.normalize(); });
  state.hl = state.hl.filter(x => x.id !== id); save(); if (filter === 34) renderSDX();
}
function hlGo(h){
  const k = h.key;
  if (k.startsWith("sdc-")) sdGo(k.slice(4));
  else if (k.startsWith("qa-")) tmGo("qa:" + k.slice(3));
  else if (k.startsWith("mqa-")) tmGo("mlqa:" + k.slice(4));
  else if (k.startsWith("day:") || k.startsWith("pat:")) tmGo(k);
}
const hlObs = new MutationObserver(ms => { if (!state.hl.length) return; clearTimeout(hlObs.t); hlObs.t = setTimeout(() => {
  const roots = new Set(); ms.forEach(m => { if (m.target && m.target.nodeType === 1) roots.add(m.target); });
  roots.forEach(r => { if (r.isConnected && !r.closest(".seltool, .exppop, .hlmenu")) applyHighlights(r); }); }, 30); });
function startHighlights(){ applyHighlights(document.body); hlObs.observe(document.body, {childList: true, subtree: true}); }

/* highlights touched by the current selection (or containing it) */
function selectedHighlightIds(){
  const sel = getSelection(); if (!sel || !sel.rangeCount) return [];
  const r = sel.getRangeAt(0), ids = new Set();
  const inMark = n => { const e = n.nodeType === 1 ? n : n.parentElement; const m = e && e.closest("mark[data-hl]"); if (m) ids.add(m.dataset.hl); };
  inMark(r.startContainer); inMark(r.endContainer);
  const root = r.commonAncestorContainer.nodeType === 1 ? r.commonAncestorContainer : r.commonAncestorContainer.parentElement;
  if (root) root.querySelectorAll("mark[data-hl]").forEach(m => { if (r.intersectsNode(m)) ids.add(m.dataset.hl); });
  return [...ids];
}
function removeSelectedHighlights(){ selectedHighlightIds().forEach(removeHighlight); getSelection().removeAllRanges(); }
