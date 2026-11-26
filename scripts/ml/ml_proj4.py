"""End-to-end projects 21-26: statistics toolkit, regression engine, credit scorecard, face explorer, text analytics, mini-GPT."""
from ml_proj_util import P, S

TITANIC = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
HOUSING = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
GERMAN = "https://raw.githubusercontent.com/selva86/datasets/master/GermanCredit.csv"
SMS = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
SHAKES = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
GI = "__pycache__/\n.venv/\ndata/\n*.joblib\n*.pt\n*.png\n.ipynb_checkpoints/\n"

# ---------------------------------------------------------------- P21
P21 = P("p-stats-toolkit", "Statistics & probability toolkit in pure Python + NumPy (Titanic)", "stats", "Basic", "2–3 days", "VS Code or Colab (CPU)",
  "Build your own small statistics library — data loading with a cleaning log, robust summaries, probability tables, conditional probability and Bayes, random variables, ECDF/KDE, correlation and entropy — implemented with plain Python and NumPy, verified against pandas/SciPy by tests, and used to write a data report on the Titanic passengers.",
  ["`check_env.py`: environment health check (interpreter, versions, GPU) that writes requirements.lock", "`toolkit/data.py`: download + cache + typed cleaning with a logged rule table (missing ages, fares, ports)",
   "`toolkit/describe.py`: a `Summary` class (mean/median/mode, variance, IQR, MAD, skew, outliers) in NumPy", "`toolkit/prob.py`: `ProbTable` (joint/conditional/marginal, independence, Bayes), random-variable helpers, ECDF, KDE, Pearson/Spearman, entropy & information gain",
   "`report.py`: a Markdown report answering real questions with uncertainty", "`tests/`: every function checked against pandas/SciPy"],
  ["Python data types and classes", "NumPy vectorisation", "data cleaning with an audit log", "probability rules, Bayes", "expectation/variance", "ECDF, KDE", "correlation", "entropy", "pytest"],
  "Titanic passenger list (891 passengers) from a public GitHub mirror.",
  ["environment check", "load + clean with log", "robust summaries", "probability tables", "distributions", "dependence measures", "report", "tests"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\npandas>=2.0\nscipy>=1.11\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Environment check", """Run this first on any new machine or Colab runtime: it proves you're using the interpreter you think you are, records exact versions for reproducibility, and tells you whether a GPU is available.""",
     "check_env.py", '''
import importlib, platform, sys


def main() -> dict:
    info = {"python": platform.python_version(), "interpreter": sys.executable}
    for pkg in ["numpy", "pandas", "scipy"]:
        try:
            info[pkg] = importlib.import_module(pkg).__version__
        except ImportError:
            info[pkg] = None
    try:
        import torch
        info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"
    except ImportError:
        info["gpu"] = "torch not installed"
    with open("requirements.lock", "w") as f:
        f.writelines(f"{k}=={v}\\n" for k, v in info.items() if k in ("numpy", "pandas", "scipy") and v)
    return info


if __name__ == "__main__":
    for k, v in main().items():
        print(f"{k:12s} {v}")
'''),
   S("Package marker", "", "toolkit/__init__.py", '"""A tiny statistics toolkit."""\n'),
   S("Load and clean with a log", """Real data is messy; every cleaning rule is recorded with how many rows it touched, so the report can say exactly what was done. Ages are imputed by passenger title (Mr/Mrs/Miss/Master) — a group-wise rule that is far better than one global median.""",
     "toolkit/data.py", f'''
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd

URL = "{TITANIC}"


@dataclass
class Cleaned:
    df: pd.DataFrame
    log: list[tuple[str, int]] = field(default_factory=list)


def load_raw(cache: str = "data/titanic.csv") -> pd.DataFrame:
    p = Path(cache); p.parent.mkdir(exist_ok=True)
    if not p.exists():
        pd.read_csv(URL).to_csv(p, index=False)
    return pd.read_csv(p)


def clean(raw: pd.DataFrame) -> Cleaned:
    df, log = raw.copy(), []
    n = len(df); df = df.drop_duplicates("PassengerId"); log.append(("duplicate passengers removed", n - len(df)))
    df["Title"] = df["Name"].str.extract(r",\\s*([^.]+)\\.")[0].replace({{"Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs"}})
    df.loc[~df["Title"].isin(["Mr", "Mrs", "Miss", "Master"]), "Title"] = "Rare"
    miss = int(df["Age"].isna().sum()); df["Age"] = df["Age"].fillna(df.groupby("Title")["Age"].transform("median")); log.append(("ages imputed by title median", miss))
    miss = int(df["Embarked"].isna().sum()); df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0]); log.append(("ports filled with the most common port", miss))
    zero = int((df["Fare"] == 0).sum()); df.loc[df["Fare"] == 0, "Fare"] = pd.NA
    df["Fare"] = df["Fare"].astype(float).fillna(df.groupby("Pclass")["Fare"].transform("median")); log.append(("zero fares replaced by class median", zero))
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1; df["Female"] = (df["Sex"] == "female").astype(int)
    return Cleaned(df, log)
'''),
   S("Robust summaries (a class)", """A small class that computes everything once and exposes it as attributes — the same pattern scikit-learn uses. All maths is NumPy (no pandas helpers) so you see the formulas: sample variance divides by n − 1; MAD × 1.4826 estimates σ robustly; Tukey fences flag outliers.""",
     "toolkit/describe.py", '''
from __future__ import annotations
import numpy as np


class Summary:
    """Centre, spread, shape and outliers of one numeric column."""

    def __init__(self, values):
        x = np.asarray(values, dtype=float); self.x = x[~np.isnan(x)]; x = self.x; n = len(x)
        self.n, self.mean, self.median = n, x.sum() / n, float(np.median(x))
        vals, counts = np.unique(x, return_counts=True); self.mode = float(vals[counts.argmax()])
        self.var = ((x - self.mean) ** 2).sum() / (n - 1); self.std = self.var ** 0.5
        self.q1, self.q3 = np.percentile(x, [25, 75]); self.iqr = self.q3 - self.q1
        self.mad = float(np.median(np.abs(x - self.median)) * 1.4826)
        self.skew = float((((x - self.mean) / x.std()) ** 3).mean())
        self.lo_fence, self.hi_fence = self.q1 - 1.5 * self.iqr, self.q3 + 1.5 * self.iqr

    def outliers(self) -> np.ndarray:
        return self.x[(self.x < self.lo_fence) | (self.x > self.hi_fence)]

    def as_dict(self) -> dict:
        return {k: round(float(getattr(self, k)), 3) for k in ("n", "mean", "median", "mode", "std", "iqr", "mad", "skew")}
'''),
   S("Probability, distributions, dependence", """`ProbTable` turns two categorical columns into joint, marginal and conditional probabilities, checks independence and applies Bayes' rule. The other helpers implement expectation/variance of a discrete random variable, the empirical CDF, a Gaussian KDE, Pearson/Spearman correlation and entropy/information gain — each a few NumPy lines.""",
     "toolkit/prob.py", '''
from __future__ import annotations
import numpy as np, pandas as pd


class ProbTable:
    def __init__(self, a: pd.Series, b: pd.Series):
        self.joint = pd.crosstab(a, b, normalize=True); self.pa = self.joint.sum(1); self.pb = self.joint.sum(0)

    def p_b_given_a(self) -> pd.DataFrame:            # P(B | A) = P(A, B) / P(A)
        return self.joint.div(self.pa, axis=0)

    def p_a_given_b(self) -> pd.DataFrame:            # Bayes: P(A | B) = P(B | A) P(A) / P(B)
        return self.p_b_given_a().mul(self.pa, axis=0).div(self.pb, axis=1)

    def independence_gap(self) -> float:              # max |P(A,B) - P(A)P(B)|; 0 means independent
        return float((self.joint - np.outer(self.pa, self.pb)).abs().to_numpy().max())


def expectation(values, probs) -> tuple[float, float]:
    v, p = np.asarray(values, float), np.asarray(probs, float); m = (v * p).sum(); return float(m), float(((v - m) ** 2 * p).sum())


def ecdf(x, t) -> float:
    x = np.asarray(x, float); return float((x <= t).mean())


def kde(x, grid, bandwidth=None) -> np.ndarray:
    x, grid = np.asarray(x, float), np.asarray(grid, float)
    h = bandwidth or 1.06 * x.std(ddof=1) * len(x) ** (-1 / 5)                # Silverman's rule
    z = (grid[:, None] - x[None]) / h; return np.exp(-0.5 * z ** 2).sum(1) / (len(x) * h * np.sqrt(2 * np.pi))


def pearson(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float); a, b = a - a.mean(), b - b.mean(); return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def spearman(a, b) -> float:
    return pearson(pd.Series(a).rank(), pd.Series(b).rank())


def entropy(labels) -> float:
    p = pd.Series(labels).value_counts(normalize=True).to_numpy(); return float(-(p * np.log2(p)).sum())


def information_gain(feature, labels) -> float:
    df = pd.DataFrame({"f": feature, "y": labels}); cond = sum(len(g) / len(df) * entropy(g.y) for _, g in df.groupby("f")); return entropy(labels) - cond
'''),
   S("The report", """Answer real questions with the toolkit and write them to `report.md`, always with an uncertainty estimate (standard error) and the cleaning log at the top.""",
     "report.py", '''
import numpy as np
from toolkit.data import clean, load_raw
from toolkit.describe import Summary
from toolkit.prob import ProbTable, ecdf, entropy, expectation, information_gain, kde, pearson, spearman


def build() -> str:
    c = clean(load_raw()); df = c.df; lines = ["# Titanic statistics report", "", "## Cleaning log"] + [f"- {r}: {k}" for r, k in c.log]
    p = df.Survived.mean(); se = np.sqrt(p * (1 - p) / len(df))
    lines += ["", "## Survival", f"- P(survive) = {p:.3f} ± {1.96 * se:.3f} (95% CI)"]
    t = ProbTable(df.Sex, df.Survived); lines += [f"- P(survive | {s}) = {t.p_b_given_a().loc[s, 1]:.3f}" for s in ("female", "male")]
    lines += [f"- Bayes: P(female | survived) = {t.p_a_given_b().loc['female', 1]:.3f}; independence gap = {t.independence_gap():.3f}"]
    pmf = df.FamilySize.value_counts(normalize=True).sort_index(); m, v = expectation(pmf.index, pmf.values)
    lines += ["", "## Family size as a random variable", f"- E[size] = {m:.2f}, Var = {v:.2f}"]
    fare = Summary(df.Fare); lines += ["", "## Fare (robust summary)", f"- {fare.as_dict()}", f"- Tukey outliers: {len(fare.outliers())} fares above £{fare.hi_fence:.0f}"]
    lines += [f"- ECDF: {ecdf(df.Fare, 15):.0%} of passengers paid ≤ £15; KDE peak near £{np.linspace(0, 100, 201)[kde(df.Fare, np.linspace(0, 100, 201)).argmax()]:.1f}"]
    lines += ["", "## Dependence", f"- Fare vs class: Pearson {pearson(df.Fare, df.Pclass):.3f}, Spearman {spearman(df.Fare, df.Pclass):.3f}",
              f"- H(survived) = {entropy(df.Survived):.3f} bits; information gain: " + ", ".join(f"{f} {information_gain(df[f], df.Survived):.3f}" for f in ("Sex", "Pclass", "Embarked", "Title"))]
    return "\\n".join(lines)


if __name__ == "__main__":
    text = build(); open("report.md", "w").write(text); print(text)
'''),
   S("Tests against pandas and SciPy", "", "tests/test_toolkit.py", '''
import numpy as np, pandas as pd
from scipy import stats
from toolkit.data import clean, load_raw
from toolkit.describe import Summary
from toolkit.prob import ProbTable, ecdf, entropy, expectation, kde, pearson, spearman

DF = clean(load_raw()).df


def test_cleaning_removes_missing_values():
    assert DF[["Age", "Embarked", "Fare"]].isna().sum().sum() == 0 and (DF.Fare > 0).all()


def test_summary_matches_pandas():
    s = Summary(DF.Age); assert np.isclose(s.mean, DF.Age.mean()) and np.isclose(s.std, DF.Age.std()) and np.isclose(s.median, DF.Age.median())
    assert np.isclose(s.mad, stats.median_abs_deviation(DF.Age, scale="normal"))


def test_probability_rules():
    t = ProbTable(DF.Sex, DF.Survived); assert np.isclose(t.joint.to_numpy().sum(), 1)
    assert np.allclose(t.p_b_given_a().sum(1), 1)
    total = (t.p_b_given_a()[1] * t.pa).sum(); assert np.isclose(total, DF.Survived.mean())       # law of total probability


def test_distributions_and_dependence():
    assert np.isclose(expectation([1, 2, 3, 4, 5, 6], [1 / 6] * 6)[0], 3.5)
    assert ecdf([1, 2, 3, 4], 2) == 0.5
    grid = np.linspace(-50, 400, 2000); assert abs(np.trapezoid(kde(DF.Fare, grid), grid) - 1) < 0.02
    assert np.isclose(pearson(DF.Age, DF.Fare), stats.pearsonr(DF.Age, DF.Fare)[0]) and np.isclose(spearman(DF.Age, DF.Fare), stats.spearmanr(DF.Age, DF.Fare)[0])
    assert np.isclose(entropy([0, 1, 0, 1]), 1.0) and np.isclose(entropy(pd.Series([1, 1, 1])), 0.0)
'''),
   S("Run it", "", None, "python check_env.py\npython report.py\npytest -q", "bash"),
  ],
  check=["python check_env.py", "python report.py", "pytest -q"],
  talk=["Why group-wise imputation beats a global median, and how you documented every cleaning rule.", "The difference between P(survive | female) and P(female | survive) — and Bayes' rule connecting them.",
        "Why MAD/IQR are more robust than standard deviation for fares."],
  errors=[("ModuleNotFoundError: toolkit", "run commands from the project root (pytest.ini sets the path)"), ("KDE integrates far from 1", "the grid doesn't cover the data range — widen it")],
  extend=["Add bootstrap confidence intervals for every statistic", "Add a chi-square independence test and compare with `independence_gap`", "Publish the toolkit as an installable package (pyproject.toml)"],
  see=["m-setup", "m-py-basics", "m-py-datatypes", "m-py-oop", "m-numpy", "m-data-processing", "m-real-world-data", "m-prob-basics", "m-prob-events", "m-random-variables", "m-pdf-cdf", "m-centre-spread", "m-correlation", "m-info-theory"])

