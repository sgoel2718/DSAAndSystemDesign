/* ---------- Cross-device sync of bookmarks, notes, highlights, comments and progress ----------
   Two backends, both optional, both merged on every page load:
   1. Claude account (only inside the Claude viewer): a private per-user document via the `db` capability.
   2. GitHub: a JSON file in a private repo you own, via a fine-grained token you paste once per device.
   State is flattened into leaf paths, each with a last-modified time (deletes keep a tombstone), and every
   merge keeps the newer value per path, so edits made on different devices combine instead of overwriting. */
const SYK = "dsa30-sync-meta-v1", GHK = "dsa30-ghsync-v1", SEP = "\u001f";
const SY = {meta: {}, prev: {}, ready: false, timer: 0, writing: null, claude: {on: false, state: "off", at: 0, err: ""}, gh: {state: "off", at: 0, err: ""}};
let GH = {repo: "", token: "", path: "board-sync.json", sha: ""};
try { SY.meta = JSON.parse(localStorage.getItem(SYK)) || {}; } catch (e) {}
try { GH = Object.assign(GH, JSON.parse(localStorage.getItem(GHK)) || {}); } catch (e) {}
const syMetaSave = () => { try { localStorage.setItem(SYK, JSON.stringify(SY.meta)); } catch (e) {} };
const ghSave = () => { try { localStorage.setItem(GHK, JSON.stringify(GH)); } catch (e) {} };

function syIsIdArr(a){ return Array.isArray(a) && a.every(x => x && typeof x === "object" && !Array.isArray(x) && "id" in x); }
function syFlat(obj, pre = "", out = {}){
  if (syIsIdArr(obj)) { obj.forEach(x => { out[pre + SEP + "#" + x.id] = JSON.stringify(x); }); return out; }
  for (const [k, v] of Object.entries(obj)) {
    const p = pre ? pre + SEP + k : k;
    if (v && typeof v === "object" && (!Array.isArray(v) || syIsIdArr(v))) syFlat(v, p, out);
    else if (v !== undefined) out[p] = JSON.stringify(v);
  }
  return out;
}
function sySet(path, json){
  const parts = path.split(SEP); let o = state;
  for (let i = 0; i < parts.length - 1; i++) {
    const k = parts[i], next = parts[i + 1];
    if (Array.isArray(o)) { const id = k.slice(1); let it = o.find(x => String(x.id) === id); if (!it) return; o = it; continue; }
    if (o[k] === null || typeof o[k] !== "object") o[k] = next.startsWith("#") ? [] : {};
    o = o[k];
  }
  const last = parts[parts.length - 1], v = JSON.parse(json);
  if (Array.isArray(o) && last.startsWith("#")) { const i = o.findIndex(x => String(x.id) === last.slice(1)); if (i >= 0) o[i] = v; else o.push(v); }
  else if (!Array.isArray(o)) o[last] = v;
}
function syDel(path){
  const parts = path.split(SEP); let o = state;
  for (let i = 0; i < parts.length - 1; i++) {
    const k = parts[i];
    o = Array.isArray(o) ? o.find(x => String(x.id) === k.slice(1)) : o[k];
    if (!o || typeof o !== "object") return;
  }
  const last = parts[parts.length - 1];
  if (Array.isArray(o)) { const i = o.findIndex(x => String(x.id) === last.slice(1)); if (i >= 0) o.splice(i, 1); }
  else delete o[last];
}
// record which paths changed since the last look (called after every save)
function syDiff(){
  const cur = syFlat(state), now = Date.now(); let changed = false;
  for (const [p, v] of Object.entries(cur)) if (SY.prev[p] !== v) { SY.meta[p] = now; changed = true; }
  for (const p of Object.keys(SY.prev)) if (!(p in cur)) { SY.meta[p] = -now; changed = true; }
  SY.prev = cur;
  if (changed) syMetaSave();
  return changed;
}
function syPayload(){
  const e = {}, cur = SY.prev, cutoff = Date.now() - 90 * 864e5;
  for (const [p, t] of Object.entries(SY.meta)) {
    if (t < 0) { if (-t > cutoff) e[p] = [t]; else delete SY.meta[p]; }      // tombstones older than 90 days are dropped
    else if (p in cur) e[p] = [t, cur[p]];
  }
  for (const [p, v] of Object.entries(cur)) if (!(p in e)) e[p] = [SY.meta[p] || 0, v];
  return {v: 1, at: Date.now(), e};
}
// merge a remote payload into local state; returns {changed, localNewer}
function syMerge(remote){
  if (!remote || !remote.e) return {changed: false, localNewer: true};
  syDiff();
  const cur = SY.prev, dels = [], sets = []; let localNewer = false;
  const keys = new Set([...Object.keys(remote.e), ...Object.keys(SY.meta), ...Object.keys(cur)]);
  for (const p of keys) {
    const r = remote.e[p], lt = Math.abs(SY.meta[p] || 0), lAlive = p in cur;
    if (!r) { if (lAlive || SY.meta[p]) localNewer = true; continue; }
    const rt = Math.abs(r[0]), rAlive = r.length > 1;
    if (rt > lt || (rt === lt && rAlive && lAlive && r[1] > cur[p])) {
      if (rAlive && cur[p] !== r[1]) sets.push([p, r[1]]);
      if (!rAlive && lAlive) dels.push(p);
      SY.meta[p] = rAlive ? rt : -rt;
    } else if (lt > rt || (lAlive && rAlive && cur[p] !== r[1])) localNewer = true;
  }
  dels.sort((a, b) => b.length - a.length).forEach(syDel);
  sets.sort((a, b) => a[0].length - b[0].length).forEach(([p, v]) => sySet(p, v));
  const changed = dels.length + sets.length > 0;
  if (changed) { SY.prev = syFlat(state); try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} syRerender(); }
  syMetaSave();
  return {changed, localNewer};
}
function syRerender(){
  const a = document.activeElement;
  if (a && /^(TEXTAREA|INPUT)$/.test(a.tagName) && a.type !== "checkbox") { a.addEventListener("blur", syRerender, {once: true}); return; }   // never wipe what you're typing
  try { renderTop(); renderTabs(); renderBoard(); if (!askPane.hidden && !ASK.busy) renderAsk(); } catch (e) {}
}

