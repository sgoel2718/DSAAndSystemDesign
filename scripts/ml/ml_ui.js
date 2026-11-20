/* ================= ML & AI section (third group) ================= */
const MLX = PLAN.mlx;
const ML_TABS = [[40, "Start here"], ...MLX.tabs.map((t, i) => [41 + i, t.label]), [52, "▶ Live demos"], [53, "Hands-on labs"], [54, "Interview Q&A"],
  [55, "Capstone projects"], [56, "Cheat sheet"], [57, MLX.plan.length + "-day study plan"], [34, "✎ My notes & bookmarks"]];
MLX.tabs.forEach((t, i) => t.sections.forEach(s => s.ids.forEach(id => SD_TAB_OF[id] = 41 + i)));
MLX.labs.forEach(l => SD_TAB_OF[l.id] = 53);
const ML_TABNUM = {}; MLX.tabs.forEach((t, i) => ML_TABNUM[t.key] = 41 + i);
let MLV = {qaTopic: "All", module: "All", capSort: "", capOpen: null};
if (!state.mlcap) state.mlcap = {short: {}, pick: ""};
const ML_DEMO_TITLE = k => (MLX.demos.find(d => d.id === k) || {title: k}).title;
const mlLearned = id => !!state.sd.c[id];

/* ---------- Python code blocks with light syntax highlighting ---------- */
const PY_RE = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|[rbf]?"(?:\\.|[^"\\\n])*"|[rbf]?'(?:\\.|[^'\\\n])*')|\b(def|class|return|if|elif|else|for|while|in|import|from|as|with|try|except|finally|raise|lambda|yield|not|and|or|is|None|True|False|pass|break|continue|global|nonlocal|async|await|assert|del)\b|\b(\d+\.?\d*(?:e[-+]?\d+)?)\b/g;
function pyHL(src){
  let out = "", last = 0, m; PY_RE.lastIndex = 0;
  while ((m = PY_RE.exec(src))) {
    out += esc(src.slice(last, m.index));
    const cls = m[1] ? "c" : m[2] ? "s" : m[3] ? "k" : "n";
    out += `<span class="tk-${cls}">${esc(m[0])}</span>`; last = m.index + m[0].length;
  }
  return out + esc(src.slice(last));
}
function pyBlock(code, net){
  return `<div class="codewrap"><div class="codebar"><span>Python · ${net ? "needs internet or an API key: run it in Colab / VS Code" : "verified: runs as-is in Google Colab or VS Code"}</span><span class="cbtns"><button type="button" class="copy sdcopy">Copy</button><a class="copy" href="https://colab.research.google.com/#create=true" target="_blank" rel="noopener">New Colab notebook ↗</a></span></div><pre class="code py">${pyHL(code)}</pre></div>`;
}

/* ---------- toolbar shared by ML tabs ---------- */
const mlToolbar = (ph, extra = "") => sdToolbar(ph, extra).replace('<span class="sr">Search system design</span>', '<span class="sr">Search machine learning</span>');
const mlProg = (n, d, what) => `<div class="sdprog"><div class="trbar"><i style="width:${n ? d / n * 100 : 0}%"></i></div><span><b>${d}</b> of ${n} ${what}</span></div>`;
function mlGoLab(id){ filter = 53; GROUP = "ml"; SDV.q = ""; MLV.module = "All"; SDV.open.add(id); renderTabs(); renderBoard();
  requestAnimationFrame(() => { const el = document.getElementById("sdc-" + id); if (el) { openCard(el); el.scrollIntoView({block: "start"}); } }); }
function mlGoTab(key){ filter = ML_TABNUM[key] || 40; GROUP = "ml"; SDV.q = ""; renderTabs(); renderBoard(); document.getElementById("tabs").scrollIntoView({behavior: "smooth"}); }

