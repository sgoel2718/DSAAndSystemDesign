"""Real-data walkthroughs: Probability and statistics."""
import math
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt


@walk("m-prob-basics", "titanic")
def _():
    df = D("titanic"); n = len(df)
    s = int(df["Survived"].sum())
    rng = np.random.default_rng(0)
    draws = pd.DataFrame([{"random passengers drawn": k, "share who survived": pct(df["Survived"].sample(k, random_state=k, replace=True).mean())} for k in [10, 100, 1000, 10000]])
    return [
        ("Probability as a fraction of outcomes", f"Pick one of the {n} real passengers at random. P(survived) = survivors ÷ passengers = {s} ÷ {n} = **{s / n:.3f}**. P(died) = 1 − {s / n:.3f} = {1 - s / n:.3f}. Probabilities are between 0 and 1 and the options add up to 1."),
        ("The long-run frequency", f"Draw passengers at random (with replacement) and count survivors:\n\n{t(draws)}\n\nSmall samples bounce around; large samples settle near the true {pct(s / n, 1)} (law of large numbers)."),
        ("Counting outcomes", f"P(a random passenger is in 1st class) = {int((df.Pclass == 1).sum())}/{n} = {(df.Pclass == 1).mean():.3f}. Picking two different passengers, P(both survived) = ({s}/{n}) × ({s - 1}/{n - 1}) = {s / n * (s - 1) / (n - 1):.3f}: the second draw has one survivor fewer to choose from."),
    ], "A probability is the share of possible outcomes where an event happens; with real data, it's a count divided by a total."


@walk("m-prob-events", "titanic")
def _():
    df = D("titanic"); n = len(df)
    A = df["Sex"] == "female"; B = df["Survived"] == 1; C = df["Pclass"] == 1
    ct = pd.crosstab(df["Sex"], df["Survived"].map({0: "died", 1: "survived"}), margins=True)
    return [
        ("Two events in a table", f"A = female, B = survived:\n\n{t(ct, index=True)}"),
        ("And, or, given", f"- P(A and B) = {int((A & B).sum())}/{n} = **{(A & B).mean():.3f}**\n- P(A or B) = P(A) + P(B) − P(A and B) = {A.mean():.3f} + {B.mean():.3f} − {(A & B).mean():.3f} = **{(A | B).mean():.3f}**\n- P(B given A) = P(A and B) / P(A) = **{(A & B).mean() / A.mean():.3f}**: survival rate among women\n- P(B given not A) = **{(~A & B).mean() / (~A).mean():.3f}**: among men"),
        ("Independent or not?", f"If sex didn't matter, P(B given A) would equal P(B) = {B.mean():.3f}. It's {(A & B).mean() / A.mean():.3f}, so they are strongly **dependent**. Check: P(A) × P(B) = {A.mean() * B.mean():.3f}, but P(A and B) = {(A & B).mean():.3f}. Same for 1st class: P(survived | 1st class) = {(C & B).mean() / C.mean():.3f}."),
    ], "Joint, union and conditional probabilities come straight from a cross-table; independence means conditioning changes nothing."


@walk("m-bayes", "sms")
def _():
    df = D("sms"); spam = df["label"] == "spam"; w = df["text"].str.lower().str.contains(r"\bfree\b")
    ps = spam.mean(); pw_s = w[spam].mean(); pw_h = w[~spam].mean(); pw = w.mean()
    post = pw_s * ps / pw
    w2 = df["text"].str.lower().str.contains(r"\bcall\b")
    p2 = (w & w2)[spam].mean() * ps / (w & w2).mean()
    return [
        ("Prior", f"Before reading a message: P(spam) = **{ps:.3f}** ({int(spam.sum())} of {len(df):,} real SMS)."),
        ("Evidence: the word 'free'", f"P('free' | spam) = **{pw_s:.3f}**, P('free' | ham) = **{pw_h:.4f}**. Overall P('free') = {pw:.4f}."),
        ("Bayes' rule", f"P(spam | 'free') = P('free' | spam) × P(spam) / P('free') = {pw_s:.3f} × {ps:.3f} / {pw:.4f} = **{post:.3f}**. One word moved the belief from {pct(ps)} to {pct(post)}. Directly counting messages with 'free': {pct(spam[w].mean())} are spam (the same, as it must be). Adding 'call' too: P(spam | 'free' and 'call') = {p2:.3f}. Naive Bayes spam filters chain this for every word."),
    ], "Bayes' rule updates a prior belief with evidence: posterior ∝ likelihood × prior."


