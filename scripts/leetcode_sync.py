"""Pulls your accepted LeetCode submissions (with code) into leetcode/ in this repo.
Runs in GitHub Actions with two repository secrets you add yourself: LEETCODE_SESSION and LEETCODE_CSRF_TOKEN.
Layout: leetcode/<slug>/<slug>.<ext>  +  leetcode/index.json (titles, first/last accepted time, files) read by the website.
Incremental: stops paging once it reaches a submission already recorded in index.json."""
import json, os, sys, time, urllib.request, urllib.error

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leetcode")
INDEX = os.path.join(ROOT, "index.json")
EXT = {"java": "java", "python3": "py", "python": "py", "cpp": "cpp", "c": "c", "javascript": "js", "typescript": "ts",
       "csharp": "cs", "golang": "go", "kotlin": "kt", "rust": "rs", "swift": "swift", "mysql": "sql", "mssql": "sql",
       "oraclesql": "sql", "postgresql": "sql", "ruby": "rb", "scala": "scala", "php": "php", "dart": "dart"}

session, csrf = os.environ.get("LEETCODE_SESSION", "").strip(), os.environ.get("LEETCODE_CSRF_TOKEN", "").strip()
if not session or not csrf:
    # Not set up yet: skip quietly (exit 0) so scheduled runs don't fail and email every 3 hours.
    print("LeetCode sync skipped: add LEETCODE_SESSION and LEETCODE_CSRF_TOKEN in Settings > Secrets and variables > Actions to enable it.")
    sys.exit(0)
HEAD = {"Cookie": f"LEETCODE_SESSION={session}; csrftoken={csrf}", "x-csrftoken": csrf, "Referer": "https://leetcode.com/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"}


def get(url, tries=4):
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD), timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                sys.exit(f"LeetCode refused the login ({e.code}). Your LEETCODE_SESSION has probably expired: copy fresh values and update the two secrets.")
            if t == tries - 1: raise
        except (urllib.error.URLError, TimeoutError):
            if t == tries - 1: raise
        time.sleep(3 * (t + 1))


idx = json.load(open(INDEX)) if os.path.exists(INDEX) else {"problems": {}, "seen": 0}
seen = idx.get("seen", 0)
offset, last_key, new = 0, "", []
while True:
    d = get(f"https://leetcode.com/api/submissions/?offset={offset}&limit=20&lastkey={last_key}")
    if offset == 0 and "submissions_dump" not in d:
        sys.exit("LeetCode did not return submissions. Your LEETCODE_SESSION has probably expired: update the secrets.")
    batch = d.get("submissions_dump", [])
    stop = False
    for s in batch:
        if int(s["id"]) <= seen: stop = True; break
        new.append(s)
    if stop or not d.get("has_next") or not batch: break
    offset += 20; last_key = d.get("last_key", ""); time.sleep(1.2)

added = 0
for s in sorted(new, key=lambda s: int(s["timestamp"])):          # oldest first, so later code overwrites earlier
    if s.get("status_display") != "Accepted": continue
    slug, ext = s["title_slug"], EXT.get(s["lang"], s["lang"])
    p = idx["problems"].setdefault(slug, {"title": s.get("title", slug), "first": int(s["timestamp"]), "files": {}})
    p["first"] = min(p["first"], int(s["timestamp"])); p["last"] = max(p.get("last", 0), int(s["timestamp"]))
    rel = f"{slug}/{slug}.{ext}"
    os.makedirs(os.path.join(ROOT, slug), exist_ok=True)
    open(os.path.join(ROOT, rel), "w", encoding="utf-8").write(s["code"].rstrip() + "\n")
    p["files"][ext] = {"path": "leetcode/" + rel, "lang": s["lang"], "at": int(s["timestamp"]),
                       "runtime": s.get("runtime", ""), "memory": s.get("memory", "")}
    added += 1
if new: idx["seen"] = max(seen, max(int(s["id"]) for s in new))
idx["updated"] = int(time.time())
os.makedirs(ROOT, exist_ok=True)
json.dump(idx, open(INDEX, "w"), indent=1, sort_keys=True)
print(f"{len(new)} new submissions checked, {added} accepted saved, {len(idx['problems'])} problems in total")