# ---------------------------------------------------------------- P22
P22 = P("p-regression-engine", "Regression engine from scratch: least squares, gradients, regularisation (California housing)", "math", "Intermediate", "2–3 days", "VS Code or Colab (CPU)",
  "Implement linear regression the way libraries do — normal equations, QR, gradient descent with feature scaling, Ridge in closed form and Lasso by coordinate descent — with rank/condition diagnostics, then run the classic experiments: scaling vs convergence, polynomial degree vs overfitting, regularisation paths, bias–variance and learning curves, all checked against scikit-learn.",
  ["`engine/linear.py`: `LinearRegressor` with solvers `normal`, `qr`, `gd` and `ridge`, plus `LassoCD`", "`engine/diagnostics.py`: rank, singular values, condition number, VIF, norms", "`experiments.py`: five experiments printed as tables",
   "`tests/`: parity with scikit-learn and gradient checks"],
  ["vectors, norms, matrix rank", "normal equations and QR", "gradients and step sizes", "feature scaling", "Ridge/Lasso", "overfitting and validation curves", "bias–variance"],
  "California housing (20,640 districts, 1990 census) from the Hands-On ML GitHub repository.",
  ["load + split", "solvers", "diagnostics", "scaling experiment", "complexity experiment", "regularisation path", "bias–variance"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\npandas>=2.0\nscikit-learn>=1.4\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Package marker", "", "engine/__init__.py", ""),
   S("The solvers", """One class, several solvers. `normal` solves XᵀXw = Xᵀy with `np.linalg.solve` (never an explicit inverse); `qr` is the numerically stable route; `gd` follows the gradient (2/n)Xᵀ(Xw − y) with a step size chosen from the largest Hessian eigenvalue; `ridge` adds λI (not to the intercept). `LassoCD` uses soft-thresholding coordinate descent.""",
     "engine/linear.py", '''
from __future__ import annotations
import numpy as np


class LinearRegressor:
    def __init__(self, solver: str = "qr", alpha: float = 0.0, lr: float | None = None, iters: int = 2000):
        self.solver, self.alpha, self.lr, self.iters = solver, alpha, lr, iters

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y, float); A = np.c_[np.ones(len(X)), X]; self.history_ = []
        if self.solver == "normal":
            w = np.linalg.solve(A.T @ A, A.T @ y)
        elif self.solver == "qr":
            Q, R = np.linalg.qr(A); w = np.linalg.solve(R, Q.T @ y)
        elif self.solver == "ridge":
            P = np.eye(A.shape[1]) * self.alpha; P[0, 0] = 0; w = np.linalg.solve(A.T @ A + P, A.T @ y)
        elif self.solver == "gd":
            H = 2 / len(A) * A.T @ A; lr = self.lr or 1.0 / np.linalg.eigvalsh(H).max(); w = np.zeros(A.shape[1])
            for _ in range(self.iters):
                w -= lr * 2 / len(A) * A.T @ (A @ w - y); self.history_.append(float(np.mean((A @ w - y) ** 2)))
        else:
            raise ValueError(self.solver)
        self.intercept_, self.coef_ = w[0], w[1:]; return self

    def predict(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_


class LassoCD:
    """min (1/2n)||y - Xw - b||^2 + alpha*||w||_1 via cyclic coordinate descent with soft-thresholding."""

    def __init__(self, alpha: float, iters: int = 3000, tol: float = 1e-8):
        self.alpha, self.iters, self.tol = alpha, iters, tol

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y, float); n, p = X.shape; xm, ym = X.mean(0), y.mean(); Xc = X - xm
        w, z, r = np.zeros(p), (Xc ** 2).sum(0) / n, y - ym
        for _ in range(self.iters):
            biggest = 0.0
            for j in range(p):
                r += Xc[:, j] * w[j]; rho = Xc[:, j] @ r / n; new = np.sign(rho) * max(abs(rho) - self.alpha, 0) / z[j]
                biggest = max(biggest, abs(new - w[j])); w[j] = new; r -= Xc[:, j] * w[j]
            if biggest < self.tol:
                break
        self.coef_, self.intercept_ = w, ym - xm @ w; return self

    def predict(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_


def standardise(train, *others):
    mu, sd = train.mean(0), train.std(0) + 1e-12; return [(m - mu) / sd for m in (train, *others)]
'''),
   S("Diagnostics", """Before trusting coefficients, check the design matrix: rank (exact dependence), smallest singular value and condition number (near dependence), VIF per feature, and the three norms of the weights.""",
     "engine/diagnostics.py", '''
import numpy as np


def design_report(X) -> dict:
    X = np.asarray(X, float); s = np.linalg.svd(X - X.mean(0), compute_uv=False)
    return {"rank": int(np.linalg.matrix_rank(X - X.mean(0))), "columns": X.shape[1], "smallest_sv": float(s[-1]), "condition": float(s[0] / max(s[-1], 1e-300))}


def vif(X) -> np.ndarray:
    X = np.asarray(X, float); out = []
    for j in range(X.shape[1]):
        others = np.c_[np.ones(len(X)), np.delete(X, j, 1)]; w = np.linalg.lstsq(others, X[:, j], rcond=None)[0]
        r2 = 1 - ((X[:, j] - others @ w) ** 2).sum() / ((X[:, j] - X[:, j].mean()) ** 2).sum(); out.append(1 / max(1 - r2, 1e-12))
    return np.array(out)


def norms(w) -> dict:
    w = np.asarray(w, float); return {"L1": float(np.abs(w).sum()), "L2": float(np.sqrt((w ** 2).sum())), "Linf": float(np.abs(w).max())}
'''),
   S("Experiments", """Five experiments, each answering one question. (1) Do all solvers agree? (2) Why scale features before gradient descent? (3) How does polynomial degree trade bias for variance? (4) What do Ridge and Lasso do to coefficients? (5) More data or more capacity? (learning curve + bias–variance decomposition).""",
     "experiments.py", f'''
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from engine.diagnostics import design_report, norms, vif
from engine.linear import LassoCD, LinearRegressor, standardise

URL = "{HOUSING}"


def load():
    df = pd.read_csv(URL).dropna(); df = df[df.median_house_value < 500001]
    df["rooms_per_hh"] = df.total_rooms / df.households; df["bedrooms_ratio"] = df.total_bedrooms / df.total_rooms
    cols = ["median_income", "housing_median_age", "rooms_per_hh", "bedrooms_ratio", "population", "latitude", "longitude"]
    return df[cols].to_numpy(float), np.log(df.median_house_value.to_numpy()), cols


def rmse(m, X, y): return float(np.sqrt(np.mean((m.predict(X) - y) ** 2)))


def main():
    X, y, cols = load(); Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0); Str, Ste = standardise(Xtr, Xte)
    print("design:", design_report(Str), "| VIF:", dict(zip(cols, vif(Str).round(1))))
    print("\\n1) solvers agree (test RMSE, log $):")
    for s in ["normal", "qr", "gd", "ridge"]:
        m = LinearRegressor(s, alpha=1.0, iters=3000).fit(Str, ytr); print(f"   {{s:7s}} {{rmse(m, Ste, yte):.4f}} | weight norms {{ {{k: round(v, 3) for k, v in norms(m.coef_).items()}} }}")
    print("\\n2) gradient descent: raw vs standardised features (MSE after 300 steps)")
    for name, A in [("raw", Xtr), ("standardised", Str)]:
        m = LinearRegressor("gd", iters=300).fit(A, ytr); print(f"   {{name:12s}} condition {{design_report(A)['condition']:.1e}} | final train MSE {{m.history_[-1]:.4f}}")
    print("\\n3) polynomial degree on 2,000 rows (validation curve)")
    small = slice(0, 2000)
    for d in [1, 2, 3, 4, 5]:
        pf = PolynomialFeatures(d, include_bias=False).fit(Str[small, :4]); A, B = standardise(pf.transform(Str[small, :4]), pf.transform(Ste[:, :4]))
        m = LinearRegressor("qr").fit(A, ytr[small]); print(f"   degree {{d}}: features {{A.shape[1]:3d}} | train {{rmse(m, A, ytr[small]):.3f}} | test {{rmse(m, B, yte):.3f}}")
    print("\\n4) regularisation on degree-4 features")
    for a in [0.0, 1.0, 100.0]: m = LinearRegressor("ridge", alpha=a).fit(A, ytr[small]); print(f"   ridge α={{a:<6}} test {{rmse(m, B, yte):.3f}} | L2 norm {{norms(m.coef_)['L2']:.2f}}")
    for a in [0.001, 0.01, 0.05]: m = LassoCD(a).fit(A, ytr[small]); print(f"   lasso α={{a:<6}} test {{rmse(m, B, yte):.3f}} | non-zero {{int((m.coef_ != 0).sum())}}/{{A.shape[1]}}")
    print("\\n5) learning curve and bias-variance for degree 1 vs 4")
    rng = np.random.default_rng(0)
    for d in [1, 4]:
        pf = PolynomialFeatures(d, include_bias=False).fit(Str[:, :4]); Atr_all, Ate = standardise(pf.transform(Str[:, :4]), pf.transform(Ste[:, :4]))
        curve = [round(rmse(LinearRegressor("ridge", alpha=1e-3).fit(Atr_all[:n], ytr[:n]), Ate, yte), 3) for n in (200, 1000, 5000, len(ytr))]
        P = np.array([LinearRegressor("ridge", alpha=1e-3).fit(Atr_all[i], ytr[i]).predict(Ate) for i in (rng.integers(0, 1000, 1000) for _ in range(20))])
        print(f"   degree {{d}}: test RMSE vs n {{curve}} | bias²+noise {{((P.mean(0) - yte) ** 2).mean():.3f}} variance {{P.var(0).mean():.3f}}")


if __name__ == "__main__":
    main()
'''),
   S("Tests: parity with scikit-learn", "", "tests/test_engine.py", '''
import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from engine.diagnostics import design_report
from engine.linear import LassoCD, LinearRegressor, standardise

X, y = make_regression(400, 6, noise=5.0, random_state=0); (X,) = standardise(X)


def test_solvers_match_sklearn():
    ref = LinearRegression().fit(X, y)
    for s in ["normal", "qr", "gd"]:
        m = LinearRegressor(s, iters=5000).fit(X, y); assert np.allclose(m.coef_, ref.coef_, atol=1e-3), s


def test_ridge_and_lasso_match_sklearn():
    assert np.allclose(LinearRegressor("ridge", alpha=10).fit(X, y).coef_, Ridge(alpha=10).fit(X, y).coef_, atol=1e-6)
    assert np.allclose(LassoCD(1.0).fit(X, y).coef_, Lasso(alpha=1.0, tol=1e-10, max_iter=100000).fit(X, y).coef_, atol=1e-4)


def test_rank_detects_dependence():
    D = np.c_[X, X[:, 0] + X[:, 1]]; assert design_report(D)["rank"] == 6 and design_report(D)["condition"] > 1e10


def test_gradient_formula_matches_finite_difference():
    A = np.c_[np.ones(len(X)), X]; w = np.random.default_rng(0).normal(size=7); L = lambda w: np.mean((A @ w - y) ** 2)
    g = 2 / len(A) * A.T @ (A @ w - y); num = np.array([(L(w + e) - L(w - e)) / 2e-6 for e in np.eye(7) * 1e-6]); assert np.allclose(g, num, rtol=1e-4)
'''),
   S("Run it", "", None, "python experiments.py\npytest -q", "bash"),
  ],
  check=["python experiments.py", "pytest -q"],
  talk=["Why QR is preferred over the normal equations numerically.", "What the condition number tells you about gradient descent speed and coefficient stability.", "How you'd explain the validation curve and the Ridge/Lasso results to a stakeholder."],
  errors=[("GD diverges (nan)", "the learning rate is above 2/λmax — scale features or use the automatic step"), ("Lasso keeps all features", "alpha too small relative to the scale of y")],
  extend=["Add Huber regression via iteratively reweighted least squares", "Add k-fold cross-validation to choose α automatically", "Add an Elastic Net solver"],
  see=["m-linear-regression", "m-least-squares", "m-lin-indep", "m-norms", "m-normalization", "m-optim-math", "m-regularization", "m-overfitting", "m-ml-principles", "m-gradients", "m-matrices"])

