"""Deep layer + end-to-end walkthroughs: Supervised learning."""
from deep.util import X

TITANIC = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
PENGUINS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
HOUSING = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
TELCO = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
SONAR = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/sonar.csv"
PIMA = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
PIMA_COLS = ["pregnancies", "glucose", "bp", "skin", "insulin", "bmi", "pedigree", "age", "diabetes"]
GERMAN = "https://raw.githubusercontent.com/selva86/datasets/master/GermanCredit.csv"
FMNIST = '''import gzip, urllib.request
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
get = lambda f, off: np.frombuffer(gzip.decompress(urllib.request.urlopen(base + f).read()), np.uint8, offset=off)
X = get("t10k-images-idx3-ubyte.gz", 16).reshape(-1, 784) / 255.0; y = get("t10k-labels-idx1-ubyte.gz", 8)
NAMES = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Boot"]'''
LOAD_TELCO = f'''df = pd.read_csv("{TELCO}")
df["TotalCharges"] = pd.to_numeric(df.TotalCharges, errors="coerce").fillna(0); y = (df.pop("Churn") == "Yes").astype(int); df = df.drop(columns="customerID")'''

X("m-linear-regression",
  "Linear regression predicts a number as a weighted sum of features plus an intercept. Each weight says how much the prediction changes when that feature rises by one unit, holding the others fixed. It's fast, interpretable and the baseline every regression project should start with.",
  """**Model and fit.** ŷ = b + Σwⱼxⱼ. Minimise MSE → normal equations w = (XᵀX)⁻¹Xᵀy (or gradient descent). **Assumptions for valid inference:** linearity, independent errors, constant variance (homoscedasticity), roughly Normal errors, no perfect multicollinearity. Coefficient standard errors: SE(w) = √(σ̂²·diag((XᵀX)⁻¹)), t = w/SE. **R²** = explained variance; **adjusted R²** penalises extra features. Log-transforming the target turns coefficients into approximate % effects: w = 0.05 ⇒ +5% per unit. Non-linearity enters through engineered features (polynomials, splines, interactions) — the model is linear in the *weights*.""",
  """**By hand.** House value (₹ lakh) vs income (₹ lakh): points (2, 30), (4, 50), (6, 60). x̄ = 4, ȳ = 46.7. Slope = Σ(x−x̄)(y−ȳ)/Σ(x−x̄)² = ((−2)(−16.7) + 0 + 2·13.3)/8 = (33.3 + 26.7)/8 = **7.5**; intercept = 46.7 − 7.5·4 = **16.7**. Predict income 5 → 16.7 + 37.5 = **54.2**.""",
  ["Interpreting coefficients of unscaled or collinear features", "Extrapolating far outside the training range", "Ignoring heteroscedastic, curved residuals", "Reading a coefficient as causal"],
  ["Baselines, interpretable effects, forecasting with engineered features"], ["Strongly non-linear interactions without feature engineering — use trees/boosting"],
  "California housing — fit linear regression with statsmodels (coefficients, SEs, p-values) and scikit-learn, check assumptions with residual diagnostics, log-transform the target, add splines, and interpret the coefficients.",
  ["Load data; log target; split", "Fit OLS with statsmodels for inference", "Check residuals (linearity, heteroscedasticity)", "Improve with spline features on income/location", "Interpret effects in plain language and evaluate on the test set"],
  f'''
import numpy as np, pandas as pd, statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import SplineTransformer, StandardScaler
df = pd.read_csv("{HOUSING}").dropna(); df = df[df.median_house_value < 500001]
df["rooms_per_hh"] = df.total_rooms / df.households; df["coastal"] = (df.ocean_proximity != "INLAND").astype(int)
feats = ["median_income", "housing_median_age", "rooms_per_hh", "coastal", "latitude", "longitude"]
tr, te = train_test_split(df, test_size=0.25, random_state=0); ytr, yte = np.log(tr.median_house_value), np.log(te.median_house_value)
ols = sm.OLS(ytr, sm.add_constant(tr[feats])).fit()
print(ols.summary2().tables[1][["Coef.", "Std.Err.", "P>|t|"]].round(4))
print(f"income +1 (=$10k) -> value ×{{np.exp(ols.params.median_income):.3f}} | coastal -> ×{{np.exp(ols.params.coastal):.2f}} (holding others fixed)")
res = ols.resid; fitted = ols.fittedvalues
print("residual mean by fitted-value decile (should be ~0):", res.groupby(pd.qcut(fitted, 10, labels=False)).mean().round(3).tolist())
print("Breusch-Pagan p (heteroscedasticity):", f"{{sm.stats.het_breuschpagan(res, sm.add_constant(tr[feats]))[1]:.1e}}")
lin = LinearRegression().fit(tr[feats], ytr)
spl = make_pipeline(make_column_transformer((SplineTransformer(n_knots=8), ["median_income", "latitude", "longitude"]), remainder=StandardScaler()), LinearRegression()).fit(tr[feats], ytr)
for name, m in [("linear", lin), ("linear + splines", spl)]:
    p = m.predict(te[feats]); print(f"  {{name:17s}} test R² {{1 - ((yte - p) ** 2).sum() / ((yte - yte.mean()) ** 2).sum():.3f}} | median abs % error {{np.median(np.abs(np.exp(p) / np.exp(yte) - 1)):.1%}}")
''')

X("m-logistic-regression",
  "Logistic regression predicts a probability for a yes/no outcome by passing a linear score through the sigmoid. It's the workhorse classifier: fast, well-calibrated, interpretable through **odds ratios**, and the building block of neural networks' output layers.",
  """**Model.** z = b + w·x, p = σ(z) = 1/(1 + e^(−z)); equivalently log-odds log(p/(1−p)) = z, so a one-unit increase in xⱼ multiplies the odds by e^(wⱼ). **Loss** = negative log-likelihood (binary cross-entropy) L = −Σ[y log p + (1−y) log(1−p)]; gradient Xᵀ(p − y) — same form as linear regression. Convex, solved by L-BFGS/Newton (IRLS). Regularisation via C = 1/λ. Decision boundary w·x + b = 0 is linear; threshold choice is separate from the model. On perfectly separable data weights diverge without regularisation.""",
  """**Odds by hand.** Model: log-odds = −8 + 0.04·glucose + 0.08·BMI. Patient glucose 150, BMI 32: z = −8 + 6 + 2.56 = 0.56 → p = 1/(1 + e^(−0.56)) = **0.636**. Glucose +10 multiplies odds by e^(0.4) = **1.49** (49% higher odds), whatever the starting point.""",
  ["Confusing odds ratios with probability ratios", "Comparing coefficients of unscaled features", "Assuming a linear boundary when interactions matter", "Using 0.5 threshold blindly"],
  ["Binary outcomes, baselines, risk scores, when calibrated probabilities and explanations matter"], ["Highly non-linear boundaries without feature engineering"],
  "Pima diabetes — logistic regression from scratch (gradient descent) vs scikit-learn vs statsmodels, odds ratios with confidence intervals, a risk calculator for a new patient, and the decision boundary in two features.",
  ["Standardise features and split", "Implement gradient descent on cross-entropy", "Compare with sklearn and statsmodels; odds ratios with CIs", "Evaluate AUC and calibration", "Score a new patient and explain the score"],
  f'''
import numpy as np, pandas as pd, statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
df = pd.read_csv("{PIMA}", names={PIMA_COLS}); feats = ["glucose", "bmi", "age", "pregnancies", "pedigree"]
df = df[(df.glucose > 0) & (df.bmi > 0)]
tr, te = train_test_split(df, test_size=0.3, stratify=df.diabetes, random_state=0); mu, sd = tr[feats].mean(), tr[feats].std()
A, B = ((tr[feats] - mu) / sd).to_numpy(), ((te[feats] - mu) / sd).to_numpy(); ytr, yte = tr.diabetes.to_numpy(), te.diabetes.to_numpy()
w, b = np.zeros(len(feats)), 0.0; sig = lambda z: 1 / (1 + np.exp(-z))
for _ in range(3000):
    p = sig(A @ w + b); w -= 0.1 * A.T @ (p - ytr) / len(ytr); b -= 0.1 * (p - ytr).mean()
sk = LogisticRegression(C=1e6).fit(A, ytr)
print("from scratch:", np.r_[b, w].round(3)); print("sklearn     :", np.r_[sk.intercept_, sk.coef_[0]].round(3))
sm_fit = sm.Logit(ytr, sm.add_constant(A)).fit(disp=0); ci = np.exp(sm_fit.conf_int()[1:])
for f, c, (lo, hi) in zip(feats, sm_fit.params[1:], ci): print(f"  {{f:12s}} odds ×{{np.exp(c):.2f}} per +1 SD ({{sd[f]:.1f}} units), 95% CI [{{lo:.2f}}, {{hi:.2f}}]")
p = sig(B @ w + b); print(f"test AUC {{roc_auc_score(yte, p):.3f}} | Brier {{brier_score_loss(yte, p):.3f}}")
patient = pd.Series({{"glucose": 150, "bmi": 32, "age": 45, "pregnancies": 2, "pedigree": 0.5}}); z = ((patient - mu) / sd).to_numpy()
contrib = dict(zip(feats, (w * z).round(2).tolist())); print(f"new patient risk {{sig(z @ w + b):.1%}} | log-odds contributions {{contrib}} (+ intercept {{b:.2f}})")
''')

