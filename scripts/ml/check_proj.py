"""Build every end-to-end project into a temp folder and verify it.
full/smoke: run the project's check commands; static: py_compile + pyflakes on every .py file.
usage: python3 check_proj.py [project-id ...]"""
import os, subprocess, sys, tempfile, time, shutil
sys.path.insert(0, os.path.dirname(__file__))
from ml_projects import PROJECTS

ENV = dict(os.environ, KERAS_BACKEND="torch", MPLBACKEND="Agg", PYTHONWARNINGS="ignore", TOKENIZERS_PARALLELISM="false", MLFLOW_DISABLE_AGENT_HINT="1",
           DATA_CACHE="/tmp/claude-0/data")


def materialise(p, d):
    for s in p["steps"]:
        if s["file"]:
            path = os.path.join(d, s["file"]); os.makedirs(os.path.dirname(path) or d, exist_ok=True)
            open(path, "w").write(s["code"])


def main(ids):
    bad = []
    for p in PROJECTS:
        if ids and p["id"] not in ids:
            continue
        d = tempfile.mkdtemp(prefix=p["id"] + "-"); materialise(p, d); t0 = time.time()
        pys = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if f.endswith(".py")]
        r = subprocess.run([sys.executable, "-m", "pyflakes", *pys], capture_output=True, text=True)
        issues = [l for l in r.stdout.splitlines() if "imported but unused" not in l and "redefinition of unused" not in l and "f-string is missing placeholders" not in l]
        if issues:
            bad.append(p["id"]); print("PYFLAKES", p["id"], *issues, sep="\n  ")
        if p["verify"] != "static":
            for cmd in p["check"]:
                r = subprocess.run(cmd, shell=True, cwd=d, env=ENV, capture_output=True, text=True, timeout=1500)
                if r.returncode:
                    bad.append(p["id"]); print("FAIL", p["id"], cmd, "\n", (r.stdout[-1500:] + r.stderr[-2500:])); break
                print(f"  {p['id']:24s} $ {cmd[:60]:60s} ok  | {(r.stdout.strip().splitlines() or [''])[-1][:90]}")
        print(f"{p['id']:24s} [{p['verify']}] {len(pys)} py files, {time.time() - t0:.0f}s")
        shutil.rmtree(d, ignore_errors=True)
    print("FAILED:", bad if bad else "none")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
