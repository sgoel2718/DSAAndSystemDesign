"""End-to-end projects 1-7: Python, statistics, maths-from-scratch, tabular ML, supervised, unsupervised, recommenders."""
from ml_proj_util import P, S

RETAIL_URL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"
GITIGNORE = """__pycache__/
.venv/
data/
*.joblib
*.pt
*.onnx
mlruns/
.ipynb_checkpoints/
.env
"""

P1 = P("p-retail-analytics", "Retail sales analytics toolkit (Python, pandas, Matplotlib)", "py", "Basic", "1–2 days", "VS Code or Colab (CPU)",
  "Turn 540,000 raw e-commerce transactions into a clean dataset, business KPIs, charts and an HTML report — packaged as a reusable Python module with a command-line tool and unit tests.",
  ["A Python package `retail` that downloads, caches and cleans the UCI Online Retail data", "KPI functions: monthly revenue, top products, countries, basket size, repeat-customer rate, cohort retention",
   "Charts with Matplotlib and an auto-generated HTML report", "A command-line interface (`python -m retail.cli`)", "pytest unit tests"],
  ["Python packages and modules", "functions, type hints, docstrings", "pandas cleaning, groupby, pivot, datetime", "Matplotlib", "argparse CLI", "pytest", "Git"],
  "UCI Online Retail (UK online gift shop, Dec 2010–Dec 2011, 541,909 rows) — downloaded automatically from a public GitHub mirror.",
  ["download + cache CSV", "clean (cancellations, missing IDs, bad prices)", "KPI functions", "charts", "HTML report", "CLI + tests"],
  [
   S("Set up the project", """Create a folder, a virtual environment and install the libraries. In Colab, skip the venv and just `pip install` (most are pre-installed). Keep code in a package folder (`retail/`) instead of one giant notebook — that makes it testable and reusable.""",
     "setup.sh", """
mkdir retail-analytics && cd retail-analytics
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
git init""", "bash"),
   S("Dependencies", "Pin major versions so the project behaves the same on every machine.", "requirements.txt", """
pandas>=2.0
numpy>=1.26
matplotlib>=3.8
pytest>=8.0""", "text"),
   S("Ignore generated files", "Never commit data, virtual environments or caches.", ".gitignore", GITIGNORE, "text"),
   S("Package marker", "An `__init__.py` makes `retail` an importable package.", "retail/__init__.py", '''
"""Retail analytics toolkit."""
__version__ = "0.1.0"
'''),
   S("Load and clean the data", """Download once and cache to `data/`. Cleaning rules come from exploring the data: invoices starting with **C** are cancellations, some rows have no customer, some prices are zero or negative. Keep the rules in one function so every analysis uses the same clean data.""",
     "retail/data.py", f'''
"""Download, cache and clean the Online Retail dataset."""
from pathlib import Path
import pandas as pd

URL = "{RETAIL_URL}"
DATA_DIR = Path("data")


def load_raw(nrows: int | None = None) -> pd.DataFrame:
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / "online_retail.csv"
    if not path.exists():
        print("downloading", URL)
        pd.read_csv(URL, dtype={{"InvoiceNo": str, "StockCode": str, "CustomerID": "Int64"}}).to_csv(path, index=False)
    return pd.read_csv(path, dtype={{"InvoiceNo": str, "StockCode": str, "CustomerID": "Int64"}}, nrows=nrows)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return completed sales with a Revenue column (cancellations and bad rows removed)."""
    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M")
    df["is_cancel"] = df["InvoiceNo"].str.startswith("C")
    df = df[~df["is_cancel"] & (df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df = df.dropna(subset=["CustomerID"]).drop_duplicates()
    df["Description"] = df["Description"].str.strip().str.upper()
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df.drop(columns="is_cancel").reset_index(drop=True)
'''),
   S("Business KPIs", """Each KPI is a small, pure function: data in, DataFrame/number out. Pure functions are easy to test and to reuse in a dashboard later. Cohort retention shows what share of customers who first bought in month *m* come back *k* months later.""",
     "retail/analysis.py", '''
"""KPI calculations on cleaned sales data."""
import pandas as pd


def monthly_revenue(df: pd.DataFrame) -> pd.Series:
    return df.groupby("Month")["Revenue"].sum().round(2)


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (df.groupby("Description").agg(revenue=("Revenue", "sum"), units=("Quantity", "sum"), orders=("InvoiceNo", "nunique"))
              .sort_values("revenue", ascending=False).head(n).round(2))


def country_summary(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    g = df.groupby("Country").agg(revenue=("Revenue", "sum"), customers=("CustomerID", "nunique"), orders=("InvoiceNo", "nunique"))
    g["revenue_per_customer"] = g["revenue"] / g["customers"]
    return g.sort_values("revenue", ascending=False).head(n).round(2)


def kpis(df: pd.DataFrame) -> dict:
    orders = df.groupby("InvoiceNo")["Revenue"].sum()
    per_customer = df.groupby("CustomerID")["InvoiceNo"].nunique()
    return {"revenue": round(float(df["Revenue"].sum()), 2), "orders": int(df["InvoiceNo"].nunique()),
            "customers": int(df["CustomerID"].nunique()), "avg_order_value": round(float(orders.mean()), 2),
            "repeat_customer_rate": round(float((per_customer > 1).mean()), 3)}


def cohort_retention(df: pd.DataFrame, months: int = 6) -> pd.DataFrame:
    d = df[["CustomerID", "InvoiceDate"]].copy()
    d["order_month"] = d["InvoiceDate"].dt.to_period("M")
    d["cohort"] = d.groupby("CustomerID")["order_month"].transform("min")
    d["age"] = (d["order_month"] - d["cohort"]).apply(lambda x: x.n)
    counts = d.groupby(["cohort", "age"])["CustomerID"].nunique().unstack(fill_value=0)
    return counts.div(counts[0], axis=0).iloc[:, :months].round(3)
'''),
   S("Charts and the HTML report", """Generate figures with Matplotlib's object-oriented API and write a self-contained HTML report (tables via `DataFrame.to_html`). Anyone can open the report in a browser — a typical deliverable for a manager.""",
     "retail/report.py", '''
"""Build charts and an HTML report."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from . import analysis


def build_report(df: pd.DataFrame, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    rev = analysis.monthly_revenue(df)
    fig, ax = plt.subplots(figsize=(9, 3.5)); rev.plot(ax=ax, marker="o", color="#2a78d6")
    ax.set(title="Monthly revenue", xlabel="", ylabel="£"); ax.grid(alpha=0.3); fig.tight_layout(); fig.savefig(out / "monthly_revenue.png", dpi=120); plt.close(fig)
    top = analysis.top_products(df)
    fig, ax = plt.subplots(figsize=(9, 4)); top["revenue"][::-1].plot.barh(ax=ax, color="#eb6834")
    ax.set(title="Top 10 products by revenue", xlabel="£"); fig.tight_layout(); fig.savefig(out / "top_products.png", dpi=120); plt.close(fig)
    k = analysis.kpis(df)
    cards = "".join(f"<div class='k'><b>{v:,}</b><span>{name.replace('_', ' ')}</span></div>" for name, v in k.items())
    html = f"""<!doctype html><meta charset="utf-8"><title>Retail report</title>
<style>body{{font-family:system-ui;max-width:960px;margin:24px auto;padding:0 16px}}.ks{{display:flex;gap:12px;flex-wrap:wrap}}
.k{{border:1px solid #ddd;border-radius:8px;padding:10px 14px}}.k b{{display:block;font-size:22px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:4px 8px}}</style>
<h1>Online retail — sales report</h1><div class="ks">{cards}</div>
<h2>Revenue trend</h2><img src="monthly_revenue.png" width="100%">
<h2>Top products</h2><img src="top_products.png" width="100%">{top.to_html()}
<h2>Countries</h2>{analysis.country_summary(df).to_html()}
<h2>Cohort retention (share of customers returning k months after first purchase)</h2>{analysis.cohort_retention(df).to_html()}"""
    path = out / "report.html"; path.write_text(html, encoding="utf-8")
    return path
'''),
   S("Command-line interface", """`argparse` turns the toolkit into a command anyone can run. `--sample` lets you develop quickly on a subset.""",
     "retail/cli.py", '''
"""python -m retail.cli --out reports/ [--sample 100000]"""
import argparse
from pathlib import Path
from . import data, analysis, report


def main(argv=None):
    ap = argparse.ArgumentParser(description="Retail sales analytics")
    ap.add_argument("--out", default="reports", help="output folder")
    ap.add_argument("--sample", type=int, default=None, help="only read the first N rows")
    args = ap.parse_args(argv)
    df = data.clean(data.load_raw(args.sample))
    print("clean rows:", len(df))
    for k, v in analysis.kpis(df).items():
        print(f"{k:22s} {v:,}")
    print("report written to", report.build_report(df, Path(args.out)))


if __name__ == "__main__":
    main()
'''),
   S("Unit tests", """Tests use a tiny hand-made DataFrame, so they run in milliseconds and catch regressions when you change the cleaning rules. Run `pytest -q`.""",
     "tests/test_analysis.py", '''
import pandas as pd
from retail import data, analysis


def sample():
    return pd.DataFrame({"InvoiceNo": ["1", "1", "C2", "3", "4"], "StockCode": ["A", "B", "A", "A", "B"],
                         "Description": [" mug", "plate", "mug", "mug ", "plate"], "Quantity": [2, 1, -2, 5, 1],
                         "InvoiceDate": ["12/1/2010 8:26", "12/1/2010 8:26", "12/2/2010 9:00", "1/5/2011 10:00", "1/6/2011 11:00"],
                         "UnitPrice": [3.0, 10.0, 3.0, 3.0, 0.0], "CustomerID": pd.array([1, 1, 1, 2, 3], dtype="Int64"), "Country": ["UK"] * 5})


def test_clean_removes_cancellations_and_bad_prices():
    df = data.clean(sample())
    assert len(df) == 3 and (df["Revenue"] > 0).all()
    assert set(df["Description"]) == {"MUG", "PLATE"}


def test_kpis():
    k = analysis.kpis(data.clean(sample()))
    assert k["revenue"] == 2 * 3 + 10 + 15 and k["customers"] == 2 and k["orders"] == 2


def test_monthly_revenue_sums_to_total():
    df = data.clean(sample())
    assert abs(analysis.monthly_revenue(df).sum() - df["Revenue"].sum()) < 1e-9
'''),
   S("Run it", "Generate the full report, open `reports/report.html`, then commit and push to GitHub.", None, """
python -m retail.cli --out reports            # full data (~1 minute the first time: download)
pytest -q
git add . && git commit -m "Retail analytics toolkit" && git push""", "bash"),
  ],
  check=["python -m retail.cli --out reports", "pytest -q", "test -f reports/report.html"],
  talk=["Explain your cleaning rules and how you validated them (cancellations, missing customer IDs, zero prices).",
        "Why a package + tests instead of a notebook: reproducibility, reuse, reviewability.", "One insight: e.g. revenue peaks in November (Christmas gifting), most revenue from the UK, repeat customers drive most sales."],
  errors=[("UnicodeDecodeError reading the CSV", "pass encoding='ISO-8859-1' (the original UCI Excel file uses it)"),
          ("ModuleNotFoundError: No module named 'retail'", "run commands from the project root (the folder that contains retail/)"),
          ("Dates parsed wrongly (day/month swapped)", "always pass an explicit format to pd.to_datetime")],
  extend=["Add a Streamlit dashboard reading the same analysis functions", "Schedule the report weekly with GitHub Actions", "Add RFM features and hand them to the segmentation project"],
  see=["m-py-functions", "m-py-libraries", "m-pandas", "m-matplotlib", "m-py-io"])