/* ---------- labs ---------- */
function mlLabCard(l){
  const open = SDV.open.has(l.id), done = !!state.sd.m[l.id];
  return `<article class="sdc mlcard${done ? " learned" : ""}" id="sdc-${l.id}">
    <button type="button" class="sdch" aria-expanded="${open}" aria-controls="sdb-${l.id}" data-id="${l.id}">
      <span class="sdct"><b>${esc(l.title)}</b>${doneMark(done)}</span><span class="sdlv I">${esc(l.module)}</span>
      <span class="sdwhat">${mdInline(l.goal)}</span></button>${tmActs("mlab:" + l.id, l.title, "mlab")}${state.tn["mlab:" + l.id] ? tmNoteArea("mlab:" + l.id) : ""}
    <div class="sdcb" id="sdb-${l.id}"${open ? "" : " hidden"}>${open ? mlLabBody(l) : ""}</div></article>`;
}
function mlLabBody(l){
  if (!l) return "";
  return `<p><b>Goal.</b> ${mdInline(l.goal)}</p><p><b>Data.</b> ${mdInline(l.data)}</p>
    <div class="sdbox tip"><b>Steps</b><ol>${l.steps.map(s => `<li>${mdInline(s)}</li>`).join("")}</ol></div>
    ${l.reuse ? `<p class="labnote">The notebook for this lab is the end-to-end example from <button type="button" class="sdlink" data-go="${l.reuse}">${esc(SD_TITLE(l.reuse))}</button>, repeated here so you can run it straight away.</p>` : ""}
    ${pyBlock(l.code, l.net)}
    ${l.observe.length ? `<div class="sdbox ex"><b>What you should see</b><ul>${l.observe.map(x => `<li>${mdInline(x)}</li>`).join("")}</ul></div>` : ""}
    ${l.extend.length ? `<div class="sdbox an"><b>Take it further</b><ul>${l.extend.map(x => `<li>${mdInline(x)}</li>`).join("")}</ul></div>` : ""}
    ${l.see.length ? `<div class="sdsee"><span>Concepts used:</span>${l.see.map(s => `<button type="button" class="sdlink" data-go="${s}">${esc(SD_TITLE(s))}</button>`).join("")}</div>` : ""}
    <label class="sdlearn"><input type="checkbox" data-mllab="${l.id}"${state.sd.m[l.id] ? " checked" : ""}> I completed this lab</label>`;
}
function renderMLLabs(root){
  const q = SDV.q.trim().toLowerCase(), mods = ["All", ...new Set(MLX.labs.map(l => l.module))];
  const list = MLX.labs.filter(l => (MLV.module === "All" || l.module === MLV.module) && hit(q, l.title, l.goal, l.data, l.steps.join(" "), l.code));
  const done = MLX.labs.filter(l => state.sd.m[l.id]).length;
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · experiential learning</div><h2>Hands-on labs</h2>
    <p class="lead">${MLX.labs.length} end-to-end practicals covering every lab in the syllabus. Each has a goal, dataset, steps, a complete notebook you can paste into Google Colab or VS Code (every offline one has been run and verified), what you should observe and how to extend it.</p>
    ${mlProg(MLX.labs.length, done, "labs completed")}
    ${mlToolbar("Search labs, e.g. XGBoost, PCA, RAG, LSTM").replace(/<div class="sdlvls"[\s\S]*?<\/div>/, "")}
    <div class="sdtopics" role="group" aria-label="Module">${mods.map(m => `<button type="button" data-mod="${esc(m)}" aria-pressed="${MLV.module === m}">${esc(m === "All" ? "All modules" : m)}</button>`).join("")}</div>
    <div class="sdlist mllabs">${list.map(mlLabCard).join("") || `<p class="qempty">No labs match.</p>`}</div>`;
  sdWireToolbar(root);
  root.querySelectorAll("[data-mod]").forEach(b => b.onclick = () => { MLV.module = b.dataset.mod; renderSDX(); });
}

/* ---------- interview Q&A ---------- */
function renderMLQA(root){
  const q = SDV.q.trim().toLowerCase(), topics = ["All", ...new Set(MLX.qa.map(x => x.topic))];
  const cm = {}; MLX.qa.forEach(x => x.companies.forEach(c => cm[c] = (cm[c] || 0) + 1));
  const list = MLX.qa.filter(x => lvOK(x.level) && (SDV.company === "All" || x.companies.includes(SDV.company)) && (SDV.freq === "All" || x.freq === SDV.freq) && (MLV.qaTopic === "All" || x.topic === MLV.qaTopic) && hit(q, x.q, x.a, x.topic, x.companies.join(" ")))
    .sort((a, b) => SDV.qaSort === "freq" ? FREQ_ORDER[a.freq] - FREQ_ORDER[b.freq] : 0);
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · interview preparation</div><h2>Interview Q&amp;A</h2>
    <p class="lead">${MLX.qa.length} questions asked in data-science, ML-engineer and GenAI interviews, with model answers. Badges show how often each comes up (★★★ almost every loop) and companies where it is typically asked (a guide, not a guarantee). Every concept card also has an <i>In the interview</i> answer.</p>
    ${mlToolbar("Search questions or a company", `<label class="sdco-sel">Company <select id="sdCo"><option value="All">All companies</option>${Object.entries(cm).sort((a, b) => b[1] - a[1]).map(([c, n]) => `<option value="${esc(c)}"${SDV.company === c ? " selected" : ""}>${esc(c)} (${n})</option>`).join("")}</select></label><label class="sdco-sel">How often <select id="sdFreq">${["All", "Very common", "Common", "Sometimes"].map(f => `<option${SDV.freq === f ? " selected" : ""}>${f}</option>`).join("")}</select></label><label class="sdpract"><input type="checkbox" id="sdSort"${SDV.qaSort === "freq" ? " checked" : ""}> Most asked first</label><button type="button" class="sdtog" id="sdShowAll">${SDV.qaShowAll ? "Hide all answers" : "Show all answers"}</button>`)}
    <div class="sdtopics" role="group" aria-label="Topic">${topics.map(t => `<button type="button" data-tp="${esc(t)}" aria-pressed="${MLV.qaTopic === t}">${esc(t)}</button>`).join("")}</div>
    <p class="sdcount">${list.length} questions</p>
    <div class="sdqa">${list.map((x, i) => `<details class="sdq" id="mqa-${x.id}"${SDV.qaShowAll || state.tn["mlqa:" + x.id] ? " open" : ""}><summary><span class="sdqn">${i + 1}</span><span class="sdqq">${mdInline(x.q)}<span class="sdqco">Asked at ${x.companies.map(esc).join(" · ")}</span></span><span class="sdbadges">${freqBadge(x.freq)}${lvBadge(x.level)}<span class="sdqt">${esc(x.topic)}</span>${tmActs("mlqa:" + x.id, x.q, "mlqa")}</span></summary>${state.tn["mlqa:" + x.id] ? tmNoteArea("mlqa:" + x.id) : ""}<div class="sdqa-a">${md(x.a)}</div></details>`).join("") || `<p class="qempty">No questions match.</p>`}</div>`;
  sdWireToolbar(root);
  root.querySelector("#sdShowAll").onclick = () => { SDV.qaShowAll = !SDV.qaShowAll; renderSDX(); };
  root.querySelector("#sdCo").onchange = e => { SDV.company = e.target.value; renderSDX(); };
  root.querySelector("#sdFreq").onchange = e => { SDV.freq = e.target.value; renderSDX(); };
  root.querySelector("#sdSort").onchange = e => { SDV.qaSort = e.target.checked ? "freq" : ""; renderSDX(); };
  root.querySelectorAll(".sdtopics button").forEach(b => b.onclick = () => { MLV.qaTopic = b.dataset.tp; renderSDX(); });
}