X("m-multiclass",
  "With more than two classes you either use a natively multiclass model (softmax regression, trees, kNN, neural nets) or combine binary ones (**one-vs-rest**, **one-vs-one**). Evaluation also changes: per-class metrics, macro vs weighted averages, and the confusion matrix shows which classes are confused.",
  """**Softmax regression.** Scores zₖ = wₖ·x + bₖ; pₖ = e^(zₖ)/Σⱼe^(zⱼ); loss = −log p_true. Gradient for class k: (pₖ − 1[y = k])·x. Subtracting max(z) before exponentiating avoids overflow (softmax is shift-invariant). **OvR:** K binary models, pick the highest score (scores may be on different scales). **OvO:** K(K−1)/2 models, majority vote (used by SVC). Multi-label (several labels at once) is different: K independent sigmoids. **Metrics:** macro-F1 treats each class equally (good for rare classes); weighted-F1 by support; top-k accuracy for many classes.""",
  """**Softmax by hand.** Scores [2, 1, 0] → e² = 7.39, e¹ = 2.72, e⁰ = 1 → sum 11.11 → p = **[0.665, 0.245, 0.090]**. If the true class is the 2nd, loss = −ln 0.245 = **1.41**; gradient on the scores = p − onehot = [0.665, −0.755, 0.090].""",
  ["Using binary metrics without specifying averaging", "Softmax for multi-label problems", "Ignoring which classes get confused", "Numerical overflow in a hand-written softmax"],
  ["Any K-class problem; check the confusion matrix"], ["Hundreds of thousands of classes — use hierarchical/sampled softmax or retrieval"],
  "Fashion-MNIST (10,000 real clothing images, 10 classes) — softmax regression from scratch in NumPy, sklearn multinomial vs one-vs-rest vs one-vs-one, a confusion matrix showing which garments are confused, and macro vs weighted metrics.",
  ["Load images and split", "Softmax regression from scratch with mini-batch gradient descent", "Compare multinomial, OvR and OvO models", "Confusion matrix: most confused pairs", "Per-class F1, macro vs weighted, top-2 accuracy"],
  '''
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
''' + FMNIST + '''
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
W, b, rng = np.zeros((784, 10)), np.zeros(10), np.random.default_rng(0)
def softmax(Z): Z = Z - Z.max(1, keepdims=True); E = np.exp(Z); return E / E.sum(1, keepdims=True)
for epoch in range(15):
    for idx in np.array_split(rng.permutation(len(Xtr)), len(Xtr) // 128):
        P = softmax(Xtr[idx] @ W + b); P[np.arange(len(idx)), ytr[idx]] -= 1        # gradient of CE wrt scores = p - onehot
        W -= 0.5 * Xtr[idx].T @ P / len(idx) + 1e-4 * W; b -= 0.5 * P.mean(0)
print("softmax from scratch accuracy:", round((softmax(Xte @ W + b).argmax(1) == yte).mean(), 3))
models = {"multinomial": LogisticRegression(max_iter=300, C=0.5), "one-vs-rest": OneVsRestClassifier(LogisticRegression(max_iter=300, C=0.5)), "one-vs-one": OneVsOneClassifier(LogisticRegression(max_iter=300, C=0.5))}
for name, m in models.items(): print(f"  {name:12s} accuracy {m.fit(Xtr, ytr).score(Xte, yte):.3f}")
m = models["multinomial"]; pred = m.predict(Xte); cm = confusion_matrix(yte, pred); off = cm - np.diag(np.diag(cm))
pairs = sorted(((off[i, j], NAMES[i], NAMES[j]) for i in range(10) for j in range(10) if i != j), reverse=True)[:4]
print("most confused (true -> predicted):", [(a, b, int(n)) for n, a, b in pairs])
print("per-class F1:", dict(zip(NAMES, f1_score(yte, pred, average=None).round(2).tolist())))
print(f"macro F1 {f1_score(yte, pred, average='macro'):.3f} | weighted F1 {f1_score(yte, pred, average='weighted'):.3f} | top-2 accuracy {top_k_accuracy_score(yte, m.predict_proba(Xte), k=2):.3f}")
''')

X("m-knn",
  "k-nearest neighbours predicts by looking up the k most similar training examples and voting (classification) or averaging (regression). There's no training step — the data *is* the model — which makes it simple, flexible and a great baseline, but slow and sensitive to scaling and dimensionality.",
  """**Mechanics.** Distance d(x, xᵢ) (Euclidean, Manhattan, cosine); take the k nearest; predict majority or mean, optionally weighted by 1/d. **k controls bias–variance:** k = 1 → zero training error, jagged boundary (high variance); large k → smooth (high bias). 1-NN's asymptotic error is at most twice the Bayes error. **Cost:** prediction O(n·d) per query naïvely; KD-trees/ball-trees help in low dimensions; approximate nearest neighbour (HNSW, FAISS) at scale — the same idea powers vector databases. Needs scaling; suffers from the curse of dimensionality.""",
  """**By hand.** Training points (height cm, weight kg → size): (160, 55, S), (165, 60, S), (175, 75, L), (180, 80, L), (170, 68, M). Query (172, 70): distances ≈ M: 2.8, L(175,75): 5.8, S(165,60): 12.2, L(180,80): 12.8. k = 1 → **M**; k = 3 → M, L, S → tie broken by nearest → M; distance-weighted k = 3: M 1/2.8 = 0.36 vs L 0.17 vs S 0.08 → **M**.""",
  ["No feature scaling", "Choosing k on the test set", "Using kNN with hundreds of raw features", "Expecting fast predictions on millions of rows without an index"],
  ["Small/medium data, baselines, recommendation & similarity search with embeddings"], ["High-dimensional raw data, latency-critical prediction without ANN indexes"],
  "Fashion-MNIST — kNN from scratch with vectorised distances, choose k by cross-validation, compare distance weighting and metrics, speed up with PCA and a ball tree, and show nearest-neighbour 'explanations'.",
  ["Load images and split", "Vectorised kNN from scratch", "Tune k and weighting with CV", "PCA to 50 dims and tree indexes for speed", "Explain a prediction by its neighbours"],
  '''
import time, numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsClassifier
''' + FMNIST + '''
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=2000, stratify=y, random_state=0)
def knn_predict(A, ya, B, k):
    d = (B ** 2).sum(1)[:, None] - 2 * B @ A.T + (A ** 2).sum(1)[None]          # squared distances, fully vectorised
    nn = np.argpartition(d, k, axis=1)[:, :k]; return np.array([np.bincount(ya[r], minlength=10).argmax() for r in nn])
t = time.perf_counter(); acc = (knn_predict(Xtr, ytr, Xte[:500], 5) == yte[:500]).mean(); print(f"from-scratch 5-NN accuracy {acc:.3f} ({time.perf_counter() - t:.1f}s for 500 queries)")
gs = GridSearchCV(KNeighborsClassifier(), {"n_neighbors": [1, 3, 5, 9, 15], "weights": ["uniform", "distance"]}, cv=3).fit(Xtr[:4000], ytr[:4000])
print("CV best:", gs.best_params_, round(gs.best_score_, 3))
pca = PCA(50, random_state=0).fit(Xtr); Ptr, Pte = pca.transform(Xtr), pca.transform(Xte)
for name, A, B, algo in [("784 dims brute", Xtr, Xte, "brute"), ("50 PCA dims brute", Ptr, Pte, "brute"), ("50 PCA dims ball-tree", Ptr, Pte, "ball_tree")]:
    m = KNeighborsClassifier(**gs.best_params_, algorithm=algo).fit(A, ytr); t = time.perf_counter(); s = m.score(B, yte)
    print(f"  {name:22s} accuracy {s:.3f} | predict {time.perf_counter() - t:.2f}s")
m = KNeighborsClassifier(5).fit(Ptr, ytr); i = int(np.flatnonzero(m.predict(Pte) != yte)[0]); dist, nb = m.kneighbors(Pte[i:i + 1])
print(f"explaining a mistake: true {NAMES[yte[i]]}, predicted {NAMES[m.predict(Pte[i:i + 1])[0]]}; neighbours were", [NAMES[ytr[j]] for j in nb[0]])
''')

X("m-decision-tree",
  "A decision tree asks a sequence of yes/no questions about features ('tenure < 12?', 'contract = month-to-month?') and predicts at the leaf. It handles mixed data, non-linearities and interactions with no scaling, and is readable — but a single deep tree overfits, which is why forests and boosting exist.",
  """**Growing (CART).** At each node try every feature and threshold; pick the split maximising impurity decrease: Gini G = 1 − Σpₖ², entropy H = −Σpₖ log pₖ (classification), variance/MSE (regression). Stop at max_depth, min_samples_leaf, or no gain. Leaf prediction = majority class / mean. **Pruning:** cost-complexity R_α(T) = R(T) + α·|leaves|; larger α → smaller tree, α chosen by CV. Trees are greedy (locally optimal splits), unstable (small data changes → different tree), axis-aligned (diagonal boundaries need many splits).""",
  """**Gini by hand.** Node: 10 churn, 30 stay → G = 1 − (0.25² + 0.75²) = **0.375**. Split on contract: left (month-to-month) 9 churn/11 stay → G = 1 − (0.45² + 0.55²) = 0.495; right 1/19 → G = 1 − (0.05² + 0.95²) = 0.095. Weighted = (20·0.495 + 20·0.095)/40 = 0.295 → gain **0.08**.""",
  ["Unlimited depth (memorises noise)", "Reading impurity importances as causal or unbiased", "Expecting stable trees across samples", "One-hot encoding hundreds of levels (sparse useless splits)"],
  ["Explainable rules, mixed-type tabular data, building block for ensembles"], ["As a final model when accuracy matters — use forests/boosting"],
  "IBM Telco churn — implement a small CART (Gini) from scratch, compare with scikit-learn, print the tree's rules, prune with cost-complexity and cross-validation, and show instability across bootstrap samples.",
  ["Prepare features (ordinal-encoded categoricals)", "Gini split search and recursive tree from scratch", "sklearn tree and text rules", "Cost-complexity pruning path + CV choice of α", "Instability: root splits across bootstrap samples"],
  f'''
import numpy as np, pandas as pd
from collections import Counter
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
{LOAD_TELCO}
X = df.apply(lambda s: pd.factorize(s)[0] if not pd.api.types.is_numeric_dtype(s) else s).to_numpy(float); names = list(df.columns)
Xtr, Xte, ytr, yte = train_test_split(X, y.to_numpy(), test_size=0.3, stratify=y, random_state=0)
gini = lambda t: 1 - ((np.bincount(t, minlength=2) / len(t)) ** 2).sum()
def best_split(A, t):
    best = (0, None, None); g0 = gini(t)
    for j in range(A.shape[1]):
        for thr in np.unique(np.quantile(A[:, j], np.linspace(0.05, 0.95, 19))):
            m = A[:, j] <= thr
            if 20 <= m.sum() <= len(t) - 20:
                gain = g0 - (m.mean() * gini(t[m]) + (1 - m.mean()) * gini(t[~m]))
                if gain > best[0]: best = (gain, j, thr)
    return best
def grow(A, t, depth):
    gain, j, thr = best_split(A, t)
    if depth == 0 or j is None: return Counter(t).most_common(1)[0][0]
    m = A[:, j] <= thr; return (j, thr, grow(A[m], t[m], depth - 1), grow(A[~m], t[~m], depth - 1))
def predict(node, x): return node if not isinstance(node, tuple) else predict(node[2] if x[node[0]] <= node[1] else node[3], x)
tree = grow(Xtr, ytr, 3); print(f"from-scratch depth-3 root split: {{names[tree[0]]}} <= {{tree[1]:.1f}} | test acc {{np.mean([predict(tree, x) == t for x, t in zip(Xte, yte)]):.3f}}")
sk = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr); print(f"sklearn depth-3 test acc {{sk.score(Xte, yte):.3f}}\\n" + export_text(sk, feature_names=names, max_depth=2))
path = DecisionTreeClassifier(random_state=0).cost_complexity_pruning_path(Xtr, ytr); alphas = path.ccp_alphas[::max(1, len(path.ccp_alphas) // 25)]
scores = [cross_val_score(DecisionTreeClassifier(ccp_alpha=a, random_state=0), Xtr, ytr, cv=5).mean() for a in alphas]
a = alphas[int(np.argmax(scores))]; pruned = DecisionTreeClassifier(ccp_alpha=a, random_state=0).fit(Xtr, ytr); full = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)
print(f"unpruned: {{full.get_n_leaves()}} leaves, test {{full.score(Xte, yte):.3f}} | pruned α={{a:.5f}}: {{pruned.get_n_leaves()}} leaves, test {{pruned.score(Xte, yte):.3f}}")
rng = np.random.default_rng(0); roots = Counter(names[DecisionTreeClassifier(max_depth=1).fit(Xtr[i], ytr[i]).tree_.feature[0]] for i in (rng.integers(0, len(Xtr), len(Xtr)) for _ in range(30)))
second = Counter(names[DecisionTreeClassifier(max_depth=2).fit(Xtr[i], ytr[i]).tree_.feature[1]] for i in (rng.integers(0, len(Xtr), len(Xtr)) for _ in range(30)))
print("root feature over 30 bootstraps:", dict(roots), "| second-level feature:", dict(second))
''')

