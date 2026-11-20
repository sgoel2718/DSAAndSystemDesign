"""Experiential learning labs: hands-on, end-to-end notebooks (paste into Colab / VS Code)."""


def L(id, title, module, goal, data, steps, code="", reuse=None, observe=(), extend=(), net=False, see=()):
    assert id.startswith("m-lab-")
    assert code or reuse, id
    return dict(id=id, title=title, module=module, goal=goal, data=data, steps=list(steps), code=code.strip("\n"), reuse=reuse,
                observe=list(observe), extend=list(extend), net=net, see=list(see))


LABS = [
L("m-lab-preprocess", "Lab 1 · Data pre-processing and visualisation", "Module 1",
  "Clean a messy customer table, engineer features and visualise relationships before modelling.",
  "Synthetic 'telecom customers' table generated in the notebook (try Kaggle 'Telco Customer Churn' next).",
  ["Load data and inspect info(), describe(), missing values and duplicates", "Fix types, standardise categories, impute missing values, cap outliers",
   "Create features (tenure bands, charges per month of tenure)", "Plot distributions, churn rate by category and a correlation heatmap", "Write down 3 insights"],
  code="""
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
rng = np.random.default_rng(42); n = 800
df = pd.DataFrame({"customer_id": np.arange(n), "tenure_months": rng.integers(0, 72, n), "monthly_charges": rng.normal(70, 25, n).round(2),
                   "contract": rng.choice(["Month-to-month", "month-to-month ", "One year", "Two year"], n, p=[0.45, 0.1, 0.25, 0.2]),
                   "internet": rng.choice(["Fiber", "DSL", "None"], n), "senior": rng.integers(0, 2, n)})
df.loc[rng.random(n) < 0.05, "monthly_charges"] = np.nan; df.loc[rng.random(n) < 0.01, "monthly_charges"] = 9999
df = pd.concat([df, df.sample(10, random_state=0)])                                    # duplicates
p = 1 / (1 + np.exp(-(-1 + 1.2 * df["contract"].str.lower().str.strip().eq("month-to-month") - 0.03 * df["tenure_months"] + 0.01 * df["monthly_charges"].fillna(70).clip(0, 150))))
df["churn"] = (rng.random(len(df)) < p).astype(int)
print(df.info()); print(df.isna().sum()[lambda s: s > 0]); print("duplicates:", df.duplicated().sum())
df = df.drop_duplicates()
df["contract"] = df["contract"].str.strip().str.title()
q1, q3 = df["monthly_charges"].quantile([0.25, 0.75]); df["monthly_charges"] = df["monthly_charges"].clip(upper=q3 + 3 * (q3 - q1))
df["monthly_charges"] = df["monthly_charges"].fillna(df.groupby("internet")["monthly_charges"].transform("median"))
df["tenure_band"] = pd.cut(df["tenure_months"], [-1, 12, 24, 48, 72], labels=["0-1y", "1-2y", "2-4y", "4-6y"])
print(df.groupby("contract")["churn"].mean().round(3).sort_values(ascending=False))
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
sns.histplot(df, x="monthly_charges", hue="churn", ax=ax[0]); sns.barplot(df, x="tenure_band", y="churn", ax=ax[1])
sns.heatmap(df.select_dtypes("number").drop(columns="customer_id").corr(), annot=True, cmap="vlag", ax=ax[2]); fig.tight_layout(); fig.savefig("lab1.png")
print("saved lab1.png")
""",
  observe=["Month-to-month contracts churn far more", "Churn falls as tenure rises", "Imputing by group keeps realistic values"],
  extend=["Repeat on the real Telco churn dataset", "Try KNNImputer and compare", "Add an interactive plot with plotly"], see=["m-data-processing", "m-eda", "m-pandas"]),

L("m-lab-clf-reg", "Lab 2 · Classification and regression end to end", "Module 1",
  "Train and evaluate a classifier and a regressor with proper splits, baselines and metrics.",
  "scikit-learn breast cancer (classification) and diabetes (regression) datasets.",
  ["Split train/test (stratified for classification)", "Fit a baseline (Dummy) and two real models", "Report accuracy, precision, recall, F1, ROC-AUC / MAE, RMSE, R²",
   "Plot a confusion matrix and residuals", "Explain which model you'd ship and why"],
  code="""
from sklearn.datasets import load_breast_cancer, load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
X, y = load_breast_cancer(return_X_y=True); Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
for name, m in [("baseline", DummyClassifier()), ("logistic", make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))), ("random forest", RandomForestClassifier(300, random_state=0))]:
    m.fit(Xtr, ytr); p = m.predict(Xte); prob = m.predict_proba(Xte)[:, 1]
    print(f"== {name}: ROC-AUC {roc_auc_score(yte, prob):.3f}\\n{confusion_matrix(yte, p)}"); print(classification_report(yte, p, digits=3, zero_division=0)) if name == "logistic" else None
X, y = load_diabetes(return_X_y=True); Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0)
for name, m in [("baseline", DummyRegressor()), ("ridge", Ridge(1.0)), ("random forest", RandomForestRegressor(300, random_state=0))]:
    p = m.fit(Xtr, ytr).predict(Xte)
    print(f"{name:14s} MAE {mean_absolute_error(yte, p):6.1f}  RMSE {mean_squared_error(yte, p) ** 0.5:6.1f}  R2 {r2_score(yte, p):.3f}")
""",
  observe=["Both real models crush the baseline", "A simple linear model is competitive on small tabular data"],
  extend=["Add cross-validation and confidence intervals", "Try gradient boosting"], see=["m-metrics-clf", "m-metrics-reg", "m-train-val-test"]),

L("m-lab-knn", "Lab 3 · k-nearest neighbours from scratch and in scikit-learn", "Module 1",
  "Implement kNN, then study how k and feature scaling change the decision boundary and accuracy.",
  "Wine dataset (13 chemical features, 3 classes).",
  ["Write a kNN classifier with NumPy (distances, argsort, vote)", "Compare with KNeighborsClassifier", "Sweep k with cross-validation", "Show the effect of StandardScaler"],
  code="""
import numpy as np
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
X, y = load_wine(return_X_y=True); Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=1)
sc = StandardScaler().fit(Xtr); Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)
def knn_predict(Xtr, ytr, Xq, k=5):
    d = np.linalg.norm(Xq[:, None, :] - Xtr[None, :, :], axis=2); nn = np.argsort(d, axis=1)[:, :k]
    return np.array([np.bincount(row, minlength=3).argmax() for row in ytr[nn]])
print("from scratch (scaled):", round((knn_predict(Xtr_s, ytr, Xte_s) == yte).mean(), 3), " sklearn:", round(KNeighborsClassifier(5).fit(Xtr_s, ytr).score(Xte_s, yte), 3))
for k in (1, 3, 5, 9, 15, 31):
    raw = cross_val_score(KNeighborsClassifier(k), X, y, cv=5).mean(); scaled = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier(k)), X, y, cv=5).mean()
    print(f"k={k:2d}  raw {raw:.3f}  scaled {scaled:.3f}")
""",
  observe=["Scaling raises accuracy by ~25 points: proline (values ~1000) dominated distances", "Very small and very large k both hurt"],
  extend=["Add distance weighting", "Use a KD-tree and time predictions"], see=["m-knn", "m-normalization"]),

L("m-lab-linear-clf", "Lab 4 · Linear classifiers: perceptron, logistic regression, linear SVM", "Module 1",
  "Train three linear classifiers on the same 2-D data and compare their boundaries, margins and probabilities.",
  "Two Gaussian blobs (separable) and a noisy version (overlapping).",
  ["Generate separable and overlapping data", "Fit Perceptron, LogisticRegression, LinearSVC", "Print each boundary's equation and accuracy", "Compare behaviour when classes overlap"],
  code="""
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.linear_model import Perceptron, LogisticRegression
from sklearn.svm import LinearSVC
for name, std in [("separable", 0.8), ("overlapping", 2.5)]:
    X, y = make_blobs(400, centers=[[-2, -2], [2, 2]], cluster_std=std, random_state=0)
    print(f"== {name} data")
    for m in (Perceptron(random_state=0), LogisticRegression(), LinearSVC()):
        m.fit(X, y); w, b = m.coef_[0], m.intercept_[0]
        print(f"  {type(m).__name__:18s} boundary {w[0]:+.2f}*x1 {w[1]:+.2f}*x2 {b:+.2f} = 0   accuracy {m.score(X, y):.3f}")
lr = LogisticRegression().fit(X, y); print("logistic gives probabilities, e.g.", lr.predict_proba([[0, 0], [3, 3]]).round(3))
""",
  observe=["All find similar lines on separable data", "Perceptron is unstable on overlapping data; logistic/SVM optimise a smooth loss"],
  extend=["Add a third class (one-vs-rest)", "Plot the boundaries with matplotlib"], see=["m-perceptron", "m-logistic-regression", "m-svm", "m-separability"]),

L("m-lab-tree", "Lab 5 · Decision trees: grow, visualise, prune", "Module 1",
  "Train a decision tree, read its rules, and control overfitting with depth and cost-complexity pruning.",
  "Breast cancer dataset.",
  ["Fit an unrestricted tree; compare train vs test accuracy", "Print the top of the tree as rules", "Compute the cost-complexity pruning path", "Pick ccp_alpha by cross-validation"],
  code="""
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split, cross_val_score
data = load_breast_cancer(); Xtr, Xte, ytr, yte = train_test_split(data.data, data.target, stratify=data.target, random_state=0)
full = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)
print(f"unpruned: depth {full.get_depth()}, leaves {full.get_n_leaves()}, train {full.score(Xtr, ytr):.3f}, test {full.score(Xte, yte):.3f}")
print(export_text(DecisionTreeClassifier(max_depth=2, random_state=0).fit(Xtr, ytr), feature_names=list(data.feature_names)))
alphas = full.cost_complexity_pruning_path(Xtr, ytr).ccp_alphas[:-1]
scores = [cross_val_score(DecisionTreeClassifier(ccp_alpha=a, random_state=0), Xtr, ytr, cv=5).mean() for a in alphas]
best = alphas[int(np.argmax(scores))]; pruned = DecisionTreeClassifier(ccp_alpha=best, random_state=0).fit(Xtr, ytr)
print(f"best ccp_alpha {best:.4f}: leaves {pruned.get_n_leaves()}, test {pruned.score(Xte, yte):.3f}")
""",
  observe=["The unpruned tree memorises training data (100%)", "Pruning cuts leaves drastically with equal or better test accuracy"],
  extend=["Plot the tree with sklearn.tree.plot_tree", "Compare gini vs entropy"], see=["m-decision-tree"]),

L("m-lab-bagging", "Lab 6 · Bagging and the bootstrap", "Module 1",
  "See variance reduction: compare one deep tree with bagged trees as the number of estimators grows, and use OOB estimates.",
  "Noisy synthetic classification data.",
  ["Train a single deep tree on several bootstrap samples and watch predictions vary", "Train BaggingClassifier with 1→200 trees", "Compare OOB score with test score"],
  code="""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
X, y = make_classification(2000, 20, n_informative=6, flip_y=0.15, random_state=0); Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
rng = np.random.default_rng(0); preds = []
for b in range(10):
    idx = rng.integers(0, len(ytr), len(ytr)); preds.append(DecisionTreeClassifier(random_state=b).fit(Xtr[idx], ytr[idx]).predict(Xte))
preds = np.array(preds); print("single trees disagree on", ((preds != preds[0]).any(0)).mean().round(3), "of test points")
for n in (1, 5, 25, 100, 200):
    bag = BaggingClassifier(DecisionTreeClassifier(), n_estimators=n, oob_score=n >= 25, random_state=0).fit(Xtr, ytr)
    print(f"{n:3d} trees: test {bag.score(Xte, yte):.3f}" + (f"  OOB {bag.oob_score_:.3f}" if n >= 25 else ""))
""",
  observe=["Individual trees disagree a lot (high variance)", "Accuracy climbs then plateaus as trees are added", "OOB ≈ test accuracy without a validation split"],
  extend=["Bag kNN or linear models — does it help?", "Try max_samples=0.5 and max_features=0.5"], see=["m-bootstrap-bagging"]),

L("m-lab-voting", "Lab 7 · Voting and stacking ensembles", "Module 1",
  "Combine diverse models with hard/soft voting and stacking and measure the gain.",
  "Synthetic 'loan default' style data.",
  ["Train logistic regression, random forest, SVM and kNN", "Build hard and soft voting classifiers", "Build a stacking classifier", "Compare cross-validated scores and correlation of model errors"],
  code="""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
X, y = make_classification(1500, 15, n_informative=6, flip_y=0.08, random_state=3)
models = [("lr", make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))), ("rf", RandomForestClassifier(200, random_state=0)),
          ("svm", make_pipeline(StandardScaler(), SVC(probability=True, random_state=0))), ("knn", make_pipeline(StandardScaler(), KNeighborsClassifier(15)))]
errs = {}
for name, m in models:
    errs[name] = cross_val_predict(m, X, y, cv=5) != y; print(f"{name:4s} {1 - errs[name].mean():.3f}")
print("error correlation lr vs rf:", np.corrcoef(errs["lr"], errs["rf"])[0, 1].round(2))
for name, ens in [("hard vote", VotingClassifier(models, voting="hard")), ("soft vote", VotingClassifier(models, voting="soft")), ("stacking", StackingClassifier(models, LogisticRegression()))]:
    print(f"{name:9s} {cross_val_score(ens, X, y, cv=5).mean():.3f}")
""",
  observe=["Ensembles help most when model errors are weakly correlated", "Soft voting usually beats hard voting"],
  extend=["Weight the voters", "Add XGBoost to the stack"], see=["m-voting-stacking"]),

L("m-lab-linreg-logreg", "Lab 8 · Linear and logistic regression from scratch with gradient descent", "Module 1",
  "Implement both models with NumPy gradient descent, verify against scikit-learn, and plot the loss curve.",
  "Synthetic house prices (regression) and breast cancer (classification).",
  ["Standardise features", "Write the loss and gradient", "Run gradient descent and record loss", "Compare weights/accuracy with scikit-learn", "Experiment with learning rates"],
  code="""
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
rng = np.random.default_rng(0); n = 300
X = np.column_stack([rng.uniform(500, 3000, n), rng.uniform(1, 5, n), rng.uniform(0, 30, n)]); y = 20 + 0.1 * X[:, 0] + 15 * X[:, 1] - 2 * X[:, 2] + rng.normal(0, 10, n)
Xs = StandardScaler().fit_transform(X); Xb = np.column_stack([np.ones(n), Xs])
for lr in (0.001, 0.1, 1.0):
    w = np.zeros(4); hist = []
    for _ in range(500):
        err = Xb @ w - y; hist.append((err ** 2).mean()); w -= lr * 2 * Xb.T @ err / n
    print(f"lr={lr:<5} final MSE {hist[-1]:10.2f}  (start {hist[0]:.0f})")
print("GD weights:", w.round(2), " sklearn:", np.r_[LinearRegression().fit(Xs, y).intercept_, LinearRegression().fit(Xs, y).coef_].round(2))
Xc, yc = load_breast_cancer(return_X_y=True); Xc = StandardScaler().fit_transform(Xc); Xcb = np.column_stack([np.ones(len(yc)), Xc])
w = np.zeros(Xcb.shape[1]); sig = lambda z: 1 / (1 + np.exp(-z))
for i in range(1000):
    p = sig(Xcb @ w); w -= 0.1 * (Xcb.T @ (p - yc) / len(yc) + 0.01 * np.r_[0, w[1:]])        # L2-regularised
loss = -np.mean(yc * np.log(p + 1e-12) + (1 - yc) * np.log(1 - p + 1e-12))
print(f"logistic GD: loss {loss:.4f} accuracy {((p > 0.5) == yc).mean():.4f} | sklearn accuracy {LogisticRegression(max_iter=1000).fit(Xc, yc).score(Xc, yc):.4f}")
""",
  observe=["Too small a learning rate converges slowly; a stable larger one converges fast", "From-scratch results match scikit-learn"],
  extend=["Implement mini-batch SGD", "Add polynomial features and Ridge"], see=["m-linear-regression", "m-logistic-regression", "m-gradients"]),

L("m-lab-features", "Lab 9 · Feature extraction, normalisation and transformation pipelines", "Module 1",
  "Build a leakage-free ColumnTransformer pipeline with scaling, encoding, log/power transforms and engineered features, and measure each step's value.",
  "Synthetic 'bank term deposit' marketing data (mirrors the UCI Bank Marketing capstone).",
  ["Create numeric, categorical and date-like features", "Build preprocessing per column type", "Compare models: raw numeric only vs full pipeline", "Inspect transformed feature names"],
  code="""
import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PowerTransformer, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
rng = np.random.default_rng(0); n = 3000
df = pd.DataFrame({"age": rng.integers(18, 90, n), "balance": rng.lognormal(7, 1.5, n), "duration_sec": rng.exponential(250, n), "campaign": rng.integers(1, 10, n),
                   "job": rng.choice(["admin", "technician", "student", "retired", "services"], n), "month": rng.choice(["may", "jun", "oct", "dec"], n), "housing_loan": rng.choice(["yes", "no"], n)})
logit = -3 + 0.004 * df["duration_sec"] + 0.8 * df["job"].isin(["student", "retired"]) + 0.7 * df["month"].isin(["oct", "dec"]) + 0.3 * np.log(df["balance"]) - 0.2 * df["campaign"]
y = (rng.random(n) < 1 / (1 + np.exp(-logit + 2))).astype(int); print("subscribed rate:", y.mean().round(3))
num, skewed, cat = ["age", "campaign"], ["balance", "duration_sec"], ["job", "month", "housing_loan"]
pre = ColumnTransformer([("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num),
                         ("skew", Pipeline([("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")), ("pt", PowerTransformer())]), skewed),
                         ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
full = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000))])
raw = Pipeline([("sc", StandardScaler()), ("clf", LogisticRegression(max_iter=2000))])
print("raw numeric columns only ROC-AUC:", cross_val_score(raw, df[num + skewed], y, cv=5, scoring="roc_auc").mean().round(3))
print("full feature pipeline ROC-AUC:   ", cross_val_score(full, df, y, cv=5, scoring="roc_auc").mean().round(3))
print("features after transformation:", list(full.fit(df, y).named_steps["pre"].get_feature_names_out())[:8], "...")
""",
  observe=["Encoding categories and fixing skew lifts ROC-AUC", "Everything is fitted inside CV — no leakage"],
  extend=["Note: 'duration' is only known after the call — a leakage trap in the real Bank Marketing data; drop it and compare", "Add target encoding"], see=["m-feature-engineering", "m-encoding", "m-normalization", "m-leakage"]),

L("m-lab-scrape-nltk", "Lab 10 · Web scraping and NLTK text processing", "Module 1",
  "Scrape review text from HTML, clean and tokenise it with NLTK, and find the most frequent meaningful words and bigrams.",
  "An embedded HTML page (swap in requests.get(url).text for a real site you're allowed to scrape).",
  ["Parse HTML with BeautifulSoup", "Clean text and tokenise", "Remove stop words, lemmatise", "Count words and bigrams; run VADER sentiment"],
  code="""
import nltk, re
for p in ["punkt", "punkt_tab", "stopwords", "wordnet", "vader_lexicon"]: nltk.download(p, quiet=True)
from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
html = "".join(f"<div class='r'><p>{t}</p></div>" for t in [
    "The delivery was super fast and the packaging was great!", "Battery life is poor, the phone heats up while charging.",
    "Great camera, great display, but battery drains fast.", "Customer service never replied. Very disappointed!!",
    "Fast delivery, phone works great. Loving the camera.", "Charging is slow and battery life is bad."])
reviews = [d.get_text(" ", strip=True) for d in BeautifulSoup(html, "html.parser").select("div.r p")]
stops, lem = set(stopwords.words("english")), WordNetLemmatizer()
tokens = [[lem.lemmatize(t) for t in nltk.word_tokenize(re.sub(r"[^a-z ]", " ", r.lower())) if t not in stops] for r in reviews]
print("top words:", Counter(w for t in tokens for w in t).most_common(6))
print("top bigrams:", Counter(b for t in tokens for b in nltk.bigrams(t)).most_common(4))
sia = SentimentIntensityAnalyzer()
for r in reviews: print(f"{sia.polarity_scores(r)['compound']:+.2f}  {r}")
""",
  observe=["'battery' and 'great' dominate; bigrams reveal 'battery life'", "VADER catches '!!' and negative words"],
  extend=["Scrape multiple pages with pagination and polite delays", "Build a word cloud"], see=["m-web-scraping", "m-text-preprocessing"]),

L("m-lab-pca", "Lab 11 · Dimensionality reduction and simple PCA", "Module 1",
  "Implement PCA with NumPy, compare with scikit-learn, choose the number of components and see the effect on a classifier.",
  "Digits dataset (64 pixel features).",
  ["Centre data and compute the covariance matrix", "Eigen-decompose and sort components", "Plot cumulative explained variance", "Train a classifier on 2, 10, 20, 40 components"],
  code="""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
X, y = load_digits(return_X_y=True); Xc = X - X.mean(0)
vals, vecs = np.linalg.eigh(np.cov(Xc.T)); order = np.argsort(vals)[::-1]; vals, vecs = vals[order], vecs[:, order]
Z = Xc @ vecs[:, :2]; Zs = PCA(2).fit_transform(X)
print("from-scratch PC1 matches sklearn (up to sign):", np.allclose(np.abs(Z[:, 0]), np.abs(Zs[:, 0]), atol=1e-6))
cum = np.cumsum(vals) / vals.sum(); print("variance explained by 2/10/20/40 components:", cum[[1, 9, 19, 39]].round(3))
for k in (2, 10, 20, 40, 64):
    s = cross_val_score(make_pipeline(StandardScaler(), PCA(k), LogisticRegression(max_iter=3000)), X, y, cv=5).mean(); print(f"{k:2d} components -> accuracy {s:.3f}")
""",
  observe=["20 of 64 components keep ~90% variance and nearly all accuracy", "2 components are enough to visualise but not to classify well"],
  extend=["Plot the 2-D projection coloured by digit", "Use PCA for denoising: reconstruct noisy digits"], see=["m-pca", "m-lin-transform"]),

L("m-lab-text", "Lab 12 · Text representation, generation and classification", "Module 1",
  "Represent text as bag-of-words/TF-IDF/embeddings, classify news-like headlines, and generate text with a bigram model.",
  "Small embedded headline dataset (use 20 Newsgroups or AG News in Colab for scale).",
  ["Vectorise with CountVectorizer and TfidfVectorizer", "Train Naive Bayes and logistic regression", "Inspect the most predictive words per class", "Train a bigram language model and generate headlines"],
  code="""
import random, numpy as np
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
heads = [("india wins the cricket series", "sport"), ("star batsman scores century in final", "sport"), ("football club signs new striker", "sport"),
         ("team captain injured before match", "sport"), ("sensex rises as banks rally", "business"), ("rupee falls against the dollar", "business"),
         ("startup raises funding from investors", "business"), ("bank cuts interest rates on loans", "business"), ("new phone launched with ai camera", "tech"),
         ("chip maker unveils faster processor", "tech"), ("app update brings dark mode", "tech"), ("ai model writes code for developers", "tech")] * 4
X, y = zip(*heads)
for name, vec in [("counts", CountVectorizer()), ("tf-idf", TfidfVectorizer())]:
    for clf in (MultinomialNB(), LogisticRegression(max_iter=1000)):
        from sklearn.pipeline import make_pipeline
        print(f"{name:7s} + {type(clf).__name__:18s} CV accuracy {cross_val_score(make_pipeline(vec, clf), X, y, cv=4).mean():.3f}")
m = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=1000)).fit(X, y); words = m[0].get_feature_names_out()
for k, c in enumerate(m[1].classes_): print(c, "->", [words[i] for i in np.argsort(m[1].coef_[k])[::-1][:4]])
nxt = defaultdict(Counter)
for h in set(X):
    toks = ["<s>"] + h.split() + ["</s>"]
    for a, b in zip(toks, toks[1:]): nxt[a][b] += 1
random.seed(7)
for _ in range(3):
    w, out = "<s>", []
    while True:
        w = random.choices(*zip(*nxt[w].items()))[0]
        if w == "</s>" or len(out) > 10: break
        out.append(w)
    print("generated:", " ".join(out))
""",
  observe=["Each class has clear indicative words", "Bigram generation is locally fluent but globally silly — why neural LMs exist"],
  extend=["Use sentence-transformer embeddings + logistic regression", "Fine-tune DistilBERT on AG News"], see=["m-text-representation", "m-language-models", "m-text-classification"]),

L("m-lab-separability", "Lab 13 · Separability: when is a linear model enough?", "Module 1",
  "Test linear separability, then make non-separable data separable with feature maps and kernels.",
  "Synthetic blobs, XOR and circles.",
  ["Fit a hard-margin linear SVM to detect separability", "Add hand-made features (x·y, x²+y²)", "Compare with RBF-kernel SVM and a small MLP"],
  code="""
import numpy as np
from sklearn.datasets import make_blobs, make_circles
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
rng = np.random.default_rng(0)
xor_X = rng.uniform(-1, 1, (400, 2)); xor_y = (xor_X[:, 0] * xor_X[:, 1] > 0).astype(int)
sets = {"blobs": make_blobs(300, centers=2, random_state=2), "XOR": (xor_X, xor_y), "circles": make_circles(300, factor=0.4, noise=0.05, random_state=0)}
maps = {"blobs": lambda X: X, "XOR": lambda X: np.c_[X, X[:, 0] * X[:, 1]], "circles": lambda X: np.c_[X, (X ** 2).sum(1)]}
for name, (X, y) in sets.items():
    lin = SVC(kernel="linear", C=1e4).fit(X, y).score(X, y); mapped = SVC(kernel="linear", C=1e4).fit(maps[name](X), y).score(maps[name](X), y)
    rbf = SVC(kernel="rbf").fit(X, y).score(X, y); mlp = MLPClassifier(hidden_layer_sizes=(16,), max_iter=3000, random_state=0).fit(X, y).score(X, y)
    print(f"{name:8s} linearly separable? {lin == 1.0!s:5s} | linear {lin:.2f}  with feature map {mapped:.2f}  RBF SVM {rbf:.2f}  MLP {mlp:.2f}")
""",
  observe=["Only blobs are linearly separable", "The right feature map makes XOR and circles linearly separable — kernels and hidden layers learn such maps"],
  extend=["Visualise the 3-D feature space", "Try a polynomial kernel of degree 2"], see=["m-separability", "m-kernels", "m-mlp"]),

L("m-lab-mlp", "Lab 14 · MLP classifier and MLP regression", "Module 2",
  "Train multilayer perceptrons for classification and regression, tune width/depth/regularisation, and read learning curves.",
  "Digits (classification) and a noisy non-linear function (regression).",
  ["Scale inputs", "Train MLPClassifier with different hidden sizes and alpha", "Train MLPRegressor on y = sin(x)·x", "Plot loss curves; use early stopping"],
  code="""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
X, y = load_digits(return_X_y=True); Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0); sc = StandardScaler().fit(Xtr)
for hidden, alpha in [((16,), 1e-4), ((128,), 1e-4), ((128, 64), 1e-4), ((128, 64), 1.0)]:
    m = MLPClassifier(hidden_layer_sizes=hidden, alpha=alpha, early_stopping=True, max_iter=500, random_state=0).fit(sc.transform(Xtr), ytr)
    print(f"hidden={str(hidden):10s} alpha={alpha:<6} epochs={m.n_iter_:3d} test acc={m.score(sc.transform(Xte), yte):.3f}")
rng = np.random.default_rng(0); x = rng.uniform(-6, 6, (800, 1)); yr = (np.sin(x) * x).ravel() + rng.normal(0, 0.3, 800)
for hidden in [(4,), (64, 64)]:
    r = MLPRegressor(hidden_layer_sizes=hidden, max_iter=4000, random_state=0).fit(x[:600], yr[:600])
    print(f"regression hidden={str(hidden):8s} test R2={r.score(x[600:], yr[600:]):.3f}  final loss {r.loss_curve_[-1]:.3f}")
""",
  observe=["Too few units underfit; strong alpha (L2) over-regularises", "A 2-layer MLP fits the wavy function well"],
  extend=["Rebuild the best MLP in PyTorch", "Plot loss_curve_ and validation_scores_"], see=["m-mlp", "m-dl-regularization"]),

L("m-lab-svm", "Lab 15 · Support vector machines with kernels", "Module 3",
  "Tune C and gamma for an RBF SVM, inspect support vectors, and compare kernels on a real dataset.",
  "Breast cancer dataset and two-moons.",
  ["Grid-search C and gamma with a pipeline", "Compare linear, poly and RBF kernels", "Count support vectors as C changes"],
  code="""
from sklearn.datasets import load_breast_cancer, make_moons
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, cross_val_score
X, y = load_breast_cancer(return_X_y=True)
for k in ("linear", "poly", "rbf"): print(f"{k:6s} kernel CV accuracy {cross_val_score(make_pipeline(StandardScaler(), SVC(kernel=k)), X, y, cv=5).mean():.4f}")
gs = GridSearchCV(make_pipeline(StandardScaler(), SVC()), {"svc__C": [0.1, 1, 10, 100], "svc__gamma": ["scale", 0.001, 0.01, 0.1]}, cv=5).fit(X, y)
print("best:", gs.best_params_, round(gs.best_score_, 4))
Xm, ym = make_moons(300, noise=0.25, random_state=0)
for C in (0.1, 1, 100): m = SVC(C=C).fit(Xm, ym); print(f"moons C={C:<5} support vectors {m.n_support_.sum():3d}  train acc {m.score(Xm, ym):.3f}")
""",
  observe=["Scaling + RBF is a strong default", "Larger C → fewer support vectors and a tighter fit"],
  extend=["Try SVR on a regression dataset", "Time SVC vs LinearSVC on 50k rows"], see=["m-svm", "m-kernels"]),

L("m-lab-rf", "Lab 16 · Random forests and feature importance", "Module 3",
  "Train and tune a random forest, compare impurity vs permutation importance, and inspect partial dependence.",
  "Synthetic employee-attrition data (mirrors the talent-retention capstone).",
  ["Generate HR-style features", "Train RandomForestClassifier with class weights", "Tune n_estimators, max_features, min_samples_leaf", "Compare importance methods"],
  code="""
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
rng = np.random.default_rng(0); n = 3000
df = pd.DataFrame({"satisfaction": rng.uniform(0, 1, n), "overtime_hours": rng.exponential(10, n), "years_at_company": rng.integers(0, 20, n),
                   "salary_hike_pct": rng.uniform(0, 25, n), "distance_km": rng.uniform(1, 40, n), "employee_id": rng.permutation(n)})
logit = 1.5 - 4 * df["satisfaction"] + 0.08 * df["overtime_hours"] - 0.1 * df["years_at_company"] - 0.08 * df["salary_hike_pct"]
y = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int); print("attrition rate:", y.mean().round(3))
Xtr, Xte, ytr, yte = train_test_split(df, y, stratify=y, random_state=0)
rs = RandomizedSearchCV(RandomForestClassifier(class_weight="balanced", random_state=0, n_jobs=-1), {"n_estimators": [100, 300], "max_features": ["sqrt", 0.5, 1.0], "min_samples_leaf": [1, 5, 20]},
                        n_iter=8, cv=4, scoring="roc_auc", random_state=0).fit(Xtr, ytr)
rf = rs.best_estimator_; print("best params:", rs.best_params_, " test ROC-AUC:", round(roc_auc_score(yte, rf.predict_proba(Xte)[:, 1]), 3))
imp = pd.DataFrame({"impurity": rf.feature_importances_, "permutation": permutation_importance(rf, Xte, yte, scoring="roc_auc", n_repeats=5, random_state=0).importances_mean}, index=df.columns)
print(imp.sort_values("permutation", ascending=False).round(3))
""",
  observe=["Satisfaction and overtime drive attrition", "Impurity importance gives the random 'employee_id' some credit; permutation importance correctly says ~0"],
  extend=["Use the IBM HR Analytics attrition dataset", "Explain individual predictions with SHAP"], see=["m-random-forest", "m-interpretability"]),

L("m-lab-xgboost", "Lab 17 · XGBoost with early stopping and imbalance handling", "Module 3",
  "Train an XGBoost classifier with a validation set, early stopping, scale_pos_weight and threshold tuning.",
  "Synthetic imbalanced 'fraud' data.",
  ["Split train/validation/test", "Train with early stopping on validation log-loss", "Set scale_pos_weight for imbalance", "Tune the threshold for F1 and report PR-AUC"],
  code="""
import numpy as np, xgboost as xgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score, f1_score, precision_recall_curve
X, y = make_classification(30000, 25, n_informative=10, weights=[0.97], class_sep=1.2, random_state=0)
Xtv, Xte, ytv, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0); Xtr, Xva, ytr, yva = train_test_split(Xtv, ytv, test_size=0.2, stratify=ytv, random_state=0)
for spw in (1, (ytr == 0).sum() / (ytr == 1).sum()):
    m = xgb.XGBClassifier(n_estimators=2000, learning_rate=0.05, max_depth=5, subsample=0.8, colsample_bytree=0.8, scale_pos_weight=spw,
                          early_stopping_rounds=50, eval_metric="aucpr", random_state=0).fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    pv = m.predict_proba(Xva)[:, 1]; pr, rc, th = precision_recall_curve(yva, pv); f1 = 2 * pr * rc / (pr + rc + 1e-9); t = th[np.argmax(f1[:-1])]
    pt = m.predict_proba(Xte)[:, 1]
    print(f"scale_pos_weight={spw:5.1f}: trees {m.best_iteration:4d}  test PR-AUC {average_precision_score(yte, pt):.3f}  F1@0.5 {f1_score(yte, pt > 0.5):.3f}  F1@tuned({t:.2f}) {f1_score(yte, pt > t):.3f}")
print("top features by gain:", [(f, round(g, 1)) for f, g in sorted(m.get_booster().get_score(importance_type="gain").items(), key=lambda kv: -kv[1])[:3]])
""",
  observe=["Early stopping picks the number of trees", "Threshold tuning matters as much as class weighting for F1"],
  extend=["Compare LightGBM and CatBoost", "Tune with Optuna"], see=["m-gradient-boosting", "m-imbalance"]),

L("m-lab-nlp-speech", "Lab 18 · NLP and speech: from audio features to text features", "Module 3",
  "Extract MFCCs from synthetic 'spoken digit' sounds and classify them; then classify short commands as text.",
  "Synthetic tone-sequence 'words' (use the Free Spoken Digit Dataset or Google Speech Commands in Colab).",
  ["Generate audio clips for 3 'words' with different pitch contours", "Compute MFCC mean/std features with librosa", "Train a classifier and report accuracy", "Build a text intent classifier for the transcribed commands"],
  code="""
import numpy as np, librosa
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
rng = np.random.default_rng(0); sr = 16000
contours = {"yes": (300, 500), "no": (400, 250), "stop": (200, 200)}
def clip(word):
    f0, f1 = contours[word]; t = np.arange(int(0.5 * sr)) / sr; f = np.linspace(f0, f1, t.size) * rng.uniform(0.9, 1.1)
    return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.hanning(t.size) + 0.05 * rng.normal(size=t.size)
X, y = [], []
for w in contours:
    for _ in range(40):
        m = librosa.feature.mfcc(y=clip(w), sr=sr, n_mfcc=13); X.append(np.r_[m.mean(1), m.std(1)]); y.append(w)
print("audio clips:", len(X), " MFCC feature size:", len(X[0]))
print("spoken-word classifier CV accuracy:", cross_val_score(RandomForestClassifier(random_state=0), np.array(X), y, cv=5).mean().round(3))
cmds = [("turn on the lights", "lights_on"), ("switch the lights on", "lights_on"), ("lights off please", "lights_off"), ("turn off the light", "lights_off"),
        ("play some music", "music"), ("start a song", "music")] * 3
nlu = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000)).fit(*zip(*cmds))
print("intent for 'please turn the lights on':", nlu.predict(["please turn the lights on"])[0])
""",
  observe=["MFCC statistics separate words by pitch/spectral shape", "A voice assistant = ASR (speech→text) + NLU (text→intent)"],
  extend=["Use Whisper to transcribe real audio (needs internet)", "Train a small CNN on log-mel spectrograms"], see=["m-speech-features", "m-speech-recognition"]),

L("m-lab-manifold", "Lab 19 · ISOMAP and t-SNE", "Module 3",
  "Unroll a Swiss roll with ISOMAP and visualise digits with t-SNE; study the effect of n_neighbors and perplexity.",
  "Swiss roll and digits.",
  ["Embed the Swiss roll with PCA vs ISOMAP", "Vary n_neighbors", "Run t-SNE on digits with perplexity 5, 30, 50", "Measure trustworthiness"],
  code="""
from sklearn.datasets import make_swiss_roll, load_digits
from sklearn.manifold import Isomap, TSNE, trustworthiness
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
X, t = make_swiss_roll(1200, noise=0.05, random_state=0)
print("PCA recovers roll position:", round(abs(spearmanr(PCA(1).fit_transform(X)[:, 0], t).statistic), 2))
for k in (5, 10, 30, 80):
    print(f"ISOMAP n_neighbors={k:2d}: |spearman| = {abs(spearmanr(Isomap(n_neighbors=k, n_components=1).fit_transform(X)[:, 0], t).statistic):.2f}")
Xd, yd = load_digits(return_X_y=True); Xp = PCA(30, random_state=0).fit_transform(Xd)
for perp in (5, 30, 50):
    Z = TSNE(2, perplexity=perp, init="pca", random_state=0).fit_transform(Xp); print(f"t-SNE perplexity {perp:2d}: trustworthiness {trustworthiness(Xd, Z, n_neighbors=10):.3f}")
""",
  observe=["PCA can't unroll the roll; ISOMAP can with a sensible n_neighbors", "Too many neighbours short-circuits the manifold"],
  extend=["Plot the embeddings coloured by t / digit", "Try UMAP (pip install umap-learn)"], see=["m-manifold"]),

L("m-lab-overfit", "Lab 20 · Train/validation/test splits and avoiding overfitting", "Module 1",
  "Diagnose overfitting with learning and validation curves, then fix it with regularisation, early stopping and more data.",
  "Digits dataset and a deliberately over-sized model.",
  ["Make a proper train/validation/test split", "Plot validation curve over tree depth", "Plot learning curve over training size", "Compare an over-sized MLP with/without early stopping and L2"],
  code="""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import validation_curve, learning_curve, train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
X, y = load_digits(return_X_y=True)
depths = [2, 4, 8, 16, 32]; tr, va = validation_curve(DecisionTreeClassifier(random_state=0), X, y, param_name="max_depth", param_range=depths, cv=5)
for d, a, b in zip(depths, tr.mean(1), va.mean(1)): print(f"depth {d:2d}: train {a:.3f}  validation {b:.3f}  gap {a - b:.3f}")
sizes, tr, va = learning_curve(DecisionTreeClassifier(max_depth=10, random_state=0), X, y, train_sizes=[0.1, 0.3, 0.6, 1.0], cv=5)
for s, a, b in zip(sizes, tr.mean(1), va.mean(1)): print(f"{s:4d} samples: train {a:.3f} validation {b:.3f}")
Xtr, Xte, ytr, yte = train_test_split(X / 16, y, train_size=300, random_state=0, stratify=y)
for name, m in [("big MLP, no regularisation", MLPClassifier(hidden_layer_sizes=(512, 512), alpha=0, max_iter=400, random_state=0)),
                ("big MLP + L2 + early stopping", MLPClassifier(hidden_layer_sizes=(512, 512), alpha=1e-2, early_stopping=True, max_iter=400, random_state=0))]:
    m.fit(Xtr, ytr); print(f"{name:30s} train {m.score(Xtr, ytr):.3f}  test {m.score(Xte, yte):.3f}")
""",
  observe=["Deep trees: train → 1.0 while validation plateaus (overfitting)", "Validation keeps rising with more data → variance problem"],
  extend=["Add data augmentation (shifted digits)", "Use nested CV for an unbiased estimate"], see=["m-overfitting", "m-train-val-test", "m-regularization"]),

L("m-lab-clustering", "Lab 21 · k-means and hierarchical clustering: customer segmentation", "Module 1",
  "Segment retail customers with RFM features using k-means and hierarchical clustering, choose k, and profile the segments.",
  "Synthetic retail transactions (mirrors the retail customer segmentation capstone; try the UCI Online Retail dataset).",
  ["Build Recency, Frequency, Monetary features per customer", "Log-transform and scale", "Choose k with elbow and silhouette", "Compare with Ward hierarchical clustering", "Name each segment from its profile"],
  code="""
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
rng = np.random.default_rng(0); rows = []
for cid in range(600):
    kind = rng.choice(["loyal", "occasional", "big_spender", "lapsed"], p=[0.3, 0.4, 0.1, 0.2])
    n_tx = {"loyal": 25, "occasional": 5, "big_spender": 8, "lapsed": 3}[kind]; amt = {"loyal": 40, "occasional": 30, "big_spender": 400, "lapsed": 35}[kind]
    last = {"loyal": 10, "occasional": 60, "big_spender": 30, "lapsed": 300}[kind]
    for _ in range(max(1, rng.poisson(n_tx))): rows.append((cid, int(rng.integers(last, last + 60)), rng.gamma(2, amt / 2), kind))
tx = pd.DataFrame(rows, columns=["customer", "days_ago", "amount", "true_type"])
rfm = tx.groupby("customer").agg(recency=("days_ago", "min"), frequency=("amount", "size"), monetary=("amount", "sum"), true_type=("true_type", "first"))
Z = StandardScaler().fit_transform(np.log1p(rfm[["recency", "frequency", "monetary"]]))
for k in range(2, 8):
    km = KMeans(k, n_init=10, random_state=0).fit(Z); print(f"k={k} inertia {km.inertia_:7.1f} silhouette {silhouette_score(Z, km.labels_):.3f}")
rfm["kmeans"] = KMeans(4, n_init=10, random_state=0).fit_predict(Z); rfm["ward"] = AgglomerativeClustering(4, linkage="ward").fit_predict(Z)
print("agreement k-means vs Ward (ARI):", round(adjusted_rand_score(rfm["kmeans"], rfm["ward"]), 2))
print(rfm.groupby("kmeans")[["recency", "frequency", "monetary"]].median().round(0).assign(size=rfm["kmeans"].value_counts()))
""",
  observe=["Segments map to loyal / occasional / big spenders / lapsed", "Business naming of clusters is the real deliverable"],
  extend=["Plot a dendrogram (scipy)", "Try GMM and DBSCAN", "Recommend one action per segment"], see=["m-kmeans", "m-hierarchical"]),

L("m-lab-eigenfaces", "Lab 22 · PCA EigenFaces", "Module 3",
  "Build an EigenFaces face recogniser: PCA on face images + SVM, reconstruct faces from a few components.",
  "Olivetti faces (downloads automatically in Colab; the code falls back to synthetic data offline) or LFW people.",
  ["Load faces and split by person", "Fit PCA, view eigenfaces and explained variance", "Train an SVM on PCA features", "Reconstruct a face with 10, 50, 150 components"],
  reuse="m-eigenfaces", observe=["~60 eigenfaces capture most variation", "Accuracy is high on aligned, evenly lit faces"],
  extend=["Try LFW (fetch_lfw_people) — harder", "Compare with Fisherfaces (PCA + LDA)"], see=["m-eigenfaces", "m-pca"]),

L("m-lab-nn-scratch", "Lab 23 · Gradient descent, perceptrons and a simple neural network from scratch", "Module 2",
  "Implement a perceptron and a 2-layer neural network with backpropagation in NumPy, check gradients numerically, and solve XOR and moons.",
  "XOR and two-moons.",
  ["Train a perceptron on AND/OR; watch it fail on XOR", "Write forward/backward for a 2-layer net", "Gradient-check against finite differences", "Train on moons with mini-batch GD"],
  code="""
import numpy as np
from sklearn.datasets import make_moons
rng = np.random.default_rng(0)
class TwoLayerNet:
    def __init__(self, d, h): self.W1 = rng.normal(0, np.sqrt(2 / d), (d, h)); self.b1 = np.zeros(h); self.W2 = rng.normal(0, np.sqrt(1 / h), (h, 1)); self.b2 = np.zeros(1)
    def forward(self, X):
        self.X = X; self.z1 = X @ self.W1 + self.b1; self.a1 = np.tanh(self.z1); self.p = 1 / (1 + np.exp(-(self.a1 @ self.W2 + self.b2))); return self.p
    def loss(self, y): return -np.mean(y * np.log(self.p + 1e-12) + (1 - y) * np.log(1 - self.p + 1e-12))
    def backward(self, y):
        n = len(y); dz2 = (self.p - y) / n; self.gW2 = self.a1.T @ dz2; self.gb2 = dz2.sum(0)
        dz1 = dz2 @ self.W2.T * (1 - self.a1 ** 2); self.gW1 = self.X.T @ dz1; self.gb1 = dz1.sum(0)
net = TwoLayerNet(2, 8); Xg = rng.normal(size=(5, 2)); yg = rng.integers(0, 2, (5, 1))
net.forward(Xg); net.backward(yg); eps = 1e-5; i, j = 1, 3; net.W1[i, j] += eps; net.forward(Xg); lp = net.loss(yg); net.W1[i, j] -= 2 * eps; net.forward(Xg); lm = net.loss(yg); net.W1[i, j] += eps
print(f"gradient check: analytic {net.gW1[i, j]:.6f} vs numeric {(lp - lm) / (2 * eps):.6f}")
for name, (X, y) in {"XOR": (np.array([[0, 0], [0, 1], [1, 0], [1, 1.]]), np.array([[0], [1], [1], [0.]])), "moons": (lambda d: (d[0], d[1][:, None].astype(float)))(make_moons(500, noise=0.2, random_state=0))}.items():
    net = TwoLayerNet(2, 16)
    for epoch in range(3000):
        idx = rng.permutation(len(X))
        for b in range(0, len(X), 64):
            sl = idx[b:b + 64]; net.forward(X[sl]); net.backward(y[sl])
            for P, G in [("W1", "gW1"), ("b1", "gb1"), ("W2", "gW2"), ("b2", "gb2")]: setattr(net, P, getattr(net, P) - 0.5 * getattr(net, G))
    print(f"{name}: final loss {net.loss(y) if net.forward(X) is not None else 0:.4f}, accuracy {((net.forward(X) > 0.5) == y).mean():.3f}")
""",
  observe=["Analytic and numeric gradients agree to ~6 decimals", "A hidden layer with tanh solves XOR and moons"],
  extend=["Add ReLU and softmax for 3 classes", "Implement momentum and Adam"], see=["m-perceptron", "m-backprop", "m-gradients"]),

L("m-lab-reconstruct", "Lab 24 · Image reconstruction with autoencoders (denoising and inpainting)", "Module 3",
  "Train a convolutional autoencoder to denoise digits and fill in missing patches, and measure PSNR.",
  "Digits (8×8); use MNIST/Fashion-MNIST via torchvision in Colab for 28×28 images.",
  ["Corrupt images with noise and random masks", "Build a conv encoder–decoder", "Train to reconstruct clean images", "Compare PSNR of corrupted vs reconstructed images"],
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
torch.manual_seed(0); X = torch.tensor(load_digits().images / 16, dtype=torch.float32)[:, None]; Xtr, Xte = X[:1500], X[1500:]
def corrupt(x):
    noisy = (x + 0.25 * torch.randn_like(x)).clamp(0, 1); mask = torch.ones_like(x)
    for i in range(len(x)): r, c = torch.randint(0, 5, (2,)).tolist(); mask[i, :, r:r + 3, c:c + 3] = 0
    return noisy * mask
net = nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                    nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.Upsample(scale_factor=2), nn.Conv2d(64, 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, 1, 3, padding=1), nn.Sigmoid())
opt = torch.optim.Adam(net.parameters(), 2e-3)
for epoch in range(25):
    for i in range(0, 1500, 100): xb = Xtr[i:i + 100]; opt.zero_grad(); F.mse_loss(net(corrupt(xb)), xb).backward(); opt.step()
psnr = lambda a, b: (10 * torch.log10(1 / F.mse_loss(a, b))).item()
with torch.no_grad(): c = corrupt(Xte); r = net(c)
print(f"PSNR corrupted {psnr(c, Xte):.2f} dB -> reconstructed {psnr(r, Xte):.2f} dB")
""",
  observe=["The network learns digit shapes and fills masked holes", "PSNR improves several dB"],
  extend=["Use Fashion-MNIST at 28×28", "Try a U-Net with skip connections", "Super-resolution: input a downsampled image"], see=["m-autoencoder", "m-super-resolution"]),

L("m-lab-pytorch", "Lab 25 · PyTorch fundamentals", "Module 3",
  "Practise tensors, autograd, nn.Module, DataLoader, GPU use, training/evaluation loops, checkpointing.",
  "Synthetic tabular regression and digits classification.",
  ["Tensor operations and shapes, moving to GPU", "Autograd on a small function", "Write a Dataset and DataLoader", "Train an MLP with a full loop, evaluate, save and reload"],
  code="""
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
dev = "cuda" if torch.cuda.is_available() else "cpu"; torch.manual_seed(0)
a = torch.arange(12.).reshape(3, 4); print("shape", a.shape, "| sum over rows", a.sum(0), "| matmul", (a @ a.T).shape, "| device", a.to(dev).device)
x = torch.tensor(2.0, requires_grad=True); y = x ** 3 + 4 * x; y.backward(); print("dy/dx at 2 =", x.grad.item(), "(3*4 + 4 = 16)")
X = torch.randn(2000, 5); w_true = torch.tensor([1.5, -2.0, 0.5, 0.0, 3.0]); y = X @ w_true + 0.3 * torch.randn(2000)
dl = DataLoader(TensorDataset(X[:1600], y[:1600]), batch_size=64, shuffle=True)
model = nn.Sequential(nn.Linear(5, 32), nn.ReLU(), nn.Linear(32, 1)).to(dev); opt = torch.optim.AdamW(model.parameters(), 1e-2); lossf = nn.MSELoss()
for epoch in range(20):
    model.train()
    for xb, yb in dl: xb, yb = xb.to(dev), yb.to(dev); opt.zero_grad(); loss = lossf(model(xb).squeeze(1), yb); loss.backward(); opt.step()
    model.eval()
    with torch.no_grad(): val = lossf(model(X[1600:].to(dev)).squeeze(1), y[1600:].to(dev)).item()
    if epoch % 5 == 4: print(f"epoch {epoch + 1}: val MSE {val:.4f}")
torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "epoch": epoch}, "ckpt.pt")
ck = torch.load("ckpt.pt"); model.load_state_dict(ck["model"]); print("checkpoint restored from epoch", ck["epoch"] + 1)
""",
  observe=["Autograd matches hand derivatives", "Validation MSE approaches the noise level (0.09)"],
  extend=["Add a learning-rate scheduler", "Use torch.compile and mixed precision on GPU"], see=["m-pytorch"]),

L("m-lab-keras", "Lab 26 · TensorFlow / Keras: a CNN image classifier", "Module 3",
  "Build, train and evaluate a CNN with Keras, using callbacks, augmentation layers and saving.",
  "Digits (8×8) here; use keras.datasets.mnist / fashion_mnist / cifar10 in Colab.",
  ["Prepare images (N, H, W, C) and scale", "Build a Sequential CNN with augmentation layers", "compile/fit with EarlyStopping", "Evaluate, show a confusion matrix, save .keras"],
  code="""
