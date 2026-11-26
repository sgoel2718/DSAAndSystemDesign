"""Real-data walkthroughs: Supervised learning."""
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt

def _titanic_X():
    df = D("titanic").copy()
    df["Age"] = df["Age"].fillna(df["Age"].median())
    X = pd.DataFrame({"is_female": (df["Sex"] == "female").astype(int), "Pclass": df["Pclass"], "Age": df["Age"], "Fare": df["Fare"]})
    return df, X, df["Survived"]


@walk("m-linear-regression", "housing")
def _():
    df = D("housing").dropna()
    from sklearn.linear_model import LinearRegression
    X = df[["median_income", "housing_median_age"]]; y = df["median_house_value"] / 1000
    m = LinearRegression().fit(X, y)
    ex = df.head(4)[["median_income", "housing_median_age", "median_house_value"]].copy()
    ex["predicted"] = m.predict(ex[["median_income", "housing_median_age"]]) * 1000
    r = ex.iloc[0]
    return [
        ("The data", f"Each row is a district. We'll predict median house value from median income (×$10k) and median house age (years).\n\n{t(ex[['median_income', 'housing_median_age', 'median_house_value']])}"),
        ("What the model learned", f"value (in $k) = **{m.intercept_:.1f}** + **{m.coef_[0]:.1f}** × income + **{m.coef_[1]:.2f}** × age.\n\nEach extra $10k of median income adds about ${m.coef_[0]:.0f}k; each extra year of house age adds about ${m.coef_[1] * 1000:,.0f}, holding income fixed."),
        ("Predict the first district by hand", f"{m.intercept_:.1f} + {m.coef_[0]:.1f} × {r['median_income']:.2f} + {m.coef_[1]:.2f} × {r['housing_median_age']:.0f} = **{r['predicted'] / 1000:.1f}k**, while the real value is {r['median_house_value'] / 1000:.1f}k.\n\n{t(ex)}"),
        ("How good overall", f"R² = **{m.score(X, y):.2f}**: income and age explain about {pct(m.score(X, y))} of the variation in house values. Location, which we left out, explains much of the rest."),
    ], "Linear regression = a weighted sum of features; each weight is readable as 'how much the prediction moves per unit'."


@walk("m-logistic-regression", "titanic")
def _():
    df, X, y = _titanic_X()
    from sklearn.linear_model import LogisticRegression
    m = LogisticRegression(max_iter=2000).fit(X, y)
    ex = df.iloc[[0, 1, 2, 7]][["Who", "Sex", "Pclass", "Age", "Fare", "Survived"]].copy()
    z = m.decision_function(X.iloc[[0, 1, 2, 7]]); p = m.predict_proba(X.iloc[[0, 1, 2, 7]])[:, 1]
    ex["score z"] = z; ex["P(survive)"] = p
    w = pd.Series(m.coef_[0], index=X.columns).round(3)
    return [
        ("The learned weights", f"{t(w.rename('weight').to_frame(), index=True, nd=4)}\n\nBeing female pushes the score up a lot; each step down in class (1st → 3rd) and each year of age push it down."),
        ("Score each passenger", f"z = {m.intercept_[0]:.2f} + weights × features, then P = 1 / (1 + e^(−z)):\n\n{t(ex, nd=2)}"),
        ("Decide", f"P ≥ 0.5 → predict \"survived\". Overall training accuracy: **{pct(m.score(X, y))}**. Notice Florence Cumings (1st class, female) gets a high probability and Owen Braund (3rd class, male) a low one."),
    ], "Logistic regression turns a weighted score into a probability with the sigmoid curve."


@walk("m-multiclass", "penguins")
def _():
    df = D("penguins").dropna()
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(df[cols], df["species"])
    ex = df.sample(4, random_state=3)
    P = pd.DataFrame(m.predict_proba(ex[cols]), columns=[f"P({c})" for c in m.classes_]).round(3)
    out = pd.concat([ex[["species"] + cols[:2]].reset_index(drop=True), P], axis=1)
    out["predicted"] = m.predict(ex[cols])
    return [
        ("Three classes", f"{df['species'].value_counts().to_dict()}"),
        ("Softmax gives one probability per species", f"{t(out, nd=3)}\n\nEach row's probabilities add up to 1; the largest one is the prediction."),
        ("Multi-label is different", "If we also wanted tags like \"heavy\" and \"long flippers\" at the same time, each tag would get its own yes/no sigmoid, and a penguin could have both."),
    ], "Multiclass = one answer among many (softmax); multi-label = several independent yes/no answers."


