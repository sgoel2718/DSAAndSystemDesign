"""Real-data walkthroughs: ML foundations & data."""
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt


@walk("m-ai-overview", "titanic")
def _():
    df = D("titanic")
    rows = df[["Who", "Sex", "Pclass", "Age", "Survived"]].head(6)
    rule = np.where(df["Sex"] == "female", 1, 0)
    rule_acc = (rule == df["Survived"]).mean()
    from sklearn.tree import DecisionTreeClassifier
    X = pd.get_dummies(df[["Pclass", "Sex", "Age", "Fare"]].fillna(df["Age"].median()), drop_first=True)
    tr, te = slice(0, 600), slice(600, None)
    m = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X[tr], df["Survived"][tr])
    ml_acc = m.score(X[te], df["Survived"][te]); rule_te = (rule[600:] == df["Survived"][600:]).mean()
    return [
        ("The data: real passengers", f"Each row is a person on the Titanic. The last column is what happened to them.\n\n{t(rows)}"),
        ("A hand-written rule (AI, but not ML)", f"A person writes the rule **\"women survive, men don't\"** (\"women and children first\"). Nobody learned it from data. It is right for **{pct(rule_acc)}** of all 891 passengers."),
        ("A learned rule (machine learning)", f"Give a decision tree the first 600 passengers with their outcomes. It finds its own questions about sex, class, age and fare. On the 291 passengers it never saw it is right **{pct(ml_acc)}** of the time, against **{pct(rule_te)}** for the hand rule on the same people."),
        ("Deep learning and generative AI", "The same idea scaled up: a deep network would read a photo or the passenger's letters directly, and a generative model could write a new, realistic passenger diary. Both still learn from examples."),
    ], "Machine learning = the computer finds the rule from labelled examples instead of a person writing it."


@walk("m-ml-types", ("titanic", "sms"))
def _():
    df = D("titanic"); s = D("sms")
    from sklearn.cluster import KMeans
    feats = df[["Age", "Fare"]].dropna().head(400)
    km = KMeans(3, n_init=10, random_state=0).fit(feats)
    g = feats.assign(group=km.labels_).groupby("group").agg(passengers=("Age", "size"), avg_age=("Age", "mean"), avg_fare=("Fare", "mean")).round(1)
    return [
        ("Supervised: the answer column is there", f"Titanic rows come with `Survived`. A model learns *inputs → answer*.\n\n{t(df[['Who', 'Pclass', 'Sex', 'Survived']], 3)}"),
        ("Supervised on text: labelled messages", f"Every SMS already says spam or ham, so a spam filter is supervised too.\n\n{t(s, 3)}"),
        ("Unsupervised: hide the answers, find groups", f"Drop `Survived` and give k-means only age and fare of 400 passengers. It invents 3 groups by itself:\n\n{t(g, index=True)}\n\nNobody told it about ticket classes, yet it separated the many cheap tickets, a group of pricier ones, and a handful of very expensive first-class tickets."),
        ("Self-supervised and reinforcement", "Self-supervised: hide a word in each SMS (\"Free entry in 2 a wkly ___\") and predict it from the rest; the text labels itself. Reinforcement: no table at all, an agent tries actions and gets a reward, e.g. a lifeboat-loading game scoring +1 per person saved."),
    ], "The type of learning is decided by the feedback in your data: answers, no answers, self-made answers, or rewards."


@walk("m-ml-principles", "housing")
def _():
    df = D("housing").head(200)
    x, y = df["median_income"].values, df["median_house_value"].values / 1000
    lines = [(30, 50), (40, 40), None]
    from numpy.linalg import lstsq
    w, b = lstsq(np.c_[x, np.ones_like(x)], y, rcond=None)[0]
    rows = []
    for wb in [(30, 50), (40, 40), (w, b)]:
        mse = np.mean((wb[0] * x + wb[1] - y) ** 2)
        rows.append({"line": f"value = {wb[0]:.1f} × income + {wb[1]:.1f}", "average squared error": mse})
    ex = df.iloc[:4][["median_income", "median_house_value"]].assign(guess_30_50=lambda d: 30 * d["median_income"] + 50)
    ex["median_house_value"] /= 1000
    return [
        ("The data", f"200 California districts: median income (in tens of thousands of dollars) and median house value (in thousands).\n\n{t(df[['median_income', 'median_house_value']], 4)}"),
        ("Pick a family of functions", "We decide to try straight lines: **value = w × income + b**. Every pair (w, b) is one candidate model."),
        ("Score one candidate on real rows", f"Line w = 30, b = 50 on the first 4 districts:\n\n{t(ex.rename(columns={'median_house_value': 'true value', 'guess_30_50': 'line guess'}))}\n\nThe gaps between true value and guess are the errors."),
        ("Search for the lowest loss", f"Average squared error over all 200 districts for three lines:\n\n{t(pd.DataFrame(rows))}\n\nTraining = searching for the line with the smallest error. The best one says each extra $10k of median income adds about **${w:.0f}k** of house value."),
    ], "Every ML algorithm is: a family of functions + a loss that measures mistakes + an optimiser that searches for the smallest loss."