P2 = P("p-ab-testing", "A/B test analyser app (statistics + Streamlit)", "stats", "Intermediate", "1–2 days", "VS Code or Colab (CPU)",
  "Build a reusable statistics module and a Streamlit web app that tells a product team whether an experiment won: sample-size planning, z-test, confidence intervals, bootstrap and a plain-English verdict.",
  ["`abtest.py`: sample-size calculator, two-proportion z-test, Welch t-test, bootstrap confidence intervals, sequential-peeking simulation",
   "`simulate.py`: generates realistic experiment logs (users, variant, converted, revenue)", "`app.py`: Streamlit app — upload a CSV or use the simulated one, see results and charts",
   "Tests that check the maths against SciPy/statsmodels"],
  ["hypothesis testing", "p-values and confidence intervals", "power and sample size", "bootstrap", "Type I error from peeking", "Streamlit"],
  "Simulated experiment logs (so you know the true effect and can check the maths), or any CSV with columns variant, converted[, revenue].",
  ["experiment design (sample size)", "collect/simulate logs", "test + intervals", "bootstrap revenue lift", "verdict + charts in Streamlit"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\npandas>=2.0\nscipy>=1.11\nstatsmodels>=0.14\nstreamlit>=1.30\nmatplotlib>=3.8\npytest>=8.0", "text"),
   S("The statistics module", """All maths lives in one tested module. **Sample size**: how many users per variant to detect a given lift with 80% power. **Two-proportion z-test** for conversion, **Welch's t-test** and a **bootstrap** interval for revenue per user (skewed data). The verdict function turns numbers into a decision a product manager understands.""",
     "abtest.py", '''
"""Statistics for A/B tests."""
from dataclasses import dataclass
import numpy as np
from scipy import stats


def sample_size_per_arm(base_rate: float, min_lift: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Users per variant to detect an absolute lift `min_lift` over `base_rate` (two-sided)."""
    p1, p2 = base_rate, base_rate + min_lift
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    pbar = (p1 + p2) / 2
    n = (z_a * np.sqrt(2 * pbar * (1 - pbar)) + z_b * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return int(np.ceil(n))


@dataclass
class PropResult:
    rate_a: float; rate_b: float; lift: float; ci_low: float; ci_high: float; z: float; p_value: float


def two_proportion_test(conv_a: int, n_a: int, conv_b: int, n_b: int, alpha: float = 0.05) -> PropResult:
    pa, pb = conv_a / n_a, conv_b / n_b
    pooled = (conv_a + conv_b) / (n_a + n_b)
    se_pooled = np.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (pb - pa) / se_pooled
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    se = np.sqrt(pa * (1 - pa) / n_a + pb * (1 - pb) / n_b)            # unpooled SE for the interval
    m = stats.norm.ppf(1 - alpha / 2) * se
    return PropResult(pa, pb, pb - pa, pb - pa - m, pb - pa + m, float(z), float(p))


def welch_t(a: np.ndarray, b: np.ndarray):
    t, p = stats.ttest_ind(b, a, equal_var=False)
    return float(t), float(p)


def bootstrap_diff_ci(a: np.ndarray, b: np.ndarray, n_boot: int = 4000, alpha: float = 0.05, seed: int = 0):
    rng = np.random.default_rng(seed)
    diffs = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(n_boot)]
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def verdict(res: PropResult, alpha: float = 0.05) -> str:
    if res.p_value < alpha and res.ci_low > 0:
        return f"B wins: conversion +{res.lift:.2%} (95% CI {res.ci_low:+.2%} to {res.ci_high:+.2%}), p = {res.p_value:.4f}. Ship B."
    if res.p_value < alpha and res.ci_high < 0:
        return f"B is worse: {res.lift:.2%} (p = {res.p_value:.4f}). Keep A."
    return f"No significant difference (p = {res.p_value:.3f}); the true lift could be anywhere from {res.ci_low:+.2%} to {res.ci_high:+.2%}. Keep collecting data or stop."


def peeking_false_positive_rate(n_sims: int = 500, n_per_arm: int = 5000, looks: int = 20, seed: int = 1) -> float:
    """Simulate A/A tests where the analyst checks p < 0.05 after every batch: shows why peeking inflates false positives."""
    rng = np.random.default_rng(seed); hits = 0
    for _ in range(n_sims):
        a = rng.random(n_per_arm) < 0.1; b = rng.random(n_per_arm) < 0.1
        for k in np.linspace(n_per_arm / looks, n_per_arm, looks).astype(int):
            if two_proportion_test(a[:k].sum(), k, b[:k].sum(), k).p_value < 0.05:
                hits += 1; break
    return hits / n_sims
'''),
   S("Simulate an experiment", """A simulator with a *known* true effect is the best way to check your analysis: if you set +0.8 points and the CI covers it, the code works.""",
     "simulate.py", '''
"""python simulate.py  -> experiment.csv with 40,000 users"""
import numpy as np, pandas as pd


def simulate(n=40_000, base=0.10, lift=0.008, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    variant = rng.choice(["A", "B"], n)
    p = np.where(variant == "B", base + lift, base)
    converted = rng.random(n) < p
    revenue = np.where(converted, rng.lognormal(6.0, 0.6, n), 0.0).round(2)     # skewed order values in rupees
    return pd.DataFrame({"user_id": np.arange(n), "variant": variant, "converted": converted.astype(int), "revenue": revenue})


if __name__ == "__main__":
    df = simulate(); df.to_csv("experiment.csv", index=False)
    print(df.groupby("variant")[["converted", "revenue"]].mean().round(4))
'''),
   S("Analyse from the command line", "A script version of the analysis — useful in notebooks and CI.", "analyze.py", '''
"""python analyze.py experiment.csv"""
import sys
import pandas as pd
import abtest

df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "experiment.csv")
g = df.groupby("variant")
n, conv = g.size(), g["converted"].sum()
print("planning: users per arm to detect +0.8 points from 10%:", abtest.sample_size_per_arm(0.10, 0.008))
res = abtest.two_proportion_test(conv["A"], n["A"], conv["B"], n["B"])
print(res)
print(abtest.verdict(res))
a, b = df.loc[df.variant == "A", "revenue"].to_numpy(), df.loc[df.variant == "B", "revenue"].to_numpy()
print("revenue/user: A %.2f  B %.2f" % (a.mean(), b.mean()), "| Welch t, p =", abtest.welch_t(a, b), "| bootstrap 95%% CI of diff = (%.2f, %.2f)" % abtest.bootstrap_diff_ci(a, b, 1000))
print("false-positive rate if you peek 20 times in an A/A test: %.0f%% (should be 5%%)" % (100 * abtest.peeking_false_positive_rate(200)))
'''),
   S("The Streamlit app", """Streamlit turns a Python script into a web app. Run `streamlit run app.py`; deploy free on Streamlit Community Cloud or Hugging Face Spaces.""",
     "app.py", '''
import streamlit as st, pandas as pd, matplotlib.pyplot as plt
import abtest
from simulate import simulate

st.set_page_config(page_title="A/B test analyser", layout="centered")
st.title("A/B test analyser")
with st.expander("1 · Plan the experiment"):
    base = st.number_input("Current conversion rate", 0.001, 0.99, 0.10); lift = st.number_input("Smallest lift worth detecting (absolute)", 0.001, 0.5, 0.008, format="%.3f")
    st.write(f"You need **{abtest.sample_size_per_arm(base, lift):,} users per variant** (alpha 0.05, power 0.8).")
up = st.file_uploader("2 · Upload results CSV (columns: variant, converted[, revenue])", type="csv")
df = pd.read_csv(up) if up else simulate()
if not up: st.caption("Showing a simulated experiment — upload your own CSV to analyse it.")
g = df.groupby("variant"); n, conv = g.size(), g["converted"].sum()
res = abtest.two_proportion_test(conv.iloc[0], n.iloc[0], conv.iloc[1], n.iloc[1])
c1, c2, c3 = st.columns(3); c1.metric("Conversion A", f"{res.rate_a:.2%}"); c2.metric("Conversion B", f"{res.rate_b:.2%}", f"{res.lift:+.2%}"); c3.metric("p-value", f"{res.p_value:.4f}")
st.success(abtest.verdict(res)) if res.p_value < 0.05 else st.info(abtest.verdict(res))
fig, ax = plt.subplots(figsize=(6, 2)); ax.errorbar([res.lift], [0], xerr=[[res.lift - res.ci_low], [res.ci_high - res.lift]], fmt="o", capsize=6)
ax.axvline(0, color="grey", ls="--"); ax.set_yticks([]); ax.set_xlabel("lift in conversion (B − A), 95% CI"); st.pyplot(fig)
if "revenue" in df:
    a, b = (df.loc[df.variant == v, "revenue"].to_numpy() for v in n.index[:2])
    lo, hi = abtest.bootstrap_diff_ci(a, b, 2000); st.write(f"Revenue per user difference: **{b.mean() - a.mean():+.2f}** (bootstrap 95% CI {lo:+.2f} to {hi:+.2f})")
'''),
   S("Tests against SciPy/statsmodels", "Validate your implementation against trusted libraries.", "tests/test_abtest.py", '''
import numpy as np
from statsmodels.stats.proportion import proportions_ztest
import abtest


def test_z_matches_statsmodels():
    res = abtest.two_proportion_test(480, 10000, 560, 10000)
    z, p = proportions_ztest([560, 480], [10000, 10000])
    assert abs(res.z - z) < 1e-9 and abs(res.p_value - p) < 1e-9


def test_sample_size_reasonable():
    n = abtest.sample_size_per_arm(0.10, 0.01)
    assert 13000 < n < 16500


def test_ci_covers_true_effect_on_simulation():
    from simulate import simulate
    df = simulate(n=200_000, lift=0.01, seed=3); g = df.groupby("variant")
    r = abtest.two_proportion_test(g.converted.sum()["A"], g.size()["A"], g.converted.sum()["B"], g.size()["B"])
    assert r.ci_low < 0.01 < r.ci_high
'''),
   S("Run it", "", None, "python simulate.py && python analyze.py experiment.csv\npytest -q\nstreamlit run app.py", "bash"),
  ],
  check=["python simulate.py", "python analyze.py experiment.csv", "pytest -q"],
  talk=["How you chose the sample size before starting, and why stopping early when p < 0.05 ('peeking') inflates false positives (your simulation shows ~20%+).",
        "Why you used a bootstrap for revenue (heavy-tailed) instead of assuming normality.", "Statistical vs practical significance: the CI tells the business the plausible range of impact."],
  errors=[("p-value is 0.0 or nan", "a variant has zero conversions or n is tiny; check the grouping column values"),
          ("Streamlit shows nothing", "run with `streamlit run app.py`, not `python app.py`")],
  extend=["Add CUPED variance reduction using pre-experiment data", "Bayesian A/B testing with Beta posteriors", "Sequential testing (always-valid p-values)"],
  see=["m-hypothesis", "m-sampling-ci", "m-distributions", "m-bayes", "m-scipy"])

