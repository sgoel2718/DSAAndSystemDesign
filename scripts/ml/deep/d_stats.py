"""Deep layer + end-to-end walkthroughs: Probability & statistics."""
from deep.util import X

TITANIC = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
TIPS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
PENGUINS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
DIAMONDS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv"
PIMA = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
PIMA_COLS = ["pregnancies", "glucose", "bp", "skin", "insulin", "bmi", "pedigree", "age", "diabetes"]
SMS = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
BIRTHS = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-total-female-births.csv"

X("m-prob-basics",
  "Probability is a number between 0 and 1 measuring how often something happens in the long run (frequentist) or how strongly you believe it (Bayesian). Every ML classifier outputs probabilities, every evaluation is an estimate from a sample, so you need to read these numbers correctly.",
  """**Axioms (Kolmogorov).** P(A) ≥ 0; P(Ω) = 1; for disjoint events P(A ∪ B) = P(A) + P(B). Everything else is derived: P(not A) = 1 − P(A); P(A ∪ B) = P(A) + P(B) − P(A ∩ B) (inclusion–exclusion, so the overlap isn't counted twice). **Law of large numbers:** the empirical frequency k/n converges to the true p as n grows; its error shrinks like √(p(1−p)/n) — 4× the data halves the error.""",
  """**Titanic by hand.** 891 passengers, 342 survived → P(survive) = 342/891 = **0.384**. 314 were female, 233 of whom survived → P(female ∩ survive) = 233/891 = 0.262. P(female ∪ survive) = 314/891 + 0.384 − 0.262 = 0.352 + 0.384 − 0.262 = **0.474**. Standard error of 0.384 with n = 891: √(0.384·0.616/891) ≈ **0.016**.""",
  ["Adding probabilities of overlapping events", "Treating a frequency from 20 samples as exact", "Confusing odds (p/(1−p)) with probability", "Gambler's fallacy — independent trials have no memory"],
  ["Estimating rates, reading model probabilities, simulating uncertainty"], ["Treating a model's raw score as a calibrated probability without checking"],
  "Titanic passengers — estimate probabilities from frequencies, verify the axioms empirically, and watch the law of large numbers by simulation.",
  ["Load data and compute basic event probabilities", "Check complement and union rules on real counts", "Compute standard errors", "Simulate sampling to see the law of large numbers", "Report probabilities with uncertainty"],
  f'''
import numpy as np, pandas as pd
df = pd.read_csv("{TITANIC}"); n = len(df)
S, F = df.Survived == 1, df.Sex == "female"
p = lambda m: m.mean()
print(f"P(survive)={{p(S):.3f}}  P(female)={{p(F):.3f}}  P(F∩S)={{p(F & S):.3f}}")
print(f"union rule: P(F∪S)={{p(F | S):.3f}} vs P(F)+P(S)-P(F∩S)={{p(F) + p(S) - p(F & S):.3f}}")
print(f"complement: P(not S)={{p(~S):.3f}} = 1-P(S)={{1 - p(S):.3f}}")
se = np.sqrt(p(S) * (1 - p(S)) / n); print(f"P(survive) = {{p(S):.3f}} ± {{1.96 * se:.3f}} (95%)")
rng = np.random.default_rng(0)
for k in [10, 100, 1000, 10000]:
    est = [df.Survived.sample(k, replace=True, random_state=int(rng.integers(1e9))).mean() for _ in range(200)]
    print(f"  sample size {{k:5d}}: estimates spread ±{{np.std(est):.3f}} (theory {{np.sqrt(p(S) * (1 - p(S)) / k):.3f}})")
''')

X("m-prob-events",
  "Conditional probability P(A|B) asks: *among cases where B happened, how often does A happen?* It's the core of every prediction — a classifier estimates P(class | features). Independence means knowing B tells you nothing about A.",
  """**Definitions.** P(A|B) = P(A ∩ B)/P(B). Rearranged: **product rule** P(A ∩ B) = P(A|B)·P(B). **Independence:** P(A ∩ B) = P(A)·P(B) ⇔ P(A|B) = P(A). **Law of total probability:** P(A) = Σᵢ P(A|Bᵢ)·P(Bᵢ) over a partition Bᵢ. **Simpson's paradox:** a trend in every subgroup can reverse when groups are pooled, if group sizes differ — always check confounders.""",
  """**Titanic.** P(survive | female) = 233/314 = **0.742**; P(survive | male) = 109/577 = **0.189**. Not independent (0.742 ≠ 0.384). Total probability: 0.742·(314/891) + 0.189·(577/891) = 0.261 + 0.122 = **0.384** = P(survive) ✓.""",
  ["Confusing P(A|B) with P(B|A) (prosecutor's fallacy)", "Assuming independence without checking", "Ignoring confounders (Simpson's paradox)"],
  ["Segment analysis, feature relevance, building naive Bayes"], ["Concluding causation from a conditional probability"],
  "Titanic — conditional tables, independence check, total probability, and a Simpson's-paradox style reversal by class.",
  ["Compute P(survive | each group)", "Test independence numerically and with chi-square", "Verify the law of total probability", "Look for a confounder (class vs fare)", "Summarise what's dependent on what"],
  f'''
import pandas as pd
from scipy.stats import chi2_contingency
df = pd.read_csv("{TITANIC}")
cond = df.groupby("Sex")["Survived"].mean(); prior = df["Sex"].value_counts(normalize=True)
print("P(survive | sex):", cond.round(3).to_dict())
print("total probability:", round((cond * prior).sum(), 3), "== P(survive):", round(df.Survived.mean(), 3))
tab = pd.crosstab(df.Sex, df.Survived); chi2, pval, _, expected = chi2_contingency(tab)
print("observed vs expected-if-independent:\\n", tab.values, "\\n", expected.round(0), f"\\nchi2 p-value = {{pval:.1e}} -> dependent")
df["Port"] = df["Embarked"].fillna("S")
print("P(survive | port):", df.groupby("Port").Survived.mean().round(2).to_dict())
print("...but within each class the port effect shrinks (class is a confounder):")
print(pd.crosstab([df.Pclass], df.Port, values=df.Survived, aggfunc="mean").round(2))
print("share of 1st class by port:", df.groupby("Port").Pclass.apply(lambda s: (s == 1).mean()).round(2).to_dict())
''')

