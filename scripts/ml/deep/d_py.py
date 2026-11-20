"""Deep layer + end-to-end walkthroughs: Python & libraries."""
from deep.util import X

TITANIC = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
TIPS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
PENGUINS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
MPG = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv"

X("m-setup",
  "Your ML environment is three layers: the **Python interpreter**, the **packages** (NumPy, PyTorch…) installed into an environment, and the **editor/runtime** (Colab notebook or VS Code) where you run code. Problems almost always come from the wrong interpreter or clashing package versions, so isolating each project matters.",
  """**How it works.** `pip install x` downloads a *wheel* from PyPI into the active environment's `site-packages`. A virtual environment is just a folder with its own `site-packages` and a `python` that looks there first. `import x` searches `sys.path` in order. Colab gives every notebook a fresh Linux VM (≈12 GB RAM, optional GPU) that resets after inactivity. CUDA lets PyTorch run matrix maths on an NVIDIA GPU; `torch.cuda.is_available()` tells you whether it found one.""",
  """**Check what you're running.** In a cell: `import sys; sys.executable` → `/usr/bin/python3` (Colab) or `C:\\...\\project\\.venv\\Scripts\\python.exe` (VS Code venv). If `pip install pandas` succeeded but `import pandas` fails, the two commands used different interpreters — run `python -m pip install pandas` with the same `python` you execute with.""",
  ["Installing packages globally instead of in a per-project venv", "Selecting a different interpreter in VS Code than the one you pip-installed into",
   "Forgetting to switch Colab to a GPU runtime for deep learning", "Losing work because Colab files aren't saved to Drive/GitHub", "Pasting API keys into notebooks you share"],
  ["Colab: quick experiments, free GPU, sharing notebooks", "VS Code + venv: real projects, tests, Git, deployment code"],
  ["Don't rely on Colab for long training jobs (sessions time out)", "Don't mix conda and pip in the same environment unless you know why"],
  "No dataset: an environment health check you run at the start of every project.",
  ["Print interpreter path and version", "Check each core library imports and print versions", "Detect GPU / CPU and RAM", "Write requirements.txt for reproducibility", "Time a matrix multiply to sanity-check performance"],
  '''
import sys, platform, importlib, time
import numpy as np
print("interpreter:", sys.executable, "| python", platform.python_version())
versions = {}
for pkg in ["numpy", "pandas", "sklearn", "scipy", "matplotlib", "torch"]:
    try:
        versions[pkg] = importlib.import_module(pkg).__version__
    except ImportError:
        versions[pkg] = "NOT INSTALLED -> pip install " + ("scikit-learn" if pkg == "sklearn" else pkg)
for k, v in versions.items(): print(f"  {k:11s} {v}")
try:
    import torch
    print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none (CPU only)")
except ImportError:
    pass
pip_names = {"sklearn": "scikit-learn"}
with open("requirements.txt", "w") as f:
    f.writelines(f"{pip_names.get(k, k)}=={v}\\n" for k, v in versions.items() if "NOT" not in v)
a = np.random.rand(1000, 1000); t = time.perf_counter(); a @ a
print(f"1000x1000 matmul: {1000 * (time.perf_counter() - t):.0f} ms | requirements.txt written")
''')

