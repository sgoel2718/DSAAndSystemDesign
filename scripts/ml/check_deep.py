"""Run every concept's end-to-end walkthrough. usage: python3 check_deep.py [module ...] [--only id]"""
import importlib, os, subprocess, sys, tempfile, time, ast
sys.path.insert(0, os.path.dirname(__file__))
ENV = dict(os.environ, KERAS_BACKEND="torch", MPLBACKEND="Agg", PYTHONWARNINGS="ignore", TOKENIZERS_PARALLELISM="false", HF_HUB_OFFLINE="1",
           TRANSFORMERS_VERBOSITY="error", MLFLOW_DISABLE_AGENT_HINT="1", NLTK_ALLOW_PROXIED_URLOPEN="1", PYTHONPATH="/tmp/claude-0/sitecache")
MODS = ["d_py", "d_stats", "d_math", "d_found", "d_sup", "d_unsup", "d_dl", "d_cv", "d_nlp", "d_gen", "d_ops"]


def main(argv):
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    mods = [a for a in argv if not a.startswith("--") and a != only] or MODS
    bad = []
    for m in mods:
        try: importlib.import_module("deep." + m)
        except ModuleNotFoundError as e: print("skip", m, e); continue
    from deep.util import D
    for cid, d in D.items():
        if only and cid != only: continue
        try: ast.parse(d["code"])
        except SyntaxError as e: bad.append(cid); print("SYNTAX", cid, e); continue
        if d["net"]:
            f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False); f.write(d["code"]); f.close()
            r = subprocess.run([sys.executable, "-m", "pyflakes", f.name], capture_output=True, text=True)
            iss = [l for l in r.stdout.splitlines() if "imported but unused" not in l]
            print(f"  {cid:28s} static {'ok' if not iss else iss}"); bad += [cid] if iss else []; continue
        t = time.time(); dd = tempfile.mkdtemp()
        p = subprocess.run([sys.executable, "-c", d["code"]], cwd=dd, env=ENV, capture_output=True, text=True, timeout=900)
        if p.returncode: bad.append(cid); print("FAIL", cid, p.stderr[-1500:])
        else:
            if "--show" in sys.argv: print(p.stdout)
            print(f"  {cid:28s} ok {time.time() - t:5.1f}s | {(p.stdout.strip().splitlines() or [''])[-1][:100]}")
    print(len(D), "walkthroughs; failed:", bad or "none")


if __name__ == "__main__":
    main(sys.argv[1:])
