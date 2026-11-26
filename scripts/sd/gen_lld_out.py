"""Compile and run every LLD solution and save its real output to sd_lld_out.json (shown under each LLD explanation)."""
import os, re, subprocess, sys, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sd_lld1 import LLD1
from sd_lld2 import LLD2
from sd_lld3 import LLD3
env = dict(os.environ, JAVA_TOOL_OPTIONS="")
tmp = tempfile.mkdtemp(); out = {}
for q in LLD1 + LLD2 + LLD3:
    cls = re.search(r"public class (\w+)", q["code"]).group(1)
    d = os.path.join(tmp, cls); os.makedirs(d)
    open(os.path.join(d, cls + ".java"), "w").write(q["code"])
    r = subprocess.run(["javac", "-d", d, os.path.join(d, cls + ".java")], capture_output=True, text=True, env=env)
    assert r.returncode == 0, (q["id"], r.stderr[:800])
    r = subprocess.run(["java", "-cp", d, cls], capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 0, (q["id"], r.stderr[:800])
    out[q["id"]] = r.stdout.rstrip()
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sd_lld_out.json"), "w"), indent=1, ensure_ascii=False)
print(len(out), "outputs saved")