@walk("m-problem-formulation", "titanic")
def _():
    df = D("titanic")
    base = 1 - df["Survived"].mean()
    rule = (np.where(df["Sex"] == "female", 1, 0) == df["Survived"]).mean()
    return [
        ("Vague goal", "\"Use the passenger list to help the rescue teams.\" No model can do that yet."),
        ("Precise target, inputs and timing", "Target: `Survived` (yes/no) → binary classification. Inputs available at boarding: class, sex, age, fare, family aboard, port. **Not allowed**: lifeboat number or body recovered, because they are only known after the event."),
        ("Metric", "Accuracy is fine here because survivors are 38% (not rare). If we cared most about not missing survivors we'd track recall too."),
        ("Baselines to beat", f"Always predict \"died\": **{pct(base)}** correct. The rule \"women survive\": **{pct(rule)}**. Any model must clearly beat {pct(rule)} to be worth building."),
    ], "Write down target, inputs (known at prediction time), metric and baseline before touching a model."


@walk("m-intuitive-algos", "penguins")
def _():
    df = D("penguins").dropna()
    cent = df.groupby("species")[["bill_length_mm", "flipper_length_mm"]].mean().round(1)
    new = df.sample(3, random_state=1)[["species", "bill_length_mm", "flipper_length_mm"]]
    def nearest(r):
        d = ((cent - r[["bill_length_mm", "flipper_length_mm"]].values) ** 2).sum(1) ** 0.5
        return d.idxmin()
    new["nearest centroid says"] = new.apply(nearest, axis=1)
    acc = (df.apply(nearest, axis=1) == df["species"]).mean()
    maj = df["species"].value_counts(normalize=True).iloc[0]
    return [
        ("The data", f"Real penguins with bill length and flipper length.\n\n{t(df[['species', 'island', 'bill_length_mm', 'flipper_length_mm']], 5)}"),
        ("Majority baseline", f"The most common species is {df['species'].value_counts().index[0]}. Always guessing it is right **{pct(maj)}** of the time."),
        ("Nearest centroid: average each species", f"{t(cent, index=True)}"),
        ("Classify three penguins", f"Each penguin gets the species whose average is closest:\n\n{t(new)}\n\nOver all {len(df)} penguins this two-number rule is right **{pct(acc)}** of the time."),
    ], "Simple methods tell you quickly whether there is a signal and give the score fancier models must beat."


@walk("m-search-ai", "karate")
def _():
    import networkx as nx
    G = D("karate")
    path = nx.shortest_path(G, 16, 26)
    lengths = nx.single_source_shortest_path_length(G, 16)
    far = sorted(lengths.items(), key=lambda kv: -kv[1])[:3]
    return [
        ("The data: a real friendship network", f"34 karate club members (numbered 0–33); an edge means two members were friends. Member 0 is the instructor, member 33 the club president. There are {G.number_of_edges()} friendships."),
        ("Question for search", "Member 16 wants a message passed to member 26 only through friends. What is the shortest chain?"),
        ("Breadth-first search step by step", f"Search expands friends of 16, then friends of friends, and so on, keeping the first route that reaches each person. Hops needed from member 16: member 5 → {lengths[5]}, member 0 → {lengths[0]}, member 33 → {lengths[33]}. The farthest members are {', '.join(f'{k} ({v} hops)' for k, v in far)}."),
        ("The answer", f"Shortest chain: **{' → '.join(map(str, path))}** ({len(path) - 1} hops). No training data was used: this is classical AI search, the same family as Dijkstra and A* in route planning."),
    ], "Search explores possibilities systematically; it doesn't learn from examples."