P3 = P("p-ml-from-scratch", "Build your own mini deep-learning library (autograd from scratch)", "math", "Intermediate", "2–3 days", "VS Code (CPU)",
  "Implement a tiny PyTorch-like library in NumPy: a Tensor with automatic differentiation, layers, losses and optimisers — then train linear regression, logistic regression and a neural network with it, and prove the gradients are right.",
  ["`minitorch/tensor.py`: reverse-mode autodiff (add, mul, matmul, relu, sigmoid, log, exp, sum, mean, broadcasting)", "`minitorch/nn.py`: Linear, MLP, MSE and BCE losses, SGD and Adam",
   "Gradient checks against finite differences and against PyTorch", "Training demos that match scikit-learn"],
  ["vectors and matrices", "derivatives, chain rule, gradients", "Jacobians and broadcasting", "gradient descent, Adam", "testing numerical code"],
  "No external data — synthetic regression data and scikit-learn's moons/breast-cancer datasets.",
  ["Tensor + computational graph", "backward pass (topological sort, chain rule)", "layers & losses", "optimisers", "train + verify"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\nscikit-learn>=1.4\npytest>=8.0\ntorch>=2.2   # only for the comparison test", "text"),
   S("The autograd engine", """Every operation creates a new Tensor that remembers its parents and a small `_backward` function applying the **chain rule** locally. `backward()` topologically sorts the graph and calls them in reverse. Broadcasting needs care: gradients must be summed back to the parent's shape (`_unbroadcast`).""",
     "minitorch/tensor.py", '''
"""A tiny reverse-mode automatic differentiation engine on NumPy arrays."""
import numpy as np


def _unbroadcast(grad, shape):
    while grad.ndim > len(shape):
        grad = grad.sum(axis=0)
    for i, s in enumerate(shape):
        if s == 1 and grad.shape[i] != 1:
            grad = grad.sum(axis=i, keepdims=True)
    return grad


class Tensor:
    def __init__(self, data, parents=(), requires_grad=False):
        self.data = np.asarray(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self._parents, self._backward, self.requires_grad = parents, (lambda: None), requires_grad

    shape = property(lambda self: self.data.shape)
    def __repr__(self): return f"Tensor({self.data!r})"

    # ---- operations (each defines its local derivative) ----
    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, (self, other))
        def back():
            self.grad += _unbroadcast(out.grad, self.shape); other.grad += _unbroadcast(out.grad, other.shape)
        out._backward = back; return out

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, (self, other))
        def back():
            self.grad += _unbroadcast(out.grad * other.data, self.shape); other.grad += _unbroadcast(out.grad * self.data, other.shape)
        out._backward = back; return out

    def __matmul__(self, other):
        out = Tensor(self.data @ other.data, (self, other))
        def back():
            self.grad += out.grad @ other.data.T; other.grad += self.data.T @ out.grad
        out._backward = back; return out

    def __neg__(self): return self * -1.0
    def __sub__(self, other): return self + (-other if isinstance(other, Tensor) else Tensor(-np.asarray(other)))
    def __rsub__(self, other): return Tensor(other) + (-self)
    __radd__ = __add__
    __rmul__ = __mul__

    def _unary(self, value, local_grad):
        out = Tensor(value, (self,))
        def back(): self.grad += out.grad * local_grad(out.data)
        out._backward = back; return out

    def relu(self): return self._unary(np.maximum(self.data, 0), lambda y: (self.data > 0).astype(float))
    def sigmoid(self): return self._unary(1 / (1 + np.exp(-self.data)), lambda y: y * (1 - y))
    def tanh(self): return self._unary(np.tanh(self.data), lambda y: 1 - y ** 2)
    def exp(self): return self._unary(np.exp(self.data), lambda y: y)
    def log(self): return self._unary(np.log(self.data), lambda y: 1 / self.data)

    def sum(self):
        out = Tensor(self.data.sum(), (self,))
        def back(): self.grad += np.ones_like(self.data) * out.grad
        out._backward = back; return out

    def mean(self): return self.sum() * (1.0 / self.data.size)

    # ---- backpropagation ----
    def backward(self):
        order, seen = [], set()
        def visit(t):
            if id(t) not in seen:
                seen.add(id(t))
                for p in t._parents: visit(p)
                order.append(t)
        visit(self)
        for t in order: t.grad = np.zeros_like(t.data)
        self.grad = np.ones_like(self.data)
        for t in reversed(order): t._backward()
'''),
   S("Layers, losses and optimisers", """With autograd done, a neural network is just Tensors combined; optimisers update every parameter with its `.grad`. Adam keeps running means of gradients and squared gradients.""",
     "minitorch/nn.py", '''
import numpy as np
from .tensor import Tensor


class Linear:
    def __init__(self, n_in, n_out, rng):
        self.W = Tensor(rng.normal(0, np.sqrt(2 / n_in), (n_in, n_out)), requires_grad=True)
        self.b = Tensor(np.zeros((1, n_out)), requires_grad=True)
    def __call__(self, x): return x @ self.W + self.b
    def parameters(self): return [self.W, self.b]


class MLP:
    def __init__(self, sizes, seed=0, act="relu"):
        rng = np.random.default_rng(seed); self.layers = [Linear(a, b, rng) for a, b in zip(sizes[:-1], sizes[1:])]; self.act = act
    def __call__(self, x):
        for i, layer in enumerate(self.layers):
            x = layer(x)
            if i < len(self.layers) - 1: x = getattr(x, self.act)()
        return x
    def parameters(self): return [p for l in self.layers for p in l.parameters()]


def mse(pred, target): d = pred - Tensor(target); return (d * d).mean()


def bce_with_logits(logits, target, eps=1e-9):
    p = logits.sigmoid(); t = Tensor(target)
    return -((t * (p + eps).log()) + ((1 - t) * (1 - p + eps).log())).mean()


class SGD:
    def __init__(self, params, lr=0.1): self.params, self.lr = params, lr
    def step(self):
        for p in self.params: p.data -= self.lr * p.grad


class Adam:
    def __init__(self, params, lr=1e-2, b1=0.9, b2=0.999):
        self.params, self.lr, self.b1, self.b2, self.t = params, lr, b1, b2, 0
        self.m = [np.zeros_like(p.data) for p in params]; self.v = [np.zeros_like(p.data) for p in params]
    def step(self):
        self.t += 1
        for i, p in enumerate(self.params):
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * p.grad; self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * p.grad ** 2
            mh, vh = self.m[i] / (1 - self.b1 ** self.t), self.v[i] / (1 - self.b2 ** self.t)
            p.data -= self.lr * mh / (np.sqrt(vh) + 1e-8)
'''),
   S("Package exports", "", "minitorch/__init__.py", "from .tensor import Tensor\nfrom .nn import Linear, MLP, mse, bce_with_logits, SGD, Adam\n"),
   S("Train three models", """Linear regression (should recover the true weights), logistic regression on breast-cancer data (should match scikit-learn's accuracy) and an MLP that solves the non-linear moons dataset.""",
     "demo.py", '''
import numpy as np
from sklearn.datasets import make_moons, load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from minitorch import Tensor, Linear, MLP, mse, bce_with_logits, SGD, Adam

rng = np.random.default_rng(0)
X = rng.normal(size=(500, 3)); y = X @ np.array([[2.0], [-1.0], [0.5]]) + 3 + rng.normal(0, 0.1, (500, 1))
lin = Linear(3, 1, rng); opt = SGD(lin.parameters(), lr=0.1)
for _ in range(300):
    loss = mse(lin(Tensor(X)), y); loss.backward(); opt.step()
print("linear regression weights", lin.W.data.ravel().round(3), "bias", lin.b.data.ravel().round(3), "(true [2, -1, 0.5], 3)")

Xc, yc = load_breast_cancer(return_X_y=True); Xc = StandardScaler().fit_transform(Xc); yc = yc[:, None].astype(float)
logreg = Linear(30, 1, rng); opt = Adam(logreg.parameters(), lr=0.05)
for _ in range(300):
    loss = bce_with_logits(logreg(Tensor(Xc)), yc); loss.backward(); opt.step()
acc = ((logreg(Tensor(Xc)).data > 0) == yc).mean()
print(f"logistic regression accuracy {acc:.3f} | scikit-learn {LogisticRegression(max_iter=2000).fit(Xc, yc.ravel()).score(Xc, yc.ravel()):.3f}")

Xm, ym = make_moons(400, noise=0.15, random_state=0); ym = ym[:, None].astype(float)
net = MLP([2, 16, 16, 1], seed=1); opt = Adam(net.parameters(), lr=0.02)
for step in range(800):
    loss = bce_with_logits(net(Tensor(Xm)), ym); loss.backward(); opt.step()
print(f"MLP on moons: loss {float(loss.data):.4f}, accuracy {((net(Tensor(Xm)).data > 0) == ym).mean():.3f}")
'''),
   S("Prove the gradients are correct", """Two independent checks: central finite differences, and PyTorch's autograd on the same computation. If these pass, your engine is right.""",
     "tests/test_grad.py", '''
import numpy as np, torch
from minitorch import Tensor


def f_minitorch(a, b, c):
    return (((a @ b) + c).tanh() * ((a @ b).sigmoid())).sum()


def test_against_finite_differences():
    rng = np.random.default_rng(0); A, B, C = rng.normal(size=(3, 4)), rng.normal(size=(4, 2)), rng.normal(size=(1, 2))
    a, b, c = Tensor(A), Tensor(B), Tensor(C); out = f_minitorch(a, b, c); out.backward()
    eps = 1e-6
    for (t, arr) in ((a, A), (b, B), (c, C)):
        num = np.zeros_like(arr)
        for idx in np.ndindex(arr.shape):
            p, m = arr.copy(), arr.copy(); p[idx] += eps; m[idx] -= eps
            args = [Tensor(p if x is arr else x) for x in (A, B, C)]; args2 = [Tensor(m if x is arr else x) for x in (A, B, C)]
            num[idx] = (f_minitorch(*args).data - f_minitorch(*args2).data) / (2 * eps)
        assert np.allclose(t.grad, num, atol=1e-5)


def test_against_pytorch():
    rng = np.random.default_rng(1); A, B, C = rng.normal(size=(5, 3)), rng.normal(size=(3, 4)), rng.normal(size=(1, 4))
    a, b, c = Tensor(A), Tensor(B), Tensor(C); f_minitorch(a, b, c).backward()
    ta, tb, tc = (torch.tensor(x, requires_grad=True) for x in (A, B, C))
    ((ta @ tb + tc).tanh() * torch.sigmoid(ta @ tb)).sum().backward()
    for mine, ref in ((a, ta), (b, tb), (c, tc)):
        assert np.allclose(mine.grad, ref.grad.numpy(), atol=1e-10)
'''),
   S("Run it", "", None, "python demo.py\npytest -q", "bash"),
  ],
  check=["python demo.py", "pytest -q"],
  talk=["Walk through how reverse-mode autodiff works: graph, topological order, local derivatives, gradient accumulation.", "Why broadcasting requires summing gradients back to the original shape.",
        "How you verified correctness (finite differences + PyTorch) — the same technique catches bugs in custom layers at work."],
  errors=[("Gradients double each time", "reset .grad before every backward (backward() here zeroes the graph's grads first)"), ("Shape mismatch in _unbroadcast", "bias must be shape (1, n_out), not (n_out,)")],
  extend=["Add softmax cross-entropy and train on digits", "Add Conv1D", "Add a computation-graph visualiser with graphviz"],
  see=["m-derivatives", "m-gradients", "m-matrices", "m-backprop", "m-optimizers", "m-vectors"])