/* ---- backend 1: Claude account (private per-user documents, live across devices) ---- */
const CHUNK = 180000;
async function syClaudeInit(){
  if (!(window.claude && claude.use)) { SY.claude.state = "na"; syStatus(); return; }
  SY.claude.state = "connecting"; syStatus();
  let db, user, uid;
  try { [db, user] = await Promise.all([claude.use("db"), claude.use("user")]); uid = user && await user.id(); } catch (e) {}
  if (!db || !uid) { SY.claude.state = "na"; syStatus(); return; }
  SY.claude.db = db; SY.claude.base = "data/users/" + uid; SY.claude.on = true;
  const man = db.doc(SY.claude.base + "/sync");
  let first = true;
  const timer = setTimeout(() => { if (first) { SY.claude.state = "error"; SY.claude.err = "Claude storage isn't answering yet; your changes are kept on this device and will sync when it does."; syStatus(); } }, 10000);
  man.onSnapshot(async snap => {
    if (snap.metadata && snap.metadata.fromCache && !first) return;
    const d = snap.exists ? snap.data() : null;
    if (d && d.rev === SY.claude.rev) { if (first) { first = false; clearTimeout(timer); } return; }   // our own write echoing back
    try {
      let res = {changed: false, localNewer: true};
      if (d) {
        const parts = await Promise.all(Array.from({length: d.n || 0}, (_, i) => db.doc(SY.claude.base + "/sync_p" + i).get()));
        const text = parts.map(s => (s.exists && s.data().s) || "").join("");
        if (text) res = syMerge(JSON.parse(text));
        SY.claude.rev = d.rev;
      }
      if (first) { first = false; clearTimeout(timer); }
      SY.claude.state = "ok"; SY.claude.err = ""; SY.claude.at = Date.now(); syStatus();
      if (res.localNewer) syClaudePush();
    } catch (e) { SY.claude.state = "error"; SY.claude.err = (e && e.message) || "Couldn't read your synced data."; syStatus(); }
  }, e => { SY.claude.state = "error"; SY.claude.err = e && e.code === "revoked" ? "Sync isn't available in this view." : "Claude sync stopped (" + ((e && e.code) || "error") + "). Reload to retry."; syStatus(); });
}
async function syClaudePush(){
  if (!SY.claude.on) return;
  if (SY.claude.busy) { SY.claude.again = true; return; }
  SY.claude.busy = true;
  try {
    const text = JSON.stringify(syPayload()), n = Math.max(1, Math.ceil(text.length / CHUNK)), rev = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    for (let i = 0; i < n; i++) await SY.claude.db.doc(SY.claude.base + "/sync_p" + i).set({s: text.slice(i * CHUNK, (i + 1) * CHUNK)});   // one write at a time
    SY.claude.rev = rev;
    await SY.claude.db.doc(SY.claude.base + "/sync").set({rev, n, at: Date.now()});
    SY.claude.state = "ok"; SY.claude.err = ""; SY.claude.at = Date.now();
  } catch (e) {
    SY.claude.state = "error";
    SY.claude.err = e && e.code === "quota_exceeded" ? "Your Claude sync storage is full. Export a backup and delete old highlights or notes." : "Couldn't save to your Claude account (" + ((e && e.code) || "error") + "). It will retry on your next change.";
  }
  SY.claude.busy = false; syStatus();
  if (SY.claude.again) { SY.claude.again = false; syClaudePush(); }
}