@walk("m-data-processing", "titanic")
def _():
    df = D("titanic").copy()
    miss = df[["Age", "Cabin", "Embarked", "Fare"]].isna().sum().rename("missing").to_frame()
    med_age = df["Age"].median()
    ttl = df["Name"].str.extract(r",\s*([^\.]+)\.")[0]
    idx = [df[df["Age"].isna() & (ttl == x)].index[0] for x in ["Mr", "Mrs", "Miss", "Master"]]
    mr = df.loc[idx, ["Who", "Age", "Pclass"]]
    by_title = df.assign(title=df["Name"].str.extract(r",\s*([^\.]+)\.")[0]).groupby("title")["Age"].median()
    mr2 = mr.copy(); mr2["filled (overall median)"] = med_age
    titles = df.loc[mr.index, "Name"].str.extract(r",\s*([^\.]+)\.")[0]
    mr2["filled (median for title)"] = titles.map(by_title).values
    fare_hi = df.nlargest(3, "Fare")[["Who", "Pclass", "Fare"]]
    return [
        ("Find the problems", f"Missing values per column (out of 891):\n\n{t(miss, index=True)}\n\nCabin is mostly empty, Age is missing for about 1 in 5 passengers."),
        ("Fill missing ages", f"Passengers with no age, filled two ways:\n\n{t(mr2)}\n\nUsing the median for each title (Mr, Mrs, Miss, Master) is smarter: a \"Master\" is a boy, so he shouldn't get the overall median of {med_age:.0f}."),
        ("Check the outliers", f"The highest fares:\n\n{t(fare_hi)}\n\n£512 looks extreme but it is real (luxury suites), so we keep it rather than delete it."),
        ("Decide per column", "Age: impute by title and add an `age_missing` flag. Cabin: too empty, keep only \"has cabin yes/no\". Embarked: 2 missing, fill with the most common port (S)."),
    ], "Cleaning is column-by-column detective work: count problems, understand them, then fix them with a reason."


@walk("m-eda", "titanic")
def _():
    df = D("titanic")
    by_sex = df.groupby("Sex")["Survived"].agg(passengers="size", survival_rate="mean")
    by_class = df.groupby("Pclass")["Survived"].agg(passengers="size", survival_rate="mean")
    age_bins = df.assign(age_group=pd.cut(df["Age"], [0, 12, 18, 40, 60, 80])).groupby("age_group", observed=True)["Survived"].agg(passengers="size", survival_rate="mean")
    return [
        ("Look at the target", f"{df['Survived'].sum()} of 891 passengers survived ({pct(df['Survived'].mean())}). Not rare, so plain accuracy is a fair first metric."),
        ("One feature at a time: sex", f"{t(by_sex, index=True)}\n\nA huge difference: sex will be a strong feature."),
        ("Class", f"{t(by_class, index=True)}\n\nFirst-class passengers survived far more often."),
        ("Age, in groups", f"{t(age_bins, index=True)}\n\nChildren under 12 had a better chance; the effect is weaker than sex or class."),
    ], "EDA turns a table into a list of findings: which features matter, which need cleaning, and which metric to use."


@walk("m-real-world-data", ("titanic", "digits", "sms", "speech"))
def _():
    dg = D("digits"); x, sr = D("speech"); s = D("sms")
    words = s["text"].iloc[2].lower().split()[:8]
    vocab = {w: i + 1 for i, w in enumerate(sorted(set(words)))}
    return [
        ("A table", f"Titanic: {D('titanic').shape[0]} rows × {D('titanic').shape[1]} columns. One row = one passenger, one column = one feature."),
        ("An image", f"One handwritten digit is an 8 × 8 grid of numbers (0 = white, 16 = black). The first scan, a \"{dg.target[0]}\":\n\n{t(pd.DataFrame(dg.images[0].astype(int)))}\n\nAll {len(dg.images)} scans together: shape {dg.images.shape}."),
        ("Text", f"The SMS \"{' '.join(words)} …\" becomes ids: {[vocab[w] for w in words]} using a vocabulary built from its words."),
        ("Audio", f"The speech clip is {len(x):,} numbers: {sr:,} air-pressure samples per second for {len(x) / sr:.1f} seconds. The first five: {', '.join(f'{v:.4f}' for v in x[:5])}."),
    ], "Every data type ends up as an array of numbers whose first dimension counts the examples."


