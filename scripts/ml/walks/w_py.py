"""Real-data walkthroughs: Python and the scientific libraries (tips + Titanic)."""
import io, os, sys, json, csv, tempfile, platform
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt, DATA


@walk("m-setup", "tips")
def _():
    import sklearn, scipy, matplotlib
    path = os.path.join(DATA, "tips.csv")
    with open(path) as f: head = [next(f).rstrip() for _ in range(4)]
    vers = pd.DataFrame([{"package": n, "version": v} for n, v in [("Python", platform.python_version()), ("numpy", np.__version__), ("pandas", pd.__version__), ("scikit-learn", sklearn.__version__), ("scipy", scipy.__version__), ("matplotlib", matplotlib.__version__)]])
    return [
        ("Check what you're running", f"In a notebook cell (Colab or VS Code): `import sys, numpy, pandas; print(sys.version, numpy.__version__)`. This course's numbers were produced with:\n\n{t(vers)}\n\nWrite these into `requirements.txt` so others can reproduce your results."),
        ("Get the data file", f"The restaurant-tips data is a plain text CSV file ({os.path.getsize(path):,} bytes). Its first lines:\n\n```\n" + "\n".join(head) + "\n```\n\nIn Colab, upload it or read it straight from a URL with `pd.read_csv(url)`."),
        ("First command that does something", f"`df = pd.read_csv('tips.csv'); df.shape` → **{D('tips').shape}**: {D('tips').shape[0]} bills and {D('tips').shape[1]} columns. If that works, your environment is ready."),
    ], "Set-up = a Python environment with pinned library versions, a place to run code (notebook or editor) and the data file loaded."


@walk("m-py-basics", "tips")
def _():
    df = D("tips"); rows = df.head(5).to_dict("records")
    trace = []; total = 0.0; big = 0
    for i, r in enumerate(rows):
        total = total + r["total_bill"]
        if r["tip"] / r["total_bill"] >= 0.15: big += 1
        trace.append({"loop step i": i, "bill": r["total_bill"], "tip": r["tip"], "tip % = tip / bill × 100": round(100 * r["tip"] / r["total_bill"], 1), "≥ 15%?": r["tip"] / r["total_bill"] >= 0.15, "running total": round(total, 2)})
    return [
        ("Variables hold values", f"`bill = {rows[0]['total_bill']}` and `tip = {rows[0]['tip']}` store the first real bill. `tip / bill * 100` → **{100 * rows[0]['tip'] / rows[0]['total_bill']:.1f}** (a float)."),
        ("A for loop with an if", "```python\ntotal = 0\nbig = 0\nfor i, r in enumerate(rows):\n    total = total + r['total_bill']\n    if r['tip'] / r['total_bill'] >= 0.15:\n        big += 1\n```\n\nWhat happens on each pass, with the first 5 real bills:\n\n" + t(pd.DataFrame(trace))),
        ("Result", f"After the loop: `total` = **{total:.2f}**, `big` = **{big}** of 5 bills tipped at least 15%. The same loop over all {len(df)} bills: {int((df['tip'] / df['total_bill'] >= 0.15).sum())} of them."),
    ], "Python basics are variables, arithmetic, loops and conditions; tracing them line by line on real rows shows exactly what the code does."


@walk("m-py-datatypes", "tips")
def _():
    df = D("tips")
    bills = df["total_bill"].head(6).tolist(); days = df["day"].tolist()
    count = {}
    for d in days: count[d] = count.get(d, 0) + 1
    r0 = df.iloc[0]; first = (float(r0["total_bill"]), float(r0["tip"]), r0["day"])
    return [
        ("list: ordered, changeable", f"`bills = {bills}` (first 6 real bills). `bills[0]` → {bills[0]}, `bills[-1]` → {bills[-1]}, `len(bills)` → {len(bills)}, `sorted(bills)` → {sorted(bills)}, `sum(bills)` → {sum(bills):.2f}."),
        ("dict: look things up by key", f"Counting bills per day with a dict:\n\n```python\ncount = {{}}\nfor d in days:\n    count[d] = count.get(d, 0) + 1\n```\n\n→ `{count}`. `count['Sat']` → {count['Sat']}."),
        ("set, tuple, str", f"`set(days)` → {sorted(set(days))} (duplicates removed; order not guaranteed). A row as a tuple (fixed, can't change): `{first}`. Strings: `'Sun'.upper()` → 'SUN', `f'{{bills[0]:.1f}}'` → '{bills[0]:.1f}'. Types: `type({bills[0]})` is float, `type({count['Sat']})` is int."),
    ], "Choose the container for the job: list for sequences, dict for lookups and counts, set for unique values, tuple for fixed records."