X("m-bayes",
  "Bayes' theorem flips a conditional: from *how likely is the evidence if the hypothesis is true* to *how likely is the hypothesis given the evidence*. It is how spam filters, medical tests and Bayesian models update beliefs — and why rare events produce many false alarms.",
  """**Derivation.** From the product rule twice: P(H ∩ E) = P(E|H)P(H) = P(H|E)P(E) ⇒ **P(H|E) = P(E|H)·P(H)/P(E)**, with P(E) = P(E|H)P(H) + P(E|¬H)P(¬H). Posterior ∝ likelihood × prior. **Naive Bayes** assumes features are independent given the class: P(c|x₁..xₙ) ∝ P(c)·Πᵢ P(xᵢ|c); use log-probabilities to avoid underflow and **Laplace smoothing** (count+1) so unseen words don't zero the product.""",
  """**Disease test.** Prevalence 1%, sensitivity 99%, false-positive rate 5%. P(+) = 0.99·0.01 + 0.05·0.99 = 0.0099 + 0.0495 = 0.0594. P(disease | +) = 0.0099/0.0594 = **16.7%** — most positives are false because the disease is rare. **Spam word:** P("free"|spam)=0.2, P("free"|ham)=0.01, P(spam)=0.13 → posterior = 0.026/(0.026+0.0087) = **0.75**.""",
  ["Ignoring the base rate (prior)", "Multiplying raw probabilities (underflow) instead of summing logs", "No smoothing → zero probabilities for unseen words", "Believing naive Bayes probabilities are calibrated"],
  ["Text classification baselines, diagnostic reasoning, updating beliefs with data"], ["Strongly correlated features where the independence assumption badly distorts probabilities"],
  "SMS Spam Collection — write multinomial naive Bayes from scratch with Bayes' rule, compare with scikit-learn, and work a medical-test example.",
  ["Load and split messages", "Count words per class (likelihoods with Laplace smoothing)", "Classify with log prior + Σ log likelihood", "Compare with sklearn MultinomialNB", "Inspect posterior for an example message"],
  f'''
import re, numpy as np, pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
df = pd.read_csv("{SMS}", sep="\\t", names=["label", "text"])
tr, te = train_test_split(df, test_size=0.25, stratify=df.label, random_state=0)
tok = lambda s: re.findall(r"[a-z0-9']+", s.lower())
counts = {{c: Counter(w for t in tr[tr.label == c].text for w in tok(t)) for c in ["ham", "spam"]}}
vocab = set(counts["ham"]) | set(counts["spam"]); V = len(vocab)
logprior = {{c: np.log((tr.label == c).mean()) for c in counts}}
total = {{c: sum(counts[c].values()) for c in counts}}
def loglik(w, c): return np.log((counts[c][w] + 1) / (total[c] + V))      # Laplace smoothing
def posterior(text):
    s = {{c: logprior[c] + sum(loglik(w, c) for w in tok(text) if w in vocab) for c in counts}}
    m = max(s.values()); e = {{c: np.exp(v - m) for c, v in s.items()}}; z = sum(e.values()); return {{c: e[c] / z for c in e}}
pred = [max(posterior(t), key=posterior(t).get) for t in te.text]
print("from-scratch NB accuracy:", round((np.array(pred) == te.label.values).mean(), 4))
vec = CountVectorizer(token_pattern=r"[a-z0-9']+"); nb = MultinomialNB().fit(vec.fit_transform(tr.text), tr.label)
print("sklearn MultinomialNB accuracy:", round(nb.score(vec.transform(te.text), te.label), 4))
print("P(spam | 'WIN a FREE prize now, call 0800'):", round(posterior("WIN a FREE prize now, call 0800")["spam"], 4))
prev, sens, fpr = 0.01, 0.99, 0.05
print(f"medical test: P(disease | +) = {{sens * prev / (sens * prev + fpr * (1 - prev)):.3f}}")
''')

