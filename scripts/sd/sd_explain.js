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
const selTool = document.createElement("div");
selTool.className = "seltool"; selTool.hidden = true; selTool.setAttribute("role", "toolbar"); selTool.setAttribute("aria-label", "Selected text");
selTool.innerHTML = `<span class="hlgroup"><button type="button" class="hlbtn" data-hc="y" aria-label="Highlight yellow"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 11l-5 5v4h4l5-5M14 6l4 4M9 11l5-5 4 4-5 5z"/></svg>Highlight</button><button type="button" class="hldot y" data-hc="y" aria-label="Highlight yellow"></button><button type="button" class="hldot g" data-hc="g" aria-label="Highlight green"></button><button type="button" class="hldot p" data-hc="p" aria-label="Highlight pink"></button></span><button type="button" class="hlrmbtn" hidden aria-label="Remove highlight from the selected text"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h16M7 16l-3-3 9-9 6 6-7 7H9z"/></svg>Remove highlight</button>`;
selTool.prepend(expBtn); expBtn.hidden = false;
document.body.append(selTool, expPop);

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
  const marked = typeof selectedHighlightIds === "function" ? selectedHighlightIds() : [];
  selTool.querySelector(".hlrmbtn").hidden = !marked.length;
  selTool.style.left = Math.max(window.scrollX + 8, Math.min(x - 120, window.scrollX + document.documentElement.clientWidth - 330)) + "px"; selTool.style.top = y + "px"; selTool.hidden = false;
}
let expTimer;
document.addEventListener("selectionchange", () => {
  clearTimeout(expTimer);
  expTimer = setTimeout(() => { const s = expSelection(); if (s) { EXP.last = s; placeBtn(s); } else if (!selTool.contains(document.activeElement)) selTool.hidden = true; }, 250);
});
selTool.addEventListener("mousedown", e => e.preventDefault());      // keep the selection
expBtn.addEventListener("click", () => { const s = EXP.last || expSelection(); selTool.hidden = true; if (s) explain(s); });
selTool.querySelector(".hlrmbtn").addEventListener("click", () => { selTool.hidden = true; removeSelectedHighlights(); });
selTool.querySelectorAll("[data-hc]").forEach(b => b.addEventListener("click", () => { selTool.hidden = true; addHighlight(b.dataset.hc); }));
document.addEventListener("keydown", e => { if (e.key === "Escape" && !expPop.hidden) closeExp(); });
document.addEventListener("mousedown", e => { if (!expPop.hidden && !expPop.contains(e.target) && !selTool.contains(e.target)) closeExp(); });
function closeExp(){ if (EXP.ctl) EXP.ctl.abort(); expPop.hidden = true; }

