"""Bridge module: Proficiency in Python + key libraries (NumPy, SciPy, Pandas, Matplotlib)."""
from ml_util import M

PYTHON = [
M("m-py-basics", "Python basics: variables, control flow, loops, comprehensions", "Basic",
  "Python is the language of ML: readable, interactive, with huge libraries. Start with variables, if/else, loops and list comprehensions.",
  """### Why Python for ML
Almost every ML library (NumPy, Pandas, scikit-learn, PyTorch, TensorFlow, Hugging Face) is Python-first. You write short, readable code and the heavy maths runs in fast C/C++/CUDA underneath.

### Variables and types
Python is **dynamically typed**: a variable is a name pointing to an object, and the type belongs to the object. `x = 5` then `x = "five"` is legal.

### Control flow
- `if / elif / else` for decisions; indentation (4 spaces) defines blocks — there are no braces.
- `for item in collection:` loops over anything iterable; `range(n)` gives 0…n−1.
- `while condition:` repeats until false; `break` and `continue` work as in Java.

### Comprehensions (very common in ML code)
`[f(x) for x in data if cond(x)]` builds a list in one line; the same works for dicts `{k: v for ...}` and sets.

### Running Python
- **Google Colab**: free notebooks in the browser with GPUs — best for this course.
- **VS Code** + Python extension + Jupyter extension for local work; create a **virtual environment** (`python -m venv .venv`) per project so library versions don't clash.
- Notebooks run cell by cell; restart the kernel if state gets confusing.""",
  analogy="Python is like giving instructions in plain English to a very fast assistant, who calls specialist workers (NumPy, PyTorch) for the heavy lifting.",
  code="""
scores = [72, 95, 48, 88, 61]

# loop + if
for s in scores:
    grade = "A" if s >= 85 else "B" if s >= 60 else "C"
    print(s, grade)

# list comprehension: keep passing scores, scaled to 0-1
passed = [s / 100 for s in scores if s >= 60]
print("passed:", passed)

# dict comprehension and f-strings
grades = {f"student{i}": s for i, s in enumerate(scores, start=1)}
print(grades)
print(f"average = {sum(scores) / len(scores):.1f}")
""",
  say=[("Why is Python the default language for machine learning?",
        "\"Because the ecosystem is there: NumPy, Pandas, scikit-learn, PyTorch, TensorFlow and Hugging Face are all Python-first. Python is quick to write and read, which suits experimentation in notebooks, and the slow parts run in optimised C, C++ or CUDA under the hood, so we get productivity without losing speed.\"")]),

M("m-py-datatypes", "Data types and data structures: list, tuple, dict, set", "Basic",
  "Python's built-in types (int, float, str, bool) and containers (list, tuple, dict, set) are the building blocks for holding data before it goes into NumPy or Pandas.",
  """### Scalar types
`int` (unlimited size), `float` (64-bit), `complex`, `bool` (`True/False`), `str` (immutable text), `None`.

### Containers
|Type|Syntax|Ordered|Mutable|Duplicates|Lookup|Use in ML|
|list|`[1, 2, 3]`|yes|yes|yes|by index O(1), search O(n)|sequences of samples, batches|
|tuple|`(1, 2)`|yes|no|yes|index O(1)|fixed records, shapes like `(28, 28)`|
|dict|`{"lr": 0.01}`|insertion order|yes|unique keys|by key O(1) average|configs, hyperparameters, vocabularies|
|set|`{"cat", "dog"}`|no|yes|no|membership O(1)|unique labels, stop-word lists|

### Mutability matters
Lists and dicts are **mutable**: `b = a` makes two names for one object, so changing `b` changes `a`. Use `a.copy()` (shallow) or `copy.deepcopy(a)`.

### Slicing
`x[start:stop:step]` — `x[-1]` last item, `x[::-1]` reversed, `x[:3]` first three. The same idea extends to NumPy arrays and Pandas.

### Useful built-ins
`len, sorted, min, max, sum, zip, enumerate, any, all, map, filter`; `collections.Counter` for counting words, `defaultdict` for grouping.""",
  code="""
from collections import Counter, defaultdict

sample = {"text": "great movie", "label": 1}          # dict = one record
batch = [sample, {"text": "boring plot", "label": 0}] # list of records
shape = (28, 28)                                      # tuple = fixed shape
labels = {r["label"] for r in batch}                  # set of unique labels
print(shape, labels)

words = "the cat sat on the mat the end".split()
print(Counter(words).most_common(2))                  # word frequencies

by_len = defaultdict(list)
for w in words:
    by_len[len(w)].append(w)
print(dict(by_len))

a = [1, 2, 3]; b = a; b.append(4)                     # same object!
print(a, a is b, a[::-1], a[1:3])
""",
  say=[("What's the difference between a list and a tuple, and when would you use a tuple?",
        "\"A list is mutable and a tuple is immutable. I use a tuple for fixed records that shouldn't change — like an image shape (224, 224, 3) or returning several values from a function — and because tuples are hashable they can be dictionary keys. Lists are for collections that grow or change, like accumulating predictions.\"")]),

M("m-py-functions", "Defining and calling functions; lambdas, args, scope", "Basic",
  "Functions package reusable logic. In ML you write them for preprocessing, metrics and training steps.",
  """### Defining and calling
```python
def normalize(x, low=0.0, high=1.0):
    \"\"\"Scale values in x to [low, high].\"\"\"
    ...
normalize(values)                 # positional
normalize(values, high=10)        # keyword argument
```
- **Default arguments** must not be mutable (never `def f(x=[])`; use `None`).
- **`*args`** collects extra positional arguments into a tuple; **`**kwargs`** collects keyword arguments into a dict — common in library wrappers.
- **Return** several values as a tuple: `return mean, std`.

### Lambdas and higher-order functions
`lambda x: x ** 2` is an anonymous one-line function; pass functions as arguments to `sorted(key=...)`, `map`, `filter`, or Pandas `apply`.

### Scope
LEGB rule: Local → Enclosing → Global → Built-in. Avoid modifying globals inside functions; pass data in and return results out (easier to test).

### Docstrings and type hints
`def f(x: list[float]) -> float:` documents intent; tools like VS Code use hints for autocomplete.

### Recursion and generators
Recursion works but Python has a default depth limit (~1000). **Generators** (`yield`) produce items lazily — ideal for streaming large datasets in batches.""",
  code="""
from typing import Iterable

def min_max_scale(xs: list[float], low: float = 0.0, high: float = 1.0) -> list[float]:
    \"\"\"Scale numbers into [low, high].\"\"\"
    lo, hi = min(xs), max(xs)
    return [low + (x - lo) * (high - low) / (hi - lo) for x in xs]

def summary(*values, **opts):
    rounded = opts.get("round", 2)
    return round(sum(values) / len(values), rounded), len(values)

def batches(items: Iterable, size: int):
    \"\"\"Generator: yield fixed-size batches lazily.\"\"\"
    batch = []
    for it in items:
        batch.append(it)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch

print(min_max_scale([10, 20, 15, 40]))
print(summary(3, 4, 8, round=1))
print(sorted(["banana", "kiwi", "apple"], key=lambda w: len(w)))
for b in batches(range(7), 3):
    print(b)
""",
  say=[("What is a generator and why is it useful in ML?",
        "\"A generator is a function that uses yield to produce values one at a time instead of building a whole list in memory. For ML that means I can stream a dataset that doesn't fit in RAM in mini-batches — exactly what PyTorch DataLoaders and Keras data pipelines do internally.\"")]),

M("m-py-oop", "Classes and objects in Python (how libraries are built)", "Basic",
  "scikit-learn estimators, PyTorch modules and Keras models are all Python classes; knowing classes lets you read and extend them.",
  """- `class Name:` with `__init__(self, ...)` as the constructor; `self` is the instance (like `this` in Java).
- **Inheritance**: `class MyNet(nn.Module):` — you override `forward`. scikit-learn estimators share `fit / predict / transform`.
- **Dunder methods**: `__len__`, `__getitem__` (makes a PyTorch `Dataset` indexable), `__repr__`, `__call__` (calling a model object runs `forward`).
- `@property`, `@staticmethod`, `@classmethod`; `@dataclass` for simple config objects.
- Python has no `private`; a leading underscore `_name` means "internal by convention".""",
  code="""
from dataclasses import dataclass

@dataclass
class TrainConfig:
    lr: float = 0.01
    epochs: int = 5

class MeanPredictor:
    \"\"\"A tiny estimator with the scikit-learn style fit/predict API.\"\"\"
    def fit(self, X, y):
        self.mean_ = sum(y) / len(y)     # trailing underscore = learned attribute
        return self                       # returning self allows chaining
    def predict(self, X):
        return [self.mean_ for _ in X]

class SquaresDataset:
    def __init__(self, n): self.n = n
    def __len__(self): return self.n
    def __getitem__(self, i): return i, i * i

print(TrainConfig(lr=0.1))
print(MeanPredictor().fit([[1], [2]], [10, 20]).predict([[3], [4]]))
ds = SquaresDataset(4)
print(len(ds), ds[3], [ds[i] for i in range(len(ds))])
""",
  say=[("What does fit/predict/transform mean in scikit-learn?",
        "\"Every scikit-learn estimator follows one API. fit learns parameters from training data and stores them in attributes ending with an underscore, like coef_. predict applies a fitted model to new data, and transform changes data — for scalers or PCA. Because they all share it, I can swap models or chain them in a Pipeline.\"")]),

M("m-py-libraries", "Python library packages: pip, imports, virtual environments, the ML stack", "Basic",
  "Libraries are installed with pip (or conda) and imported into your code. The ML stack is NumPy → Pandas → Matplotlib → scikit-learn → PyTorch/TensorFlow → Hugging Face.",
  """### Installing and importing
- `pip install numpy pandas scikit-learn` (in Colab prefix with `!`). `import numpy as np` — the community aliases are `np`, `pd`, `plt`, `sns`, `tf`.
- Pin versions in `requirements.txt` so others can reproduce your results.
- **Virtual environments** (`venv`, `conda`) isolate each project's packages.

### The ML stack
|Library|What it does|
|NumPy|fast n-dimensional arrays and maths (the base of everything)|
|Pandas|tables (DataFrames): load CSV/Excel, clean, group, join|
|Matplotlib / Seaborn|plots and statistical charts|
|SciPy|scientific maths: statistics, optimisation, linear algebra, signal processing|
|scikit-learn|classical ML: preprocessing, models, metrics, pipelines|
|PyTorch, TensorFlow/Keras|deep learning with GPUs and automatic differentiation|
|Hugging Face (transformers, datasets)|pretrained transformer models for NLP, vision, speech|
|NLTK / spaCy|classical NLP tools|
|OpenCV|images and video|
|FastAPI|serving models as web APIs|
|LangChain / LlamaIndex|building LLM and RAG applications|""",
  code="""
import sys, importlib
for name in ["numpy", "pandas", "sklearn", "scipy", "matplotlib"]:
    mod = importlib.import_module(name)
    print(f"{name:12s} {mod.__version__}")
print("python", sys.version.split()[0])
""",
  say=[("How do you make your ML project reproducible for someone else?",
        "\"A virtual environment with pinned versions in requirements.txt or an environment file, fixed random seeds, data versioning or a script that downloads the exact data, and a README with the run commands. For anything deployed I'd also use a Docker image so the environment is identical.\"")]),

M("m-numpy", "NumPy: arrays, shapes, broadcasting, vectorisation", "Basic",
  "NumPy arrays are fast, fixed-type n-dimensional grids of numbers. Every image, batch and weight matrix in ML is an array.",
  """### Why NumPy
A Python list of a million numbers is a million separate objects; a NumPy array is one contiguous block of memory processed by optimised C, often **50–100x faster**. Writing maths on whole arrays instead of loops is called **vectorisation**.

### Essentials
- Create: `np.array`, `np.zeros`, `np.ones`, `np.arange`, `np.linspace`, `np.random.default_rng(42).normal(...)`.
- **Shape and axes**: `a.shape` like `(batch, height, width, channels)`; `axis=0` operates down rows (per column), `axis=1` across columns.
- **Indexing**: slices `a[1:3, :]`, boolean masks `a[a > 0]`, fancy indexing `a[[0, 2]]`.
- **Reshape**: `reshape`, `ravel`, `transpose`/`.T`, `np.newaxis`/`expand_dims`.
- **Broadcasting**: arrays of different shapes combine when trailing dimensions match or are 1 — e.g. subtract a per-column mean `(n, d) - (d,)`.
- Maths: `@` matrix multiply, `np.dot`, `np.linalg.inv/eig/svd/norm`, `sum/mean/std(axis=...)`, `argmax`.""",
  code="""
import numpy as np

rng = np.random.default_rng(42)
X = rng.normal(loc=50, scale=10, size=(5, 3))   # 5 samples, 3 features
print("shape:", X.shape)

# vectorised standardisation with broadcasting: (5,3) - (3,)
Xz = (X - X.mean(axis=0)) / X.std(axis=0)
print("column means ~0:", Xz.mean(axis=0).round(6))

# boolean mask + argmax
print("values > 55:", X[X > 55].round(1))
print("best sample per feature:", X.argmax(axis=0))

# matrix multiply: linear model y = X w + b
w, b = np.array([0.2, -0.1, 0.5]), 1.0
print("predictions:", (X @ w + b).round(2))

img = np.arange(16).reshape(4, 4)               # a tiny 'image'
print(img[1:3, 1:3])                            # crop
""",
  demo=None,
  say=[("What is broadcasting in NumPy?",
        "\"Broadcasting is how NumPy combines arrays of different shapes without copying: dimensions are compared from the right and must be equal or 1, and size-1 dimensions are stretched. So I can subtract a (3,) vector of column means from a (1000, 3) matrix in one vectorised operation instead of a loop.\"")]),

M("m-pandas", "Pandas: DataFrames for loading, cleaning and analysing data", "Basic",
  "Pandas gives you DataFrames — Excel-like tables in Python — to load CSV/Excel/SQL data, clean it, group it and feed it to models.",
  """### Core objects
- **Series**: one labelled column. **DataFrame**: a table of Series sharing an index.

### Everyday operations
- Load: `pd.read_csv`, `read_excel`, `read_json`, `read_sql`. Inspect: `head`, `info`, `describe`, `shape`, `dtypes`, `value_counts`.
- Select: `df["col"]`, `df[["a","b"]]`, `df.loc[row_labels, cols]`, `df.iloc[row_positions, cols]`, filter `df[df.age > 30]`, `query("age > 30")`.
- Clean: `isna().sum()`, `fillna`, `dropna`, `drop_duplicates`, `astype`, `str` methods, `pd.to_datetime`.
- Transform: new columns, `apply`, `map`, `pd.cut` (binning), `pd.get_dummies` (one-hot).
- Aggregate: `groupby(...).agg(...)`, `pivot_table`, `merge` (SQL joins), `concat`.
- Time series: datetime index, `resample("D").sum()`, `rolling(7).mean()`, `shift`.

### Pitfalls
Avoid row-by-row loops (`iterrows`) — use vectorised column operations. Beware **chained assignment**; use `.loc[mask, "col"] = value`.""",
  code="""
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "city":   ["Chennai", "Mumbai", "Chennai", "Delhi", "Mumbai", "Delhi"],
    "age":    [25, 32, np.nan, 41, 29, 35],
    "salary": [52000, 81000, 61000, np.nan, 75000, 69000],
    "left":   [0, 1, 0, 0, 1, 0],
})
print(df.info() or "")
print(df.isna().sum())

df["age"] = df["age"].fillna(df["age"].median())
df["salary"] = df.groupby("city")["salary"].transform(lambda s: s.fillna(s.mean()))
df["age_band"] = pd.cut(df["age"], bins=[0, 30, 40, 100], labels=["<30", "30-40", "40+"])

print(df.groupby("city").agg(avg_salary=("salary", "mean"), attrition=("left", "mean")))
print(pd.get_dummies(df, columns=["city"], dtype=int).head(3))
""",
  say=[("How do you handle missing values in a dataset?",
        "\"First I check how much is missing and whether it's random — sometimes 'missing' is itself informative, so I add an is_missing flag. For a few missing numeric values I impute the median, or a group-wise median; for categories, the mode or an 'Unknown' category. If a column is mostly empty I drop it. For important features I might use model-based imputation like KNN or iterative imputation. And imputation is fitted on the training set only, inside a pipeline, to avoid leakage.\"")]),

M("m-matplotlib", "Matplotlib and Seaborn: visualising data", "Basic",
  "Plots reveal distributions, relationships and model behaviour faster than tables. Matplotlib is the base; Seaborn adds statistical plots in one line.",
  """### The two interfaces
- Quick: `plt.plot(x, y); plt.show()`.
- Recommended: `fig, ax = plt.subplots(1, 2, figsize=(10, 4))` then `ax.plot(...)`, `ax.set_title(...)` — explicit and works for grids of plots.

### Which plot for which question
|Question|Plot|
|How is one variable distributed?|histogram, KDE, box plot|
|How do two numeric variables relate?|scatter plot (+ regression line)|
|Compare categories|bar chart, box/violin per category|
|Trend over time|line chart|
|Correlations among many features|heatmap of the correlation matrix|
|Model quality|confusion matrix, ROC/PR curves, learning curves, residual plots|
|High-dimensional data|PCA / t-SNE scatter|

### Good habits
Label axes with units, title every plot, use colour-blind-safe palettes, save with `fig.savefig("plot.png", dpi=150, bbox_inches="tight")`.""",
  code="""
import matplotlib
matplotlib.use("Agg")                     # headless; in Colab/VS Code plots show inline
import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(0)
heights = rng.normal(165, 8, 500)
x = rng.uniform(0, 10, 100); y = 3 * x + rng.normal(0, 3, 100)

fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
axes[0].hist(heights, bins=30, color="#2a78d6", edgecolor="white")
axes[0].set(title="Distribution of heights", xlabel="cm", ylabel="count")
axes[1].scatter(x, y, s=12, alpha=0.7)
m, c = np.polyfit(x, y, 1)
axes[1].plot(np.sort(x), m * np.sort(x) + c, color="#eb6834", label=f"fit y={m:.1f}x+{c:.1f}")
axes[1].set(title="Relationship", xlabel="x", ylabel="y"); axes[1].legend()
fig.tight_layout(); fig.savefig("plots.png", dpi=120)
print("saved plots.png; slope =", round(m, 2))
""",
  say=[("What visualisations do you do first on a new dataset?",
        "\"Histograms or box plots of each numeric feature to see skew and outliers, bar charts of category counts and of the target to check class imbalance, a correlation heatmap, and scatter plots of the strongest features against the target. For time series, a line plot with rolling averages and seasonality. These usually shape my preprocessing and model choice.\"")]),

M("m-scipy", "SciPy: statistics, optimisation and scientific tools", "Intermediate",
  "SciPy builds on NumPy with ready-made scientific routines: probability distributions and tests, optimisation, interpolation, sparse matrices and signal processing.",
  """- `scipy.stats`: distributions (`norm`, `binom`, `poisson`, `expon`) with `pdf/pmf`, `cdf`, `ppf` (inverse CDF), `rvs` (samples); tests (`ttest_ind`, `chi2_contingency`, `pearsonr`, `shapiro`).
- `scipy.optimize`: `minimize` (gradient-based and derivative-free), `curve_fit` for fitting functions to data, root finding.
- `scipy.sparse`: memory-efficient sparse matrices (TF-IDF matrices are sparse).
- `scipy.signal` and `scipy.fft`: filtering and frequency analysis — used for vibration and audio (bearing anomaly capstone!).
- `scipy.spatial`: distances, KD-trees for nearest neighbours.""",
  code="""
import numpy as np
from scipy import stats, optimize, signal

# probability: P(Z < 1.96) and 95th percentile of a normal
print(round(stats.norm.cdf(1.96), 4), round(stats.norm.ppf(0.95), 4))

# two-sample t-test: did the new model reduce error?
rng = np.random.default_rng(1)
old, new = rng.normal(10, 2, 40), rng.normal(9, 2, 40)
t, p = stats.ttest_ind(old, new)
print(f"t={t:.2f}, p={p:.4f}")

# optimisation: minimise (x-3)^2 + 2
res = optimize.minimize(lambda x: (x[0] - 3) ** 2 + 2, x0=[0.0])
print("argmin:", res.x.round(4), "min:", round(res.fun, 4))

# signal: dominant frequency of a noisy 50 Hz vibration sampled at 1 kHz
t_ = np.arange(0, 1, 1 / 1000); x = np.sin(2 * np.pi * 50 * t_) + 0.5 * rng.normal(size=t_.size)
f, pxx = signal.periodogram(x, fs=1000)
print("dominant frequency:", f[pxx.argmax()], "Hz")
""",
  say=[("How would you check whether a new model is really better than the old one?",
        "\"Compare them on the same held-out folds and use a statistical test on the per-fold or per-sample errors — a paired t-test or a Wilcoxon signed-rank test — or bootstrap the metric difference to get a confidence interval. If the interval excludes zero, the improvement is unlikely to be noise. And then confirm with an online A/B test if it's a production model.\"")]),

M("m-py-io", "Files, errors and working with data formats (CSV, JSON, images)", "Basic",
  "Real projects read and write files, call web APIs and must not crash on bad data: use context managers, exceptions and the right format libraries.",
  """- **Files**: `with open("data.txt", encoding="utf-8") as f:` closes the file automatically. `pathlib.Path` for paths that work on Windows and Linux.
- **CSV/Excel**: Pandas `read_csv/to_csv`, `read_excel`. **JSON**: `json.load/dump`. **Parquet**: fast columnar format for big tables.
- **Images**: Pillow (`PIL.Image.open`), OpenCV (`cv2.imread`, note BGR order), or `torchvision.io`.
- **Exceptions**: `try / except ValueError as e / else / finally`; raise your own with `raise ValueError("...")`. Catch specific exceptions, not bare `except:`.
- **Logging** instead of print in production scripts; **argparse** for command-line options.
- **Web/APIs**: `requests.get(url, timeout=10).json()`.""",
  code="""
import json, csv
from pathlib import Path

folder = Path("demo_data"); folder.mkdir(exist_ok=True)
rows = [{"text": "loved it", "label": 1}, {"text": "waste of time", "label": 0}]

with open(folder / "reviews.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)
with open(folder / "reviews.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["text", "label"]); w.writeheader(); w.writerows(rows)

def parse_label(value):
    try:
        return int(value)
    except ValueError:
        print(f"bad label {value!r}, using -1")
        return -1

print([parse_label(v) for v in ["1", "0", "positive"]])
print(json.loads((folder / "reviews.json").read_text())[0])
print(sorted(p.name for p in folder.iterdir()))
""",
  say=[("How do you load a dataset that doesn't fit in memory?",
        "\"Read it in chunks — pandas read_csv with chunksize, or a generator — and process or aggregate each chunk. Better formats help too: Parquet with only the needed columns, or memory-mapped NumPy arrays. For training, a streaming DataLoader or tf.data pipeline that reads batches from disk, or tools like Dask or Spark for distributed processing.\"")]),
]

