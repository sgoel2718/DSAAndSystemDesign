"""Adds a solution you pasted to leetcode/ in the same format the LeetCode sync uses, so the website shows it.
Usage: python3 scripts/add_submission.py <slug> <title> <code-file> [lang=java] [unix-time] [time-complexity] [space-complexity]"""
import json, os, sys, time
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leetcode")
EXT = {"java": "java", "python3": "py", "cpp": "cpp", "javascript": "js", "csharp": "cs", "mysql": "sql"}
slug, title, src = sys.argv[1:4]
lang = sys.argv[4] if len(sys.argv) > 4 else "java"
at = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] else int(time.time())
tc, sc = (sys.argv[6] if len(sys.argv) > 6 else ""), (sys.argv[7] if len(sys.argv) > 7 else "")
idx_path = os.path.join(ROOT, "index.json")
idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {"problems": {}, "seen": 0}
ext = EXT.get(lang, lang)
rel = f"{slug}/{slug}.{ext}"
os.makedirs(os.path.join(ROOT, slug), exist_ok=True)
open(os.path.join(ROOT, rel), "w", encoding="utf-8").write(open(src, encoding="utf-8").read().rstrip() + "\n")
p = idx["problems"].setdefault(slug, {"title": title, "first": at, "files": {}})
p["first"] = min(p["first"], at); p["last"] = max(p.get("last", 0), at)
p["files"][ext] = {"path": "leetcode/" + rel, "lang": lang, "at": at, "runtime": tc and "Time " + tc, "memory": sc and "Space " + sc, "manual": True}
idx["updated"] = int(time.time())
json.dump(idx, open(idx_path, "w"), indent=1, sort_keys=True)
print("added", rel)