X("m-py-basics",
  "A program is a list of instructions run top to bottom; **variables** are labels on values, **conditions** choose a path, **loops** repeat work. In data work you rarely write raw loops over millions of rows (libraries do that faster), but you constantly write small loops and comprehensions for files, configs and experiments.",
  """**Internals.** Python is interpreted: each line becomes bytecode run by the interpreter, so a Python `for` loop over 10⁶ numbers costs ~0.1 s while NumPy does the same in ~1 ms in compiled C. Truthiness: `0`, `""`, `[]`, `None` are false. A comprehension `[f(x) for x in xs if c(x)]` is equivalent to a loop that appends, but faster and clearer. Integer division `//`, modulo `%`, power `**`; floats follow IEEE-754 (`0.1 + 0.2 != 0.3` — compare with `math.isclose`).""",
  """**Trace a loop by hand.** `total = 0; for x in [3, 5, 2]: if x > 2: total += x` → iteration 1: x=3 → total 3; iteration 2: x=5 → total 8; iteration 3: x=2 fails the condition → total stays **8**. The comprehension `sum(x for x in [3, 5, 2] if x > 2)` gives the same 8.""",
  ["Mutating a list while iterating over it", "Using `==` to compare floats", "Off-by-one with `range(n)` (it stops at n-1)", "Writing Python loops over big arrays instead of vectorising"],
  ["Control logic, file handling, experiment loops, small data"], ["Row-by-row loops on large DataFrames/arrays — use pandas/NumPy instead"],
  "Titanic passengers (891 rows, GitHub mirror) read with only the csv module — pure Python, no pandas.",
  ["Download and read the CSV with the standard library", "Clean values in a loop (missing ages)", "Compute survival rate by sex and class with dicts", "Answer a question with conditions", "Print a small report"],
  f'''
import csv, io, urllib.request
from collections import defaultdict
# 1. data (pure Python)
text = urllib.request.urlopen("{TITANIC}").read().decode()
rows = list(csv.DictReader(io.StringIO(text)))
print(len(rows), "passengers; columns:", list(rows[0])[:6], "...")
# 2. prepare: convert types, handle missing ages
ages = [float(r["Age"]) for r in rows if r["Age"]]
median_age = sorted(ages)[len(ages) // 2]
for r in rows:
    r["Age"] = float(r["Age"]) if r["Age"] else median_age
    r["Survived"] = int(r["Survived"])
# 3. analyse with dicts and comprehensions
groups = defaultdict(list)
for r in rows:
    groups[(r["Sex"], r["Pclass"])].append(r["Survived"])
rates = {{k: sum(v) / len(v) for k, v in groups.items()}}
# 4. answer questions
children = [r for r in rows if r["Age"] < 12]
print(f"children: {{len(children)}}, survival {{sum(r['Survived'] for r in children) / len(children):.0%}}")
for (sex, cls), rate in sorted(rates.items(), key=lambda kv: -kv[1]):
    print(f"  {{sex:6s}} class {{cls}}: {{rate:.0%}} survived ({{len(groups[(sex, cls)])}} people)")
''')

X("m-py-datatypes",
  "Choosing the right container makes code both correct and fast: a **list** for ordered sequences, a **dict** for lookup by key, a **set** for uniqueness and fast membership, a **tuple** for fixed records. ML code is full of them — vocabularies are dicts, label sets are sets, shapes are tuples.",
  """**Internals and costs.** A list is a dynamic array: index O(1), append amortised O(1), `x in list` O(n). Dicts and sets are hash tables: insert/lookup/`in` average O(1) — which is why converting a 100k-word stop-list to a set makes filtering ~1000× faster. Keys must be hashable (immutable): tuples yes, lists no. Since Python 3.7 dicts keep insertion order. Assignment copies references, not objects: `b = a` shares the same list; `copy.deepcopy` copies nested structures.""",
  """**Membership cost.** Checking 10,000 tokens against a 10,000-word stop-list: list → 10⁴ × 10⁴/2 ≈ 5×10⁷ comparisons; set → 10⁴ hash lookups. **Aliasing:** `a = [[0]*2]*2; a[0][0] = 9` gives `[[9, 0], [9, 0]]` because both rows are the same object — build with `[[0]*2 for _ in range(2)]`.""",
  ["Using a list for membership tests on large collections", "Mutable default arguments / aliasing nested lists", "Using a list as a dict key (unhashable)", "Assuming sets keep order"],
  ["dict for vocabularies, configs, counting", "set for unique labels / stop-words", "tuple for shapes, fixed records, dict keys"],
  ["Big numeric data in lists — use NumPy arrays"],
  "SMS Spam Collection (5,572 real SMS messages) — build a vocabulary and word statistics with core data structures only.",
  ["Load messages into a list of (label, text) tuples", "Tokenise and build a word→count dict", "Use sets for stop-words and vocabulary differences", "Find words most typical of spam with dict maths", "Benchmark list vs set membership"],
  '''
import urllib.request, time, re
from collections import Counter
# 1. data -> list of tuples
lines = urllib.request.urlopen("https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv").read().decode().splitlines()
msgs = [tuple(l.split("\\t", 1)) for l in lines if "\\t" in l]
print(len(msgs), "messages, spam share:", round(sum(lbl == "spam" for lbl, _ in msgs) / len(msgs), 3))
# 2. tokens + dict counts per class
STOP = {"the", "a", "to", "you", "i", "and", "is", "in", "u", "of", "for", "your", "me", "my", "it", "on", "have", "be", "are", "that", "or", "at", "now", "this"}
count = {"spam": Counter(), "ham": Counter()}
for lbl, text in msgs:
    count[lbl].update(w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOP)
# 3. set operations on vocabularies
spam_vocab, ham_vocab = set(count["spam"]), set(count["ham"])
print("vocab sizes:", len(spam_vocab), len(ham_vocab), "| only-in-spam words:", len(spam_vocab - ham_vocab))
# 4. which words are most 'spammy'? (smoothed ratio of relative frequencies)
ts, th = sum(count["spam"].values()), sum(count["ham"].values())
score = {w: ((count["spam"][w] + 1) / ts) / ((count["ham"][w] + 1) / th) for w in spam_vocab | ham_vocab if count["spam"][w] + count["ham"][w] >= 20}
print("most spammy:", [w for w, _ in sorted(score.items(), key=lambda kv: -kv[1])[:8]])
# 5. list vs set membership speed
words = [w for _, t in msgs for w in t.lower().split()][:20000]; stop_list = list(STOP) * 50
t = time.perf_counter(); sum(w in stop_list for w in words); tl = time.perf_counter() - t
t = time.perf_counter(); sum(w in STOP for w in words); tset = time.perf_counter() - t
print(f"membership: list {tl * 1000:.1f} ms vs set {tset * 1000:.2f} ms")
''')

