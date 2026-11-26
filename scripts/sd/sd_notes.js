/* ================= My notes: notepad + bookmarks and notes on every topic ================= */
if (!state.tm) state.tm = {};     // topic bookmarks: id -> {at, title, kind}
if (!state.tn) state.tn = {};     // topic notes:     id -> {t, at, title, kind}
if (!state.pad) state.pad = [];   // free notes:      [{id, title, text, at, up}]
let NV = {q: "", kind: "All", confirm: null};
const TM_KINDS = {sd: "System Design concept", hld: "HLD question", lld: "LLD question", qa: "Interview Q&A", day: "DSA day lesson", pat: "DSA pattern", ml: "ML & AI concept", mlab: "ML lab", mlqa: "ML interview Q&A", mlpj: "ML project"};
const TM_ICON = on => `<svg viewBox="0 0 24 24" aria-hidden="true" class="tmico${on ? " on" : ""}"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4.5L5 21V4a1 1 0 0 1 1-1z"/></svg>`;
const NOTE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" class="tmico"><path d="M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4"/></svg>';
function tmKindOf(id){ const k = id.split(":")[0]; return k; }
/* compact actions for cards (icons) or full actions for sheets (with labels) */
function tmActs(id, title, kind, full){
  const on = !!state.tm[id], note = state.tn[id];
  return `<span class="tmacts${full ? " full" : ""}" data-tm="${esc(id)}" data-title="${esc(title)}" data-kind="${kind}">
    <button type="button" class="tmb" aria-pressed="${on}" aria-label="${on ? "Remove bookmark" : "Bookmark"}: ${esc(title)}" title="${on ? "Bookmarked" : "Bookmark to check later"}">${TM_ICON(on)}${full ? `<span>${on ? "Bookmarked" : "Bookmark"}</span>` : ""}</button>
    <button type="button" class="tmn${note ? " has" : ""}" aria-expanded="false" aria-label="${note ? "Edit note" : "Add note"}: ${esc(title)}" title="${note ? "Edit your note" : "Write a note"}">${NOTE_ICON}${full ? `<span>${note ? "Edit note" : "Add note"}</span>` : ""}</button></span>`;
}
function tmNoteArea(id){
  const n = state.tn[id];
  return `<div class="tmnote" data-tmnote="${esc(id)}"${n ? "" : " hidden"}>
    ${n ? `<p class="tmprev"><b>Your note</b> · ${new Date(n.at).toLocaleDateString("en-IN", {day: "2-digit", month: "short"})}</p>` : ""}
    <textarea rows="${n ? Math.min(8, Math.max(2, n.t.split("\n").length + 1)) : 3}" placeholder="Write anything to check later: doubts, key points, interview tips…" aria-label="Your note">${esc(n ? n.t : "")}</textarea>
    <span class="tmsaved" aria-live="polite"></span></div>`;
}
function tmToggle(id, title, kind){
  if (state.tm[id]) delete state.tm[id]; else state.tm[id] = {at: Date.now(), title, kind};
  save();
  document.querySelectorAll(`.tmacts[data-tm="${CSS.escape(id)}"] .tmb`).forEach(b => {
    const on = !!state.tm[id]; b.setAttribute("aria-pressed", on); b.innerHTML = TM_ICON(on) + (b.parentElement.classList.contains("full") ? `<span>${on ? "Bookmarked" : "Bookmark"}</span>` : "");
    b.title = on ? "Bookmarked" : "Bookmark to check later";
  });
  if (filter === 34) renderSDX();
}
let tmTimer;
function tmSave(id, text, title, kind, area){
  clearTimeout(tmTimer);
  tmTimer = setTimeout(() => {
    if (text.trim()) state.tn[id] = {t: text, at: Date.now(), title, kind}; else delete state.tn[id];
    save();
    const s = area.querySelector(".tmsaved"); if (s) { s.textContent = text.trim() ? "Saved" : "Note removed"; setTimeout(() => s.textContent = "", 1500); }
    document.querySelectorAll(`.tmacts[data-tm="${CSS.escape(id)}"] .tmn`).forEach(b => b.classList.toggle("has", !!state.tn[id]));
  }, 400);
}
document.addEventListener("click", e => {
  const b = e.target.closest(".tmb, .tmn"); if (!b) return;
  e.preventDefault(); e.stopPropagation();          // don't toggle the card / <details> it sits in
  const box = b.closest(".tmacts"), id = box.dataset.tm, title = box.dataset.title, kind = box.dataset.kind;
  if (b.classList.contains("tmb")) { tmToggle(id, title, kind); return; }
  const host = box.closest(".sdc, .sdq, .sheet, .tmhost") || document, anchor = box.closest("summary") || box;
  if (box.closest("summary")) box.closest("details").open = true;
  let area = host.querySelector(`.tmnote[data-tmnote="${CSS.escape(id)}"]`);
  if (!area) { anchor.insertAdjacentHTML("afterend", tmNoteArea(id)); area = anchor.nextElementSibling; }
  const open = area.hidden || b.getAttribute("aria-expanded") !== "true";
  area.hidden = !open && !state.tn[id]; b.setAttribute("aria-expanded", open);
  if (open) { area.hidden = false; area.querySelector("textarea").focus(); }
}, true);
document.addEventListener("input", e => {
  const ta = e.target; if (ta.tagName !== "TEXTAREA") return;
  const area = ta.closest(".tmnote");
  if (area) { const id = area.dataset.tmnote, box = document.querySelector(`.tmacts[data-tm="${CSS.escape(id)}"]`);
    const old = state.tn[id] || state.tm[id] || {};
    tmSave(id, ta.value, box ? box.dataset.title : old.title, box ? box.dataset.kind : old.kind, area); return; }
  const pad = ta.closest(".padnote");
  if (pad) { const n = state.pad.find(x => x.id === pad.dataset.pad); if (n) { n.text = ta.value; n.up = Date.now(); clearTimeout(tmTimer); tmTimer = setTimeout(() => { save(); const s = pad.querySelector(".tmsaved"); s.textContent = "Saved"; setTimeout(() => s.textContent = "", 1200); }, 400); } }
});
document.addEventListener("click", e => { if (e.target.closest("summary .tmacts")) e.preventDefault(); });

