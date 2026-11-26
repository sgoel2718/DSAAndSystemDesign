/* ================= Select text → "Ask Claude" → a separate chat for every section ================= */
if (!state.chats || typeof state.chats !== "object") state.chats = {};   // key -> {title, at, msgs: [{id, r: "u"|"a", t, q, at}]}  (synced across devices)
const ASK = {key: null, unit: null, quote: "", ctl: null, busy: false};
const askBtn = document.createElement("button");
askBtn.type = "button"; askBtn.className = "expbtn askbtn";
askBtn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg>Ask Claude';
expBtn.after(askBtn);
const askPane = document.createElement("aside");
askPane.className = "askpane"; askPane.hidden = true; askPane.setAttribute("role", "dialog"); askPane.setAttribute("aria-label", "Ask Claude about this section");
document.body.append(askPane);

function askUnitFromSelection(){
  const sel = getSelection(); if (!sel || !sel.rangeCount || sel.isCollapsed) return null;
  const text = sel.toString().replace(/\s+/g, " ").trim(); if (text.length < 2) return null;
  const node = sel.getRangeAt(0).startContainer;
  let u = hlUnitOf(node);
  if (!u) { const tab = document.querySelector(".tabs [aria-pressed='true'], .tabs .on"); const t = (tab && tab.textContent.trim()) || "This page";
    u = {unit: document.getElementById("sdx") && !document.getElementById("sdx").hidden ? document.getElementById("sdx") : document.querySelector(".wrap"), key: "page:" + GROUP + ":" + filter, title: t}; }
  return {key: u.key, title: hlNorm(u.title || "").slice(0, 160) || "This section", unit: u.unit, quote: text.slice(0, 2000)};
}
askBtn.addEventListener("click", () => { const s = askUnitFromSelection(); selTool.hidden = true; if (s) openAsk(s.key, s.title, s.unit, s.quote); });