@walk("m-py-functions", "tips")
def _():
    df = D("tips")

    def tip_pct(bill, tip, nd=1):
        """Tip as a percentage of the bill."""
        return round(100 * tip / bill, nd)
    ex = [(r.total_bill, r.tip) for r in df.head(3).itertuples()]
    by = df.assign(p=[tip_pct(b, t_) for b, t_ in zip(df.total_bill, df.tip)]).groupby("time")["p"].mean().round(1)
    top = sorted(df.head(8).itertuples(), key=lambda r: r.tip / r.total_bill, reverse=True)[:3]
    return [
        ("Define once", "```python\ndef tip_pct(bill, tip, nd=1):\n    \"\"\"Tip as a percentage of the bill.\"\"\"\n    return round(100 * tip / bill, nd)\n```\n\n`bill` and `tip` are parameters; `nd=1` has a default value."),
        ("Call it on real bills", "\n".join(f"- `tip_pct({b}, {t_})` → **{tip_pct(b, t_)}**" for b, t_ in ex) + f"\n- `tip_pct({ex[0][0]}, {ex[0][1]}, nd=3)` → {tip_pct(*ex[0], nd=3)}"),
        ("Reuse it everywhere", f"Average tip % by meal over all {len(df)} bills: {', '.join(f'{k}: {v}%' for k, v in by.items())}. With a lambda as the sort key, the 3 most generous of the first 8 bills: {', '.join(f'${r.total_bill} (tip {tip_pct(r.total_bill, r.tip)}%)' for r in top)}."),
    ], "Functions package a calculation under a name so it is written once, tested once and reused on any data."


@walk("m-py-oop", "tips")
def _():
    df = D("tips")

    class Bill:
        def __init__(self, total, tip, day, size):
            self.total, self.tip, self.day, self.size = total, tip, day, size
        def tip_pct(self): return 100 * self.tip / self.total
        def per_person(self): return self.total / self.size
        def __repr__(self): return f"Bill(${self.total}, tip ${self.tip}, {self.day}, party of {self.size})"

    class GroupBill(Bill):
        def per_person(self): return (self.total + self.tip) / self.size
    bills = [Bill(r.total_bill, r.tip, r.day, r.size) for r in df.head(3).itertuples()]
    g = GroupBill(*df.loc[df["size"].idxmax(), ["total_bill", "tip", "day", "size"]])
    rows = pd.DataFrame([{"object": repr(b), "b.tip_pct()": round(b.tip_pct(), 1), "b.per_person()": round(b.per_person(), 2)} for b in bills])
    return [
        ("A class = data + behaviour", "```python\nclass Bill:\n    def __init__(self, total, tip, day, size):\n        self.total, self.tip, self.day, self.size = total, tip, day, size\n    def tip_pct(self):\n        return 100 * self.tip / self.total\n    def per_person(self):\n        return self.total / self.size\n```"),
        ("Objects from real rows", f"Each bill becomes its own object with its own attributes:\n\n{t(rows)}"),
        ("Inheritance", f"`class GroupBill(Bill)` reuses everything and changes one method (per-person cost including the tip). The largest real party: {g!r} → `per_person()` = **{g.per_person():.2f}** vs {Bill.per_person(g):.2f} without the tip. scikit-learn models are classes too: `fit` and `predict` are methods."),
    ], "Classes bundle data (attributes) with the functions that use it (methods); subclasses reuse and adjust behaviour."


@walk("m-py-io", "tips")
def _():
    df = D("tips"); d = tempfile.mkdtemp()
    p = os.path.join(d, "sunday.csv"); sun = df[df["day"] == "Sun"]
    sun.to_csv(p, index=False)
    with open(p) as f:
        r = csv.DictReader(f); first = next(r)
    summary = {"day": "Sun", "bills": int(len(sun)), "average_tip": round(float(sun["tip"].mean()), 2)}
    pj = os.path.join(d, "summary.json")
    with open(pj, "w") as f: json.dump(summary, f)
    with open(pj) as f: back = json.load(f)
    pp = os.path.join(d, "tips.parquet")
    try:
        df.to_parquet(pp); sizes = {"CSV": os.path.getsize(os.path.join(DATA, "tips.csv")), "Parquet": os.path.getsize(pp)}
    except Exception:
        sizes = {"CSV": os.path.getsize(os.path.join(DATA, "tips.csv"))}
    return [
        ("Write and read a CSV", f"`df[df.day == 'Sun'].to_csv('sunday.csv', index=False)` writes {len(sun)} real Sunday bills. Reading it back row by row with the `csv` module gives dictionaries of strings: `{dict(first)}` (note: numbers come back as text unless you convert them)."),
        ("JSON for small structured results", f"`json.dump({summary}, f)` then `json.load(f)` → `{back}` with types kept (int, float, str)."),
        ("Pick the format", f"File sizes: {', '.join(f'{k} {v:,} bytes' for k, v in sizes.items())}. CSV is readable anywhere; Parquet keeps column types and is much faster for big tables. Always open files with `with open(...)` so they close even if an error happens."),
    ], "File I/O moves data between programs: CSV for tables anyone can open, JSON for nested results, Parquet for large typed tables."


