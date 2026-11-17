"""Builds step-by-step traces for every approach by running the real Java code under the debugger (Tracer.java).
For each approach: a harness class runs the first test case, Tracer records each executed line with all local variables.
Output: viz/traces/<slug>.json = {"approaches":[{"input":..., "steps":[...], "truncated":bool, "line0":k}, ...]}
Steps are delta-encoded: each step stores only variables that changed ("v") and names that went out of scope ("x").
Usage: python3 viz/make_traces.py [slug ...]"""
import json, os, re, subprocess, sys, tempfile, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from solutions_data import SOLUTIONS
import check_solutions as cs

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "traces")
MAX_STEPS = 220
ENV = dict(os.environ, JAVA_TOOL_OPTIONS="")

FMT = """
    public static String fmt(Object o) {                         // called by the debugger to show collections readably
        String s;
        if (o == null) s = "null";
        else if (o instanceof int[][] a) s = Arrays.deepToString(a);
        else if (o instanceof Object[] a) s = Arrays.deepToString(a);
        else if (o instanceof Map<?, ?> m) {
            StringBuilder b = new StringBuilder("{");
            for (Map.Entry<?, ?> e : m.entrySet()) { if (b.length() > 1) b.append(", "); b.append(fmt(e.getKey())).append("=").append(fmt(e.getValue())); }
            s = b.append("}").toString();
        } else if (o instanceof PriorityQueue<?> pq) {
            List<Object> c = new ArrayList<>(pq);
            StringBuilder b = new StringBuilder("heap[");
            for (int i = 0; i < c.size(); i++) { if (i > 0) b.append(", "); b.append(fmt(c.get(i))); }
            s = b.append("]").toString();
        } else if (o instanceof Collection<?> c) {
            StringBuilder b = new StringBuilder(o instanceof Deque ? "top->[" : "[");
            int i = 0;
            for (Object x : c) { if (i++ > 0) b.append(", "); b.append(fmt(x)); }
            s = b.append("]").toString();
        } else if (o instanceof int[] a) s = Arrays.toString(a);
        else if (o instanceof long[] a) s = Arrays.toString(a);
        else if (o instanceof char[] a) s = new String(a);
        else if (o instanceof ListNode n) s = "Node(" + n.val + ")";
        else s = String.valueOf(o);
        return s.length() > 300 ? s.substring(0, 297) + "..." : s;
    }
"""


def harness(slug, i, a, case):
    """Java source: approach i as a nested class + helpers + main that runs one test case."""
    cls = f"T_{re.sub(r'[^A-Za-z0-9]', '_', slug)}_{i}"
    m = cs.method_name(a["code"])
    args, _ = case
    body = args[1:].replace("{m}", m) if args.startswith("!") else f"r = o.{m}({args});"
    code_lines = a["code"].splitlines()
    head = f"import java.util.*;\nimport java.util.stream.*;\n\npublic class {cls} {{\n    static class Approach {{\n"
    line0 = head.count("\n") + 1                       # first line of the approach code in the file
    src = head + "\n".join(code_lines) + "\n    }\n" + cs.HELPERS + FMT + \
        f"\n    public static void main(String[] mainArgs) {{ Approach o = new Approach(); Object r; {body} System.out.println(show(r)); }}\n}}\n"
    return cls, src, line0, args


def describe(args):
    if not args.startswith("!"):
        a = "solve(" + args + ")"
    else:
        a = re.sub(r"\bo\.\{m\}\(", "solve(", args[1:])
        a = re.sub(r"\s*r\s*=\s*[^;]*;\s*$", "", a) if "solve(" in re.sub(r"r\s*=.*$", "", a) else a
        a = re.sub(r"\br\s*=\s*", "", a)
        for w in ("toList(", "norm(", "sorted("):
            while w in a:
                i = a.index(w); depth = 0
                for j in range(i + len(w) - 1, len(a)):
                    depth += a[j] == "("; depth -= a[j] == ")"
                    if depth == 0: break
                a = a[:i] + a[i + len(w):j] + a[j + 1:]
        a = re.sub(r"ListNode |int\[\]\[\] |int\[\] |char\[\] |int (?=\w+ = solve)", "", a)
        a = a.strip().rstrip(";")
    a = a.replace("new int[][][]", "").replace("new int[][]", "").replace("new int[]", "").replace("new String[]", "")
    a = a.replace("Approach o = new Approach(); ", "")
    return a.strip()


def trace_one(slug, i, a, tmp):
    cases = cs.OVERRIDE.get((slug, cs.method_name(a["code"])), cs.TESTS[slug])
    cls, src, line0, args = harness(slug, i, a, cases[0])
    d = os.path.join(tmp, cls)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, cls + ".java")
    open(p, "w").write(src)
    r = subprocess.run(["javac", "-g", "-d", d, p], capture_output=True, text=True, env=ENV)
    if r.returncode:
        raise RuntimeError(f"{slug}#{i} compile: {r.stderr[:500]}")
    out = os.path.join(d, "trace.json")
    r = subprocess.run(["java", "-cp", HERE, "Tracer", d, cls, cls + "$Approach", str(MAX_STEPS), out],
                       capture_output=True, text=True, env=ENV, timeout=180)
    if r.returncode or not os.path.exists(out):
        raise RuntimeError(f"{slug}#{i} trace: {r.stderr[-800:]}")
    raw = json.load(open(out))
    res = subprocess.run(["java", "-cp", d, cls], capture_output=True, text=True, env=ENV, timeout=60).stdout.strip()
    # delta-encode variables
    prev, steps = {}, []
    for s in raw["steps"]:
        v = s["v"]
        st = {"l": s["l"] - line0 + 1, "d": s["d"]}
        if s["m"] != cs.method_name(a["code"]):
            st["m"] = s["m"]
        ch = {k: val for k, val in v.items() if prev.get(k, object()) != val}
        gone = [k for k in prev if k not in v]
        if "ret" in s: st["ret"] = s["ret"]
        if ch: st["v"] = ch
        if gone: st["x"] = gone
        steps.append(st)
        prev = v
    return {"input": describe(args), "result": res, "steps": steps, "truncated": raw["truncated"]}


def main():
    want = sys.argv[1:] or list(SOLUTIONS)
    os.makedirs(OUT, exist_ok=True)
    subprocess.run(["javac", "-d", HERE, os.path.join(HERE, "Tracer.java")], check=True, env=ENV, capture_output=True)
    tmp = tempfile.mkdtemp()
    jobs = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for slug in want:
            for i, a in enumerate(SOLUTIONS[slug]):
                jobs[ex.submit(trace_one, slug, i, a, tmp)] = (slug, i)
        results, errors = {}, []
        for fut in cf.as_completed(jobs):
            slug, i = jobs[fut]
            try:
                results[(slug, i)] = fut.result()
            except Exception as e:
                errors.append(str(e))
    total_steps = 0
    for slug in want:
        apps = [results.get((slug, i)) for i in range(len(SOLUTIONS[slug]))]
        total_steps += sum(len(a["steps"]) for a in apps if a)
        json.dump({"approaches": apps}, open(os.path.join(OUT, slug + ".json"), "w"), separators=(",", ":"))
    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"traced {len(results)} approaches, {total_steps} steps, {len(errors)} errors, traces dir {size/1e6:.1f} MB")
    for e in errors[:20]:
        print("ERR", e)


if __name__ == "__main__":
    main()