# ---------------------------------------------------------------- P23
P23 = P("p-credit-scorecard", "Credit-risk scorecard: classical ML model zoo, costs and a system design (German Credit)", "sup", "Intermediate", "3–4 days", "VS Code or Colab (CPU)",
  "Predict loan default for 1,000 real applicants with every classical model family — baselines and 1R, naive Bayes, LDA/QDA, kNN, decision trees, bagging, AdaBoost, SVMs with different kernels, voting and stacking — using leak-free encoding pipelines, feature selection, cost-based thresholds (AUC computed by integration), reason codes for each decision, and a written system design with capacity and monitoring plans.",
  ["`data.py`: load, encode (one-hot / ordinal / target) inside pipelines, cost matrix", "`zoo.py`: 16 models from 1R to stacking, compared with repeated stratified CV",
   "`select.py`: filter, RFE and L1 selection inside CV", "`scorecard.py`: final calibrated model, expected-cost threshold, AUC by trapezoid integration, reason codes", "`DESIGN.md`: the production system design", "`tests/`"],
  ["categorical encoding without leakage", "kNN, trees, bagging, AdaBoost, SVM kernels, voting, stacking", "feature selection inside CV", "cost-sensitive thresholds", "ROC-AUC as an integral", "reason codes", "ML system design"],
  "Statlog German Credit (1,000 applicants, 20 attributes, 'good'/'bad' credit) from a public GitHub mirror.",
  ["load + cost matrix", "encoders", "model zoo", "feature selection", "calibrated scorecard", "threshold by expected cost", "reason codes", "design doc"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\npandas>=2.0\nscikit-learn>=1.5\njoblib>=1.3\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Data, encoders and the cost matrix", """The classic cost matrix for this dataset says approving a bad applicant costs **5×** rejecting a good one. Encoders live inside pipelines so cross-validation never sees statistics from the validation fold.""",
     "data.py", f'''
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, TargetEncoder

URL = "{GERMAN}"
COST_FN, COST_FP = 5.0, 1.0          # approve a bad applicant vs reject a good one


def load():
    p = Path("data/german.csv"); p.parent.mkdir(exist_ok=True)
    if not p.exists():
        pd.read_csv(URL).to_csv(p, index=False)
    df = pd.read_csv(p); y = (df.pop("credit_risk") == 0).astype(int)     # 1 = BAD credit (the event we predict)
    return df, y


def columns(df):
    num = [c for c in df if pd.api.types.is_numeric_dtype(df[c])]; return num, [c for c in df if c not in num]


def encoder(df, kind="onehot"):
    num, cat = columns(df)
    enc = {{"onehot": OneHotEncoder(handle_unknown="ignore", sparse_output=False), "ordinal": OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
           "target": TargetEncoder(random_state=0)}}[kind]
    return make_column_transformer((StandardScaler(), num), (enc, cat))


def expected_cost(y_true, flag_bad):
    y_true, flag_bad = np.asarray(y_true), np.asarray(flag_bad).astype(bool)
    return float(((~flag_bad) & (y_true == 1)).sum() * COST_FN + (flag_bad & (y_true == 0)).sum() * COST_FP) / len(y_true)
'''),
   S("The model zoo", """Every model is a pipeline (encoder → model) so the comparison is fair and leak-free. 1R and the majority class are the baselines to beat; naive Bayes, LDA and QDA are the probabilistic (generative) classifiers; kernels show linear vs non-linear SVMs; bagging/AdaBoost/voting/stacking show what ensembles add. Repeated stratified CV gives a mean and spread for each.""",
     "zoo.py", '''
import numpy as np, pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier, RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from data import encoder, load


class OneRule(ClassifierMixin, BaseEstimator):
    """1R: pick the single categorical column whose per-value majority vote makes the fewest errors."""

    def fit(self, X, y):
        X, y = pd.DataFrame(X).reset_index(drop=True), pd.Series(np.asarray(y)); best = None
        for c in X:
            rule = y.groupby(X[c].astype(str)).mean(); err = ((X[c].astype(str).map(rule) > 0.5).astype(int) != y).mean()
            if best is None or err < best[0]: best = (err, c, rule)
        _, self.col_, self.rule_ = best; self.classes_ = np.array([0, 1]); self.prior_ = y.mean(); return self

    def predict_proba(self, X):
        p = pd.DataFrame(X)[self.col_].astype(str).map(self.rule_).fillna(self.prior_).to_numpy(); return np.c_[1 - p, p]

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] > 0.5).astype(int)


def models(df):
    e = lambda kind="onehot": encoder(df, kind); lr = LogisticRegression(max_iter=3000, C=0.5)
    base = {"knn": make_pipeline(e(), KNeighborsClassifier(25)), "svm_rbf": make_pipeline(e(), SVC(C=1.0, probability=True, random_state=0)),
            "forest": make_pipeline(e("ordinal"), RandomForestClassifier(400, min_samples_leaf=3, random_state=0, n_jobs=-1)), "logreg": make_pipeline(e(), lr)}
    return {"majority": DummyClassifier(strategy="prior"), "1R (one rule)": OneRule(), "logistic": base["logreg"], "kNN k=25": base["knn"],
            "decision tree": make_pipeline(e("ordinal"), DecisionTreeClassifier(max_depth=4, min_samples_leaf=20, random_state=0)),
            "bagged trees": make_pipeline(e("ordinal"), BaggingClassifier(DecisionTreeClassifier(min_samples_leaf=5), n_estimators=200, random_state=0, n_jobs=-1)),
            "random forest": base["forest"], "AdaBoost stumps": make_pipeline(e("ordinal"), AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=300, learning_rate=0.5, random_state=0)),
            "SVM linear": make_pipeline(e(), SVC(kernel="linear", C=0.05, probability=True, random_state=0)), "SVM RBF": base["svm_rbf"],
            "SVM poly-3": make_pipeline(e(), SVC(kernel="poly", degree=3, C=0.5, probability=True, random_state=0)),
            "naive Bayes": make_pipeline(e(), GaussianNB()), "LDA": make_pipeline(e(), LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
            "QDA": make_pipeline(e(), QuadraticDiscriminantAnalysis(reg_param=0.5)),
            "soft voting": VotingClassifier(list(base.items()), voting="soft"), "stacking": StackingClassifier(list(base.items()), LogisticRegression(), cv=5)}


def compare(repeats=2):
    df, y = load(); cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=repeats, random_state=0); rows = []
    for name, m in models(df).items():
        s = cross_val_score(m, df, y, cv=cv, scoring="roc_auc"); rows.append((name, s.mean(), s.std())); print(f"  {name:16s} AUC {s.mean():.3f} ± {s.std():.3f}", flush=True)
    return pd.DataFrame(rows, columns=["model", "auc", "sd"]).sort_values("auc", ascending=False)


if __name__ == "__main__":
    print(compare())
'''),
   S("Feature selection inside cross-validation", """Three selectors — univariate filter, recursive feature elimination and L1 — each wrapped in the pipeline so selection is re-done in every fold (selecting first and then cross-validating leaks).""",
     "select.py", '''
from sklearn.feature_selection import RFE, SelectFromModel, SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from data import encoder, load


def main():
    df, y = load(); cv = StratifiedKFold(5, shuffle=True, random_state=0); lr = lambda: LogisticRegression(max_iter=3000, C=0.5)
    variants = {"all features": [], "filter ANOVA k=20": [SelectKBest(f_classif, k=20)], "RFE 20": [RFE(lr(), n_features_to_select=20, step=3)],
                "L1 (C=0.1)": [SelectFromModel(LogisticRegression(penalty="l1", solver="liblinear", C=0.1))]}
    for name, sel in variants.items():
        s = cross_val_score(make_pipeline(encoder(df), *sel, lr()), df, y, cv=cv, scoring="roc_auc"); print(f"  {name:18s} AUC {s.mean():.3f} ± {s.std():.3f}")
    pipe = make_pipeline(encoder(df), SelectFromModel(LogisticRegression(penalty="l1", solver="liblinear", C=0.1)), lr()).fit(df, y)
    names = pipe[0].get_feature_names_out()[pipe[1].get_support()]; print(f"L1 keeps {len(names)} of {len(pipe[1].get_support())} encoded features, e.g.", [n.split("__")[1] for n in names[:6]])


if __name__ == "__main__":
    main()
'''),
   S("The scorecard: calibration, cost threshold, AUC as an integral, reason codes", """The final model is a calibrated logistic regression (transparent and stable). The threshold minimises **expected cost** on out-of-fold predictions; ROC-AUC is computed by trapezoid integration of the ROC curve and cross-checked with the pairwise-probability definition. Each decision gets **reason codes** — the features pushing the score up most.""",
     "scorecard.py", '''
import joblib, numpy as np, pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline
from data import COST_FN, COST_FP, encoder, expected_cost, load


def auc_trapezoid(y, s):
    fpr, tpr, _ = roc_curve(y, s); return float(np.sum((fpr[1:] - fpr[:-1]) * (tpr[1:] + tpr[:-1]) / 2))


def reason_codes(pipe, row, top=3):
    enc, lr = pipe[0], pipe[-1]; x = enc.transform(row)[0]; contrib = x * lr.coef_[0]; names = enc.get_feature_names_out()
    return [names[i].split("__")[1] for i in np.argsort(-contrib)[:top] if contrib[i] > 0]


def main():
    df, y = load(); Xtr, Xte, ytr, yte = train_test_split(df, y, test_size=0.25, stratify=y, random_state=0)
    base = make_pipeline(encoder(df), LogisticRegression(max_iter=3000, C=0.5))
    oof = cross_val_predict(CalibratedClassifierCV(base, cv=5), Xtr, ytr, cv=5, method="predict_proba")[:, 1]
    grid = np.linspace(0.05, 0.9, 86); costs = [expected_cost(ytr, oof > t) for t in grid]; t_best = float(grid[int(np.argmin(costs))])
    print(f"threshold by expected cost: {t_best:.2f} (theory for calibrated scores: {COST_FP / (COST_FP + COST_FN):.2f})")
    model = CalibratedClassifierCV(base, cv=5).fit(Xtr, ytr); p = model.predict_proba(Xte)[:, 1]
    pos, neg = p[yte.to_numpy() == 1], p[yte.to_numpy() == 0]; pairwise = float((pos[:, None] > neg[None]).mean() + 0.5 * (pos[:, None] == neg[None]).mean())
    print(f"test AUC trapezoid {auc_trapezoid(yte, p):.4f} | pairwise {pairwise:.4f} | sklearn {roc_auc_score(yte, p):.4f}")
    for name, flag in [("approve everyone", np.zeros(len(yte))), ("threshold 0.5", p > 0.5), (f"cost threshold {t_best:.2f}", p > t_best)]:
        print(f"  {name:22s} expected cost per applicant {expected_cost(yte, flag):.3f} | rejected {np.mean(flag):.0%}")
    explain = base.fit(Xtr, ytr)
    for i in np.argsort(-p)[:3]: print(f"  applicant {Xte.index[i]}: P(bad) {p[i]:.2f} -> reasons {reason_codes(explain, Xte.iloc[[i]])}")
    joblib.dump({"model": model, "explainer": explain, "threshold": t_best}, "scorecard.joblib"); print("saved scorecard.joblib")


if __name__ == "__main__":
    main()
'''),
   S("System design document", """Write the design before building the service: requirements, data flow, model, serving, capacity, monitoring and governance. Interviewers and reviewers look for exactly these sections.""",
     "DESIGN.md", """
# Credit pre-screening — system design

## 1. Requirements
- Decision: route each new loan application to *auto-approve*, *manual review* or *decline-with-review*. Humans make every final rejection.
- Volume: ~20,000 applications/day, peak 5/s; latency budget 200 ms (form submission).
- Constraints: explainable reason codes; fairness audit by age and sex; data retention per DPDP Act; RBI model-risk guidance.

## 2. ML framing
- Target: 'bad' = 90+ days past due within 12 months (label arrives 12 months later → monitor proxies early).
- Offline metric: AUC + expected cost with the 5:1 cost matrix; online: default rate and approval rate by segment.

## 3. Data & features
- Application form + bureau pull. One feature function shared by training and serving (no skew); point-in-time correct joins.

## 4. Model
- Calibrated logistic regression (scorecard) as champion; gradient boosting challenger in shadow mode.

## 5. Serving
- FastAPI service, model loaded once; p95 latency < 30 ms on 1 vCPU → 2 replicas cover peak with headroom.
- Every decision logged with model version, inputs (minimised), score, threshold and reason codes.

## 6. Monitoring
- Daily PSI on inputs and scores; weekly approval-rate and fairness dashboards; quarterly backtest when labels mature.
- Retrain trigger: PSI > 0.25 on key features or AUC drop > 0.03 on matured cohorts.

## 7. Rollout
- Shadow → 10% canary for 4 weeks → A/B on approval quality; rollback by switching the model alias.
""", "markdown"),
   S("Tests", "", "tests/test_scorecard.py", '''
import numpy as np
from data import encoder, expected_cost, load
from scorecard import auc_trapezoid
from sklearn.metrics import roc_auc_score
from zoo import OneRule


def test_data_and_costs():
    df, y = load(); assert len(df) == 1000 and set(y.unique()) == {0, 1}
    assert expected_cost([1, 0], [0, 0]) == 2.5 and expected_cost([1, 0], [1, 1]) == 0.5


def test_encoder_output_is_numeric():
    df, y = load(); Z = encoder(df).fit_transform(df, y); assert np.isfinite(Z).all()


def test_auc_by_integration_matches_sklearn():
    rng = np.random.default_rng(0); y = rng.integers(0, 2, 300); s = y * 0.5 + rng.random(300); assert abs(auc_trapezoid(y, s) - roc_auc_score(y, s)) < 1e-9


def test_one_rule_beats_majority():
    df, y = load(); r = OneRule().fit(df, y); assert (r.predict(df) == y).mean() > 1 - y.mean()
'''),
   S("Run it", "", None, "python zoo.py\npython select.py\npython scorecard.py\npytest -q", "bash"),
  ],
  check=["python zoo.py", "python select.py", "python scorecard.py", "pytest -q"],
  talk=["Why the threshold comes from the cost matrix, not 0.5.", "Which models won and why ensembles help less on 1,000 rows than on 100,000.", "How reason codes are computed and why regulators require them.",
        "Walk through DESIGN.md: latency, monitoring with delayed labels, rollout."],
  errors=[("Stacking is slow", "SVM with probability=True runs internal CV — reduce repeats or use LinearSVC + calibration"), ("TargetEncoder leaks", "it must be inside the pipeline (it cross-fits automatically)")],
  extend=["Add a FastAPI endpoint that returns score + reason codes", "Add the fairness audit from the Responsible AI concept", "Replace the stacker's base models with gradient boosting and compare"],
  see=["m-encoding", "m-intuitive-algos", "m-knn", "m-decision-tree", "m-bootstrap-bagging", "m-adaboost", "m-svm", "m-kernels", "m-separability", "m-voting-stacking", "m-feature-selection",
       "m-integration", "m-industry-cases", "m-ml-system-design", "m-metrics-clf",
       "m-linear-classification", "m-naive-bayes", "m-discriminant-analysis", "m-threshold-calibration", "m-choosing-classifier"])

# ---------------------------------------------------------------- P24
P24 = P("p-face-explorer", "Face explorer: EigenFaces, Fisherfaces, manifolds and outlier detection (Olivetti faces)", "unsup", "Intermediate", "2–3 days", "VS Code or Colab (CPU)",
  "Treat 400 face photos as 4,096-dimensional vectors and explore them with unsupervised tools: image basics and HOG features, the curse of dimensionality, EigenFaces (PCA) and Fisherfaces (LDA) for recognition, t-SNE/Isomap maps of the face space, and anomaly detection that flags non-face images by reconstruction error.",
  ["`faces.py`: load Olivetti faces, image statistics, HOG features", "`dimensions.py`: distance concentration and kNN accuracy vs dimension", "`recognise.py`: EigenFaces vs Fisherfaces vs HOG — accuracy and components",
   "`maps.py`: PCA / Isomap / t-SNE embeddings with trustworthiness", "`outliers.py`: reconstruction-error anomaly detector tested on non-face photos", "`tests/`"],
  ["images as arrays", "HOG features", "curse of dimensionality", "PCA / EigenFaces", "LDA / Fisherfaces", "t-SNE, Isomap", "anomaly detection", "unsupervised workflow"],
  "Olivetti faces (AT&T Laboratories Cambridge: 40 people × 10 photos, 64×64 grey) via scikit-learn's downloader; non-face photos from scikit-image.",
  ["load + inspect", "features", "dimension study", "recognition", "manifold maps", "outlier detection"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\nscikit-learn>=1.4\nscikit-image>=0.22\nmatplotlib>=3.8\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Load faces, image statistics, HOG", "", "faces.py", '''
import numpy as np
from skimage.feature import hog
from sklearn.datasets import fetch_olivetti_faces
from sklearn.model_selection import train_test_split


def load():
    f = fetch_olivetti_faces(); return f.images, f.data, f.target          # (400, 64, 64), (400, 4096), (400,)


def split(X, y):
    return train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)


def hog_features(images):
    return np.array([hog(im, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2)) for im in images])


if __name__ == "__main__":
    imgs, X, y = load()
    print(f"{len(imgs)} images of {len(np.unique(y))} people | shape {imgs.shape[1:]} | pixel range {X.min():.2f}..{X.max():.2f} | mean brightness {X.mean():.3f}")
    print("per-person brightness spread (std of means):", round(float(np.std([X[y == p].mean() for p in np.unique(y)])), 4))
    print("HOG vector length:", hog_features(imgs[:1]).shape[1], "vs", X.shape[1], "pixels")
'''),
   S("Curse of dimensionality", "", "dimensions.py", '''
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from faces import load, split


def contrast(X):
    d = np.linalg.norm(X[1:] - X[0], axis=1); return float((d.max() - d.min()) / d.min())


if __name__ == "__main__":
    _, X, y = load(); Xtr, Xte, ytr, yte = split(X, y); rng = np.random.default_rng(0)
    for dim in [2, 20, 200, 4096]: print(f"uniform random data, dim {dim:4d}: (max-min)/min distance {contrast(rng.random((300, dim))):.2f}")
    print(f"real faces (4096 dims): {contrast(X):.2f}  <- far from uniform: faces live on a low-dimensional manifold")
    for k in [5, 20, 50, 150, 299]:
        acc = KNeighborsClassifier(1).fit(PCA(k, random_state=0).fit(Xtr).transform(Xtr), ytr).score(PCA(k, random_state=0).fit(Xtr).transform(Xte), yte)
        print(f"  1-NN on {k:3d} PCA dims: accuracy {acc:.3f}")
'''),
   S("Recognition: EigenFaces vs Fisherfaces vs HOG", """EigenFaces = PCA (unsupervised, maximises variance); Fisherfaces = PCA then LDA (supervised, maximises class separation — more robust to lighting). Both feed a simple classifier.""",
     "recognise.py", '''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from faces import hog_features, load, split


def pipelines(n_train):
    return {"raw pixels + 1-NN": make_pipeline(KNeighborsClassifier(1)), "EigenFaces (PCA 60, whitened) + SVM": make_pipeline(PCA(60, whiten=True, random_state=0), SVC(C=10)),
            "Fisherfaces (PCA + LDA) + 1-NN": make_pipeline(PCA(n_train - 40, random_state=0), LinearDiscriminantAnalysis(), KNeighborsClassifier(1))}


def main():
    imgs, X, y = load(); Xtr, Xte, ytr, yte = split(X, y); scores = {}
    for name, pipe in pipelines(len(Xtr)).items(): scores[name] = pipe.fit(Xtr, ytr).score(Xte, yte); print(f"  {name:38s} accuracy {scores[name]:.3f}")
    H = hog_features(imgs); Htr, Hte, _, _ = split(H, y); scores["HOG + SVM"] = SVC(kernel="linear").fit(Htr, ytr).score(Hte, yte); print(f"  {'HOG + linear SVM':38s} accuracy {scores['HOG + SVM']:.3f}")
    pca = PCA(16).fit(Xtr); fig, ax = plt.subplots(2, 8, figsize=(12, 3.5))
    for i, a in enumerate(ax.flat): a.imshow((Xtr.mean(0) if i == 0 else pca.components_[i - 1]).reshape(64, 64), cmap="gray"); a.axis("off")
    fig.savefig("eigenfaces.png", dpi=90); print("variance in 16 eigenfaces:", round(float(pca.explained_variance_ratio_.sum()), 3), "| saved eigenfaces.png")
    return scores


if __name__ == "__main__":
    main()
'''),
   S("Maps of face space", "", "maps.py", '''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, Isomap, trustworthiness
from faces import load

if __name__ == "__main__":
    _, X, y = load(); Z = PCA(50, random_state=0).fit_transform(X); maps = {"PCA": Z[:, :2], "Isomap": Isomap(n_neighbors=8).fit_transform(Z), "t-SNE": TSNE(perplexity=15, random_state=0).fit_transform(Z)}
    fig, ax = plt.subplots(1, 3, figsize=(13, 4))
    for a, (name, E) in zip(ax, maps.items()):
        print(f"  {name:6s} trustworthiness {trustworthiness(Z, E, n_neighbors=5):.3f}"); a.scatter(E[:, 0], E[:, 1], c=y, cmap="tab20", s=10); a.set_title(name)
    fig.savefig("face_maps.png", dpi=90); print("saved face_maps.png — each colour is one person")
'''),
   S("Outlier detection by reconstruction error", """Fit PCA on faces only. A real face is rebuilt well from 50 eigenfaces; a non-face (a cat, coffee, a rocket) is not. The threshold is the 99th percentile of errors on held-out *calibration* faces (training faces reconstruct too well and would give a threshold that's too strict).""",
     "outliers.py", '''
import numpy as np
from skimage import color, data, transform
from sklearn.decomposition import PCA
from faces import load, split


def to_face_format(img):
    g = color.rgb2gray(img) if img.ndim == 3 else img / 255.0; return transform.resize(g, (64, 64), anti_aliasing=True).ravel()


def detector(Xtr, k=50):
    fit_part, calib = Xtr[: int(0.8 * len(Xtr))], Xtr[int(0.8 * len(Xtr)):]          # threshold from faces the PCA has NOT seen
    pca = PCA(k, random_state=0).fit(fit_part); err = lambda A: ((A - pca.inverse_transform(pca.transform(A))) ** 2).mean(1)
    return err, float(np.percentile(err(calib), 99))


if __name__ == "__main__":
    _, X, y = load(); Xtr, Xte, _, _ = split(X, y); err, thr = detector(Xtr)
    others = {name: to_face_format(getattr(data, name)()) for name in ["chelsea", "coffee", "rocket", "camera", "astronaut"]}
    print(f"threshold {thr:.4f} | held-out faces flagged: {(err(Xte) > thr).mean():.1%}")
    for name, v in others.items(): e = float(err(v[None])[0]); print(f"  {name:10s} error {e:.4f} -> {'ANOMALY' if e > thr else 'looks like a face'}")
'''),
   S("Tests", "", "tests/test_faces.py", '''
import numpy as np
from faces import hog_features, load, split
from outliers import detector


def test_shapes():
    imgs, X, y = load(); assert imgs.shape == (400, 64, 64) and X.shape == (400, 4096) and len(np.unique(y)) == 40


def test_hog_is_compact():
    imgs, _, _ = load(); assert hog_features(imgs[:2]).shape[1] < 4096


def test_detector_flags_few_faces():
    _, X, y = load(); Xtr, Xte, _, _ = split(X, y); err, thr = detector(Xtr); assert (err(Xte) > thr).mean() < 0.3
'''),
   S("Run it", "", None, "python faces.py\npython dimensions.py\npython recognise.py\npython maps.py\npython outliers.py\npytest -q", "bash"),
  ],
  check=["python faces.py", "python dimensions.py", "python recognise.py", "python maps.py", "python outliers.py", "pytest -q"], verify="smoke",
  talk=["Why 1-NN on raw pixels works poorly and PCA/LDA help.", "EigenFaces vs Fisherfaces: unsupervised variance vs supervised separation.", "What t-SNE distances do and don't mean.", "How the reconstruction-error detector picks its threshold."],
  errors=[("URLError downloading Olivetti", "your network blocks figshare — run in Colab or download olivetti_faces once and set data_home"), ("LDA warning: variables are collinear", "reduce with PCA first (that's why Fisherfaces uses PCA → LDA)")],
  extend=["Try LFW (fetch_lfw_people) — harder, more realistic", "Add a Siamese network (see the Siamese concept) and compare", "Detect faces in your own photos with OpenCV, then recognise them"],
  see=["m-image-basics", "m-image-features", "m-curse-dim", "m-eigenfaces", "m-lda", "m-manifold", "m-feature-extraction", "m-anomaly", "m-unsup-overview", "m-pca"])