P4 = P("p-house-prices", "House price prediction: end-to-end tabular ML with FastAPI and Docker", "found", "Intermediate", "3–4 days", "VS Code (CPU); Docker optional",
  "The complete classical ML workflow on California housing data: EDA, leakage-free pipelines, feature engineering, model comparison with cross-validation, tuning, a test-set evaluation, a model card, a FastAPI prediction service with tests, and a Docker image.",
  ["`src/data.py` (download + stratified split by income band)", "`src/features.py` (custom scikit-learn transformer for ratio features)", "`src/train.py` (compare 4 models with CV, tune the best, save model + metrics)",
   "`src/evaluate.py` (test-set metrics, residual plot, error by segment)", "`app/main.py` FastAPI service + `tests/test_api.py`", "Dockerfile and model card"],
  ["EDA", "train/test split strategy", "ColumnTransformer + Pipeline", "custom transformers", "cross-validation and RandomizedSearchCV", "regression metrics", "FastAPI", "Docker", "model cards"],
  "California Housing (1990 census, 20,640 districts, from the 'Hands-On ML' GitHub repository).",
  ["download", "stratified split", "EDA", "pipeline (impute, ratios, scale, one-hot)", "CV model comparison", "tune", "test evaluation", "save artifact", "FastAPI + Docker"],
  [
   S("Dependencies", "", "requirements.txt", "pandas>=2.0\nnumpy>=1.26\nscikit-learn>=1.4\nlightgbm>=4.0\nmatplotlib>=3.8\njoblib\nfastapi>=0.110\nuvicorn[standard]\nhttpx\npydantic>=2\npytest>=8.0", "text"),
   S("Ignore data and models", "", ".gitignore", GITIGNORE),
   S("Data and a careful split", """Split **before** any analysis. Median income is the strongest predictor, so stratify by income band to keep the test set representative (otherwise your test score depends on luck).""",
     "src/data.py", '''
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split

URL = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
TARGET = "median_house_value"


def load() -> pd.DataFrame:
    path = Path("data/housing.csv"); path.parent.mkdir(exist_ok=True)
    if not path.exists():
        pd.read_csv(URL).to_csv(path, index=False)
    return pd.read_csv(path)


def split(df: pd.DataFrame, seed: int = 42):
    band = pd.cut(df["median_income"], [0, 1.5, 3, 4.5, 6, np.inf], labels=False)
    train, test = train_test_split(df, test_size=0.2, stratify=band, random_state=seed)
    return train.reset_index(drop=True), test.reset_index(drop=True)
'''),
   S("Package markers", "", "src/__init__.py", ""),
   S("Feature engineering as a transformer", """Ratio features (rooms per household, bedrooms per room, people per household) carry more signal than raw totals. Wrapping them in a scikit-learn transformer means the **same code** runs in training, cross-validation and the API — no training–serving skew.""",
     "src/features.py", '''
import numpy as np, pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUM = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms", "population", "households", "median_income"]
CAT = ["ocean_proximity"]


class RatioFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        X = X.copy()
        X["rooms_per_household"] = X["total_rooms"] / X["households"]
        X["bedrooms_per_room"] = X["total_bedrooms"] / X["total_rooms"]
        X["people_per_household"] = X["population"] / X["households"]
        for c in ["total_rooms", "total_bedrooms", "population", "households"]:
            X[c] = np.log1p(X[c])
        return X


def preprocessor() -> Pipeline:
    num = NUM + ["rooms_per_household", "bedrooms_per_room", "people_per_household"]
    cols = ColumnTransformer([("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num),
                              ("cat", OneHotEncoder(handle_unknown="ignore"), CAT)])
    return Pipeline([("ratios", RatioFeatures()), ("cols", cols)])
'''),
   S("Compare models, tune, save", """Compare a baseline and three models with 5-fold CV (RMSE), tune the winner with RandomizedSearchCV, then refit on all training data and save the **whole pipeline** with joblib together with metrics and a model card. `--fast` uses fewer iterations for quick checks.""",
     "src/train.py", '''
"""python -m src.train [--fast]"""
import argparse, json, time
from pathlib import Path
import joblib, numpy as np
from lightgbm import LGBMRegressor
from scipy.stats import randint, uniform
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, RandomizedSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from .data import TARGET, load, split
from .features import preprocessor


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fast", action="store_true"); args = ap.parse_args()
    train, _ = split(load()); X, y = train.drop(columns=TARGET), train[TARGET]
    cv = KFold(5, shuffle=True, random_state=0)
    models = {"baseline (mean)": DummyRegressor(), "ridge": Ridge(1.0),
              "random forest": RandomForestRegressor(n_estimators=60 if args.fast else 200, n_jobs=-1, random_state=0),
              "lightgbm": LGBMRegressor(n_estimators=400, learning_rate=0.05, verbose=-1, random_state=0)}
    results = {}
    for name, m in models.items():
        t = time.time(); s = -cross_val_score(Pipeline([("pre", preprocessor()), ("m", m)]), X, y, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=1)
        results[name] = float(s.mean()); print(f"{name:16s} CV RMSE {s.mean():9,.0f} ± {s.std():6,.0f}  ({time.time() - t:.0f}s)")
    search = RandomizedSearchCV(Pipeline([("pre", preprocessor()), ("m", LGBMRegressor(verbose=-1, random_state=0))]),
        {"m__n_estimators": randint(200, 1200), "m__learning_rate": uniform(0.02, 0.1), "m__num_leaves": randint(15, 127), "m__min_child_samples": randint(5, 60),
         "m__subsample": uniform(0.6, 0.4), "m__subsample_freq": [1], "m__colsample_bytree": uniform(0.6, 0.4)},
        n_iter=4 if args.fast else 25, cv=cv, scoring="neg_root_mean_squared_error", random_state=0, n_jobs=1).fit(X, y)
    print("tuned lightgbm CV RMSE", f"{-search.best_score_:,.0f}", search.best_params_)
    Path("models").mkdir(exist_ok=True); joblib.dump(search.best_estimator_, "models/model.joblib")
    meta = {"cv_rmse": results | {"lightgbm tuned": float(-search.best_score_)}, "params": {k: (float(v) if isinstance(v, (float, np.floating)) else int(v)) for k, v in search.best_params_.items()},
            "trained_rows": len(X), "features": list(X.columns)}
    Path("models/metrics.json").write_text(json.dumps(meta, indent=2)); print("saved models/model.joblib")


if __name__ == "__main__":
    main()
'''),
   S("Evaluate once on the test set", """Only now touch the test set. Report RMSE, MAE, R², and — more useful to the business — error by segment and a residual plot. Then write the model card.""",
     "src/evaluate.py", '''
"""python -m src.evaluate"""
import json
from pathlib import Path
import joblib, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from .data import TARGET, load, split

_, test = split(load()); model = joblib.load("models/model.joblib")
y, pred = test[TARGET], model.predict(test.drop(columns=TARGET))
m = {"rmse": float(np.sqrt(mean_squared_error(y, pred))), "mae": float(mean_absolute_error(y, pred)), "r2": float(r2_score(y, pred))}
print({k: round(v, 3) for k, v in m.items()})
seg = pd.DataFrame({"ocean": test["ocean_proximity"], "abs_err": np.abs(y - pred)}).groupby("ocean")["abs_err"].agg(["mean", "count"]).round(0)
print(seg)
fig, ax = plt.subplots(1, 2, figsize=(10, 4)); ax[0].scatter(y, pred, s=3, alpha=0.3); ax[0].plot([0, 5e5], [0, 5e5], "r--"); ax[0].set(xlabel="actual", ylabel="predicted")
ax[1].scatter(pred, y - pred, s=3, alpha=0.3); ax[1].axhline(0, color="r"); ax[1].set(xlabel="predicted", ylabel="residual"); fig.tight_layout(); fig.savefig("models/residuals.png", dpi=110)
card = f"""# Model card — California house price regressor
**Model:** tuned LightGBM inside a scikit-learn pipeline (ratio features, imputation, scaling, one-hot).
**Data:** 1990 California census districts; 80/20 split stratified by income band.
**Test metrics:** RMSE ${m['rmse']:,.0f} · MAE ${m['mae']:,.0f} · R² {m['r2']:.3f}
**Intended use:** teaching/portfolio; rough district-level price estimates.
**Limitations:** 1990 prices capped at $500,001 (the model can't predict above the cap); district averages, not individual houses; error is higher for ISLAND/NEAR BAY segments.
**Error by segment:**\\n\\n{seg.to_markdown() if hasattr(seg, "to_markdown") else seg.to_string()}"""
Path("models/MODEL_CARD.md").write_text(card); Path("models/test_metrics.json").write_text(json.dumps(m, indent=2)); print("wrote models/MODEL_CARD.md")
'''),
   S("Prediction API", """Load the pipeline once at startup; validate inputs with Pydantic (types, ranges, allowed categories). The API returns the prediction and the model version.""",
     "app/main.py", '''
from typing import Literal
import joblib, pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="House price API", version="1.0")
model = joblib.load("models/model.joblib")


class District(BaseModel):
    longitude: float = Field(ge=-125, le=-114); latitude: float = Field(ge=32, le=42.5)
    housing_median_age: float = Field(ge=0, le=100); total_rooms: float = Field(gt=0); total_bedrooms: float | None = Field(default=None, gt=0)
    population: float = Field(gt=0); households: float = Field(gt=0); median_income: float = Field(gt=0, le=20)
    ocean_proximity: Literal["<1H OCEAN", "INLAND", "NEAR OCEAN", "NEAR BAY", "ISLAND"]


@app.get("/health")
def health(): return {"status": "ok"}


@app.post("/predict")
def predict(d: District):
    price = float(model.predict(pd.DataFrame([d.model_dump()]))[0])
    return {"predicted_median_house_value": round(price, -2), "model_version": "1.0"}
'''),
   S("App package marker", "", "app/__init__.py", ""),
   S("API tests", "TestClient calls the app in-process — no server needed.", "tests/test_api.py", '''
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
GOOD = {"longitude": -122.23, "latitude": 37.88, "housing_median_age": 41, "total_rooms": 880, "total_bedrooms": 129,
        "population": 322, "households": 126, "median_income": 8.3252, "ocean_proximity": "NEAR BAY"}


def test_health(): assert client.get("/health").json() == {"status": "ok"}


def test_predict_reasonable():
    r = client.post("/predict", json=GOOD); assert r.status_code == 200
    assert 150_000 < r.json()["predicted_median_house_value"] < 600_000


def test_rejects_bad_category():
    assert client.post("/predict", json=GOOD | {"ocean_proximity": "MARS"}).status_code == 422
'''),
   S("Docker image", "Package code + model so it runs identically anywhere.", "Dockerfile", '''
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY app ./app
COPY models ./models
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]''', "dockerfile"),
   S("Run everything", "", None, """
python -m src.train          # ~2 minutes (use --fast while developing)
python -m src.evaluate
pytest -q
uvicorn app.main:app --reload            # open http://127.0.0.1:8000/docs
docker build -t house-api . && docker run -p 8000:8000 house-api""", "bash"),
  ],
  check=["python -m src.train --fast", "python -m src.evaluate", "pytest -q"],
  talk=["Why you stratified the split by income and kept the test set untouched until the end.", "How the pipeline prevents leakage and training–serving skew (same transformer in CV and in the API).",
        "Model choice: LightGBM beat Ridge and Random Forest in CV; you report RMSE ± std across folds.", "Limitations from the model card (capped prices, 1990 data)."],
  errors=[("ValueError: Input contains NaN in total_bedrooms", "keep the SimpleImputer inside the pipeline"), ("FileNotFoundError models/model.joblib when starting the API", "run python -m src.train first, from the project root"),
          ("Docker image huge/slow", "use python:3.12-slim and --no-cache-dir; add a .dockerignore for data/ and .venv/")],
  extend=["Add SHAP explanations to the API response", "Log experiments with MLflow", "Deploy the container on Render/Railway/Azure App Service"],
  see=["m-problem-formulation", "m-eda", "m-train-val-test", "m-feature-engineering", "m-hyperparams", "m-metrics-reg", "m-leakage", "m-fastapi", "m-deployment"])