X("m-bootstrap-bagging",
  "The **bootstrap** resamples your data with replacement to simulate 'another dataset from the same world'. **Bagging** (bootstrap aggregating) trains one model per bootstrap sample and averages them — cutting the variance of unstable models like deep trees without increasing bias.",
  """**Why averaging helps.** B models each with variance σ² and pairwise correlation ρ: Var(average) = ρσ² + (1 − ρ)σ²/B. More models shrink the second term; the first term (correlation) remains — hence random forests also decorrelate trees. A bootstrap sample contains ~63.2% unique rows (1 − (1 − 1/n)ⁿ → 1 − 1/e); the left-out ~36.8% are **out-of-bag (OOB)** rows that give a free validation estimate. Bagging helps high-variance/low-bias learners (deep trees, kNN with small k), not stable ones (linear regression).""",
  """**Variance by hand.** Trees with σ² = 1, ρ = 0.3, B = 100: Var = 0.3 + 0.7/100 = **0.307** (≈ 70% reduction). With ρ = 0.8 you only get to 0.802 — decorrelation matters more than adding trees. **Unique fraction:** n = 1000 → 1 − 0.999¹⁰⁰⁰ = **0.632**.""",
  ["Bagging stable models (no gain)", "Expecting bagging to fix bias", "Forgetting OOB is a free validation set"],
  ["Deep trees and other high-variance models; uncertainty estimates via bootstrap"], ["Time series without block bootstrap"],
  "California housing — bootstrap from scratch (unique fraction, OOB rows), bagged trees from scratch vs one tree vs sklearn BaggingRegressor, error vs number of models, OOB vs test error, and bagging a stable linear model for contrast.",
  ["Draw bootstrap samples and count unique/OOB rows", "Bag deep trees from scratch; track error as B grows", "Compare with sklearn BaggingRegressor and its OOB score", "Show bagging doesn't help linear regression", "Prediction intervals from the spread of bagged predictions"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import BaggingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
df = pd.read_csv("{HOUSING}").dropna(); y = df.median_house_value.to_numpy() / 1e5
X = df[["median_income", "housing_median_age", "total_rooms", "population", "households", "latitude", "longitude"]].to_numpy()
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0); rng = np.random.default_rng(0)
i = rng.integers(0, len(Xtr), len(Xtr)); print(f"bootstrap: unique rows {{len(np.unique(i)) / len(Xtr):.3f}} | out-of-bag {{1 - len(np.unique(i)) / len(Xtr):.3f}}")
rmse = lambda p: np.sqrt(np.mean((p - yte) ** 2)); preds = []
for b in range(1, 51):
    i = rng.integers(0, len(Xtr), len(Xtr)); preds.append(DecisionTreeRegressor(random_state=b).fit(Xtr[i], ytr[i]).predict(Xte))
    if b in (1, 5, 10, 25, 50): print(f"  bagged trees B={{b:2d}}: test RMSE {{rmse(np.mean(preds, 0)):.3f}}")
P = np.array(preds); print("average single-tree RMSE:", round(np.mean([rmse(p) for p in P]), 3), "| mean pairwise correlation of tree errors:", round(np.corrcoef(P - yte)[np.triu_indices(50, 1)].mean(), 2))
bag = BaggingRegressor(DecisionTreeRegressor(), n_estimators=50, oob_score=True, n_jobs=-1, random_state=0).fit(Xtr, ytr)
print(f"sklearn bagging: OOB R² {{bag.oob_score_:.3f}} vs test R² {{bag.score(Xte, yte):.3f}}")
lin, blin = LinearRegression().fit(Xtr, ytr), BaggingRegressor(LinearRegression(), n_estimators=50, random_state=0).fit(Xtr, ytr)
print(f"linear: single {{rmse(lin.predict(Xte)):.4f}} vs bagged {{rmse(blin.predict(Xte)):.4f}} (stable model -> no gain)")
lo, hi = np.percentile(P, [5, 95], axis=0); print(f"spread-based 90% band covers {{((yte >= lo) & (yte <= hi)).mean():.1%}} of test targets (too narrow: tree spread ≠ full predictive uncertainty)")
''')

X("m-random-forest",
  "A random forest is bagging of decision trees plus **random feature subsets at each split**, which decorrelates the trees so averaging removes more variance. It's one of the most reliable off-the-shelf models for tabular data: little tuning, robust to outliers and irrelevant features, with built-in OOB validation and importances.",
  """**Algorithm.** For b = 1..B: bootstrap sample; grow a deep tree where each split considers only m random features (default √p for classification, p/3 or all for regression in sklearn ≥ 1.1 — tune max_features). Predict by averaging probabilities. **Key hyperparameters:** n_estimators (more is never worse, just slower), max_features (lower → less correlation, more bias), min_samples_leaf/max_depth (smoothness), class_weight. **Importances:** impurity-based (biased to high-cardinality/continuous features) vs permutation (on validation data, preferred). Proximity: how often two rows land in the same leaf. ExtraTrees: random thresholds too → even less variance.""",
  """**Decorrelation by hand.** p = 16 features, one dominant. Plain bagging: almost every tree splits first on the dominant feature → ρ ≈ 0.8. With max_features = 4, the dominant feature is available at the root only 4/16 = **25%** of the time, so trees differ more → ρ drops (say 0.4) → ensemble variance ρσ² halves.""",
  ["Using impurity importances to drop features", "Too few trees for stable importances", "Expecting extrapolation beyond the training range", "Huge memory with deep trees on big data"],
  ["Strong tabular baseline, mixed features, OOB estimate, feature importance screening"], ["Extrapolation (trends), very high-dimensional sparse text, low-latency edge devices"],
  "IBM Telco churn — random forest with OOB error vs number of trees, tune max_features/min_samples_leaf, compare with a single tree and ExtraTrees, and contrast impurity vs permutation importances.",
  ["Encode features and split", "OOB error as trees are added (warm start)", "Tune max_features and min_samples_leaf by CV", "Compare tree vs forest vs ExtraTrees on test AUC", "Impurity vs permutation importance"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeClassifier
{LOAD_TELCO}
X = pd.get_dummies(df, drop_first=True, dtype=int); Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
rf = RandomForestClassifier(warm_start=True, oob_score=True, min_samples_leaf=5, n_jobs=-1, random_state=0)
for n in [25, 50, 100, 200, 400]: rf.set_params(n_estimators=n).fit(Xtr, ytr); print(f"  trees {{n:3d}}: OOB accuracy {{rf.oob_score_:.4f}}")
gs = GridSearchCV(RandomForestClassifier(200, n_jobs=-1, random_state=0), {{"max_features": [0.1, "sqrt", 0.5, 1.0], "min_samples_leaf": [1, 5, 20]}}, cv=3, scoring="roc_auc").fit(Xtr, ytr)
print("best:", gs.best_params_, round(gs.best_score_, 4))
for name, m in [("single tree", DecisionTreeClassifier(min_samples_leaf=20, random_state=0)), ("random forest", gs.best_estimator_),
                ("bagging (max_features=1.0)", RandomForestClassifier(200, max_features=1.0, min_samples_leaf=5, n_jobs=-1, random_state=0)),
                ("extra trees", ExtraTreesClassifier(400, min_samples_leaf=5, n_jobs=-1, random_state=0))]:
    print(f"  {{name:26s}} test AUC {{roc_auc_score(yte, m.fit(Xtr, ytr).predict_proba(Xte)[:, 1]):.4f}}")
best = gs.best_estimator_; imp = pd.Series(best.feature_importances_, X.columns).nlargest(6)
perm = pd.Series(permutation_importance(best, Xte, yte, scoring="roc_auc", n_repeats=10, random_state=0).importances_mean, X.columns).nlargest(6)
print("impurity top-6:", imp.round(3).to_dict()); print("permutation top-6 (AUC drop):", perm.round(4).to_dict())
''')