X("m-random-variables",
  "A random variable assigns a number to each outcome (number of clicks, a house price). Its **expectation** is the long-run average and its **variance** the typical squared deviation. Losses, risks and model predictions are all expectations of random variables.",
  """**Definitions.** Discrete: E[X] = Σ x·p(x); continuous: E[X] = ∫ x f(x) dx. Var(X) = E[(X − μ)²] = E[X²] − μ². **Linearity:** E[aX + bY] = aE[X] + bE[Y] always; Var(aX + b) = a²Var(X); Var(X + Y) = Var X + Var Y + 2Cov(X, Y) (independent ⇒ Cov = 0). **Sum of n i.i.d. variables:** mean nμ, variance nσ² ⇒ the average has variance σ²/n — the basis of standard errors. **Central limit theorem:** that average is approximately Normal for large n, whatever the original distribution.""",
  """**Die.** E[X] = (1+…+6)/6 = 3.5; E[X²] = 91/6 = 15.17; Var = 15.17 − 12.25 = **2.92**. Two dice: E = 7, Var = 5.83. **Expected value of a bet:** win ₹100 with p = 0.3, lose ₹40 otherwise → E = 0.3·100 − 0.7·40 = **₹2** per bet.""",
  ["Var(X + Y) = Var X + Var Y when X, Y are correlated", "E[f(X)] ≠ f(E[X]) for non-linear f (Jensen)", "Using the mean of a heavy-tailed variable as 'typical'"],
  ["Expected cost/profit, risk, understanding losses and averages"], ["Heavy-tailed data where the mean is dominated by rare extremes — report medians/quantiles"],
  "Restaurant tips (244 bills) — treat tip % and party size as random variables: expectations, variances, linearity, and a CLT simulation.",
  ["Estimate the distribution of party size (discrete RV)", "Compute E, Var by formula and compare with pandas", "Check linearity of expectation and the Var(X+Y) rule", "Simulate the CLT for the mean tip", "Compute an expected value for a decision"],
  f'''
import numpy as np, pandas as pd
df = pd.read_csv("{TIPS}"); df["pct"] = df.tip / df.total_bill
pmf = df["size"].value_counts(normalize=True).sort_index()
E = (pmf.index * pmf).sum(); Var = ((pmf.index - E) ** 2 * pmf).sum()
print("P(size):", pmf.round(3).to_dict()); print(f"E[size]={{E:.3f}} Var={{Var:.3f}} (pandas: {{df['size'].mean():.3f}}, {{df['size'].var(ddof=0):.3f}})")
X1, X2 = df.total_bill, df.tip
print(f"E[bill+tip]={{(X1 + X2).mean():.2f}} = E[bill]+E[tip]={{X1.mean() + X2.mean():.2f}}")
print(f"Var(bill+tip)={{(X1 + X2).var():.1f}} vs Var+Var={{X1.var() + X2.var():.1f}} vs +2Cov={{X1.var() + X2.var() + 2 * X1.cov(X2):.1f}}")
rng = np.random.default_rng(0)
for n in [1, 5, 30]:
    means = rng.choice(df.pct.to_numpy(), size=(5000, n)).mean(1)
    print(f"  mean of {{n:2d}} tips: sd {{means.std():.4f}} (theory {{df.pct.std(ddof=0) / np.sqrt(n):.4f}}), skew {{pd.Series(means).skew():.2f}}")
print(f"expected tip revenue for 40 tables/night: ₹{{40 * df.tip.mean() * 80:.0f}} ± {{np.sqrt(40) * df.tip.std() * 80:.0f}} (tip in $→₹80)")
''')

X("m-distributions",
  "A distribution is the 'shape' of randomness. A few families cover most real data: **Bernoulli/Binomial** (yes/no counts), **Poisson** (event counts per interval), **Normal** (sums of many effects), **Exponential** (waiting times), **Uniform**, **log-normal/power-law** (incomes, prices). Picking the right one guides loss functions, simulations and tests.",
  """**Key facts.** Binomial(n, p): mean np, var np(1−p). Poisson(λ): P(k) = λᵏe^(−λ)/k!, mean = var = λ (overdispersion if var ≫ mean → negative binomial). Normal(μ, σ²): 68/95/99.7% within 1/2/3σ. Exponential(λ): memoryless, mean 1/λ. **Maximum likelihood fit:** choose parameters maximising Π f(xᵢ); for the Normal this gives μ̂ = mean, σ̂² = mean squared deviation; for Poisson λ̂ = mean. Check fit with a Q–Q plot or a KS test.""",
  """**Poisson by hand.** Average 42 births/day. P(exactly 42) = 42⁴²e⁻⁴²/42! ≈ **0.061**. Observed variance ≈ 54 vs mean 42 → mild overdispersion. **Normal:** mean 42, sd 7.3 → P(> 56.6) = P(Z > 2) ≈ **2.3%**.""",
  ["Assuming Normality for counts or skewed money data", "Using a Normal for bounded data near the bound", "Ignoring overdispersion in Poisson data"],
  ["Simulation, choosing losses (MSE↔Normal, Poisson loss↔counts), anomaly thresholds"], ["Forcing a parametric fit when the data is clearly multi-modal — use mixtures or non-parametric methods"],
  "Daily female births in California (1959, 365 days) and diamond prices (53,940) — fit Poisson, Normal and log-normal by maximum likelihood and test the fits.",
  ["Load counts and prices", "Fit Poisson and Normal to daily births; compare mean vs variance", "KS-test the fits", "Show prices are log-normal-ish (log transform)", "Use a fitted distribution to set an anomaly threshold"],
  f'''
import numpy as np, pandas as pd
from scipy import stats
births = pd.read_csv("{BIRTHS}")["Births"].to_numpy()
lam = births.mean(); print(f"births/day: mean {{lam:.1f}}, var {{births.var():.1f}} -> dispersion ratio {{births.var() / lam:.2f}}")
mu, sd = stats.norm.fit(births)
print("KS Normal p =", round(stats.kstest(births, stats.norm(mu, sd).cdf).pvalue, 3))
obs = np.bincount(births, minlength=80)[20:70]; exp = stats.poisson.pmf(np.arange(20, 70), lam) * len(births)
print("Poisson vs observed counts (35-49):", list(zip(range(35, 50, 3), obs[15:30:3].tolist(), exp[15:30:3].round(1).tolist())))
print(f"P(>= 60 births) Normal {{stats.norm.sf(59.5, mu, sd):.4f}}, Poisson {{stats.poisson.sf(59, lam):.4f}}, observed {{(births >= 60).mean():.4f}}")
price = pd.read_csv("{DIAMONDS}")["price"].to_numpy()
print(f"price skew {{stats.skew(price):.2f}} -> log-price skew {{stats.skew(np.log(price)):.2f}}")
shape, loc, scale = stats.lognorm.fit(price, floc=0)
print(f"lognormal median ${{scale:.0f}} (actual {{np.median(price):.0f}}); 99th pct threshold ${{stats.lognorm.ppf(0.99, shape, loc, scale):.0f}} (actual {{np.percentile(price, 99):.0f}}) -> fitted tail too heavy: check fits at the quantiles you care about")
''')

