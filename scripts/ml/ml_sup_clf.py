"""Extra classification concepts for the Supervised learning tab."""
from ml_util import M

SUP_CLF = [
M("m-linear-classification", "Linear classifiers and decision boundaries (perceptron, logistic, linear SVM)", "Basic",
  "A linear classifier separates classes with a straight line (a hyperplane in more dimensions): it computes a score w·x + b and predicts by its sign. Perceptron, logistic regression, linear SVM and LDA all draw such a line; they differ only in how they choose it.",
  """### The shared model
score(x) = w·x + b → predict class 1 if score > 0, else class 0. The **decision boundary** is the set w·x + b = 0: a line in 2-D, a plane in 3-D, a hyperplane in general. **w** is perpendicular to the boundary; |score| / ‖w‖ is the distance from it.

### How each method picks w (the loss)
|Method|Loss on one example (y = ±1, m = y·score)|What it cares about|
|Perceptron|max(0, −m)|only mistakes; stops at any separating line|
|Logistic regression|log(1 + e^(−m))|every point, smoothly; gives probabilities|
|Linear SVM|max(0, 1 − m) (hinge) + ½‖w‖²|the widest margin; only support vectors matter|
|LDA|Gaussian classes with shared covariance|class means and spread|

### Linear separability
If some line separates the classes perfectly, the perceptron is guaranteed to find one; logistic regression without regularisation then pushes weights to infinity. If no line can (XOR, circles), add features (x², x·y), use kernels, trees or neural networks.

### Multiclass
One-vs-rest (one line per class) or softmax (one score per class, pick the largest): the regions are still bounded by straight lines.

### Why use them
Fast to train and predict, work well with many features (text), easy to inspect (one weight per feature), hard to overfit with regularisation. Scale the features first.""",
  demo="perceptron",
  code="""
import numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import Perceptron, LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
X = StandardScaler().fit_transform(X[y < 2][:, 2:]); y = y[y < 2]      # setosa vs versicolor, petal length & width
for name, m in [("perceptron", Perceptron(random_state=0)), ("logistic", LogisticRegression()),
                ("linear SVM", LinearSVC()), ("LDA", LinearDiscriminantAnalysis())]:
    m.fit(X, y); w, b = m.coef_[0], m.intercept_[0]
    print(f"{name:10s} boundary: {w[0]:+.2f}*x1 {w[1]:+.2f}*x2 {b:+.2f} = 0 | accuracy {m.score(X, y):.2f}")
""",
  say=[("What do logistic regression, a linear SVM and the perceptron have in common, and how do they differ?",
        "\"All three predict with the sign of a linear score w·x + b, so their decision boundaries are hyperplanes. They differ in the loss used to choose w: the perceptron only reacts to mistakes, logistic regression minimises log loss over all points and gives probabilities, and the SVM minimises hinge loss with L2 regularisation, which maximises the margin and depends only on the support vectors.\"")],
  see=["m-logistic-regression", "m-perceptron", "m-svm", "m-separability", "m-discriminant-analysis"]),

M("m-naive-bayes", "Naive Bayes classifiers (Gaussian, multinomial, Bernoulli)", "Basic",
  "Naive Bayes applies Bayes' rule to pick the most probable class, assuming features are independent given the class. The assumption is usually wrong, but the classifier is fast, needs little data and is very strong for text.",
  """### The rule
P(class | x₁…xₙ) ∝ P(class) · Π P(xᵢ | class). Predict the class with the largest value. Work with **log probabilities** (sum instead of product) to avoid underflow.

### Three flavours (how P(xᵢ | class) is modelled)
- **Gaussian NB**: continuous features, a normal distribution per feature per class (mean and variance).
- **Multinomial NB**: word counts; P(word | class) = (count + α) / (total + α·V). The default for text.
- **Bernoulli NB**: word present / absent; also penalises missing words.

### Laplace (additive) smoothing
α = 1 adds one imaginary count to every word, so a word never seen in a class doesn't make the whole probability 0.

### Why "naive" works
Classification only needs the right class to score highest, not accurate probabilities. Dependent features (e.g. "free" and "prize") double-count evidence, which makes probabilities over-confident but often keeps the ranking right.

### Pros and cons
Training is one pass of counting; works with tiny data and huge vocabularies; a great baseline for spam, sentiment and topic classification. Probabilities are poorly calibrated; correlated or continuous non-normal features hurt; usually beaten by logistic regression with enough data.""",
  code="""
import numpy as np
from sklearn.datasets import load_wine
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_val_score

X, y = load_wine(return_X_y=True)
print("Gaussian NB on wine, 5-fold accuracy:", cross_val_score(GaussianNB(), X, y, cv=5).mean().round(3))

texts = ["win a free prize now", "free entry win cash", "are we meeting for lunch", "see you at lunch tomorrow", "claim your free cash prize"]
labels = [1, 1, 0, 0, 1]
vec = CountVectorizer(); Xt = vec.fit_transform(texts)
nb = MultinomialNB(alpha=1.0).fit(Xt, labels)
for msg in ["free lunch tomorrow", "win cash now"]:
    print(f"{msg!r}: P(spam) = {nb.predict_proba(vec.transform([msg]))[0, 1]:.2f}")
words = vec.get_feature_names_out(); ratio = nb.feature_log_prob_[1] - nb.feature_log_prob_[0]
print("most spam-like words:", list(words[np.argsort(-ratio)[:4]]))
""",
  say=[("Why is Naive Bayes called naive, and why does it still work?",
        "\"It assumes all features are conditionally independent given the class, so the likelihood is just a product of per-feature probabilities. That's rarely true, but classification only needs the correct class to get the highest score. The errors from correlated features mostly inflate confidence rather than flip the ranking, so it works well, especially for text, where it's fast and needs little data.\"")],
  see=["m-bayes", "m-text-classification", "m-logistic-regression"]),

M("m-discriminant-analysis", "Discriminant analysis classifiers: LDA and QDA", "Intermediate",
  "Discriminant analysis models each class as a Gaussian cloud and classifies a point to the class whose cloud makes it most likely. With one shared covariance (LDA) the boundaries are straight; with a covariance per class (QDA) they are curved.",
  """### Generative classification
Model P(x | class) as a multivariate normal N(μₖ, Σₖ) and the prior P(class) = πₖ; classify with Bayes' rule: pick the k maximising log πₖ + log N(x; μₖ, Σₖ).

### LDA (Linear Discriminant Analysis)
All classes share one covariance Σ. The quadratic terms cancel, so the score is **linear** in x: δₖ(x) = xᵀΣ⁻¹μₖ − ½μₖᵀΣ⁻¹μₖ + log πₖ. Parameters: K means + one covariance → stable with little data.

### QDA (Quadratic Discriminant Analysis)
Each class has its own Σₖ → **quadratic (curved)** boundaries. Many more parameters (K·d(d+1)/2) → needs more data; use `reg_param` to shrink covariances.

### LDA also reduces dimensions
Projecting onto the K − 1 directions that best separate the class means (Fisher's discriminant) is the supervised alternative to PCA (see the unsupervised tab).

### Compared with logistic regression
Both give linear boundaries. LDA is more efficient when the Gaussian assumption roughly holds and with small data; logistic regression makes fewer assumptions and is more robust to outliers and non-normal features. Scaling doesn't change LDA's predictions.""",
  code="""
import numpy as np
from sklearn.datasets import load_wine, make_gaussian_quantiles
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA, QuadraticDiscriminantAnalysis as QDA
from sklearn.model_selection import cross_val_score

X, y = load_wine(return_X_y=True)
for name, m in [("LDA", LDA()), ("QDA", QDA(reg_param=0.1))]:
    print(f"wine {name}: 5-fold accuracy {cross_val_score(m, X, y, cv=5).mean():.3f}")

Xc, yc = make_gaussian_quantiles(n_samples=400, n_features=2, n_classes=2, random_state=0)   # inner vs outer ring
for name, m in [("LDA", LDA()), ("QDA", QDA())]:
    print(f"rings {name}: 5-fold accuracy {cross_val_score(m, Xc, yc, cv=5).mean():.3f}")
lda = LDA().fit(X, y); print("class means (first 3 features):", lda.means_[:, :3].round(2).tolist())
""",
  say=[("When would you choose LDA over logistic regression?",
        "\"When the data is small and the classes look roughly Gaussian with similar spread, LDA uses that structure and estimates fewer, more stable parameters, so it can beat logistic regression. It also gives a natural low-dimensional projection. With lots of data, outliers or clearly non-normal features, logistic regression is safer because it models only the boundary, not the full distribution. If class spreads differ, QDA gives curved boundaries.\"")],
  see=["m-lda", "m-linear-classification", "m-bayes", "m-distributions"]),

M("m-threshold-calibration", "Decision thresholds and probability calibration", "Intermediate",
  "A classifier's probability is only half the decision: you also choose the threshold above which to say 'yes', and you check that a predicted 70% really happens about 70% of the time (calibration).",
  """### The threshold is a business decision
predict 1 if p ≥ t. The default t = 0.5 is only right if both mistakes cost the same and the probabilities are calibrated. Lower t → more positives caught (recall ↑), more false alarms (precision ↓).

### Choosing t
- **From costs**: with calibrated probabilities, flag when p · cost(miss) > (1 − p) · cost(false alarm) ⇒ t = C_FP / (C_FP + C_FN).
- **From a constraint**: the lowest t that keeps precision ≥ 90%, or the t giving recall ≥ 95%.
- **From capacity**: flag only the top 200 cases a team can review per day.
Choose t on validation data (or out-of-fold predictions), never on the test set.

### Calibration
A model is calibrated if, among all cases with p ≈ 0.7, about 70% are positive. Check with a **reliability diagram** (bin predictions, compare mean p with the observed rate) and the **Brier score** = mean (p − y)².
- Logistic regression is usually well calibrated.
- Naive Bayes and boosted trees tend to be over-confident; SVM scores and random forests are squashed towards the middle.

### Fixing calibration
**Platt scaling** (fit a logistic curve on the scores) or **isotonic regression** (a monotone step function, needs more data), via `CalibratedClassifierCV` on held-out folds. Calibration changes the probabilities, not (much) the ranking, so AUC stays about the same.""",
  demo="roc",
  code="""
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.naive_bayes import GaussianNB
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import brier_score_loss, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True); y = 1 - y                       # 1 = malignant
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, stratify=y, random_state=0)
raw = GaussianNB().fit(Xtr, ytr); cal = CalibratedClassifierCV(GaussianNB(), method="isotonic", cv=5).fit(Xtr, ytr)
for name, m in [("raw NB", raw), ("calibrated NB", cal)]:
    p = m.predict_proba(Xte)[:, 1]
    print(f"{name:14s} Brier {brier_score_loss(yte, p):.3f}  AUC {roc_auc_score(yte, p):.3f}")
p = cal.predict_proba(Xte)[:, 1]
for t in (0.1, 0.3, 0.5, 0.7):
    f = p >= t; print(f"threshold {t}: recall {recall_score(yte, f):.2f} precision {precision_score(yte, f):.2f}")
print("cost-based threshold if a miss costs 10x a false alarm:", round(1 / (1 + 10), 3))
""",
  say=[("Your model outputs probabilities. How do you pick the threshold?",
        "\"From the cost of each error or an operating constraint, not 0.5 by default. If probabilities are calibrated, the cost-optimal threshold is C_FP / (C_FP + C_FN), so if missing fraud costs ten times a false alarm I'd flag above about 0.09. Otherwise I pick the threshold on validation data that meets a precision or recall target or the team's review capacity, then check calibration with a reliability curve and fix it with Platt or isotonic scaling if needed.\"")],
  see=["m-metrics-clf", "m-imbalance", "m-logistic-regression"]),

M("m-choosing-classifier", "Choosing a classifier: comparing algorithms fairly", "Intermediate",
  "No classifier is best everywhere. The practical way to choose is to compare a few model families on the same cross-validation folds, with the right metric, and weigh accuracy against speed, interpretability and how much data you have.",
  """### A fair comparison
1. Fix the metric that matches the goal (AUC, F1, recall at fixed precision, log loss).
2. Put preprocessing inside a **pipeline** so every fold is leak-free.
3. Use the **same** (repeated, stratified) CV folds for every model; report mean ± spread.
4. Start with baselines: majority class, logistic regression.
5. Tune each serious candidate a little; don't compare a tuned model with a default one.

### Rules of thumb
|Situation|Good first choices|
|Small tabular data|logistic regression, LDA, Naive Bayes, small trees|
|Medium/large tabular data|gradient boosting (XGBoost/LightGBM), random forest|
|Text (bag of words)|linear models: logistic regression, linear SVM, multinomial NB|
|Images, audio, raw sequences|neural networks (CNNs, transformers), usually pre-trained|
|Must explain every decision|logistic regression / scorecard, shallow tree|
|Need probabilities|logistic regression or calibrated models|
|Very low latency / tiny device|linear models, small trees|

### Beyond the score
Differences smaller than the spread across folds are noise. Also weigh training/prediction time, memory, robustness to missing values and drift, ease of explaining to stakeholders, and maintenance cost. A simple model that is 0.5% worse is often the right production choice.""",
  code="""
import time
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.svm import SVC

X, y = load_breast_cancer(return_X_y=True)
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=0)
models = {"majority": DummyClassifier(), "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
          "naive Bayes": GaussianNB(), "LDA": LinearDiscriminantAnalysis(), "kNN": make_pipeline(StandardScaler(), KNeighborsClassifier(7)),
          "tree": DecisionTreeClassifier(max_depth=4, random_state=0), "random forest": RandomForestClassifier(300, random_state=0, n_jobs=-1),
          "boosting": HistGradientBoostingClassifier(random_state=0), "SVM RBF": make_pipeline(StandardScaler(), SVC())}
for name, m in models.items():
    t0 = time.time(); s = cross_val_score(m, X, y, cv=cv, scoring="roc_auc")      # SVC is scored via its decision_function
    print(f"{name:14s} AUC {s.mean():.3f} ± {s.std():.3f}  ({time.time() - t0:.1f}s)")
""",
  say=[("How do you decide which classification algorithm to use for a new problem?",
        "\"I start from the data type and constraints: for tabular data, a logistic regression baseline and gradient boosting; for text, linear models on TF-IDF; for images or audio, a pre-trained network. Then I compare a few candidates on the same stratified cross-validation folds inside leak-free pipelines, using the metric that matches the business goal, and look at the spread, not just the mean. If the difference is within noise, I prefer the simpler, faster, more explainable model.\"")],
  see=["m-train-val-test", "m-metrics-clf", "m-hyperparams", "m-gradient-boosting"]),
]