@walk("m-encoding", "titanic")
def _():
    df = D("titanic").loc[[0, 1, 5, 9, 16], ["Who", "Embarked", "Pclass", "Sex"]]
    oh = pd.get_dummies(df["Embarked"], prefix="port").astype(int)
    full = D("titanic").dropna(subset=["Embarked"])
    te = full.groupby("Embarked")["Survived"].mean()
    out = df.join(oh)
    out["port_target_enc"] = df["Embarked"].map(te).round(2)
    return [
        ("Text categories in real rows", f"{t(df)}\n\nEmbarked: C = Cherbourg, Q = Queenstown, S = Southampton. A model can't use letters."),
        ("One-hot: one 0/1 column per port", f"{t(out[['Who', 'Embarked', 'port_C', 'port_Q', 'port_S']])}\n\nNo fake order: Southampton isn't \"bigger\" than Cherbourg."),
        ("Ordinal: class has a real order", "Pclass 1st < 2nd < 3rd, so keeping it as 1, 2, 3 is fine (and sex becomes 0/1)."),
        ("Target encoding: replace a port by its survival rate", f"Survival by port: {', '.join(f'{k} {v:.2f}' for k, v in te.items())}.\n\n{t(out[['Who', 'Embarked', 'port_target_enc']])}\n\nCompact for columns with many categories, but compute it on training rows only."),
    ], "Choose the encoding by the meaning: no order → one-hot; real order → ordinal; many categories → target encoding or hashing."


@walk("m-feature-engineering", "titanic")
def _():
    df = D("titanic").copy()
    df["family_size"] = df["SibSp"] + df["Parch"] + 1
    df["title"] = df["Name"].str.extract(r",\s*([^\.]+)\.")[0]
    df["fare_per_person"] = (df["Fare"] / df.groupby("Ticket")["Ticket"].transform("size")).round(2)
    show = df[["Who", "SibSp", "Parch", "family_size", "title", "Fare", "fare_per_person"]].iloc[[0, 1, 7, 13]]
    fam = df.assign(fam=pd.cut(df["family_size"], [0, 1, 4, 11], labels=["alone", "2-4", "5+"])).groupby("fam", observed=True)["Survived"].agg(passengers="size", survival_rate="mean")
    tit = df[df["title"].isin(["Mr", "Mrs", "Miss", "Master"])].groupby("title")["Survived"].agg(passengers="size", survival_rate="mean")
    return [
        ("Create features from raw columns", f"{t(show)}\n\nfamily_size = siblings/spouses + parents/children + 1; title comes from the name; fare_per_person divides a group ticket's fare by the people sharing it."),
        ("Does family size help?", f"{t(fam, index=True)}\n\nSmall families did best; people alone and very large families did worse. The raw SibSp and Parch columns hid this."),
        ("Does title help?", f"{t(tit, index=True)}\n\n\"Master\" (young boys) survived much more than \"Mr\": title captures age and sex together."),
    ], "Good features put domain knowledge into a column, so the model doesn't have to discover it."


@walk("m-feature-selection", "cancer")
def _():
    df = D("cancer")
    from sklearn.feature_selection import mutual_info_classif
    X = df.drop(columns=["target", "diagnosis"]); y = df["target"]
    mi = pd.Series(mutual_info_classif(X, y, random_state=0), index=X.columns).sort_values(ascending=False)
    corr = X[["mean radius", "mean perimeter", "mean area"]].corr().round(3)
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))
    all30 = cross_val_score(m, X, y, cv=5).mean(); top5 = cross_val_score(m, X[mi.index[:5]], y, cv=5).mean()
    return [
        ("30 measurements per biopsy", f"{t(df[['mean radius', 'mean texture', 'mean smoothness', 'worst area', 'diagnosis']], 4)}"),
        ("Score each feature alone (filter)", f"Mutual information with the diagnosis, top 5 and bottom 3:\n\n{t(pd.concat([mi.head(5), mi.tail(3)]).rename('score').round(3).to_frame(), index=True)}"),
        ("Spot duplicates", f"Radius, perimeter and area of the same cell are almost the same information:\n\n{t(corr, index=True)}"),
        ("Compare", f"Logistic regression with all 30 features: **{pct(all30, 1)}** accuracy. With only the top 5: **{pct(top5, 1)}**. Six times fewer inputs for only a few points less, and a much simpler model to explain."),
    ], "Keep features that carry new information about the target; drop noise and near-duplicates."


