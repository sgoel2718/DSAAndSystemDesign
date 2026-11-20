"""Run every Python snippet in the ML course (concept cards + labs) in a fresh process.
usage: python3 check_ml.py [module_name ...]   (default: all)"""
import importlib, os, subprocess, sys, tempfile, textwrap, time, ast
sys.path.insert(0, os.path.dirname(__file__))

MODS = ["ml_py", "ml_math", "ml_m1", "ml_sup", "ml_unsup", "ml_dl", "ml_cv", "ml_nlp", "ml_adv", "ml_ops", "ml_labs"]
ENV = dict(os.environ, KERAS_BACKEND="torch", MPLBACKEND="Agg", PYTHONWARNINGS="ignore", TOKENIZERS_PARALLELISM="false",
           HF_HUB_OFFLINE="1", TRANSFORMERS_VERBOSITY="error", MLFLOW_DISABLE_AGENT_HINT="1")


def items(mod):
    m = importlib.import_module(mod)
    for name in dir(m):
        v = getattr(m, name)
        if isinstance(v, list) and v and isinstance(v[0], dict) and "code" in v[0]:
            for c in v:
                yield c


def main(argv):
    mods = argv or MODS
    bad, n = [], 0
    for mod in mods:
        try:
            its = list(items(mod))
        except ModuleNotFoundError as e:
            print("skip", mod, e); continue
        for c in its:
            code = c.get("code") or ""
            if not code.strip():
                continue
            n += 1
            try:
                ast.parse(code)
            except SyntaxError as e:
                bad.append((c["id"], "syntax " + str(e))); print("SYNTAX", c["id"], e); continue
            if c.get("net"):
                print(f"  {c['id']:34s} syntax ok (needs internet/API)"); continue
            d = tempfile.mkdtemp(prefix="mlchk")
            t = time.time()
            p = subprocess.run([sys.executable, "-c", code], cwd=d, env=ENV, capture_output=True, text=True, timeout=600)
            dt = time.time() - t
            if p.returncode:
                bad.append((c["id"], p.stderr[-1500:])); print("FAIL", c["id"], "\n", textwrap.indent(p.stderr[-1500:], "    "))
            else:
                last = (p.stdout.strip().splitlines() or [""])[-1][:70]
                print(f"  {c['id']:34s} ok {dt:5.1f}s  {last}")
    print(f"\n{n} snippets, {len(bad)} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