X("m-voting-stacking",
  "Ensembles combine different models so their errors cancel. **Voting** averages predictions (hard: majority labels; soft: average probabilities). **Stacking** trains a meta-model on the base models' out-of-fold predictions to learn how much to trust each one. **Blending** does the same with a single hold-out set.",
  """**When combining helps.** Average of K models with errors eᵢ: MSE = (1/K²)ΣΣ Cov(eᵢ, eⱼ) — gains come from **diverse, comparably good** models (low error correlation). Soft voting needs calibrated probabilities. **Stacking procedure:** for each base model, produce out-of-fold predictions on the training set via k-fold CV; train a simple meta-learner (logistic/ridge) on those columns; at prediction time feed base predictions of fully-refit base models. Using in-fold predictions leaks (the meta-model trusts overfit models). Typical gains are small (0.5–2%) — worth it in competitions, debatable in production (complexity, latency).""",
  """**Hard vote by hand.** Three models say [spam, ham, spam] → spam. Soft vote with P(spam) = [0.55, 0.10, 0.52] → mean 0.39 → **ham**: two lukewarm yeses lose to one confident no. **Correlation:** two models each 80% accurate with independent errors → when combined with a third, majority-vote accuracy = 0.8³ + 3·0.8²·0.2 = **0.896**; with perfectly correlated errors, still 0.80.""",
  ["Stacking on in-fold predictions (leakage)", "Ensembling near-identical models (no diversity)", "Soft voting with uncalibrated models (e.g. SVM scores)", "A complex meta-model that overfits"],
  ["Squeezing the last % of accuracy, combining heterogeneous models"], ["Latency/interpretability-constrained production systems"],
  "Pima diabetes — five diverse base models, their error correlations, hard vs soft voting, stacking with out-of-fold predictions (by hand and with StackingClassifier), and the leakage of in-fold stacking.",
  ["Train diverse base models", "Measure accuracy and error correlations", "Hard and soft voting", "Stacking with out-of-fold predictions from scratch and with sklearn", "Show in-fold stacking leaks"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_predict, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
df = pd.read_csv("{PIMA}", names={PIMA_COLS}); X, y = df.drop(columns="diabetes"), df.diabetes
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
base = [("logreg", make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))), ("knn", make_pipeline(StandardScaler(), KNeighborsClassifier(25))),
        ("rf", RandomForestClassifier(300, min_samples_leaf=3, random_state=0)), ("gbm", HistGradientBoostingClassifier(max_depth=3, random_state=0)), ("nb", GaussianNB())]
P = {{n: m.fit(Xtr, ytr).predict_proba(Xte)[:, 1] for n, m in base}}
for n, p in P.items(): print(f"  {{n:7s}} AUC {{roc_auc_score(yte, p):.4f}}")
E = pd.DataFrame({{n: (p > 0.5) != yte.to_numpy() for n, p in P.items()}}).astype(float); print("error correlation:\\n", E.corr().round(2))
for vote in ["hard", "soft"]:
    v = VotingClassifier(base, voting=vote).fit(Xtr, ytr); s = v.predict_proba(Xte)[:, 1] if vote == "soft" else v.predict(Xte)
    print(f"{{vote}} voting: accuracy {{(v.predict(Xte) == yte).mean():.3f}}" + (f" AUC {{roc_auc_score(yte, s):.4f}}" if vote == "soft" else ""))
oof = np.column_stack([cross_val_predict(m, Xtr, ytr, cv=5, method="predict_proba")[:, 1] for _, m in base])
meta = LogisticRegression().fit(oof, ytr); test_cols = np.column_stack([P[n] for n, _ in base])
print("stacking (out-of-fold, by hand) AUC:", round(roc_auc_score(yte, meta.predict_proba(test_cols)[:, 1]), 4), "| meta weights:", dict(zip(P, meta.coef_[0].round(2).tolist())))
st = StackingClassifier(base, LogisticRegression(), cv=5).fit(Xtr, ytr); print("StackingClassifier AUC:", round(roc_auc_score(yte, st.predict_proba(Xte)[:, 1]), 4))
infold = np.column_stack([m.predict_proba(Xtr)[:, 1] for _, m in base]); leak = LogisticRegression().fit(infold, ytr)
print("in-fold stacking meta weights (trusts the overfit RF):", dict(zip(P, leak.coef_[0].round(2).tolist())), "AUC", round(roc_auc_score(yte, leak.predict_proba(test_cols)[:, 1]), 4))
''')

X("m-adaboost",
  "AdaBoost builds a strong classifier from many weak ones (usually one-split stumps) trained **in sequence**: after each round, misclassified examples get more weight, so the next stump focuses on them. The final model is a weighted vote where better stumps get bigger say.",
  """**Algorithm (binary, y ∈ {−1, +1}).** Start weights wᵢ = 1/n. For t = 1..T: fit weak learner hₜ on weighted data; error εₜ = Σ wᵢ·1[hₜ(xᵢ) ≠ yᵢ]; say αₜ = ½ ln((1 − εₜ)/εₜ); update wᵢ ← wᵢ·exp(−αₜyᵢhₜ(xᵢ)) then normalise (wrong → ×e^α, right → ×e^−α). Predict sign(Σαₜhₜ(x)). AdaBoost = stage-wise minimisation of the **exponential loss** e^(−y·F(x)) — which is why it's sensitive to label noise and outliers (their weights blow up). Training error falls exponentially if every εₜ < 0.5.""",
  """**One round by hand.** 10 points, equal weights 0.1. Stump misclassifies 3 → ε = 0.3 → α = ½ ln(0.7/0.3) = **0.424**. Wrong points: 0.1·e^0.424 = 0.153; right: 0.1·e^−0.424 = 0.065. Normalise (3·0.153 + 7·0.065 = 0.917): wrong → **0.167**, right → **0.071**. The 3 mistakes now carry 50% of the total weight.""",
  ["Noisy labels (weights explode on mislabeled points)", "Too strong base learners (overfit fast)", "Too many rounds without validation", "Forgetting learning_rate/n_estimators trade-off"],
  ["Clean data, weak learners, teaching boosting intuition"], ["Noisy labels/outliers — prefer gradient boosting with robust losses"],
  "Sonar (rock vs mine) — AdaBoost with stumps from scratch, watch the weights concentrate on hard examples, compare with sklearn, track train/test error vs rounds, and show sensitivity to label noise.",
  ["Load and split data (labels ±1)", "Implement AdaBoost with weighted stumps", "Compare with sklearn AdaBoostClassifier", "Error vs number of rounds (staged predictions)", "Inject 10% label noise and compare with gradient boosting"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
df = pd.read_csv("{SONAR}", header=None); X, y = df.iloc[:, :60].to_numpy(), np.where(df[60] == "M", 1, -1)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=1)
def adaboost(A, t, T):
    w = np.full(len(t), 1 / len(t)); models = []
    for r in range(T):
        h = DecisionTreeClassifier(max_depth=1).fit(A, t, sample_weight=w); pred = h.predict(A)
        eps = w[pred != t].sum(); alpha = 0.5 * np.log((1 - eps) / max(eps, 1e-10))
        w *= np.exp(-alpha * t * pred); w /= w.sum(); models.append((alpha, h))
        if r in (0, 9, 49): print(f"  round {{r + 1:3d}}: ε={{eps:.3f}} α={{alpha:.3f}} | top 10% of points hold {{np.sort(w)[-len(w) // 10:].sum():.0%}} of the weight")
    return models
F = lambda models, A: np.sign(sum(a * h.predict(A) for a, h in models))
mine = adaboost(Xtr, ytr, 200); print("from-scratch AdaBoost test accuracy:", round((F(mine, Xte) == yte).mean(), 3))
sk = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=200, learning_rate=1.0, random_state=0).fit(Xtr, ytr)
print("sklearn AdaBoost test accuracy:", round(sk.score(Xte, yte), 3))
staged = [(n + 1, (p == ytr).mean(), (q == yte).mean()) for n, (p, q) in enumerate(zip(sk.staged_predict(Xtr), sk.staged_predict(Xte)))]
print("rounds -> (train, test):", {{n: (round(float(a), 2), round(float(b), 2)) for n, a, b in staged if n in (1, 10, 50, 100, 200)}})
rng = np.random.default_rng(0); noisy = ytr.copy(); flip = rng.choice(len(noisy), len(noisy) // 10, replace=False); noisy[flip] *= -1
ab = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=200, random_state=0).fit(Xtr, noisy)
gb = GradientBoostingClassifier(loss="log_loss", n_estimators=200, max_depth=1, learning_rate=0.1, subsample=0.8, random_state=0).fit(Xtr, noisy)
print(f"with 10% flipped labels: AdaBoost {{ab.score(Xte, yte):.3f}} | gradient boosting (log-loss) {{gb.score(Xte, yte):.3f}}")
''')

X("m-gradient-boosting",
  "Gradient boosting builds an ensemble of small trees **one after another, each fitting the errors (negative gradients) of the current model**, added with a small learning rate. Libraries like XGBoost, LightGBM, CatBoost and sklearn's HistGradientBoosting are the strongest general-purpose models for tabular data.",
  """**Algorithm.** F₀ = constant (mean, or log-odds). For m = 1..M: compute pseudo-residuals rᵢ = −∂L(yᵢ, F(xᵢ))/∂F (for MSE: yᵢ − F(xᵢ); for log-loss: yᵢ − pᵢ); fit a regression tree to r; set leaf values (line search / Newton step: Σg/(Σh + λ) in XGBoost); F ← F + η·tree. **Regularisation:** learning rate η (smaller + more trees = better), tree depth/leaves, min child weight, subsampling rows/columns (stochastic GB), L1/L2 on leaf weights, early stopping on validation. Histogram binning (LightGBM/HistGB) makes split search O(bins) instead of O(n). Supports custom losses (quantile, Poisson, ranking).""",
  """**Two rounds by hand (MSE, η = 0.5).** Targets [3, 5, 10]. F₀ = 6. Residuals [−3, −1, 4]. A stump splits {1, 2} | {3}: leaves −2 and 4 → F₁ = 6 + 0.5·[−2, −2, 4] = [5, 5, 8]. New residuals [−2, 0, 2] → stump leaves −1 and 2 → F₂ = [4.5, 4.5, 9]. MSE fell 8.67 → 4.33 → **1.17**.""",
  ["High learning rate with many trees (overfit)", "No early stopping", "Tuning n_estimators on the test set", "Deep trees by default (6–8 levels is plenty)", "Ignoring categorical support (native handling beats one-hot in LightGBM/CatBoost)"],
  ["Tabular prediction where accuracy matters (the default choice)"], ["Raw images/audio/text, tiny datasets where simpler models are as good, extrapolation"],
  "California housing — gradient boosting from scratch with regression trees, compare with sklearn GradientBoosting, HistGradientBoosting, XGBoost and LightGBM, use early stopping, study the learning rate / trees trade-off, and fit a quantile model.",
  ["Implement boosting from scratch (MSE pseudo-residuals)", "Learning rate vs number of trees", "Library comparison: sklearn GB, HistGB, XGBoost, LightGBM (time + RMSE)", "Early stopping on a validation set", "Quantile boosting for prediction intervals"],
  f'''
import time, numpy as np, pandas as pd, lightgbm as lgb, xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
df = pd.read_csv("{HOUSING}").dropna(); y = np.log(df.pop("median_house_value")); X = pd.get_dummies(df.assign(ocean_proximity=df.ocean_proximity.str.replace("<", "under ")), dtype=float)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0); rmse = lambda p: np.sqrt(np.mean((p - yte) ** 2))
def boost(eta, M):
    F, Ft, trees = np.full(len(ytr), ytr.mean()), np.full(len(yte), ytr.mean()), []
    for m in range(M):
        t = DecisionTreeRegressor(max_depth=4, random_state=m).fit(Xtr, ytr - F)          # fit the residuals = -gradient of MSE
        F += eta * t.predict(Xtr); Ft += eta * t.predict(Xte)
    return rmse(Ft)
for eta, M in [(1.0, 50), (0.3, 50), (0.1, 50), (0.1, 300)]: print(f"  from scratch η={{eta}} trees={{M}}: test RMSE {{boost(eta, M):.4f}}")
models = {{"sklearn GradientBoosting": GradientBoostingRegressor(n_estimators=300, max_depth=4, learning_rate=0.1, random_state=0),
          "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=300, learning_rate=0.1, random_state=0),
          "XGBoost": xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, n_jobs=4, random_state=0),
          "LightGBM": lgb.LGBMRegressor(n_estimators=300, num_leaves=31, learning_rate=0.1, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=0)}}
for name, m in models.items():
    t = time.perf_counter(); m.fit(Xtr, ytr); print(f"  {{name:25s}} RMSE {{rmse(m.predict(Xte)):.4f}} | {{time.perf_counter() - t:4.1f}}s")
A, V, ya, yv = train_test_split(Xtr, ytr, test_size=0.2, random_state=1)
es = lgb.LGBMRegressor(n_estimators=5000, learning_rate=0.03, verbose=-1, random_state=0).fit(A, ya, eval_set=[(V, yv)], callbacks=[lgb.early_stopping(100, verbose=False)])
print(f"early stopping picked {{es.best_iteration_}} trees -> test RMSE {{rmse(es.predict(Xte)):.4f}}")
lo, hi = [lgb.LGBMRegressor(objective="quantile", alpha=a, n_estimators=400, verbose=-1, random_state=0).fit(Xtr, ytr).predict(Xte) for a in (0.1, 0.9)]
print(f"80% interval coverage {{((yte >= lo) & (yte <= hi)).mean():.1%}}, median width ×{{np.exp(np.median(hi - lo)):.2f}} in price (under-covers: quantile trees are over-confident -> calibrate, e.g. conformal)")
''')