X("m-py-functions",
  "A function packages a piece of logic behind a name with inputs and an output, so you can test it, reuse it and reason about it separately. Good ML code is mostly small pure functions — `load()`, `clean()`, `featurise()`, `evaluate()` — composed into a pipeline.",
  """**Internals.** Arguments are passed by *object reference*: a function can mutate a list you pass in, but rebinding the parameter doesn't affect the caller. Default values are evaluated **once** at definition (hence `def f(x=None)` then `x = x or []`). Functions are objects: you can pass them (`sorted(key=...)`), return them (closures, decorators) and store them in dicts. Generators (`yield`) produce values lazily — O(1) memory for streams. Recursion depth is limited (~1000).""",
  """**Closure by hand.** `def make_scaler(lo, hi): return lambda x: (x - lo) / (hi - lo)`; `s = make_scaler(10, 30)`; `s(25)` → (25−10)/20 = **0.75**. The returned lambda "remembers" lo=10, hi=30 — exactly how a fitted scaler remembers training statistics.""",
  ["Mutable default arguments", "Functions that both modify inputs and return them (confusing)", "Huge functions doing load+clean+train+plot at once", "Missing docstrings/type hints on reusable utilities"],
  ["Any logic you'll call twice or want to test", "Generators for streaming large files/batches"],
  ["Deep recursion on large inputs (use loops)"],
  "Tips dataset (244 restaurant bills) — build a mini analysis pipeline out of small, typed, tested functions.",
  ["Write a loader with caching", "Write pure feature functions and a decorator that times them", "Compose them into a pipeline function", "Test each function with asserts", "Use a generator to stream batches"],
  f'''
import time, functools
import pandas as pd

def timed(fn):
    """Decorator: print how long a step took."""
    @functools.wraps(fn)
    def wrapper(*a, **k):
        t = time.perf_counter(); out = fn(*a, **k); print(f"  {{fn.__name__:14s}} {{(time.perf_counter() - t) * 1000:5.1f}} ms"); return out
    return wrapper

@timed
def load(url: str = "{TIPS}") -> pd.DataFrame:
    return pd.read_csv(url)

@timed
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Pure: returns a new frame, never mutates the input."""
    return df.assign(tip_pct=df["tip"] / df["total_bill"], per_person=df["total_bill"] / df["size"])

@timed
def summarise(df: pd.DataFrame, by: str) -> pd.DataFrame:
    return df.groupby(by)[["tip_pct", "per_person"]].mean().round(3)

def pipeline(by="day"):
    return summarise(add_features(load()), by)

def batches(df, size):
    for i in range(0, len(df), size):
        yield df.iloc[i:i + size]

# tests: each function in isolation
toy = pd.DataFrame({{"total_bill": [10.0, 20.0], "tip": [1.0, 5.0], "size": [1, 2]}})
assert add_features(toy)["tip_pct"].tolist() == [0.1, 0.25] and "tip_pct" not in toy
print(pipeline("day")); print(pipeline("smoker"))
print("batch sizes:", [len(b) for b in batches(load(), 100)])
''')