@walk("m-knn", "penguins")
def _():
    df = D("penguins").dropna().reset_index(drop=True)
    from sklearn.preprocessing import StandardScaler
    cols = ["bill_length_mm", "flipper_length_mm"]
    sc = StandardScaler().fit(df[cols]); Z = sc.transform(df[cols])
    q = 10; d = np.sqrt(((Z - Z[q]) ** 2).sum(1)); d[q] = np.inf
    nn = np.argsort(d)[:5]
    nb = df.loc[nn, ["species"] + cols].assign(distance=d[nn])
    raw = np.sqrt(((df[["bill_length_mm", "body_mass_g"]].values - df.loc[q, ["bill_length_mm", "body_mass_g"]].values.astype(float)) ** 2).sum(1))
    return [
        ("A penguin to classify", f"Pretend we don't know this penguin's species:\n\n{t(df.loc[[q], cols])}"),
        ("Scale, then find the 5 nearest penguins", f"{t(nb, nd=3)}"),
        ("Vote", f"The 5 neighbours vote: {nb['species'].value_counts().to_dict()} → predict **{nb['species'].mode()[0]}**. The true species is **{df.loc[q, 'species']}**."),
        ("Why scaling matters", "If we used body mass in grams together with bill length in mm without scaling, a 100 g difference would count as much as a 100 mm bill difference; mass would decide every distance."),
    ], "k-NN copies the majority answer of the most similar known examples, so the distance (and scaling) is everything."


@walk("m-decision-tree", "titanic")
def _():
    df, X, y = _titanic_X()
    from sklearn.tree import DecisionTreeClassifier, export_text
    tr = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
    rules = export_text(tr, feature_names=list(X.columns), show_weights=True)
    g = lambda p: 1 - p ** 2 - (1 - p) ** 2
    pf, pm = y[X.is_female == 1].mean(), y[X.is_female == 0].mean()
    nf, nm = (X.is_female == 1).sum(), (X.is_female == 0).sum()
    ex = df.iloc[[0, 1, 7, 9]][["Who", "Sex", "Pclass", "Age", "Survived"]].copy()
    ex["tree says"] = np.where(tr.predict(X.iloc[[0, 1, 7, 9]]) == 1, "survived", "died")
    return [
        ("Start: everyone in one box", f"891 passengers, {pct(y.mean())} survived. Gini impurity = 1 − p² − (1−p)² = **{g(y.mean()):.3f}** (very mixed)."),
        ("First question: sex", f"Women: {nf} passengers, {pct(pf)} survived, Gini {g(pf):.3f}. Men: {nm}, {pct(pm)} survived, Gini {g(pm):.3f}. Weighted Gini = **{(nf * g(pf) + nm * g(pm)) / 891:.3f}**, the biggest drop of any question, so the tree splits on sex first."),
        ("The tree after two levels", f"```\n{rules}```\nValues in brackets are [died, survived] counts in each leaf."),
        ("Follow real passengers down the tree", f"{t(ex)}" + ("" if (ex['tree says'].eq('survived').astype(int) == ex['Survived']).all() else "\n\nThe tree is wrong about " + ", ".join(ex.loc[ex['tree says'].eq('survived').astype(int) != ex['Survived'], 'Who']) + ": the leaf they fall into usually had the other outcome. Trees give the majority answer of their box.")),
    ], "A tree keeps asking the yes/no question that makes the groups purest."


@walk("m-bootstrap-bagging", "titanic")
def _():
    df, X, y = _titanic_X()
    rng = np.random.default_rng(0)
    idx = rng.integers(0, 891, 891)
    counts = pd.Series(idx).value_counts()
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import BaggingClassifier
    from sklearn.model_selection import cross_val_score
    who = [1, 7]
    preds = []
    for b in range(5):
        s = rng.integers(0, 891, 891)
        m = DecisionTreeClassifier(random_state=b).fit(X.iloc[s], y.iloc[s])
        preds.append(m.predict_proba(X.iloc[who])[:, 1])
    P = pd.DataFrame(np.array(preds).T, columns=[f"tree {i + 1}" for i in range(5)]); P.insert(0, "passenger", df.loc[who, "Who"].values); P["average"] = np.array(preds).mean(0)
    one = cross_val_score(DecisionTreeClassifier(random_state=0), X, y, cv=5).mean()
    bag = cross_val_score(BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, random_state=0), X, y, cv=5).mean()
    return [
        ("Draw a bootstrap sample of passengers", f"Pick 891 passengers at random **with replacement**: {(counts == 2).sum()} appear twice, {(counts >= 3).sum()} three or more times, and {891 - counts.size} ({pct((891 - counts.size) / 891)}) are left out (out-of-bag)."),
        ("Each tree sees a different sample", f"P(survive) from 5 trees, each trained on its own bootstrap sample:\n\n{t(P, nd=2)}\n\nSingle trees disagree; the average is steadier."),
        ("Bagging 100 trees", f"Cross-validated accuracy: one tree **{pct(one, 1)}**, 100 bagged trees **{pct(bag, 1)}**."),
    ], "Bagging averages many models trained on resampled data, cancelling much of each one's randomness."