@walk("m-random-variables", "tips")
def _():
    df = D("tips")
    pmf = df["size"].value_counts(normalize=True).sort_index()
    xs = pmf.index.to_numpy(); ps_ = pmf.to_numpy()
    ex = float(np.sum(xs * ps_)); var = float(np.sum((xs - ex) ** 2 * ps_))
    tab = pd.DataFrame({"party size x": xs, "P(X = x)": ps_, "x · P(x)": xs * ps_})
    return [
        ("A random variable maps outcomes to numbers", f"X = party size of a random bill from the {len(df)} real bills. Its distribution (probability mass function):\n\n{t(tab, nd=3)}"),
        ("Expected value and variance", f"E[X] = Σ x · P(x) = **{ex:.3f}** people (the average party). Var(X) = Σ (x − E[X])² · P(x) = {var:.3f}; standard deviation {math.sqrt(var):.3f}."),
        ("Continuous variables", f"Y = tip in dollars can take any value, so we use ranges: P(Y > $5) = {(df.tip > 5).mean():.3f}, P($2 ≤ Y ≤ $4) = {((df.tip >= 2) & (df.tip <= 4)).mean():.3f}. E[Y] = {df.tip.mean():.2f}. Linearity: E[tip + bill] = E[tip] + E[bill] = {df.tip.mean():.2f} + {df.total_bill.mean():.2f} = {(df.tip + df.total_bill).mean():.2f}."),
    ], "A random variable turns outcomes into numbers; its distribution, expected value and variance summarise it."


@walk("m-distributions", ("titanic", "penguins", "sms"))
def _():
    from scipy import stats
    tf = D("titanic"); pg = D("penguins").dropna(); sms = D("sms")
    p = tf["Survived"].mean(); n = 10
    binom = pd.DataFrame({"survivors among 10 random passengers": range(0, 7), "binomial probability": stats.binom.pmf(range(0, 7), n, p),
                          "seen in 20,000 random groups": [np.mean(np.random.default_rng(0).binomial(n, p, 20000) == k) for k in range(0, 7)]})
    m = pg[(pg.species == "Gentoo") & (pg.sex == "MALE")]["body_mass_g"]
    mu, sd = m.mean(), m.std()
    within = pd.DataFrame([{"range": f"mean ± {k} sd", "normal says": pct(stats.norm.cdf(k) - stats.norm.cdf(-k)), "real male Gentoos": pct(((m > mu - k * sd) & (m < mu + k * sd)).mean())} for k in [1, 2]])
    sp = (sms["label"] == "spam").astype(int).values[:5000].reshape(50, 100).sum(1)
    pois = pd.DataFrame({"spam per 100 messages": range(8, 19, 2), "Poisson(λ = %.1f)" % sp.mean(): stats.poisson.pmf(range(8, 19, 2), sp.mean())})
    return [
        ("Binomial: count successes in n tries", f"P(survive) = {p:.3f}. Survivors in a random group of 10:\n\n{t(binom, nd=3)}"),
        ("Normal: measurements that cluster around a mean", f"Body mass of {len(m)} real male Gentoo penguins: mean {mu:.0f} g, sd {sd:.0f} g.\n\n{t(within)}"),
        ("Poisson: counts of rare events", f"Split the real SMS stream into 50 blocks of 100 messages and count spam: on average λ = {sp.mean():.1f} per block (min {sp.min()}, max {sp.max()}).\n\n{t(pois, nd=3)}"),
    ], "Common distributions describe common data-generating stories: successes in trials (binomial), measurements (normal), rare-event counts (Poisson)."


@walk("m-pdf-cdf", "penguins")
def _():
    from scipy import stats
    pg = D("penguins").dropna(); f = pg[pg.species == "Adelie"]["flipper_length_mm"]
    mu, sd = f.mean(), f.std()
    rows = pd.DataFrame([{"flipper length x (mm)": x, "pdf height": stats.norm.pdf(x, mu, sd), "normal CDF P(X ≤ x)": stats.norm.cdf(x, mu, sd), "real share ≤ x": (f <= x).mean()} for x in [180, 185, 190, 195, 200]])
    return [
        ("A real measurement", f"Flipper lengths of {len(f)} real Adelie penguins: mean {mu:.1f} mm, sd {sd:.1f} mm. Model them as normal."),
        ("PDF vs CDF", f"{t(rows, nd=3)}\n\nThe PDF is a density (height of the curve, per mm), not a probability. The CDF is a probability: the share of penguins at or below x, and the model's CDF tracks the real share closely."),
        ("Probabilities are areas", f"P(185 < X ≤ 195) = CDF(195) − CDF(185) = {stats.norm.cdf(195, mu, sd):.3f} − {stats.norm.cdf(185, mu, sd):.3f} = **{stats.norm.cdf(195, mu, sd) - stats.norm.cdf(185, mu, sd):.3f}**; in the data: {((f > 185) & (f <= 195)).mean():.3f}. The 90th percentile (inverse CDF): {stats.norm.ppf(0.9, mu, sd):.1f} mm vs real {f.quantile(0.9):.1f} mm."),
    ], "A PDF gives density; the CDF gives P(X ≤ x); probabilities of ranges are differences of the CDF (areas under the PDF)."


