"""Module 1 (part B): supervised algorithms — regression, classification, trees, ensembles, SVM, interpretation."""
from ml_util import M

SUP = [
M("m-linear-regression", "Linear regression (simple and multiple)", "Basic",
  "Linear regression predicts a number as a weighted sum of features plus a bias: ŷ = w·x + b, choosing weights that minimise squared error.",
  """### Model
ŷ = b + w₁x₁ + … + w_dx_d. Each weight is the change in ŷ for a one-unit change in that feature, holding others fixed.

### Training
Minimise MSE — closed form (normal equation / least squares) or gradient descent: w ← w − η·(2/n)Xᵀ(Xw − y).

### Assumptions (for valid inference, less critical for pure prediction)
**L**inearity, **I**ndependent errors, **N**ormally distributed errors, **E**qual variance (homoscedasticity), no severe multicollinearity.

### Extensions
- **Polynomial regression**: add x², x³ features — still linear in the weights.
- **Ridge / Lasso / Elastic Net**: regularised versions.
- **Robust regression** (Huber, RANSAC) for outliers; **quantile regression** for percentiles.
- **Generalised linear models**: Poisson (counts), logistic (probabilities).

### Interpreting
Standardise features to compare weight sizes; check residual plots; p-values and confidence intervals come from statsmodels.""",
  analogy="Like estimating a taxi fare: a fixed starting charge (bias) plus a rate per kilometre and a rate per minute (weights).",
  demo="linreg",
  code="""
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(0); n = 200
area = rng.uniform(500, 3000, n); age = rng.uniform(0, 40, n)
price = 50 + 0.12 * area - 1.5 * age + rng.normal(0, 25, n)          # in lakhs
X = np.column_stack([area, age])

lr = LinearRegression().fit(X, price)
print("sklearn: intercept", round(lr.intercept_, 2), " weights", lr.coef_.round(3), " R^2", round(lr.score(X, price), 3))

w = np.zeros(3); Xb = np.column_stack([np.ones(n), (X - X.mean(0)) / X.std(0)])    # gradient descent on scaled data
for _ in range(2000):
    w -= 0.1 * 2 / n * Xb.T @ (Xb @ w - price)
print("gradient descent (scaled features) weights:", w.round(2))

ols = sm.OLS(price, sm.add_constant(X)).fit()
print(ols.summary().tables[1])
""",
  say=[("How do you interpret a coefficient in multiple linear regression?",
        "\"It's the expected change in the target for a one-unit increase in that feature, holding all other features constant. So if the area coefficient is 0.12 lakh, an extra square foot adds about 12,000 rupees at the same age. To compare importance across features I standardise them first, and I'm careful when features are correlated because coefficients become unstable.\"")]),

M("m-logistic-regression", "Logistic regression (binary and multinomial)", "Basic",
  "Logistic regression is a linear model for classification: it squashes w·x + b through the sigmoid to get a probability, trained with cross-entropy loss.",
  """### Model
p(y = 1 | x) = σ(w·x + b) = 1 / (1 + e^−(w·x+b)). Decision boundary: w·x + b = 0 (a hyperplane) when the threshold is 0.5.

### Log-odds interpretation
log(p / (1 − p)) = w·x + b. A one-unit increase in xⱼ multiplies the **odds** by e^wⱼ (odds ratio).

### Training
Minimise **binary cross-entropy** (log loss) — convex, solved by gradient descent / L-BFGS. Gradient: Xᵀ(p − y)/n.

### Multiclass
**Softmax (multinomial) regression**: one weight vector per class, p(k) = e^zₖ / Σe^zⱼ, trained with categorical cross-entropy. Alternative: one-vs-rest.

### Practical
Regularised by default in scikit-learn (C = 1/λ); scale features; outputs are fairly well calibrated; fast and interpretable — the go-to baseline for classification.""",
  code="""
import numpy as np
from sklearn.datasets import load_breast_cancer, load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True); X = StandardScaler().fit_transform(X)
sig = lambda z: 1 / (1 + np.exp(-z))
w, b = np.zeros(X.shape[1]), 0.0
for _ in range(500):                                         # logistic regression from scratch
    p = sig(X @ w + b); w -= 0.1 * X.T @ (p - y) / len(y); b -= 0.1 * (p - y).mean()
print("from-scratch accuracy:", ((sig(X @ w + b) >= 0.5) == y).mean().round(4))
sk = LogisticRegression(max_iter=1000).fit(X, y); print("sklearn accuracy:      ", round(sk.score(X, y), 4))
print("odds ratio for 1 std of feature 0:", np.exp(sk.coef_[0][0]).round(3))

Xi, yi = load_iris(return_X_y=True)
soft = LogisticRegression(max_iter=1000).fit(Xi, yi)                       # multinomial softmax
print("softmax probabilities for one flower:", soft.predict_proba(Xi[100:101]).round(3))
""",
  say=[("Why is it called logistic 'regression' if it's a classifier?",
        "\"Because it regresses the log-odds of the positive class as a linear function of the features, then maps that through the logistic sigmoid to a probability. The classification only happens when we apply a threshold to that probability.\"")]),

M("m-knn", "k-nearest neighbours (kNN)", "Basic",
  "kNN classifies a point by a majority vote of its k closest training examples (or averages them for regression). No training — it just remembers the data.",
  """### Algorithm
1. Choose k and a distance (Euclidean, Manhattan, cosine).
2. For a query point, find the k nearest training points.
3. Classification: majority vote (optionally distance-weighted). Regression: average.

### Choosing k
Small k ⇒ jagged boundary, low bias, high variance (k = 1 memorises noise). Large k ⇒ smooth boundary, high bias. Pick by cross-validation; odd k avoids ties in binary problems.

### Practical points
- **Scale features** — distances are dominated by large-range features.
- **Curse of dimensionality**: in high dimensions all points are almost equally far; reduce dimensions first.
- Prediction is slow (O(n·d) per query) — speed up with KD-trees, ball trees or approximate nearest neighbour (FAISS, HNSW) — the same tech behind vector databases.
- Lazy, non-parametric, naturally multiclass, easy to explain ("these 5 similar customers churned").""",
  demo="knn",
  code="""
from sklearn.datasets import make_moons
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np

X, y = make_moons(500, noise=0.3, random_state=0)
for k in (1, 5, 15, 51, 201):
    s = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier(k)), X, y, cv=5).mean()
    print(f"k={k:3d}  CV accuracy {s:.3f}")

# kNN from scratch for one query
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
q = Xte[0]; d = np.linalg.norm(Xtr - q, axis=1); nn = d.argsort()[:5]
print("5 nearest labels:", ytr[nn], "-> predict", np.bincount(ytr[nn]).argmax(), " true:", yte[0])
""",
  say=[("What are the downsides of kNN?",
        "\"Prediction is slow and memory-heavy because it compares against all training data; it's sensitive to feature scaling and irrelevant features; it degrades in high dimensions because distances become meaningless; and choosing k matters. I'd scale features, reduce dimensions, and use approximate nearest-neighbour indexes for large data.\"")]),

M("m-decision-tree", "Decision trees: splits, Gini, entropy, pruning", "Basic",
  "A decision tree asks a sequence of yes/no questions about features, splitting data into purer groups, until it reaches a leaf that gives the prediction.",
  """### How a tree is grown (CART algorithm)
At each node, try every feature and threshold; choose the split that most reduces impurity; recurse until a stopping rule. Greedy, top-down.

### Impurity measures
- **Gini** = 1 − Σpₖ² (scikit-learn default).
- **Entropy** = −Σpₖ log₂pₖ; reduction = **information gain**.
- Regression trees use variance/MSE reduction; leaves predict the mean.

### Controlling overfitting
A fully grown tree memorises the data. Limit `max_depth`, `min_samples_leaf`, `min_samples_split`, `max_leaf_nodes`, or **cost-complexity pruning** (`ccp_alpha`).

### Pros
Interpretable (draw it!), handles mixed data, no scaling needed, captures non-linearity and interactions, fast predictions.

### Cons
High variance (small data changes ⇒ different tree), axis-aligned step boundaries, biased toward features with many split points. **Ensembles (random forests, boosting) fix most of this.**""",
  demo="tree",
  code="""
import numpy as np
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import cross_val_score

def gini(labels):
    _, c = np.unique(labels, return_counts=True); p = c / c.sum(); return 1 - (p ** 2).sum()
parent = np.array([0] * 5 + [1] * 5); left, right = parent[:4], parent[4:]
gain = gini(parent) - (len(left) * gini(left) + len(right) * gini(right)) / len(parent)
print(f"gini parent={gini(parent):.3f}, weighted children={gini(parent) - gain:.3f}, gain={gain:.3f}")

data = load_iris(); X, y = data.data, data.target
tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
print(export_text(tree, feature_names=list(data.feature_names)))
for d in (1, 2, 3, None):
    print("max_depth", d, "CV:", round(cross_val_score(DecisionTreeClassifier(max_depth=d, random_state=0), X, y, cv=5).mean(), 3))
""",
  say=[("How does a decision tree choose where to split?",
        "\"For each node it tries every feature and candidate threshold and picks the split that gives the biggest drop in impurity — Gini or entropy for classification, variance for regression — weighted by the size of each child. It's greedy: the best split now, not globally optimal. Then it recurses until a stopping condition like max depth or min samples per leaf.\"")]),

M("m-bootstrap-bagging", "Bootstrap and bagging (bootstrap aggregating)", "Intermediate",
  "Bagging trains many models on different bootstrap samples (random draws with replacement) and averages their predictions, which reduces variance without increasing bias.",
  """### Bootstrap
Draw n samples **with replacement** from n data points. Each bootstrap sample contains ≈ **63.2%** unique points (1 − 1/e); the rest (~36.8%) are **out-of-bag (OOB)** and can be used for validation for free.

### Bagging
1. Make B bootstrap samples. 2. Train a high-variance model (usually a deep decision tree) on each. 3. Average (regression) or vote (classification).
Averaging B models with variance σ² and correlation ρ gives variance ρσ² + (1 − ρ)σ²/B — so the models should be **diverse** (low ρ).

### When it helps
Unstable, high-variance learners (deep trees, kNN with small k on noisy data). It does little for stable models like linear regression.

### Related ideas
**Random forest** = bagging + random feature subsets at each split (lower ρ). **Pasting** = sampling without replacement. **Random subspaces** = sample features. The bootstrap also gives confidence intervals for any statistic.""",
  code="""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier

rng = np.random.default_rng(0); n = 10_000
uniq = np.mean([len(np.unique(rng.integers(0, n, n))) / n for _ in range(20)])
print(f"unique fraction in a bootstrap sample: {uniq:.3f} (theory 1 - 1/e = {1 - np.exp(-1):.3f})")

X, y = make_classification(1000, 20, n_informative=6, flip_y=0.1, random_state=0)
tree = DecisionTreeClassifier(random_state=0)
bag = BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, oob_score=True, random_state=0)
print("single deep tree CV:", cross_val_score(tree, X, y, cv=5).mean().round(3))
print("bagged trees CV:    ", cross_val_score(bag, X, y, cv=5).mean().round(3))
print("bagging OOB score:  ", round(bag.fit(X, y).oob_score_, 3))
""",
  say=[("Why does bagging reduce variance but not bias?",
        "\"Each model is trained on a slightly different bootstrap sample, so their errors partly cancel when averaged — variance drops, especially if the models are diverse. But every model has the same underlying form and capacity, so systematic errors are shared and survive averaging. That's why bagging uses low-bias, high-variance learners like deep trees, while boosting attacks bias.\"")]),

M("m-random-forest", "Random forests", "Intermediate",
  "A random forest is bagging of decision trees where each split considers only a random subset of features. The extra randomness decorrelates the trees, making the average more accurate.",
  """### Algorithm
For b = 1…B: bootstrap sample → grow a deep tree where **each split picks the best feature from a random subset** of size max_features (√d for classification, d/3 or all for regression in scikit-learn). Predict by majority vote / average.

### Key hyperparameters
`n_estimators` (more is better until it plateaus), `max_features` (lower ⇒ more diversity), `max_depth`, `min_samples_leaf`, `class_weight`.

### Extras you get for free
- **OOB score** — validation without a split.
- **Feature importance** (mean decrease in impurity — biased toward high-cardinality features; prefer permutation importance).
- Robust to outliers and noise, little tuning, no scaling, handles non-linearity; parallel training.

### Limitations
Large models and slower predictions; can't extrapolate beyond the training range in regression; usually beaten by gradient boosting on tabular data; less interpretable than one tree.

**Extra-Trees** (extremely randomised trees) also pick random thresholds — even more variance reduction and faster.""",
  code="""
from sklearn.datasets import fetch_california_housing, load_breast_cancer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.inspection import permutation_importance
import numpy as np

data = load_breast_cancer(); X, y = data.data, data.target
for name, m in [("random forest", RandomForestClassifier(300, random_state=0, n_jobs=-1)), ("extra trees", ExtraTreesClassifier(300, random_state=0, n_jobs=-1))]:
    print(f"{name:14s} CV accuracy {cross_val_score(m, X, y, cv=5).mean():.4f}")
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
rf = RandomForestClassifier(300, oob_score=True, random_state=0, n_jobs=-1).fit(Xtr, ytr)
print("OOB:", round(rf.oob_score_, 4), " test:", round(rf.score(Xte, yte), 4))
pi = permutation_importance(rf, Xte, yte, n_repeats=10, random_state=0)
top = np.argsort(pi.importances_mean)[::-1][:3]
print("top features (permutation):", [str(data.feature_names[i]) for i in top])
""",
  say=[("What makes a random forest better than bagging plain trees?",
        "\"Feature subsampling at each split. With plain bagging, a few strong features dominate the top splits of every tree, so the trees are highly correlated and averaging helps less. Restricting each split to a random subset of features forces diversity, lowering correlation between trees and therefore the variance of the average.\"")]),

M("m-voting-stacking", "Ensembles: voting, averaging, stacking and blending", "Intermediate",
  "Combining different models often beats the best single model. Voting averages their predictions; stacking trains a meta-model to learn how to combine them.",
  """### Voting
- **Hard voting**: majority of predicted classes.
- **Soft voting**: average predicted probabilities (usually better; needs calibrated probabilities).
- **Weighted** voting/averaging gives better models more say.

### Stacking (stacked generalisation)
1. Train diverse base models (logistic regression, random forest, kNN, gradient boosting…).
2. Generate their **out-of-fold** predictions on the training data.
3. Train a meta-learner (often logistic/linear regression) on those predictions.
Out-of-fold predictions are essential — otherwise the meta-model learns from overfit predictions.

### Blending
Like stacking, but the meta-model is trained on a held-out validation set — simpler, uses less data.

### Why ensembles work
Different models make different errors; combining them cancels some errors (wisdom of crowds). Diversity matters more than individual strength. Kaggle winners almost always ensemble; production systems weigh the gain against complexity and latency.""",
  code="""
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = make_classification(1500, 20, n_informative=8, flip_y=0.05, random_state=7)
base = [("lr", make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))), ("rf", RandomForestClassifier(200, random_state=0)),
        ("knn", make_pipeline(StandardScaler(), KNeighborsClassifier(15))), ("nb", GaussianNB())]
for name, m in base:
    print(f"{name:10s} {cross_val_score(m, X, y, cv=5).mean():.4f}")
print(f"{'hard vote':10s} {cross_val_score(VotingClassifier(base, voting='hard'), X, y, cv=5).mean():.4f}")
print(f"{'soft vote':10s} {cross_val_score(VotingClassifier(base, voting='soft'), X, y, cv=5).mean():.4f}")
print(f"{'stacking':10s} {cross_val_score(StackingClassifier(base, LogisticRegression(), cv=5), X, y, cv=5).mean():.4f}")
""",
  say=[("What's the difference between bagging, boosting and stacking?",
        "\"Bagging trains the same type of model in parallel on bootstrap samples and averages them — it reduces variance. Boosting trains models sequentially, each one fixing the previous ones' errors — it reduces bias. Stacking trains different types of models and then a meta-model on their out-of-fold predictions to learn the best combination.\"")]),

M("m-adaboost", "Boosting and AdaBoost", "Intermediate",
  "Boosting builds a strong model from many weak ones trained in sequence, each focusing on the examples the previous ones got wrong. AdaBoost does this by re-weighting samples.",
  """### AdaBoost (Adaptive Boosting) for binary labels ±1
1. Start with equal sample weights wᵢ = 1/n.
2. For t = 1…T: train a weak learner hₜ (usually a decision stump) on weighted data; compute weighted error εₜ.
3. Model weight **αₜ = ½ ln((1 − εₜ)/εₜ)** — accurate learners get more say.
4. Update **wᵢ ← wᵢ · exp(−αₜ yᵢ hₜ(xᵢ))** and normalise — misclassified points get heavier.
5. Final: **H(x) = sign(Σ αₜ hₜ(x))**.
AdaBoost minimises exponential loss; it's sensitive to noisy labels and outliers (they keep gaining weight).

### Boosting in general
Sequential, reduces bias (and variance somewhat). Key controls: number of rounds, learning rate (shrinkage), weak-learner depth. Generalised by **gradient boosting**, which fits each new model to the gradient of any differentiable loss.""",
  code="""
import numpy as np
from sklearn.datasets import make_moons
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split

X, y01 = make_moons(600, noise=0.25, random_state=0); y = 2 * y01 - 1
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
w = np.full(len(ytr), 1 / len(ytr)); stumps, alphas = [], []
for t in range(50):                                     # AdaBoost from scratch
    s = DecisionTreeClassifier(max_depth=1).fit(Xtr, ytr, sample_weight=w)
    pred = s.predict(Xtr); err = w[pred != ytr].sum()
    a = 0.5 * np.log((1 - err) / max(err, 1e-10))
    w *= np.exp(-a * ytr * pred); w /= w.sum(); stumps.append(s); alphas.append(a)
F = sum(a * s.predict(Xte) for a, s in zip(alphas, stumps))
print("one stump test accuracy:     ", round((stumps[0].predict(Xte) == yte).mean(), 3))
print("from-scratch AdaBoost (50):  ", round((np.sign(F) == yte).mean(), 3))
print("sklearn AdaBoostClassifier:  ", round(AdaBoostClassifier(n_estimators=50, random_state=0).fit(Xtr, ytr).score(Xte, yte), 3))
""",
  say=[("How does AdaBoost decide which samples to focus on?",
        "\"After each round it increases the weights of misclassified samples and decreases the weights of correct ones, by a factor that depends on that learner's accuracy. The next weak learner is trained on the re-weighted data, so it concentrates on the hard examples. The final prediction is a weighted vote where more accurate learners count more.\"")]),

M("m-gradient-boosting", "Gradient boosting, XGBoost, LightGBM and CatBoost", "Intermediate",
  "Gradient boosting adds trees one at a time, each fitted to the residual errors (negative gradients) of the current ensemble. XGBoost, LightGBM and CatBoost are fast, regularised implementations that dominate tabular ML.",
  """### Algorithm
F₀ = constant (e.g. mean). For m = 1…M: compute pseudo-residuals rᵢ = −∂L(yᵢ, F(xᵢ))/∂F (for MSE, just y − F); fit a small tree hₘ to them; update **Fₘ = Fₘ₋₁ + η·hₘ**. Works for any differentiable loss (MSE, log loss, ranking, quantile).

### XGBoost (eXtreme Gradient Boosting)
Second-order (gradient + Hessian) split finding, L1/L2 regularisation on leaf weights, built-in missing-value handling, column/row subsampling, parallelism, early stopping.

### LightGBM
Histogram-based splits, **leaf-wise** growth (deeper, more accurate, watch overfitting via `num_leaves`), GOSS and EFB for speed — very fast on large data.

### CatBoost
Native categorical features with ordered target statistics (avoids leakage), ordered boosting, symmetric trees — strong defaults.

### Key hyperparameters
learning_rate (0.01–0.1) × n_estimators (use **early stopping** on validation), max_depth / num_leaves, min_child_weight, subsample, colsample_bytree, reg_lambda / reg_alpha, scale_pos_weight for imbalance.

### Why it wins on tabular data
Handles mixed types, missing values, non-linearity and interactions with little preprocessing; still usually beats deep learning on tables.""",
  code="""
import numpy as np, xgboost as xgb
from sklearn.datasets import make_regression, load_breast_cancer
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

X, y = make_regression(800, 8, noise=10, random_state=0)
F = np.full_like(y, y.mean()); lr = 0.1
for m in range(100):                                   # gradient boosting from scratch (MSE)
    t = DecisionTreeRegressor(max_depth=3).fit(X, y - F); F += lr * t.predict(X)
    if m in (0, 9, 99): print(f"after {m + 1:3d} trees train RMSE = {np.sqrt(((y - F) ** 2).mean()):.2f}")

Xc, yc = load_breast_cancer(return_X_y=True)
Xtr, Xva, ytr, yva = train_test_split(Xc, yc, stratify=yc, random_state=0)
clf = xgb.XGBClassifier(n_estimators=1000, learning_rate=0.05, max_depth=4, subsample=0.8, colsample_bytree=0.8,
                        reg_lambda=1.0, early_stopping_rounds=50, eval_metric="logloss", random_state=0)
clf.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
print("XGBoost best iteration:", clf.best_iteration, " AUC:", round(roc_auc_score(yva, clf.predict_proba(Xva)[:, 1]), 4))
hgb = HistGradientBoostingClassifier(random_state=0).fit(Xtr, ytr)   # LightGBM-style, built into sklearn
print("HistGradientBoosting AUC:", round(roc_auc_score(yva, hgb.predict_proba(Xva)[:, 1]), 4))
""",
  say=[("Explain gradient boosting in simple terms.",
        "\"Start with a simple prediction like the average. Then repeatedly train a small tree to predict the current model's mistakes — technically the negative gradient of the loss — and add a scaled-down version of it to the model. Each tree corrects what the ensemble still gets wrong. A small learning rate with many trees and early stopping on a validation set gives the best results.\"")]),

M("m-svm", "Support vector machines (SVM): maximum margin classifiers", "Intermediate",
  "An SVM finds the separating hyperplane with the widest margin between classes. Only the closest points — the support vectors — define it.",
  """### Hard-margin SVM
Maximise the margin 2/‖w‖ ⇔ minimise ½‖w‖² subject to yᵢ(w·xᵢ + b) ≥ 1 for all i.

### Soft-margin SVM
Real data overlaps, so allow violations with slack ξᵢ: minimise ½‖w‖² + C Σξᵢ. Equivalent to **hinge loss** max(0, 1 − y·f(x)) + L2 regularisation.
- **Large C**: few violations, narrow margin, risk of overfitting.
- **Small C**: wide margin, more violations, smoother boundary.

### Support vectors
Points on or inside the margin; the solution depends only on them (sparse). Removing other points doesn't change the model.

### Practical
- **Scale features** (essential).
- Training is O(n²)–O(n³): great for small/medium data (≤ ~100k), slow for millions — use `LinearSVC` / SGD then.
- No native probabilities (Platt scaling via `probability=True`).
- **SVR** (support vector regression) uses an ε-insensitive tube.
- Multiclass via one-vs-one (SVC) or one-vs-rest.""",
  code="""
import numpy as np
from sklearn.svm import SVC, LinearSVC, SVR
from sklearn.datasets import make_blobs, load_digits
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = make_blobs(80, centers=2, cluster_std=1.2, random_state=6)
for C in (0.01, 1, 100):
    m = SVC(kernel="linear", C=C).fit(X, y)
    print(f"C={C:<6} support vectors={m.n_support_.sum():3d}  margin width={2 / np.linalg.norm(m.coef_):.2f}")

Xd, yd = load_digits(return_X_y=True)
print("digits, linear SVM CV:", cross_val_score(make_pipeline(StandardScaler(), LinearSVC(max_iter=5000)), Xd, yd, cv=3).mean().round(3))
x = np.linspace(0, 6, 60)[:, None]; yr = np.sin(x).ravel()
print("SVR fit R^2:", round(SVR(C=10, epsilon=0.05).fit(x, yr).score(x, yr), 3))
""",
  say=[("What is the C parameter in an SVM?",
        "\"C controls the trade-off between a wide margin and classifying training points correctly. A large C penalises violations heavily, giving a narrow margin that fits the training data closely and may overfit; a small C allows more violations for a wider, smoother margin. It's the inverse of regularisation strength, tuned with cross-validation together with the kernel's gamma.\"")]),

M("m-kernels", "Kernel methods and the kernel trick (RBF, polynomial)", "Advanced",
  "The kernel trick lets linear algorithms like SVMs learn non-linear boundaries by computing similarities in a high-dimensional space without ever building that space.",
  """### Idea
Map x → φ(x) in a richer space where classes are linearly separable. The SVM dual only needs dot products φ(xᵢ)·φ(xⱼ), so replace them with a **kernel K(xᵢ, xⱼ)** computed directly.

### Common kernels
|Kernel|Formula|Notes|
|Linear|x·z|high-dimensional sparse data (text)|
|Polynomial|(γ x·z + r)ᵈ|feature interactions up to degree d|
|RBF / Gaussian|exp(−γ‖x − z‖²)|default; infinite-dimensional; γ = how far one point's influence reaches|
|Sigmoid|tanh(γ x·z + r)|neural-net-like|

### γ (gamma) for RBF
Large γ ⇒ each point influences only its close neighbourhood ⇒ wiggly boundary (overfit). Small γ ⇒ smooth (underfit). Tune C and γ together on a log grid.

### Mercer's condition
A valid kernel gives a positive semi-definite Gram matrix. Kernels also power **kernel PCA**, **Gaussian processes** and kernel ridge regression. Cost: the n×n kernel matrix — doesn't scale to millions (use random Fourier features / Nyström approximation).""",
  code="""
import numpy as np
from sklearn.datasets import make_moons
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

x, z = np.array([1.0, 2.0]), np.array([3.0, 1.0])
phi = lambda v: np.array([v[0] ** 2, np.sqrt(2) * v[0] * v[1], v[1] ** 2])      # explicit degree-2 map
print("explicit phi(x).phi(z) =", phi(x) @ phi(z), "  kernel (x.z)^2 =", (x @ z) ** 2)

X, y = make_moons(300, noise=0.2, random_state=0)
for kern in ("linear", "poly", "rbf"):
    print(f"{kern:6s} train accuracy {SVC(kernel=kern, degree=3).fit(X, y).score(X, y):.3f}")
gs = GridSearchCV(SVC(kernel="rbf"), {"C": [0.1, 1, 10, 100], "gamma": [0.01, 0.1, 1, 10]}, cv=5).fit(X, y)
print("best", gs.best_params_, "CV", round(gs.best_score_, 3))
""",
  say=[("What is the kernel trick?",
        "\"Many algorithms, like the SVM dual, only use dot products between data points. A kernel function computes the dot product of the points in a high-dimensional feature space directly from the original inputs, so we get the power of that space — non-linear boundaries — without ever computing the mapping. The RBF kernel corresponds to an infinite-dimensional space.\"")]),

M("m-multiclass", "Multiclass, multi-label and multi-output classification", "Intermediate",
  "Multiclass picks one of many classes; multi-label assigns any number of tags; strategies like one-vs-rest adapt binary classifiers to these settings.",
  """|Setting|Example|Output layer / method|Loss|
|Binary|spam or not|1 sigmoid unit|binary cross-entropy|
|Multiclass (exclusive)|digit 0–9|softmax over K classes|categorical cross-entropy|
|Multi-label|movie genres (action AND comedy)|K independent sigmoids|binary cross-entropy per label|
|Multi-output regression|predict x and y coordinates|K linear units|MSE|
|Ordinal|ratings 1–5|cumulative thresholds or regression|ordinal losses|
|Hierarchical|product category tree|per-level classifiers|—|

### Adapting binary classifiers
- **One-vs-rest (OvR)**: K classifiers, each "class k vs all"; pick the most confident.
- **One-vs-one (OvO)**: K(K−1)/2 pairwise classifiers; vote (SVC default).
- **Multi-label**: binary relevance (one classifier per label) or classifier chains (use earlier labels as features).

### Metrics
Macro/micro/weighted F1, top-k accuracy; for multi-label: Hamming loss, subset accuracy, per-label F1.""",
  code="""
import numpy as np
from sklearn.datasets import load_digits, make_multilabel_classification
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, hamming_loss, top_k_accuracy_score

X, y = load_digits(return_X_y=True); Xtr, Xte, ytr, yte = train_test_split(X / 16, y, random_state=0)
for name, m in [("OvR", OneVsRestClassifier(LinearSVC(max_iter=5000))), ("OvO", OneVsOneClassifier(LinearSVC(max_iter=5000))), ("softmax", LogisticRegression(max_iter=2000))]:
    p = m.fit(Xtr, ytr).predict(Xte); print(f"{name:8s} macro-F1 {f1_score(yte, p, average='macro'):.3f}  classifiers: {len(getattr(m, 'estimators_', [1]))}")
sm = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
print("top-2 accuracy:", round(top_k_accuracy_score(yte, sm.predict_proba(Xte), k=2), 3))

Xm, Ym = make_multilabel_classification(500, 10, n_classes=4, random_state=0)
Xtr, Xte, Ytr, Yte = train_test_split(Xm, Ym, random_state=0)
P = MultiOutputClassifier(LogisticRegression(max_iter=1000)).fit(Xtr, Ytr).predict(Xte)
print("multi-label: Hamming loss", round(hamming_loss(Yte, P), 3), " micro-F1", round(f1_score(Yte, P, average='micro'), 3))
""",
  say=[("How would you change a neural network from multiclass to multi-label?",
        "\"Replace the softmax output with independent sigmoid units, one per label, and switch from categorical cross-entropy to binary cross-entropy summed over labels. At prediction time I apply a threshold per label — tuned on validation data — instead of taking the argmax.\"")]),

M("m-interpretability", "Model interpretability: feature importance, SHAP, partial dependence, LIME", "Intermediate",
  "Interpretability explains why a model predicts what it does — globally (which features matter) and locally (why this one customer was rejected). It builds trust, aids debugging and is often legally required.",
  """### Intrinsically interpretable models
Linear/logistic regression (coefficients), small decision trees, rule lists, GAMs (generalised additive models).

### Model-agnostic, global
- **Permutation importance**: drop in score when a feature is shuffled.
- **Partial dependence plots (PDP)**: average prediction as one feature varies. **ICE** curves: the same per individual.
- **Global surrogate**: fit a simple tree to mimic the complex model.

### Local explanations
- **SHAP** (SHapley Additive exPlanations): game-theory credit assignment; each feature's contribution sums to (prediction − average prediction). TreeSHAP is fast for tree ensembles.
- **LIME**: fit a simple model around one prediction using perturbed samples.
- **Counterfactuals**: "if income were ₹5k higher, the loan would be approved".
- Deep learning: saliency maps, Grad-CAM (CNNs), attention visualisation, integrated gradients.

### Cautions
Correlated features split credit unpredictably; explanations describe the model, not causality.""",
  code="""
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.inspection import partial_dependence, permutation_importance

data = load_diabetes(); X, y = data.data, data.target
gbr = GradientBoostingRegressor(random_state=0).fit(X, y)
pi = permutation_importance(gbr, X, y, n_repeats=5, random_state=0)
print("top features:", [str(data.feature_names[i]) for i in pi.importances_mean.argsort()[::-1][:3]])
pd_ = partial_dependence(gbr, X, [2], grid_resolution=5)
print("partial dependence on bmi:", pd_["average"][0].round(1))

# Exact Shapley values for one prediction (small feature set: brute force over coalitions)
from itertools import combinations
from math import factorial
feats = [2, 8, 3]; x0 = X[0]; base = X.mean(0)
def v(S):
    z = base.copy(); z[list(S)] = x0[list(S)]; return gbr.predict(z[None])[0]
phi = {}
for f in feats:
    others = [g for g in feats if g != f]; total = 0
    for r in range(len(others) + 1):
        for S in combinations(others, r):
            w = factorial(len(S)) * factorial(len(feats) - len(S) - 1) / factorial(len(feats))
            total += w * (v(S + (f,)) - v(S))
    phi[data.feature_names[f]] = round(float(total), 1)
print("Shapley contributions for patient 0:", phi, " sum:", round(sum(phi.values()), 1), "= f(x) - f(baseline) =", round(float(v(tuple(feats)) - v(())), 1))
""",
  say=[("How would you explain a credit-rejection decision made by a gradient-boosted model?",
        "\"With local explanations: SHAP values show how much each feature pushed this applicant's score up or down relative to the average applicant — say high debt-to-income and a recent default. I'd also generate a counterfactual, like what change would flip the decision, and check the explanation for proxies of protected attributes. Globally, permutation importance and partial dependence plots show what the model relies on overall.\"")]),
]