@walk("m-feature-extraction", "sms")
def _():
    s = D("sms").head(4)
    from sklearn.feature_extraction.text import CountVectorizer
    cv = CountVectorizer(vocabulary=["free", "win", "call", "ok", "lar", "txt", "text"])
    X = pd.DataFrame(cv.transform(s["text"].str.lower()).toarray(), columns=cv.get_feature_names_out())
    X.insert(0, "label", s["label"].values)
    s2 = D("sms").copy(); s2["length"] = s2["text"].str.len(); s2["digits"] = s2["text"].str.count(r"\d"); s2["capitals"] = s2["text"].str.count(r"[A-Z]")
    agg = s2.groupby("label")[["length", "digits", "capitals"]].mean().round(1)
    return [
        ("Raw messages", f"{t(s)}"),
        ("Turn words into counts", f"Counting a few chosen words in each message:\n\n{t(X)}"),
        ("Hand-crafted numeric features", f"Average per message:\n\n{t(agg, index=True)}\n\nSpam is longer and full of digits (phone numbers, prices) and capitals: three easy, strong features."),
    ], "Extraction turns raw text, images or sound into a fixed list of numbers a model can use."


@walk("m-imbalance", "sms")
def _():
    s = D("sms")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import recall_score, precision_score
    Xtr, Xte, ytr, yte = train_test_split(s["text"], s["label"] == "spam", test_size=0.3, stratify=s["label"], random_state=0)
    v = TfidfVectorizer(min_df=2).fit(Xtr)
    rows = []
    for name, cw in [("plain", None), ("class_weight=balanced", "balanced")]:
        m = LogisticRegression(class_weight=cw, max_iter=2000).fit(v.transform(Xtr), ytr)
        p = m.predict(v.transform(Xte))
        rows.append({"model": name, "accuracy": (p == yte).mean(), "spam recall": recall_score(yte, p), "spam precision": precision_score(yte, p)})
    return [
        ("How rare is spam?", f"{(s['label'] == 'spam').sum()} spam out of {len(s):,} messages ({pct((s['label'] == 'spam').mean())})."),
        ("The useless model", f"\"Everything is ham\" scores **{pct((s['label'] == 'ham').mean(), 1)}** accuracy and catches 0 spam. Accuracy alone would call it good."),
        ("Train with and without class weights", f"{t(pd.DataFrame(rows), nd=3)}\n\nWeighting spam mistakes more catches more spam (higher recall), at the cost of a few more false alarms."),
    ], "With rare classes, measure recall and precision, and use class weights, resampling or a tuned threshold."


@walk("m-train-val-test", "housing")
def _():
    df = D("housing")
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.ensemble import RandomForestRegressor
    X = df.drop(columns=["median_house_value", "ocean_proximity"]).fillna(0); y = df["median_house_value"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0)
    m = RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=-1)
    cvs = cross_val_score(m, Xtr, ytr, cv=5, scoring="r2")
    m.fit(Xtr, ytr)
    return [
        ("Split the districts", f"{len(df):,} districts → **{len(Xtr):,} for training** and **{len(Xte):,} locked away for the final test**."),
        ("5-fold cross-validation on the training part", f"The {len(Xtr):,} training districts are cut into 5 folds; each fold is validated once. R² per fold: {', '.join(f'{v:.3f}' for v in cvs)}. Average **{cvs.mean():.3f}**, and the folds agree closely, so the estimate is reliable."),
        ("Train on memory vs test on new data", f"R² on the training districts: **{m.score(Xtr, ytr):.3f}**. R² on the test districts it never saw: **{m.score(Xte, yte):.3f}**. The training score is far too optimistic; only the test score is honest."),
    ], "Learn on training data, choose with validation (or CV), report once on a test set."