@walk("m-centre-spread", "housing")
def _():
    h = D("housing")["median_income"] * 10000
    q1, q3 = h.quantile([0.25, 0.75])
    tab = pd.DataFrame([{"measure": "mean", "value ($)": h.mean()}, {"measure": "median", "value ($)": h.median()}, {"measure": "standard deviation", "value ($)": h.std()}, {"measure": "IQR (Q3 − Q1)", "value ($)": q3 - q1}, {"measure": "min", "value ($)": h.min()}, {"measure": "max", "value ($)": h.max()}])
    h2 = pd.concat([h, pd.Series([5_000_000])])
    return [
        ("Real incomes", f"Median household income of {len(h):,} California districts (1990):\n\n{t(tab, nd=0)}"),
        ("Mean vs median", f"The mean ({h.mean():,.0f}) is above the median ({h.median():,.0f}): a long tail of rich districts pulls the mean up. Add one fake district earning $5,000,000: mean → **{h2.mean():,.0f}**, median → **{h2.median():,.0f}**. The median barely moves; it is robust."),
        ("Spread", f"Standard deviation {h.std():,.0f} measures typical distance from the mean (sensitive to outliers); IQR {q3 - q1:,.0f} covers the middle 50% of districts (robust). With the fake district the sd becomes {h2.std():,.0f}."),
    ], "Centre (mean, median) and spread (sd, IQR) summarise data; medians and IQRs resist outliers, means and sds don't."


@walk("m-normalization", "housing")
def _():
    h = D("housing").dropna().reset_index(drop=True)
    cols = ["median_income", "total_rooms", "housing_median_age"]
    x = h[cols].head(4)
    z = (x - h[cols].mean()) / h[cols].std(); mm = (x - h[cols].min()) / (h[cols].max() - h[cols].min())
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import cross_val_score
    y = h["median_house_value"]
    raw = -cross_val_score(KNeighborsRegressor(10), h[cols], y, cv=5, scoring="neg_root_mean_squared_error").mean()
    sc = -cross_val_score(make_pipeline(StandardScaler(), KNeighborsRegressor(10)), h[cols], y, cv=5, scoring="neg_root_mean_squared_error").mean()
    return [
        ("Different scales", f"Four real districts:\n\n{t(x)}\n\nRooms are in the thousands, income in single digits. Any method that uses distances would be dominated by rooms."),
        ("Standardise (z-score) and min-max", f"z = (x − mean) / sd:\n\n{t(z.round(2))}\n\nmin-max = (x − min) / (max − min), into 0–1:\n\n{t(mm.round(3))}"),
        ("Does it matter?", f"k-nearest-neighbours predicting house value (5-fold RMSE): raw columns **${raw / 1000:.0f}k**, standardised **${sc / 1000:.0f}k**. Fit the scaler on training data only, then apply the same numbers to test data."),
    ], "Normalisation puts features on comparable scales; distance-based and gradient-based methods need it."