@walk("m-random-forest", "housing")
def _():
    df = D("housing").dropna()
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    X = pd.get_dummies(df.drop(columns="median_house_value"), dtype=int); y = df["median_house_value"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0)
    rf = RandomForestRegressor(n_estimators=200, max_features="sqrt", random_state=0, n_jobs=-1).fit(Xtr, ytr)
    imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(5).round(3)
    r = Xte.iloc[[0]]
    per_tree = np.array([e.predict(r.values)[0] for e in rf.estimators_[:5]])
    return [
        ("One district, many trees", f"The first test district (true value **${yte.iloc[0]:,.0f}**). Five of the 200 trees predict: {', '.join(f'${v:,.0f}' for v in per_tree)}."),
        ("Average all 200", f"The forest's prediction is the average of all trees: **${rf.predict(r)[0]:,.0f}**. Over all test districts R² = **{rf.score(Xte, yte):.3f}**."),
        ("What the forest relies on", f"{t(imp.rename('importance').to_frame(), index=True)}\n\nMedian income dominates, followed by location (inland vs coast, latitude/longitude)."),
    ], "A random forest averages many decorrelated trees and tells you which features it used most."


@walk("m-voting-stacking", "cancer")
def _():
    df = D("cancer")
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    X = df.drop(columns=["target", "diagnosis"]); y = df["target"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, random_state=2, stratify=y)
    base = [("logreg", make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))), ("knn", make_pipeline(StandardScaler(), KNeighborsClassifier())), ("forest", RandomForestClassifier(random_state=0))]
    fitted = {n: m.fit(Xtr, ytr) for n, m in base}
    hard = [i for i in range(len(Xte)) if len({fitted[n].predict(Xte.iloc[[i]])[0] for n in fitted}) > 1][:3]
    rows = []
    for i in hard:
        r = {"biopsy": i, "true": df["diagnosis"].iloc[Xte.index[i]]}
        for n in fitted: r[f"P(benign) {n}"] = fitted[n].predict_proba(Xte.iloc[[i]])[0, 1]
        r["soft vote"] = np.mean([r[f"P(benign) {n}"] for n in fitted]); rows.append(r)
    scores = {n: m.score(Xte, yte) for n, m in fitted.items()}
    scores["soft vote"] = VotingClassifier(base, voting="soft").fit(Xtr, ytr).score(Xte, yte)
    scores["stacking"] = StackingClassifier(base, final_estimator=LogisticRegression()).fit(Xtr, ytr).score(Xte, yte)
    return [
        ("Biopsies where the models disagree", f"{t(pd.DataFrame(rows), nd=2)}\n\nAveraging the three probabilities settles the disagreement."),
        ("Accuracy on 228 test biopsies", f"{t(pd.Series(scores).rename('accuracy').to_frame(), index=True, nd=3)}"),
        ("What to conclude", ("Combining matched or beat the best single model: the three make different mistakes, so averaging cancels some." if max(scores['soft vote'], scores['stacking']) >= max(scores['logreg'], scores['knn'], scores['forest']) else f"Here the best single model (logistic regression, {scores['logreg']:.3f}) is already as good as the ensembles: on this clean dataset the models are already very accurate, so there is little left for combining to fix. Ensembles help most when the models are weaker and err in different places; they still make predictions steadier, as the disagreement table shows.")),
    ], "Ensembles combine models that err differently; voting averages them, stacking learns the combination."


@walk("m-adaboost", "titanic")
def _():
    df, X, y = _titanic_X()
    from sklearn.tree import DecisionTreeClassifier
    w = np.full(891, 1 / 891); rows = []
    stumps = []
    for k in range(3):
        s = DecisionTreeClassifier(max_depth=1).fit(X, y, sample_weight=w)
        wrong = s.predict(X) != y.values
        err = w[wrong].sum(); alpha = 0.5 * np.log((1 - err) / err)
        f = X.columns[s.tree_.feature[0]]; thr = s.tree_.threshold[0]
        rows.append({"round": k + 1, "stump question": f"{f} ≤ {thr:.1f}", "weighted error": err, "say (alpha)": alpha, "weight of passenger 'Cumings' before": w[1] * 891})
        w = w * np.exp(np.where(wrong, alpha, -alpha)); w /= w.sum()
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.model_selection import cross_val_score
    acc1 = cross_val_score(DecisionTreeClassifier(max_depth=1), X, y, cv=5).mean()
    acc = cross_val_score(AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=100, random_state=0), X, y, cv=5).mean()
    return [
        ("Three rounds of boosting on the passengers", f"{t(pd.DataFrame(rows), nd=3)}\n\n(Passenger weights are shown ×891, so 1 means 'normal'.)"),
        ("What changed between rounds", "Round 1 splits on sex. The passengers it got wrong (women who died, men who survived) get heavier, so round 2's stump looks for a question that fixes many of them, such as class or fare."),
        ("Final model", f"One stump: **{pct(acc1, 1)}** accuracy. 100 boosted stumps voting with their alphas: **{pct(acc, 1)}**."),
    ], "Boosting trains weak models one after another, each focusing on the examples the previous ones got wrong."