/* ---- backend 2: GitHub (a JSON file in your private repo) ---- */
const b64enc = s => { const b = new TextEncoder().encode(s); let bin = ""; for (let i = 0; i < b.length; i += 8192) bin += String.fromCharCode.apply(null, b.subarray(i, i + 8192)); return btoa(bin); };
const b64dec = s => new TextDecoder().decode(Uint8Array.from(atob(s.replace(/\s/g, "")), c => c.charCodeAt(0)));
function ghApi(method, body){
  const url = `https://api.github.com/repos/${GH.repo}/contents/${GH.path.split("/").map(encodeURIComponent).join("/")}`;
  return fetch(url + (method === "GET" ? "?t=" + Date.now() : ""), {method, cache: "no-store",
    headers: {Accept: "application/vnd.github+json", Authorization: "Bearer " + GH.token, "X-GitHub-Api-Version": "2022-11-28", ...(body ? {"Content-Type": "application/json"} : {})},
    body: body ? JSON.stringify(body) : undefined});
}
function ghErr(r){
  if (r.status === 401) return "GitHub rejected the token (expired or wrong). Paste a new one.";
  if (r.status === 403) return "The token can't access that repo. Give it Contents: Read and write on " + GH.repo + ".";
  if (r.status === 404) return "Repo " + GH.repo + " not found, or the token has no access to it.";
  return "GitHub said " + r.status + ".";
}
async function syGhPull(){
  if (!GH.repo || !GH.token) { SY.gh.state = "off"; syStatus(); return; }
  if (SY.gh.busy) return;
  SY.gh.busy = true; SY.gh.state = SY.gh.at ? SY.gh.state : "connecting"; syStatus();
  try {
    const r = await ghApi("GET");
    let res = {changed: false, localNewer: true};
    if (r.status === 404) {
      const repo = await fetch(`https://api.github.com/repos/${GH.repo}`, {headers: {Authorization: "Bearer " + GH.token}});
      if (!repo.ok) throw new Error(ghErr(repo));
      GH.sha = "";                                                    // repo exists, file doesn't yet: the first push creates it
    } else if (!r.ok) throw new Error(ghErr(r));
    else { const j = await r.json(); GH.sha = j.sha; res = syMerge(JSON.parse(b64dec(j.content || "") || "{}")); }
    ghSave(); SY.gh.state = "ok"; SY.gh.err = ""; SY.gh.at = Date.now(); SY.gh.busy = false; syStatus();
    if (res.localNewer) await syGhPush();
  } catch (e) { SY.gh.busy = false; SY.gh.state = "error"; SY.gh.err = /fetch/i.test(e.message) ? "Couldn't reach GitHub from this page (offline, or blocked here)." : e.message; syStatus(); }
}
async function syGhPush(retry = true){
  if (!GH.repo || !GH.token) return;
  if (SY.gh.busy) { SY.gh.again = true; return; }
  SY.gh.busy = true;
  try {
    const r = await ghApi("PUT", {message: "Sync board notes and progress", content: b64enc(JSON.stringify(syPayload())), ...(GH.sha ? {sha: GH.sha} : {})});
    if ((r.status === 409 || r.status === 422) && retry) { SY.gh.busy = false; await syGhPull(); return; }   // another device wrote first: merge, then push again
    if (!r.ok) throw new Error(ghErr(r));
    GH.sha = (await r.json()).content.sha; ghSave();
    SY.gh.state = "ok"; SY.gh.err = ""; SY.gh.at = Date.now();
  } catch (e) { SY.gh.state = "error"; SY.gh.err = /fetch/i.test(e.message) ? "Couldn't reach GitHub from this page (offline, or blocked here)." : e.message; }
  SY.gh.busy = false; syStatus();
  if (SY.gh.again) { SY.gh.again = false; syGhPush(); }
}

/* ---- wiring: every save marks changes and pushes ~1.5 s later; load, focus and a 60 s timer pull ---- */
const syBaseSave = save;
save = function(){ syBaseSave(); if (!SY.ready) return; clearTimeout(SY.timer); SY.timer = setTimeout(() => { if (syDiff()) { syClaudePush(); syGhPush(); } }, 1500); };
function syStart(){
  SY.prev = syFlat(state);
  for (const p of Object.keys(SY.prev)) if (!(p in SY.meta)) SY.meta[p] = 1;   // existing data with no history: oldest possible time
  syMetaSave(); SY.ready = true;
  syClaudeInit(); syGhPull();
  document.addEventListener("visibilitychange", () => { if (!document.hidden) syGhPull(); });
  setInterval(() => { if (!document.hidden) syGhPull(); }, 60000);
  window.addEventListener("pagehide", () => { if (syDiff()) { syClaudePush(); syGhPush(); } });
}
setTimeout(syStart, 0);