X("m-pdf-cdf",
  "For a continuous variable, the **PDF** is a density curve (height = how concentrated values are near x), the **CDF** gives P(X ≤ x), and its inverse — the **quantile function** — gives percentiles. Thresholds, p-values, percentiles and calibration all live on the CDF.",
  """**Relations.** F(x) = ∫₋∞ˣ f(t)dt, f = F′. P(a < X ≤ b) = F(b) − F(a). A PDF can exceed 1 (it's a density, not a probability); only areas are probabilities. **Empirical CDF** F̂(x) = (#xᵢ ≤ x)/n — no assumptions, converges uniformly (Glivenko–Cantelli). **Probability integral transform:** F(X) ~ Uniform(0, 1); inverse-transform sampling draws X = F⁻¹(U). **KDE:** f̂(x) = (1/nh) Σ K((x − xᵢ)/h) — the bandwidth h trades bias vs variance.""",
  """**Standard normal.** F(1.96) = 0.975 ⇒ P(−1.96 < Z < 1.96) = 0.95. Exponential with mean 2 min: F(x) = 1 − e^(−x/2) → P(wait ≤ 3) = 1 − e^(−1.5) = **0.777**; median = F⁻¹(0.5) = 2 ln 2 = **1.39 min**. A density of 2.5 at x is fine if the variable lives on a narrow range (Uniform(0, 0.4) has density 2.5).""",
  ["Reading a PDF height as a probability", "Too small/large KDE bandwidth", "Using a fitted parametric CDF when the ECDF disagrees"],
  ["Percentiles, thresholds, sampling, comparing distributions (KS)"], ["Discrete data — use a PMF"],
  "Penguins body mass — histogram vs KDE vs fitted Normal PDF, empirical CDF and quantiles, inverse-transform sampling, and a KS comparison between species.",
  ["Load body mass", "Estimate PDF with histogram and KDE (two bandwidths)", "Build the empirical CDF and read percentiles", "Sample new values by inverse transform", "Compare two species' CDFs with the KS test"],
  f'''
import numpy as np, pandas as pd
from scipy import stats
df = pd.read_csv("{PENGUINS}").dropna(); m = df.body_mass_g.to_numpy()
hist, edges = np.histogram(m, bins=20, density=True)
print("histogram density integrates to", round((hist * np.diff(edges)).sum(), 3))
for bw in [0.1, 0.5]:
    kde = stats.gaussian_kde(m, bw_method=bw); grid = np.linspace(2500, 6500, 9)
    print(f"KDE bw={{bw}}:", (kde(grid) * 1e4).round(2))
ecdf = lambda x: (m <= x).mean()
print(f"ECDF: P(mass <= 4000g) = {{ecdf(4000):.3f}}; Normal fit says {{stats.norm.cdf(4000, m.mean(), m.std()):.3f}}")
print("quantiles 10/50/90%:", np.quantile(m, [0.1, 0.5, 0.9]))
u = np.random.default_rng(0).uniform(size=2000); samples = np.quantile(m, u)       # inverse-transform sampling
print("resampled mean/sd:", round(samples.mean()), round(samples.std()), "vs", round(m.mean()), round(m.std()))
a, g = df[df.species == "Adelie"].body_mass_g, df[df.species == "Gentoo"].body_mass_g
ks = stats.ks_2samp(a, g); print(f"KS Adelie vs Gentoo: D={{ks.statistic:.2f}}, p={{ks.pvalue:.1e}}")
''')