/* ---------- start page + search ---------- */
function mlTabProgress(t){ const ids = t.sections.flatMap(s => s.ids); return [ids.length, ids.filter(mlLearned).length]; }
function mlNext(){ for (const d of MLX.plan) { const id = d.ids.find(i => !mlLearned(i)); if (id) return {day: d, id}; } return null; }
function renderMLStart(root){
  if (SDV.q.trim()) { renderMLSearch(root); return; }
  const allIds = Object.keys(MLX.concepts), learned = allIds.filter(mlLearned).length, labsDone = MLX.labs.filter(l => state.sd.m[l.id]).length, nx = mlNext();
  const pick = MLX.capstones.find(c => c.id === state.mlcap.pick);
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · start here</div><h2>Machine Learning &amp; AI: from Python basics to generative and agentic AI</h2>
    ${mlToolbar("Search all of ML & AI: concepts, labs, interview questions")}
    <p class="lead">A complete course in the order you should learn it: the Python and maths bridge, classical machine learning, deep learning, computer vision and speech, NLP and transformers, LLMs, RAG, generative and agentic AI, and deploying models. Every topic has a plain-English explanation, an analogy or example, runnable Python, and what to say in an interview. Live demos run in your browser.</p>
    <div class="sdstats"><div><b>${learned}<span>/${allIds.length}</span></b>concepts learned</div><div><b>${labsDone}<span>/${MLX.labs.length}</span></b>labs completed</div>
      <div><b>${MLX.demos.length}</b>live demos</div><div><b>${MLX.qa.length}</b>interview Q&amp;As</div><div><b>${MLX.projects.length}</b>end-to-end projects</div><div><b>${MLX.capstones.length}</b>capstone options</div></div>
    ${nx ? `<div class="sdbox tip mlnext"><b>Continue where you left off</b><p>Day ${nx.day.day} of ${MLX.plan.length}: ${esc(nx.day.title)}</p><button type="button" class="sdlabbtn" data-go="${nx.id}">Open: ${esc(SD_TITLE(nx.id))} →</button></div>` : `<div class="sdbox tip"><b>Every concept learned!</b><p>Finish the labs and pick a capstone.</p></div>`}
    <div class="sdbox an"><b>How to use this section</b><ol>
      <li><b>Learn</b> one day of the <button type="button" class="sdlink" data-mltab="57">${MLX.plan.length}-day study plan</button> at a time: open each concept card, read it, run its code in Colab, and tick <i>I understand this concept</i>.</li>
      <li><b>Play</b> with the <button type="button" class="sdlink" data-mltab="52">live demos</button> to build intuition (gradient descent, overfitting, k-means, neural networks, attention…).</li>
      <li><b>Do</b> the <button type="button" class="sdlink" data-mltab="53">hands-on lab</button> attached to each day, then <b>build</b> the <button type="button" class="sdlink" data-mltab="58">end-to-end project</button> for that topic.</li>
      <li><b>Revise</b> with the <button type="button" class="sdlink" data-mltab="54">interview Q&amp;A</button> and <button type="button" class="sdlink" data-mltab="56">cheat sheet</button>, then build a <button type="button" class="sdlink" data-mltab="55">capstone project</button>${pick ? ` (your pick: <b>${esc(pick.title)}</b>)` : ""}.</li>
      <li>Select any text to <b>Explain</b> or <b>Highlight</b> it; tap ☆ / ✎ on any card to bookmark or write a note.</li></ol></div>
    ${MLX.roadmap.map(st => `<div class="sdstage"><div class="sdsh"><h3>${esc(st.name)}</h3></div><p>${esc(st.why)}</p>
      <div class="mltabs">${st.tabs.map(k => { const t = MLX.tabs.find(x => x.key === k), [n, d] = mlTabProgress(t);
        return `<button type="button" class="mltabcard" data-mlkey="${k}"><b>${esc(t.label)}</b><span>${esc(t.intro.split(" · ")[1] || t.intro)}</span><div class="trbar"><i style="width:${d / n * 100}%"></i></div><em>${d}/${n} concepts</em></button>`; }).join("")}</div></div>`).join("")}
    <p class="labnote">Code runs on Python 3.10+ with scikit-learn, PyTorch, Keras, Hugging Face and friends. In Colab most libraries are pre-installed; switch the runtime to GPU for deep-learning chapters. Cards marked <i>needs internet or an API key</i> download pretrained models or call paid APIs.</p>`;
  sdWireToolbar(root);
  root.querySelectorAll("[data-mlkey]").forEach(b => b.onclick = () => mlGoTab(b.dataset.mlkey));
}
function renderMLSearch(root){
  const q = SDV.q.trim().toLowerCase();
  const cs = Object.values(MLX.concepts).filter(c => lvOK(c.level) && hit(q, c.title, c.what, c.body, c.code));
  const ls = MLX.labs.filter(l => hit(q, l.title, l.goal, l.steps.join(" "))), qs = MLX.qa.filter(x => lvOK(x.level) && hit(q, x.q, x.a));
  const item = (id, t, type, lv, sub) => `<li><button type="button" class="sdres" data-go="${id}"><span class="sdrt">${type}</span><b>${esc(t)}</b>${lv ? lvBadge(lv) : ""}<span class="sdrs">${sub}</span></button></li>`;
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · search</div><h2>Results for “${esc(SDV.q)}”</h2>${mlToolbar("Search all of ML & AI")}
    <p class="sdcount">${cs.length} concepts · ${ls.length} labs · ${qs.length} Q&amp;A</p>
    <ul class="sdresults">${cs.map(c => item(c.id, c.title, "Concept", c.level, mdInline(c.what))).join("")}${ls.map(l => item(l.id, l.title, "Lab", "", esc(l.goal))).join("")}</ul>
    ${qs.length ? `<h3>Interview Q&amp;A</h3><div class="sdqa">${qs.map(x => `<details class="sdq"><summary><span class="sdqq">${mdInline(x.q)}</span>${lvBadge(x.level)}</summary><div class="sdqa-a">${md(x.a)}</div></details>`).join("")}</div>` : ""}`;
  sdWireToolbar(root);
}