/* ---- status pill + settings panel (in "My notes & bookmarks") ---- */
const syTime = t => t ? new Date(t).toLocaleTimeString("en-IN", {hour: "2-digit", minute: "2-digit"}) : "";
function syStatus(){
  let pill = document.getElementById("syncpill");
  if (!pill) { pill = document.createElement("button"); pill.id = "syncpill"; pill.type = "button"; pill.onclick = () => { filter = 34; renderTabs(); renderBoard(); window.scrollTo(0, 0); }; document.body.appendChild(pill); }
  const c = SY.claude, g = SY.gh, on = [c.state === "ok" && "Claude", g.state === "ok" && "GitHub"].filter(Boolean);
  const err = c.state === "error" || g.state === "error", busy = c.state === "connecting" || g.state === "connecting";
  pill.className = err ? "err" : on.length ? "ok" : "";
  pill.textContent = err ? "⚠ Sync problem" : busy ? "⟳ Syncing…" : on.length ? `✓ Synced ${syTime(Math.max(c.at, g.at))} · ${on.join(" + ")}` : "Sync: this device only";
  pill.title = "Bookmarks, notes, highlights and progress sync. Click for settings.";
  const box = document.getElementById("syncbox"); if (box) box.innerHTML = syPanel();
  syWire();
}
function syLine(name, s, offText){
  const st = s.state === "ok" ? `<span class="syok">✓ On</span> · last synced ${syTime(s.at)}` : s.state === "connecting" ? "Connecting…" : s.state === "error" ? `<span class="syerr">⚠ ${esc(s.err)}</span>` : offText;
  return `<div class="syrow"><b>${name}</b><span>${st}</span></div>`;
}
function syPanel(){
  const claudeOff = SY.claude.state === "na" ? "Not available here. It works automatically when you open the board inside Claude (web, desktop or phone app) while signed in." : "Off";
  return `<h3>Sync across devices</h3>
    <p class="vxnote2">Bookmarks, notes, highlights, notepad, comments and progress are merged on every page load, when you come back to the tab, every minute, and about 1.5 s after each change. Edits from different devices combine; for the same item the newest edit wins.</p>
    ${syLine("Claude account", SY.claude, claudeOff)}
    ${syLine("GitHub", SY.gh, "Not connected on this device")}
    ${GH.repo && GH.token ? `<div class="syrow"><span>Saving to <code>${esc(GH.repo)}/${esc(GH.path)}</code></span><span><button type="button" class="sdtog" id="syNow">Sync now</button> <button type="button" class="sdtog" id="syOff">Disconnect GitHub on this device</button></span></div>`
    : `<details class="sysetup"><summary>Connect GitHub (needed for the GitHub Pages site, and to share notes between it and Claude)</summary>
      <ol><li>On GitHub create a new <b>private</b> repository, e.g. <code>dsa-board-data</code> (empty is fine).</li>
        <li>Settings → Developer settings → <b>Fine-grained tokens</b> → Generate new token. Repository access: <b>Only select repositories</b> → that repo. Permissions → Repository → <b>Contents: Read and write</b>. Pick an expiry.</li>
        <li>Paste the repo and token below. Do this once on each device. The token is stored only in this browser and is sent only to api.github.com; never paste it into a chat.</li></ol>
      <div class="syform"><input id="syRepo" placeholder="your-username/dsa-board-data" value="${esc(GH.repo)}" autocomplete="off" spellcheck="false">
        <input id="syTok" type="password" placeholder="github_pat_…" autocomplete="off" spellcheck="false"><button type="button" class="sdlabbtn" id="syGo">Connect and sync</button></div></details>`}`;
}
function syWire(){
  const go = document.getElementById("syGo");
  if (go) go.onclick = () => {
    const repo = document.getElementById("syRepo").value.trim().replace(/^https?:\/\/github\.com\//, "").replace(/\.git$|\/$/g, ""), tok = document.getElementById("syTok").value.trim();
    if (!/^[\w.-]+\/[\w.-]+$/.test(repo) || !tok) { SY.gh.state = "error"; SY.gh.err = "Enter the repo as owner/name and paste the token."; syStatus(); return; }
    GH = {repo, token: tok, path: "board-sync.json", sha: ""}; ghSave(); syGhPull();
  };
  const now = document.getElementById("syNow"); if (now) now.onclick = () => { syGhPull(); if (SY.claude.on) syClaudePush(); };
  const off = document.getElementById("syOff"); if (off) off.onclick = () => { GH = {repo: "", token: "", path: "board-sync.json", sha: ""}; ghSave(); SY.gh = {state: "off", at: 0, err: ""}; syStatus(); };
}