X("m-py-oop",
  "A class bundles **data** (attributes) with **behaviour** (methods). Libraries use classes everywhere: a scikit-learn estimator stores learned parameters after `fit`; a PyTorch `nn.Module` stores layers and defines `forward`. Writing your own small classes lets your code plug into those ecosystems.",
  """**Internals.** `obj.method(x)` is `Class.method(obj, x)` — `self` is the instance. Inheritance looks methods up the MRO (method resolution order). Duck typing: scikit-learn only needs objects with `fit`/`predict`/`get_params`, which `BaseEstimator` provides via introspection of `__init__` arguments — so **store constructor arguments unchanged** and put learned values in attributes ending with `_`. Dunder methods (`__len__`, `__getitem__`, `__call__`, `__repr__`) let your objects behave like built-ins.""",
  """**Design a transformer.** `ClipOutliers(k=1.5)` → `fit(X)` computes per-column Q1, Q3 → stores `lo_ = Q1 − 1.5·IQR`, `hi_ = Q3 + 1.5·IQR`; `transform(X)` clips. For a column [1, 2, 3, 4, 100]: Q1=2, Q3=4, IQR=2 → lo=−1, hi=7 → 100 becomes **7**. Because it follows the API, `Pipeline` and `GridSearchCV` can tune `k` automatically.""",
  ["Computing learned values in `__init__` (breaks cloning/grid search)", "Not returning `self` from `fit`", "Deep inheritance hierarchies", "Shared mutable class attributes"],
  ["Custom scikit-learn transformers/estimators", "PyTorch Datasets and Modules", "Config objects (@dataclass)"],
  ["Simple scripts where plain functions are clearer"],
  "Penguins (344 birds, real measurements) — write a scikit-learn-compatible outlier-clipping transformer and a tiny nearest-centroid classifier, and run them inside Pipeline + GridSearchCV.",
  ["Load data and split", "Write ClipOutliers (TransformerMixin) with fit/transform", "Write NearestCentroid (ClassifierMixin) with fit/predict", "Plug both into Pipeline and GridSearchCV", "Evaluate and inspect learned attributes"],
  f'''
import numpy as np, pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

class ClipOutliers(BaseEstimator, TransformerMixin):
    def __init__(self, k=1.5): self.k = k                    # store params unchanged
    def fit(self, X, y=None):
        q1, q3 = np.percentile(X, [25, 75], axis=0); iqr = q3 - q1
        self.lo_, self.hi_ = q1 - self.k * iqr, q3 + self.k * iqr; return self
    def transform(self, X): return np.clip(X, self.lo_, self.hi_)

class NearestCentroid(BaseEstimator, ClassifierMixin):
    def __init__(self, shrink=0.0): self.shrink = shrink
    def fit(self, X, y):
        self.classes_ = np.unique(y); overall = X.mean(0)
        self.centroids_ = np.array([(1 - self.shrink) * X[y == c].mean(0) + self.shrink * overall for c in self.classes_]); return self
    def predict(self, X):
        return self.classes_[((X[:, None, :] - self.centroids_[None]) ** 2).sum(-1).argmin(1)]

df = pd.read_csv("{PENGUINS}").dropna()
X = df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]].to_numpy(); y = df["species"].to_numpy()
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0)
pipe = Pipeline([("clip", ClipOutliers()), ("scale", StandardScaler()), ("clf", NearestCentroid())])
gs = GridSearchCV(pipe, {{"clip__k": [1.0, 1.5, 3.0], "clf__shrink": [0.0, 0.2, 0.5]}}, cv=5).fit(Xtr, ytr)
print("best params:", gs.best_params_, "| CV accuracy", round(gs.best_score_, 3), "| test accuracy", round(gs.score(Xte, yte), 3))
print("learned centroids (scaled):", gs.best_estimator_["clf"].centroids_.round(2)[0])
''')

X("m-py-io",
  "Real projects start and end with files and services: CSV/JSON/Parquet in, models and reports out, APIs that fail sometimes. Robust I/O — paths, encodings, formats, error handling, logging — is what separates a notebook from a tool someone else can run.",
  """**Formats and trade-offs.** CSV: universal, slow, no types. JSON: nested, human-readable. **Parquet**: columnar, typed, compressed — often 5–10× smaller and much faster to read only the columns you need. Pickle/joblib: Python objects (never unpickle untrusted files — it can execute code). Text needs an **encoding** (UTF-8 by default; old Excel exports may be latin-1). Exceptions propagate up the call stack until caught; catch *specific* ones and let unexpected ones crash loudly. `with` guarantees files close even on errors.""",
  """**Size by hand.** 1,000,000 rows × 10 float columns: CSV ≈ 10⁷ numbers × ~10 characters ≈ 100 MB; Parquet stores 8-byte floats with compression ≈ 30–60 MB, and reading 2 columns reads ~1/5 of that.""",
  ["Hard-coding absolute Windows paths", "Ignoring encoding errors", "Bare `except:` that hides bugs", "Unpickling files from the internet", "No retries/timeouts on web requests"],
  ["pathlib for paths", "Parquet for intermediate data", "logging + specific exceptions in scripts"],
  ["Pickle for long-term or shared storage of data"],
  "MPG cars dataset (398 cars) — download with retries, validate, convert formats, log what happens, and handle bad records.",
  ["Download with timeout and retry", "Validate rows and log/skip bad ones", "Save as CSV, JSON and Parquet; compare sizes and read speed", "Write and reload a small config in JSON", "Use pathlib for every path"],
  f'''
import json, logging, time, urllib.error, urllib.request
from pathlib import Path
import pandas as pd
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s"); log = logging.getLogger("io")
out = Path("output"); out.mkdir(exist_ok=True)

def download(url, retries=3, timeout=15):
    for attempt in range(1, retries + 1):
        try:
            return urllib.request.urlopen(url, timeout=timeout).read()
        except urllib.error.URLError as e:
            log.warning("attempt %d failed: %s", attempt, e); time.sleep(2 * attempt)
    raise RuntimeError("download failed after retries")

(out / "mpg_raw.csv").write_bytes(download("{MPG}"))
df = pd.read_csv(out / "mpg_raw.csv")
bad = df[df["horsepower"].isna() | (df["mpg"] <= 0)]
log.info("rows %d, invalid %d (missing horsepower) -> dropped", len(df), len(bad))
df = df.drop(bad.index)
df.to_csv(out / "mpg.csv", index=False); df.to_json(out / "mpg.json", orient="records"); df.to_parquet(out / "mpg.parquet")
for f in ["mpg.csv", "mpg.json", "mpg.parquet"]:
    t = time.perf_counter(); (pd.read_parquet if f.endswith("parquet") else pd.read_json if f.endswith("json") else pd.read_csv)(out / f)
    log.info("%-12s %6.1f KB, read %.1f ms", f, (out / f).stat().st_size / 1024, 1000 * (time.perf_counter() - t))
cfg = {{"target": "mpg", "features": ["weight", "horsepower", "model_year"], "created": time.strftime("%Y-%m-%d")}}
(out / "config.json").write_text(json.dumps(cfg, indent=2)); log.info("config round-trip ok: %s", json.loads((out / "config.json").read_text()) == cfg)
''')