X("m-svm",
  "A support vector machine finds the boundary with the **widest margin** between classes; only the closest points (support vectors) define it. A soft margin (C) tolerates some errors, and kernels make the boundary non-linear. SVMs shine on small-to-medium, high-dimensional data like text or spectra.",
  """**Hard margin.** Maximise margin 2/‖w‖ s.t. yᵢ(w·xᵢ + b) ≥ 1 ⇔ minimise ½‖w‖². **Soft margin:** minimise ½‖w‖² + C·Σξᵢ, ξᵢ ≥ 0 slack ⇔ minimise ½‖w‖² + C·Σ max(0, 1 − yᵢ(w·xᵢ + b)) — the **hinge loss** + L2 regularisation. Large C → fewer violations, narrower margin (low bias, high variance). **Dual:** maximise Σαᵢ − ½ΣΣαᵢαⱼyᵢyⱼ(xᵢ·xⱼ) s.t. 0 ≤ αᵢ ≤ C, Σαᵢyᵢ = 0; points with αᵢ > 0 are support vectors; data appear only via dot products → kernel trick. Not probabilistic (Platt scaling for probabilities); training is O(n²–n³) for kernel SVMs → use LinearSVC/SGD for big data.""",
  """**Margin by hand.** w = [2, 1], b = −5. Point (2, 2): w·x + b = 1 → exactly on the margin (a support vector). Point (3, 2): 3 → outside, ξ = 0. Point (2, 1), label +1: 0 → hinge loss max(0, 1 − 0) = **1**. Margin width = 2/‖w‖ = 2/√5 = **0.894**.""",
  ["Not scaling features (margins depend on scale)", "Using predict_proba without knowing it's Platt-calibrated via internal CV", "Kernel SVM on 1M rows", "Tuning C and gamma on a coarse linear grid"],
  ["High-dimensional data with few samples (spectra, text, genomics), clear-margin problems"], ["Very large datasets with kernels, when calibrated probabilities are essential"],
  "Sonar returns (60 spectral features, 208 samples) — linear SVM via hinge-loss subgradient descent from scratch, sklearn SVC/LinearSVC, effect of C on margin and support vectors, RBF tuning with log-grids, and Platt-calibrated probabilities.",
  ["Scale features and split", "Linear SVM from scratch (subgradient on hinge + L2)", "Compare with LinearSVC and SVC(linear)", "C vs margin width vs number of support vectors", "RBF SVM with a log grid over C and gamma; probabilities"],
  f'''
import numpy as np, pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, LinearSVC
df = pd.read_csv("{SONAR}", header=None); X, y = df.iloc[:, :60].to_numpy(), np.where(df[60] == "M", 1, -1)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
sc = StandardScaler().fit(Xtr); A, B = sc.transform(Xtr), sc.transform(Xte)
w, b, lam = np.zeros(60), 0.0, 0.01
for epoch in range(1, 301):
    eta = 1 / (lam * epoch * 10)
    for i in np.random.default_rng(epoch).permutation(len(A)):
        if ytr[i] * (A[i] @ w + b) < 1: w = (1 - eta * lam) * w + eta * ytr[i] * A[i]; b += eta * ytr[i] * 0.1
        else: w = (1 - eta * lam) * w
print("from-scratch linear SVM test accuracy:", round((np.sign(B @ w + b) == yte).mean(), 3))
print("LinearSVC test accuracy:", round(LinearSVC(C=0.05, max_iter=20000).fit(A, ytr).score(B, yte), 3))
for C in [0.001, 0.01, 0.1, 1, 100]:
    s = SVC(kernel="linear", C=C).fit(A, ytr); print(f"  C={{C:<6}} margin {{2 / np.linalg.norm(s.coef_):.3f}} | support vectors {{s.n_support_.sum():3d}} | train {{s.score(A, ytr):.3f}} test {{s.score(B, yte):.3f}}")
gs = GridSearchCV(make_pipeline(StandardScaler(), SVC()), {{"svc__C": np.logspace(-1, 3, 5), "svc__gamma": np.logspace(-4, 0, 5)}}, cv=5).fit(Xtr, ytr)
print("RBF best", {{k: float(v) for k, v in gs.best_params_.items()}}, "CV", round(gs.best_score_, 3), "test", round(gs.score(Xte, yte), 3))
prob = make_pipeline(StandardScaler(), SVC(C=gs.best_params_["svc__C"], gamma=gs.best_params_["svc__gamma"], probability=True, random_state=0)).fit(Xtr, ytr)
print("Platt probabilities for 5 test sonar returns:", prob.predict_proba(Xte[:5])[:, 1].round(2), "true:", yte[:5])
''')

X("m-kernels",
  "A kernel is a similarity function that equals a dot product in some (possibly infinite-dimensional) feature space. The **kernel trick** lets linear algorithms (SVM, ridge regression, PCA) learn non-linear patterns by replacing every xᵢ·xⱼ with k(xᵢ, xⱼ) — without ever computing the features.",
  """**Common kernels.** Linear x·z; polynomial (γx·z + r)^d; **RBF** exp(−γ‖x − z‖²) (infinite-dimensional, local similarity — γ large → very local, wiggly; small → smooth); sigmoid. **Mercer:** valid kernels give positive semi-definite Gram matrices K. **Kernel ridge:** α = (K + λI)⁻¹y, f(x) = Σαᵢk(xᵢ, x) — O(n³). **Scaling up:** random Fourier features approximate RBF with explicit features z(x) = √(2/D)cos(Wx + b), W ~ N(0, 2γI) (Rahimi–Recht), or Nyström low-rank approximation — then use a fast linear model.""",
  """**Polynomial kernel by hand.** x = (1, 2), z = (3, 1); k(x, z) = (x·z)² = 5² = **25**. Explicit features φ(x) = (x₁², √2x₁x₂, x₂²) = (1, 2.83, 4), φ(z) = (9, 4.24, 1); φ(x)·φ(z) = 9 + 12 + 4 = **25** ✓. **RBF:** ‖x − z‖² = 4 + 1 = 5; γ = 0.1 → e^(−0.5) = **0.61**; γ = 1 → e^(−5) = 0.0067 (nearly unrelated).""",
  ["Huge γ (memorisation) or tiny γ (linear-like)", "Kernel methods on 100k+ rows without approximation", "Invalid custom kernels (not PSD)"],
  ["Non-linear patterns on small/medium data; when you have a good similarity function (strings, graphs)"], ["Large datasets — use approximations or trees/neural nets"],
  "California housing (regression) and penguins — kernel ridge regression from scratch with the RBF Gram matrix, verify the polynomial kernel trick numerically, compare linear/poly/RBF kernels, and scale up with random Fourier features and Nyström.",
  ["Verify k(x, z) = φ(x)·φ(z) for a polynomial kernel", "Kernel ridge from scratch on 2,000 houses", "Compare kernels and γ values", "Random Fourier features + linear ridge on 15,000 houses", "Nyström approximation; accuracy vs time"],
  f'''
import time, numpy as np, pandas as pd
from sklearn.kernel_approximation import Nystroem, RBFSampler
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import Ridge
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
x, z = np.array([1.0, 2.0]), np.array([3.0, 1.0]); phi = lambda v: np.array([v[0] ** 2, np.sqrt(2) * v[0] * v[1], v[1] ** 2])
print("poly kernel (x·z)² =", (x @ z) ** 2, "| explicit φ(x)·φ(z) =", round(phi(x) @ phi(z), 6))
df = pd.read_csv("{HOUSING}").dropna(); y = np.log(df.median_house_value.to_numpy())
X = StandardScaler().fit_transform(df[["median_income", "housing_median_age", "latitude", "longitude", "total_rooms"]])
Xtr, Xte, ytr, yte = train_test_split(X, y, train_size=17000, random_state=0); s = slice(0, 2000)
rmse = lambda p: np.sqrt(np.mean((p - yte) ** 2))
K = rbf_kernel(Xtr[s], Xtr[s], gamma=0.5); alpha = np.linalg.solve(K + 0.1 * np.eye(2000), ytr[s] - ytr[s].mean())
print("kernel ridge from scratch (2k rows) RMSE:", round(rmse(rbf_kernel(Xte, Xtr[s], gamma=0.5) @ alpha + ytr[s].mean()), 4))
print("linear ridge (2k rows) RMSE:", round(rmse(Ridge().fit(Xtr[s], ytr[s]).predict(Xte)), 4))
for name, kr in [("poly d=3", KernelRidge(kernel="poly", degree=3, alpha=1)), ("RBF γ=0.05", KernelRidge(kernel="rbf", gamma=0.05, alpha=0.1)), ("RBF γ=0.5", KernelRidge(kernel="rbf", gamma=0.5, alpha=0.1)), ("RBF γ=20", KernelRidge(kernel="rbf", gamma=20, alpha=0.1))]:
    print(f"  KernelRidge {{name:10s}} RMSE {{rmse(kr.fit(Xtr[s], ytr[s]).predict(Xte)):.4f}}")
for name, approx in [("random Fourier 1000", RBFSampler(gamma=0.5, n_components=1000, random_state=0)), ("Nyström 1000", Nystroem(gamma=0.5, n_components=1000, random_state=0))]:
    t = time.perf_counter(); m = make_pipeline(approx, Ridge(alpha=0.1)).fit(Xtr, ytr); print(f"  {{name:20s}} on 17k rows RMSE {{rmse(m.predict(Xte)):.4f}} in {{time.perf_counter() - t:.1f}}s")
''')

