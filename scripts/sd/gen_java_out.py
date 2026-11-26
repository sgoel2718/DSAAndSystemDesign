"""Compile and run every System Design Java practice program; save real outputs to sd_java_out.json
and write the sources to java-practice/system-design/<tab>/ in the repo so they can be opened in an IDE."""
import os, sys, glob, json, hashlib, importlib, subprocess, tempfile, shutil
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
from sd_j_util import JAVA
for f in sorted(glob.glob(os.path.join(here, "sd_j_*.py"))):
    m = os.path.basename(f)[:-3]
    if m != "sd_j_util": importlib.import_module(m)
env = dict(os.environ, JAVA_TOOL_OPTIONS="")
out_f = os.path.join(here, "sd_java_out.json")
old = json.load(open(out_f)) if os.path.exists(out_f) else {}
classes = {}
for id, j in JAVA.items():
    assert j["cls"] not in classes, f"class name {j['cls']} used by {classes[j['cls']]} and {id}"
    classes[j["cls"]] = id
only = set(sys.argv[1:])


def run(item):
    id, j = item
    h = hashlib.sha1(j["code"].encode()).hexdigest()
    if id in old and old[id]["h"] == h and (not only or id not in only): return id, old[id], None
    d = tempfile.mkdtemp(); src = os.path.join(d, j["cls"] + ".java"); open(src, "w").write(j["code"])
    r = subprocess.run(["javac", "-Xlint:none", "-d", d, src], capture_output=True, text=True, env=env)
    if r.returncode: return id, None, "COMPILE " + r.stderr[:1500]
    try: r = subprocess.run(["java", "-cp", d, j["cls"]], capture_output=True, text=True, env=env, timeout=90)
    except subprocess.TimeoutExpired: return id, None, "TIMEOUT"
    shutil.rmtree(d, ignore_errors=True)
    if r.returncode: return id, None, "RUN " + r.stderr[:1500]
    return id, dict(h=h, out=r.stdout.rstrip()), None


res, errs = {}, []
with ThreadPoolExecutor(8) as ex:
    for id, v, e in ex.map(run, JAVA.items()):
        if e: errs.append((id, e))
        else: res[id] = v
for id, e in errs: print("✘", id, e, "\n")
json.dump(res, open(out_f, "w"), indent=1, ensure_ascii=False)
print(len(res), "ok,", len(errs), "failed, of", len(JAVA))