@walk("m-py-libraries", "tips")
def _():
    df = D("tips")
    from scipy import stats
    from sklearn.linear_model import LinearRegression
    arr = df["total_bill"].to_numpy()
    lr = LinearRegression().fit(df[["total_bill"]], df["tip"])
    r = stats.pearsonr(df["total_bill"], df["tip"])
    hist, edges = np.histogram(df["tip"], bins=5)
    rows = pd.DataFrame([
        {"library": "NumPy", "what it's for": "fast arrays and maths", "on the tips data": f"arr.mean() = {arr.mean():.2f}, arr.max() = {arr.max():.2f}"},
        {"library": "pandas", "what it's for": "tables: load, filter, group", "on the tips data": f"df.groupby('day').tip.mean() → Sun {df[df.day == 'Sun'].tip.mean():.2f}"},
        {"library": "Matplotlib", "what it's for": "charts", "on the tips data": f"plt.hist(df.tip, bins=5) → bar heights {[int(v) for v in hist]}"},
        {"library": "SciPy", "what it's for": "statistics, optimisation, signals", "on the tips data": f"pearsonr(bill, tip) → r = {r.statistic:.2f}"},
        {"library": "scikit-learn", "what it's for": "machine-learning models", "on the tips data": f"LinearRegression → tip ≈ {lr.intercept_:.2f} + {lr.coef_[0]:.3f} × bill"},
    ])
    return [
        ("The stack, one job each", t(rows)),
        ("They work together", "pandas columns are NumPy arrays underneath (`df.total_bill.to_numpy()`), Matplotlib and scikit-learn accept them directly, and SciPy functions take them as inputs. One import line: `import numpy as np, pandas as pd, matplotlib.pyplot as plt`."),
        ("Where to go next", "Deep learning adds PyTorch or TensorFlow/Keras; NLP adds Hugging Face; images add OpenCV or Pillow. All of them read NumPy arrays, so the basics here carry over."),
    ], "Each library does one job (arrays, tables, charts, statistics, models) and they all share NumPy arrays."


@walk("m-numpy", "tips")
def _():
    df = D("tips"); a = df["total_bill"].to_numpy(); tip = df["tip"].to_numpy()
    p = tip / a * 100
    M = df[["total_bill", "tip", "size"]].to_numpy()[:4]
    return [
        ("An array of 244 real bills", f"`a = df.total_bill.to_numpy()` → shape {a.shape}, dtype {a.dtype}. First five: {a[:5].tolist()}. `a.mean()` = {a.mean():.2f}, `a.std()` = {a.std():.2f}, `np.median(a)` = {np.median(a):.2f}."),
        ("Vectorised maths and boolean masks", f"`p = tip / a * 100` divides all 244 pairs at once (no loop): first five {np.round(p[:5], 1).tolist()}. `mask = p > 20` → {int((p > 20).sum())} True values; `a[mask].mean()` = {a[p > 20].mean():.2f} (bills with tips over 20% are smaller on average than {a.mean():.2f})."),
        ("2-D arrays and broadcasting", f"`M` = bill, tip, party size for 4 rows, shape {M.shape}:\n\n{t(pd.DataFrame(M, columns=['bill', 'tip', 'size']))}\n\n`M.mean(axis=0)` (down the columns) = {np.round(M.mean(0), 2).tolist()}. `M / M.max(axis=0)` scales each column to 0–1: the (3,)-shaped maxima are 'broadcast' over all 4 rows."),
    ], "NumPy arrays let you compute on whole columns at once, select with boolean masks and combine shapes by broadcasting."