X("m-interpretability",
  "Interpretability answers *why* a model predicts what it does — globally (which features matter overall, how predictions change with a feature) and locally (why this customer got this score). Tools: coefficients, permutation importance, partial dependence/ICE, **SHAP** values, LIME, counterfactuals. Needed for trust, debugging, regulation and fairness.",
  """**Methods.** *Permutation importance:* drop in validation score when a feature is shuffled (breaks its link to y). *PDP:* average prediction as a feature is varied over its range (marginal effect; misleading with correlated features). *ICE:* one curve per row — reveals heterogeneity hidden by the PDP. **SHAP:** Shapley values from cooperative game theory — φⱼ = Σ over subsets S of |S|!(p−|S|−1)!/p! · [f(S ∪ {j}) − f(S)]; properties: local accuracy (Σφⱼ + base = prediction), consistency, missingness. TreeSHAP computes them exactly for trees in polynomial time. **Counterfactual:** the smallest change to x that flips the decision ('if tenure were 6 months longer'). Explanations describe the model, not causal reality.""",
  """**Shapley by hand (2 features).** f(∅) = 0.26 (base churn), f({contract}) = 0.40, f({tenure}) = 0.35, f({contract, tenure}) = 0.55. φ_contract = ½[(0.40 − 0.26) + (0.55 − 0.35)] = ½(0.14 + 0.20) = **0.17**; φ_tenure = ½[(0.35 − 0.26) + (0.55 − 0.40)] = **0.12**. Check: 0.26 + 0.17 + 0.12 = 0.55 ✓.""",
  ["Reading explanations as causal effects", "Impurity importance for decisions", "PDPs with strongly correlated features", "Explaining a bad model instead of fixing it"],
  ["Model debugging, stakeholder trust, regulated decisions (credit, health), feature selection"], ["Using post-hoc explanations to justify an unfair or leaky model"],
  "IBM Telco churn with gradient boosting — global permutation importance, partial dependence and ICE curves, exact Shapley values by hand for one customer (small model) checked against TreeSHAP, SHAP summary, and a simple counterfactual search.",
  ["Train a boosted model on churn", "Permutation importance on the test set", "PDP + ICE for tenure and monthly charges", "SHAP values for one customer (+ brute-force Shapley check on 3 features)", "Counterfactual: smallest tenure/contract change that flips the decision"],
  f'''
import itertools, math, numpy as np, pandas as pd, shap
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.inspection import partial_dependence, permutation_importance
from sklearn.model_selection import train_test_split
{LOAD_TELCO}
X = df[["tenure", "MonthlyCharges", "Contract", "InternetService", "PaymentMethod", "TechSupport", "OnlineSecurity", "SeniorCitizen"]].copy()
for c in X:
    if not pd.api.types.is_numeric_dtype(X[c]): X[c] = X[c].astype("category").cat.codes
X = X.astype(float)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
gb = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=0).fit(Xtr, ytr)
pi = permutation_importance(gb, Xte, yte, scoring="roc_auc", n_repeats=10, random_state=0); print("permutation importance:", pd.Series(pi.importances_mean, X.columns).sort_values(ascending=False).round(4).to_dict())
pd_t = partial_dependence(gb, Xtr, ["tenure"], kind="both", grid_resolution=6)
print("PDP tenure:", dict(zip(pd_t["grid_values"][0].round(0).tolist(), pd_t["average"][0].round(2).tolist())), "| ICE spread at tenure=1:", round(pd_t["individual"][0][:, 0].std(), 2))
ex = shap.TreeExplainer(gb); sv = ex.shap_values(Xte); base = float(np.ravel(ex.expected_value)[0]); i = 0
print(f"customer 0: base {{base:.3f}} + Σφ {{sv[i].sum():.3f}} = log-odds {{gb.decision_function(Xte.iloc[[i]])[0]:.3f}}"); print("  SHAP:", dict(zip(X.columns, sv[i].round(3).tolist())))
print("mean |SHAP| ranking:", pd.Series(np.abs(sv).mean(0), X.columns).sort_values(ascending=False).round(3).to_dict())
small = ["tenure", "MonthlyCharges", "Contract"]; m3 = GradientBoostingClassifier(n_estimators=100, max_depth=2, random_state=0).fit(Xtr[small], ytr); x0 = Xte[small].iloc[0]
def v(S):                                  # value of coalition S = mean prediction with features outside S marginalised over background data
    bg = Xtr[small].sample(300, random_state=0).copy(); bg[list(S)] = x0[list(S)].values; return m3.decision_function(bg).mean()
phi = {{j: sum(math.factorial(len(S)) * math.factorial(2 - len(S)) / 6 * (v(S + (j,)) - v(S)) for r in range(3) for S in itertools.combinations([k for k in small if k != j], r)) for j in small}}
print("brute-force Shapley (3 features):", {{k: round(float(val), 3) for k, val in phi.items()}}, "| sums to", round(sum(phi.values()), 3), "=", round(v(tuple(small)) - v(()), 3))
c = Xte.iloc[[int(np.argmax(gb.predict_proba(Xte)[:, 1]))]].copy(); print("highest-risk customer P(churn) =", round(gb.predict_proba(c)[0, 1], 2))
for months in range(0, 73, 6):
    for contract in sorted(X.Contract.unique()):
        cf = c.assign(tenure=c.tenure + months, Contract=contract)
        if gb.predict_proba(cf)[0, 1] < 0.5: print(f"counterfactual: +{{months}} months tenure and contract code {{contract}} -> P = {{gb.predict_proba(cf)[0, 1]:.2f}}"); break
    else: continue
    break
''')


SMS = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"

X("m-linear-classification",
  "A linear classifier scores each example with a weighted sum and predicts by the sign of that score, so its decision boundary is a straight line (a hyperplane). Perceptron, logistic regression, linear SVM and LDA share this form and differ only in the loss used to choose the weights, which decides *which* separating line you get.",
  """**Geometry.** f(x) = w·x + b; boundary {x : f(x) = 0}; w is normal to it and the signed distance of x is f(x)/‖w‖. **Losses with margin m = y·f(x), y ∈ {−1, +1}:** perceptron max(0, −m) (zero once correct, so any separating line is a minimum); logistic log(1 + e^(−m)) (always positive, pushes every point further out; gives P(y|x) = σ(f)); hinge max(0, 1 − m) + λ‖w‖² (zero beyond margin 1, so only points near the boundary matter → maximum margin 2/‖w‖). **Perceptron convergence:** if the data are separable with margin γ and ‖x‖ ≤ R, it makes at most (R/γ)² mistakes. **Separable data + unregularised logistic:** the loss keeps falling as ‖w‖ → ∞, so the weights diverge; regularisation fixes a finite solution. **Capacity:** a linear classifier in d dimensions can shatter d + 1 points (VC dimension d + 1).""",
  """**Perceptron by hand.** Points (x₁, x₂, y): A = (1, 1, +1), B = (−1, −1, −1). Start w = (0, 0), b = 0. A: score 0 → treated as wrong → w = (1, 1), b = 1. B: score −1 − 1 + 1 = −1 → correct. A again: 1 + 1 + 1 = 3 → correct. Boundary **x₁ + x₂ + 1 = 0**; distance of A = 3/√2 = **2.12**, of B = 1/√2 = **0.71**. A linear SVM would instead put the boundary at x₁ + x₂ = 0, equally far (√2) from both: the maximum margin.""",
  ["Forgetting to scale features (the boundary and the regularisation depend on units)", "Expecting a straight line to separate rings or XOR patterns", "Reading raw weights as importance when features are correlated", "Unregularised logistic regression on separable data (weights blow up)"],
  ["Text and other high-dimensional sparse data", "Baselines and explainable scorecards", "Low-latency prediction"], ["Clearly curved or interacting boundaries without feature engineering"],
  "Palmer penguins (real Antarctic field measurements) — perceptron, logistic regression, linear SVM and LDA on the same two features, compared by boundary, margin and accuracy; then a pair that is not separable.",
  ["Load penguins and keep two species and two features", "Standardise and fit four linear classifiers", "Print each boundary as an equation and its margin to the nearest penguin", "Repeat on a harder pair and see where straight lines fail", "Compare adding an informative new measurement (bill length) with adding quadratic terms"],
  '''
import numpy as np, pandas as pd
from sklearn.linear_model import Perceptron, LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
pg = pd.read_csv("URL_PENGUINS").dropna()
def run(a, b, feats):
    d = pg[pg.species.isin([a, b])]; X = StandardScaler().fit_transform(d[feats]); y = (d.species == b).astype(int).to_numpy()
    print(f"--- {a} vs {b} on {feats}")
    for name, m in [("perceptron", Perceptron(random_state=0)), ("logistic", LogisticRegression()), ("linear SVM", LinearSVC(C=1.0)), ("LDA", LinearDiscriminantAnalysis())]:
        m.fit(X, y); w, c = m.coef_[0], m.intercept_[0]; margin = np.min(np.abs(X @ w + c)) / np.linalg.norm(w)
        print(f"  {name:10s} {w[0]:+.2f}*x1 {w[1]:+.2f}*x2 {c:+.2f} = 0 | train acc {m.score(X, y):.3f} | closest penguin {margin:.3f} sd away | 5-fold {cross_val_score(m, X, y, cv=5).mean():.3f}")
    return d, y
run("Adelie", "Gentoo", ["bill_depth_mm", "flipper_length_mm"])
d, y = run("Adelie", "Chinstrap", ["bill_depth_mm", "flipper_length_mm"])
poly = make_pipeline(StandardScaler(), PolynomialFeatures(2), StandardScaler(), LogisticRegression(max_iter=2000))
print("Adelie vs Chinstrap with bill length added:", cross_val_score(make_pipeline(StandardScaler(), LogisticRegression()), d[["bill_length_mm", "bill_depth_mm"]], y, cv=5).mean().round(3),
      "| quadratic features:", cross_val_score(poly, d[["bill_depth_mm", "flipper_length_mm"]], y, cv=5).mean().round(3))
'''.replace("URL_PENGUINS", PENGUINS))

