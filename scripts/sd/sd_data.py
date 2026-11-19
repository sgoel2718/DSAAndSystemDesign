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


def build():
    concepts = {}
    for _, _, _, secs in CONCEPT_TABS:
        for _, cs in secs:
            for c in cs:
                assert c["id"] not in concepts, "duplicate concept " + c["id"]
                concepts[c["id"]] = c
    hld = HLD1 + HLD2
    lld = LLD1 + LLD2
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
        h["freq"] = "Very common" if h["id"] in very else "Common" if h["id"] in common else "Sometimes" if h["id"] in some else ""
    lvery = ["parkinglot-lld", "lru-lld", "splitwise-lld", "bookmyshow-lld", "elevator-lld", "ratelimiter-lld"]
    lcommon = ["vending-lld", "snakeladder-lld", "tictactoe-lld", "library-lld", "logger-lld", "kvstore-lld", "pubsub-lld", "atm-lld", "taskscheduler-lld"]
    for l in lld:
        l["freq"] = "Very common" if l["id"] in lvery else "Common" if l["id"] in lcommon else "Sometimes"
    tabs = [dict(key=k, label=l, intro=i, sections=[dict(name=n, ids=[c["id"] for c in cs]) for n, cs in secs]) for k, l, i, secs in CONCEPT_TABS]
    return dict(tabs=tabs, concepts=concepts, hld=hld, lld=lld, qa=QA,
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
