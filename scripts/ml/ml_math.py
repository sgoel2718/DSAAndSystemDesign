"""Bridge module: Probability & Statistics, Calculus & Linear Algebra for ML."""
from ml_util import M

PROB = [
M("m-prob-basics", "Probability basics: experiments, events, sample space, axioms", "Basic",
  "Probability measures how likely an event is, from 0 (impossible) to 1 (certain). ML models are mostly machines that output probabilities.",
  """### Vocabulary
- **Experiment**: something with an uncertain outcome (toss a coin, a user visits a page).
- **Sample space S**: all possible outcomes ({H, T}; {1,…,6}).
- **Event A**: a subset of outcomes ("die shows an even number" = {2, 4, 6}).
- **P(A)** = favourable outcomes / total outcomes when all outcomes are equally likely.

### Axioms (Kolmogorov)
1. 0 ≤ P(A) ≤ 1. 2. P(S) = 1. 3. For mutually exclusive events, P(A ∪ B) = P(A) + P(B).

### Rules you use every day
- **Complement**: P(not A) = 1 − P(A).
- **Addition (general)**: P(A ∪ B) = P(A) + P(B) − P(A ∩ B).
- **Conditional probability**: P(A | B) = P(A ∩ B) / P(B) — "probability of A given that B happened".
- **Multiplication**: P(A ∩ B) = P(A | B) · P(B).
- **Law of total probability**: P(A) = Σ P(A | Bᵢ) P(Bᵢ) over a partition Bᵢ.

### Frequentist vs Bayesian view
Frequentist: probability = long-run frequency. Bayesian: probability = degree of belief, updated with evidence (Bayes' theorem). ML uses both.""",
  analogy="Probability is a weather forecast for events: 70% rain doesn't mean it will rain, it means in many days like this one, 7 out of 10 had rain.",
  code="""
import numpy as np
rng = np.random.default_rng(0)

die = rng.integers(1, 7, size=100_000)          # simulate 100k die rolls
even = die % 2 == 0
gt4 = die > 4
print("P(even)        ~", even.mean().round(3), "(exact 0.5)")
print("P(even or >4)  ~", (even | gt4).mean().round(3), "(exact 4/6 = 0.667)")
print("P(even | >4)   ~", round((even & gt4).mean() / gt4.mean(), 3), "(exact 1/2: only 6 of {5, 6})")
print("P(not 6)       ~", (die != 6).mean().round(3), "(exact 5/6 = 0.833)")
""",
  say=[("What is conditional probability? Give an ML example.",
        "\"P(A given B) is the probability of A once we know B happened: P(A and B) divided by P(B). A classifier's output is exactly that — P(spam given these words). Precision is also conditional: P(actually positive given the model said positive).\"")]),

M("m-prob-events", "Mutually exclusive vs non-exclusive; independent vs dependent events", "Basic",
  "Mutually exclusive events cannot happen together; independent events don't affect each other's probability. They are different ideas and people often mix them up.",
  """### Mutually exclusive (disjoint)
A ∩ B = ∅, so **P(A ∩ B) = 0** and P(A ∪ B) = P(A) + P(B). Example: one die roll shows 2 *or* 5, never both.

### Non-exclusive (overlapping)
They can happen together, so subtract the overlap: P(A ∪ B) = P(A) + P(B) − P(A ∩ B). Example: a card that is a King *or* a Heart: 4/52 + 13/52 − 1/52 = 16/52.

### Independent
Knowing B tells you nothing about A: **P(A | B) = P(A)**, equivalently **P(A ∩ B) = P(A)·P(B)**. Example: two separate coin tosses.

### Dependent
P(A | B) ≠ P(A). Example: drawing two cards *without replacement* — the second draw depends on the first. Disease and a positive test are dependent (that's the point of a test).

### The classic trap
Mutually exclusive events with non-zero probabilities are **always dependent**: if A happened, B certainly didn't, so P(B | A) = 0 ≠ P(B).

### Why ML cares
**Naive Bayes** assumes features are conditionally independent given the class; **i.i.d.** (independent and identically distributed) samples is the assumption behind train/test splits and most theory — time series break it.""",
  code="""
import numpy as np
rng = np.random.default_rng(1)
n = 200_000
c1, c2 = rng.integers(0, 2, n), rng.integers(0, 2, n)             # two coins
print("independent: P(H1 and H2) =", (c1 & c2).mean().round(3), " P(H1)P(H2) =", (c1.mean() * c2.mean()).round(3))

deck = np.array([r for r in range(13) for _ in range(4)])         # 13 ranks x 4 suits, rank 12 = King
draws = np.array([rng.permutation(deck)[:2] for _ in range(50_000)])
first_k, second_k = draws[:, 0] == 12, draws[:, 1] == 12
print("dependent: P(2nd King) =", second_k.mean().round(4), " P(2nd King | 1st King) =", second_k[first_k].mean().round(4), "(exact 3/51 = 0.0588)")

king_or_heart = 4 / 52 + 13 / 52 - 1 / 52
print("non-exclusive P(King or Heart) =", round(king_or_heart, 4))
""",
  say=[("Are mutually exclusive events independent?",
        "\"No — the opposite. If two events with non-zero probability are mutually exclusive, knowing one happened tells me the other definitely didn't, so P(B given A) is zero, not P(B). Independence means P(A and B) equals P(A) times P(B), which can't be zero if both are positive.\"")]),

M("m-bayes", "Bayes' theorem and Naive Bayes intuition", "Basic",
  "Bayes' theorem updates a prior belief with new evidence: P(A | B) = P(B | A)·P(A) / P(B). It powers spam filters, medical test reasoning and Bayesian ML.",
  """### The formula
**P(H | E) = P(E | H) · P(H) / P(E)**
- **Prior** P(H): belief before evidence. **Likelihood** P(E | H): how probable the evidence is if H is true. **Posterior** P(H | E): updated belief. **Evidence** P(E) = Σ P(E | Hᵢ)P(Hᵢ) normalises.

### The medical test example (base-rate fallacy)
Disease prevalence 1%, test sensitivity 99%, false-positive rate 5%. A positive test gives P(disease | +) = 0.99·0.01 / (0.99·0.01 + 0.05·0.99) ≈ **16.7%** — not 99%! Rare events stay unlikely even after a good test.

### Naive Bayes classifier
P(class | words) ∝ P(class) · Π P(wordᵢ | class), assuming words are independent given the class ("naive"). Fast, needs little data, strong baseline for text. Variants: Multinomial (counts), Bernoulli (presence), Gaussian (continuous features). Use **Laplace smoothing** so an unseen word doesn't zero the product, and sum **log** probabilities to avoid underflow.""",
  code="""
prior, sens, fpr = 0.01, 0.99, 0.05
p_pos = sens * prior + fpr * (1 - prior)
print(f"P(disease | positive) = {sens * prior / p_pos:.3f}")

# Naive Bayes spam filter in scikit-learn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
texts = ["win money now", "cheap pills win", "meeting at noon", "lunch with team", "win a free prize now", "project meeting notes"]
y = [1, 1, 0, 0, 1, 0]                      # 1 = spam
vec = CountVectorizer(); X = vec.fit_transform(texts)
nb = MultinomialNB(alpha=1.0).fit(X, y)     # alpha = Laplace smoothing
test = ["free money prize", "team meeting tomorrow"]
print(nb.predict(vec.transform(test)), nb.predict_proba(vec.transform(test)).round(3))
""",
  say=[("A test is 99% accurate and you test positive for a rare disease. Are you 99% likely to have it?",
        "\"Not necessarily — it depends on the base rate. With 1% prevalence and a 5% false-positive rate, Bayes' theorem gives about 17%, because the many healthy people produce more false positives than the few sick people produce true positives. This is why precision collapses on rare classes and why we look at prevalence, not just accuracy.\"")]),

M("m-random-variables", "Random variables: discrete vs continuous", "Basic",
  "A random variable maps each outcome to a number. Discrete ones take countable values (clicks, dice); continuous ones take any value in a range (height, time).",
  """### Discrete random variable
Countable values. Described by a **PMF** (probability mass function) P(X = x), with Σ P(X = x) = 1.
Examples: number of purchases, die roll, number of defects, word counts.

### Continuous random variable
Uncountably many values. Described by a **PDF** f(x); **P(X = exact value) = 0**, only intervals have probability: P(a ≤ X ≤ b) = ∫ₐᵇ f(x) dx. Examples: temperature, sensor voltage, house price.

### Expectation and variance
- **E[X]** = Σ x P(x) (discrete) or ∫ x f(x) dx (continuous) — the long-run average.
- **Var(X)** = E[(X − μ)²] = E[X²] − (E[X])²; **standard deviation** σ = √Var.
- Linearity: E[aX + b] = aE[X] + b; Var(aX + b) = a²Var(X). For independent X, Y: Var(X + Y) = Var X + Var Y.

### Joint, marginal and covariance
Two variables have a joint distribution; **covariance** Cov(X, Y) = E[(X − μx)(Y − μy)] measures how they move together and **correlation** ρ = Cov/(σxσy) ∈ [−1, 1] normalises it.""",
  code="""
import numpy as np
values = np.array([1, 2, 3, 4, 5, 6]); pmf = np.full(6, 1 / 6)      # fair die PMF
mean = (values * pmf).sum(); var = ((values - mean) ** 2 * pmf).sum()
print("die: E[X] =", mean, " Var =", round(var, 3))

rng = np.random.default_rng(0)
heights = rng.normal(170, 7, 100_000)                                # continuous
print("P(165 <= height <= 175) ~", ((heights >= 165) & (heights <= 175)).mean().round(3))
print("P(height == 170.000) ~", (heights == 170.0).mean())             # zero for continuous

weight = 0.9 * heights - 85 + rng.normal(0, 5, heights.size)
print("cov =", np.cov(heights, weight)[0, 1].round(2), " corr =", np.corrcoef(heights, weight)[0, 1].round(3))
""",
  say=[("What's the difference between a PMF and a PDF?",
        "\"A PMF is for discrete variables and gives actual probabilities P(X = x) that sum to 1. A PDF is for continuous variables; its value is a density, not a probability, and can even exceed 1 — probabilities come from integrating it over an interval, and any single exact value has probability zero.\"")]),

M("m-distributions", "Common distributions: Bernoulli, Binomial, Poisson, Uniform, Normal, Exponential", "Basic",
  "A handful of distributions model most real data. Knowing their shape and parameters lets you choose losses, simulate data and spot anomalies.",
  """|Distribution|Type|Parameters|Mean / variance|Models|
|Bernoulli|discrete|p|p / p(1−p)|one yes/no outcome: click, churn|
|Binomial|discrete|n, p|np / np(1−p)|number of successes in n trials|
|Poisson|discrete|λ|λ / λ|counts per interval: calls per minute, defects|
|Geometric|discrete|p|1/p|trials until first success|
|Uniform|continuous|a, b|(a+b)/2 / (b−a)²/12|random initialisation, "no information"|
|Normal (Gaussian)|continuous|μ, σ|μ / σ²|heights, measurement errors, sums of many effects|
|Exponential|continuous|λ|1/λ / 1/λ²|waiting time between events|
|Beta|continuous|α, β|α/(α+β)|a probability itself (conversion rates)|
|Categorical / Multinomial|discrete|p₁…pₖ|—|class labels; softmax outputs|

### The normal distribution
Bell-shaped, symmetric. **68–95–99.7 rule**: 68% within ±1σ, 95% within ±2σ, 99.7% within ±3σ. Standard normal Z has μ = 0, σ = 1.

### Central Limit Theorem (CLT)
The mean of many independent samples is approximately normal, whatever the original distribution — why confidence intervals and many tests work.

### Link to ML losses
Gaussian noise ⇒ maximum likelihood = **mean squared error**; Bernoulli labels ⇒ **binary cross-entropy**; Categorical ⇒ **cross-entropy**; Poisson ⇒ Poisson loss for counts.""",
  demo="clt",
  code="""
import numpy as np
from scipy import stats
print("Binomial(10, 0.3): P(X=3) =", round(stats.binom.pmf(3, 10, 0.3), 4))
print("Poisson(4): P(X<=2)       =", round(stats.poisson.cdf(2, 4), 4))
print("Normal: within 1/2/3 sigma =", [round(stats.norm.cdf(k) - stats.norm.cdf(-k), 4) for k in (1, 2, 3)])
print("Exponential(rate 2): mean  =", stats.expon(scale=1 / 2).mean())

# Central Limit Theorem: means of skewed exponential samples become normal
rng = np.random.default_rng(0)
means = rng.exponential(1.0, size=(20_000, 50)).mean(axis=1)
print("skew of raw data:", round(stats.skew(rng.exponential(1.0, 20_000)), 2), " skew of sample means:", round(stats.skew(means), 2))
""",
  say=[("What does the Central Limit Theorem say and why does it matter?",
        "\"The average of many independent samples is approximately normally distributed, with standard error sigma over root n, regardless of the original distribution. That's why we can build confidence intervals for a metric, run A/B tests with z or t tests, and why averaged errors often look Gaussian.\"")]),

M("m-pdf-cdf", "Probability density functions (PDF) and cumulative distribution functions (CDF)", "Basic",
  "The PDF shows where values are dense; the CDF F(x) = P(X ≤ x) accumulates it. Percentiles, p-values and quantile transforms all come from the CDF.",
  """### PDF f(x)
- f(x) ≥ 0 and the total area ∫ f(x) dx = 1.
- Height is density, not probability; probability = area under the curve.

### CDF F(x) = P(X ≤ x)
- Goes from 0 to 1, never decreases. For continuous X, F′(x) = f(x).
- P(a < X ≤ b) = F(b) − F(a).
- Works for discrete variables too (a staircase).

### Inverse CDF (quantile function, ppf)
F⁻¹(p) gives the value below which a fraction p lies: the median is F⁻¹(0.5); the 95th percentile latency is F⁻¹(0.95). **Inverse transform sampling**: if U ~ Uniform(0, 1), F⁻¹(U) has distribution F.

### Empirical CDF
From data: the fraction of samples ≤ x. Used to compare distributions (Kolmogorov–Smirnov test) and to detect **data drift** between training and production.

### Kernel density estimation (KDE)
A smooth estimate of the PDF from samples by placing a small bump (kernel) at each point; bandwidth controls smoothness.""",
  code="""
import numpy as np
from scipy import stats
X = stats.norm(loc=100, scale=15)                 # IQ-like scores
print("pdf(100) =", round(X.pdf(100), 4), " cdf(130) =", round(X.cdf(130), 4))
print("P(85 < X <= 115) =", round(X.cdf(115) - X.cdf(85), 4))
print("95th percentile =", round(X.ppf(0.95), 1))

# inverse-transform sampling: exponential from uniforms
rng = np.random.default_rng(0); u = rng.uniform(size=100_000)
samples = -np.log(1 - u) / 2.0                    # F^-1 of Exponential(rate=2)
print("mean of inverse-transform samples:", samples.mean().round(3), "(expected 0.5)")

# empirical CDF and drift test
train, prod = rng.normal(0, 1, 2000), rng.normal(0.3, 1, 2000)
print("KS test train vs prod p-value:", stats.ks_2samp(train, prod).pvalue)
""",
  say=[("How would you detect that production data has drifted from the training data?",
        "\"Compare feature distributions: a two-sample Kolmogorov–Smirnov test on the empirical CDFs for continuous features, chi-square for categorical ones, or the Population Stability Index. I'd monitor these per feature on a schedule, plus prediction-distribution drift, and alert when the change is significant — then investigate and retrain if needed.\"")]),

M("m-centre-spread", "Descriptive statistics: centre (mean, median, mode) and spread (variance, IQR)", "Basic",
  "Summaries of centre and spread describe a feature in a few numbers; robust ones (median, IQR) resist outliers.",
  """### Measures of centre
- **Mean** x̄ = Σx/n — uses every value, pulled by outliers (average salary in a room when a billionaire walks in).
- **Median** — middle value when sorted; robust to outliers. Use for skewed data (income, house prices, latency).
- **Mode** — most frequent value; the only one for categories.
- Skew: right-skewed ⇒ mean > median.

### Measures of spread
- **Range** = max − min (sensitive to outliers).
- **Variance** s² = Σ(x − x̄)²/(n − 1) (sample; n − 1 is Bessel's correction). **Standard deviation** s = √s², same units as data.
- **IQR** = Q3 − Q1 (middle 50%), robust. Box plots show Q1, median, Q3 and whiskers.
- **Coefficient of variation** = s / x̄ to compare spreads across scales.
- **MAD** (median absolute deviation) — robust alternative to s.

### Outlier rules
- **IQR rule**: outside [Q1 − 1.5·IQR, Q3 + 1.5·IQR].
- **Z-score rule**: |z| > 3.

### Shape
**Skewness** (asymmetry) and **kurtosis** (heavy tails). Log transform often fixes right skew.""",
  code="""
import numpy as np
from scipy import stats
salaries = np.array([32, 35, 38, 40, 41, 43, 45, 47, 50, 400])   # in thousands, one outlier
print("mean", salaries.mean(), " median", np.median(salaries), " mode", stats.mode(salaries, keepdims=False).mode)
print("std", salaries.std(ddof=1).round(1), " IQR", np.subtract(*np.percentile(salaries, [75, 25])))
q1, q3 = np.percentile(salaries, [25, 75]); iqr = q3 - q1
print("IQR outliers:", salaries[(salaries < q1 - 1.5 * iqr) | (salaries > q3 + 1.5 * iqr)])
print("skewness", round(stats.skew(salaries), 2), "-> after log:", round(stats.skew(np.log(salaries)), 2))
""",
  say=[("When would you use the median instead of the mean?",
        "\"When the data is skewed or has outliers — salaries, house prices, response latencies. One huge value drags the mean but barely moves the median. That's also why I'd impute missing values with the median for skewed features and report p50/p95 latency rather than the average.\"")]),

M("m-normalization", "Normalization and standardization (feature scaling)", "Basic",
  "Scaling puts features on comparable ranges. Min-max normalization maps to [0, 1]; standardization (z-score) gives mean 0, std 1. Distance- and gradient-based models need it.",
  """### Min-max normalization
x′ = (x − min) / (max − min) → [0, 1]. Keeps the shape; sensitive to outliers. Used for pixel values (÷255) and bounded features.

### Standardization (z-score)
z = (x − μ) / σ → mean 0, std 1. Default for most models (linear/logistic regression, SVM, kNN, PCA, neural nets).

### Robust scaling
(x − median) / IQR — for data with outliers.

### Other transforms
- **Log / Box-Cox / Yeo-Johnson**: reduce skew.
- **L2 normalization** of each *row* to unit length — for text vectors and embeddings (cosine similarity).
- **Quantile transform**: map to uniform or normal ranks.

### Who needs scaling?
|Needs it|Doesn't|
|kNN, k-means, SVM, PCA, linear/logistic regression with regularisation, neural nets (faster convergence)|decision trees, random forests, gradient-boosted trees (split thresholds are scale-invariant)|

### The golden rule: no leakage
**Fit the scaler on the training set only**, then transform validation and test with those same μ, σ. Put it inside a scikit-learn `Pipeline` so cross-validation does this automatically.""",
  code="""
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_wine

X = np.array([[1000.0, 1], [2000, 2], [3000, 3], [100000, 4]])    # income, rooms
print("min-max:\\n", MinMaxScaler().fit_transform(X).round(3))
print("standard:\\n", StandardScaler().fit_transform(X).round(3))
print("robust:\\n", RobustScaler().fit_transform(X).round(3))

Xw, yw = load_wine(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(Xw, yw, random_state=0, stratify=yw)
raw = KNeighborsClassifier().fit(Xtr, ytr).score(Xte, yte)
scaled = make_pipeline(StandardScaler(), KNeighborsClassifier()).fit(Xtr, ytr).score(Xte, yte)
print(f"kNN accuracy raw={raw:.3f}  scaled={scaled:.3f}")
""",
  say=[("Why should the scaler be fitted only on training data?",
        "\"Because fitting on all data leaks information about the test set — its mean and spread — into training, making the evaluation optimistic. In production the model only ever sees statistics from the past. So I fit the scaler on the training fold and apply it to validation and test, ideally inside a Pipeline so cross-validation handles it.\"")]),

M("m-sampling-ci", "Sampling, estimation and confidence intervals", "Intermediate",
  "We estimate population quantities from samples. A confidence interval gives a range that captures the true value in, say, 95% of repeated experiments.",
  """### Population vs sample
Parameters (μ, σ) describe the population; statistics (x̄, s) estimate them from a sample. **Sampling methods**: simple random, **stratified** (keep class ratios — use for train/test splits), cluster, systematic. Biased sampling (only surveying app users) ruins models.

### Standard error
SE of the mean = σ/√n — more data shrinks uncertainty by √n.

### Confidence interval (95%)
x̄ ± 1.96·SE (z) or t-value for small n. Interpretation: the *procedure* captures μ 95% of the time — not "95% chance μ is in this particular interval" (that's a Bayesian credible interval).

### Bootstrap confidence intervals
Resample the data with replacement many times, compute the statistic each time, take the 2.5th and 97.5th percentiles. Works for any metric (F1, AUC, median) — very useful for model evaluation.

### Maximum likelihood estimation (MLE)
Choose parameters that make the observed data most probable. Most ML training is MLE (or MAP — MLE plus a prior, which equals regularisation).""",
  code="""
import numpy as np
from scipy import stats
rng = np.random.default_rng(0)
sample = rng.exponential(scale=20, size=60)          # e.g. session lengths in minutes

m, se = sample.mean(), stats.sem(sample)
lo, hi = stats.t.interval(0.95, df=len(sample) - 1, loc=m, scale=se)
print(f"mean {m:.1f}, 95% t-interval ({lo:.1f}, {hi:.1f})")

boots = [np.median(rng.choice(sample, len(sample), replace=True)) for _ in range(5000)]
print("bootstrap 95% CI for the median:", np.percentile(boots, [2.5, 97.5]).round(1))

# MLE for an exponential rate = 1 / mean
print("MLE of rate:", round(1 / sample.mean(), 4), "(true 0.05)")
""",
  say=[("How would you put an error bar on your model's F1 score?",
        "\"Bootstrap the test set: resample it with replacement a thousand or so times, compute F1 on each resample, and take the 2.5th and 97.5th percentiles as a 95% interval. Or report mean and standard deviation across cross-validation folds. If two models' intervals overlap heavily, I wouldn't claim one is better.\"")]),

M("m-hypothesis", "Hypothesis testing, p-values and A/B tests", "Intermediate",
  "Hypothesis tests ask whether an observed effect could be due to chance. A/B tests apply this to product changes and model launches.",
  """### Procedure
1. **Null hypothesis H₀**: no effect (new model = old model). **Alternative H₁**: there is an effect.
2. Choose significance level α (usually 0.05).
3. Compute a test statistic and its **p-value**: the probability of seeing data at least this extreme *if H₀ were true*.
4. p < α ⇒ reject H₀ (statistically significant).

### Errors
- **Type I** (false positive): reject a true H₀; rate = α.
- **Type II** (false negative): miss a real effect; rate = β. **Power** = 1 − β (aim 0.8). More samples ⇒ more power.

### Which test?
|Situation|Test|
|compare two means|t-test (Welch if variances differ); paired t-test for before/after|
|compare proportions (conversion rates)|z-test for proportions / chi-square|
|categorical association|chi-square test of independence|
|non-normal data|Mann–Whitney U, Wilcoxon|
|more than two groups|ANOVA / Kruskal–Wallis|
|correlation|Pearson (linear), Spearman (rank)|

### A/B testing pitfalls
Decide sample size up front; don't "peek" and stop early; correct for **multiple comparisons** (Bonferroni); watch novelty effects; significance ≠ business importance (report effect size and CI).""",
  code="""
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# A/B test: old model 480/10000 clicks, new model 560/10000
z, p = proportions_ztest([560, 480], [10000, 10000])
print(f"CTR 5.6% vs 4.8%: z={z:.2f}, p={p:.4f} ->", "significant" if p < 0.05 else "not significant")

# chi-square: is churn associated with plan type?
table = np.array([[120, 380], [60, 440]])             # rows: basic, premium; cols: churned, stayed
chi2, p2, dof, _ = stats.chi2_contingency(table)
print(f"chi2={chi2:.1f}, p={p2:.2e}")

# sample size needed to detect 4.8% -> 5.3% with 80% power
es = proportion_effectsize(0.053, 0.048)
print("users per arm:", int(NormalIndPower().solve_power(effect_size=es, alpha=0.05, power=0.8)))
""",
  say=[("What is a p-value? What it is not?",
        "\"It's the probability of getting a result at least as extreme as what we observed, assuming the null hypothesis is true. It is not the probability that the null is true, and a small p-value doesn't mean the effect is large or important — so I always report the effect size and a confidence interval alongside it.\"")]),

M("m-correlation", "Correlation vs causation, covariance matrix", "Basic",
  "Correlation measures how two variables move together; it does not prove one causes the other. The covariance matrix summarises all pairwise relationships and drives PCA.",
  """- **Pearson r**: linear correlation in [−1, 1]. **Spearman ρ**: correlation of ranks — catches monotonic non-linear relationships and resists outliers.
- r ≈ 0 does *not* mean independent: y = x² on symmetric x has r = 0.
- **Covariance matrix** Σ (d×d): Σᵢⱼ = Cov(featureᵢ, featureⱼ); symmetric, positive semi-definite. Its eigenvectors are the principal components.
- **Multicollinearity**: highly correlated features make linear-model coefficients unstable; detect with correlation heatmaps or VIF (variance inflation factor).
- **Causation** needs experiments (A/B tests) or causal inference (confounder adjustment, instrumental variables). Classic confounder: ice-cream sales and drownings both rise with summer heat.
- **Simpson's paradox**: a trend in every group can reverse when groups are combined.""",
  code="""
import numpy as np, pandas as pd
rng = np.random.default_rng(0)
temp = rng.uniform(15, 40, 300)                                 # confounder: temperature
ice_cream = 20 * temp + rng.normal(0, 60, 300)
drownings = 0.3 * temp + rng.normal(0, 2, 300)
df = pd.DataFrame({"temp": temp, "ice_cream": ice_cream, "drownings": drownings})
print(df.corr().round(2))

x = rng.uniform(-3, 3, 1000)
print("y = x^2: pearson", np.corrcoef(x, x ** 2)[0, 1].round(3), "(no linear relation, but fully dependent)")
from scipy.stats import spearmanr
z = np.exp(x)
print("y = e^x: pearson", np.corrcoef(x, z)[0, 1].round(3), " spearman", round(spearmanr(x, z).statistic, 3))
""",
  say=[("Your model finds a strong correlation between a feature and the target. Can the business act on it?",
        "\"Not as a causal lever without more evidence. Correlation can come from a confounder or reverse causation. It's fine for prediction, but to claim that changing the feature changes the outcome I'd want a randomized experiment, or at least a causal analysis controlling for confounders.\"")]),

M("m-info-theory", "Information theory: entropy, cross-entropy, KL divergence", "Intermediate",
  "Entropy measures uncertainty; cross-entropy is the standard classification loss; KL divergence measures how one distribution differs from another (used in VAEs, distillation, RLHF).",
  """- **Entropy** H(p) = −Σ p(x) log p(x). A fair coin has 1 bit; a certain outcome has 0. Decision trees pick splits that reduce entropy (**information gain**).
- **Cross-entropy** H(p, q) = −Σ p(x) log q(x): the cost of encoding true distribution p using model q. With one-hot labels it becomes −log q(true class) — the **log loss** used to train classifiers and LLMs.
- **KL divergence** D_KL(p‖q) = Σ p log(p/q) = H(p, q) − H(p) ≥ 0, zero only when p = q; *not symmetric*.
- **Perplexity** = exp(cross-entropy) — the language-model metric ("how many words is the model choosing between").
- **Mutual information** I(X; Y) = how much knowing X reduces uncertainty in Y — a feature selection score.""",
  code="""
import numpy as np
from scipy.stats import entropy
from sklearn.feature_selection import mutual_info_classif
from sklearn.datasets import load_iris

print("H(fair coin) =", entropy([0.5, 0.5], base=2), "bits;  H(0.9/0.1) =", round(entropy([0.9, 0.1], base=2), 3))
p = np.array([0, 1, 0])                        # true class 1 (one-hot)
for q in ([0.1, 0.8, 0.1], [0.3, 0.4, 0.3], [0.7, 0.2, 0.1]):
    ce = -np.sum(p * np.log(np.array(q)))
    print(f"prediction {q}: cross-entropy {ce:.3f}")
P, Q = np.array([0.4, 0.4, 0.2]), np.array([0.3, 0.5, 0.2])
print("KL(P||Q) =", round(entropy(P, Q), 4), " KL(Q||P) =", round(entropy(Q, P), 4), "(not symmetric)")
X, y = load_iris(return_X_y=True)
print("mutual information per iris feature:", mutual_info_classif(X, y, random_state=0).round(2))
""",
  say=[("Why do we use cross-entropy instead of accuracy as the training loss?",
        "\"Accuracy is a step function — not differentiable and it ignores confidence. Cross-entropy is smooth, penalises confident wrong answers heavily, and is the negative log-likelihood of the labels, so minimising it is maximum likelihood. Combined with softmax it also gives a clean gradient: predicted probability minus the true label.\"")]),
]