P5 = P("p-churn", "Customer churn prediction with XGBoost, SHAP and a Streamlit app", "sup", "Intermediate", "3–4 days", "VS Code or Colab (CPU)",
  "Predict which telecom customers will leave, choose the decision threshold by expected profit, explain predictions with SHAP, and ship a Streamlit app for the retention team plus a batch-scoring script.",
  ["`train.py`: clean data, compare logistic regression / random forest / XGBoost with stratified CV, calibrate, pick the profit-maximising threshold, save", "`explain.py`: global and per-customer SHAP explanations",
   "`predict.py`: batch-score a CSV and export a call list ranked by expected value", "`app.py`: Streamlit app — enter a customer, see churn risk, top reasons and recommended action"],
  ["imbalanced classification", "pipelines with mixed types", "XGBoost", "PR-AUC, recall@k", "probability calibration", "threshold tuning by business cost", "SHAP", "Streamlit"],
  "IBM Telco Customer Churn (7,043 customers, 21 columns) from IBM's public GitHub repository.",
  ["download + clean (TotalCharges as numeric)", "stratified CV model comparison", "calibration", "profit-based threshold", "SHAP explanations", "batch scoring + app"],
  [
   S("Dependencies", "", "requirements.txt", "pandas>=2.0\nnumpy>=1.26\nscikit-learn>=1.4\nxgboost>=2.0\nshap>=0.44\njoblib\nstreamlit>=1.30\nmatplotlib>=3.8", "text"),
   S("Ignore data and models", "", ".gitignore", GITIGNORE),
   S("Shared data code", """`TotalCharges` is stored as text with blanks for brand-new customers — a classic real-data trap. Fix it in one function used by every script.""",
     "churn_data.py", '''
from pathlib import Path
import pandas as pd

URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
CAT = ["gender", "Partner", "Dependents", "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
       "TechSupport", "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod"]
NUM = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]


def load() -> pd.DataFrame:
    p = Path("data/telco.csv"); p.parent.mkdir(exist_ok=True)
    if not p.exists(): pd.read_csv(URL).to_csv(p, index=False)
    df = pd.read_csv(p)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0.0)
    df["Churn"] = (df["Churn"] == "Yes").astype(int)
    return df
'''),
   S("Train, calibrate and pick the threshold", """Business framing: a retention offer costs ₹500 and saves 30% of the churners who get it; a saved customer is worth ₹12,000. The threshold that maximises **expected profit** on validation predictions is usually far from 0.5. Calibration makes the probabilities trustworthy for that calculation.""",
     "train.py", '''
import json, joblib, numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier
from churn_data import CAT, NUM, load

OFFER_COST, SAVE_RATE, CUSTOMER_VALUE = 500, 0.30, 12_000
df = load(); X, y = df[CAT + NUM], df["Churn"]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)
pre = lambda: ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CAT), ("num", StandardScaler(), NUM)])
pos_w = (ytr == 0).sum() / (ytr == 1).sum()
models = {"logistic": LogisticRegression(max_iter=2000, class_weight="balanced"),
          "random_forest": RandomForestClassifier(400, min_samples_leaf=5, class_weight="balanced", n_jobs=-1, random_state=0),
          "xgboost": XGBClassifier(n_estimators=400, learning_rate=0.03, max_depth=4, subsample=0.8, colsample_bytree=0.8, scale_pos_weight=pos_w, eval_metric="logloss", random_state=0)}
cv = StratifiedKFold(5, shuffle=True, random_state=0); scores = {}
for name, m in models.items():
    p = cross_val_predict(Pipeline([("pre", pre()), ("m", m)]), Xtr, ytr, cv=cv, method="predict_proba")[:, 1]
    scores[name] = {"roc_auc": roc_auc_score(ytr, p), "pr_auc": average_precision_score(ytr, p)}
    print(f"{name:14s} ROC-AUC {scores[name]['roc_auc']:.3f}  PR-AUC {scores[name]['pr_auc']:.3f}")
best = max(scores, key=lambda k: scores[k]["pr_auc"]); print("best:", best)
model = CalibratedClassifierCV(Pipeline([("pre", pre()), ("m", models[best])]), method="isotonic", cv=5).fit(Xtr, ytr)

def profit(p, y_true, t):
    target = p >= t
    return float((target * (y_true * SAVE_RATE * CUSTOMER_VALUE - OFFER_COST)).sum())
oof = cross_val_predict(CalibratedClassifierCV(Pipeline([("pre", pre()), ("m", models[best])]), method="isotonic", cv=3), Xtr, ytr, cv=cv, method="predict_proba")[:, 1]
grid = np.linspace(0.05, 0.9, 86); t_best = float(grid[np.argmax([profit(oof, ytr.to_numpy(), t) for t in grid])])
pt = model.predict_proba(Xte)[:, 1]
report = {"model": best, "threshold": t_best, "test_roc_auc": roc_auc_score(yte, pt), "test_pr_auc": average_precision_score(yte, pt),
          "test_profit_at_threshold": profit(pt, yte.to_numpy(), t_best), "test_profit_at_0.5": profit(pt, yte.to_numpy(), 0.5),
          "customers_contacted": int((pt >= t_best).sum()), "churners_caught_pct": float(((pt >= t_best) & (yte == 1)).sum() / yte.sum())}
print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in report.items()}, indent=2))
joblib.dump({"model": model, "threshold": t_best, "features": CAT + NUM}, "churn_model.joblib"); json.dump(report, open("report.json", "w"), indent=2)
'''),
   S("Explain with SHAP", """SHAP needs the tree model and the *transformed* features. Global importance tells the business what drives churn; per-customer contributions tell an agent why this customer is at risk.""",
     "explain.py", '''
import numpy as np, shap, joblib, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier
from churn_data import CAT, NUM, load

df = load(); X, y = df[CAT + NUM], df["Churn"]
pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT), ("num", StandardScaler(), NUM)]).fit(X)
Xt = pre.transform(X); names = pre.get_feature_names_out()
xgb = XGBClassifier(n_estimators=400, learning_rate=0.03, max_depth=4, subsample=0.8, colsample_bytree=0.8, eval_metric="logloss", random_state=0).fit(Xt, y)
sv = shap.TreeExplainer(xgb).shap_values(Xt)
imp = pd.Series(np.abs(sv).mean(0), index=names).sort_values(ascending=False)
print("top churn drivers:\\n", imp.head(8).round(3))
i = int(np.argmax(xgb.predict_proba(Xt)[:, 1]))
contrib = pd.Series(sv[i], index=names).sort_values(key=abs, ascending=False).head(5)
print(f"\\ncustomer {df.customerID[i]} (risk {xgb.predict_proba(Xt[i:i + 1])[0, 1]:.0%}) — reasons:\\n", contrib.round(3))
joblib.dump({"pre": pre, "xgb": xgb, "names": list(names)}, "explainer.joblib")
'''),
   S("Batch scoring", "Score a whole file and rank customers by expected value of contacting them — the list the retention team actually uses.", "predict.py", '''
"""python predict.py data/telco.csv calls.csv"""
import sys, joblib, pandas as pd

OFFER_COST, SAVE_RATE, CUSTOMER_VALUE = 500, 0.30, 12_000
bundle = joblib.load("churn_model.joblib")
df = pd.read_csv(sys.argv[1]); df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
df["churn_risk"] = bundle["model"].predict_proba(df[bundle["features"]])[:, 1]
df["expected_value_of_call"] = df["churn_risk"] * SAVE_RATE * CUSTOMER_VALUE - OFFER_COST
calls = df[df["churn_risk"] >= bundle["threshold"]].sort_values("expected_value_of_call", ascending=False)
calls[["customerID", "churn_risk", "expected_value_of_call", "Contract", "tenure", "MonthlyCharges"]].round(3).to_csv(sys.argv[2], index=False)
print(f"{len(calls)} customers to contact; top 3:\\n", calls[["customerID", "churn_risk"]].head(3).round(3))
'''),
   S("Streamlit app for the retention team", "", "app.py", '''
import joblib, numpy as np, pandas as pd, streamlit as st
from churn_data import CAT, NUM, load

st.title("Churn risk checker")
bundle, ex = joblib.load("churn_model.joblib"), joblib.load("explainer.joblib")
ref = load()
row = {}
cols = st.columns(2)
for i, c in enumerate(CAT):
    row[c] = cols[i % 2].selectbox(c, sorted(ref[c].unique()))
row["SeniorCitizen"] = int(st.checkbox("Senior citizen")); row["tenure"] = st.slider("Tenure (months)", 0, 72, 5)
row["MonthlyCharges"] = st.slider("Monthly charges", 18.0, 120.0, 80.0); row["TotalCharges"] = row["tenure"] * row["MonthlyCharges"]
X = pd.DataFrame([row])[CAT + NUM]
risk = bundle["model"].predict_proba(X)[0, 1]
st.metric("Churn risk", f"{risk:.0%}", "above action threshold" if risk >= bundle["threshold"] else "below threshold")
import shap
sv = shap.TreeExplainer(ex["xgb"]).shap_values(ex["pre"].transform(X))[0]
top = pd.Series(sv, index=ex["names"]).sort_values(key=np.abs, ascending=False).head(5)
st.subheader("Why"); st.bar_chart(top)
st.write("Suggested action:", "offer a 1-year contract discount" if row["Contract"] == "Month-to-month" else "check service quality / tech support")
'''),
   S("Run it", "", None, "python train.py\npython explain.py\npython predict.py data/telco.csv calls.csv\nstreamlit run app.py", "bash"),
  ],
  check=["python train.py", "python explain.py", "python predict.py data/telco.csv calls.csv"],
  talk=["Framing: a retention budget decision, not 'accuracy' — you chose the threshold by expected profit and compared it with 0.5.", "Why PR-AUC with 26% positives, stratified CV, calibration before using probabilities as money.",
        "SHAP findings: month-to-month contracts, short tenure, fibre internet and electronic-check payments drive churn.", "How the call list is used, and how you'd A/B test the retention offer."],
  errors=[("ValueError: could not convert string to float: ' '", "TotalCharges has blanks — convert with pd.to_numeric(errors='coerce')"),
          ("SHAP shape mismatch", "explain the tree model on the transformed (one-hot) matrix, not the raw DataFrame")],
  extend=["Uplift modelling: who churns less *because* of the offer", "Survival analysis: predict when they'll churn", "Wrap it with the MLOps project (MLflow + CI + drift monitoring)"],
  see=["m-gradient-boosting", "m-imbalance", "m-metrics-clf", "m-interpretability", "m-logistic-regression", "m-random-forest"])