X("m-centre-spread",
  "Summaries compress a column into a few numbers: where it sits (**mean, median, mode**) and how much it varies (**variance, std, IQR, range**), plus its shape (**skewness, kurtosis**). Choosing robust summaries protects you from outliers and wrong conclusions.",
  """**Formulas.** Mean x̄ = Σxᵢ/n minimises squared error; median minimises absolute error (so MSE regression predicts conditional means, MAE regression conditional medians). Sample variance s² = Σ(xᵢ − x̄)²/(n − 1) — dividing by n−1 (Bessel) makes it unbiased because x̄ is itself fitted. IQR = Q3 − Q1; Tukey outliers lie beyond 1.5·IQR. **Robustness:** one huge value can move the mean arbitrarily (breakdown point 0%), the median needs half the data corrupted (50%). MAD = median|xᵢ − median| × 1.4826 estimates σ robustly.""",
  """**By hand.** Salaries (₹ lakh): 4, 5, 5, 6, 50. Mean = 70/5 = **14**; median = **5**; mode 5. Deviations from the mean: −10, −9, −9, −8, 36 → s² = (100+81+81+64+1296)/4 = **405.5**, s ≈ 20.1. Q1 = 5, Q3 = 6, IQR = 1 → upper fence 7.5 → 50 is an outlier. The median describes the 'typical' employee; the mean doesn't.""",
  ["Reporting the mean for skewed data", "Using population vs sample variance inconsistently", "Deleting 'outliers' that are real", "Comparing spreads of variables with different units (use CV or standardise)"],
  ["EDA summaries, robust scaling, outlier rules"], ["Summary statistics alone — always also plot (Anscombe's quartet)"],
  "Diamonds (53,940 prices) — centre, spread and shape by cut; robust vs non-robust statistics with and without injected outliers; Anscombe's quartet reminder.",
  ["Describe price overall", "Compare mean vs median and std vs IQR/MAD per group", "Inject outliers and measure each statistic's sensitivity", "Flag Tukey outliers", "Show identical summaries with different shapes (Anscombe)"],
  f'''
import numpy as np, pandas as pd
from scipy import stats
df = pd.read_csv("{DIAMONDS}"); p = df.price
print(f"mean {{p.mean():.0f}} median {{p.median():.0f}} | std {{p.std():.0f}} IQR {{p.quantile(.75) - p.quantile(.25):.0f}} MAD {{stats.median_abs_deviation(p, scale='normal'):.0f}} | skew {{p.skew():.2f}} kurt {{p.kurt():.2f}}")
print(df.groupby("cut").price.agg(["mean", "median", "std"]).round(0))
q1, q3 = p.quantile([.25, .75]); out = p[(p < q1 - 1.5 * (q3 - q1)) | (p > q3 + 1.5 * (q3 - q1))]
print(f"Tukey outliers: {{len(out)}} ({{len(out) / len(p):.1%}}) above ${{q3 + 1.5 * (q3 - q1):.0f}}")
sample = p.sample(200, random_state=0).to_numpy(); bad = np.append(sample, [1e6, 2e6])
for name, f in [("mean", np.mean), ("median", np.median), ("std", np.std), ("MAD", lambda x: stats.median_abs_deviation(x, scale="normal"))]:
    print(f"  {{name:6s}} clean {{f(sample):10.0f}} | with 2 bad rows {{f(bad):10.0f}}")
ans = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/anscombe.csv")
print(ans.groupby("dataset").agg(x_mean=("x", "mean"), y_mean=("y", "mean"), y_std=("y", "std")).round(2), "\\n-> same numbers, totally different plots")
''')

X("m-normalization",
  "Features measured in different units (kg vs mm) dominate distance- and gradient-based models unequally. **Scaling** puts them on comparable ranges: standardisation (z-scores), min–max, robust scaling, and non-linear transforms (log, Box-Cox/Yeo-Johnson, quantile) that also fix skew.",
  """**Formulas.** z = (x − μ)/σ (mean 0, sd 1). Min–max: (x − min)/(max − min) ∈ [0, 1] — sensitive to outliers. Robust: (x − median)/IQR. Box-Cox: (x^λ − 1)/λ (x > 0), λ chosen by maximum likelihood to make data most Normal; λ = 0 is log. **Why it matters:** in gradient descent, the loss contours of unscaled features are elongated ellipses, so steps zig-zag; scaling makes them rounder and convergence faster (condition number drops). Tree models are invariant to monotonic transforms — no scaling needed. **Always fit scalers on training data only.**""",
  """**By hand.** Heights 150, 160, 170 cm: μ = 160, σ = 8.16 → z = −1.22, 0, 1.22. Min–max → 0, 0.5, 1. Add an outlier 300: min–max now maps 150..170 into 0..0.13 (squashed), while robust scaling keeps them spread.""",
  ["Fitting the scaler on all data (leakage)", "Scaling the target and forgetting to invert predictions", "Min–max scaling with outliers", "Scaling one-hot/binary columns unnecessarily"],
  ["kNN, SVM, PCA, linear/logistic regression with regularisation, neural networks"], ["Tree ensembles (no effect)"],
  "Pima diabetes (768 patients, real clinical measurements) — compare no scaling vs standard/min–max/robust/quantile for kNN and logistic regression, inside leak-free pipelines.",
  ["Load and inspect feature ranges", "Build pipelines with each scaler", "Cross-validate kNN and logistic regression", "Check convergence speed of gradient-based models", "Show trees don't care"],
  f'''
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, MinMaxScaler, PowerTransformer, QuantileTransformer, RobustScaler, StandardScaler
from sklearn.tree import DecisionTreeClassifier
df = pd.read_csv("{PIMA}", names={PIMA_COLS}); X, y = df.drop(columns="diabetes"), df.diabetes
print("feature ranges:", (X.max() - X.min()).round(0).to_dict())
scalers = {{"none": FunctionTransformer(), "standard": StandardScaler(), "minmax": MinMaxScaler(), "robust": RobustScaler(),
           "yeo-johnson": PowerTransformer(), "quantile": QuantileTransformer(n_quantiles=200, output_distribution="normal")}}
for name, sc in scalers.items():
    knn = cross_val_score(make_pipeline(sc, KNeighborsClassifier(15)), X, y, cv=5).mean()
    lr = make_pipeline(sc, LogisticRegression(max_iter=5000)).fit(X, y)
    tree = cross_val_score(make_pipeline(sc, DecisionTreeClassifier(max_depth=4, random_state=0)), X, y, cv=5).mean()
    print(f"  {{name:12s}} kNN {{knn:.3f}} | logistic iterations {{lr[-1].n_iter_[0]:4d}} | tree {{tree:.3f}}")
''')