/* ---------- study plan ---------- */
function renderMLPlan(root){
  const nx = mlNext(), daysDone = MLX.plan.filter(d => d.ids.every(mlLearned) && d.labs.every(l => state.sd.m[l])).length;
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · study plan</div><h2>${MLX.plan.length}-day study plan</h2>
    <p class="lead">One focused session a day (about 1–2 hours): learn 2–4 concepts, run their code, and do the attached lab. Days follow the syllabus order, so each builds on the last. A day turns green when all its concepts are ticked and its labs are completed.</p>
    ${mlProg(MLX.plan.length, daysDone, "days complete")}
    <ol class="mlplan">${MLX.plan.map(d => { const c = d.ids.filter(mlLearned).length + d.labs.filter(l => state.sd.m[l]).length, n = d.ids.length + d.labs.length, cur = nx && nx.day.day === d.day;
      return `<li class="mlday${c === n ? " done" : ""}${cur ? " cur" : ""}"><div class="mldh"><span class="mldn">Day ${d.day}</span><b>${esc(d.title)}</b><span class="mldc">${c}/${n}${cur ? " · you are here" : ""}</span></div>
        <div class="sdchips">${d.ids.map(id => `<button type="button" class="sdchip${mlLearned(id) ? " on" : ""}" data-go="${id}">${mlLearned(id) ? "✓ " : ""}${esc(SD_TITLE(id))}</button>`).join("")}
        ${d.labs.map(l => `<button type="button" class="sdchip lab${state.sd.m[l] ? " on" : ""}" data-golab-ml="${l}">${state.sd.m[l] ? "✓ " : "🧪 "}${esc(SD_TITLE(l))}</button>`).join("")}</div></li>`; }).join("")}</ol>
    <p class="labnote">After the plan: build a capstone (about 2–6 weeks), and revise with the Interview Q&amp;A and cheat sheet.</p>`;
}

/* ---------- capstones ---------- */
const CAP_DIFF = {"Easy": 1, "Easy-Medium": 2, "Medium": 3, "Medium-Hard": 4, "Hard": 5};
const stars = n => "★".repeat(n) + "☆".repeat(5 - n);
function renderCapstones(root){
  const caps = [...MLX.capstones].sort((a, b) => MLV.capSort === "diff" ? CAP_DIFF[a.difficulty] - CAP_DIFF[b.difficulty] : MLV.capSort === "port" ? b.portfolio - a.portfolio : MLV.capSort === "int" ? b.interview - a.interview : 0);
  const pick = MLX.capstones.find(c => c.id === state.mlcap.pick), K = MLX.kit;
  const card = c => `<article class="mlcap${state.mlcap.pick === c.id ? " picked" : ""}" id="cap-${c.id}"><div class="mlcaph"><h3>${esc(c.title)}</h3><span class="nvkind">${esc(c.domain)}</span></div>
      <p><b>Problem type:</b> ${esc(c.type)} · <b>Difficulty:</b> ${esc(c.difficulty)} · <b>Time:</b> ${esc(c.weeks)} weeks</p>
      <p><b>Data:</b> ${mdInline(c.data)}</p><p><b>Skills you'll show:</b> ${c.skills.map(esc).join(" · ")}</p>
      <div class="sdbox tip"><b>Suggested approach</b><ol>${c.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol></div>
      <p><b>Stretch goals:</b> ${esc(c.stretch)}</p><p><b>Watch out:</b> ${esc(c.risk)}</p>
      <div class="mlcapb"><button type="button" class="sdtog" data-short="${c.id}" aria-pressed="${!!state.mlcap.short[c.id]}">${state.mlcap.short[c.id] ? "★ Shortlisted" : "☆ Shortlist"}</button>
        <button type="button" class="sdlabbtn" data-pick="${c.id}">${state.mlcap.pick === c.id ? "✓ My capstone" : "Choose this capstone"}</button></div></article>`;
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · capstone</div><h2>Capstone projects</h2>
    <p class="lead">All ${MLX.capstones.length} capstone options compared side by side, with data sources, skills, effort and a suggested approach — plus a documentation and presentation kit. You haven't picked one yet${pick ? "" : ""}; shortlist a few, then choose when you're ready.</p>
    ${pick ? `<div class="sdbox ex"><b>Your capstone: ${esc(pick.title)}</b><p>${esc(pick.type)} · ${esc(pick.weeks)} weeks. Follow the approach below and use the kit at the bottom for the report and slides.</p><button type="button" class="sdlink" data-capgo="${pick.id}">Jump to its plan ↓</button></div>` : ""}
    <div class="sdbar"><label class="sdco-sel">Sort by <select id="capSort"><option value="">Syllabus order</option><option value="diff"${MLV.capSort === "diff" ? " selected" : ""}>Easiest first</option><option value="port"${MLV.capSort === "port" ? " selected" : ""}>Portfolio impact</option><option value="int"${MLV.capSort === "int" ? " selected" : ""}>Interview value</option></select></label></div>
    <div class="tscroll"><table class="sdt mlcapt"><thead><tr><th>Project</th><th>Type</th><th>Difficulty</th><th>Weeks</th><th>Portfolio</th><th>Interview value</th><th>Main risk</th></tr></thead><tbody>
      ${caps.map(c => `<tr${state.mlcap.pick === c.id ? ' class="picked"' : ""}><td><button type="button" class="sdlink" data-capgo="${c.id}">${state.mlcap.short[c.id] ? "★ " : ""}${esc(c.title)}</button></td><td>${esc(c.type)}</td><td>${esc(c.difficulty)}</td><td>${esc(c.weeks)}</td><td class="mlstars" title="${c.portfolio}/5">${stars(c.portfolio)}</td><td class="mlstars" title="${c.interview}/5">${stars(c.interview)}</td><td>${esc(c.risk)}</td></tr>`).join("")}</tbody></table></div>
    <div class="sdbox an"><b>How to choose</b><ul><li>Want a job in <b>GenAI / NLP</b>: Quora question pairs or real-time tweet analytics.</li><li><b>Computer vision</b>: food segmentation or GAN super-resolution (needs a GPU — Colab is enough).</li>
      <li><b>Data science / analytics</b>: talent retention, bank term deposit, retail segmentation, IPL, literacy rate.</li><li><b>Forecasting / industry</b>: logistics demand, stock time series, bearing anomaly detection.</li>
      <li><b>Recommenders</b> (very common in interviews): movie recommendation. Pick something you can finish well — depth beats ambition.</li></ul></div>
    <div class="mlcaps">${caps.map(card).join("")}</div>
    <div class="sdstage" id="mlkit"><h3>Documentation &amp; presentation kit</h3>
      <div class="mlkit"><div><h4>Project report outline</h4><ol>${K.report.map(x => `<li>${esc(x)}</li>`).join("")}</ol></div>
        <div><h4>10-slide presentation</h4><ol class="plain">${K.slides.map(x => `<li>${esc(x)}</li>`).join("")}</ol></div>
        <div><h4>README for GitHub</h4><ol>${K.readme.map(x => `<li>${esc(x)}</li>`).join("")}</ol></div>
        <div><h4>Submission checklist</h4><ul>${K.checklist.map(x => `<li>${esc(x)}</li>`).join("")}</ul></div></div>
      <h4>How it will be judged (self-review rubric)</h4><div class="tscroll"><table class="sdt"><thead><tr><th>Criterion</th><th>What good looks like</th></tr></thead><tbody>${K.rubric.map(([a, b]) => `<tr><td>${esc(a)}</td><td>${esc(b)}</td></tr>`).join("")}</tbody></table></div></div>`;
  root.querySelector("#capSort").onchange = e => { MLV.capSort = e.target.value; renderSDX(); };
  root.querySelectorAll("[data-short]").forEach(b => b.onclick = () => { const k = b.dataset.short; if (state.mlcap.short[k]) delete state.mlcap.short[k]; else state.mlcap.short[k] = Date.now(); save(); const y = scrollY; renderSDX(); scrollTo(0, y); });
  root.querySelectorAll("[data-pick]").forEach(b => b.onclick = () => { state.mlcap.pick = state.mlcap.pick === b.dataset.pick ? "" : b.dataset.pick; save(); const y = scrollY; renderSDX(); scrollTo(0, y); });
  root.querySelectorAll("[data-capgo]").forEach(b => b.onclick = () => { const el = document.getElementById("cap-" + b.dataset.capgo); if (el) el.scrollIntoView({block: "start", behavior: "smooth"}); });
}

/* ---------- cheat sheet ---------- */
function renderMLCheat(root){
  const C = MLX.cheat, tbl = (h, rows) => `<div class="tscroll"><table class="sdt"><thead><tr>${h.map(x => `<th>${x}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(x => `<td>${mdInline(x)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · revise before the interview</div><h2>Cheat sheet</h2>
    <p class="lead">Which model, which metric, which loss, sensible defaults, how to debug, key formulas and the classic mistakes — on one page.</p>
    <div class="sdstage"><h3>If the problem is… start with…</h3>${tbl(["Problem", "Reach for"], C.algos)}</div>
    <div class="sdstage"><h3>Which metric?</h3>${tbl(["Situation", "Metric"], C.metrics)}</div>
    <div class="sdstage"><h3>Output layer and loss</h3>${tbl(["Task", "Output", "Loss"], C.heads)}</div>
    <div class="sdstage"><h3>Sensible defaults</h3>${tbl(["Setting", "Start with"], C.defaults)}</div>
    <div class="sdstage"><h3>Diagnose your model</h3>${tbl(["Symptom", "Likely cause → fix"], C.diagnose)}</div>
    <div class="sdstage"><h3>Formulas to remember</h3><ul class="mlform">${C.formulas.map(f => `<li>${esc(f)}</li>`).join("")}</ul></div>
    <div class="sdstage"><h3>Mistakes that fail projects and interviews</h3><ul>${C.pitfalls.map(p => `<li>${mdInline(p)}</li>`).join("")}</ul></div>`;
}

/* ---------- demos tab ---------- */
function mlDemoHTML(k, mode){ const d = MLX.demos.find(x => x.id === k) || {title: k, desc: ""};
  return `<section class="lab mldemo" id="${mode === "in" ? "" : "demo-" + k}" data-demo="${k}"><h3>${esc(d.title)}</h3><p class="labd">${esc(d.desc)}</p><div class="labbody"></div></section>`; }
function renderMLDemos(root){
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · learn by playing</div><h2>Live demos</h2>
    <p class="lead">${MLX.demos.length} interactive simulations that run right here in your browser — no install. Change the controls and watch the algorithm respond. Each is also linked from its concept card.</p>
    <div class="labgrid">${MLX.demos.map(d => mlDemoHTML(d.id)).join("")}</div>`;
  root.querySelectorAll(".mldemo").forEach(el => ML_DEMOS[el.dataset.demo](el));
}

/* ---------- router ---------- */
function renderMLX(root){
  if (filter === 40) renderMLStart(root);
  else if (filter >= 41 && filter < 41 + MLX.tabs.length) renderConceptTab(root, MLX.tabs[filter - 41]);
  else if (filter === 52) renderMLDemos(root);
  else if (filter === 53) renderMLLabs(root);
  else if (filter === 54) renderMLQA(root);
  else if (filter === 55) renderCapstones(root);
  else if (filter === 56) renderMLCheat(root);
  else if (filter === 57) renderMLPlan(root);
  else if (filter === 58) renderProjects(root);
}
document.addEventListener("click", e => {
  const t = e.target.closest("[data-mltab]"); if (t) { filter = +t.dataset.mltab; renderTabs(); renderBoard(); document.getElementById("tabs").scrollIntoView({behavior: "smooth"}); }
});

/* ---------- end-to-end projects ---------- */
ML_TABS.splice(ML_TABS.findIndex(t => t[0] === 53), 0, [58, "🛠 End-to-end projects"]);
MLX.projects.forEach(p => SD_TAB_OF[p.id] = 58);
const PJ_VERIFY = {full: ["✓ Verified end to end", "ok"], smoke: ["✓ Pipeline verified (smoke run)", "sm"], static: ["Code-checked · needs GPU/API", "st"]};
let PJV = {tab: "All"};
function codeBlock(code, lang, file){
  const body = lang === "python" ? pyHL(code) : esc(code);
  return `<div class="codewrap"><div class="codebar"><span>${file ? `<b>${esc(file)}</b>` : esc(lang === "bash" ? "Terminal" : lang)}</span><span class="cbtns"><button type="button" class="copy sdcopy">Copy</button></span></div><pre class="code ${lang === "python" ? "py" : ""}">${body}</pre></div>`;
}
function pjBody(p){
  const v = PJ_VERIFY[p.verify], tabLbl = (MLX.tabs.find(t => t.key === p.tab) || {}).label || "";
  const stepsDone = (state.mlpj && state.mlpj[p.id]) || {};
  return `<p class="pjmeta"><span class="pjv ${v[1]}">${v[0]}</span> · ${esc(p.time)} · ${esc(p.run)} · topic: ${esc(tabLbl)}</p>
    <p class="labnote">${esc(PLAN.mlx.pjlevels[p.verify])}</p>
    <div class="sdbox an"><b>What you'll build</b><ul>${p.build.map(x => `<li>${mdInline(x)}</li>`).join("")}</ul></div>
    <p><b>Skills:</b> ${p.skills.map(esc).join(" · ")}</p><p><b>Data:</b> ${mdInline(p.data)}</p>
    <div class="pjflow">${p.arch.map(a => `<span>${esc(a)}</span>`).join("<i>→</i>")}</div>
    <h4>Project structure</h4><pre class="code pjtree">${esc(p.tree)}</pre>
    <h4>Build it step by step</h4>
    <ol class="pjsteps">${p.steps.map((s, i) => `<li class="${stepsDone[i] ? "done" : ""}"><div class="pjsh"><label><input type="checkbox" data-pjstep="${p.id}|${i}"${stepsDone[i] ? " checked" : ""}> <b>${esc(s.title)}</b></label>${s.file ? `<code>${esc(s.file)}</code>` : ""}</div>
      ${s.text ? md(s.text) : ""}${s.code ? codeBlock(s.code.replace(/\n$/, ""), s.lang, s.file) : ""}</li>`).join("")}</ol>
    ${p.check.length ? `<div class="sdbox ex"><b>How it was verified here</b><p>These commands were run on the real project files${p.verify === "smoke" ? " (smoke mode)" : ""}:</p>${codeBlock(p.check.join("\n"), "bash")}</div>` : ""}
    ${p.errors.length ? `<div class="sdbox tip"><b>Errors you may hit and the fix</b><ul>${p.errors.map(([e, f]) => `<li><b>${esc(e)}</b> → ${mdInline(f)}</li>`).join("")}</ul></div>` : ""}
    ${p.talk.length ? `<div class="sdbox tip sdsay"><b>In the interview: how to present this project</b><ul>${p.talk.map(t => `<li>${mdInline(t)}</li>`).join("")}</ul></div>` : ""}
    ${p.extend.length ? `<div class="sdbox an"><b>Take it further</b><ul>${p.extend.map(x => `<li>${mdInline(x)}</li>`).join("")}</ul></div>` : ""}
    <div class="sdbox"><b>Publish it</b><ol><li>Create a GitHub repo (or a folder in your <i>AI-ML-Projects</i> repo), add a README with the goal, results table, screenshots and how to run.</li><li>For apps, deploy a demo (Hugging Face Spaces / Streamlit Cloud) and link it in the README.</li><li>Add the project to your resume with one quantified result line.</li></ol></div>
    ${p.see.length ? `<div class="sdsee"><span>Concepts used:</span>${p.see.map(s => `<button type="button" class="sdlink" data-go="${s}">${esc(SD_TITLE(s))}</button>`).join("")}</div>` : ""}
    <label class="sdlearn"><input type="checkbox" data-pjdone="${p.id}"${state.mlpj && state.mlpj[p.id] && state.mlpj[p.id].done ? " checked" : ""}> I built this project</label>`;
}
function pjCard(p){
  const open = SDV.open.has(p.id), done = !!(state.mlpj && state.mlpj[p.id] && state.mlpj[p.id].done), v = PJ_VERIFY[p.verify];
  return `<article class="sdc mlcard pjcard${done ? " learned" : ""}" id="sdc-${p.id}">
    <button type="button" class="sdch" aria-expanded="${open}" aria-controls="sdb-${p.id}" data-id="${p.id}">
      <span class="sdct"><b>${esc(p.title)}</b>${doneMark(done)}</span><span class="sdlv ${p.level[0]}">${esc(p.level)}</span>
      <span class="sdwhat">${mdInline(p.what)}<br><span class="pjv ${v[1]}">${v[0]}</span> <span class="pjsm">${esc(p.time)} · ${p.steps.filter(s => s.file).length} files</span></span></button>${tmActs("mlpj:" + p.id, p.title, "mlpj")}${state.tn["mlpj:" + p.id] ? tmNoteArea("mlpj:" + p.id) : ""}
    <div class="sdcb" id="sdb-${p.id}"${open ? "" : " hidden"}>${open ? pjBody(p) : ""}</div></article>`;
}
function renderProjects(root){
  const q = SDV.q.trim().toLowerCase(), tabs = ["All", ...new Set(MLX.projects.map(p => p.tab))];
  const list = MLX.projects.filter(p => (PJV.tab === "All" || p.tab === PJV.tab) && hit(q, p.title, p.what, p.skills.join(" "), p.steps.map(s => s.title + " " + s.code).join(" ")));
  const done = MLX.projects.filter(p => state.mlpj && state.mlpj[p.id] && state.mlpj[p.id].done).length, nv = k => MLX.projects.filter(p => p.verify === k).length;
  root.innerHTML = `<div class="eyebrow">ML &amp; AI · build real things</div><h2>End-to-end projects</h2>
    <p class="lead">${MLX.projects.length} complete projects, at least one for every topic, from an empty folder to a working, deployed app: real datasets, real pretrained models, full source files, tests, a demo app and deployment. Open one and follow the steps; every file has a Copy button and the folder tree shows where it goes.</p>
    <div class="sdstats"><div><b>${nv("full")}</b>verified end to end here on real data</div><div><b>${nv("smoke")}</b>pipeline verified (full run on a Colab GPU)</div><div><b>${nv("static")}</b>code-checked; need a GPU or API key</div><div><b>${done}<span>/${MLX.projects.length}</span></b>built by you</div></div>
    ${mlToolbar("Search projects, e.g. RAG, YOLO, FastAPI, forecasting").replace(/<div class="sdlvls"[\s\S]*?<\/div>/, "")}
    <div class="sdtopics" role="group" aria-label="Topic">${tabs.map(t => `<button type="button" data-pjtab="${t}" aria-pressed="${PJV.tab === t}">${esc(t === "All" ? "All topics" : (MLX.tabs.find(x => x.key === t) || {}).label)}</button>`).join("")}</div>
    <div class="sdlist">${list.map(pjCard).join("") || `<p class="qempty">No projects match.</p>`}</div>`;
  sdWireToolbar(root);
  root.querySelectorAll("[data-pjtab]").forEach(b => b.onclick = () => { PJV.tab = b.dataset.pjtab; renderSDX(); });
}
document.addEventListener("change", e => {
  const s = e.target.closest("[data-pjstep]"), d = e.target.closest("[data-pjdone]"); if (!s && !d) return;
  state.mlpj = state.mlpj || {};
  if (s) { const [id, i] = s.dataset.pjstep.split("|"); const o = state.mlpj[id] = state.mlpj[id] || {}; if (s.checked) o[i] = Date.now(); else delete o[i]; s.closest("li").classList.toggle("done", s.checked); }
  if (d) { const o = state.mlpj[d.dataset.pjdone] = state.mlpj[d.dataset.pjdone] || {}; if (d.checked) o.done = Date.now(); else delete o.done; d.closest(".sdc").classList.toggle("learned", d.checked); }
  save();
});