@walk("m-gradient-boosting", "housing")
def _():
    df = D("housing").dropna().head(1500)
    from sklearn.tree import DecisionTreeRegressor
    X = pd.get_dummies(df.drop(columns="median_house_value"), dtype=int); y = df["median_house_value"].values / 1000
    pred = np.full(len(y), y.mean()); show = [0, 1, 2]
    rows = [{"round": 0, **{f"district {i + 1}": pred[i] for i in show}, "RMSE ($k)": np.sqrt(((y - pred) ** 2).mean())}]
    for r in range(1, 51):
        tree = DecisionTreeRegressor(max_depth=3).fit(X, y - pred); pred = pred + 0.3 * tree.predict(X)
        if r in (1, 2, 10, 50): rows.append({"round": r, **{f"district {i + 1}": pred[i] for i in show}, "RMSE ($k)": np.sqrt(((y - pred) ** 2).mean())})
    return [
        ("Three real districts", f"True values: {', '.join(f'district {i + 1} = ${y[i]:.0f}k' for i in show)}."),
        ("Start from the average, then add trees that fix the errors", f"Each round fits a small tree to the current errors and adds 30% of its correction (learning rate 0.3):\n\n{t(pd.DataFrame(rows), nd=1)}"),
        ("Read it", (f"The overall error (RMSE) falls every round, from {rows[0]['RMSE ($k)']:.0f}k to {rows[-1]['RMSE ($k)']:.0f}k. Individual districts can still move the wrong way or overshoot (" + ", ".join(f"district {i + 1}" for i in show if abs(rows[-1][f'district {i + 1}'] - y[i]) > abs(rows[0][f'district {i + 1}'] - y[i])) + " here), because each small tree corrects the average error of a whole group of similar districts, not each district on its own. Real libraries (XGBoost, LightGBM) use hundreds of trees and early stopping.") if any(abs(rows[-1][f'district {i + 1}'] - y[i]) > abs(rows[0][f'district {i + 1}'] - y[i]) for i in show) else f"Every district moves from the overall average toward its true value and the overall error falls from {rows[0]['RMSE ($k)']:.0f}k to {rows[-1]['RMSE ($k)']:.0f}k."),
    ], "Gradient boosting starts with a simple guess and keeps adding small trees that predict what's still wrong."


@walk("m-svm", "penguins")
def _():
    df = D("penguins").dropna()
    pair = df[df["species"].isin(["Adelie", "Gentoo"])].reset_index(drop=True)
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    cols = ["bill_depth_mm", "flipper_length_mm"]
    sc = StandardScaler().fit(pair[cols]); Z = sc.transform(pair[cols])
    rows = []
    for C in [0.01, 1, 100]:
        m = SVC(kernel="linear", C=C).fit(Z, pair["species"])
        rows.append({"C": C, "support vectors": int(m.n_support_.sum()), "margin width (scaled units)": 2 / np.linalg.norm(m.coef_), "training accuracy": m.score(Z, pair["species"])})
    m = SVC(kernel="linear", C=1).fit(Z, pair["species"])
    sv = pair.loc[m.support_, ["species"] + cols]
    return [
        ("Two species to separate", f"{len(pair)} Adelie and Gentoo penguins, using bill depth and flipper length."),
        ("The penguins that define the boundary", f"With C = 1, only these {len(sv)} penguins (the support vectors) sit on the edge of the margin:\n\n{t(sv)}\n\nMove any other penguin and the boundary stays the same."),
        ("Effect of C", f"{t(pd.DataFrame(rows), nd=3)}\n\nSmall C allows a wide street with more penguins touching it; large C squeezes the street to avoid any violation."),
    ], "An SVM draws the widest possible street between classes, decided only by the closest examples."


@walk("m-kernels", "penguins")
def _():
    df = D("penguins").dropna()
    pair = df[df["species"].isin(["Adelie", "Chinstrap"])].reset_index(drop=True)
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import cross_val_score
    cols = ["bill_depth_mm", "body_mass_g"]
    rows = []
    for name, m in [("linear", SVC(kernel="linear")), ("polynomial (degree 3)", SVC(kernel="poly", degree=3)), ("RBF gamma=1", SVC(kernel="rbf", gamma=1)), ("RBF gamma=100", SVC(kernel="rbf", gamma=100))]:
        rows.append({"kernel": name, "cross-validated accuracy": cross_val_score(make_pipeline(StandardScaler(), m), pair[cols], pair["species"], cv=5).mean()})
    Z = StandardScaler().fit_transform(pair[cols])
    k = lambda a, b, g=1: np.exp(-g * ((Z[a] - Z[b]) ** 2).sum())
    d0 = ((Z - Z[0]) ** 2).sum(1); d0[0] = np.inf; near = int(d0.argmin()); d0[0] = -1; far = int(d0.argmax())
    accs = [r["cross-validated accuracy"] for r in rows]
    return [
        ("A harder pair", f"Adelie vs Chinstrap using bill depth and body mass: the two species overlap heavily ({len(pair)} penguins)."),
        ("RBF similarity between real penguins", f"Penguin 0 vs its most similar penguin ({near}): **{k(0, near):.3f}**. Penguin 0 vs its least similar penguin ({far}): **{k(0, far):.5f}**. Near-identical penguins score close to 1, very different ones close to 0."),
        ("Compare kernels", f"{t(pd.DataFrame(rows), nd=3)}\n\nEvery kernel lands between {min(accs):.0%} and {max(accs):.0%}: bending the boundary can't help, because these two species really do overlap on these two features. Using bill length instead would separate them easily."),
    ], "Kernels let an SVM bend its boundary, but they can't create information the features don't have."