X("m-naive-bayes",
  "Naive Bayes turns class-conditional frequencies into a classifier with Bayes' rule, assuming features are independent given the class. Training is just counting, prediction is a sum of log-probabilities, and for text it is a fast, surprisingly strong baseline.",
  """**Decision rule.** ŷ = argmaxₖ [log πₖ + Σᵢ log P(xᵢ | k)]. **Multinomial:** P(word w | k) = (N_kw + α)/(N_k + αV); a document's log-likelihood is Σ_w count_w · log P(w | k). **Bernoulli:** P(x | k) = Πᵢ pₖᵢ^xᵢ (1 − pₖᵢ)^(1−xᵢ), so absent words count as evidence too. **Gaussian:** P(xᵢ | k) = N(μₖᵢ, σ²ₖᵢ) → quadratic boundaries with diagonal covariances. **Linear in disguise:** multinomial/Bernoulli NB give a linear decision function in the counts (log-odds = b + Σ w_w·count_w), the generative twin of logistic regression; NB converges faster with little data, logistic regression reaches lower error with lots of data (Ng & Jordan, 2002). **Calibration:** correlated features add the same evidence repeatedly, so posteriors are pushed towards 0 and 1.""",
  """**Multinomial NB by hand (α = 1, V = 4 words: free, win, lunch, call).** Spam counts: free 3, win 2, lunch 0, call 1 (total 6); ham: free 0, win 0, lunch 3, call 2 (total 5). P(free|spam) = 4/10 = 0.4, P(call|spam) = 2/10 = 0.2; P(free|ham) = 1/9 = 0.111, P(call|ham) = 3/9 = 0.333. Priors 0.5/0.5. Message "free call": spam 0.5 × 0.4 × 0.2 = **0.040**, ham 0.5 × 0.111 × 0.333 = **0.0185** → P(spam) = 0.040/0.0585 = **0.68**.""",
  ["Using Gaussian NB on word counts (use Multinomial/Bernoulli)", "Forgetting smoothing (zero probabilities)", "Trusting NB's probabilities without calibration", "Feeding TF-IDF and expecting probabilistic meaning"],
  ["Text classification baselines (spam, sentiment, topics)", "Very small labelled sets", "Streaming / incremental updates (just update counts)"], ["When calibrated probabilities matter", "Strongly correlated continuous features"],
  "SMS Spam Collection (5,572 real messages) — Multinomial and Bernoulli NB vs logistic regression, a learning curve with few labels, the most spam-indicative words, and a calibration check.",
  ["Load SMS, stratified train/test split", "Count words, fit Multinomial and Bernoulli NB", "Compare with logistic regression at 50 / 200 / all training messages", "Inspect log-probability ratios per word", "Check calibration with the Brier score"],
  '''
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, brier_score_loss
df = pd.read_csv("URL_SMS", sep="\\t", header=None, names=["label", "text"]); y = (df.label == "spam").astype(int).to_numpy()
tr, te, ytr, yte = train_test_split(df.text, y, test_size=0.25, stratify=y, random_state=0)
rng = np.random.default_rng(0)
for n in (50, 200, len(tr)):
    idx = rng.choice(len(tr), n, replace=False) if n < len(tr) else np.arange(len(tr))
    vec = CountVectorizer().fit(tr.iloc[idx]); A, B = vec.transform(tr.iloc[idx]), vec.transform(te)
    row = []
    for name, m in [("multinomial NB", MultinomialNB()), ("Bernoulli NB", BernoulliNB()), ("logistic", LogisticRegression(max_iter=2000, C=10))]:
        m.fit(A, ytr[idx]); row.append(f"{name} F1 {f1_score(yte, m.predict(B)):.3f}")
    print(f"{n:5d} training messages: " + " | ".join(row))
vec = CountVectorizer().fit(tr); nb = MultinomialNB().fit(vec.transform(tr), ytr)
ratio = nb.feature_log_prob_[1] - nb.feature_log_prob_[0]; words = vec.get_feature_names_out()
print("most spam-indicative words:", list(words[np.argsort(-ratio)[:10]]))
p = nb.predict_proba(vec.transform(te))[:, 1]
print(f"Brier score {brier_score_loss(yte, p):.4f}; share of probabilities below 0.01 or above 0.99: {np.mean((p < 0.01) | (p > 0.99)):.1%}")
'''.replace("URL_SMS", SMS))

X("m-discriminant-analysis",
  "Discriminant analysis is a generative classifier: it fits a Gaussian to each class and assigns a point to the class with the highest prior × likelihood. Sharing one covariance across classes (LDA) gives linear boundaries and a supervised projection; per-class covariances (QDA) give quadratic boundaries.",
  """**Discriminant functions.** δₖ(x) = −½ log|Σₖ| − ½(x − μₖ)ᵀΣₖ⁻¹(x − μₖ) + log πₖ (QDA). With Σₖ = Σ the quadratic term xᵀΣ⁻¹x is common to all classes and cancels: δₖ(x) = xᵀΣ⁻¹μₖ − ½μₖᵀΣ⁻¹μₖ + log πₖ (LDA, linear). **Estimates:** μ̂ₖ = class means, Σ̂ = pooled within-class covariance, π̂ₖ = class shares. **Parameters:** LDA Kd + d(d+1)/2, QDA K·(d + d(d+1)/2). **Shrinkage:** Σ̂(λ) = (1 − λ)Σ̂ + λ·(tr Σ̂/d)·I (Ledoit–Wolf chooses λ) keeps Σ̂ invertible when d is close to n. **Fisher view:** LDA's projection maximises between-class over within-class variance; at most K − 1 useful directions. **Two equal-variance 1-D classes:** boundary at (μ₁ + μ₂)/2 + σ² log(π₂/π₁)/(μ₁ − μ₂).""",
  """**LDA by hand (1 feature).** Flipper length: Adelie mean 190, Gentoo 217, shared sd 7, priors 0.6 / 0.4. Boundary = (190 + 217)/2 + 7² · ln(0.4/0.6)/(190 − 217) = 203.5 + 49 · (−0.405)/(−27) = 203.5 + 0.74 = **204.2 mm** — the more common class gets a little more room. A 204 mm penguin → **Adelie**; 205 mm → **Gentoo**.""",
  ["Using QDA with few samples per class (singular covariances) — add reg_param", "Assuming LDA needs scaled features (it doesn't change predictions)", "Ignoring strong non-normality / outliers", "Confusing LDA (classifier/projection) with LDA topic models"],
  ["Small, roughly Gaussian tabular data", "Supervised dimensionality reduction for plotting", "Fast, stable multiclass baselines"], ["Heavy outliers, very skewed or categorical features"],
  "Palmer penguins (3 species) and Pima diabetes — LDA vs QDA vs logistic regression with cross-validation, the boundary computed from class means, shrinkage when data are scarce, and a 2-D LDA projection.",
  ["Load penguins, fit LDA/QDA/logistic and compare", "Compute the 1-D LDA boundary from means and pooled sd, and check against sklearn", "Learning curve with 10/30/all samples per class, with and without shrinkage", "Project onto LDA's 2 discriminant directions", "Repeat on Pima diabetes where classes overlap"],
  '''
import numpy as np, pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA, QuadraticDiscriminantAnalysis as QDA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
pg = pd.read_csv("URL_PENGUINS").dropna(); feats = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
X, y = pg[feats].to_numpy(), pg.species.to_numpy(); cv = StratifiedKFold(5, shuffle=True, random_state=0)
for name, m in [("LDA", LDA()), ("QDA", QDA(reg_param=0.05)), ("logistic", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)))]:
    print(f"penguins {name:9s} 5-fold accuracy {cross_val_score(m, X, y, cv=cv).mean():.3f}")
two = pg[pg.species.isin(["Adelie", "Gentoo"])]; f = two.flipper_length_mm.to_numpy(); s = (two.species == "Gentoo").to_numpy()
m1, m2 = f[~s].mean(), f[s].mean(); pooled = np.sqrt((((f[~s] - m1) ** 2).sum() + ((f[s] - m2) ** 2).sum()) / (len(f) - 2)); pa, pgt = (~s).mean(), s.mean()
by_hand = (m1 + m2) / 2 + pooled ** 2 * np.log(pgt / pa) / (m1 - m2)
lda1 = LDA().fit(f.reshape(-1, 1), s); grid = np.linspace(180, 230, 5001); learned = grid[np.argmax(lda1.predict(grid.reshape(-1, 1)))]
print(f"1-D boundary by hand {by_hand:.2f} mm vs sklearn {learned:.2f} mm")
rng = np.random.default_rng(0)
for n in (5, 15, 50):
    acc = {"LDA": [], "LDA shrinkage": [], "QDA": []}
    for r in range(10):
        idx = np.concatenate([rng.choice(np.where(y == k)[0], n, replace=False) for k in np.unique(y)]); test = np.setdiff1d(np.arange(len(y)), idx)
        for name, m in [("LDA", LDA()), ("LDA shrinkage", LDA(solver="lsqr", shrinkage="auto")), ("QDA", QDA(reg_param=0.0))]:
            try: acc[name].append(m.fit(X[idx], y[idx]).score(X[test], y[test]))
            except Exception: acc[name].append(np.nan)
    print(f"{n:3d} per class: " + " | ".join(f"{k} {np.nanmean(v):.3f}" for k, v in acc.items()))
Z = LDA(n_components=2).fit(X, y).transform(X)
print(pd.DataFrame(Z, columns=["LD1", "LD2"]).assign(species=y).groupby("species").mean().round(2))
pima = pd.read_csv("URL_PIMA", names=PIMA_COLS_LIST); Xp, yp = pima.drop(columns="diabetes"), pima.diabetes
for name, m in [("LDA", LDA()), ("QDA", QDA(reg_param=0.1)), ("logistic", make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)))]:
    print(f"Pima {name:9s} AUC {cross_val_score(m, Xp, yp, cv=cv, scoring='roc_auc').mean():.3f}")
'''.replace("URL_PENGUINS", PENGUINS).replace("URL_PIMA", PIMA).replace("PIMA_COLS_LIST", repr(PIMA_COLS)))