P6 = P("p-segmentation", "Customer segmentation and market-basket analysis (Online Retail)", "unsup", "Intermediate", "2–3 days", "VS Code or Colab (CPU)",
  "Group 4,300 real customers into actionable segments with RFM features and clustering, compare algorithms, name the segments, mine product associations per segment, and present it in a dashboard.",
  ["`features.py`: Recency, Frequency, Monetary + tenure and basket-size features per customer", "`segment.py`: k-means vs GMM vs hierarchical, silhouette/Davies–Bouldin, PCA plot, segment profiles and names",
   "`basket.py`: Apriori-style association rules (support, confidence, lift) overall and for the top segment", "`dashboard.py`: Streamlit dashboard"],
  ["feature engineering for customers", "scaling and log transforms", "k-means, GMM, Agglomerative", "choosing k", "PCA for visualisation", "association rules", "turning clusters into business actions"],
  "UCI Online Retail (541,909 transactions) from a public GitHub mirror.",
  ["clean transactions", "customer-level RFM features", "log + scale", "cluster & compare", "profile & name", "association rules", "dashboard"],
  [
   S("Dependencies", "", "requirements.txt", "pandas>=2.0\nnumpy>=1.26\nscikit-learn>=1.4\nmatplotlib>=3.8\nstreamlit>=1.30", "text"),
   S("Customer features", """Aggregate transactions to one row per customer. RFM is the classic marketing representation; adding tenure and average basket size helps separate 'new big spenders' from 'loyal small buyers'.""",
     "features.py", f'''
from pathlib import Path
import numpy as np, pandas as pd
URL = "{RETAIL_URL}"


def transactions() -> pd.DataFrame:
    p = Path("data/retail.csv"); p.parent.mkdir(exist_ok=True)
    if not p.exists(): pd.read_csv(URL, dtype={{"InvoiceNo": str, "StockCode": str}}).to_csv(p, index=False)
    df = pd.read_csv(p, dtype={{"InvoiceNo": str, "StockCode": str}})
    df = df[~df.InvoiceNo.str.startswith("C") & (df.Quantity > 0) & (df.UnitPrice > 0)].dropna(subset=["CustomerID"])
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M"); df["Revenue"] = df.Quantity * df.UnitPrice
    df["Description"] = df["Description"].str.strip(); return df


def rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot = df.InvoiceDate.max() + pd.Timedelta(days=1)
    f = df.groupby("CustomerID").agg(recency=("InvoiceDate", lambda s: (snapshot - s.max()).days), frequency=("InvoiceNo", "nunique"),
                                      monetary=("Revenue", "sum"), tenure=("InvoiceDate", lambda s: (snapshot - s.min()).days),
                                      items=("Quantity", "sum"))
    f["avg_basket"] = f["monetary"] / f["frequency"]
    return f[f.monetary < f.monetary.quantile(0.995)]   # drop extreme wholesale outliers for clustering


if __name__ == "__main__":
    print(rfm(transactions()).describe().round(1))
'''),
   S("Cluster, compare, profile, name", """Log-transform (money and counts are skewed), scale, then compare algorithms for k = 2…8. Profiles (medians per cluster) are what the business reads, so the script names segments with simple rules.""",
     "segment.py", '''
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from features import rfm, transactions

F = rfm(transactions()); Z = StandardScaler().fit_transform(np.log1p(F[["recency", "frequency", "monetary", "tenure", "avg_basket"]]))
print(f"{len(F)} customers")
for k in range(2, 9):
    km = KMeans(k, n_init=10, random_state=0).fit(Z)
    print(f"k={k}  inertia {km.inertia_:8.0f}  silhouette {silhouette_score(Z, km.labels_):.3f}  DB {davies_bouldin_score(Z, km.labels_):.3f}")
K = 4
labels = {"kmeans": KMeans(K, n_init=10, random_state=0).fit_predict(Z), "gmm": GaussianMixture(K, random_state=0).fit_predict(Z),
          "ward": AgglomerativeClustering(K).fit_predict(Z)}
for n, l in labels.items(): print(f"{n:7s} silhouette {silhouette_score(Z, l):.3f}")
F["segment"] = labels["kmeans"]
prof = F.groupby("segment").agg(customers=("recency", "size"), recency=("recency", "median"), frequency=("frequency", "median"),
                                 monetary=("monetary", "median"), avg_basket=("avg_basket", "median")).round(0)
def name(r):
    if r.recency > 150: return "Lapsed"
    if r.frequency >= 6: return "Loyal regulars"
    if r.frequency <= 1 and r.recency < 60: return "New customers"
    if r.avg_basket >= prof.avg_basket.median() and r.recency < 60: return "Recent big spenders"
    return "Occasional"
prof["name"] = prof.apply(name, axis=1); print(prof)
F["segment_name"] = F.segment.map(prof["name"]); F.to_csv("segments.csv")
P2 = PCA(2).fit_transform(Z); fig, ax = plt.subplots(figsize=(6, 5))
for s, g in F.groupby("segment_name"): ax.scatter(P2[F.index.get_indexer(g.index), 0], P2[F.index.get_indexer(g.index), 1], s=4, label=s)
ax.legend(markerscale=4); ax.set_title("Customer segments (PCA projection)"); fig.savefig("segments_pca.png", dpi=110)
json.dump(prof.reset_index().to_dict("records"), open("profiles.json", "w"), indent=2, default=int)
'''),
   S("Market-basket rules", """Count product pairs per invoice (Apriori with max itemset size 2 is enough and fast), compute support, confidence and lift, and keep rules with lift > 1 and enough support.""",
     "basket.py", '''
from collections import Counter
from itertools import combinations
import pandas as pd
from features import transactions


def rules(df, min_support=0.01, top=10):
    baskets = df.groupby("InvoiceNo")["Description"].apply(lambda s: sorted(set(s)))
    n = len(baskets); single = Counter(i for b in baskets for i in b)
    frequent = {i for i, c in single.items() if c / n >= min_support}
    pairs = Counter(p for b in baskets for p in combinations([i for i in b if i in frequent], 2))
    out = []
    for (a, b), c in pairs.items():
        if c / n < min_support: continue
        for x, y in ((a, b), (b, a)):
            conf = c / single[x]; out.append((x, y, c / n, conf, conf / (single[y] / n)))
    return pd.DataFrame(out, columns=["if_bought", "then_buy", "support", "confidence", "lift"]).sort_values("lift", ascending=False).head(top).round(3)


if __name__ == "__main__":
    df = transactions(); uk = df[df.Country == "United Kingdom"]
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 36); pd.set_option("display.max_columns", None)
    print(rules(uk))
    seg = pd.read_csv("segments.csv", index_col=0)
    loyal = seg.index[seg.segment_name == "Loyal regulars"]
    print("\\nrules for Loyal regulars:\\n", rules(uk[uk.CustomerID.isin(loyal)], min_support=0.02, top=5))
'''),
   S("Dashboard", "", "dashboard.py", '''
import json, pandas as pd, streamlit as st
st.title("Customer segments")
seg = pd.read_csv("segments.csv"); prof = pd.DataFrame(json.load(open("profiles.json")))
st.dataframe(prof)
choice = st.selectbox("Segment", sorted(seg.segment_name.unique()))
st.image("segments_pca.png")
st.write(seg[seg.segment_name == choice].describe().round(1))
ACTIONS = {"New customers": "welcome series and second-purchase coupon", "Lapsed": "win-back email with a discount", "Loyal regulars": "loyalty programme, early access", "Recent big spenders": "VIP onboarding, cross-sell bundles", "Occasional": "reminders and bundles"}
st.success("Suggested action: " + ACTIONS.get(choice, "test offers"))
'''),
   S("Run it", "", None, "python segment.py\npython basket.py\nstreamlit run dashboard.py", "bash"),
  ],
  check=["python segment.py", "python basket.py"],
  talk=["Why log + scaling before k-means; how you chose k (silhouette, Davies–Bouldin, interpretability).", "How segments map to actions and how you'd measure success (A/B test the campaigns).",
        "Lift vs confidence in association rules."],
  errors=[("One giant cluster", "you forgot to log-transform skewed money/count features"), ("MemoryError in basket analysis", "filter rare items first (min_support) or limit to one country")],
  extend=["Predict customer lifetime value (BG/NBD models via the `lifetimes` package)", "Use HDBSCAN", "Recommend next products per segment from the rules"],
  see=["m-kmeans", "m-hierarchical", "m-dbscan-gmm", "m-pca", "m-assoc-rules", "m-feature-engineering"])