X("m-py-libraries",
  "The Python ML stack is layered: **NumPy** arrays at the bottom; **pandas** tables and **SciPy** maths on top of it; **scikit-learn** models consuming NumPy/pandas; **PyTorch/TensorFlow** for deep learning; **Hugging Face** on top of PyTorch for pretrained models. Knowing which layer does what tells you where to look when something breaks.",
  """**How they interoperate.** Most libraries accept NumPy arrays and pandas DataFrames (`df.to_numpy()` shares memory when possible). scikit-learn outputs NumPy (or pandas with `set_output(transform="pandas")`). PyTorch tensors convert with `torch.from_numpy(arr)` (zero-copy) and `.numpy()`. Versions matter: major releases change APIs (pandas 2 → copy-on-write; NumPy 2 → dtype rules; Keras 3 → multi-backend), so pin versions per project.""",
  """**One dataset through every layer.** Penguins CSV → pandas (clean, group) → NumPy (array of 4 features) → SciPy (t-test: are Adelie and Gentoo flippers different?) → scikit-learn (classifier, 97–99% accuracy) → PyTorch (same data as tensors, tiny network) → Matplotlib (chart). That pipeline is the walkthrough below.""",
  ["Mixing library versions from different eras (old tutorials)", "Converting between pandas/NumPy/torch repeatedly in a loop", "Forgetting `set_output`/column names when moving from pandas to NumPy"],
  ["pandas for tabular wrangling, scikit-learn for classical models, PyTorch for deep learning, HF for pretrained transformers"],
  ["A heavy deep-learning framework for a problem logistic regression solves"],
  "Penguins — one dataset passed through pandas → NumPy → SciPy → scikit-learn → PyTorch → Matplotlib.",
  ["pandas: load, clean, group", "SciPy: a statistical test", "scikit-learn: pipeline + cross-validation", "PyTorch: same data as tensors, small network", "Matplotlib: one chart summarising the result"],
  f'''
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd, torch
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
df = pd.read_csv("{PENGUINS}").dropna()                                           # pandas
print(df.groupby("species")[["flipper_length_mm", "body_mass_g"]].mean().round(0))
t = stats.ttest_ind(df.query("species=='Adelie'").flipper_length_mm, df.query("species=='Gentoo'").flipper_length_mm, equal_var=False)
print(f"SciPy Welch t-test Adelie vs Gentoo flippers: t={{t.statistic:.1f}}, p={{t.pvalue:.1e}}")
cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
X, y = df[cols].to_numpy(), pd.factorize(df["species"])[0]                            # NumPy
print("scikit-learn CV accuracy:", cross_val_score(make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)), X, y, cv=5).mean().round(3))
Xt = torch.tensor(StandardScaler().fit_transform(X), dtype=torch.float32); yt = torch.tensor(y)  # PyTorch
torch.manual_seed(0); net = torch.nn.Sequential(torch.nn.Linear(4, 16), torch.nn.ReLU(), torch.nn.Linear(16, 3)); opt = torch.optim.Adam(net.parameters(), 0.01)
for _ in range(200): opt.zero_grad(); torch.nn.functional.cross_entropy(net(Xt), yt).backward(); opt.step()
print("PyTorch training accuracy:", round((net(Xt).argmax(1) == yt).float().mean().item(), 3))
fig, ax = plt.subplots(); [ax.scatter(g.flipper_length_mm, g.body_mass_g, s=8, label=s) for s, g in df.groupby("species")]
ax.set(xlabel="flipper (mm)", ylabel="mass (g)"); ax.legend(); fig.savefig("penguins.png"); print("chart saved")
''')