X("m-threshold-calibration",
  "Turning a probability into a decision needs two separate things: probabilities you can trust (calibration) and a threshold chosen from the costs or constraints of the application. Neither is the model's job by default, and 0.5 is rarely the right cut-off.",
  """**Cost-optimal threshold.** With calibrated p and costs C_FN (miss) and C_FP (false alarm), flagging costs (1 − p)C_FP and not flagging costs pC_FN ⇒ flag iff p > C_FP/(C_FP + C_FN). **Calibration** means P(Y = 1 | p̂ = q) = q. Measures: **Brier score** (1/n)Σ(p − y)², which splits into a calibration part and a discrimination (refinement) part; **expected calibration error** ECE = Σ_bins (n_b/n)|mean p_b − rate_b|; reliability diagrams. **Platt scaling:** fit p = σ(a·s + b) on held-out scores s (2 parameters, needs little data, assumes a sigmoid-shaped distortion). **Isotonic regression:** monotone, non-parametric step function (needs more data, can overfit). Always fit the calibrator on data the model didn't train on (CalibratedClassifierCV cross-fits). **Prevalence shift:** if the positive rate changes from π to π′, adjust odds by (π′/(1−π′))/(π/(1−π)).""",
  """**Threshold from costs.** Screening for diabetes: a missed case costs 8 units (late treatment), a false alarm costs 1 (an extra test). t = 1/(1 + 8) = **0.11**. Out of 100 patients with calibrated p = 0.2: expected cost of not flagging = 0.2 × 8 = 1.6 per patient; of flagging = 0.8 × 1 = 0.8 → flag. **Calibration check:** 40 patients predicted around 0.30, 18 actually diabetic → observed 0.45: the model under-predicts in this bin.""",
  ["Tuning the threshold on the test set", "Calibrating on the training data", "Assuming accuracy or AUC say anything about calibration", "Using 0.5 with imbalanced classes", "Forgetting to recalibrate when the base rate changes"],
  ["Any decision with unequal error costs", "Risk scores shown to people", "Combining model outputs with business rules"], ["Pure ranking tasks where only the order matters"],
  "Pima Indians diabetes (768 real patients) — reliability diagrams and Brier/ECE for logistic regression, Naive Bayes and random forest, Platt vs isotonic calibration, and thresholds chosen by cost, by a recall target and by review capacity.",
  ["Split into train / calibration-by-CV / test", "Measure calibration per model with bins, Brier and ECE", "Calibrate with Platt and isotonic and re-measure", "Choose thresholds three ways on out-of-fold predictions", "Report test recall, precision and expected cost per threshold"],
  '''
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import brier_score_loss, roc_auc_score
df = pd.read_csv("URL_PIMA", names=PIMA_COLS_LIST); y = df.pop("diabetes").to_numpy(); X = df.to_numpy()
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
def ece(y, p, bins=10):
    b = np.minimum((p * bins).astype(int), bins - 1); return sum((b == k).mean() * abs(p[b == k].mean() - y[b == k].mean()) for k in range(bins) if (b == k).any())
models = {"logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)), "naive Bayes": GaussianNB(), "random forest": RandomForestClassifier(300, min_samples_leaf=5, random_state=0)}
for name, m in models.items():
    for tag, est in [("raw", m), ("Platt", CalibratedClassifierCV(m, method="sigmoid", cv=5)), ("isotonic", CalibratedClassifierCV(m, method="isotonic", cv=5))]:
        p = est.fit(Xtr, ytr).predict_proba(Xte)[:, 1]
        print(f"{name:13s} {tag:8s} Brier {brier_score_loss(yte, p):.3f} ECE {ece(yte, p):.3f} AUC {roc_auc_score(yte, p):.3f}")
frac, mean_p = calibration_curve(yte, GaussianNB().fit(Xtr, ytr).predict_proba(Xte)[:, 1], n_bins=5)
print("naive Bayes reliability (predicted -> observed):", [f"{a:.2f}->{b:.2f}" for a, b in zip(mean_p, frac)])
final = CalibratedClassifierCV(models["logistic"], method="sigmoid", cv=5)
oof = cross_val_predict(final, Xtr, ytr, cv=5, method="predict_proba")[:, 1]
C_FN, C_FP = 8.0, 1.0
cost = lambda yy, f: ((~f & (yy == 1)).sum() * C_FN + (f & (yy == 0)).sum() * C_FP) / len(yy)
grid = np.linspace(0.02, 0.9, 89)
t_cost = grid[np.argmin([cost(ytr, oof >= t) for t in grid])]
t_recall = max(t for t in grid if ((oof >= t) & (ytr == 1)).sum() / (ytr == 1).sum() >= 0.9)
t_cap = np.quantile(oof, 1 - 0.25)                    # team can review the top 25% of patients
p = final.fit(Xtr, ytr).predict_proba(Xte)[:, 1]
for name, t in [("0.5 default", 0.5), (f"cost-optimal (theory {C_FP / (C_FP + C_FN):.2f})", t_cost), ("recall >= 90%", t_recall), ("review top 25%", t_cap)]:
    f = p >= t; tp = (f & (yte == 1)).sum()
    print(f"{name:28s} t={t:.2f} recall {tp / (yte == 1).sum():.2f} precision {tp / max(f.sum(), 1):.2f} flagged {f.mean():.0%} cost/patient {cost(yte, f):.3f}")
'''.replace("URL_PIMA", PIMA).replace("PIMA_COLS_LIST", repr(PIMA_COLS)))

X("m-choosing-classifier",
  "Choosing a classifier is an experiment, not a preference: compare several model families on identical, leak-free cross-validation folds with the metric that reflects the goal, read the spread as well as the mean, and pick the simplest model whose performance is not distinguishably worse.",
  """**Same folds, paired comparison.** With per-fold scores a_i, b_i on the same K folds, the paired differences dᵢ = aᵢ − bᵢ cancel fold difficulty; a rough check is mean(d) vs its standard error sd(d)/√K (CV folds overlap, so this is optimistic; the corrected resampled t-test of Nadeau & Bengio inflates the variance by (1/K + n_test/n_train)). **Repeated stratified CV** reduces the variance of the estimate. **Nested CV** when tuning: inner loop selects hyperparameters, outer loop estimates performance, otherwise the winner's score is biased upwards. **No free lunch:** averaged over all problems no learner is better; good choices come from matching the inductive bias (linear, local, axis-aligned splits, smooth kernels) to the data. **Bias–variance:** small n favours simple, high-bias models (NB, LDA, regularised linear); large n lets flexible models (boosting, deep nets) win.""",
  """**Is the gap real?** 5-fold AUCs — boosting: 0.87, 0.85, 0.88, 0.86, 0.84; logistic: 0.86, 0.85, 0.86, 0.86, 0.83. Differences: 0.01, 0.00, 0.02, 0.00, 0.01 → mean **0.008**, sd 0.0084, standard error 0.0084/√5 = **0.0037** → about 2 standard errors, and folds overlap, so the evidence is weak. If explanations are required, logistic regression is a defensible choice.""",
  ["Comparing models on different splits", "Preprocessing (scaling, encoding, selection) outside the CV loop", "Reporting the best tuned score without nested CV", "Ignoring the spread across folds", "Picking on accuracy when the goal is recall or calibration"],
  ["Every new classification project", "Model reviews and interview case studies"], ["—"],
  "Titanic passengers (891 real people) — nine classifier families in leak-free pipelines on the same repeated stratified folds, with AUC mean ± sd, paired differences against logistic regression, fit time, and a final pick with reasons.",
  ["Load Titanic and build a ColumnTransformer for numeric and categorical columns", "Define nine models inside pipelines", "Score all on the same RepeatedStratifiedKFold with AUC and time them", "Compute paired fold differences vs logistic regression", "Choose and justify the final model"],
  '''
import time, numpy as np, pandas as pd
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
df = pd.read_csv("URL_TITANIC"); y = df.pop("Survived")
num, cat = ["Age", "Fare", "SibSp", "Parch", "Pclass"], ["Sex", "Embarked"]
pre = lambda: make_column_transformer((make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num),
                                      (make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", sparse_output=False)), cat))
models = {"majority": DummyClassifier(), "logistic": LogisticRegression(max_iter=2000), "naive Bayes": GaussianNB(), "LDA": LinearDiscriminantAnalysis(),
          "kNN (k=15)": KNeighborsClassifier(15), "tree (depth 4)": DecisionTreeClassifier(max_depth=4, random_state=0),
          "random forest": RandomForestClassifier(300, min_samples_leaf=3, random_state=0, n_jobs=-1), "grad. boosting": HistGradientBoostingClassifier(max_depth=3, random_state=0),
          "SVM RBF": SVC(probability=True, random_state=0)}
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=0); scores = {}
for name, m in models.items():
    t0 = time.time(); s = cross_val_score(make_pipeline(pre(), m), df, y, cv=cv, scoring="roc_auc"); scores[name] = s
    print(f"{name:15s} AUC {s.mean():.3f} ± {s.std():.3f}   {time.time() - t0:5.1f}s")
base = scores["logistic"]
for name, s in scores.items():
    if name in ("logistic", "majority"): continue
    d = s - base; print(f"{name:15s} minus logistic: {d.mean():+.3f} (std error {d.std(ddof=1) / np.sqrt(len(d)):.3f})")
best = max(scores, key=lambda k: scores[k].mean()); d = scores[best] - base; se = d.std(ddof=1) / np.sqrt(len(d))
verdict = "a real gain: use it unless every decision must be explained" if d.mean() > 2 * se else "within noise: prefer the simpler logistic regression"
print(f"highest mean AUC: {best}, {d.mean():+.3f} vs logistic ({d.mean() / se:.1f} standard errors) → {verdict}")
'''.replace("URL_TITANIC", TITANIC))