LINALG = [
M("m-vectors", "Vectors: geometry, dot product, cosine similarity", "Basic",
  "A vector is an ordered list of numbers — a point or an arrow in space. Every data sample, embedding and weight set is a vector.",
  """### Operations
- Addition and scalar multiplication work element-wise.
- **Dot product** a·b = Σ aᵢbᵢ = ‖a‖‖b‖cos θ. Positive ⇒ same general direction; 0 ⇒ **orthogonal**; negative ⇒ opposite.
- **Projection** of a onto b: (a·b / ‖b‖²) b.
- **Cosine similarity** = a·b / (‖a‖‖b‖) ∈ [−1, 1] — the standard similarity for text embeddings and in RAG retrieval, because it ignores length.

### In ML
- A sample with d features = a point in d-dimensional space.
- A linear model computes w·x + b — a dot product.
- A neuron = dot product + non-linearity.
- Embeddings place similar words/images close together; "king − man + woman ≈ queen" is vector arithmetic.""",
  code="""
import numpy as np
a, b = np.array([3.0, 4.0]), np.array([4.0, 3.0])
print("a+b", a + b, " 2a", 2 * a, " a.b", a @ b)
cos = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
print("cosine similarity", round(cos, 3), " angle", round(np.degrees(np.arccos(cos)), 1), "deg")
print("projection of a on b", ((a @ b) / (b @ b) * b).round(3))

docs = {"cats purr": [0.9, 0.1, 0.0], "kittens meow": [0.8, 0.2, 0.1], "stock prices fell": [0.0, 0.1, 0.95]}
query = np.array([0.85, 0.15, 0.05])
for d, v in docs.items():
    v = np.array(v); print(f"{d:18s} cos={query @ v / np.linalg.norm(query) / np.linalg.norm(v):.3f}")
""",
  say=[("Why is cosine similarity preferred over Euclidean distance for text embeddings?",
        "\"Cosine looks only at direction, not length. A long document and a short one about the same topic point the same way but have very different magnitudes, so Euclidean distance would call them far apart. For normalised embeddings, cosine and Euclidean ranking are equivalent, which is why vector databases often normalise.\"")]),

M("m-norms", "Norms: L1, L2, L-infinity and why they matter for regularisation", "Basic",
  "A norm measures a vector's size. L2 is straight-line length, L1 is the 'city-block' sum of absolute values. They define distances and regularisation penalties.",
  """|Norm|Formula|Distance it gives|Used for|
|L1 (Manhattan)|Σ|xᵢ||city-block distance|Lasso regularisation → sparse weights (feature selection), MAE loss, robust to outliers|
|L2 (Euclidean)|√Σxᵢ²|straight-line distance|Ridge / weight decay → small spread-out weights, MSE loss, kNN, k-means|
|L∞ (max)|max |xᵢ||chessboard distance|adversarial perturbation budgets|
|L0 ("norm")|count of non-zeros|—|true sparsity (not convex)|
|Frobenius|√Σ aᵢⱼ² for matrices|—|matrix size, low-rank approximation error|

### Why L1 gives sparse solutions
The L1 ball has corners on the axes; the loss contours usually touch it at a corner where some weights are exactly 0. The round L2 ball has no corners, so weights shrink but rarely hit zero.

### Unit vectors
x / ‖x‖₂ has length 1 — normalising embeddings this way makes dot product = cosine similarity.""",
  code="""
import numpy as np
from sklearn.linear_model import Lasso, Ridge
x = np.array([3.0, -4.0, 0.0, 1.0])
print("L1", np.linalg.norm(x, 1), " L2", round(np.linalg.norm(x), 3), " Linf", np.linalg.norm(x, np.inf), " L0", np.count_nonzero(x))

rng = np.random.default_rng(0)
X = rng.normal(size=(200, 10)); true_w = np.array([5, -3, 0, 0, 0, 0, 0, 0, 0, 2.0])
y = X @ true_w + rng.normal(0, 0.5, 200)
print("Lasso (L1) weights:", Lasso(alpha=0.1).fit(X, y).coef_.round(2))
print("Ridge (L2) weights:", Ridge(alpha=10).fit(X, y).coef_.round(2))
""",
  say=[("What's the difference between L1 and L2 regularisation?",
        "\"Both add a penalty on weight size. L1 adds the sum of absolute weights and drives many weights exactly to zero, so it does feature selection — Lasso. L2 adds the sum of squares and shrinks all weights smoothly without zeroing them, which handles correlated features well — Ridge, or weight decay in neural nets. Elastic Net combines both.\"")]),

M("m-matrices", "Matrices and matrix operations", "Basic",
  "A matrix is a 2-D grid of numbers. A dataset is a matrix (rows = samples, columns = features), and every neural-network layer is a matrix multiplication.",
  """### Operations
- **Addition / scalar multiply**: element-wise.
- **Matrix multiplication** C = AB: (m×n)(n×p) → (m×p), Cᵢⱼ = row i of A · column j of B. **Not commutative** (AB ≠ BA), but associative.
- **Element-wise (Hadamard) product** A ⊙ B (`*` in NumPy) — different from `@`.
- **Transpose** Aᵀ swaps rows and columns; (AB)ᵀ = BᵀAᵀ.
- **Identity** I: AI = A. **Inverse** A⁻¹: AA⁻¹ = I (only square, non-singular matrices; determinant ≠ 0).
- **Determinant**: how much the matrix scales area/volume; 0 ⇒ squashes space ⇒ not invertible.
- **Trace**: sum of the diagonal = sum of eigenvalues.
- **Rank**: number of linearly independent rows/columns.

### Special matrices
Diagonal, symmetric (A = Aᵀ, e.g. covariance), orthogonal (QᵀQ = I, rotations), positive (semi-)definite (xᵀAx ≥ 0), sparse.

### In ML
A batch of inputs X (batch × features) times weights W (features × outputs) plus bias b = a dense layer: **Y = XW + b**. GPUs exist because they do this very fast.""",
  code="""
import numpy as np
A = np.array([[1, 2], [3, 4]]); B = np.array([[0, 1], [1, 0]])
print("A@B =\\n", A @ B, "\\nB@A =\\n", B @ A, "\\n(not commutative)")
print("A*B (element-wise) =\\n", A * B)
print("det", round(np.linalg.det(A), 3), " rank", np.linalg.matrix_rank(A), " trace", np.trace(A))
Ainv = np.linalg.inv(A); print("A @ inv(A) =\\n", (A @ Ainv).round(10))

# a dense layer: batch of 4 samples, 3 features -> 2 outputs
rng = np.random.default_rng(0)
X, W, b = rng.normal(size=(4, 3)), rng.normal(size=(3, 2)), np.array([0.1, -0.1])
print("layer output shape:", (X @ W + b).shape)
""",
  say=[("What does it mean if a matrix is singular, and why does it matter for linear regression?",
        "\"Singular means its determinant is zero — its columns are linearly dependent — so it has no inverse. In linear regression the normal equation needs the inverse of X-transpose-X; if two features are perfectly collinear that matrix is singular and the solution isn't unique. Fixes are dropping redundant features, using the pseudo-inverse, or Ridge regularisation, which adds lambda times identity and makes it invertible.\"")]),

M("m-lin-indep", "Linear combinations, span, linear dependence and independence, basis, rank", "Intermediate",
  "Vectors are linearly independent if none can be written as a combination of the others. Independence tells you how much genuinely new information features carry.",
  """- **Linear combination**: c₁v₁ + c₂v₂ + … + cₖvₖ.
- **Span**: all vectors reachable by linear combinations.
- **Linearly dependent**: some non-trivial combination equals 0 (one vector is redundant). Example: features "price in ₹" and "price in $" — one is a multiple of the other.
- **Basis**: a set of independent vectors that spans the space; the number of them is the **dimension**.
- **Rank** of a matrix = number of independent columns = dimension of its column space. A data matrix with rank < number of features has redundant features.
- **Null space**: vectors x with Ax = 0. **Rank–nullity**: rank + nullity = number of columns.

### Why ML cares
- Redundant features (multicollinearity) make linear-model weights unstable.
- PCA finds a new basis aligned with the variance; dropping low-variance directions = low-rank approximation.
- LoRA fine-tuning assumes weight *updates* are low rank.""",
  code="""
import numpy as np
v1, v2 = np.array([1, 2, 3]), np.array([2, 4, 6])
v3 = np.array([0, 1, 1])
print("rank [v1, v2]     =", np.linalg.matrix_rank(np.column_stack([v1, v2])), "-> dependent (v2 = 2*v1)")
print("rank [v1, v3]     =", np.linalg.matrix_rank(np.column_stack([v1, v3])), "-> independent")

rng = np.random.default_rng(0)
price_inr = rng.uniform(100, 1000, 50)
X = np.column_stack([price_inr, price_inr / 83.0, rng.normal(size=50)])   # 2nd column redundant
print("data matrix shape", X.shape, "rank", np.linalg.matrix_rank(X))
print("condition number (huge = near-dependent):", f"{np.linalg.cond(X):.2e}")
""",
  say=[("How would you detect redundant features in a dataset?",
        "\"Look at the correlation matrix and variance inflation factors for near-linear dependence; check the rank or condition number of the feature matrix; and PCA — if a few components explain almost all the variance, the features are largely redundant. Then drop or combine them, or use regularisation.\"")]),

M("m-lin-transform", "Linear transformations, eigenvalues and eigenvectors", "Intermediate",
  "A matrix is a function that transforms space — rotating, scaling, shearing or projecting it. Eigenvectors are the special directions it only stretches.",
  """### Linear transformation
T(x) = Ax with T(a + b) = T(a) + T(b) and T(cx) = cT(x): lines stay lines, the origin stays put. Rotation, scaling, shear, reflection and projection are all matrices. Composition = matrix multiplication. A neural-network layer is a linear transformation followed by a non-linearity — without the non-linearity, stacked layers collapse into one matrix.

### Eigenvalues and eigenvectors
**Av = λv**: v keeps its direction, scaled by λ. Found from det(A − λI) = 0.
- Symmetric matrices (covariance!) have real eigenvalues and orthogonal eigenvectors: **A = QΛQᵀ** (eigendecomposition).
- Covariance eigenvectors = principal components; eigenvalues = variance along them.
- Google PageRank is the dominant eigenvector of the link matrix; power iteration finds it.
- Eigenvalues of the Hessian tell you if a point is a minimum (all positive) or a saddle.

### Singular value decomposition (SVD)
Any m×n matrix **A = UΣVᵀ** (rotate → scale → rotate). Keeping the top-k singular values gives the best rank-k approximation (Eckart–Young). Used in PCA, recommender systems (matrix factorisation), latent semantic analysis, image compression and the pseudo-inverse.""",
  code="""
import numpy as np
theta = np.radians(90)
R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])   # rotation
S = np.diag([2.0, 0.5])                                                          # scaling
x = np.array([1.0, 0.0])
print("rotate:", (R @ x).round(3), " scale:", S @ x, " rotate then scale:", (S @ R @ x).round(3))

C = np.array([[4.0, 2.0], [2.0, 3.0]])           # a covariance matrix
vals, vecs = np.linalg.eigh(C)
print("eigenvalues", vals.round(3)); print("eigenvectors (columns)\\n", vecs.round(3))
print("check A v = lambda v:", np.allclose(C @ vecs[:, 1], vals[1] * vecs[:, 1]))

rng = np.random.default_rng(0)
img = np.outer(np.sin(np.linspace(0, 3, 64)), np.cos(np.linspace(0, 3, 64))) + 0.05 * rng.normal(size=(64, 64))
U, s, Vt = np.linalg.svd(img)
k = 3; approx = U[:, :k] @ np.diag(s[:k]) @ Vt[:k]
print(f"rank-{k} approximation keeps {(s[:k] ** 2).sum() / (s ** 2).sum():.1%} of the energy, relative error {np.linalg.norm(img - approx) / np.linalg.norm(img):.3f}")
""",
  say=[("What is an eigenvector, intuitively, and where is it used in ML?",
        "\"It's a direction that a matrix only stretches or shrinks, never rotates; the eigenvalue is the stretch factor. In PCA the eigenvectors of the covariance matrix are the directions of maximum variance and the eigenvalues tell how much variance each captures. They also appear in spectral clustering, PageRank, and analysing the curvature of a loss via the Hessian.\"")]),

M("m-least-squares", "Least squares error and the normal equation", "Intermediate",
  "Least squares finds the line (or hyperplane) that minimises the sum of squared errors. It is the maths behind linear regression.",
  """### Problem
Given X (n×d) and y (n), find w minimising **‖Xw − y‖²** = Σ(ŷᵢ − yᵢ)².

### Normal equation
Setting the gradient 2Xᵀ(Xw − y) to zero gives **XᵀXw = Xᵀy ⇒ w = (XᵀX)⁻¹Xᵀy**.
Geometrically, Xw is the **projection** of y onto the column space of X; the residual is orthogonal to every column.

### In practice
- Don't compute the inverse explicitly; use `np.linalg.lstsq` (QR/SVD) — numerically stable and works when XᵀX is singular (pseudo-inverse).
- O(nd² + d³): fine for thousands of features, too slow for millions → use **gradient descent**.
- **Ridge**: w = (XᵀX + λI)⁻¹Xᵀy — always invertible.
- Why squares? Differentiable, penalises large errors, and equals maximum likelihood under Gaussian noise. Downside: sensitive to outliers (use Huber or MAE then).""",
  code="""
import numpy as np
rng = np.random.default_rng(0)
x = rng.uniform(0, 10, 50)
y = 2.5 * x + 4 + rng.normal(0, 2, 50)
X = np.column_stack([np.ones_like(x), x])           # add bias column

w_normal = np.linalg.inv(X.T @ X) @ X.T @ y          # textbook formula
w_lstsq, *_ = np.linalg.lstsq(X, y, rcond=None)      # stable way
print("normal equation:", w_normal.round(3), " lstsq:", w_lstsq.round(3), "(true [4, 2.5])")
resid = y - X @ w_lstsq
print("residuals orthogonal to columns:", (X.T @ resid).round(8))
print("SSE", round((resid ** 2).sum(), 2), " R^2", round(1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum(), 3))
""",
  say=[("Why not always use the normal equation for linear regression?",
        "\"It needs inverting a d-by-d matrix, which is cubic in the number of features and memory-heavy, and it's numerically unstable when features are collinear. For large or streaming data, gradient descent or SGD scales better; for moderate sizes I'd use a QR or SVD-based solver like lstsq, or Ridge to keep it well-conditioned.\"")]),

M("m-derivatives", "Derivatives, partial derivatives and the chain rule", "Basic",
  "A derivative is the slope — how fast the output changes when the input changes. Training a model is just following derivatives of the loss downhill; the chain rule makes backpropagation possible.",
  """### Derivative
f′(x) = lim (f(x + h) − f(x))/h. Rules: (xⁿ)′ = nxⁿ⁻¹, (eˣ)′ = eˣ, (ln x)′ = 1/x, (sin x)′ = cos x; sum, product (uv)′ = u′v + uv′, quotient rules.

### Partial derivatives
For f(x, y), ∂f/∂x treats y as a constant. A loss depends on millions of weights; each has a partial derivative.

### Chain rule
If y = f(g(x)), then **dy/dx = f′(g(x)) · g′(x)** — multiply the local slopes along the path. For a network: ∂Loss/∂w = ∂Loss/∂ŷ · ∂ŷ/∂z · ∂z/∂w. **Backpropagation** applies the chain rule from the loss backwards, reusing intermediate results.

### Derivatives you meet in ML
|Function|Derivative|
|sigmoid σ(x)|σ(x)(1 − σ(x)) (max 0.25 → vanishing gradients)|
|tanh|1 − tanh²|
|ReLU|1 if x > 0 else 0|
|MSE (ŷ − y)²|2(ŷ − y)|
|softmax + cross-entropy|ŷ − y|

### Checking gradients numerically
Finite differences (f(x + h) − f(x − h))/2h verify hand-written gradients.""",
  code="""
import numpy as np
import torch

f = lambda x: x ** 3 + 2 * x                          # f'(x) = 3x^2 + 2
h, x0 = 1e-5, 2.0
print("numerical f'(2) =", round((f(x0 + h) - f(x0 - h)) / (2 * h), 5), " analytic =", 3 * x0 ** 2 + 2)

# chain rule: y = sigmoid(w*x + b), loss = (y - t)^2
x, t = 1.5, 1.0
w = torch.tensor(0.8, requires_grad=True); b = torch.tensor(-0.2, requires_grad=True)
z = w * x + b; y = torch.sigmoid(z); loss = (y - t) ** 2
loss.backward()                                       # autograd = automatic chain rule
manual = 2 * (y.item() - t) * y.item() * (1 - y.item()) * x
print("autograd dL/dw =", round(w.grad.item(), 6), " manual chain rule =", round(manual, 6))
""",
  say=[("Explain the chain rule's role in training neural networks.",
        "\"A network is a composition of functions, so the gradient of the loss with respect to an early weight is the product of local derivatives along the path from that weight to the loss. Backpropagation computes these products efficiently by going backwards once and reusing intermediate gradients. Frameworks like PyTorch do it automatically with autograd.\"")]),

M("m-gradients", "Gradients, Jacobian, Hessian and the geometry of optimisation", "Intermediate",
  "The gradient is the vector of all partial derivatives; it points in the direction of steepest increase. Gradient descent steps the opposite way to reduce the loss.",
  """### Gradient
∇f = [∂f/∂x₁, …, ∂f/∂xₙ]. Its direction is steepest ascent; its size is the slope. At a minimum, ∇f = 0.

### Gradient descent update
**w ← w − η ∇L(w)**, where η is the learning rate. Too large ⇒ overshoot/diverge; too small ⇒ slow.

### Jacobian and Hessian
- **Jacobian** J: matrix of partial derivatives of a vector function (each output w.r.t. each input) — what backprop multiplies through layers.
- **Hessian** H: matrix of second derivatives (curvature). Positive definite ⇒ local minimum; mixed signs ⇒ **saddle point** (common in high-dimensional deep learning). Newton's method uses H⁻¹∇f — fast but too expensive for big nets.

### Convexity
A convex function has one global minimum (linear/logistic regression, SVM). Neural-network losses are non-convex but SGD still finds good solutions.

### Taylor approximation
f(x + Δ) ≈ f(x) + ∇fᵀΔ + ½ΔᵀHΔ — the basis of gradient descent and Newton steps.""",
  demo="gd",
  code="""
import numpy as np
f = lambda w: (w[0] - 3) ** 2 + 10 * (w[1] + 1) ** 2          # elongated bowl, min at (3, -1)
grad = lambda w: np.array([2 * (w[0] - 3), 20 * (w[1] + 1)])
H = np.array([[2.0, 0], [0, 20.0]])
print("Hessian eigenvalues", np.linalg.eigvalsh(H), "-> both positive: a minimum")

for lr in (0.01, 0.09, 0.11):
    w = np.array([0.0, 0.0])
    for _ in range(100):
        w = w - lr * grad(w)
    print(f"lr={lr}: w={w.round(3)}, loss={f(w):.4g}")
w = np.array([0.0, 0.0]); w = w - np.linalg.solve(H, grad(w))
print("one Newton step:", w)
""",
  say=[("Why does a learning rate that is too high make training diverge?",
        "\"Each step moves by the learning rate times the gradient. If that overshoots the minimum by more than the distance to it — specifically if the rate exceeds two over the largest curvature — the error grows each step and the loss explodes. That's why we tune the rate, use warm-up and schedules, and adaptive optimisers like Adam.\"")]),

M("m-integration", "Integration and its role in probability and ML", "Basic",
  "Integration is the area under a curve — the reverse of differentiation. In ML it turns densities into probabilities and defines expectations and AUC.",
  """- **Definite integral** ∫ₐᵇ f(x) dx = area between f and the x-axis from a to b. **Fundamental theorem**: if F′ = f, then ∫ₐᵇ f = F(b) − F(a).
- Common antiderivatives: ∫xⁿ dx = xⁿ⁺¹/(n + 1), ∫eˣ = eˣ, ∫1/x = ln|x|.
- **Probability**: P(a ≤ X ≤ b) = ∫ f(x) dx; CDF F(x) = ∫₋∞ˣ f(t) dt; expectation E[g(X)] = ∫ g(x) f(x) dx.
- **AUC** (area under the ROC curve) is literally an integral, computed with the trapezoidal rule.
- **Numerical integration**: trapezoid/Simpson rules; **Monte Carlo** — average f at random samples (scales to high dimensions; used in Bayesian ML, reinforcement learning, diffusion models).
- **Marginalising** a joint distribution integrates out a variable: p(x) = ∫ p(x, z) dz — the hard part of latent-variable models (VAEs use the ELBO to avoid it).""",
  code="""
import numpy as np
from scipy import integrate, stats

area, _ = integrate.quad(lambda x: x ** 2, 0, 3)
print("integral of x^2 from 0 to 3 =", round(area, 4), "(exact 9)")
p, _ = integrate.quad(stats.norm.pdf, -1.96, 1.96)
print("P(-1.96 < Z < 1.96) =", round(p, 4))

rng = np.random.default_rng(0)
u = rng.uniform(0, 3, 200_000)
print("Monte Carlo estimate =", round(3 * (u ** 2).mean(), 3))

fpr = np.array([0, 0.1, 0.3, 0.6, 1.0]); tpr = np.array([0, 0.6, 0.85, 0.95, 1.0])
print("AUC by trapezoid rule =", round(np.trapezoid(tpr, fpr), 3))
""",
  say=[("What does AUC measure, and how is it related to integration?",
        "\"AUC is the area under the ROC curve — the integral of true-positive rate over false-positive rate from 0 to 1, computed numerically with the trapezoid rule. It equals the probability that a randomly chosen positive is scored higher than a randomly chosen negative, so it measures ranking quality independent of the threshold.\"")]),

M("m-optim-math", "Optimisation maths: convexity, constraints, Lagrange multipliers", "Advanced",
  "Learning = optimisation. Convex problems have one global optimum; constrained ones (like SVMs) are solved with Lagrange multipliers and duality.",
  """- **Convex set / function**: the line between any two points stays inside / above. Sum of convex functions is convex; local minimum = global minimum.
- **Unconstrained**: set ∇f = 0 or run gradient descent.
- **Equality constraints**: minimise f(x) subject to g(x) = 0 ⇒ **Lagrangian** L = f + λg, set all partials to 0. At the optimum, ∇f is parallel to ∇g.
- **Inequality constraints**: **KKT conditions** (primal feasibility, dual feasibility λ ≥ 0, complementary slackness λg = 0). In SVMs, complementary slackness means only **support vectors** have non-zero multipliers.
- **Duality**: the dual problem of the SVM depends only on dot products xᵢ·xⱼ — this is what makes the **kernel trick** possible.
- **Regularisation as constraint**: minimising loss + λ‖w‖² ≡ minimising loss subject to ‖w‖² ≤ t.""",
  code="""
import numpy as np
from scipy.optimize import minimize
# maximise area x*y with perimeter 2x + 2y = 20  -> Lagrange gives x = y = 5
res = minimize(lambda v: -v[0] * v[1], x0=[1, 1], constraints={"type": "eq", "fun": lambda v: 2 * v[0] + 2 * v[1] - 20})
print("optimum", res.x.round(4), "area", round(-res.fun, 4))

# inequality constraint: minimise (x-3)^2 + (y-3)^2 subject to x + y <= 4
res2 = minimize(lambda v: (v[0] - 3) ** 2 + (v[1] - 3) ** 2, x0=[0, 0], constraints={"type": "ineq", "fun": lambda v: 4 - v[0] - v[1]})
print("constrained optimum", res2.x.round(4), "(on the boundary x + y = 4)")
""",
  say=[("Why does the SVM dual formulation matter?",
        "\"In the dual, the data appear only through dot products between pairs of points, so I can replace them with a kernel function and get a non-linear classifier without ever computing the high-dimensional features. Complementary slackness also shows that only the support vectors have non-zero weights, which explains why SVMs are sparse in the training points.\"")]),
]