@walk("m-interpretability", "titanic")
def _():
    df, X, y = _titanic_X()
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import train_test_split
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0)
    rf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=0).fit(Xtr, ytr)
    pi = permutation_importance(rf, Xte, yte, n_repeats=20, random_state=0)
    imp = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)
    base = rf.predict_proba(Xte)[:, 1].mean()
    who = 1; row = X.iloc[[who]].copy(); p0 = rf.predict_proba(row)[0, 1]
    contrib = []
    for c in X.columns:
        r2 = row.copy(); r2[c] = X[c].median(); contrib.append({"feature": c, "her value": row[c].iloc[0], "P(survive) if typical value": rf.predict_proba(r2)[0, 1]})
    cdf = pd.DataFrame(contrib); top2 = cdf.nsmallest(2, "P(survive) if typical value")["feature"].tolist()
    return [
        ("Global: which features matter (permutation importance)", f"Shuffle one column in the test passengers and see how much accuracy drops:\n\n{t(imp.rename('accuracy drop').to_frame(), index=True, nd=3)}"),
        ("Local: why did Florence Cumings get her prediction?", f"Average predicted survival is {pct(base)}; for her it is **{pct(p0)}**. Replace one feature at a time by the typical (median) passenger's value:\n\n{t(cdf, nd=3)}\n\nChanging **{top2[0]}** or **{top2[1]}** to the typical value drops her chance the most, so being a first-class woman is the main reason for her high prediction."),
        ("Use it", "Global importance explains the model to a manager; local explanations (this, or SHAP values) explain one decision to the person affected."),
    ], "Interpretability answers 'what matters overall' and 'why this one prediction'."


def _pen2(a, b, cols):
    pg = D("penguins").dropna().reset_index(drop=True)
    d = pg[pg["species"].isin([a, b])].reset_index(drop=True)
    return d, d[cols].to_numpy(float), (d["species"] == b).astype(int).to_numpy()


@walk("m-linear-classification", "penguins")
def _():
    from sklearn.linear_model import Perceptron, LogisticRegression
    from sklearn.svm import LinearSVC
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.model_selection import cross_val_score
    cols = ["bill_depth_mm", "flipper_length_mm"]
    d, X, y = _pen2("Adelie", "Gentoo", cols)
    mu, sd = X.mean(0), X.std(0); Z = (X - mu) / sd
    rows = []; models = {}
    for name, m in [("perceptron", Perceptron(random_state=0)), ("logistic regression", LogisticRegression()), ("linear SVM", LinearSVC(C=1.0)), ("LDA", LinearDiscriminantAnalysis())]:
        m.fit(Z, y); w, b = m.coef_[0], m.intercept_[0]; models[name] = m
        # boundary in real units: flipper = a + c·depth
        wr = w / sd; br = b - (w * mu / sd).sum(); a_, c_ = -br / wr[1], -wr[0] / wr[1]
        rows.append({"method": name, "boundary (real units)": f"flipper = {a_:.1f} {'+' if c_ >= 0 else '−'} {abs(c_):.2f} × bill depth", "training accuracy": m.score(Z, y),
                     "closest penguin to the line (sd units)": np.min(np.abs(Z @ w + b)) / np.linalg.norm(w)})
    lr = models["logistic regression"]
    pick = [int(np.argmin(np.abs(Z @ lr.coef_[0] + lr.intercept_[0])))] + [0, len(d) - 1]
    ex = d.loc[pick, ["species"] + cols].assign(**{"score w·x + b": (Z[pick] @ lr.coef_[0] + lr.intercept_[0]), "prediction": np.where(lr.predict(Z[pick]) == 1, "Gentoo", "Adelie")})
    d2, X2, y2 = _pen2("Adelie", "Chinstrap", cols)
    hard = cross_val_score(LogisticRegression(), (X2 - X2.mean(0)) / X2.std(0), y2, cv=5).mean()
    d3, X3, y3 = _pen2("Adelie", "Chinstrap", ["bill_length_mm", "bill_depth_mm"])
    fixed = cross_val_score(LogisticRegression(), (X3 - X3.mean(0)) / X3.std(0), y3, cv=5).mean()
    best = max(rows, key=lambda r: r["closest penguin to the line (sd units)"])["method"]
    return [
        ("Four methods, same straight-line rule", f"{len(d)} real Adelie and Gentoo penguins, 2 measurements each. Every method learns a score w·x + b and draws the line where it is 0:\n\n{t(pd.DataFrame(rows), nd=3)}\n\nAll four separate the species perfectly, but they pick different lines. The **{best}** leaves the widest gap to the nearest penguin, because maximising that gap (the margin) is exactly what it optimises."),
        ("Scoring real penguins", f"Logistic regression's score for three penguins (positive → Gentoo):\n\n{t(ex, nd=2)}\n\nThe first one is the penguin nearest the line: its score is close to 0, so it's the least certain."),
        ("When a straight line isn't enough", f"Adelie vs Chinstrap on the same two measurements: their clouds overlap, and the best line is right only **{pct(hard)}** of the time (5-fold). Switching to bill length + bill depth, where Chinstraps stand out, the same linear model scores **{pct(fixed)}**: often the fix is a better feature, not a more complex model."),
    ], "Linear classifiers all predict by which side of a straight line a point falls on; the method only decides which line, and good features decide whether a line can work at all."