/* ---------- relevance search over the site's own notes (works everywhere, offline) ---------- */
const EXP_STOP = new Set("the a an and or of to in on for with by is are was be as at it its this that from into than then so if not no can you your we our they their them how what why when which who use used using also more most very just only each per vs via e.g like such about over under between both all any some other one two three".split(" "));
const expStem = w => w.replace(/(ings|ing|ied|ies|es|ed|s)$/, m => m === "ies" || m === "ied" ? "y" : "").replace(/(.)\1$/, "$1");
const expTok = t => (t.toLowerCase().match(/[a-z0-9+#]+/g) || []).filter(w => w.length > 2 && !EXP_STOP.has(w)).map(expStem);
let EXP_IDX = null;
function expIndex(){
  if (EXP_IDX) return EXP_IDX;
  const docs = [], strip = x => (x || "").replace(/```[\s\S]*?```/g, " ").replace(/[*`#|]/g, " ");
  const add = (d, parts) => { const tf = {}; parts.forEach(([txt, w]) => expTok(strip(txt)).forEach(t => tf[t] = (tf[t] || 0) + w)); d.tf = tf; docs.push(d); };
  Object.values(SDX.concepts).forEach(c => add({kind: "System Design concept", title: c.title, what: c.what, body: strip(c.body), go: c.id,
    say: (c.say || [])[0]}, [[c.title, 6], [c.what, 3], [c.body, 1], [(c.say || []).map(x => x.p + " " + x.a).join(" "), 1]]));
  SDX.qa.forEach(x => add({kind: "Interview Q&A", title: x.q, what: x.a, body: x.a}, [[x.q, 4], [x.a, 1.5]]));
  PLAN.patterns.forEach(([n, sig]) => { const P = PLAN.playbook[n] || {}; add({kind: "DSA pattern", title: n, what: sig, body: strip(JSON.stringify(P)), pat: n}, [[n, 6], [sig, 3], [JSON.stringify(P), 0.5]]); });
  if (typeof MLX !== "undefined") {
    Object.values(MLX.concepts).forEach(c => add({kind: "ML & AI concept", title: c.title, what: c.what, body: strip(c.body), go: c.id,
      say: (c.say || [])[0]}, [[c.title, 6], [c.what, 3], [c.body, 1], [(c.say || []).map(x => x.p + " " + x.a).join(" "), 1]]));
    MLX.qa.forEach(x => add({kind: "ML interview Q&A", title: x.q, what: x.a, body: x.a}, [[x.q, 4], [x.a, 1.5]]));
  }
  SDX.hld.forEach(h => add({kind: "HLD question", title: h.title, what: "Tests " + h.tests, body: strip(h.deep.join(" ") + " " + h.flow.join(" ")), go: h.id}, [[h.title, 4], [h.tests, 2], [h.deep.join(" "), 0.7]]));
  const df = {}; docs.forEach(d => Object.keys(d.tf).forEach(t => df[t] = (df[t] || 0) + 1));
  const N = docs.length, idf = t => Math.log(1 + N / (df[t] || 0.5));
  EXP_IDX = {docs, idf};
  return EXP_IDX;
}
function expSearch(q, ctx){
  const {docs, idf} = expIndex();
  const qt = {}; expTok(q).forEach(t => qt[t] = (qt[t] || 0) + 1);
  if (Object.keys(qt).length < 2 && ctx) expTok(ctx).forEach(t => qt[t] = (qt[t] || 0) + 0.25);   // very short selection: lean on its sentence
  const scored = docs.map(d => { let s = 0; for (const t in qt) if (d.tf[t]) s += qt[t] * idf(t) * Math.log(1 + d.tf[t]); return [s, d]; })
    .filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]);
  return scored;
}
function bestSentences(body, q, n){
  const qt = new Set(expTok(q)), sents = body.replace(/\s+/g, " ").split(/(?<=[.!?])\s+(?=[A-Z0-9*(“"])|\s-\s/).map(x => x.trim()).filter(x => x.length > 25 && x.length < 400);
  return sents.map(x => [expTok(x).filter(t => qt.has(t)).length, x]).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, n).map(x => x[1].replace(/^[-\d.\s]+/, "").replace(/\s+([:;,.])/g, "$1"));
}
/* answers from the site itself (works everywhere, also offline) */
function localExplain(t, ctx){
  const out = [], key = t.replace(/[^\w]/g, "");
  if (typeof ABBR !== "undefined") { const k = ABBR[key] ? key : ABBR[key.replace(/s$/, "")] ? key.replace(/s$/, "") : null; if (k) out.push({kind: "Short form", title: k + " = " + ABBR[k], body: ""}); }
  const res = expSearch(t, ctx);
  if (!res.length) return out;
  const top = res[0][0], picks = res.filter(([sc]) => sc >= top * 0.55).slice(0, 3).map(x => x[1]);
  picks.forEach((d, i) => {
    const sents = i === 0 ? bestSentences(d.body, t + " " + (ctx || "").slice(0, 200), 2) : [];
    out.push({kind: (i === 0 ? "Best match · " : "Related · ") + d.kind, title: d.title, body: d.what, extra: sents, go: d.go, pat: d.pat, say: i === 0 ? d.say : null});
  });
  return out;
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
  const local = localExplain(s.text, s.context);
  const localHTML = local.length ? `<div class="explocal">${local.map(x => `<div class="expitem"><span class="nvkind">${esc(x.kind)}</span><b>${esc(x.title)}</b>${x.body ? `<p class="expwhat">${mdInline(x.body.length > 420 ? x.body.slice(0, 420) + "…" : x.body)}</p>` : ""}${x.extra && x.extra.length ? `<ul class="expsent">${x.extra.map(e => `<li>${mdInline(e)}</li>`).join("")}</ul>` : ""}${x.say ? `<p class="expsay"><span class="sayw">In the interview</span>${mdInline(x.say.a.replace(/^"|"$/g, "").slice(0, 360))}${x.say.a.length > 360 ? "…" : ""}</p>` : ""}${x.go ? `<button type="button" class="sdlink" data-exp-go="${x.go}">Open full topic →</button>` : x.pat ? `<button type="button" class="sdlink" data-exp-pat="${esc(x.pat)}">Open pattern →</button>` : ""}</div>`).join("")}</div>` : "";
  if (!EXP.ready) await new Promise(r => { const t = setInterval(() => { if (EXP.ready) { clearInterval(t); r(); } }, 100); setTimeout(() => { clearInterval(t); r(); }, 3000); });
  const apiKey = (() => { try { return localStorage.getItem("dsa30-anthropic-key") || ""; } catch (e) { return ""; } })();
  if (!EXP.sample && apiKey) EXP.sample = apiSample(apiKey);
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
      const msg = {not_granted: "Claude isn't allowed for this page, so here is what the site itself says.", sampling_disabled: "Claude isn't available on this account.", rate_limited: "Too many questions at once — try again in a moment.", cancelled: "", bad_key: "That API key was rejected, so it has been removed. Here is what the site says."}[e.code];
      if (e.code === "bad_key") { try { localStorage.removeItem("dsa30-anthropic-key"); } catch (er) {} EXP.sample = null; }
      if (e.code === "not_granted" || e.code === "sampling_disabled") EXP.sample = null;
      if (!e.text) box.innerHTML = (msg !== undefined ? (msg ? `<p class="expnote">${msg}</p>` : "") : `<p class="expnote">Couldn't get an answer right now.</p>`) + (localHTML || "");
    }
    if (stop.isConnected) stop.remove();
  } else {
    expPop.innerHTML = expShell(s, (localHTML || `<p class="expnote">Nothing on the site matches this yet.</p>`) +
      `<details class="expkey"><summary>Want Claude's full answer right here? Add your Anthropic API key</summary>
        <p class="expnote">Paste a key from console.anthropic.com. It is stored only in this browser and sent only to Anthropic. API use is billed to your Anthropic account (a few paise per explanation). The Claude copy of this site needs no key.</p>
        <div class="expkeyrow"><input type="password" class="expkeyin" placeholder="sk-ant-…" autocomplete="off" aria-label="Anthropic API key"><button type="button" class="sdtog expkeysave">Save &amp; explain</button></div></details>`);
    s.answer = local.map(x => x.title + (x.body ? ": " + x.body : "")).join("\n\n");
    wireExp(s);
  }
}
function apiSample(key){
  // Calls the Anthropic Messages API straight from this browser with the viewer's own key (streams the answer).
  return async (prompt, opt = {}) => {
    const r = await fetch("https://api.anthropic.com/v1/messages", {method: "POST", signal: opt.signal,
      headers: {"content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01", "anthropic-dangerous-direct-browser-access": "true"},
      body: JSON.stringify({model: "claude-haiku-5-5", max_tokens: 500, stream: true, messages: [{role: "user", content: prompt}]})})
      .catch(e => { throw {code: e.name === "AbortError" ? "cancelled" : "upstream_error", message: String(e)}; });
    if (!r.ok) { const t = await r.text().catch(() => ""); throw {code: r.status === 401 ? "bad_key" : r.status === 429 ? "rate_limited" : "upstream_error", message: t.slice(0, 300)}; }
    const rd = r.body.getReader(), dec = new TextDecoder(); let buf = "", text = "";
    try {
      for (;;) { const {done, value} = await rd.read(); if (done) break; buf += dec.decode(value, {stream: true});
        let i; while ((i = buf.indexOf("\n")) >= 0) { const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
          if (!line.startsWith("data:")) continue; let ev; try { ev = JSON.parse(line.slice(5)); } catch (e) { continue; }
          if (ev.type === "content_block_delta" && ev.delta && ev.delta.text) { text += ev.delta.text; opt.onText && opt.onText({text, delta: ev.delta.text}); }
          if (ev.type === "error") throw {code: "upstream_error", message: ev.error && ev.error.message, text}; } }
    } catch (e) { if (e && e.code) throw e; throw {code: opt.signal && opt.signal.aborted ? "cancelled" : "upstream_error", message: String(e), text}; }
    if (!text) throw {code: "empty_completion", message: "no text"};
    return {text, truncated: false};
  };
}
function wireExp(s){
  expPop.querySelector(".expx").onclick = closeExp;
  expPop.querySelectorAll("[data-exp-go]").forEach(b => b.onclick = () => { closeExp(); sdGo(b.dataset.expGo); });
  expPop.querySelectorAll("[data-exp-pat]").forEach(b => b.onclick = () => { closeExp(); const i = PLAN.patterns.findIndex(p => p[0] === b.dataset.expPat); if (i >= 0) openPattern(i); });
  const ks = expPop.querySelector(".expkeysave");
  if (ks) ks.onclick = () => { const v = expPop.querySelector(".expkeyin").value.trim(); if (!/^sk-ant-/.test(v)) { expPop.querySelector(".expkeyin").setCustomValidity("Keys start with sk-ant-"); expPop.querySelector(".expkeyin").reportValidity(); return; }
    try { localStorage.setItem("dsa30-anthropic-key", v); } catch (e) {} EXP.sample = apiSample(v); explain(s); };
  const sv = expPop.querySelector('[data-exp="save"]');
  sv.onclick = () => {
    const ans = (expPop.querySelector(".expans") || {}).innerText || s.answer || "";
    state.pad.push({id: "n" + Date.now().toString(36), title: "Explain: " + s.text.slice(0, 80), text: (s.title ? "From: " + s.title + "\n\n" : "") + ans.trim(), at: Date.now(), up: Date.now()});
    save(); sv.textContent = "Saved to My notes ✓"; sv.disabled = true;
  };
}