import os; os.environ.setdefault("KERAS_BACKEND", "torch")      # Colab default is TensorFlow; any backend works
import numpy as np, keras
from keras import layers
from sklearn.datasets import load_digits
from sklearn.metrics import confusion_matrix
keras.utils.set_random_seed(0)
d = load_digits(); X = (d.images / 16).astype("float32")[..., None]; y = d.target          # (N, 8, 8, 1)
Xtr, Xte, ytr, yte = X[:1500], X[1500:], y[:1500], y[1500:]
model = keras.Sequential([keras.Input((8, 8, 1)), layers.RandomTranslation(0.1, 0.1),
                          layers.Conv2D(32, 3, padding="same", activation="relu"), layers.BatchNormalization(), layers.MaxPooling2D(),
                          layers.Conv2D(64, 3, padding="same", activation="relu"), layers.GlobalAveragePooling2D(), layers.Dropout(0.3), layers.Dense(10, activation="softmax")])
model.compile(optimizer=keras.optimizers.Adam(2e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
h = model.fit(Xtr, ytr, validation_split=0.15, epochs=40, batch_size=64, verbose=0, callbacks=[keras.callbacks.EarlyStopping(patience=6, restore_best_weights=True)])
print("epochs:", len(h.history["loss"]), " test:", dict(zip(model.metrics_names, np.round(model.evaluate(Xte, yte, verbose=0), 3))))
print(confusion_matrix(yte, model.predict(Xte, verbose=0).argmax(1)))
model.save("digits_cnn.keras"); print("saved digits_cnn.keras")
""",
  observe=["CNN beats the MLP on images with fewer parameters", "EarlyStopping restores the best epoch"],
  extend=["Train on Fashion-MNIST", "Visualise first-layer filters"], see=["m-keras", "m-cnn"]),

L("m-lab-rnn", "Lab 27 · Recurrent neural networks: character-level text generation", "Module 3",
  "Train a GRU language model on a small text, sample with temperature, and compare with an LSTM.",
  "An embedded paragraph (use a book from Project Gutenberg in Colab).",
  ["Build a character vocabulary", "Create input/target sequences shifted by one", "Train an embedding + GRU + linear model", "Generate text with different temperatures"],
  code="""
import torch, torch.nn as nn
torch.manual_seed(0)
text = ("machine learning is the study of algorithms that learn from data. deep learning uses neural networks with many layers. "
        "neural networks learn features from data. learning from data is the heart of machine learning. ") * 6
chars = sorted(set(text)); stoi = {c: i for i, c in enumerate(chars)}; data = torch.tensor([stoi[c] for c in text])
L = 40; X = torch.stack([data[i:i + L] for i in range(0, len(data) - L - 1, 3)]); Y = torch.stack([data[i + 1:i + L + 1] for i in range(0, len(data) - L - 1, 3)])
class CharRNN(nn.Module):
    def __init__(self, V, cell=nn.GRU): super().__init__(); self.emb = nn.Embedding(V, 32); self.rnn = cell(32, 128, batch_first=True); self.out = nn.Linear(128, V)
    def forward(self, x, h=None): o, h = self.rnn(self.emb(x), h); return self.out(o), h
m = CharRNN(len(chars)); opt = torch.optim.Adam(m.parameters(), 5e-3)
for epoch in range(30):
    for i in range(0, len(X), 32): logits, _ = m(X[i:i + 32]); loss = nn.functional.cross_entropy(logits.reshape(-1, len(chars)), Y[i:i + 32].reshape(-1)); opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1); opt.step()
print("final loss:", round(loss.item(), 3))
@torch.no_grad()
def sample(seed, n=80, T=0.5):
    x = torch.tensor([[stoi[c] for c in seed]]); h = None; out = seed
    for _ in range(n):
        logits, h = m(x, h); c = torch.multinomial(torch.softmax(logits[0, -1] / T, 0), 1).item(); out += chars[c]; x = torch.tensor([[c]])
    return out
for T in (0.2, 1.0): print(f"T={T}:", sample("neural ", T=T))
""",
  observe=["Low temperature repeats training phrases; high temperature invents words", "The model learns spelling and word boundaries from characters alone"],
  extend=["Swap GRU for LSTM and compare loss", "Train on a larger corpus on GPU"], see=["m-rnn", "m-lstm-gru", "m-decoding"]),

L("m-lab-timeseries", "Lab 28 · Time-series forecasting: logistics daily demand", "Module 3",
  "Forecast daily order demand with seasonal naive, SARIMA and gradient boosting on lag features, using walk-forward validation.",
  "Synthetic daily logistics demand with trend, weekly seasonality and holidays (mirrors the logistics capstone).",
  ["Create the series and plot it", "Decompose into trend/seasonality", "Build lag and calendar features", "Walk-forward evaluate three models with MAE and MAPE"],
  code="""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import HistGradientBoostingRegressor
rng = np.random.default_rng(1); idx = pd.date_range("2024-01-01", "2025-12-31", freq="D"); t = np.arange(len(idx))
holiday = idx.strftime("%m-%d").isin(["01-26", "08-15", "10-02", "11-01", "12-25"])
y = pd.Series(500 + 0.4 * t + 80 * np.isin(idx.dayofweek, [0, 1]) - 120 * (idx.dayofweek == 6) - 200 * holiday + 40 * np.sin(2 * np.pi * t / 365) + rng.normal(0, 25, len(t)), idx)
def features(s):
    f = pd.DataFrame({"y": s, "dow": s.index.dayofweek, "month": s.index.month, "holiday": holiday[: len(s)].astype(int), "t": np.arange(len(s))})
    for l in (7, 14, 28): f[f"lag{l}"] = s.shift(l)
    f["roll7"] = s.shift(7).rolling(7).mean(); return f
F = features(y); horizon = 28; res = {"seasonal naive": [], "SARIMA": [], "GBM lags": []}
for origin in pd.date_range("2025-09-01", periods=4, freq="28D"):
    train, test = y[:origin - pd.Timedelta(days=1)], y[origin: origin + pd.Timedelta(days=horizon - 1)]
    res["seasonal naive"].append(np.abs(test.values - np.resize(train[-7:].values, len(test))).mean())
    sar = SARIMAX(train[-400:], order=(1, 0, 1), seasonal_order=(1, 1, 1, 7), trend="t").fit(disp=False).forecast(len(test))
    res["SARIMA"].append(np.abs(test.values - sar.values).mean())
    tr, te = F.loc[: train.index[-1]].dropna(), F.loc[test.index]
    g = HistGradientBoostingRegressor(random_state=0).fit(tr.drop(columns="y"), tr["y"]); res["GBM lags"].append(np.abs(test.values - g.predict(te.drop(columns="y"))).mean())
for k, v in res.items(): print(f"{k:15s} walk-forward MAE {np.mean(v):6.1f}  (MAPE ~{np.mean(v) / y[-120:].mean():.1%})")
""",
  observe=["Calendar + holiday features let GBM handle holiday dips naive models miss", "Walk-forward over several origins gives a stable estimate"],
  extend=["Add Prophet", "Train an LSTM global model across many warehouses"], see=["m-time-series", "m-ts-dl"]),

L("m-lab-transfer", "Lab 29 · Transfer learning and fine-tuning an image model", "Module 3",
  "Fine-tune a pretrained ResNet-18 on a small image dataset: frozen-backbone training, then unfreezing with discriminative learning rates.",
  "In Colab: a folder of images per class (e.g. Kaggle 'Food-11', flowers, or your own photos) loaded with torchvision.datasets.ImageFolder.",
  ["Load pretrained weights and the matching transforms", "Replace the final layer", "Train the head only, then unfreeze layer4", "Evaluate and check Grad-CAM on errors"],
  reuse="m-transfer-learning", observe=["Head-only training is fast and already strong", "Unfreezing with a small lr adds a few points"],
  extend=["Use timm for EfficientNet/ConvNeXt", "Export the model to ONNX"], see=["m-transfer-learning", "m-augmentation"]),

L("m-lab-sentiment", "Lab 30 · Sentiment analysis: lexicon vs classical ML vs transformer", "Module 3",
  "Compare VADER, TF-IDF + logistic regression and (in Colab) a fine-tuned DistilBERT on product reviews, and analyse errors.",
  "Embedded review set; in Colab use IMDB or Amazon/Flipkart reviews from Hugging Face datasets.",
  ["Score reviews with VADER", "Train TF-IDF + logistic regression with word and char n-grams", "Evaluate macro-F1 and confusion matrix", "Inspect misclassified examples (negation, sarcasm)"],
  code="""
import nltk; nltk.download("vader_lexicon", quiet=True)
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import f1_score, confusion_matrix
pos = ["absolutely love this phone", "battery life is amazing", "great value for money", "camera quality is superb", "fast delivery and great packing", "works perfectly, very happy",
       "not bad at all, quite good actually", "display is gorgeous", "best purchase this year", "sound is crisp and clear"]
neg = ["stopped working after a week", "battery drains too fast", "not worth the money", "camera is blurry and slow", "late delivery and damaged box", "very disappointed with quality",
       "not good, would not recommend", "screen cracked easily", "worst purchase ever", "yeah great, it broke on day one"]
texts, y = pos * 3 + neg * 3, np.array([1] * 30 + [0] * 30)
sia = SentimentIntensityAnalyzer(); vader = np.array([sia.polarity_scores(t)["compound"] > 0 for t in texts]).astype(int)
print("VADER macro-F1:", round(f1_score(y, vader, average="macro"), 3))
clf = make_pipeline(make_union(TfidfVectorizer(ngram_range=(1, 2)), TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))), LogisticRegression(C=10, max_iter=2000))
pred = cross_val_predict(clf, texts, y, cv=5); print("TF-IDF + LR macro-F1:", round(f1_score(y, pred, average="macro"), 3)); print(confusion_matrix(y, pred))
print("VADER mistakes:", sorted({t for t, p, l in zip(texts, vader, y) if p != l}))
# Colab: pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")(texts)
""",
  observe=["Lexicons stumble on sarcasm ('yeah great, it broke')", "Supervised models learn domain words like 'drains'"],
  extend=["Fine-tune DistilBERT (Lab 36)", "Aspect-based sentiment: battery vs camera"], see=["m-text-classification", "m-finetune-bert"]),

L("m-lab-emotion", "Lab 31 · Emotion recognition from faces and speech", "Module 3",
  "Build the pipeline: detect faces → crop → classify expression; extract prosody features from speech → classify emotion.",
  "In Colab: FER-2013 (Kaggle) for faces, RAVDESS for speech. Offline here: synthetic speech features.",
  ["Detect faces with OpenCV (Haar or YuNet) and crop to 48×48", "Train a small CNN on FER-2013 (7 classes)", "Extract pitch/energy/MFCC features from speech clips", "Train a speech-emotion classifier and report per-class recall"],
  reuse="m-face-emotion", observe=["Speech energy and pitch variability separate high- and low-arousal emotions", "FER accuracy ~65–73% is typical — the task is hard"],
  extend=["Fuse face and voice predictions", "Evaluate accuracy per demographic group"], see=["m-face-emotion", "m-speech-features"]),

L("m-lab-route", "Lab 32 · Optimal route: shortest paths and delivery-route optimisation", "Module 1",
  "Find shortest delivery paths on a city road graph with Dijkstra and A*, then optimise a multi-stop route (travelling salesman) with heuristics.",
  "A synthetic city grid with random road speeds (use OpenStreetMap via osmnx in Colab).",
  ["Build a weighted graph", "Run Dijkstra and A* with a straight-line heuristic", "Compare nodes expanded", "Order 10 delivery stops with nearest-neighbour + 2-opt"],
  code="""