@walk("m-pandas", "titanic")
def _():
    df = D("titanic")
    miss = df.isna().sum(); miss = miss[miss > 0]
    g = df.groupby(["Pclass", "Sex"])["Survived"].agg(["count", "mean"]).round(2)
    pv = df.pivot_table(index="Pclass", columns="Sex", values="Fare", aggfunc="median").round(1)
    return [
        ("Load and inspect", f"`df = pd.read_csv('titanic.csv')` → {df.shape[0]} rows × {df.shape[1]} columns. `df.head(3)`:\n\n{t(df[['Name', 'Pclass', 'Sex', 'Age', 'Fare', 'Survived']].assign(Name=df['Name'].str.slice(0, 26)), 3)}\n\n`df.isna().sum()` shows missing values: {', '.join(f'{k} {v}' for k, v in miss.items())}."),
        ("Filter, then group", f"`df[(df.Sex == 'female') & (df.Pclass == 3)]` → {int(((df.Sex == 'female') & (df.Pclass == 3)).sum())} passengers. `df.groupby(['Pclass', 'Sex']).Survived.agg(['count', 'mean'])`:\n\n{t(g, index=True)}"),
        ("Reshape", f"`df.pivot_table(index='Pclass', columns='Sex', values='Fare', aggfunc='median')`:\n\n{t(pv, index=True)}\n\nOther everyday tools: `fillna`, `merge` (join two tables), `apply`, `sort_values`, `value_counts`."),
    ], "pandas is the everyday tool for tables: load, inspect, filter, group, aggregate and reshape."


@walk("m-matplotlib", "tips")
def _():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    df = D("tips")
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    n, edges, _ = ax[0].hist(df["tip"], bins=6)
    ax[1].scatter(df["total_bill"], df["tip"], s=8)
    k, b = np.polyfit(df["total_bill"], df["tip"], 1)
    ax[1].plot([3, 51], [k * 3 + b, k * 51 + b])
    ax[0].set_title("Tips"); ax[1].set_xlabel("bill ($)"); ax[1].set_ylabel("tip ($)")
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=80); plt.close(fig)
    bins = pd.DataFrame({"bar (tip range $)": [f"{edges[i]:.2f}–{edges[i + 1]:.2f}" for i in range(len(n))], "height (bills)": n.astype(int)})
    return [
        ("Figure and axes", "```python\nfig, ax = plt.subplots(1, 2, figsize=(8, 3))\nax[0].hist(df.tip, bins=6)\nax[1].scatter(df.total_bill, df.tip, s=8)\nax[1].plot(xs, k * xs + b)\nax[1].set_xlabel('bill ($)')\nfig.savefig('tips.png')\n```\n\nA figure holds one or more axes (panels); you draw on each axes."),
        ("What the histogram draws", f"`hist` splits the 244 real tips into 6 equal-width bins and draws one bar per bin:\n\n{t(bins)}\n\nMost tips are $1–4; a few big tips make a long right tail."),
        ("What the scatter and line draw", f"One dot per bill at (bill, tip). The straight line from `np.polyfit(bill, tip, 1)` is tip ≈ {k:.3f} × bill + {b:.2f}: about {100 * k:.0f} cents per extra dollar. The saved PNG is {buf.getbuffer().nbytes / 1e3:.0f} kB. Always label axes and units."),
    ], "Matplotlib draws data on axes inside a figure; knowing what each call computes (bins, points, fitted line) makes charts honest."


@walk("m-scipy", ("tips", "flights"))
def _():
    from scipy import stats, optimize, interpolate
    df = D("tips"); p = df["tip"] / df["total_bill"] * 100
    a, b = p[df["smoker"] == "Yes"], p[df["smoker"] == "No"]
    tt = stats.ttest_ind(a, b, equal_var=False)
    res = optimize.minimize_scalar(lambda x: ((p - x) ** 2).sum())
    resm = optimize.minimize_scalar(lambda x: np.abs(p - x).sum(), bounds=(0, 100), method="bounded")
    fl = D("flights"); y = fl["passengers"].values[:12]
    cs = interpolate.CubicSpline(np.arange(12), y)
    return [
        ("scipy.stats: a significance test", f"Do smokers tip a different percentage? Smokers average {a.mean():.1f}% ({len(a)} bills), non-smokers {b.mean():.1f}% ({len(b)}). Welch's t-test: t = {tt.statistic:.2f}, p = {tt.pvalue:.2f}. {'p > 0.05: no clear evidence of a difference.' if tt.pvalue > 0.05 else 'p < 0.05: evidence of a difference.'}"),
        ("scipy.optimize: find the best value", f"Which single number x is 'closest' to all 244 tip percentages? Minimising Σ(p − x)² gives x = **{res.x:.2f}** (= the mean, {p.mean():.2f}); minimising Σ|p − x| gives **{resm.x:.2f}** (≈ the median, {p.median():.2f}). Model training is this same idea with many parameters."),
        ("scipy.interpolate: fill between points", f"Real 1949 airline passengers are monthly. A cubic spline through the 12 points estimates mid-month values, e.g. halfway between June ({y[5]}) and July ({y[6]}): **{cs(5.5):.0f}** thousand."),
    ], "SciPy adds ready-made scientific tools on top of NumPy: statistical tests, optimisers, interpolation and more."