/* ---------- open a saved topic ---------- */
function tmGo(id){
  const [k, ...rest] = id.split(":"), key = rest.join(":");
  if (k === "day") { openSheet(+key); return; }
  if (k === "pat") { const i = PLAN.patterns.findIndex(p => p[0] === key); if (i >= 0) openPattern(i); return; }
  if (k === "mlqa") { filter = 54; SDV.q = ""; MLV.qaTopic = "All"; renderTabs(); renderBoard();
    requestAnimationFrame(() => { const el = document.getElementById("mqa-" + key); if (el) { el.open = true; el.scrollIntoView({block: "start"}); } }); return; }
  if (k === "qa") { filter = 31; SDV.q = ""; SDV.qaTopic = "All"; renderTabs(); renderBoard();
    requestAnimationFrame(() => { const el = document.getElementById("qa-" + key); if (el) { el.open = true; el.scrollIntoView({block: "start"}); } }); return; }
  sdGo(key);
}

/* ---------- the My notes page ---------- */
function renderNotes(root){
  const q = NV.q.trim().toLowerCase(), m = s => !q || (s || "").toLowerCase().includes(q);
  const pad = state.pad.filter(n => m(n.title) || m(n.text)).sort((a, b) => b.up - a.up);
  const ids = [...new Set([...Object.keys(state.tm), ...Object.keys(state.tn)])];
  const items = ids.map(id => { const a = state.tm[id], n = state.tn[id], meta = a || n; return {id, kind: meta.kind || tmKindOf(id), title: meta.title, marked: !!a, note: n && n.t, at: Math.max(a ? a.at : 0, n ? n.at : 0)}; })
    .filter(x => (NV.kind === "All" || x.kind === NV.kind || (NV.kind === "notes" && x.note) || (NV.kind === "marks" && x.marked)) && (m(x.title) || m(x.note)))
    .sort((a, b) => b.at - a.at);
  const probMarks = Object.keys(state.marks).length, probNotes = Object.keys(state.notes).length;
  const kinds = [["All", "Everything"], ["marks", "Bookmarked"], ["notes", "With notes"], ...Object.entries(TM_KINDS)];
  root.innerHTML = `<div class="eyebrow">Your space</div><h2>My notes &amp; bookmarks</h2>
    <p class="lead">Write anything to revisit later, and find every topic you bookmarked or annotated across DSA, System Design and ML &amp; AI. Tap ☆ to bookmark or ✎ to write a note on any topic card, day lesson, pattern, HLD/LLD question, ML lab or Q&amp;A. Select any text and tap <b>Highlight</b> to mark it.</p>
    <div class="sdbar"><label class="sdsearch"><span class="sr">Search notes</span><input type="search" id="nvQ" placeholder="Search your notes and bookmarks" value="${esc(NV.q)}"></label>
      <button type="button" class="sdtog" id="nvExport">Export backup</button><label class="sdtog nvimp">Import backup<input type="file" id="nvImport" accept="application/json" hidden></label></div>
    <section class="nvsec sybox" id="syncbox">${syPanel()}</section>
    <div class="nvstats"><span><b>${state.pad.length}</b> notepad notes</span><span><b>${Object.keys(state.tm).length}</b> bookmarked topics</span><span><b>${Object.keys(state.tn).length}</b> topic notes</span><span><b>${state.hl.length}</b> highlights</span>
      <button type="button" class="sdlink" id="nvProb">${probMarks} bookmarked · ${probNotes} commented DSA questions →</button></div>
    <section class="nvsec"><div class="trhead"><h3>Notepad</h3><button type="button" class="sdlabbtn" id="nvNew">+ New note</button></div>
      ${pad.length ? `<div class="padgrid">${pad.map(n => `<article class="padnote" data-pad="${n.id}">
        <input class="padtitle" value="${esc(n.title)}" placeholder="Title" aria-label="Note title">
        <textarea rows="${Math.min(14, Math.max(4, n.text.split("\n").length + 1))}" placeholder="Write here… saved automatically" aria-label="Note text">${esc(n.text)}</textarea>
        <div class="padfoot"><span>Edited ${new Date(n.up).toLocaleString("en-IN", {day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit"})}</span><span class="tmsaved" aria-live="polite"></span>
          <button type="button" class="paddel" data-del="${n.id}">${NV.confirm === n.id ? "Tap again to delete" : "Delete"}</button></div></article>`).join("")}</div>`
        : `<p class="qempty">${q ? "No notes match your search." : "No notes yet. Press <b>+ New note</b> to write your first one."}</p>`}</section>
    <section class="nvsec"><h3>Highlights <span class="nvcount">${state.hl.length}</span></h3>
      ${(() => { const hs = state.hl.filter(h => m(h.text) || m(h.title)).sort((a, b) => b.at - a.at);
        return hs.length ? `<ul class="nvlist">${hs.map(h => `<li class="nvitem"><div class="nvhead"><span class="nvkind">${esc(h.title)}</span><span class="nvdate">${new Date(h.at).toLocaleDateString("en-IN", {day: "2-digit", month: "short"})}</span></div>
          <p class="nvhl"><mark class="hl hl-${h.color}">${esc(h.text.length > 400 ? h.text.slice(0, 400) + "…" : h.text)}</mark></p>
          <div class="nvacts"><button type="button" class="sdlink" data-hlgo="${h.id}">Open where it is →</button><button type="button" class="sdlink" data-hlrm="${h.id}">Remove</button></div></li>`).join("")}</ul>`
          : `<p class="qempty">${q ? "No highlights match." : "No highlights yet. Select any text and tap <b>Highlight</b>."}</p>`; })()}</section>
    <section class="nvsec"><h3>Saved topics</h3>
      <div class="sdtopics" role="group" aria-label="Filter saved topics">${kinds.map(([k, l]) => `<button type="button" data-nk="${k}" aria-pressed="${NV.kind === k}">${esc(l)}</button>`).join("")}</div>
      ${items.length ? `<ul class="nvlist">${items.map(x => `<li class="nvitem">
          <div class="nvhead"><span class="nvkind">${esc(TM_KINDS[x.kind] || x.kind)}</span>${x.marked ? `<span class="nvmark">${TM_ICON(true)} bookmarked</span>` : ""}
            <span class="nvdate">${new Date(x.at).toLocaleDateString("en-IN", {day: "2-digit", month: "short"})}</span></div>
          <button type="button" class="nvopen" data-open="${esc(x.id)}">${esc(x.title)} →</button>
          ${x.note ? `<p class="nvnote">${esc(x.note).replace(/\n/g, "<br>")}</p>` : ""}
          <div class="nvacts">${x.marked ? `<button type="button" class="sdlink" data-unmark="${esc(x.id)}">Remove bookmark</button>` : ""}${x.note ? `<button type="button" class="sdlink" data-unnote="${esc(x.id)}">${NV.confirm === "n:" + x.id ? "Tap again to delete note" : "Delete note"}</button>` : ""}</div></li>`).join("")}</ul>`
        : `<p class="qempty">Nothing saved here yet. Tap ☆ or ✎ on any topic to collect it here.</p>`}</section>
    <p class="labnote">Notes and bookmarks are saved in this browser. Use <b>Export backup</b> to keep a copy or move them to another device, then <b>Import backup</b> there.</p>`;
  const nq = root.querySelector("#nvQ");
  nq.oninput = () => { NV.q = nq.value; const p = nq.selectionStart; renderSDX(); const n = document.getElementById("nvQ"); n.focus(); n.setSelectionRange(p, p); };
  root.querySelector("#nvNew").onclick = () => { const id = "n" + Date.now().toString(36); state.pad.push({id, title: "", text: "", at: Date.now(), up: Date.now()}); save(); NV.q = ""; renderSDX();
    const el = root.querySelector(`[data-pad="${id}"] .padtitle`); if (el) el.focus(); };
  root.querySelectorAll(".padtitle").forEach(i => i.oninput = () => { const n = state.pad.find(x => x.id === i.closest(".padnote").dataset.pad); n.title = i.value; n.up = Date.now(); save(); });
  root.querySelectorAll("[data-del]").forEach(b => b.onclick = () => { if (NV.confirm === b.dataset.del) { state.pad = state.pad.filter(x => x.id !== b.dataset.del); NV.confirm = null; save(); } else NV.confirm = b.dataset.del; renderSDX(); });
  root.querySelectorAll("[data-hlgo]").forEach(b => b.onclick = () => { const h = state.hl.find(x => x.id === b.dataset.hlgo); if (h) { hlGo(h);
    setTimeout(() => { const mk = document.querySelector(`mark[data-hl="${h.id}"]`); if (mk) { mk.scrollIntoView({block: "center"}); mk.classList.add("hlflash"); setTimeout(() => mk.classList.remove("hlflash"), 1600); } }, 350); } });
  root.querySelectorAll("[data-hlrm]").forEach(b => b.onclick = () => removeHighlight(b.dataset.hlrm));
  root.querySelectorAll("[data-nk]").forEach(b => b.onclick = () => { NV.kind = b.dataset.nk; renderSDX(); });
  root.querySelectorAll("[data-open]").forEach(b => b.onclick = () => tmGo(b.dataset.open));
  root.querySelectorAll("[data-unmark]").forEach(b => b.onclick = () => { delete state.tm[b.dataset.unmark]; save(); renderSDX(); });
  root.querySelectorAll("[data-unnote]").forEach(b => b.onclick = () => { const k = "n:" + b.dataset.unnote; if (NV.confirm === k) { delete state.tn[b.dataset.unnote]; NV.confirm = null; save(); } else NV.confirm = k; renderSDX(); });
  root.querySelector("#nvProb").onclick = () => { filter = 5; qFilter.marks = true; qFilter.notes = false; GROUP = "dsa"; renderTabs(); renderBoard(); };
  syWire();
  root.querySelector("#nvExport").onclick = async () => {
    const blob = new Blob([JSON.stringify({app: "dsa30", exported: new Date().toISOString(), state}, null, 1)], {type: "application/json"});
    const fname = "dsa-notes-backup-" + new Date().toISOString().slice(0, 10) + ".json";
    try { const dl = window.claude && claude.use ? await claude.use("downloads") : null;     // inside the Claude viewer
      if (dl) { await dl.save({filename: fname, data: blob}); return; } } catch (e) { if (e && e.code) return; }
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "dsa-notes-backup-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  };
  root.querySelector("#nvImport").onchange = e => {
    const f = e.target.files[0]; if (!f) return;
    f.text().then(t => { const d = JSON.parse(t), s = d.state || d;
      if (Array.isArray(s.hl)) { const have = new Set(state.hl.map(x => x.id)); state.hl.push(...s.hl.filter(x => !have.has(x.id))); }
      ["days", "probs", "marks", "notes", "tm", "tn"].forEach(k => { if (s[k]) state[k] = Object.assign({}, s[k], state[k] || {}); });   // merge, keep current on clash
      if (s.sd) ["c", "h", "l", "m"].forEach(k => state.sd[k] = Object.assign({}, s.sd[k] || {}, state.sd[k] || {}));
      if (s.mlpj) state.mlpj = Object.assign({}, s.mlpj, state.mlpj || {});
      if (s.mlcap) { state.mlcap.short = Object.assign({}, s.mlcap.short || {}, state.mlcap.short); if (!state.mlcap.pick) state.mlcap.pick = s.mlcap.pick || ""; }
      if (Array.isArray(s.pad)) { const have = new Set(state.pad.map(x => x.id)); state.pad.push(...s.pad.filter(x => !have.has(x.id))); }
      save(); renderTop(); renderSDX(); root.querySelector(".lead").insertAdjacentHTML("afterend", `<p class="labrule ok">Backup imported and merged.</p>`);
    }).catch(() => root.querySelector(".lead").insertAdjacentHTML("afterend", `<p class="labrule no">That file isn't a valid backup.</p>`));
  };
}