X("m-sampling-ci",
  "We almost never see the whole population, only a sample. **Sampling distributions** tell us how much an estimate would wobble across samples; a **confidence interval** turns that wobble into a range that captures the true value 95% of the time. Every model metric you report should come with one.",
  """**Theory.** Standard error of a mean: SE = s/√n. By the CLT, x̄ ± t₀.₉₇₅,ₙ₋₁·SE is a 95% CI. For a proportion: p̂ ± 1.96√(p̂(1−p̂)/n) (use Wilson for small n or p near 0/1). **Bootstrap:** resample the data with replacement B times, recompute the statistic, take the 2.5–97.5% percentiles — works for medians, AUC, any metric. **Interpretation:** the *procedure* captures the truth 95% of the time; it's not '95% probability the true value is in this particular interval' (that's a Bayesian credible interval). Sampling bias (who got sampled) is not fixed by bigger n.""",
  """**Accuracy CI.** A model gets 850/1000 test cases right: p̂ = 0.85, SE = √(0.85·0.15/1000) = 0.0113 → CI = 0.85 ± 0.022 = **[0.828, 0.872]**. Another model at 0.86 on the same test set is *not* clearly better. Halving the CI width needs 4× the test data.""",
  ["Reporting a single test score with no interval", "Thinking more data fixes biased sampling", "Bootstrapping time series i.i.d. (breaks dependence — use block bootstrap)", "Overlapping CIs ≠ no significant difference (use a paired test)"],
  ["Reporting metrics, A/B results, survey estimates"], ["Very small samples with heavy tails — intervals will be unreliable"],
  "Pima diabetes — CI for mean glucose (t-formula vs bootstrap), CI for a model's test accuracy and AUC by bootstrap, and a coverage simulation showing what '95%' means.",
  ["t-interval for a mean", "Bootstrap CI for the median and the mean", "Train a model and bootstrap its test AUC", "Simulate coverage of 95% intervals", "Report results with intervals"],
  f'''
import numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
df = pd.read_csv("{PIMA}", names={PIMA_COLS}); g = df.glucose[df.glucose > 0].to_numpy(); rng = np.random.default_rng(0)
print("t 95% CI mean glucose:", np.round(stats.t.interval(0.95, len(g) - 1, g.mean(), stats.sem(g)), 1))
boot = rng.choice(g, (5000, len(g)))
print("bootstrap CI mean:", np.percentile(boot.mean(1), [2.5, 97.5]).round(1), "| median:", np.percentile(np.median(boot, 1), [2.5, 97.5]))
Xtr, Xte, ytr, yte = train_test_split(df.drop(columns="diabetes"), df.diabetes, test_size=0.3, random_state=0, stratify=df.diabetes)
p = LogisticRegression(max_iter=5000).fit(Xtr, ytr).predict_proba(Xte)[:, 1]; yte = yte.to_numpy()
aucs = [roc_auc_score(yte[i], p[i]) for i in (rng.integers(0, len(yte), len(yte)) for _ in range(2000))]
print(f"test AUC {{roc_auc_score(yte, p):.3f}}, 95% bootstrap CI [{{np.percentile(aucs, 2.5):.3f}}, {{np.percentile(aucs, 97.5):.3f}}]")
hits = 0
for _ in range(2000):
    s = rng.choice(g, 40); lo, hi = stats.t.interval(0.95, 39, s.mean(), stats.sem(s)); hits += lo <= g.mean() <= hi
print(f"coverage of 95% intervals from samples of 40: {{hits / 2000:.1%}}")
''')