@walk("m-leakage", "titanic")
def _():
    df = D("titanic").copy()
    rng = np.random.default_rng(0)
    df["body_recovered"] = np.where(df["Survived"] == 0, rng.random(len(df)) < 0.4, False)
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import cross_val_score
    base = pd.get_dummies(df[["Pclass", "Sex", "Fare"]], drop_first=True)
    leak = base.assign(body_recovered=df["body_recovered"].astype(int))
    a = cross_val_score(DecisionTreeClassifier(max_depth=4, random_state=0), base, df["Survived"], cv=5).mean()
    b = cross_val_score(DecisionTreeClassifier(max_depth=4, random_state=0), leak, df["Survived"], cv=5).mean()
    return [
        ("A tempting extra column", f"Suppose the data also had `body_recovered` (filled in after the disaster; simulated here for 40% of victims).\n\n{t(df[['Who', 'Sex', 'Pclass', 'body_recovered', 'Survived']], 5)}"),
        ("Scores look better", f"Without it: **{pct(a, 1)}** accuracy. With it: **{pct(b, 1)}**. Anyone recovered as a body certainly died, so the column hands the model part of the answer."),
        ("Why it's useless in practice", "When you'd actually use the model (at boarding, or during the rescue) nobody knows yet whose body will be recovered. The column doesn't exist at prediction time, so the extra accuracy is fake."),
    ], "For every feature ask: would I know this value at the moment I make the prediction?"


@walk("m-overfitting", "mpg")
def _():
    df = D("mpg").dropna().sort_values("horsepower")
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error
    X, y = df[["horsepower"]].values, df["mpg"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=1)
    Xtr, ytr = Xtr[:40], ytr[:40]
    rows = []
    for d in [1, 2, 12]:
        m = make_pipeline(StandardScaler(), PolynomialFeatures(d), LinearRegression()).fit(Xtr, ytr)
        rows.append({"curve": f"degree {d}", "train error (mpg)": mean_absolute_error(ytr, m.predict(Xtr)), "new cars error (mpg)": mean_absolute_error(yte, m.predict(Xte))})
    return [
        ("The data", f"Real cars: more horsepower usually means fewer miles per gallon.\n\n{t(df[['name', 'horsepower', 'mpg']], 4)}"),
        ("Fit three curves to just 40 cars", f"{t(pd.DataFrame(rows))}"),
        ("Read the table", "A straight line (degree 1) misses the bend: a little underfit. Degree 2 follows the real curve. Degree 12 bends through every training car (lowest training error) but is worse on new cars: overfitting."),
    ], "Compare training error with error on new data: a big gap means overfitting."


@walk("m-regularization", "housing")
def _():
    df = D("housing").fillna(0)
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.linear_model import Ridge, Lasso, LinearRegression
    from sklearn.model_selection import train_test_split
    X = df.drop(columns=["median_house_value", "ocean_proximity"]); y = df["median_house_value"] / 1000
    Xp = PolynomialFeatures(2, include_bias=False).fit_transform(StandardScaler().fit_transform(X))
    Xtr, Xte, ytr, yte = train_test_split(Xp, y, train_size=300, random_state=0)
    rows = []
    for name, m in [("no penalty", LinearRegression()), ("ridge alpha=10", Ridge(alpha=10)), ("lasso alpha=1", Lasso(alpha=1, max_iter=20000))]:
        m.fit(Xtr, ytr)
        rows.append({"model": name, "train R2": m.score(Xtr, ytr), "test R2": m.score(Xte, yte), "weights exactly 0": int((np.abs(m.coef_) < 1e-9).sum())})
    return [
        ("A model with too much freedom", f"Using all 8 numeric columns plus every pair multiplied together gives **{Xp.shape[1]} features**, trained on only 300 districts."),
        ("Add a penalty for big weights", f"{t(pd.DataFrame(rows), nd=3)}"),
        ("What happened", "Without a penalty the model fits the 300 districts well but does worse on the rest. Ridge shrinks all weights and generalises better; Lasso also switches many features off completely."),
    ], "Regularisation trades a little training fit for much better performance on new data."


@walk("m-metrics-clf", "cancer")
def _():
    df = D("cancer")
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix
    X = df.drop(columns=["target", "diagnosis"]); y = (df["diagnosis"] == "malignant").astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, stratify=y, random_state=0)
    p = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
    rows = []
    for thr in [0.5, 0.2]:
        tn, fp, fn, tp = confusion_matrix(yte, p >= thr).ravel()
        rows.append({"threshold": thr, "cancers caught (TP)": tp, "cancers missed (FN)": fn, "false alarms (FP)": fp, "precision": tp / (tp + fp), "recall": tp / (tp + fn)})
    return [
        ("The test patients", f"{len(yte)} biopsies, {yte.sum()} of them malignant."),
        ("Confusion matrix at two thresholds", f"{t(pd.DataFrame(rows), nd=3)}"),
        ("Pick the threshold by the cost of mistakes", "Missing a cancer is far worse than an extra follow-up test. Lowering the threshold from 0.5 to 0.2 catches more cancers (higher recall) and accepts a few more false alarms (lower precision)."),
    ], "Accuracy hides which mistakes you make; precision and recall show the trade-off you're choosing."