X("m-numpy",
  "NumPy turns 'do this to every number' into one operation on a whole array, executed in compiled C. Thinking in **arrays and axes** instead of loops is the single biggest speed-up in ML code, and every deep-learning tensor library copies NumPy's ideas.",
  """**Internals.** An `ndarray` = a contiguous memory buffer + dtype + shape + **strides** (bytes to jump per axis). `reshape`/`transpose`/slicing usually create *views* (no copy) by changing shape/strides — so editing a slice edits the original. **Broadcasting rule**: align shapes from the right; each dimension must be equal or 1; size-1 dims stretch. (5, 3) − (3,) → OK; (5, 3) − (5,) → error, needs (5, 1). Reductions take `axis`: `X.mean(axis=0)` collapses rows → one value per column.""",
  """**Standardise by hand.** X = [[1, 10], [3, 30]]. Column means = [2, 20]; stds (population) = [1, 10]. (X − mean)/std = [[−1, −1], [1, 1]]. In NumPy: `(X - X.mean(0)) / X.std(0)` — the (2,) mean broadcasts across both rows. **Distance matrix without loops:** `((A[:, None, :] - B[None, :, :])**2).sum(-1)` → shape (len A, len B).""",
  ["Accidental views (modifying a slice changes the source)", "Shape (n,) vs (n, 1) broadcasting surprises", "Integer dtype truncation (`np.array([1, 2]) / 2` is fine, but assigning 0.5 into an int array truncates)", "Python loops over array elements"],
  ["Numeric arrays, images, vectorised maths, custom metrics"], ["Heterogeneous tables with names/strings — use pandas"],
  "Fashion-MNIST test images (10,000 real 28×28 images, from GitHub) — image statistics, a vectorised nearest-centroid classifier, and loop vs vectorised timing.",
  ["Download and parse raw bytes into a (10000, 28, 28) uint8 array", "Normalise with broadcasting", "Compute per-class mean images (centroids)", "Classify by vectorised distances", "Compare loop vs vectorised speed"],
  '''
import gzip, time, urllib.request
import numpy as np
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
X = np.frombuffer(gzip.decompress(urllib.request.urlopen(base + "t10k-images-idx3-ubyte.gz").read()), np.uint8, offset=16).reshape(-1, 28, 28)
y = np.frombuffer(gzip.decompress(urllib.request.urlopen(base + "t10k-labels-idx1-ubyte.gz").read()), np.uint8, offset=8)
print("images", X.shape, X.dtype, "| strides", X.strides)
Xf = X.reshape(len(X), -1).astype(np.float32) / 255.0           # view -> copy as float
Xs = (Xf - Xf.mean(0)) / (Xf.std(0) + 1e-6)                    # broadcasting (10000,784) - (784,)
tr, te = np.arange(8000), np.arange(8000, 10000)
centroids = np.stack([Xs[tr][y[tr] == c].mean(0) for c in range(10)])        # (10, 784)
d = ((Xs[te][:, None, :] - centroids[None]) ** 2).sum(-1)                   # (2000, 10) distances, no loops
print("nearest-centroid accuracy:", round((d.argmin(1) == y[te]).mean(), 3))
t = time.perf_counter(); loop = [[sum((a - b) ** 2 for a, b in zip(Xs[i, :100], centroids[c, :100])) for c in range(10)] for i in te[:200]]; tl = time.perf_counter() - t
t = time.perf_counter(); vec = ((Xs[te[:200], None, :100] - centroids[None, :, :100]) ** 2).sum(-1); tv = time.perf_counter() - t
print(f"same result: {np.allclose(loop, vec, atol=1e-3)} | loops {tl * 1000:.0f} ms vs vectorised {tv * 1000:.2f} ms")
''')