P7 = P("p-movie-recsys", "Movie recommendation system (collaborative filtering + content + app)", "unsup", "Intermediate", "3–4 days", "VS Code or Colab (CPU)",
  "Build and evaluate four recommenders on ~900,000 real movie ratings — popularity, item-based collaborative filtering, matrix factorisation (truncated SVD) and content-based genres — combine them into a hybrid, and serve recommendations in a Gradio app.",
  ["`data.py`: load MovieTweetings ratings/movies, filter sparse users/items, time-based train/test split", "`models.py`: Popularity, ItemKNN (sparse cosine), SVD factorisation, Genre content model, Hybrid",
   "`evaluate.py`: precision@10, recall@10, NDCG@10, catalogue coverage", "`app.py`: pick movies you like → recommendations"],
  ["sparse matrices", "cosine similarity", "matrix factorisation", "TF-IDF on genres", "ranking metrics", "time-based evaluation", "cold start"],
  "MovieTweetings (ratings 0–10 tweeted from IMDb, ~900k ratings, ~38k movies) from its GitHub repository.",
  ["load + filter", "time split", "user–item sparse matrix", "4 models", "ranking evaluation", "hybrid", "app"],
  [
   S("Dependencies", "", "requirements.txt", "pandas>=2.0\nnumpy>=1.26\nscipy>=1.11\nscikit-learn>=1.4\ngradio>=4.0", "text"),
   S("Data and a time-based split", """Recommenders must be evaluated on the **future**: train on ratings before a cut-off, test on later ones. Ratings ≥ 8/10 count as 'liked'. Filtering users and movies with few ratings keeps the matrix learnable.""",
     "data.py", '''
from pathlib import Path
import numpy as np, pandas as pd
from scipy import sparse

BASE = "https://raw.githubusercontent.com/sidooms/MovieTweetings/master/latest/"


def _get(name, cols):
    p = Path("data") / name; p.parent.mkdir(exist_ok=True)
    if not p.exists():
        pd.read_csv(BASE + name, sep="::", engine="python", names=cols, encoding="utf-8").to_csv(p, index=False)
    return pd.read_csv(p)


def load(min_user=10, min_item=10):
    r = _get("ratings.dat", ["user", "movie", "rating", "ts"]); m = _get("movies.dat", ["movie", "title", "genres"])
    for _ in range(3):
        r = r[r.groupby("user").user.transform("size") >= min_user]; r = r[r.groupby("movie").movie.transform("size") >= min_item]
    m["genres"] = m["genres"].fillna(""); m = m.drop_duplicates("movie")
    return r.reset_index(drop=True), m[m.movie.isin(r.movie.unique())].reset_index(drop=True)


def split(r, frac=0.85):
    cut = r.ts.quantile(frac); train, test = r[r.ts <= cut], r[r.ts > cut]
    test = test[test.user.isin(train.user) & test.movie.isin(train.movie)]
    return train, test


class Index:
    def __init__(self, train):
        self.users = {u: i for i, u in enumerate(train.user.unique())}; self.items = {m: j for j, m in enumerate(train.movie.unique())}
        self.item_ids = np.array(list(self.items))
    def matrix(self, df, liked_only=False):
        d = df[df.rating >= 8] if liked_only else df
        return sparse.csr_matrix((np.ones(len(d)) if liked_only else d.rating.to_numpy(float), (d.user.map(self.users), d.movie.map(self.items))),
                                 shape=(len(self.users), len(self.items)))
'''),
   S("The models", """All models expose `scores(user_rows) -> matrix` so evaluation is uniform. ItemKNN: cosine similarity between item columns (sparse, top-k neighbours). SVD: factorise the user×item matrix into latent tastes. Content: TF-IDF of genres, so brand-new movies can be recommended (cold start). Hybrid: blend normalised scores.""",
     "models.py", '''
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class Popularity:
    def fit(self, X): self.pop = np.asarray(X.sum(0)).ravel(); return self
    def scores(self, X): return np.tile(self.pop, (X.shape[0], 1))


class ItemKNN:
    def __init__(self, k=50): self.k = k
    def fit(self, X):
        S = (normalize(X.T.tocsr(), axis=1) @ normalize(X.T.tocsr(), axis=1).T).tocsr(); S.setdiag(0); S.eliminate_zeros()
        rows = []
        for i in range(S.shape[0]):                       # keep top-k neighbours per item
            r = S.getrow(i); keep = np.argsort(r.data)[-self.k:]; rows.append(sparse.csr_matrix((r.data[keep], (np.zeros(len(keep)), r.indices[keep])), shape=(1, S.shape[1])))
        self.S = sparse.vstack(rows).tocsr(); return self
    def scores(self, X): return (X @ self.S).toarray()


class SVD:
    def __init__(self, k=64): self.k = k
    def fit(self, X): self.svd = TruncatedSVD(self.k, random_state=0).fit(X); return self
    def scores(self, X): return self.svd.transform(X) @ self.svd.components_


class Content:
    def __init__(self, item_genres): self.G = normalize(TfidfVectorizer(token_pattern=r"[^|]+").fit_transform(item_genres))
    def fit(self, X): return self
    def scores(self, X): return ((normalize(X, axis=1) @ self.G) @ self.G.T).toarray()


class Hybrid:
    def __init__(self, parts, weights): self.parts, self.w = parts, weights
    def fit(self, X):
        for p in self.parts: p.fit(X)
        return self
    def scores(self, X):
        out = 0
        for p, w in zip(self.parts, self.w):
            s = p.scores(X); s = (s - s.mean(1, keepdims=True)) / (s.std(1, keepdims=True) + 1e-9); out = out + w * s
        return out
'''),
   S("Evaluate with ranking metrics", """For each test user, recommend 10 unseen movies and compare with what they actually liked later. NDCG rewards putting hits near the top; coverage shows whether you only recommend blockbusters.""",
     "evaluate.py", '''
import numpy as np
from data import Index, load, split
from models import SVD, Content, Hybrid, ItemKNN, Popularity

r, movies = load(); train, test = split(r); idx = Index(train)
X = idx.matrix(train, liked_only=True); Xall = idx.matrix(train)
liked = test[test.rating >= 8].groupby("user").movie.apply(set)
users = [u for u in liked.index if u in idx.users][:3000]; rows = [idx.users[u] for u in users]
genres = movies.set_index("movie").reindex(idx.item_ids)["genres"].fillna("").tolist()
print(f"train {len(train):,} ratings, {X.shape[0]:,} users x {X.shape[1]:,} movies; evaluating {len(users)} users")


def evaluate(model, k=10):
    S = model.scores(X[rows]); S[Xall[rows].toarray() > 0] = -np.inf           # never recommend already-rated movies
    top = np.argsort(-S, 1)[:, :k]; P = R = N = 0; shown = set()
    for u, t in zip(users, top):
        rec = idx.item_ids[t]; shown.update(rec); hits = [m in liked[u] for m in rec]
        P += sum(hits) / k; R += sum(hits) / len(liked[u])
        dcg = sum(h / np.log2(i + 2) for i, h in enumerate(hits)); ideal = sum(1 / np.log2(i + 2) for i in range(min(k, len(liked[u])))); N += dcg / ideal
    n = len(users); return P / n, R / n, N / n, len(shown) / X.shape[1]


models = {"popularity": Popularity(), "item-kNN": ItemKNN(50), "SVD (64 factors)": SVD(64), "content (genres)": Content(genres),
          "hybrid": Hybrid([SVD(64), ItemKNN(50), Popularity()], [0.6, 0.3, 0.1])}
for name, m in models.items():
    p, rc, nd, cov = evaluate(m.fit(X)); print(f"{name:17s} precision@10 {p:.4f}  recall@10 {rc:.4f}  NDCG@10 {nd:.4f}  coverage {cov:.3f}")
'''),
   S("Recommendation app", """Users pick movies they like; we build a one-row 'user vector' and score it with the fitted models — this also solves the cold-start problem for new users.""",
     "app.py", '''
import gradio as gr, numpy as np
from scipy import sparse
from data import Index, load
from models import Hybrid, ItemKNN, Popularity

r, movies = load(); idx = Index(r); X = idx.matrix(r, liked_only=True)
model = Hybrid([ItemKNN(50), Popularity()], [0.85, 0.15]).fit(X)
title = movies.set_index("movie")["title"]; choices = [title[m] for m in idx.item_ids if m in title.index]
to_id = {title[m]: m for m in idx.item_ids if m in title.index}


def recommend(picks):
    v = sparse.csr_matrix((np.ones(len(picks)), (np.zeros(len(picks)), [idx.items[to_id[p]] for p in picks])), shape=(1, X.shape[1]))
    s = model.scores(v)[0]; s[v.indices] = -np.inf
    return "\\n".join(title.get(m, str(m)) for m in idx.item_ids[np.argsort(-s)[:10]])


gr.Interface(recommend, gr.Dropdown(choices, multiselect=True, label="Movies you liked"), gr.Textbox(lines=10, label="You might like")).launch()
'''),
   S("Run it", "", None, "python evaluate.py      # ~3 minutes the first time (download)\npython app.py           # opens a local web app", "bash"),
  ],
  check=["python evaluate.py"],
  talk=["Why a time-based split and ranking metrics (precision@k, NDCG) instead of RMSE on ratings.", "Popularity is a strong baseline; personalised models win on NDCG and coverage.",
        "Cold start: the content model and the 'pick a few movies' vector handle new users/items.", "At scale: two-tower retrieval + ANN index + ranker (link to the system-design tab)."],
  errors=[("ParserError with '::' separator", "use engine='python' in read_csv"), ("MemoryError building similarities", "keep matrices sparse and keep only top-k neighbours")],
  extend=["Implicit ALS (`implicit` library)", "Two-tower model in PyTorch with FAISS retrieval", "LLM-generated explanations: 'because you liked …'"],
  see=["m-recsys", "m-lin-transform", "m-vectors", "m-text-representation", "m-metrics-clf"])

PROJECTS_1 = [P1, P2, P3, P4, P5, P6, P7]