X("m-hypothesis",
  "A hypothesis test asks: *if there were really no effect, how surprising would data like mine be?* That surprise is the **p-value**. Tests decide whether an A/B change, a new feature or a better model is real or noise — when used with effect sizes and power, not alone.",
  """**Recipe.** H₀ (no effect) vs H₁. Choose a statistic whose distribution under H₀ is known: two-sample t = (x̄₁ − x̄₂)/√(s₁²/n₁ + s₂²/n₂) (Welch); chi-square for counts; Mann–Whitney for ranks; permutation tests for anything (shuffle labels, recompute). p = P(statistic at least this extreme | H₀). Reject if p < α (Type I error rate). **Power** = 1 − β = P(reject | real effect) — depends on effect size, n, α. Required n per group ≈ 2(z₁₋α/₂ + z₁₋β)²σ²/δ². **Multiple testing:** 20 tests at α = 0.05 give ~1 false positive — use Bonferroni/Holm or FDR (Benjamini–Hochberg).""",
  """**Sample size by hand.** Detect a 2-point difference (δ = 2) in a metric with σ = 10, α = 0.05, power 80%: n = 2(1.96 + 0.84)²·100/4 = 2·7.84·25 = **392 per group**. **t by hand:** means 5.2 vs 4.8, s = 1, n = 50 each → SE = √(1/50 + 1/50) = 0.2 → t = 2.0 → p ≈ 0.048.""",
  ["p-value = probability H₀ is true (it isn't)", "Peeking and stopping when p < 0.05", "Testing many things and reporting the winners", "Statistically significant ≠ practically important — report effect sizes and CIs"],
  ["A/B tests, comparing models, feature effects"], ["Huge n where everything is 'significant' — focus on effect size"],
  "Tips dataset — do smokers tip differently? Welch t-test, Mann–Whitney, a permutation test by hand, chi-square for day vs time, effect size, power and multiple-testing correction.",
  ["State H₀/H₁ and compute the observed difference", "Welch t-test and Mann–Whitney", "Permutation test from scratch", "Effect size (Cohen's d) and power / required n", "Multiple comparisons across days with Holm correction"],
  f'''
import numpy as np, pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import TTestIndPower
df = pd.read_csv("{TIPS}"); df["pct"] = df.tip / df.total_bill
a, b = df[df.smoker == "Yes"].pct.to_numpy(), df[df.smoker == "No"].pct.to_numpy(); obs = a.mean() - b.mean()
print(f"smoker - non-smoker tip%: {{obs:+.4f}}")
print("Welch t-test p =", round(stats.ttest_ind(a, b, equal_var=False).pvalue, 3), "| Mann-Whitney p =", round(stats.mannwhitneyu(a, b).pvalue, 3))
rng = np.random.default_rng(0); pooled = np.concatenate([a, b]); null = []
for _ in range(10000):
    rng.shuffle(pooled); null.append(pooled[:len(a)].mean() - pooled[len(a):].mean())
print("permutation p =", round((np.abs(null) >= abs(obs)).mean(), 3))
d = obs / np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
print(f"Cohen's d = {{d:.2f}} | power now = {{TTestIndPower().power(d, nobs1=len(a), ratio=len(b) / len(a), alpha=0.05):.2f}} | n/group for 80% power = {{TTestIndPower().solve_power(abs(d), power=0.8, alpha=0.05):.0f}}")
print("chi-square day x time p =", f"{{stats.chi2_contingency(pd.crosstab(df.day, df.time))[1]:.1e}}")
days = df.day.unique(); pvals = [stats.ttest_ind(df[df.day == d].pct, df[df.day != d].pct, equal_var=False).pvalue for d in days]
print("day-vs-rest p (raw → Holm):", {{d: (round(float(p), 3), round(float(q), 3)) for d, p, q in zip(days, pvals, multipletests(pvals, method="holm")[1])}})
''')

X("m-correlation",
  "Correlation measures how strongly two variables move together. **Pearson** captures linear association, **Spearman** monotonic (rank) association, and **mutual information** any dependence. Correlation is the first screen for features and multicollinearity — and the classic trap for causal claims.",
  """**Formulas.** Cov(X, Y) = E[(X − μx)(Y − μy)]; Pearson r = Cov/(σxσy) ∈ [−1, 1]; r² = fraction of variance explained by a linear fit. Spearman ρ = Pearson on ranks (robust to outliers, catches any monotonic curve). Test H₀: ρ = 0 with t = r√(n−2)/√(1−r²). **r = 0 does not mean independent** (y = x² on symmetric x has r ≈ 0). **Confounding:** a third variable can create correlation; partial correlation controls for it by correlating residuals. Multicollinearity inflates coefficient variance: VIF = 1/(1 − R²ⱼ) (> 5–10 is a warning).""",
  """**By hand.** x = 1, 2, 3; y = 2, 4, 5. x̄ = 2, ȳ = 3.67. Products of deviations: (−1)(−1.67) + 0 + (1)(1.33) = 3.0. Σ(x−x̄)² = 2, Σ(y−ȳ)² = 2.78+0.11+1.78 = 4.67. r = 3/√(2·4.67) = 3/3.06 = **0.98**.""",
  ["Correlation ⇒ causation", "Pearson on non-linear/monotonic relations", "Ignoring outliers that drive r", "Dropping features only because they're weakly correlated with the target (interactions)"],
  ["Feature screening, multicollinearity checks, EDA"], ["Categorical variables — use Cramér's V / mutual information"],
  "Diamonds and MPG — Pearson vs Spearman vs mutual information, a confounder (carat drives both price and 'worse' cut), partial correlation and VIF.",
  ["Correlation matrix of numeric features", "Pearson vs Spearman vs MI on a non-linear pair", "Expose the confounder: price vs cut quality controlling for carat", "Partial correlation via residuals", "VIF for multicollinearity"],
  f'''
import numpy as np, pandas as pd
from scipy import stats
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression
df = pd.read_csv("{DIAMONDS}").sample(8000, random_state=0)
print(df[["carat", "depth", "table", "price", "x"]].corr().round(2))
print(f"carat-price Pearson {{stats.pearsonr(df.carat, df.price)[0]:.3f}}, Spearman {{stats.spearmanr(df.carat, df.price)[0]:.3f}}, MI {{mutual_info_regression(df[['carat']], df.price, random_state=0)[0]:.2f}}")
x = np.random.default_rng(0).uniform(-3, 3, 2000); y = x ** 2
print(f"y=x² : Pearson {{stats.pearsonr(x, y)[0]:.3f}}, MI {{mutual_info_regression(x[:, None], y, random_state=0)[0]:.2f}} -> dependent but uncorrelated")
q = df.cut.map({{"Fair": 0, "Good": 1, "Very Good": 2, "Premium": 3, "Ideal": 4}})
print(f"cut quality vs price: r = {{stats.spearmanr(q, df.price)[0]:.3f}} (better cut, cheaper?!)")
res = lambda v: v - LinearRegression().fit(np.log(df[["carat"]]), v).predict(np.log(df[["carat"]]))
print(f"partial correlation controlling for carat: {{stats.pearsonr(res(q), res(np.log(df.price)))[0]:.3f}} (positive once size is fixed)")
Xv = df[["carat", "x", "depth", "table"]]
for c in Xv:
    r2 = LinearRegression().fit(Xv.drop(columns=c), Xv[c]).score(Xv.drop(columns=c), Xv[c]); print(f"  VIF {{c:6s}} {{1 / (1 - r2):6.1f}}")
''')