X("m-pandas",
  "pandas is a spreadsheet you program: labelled columns of different types, with fast vectorised operations for filtering, grouping, joining and reshaping. 70% of an ML project is this kind of wrangling, so fluency here pays off more than any model trick.",
  """**Mental model.** A DataFrame is a dict of Series sharing an index; each column is a NumPy (or Arrow) array. Vectorised column operations are fast; `apply` with Python functions is slow; `iterrows` is slowest. **Split–apply–combine**: `groupby(keys)` splits rows, an aggregation applies per group, results combine into a new frame; `transform` returns a result aligned to the original rows (for group-wise imputation/features). `merge` = SQL join (watch for duplicate keys multiplying rows). `.loc` selects by labels, `.iloc` by positions. pandas 2+ uses copy-on-write: modifying a derived frame no longer silently changes the original.""",
  """**groupby by hand.** Rows (city, sales): (A, 10), (B, 5), (A, 30). `groupby("city").sales.mean()` → A: (10+30)/2 = **20**, B: **5**. `transform("mean")` instead returns [20, 5, 20] aligned to each row — useful for "sales minus city average" features.""",
  ["Chained assignment `df[df.x > 0]['y'] = 1` (doesn't stick)", "`merge` on non-unique keys exploding row counts", "Using `apply`/loops where a vectorised method exists", "Forgetting `reset_index` after groupby"],
  ["Tabular cleaning, feature engineering, aggregations, joins, time series resampling"],
  ["Tens of GB of data on one machine — use Polars, DuckDB, Spark"],
  "Titanic — full wrangling workflow: inspect, clean, engineer features with groupby/transform, join a lookup table, pivot, and export a model-ready table.",
  ["Inspect types, missing values, duplicates", "Clean and impute with group-wise statistics", "Engineer features (title from name, family size, fare per person)", "Merge a lookup table and pivot a summary", "Export a numeric, model-ready table"],
  f'''
import pandas as pd
df = pd.read_csv("{TITANIC}")
print(df.shape, "| missing per column:", df.isna().sum()[lambda s: s > 0].to_dict())
df["Title"] = df["Name"].str.extract(r",\\s*([^.]+)\\.")[0].replace({{"Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs"}})
df.loc[~df["Title"].isin(["Mr", "Mrs", "Miss", "Master"]), "Title"] = "Rare"
df["Age"] = df["Age"].fillna(df.groupby("Title")["Age"].transform("median"))   # group-wise imputation
df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])
df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
df["FarePerPerson"] = df["Fare"] / df.groupby("Ticket")["Ticket"].transform("size")
ports = pd.DataFrame({{"Embarked": ["S", "C", "Q"], "Port": ["Southampton", "Cherbourg", "Queenstown"]}})
df = df.merge(ports, on="Embarked", how="left", validate="many_to_one")
print(pd.pivot_table(df, values="Survived", index="Title", columns="Pclass", aggfunc="mean").round(2))
print(df.groupby("Port").agg(passengers=("PassengerId", "size"), survival=("Survived", "mean"), median_fare=("Fare", "median")).round(2))
model_ready = pd.get_dummies(df[["Survived", "Pclass", "Sex", "Age", "FamilySize", "FarePerPerson", "Title", "Port"]], columns=["Sex", "Title", "Port"], drop_first=True, dtype=int)
print("model-ready table:", model_ready.shape, "| any missing:", bool(model_ready.isna().any().any()))
''')

X("m-matplotlib",
  "A good chart answers one question at a glance. Matplotlib gives full control (figure → axes → artists); Seaborn adds statistical plots with sensible defaults. In ML you plot to understand data, to diagnose models (learning curves, residuals, confusion matrices) and to communicate results.",
  """**Anatomy.** `Figure` (the canvas) contains one or more `Axes` (a plot with x/y axes); you call methods on axes: `ax.plot`, `ax.scatter`, `ax.hist`, `ax.imshow`, `ax.set(title=..., xlabel=...)`. `plt.subplots(r, c)` makes a grid. Save with `fig.savefig(path, dpi=..., bbox_inches="tight")`. **Choosing encodings**: position (most accurate) > length > angle/area > colour. Use a sequential colour map for magnitude, diverging for ± around zero, categorical for groups; never rainbow for ordered data.""",
  """**Pick the chart.** Question "is horsepower related to mpg?" → scatter with trend line (two numeric). "How do mpg distributions differ by origin?" → box/violin plot (numeric by category). "How did average mpg change by model year?" → line plot (trend). "Which features correlate?" → heatmap with a diverging map centred at 0.""",
  ["Unlabelled axes/units", "Dual y-axes that mislead", "Rainbow colour maps for ordered values", "Pie charts with many slices", "Overplotting thousands of points without transparency"],
  ["EDA, model diagnostics, reports"], ["Interactive dashboards for end users — use Plotly/Streamlit/Power BI"],
  "MPG cars dataset — a 4-panel EDA figure plus a model-diagnostics figure, saved as a report image.",
  ["Load and clean", "Distribution + relationship + category + trend panels", "Correlation heatmap", "Fit a simple model and plot residuals", "Save high-resolution figures"],
  f'''
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd, seaborn as sns
from sklearn.linear_model import LinearRegression
df = pd.read_csv("{MPG}").dropna()
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
sns.histplot(df, x="mpg", bins=25, ax=ax[0, 0]); ax[0, 0].set(title="Distribution of fuel efficiency", xlabel="miles per gallon")
sns.regplot(df, x="horsepower", y="mpg", scatter_kws={{"s": 10, "alpha": 0.5}}, line_kws={{"color": "C1"}}, ax=ax[0, 1]); ax[0, 1].set(title="More power, fewer miles")
sns.boxplot(df, x="origin", y="mpg", ax=ax[1, 0]); ax[1, 0].set(title="Efficiency by origin")
df.groupby("model_year")["mpg"].mean().plot(marker="o", ax=ax[1, 1]); ax[1, 1].set(title="Average mpg by model year", xlabel="year (19xx)")
fig.tight_layout(); fig.savefig("eda.png", dpi=150, bbox_inches="tight")
X = df[["weight", "horsepower", "model_year"]]; m = LinearRegression().fit(X, df["mpg"]); res = df["mpg"] - m.predict(X)
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.heatmap(df.select_dtypes("number").corr(), cmap="vlag", center=0, annot=True, fmt=".1f", ax=ax[0]); ax[0].set_title("Correlations")
ax[1].scatter(m.predict(X), res, s=10, alpha=0.6); ax[1].axhline(0, color="k", lw=1); ax[1].set(title="Residuals vs predicted (curve = missed non-linearity)", xlabel="predicted mpg", ylabel="residual")
fig.tight_layout(); fig.savefig("diagnostics.png", dpi=150)
print(f"R² = {{m.score(X, df['mpg']):.3f}}; saved eda.png and diagnostics.png")
''')