@walk("m-naive-bayes", "sms")
def _():
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    df = D("sms"); y = (df["label"] == "spam").astype(int).to_numpy()
    tr, te, ytr, yte = train_test_split(df["text"], y, test_size=0.25, stratify=y, random_state=0)
    vec = CountVectorizer(); A = vec.fit_transform(tr); B = vec.transform(te)
    nb = MultinomialNB(alpha=1.0).fit(A, ytr)
    voc = vec.vocabulary_; prior = np.exp(nb.class_log_prior_)
    words = [w for w in ["free", "call", "now", "lunch", "home", "prize"] if w in voc]
    lik = pd.DataFrame({"word": words, "count in spam": [int(nb.feature_count_[1, voc[w]]) for w in words], "count in ham": [int(nb.feature_count_[0, voc[w]]) for w in words],
                        "ps": [np.exp(nb.feature_log_prob_[1, voc[w]]) for w in words], "ph": [np.exp(nb.feature_log_prob_[0, voc[w]]) for w in words]})
    lik["spam ÷ ham"] = (lik["ps"] / lik["ph"]).map(lambda v: f"{v:.2g}" if v < 10 else f"{v:.0f}")
    lik["P(word ∣ spam)"] = lik.pop("ps").map(lambda v: f"{v:.2g}"); lik["P(word ∣ ham)"] = lik.pop("ph").map(lambda v: f"{v:.2g}")
    lik = lik[["word", "count in spam", "count in ham", "P(word ∣ spam)", "P(word ∣ ham)", "spam ÷ ham"]]
    msg = "free call now"
    ls = np.log(prior[1]) + sum(nb.feature_log_prob_[1, voc[w]] for w in msg.split()); lh = np.log(prior[0]) + sum(nb.feature_log_prob_[0, voc[w]] for w in msg.split())
    p_hand = 1 / (1 + np.exp(lh - ls)); p_sk = nb.predict_proba(vec.transform([msg]))[0, 1]
    rng = np.random.default_rng(0); rows = []
    for n in [30, 100, len(tr)]:
        r = {"labelled messages": n}
        sc = {"NB": [], "LR": []}
        for rep in range(5 if n < len(tr) else 1):
            idx = rng.choice(len(tr), n, replace=False) if n < len(tr) else np.arange(len(tr))
            while ytr[idx].sum() == 0: idx = rng.choice(len(tr), n, replace=False)
            v = CountVectorizer().fit(tr.iloc[idx]); a, b = v.transform(tr.iloc[idx]), v.transform(te)
            sc["NB"].append(f1_score(yte, MultinomialNB().fit(a, ytr[idx]).predict(b)))
            sc["LR"].append(f1_score(yte, LogisticRegression(max_iter=2000, C=10).fit(a, ytr[idx]).predict(b)))
        r["Naive Bayes spam F1"] = np.mean(sc["NB"]); r["logistic regression spam F1"] = np.mean(sc["LR"]); rows.append(r)
    return [
        ("Count words per class", f"{len(tr):,} real training SMS. Prior P(spam) = **{prior[1]:.3f}**. With Laplace smoothing (add 1 to every count):\n\n{t(lik, nd=4)}"),
        ("Score a new message by hand", f"“{msg}”: spam score = log P(spam) + Σ log P(word ∣ spam) = **{ls:.2f}**; ham score = **{lh:.2f}**. P(spam) = 1 / (1 + e^(ham − spam)) = **{p_hand:.4f}**; scikit-learn gives {p_sk:.4f}. Words multiply their evidence, so three mildly spam-ish words together make spam very likely."),
        ("Little data? Naive Bayes shines", f"Test spam F1 on {len(te):,} unseen messages (averaged over 5 random training sets for the small sizes):\n\n{t(pd.DataFrame(rows), nd=3)}\n\n{'With few labels Naive Bayes beats logistic regression clearly; with all the data they end up close.' if rows[0]['Naive Bayes spam F1'] > rows[0]['logistic regression spam F1'] else 'Here the two are close even with few labels.'}"),
    ], "Naive Bayes multiplies per-word evidence with the class prior; it's crude but fast and especially strong when labelled data is scarce."


