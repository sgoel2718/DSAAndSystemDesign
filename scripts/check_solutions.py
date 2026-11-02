"""Generates one Java file per problem (all approaches as nested classes + a main() with tests),
compiles and runs every file. Usage:
    python3 check_solutions.py                 # check only (temp dir)
    python3 check_solutions.py <repo_days_dir> # also write days/day-NN/solutions/<Problem>.java
Fails loudly on any compile error or wrong answer."""
import os, re, shutil, subprocess, sys, tempfile
from solutions_data import SOLUTIONS
import plan_data

# Test cases: (args, expected). args starting with "!" is a raw Java block using `o` (the instance) and {m}
# (method name) that must assign `r`.
TESTS = {
 "two-sum": [("new int[]{2,7,11,15}, 9", "[0, 1]"), ("new int[]{3,2,4}, 6", "[1, 2]"), ("new int[]{3,3}, 6", "[0, 1]")],
 "two-sum-ii-input-array-is-sorted": [("new int[]{2,7,11,15}, 9", "[1, 2]"), ("new int[]{2,3,4}, 6", "[1, 3]"), ("new int[]{-1,0}, -1", "[1, 2]")],
 "contains-duplicate": [("new int[]{1,2,3,1}", "true"), ("new int[]{1,2,3,4}", "false"), ("new int[]{}", "false")],
 "fizz-buzz": [("3", "[1, 2, Fizz]"), ("15", "[1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz]")],
 "richest-customer-wealth": [("new int[][]{{1,5},{7,3},{3,5}}", "10"), ("new int[][]{{2,8,7},{7,1,3},{1,9,5}}", "17")],
 # ---- Day 2 ----
 "best-time-to-buy-and-sell-stock": [("new int[]{7,1,5,3,6,4}", "5"), ("new int[]{7,6,4,3,1}", "0"), ("new int[]{2,4,1}", "2")],
 "container-with-most-water": [("new int[]{1,8,6,2,5,4,8,3,7}", "49"), ("new int[]{1,1}", "1")],
 "3sum": [("!r = norm(o.{m}(new int[]{-1,0,1,2,-1,-4}));", "[[-1, -1, 2], [-1, 0, 1]]"),
          ("!r = norm(o.{m}(new int[]{0,0,0,0}));", "[[0, 0, 0]]"), ("!r = norm(o.{m}(new int[]{0,1,1}));", "[]")],
 "longest-substring-without-repeating-characters": [('"abcabcbb"', "3"), ('"bbbbb"', "1"), ('"pwwkew"', "3"), ('""', "0"), ('"abba"', "2")],
 "maximum-subarray": [("new int[]{-2,1,-3,4,-1,2,1,-5,4}", "6"), ("new int[]{5,4,-1,7,8}", "23"), ("new int[]{-3,-1,-2}", "-1")],
 "product-of-array-except-self": [("new int[]{1,2,3,4}", "[24, 12, 8, 6]"), ("new int[]{-1,1,0,-3,3}", "[0, 0, 9, 0, 0]")],
 "minimum-window-substring": [('"ADOBECODEBANC", "ABC"', "BANC"), ('"a", "a"', "a"), ('"a", "aa"', "")],
 "trapping-rain-water": [("new int[]{0,1,0,2,1,0,1,3,2,1,2,1}", "6"), ("new int[]{4,2,0,3,2,5}", "9"), ("new int[]{}", "0")],
 "spiral-matrix": [("new int[][]{{1,2,3},{4,5,6},{7,8,9}}", "[1, 2, 3, 6, 9, 8, 7, 4, 5]"),
                   ("new int[][]{{1,2,3,4},{5,6,7,8},{9,10,11,12}}", "[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]"),
                   ("new int[][]{{1},{2},{3}}", "[1, 2, 3]")],
 "rotate-image": [("!int[][] a = {{1,2,3},{4,5,6},{7,8,9}}; o.{m}(a); r = a;", "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]"),
                  ("!int[][] a = {{5,1,9,11},{2,4,8,10},{13,3,6,7},{15,14,12,16}}; o.{m}(a); r = a;",
                   "[[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]"),
                  ("!int[][] a = {{1}}; o.{m}(a); r = a;", "[[1]]")],
 "set-matrix-zeroes": [("!int[][] a = {{1,1,1},{1,0,1},{1,1,1}}; o.{m}(a); r = a;", "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]"),
                       ("!int[][] a = {{0,1,2,0},{3,4,5,2},{1,3,1,5}}; o.{m}(a); r = a;", "[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]")],
 "missing-number": [("new int[]{3,0,1}", "2"), ("new int[]{0,1}", "2"), ("new int[]{9,6,4,2,3,5,7,0,1}", "8")],
 "find-all-duplicates-in-an-array": [("!r = sorted(o.{m}(new int[]{4,3,2,7,8,2,3,1}));", "[2, 3]"),
                                     ("!r = sorted(o.{m}(new int[]{1,1,2}));", "[1]"), ("!r = sorted(o.{m}(new int[]{1}));", "[]")],
 "first-missing-positive": [("new int[]{1,2,0}", "3"), ("new int[]{3,4,-1,1}", "2"), ("new int[]{7,8,9,11,12}", "1"), ("new int[]{1,1}", "2")],
}
OVERRIDE = {("two-sum", "twoSumValues"): [("new int[]{2,7,11,15}, 9", "[2, 7]"), ("new int[]{3,2,4}, 6", "[2, 4]")]}