X("m-scipy",
  "SciPy is the 'scientific calculator' layer: probability distributions, statistical tests, optimisation, signal processing, sparse matrices, interpolation. Many ML tasks — fitting a curve, testing an improvement, filtering a sensor signal — are one SciPy call once you know it exists.",
  """**Key ideas.** `scipy.stats` distributions share an API: `pdf/pmf`, `cdf`, `ppf` (inverse CDF), `rvs`, and `fit` (maximum-likelihood parameters). `scipy.optimize.minimize(f, x0)` uses gradient-based methods (BFGS/L-BFGS) and approximates gradients numerically if you don't supply them; `curve_fit` is non-linear least squares. `scipy.signal` designs filters (Butterworth) and computes spectra (Welch); `scipy.sparse` stores mostly-zero matrices (CSR) — TF-IDF matrices are 99.9% zeros.""",
  """**Curve fit by hand.** Model y = a·e^(b·t). Taking logs: ln y = ln a + b·t — a straight line, so a quick estimate is linear regression on ln y; `curve_fit` then refines a, b by minimising squared error in the original scale. For airline passengers, b ≈ 0.01 per month ⇒ ~12% growth per year.""",
  ["Interpreting p < 0.05 as 'important'", "Bad initial guesses for curve_fit (diverges)", "Filtering a signal with a cut-off above the Nyquist frequency", "Converting sparse matrices to dense by accident"],
  ["Tests, distribution fitting, optimisation, signal features"], ["Large-scale ML training — use scikit-learn/PyTorch"],
  "Airline passengers (monthly, 1949–1960) — fit an exponential growth curve with `curve_fit`, detect seasonality with a periodogram, smooth with a filter, and test whether summer traffic is significantly higher.",
  ["Load the series", "Fit y = a·e^(b·t) with curve_fit and report growth", "Find the dominant period with scipy.signal", "Smooth with a low-pass Butterworth filter", "Test summer vs winter with a statistical test"],
  '''
import numpy as np, pandas as pd
from scipy import optimize, signal, stats
df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv", parse_dates=["Month"])
y = df["Passengers"].to_numpy(float); t = np.arange(len(y))
(a, b), cov = optimize.curve_fit(lambda t, a, b: a * np.exp(b * t), t, y, p0=(100, 0.01))
print(f"fit y = {a:.1f} * exp({b:.4f} t)  -> growth {np.exp(12 * b) - 1:.1%} per year (±{np.sqrt(cov[1, 1]) * 12:.2%})")
detrended = np.log(y) - np.polyval(np.polyfit(t, np.log(y), 1), t)
f, p = signal.periodogram(detrended)
print("dominant period:", round(1 / f[1:][p[1:].argmax()], 1), "months")
bb, aa = signal.butter(3, 1 / 13, btype="low"); smooth = signal.filtfilt(bb, aa, y)
print("smoothed vs raw std of month-to-month change:", round(np.diff(smooth).std(), 1), "vs", round(np.diff(y).std(), 1))
month = df["Month"].dt.month; summer, winter = detrended[month.isin([6, 7, 8])], detrended[month.isin([11, 12, 1, 2])]
res = stats.ttest_ind(summer, winter, equal_var=False)
print(f"summer vs winter (detrended): t={res.statistic:.1f}, p={res.pvalue:.1e} -> significant seasonal peak")
''')