@walk("m-discriminant-analysis", "penguins")
def _():
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA, QuadraticDiscriminantAnalysis as QDA
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    pg = D("penguins").dropna().reset_index(drop=True)
    two = pg[pg.species.isin(["Adelie", "Gentoo"])]; f = two["flipper_length_mm"].to_numpy(float); s = (two["species"] == "Gentoo").to_numpy()
    m1, m2 = f[~s].mean(), f[s].mean(); sd = np.sqrt((((f[~s] - m1) ** 2).sum() + ((f[s] - m2) ** 2).sum()) / (len(f) - 2)); pa, pgn = (~s).mean(), s.mean()
    mid = (m1 + m2) / 2; shift = sd ** 2 * np.log(pgn / pa) / (m1 - m2); bnd = mid + shift
    acc1 = ((f > bnd) == s).mean()
    feats = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    X, y = pg[feats].to_numpy(float), pg["species"].to_numpy(); cv = StratifiedKFold(5, shuffle=True, random_state=0)
    comp = pd.DataFrame([{"model": n, "5-fold accuracy": cross_val_score(m, X, y, cv=cv).mean()} for n, m in [("LDA (shared spread, straight boundaries)", LDA()), ("QDA (own spread per class, curved)", QDA(reg_param=0.05)), ("logistic regression", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)))]])
    rng = np.random.default_rng(0); small = {"LDA": [], "QDA": []}
    for r in range(10):
        idx = np.concatenate([rng.choice(np.where(y == k)[0], 6, replace=False) for k in np.unique(y)]); test = np.setdiff1d(np.arange(len(y)), idx)
        small["LDA"].append(LDA().fit(X[idx], y[idx]).score(X[test], y[test]))
        try: small["QDA"].append(QDA().fit(X[idx], y[idx]).score(X[test], y[test]))
        except Exception: small["QDA"].append(np.nan)
    return [
        ("One feature by hand", f"Flipper length of {len(f)} real penguins. Adelie mean **{m1:.1f} mm**, Gentoo mean **{m2:.1f} mm**, pooled spread (sd) **{sd:.1f} mm**; {pct(pa)} of them are Adelie. LDA's boundary = midpoint {mid:.1f} + sd² × ln(P(Gentoo)/P(Adelie)) / (mean_A − mean_G) = {mid:.1f} {shift:+.2f} = **{bnd:.1f} mm**. The more common species gets a little extra room. This single cut classifies {pct(acc1, 1)} of the penguins correctly."),
        ("All four measurements, three species", f"{t(comp, nd=3)}\n\nWith {len(y)} penguins all three do about equally well: the species really are roughly Gaussian clouds."),
        ("Why LDA is the safer choice with little data", f"Train on only **6 penguins per species**, test on the rest (10 repeats): LDA **{pct(np.nanmean(small['LDA']), 1)}**, QDA **{pct(np.nanmean(small['QDA']), 1)}**. QDA must estimate a separate 4 × 4 spread matrix for each species from 6 birds; LDA pools all 18 into one."),
    ], "LDA and QDA classify by asking which class's Gaussian cloud a point most likely came from; shared spread gives straight, stable boundaries, separate spreads give curved ones that need more data."


