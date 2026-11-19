/* ================= Select any text → "Explain" → answer right there ================= */
let EXP = {sample: null, ready: false, ctl: null, last: null};
(async () => {                                   // Claude is available only inside the Claude artifact viewer
  try { if (window.claude && claude.use) { EXP.sample = await claude.use("sample"); } } catch (e) { EXP.sample = null; }
  EXP.ready = true;
})();
const expBtn = document.createElement("button");
expBtn.type = "button"; expBtn.className = "expbtn"; expBtn.hidden = true;
expBtn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a6 6 0 0 0-3.6 10.8c.4.3.6.8.6 1.2v1h6v-1c0-.4.2-.9.6-1.2A6 6 0 0 0 12 3zM9 19h6M10 22h4"/></svg>Explain';
const expPop = document.createElement("div");
expPop.className = "exppop"; expPop.hidden = true; expPop.setAttribute("role", "dialog"); expPop.setAttribute("aria-label", "Explanation");
document.body.append(expBtn, expPop);

function expSelection(){
  const sel = window.getSelection(); if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
  const text = sel.toString().replace(/\s+/g, " ").trim();
  if (text.length < 2 || text.length > 400) return null;
  const range = sel.getRangeAt(0), node = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentElement;
  if (!node || node.closest("input, textarea, .exppop, .expbtn, nav, .groups")) return null;
  if (!node.closest(".wrap, #sheet, #viz")) return null;
  const rects = range.getClientRects(), r = rects.length ? rects[rects.length - 1] : range.getBoundingClientRect();
  const block = node.closest("li, p, td, .sayit, .sdq, .sdcb, .sdch, .note, .pcard, .snip, .appc, section, .sheet") || node;
  const card = node.closest(".sdc, .sdq, .sheet, .note, .lab, .sdstage");
  const title = card ? (card.querySelector(".sdct b, .sdqq, h2, h3, b") || {}).textContent || "" : "";
  return {text, rect: r, context: (block.textContent || "").replace(/\s+/g, " ").trim().slice(0, 1500), title: title.trim().slice(0, 200)};
}
function placeBtn(s){
  const x = Math.min(window.scrollX + s.rect.right - 10, window.scrollX + document.documentElement.clientWidth - 110);
  const touch = matchMedia("(pointer: coarse)").matches;
  const y = window.scrollY + (touch ? s.rect.bottom + 34 : s.rect.bottom + 8);   // below the native touch menu
  expBtn.style.left = Math.max(window.scrollX + 8, x) + "px"; expBtn.style.top = y + "px"; expBtn.hidden = false;
}
let expTimer;
document.addEventListener("selectionchange", () => {
  clearTimeout(expTimer);
  expTimer = setTimeout(() => { const s = expSelection(); if (s) { EXP.last = s; placeBtn(s); } else if (!expBtn.matches(":focus")) expBtn.hidden = true; }, 250);
});
expBtn.addEventListener("mousedown", e => e.preventDefault());       // keep the selection
expBtn.addEventListener("click", () => { const s = EXP.last || expSelection(); expBtn.hidden = true; if (s) explain(s); });
document.addEventListener("keydown", e => { if (e.key === "Escape" && !expPop.hidden) closeExp(); });
document.addEventListener("mousedown", e => { if (!expPop.hidden && !expPop.contains(e.target) && !expBtn.contains(e.target)) closeExp(); });
function closeExp(){ if (EXP.ctl) EXP.ctl.abort(); expPop.hidden = true; }