function askChat(key, title){ return state.chats[key] || (state.chats[key] = {title, at: Date.now(), msgs: []}); }
function openAsk(key, title, unit, quote){
  ASK.key = key; ASK.unit = unit || null; ASK.quote = quote || "";
  const c = state.chats[key]; if (c && title && !c.title) c.title = title;
  ASK.title = (c && c.title) || title || "This section";
  askPane.hidden = false; document.body.classList.add("asking"); renderAsk();
  const ta = askPane.querySelector(".askin"); if (ta) ta.focus();
}
function closeAsk(){ if (ASK.ctl) ASK.ctl.abort(); askPane.hidden = true; document.body.classList.remove("asking"); }
function askMsgHTML(m){
  return `<div class="askmsg ${m.r === "u" ? "me" : "ai"}">${m.q ? `<blockquote class="askq">${esc(m.q.length > 300 ? m.q.slice(0, 300) + "…" : m.q)}</blockquote>` : ""}<div class="sdmd">${m.r === "u" ? esc(m.t).replace(/\n/g, "<br>") : md(m.t)}</div></div>`;
}
function renderAsk(){
  const c = state.chats[ASK.key], msgs = c ? c.msgs : [], others = Object.entries(state.chats).filter(([k, v]) => k !== ASK.key && v.msgs && v.msgs.length).sort((a, b) => b[1].at - a[1].at);
  askPane.innerHTML = `<div class="askhead"><div><div class="eyebrow">Ask Claude · separate chat for this section</div><b class="asktitle">${esc(ASK.title)}</b></div>
      <button type="button" class="askx" aria-label="Close">✕</button></div>
    <div class="asktools">${others.length ? `<select class="askswitch" aria-label="Open another section's chat"><option value="">Your other chats (${others.length})…</option>${others.map(([k, v]) => `<option value="${esc(k)}">${esc(v.title || k)} · ${v.msgs.length} msgs</option>`).join("")}</select>` : "<span></span>"}
      ${msgs.length ? `<button type="button" class="sdlink askclear">Clear this chat</button>` : ""}</div>
    <div class="asklog" aria-live="polite">${msgs.length ? msgs.map(askMsgHTML).join("") + (!ASK.busy && msgs[msgs.length - 1].r === "u" ? `<button type="button" class="sdlabbtn askretry">Get Claude's answer</button>` : "") : `<p class="expnote">Ask anything about <b>${esc(ASK.title)}</b>. Claude sees this section's content and the text you selected. This chat is saved for this section and syncs to your other devices.</p>`}</div>
    ${ASK.quote ? `<div class="askquote"><span>About:</span> “${esc(ASK.quote.length > 220 ? ASK.quote.slice(0, 220) + "…" : ASK.quote)}”<button type="button" class="askqx" aria-label="Remove quoted text">✕</button></div>` : ""}
    <div class="askrow"><textarea class="askin" rows="2" placeholder="${ASK.quote ? "What do you want to know about the selected text?" : "Ask a question about this section…"}" aria-label="Your question"></textarea>
      <button type="button" class="sdlabbtn asksend">${ASK.busy ? "Stop" : "Send"}</button></div>
    <div class="askkey"></div>`;
  const log = askPane.querySelector(".asklog"); log.scrollTop = log.scrollHeight;
  askPane.querySelector(".askx").onclick = closeAsk;
  const sw = askPane.querySelector(".askswitch"); if (sw) sw.onchange = () => { if (sw.value) openAsk(sw.value, state.chats[sw.value].title, askFindUnit(sw.value), ""); };
  const cl = askPane.querySelector(".askclear"); if (cl) cl.onclick = () => { if (cl.dataset.sure) { delete state.chats[ASK.key]; save(); renderAsk(); if (filter === 34) renderSDX(); } else { cl.dataset.sure = 1; cl.textContent = "Click again to delete this chat"; } };
  const qx = askPane.querySelector(".askqx"); if (qx) qx.onclick = () => { ASK.quote = ""; renderAsk(); };
  const ta = askPane.querySelector(".askin"), send = askPane.querySelector(".asksend");
  const go = () => askSend(ta.value).catch(err => { ASK.busy = false; renderAsk(); askNotice(`<p class="expnote">Something went wrong: ${esc(String(err && (err.message || err.code) || err))}</p>`); });
  send.onclick = () => { if (ASK.busy) { if (ASK.ctl) ASK.ctl.abort(); return; } go(); };
  ta.onkeydown = e => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); if (!ASK.busy) go(); } };
  const rt = askPane.querySelector(".askretry"); if (rt) rt.onclick = () => askReply();
}
function askFindUnit(key){
  if (key.startsWith("sdc-") || key.startsWith("qa-") || key.startsWith("mqa-")) return document.getElementById(key);
  return null;
}
function askContext(){
  let txt = "";
  const u = ASK.unit && ASK.unit.isConnected ? ASK.unit : askFindUnit(ASK.key);
  if (u) txt = (u.innerText || u.textContent || "").replace(/\n{3,}/g, "\n\n").trim();
  return txt.length > 14000 ? txt.slice(0, 14000) + "\n…(section continues)" : txt;
}
async function askGetSampler(){
  // inside Claude, claude.use("sample") can take a few seconds to answer; wait up to 12 s
  if (!EXP.ready) await new Promise(r => { const t = setInterval(() => { if (EXP.ready) { clearInterval(t); r(); } }, 100); setTimeout(() => { clearInterval(t); r(); }, 12000); });
  if (EXP.sample) return EXP.sample;
  const k = (() => { try { return localStorage.getItem("dsa30-anthropic-key") || ""; } catch (e) { return ""; } })();
  return k ? (EXP.sample = apiSample(k)) : null;
}
function askNotice(html){
  const log = askPane.querySelector(".asklog"); if (!log) return null;
  log.querySelectorAll(".asknote").forEach(n => n.remove());
  log.insertAdjacentHTML("beforeend", `<div class="askmsg ai asknote">${html}</div>`); log.scrollTop = log.scrollHeight;
  return log.lastElementChild;
}
function askKeyForm(){
  const inClaude = !!(window.claude && claude.use);
  const box = askNotice(`<p class="expnote"><b>${inClaude ? "Claude isn't connected in this view yet." : "This copy of the board isn't running inside Claude."}</b> ${inClaude ? "Reload the page and press Send again; if Claude asks for permission to answer, allow it." : "Open the board inside the Claude app to ask with your Claude account, or paste your own Anthropic API key here (stored only in this browser, sent only to Anthropic, billed to your account):"}</p>
    ${inClaude ? "" : `<div class="expkeyrow"><input type="password" class="expkeyin" placeholder="sk-ant-…" autocomplete="off" aria-label="Anthropic API key"><button type="button" class="sdtog askkeysave">Save &amp; get answer</button></div>`}
    <p class="expnote">Your question is saved in this chat; press <b>Get Claude's answer</b> any time.</p>`);
  const sv = box && box.querySelector(".askkeysave");
  if (sv) sv.onclick = () => { const v = box.querySelector(".expkeyin").value.trim(); if (!/^sk-ant-/.test(v)) { box.querySelector(".expkeyin").setCustomValidity("Keys start with sk-ant-"); box.querySelector(".expkeyin").reportValidity(); return; }
    try { localStorage.setItem("dsa30-anthropic-key", v); } catch (e) {} EXP.sample = apiSample(v); askReply(); };
}
async function askSend(text){
  text = (text || "").trim(); if (!text || ASK.busy) return;
  const c = askChat(ASK.key, ASK.title);
  c.msgs.push({id: "m" + Date.now().toString(36) + Math.random().toString(36).slice(2, 5), r: "u", t: text, q: ASK.quote || "", at: Date.now()}); c.at = Date.now();
  ASK.quote = ""; save();
  await askReply();
}
async function askReply(){
  if (ASK.busy) return;
  const c = state.chats[ASK.key]; if (!c || !c.msgs.length) return;
  ASK.busy = true; renderAsk();                                        // shows your message right away, Send becomes Stop
  let log = askPane.querySelector(".asklog");
  log.insertAdjacentHTML("beforeend", `<div class="askmsg ai"><div class="sdmd askstream"><span class="expthink">Connecting to Claude…</span></div></div>`);
  let out = log.querySelector(".askstream"); log.scrollTop = log.scrollHeight;
  let sample = null; try { sample = await askGetSampler(); } catch (e) {}
  if (!sample) { ASK.busy = false; renderAsk(); askKeyForm(); return; }
  const context = askContext();
  const intro = `You are a patient tutor helping a software engineer prepare for DSA, system design and ML interviews. They are studying this section of their study board:\n\nSECTION: ${ASK.title}\n` +
    (context ? `\nSECTION CONTENT (for reference):\n"""\n${context}\n"""\n` : "") +
    `\nAnswer their questions clearly and concisely, using the section's own examples where useful. Use short paragraphs, bullet points, tables or small code snippets (Java) when they help. If they quote text, focus on that text (it may come from a diagram). If something in the section looks wrong, say so.\n\n`;
  const recent = c.msgs.slice(-20); while (recent.length && recent[0].r !== "u") recent.shift();
  while (recent.length && recent[recent.length - 1].r !== "u") recent.pop();
  const history = recent.map((m, i) => ({role: m.r === "u" ? "user" : "assistant",
    content: (i === 0 ? intro : "") + (m.q ? `About this text: "${m.q}"\n\n` : "") + (m.t || "…")}));
  const ai = {id: "m" + Date.now().toString(36) + "a", r: "a", t: "", at: Date.now()};
  const t0 = Date.now(); let started = false;
  const tick = setInterval(() => { if (!started && out.isConnected) out.innerHTML = `<span class="expthink">Thinking… ${Math.round((Date.now() - t0) / 1000)} s</span> <span class="expnote">(the first time, Claude may ask you to allow it; answers can take up to a minute to start)</span>`; }, 1000);
  ASK.ctl = new AbortController();
  try {
    const r = await sample(history, {signal: ASK.ctl.signal, cache: false, maxTokens: 1500, onText: ({text}) => { started = true; if (out.isConnected) { out.innerHTML = md(text); log.scrollTop = log.scrollHeight; } }});
    ai.t = r.text;
  } catch (e) {
    ai.t = (e && e.text) || "";
    const code = e && e.code;
    const msg = {not_granted: "Claude wasn't allowed to answer on this page. Reload and allow it when asked.", sampling_disabled: "Claude isn't available on this account.", rate_limited: "Too many questions at once, or your usage limit was reached. Try again in a moment.", session_expired: "Please sign in to Claude again.", prompt_too_large: "This section is too long to send. Select a smaller part and ask again.", cancelled: "", bad_key: "That API key was rejected, so it has been removed."}[code];
    if (code === "bad_key") { try { localStorage.removeItem("dsa30-anthropic-key"); } catch (er) {} EXP.sample = null; }
    if (code === "not_granted" || code === "sampling_disabled") EXP.sample = null;
    if (msg === undefined) ai.t += (ai.t ? "\n\n" : "") + "*Couldn't get an answer right now" + (code ? " (" + code + ")" : "") + ".*"; else if (msg) ai.t += (ai.t ? "\n\n" : "") + "*" + msg + "*";
    else if (ai.t) ai.t += "\n\n*(stopped)*";
  }
  clearInterval(tick);
  ASK.busy = false; ASK.ctl = null;
  if (ai.t) { askChat(ASK.key, ASK.title).msgs.push(ai); save(); }
  if (!askPane.hidden) renderAsk();
  if (filter === 34 && typeof renderSDX === "function" && askPane.hidden) renderSDX();
}
function askListHTML(){
  const list = Object.entries(state.chats).filter(([, v]) => v.msgs && v.msgs.length).sort((a, b) => b[1].at - a[1].at);
  return `<section class="nvsec"><div class="trhead"><h3>Your Claude chats</h3></div>${list.length ? `<ul class="asklist">${list.map(([k, v]) => {
    const last = v.msgs.filter(m => m.r === "u").slice(-1)[0];
    return `<li><button type="button" class="sdlink" data-askopen="${esc(k)}">${esc(v.title || k)}</button> <span class="vxnote2">${v.msgs.length} messages · ${new Date(v.at).toLocaleDateString("en-IN", {day: "2-digit", month: "short"})}${last ? " · “" + esc(last.t.slice(0, 80)) + "”" : ""}</span></li>`; }).join("")}</ul>`
    : `<p class="expnote">Select any text on a topic, lesson or question and tap <b>Ask Claude</b>. Each section gets its own chat, kept here and synced to your other devices.</p>`}</section>`;
}
document.addEventListener("click", e => { const b = e.target.closest && e.target.closest("[data-askopen]"); if (!b) return; const k = b.dataset.askopen, c = state.chats[k]; if (c) openAsk(k, c.title, askFindUnit(k), ""); });
document.addEventListener("keydown", e => { if (e.key === "Escape" && !askPane.hidden && askPane.contains(document.activeElement) && !ASK.busy) closeAsk(); });