X("m-info-theory",
  "Information theory measures uncertainty and surprise in bits. **Entropy** is how unpredictable a variable is, **cross-entropy** is the cost of predicting with the wrong distribution (the classification loss!), **KL divergence** is the gap between two distributions, and **mutual information** is how much one variable tells you about another (decision-tree splits, feature selection).",
  """**Formulas.** Surprise of an event: −log₂ p. Entropy H(p) = −Σ p log p (max log₂K for uniform over K classes). Cross-entropy H(p, q) = −Σ p log q ≥ H(p); **KL(p‖q) = H(p, q) − H(p) = Σ p log(p/q) ≥ 0**, asymmetric. Minimising cross-entropy loss with one-hot targets = minimising −log q(true class) = maximum likelihood. Information gain of a split = H(parent) − Σ (nₖ/n)H(childₖ) = mutual information I(X; Y) = H(Y) − H(Y|X). Perplexity = 2^(cross-entropy) = 'effective number of choices' for a language model.""",
  """**By hand.** Coin p = 0.5: H = 1 bit; p = 0.9: H = −(0.9 log₂0.9 + 0.1 log₂0.1) = 0.137 + 0.332 = **0.469 bits**. Model predicts q = 0.7 for the true class → loss −ln 0.7 = **0.357 nats**; q = 0.01 → **4.6** (confident and wrong is punished hard). **Titanic split on sex:** H(survive) = 0.961 bits; H after split = (314/891)·0.824 + (577/891)·0.699 = 0.743 → information gain **0.218 bits**.""",
  ["Mixing log bases (bits vs nats)", "Treating KL as symmetric / a distance", "log(0) — clip predicted probabilities", "Comparing perplexities across different tokenisers"],
  ["Classification losses, tree splits, feature selection, LM evaluation, distribution drift (KL/JS)"], ["Continuous variables without a proper estimator (binning choices change MI)"],
  "Titanic and SMS spam — entropy and information gain of features by hand (= decision-tree splits), cross-entropy of a model's predictions, KL drift between ham and spam word distributions, and a unigram perplexity.",
  ["Compute entropy of the target", "Information gain of each feature; check sklearn's tree picks the max", "Cross-entropy (log-loss) of a model by hand vs sklearn", "KL divergence between two word distributions", "Perplexity of a unigram language model"],
  f'''
import re, numpy as np, pandas as pd
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.tree import DecisionTreeClassifier
def H(s): p = s.value_counts(normalize=True).to_numpy(); return -(p * np.log2(p)).sum()
df = pd.read_csv("{TITANIC}"); df["Age"] = df.Age.fillna(df.Age.median()); df["Child"] = df.Age < 12; df["Female"] = df.Sex == "female"
base = H(df.Survived); print(f"H(survived) = {{base:.3f}} bits")
for f in ["Female", "Pclass", "Child", "Embarked"]:
    cond = sum(len(g) / len(df) * H(g.Survived) for _, g in df.groupby(f)); print(f"  IG({{f}}) = {{base - cond:.3f}}")
tree = DecisionTreeClassifier(criterion="entropy", max_depth=1).fit(df[["Female", "Pclass", "Child"]], df.Survived)
print("tree's first split:", ["Female", "Pclass", "Child"][tree.tree_.feature[0]])
X = df[["Female", "Pclass", "Age"]].astype(float); p = LogisticRegression().fit(X, df.Survived).predict_proba(X)[:, 1]; y = df.Survived
print(f"cross-entropy by hand {{-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)):.4f}} = sklearn {{log_loss(y, p):.4f}} nats")
sms = pd.read_csv("{SMS}", sep="\\t", names=["label", "text"]); tok = lambda s: re.findall(r"[a-z']+", s.lower())
c = {{k: Counter(w for t in sms[sms.label == k].text for w in tok(t)) for k in ["ham", "spam"]}}; V = sorted(set(c["ham"]) | set(c["spam"]))
P = {{k: np.array([c[k][w] + 1 for w in V], float) for k in c}}; P = {{k: v / v.sum() for k, v in P.items()}}
print(f"KL(spam||ham) = {{(P['spam'] * np.log2(P['spam'] / P['ham'])).sum():.2f}} bits, KL(ham||spam) = {{(P['ham'] * np.log2(P['ham'] / P['spam'])).sum():.2f}} bits")
test = [w for t in sms.text[-500:] for w in tok(t)]; idx = {{w: i for i, w in enumerate(V)}}
ce = -np.mean([np.log2(P["ham"][idx[w]]) for w in test if w in idx]); print(f"unigram perplexity = {{2 ** ce:.0f}} (vocab {{len(V)}})")
''')