PYTHON.insert(0, M("m-setup", "Set up your ML workspace: Google Colab and VS Code", "Basic",
  "You'll run every example in this course either in Google Colab (free, browser, GPU) or locally in VS Code with a virtual environment. Set both up once.",
  """### Google Colab (recommended to start)
1. Go to colab.research.google.com and sign in with a Google account → **New notebook**.
2. A notebook is a list of **cells**: code cells (run with Shift+Enter) and text cells (Markdown).
3. Most libraries are pre-installed; install others with `!pip install xgboost` in a cell.
4. **GPU**: Runtime → Change runtime type → T4 GPU (needed for deep learning chapters). Check with `torch.cuda.is_available()`.
5. Files: upload via the folder icon, or mount Google Drive (`from google.colab import drive; drive.mount('/content/drive')`) so work survives restarts.
6. Secrets (API keys): the key icon → add `OPENAI_API_KEY` etc. → `from google.colab import userdata; userdata.get('OPENAI_API_KEY')`. Never paste keys into notebooks you share.
7. Sessions reset after inactivity — save to Drive or GitHub.

### VS Code (local)
1. Install Python 3.11+ and VS Code, then the **Python** and **Jupyter** extensions.
2. Create a project folder and a virtual environment: `python -m venv .venv` → activate (`.venv\\Scripts\\activate` on Windows, `source .venv/bin/activate` on macOS/Linux) → select it as the interpreter in VS Code.
3. `pip install numpy pandas matplotlib seaborn scikit-learn scipy jupyter` (add `torch`, `transformers`, `xgboost` later; get the right PyTorch command from pytorch.org for your GPU).
4. Use `.ipynb` notebooks for exploration and `.py` files for reusable code; freeze versions with `pip freeze > requirements.txt`.
5. Git + GitHub to version your projects (and your capstone).

### Copy-paste workflow for this course
Every concept card has a **Copy** button on its code. Paste into a Colab cell and run; cards marked *needs internet / API key* download models or call paid APIs.""",
  code='''
import sys, platform
print("Python", sys.version.split()[0], "on", platform.system())
try:
    import torch; print("PyTorch", torch.__version__, "| GPU available:", torch.cuda.is_available())
except ImportError:
    print("PyTorch not installed yet: pip install torch")
import numpy, pandas, sklearn, matplotlib
print("numpy", numpy.__version__, "| pandas", pandas.__version__, "| scikit-learn", sklearn.__version__, "| matplotlib", matplotlib.__version__)
''',
  say=[("Where do you usually prototype and how do you move to production code?",
        "\"I explore in notebooks — Colab when I need a free GPU, or Jupyter in VS Code — then move stable logic into Python modules with functions, tests and a requirements file in Git, and run training as scripts or pipelines. Notebooks are great for exploration but hard to test and review, so they shouldn't be the production artifact.\"")]))