# ---------------------------------------------------------------- P25
P25 = P("p-text-analytics", "Text analytics pipeline: scraping, preprocessing, embeddings, topics, n-gram LM and news classification", "nlp", "Intermediate", "3–4 days", "VS Code or Colab (CPU)",
  "A complete classical NLP toolkit on real text: a polite scraper (tested offline on saved HTML), configurable preprocessing, spaCy linguistic analysis, Word2Vec embeddings, LDA/NMF topic models on Reuters news, a multiclass Reuters topic classifier, and a smoothed n-gram language model with perplexity — each as a module with tests.",
  ["`scrape.py`: robots-aware fetcher with retries + BeautifulSoup parser (unit-tested on a saved page)", "`preprocess.py`: normalise, placeholders, stop-words, stemming/lemmatisation", "`linguistics.py`: spaCy POS/NER/dependencies on news",
   "`embeddings.py`: Word2Vec on SMS + news; neighbours and analogies", "`topics.py`: LDA vs NMF with coherence", "`classify.py`: multiclass Reuters classifier (macro-F1, confusion)", "`ngram.py`: add-k smoothed n-gram LM with perplexity", "`tests/`"],
  ["HTML parsing, politeness", "tokenisation, stemming, lemmatisation", "POS, NER, dependency parsing", "Word2Vec", "LDA/NMF", "multiclass metrics", "n-gram language models, perplexity"],
  "Reuters-21578 news (via NLTK) and the SMS Spam Collection; a saved HTML page for scraper tests.",
  ["scraper", "preprocessing", "linguistic analysis", "embeddings", "topics", "classification", "language model"],
  [
   S("Dependencies", "", "requirements.txt", "pandas>=2.0\nnumpy>=1.26\nscikit-learn>=1.4\nnltk>=3.8\nspacy>=3.7\ngensim>=4.3\nbeautifulsoup4>=4.12\nrequests>=2.31\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Setup (once)", "", "setup.sh", "pip install -r requirements.txt\npython -m spacy download en_core_web_sm\npython -c \"import nltk; [nltk.download(p) for p in ['reuters', 'stopwords', 'wordnet', 'omw-1.4', 'punkt_tab']]\"", "bash"),
   S("Corpora", "", "corpora.py", f'''
from pathlib import Path
import nltk, pandas as pd

SMS_URL = "{SMS}"


def reuters(min_docs=100):
    for pkg in ["reuters", "stopwords", "wordnet", "omw-1.4"]: nltk.download(pkg, quiet=True)
    from nltk.corpus import reuters as R
    ids = [f for f in R.fileids() if len(R.categories(f)) == 1]; df = pd.DataFrame({{"id": ids, "text": [R.raw(f) for f in ids], "topic": [R.categories(f)[0] for f in ids]}})
    keep = df.topic.value_counts()[lambda s: s >= min_docs].index; df = df[df.topic.isin(keep)]
    df["split"] = ["test" if i.startswith("test") else "train" for i in df.id]; return df.reset_index(drop=True)


def sms():
    p = Path("data/sms.tsv"); p.parent.mkdir(exist_ok=True)
    if not p.exists(): pd.read_csv(SMS_URL, sep="\\t", names=["label", "text"]).to_csv(p, sep="\\t", index=False)
    return pd.read_csv(p, sep="\\t")
'''),
   S("A polite scraper", """`fetch` respects robots.txt, identifies itself, retries with backoff and caches pages; `parse_books` turns HTML into records. The parser is unit-tested on a saved HTML snippet, so tests never touch the network.""",
     "scrape.py", '''
import hashlib, os, time, urllib.robotparser
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

UA = "text-analytics-course/1.0 (learning project)"
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def allowed(url):
    rp = urllib.robotparser.RobotFileParser(urljoin(f"{urlparse(url).scheme}://{urlparse(url).netloc}", "/robots.txt")); rp.read(); return rp.can_fetch(UA, url)


def fetch(url, cache="cache", retries=4, delay=1.0):
    os.makedirs(cache, exist_ok=True); path = os.path.join(cache, hashlib.md5(url.encode()).hexdigest() + ".html")
    if os.path.exists(path): return open(path, encoding="utf-8").read()
    for attempt in range(retries):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=15); r.raise_for_status(); r.encoding = "utf-8"
            open(path, "w", encoding="utf-8").write(r.text); time.sleep(delay); return r.text
        except requests.RequestException:
            time.sleep(2 ** attempt)
    raise RuntimeError(url)


def parse_books(html, base="https://books.toscrape.com/catalogue/"):
    soup = BeautifulSoup(html, "html.parser"); rows = []
    for card in soup.select("article.product_pod"):
        rows.append({"title": card.h3.a["title"], "price": float(card.select_one("p.price_color").text.strip().lstrip("£Â")),
                     "rating": RATING[card.select_one("p.star-rating")["class"][1]], "url": urljoin(base, card.h3.a["href"])})
    nxt = soup.select_one("li.next a"); return rows, (urljoin(base, nxt["href"]) if nxt else None)


def crawl(start="https://books.toscrape.com/catalogue/page-1.html", pages=3):
    if not allowed(start): raise PermissionError("robots.txt disallows this URL")
    url, out = start, []
    for _ in range(pages):
        rows, url = parse_books(fetch(url)); out += rows
        if not url: break
    return out


if __name__ == "__main__":
    import sys
    if "--online" in sys.argv:
        books = crawl(); print(f"scraped {len(books)} books; first: {books[0]}")
    else:
        print("offline mode: run `python scrape.py --online` to crawl books.toscrape.com (a sandbox site for scraping practice)")
'''),
   S("Preprocessing", "", "preprocess.py", '''
import re, unicodedata
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

STOP = set(stopwords.words("english")) - {"not", "no", "nor"}; _stem, _lem = PorterStemmer(), WordNetLemmatizer()


def normalise(text: str, placeholders: bool = True) -> str:
    t = unicodedata.normalize("NFKC", text).lower()
    if placeholders:
        t = re.sub(r"https?://\\S+|www\\.\\S+", " <url> ", t); t = re.sub(r"£\\s?\\d+|\\$\\d+", " <money> ", t); t = re.sub(r"\\b\\d{5,}\\b", " <phone> ", t); t = re.sub(r"\\d+(\\.\\d+)?", " <num> ", t)
    return t


def tokens(text: str, stop=True, mode=None) -> list[str]:
    toks = re.findall(r"<\\w+>|[a-z']+", normalise(text))
    if stop: toks = [w for w in toks if w not in STOP]
    if mode == "stem": toks = [_stem.stem(w) for w in toks]
    if mode == "lemma": toks = [_lem.lemmatize(_lem.lemmatize(w, "v"), "n") for w in toks]
    return toks
'''),
   S("Linguistic analysis with spaCy", "", "linguistics.py", '''
from collections import Counter
import spacy
from corpora import reuters

if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm"); df = reuters(); docs = list(nlp.pipe(df.text.head(200), batch_size=50))
    ents = Counter((e.label_, e.text) for d in docs for e in d.ents if e.label_ in ("ORG", "GPE"))
    print("most mentioned organisations/places:", [t for (_, t), _ in ents.most_common(8)])
    print("POS mix:", Counter(t.pos_ for d in docs for t in d).most_common(6))
    svo = Counter((t.lemma_, t.head.lemma_) for d in docs for t in d if t.dep_ == "nsubj" and t.head.pos_ == "VERB"); print("frequent subject-verb pairs:", svo.most_common(6))
'''),
   S("Word embeddings", "", "embeddings.py", '''
from gensim.models import Word2Vec
from corpora import reuters, sms
from preprocess import tokens

if __name__ == "__main__":
    sents = [tokens(t, stop=False) for t in list(reuters().text) + list(sms().text)]
    w2v = Word2Vec(sents, vector_size=100, window=5, min_count=5, sg=1, epochs=10, workers=4, seed=0)
    for w in ["oil", "profit", "bank", "free"]: print(f"  near {w!r}:", [x for x, _ in w2v.wv.most_similar(w, topn=6)])
    print("  crude - oil + gold ->", [x for x, _ in w2v.wv.most_similar(positive=["crude", "gold"], negative=["oil"], topn=4)])
    w2v.save("data/w2v.model")
'''),
   S("Topic models", "", "topics.py", '''
import numpy as np
from collections import Counter
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from corpora import reuters

PAT = r"(?u)\\b[a-z]{3,}\\b"


def umass(components, B, top=10):
    Dw = np.asarray(B.sum(0)).ravel(); out = []
    for t in components:
        w = np.argsort(-t)[:top]; co = (B[:, w].T @ B[:, w]).toarray(); out.append(np.mean([np.log((co[i, j] + 1) / Dw[w[j]]) for i in range(1, top) for j in range(i)]))
    return float(np.mean(out))


if __name__ == "__main__":
    df = reuters(); cv = CountVectorizer(stop_words="english", max_df=0.3, min_df=5, token_pattern=PAT); C = cv.fit_transform(df.text); B = (C > 0).astype(np.float32).tocsc()
    tf = TfidfVectorizer(stop_words="english", max_df=0.3, min_df=5, token_pattern=PAT); T = tf.fit_transform(df.text)
    for k in [6, 10]:
        lda = LatentDirichletAllocation(k, learning_method="online", random_state=0).fit(C); nmf = NMF(k, init="nndsvd", random_state=0).fit(T)
        print(f"k={k}: coherence LDA {umass(lda.components_, B):.3f} | NMF {umass(nmf.components_, B):.3f}")
    names = tf.get_feature_names_out(); W = nmf.transform(T)
    for i, t in enumerate(nmf.components_): print(f"  topic {i}: {' '.join(names[np.argsort(-t)[:7]])} | main Reuters label: {Counter(df.topic[W.argmax(1) == i]).most_common(1)}")
'''),
   S("Multiclass news classifier", """Reuters topics are imbalanced (earn and acq dominate), so report **macro-F1** (every topic counts equally) next to accuracy, and look at the confusion between related topics (grain/wheat, crude/ship).""",
     "classify.py", '''
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC
from corpora import reuters


def train():
    df = reuters(); tr, te = df[df.split == "train"], df[df.split == "test"]
    pipe = make_pipeline(TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2), LinearSVC(C=0.5, class_weight="balanced")).fit(tr.text, tr.topic)
    return pipe, te


if __name__ == "__main__":
    pipe, te = train(); pred = pipe.predict(te.text)
    print(f"accuracy {(pred == te.topic).mean():.3f} | macro-F1 {f1_score(te.topic, pred, average='macro'):.3f} | weighted-F1 {f1_score(te.topic, pred, average='weighted'):.3f}")
    print(classification_report(te.topic, pred, digits=3, zero_division=0))
    labels = sorted(te.topic.unique()); cm = confusion_matrix(te.topic, pred, labels=labels); np.fill_diagonal(cm, 0)
    i, j = np.unravel_index(cm.argmax(), cm.shape); print(f"most common confusion: {labels[i]} -> {labels[j]} ({cm[i, j]} articles)")
'''),
   S("n-gram language model", "", "ngram.py", '''
import math
from collections import Counter, defaultdict
from corpora import reuters
from preprocess import tokens


class NGramLM:
    def __init__(self, n=2, k=0.1):
        self.n, self.k = n, k

    def fit(self, docs):
        self.counts, self.vocab = defaultdict(Counter), set()
        for d in docs:
            seq = ["<s>"] * (self.n - 1) + d + ["</s>"]; self.vocab.update(seq)
            for i in range(self.n - 1, len(seq)): self.counts[tuple(seq[i - self.n + 1:i])][seq[i]] += 1
        return self

    def prob(self, ctx, w):
        c = self.counts.get(tuple(ctx), Counter()); return (c[w] + self.k) / (sum(c.values()) + self.k * len(self.vocab))

    def perplexity(self, docs):
        lp, n = 0.0, 0
        for d in docs:
            seq = ["<s>"] * (self.n - 1) + d + ["</s>"]
            for i in range(self.n - 1, len(seq)): lp += math.log(self.prob(seq[i - self.n + 1:i], seq[i] if seq[i] in self.vocab else "<unk>")); n += 1
        return math.exp(-lp / n)


if __name__ == "__main__":
    df = reuters(); tr = [tokens(t, stop=False) for t in df[df.split == "train"].text]; te = [tokens(t, stop=False) for t in df[df.split == "test"].text]
    for n in [1, 2, 3]: print(f"  {n}-gram (add-0.1) test perplexity {NGramLM(n).fit(tr).perplexity(te[:300]):8.1f}")
'''),
   S("Tests (offline)", "", "tests/test_text.py", '''
from ngram import NGramLM
from preprocess import tokens
from scrape import parse_books

HTML = """<html><body><ol><li><article class="product_pod"><h3><a href="a-light_1/index.html" title="A Light in the Attic">A Light</a></h3>
<p class="star-rating Three"></p><div class="product_price"><p class="price_color">£51.77</p></div></article></li></ol>
<ul class="pager"><li class="next"><a href="page-2.html">next</a></li></ul></body></html>"""


def test_parser_on_saved_page():
    rows, nxt = parse_books(HTML)
    assert rows == [{"title": "A Light in the Attic", "price": 51.77, "rating": 3, "url": "https://books.toscrape.com/catalogue/a-light_1/index.html"}] and nxt.endswith("page-2.html")


def test_preprocessing_keeps_negation_and_placeholders():
    t = tokens("I'm NOT paying £500, call 09061701461!", stop=True); assert "not" in t and "<money>" in t and "<phone>" in t


def test_ngram_probabilities_sum_to_one():
    lm = NGramLM(2).fit([["a", "b", "a"], ["b", "a"]]); total = sum(lm.prob(["a"], w) for w in lm.vocab); assert abs(total - 1) < 1e-9
'''),
   S("Run it", "", None, "bash setup.sh\npython scrape.py --online\npython linguistics.py\npython embeddings.py\npython topics.py\npython classify.py\npython ngram.py\npytest -q", "bash"),
  ],
  check=["python scrape.py", "python linguistics.py", "python embeddings.py", "python topics.py", "python classify.py", "python ngram.py", "pytest -q"],
  talk=["How your scraper stays polite and how you test parsing without the network.", "Why macro-F1 for Reuters and what the confusions tell you.", "Perplexity: what it measures and why the trigram isn't always better with little data."],
  errors=[("LookupError: Resource reuters not found", "run setup.sh (nltk.download)"), ("OSError: [E050] Can't find model 'en_core_web_sm'", "python -m spacy download en_core_web_sm")],
  extend=["Replace TF-IDF with sentence embeddings and compare", "Add BERTopic", "Scrape a news site you're allowed to and classify new articles"],
  see=["m-web-scraping", "m-text-preprocessing", "m-nlp-tasks", "m-word-embeddings", "m-topic-models", "m-multiclass", "m-language-models", "m-text-representation"])