@walk("m-sampling-ci", "titanic")
def _():
    df = D("titanic"); ages = df["Age"].dropna().values; true = ages.mean()
    rng = np.random.default_rng(0)
    s = rng.choice(ages, 50, replace=False); m, se = s.mean(), s.std(ddof=1) / math.sqrt(50)
    boots = [rng.choice(s, 50).mean() for _ in range(5000)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    cover = 0
    for _ in range(1000):
        x = rng.choice(ages, 50, replace=False); mm, ss = x.mean(), x.std(ddof=1) / math.sqrt(50)
        cover += (mm - 1.96 * ss <= true <= mm + 1.96 * ss)
    return [
        ("A sample of 50 passengers", f"The {len(ages)} passengers with known age have mean age **{true:.2f}** (treat this as the 'population'). A random sample of 50 has mean **{m:.2f}**."),
        ("How uncertain is that?", f"Standard error = sd / √n = {s.std(ddof=1):.2f} / √50 = {se:.2f}. 95% confidence interval: {m:.2f} ± 1.96 × {se:.2f} = **[{m - 1.96 * se:.2f}, {m + 1.96 * se:.2f}]**. Bootstrap (resample the 50 ages 5,000 times): [{lo:.2f}, {hi:.2f}]."),
        ("What '95%' means", f"Repeat: draw 1,000 different samples of 50 and build an interval from each. **{cover / 10:.1f}%** of the intervals contain the true mean {true:.2f}. The method is right about 95% of the time; any single interval either contains it or not."),
    ], "A sample estimate comes with a standard error; confidence intervals turn it into a range that captures the truth at a known rate."


@walk("m-hypothesis", "tips")
def _():
    from scipy import stats
    df = D("tips"); p = df["tip"] / df["total_bill"] * 100
    a, b = p[df["time"] == "Dinner"].values, p[df["time"] == "Lunch"].values
    obs = a.mean() - b.mean(); rng = np.random.default_rng(0); allp = np.r_[a, b]
    perm = []
    for _ in range(10000):
        rng.shuffle(allp); perm.append(allp[:len(a)].mean() - allp[len(a):].mean())
    pval = np.mean(np.abs(perm) >= abs(obs))
    tt = stats.ttest_ind(a, b, equal_var=False)
    ct = pd.crosstab(df["smoker"], df["size"] >= 3); chi = stats.chi2_contingency(ct)
    return [
        ("Question and null hypothesis", f"Do people tip a different percentage at dinner than at lunch? Dinner: {a.mean():.2f}% ({len(a)} bills); lunch: {b.mean():.2f}% ({len(b)}). Difference **{obs:+.2f}** points. Null hypothesis H₀: no real difference; this gap is just luck."),
        ("Permutation test", f"If H₀ is true, the dinner/lunch labels are arbitrary. Shuffle them 10,000 times and recompute the gap: {pct(pval, 1)} of shuffles give a gap at least as big. That's the **p-value = {pval:.3f}**. Welch's t-test agrees: p = {tt.pvalue:.3f}."),
        ("Decide and report", f"{'p > 0.05: no evidence of a difference (which is not proof that there is none).' if pval > 0.05 else 'p < 0.05: unlikely to be luck alone.'} Another test on the same data: are smokers more often in parties of 3+? Chi-squared test p = {chi.pvalue:.3f}. Report effect sizes and intervals, not just p-values."),
    ], "A hypothesis test asks how surprising the data would be if nothing were going on; the p-value measures that surprise."


@walk("m-correlation", "mpg")
def _():
    df = D("mpg").dropna()
    cols = ["mpg", "weight", "horsepower", "acceleration", "model_year"]
    C = df[cols].corr().round(2)
    rs = df[["weight", "mpg"]].corr(method="spearman").iloc[0, 1]
    return [
        ("Correlation matrix of real cars", f"Pearson correlation (−1 to 1) between pairs of columns for {len(df)} cars:\n\n{t(C, index=True)}"),
        ("Read it", f"Heavier cars do fewer miles per gallon (r = {C.loc['weight', 'mpg']}); weight and horsepower move together (r = {C.loc['weight', 'horsepower']}). Newer model years do better (r = {C.loc['model_year', 'mpg']}). Spearman (rank) correlation of weight and mpg is {rs:.2f}: the relationship is monotonic but curved."),
        ("Correlation is not causation", "Newer cars get better mpg partly because they are lighter, so year and weight are tangled together. Correlation also only sees straight-line (Pearson) or monotonic (Spearman) patterns, and one outlier can change it a lot: always plot the data."),
    ], "Correlation measures how two variables move together; it says nothing on its own about cause."


@walk("m-info-theory", "titanic")
def _():
    df = D("titanic")
    H = lambda p: -sum(x * math.log2(x) for x in p if x > 0)
    ps = df["Survived"].mean(); h0 = H([ps, 1 - ps])
    rows = []
    for col in ["Sex", "Pclass", "Embarked"]:
        g = df.groupby(col)["Survived"].agg(["mean", "size"])
        hc = sum(r["size"] / len(df) * H([r["mean"], 1 - r["mean"]]) for _, r in g.iterrows())
        rows.append({"split by": col, "entropy after the split (bits)": hc, "information gain (bits)": h0 - hc})
    q = df.groupby("Pclass")["Survived"].mean()
    ce = -np.mean(np.log(np.where(df["Survived"] == 1, df["Pclass"].map(q), 1 - df["Pclass"].map(q))))
    return [
        ("Entropy = uncertainty in bits", f"P(survived) = {ps:.3f}. Entropy H = −Σ p log₂ p = **{h0:.3f} bits** (1 bit would be a fair coin)."),
        ("Information gain", f"How much does knowing one column reduce the uncertainty about survival?\n\n{t(pd.DataFrame(rows), nd=3)}\n\nSex tells us the most; this is exactly how a decision tree picks its first split."),
        ("Cross-entropy = the loss of a classifier", f"Predict each passenger's survival probability as the survival rate of their class. Average −log(probability given to what actually happened) = **{ce:.3f} nats**. That's the log loss used to train logistic regression and neural networks; lower means better predictions."),
    ], "Entropy measures uncertainty, information gain measures how much a feature reduces it, and cross-entropy scores probabilistic predictions."
