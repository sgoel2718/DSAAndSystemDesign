"""Assemble and validate the ML & AI section data for the site."""
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from ml_py import PYTHON
from ml_math import PROB, LINALG
from ml_m1 import FOUND
from ml_sup import SUP
from ml_unsup import UNSUP
from ml_dl import DL
from ml_cv import CV
from ml_nlp import NLP
from ml_adv import ADV
from ml_ops import OPS
from ml_labs import LABS
from ml_qa import QA
from ml_meta import TABS, ROADMAP, DEMOS, CAPSTONES, KIT, CHEAT
from ml_projects import PROJECTS
from deep import d_py, d_stats, d_math, d_found, d_sup, d_unsup, d_dl, d_cv, d_nlp, d_gen, d_ops  # noqa: F401  (register deep layers)
from deep.util import D as DEEP
from ml_proj_util import LEVELS as PJ_LEVELS
import lessons  # noqa: F401  (registers beginner lessons)
from lesson_util import LESSONS

TOPIC_COMPANIES = {
    "ML fundamentals": ["Google", "Amazon", "Microsoft", "Flipkart", "Walmart Global Tech", "Fractal", "TCS / Infosys"],
    "Statistics & maths": ["Google", "Meta", "Amazon", "American Express", "JPMorgan Chase", "Mu Sigma", "Uber"],
    "Supervised learning": ["Amazon", "Flipkart", "PayPal", "American Express", "Walmart Global Tech", "Swiggy", "Microsoft"],
    "Evaluation metrics": ["Google", "Meta", "Amazon", "PayPal", "Swiggy", "Zomato"],
    "Unsupervised learning": ["Amazon", "Netflix", "Flipkart", "Myntra", "Spotify", "Walmart Global Tech"],
    "Deep learning": ["Google", "Microsoft", "NVIDIA", "Meta", "Samsung R&D", "Adobe", "Qualcomm"],
    "Computer vision": ["NVIDIA", "Tesla", "Samsung R&D", "Qualcomm", "Adobe", "Ola"],
    "NLP & transformers": ["Google", "Microsoft", "Amazon", "Meta", "Sprinklr", "Uniphore"],
    "LLMs & GenAI": ["OpenAI", "Anthropic", "Google DeepMind", "Microsoft", "Amazon (AWS)", "Salesforce", "GenAI startups"],
    "MLOps & deployment": ["Amazon", "Microsoft", "Uber", "Swiggy", "Flipkart", "Zomato", "Databricks"],
    "Responsible AI": ["Google", "Microsoft", "Meta", "IBM"],
}


def build():
    cards = PYTHON + PROB + LINALG + FOUND + SUP + UNSUP + DL + CV + NLP + ADV + OPS
    concepts = {}
    for c in cards:
        assert c["id"] not in concepts, "duplicate " + c["id"]
        concepts[c["id"]] = dict(c)
    tabs, placed = [], []
    for key, label, intro, sections in TABS:
        for _, ids in sections:
            for i in ids:
                assert i in concepts, (key, i)
                placed.append(i)
        tabs.append(dict(key=key, label=label, intro=intro, sections=[dict(name=n, ids=ids) for n, ids in sections]))
    assert len(placed) == len(set(placed)), [i for i in placed if placed.count(i) > 1]
    missing = set(concepts) - set(placed)
    assert not missing, "concepts not in any tab: %s" % missing
    demo_ids = {d[0] for d in DEMOS}
    for c in concepts.values():
        assert not c["demo"] or c["demo"] in demo_ids, (c["id"], c["demo"])
        for s in c["see"]:
            assert s in concepts, (c["id"], s)
    labs = []
    for l in LABS:
        l = dict(l)
        if l["reuse"]:
            assert l["reuse"] in concepts, l["id"]
            l["code"] = concepts[l["reuse"]]["code"]; l["net"] = l["net"] or concepts[l["reuse"]]["net"]
        for s in l["see"]:
            assert s in concepts, (l["id"], s)
            concepts[s].setdefault("labs", []).append(l["id"])
        labs.append(l)
    qa, seen = [], set()
    for topic, level, freq, q, a in QA:
        assert topic in TOPIC_COMPANIES, topic
        qid = hashlib.md5(q.encode()).hexdigest()[:8]
        assert qid not in seen, q
        seen.add(qid)
        cos = TOPIC_COMPANIES[topic]; h = int(qid, 16)
        pick = [cos[(h + i) % len(cos)] for i in range(4)]
        qa.append(dict(id=qid, topic=topic, level=level, freq=freq, q=q, a=a, companies=list(dict.fromkeys(pick))))
    # day-by-day study plan: walk the tabs in order, about 3 concepts a day, never mixing two sections in one day
    plan, where = [], {}
    for t in tabs:
        for s in t["sections"]:
            ids = s["ids"]; n = len(ids); k = max(1, round(n / 3))
            size = -(-n // k)
            for j in range(0, n, size):
                chunk = ids[j:j + size]
                plan.append(dict(day=len(plan) + 1, tab=t["key"], title=f"{t['label']}: {s['name']}", ids=chunk, labs=[]))
                for i in chunk: where[i] = len(plan) - 1
    for l in labs:
        d = max(where[s] for s in l["see"])
        plan[d]["labs"].append(l["id"])
    tabkeys = {t["key"] for t in tabs}
    for p in PROJECTS:
        assert p["tab"] in tabkeys, p["id"]
        for s_ in p["see"]:
            assert s_ in concepts, (p["id"], s_)
            concepts[s_].setdefault("projects", []).append(p["id"])
    for cid, c in concepts.items():
        assert cid in DEEP, "no deep layer/walkthrough for " + cid
        d = DEEP[cid]; c["deep"] = {k: d[k] for k in ("intuition", "maths", "worked", "mistakes", "use", "avoid")}
        c["e2e"] = {k: d[k] for k in ("data", "steps", "code", "net")}
        assert c.get("projects"), "concept not used in any end-to-end project: " + cid
    assert not set(DEEP) - set(concepts), set(DEEP) - set(concepts)
    for lid, les in LESSONS.items():
        assert lid in concepts, "lesson for unknown concept " + lid
        concepts[lid]["lesson"] = les
    caps = []
    for c in CAPSTONES:
        caps.append(dict(c))
    return dict(tabs=tabs, concepts=concepts, labs=labs, qa=qa, plan=plan, roadmap=[dict(name=n, why=w, tabs=k) for n, w, k in ROADMAP],
                demos=[dict(id=i, title=t, desc=d) for i, t, d in DEMOS], capstones=caps, kit=KIT, cheat=CHEAT, projects=PROJECTS, pjlevels=PJ_LEVELS)


if __name__ == "__main__":
    d = build()
    print(len(d["concepts"]), "concepts in", len(d["tabs"]), "tabs |", len(d["labs"]), "labs |", len(d["qa"]), "Q&A |", len(d["plan"]), "study days |",
          len(d["capstones"]), "capstones |", len(d["demos"]), "demos")
    import json
    print("JSON size %.0f KB" % (len(json.dumps(d)) / 1024))