# ---------------------------------------------------------------- P26
P26 = P("p-mini-gpt", "Build a GPT from scratch: BPE tokenizer, transformer, training and decoding (Tiny Shakespeare)", "nlp", "Advanced", "3–5 days", "Colab (GPU recommended) or a CPU with patience",
  "Write every piece of a small GPT yourself: a byte-pair-encoding tokenizer, scaled dot-product attention with a causal mask, multi-head attention, pre-norm transformer blocks with residuals and GELU MLPs, training with AdamW + warm-up/cosine schedule, checkpoints, perplexity, and five decoding strategies (greedy, temperature, top-k, top-p, beam) with a KV cache.",
  ["`bpe.py`: train/encode/decode a BPE tokenizer", "`model.py`: attention → block → GPT (with KV cache)", "`train.py`: data loader, AdamW, schedule, eval, checkpoint (`--steps`, `--smoke`)",
   "`generate.py`: greedy / temperature / top-k / top-p / beam", "`tests/`: causal mask, tokenizer round-trip, cache equivalence"],
  ["BPE tokenisation", "self-attention and masking", "multi-head attention", "transformer blocks", "LayerNorm, residuals, init", "learning-rate schedules", "perplexity", "decoding strategies", "KV cache"],
  "Tiny Shakespeare (1.1M characters) from Andrej Karpathy's char-rnn repository.",
  ["tokenizer", "model", "training loop", "evaluation", "decoding", "tests"],
  [
   S("Dependencies", "", "requirements.txt", "torch>=2.2\nnumpy>=1.26\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("BPE tokenizer", """Start from bytes (so any text encodes), repeatedly merge the most frequent adjacent pair. Training on the first 200k characters with 300 merges gives a 556-token vocabulary that compresses Shakespeare ~1.8×.""",
     "bpe.py", '''
from collections import Counter


class BPE:
    def __init__(self, merges: int = 300):
        self.n_merges = merges

    def fit(self, text: str):
        ids = list(text.encode("utf-8")); self.merges = {}
        for k in range(self.n_merges):
            pairs = Counter(zip(ids, ids[1:]))
            if not pairs: break
            pair = max(pairs, key=pairs.get); new = 256 + k; self.merges[pair] = new; ids = self._merge(ids, pair, new)
        self.vocab = {i: bytes([i]) for i in range(256)}
        for (a, b), new in self.merges.items(): self.vocab[new] = self.vocab[a] + self.vocab[b]
        return self

    @staticmethod
    def _merge(ids, pair, new):
        out, i = [], 0
        while i < len(ids):
            if i < len(ids) - 1 and (ids[i], ids[i + 1]) == pair: out.append(new); i += 2
            else: out.append(ids[i]); i += 1
        return out

    def encode(self, text: str) -> list[int]:
        ids = list(text.encode("utf-8"))
        while len(ids) > 1:
            pairs = set(zip(ids, ids[1:])); pair = min(pairs, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges: break
            ids = self._merge(ids, pair, self.merges[pair])
        return ids

    def decode(self, ids) -> str:
        return b"".join(self.vocab[i] for i in ids).decode("utf-8", errors="replace")

    @property
    def size(self) -> int:
        return 256 + len(self.merges)
'''),
   S("The model", """Attention(Q, K, V) = softmax(QKᵀ/√d)V with a causal mask; heads run in parallel; each block is x + attn(LN(x)) then x + MLP(LN(x)). Weights get a small normal init and the output projection of each residual branch is scaled by 1/√(2·layers) (GPT-2 trick) so the residual stream doesn't blow up. The optional `cache` stores K and V for fast generation.""",
     "model.py", '''
import math, torch, torch.nn as nn


class CausalSelfAttention(nn.Module):
    def __init__(self, d, heads, dropout=0.1):
        super().__init__(); assert d % heads == 0; self.h = heads; self.qkv = nn.Linear(d, 3 * d); self.proj = nn.Linear(d, d); self.drop = nn.Dropout(dropout)

    def forward(self, x, cache=None):
        B, T, D = x.shape; q, k, v = self.qkv(x).view(B, T, 3, self.h, D // self.h).permute(2, 0, 3, 1, 4)
        if cache is not None:
            if "k" in cache: k, v = torch.cat([cache["k"], k], 2), torch.cat([cache["v"], v], 2)
            cache["k"], cache["v"] = k, v
        S = q @ k.transpose(-2, -1) / math.sqrt(k.shape[-1])
        if T > 1:                                               # causal mask: position i may only attend to positions <= i
            S = S.masked_fill(torch.ones(T, k.shape[2], dtype=torch.bool, device=x.device).triu(k.shape[2] - T + 1), float("-inf"))
        y = self.drop(torch.softmax(S, -1)) @ v; return self.proj(y.transpose(1, 2).reshape(B, T, D))


class Block(nn.Module):
    def __init__(self, d, heads, dropout=0.1):
        super().__init__(); self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d); self.attn = CausalSelfAttention(d, heads, dropout)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d), nn.Dropout(dropout))

    def forward(self, x, cache=None):
        x = x + self.attn(self.ln1(x), cache); return x + self.mlp(self.ln2(x))


class GPT(nn.Module):
    def __init__(self, vocab, d=192, heads=6, layers=4, ctx=256, dropout=0.1):
        super().__init__(); self.ctx = ctx; self.tok, self.pos = nn.Embedding(vocab, d), nn.Embedding(ctx, d)
        self.blocks = nn.ModuleList(Block(d, heads, dropout) for _ in range(layers)); self.ln = nn.LayerNorm(d); self.head = nn.Linear(d, vocab, bias=False)
        self.head.weight = self.tok.weight                                         # weight tying
        self.apply(self._init)
        for b in self.blocks: nn.init.normal_(b.attn.proj.weight, 0, 0.02 / math.sqrt(2 * layers)); nn.init.normal_(b.mlp[2].weight, 0, 0.02 / math.sqrt(2 * layers))

    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)): nn.init.normal_(m.weight, 0, 0.02)
        if isinstance(m, nn.Linear) and m.bias is not None: nn.init.zeros_(m.bias)

    def forward(self, idx, caches=None, start=0):
        x = self.tok(idx) + self.pos(torch.arange(start, start + idx.shape[1], device=idx.device))
        for i, b in enumerate(self.blocks): x = b(x, None if caches is None else caches[i])
        return self.head(self.ln(x))
'''),
   S("Training", """AdamW with weight decay on matrices only, linear warm-up then cosine decay, gradient clipping, periodic validation perplexity and a checkpoint with the tokenizer merges. `--smoke` trains a tiny model for a few steps (used by the automated check); a GPU run of `--steps 3000` gives clearly Shakespeare-like text.""",
     "train.py", f'''
import argparse, math, os, pickle, time, urllib.request, torch
from bpe import BPE
from model import GPT

URL = "{SHAKES}"


def data(path="data/input.txt"):
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(path): urllib.request.urlretrieve(URL, path)
    return open(path, encoding="utf-8").read()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--steps", type=int, default=3000); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    torch.manual_seed(0); dev = "cuda" if torch.cuda.is_available() else "cpu"; text = data()
    cfg = dict(d=64, heads=4, layers=2, ctx=64) if a.smoke else dict(d=192, heads=6, layers=4, ctx=256); steps = 60 if a.smoke else a.steps; B = 16 if a.smoke else 32
    tok = BPE(60 if a.smoke else 300).fit(text[:50_000 if a.smoke else 200_000]); ids = torch.tensor(tok.encode(text[:300_000] if a.smoke else text)); n = int(0.9 * len(ids))
    print(f"vocab {{tok.size}} | tokens {{len(ids):,}} | compression {{len(text[:len(ids) and None]) / len(ids):.2f}} chars/token")
    model = GPT(tok.size, **cfg).to(dev); T = cfg["ctx"]; print(f"parameters {{sum(p.numel() for p in model.parameters()) / 1e6:.2f}}M on {{dev}}")
    decay = [p for p in model.parameters() if p.dim() >= 2]; no_decay = [p for p in model.parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{{"params": decay, "weight_decay": 0.1}}, {{"params": no_decay, "weight_decay": 0.0}}], lr=3e-3 if a.smoke else 1e-3, betas=(0.9, 0.95))
    warm = max(1, steps // 20); sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warm if s < warm else 0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, steps - warm))))
    def batch(split):
        d = ids[:n] if split == "train" else ids[n:]; ix = torch.randint(len(d) - T - 1, (B,)); return torch.stack([d[i:i + T] for i in ix]).to(dev), torch.stack([d[i + 1:i + T + 1] for i in ix]).to(dev)
    @torch.no_grad()
    def val_ppl(k=10):
        model.eval(); ls = [torch.nn.functional.cross_entropy(model(x).flatten(0, 1), y.flatten()).item() for x, y in (batch("val") for _ in range(k))]; model.train(); return math.exp(sum(ls) / k)
    t0 = time.time(); print(f"step 0: val perplexity {{val_ppl():.1f}}")
    for step in range(1, steps + 1):
        x, y = batch("train"); loss = torch.nn.functional.cross_entropy(model(x).flatten(0, 1), y.flatten())
        opt.zero_grad(set_to_none=True); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
        if step % max(1, steps // 5) == 0: print(f"step {{step}}: train loss {{loss.item():.3f}} | val perplexity {{val_ppl():.1f}} | lr {{sched.get_last_lr()[0]:.1e}} | {{time.time() - t0:.0f}}s")
    torch.save({{"model": model.state_dict(), "cfg": cfg, "vocab": tok.size}}, "data/gpt.pt"); pickle.dump(tok, open("data/bpe.pkl", "wb")); print("saved data/gpt.pt and data/bpe.pkl")


if __name__ == "__main__":
    main()
'''),
   S("Decoding strategies", "", "generate.py", '''
import argparse, pickle, torch
from model import GPT


def load():
    ck = torch.load("data/gpt.pt", map_location="cpu"); m = GPT(ck["vocab"], **ck["cfg"]); m.load_state_dict(ck["model"]); return m.eval(), pickle.load(open("data/bpe.pkl", "rb"))


@torch.no_grad()
def sample(model, ids, n, temperature=1.0, top_k=None, top_p=None, greedy=False, seed=0):
    g = torch.Generator().manual_seed(seed); caches = [{} for _ in model.blocks]; x = torch.tensor([ids]); logits = model(x, caches, 0)[0, -1]; out = list(ids)
    for _ in range(n):
        z = logits / temperature
        if top_k: z[z < torch.topk(z, top_k).values[-1]] = float("-inf")
        if top_p:
            s, i = torch.sort(torch.softmax(z, 0), descending=True); drop = (torch.cumsum(s, 0) - s) > top_p; z[i[drop]] = float("-inf")
        nxt = int(z.argmax()) if greedy else int(torch.multinomial(torch.softmax(z, 0), 1, generator=g)); out.append(nxt)
        if len(out) >= model.ctx: break
        logits = model(torch.tensor([[nxt]]), caches, len(out) - 1)[0, -1]
    return out


@torch.no_grad()
def beam(model, ids, n, k=4):
    beams = [(0.0, list(ids))]
    for _ in range(n):
        cand = []
        for s, seq in beams:
            lp = torch.log_softmax(model(torch.tensor([seq[-model.ctx:]]))[0, -1], 0); top = torch.topk(lp, k)
            cand += [(s + v.item(), seq + [int(i)]) for v, i in zip(top.values, top.indices)]
        beams = sorted(cand, key=lambda c: -c[0] / len(c[1]))[:k]
    return beams[0][1]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--prompt", default="ROMEO:\\n"); ap.add_argument("--n", type=int, default=120); a = ap.parse_args()
    model, tok = load(); ids = tok.encode(a.prompt); n = min(a.n, model.ctx - len(ids) - 1)
    runs = {"greedy": sample(model, ids, n, greedy=True), "temperature 0.8": sample(model, ids, n, 0.8), "top-k 20": sample(model, ids, n, top_k=20), "top-p 0.9": sample(model, ids, n, top_p=0.9), "beam 4": beam(model, ids, min(n, 40))}
    for name, out in runs.items(): print(f"--- {name}\\n{tok.decode(out)}")
'''),
   S("Tests", "", "tests/test_gpt.py", '''
import torch
from bpe import BPE
from model import GPT

TEXT = "to be or not to be, that is the question; whether tis nobler in the mind to suffer"


def test_bpe_round_trip_and_compression():
    t = BPE(30).fit(TEXT * 3); ids = t.encode(TEXT); assert t.decode(ids) == TEXT and len(ids) < len(TEXT.encode())


def test_causal_mask_blocks_the_future():
    torch.manual_seed(0); m = GPT(50, d=32, heads=4, layers=2, ctx=16, dropout=0.0).eval(); x = torch.randint(0, 50, (1, 10)); y = x.clone(); y[0, 7:] = (y[0, 7:] + 1) % 50
    assert torch.allclose(m(x)[0, :7], m(y)[0, :7], atol=1e-6)


def test_kv_cache_matches_full_forward():
    torch.manual_seed(0); m = GPT(50, d=32, heads=4, layers=2, ctx=16, dropout=0.0).eval(); x = torch.randint(0, 50, (1, 9)); full = m(x)[0, -1]
    caches = [{} for _ in m.blocks]; m(x[:, :8], caches, 0); step = m(x[:, 8:], caches, 8)[0, -1]; assert torch.allclose(full, step, atol=1e-5)
'''),
   S("Run it", "", None, "python train.py --steps 3000      # ~10 min on a Colab T4; use --smoke for a 1-minute CPU check\npython generate.py --prompt \"ROMEO:\"\npytest -q", "bash"),
  ],
  check=["python train.py --smoke", "python generate.py --n 40", "pytest -q"], verify="smoke",
  talk=["Walk through attention shapes (B, heads, T, d/h) and the causal mask.", "Why pre-norm + scaled residual init train stably.", "When you'd use greedy vs top-p vs beam search.", "What the KV cache saves and what it costs in memory."],
  errors=[("Loss stuck near log(vocab)", "learning rate too high/low or the mask is wrong — run the tests"), ("CUDA out of memory", "reduce batch size, context or d"), ("Gibberish after training", "train longer (val perplexity should fall below ~6 per BPE token)")],
  extend=["Swap learned positions for rotary embeddings (RoPE)", "Add FlashAttention via F.scaled_dot_product_attention", "Fine-tune on your own text"],
  see=["m-tokenization", "m-attention", "m-transformer", "m-decoding", "m-language-models", "m-init-norm", "m-llm-inference"])

PROJECTS_4 = [P21, P22, P23, P24, P25, P26]
