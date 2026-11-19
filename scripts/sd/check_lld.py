import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sd_lld1 import LLD1
from sd_lld2 import LLD2
env = dict(os.environ, JAVA_TOOL_OPTIONS="")
tmp = tempfile.mkdtemp(); bad = 0
for q in LLD1 + LLD2:
    cls = re.search(r"public class (\w+)", q["code"]).group(1)
    d = os.path.join(tmp, cls); os.makedirs(d)
    open(os.path.join(d, cls + ".java"), "w").write(q["code"])
    r = subprocess.run(["javac", "-d", d, os.path.join(d, cls + ".java")], capture_output=True, text=True, env=env)
    if r.returncode: bad += 1; print("COMPILE FAIL", q["id"], r.stderr[:1500]); continue
    r = subprocess.run(["java", "-cp", d, cls], capture_output=True, text=True, env=env, timeout=30)
    print(f"== {q['id']} (exit {r.returncode})\n{r.stdout.strip()}\n{r.stderr.strip()[:500]}")
    bad += r.returncode != 0
print("FAILURES:", bad)