HELPERS = """
    static String show(Object r) {
        if (r instanceof int[] a) return Arrays.toString(a);
        if (r instanceof int[][] a) return Arrays.deepToString(a);
        return String.valueOf(r);
    }
    static String norm(List<List<Integer>> x) {                 // order-independent view of a list of lists
        List<List<Integer>> c = new ArrayList<>();
        for (List<Integer> t : x) { List<Integer> s = new ArrayList<>(t); Collections.sort(s); c.add(s); }
        c.sort((p, q) -> { for (int i = 0; i < Math.min(p.size(), q.size()); i++) { int d = Integer.compare(p.get(i), q.get(i)); if (d != 0) return d; } return p.size() - q.size(); });
        return c.toString();
    }
    static String sorted(List<Integer> x) { List<Integer> c = new ArrayList<>(x); Collections.sort(c); return c.toString(); }
    static int passed = 0;
    static void check(String what, Object r, String want) {
        String got = show(r);
        if (!got.equals(want)) throw new AssertionError(what + ": got " + got + ", want " + want);
        passed++;
    }
"""


NAMES = {"3sum": "ThreeSum", "two-sum-ii-input-array-is-sorted": "TwoSumII", "4sum": "FourSum"}


def class_name(slug):
    if slug in NAMES:
        return NAMES[slug]
    words = re.split(r"[^a-zA-Z0-9]+", slug)
    name = "".join(w[:1].upper() + w[1:] for w in words if w)
    return ("Problem" + name) if name[0].isdigit() else name


def method_name(code):
    return re.search(r"public\s+[\w<>\[\], ]+?\s+(\w+)\s*\(", code).group(1)


def problem_day():
    where = {}
    for d in plan_data.DAYS:
        for name, slug, diff in d["problems"]:
            where.setdefault(slug, (d["day"], name, diff))
    return where


def java_source(slug, apps, title, day, diff):
    cls = class_name(slug)
    parts = [f"import java.util.*;\nimport java.util.stream.*;\n\n/**\n * {title} ({diff}) - Day {day}\n"
             f" * https://leetcode.com/problems/{slug}/\n *\n"]
    for i, a in enumerate(apps, 1):
        parts.append(f" * Approach {i}: {a['name']}  |  Time {a['time']}  |  Space {a['space']}{'  <- best' if a.get('best') else ''}\n")
    parts.append(f" *\n * Run: javac {cls}.java && java {cls}\n */\npublic class {cls} {{\n")
    for i, a in enumerate(apps, 1):
        body = "\n".join("        " + ln if ln.strip() else "" for ln in a["code"].splitlines())
        parts.append(f"\n    // Approach {i}: {a['name']}\n    // Time {a['time']}, Space {a['space']}\n"
                     f"    // Idea: {a['idea']}\n    static class Approach{i} {{\n{body}\n    }}\n")
    parts.append(HELPERS)
    parts.append("\n    public static void main(String[] args) {\n")
    for i, a in enumerate(apps, 1):
        m = method_name(a["code"])
        for args, want in OVERRIDE.get((slug, m), TESTS[slug]):
            label = f"Approach {i}"
            if args.startswith("!"):
                block = args[1:].replace("{m}", m)
                parts.append(f"        {{ Approach{i} o = new Approach{i}(); Object r; {block} check(\"{label}\", r, \"{want}\"); }}\n")
            else:
                parts.append(f"        check(\"{label}\", new Approach{i}().{m}({args}), \"{want}\");\n")
    parts.append(f'        System.out.println("{cls}: all {len(apps)} approaches passed " + passed + " checks");\n    }}\n}}\n')
    return cls, "".join(parts)


def main():
    out_root = sys.argv[1] if len(sys.argv) > 1 else None
    where = problem_day()
    tmp = tempfile.mkdtemp()
    src_dir = os.path.join(tmp, "src"); os.makedirs(src_dir)
    written = []
    for slug, apps in SOLUTIONS.items():
        assert slug in TESTS, f"no tests for {slug}"
        day, title, diff = where[slug]
        cls, src = java_source(slug, apps, title, day, diff)
        p = os.path.join(src_dir, cls + ".java")
        open(p, "w").write(src)
        written.append((cls, p, day))
    env = dict(os.environ, JAVA_TOOL_OPTIONS="")
    total = 0
    for cls, p, day in written:
        d = os.path.join(tmp, "bin_" + cls); os.makedirs(d)
        r = subprocess.run(["javac", "-d", d, p], capture_output=True, text=True, env=env)
        if r.returncode:
            print(cls, "\n", "\n".join(l for l in r.stderr.splitlines() if "Picked up" not in l)); sys.exit(1)
        r = subprocess.run(["java", "-cp", d, cls], capture_output=True, text=True, env=env)
        if r.returncode:
            print(cls, "\n", "\n".join(l for l in r.stderr.splitlines() if "Picked up" not in l)); sys.exit(1)
        total += int(re.search(r"passed (\d+) checks", r.stdout).group(1))
        if out_root:
            dest = os.path.join(out_root, f"day-{day:02d}", "solutions")
            os.makedirs(dest, exist_ok=True)
            shutil.copy(p, dest)
    n_app = sum(len(a) for a in SOLUTIONS.values())
    print(f"OK: {n_app} Java approaches for {len(SOLUTIONS)} problems compiled and passed {total} checks")


if __name__ == "__main__":
    main()
