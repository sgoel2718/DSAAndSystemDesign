"""Assembles the whole System Design section and validates cross-references."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sd_c1 import FOUNDATIONS, NETWORKING
from sd_c2 import LOAD_BALANCING, CACHING, ASYNC, STORAGE_TYPES
from sd_c3 import DATABASES
from sd_c4 import DISTRIBUTED, PROBABILISTIC
from sd_c5 import ARCHITECTURE, RELIABILITY, SECURITY
from sd_c6 import PATTERNS
from sd_c7 import LLD
from sd_hld1 import HLD1
from sd_hld2 import HLD2
from sd_lld1 import LLD1
from sd_lld2 import LLD2
from sd_qa import QA
from sd_qa2 import QA2
from sd_qa_tags import tag
from sd_hld3 import HLD3
from sd_lld3 import LLD3
import sd_meta as M

# (tab key, tab label, intro, [(section name, concepts)])
CONCEPT_TABS = [
    ("fund", "Fundamentals", "Start here if you are new: what systems are made of, how the internet works and how clients talk to servers.",
     [("Core ideas", FOUNDATIONS), ("Networking & APIs", NETWORKING)]),
    ("blocks", "Building blocks", "The components you combine in every design: load balancers, CDNs, caches, queues and storage.",
     [("Load balancing & CDN", LOAD_BALANCING), ("Caching", CACHING), ("Queues & streaming", ASYNC), ("Storage types & search", STORAGE_TYPES)]),
    ("data", "Databases & storage", "How data is stored, indexed, replicated, partitioned and kept consistent.",
     [("Databases", DATABASES)]),
    ("dist", "Distributed systems", "The theory behind large systems: CAP, consistency, consensus, clocks, and clever probabilistic structures.",
     [("Theory & coordination", DISTRIBUTED), ("Probabilistic & spatial structures", PROBABILISTIC)]),
    ("arch", "Architecture & reliability", "How to structure services, survive failures, operate in production and stay secure.",
     [("Architecture", ARCHITECTURE), ("Reliability & operations", RELIABILITY), ("Security", SECURITY)]),
    ("patterns", "Real-world patterns", "Recurring solutions behind feeds, chat, video, payments, sales, maps, ML and GenAI systems.",
     [("Patterns", PATTERNS)]),
    ("lldc", "LLD & OOP", "Object-oriented design for machine-coding rounds, in Java: SOLID, UML, design patterns, concurrency.",
     [("Low-level design", LLD)]),
]


def attach_explain(concepts, hld, lld):
    """Attach the detailed explanation layer (sd_x*.py) to every card and validate its diagrams."""
    import glob, importlib, json
    from sd_x_util import EXPLAIN
    here = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(glob.glob(os.path.join(here, "sd_x_*.py"))):
        m = os.path.basename(f)[:-3]
        if m != "sd_x_util": importlib.import_module(m)
    out_f = os.path.join(here, "sd_lld_out.json")
    outs = json.load(open(out_f)) if os.path.exists(out_f) else {}
    cards = dict(concepts); cards.update({h["id"]: h for h in hld}); cards.update({l["id"]: l for l in lld})
    strip = lambda n: n.split(":", 1)[1] if n.split(":", 1)[0] in ("db", "q", "c", "u", "x") and ":" in n else n
    for cid, x in EXPLAIN.items():
        assert cid in cards, "explain for unknown card " + cid
        for b in x["blocks"]:
            sp = b.get("spec")
            if b["t"] == "flow":
                names = {strip(n) for row in sp["rows"] for n in row}
                for a, bb, *_ in sp["edges"]: assert strip(a) in names and strip(bb) in names, f"{cid} flow edge {a}->{bb}"
            elif b["t"] == "uml":
                names = {n for row in sp["rows"] for n in row}
                assert names == set(sp["classes"]), f"{cid} uml rows/classes mismatch {names ^ set(sp['classes'])}"
                for a, bb, ty, *_ in sp["rels"]:
                    assert a in names and bb in names and ty in ("inh", "impl", "comp", "agg", "assoc", "dep"), f"{cid} uml rel {a}->{bb} {ty}"
            elif b["t"] == "state":
                names = {n for row in sp["rows"] for n in row}
                for a, bb, *_ in sp["edges"]: assert a in names and bb in names, f"{cid} state edge {a}->{bb}"
            elif b["t"] == "seq":
                for m in sp["msgs"]:
                    if isinstance(m, dict): assert all(a in sp["actors"] for a in m["note"]), f"{cid} note {m}"
                    else: assert m[0] in sp["actors"] and m[1] in sp["actors"] and m[3] in ("", "r", "a"), f"{cid} seq msg {m}"
        if cid in outs: x["blocks"].append(dict(t="out", text=outs[cid], title="Real output when you run main()"))
        cards[cid]["x"] = x


def build():
    concepts = {}
    for _, _, _, secs in CONCEPT_TABS:
        for _, cs in secs:
            for c in cs:
                assert c["id"] not in concepts, "duplicate concept " + c["id"]
                concepts[c["id"]] = c
    from sd_say1 import SAY1
    from sd_say2 import SAY2
    for cid, c in concepts.items():
        say = SAY1.get(cid) or SAY2.get(cid)
        assert say, "no interview answer for " + cid
        if cid in SAY1: assert [p for p, _ in SAY1[cid]] == c["tips"], "tips mismatch " + cid
        c["say"] = [dict(p=p, a=a) for p, a in say]
    assert not (set(SAY1) | set(SAY2)) - set(concepts), (set(SAY1) | set(SAY2)) - set(concepts)
    from sd_follow import FOLLOW
    hld_all = HLD1 + HLD2 + HLD3
    for h in hld_all:
        fu = FOLLOW.get(h["id"]); assert fu, "no follow-ups for " + h["id"]
        if h["followups"] and isinstance(h["followups"][0], str): assert [q for q, _ in fu] == h["followups"], "follow-up mismatch " + h["id"]
        h["followups"] = [dict(q=q, a=a) for q, a in fu]
    assert not set(FOLLOW) - {h["id"] for h in hld_all}
    hld = HLD1 + HLD2 + HLD3
    lld = LLD1 + LLD2 + LLD3
    import hashlib
    qa = [dict(tag(q), id=hashlib.md5(q["q"].encode()).hexdigest()[:8]) for q in QA + QA2]
    assert len({q["q"] for q in qa}) == len(qa), "duplicate Q&A"
    ids = set(concepts) | {h["id"] for h in hld} | {l["id"] for l in lld} | {"hld-framework"}
    assert len({h["id"] for h in hld}) == len(hld) and len({l["id"] for l in lld}) == len(lld)
    labs = {"estimator", "ratelimit", "lb", "cache", "ring", "quorum", "fanout"}
    for c in concepts.values():
        for s in c["see"]:
            assert s in ids, f"{c['id']} -> missing see '{s}'"
        assert c["lab"] in (None, *labs), c["lab"]
        d = c["diagram"]
        if d and "rows" in d:
            names = {n.split(":", 1)[1] if n[:3] in ("db:", "q:", "c:", "u:", "x:") or n[:2] in ("q:", "c:", "u:", "x:") else n for row in d["rows"] for n in row}
            strip = lambda n: n.split(":", 1)[1] if n.split(":", 1)[0] in ("db", "q", "c", "u", "x") and ":" in n else n
            names = {strip(n) for row in d["rows"] for n in row}
            for a, b, *_ in d["edges"]:
                assert strip(a) in names and strip(b) in names, f"{c['id']} edge {a}->{b}"
    for h in hld:
        d = h["design"]
        strip = lambda n: n.split(":", 1)[1] if n.split(":", 1)[0] in ("db", "q", "c", "u", "x") and ":" in n else n
        names = {strip(n) for row in d["rows"] for n in row}
        for a, b, *_ in d["edges"]:
            assert strip(a) in names and strip(b) in names, f"{h['id']} edge {a}->{b}"
    for _, _, lst in M.ROADMAP:
        for i in lst:
            assert i in ids, "roadmap missing " + i
    # How often each question shows up across public prep lists (PracHub's count of 11 sources, Nov 2026):
    # 'Very common' = top 10, 'Common' = 11-20, 'Sometimes' = the rest of the top 30.
    very = ["urlshortener-hld", "chat-hld", "newsfeed-hld", "twitter-hld", "youtube-hld", "uber-hld", "autocomplete-hld", "ratelimiter-hld", "dropbox-hld", "crawler-hld", "notification-hld"]
    common = ["proximity-hld", "instagram-hld", "ticketmaster-hld", "cache-hld", "payment-hld", "googledocs-hld", "maps-hld", "adclick-hld", "metrics-hld", "jobscheduler-hld"]
    some = ["mq-hld", "fooddelivery-hld", "stockexchange-hld", "llmserving-hld", "hotel-hld", "kvstore-hld", "leaderboard-hld", "idgen-hld", "s3-hld", "tinder-hld"]
    for h in hld:
        h["freq"] = "Very common" if h["id"] in very else "Common" if h["id"] in common else "Sometimes" if h["id"] in some else "Less common"
    lvery = ["parkinglot-lld", "lru-lld", "splitwise-lld", "bookmyshow-lld", "elevator-lld", "ratelimiter-lld"]
    lcommon = ["chess-lld", "meetingroom-lld", "vending-lld", "snakeladder-lld", "tictactoe-lld", "library-lld", "logger-lld", "kvstore-lld", "pubsub-lld", "atm-lld", "taskscheduler-lld"]
    for l in lld:
        l["freq"] = "Very common" if l["id"] in lvery else "Common" if l["id"] in lcommon else "Sometimes"
    attach_explain(concepts, hld, lld)
    tabs = [dict(key=k, label=l, intro=i, sections=[dict(name=n, ids=[c["id"] for c in cs]) for n, cs in secs]) for k, l, i, secs in CONCEPT_TABS]
    return dict(tabs=tabs, concepts=concepts, hld=hld, lld=lld, qa=qa,
                roadmap=[dict(name=n, why=w, ids=l) for n, w, l in M.ROADMAP],
                framework=M.HLD_FRAMEWORK, levels=M.LEVELS_EXPECT, mistakes=M.MISTAKES, think=M.THINK, dbpick=M.DB_PICK,
                powers=M.POWERS, numbers=M.QUICK_NUMBERS, companies=M.COMPANIES)


if __name__ == "__main__":
    d = build()
    from collections import Counter
    print(len(d["concepts"]), "concepts", Counter(c["level"] for c in d["concepts"].values()))
    print(len(d["hld"]), "HLD", Counter(h["level"] for h in d["hld"]))
    print(len(d["lld"]), "LLD", Counter(h["level"] for h in d["lld"]))
    print(len(d["qa"]), "Q&A", Counter(q["level"] for q in d["qa"]))
    print("diagrams", sum(1 for c in d["concepts"].values() if c["diagram"]), "labs", sum(1 for c in d["concepts"].values() if c["lab"]))
    import json; print("json KB", len(json.dumps(d)) // 1024)
