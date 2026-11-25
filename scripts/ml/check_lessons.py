"""Run every beginner-lesson code snippet in a fresh process.  usage: python3 check_lessons.py [l_module ...]"""
import importlib, os, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lesson_util
ENV = dict(os.environ, KERAS_BACKEND="torch", MPLBACKEND="Agg", PYTHONWARNINGS="ignore", HF_HUB_OFFLINE="1")
mods = sys.argv[1:] or sorted(m[:-3] for m in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lessons")) if m.startswith("l_"))
bad = 0
for mod in mods:
    before = set(lesson_util.LESSONS)
    importlib.import_module("lessons." + mod)
    for lid in [k for k in lesson_util.LESSONS if k not in before]:
        L = lesson_util.LESSONS[lid]
        if L.get("net"):
            compile(L["code"], lid, "exec"); print(f"  {lid:28s} syntax ok (net)"); continue
        t = time.time()
        p = subprocess.run([sys.executable, "-c", L["code"]], cwd=tempfile.mkdtemp(), env=ENV, capture_output=True, text=True, timeout=600)
        if p.returncode:
            bad += 1; print("FAIL", lid, p.stderr[-800:])
        else:
            print(f"  {lid:28s} ok {time.time()-t:4.1f}s  {(p.stdout.strip().splitlines() or [''])[-1][:80]}")
print(len(lesson_util.LESSONS), "lessons,", bad, "failed"); sys.exit(1 if bad else 0)