import heapq, math, random
random.seed(0); N = 15
nodes = {(r, c): (c * 1.0, r * 1.0) for r in range(N) for c in range(N)}
graph = {u: [] for u in nodes}
for (r, c) in nodes:
    for dr, dc in ((0, 1), (1, 0)):
        v = (r + dr, c + dc)
        if v in nodes:
            minutes = random.uniform(1, 4); graph[(r, c)].append((v, minutes)); graph[v].append(((r, c), minutes))
def search(start, goal, heuristic):
    pq, best, expanded = [(0, 0, start)], {start: 0}, 0
    while pq:
        f, g, u = heapq.heappop(pq); expanded += 1
        if u == goal: return g, expanded
        if g > best[u]: continue
        for v, w in graph[u]:
            if g + w < best.get(v, 1e18): best[v] = g + w; heapq.heappush(pq, (g + w + heuristic(v, goal), g + w, v))
h_zero = lambda a, b: 0
h_euclid = lambda a, b: abs(nodes[a][0] - nodes[b][0]) + abs(nodes[a][1] - nodes[b][1])   # Manhattan blocks x 1 min: admissible, every block costs >= 1 min
for name, h in [("Dijkstra", h_zero), ("A*", h_euclid)]:
    cost, exp = search((0, 0), (N // 2, N - 1), h); print(f"{name:8s} travel time {cost:.1f} min, nodes expanded {exp}")
stops = random.sample(list(nodes), 10); depot = (0, 0)
dist = {(a, b): search(a, b, h_euclid)[0] for a in stops + [depot] for b in stops + [depot] if a != b}
route, left = [depot], set(stops)
while left: nxt = min(left, key=lambda s: dist[(route[-1], s)]); route.append(nxt); left.remove(nxt)
route.append(depot); length = lambda rt: sum(dist[(rt[i], rt[i + 1])] for i in range(len(rt) - 1))
print("nearest-neighbour route:", round(length(route), 1), "min")
improved = True
while improved:
    improved = False
    for i in range(1, len(route) - 2):
        for j in range(i + 1, len(route) - 1):
            new = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
            if length(new) < length(route) - 1e-9: route, improved = new, True
print("after 2-opt improvement:", round(length(route), 1), "min")
""",
  observe=["A* finds the same optimal path while expanding fewer nodes", "2-opt shortens the greedy delivery tour"],
  extend=["Use real roads with osmnx + networkx", "Add time windows with Google OR-Tools", "Predict travel times with ML and plug them in"], see=["m-search-ai"]),

L("m-lab-image-pipeline", "Lab 33 · Image augmentation, segmentation and classification", "Module 3",
  "Build an augmentation pipeline, train a small CNN classifier with it, and train a U-Net segmenter on synthetic shapes; measure accuracy and IoU/Dice.",
  "Synthetic shapes (circles vs squares) generated in the notebook; use Oxford-IIIT Pets or a food segmentation dataset in Colab.",
  ["Generate images with masks and labels", "Apply torchvision v2 augmentations to image + mask together", "Train a CNN classifier with and without augmentation", "Train a tiny U-Net and compute IoU"],
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
from torchvision.transforms import v2
from torchvision import tv_tensors
torch.manual_seed(0); S = 32
def make(n):
    yy, xx = torch.meshgrid(torch.arange(S), torch.arange(S), indexing="ij"); X, M, Y = [], [], []
    for _ in range(n):
        cy, cx = torch.randint(10, 22, (2,)).tolist(); r = torch.randint(4, 8, (1,)).item(); sq = torch.rand(1).item() < 0.5
        m = ((yy - cy).abs() <= r) & ((xx - cx).abs() <= r) if sq else (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r
        X.append(m.float() * 0.7 + 0.3 * torch.rand(S, S)); M.append(m.float()); Y.append(int(sq))
    return torch.stack(X)[:, None], torch.stack(M)[:, None], torch.tensor(Y)
X, Mk, Y = make(400); Xt, Mt, Yt = make(200)
aug = v2.Compose([v2.RandomHorizontalFlip(), v2.RandomAffine(degrees=20, translate=(0.15, 0.15))])
img, mask = aug(tv_tensors.Image(X[0]), tv_tensors.Mask(Mk[0])); print("augmented image and mask stay aligned:", img.shape, mask.shape)
def cnn(): return nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(32, 2))
for use_aug in (False, True):
    m = cnn(); opt = torch.optim.Adam(m.parameters(), 3e-3)
    for ep in range(12):
        for i in range(0, 400, 50):
            xb = X[i:i + 50]; xb = torch.stack([aug(x) for x in xb]) if use_aug else xb
            opt.zero_grad(); F.cross_entropy(m(xb), Y[i:i + 50]).backward(); opt.step()
    with torch.no_grad(): print(f"classifier (augmentation={use_aug}): test accuracy {(m(Xt).argmax(1) == Yt).float().mean():.3f}")
seg = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.Conv2d(16, 16, 3, padding=2, dilation=2), nn.ReLU(), nn.Conv2d(16, 1, 1))
opt = torch.optim.Adam(seg.parameters(), 3e-3)
for ep in range(15):
    for i in range(0, 400, 50): opt.zero_grad(); F.binary_cross_entropy_with_logits(seg(X[i:i + 50]), Mk[i:i + 50]).backward(); opt.step()
with torch.no_grad(): P = (seg(Xt) > 0).float()
print(f"segmentation IoU {(P * Mt).sum() / ((P + Mt) > 0).float().sum():.3f}  Dice {2 * (P * Mt).sum() / (P.sum() + Mt.sum()):.3f}")
""",
  observe=["Augmentations must transform image and mask identically", "Segmentation is evaluated with IoU/Dice, not accuracy"],
  extend=["Replace the segmenter with the U-Net from the Segmentation card", "Food image segmentation capstone: FoodSeg103 dataset"], see=["m-augmentation", "m-segmentation", "m-cnn"]),

L("m-lab-detection", "Lab 34 · Object detection with a pretrained detector", "Module 3",
  "Run a pretrained detector on images, apply score thresholds and NMS, compute IoU against ground truth, then fine-tune on a custom dataset.",
  "In Colab: COCO-pretrained Faster R-CNN / SSDLite from torchvision or Ultralytics YOLO; a small custom dataset in YOLO/COCO format (e.g. Roboflow).",
  ["Load a pretrained detector with weights='DEFAULT'", "Run inference and draw boxes above 0.5 confidence", "Compute IoU and precision/recall vs labelled boxes", "Fine-tune: replace the box predictor with your number of classes and train"],
  reuse="m-object-detection", net=False, observe=["Lower thresholds raise recall but add false positives", "NMS removes duplicate boxes"],
  extend=["`pip install ultralytics`; `YOLO('yolo11n.pt').train(data='data.yaml', epochs=50)`", "Compute mAP@0.5 with torchmetrics"], see=["m-object-detection"]),

L("m-lab-video", "Lab 35 · Video processing: motion detection, optical flow and tracking", "Module 3",
  "Read video frames, detect motion with background subtraction, measure movement with optical flow, and track objects across frames.",
  "Synthetic moving-object video generated in the notebook; use any MP4 or webcam (cv2.VideoCapture(0)) locally.",
  ["Read frames with cv2.VideoCapture and sample them", "Detect moving regions with MOG2 and contours", "Compute Farnebäck optical flow", "Track blobs with a simple centroid tracker"],
  code="""
import numpy as np, cv2
H, W, T = 120, 160, 40; writer = cv2.VideoWriter("demo.avi", cv2.VideoWriter_fourcc(*"MJPG"), 10, (W, H))
for t in range(T):                                                      # two objects moving in opposite directions
    f = np.full((H, W, 3), 40, np.uint8); cv2.circle(f, (10 + 3 * t, 40), 8, (0, 255, 0), -1); cv2.rectangle(f, (150 - 3 * t, 80), (162 - 3 * t, 92), (0, 0, 255), -1); writer.write(f)
writer.release()
cap = cv2.VideoCapture("demo.avi"); bg = cv2.createBackgroundSubtractorMOG2(history=10, detectShadows=False); prev = None
tracks, next_id = {}, 0
while True:
    ok, frame = cap.read()
    if not ok: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY); fg = bg.apply(frame)
    cnts, _ = cv2.findContours(cv2.threshold(fg, 127, 255, cv2.THRESH_BINARY)[1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cents = [tuple(np.mean(c.reshape(-1, 2), 0).astype(int)) for c in cnts if cv2.contourArea(c) > 20]
    for c in cents:                                                     # centroid tracker: match to nearest existing track
        best = min(tracks, key=lambda k: np.hypot(*np.subtract(tracks[k][-1], c)), default=None)
        if best is not None and np.hypot(*np.subtract(tracks[best][-1], c)) < 15: tracks[best].append(c)
        else: tracks[next_id] = [c]; next_id += 1
    if prev is not None: flow = cv2.calcOpticalFlowFarneback(prev, gray, None, 0.5, 3, 9, 3, 5, 1.2, 0)
    prev = gray
cap.release()
for k, pts in tracks.items():
    if len(pts) > 10: print(f"track {k}: {len(pts)} frames, moved dx={pts[-1][0] - pts[0][0]:+d}px -> {'right' if pts[-1][0] > pts[0][0] else 'left'}")
print("last-frame mean flow magnitude:", round(float(np.linalg.norm(flow, axis=2).mean()), 3))
""",
  observe=["Background subtraction finds moving objects", "A simple tracker keeps IDs; occlusions need Kalman filters (SORT)"],
  extend=["Run YOLO + ByteTrack on a traffic video and count vehicles crossing a line", "Classify actions with a 3-D CNN"], see=["m-video"]),

L("m-lab-transformers-ft", "Lab 36 · Transformers: fine-tuning BERT and GPT", "Module 3",
  "Fine-tune a BERT-family encoder for classification and a GPT-2 decoder for instruction-style generation with Hugging Face.",
  "In Colab (GPU): IMDB or SST-2 for BERT; a small instruction dataset (e.g. a few hundred Q&A pairs) for GPT-2. Offline: the tiny-model versions on the concept cards.",
  ["Tokenise with the model's tokenizer and DataCollatorWithPadding", "Train with Trainer: lr 2e-5, 2–3 epochs, eval each epoch", "Report accuracy/F1 on the test split", "Fine-tune GPT-2 with loss on answer tokens only; generate with greedy and top-p"],
  reuse="m-finetune-bert", observe=["DistilBERT reaches ~90%+ on SST-2 in minutes on a T4", "Masking prompt tokens from the loss focuses learning on answers"],
  extend=["Use LoRA (PEFT) to fine-tune a 1B model", "Push your model to the Hugging Face Hub"], see=["m-finetune-bert", "m-finetune-gpt", "m-peft-lora"]),

L("m-lab-hf", "Lab 37 · Hugging Face Transformers tour", "Module 3",
  "Use pipelines for sentiment, NER, QA, summarisation, translation, zero-shot classification, speech recognition and image classification; then do the same steps manually.",
  "Models download from the Hugging Face Hub (needs internet — run in Colab).",
  ["Run 6+ pipelines on your own examples", "Inspect tokenizer output (ids, attention mask, special tokens)", "Load AutoModel and get logits manually", "Batch inference on GPU and time it"],
  reuse="m-huggingface", net=True, observe=["pipeline = tokenizer + model + post-processing", "Pick task-specific checkpoints from the Hub"],
  extend=["Use datasets.load_dataset('imdb') and evaluate a pipeline", "Try a multilingual model on Hindi text"], see=["m-huggingface", "m-tokenization"]),

L("m-lab-llm", "Lab 38 · Working with LLMs: OpenAI / Claude APIs and local Llama", "Module 3",
  "Call LLM APIs with system prompts, few-shot examples, structured JSON output, streaming and tool calling; compare with a local open model via Ollama.",
  "API keys from OpenAI/Anthropic (stored as Colab secrets / environment variables); Ollama with llama3.2 locally.",
  ["Send a chat request with a system prompt", "Build a few-shot classifier prompt and parse JSON output", "Measure tokens, latency and cost for 20 requests", "Run the same prompts on a local Llama and compare quality"],
  reuse="m-llm-api", net=True, observe=["Temperature 0 gives near-deterministic outputs", "Structured output + validation makes LLMs usable in code"],
  extend=["Add tool calling (a calculator or weather function)", "Build a small evaluation set and score prompts"], see=["m-llm-api", "m-prompt-engineering", "m-agents"]),

L("m-lab-rag", "Lab 39 · LangChain and RAG: chat with your documents", "Module 3",
  "Build a retrieval-augmented QA system over a document set: chunk, embed, index, retrieve, generate with citations, and evaluate retrieval.",
  "Your PDFs/notes (e.g. this course's notes) — in Colab use sentence-transformers + FAISS/Chroma and an LLM API. Offline here: TF-IDF retrieval and a template answer.",
  ["Load and chunk documents with overlap", "Embed chunks and build a vector index", "Retrieve top-k for questions; re-rank", "Prompt the LLM to answer only from context with citations", "Evaluate recall@k on 10 hand-written questions"],
  code="""
import numpy as np, re
from sklearn.feature_extraction.text import TfidfVectorizer
corpus = {"leave.md": "Employees get 24 paid leave days per year. Up to 10 unused days carry over. Sick leave is 12 days and needs a doctor's note after 2 days.",
          "wfh.md": "Work from home is allowed two days a week with manager approval. Fully remote roles need HR approval and a signed agreement.",
          "expense.md": "Submit travel expenses within 30 days with receipts. Meals are reimbursed up to 1500 rupees per day. Flights must be economy class.",
          "it.md": "Laptops are replaced every 3 years. Report lost laptops to IT within 24 hours. Passwords must be changed every 90 days."}
chunks = [(src, s) for src, txt in corpus.items() for s in re.split(r"(?<=\\.)\\s+", txt)]
vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True).fit([c for _, c in chunks]); E = vec.transform([c for _, c in chunks])
def retrieve(q, k=2):
    s = (E @ vec.transform([q]).T).toarray().ravel(); return [(chunks[i][0], chunks[i][1], round(float(s[i]), 3)) for i in np.argsort(s)[::-1][:k]]
def answer(q):
    hits = retrieve(q); ctx = "\\n".join(f"[{src}] {txt}" for src, txt, _ in hits)
    prompt = f"Answer from the context only, cite [source]. Say 'I don't know' if missing.\\n{ctx}\\nQ: {q}"   # -> send to an LLM
    return hits[0][1] + f" [{hits[0][0]}]" if hits[0][2] > 0 else "I don't know", prompt
evalset = [("how many leave days carry over", "leave.md"), ("can I work from home", "wfh.md"), ("meal reimbursement limit", "expense.md"),
           ("what if I lose my laptop", "it.md"), ("how often change password", "it.md"), ("is business class allowed for flights", "expense.md")]
hits1 = [retrieve(q, 1)[0][0] == gold for q, gold in evalset]; hits2 = [gold in [h[0] for h in retrieve(q, 2)] for q, gold in evalset]
print(f"retrieval recall@1 {np.mean(hits1):.2f}  recall@2 {np.mean(hits2):.2f}")
for q in ["what if I lose my laptop", "what is the gym policy"]: print("Q:", q, "->", answer(q)[0])
""",
  observe=["Retrieval quality bounds answer quality — measure it", "The 'I don't know' path matters as much as correct answers"],
  extend=["Switch to sentence-transformers + FAISS and compare recall", "Wrap in a LangChain LCEL chain and a Gradio UI", "Add a cross-encoder re-ranker"], see=["m-rag", "m-langchain", "m-embeddings-vectordb", "m-advanced-rag"]),

L("m-lab-recsys", "Lab 40 · Movie recommendation system", "Module 3",
  "Build popularity, item-based collaborative filtering and matrix-factorisation recommenders and evaluate with precision@k on held-out ratings.",
  "Synthetic MovieLens-style ratings (use MovieLens 100k/1M in Colab — the movie recommendation capstone).",
  ["Create a user–item rating matrix", "Hold out each user's latest ratings", "Implement popularity, item-kNN and SVD/ALS-style factorisation", "Compare precision@10 and recall@10"],
  code="""
import numpy as np
rng = np.random.default_rng(0); U, I, k = 300, 120, 4
P, Q = rng.normal(size=(U, k)), rng.normal(size=(I, k)); pop = rng.normal(0, 0.5, I)        # hidden tastes + item popularity
scores = P @ Q.T + pop; R = np.zeros((U, I))
for u in range(U):
    pr = np.exp(scores[u] / 1.5); seen = rng.choice(I, 30, replace=False, p=pr / pr.sum()); R[u, seen] = np.clip(np.round(3 + scores[u, seen] / 2), 1, 5)
test = np.zeros_like(R)
for u in range(U):
    rated = np.nonzero(R[u])[0]; hold = rng.choice(rated, 6, replace=False); test[u, hold] = R[u, hold]; R[u, hold] = 0
relevant = test >= 4
def prec_at_k(S, k=10):
    S = S.copy(); S[R > 0] = -np.inf; top = np.argsort(-S, 1)[:, :k]; hits = np.take_along_axis(relevant, top, 1).sum(1)
    return hits.mean() / k, (hits / np.maximum(relevant.sum(1), 1)).mean()
popularity = np.tile((R >= 4).sum(0), (U, 1)).astype(float)
norm = np.linalg.norm(R, axis=0) + 1e-9; sim = (R.T @ R) / np.outer(norm, norm); np.fill_diagonal(sim, 0); item_knn = R @ sim
mask = R > 0; mu = R[mask].mean(); Pu, Qi = 0.1 * rng.normal(size=(U, 8)), 0.1 * rng.normal(size=(I, 8))
for _ in range(300):
    E = mask * (R - mu - Pu @ Qi.T); Pu += 0.01 * (E @ Qi - 0.05 * Pu); Qi += 0.01 * (E.T @ Pu - 0.05 * Qi)
mf = mu + Pu @ Qi.T
for name, S in [("popularity", popularity), ("item-kNN CF", item_knn), ("matrix factorisation", mf)]:
    p, r = prec_at_k(S); print(f"{name:21s} precision@10 {p:.3f}  recall@10 {r:.3f}")
""",
  observe=["Popularity is the baseline to beat", "Collaborative filtering and matrix factorisation win when tastes vary between users"],
  extend=["Use the surprise or implicit libraries on MovieLens", "Add content features (genres) for cold-start movies"], see=["m-recsys"]),

L("m-lab-anomaly", "Lab 41 · Anomaly detection on bearing vibration data", "Module 3",
  "Detect failing bearings from vibration windows using signal features with Isolation Forest and an autoencoder trained on healthy data.",
  "Synthetic vibration signals with growing fault impulses (mirrors the bearing-vibration capstone; try NASA IMS or CWRU bearing datasets).",
  ["Simulate healthy and degrading vibration windows", "Extract RMS, kurtosis, crest factor and FFT band energies", "Fit Isolation Forest on healthy windows", "Fit an autoencoder; threshold reconstruction error; compare ROC-AUC"],
  code="""
import numpy as np, torch, torch.nn as nn
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
rng = np.random.default_rng(0); fs, n = 5000, 1024
def window(severity):
    t = np.arange(n) / fs; x = np.sin(2 * np.pi * 30 * t) + 0.3 * np.sin(2 * np.pi * 90 * t) + 0.3 * rng.normal(size=n)
    if severity > 0: x[np.arange(0, n, int(fs / 160))] += severity * rng.normal(3, 0.5, len(np.arange(0, n, int(fs / 160))))   # fault impacts at 160 Hz
    return x
def feats(x):
    spec = np.abs(np.fft.rfft(x)); f = np.fft.rfftfreq(n, 1 / fs); rms = np.sqrt((x ** 2).mean())
    return [rms, stats.kurtosis(x), np.abs(x).max() / rms, spec[(f > 100) & (f < 400)].sum(), spec[f > 1000].sum()]
healthy = np.array([feats(window(0)) for _ in range(400)])
test_sev = np.r_[np.zeros(200), rng.uniform(0.2, 1.5, 100)]; test = np.array([feats(window(s)) for s in test_sev]); y = (test_sev > 0).astype(int)
sc = StandardScaler().fit(healthy)
iso = IsolationForest(random_state=0).fit(sc.transform(healthy)); print("Isolation Forest ROC-AUC:", round(roc_auc_score(y, -iso.score_samples(sc.transform(test))), 3))
Xh = torch.tensor(sc.transform(healthy), dtype=torch.float32); Xt = torch.tensor(sc.transform(test), dtype=torch.float32)
ae = nn.Sequential(nn.Linear(5, 8), nn.ReLU(), nn.Linear(8, 2), nn.ReLU(), nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 5)); opt = torch.optim.Adam(ae.parameters(), 1e-2)
for _ in range(500): opt.zero_grad(); loss = ((ae(Xh) - Xh) ** 2).mean(); loss.backward(); opt.step()
with torch.no_grad(): err_h = ((ae(Xh) - Xh) ** 2).mean(1).numpy(); err_t = ((ae(Xt) - Xt) ** 2).mean(1).numpy()
thr = np.percentile(err_h, 99); print("autoencoder ROC-AUC:", round(roc_auc_score(y, err_t), 3), f"| alarms at 99th-pct threshold: recall {(err_t[y == 1] > thr).mean():.2f}, false alarm rate {(err_t[y == 0] > thr).mean():.2f}")
""",
  observe=["Kurtosis and crest factor jump with impulsive faults", "Training only on healthy data avoids needing fault labels"],
  extend=["Track the anomaly score over time to estimate remaining useful life", "Try a 1-D CNN autoencoder on raw windows"], see=["m-anomaly", "m-autoencoder", "m-feature-extraction"]),
]