@walk("m-metrics-reg", "housing")
def _():
    df = D("housing").fillna(0)
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    X = df.drop(columns=["median_house_value", "ocean_proximity"]); y = df["median_house_value"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0)
    pred = RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=-1).fit(Xtr, ytr).predict(Xte)
    e = pred - yte.values
    ex = pd.DataFrame({"true value": yte.values[:5], "predicted": pred[:5], "error": e[:5]})
    mae, rmse = np.abs(e).mean(), np.sqrt((e ** 2).mean())
    mape = np.mean(np.abs(e) / yte.values); r2 = 1 - (e ** 2).sum() / ((yte - yte.mean()) ** 2).sum()
    return [
        ("Predictions for real districts", f"{t(ex)}"),
        ("Four metrics over 900 test districts", f"MAE **${mae:,.0f}** (typical miss), RMSE **${rmse:,.0f}** (bigger: a few large misses count heavily), MAPE **{pct(mape, 1)}** (typical miss as a percentage), R² **{r2:.3f}** (share of the variation explained)."),
        ("Which to report", "To a home buyer: \"usually within about $" + f"{mae / 1000:.0f}" + "k\" (MAE). If big misses are dangerous, optimise RMSE. MAPE is easy to explain but unfair to cheap districts."),
    ], "MAE is the typical error; RMSE punishes big errors; R² compares with just predicting the average."


@walk("m-hyperparams", "wine")
def _():
    df = D("wine")
    from sklearn.model_selection import GridSearchCV
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    X = df.drop(columns=["target", "cultivar"]); y = df["cultivar"]
    g = GridSearchCV(make_pipeline(StandardScaler(), KNeighborsClassifier()), {"kneighborsclassifier__n_neighbors": [1, 3, 5, 11, 25, 51]}, cv=5).fit(X, y)
    res = pd.DataFrame({"k (neighbours)": g.cv_results_["param_kneighborsclassifier__n_neighbors"].data.astype(int), "CV accuracy": g.cv_results_["mean_test_score"]})
    return [
        ("The task", f"Recognise which of three cultivars an Italian wine comes from, using 13 chemical measurements ({len(df)} wines)."),
        ("Try each setting with 5-fold CV", f"{t(res, nd=3)}"),
        ("Pick the best", f"k = {g.best_params_['kneighborsclassifier__n_neighbors']} scores best ({g.best_score_:.3f}). k = 1 trusts the single most similar wine and is a little worse; after that the score levels off, so a middle value is a safe, stable choice."),
    ], "Hyperparameters are chosen by trying values and scoring each on validation data."


@walk("m-separability", "penguins")
def _():
    df = D("penguins").dropna()
    from sklearn.linear_model import LogisticRegression
    pair = df[df["species"].isin(["Adelie", "Gentoo"])]
    a = LogisticRegression(max_iter=1000).fit(pair[["bill_depth_mm", "flipper_length_mm"]], pair["species"]).score(pair[["bill_depth_mm", "flipper_length_mm"]], pair["species"])
    pair2 = df[df["species"].isin(["Adelie", "Chinstrap"])]
    b = LogisticRegression(max_iter=1000).fit(pair2[["bill_depth_mm", "flipper_length_mm"]], pair2["species"]).score(pair2[["bill_depth_mm", "flipper_length_mm"]], pair2["species"])
    c = LogisticRegression(max_iter=1000).fit(pair2[["bill_length_mm", "flipper_length_mm"]], pair2["species"]).score(pair2[["bill_length_mm", "flipper_length_mm"]], pair2["species"])
    stats = df.groupby("species")[["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]].mean().round(1)
    return [
        ("Average measurements", f"{t(stats, index=True)}"),
        ("Adelie vs Gentoo with bill depth + flipper", f"A straight line separates them **{pct(a)}** correctly: Gentoos have much longer flippers and shallower bills. Linearly separable."),
        ("Adelie vs Chinstrap with the same two features", f"Only **{pct(b)}**: their bill depth and flippers overlap a lot. With these features they are not separable."),
        ("Change the features", f"Use bill **length** instead of depth and the line gets **{pct(c)}**. The right feature makes the boundary simple."),
    ], "Separability depends on the features you choose, not only on the model."
