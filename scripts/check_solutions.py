"""Compiles every Java approach in solutions_data.py with javac. Fails loudly on any error."""
import os, re, subprocess, sys, tempfile
from solutions_data import SOLUTIONS

# Runtime tests per problem: list of (java-args-expression, expected toString). {m} = method name.
TESTS = {
 "two-sum": [("new int[]{2,7,11,15}, 9", "[0, 1]"), ("new int[]{3,2,4}, 6", "[1, 2]"), ("new int[]{3,3}, 6", "[0, 1]")],
 "two-sum-ii-input-array-is-sorted": [("new int[]{2,7,11,15}, 9", "[1, 2]"), ("new int[]{2,3,4}, 6", "[1, 3]"), ("new int[]{-1,0}, -1", "[1, 2]")],
 "contains-duplicate": [("new int[]{1,2,3,1}", "true"), ("new int[]{1,2,3,4}", "false"), ("new int[]{}", "false")],
 "fizz-buzz": [("3", "[1, 2, Fizz]"), ("15", "[1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz]")],
 "richest-customer-wealth": [("new int[][]{{1,5},{7,3},{3,5}}", "10"), ("new int[][]{{2,8,7},{7,1,3},{1,9,5}}", "17")],
}
# Approaches that legitimately return something different (values instead of indices)
OVERRIDE = {("two-sum", "twoSumValues"): [("new int[]{2,7,11,15}, 9", "[2, 7]"), ("new int[]{3,2,4}, 6", "[2, 4]")]}

def show(expr):
    return f"(r instanceof int[] a ? Arrays.toString(a) : String.valueOf(r))"

tmp = tempfile.mkdtemp()
files, classes = [], []
for slug, apps in SOLUTIONS.items():
    assert slug in TESTS, f"no tests for {slug}"
    for i, a in enumerate(apps):
        cls = "S_" + re.sub(r"\W", "_", slug) + f"_{i}"
        m = re.search(r"public\s+[\w<>\[\]]+\s+(\w+)\s*\(", a["code"]).group(1)
        cases = OVERRIDE.get((slug, m), TESTS[slug])
        body = "\n".join(
            f'        {{ Object r = new {cls}().{m}({args}); String got = (r instanceof int[] a ? Arrays.toString(a) : String.valueOf(r));'
            f' if (!got.equals("{want}")) throw new AssertionError("{slug} / {a["name"]}: got " + got + " want {want}"); }}'
            for args, want in cases)
        src = (f"import java.util.*;\nimport java.util.stream.*;\n\npublic class {cls} {{\n{a['code']}\n\n"
               f"    public static void main(String[] x) {{\n{body}\n    }}\n}}\n")
        p = os.path.join(tmp, cls + ".java")
        open(p, "w").write(src)
        files.append(p); classes.append(cls)
env = dict(os.environ, JAVA_TOOL_OPTIONS="")
r = subprocess.run(["javac", "-d", tmp] + files, capture_output=True, text=True, env=env)
err = "\n".join(l for l in r.stderr.splitlines() if "Picked up" not in l)
if r.returncode != 0:
    print(err); sys.exit(1)
# run all mains in one JVM via a tiny launcher
launcher = os.path.join(tmp, "RunAll.java")
open(launcher, "w").write("public class RunAll { public static void main(String[] a) throws Exception {\n" +
    "".join(f"  {c}.main(null);\n" for c in classes) + "} }\n")
subprocess.run(["javac", "-cp", tmp, "-d", tmp, launcher], check=True, env=env, capture_output=True)
r = subprocess.run(["java", "-cp", tmp, "RunAll"], capture_output=True, text=True, env=env)
if r.returncode != 0:
    print("\n".join(l for l in r.stderr.splitlines() if "Picked up" not in l)); sys.exit(1)
n_cases = sum(len(OVERRIDE.get((s, re.search(r"public\s+[\w<>\[\]]+\s+(\w+)\s*\(", a["code"]).group(1)), TESTS[s])) for s, apps in SOLUTIONS.items() for a in apps)
print(f"OK: {len(files)} Java approaches for {len(SOLUTIONS)} problems compiled and passed {n_cases} test runs")