@walk("m-threshold-calibration", "cancer")
def _():
    from sklearn.naive_bayes import GaussianNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import brier_score_loss
    df = D("cancer"); X = df.drop(columns=["target", "diagnosis"]).to_numpy(); y = (df["target"] == 0).astype(int).to_numpy()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, stratify=y, random_state=0)
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xtr, ytr); p = lr.predict_proba(Xte)[:, 1]
    rows = []
    for th in [0.05, 0.2, 0.5, 0.8, 0.95]:
        f = p >= th; tp = (f & (yte == 1)).sum()
        rows.append({"threshold": th, "malignant caught (recall)": tp / (yte == 1).sum(), "flagged that are malignant (precision)": tp / max(f.sum(), 1), "cancers missed": int(((~f) & (yte == 1)).sum()), "benign flagged": int((f & (yte == 0)).sum())})
    nb = GaussianNB().fit(Xtr, ytr); pn = nb.predict_proba(Xte)[:, 1]
    cal = CalibratedClassifierCV(GaussianNB(), method="isotonic", cv=5).fit(Xtr, ytr); pc = cal.predict_proba(Xte)[:, 1]
    def bins(pp):
        out = []
        for lo, hi in [(0, 0.1), (0.1, 0.9), (0.9, 1.01)]:
            m = (pp >= lo) & (pp < hi)
            out.append(f"{m.sum()} biopsies, said {pp[m].mean():.2f}, really {yte[m].mean():.2f}" if m.any() else "none")
        return out
    rel = pd.DataFrame({"predicted P(malignant)": ["below 0.1", "0.1–0.9", "above 0.9"], "raw naive Bayes": bins(pn), "calibrated naive Bayes": bins(pc)})
    ext = np.mean((pn < 0.001) | (pn > 0.999))
    return [
        ("Same model, different thresholds", f"Logistic regression on {len(yte)} unseen real biopsies ({int(yte.sum())} malignant):\n\n{t(pd.DataFrame(rows), nd=2)}\n\nA hospital would accept a few extra benign biopsies flagged to miss as few cancers as possible, so it picks a low threshold, not 0.5."),
        ("Are the probabilities honest?", f"Naive Bayes is very sure of itself: {pct(ext)} of its predictions are below 0.001 or above 0.999. Grouping predictions and comparing with what really happened:\n\n{t(rel)}\n\nBrier score (lower = better): raw **{brier_score_loss(yte, pn):.3f}**, after isotonic calibration **{brier_score_loss(yte, pc):.3f}**."),
        ("Picking the threshold from costs", f"If missing a cancer is judged 20× worse than an unnecessary follow-up, flag when P(malignant) > 1/(1 + 20) = **{1 / 21:.3f}**. With logistic regression's probabilities that flags {int((p > 1 / 21).sum())} of {len(yte)} biopsies and misses {int(((p <= 1 / 21) & (yte == 1)).sum())} cancers. This only works if the probabilities are calibrated, which is why the two steps go together."),
    ], "Choose the threshold from the cost of each mistake, and make sure the probabilities it's applied to are calibrated."


@walk("m-choosing-classifier", "titanic")
def _():
    import time
    from sklearn.compose import make_column_transformer
    from sklearn.pipeline import make_pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import GaussianNB
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.svm import SVC
    df = D("titanic").copy(); y = df["Survived"]
    num, cat = ["Age", "Fare", "SibSp", "Parch", "Pclass"], ["Sex", "Embarked"]
    pre = lambda: make_column_transformer((make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num), (make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", sparse_output=False)), cat))
    models = {"always 'died' (baseline)": DummyClassifier(), "logistic regression": LogisticRegression(max_iter=2000), "naive Bayes": GaussianNB(), "LDA": LinearDiscriminantAnalysis(),
              "kNN (k = 15)": KNeighborsClassifier(15), "decision tree (depth 4)": DecisionTreeClassifier(max_depth=4, random_state=0),
              "random forest": RandomForestClassifier(200, min_samples_leaf=3, random_state=0, n_jobs=2), "gradient boosting": HistGradientBoostingClassifier(max_depth=3, random_state=0), "SVM (RBF kernel)": SVC(random_state=0)}
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=0); sc = {}; rows = []
    for n, m in models.items():
        t0 = time.time(); s = cross_val_score(make_pipeline(pre(), m), df[num + cat], y, cv=cv, scoring="roc_auc"); sc[n] = s
        rows.append({"model": n, "AUC mean": s.mean(), "± sd across folds": s.std(), "time (s)": round(time.time() - t0, 2)})
    r = pd.DataFrame(rows).sort_values("AUC mean", ascending=False)
    base = sc["logistic regression"]; best = r.iloc[0]["model"]; d = sc[best] - base; se = d.std(ddof=1) / np.sqrt(len(d))
    near = [n for n in sc if n not in ("logistic regression", "always 'died' (baseline)") and abs((sc[n] - base).mean()) < 2 * (sc[n] - base).std(ddof=1) / np.sqrt(len(d))]
    return [
        ("Same data, same folds, same metric", f"{len(df)} real passengers, 7 columns (missing ages filled and categories encoded inside each model's pipeline, so no test fold leaks into training). Every model is scored on the **same** 10 folds (5-fold, repeated twice) by AUC."),
        ("The comparison", f"{t(r, nd=3)}"),
        ("Is the winner really better?", f"Compare fold by fold with logistic regression: **{best}** is ahead by {d.mean():+.3f} AUC, about {d.mean() / se:.1f} standard errors, {'so the gain is probably real' if d.mean() > 2 * se else 'which is within noise'}. Models statistically tied with logistic regression here: {', '.join(near) or 'none'}. Final pick depends on the job: the top model for pure accuracy, logistic regression if every decision must be explained, with the gap above as the price of explainability."),
    ], "Choose a classifier by comparing several families on identical folds with the right metric, then weigh any real gain against simplicity and explainability."