/* answers from the site itself (works everywhere, also offline) */
function localExplain(t){
  const q = t.toLowerCase().replace(/[^\w\s+/.#-]/g, " ").replace(/\s+/g, " ").trim(), out = [];
  const key = t.replace(/[^\w]/g, "");
  if (typeof ABBR !== "undefined") { const k = ABBR[key] ? key : ABBR[key.replace(/s$/, "")] ? key.replace(/s$/, "") : null; if (k) out.push({kind: "Short form", title: k + " = " + ABBR[k], body: ""}); }
  const words = q.split(" ").filter(w => w.length > 2);
  const score = s => { const L = (s || "").toLowerCase(); if (!L) return 0; if (L.includes(q)) return 10 + q.length / 10; return words.filter(w => L.includes(w)).length / Math.max(1, words.length) * 5; };
  const cands = [];
  Object.values(SDX.concepts).forEach(c => { const sc = Math.max(score(c.title) * 1.5, score(c.what)); if (sc >= 4) cands.push({sc, kind: "System Design concept", title: c.title, body: c.what, go: c.id}); });
  SDX.qa.forEach(x => { const sc = score(x.q); if (sc >= 4.5) cands.push({sc: sc - 0.5, kind: "Interview Q&A", title: x.q, body: x.a}); });
  PLAN.patterns.forEach(([n, sig]) => { const sc = score(n) * 1.5; if (sc >= 4) cands.push({sc, kind: "DSA pattern", title: n, body: sig, pat: n}); });
  cands.sort((a, b) => b.sc - a.sc);
  const top = cands.slice(0, 3);
  if (top.length < 3 && q.length >= 3) {                 // fall back to the sentence that mentions it inside a topic
    const strip = x => x.replace(/```[\s\S]*?```/g, " ").replace(/[*`#|]/g, " ").replace(/\s+/g, " ");
    for (const c of Object.values(SDX.concepts)) {
      if (top.length >= 3) break; if (top.some(x => x.go === c.id)) continue;
      const body = strip(c.body), i = body.toLowerCase().indexOf(q);
      if (i < 0) continue;
      const st = Math.max(body.lastIndexOf(". ", i) + 2, 0), en = body.indexOf(". ", i + q.length);
      top.push({kind: "Mentioned in " + c.title, title: body.slice(st, en < 0 ? undefined : en + 1).replace(/^[-\d.\s]+/, "").replace(/\s+:/g, ":").trim().slice(0, 280), body: "", go: c.id});
    }
  }
  return out.concat(top);
}
function expShell(s, inner){
  return `<div class="exphead"><b>“${esc(s.text.length > 80 ? s.text.slice(0, 80) + "…" : s.text)}”</b><button type="button" class="expx" aria-label="Close">×</button></div>${inner}
    <div class="expfoot"><button type="button" class="sdtog" data-exp="save">Save to notes</button>
      <a class="sdtog" target="_blank" rel="noopener" href="https://claude.ai/new?q=${encodeURIComponent(expPrompt(s, true))}">Ask Claude ↗</a></div>`;
}
function expPrompt(s, short){
  const head = `Explain "${s.text}" simply for someone preparing for software engineering interviews (DSA in Java and system design).`;
  if (short) return head + (s.title ? ` Context: ${s.title}.` : "");
  return head + `
Give: 1) a one-sentence plain-English meaning, 2) a short real-world example or analogy, 3) if relevant, how to mention it in an interview (one line). Expand any abbreviation as "Full form (ABBR)". Plain text, under 140 words, no headings, use short paragraphs or "- " bullets.
Topic on the page: ${s.title || "(none)"}
Surrounding text: ${s.context}`;
}
function positionPop(s){
  const w = Math.min(420, document.documentElement.clientWidth - 24);
  expPop.style.width = w + "px";
  let left = window.scrollX + Math.min(Math.max(12, s.rect.left), document.documentElement.clientWidth - w - 12);
  expPop.style.left = left + "px"; expPop.style.top = (window.scrollY + s.rect.bottom + 10) + "px";
}
async function explain(s){
  positionPop(s); expPop.hidden = false;
  requestAnimationFrame(() => { const r = expPop.getBoundingClientRect(); if (r.top > innerHeight - 160) window.scrollBy({top: r.top - innerHeight + 220, behavior: "smooth"}); });
  const local = localExplain(s.text);
  const localHTML = local.length ? `<div class="explocal">${local.map(x => `<div class="expitem"><span class="nvkind">${esc(x.kind)}</span><b>${esc(x.title)}</b>${x.body ? `<p>${esc(x.body.length > 260 ? x.body.slice(0, 260) + "…" : x.body)}</p>` : ""}${x.go ? `<button type="button" class="sdlink" data-exp-go="${x.go}">Open full topic →</button>` : x.pat ? `<button type="button" class="sdlink" data-exp-pat="${esc(x.pat)}">Open pattern →</button>` : ""}</div>`).join("")}</div>` : "";
  if (!EXP.ready) await new Promise(r => { const t = setInterval(() => { if (EXP.ready) { clearInterval(t); r(); } }, 100); setTimeout(() => { clearInterval(t); r(); }, 3000); });
  if (EXP.sample) {
    expPop.innerHTML = expShell(s, `<div class="expans" aria-live="polite"><span class="expthink">Thinking…</span></div><button type="button" class="sdlink expstop">Stop</button>${localHTML ? `<details class="expmore"><summary>Related on this site</summary>${localHTML}</details>` : ""}`);
    wireExp(s);
    EXP.ctl = new AbortController();
    const box = expPop.querySelector(".expans"), stop = expPop.querySelector(".expstop");
    stop.onclick = () => EXP.ctl.abort();
    try {
      const {text} = await EXP.sample(expPrompt(s), {modelTier: "quick", signal: EXP.ctl.signal, onText: ({text}) => { box.innerHTML = md(text); }});
      box.innerHTML = md(text); s.answer = text;
    } catch (e) {
      if (e.text) box.innerHTML = md(e.text);
      const msg = {not_granted: "Claude isn't allowed for this page, so here is what the site itself says.", sampling_disabled: "Claude isn't available on this account.", rate_limited: "Too many questions at once — try again in a moment.", cancelled: ""}[e.code];
      if (e.code === "not_granted" || e.code === "sampling_disabled") EXP.sample = null;
      if (!e.text) box.innerHTML = (msg !== undefined ? (msg ? `<p class="expnote">${msg}</p>` : "") : `<p class="expnote">Couldn't get an answer right now.</p>`) + (localHTML || "");
    }
    if (stop.isConnected) stop.remove();
  } else {
    expPop.innerHTML = expShell(s, localHTML || `<p class="expnote">This isn't covered on the site yet. Tap <b>Ask Claude ↗</b> for a full explanation.</p>`);
    s.answer = local.map(x => x.title + (x.body ? ": " + x.body : "")).join("\n\n");
    wireExp(s);
  }
}
function wireExp(s){
  expPop.querySelector(".expx").onclick = closeExp;
  expPop.querySelectorAll("[data-exp-go]").forEach(b => b.onclick = () => { closeExp(); sdGo(b.dataset.expGo); });
  expPop.querySelectorAll("[data-exp-pat]").forEach(b => b.onclick = () => { closeExp(); const i = PLAN.patterns.findIndex(p => p[0] === b.dataset.expPat); if (i >= 0) openPattern(i); });
  const sv = expPop.querySelector('[data-exp="save"]');
  sv.onclick = () => {
    const ans = (expPop.querySelector(".expans") || {}).innerText || s.answer || "";
    state.pad.push({id: "n" + Date.now().toString(36), title: "Explain: " + s.text.slice(0, 80), text: (s.title ? "From: " + s.title + "\n\n" : "") + ans.trim(), at: Date.now(), up: Date.now()});
    save(); sv.textContent = "Saved to My notes ✓"; sv.disabled = true;
  };
}
