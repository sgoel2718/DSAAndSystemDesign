"""Beginner lessons: Supervised learning."""
from lesson_util import L

L("m-linear-regression",
  "Linear regression predicts a number as a weighted sum of the inputs plus a constant, choosing the weights that make squared errors smallest.",
  """It's the simplest useful model, it's still used everywhere (prices, demand, risk scores), and most bigger models are built from the same pieces: weights, a bias, a loss and an optimiser.""",
  """With one input it's a straight line: **ŷ = w × x + b**.

- **w** (weight, slope): how much ŷ changes when x goes up by 1.
- **b** (bias, intercept): ŷ when x is 0.

With many inputs: **ŷ = w₁x₁ + w₂x₂ + … + b**. Each weight says how much that feature pushes the prediction, holding the others fixed.

Training picks w and b to minimise the **mean squared error** (MSE), the average of (prediction − truth)². There's a direct formula (least squares), or gradient descent can find it step by step.""",
  [("Fit a line by hand",
    """Data (x, y): (1, 2), (2, 4), (3, 5). Mean x = 2, mean y = 3.67. Slope w = Σ(x − x̄)(y − ȳ) / Σ(x − x̄)² = ((−1)(−1.67) + 0 + (1)(1.33)) / (1 + 0 + 1) = 3 / 2 = **1.5**. Intercept b = 3.67 − 1.5 × 2 = **0.67**. Line: ŷ = 1.5x + 0.67."""),
   ("Use it",
    """For x = 4: ŷ = 1.5 × 4 + 0.67 = **6.67**."""),
   ("Read the weights",
    """A house-price model with weight 0.05 for size (lakhs per sq ft) and −2 for age (lakhs per year): each extra 100 sq ft adds 5 lakhs; each year older removes 2 lakhs.""")],
  ("A model is ŷ = 20 + 3 × hours. What does it predict for 5 hours, and what does the 3 mean?",
   "20 + 15 = 35. The 3 means each extra hour adds 3 to the prediction."),
  [("Weight / coefficient", "how much one feature moves the prediction"),
   ("Bias / intercept", "the prediction when all features are 0"),
   ("Least squares", "choosing weights that minimise the sum of squared errors"),
   ("Residual", "truth minus prediction for one example")],
  """The hand example in scikit-learn (same answer: 1.5 and 0.67), then a multi-feature model.""",
  r'''import numpy as np
from sklearn.linear_model import LinearRegression

x = np.array([[1], [2], [3]]); y = np.array([2, 4, 5])
m = LinearRegression().fit(x, y)
print("w =", m.coef_.round(2), "b =", round(m.intercept_, 2))      # w = [1.5]  b = 0.67
print("prediction for x=4:", m.predict([[4]]).round(2))            # [6.67]

X = np.array([[1200, 5], [1500, 2], [800, 10], [2000, 1]])        # size, age
price = np.array([60, 80, 30, 110])
m2 = LinearRegression().fit(X, price)
print("per sq ft:", m2.coef_[0].round(3), " per year of age:", m2.coef_[1].round(2))''',
  [("What does linear regression minimise?", "The mean squared error between predictions and true values."),
   ("If the weight for 'age' is −2, what happens when age goes up by 1?", "The prediction drops by 2, other features held fixed.")])

L("m-logistic-regression",
  "Logistic regression turns a weighted sum into a probability with the sigmoid curve, for yes/no (or multi-class) classification.",
  """It's the standard first model for classification (spam, default, churn): fast, gives probabilities, and its weights are explainable. Despite the name it classifies, it doesn't predict numbers.""",
  """1. Compute a score like linear regression: **z = w·x + b** (any number, −∞ to +∞).
2. Squash it into a probability with the **sigmoid**: **p = 1 / (1 + e^(−z))**. Large positive z → p near 1; z = 0 → p = 0.5; large negative z → p near 0.
3. Predict "yes" if p ≥ 0.5 (or another threshold).

Training minimises **cross-entropy (log loss)**: it punishes being confidently wrong. For more than two classes, **softmax** turns one score per class into probabilities that add up to 1.""",
  [("Compute a probability",
    """Weights: w = 2 for "number of links", b = −3. An email with 2 links: z = 2 × 2 − 3 = 1, p = 1 / (1 + e^(−1)) = **0.73** → spam. With 1 link: z = −1, p = **0.27** → not spam."""),
   ("Log loss intuition",
    """True answer yes. Predicting 0.9 costs −log(0.9) = **0.11**. Predicting 0.1 costs −log(0.1) = **2.30**. Confident and wrong is punished about 20 times more.""")],
  ("With z = 0, what probability does the sigmoid give, and what does the model predict at threshold 0.5?",
   "p = 0.5, exactly on the boundary; by convention it predicts 'yes' (p ≥ 0.5)."),
  [("Sigmoid", "the S-shaped curve that maps any number into 0–1"),
   ("Log loss / cross-entropy", "the loss that punishes confident wrong probabilities"),
   ("Softmax", "turns several scores into probabilities that sum to 1"),
   ("Odds", "p / (1 − p); logistic weights change the log of the odds linearly")],
  """The sigmoid by hand, then scikit-learn's logistic regression on real data with probabilities.""",
  r'''import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sigmoid = lambda z: 1 / (1 + np.exp(-z))
print(sigmoid(np.array([-1, 0, 1])).round(2))         # [0.27 0.5  0.73]

X, y = load_breast_cancer(return_X_y=True)
m = make_pipeline(StandardScaler(), LogisticRegression()).fit(X, y)
print(m.predict_proba(X[:3]).round(3))                # [P(class 0), P(class 1)] for 3 patients
print(m.predict(X[:3]))                               # the class with the higher probability''',
  [("Why not use linear regression for yes/no?", "Its outputs aren't limited to 0–1 and it's badly hurt by extreme points; logistic gives proper probabilities."),
   ("What does softmax do?", "Turns one score per class into probabilities that add up to 1.")])

L("m-multiclass",
  "Multiclass picks one of many classes, multi-label gives any number of tags, and one-vs-rest lets yes/no models handle both.",
  """Real tasks rarely have just two answers: a ticket goes to one of 12 teams, a photo can be "beach" and "sunset" at once. Knowing which setting you're in decides the output layer, the loss and the metric.""",
  """- **Binary**: two classes (spam / not spam).
- **Multiclass**: one answer from several (digit 0–9). Probabilities over classes sum to 1 (softmax).
- **Multi-label**: each example can have **several** labels at once (a movie is "action" and "comedy"). Each label gets its own yes/no probability (sigmoid per label).
- **Multi-output**: several separate targets at once (predict both price and delivery days).

**One-vs-rest (OvR)**: train one yes/no model per class ("is it a 3, or not?") and pick the most confident. **One-vs-one**: one model per pair of classes, then vote.""",
  [("Multiclass with softmax",
    """Scores for cat, dog, bird: 2.0, 1.0, 0.1. Softmax: e² = 7.39, e¹ = 2.72, e^0.1 = 1.11, total 11.22 → **0.66, 0.24, 0.10**. Predict cat."""),
   ("Multi-label with sigmoids",
    """Tags for one photo: beach 0.92, sunset 0.81, city 0.05. With threshold 0.5 the photo gets **beach and sunset**.""")],
  ("A news article can belong to sport, politics and business at the same time. Multiclass or multi-label?",
   "Multi-label: one sigmoid (yes/no) per topic, not one softmax."),
  [("One-vs-rest", "one binary model per class against all others"),
   ("Multi-label", "each example can have several labels"),
   ("Macro average", "a metric averaged equally over classes")],
  """Multiclass on handwritten digits, and multi-label with a separate yes/no per tag.""",
  r'''import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

X, y = load_digits(return_X_y=True)                  # 10 classes: digits 0-9
m = LogisticRegression(max_iter=3000).fit(X, y)
print("multiclass prediction:", m.predict(X[:5]), "probabilities sum to", m.predict_proba(X[:1]).sum())

tags = np.column_stack([y % 2 == 0, y > 5]).astype(int)   # two tags at once: 'even' and 'big'
ml = OneVsRestClassifier(LogisticRegression(max_iter=3000)).fit(X, tags)
print("multi-label for 3 digits:", ml.predict(X[:3]), "true digits:", y[:3])''',
  [("Softmax or sigmoids for multi-label?", "Sigmoids: one independent yes/no per label."),
   ("How many models does one-vs-rest train for 10 classes?", "10.")])

L("m-knn",
  "k-nearest neighbours labels a new point by the majority vote of the k most similar training examples.",
  """It's the most intuitive classifier ("you are like your neighbours"), it needs no training, and it introduces ideas you'll need everywhere: distance, feature scaling and the effect of a hyperparameter on overfitting.""",
  """1. Store all training examples.
2. For a new point, compute its **distance** to every training point (usually straight-line, Euclidean).
3. Take the **k** closest.
4. **Classification**: majority vote. **Regression**: average their values.

Choosing k: small k (1) follows every noisy point → overfits. Large k smooths too much → underfits. Pick k with cross-validation.

**Scale features first**: if income is in lakhs and age in years, income dominates the distance.""",
  [("k = 3 by hand",
    """Training points: A (1, 1), A (1, 2), B (5, 5), B (6, 5), A (2, 1). New point (2, 2). Distances: 1.41, 1.0, 4.24, 5.0, 1.0. The 3 nearest are A, A, A → **A**."""),
   ("Why scaling matters",
    """Customers (age, income): (25, 900000) and (60, 910000). Unscaled distance ≈ 10,000, almost all from income; the 35-year age gap is invisible. After scaling both to similar ranges, age counts again.""")],
  ("Neighbours' labels for k = 5 are: spam, ham, spam, ham, spam. Prediction?",
   "Spam (3 votes to 2)."),
  [("Distance", "how far apart two examples are"),
   ("k", "how many neighbours vote"),
   ("Lazy learner", "a model that stores the data and does the work at prediction time"),
   ("Feature scaling", "putting features on similar ranges")],
  """kNN with and without scaling, and how k changes the score.""",
  r'''from sklearn.datasets import load_wine
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score

X, y = load_wine(return_X_y=True)          # features on very different scales
print("no scaling :", cross_val_score(KNeighborsClassifier(5), X, y, cv=5).mean().round(3))
for k in [1, 5, 15, 50]:
    m = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    print(f"scaled k={k:2d}:", cross_val_score(m, X, y, cv=5).mean().round(3))''',
  [("Why is kNN slow at prediction time?", "It compares the new point with every stored example."),
   ("What happens with k = 1?", "It copies the single nearest example, following noise: high variance, overfitting.")])

L("m-decision-tree",
  "A decision tree asks a series of yes/no questions about the features, each splitting the data into purer groups, until a leaf gives the answer.",
  """Trees are easy to explain to anyone ("if income < 30k and missed payments > 2 then high risk"), handle mixed data without scaling, and they are the building block of random forests and gradient boosting, the strongest models on tables.""",
  """1. At the top (root), try every feature and every threshold.
2. Pick the question that makes the two resulting groups **purest** (most of one class each), measured by **Gini impurity** or **entropy**.
3. Repeat inside each group.
4. Stop at a maximum depth, a minimum group size, or when a group is pure. Each final group (a **leaf**) predicts its majority class (or the average, for regression).

Grown fully, a tree memorises the data, so limit depth or **prune** it.""",
  [("Gini impurity",
    """Gini = 1 − Σ pᵢ². A group with 5 yes and 5 no: 1 − (0.25 + 0.25) = **0.5** (most mixed). A group with 9 yes, 1 no: 1 − (0.81 + 0.01) = **0.18**. Pure group: **0**."""),
   ("Choose a split",
    """10 loans, 5 default. Split on "income < 30k": left 4 rows (4 default) → Gini 0; right 6 rows (1 default) → Gini 1 − (1/36 + 25/36) = 0.28. Weighted: 0.4 × 0 + 0.6 × 0.28 = **0.17**, down from 0.5. A good split.""")],
  ("A leaf has 3 cats and 1 dog. What does it predict and what is its Gini impurity?",
   "Cat. Gini = 1 − (0.75² + 0.25²) = 1 − 0.625 = 0.375."),
  [("Root / node / leaf", "first question / any question / final answer box"),
   ("Gini impurity", "how mixed a group is; 0 means pure"),
   ("Information gain", "how much a split reduces entropy"),
   ("Pruning", "cutting back branches to stop overfitting")],
  """A small tree printed as readable rules, and the effect of limiting depth.""",
  r'''from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import cross_val_score

iris = load_iris()
tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(iris.data, iris.target)
print(export_text(tree, feature_names=list(iris.feature_names)))   # the learned questions

for depth in [1, 3, None]:                                          # None = grow until pure
    t = DecisionTreeClassifier(max_depth=depth, random_state=0)
    print("depth", depth, cross_val_score(t, iris.data, iris.target, cv=5).mean().round(3))''',
  [("Do decision trees need feature scaling?", "No; splits compare one feature with a threshold, so the scale doesn't matter."),
   ("How do you stop a tree overfitting?", "Limit depth, require a minimum number of samples per leaf, or prune.")])

L("m-bootstrap-bagging",
  "Bagging trains many models on random resamples of the data and averages them, which makes predictions much more stable.",
  """Single decision trees change a lot if the data changes a little (high variance). Bagging fixes this cheaply, and it's the idea behind random forests.""",
  """- A **bootstrap sample** is drawn from n rows **with replacement**: some rows appear twice, some not at all (about 63% of rows appear on average).
- **Bagging** = **b**ootstrap **agg**regat**ing**: train one model on each bootstrap sample, then **average** (regression) or **vote** (classification).

Each model makes different mistakes; averaging cancels much of the randomness, lowering variance without raising bias. Rows left out of a model's sample (**out-of-bag**) give a free validation score.""",
  [("Draw a bootstrap sample",
    """Rows 1–5. Random draws with replacement: 2, 5, 2, 1, 4. Row 2 appears twice, row 3 is left out (out-of-bag for this model)."""),
   ("Averaging helps",
    """Three trees predict a house price: 52, 61, 55 lakhs. Bagged prediction: **56**. If each tree's error is random, the average is closer to the truth than a typical single tree.""")],
  ("Five bagged classifiers vote: yes, no, yes, yes, no. What is the bagged prediction?",
   "Yes (3 votes to 2)."),
  [("Bootstrap", "sampling with replacement from the data"),
   ("Bagging", "training on bootstrap samples and averaging"),
   ("Out-of-bag (OOB)", "rows a model didn't see, used to score it")],
  """One tree versus 100 bagged trees on the same data.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True)
one = DecisionTreeClassifier(random_state=0)
bag = BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, oob_score=True, random_state=0)
print("one tree   :", cross_val_score(one, X, y, cv=5).mean().round(3))
print("100 bagged :", cross_val_score(bag, X, y, cv=5).mean().round(3))
print("OOB score  :", round(bag.fit(X, y).oob_score_, 3))''',
  [("Does bagging mainly reduce bias or variance?", "Variance."),
   ("Why is sampling done with replacement?", "So each model gets a different, same-sized sample of the data.")])

L("m-random-forest",
  "A random forest is many decision trees trained on resampled data, where each split only looks at a random subset of features; their votes are averaged.",
  """Random forests are one of the most reliable models for tables: strong accuracy with almost no tuning, little overfitting, and built-in feature importance. They're a great second model after a simple baseline.""",
  """Random forest = bagging + one extra trick:

1. Each tree trains on a bootstrap sample of the rows.
2. At **every split**, the tree may only consider a **random subset of features** (often √(number of features)).
3. Predictions are averaged (regression) or voted (classification).

Why the extra trick? If one feature is very strong, every bagged tree would split on it first and the trees would look alike. Random feature subsets make the trees **different (decorrelated)**, so averaging cancels more error.""",
  [("Feature subsets",
    """16 features, so each split looks at √16 = **4** random features. Tree 1's first split might choose between income, age, city, tenure; tree 2 between loans, age, gender, balance."""),
   ("Feature importance",
    """Each time a feature is used for a split, record how much it reduced impurity. Summed over all trees: income 0.42, missed payments 0.31, age 0.08 … → income matters most.""")],
  ("Why might 500 trees not overfit more than 100 trees in a random forest?",
   "Adding trees just averages more predictions, which reduces variance; it doesn't make individual trees more complex."),
  [("n_estimators", "number of trees"),
   ("max_features", "how many features each split may consider"),
   ("Decorrelated", "trees that make different mistakes"),
   ("Feature importance", "how much each feature reduced impurity overall")],
  """A random forest with its most important features.""",
  r'''import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

data = load_breast_cancer()
rf = RandomForestClassifier(n_estimators=300, max_features="sqrt", random_state=0)
print("CV accuracy:", cross_val_score(rf, data.data, data.target, cv=5).mean().round(3))

rf.fit(data.data, data.target)
top = np.argsort(rf.feature_importances_)[::-1][:3]                 # three biggest
for i in top:
    print(f"{data.feature_names[i]:25s} {rf.feature_importances_[i]:.3f}")''',
  [("What is the difference between bagging and a random forest?", "A random forest also restricts each split to a random subset of features."),
   ("Name one hyperparameter of a random forest.", "n_estimators, max_depth, max_features or min_samples_leaf.")])

L("m-voting-stacking",
  "Combining different models often beats the best single one: voting averages them, stacking trains a small model to combine them.",
  """Different models make different mistakes. Kaggle winners and many production systems combine models to gain the last few points of accuracy.""",
  """- **Hard voting**: each model votes for a class; the majority wins.
- **Soft voting**: average the predicted probabilities; usually better.
- **Weighted averaging**: give better models a larger weight.
- **Stacking**: train base models, then train a **meta-model** on their predictions to learn how to combine them. The base predictions must be made on data the base models didn't train on (use cross-validation), or the meta-model learns from overfit numbers.
- **Blending**: like stacking but using a single held-out set.""",
  [("Soft voting by hand",
    """P(spam) from three models: 0.9, 0.4, 0.45. Hard voting: yes, no, no → **no**. Soft voting: average 0.58 → **yes**. The confident model's strength counts."""),
   ("Stacking intuition",
    """The meta-model might learn "trust the forest on large values but the linear model on small ones", something a simple average can't do.""")],
  ("Models give probabilities 0.6, 0.7 and 0.2 with weights 1, 1, 2. What is the weighted soft vote?",
   "(0.6 + 0.7 + 2 × 0.2) / 4 = 1.7 / 4 = 0.425."),
  [("Base model", "one of the models being combined"),
   ("Meta-model", "the model that learns how to combine base predictions"),
   ("Soft voting", "averaging probabilities")],
  """Three different models, then soft voting and stacking over them.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import VotingClassifier, StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True)
base = [("lr", make_pipeline(StandardScaler(), LogisticRegression())),
        ("knn", make_pipeline(StandardScaler(), KNeighborsClassifier())),
        ("rf", RandomForestClassifier(random_state=0))]
for name, m in base + [("soft vote", VotingClassifier(base, voting="soft")),
                       ("stacking", StackingClassifier(base, final_estimator=LogisticRegression()))]:
    print(f"{name:9s}", cross_val_score(m, X, y, cv=5).mean().round(3))''',
  [("Why do ensembles help?", "Different models' errors partly cancel when combined."),
   ("Why must stacking use out-of-fold predictions?", "Predictions on the models' own training data are overconfident, so the meta-model would learn the wrong combination.")])

L("m-adaboost",
  "Boosting builds a strong model from many weak ones trained one after another, each focusing on the examples the previous ones got wrong.",
  """Boosting is the idea behind the most successful models for tabular data (XGBoost, LightGBM). AdaBoost is the clearest version to understand it.""",
  """AdaBoost, step by step:

1. Give every training example the same weight.
2. Train a **weak learner** (usually a "stump", a tree with one split).
3. Increase the weights of the examples it got **wrong**, decrease the others.
4. Train the next stump on the re-weighted data, so it focuses on the hard cases.
5. Repeat. Each stump gets a say (α) based on its accuracy; the final prediction is the **weighted vote**.

Bagging trains models **in parallel** to reduce variance; boosting trains them **in sequence** to reduce bias.""",
  [("Re-weighting",
    """10 examples, each weight 0.1. Stump 1 misclassifies 3. Its error is 0.3, so α = ½ ln((1 − 0.3)/0.3) ≈ **0.42**. The 3 mistakes get their weights multiplied by e^0.42 ≈ 1.53; the 7 correct ones by e^−0.42 ≈ 0.66; then all are rescaled to sum to 1."""),
   ("Final vote",
    """Stumps with α = 0.42, 0.65, 0.30 say yes, no, yes. Total for yes = 0.72, for no = 0.65 → **yes**.""")],
  ("A weak learner has error 0.5. How much say (α) does it get?",
   "α = ½ ln(0.5/0.5) = 0: it's no better than a coin flip, so it gets no vote."),
  [("Weak learner", "a model only slightly better than guessing, like a one-split tree"),
   ("Stump", "a decision tree with a single split"),
   ("α (alpha)", "how much each weak learner's vote counts")],
  """One stump versus AdaBoost with 200 stumps.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True)
stump = DecisionTreeClassifier(max_depth=1)
ada = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=200, random_state=0)
print("one stump :", cross_val_score(stump, X, y, cv=5).mean().round(3))
print("AdaBoost  :", cross_val_score(ada, X, y, cv=5).mean().round(3))''',
  [("Bagging trains models in parallel; how does boosting train them?", "In sequence, each correcting the previous ones."),
   ("Which examples get more weight in the next round?", "The ones the current model misclassified.")])

L("m-gradient-boosting",
  "Gradient boosting adds small trees one at a time, each one trained to fix the remaining errors of the trees before it.",
  """XGBoost, LightGBM and CatBoost (all gradient boosting) win most competitions and run in many companies on tabular data: credit risk, pricing, ranking, fraud. You will be asked how they work.""",
  """For regression with squared error:

1. Start with a simple prediction for everyone: the average.
2. Compute each example's **residual**: truth − current prediction.
3. Fit a small tree to predict those residuals.
4. Add that tree's output, scaled by a **learning rate** (e.g. 0.1), to the prediction.
5. Repeat for hundreds of trees.

"Gradient" because the residual is the negative gradient of the squared-error loss; with other losses (log loss for classification) the same recipe uses that loss's gradient.

The libraries add speed and tricks: **XGBoost** (regularised, fast), **LightGBM** (very fast on big data), **CatBoost** (handles categorical features well). Key settings: number of trees, learning rate, tree depth, and **early stopping** on a validation set.""",
  [("Two rounds by hand",
    """True prices: 50, 70, 90. Start: predict the mean **70** for all. Residuals: −20, 0, +20. Tree 1 learns those residuals exactly; learning rate 0.1 → new predictions 68, 70, 72. New residuals: −18, 0, +18. Tree 2 closes 10% more of the gap, and so on."""),
   ("Why a small learning rate?",
    """Taking only 10% of each correction makes progress slower but more careful, so it generalises better; you compensate with more trees.""")],
  ("Current prediction 100, truth 120, learning rate 0.1, and the new tree predicts the residual exactly. What is the new prediction?",
   "Residual = 20, so 100 + 0.1 × 20 = 102."),
  [("Residual", "truth minus the current prediction"),
   ("Learning rate (shrinkage)", "how much of each new tree's correction is added"),
   ("Early stopping", "stop adding trees when the validation score stops improving"),
   ("XGBoost / LightGBM / CatBoost", "fast, popular gradient boosting libraries")],
  """Gradient boosting written by hand in a few lines (to see the idea), then scikit-learn's fast version.""",
  r'''import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.datasets import make_regression
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score

X, y = make_regression(n_samples=500, n_features=5, noise=10, random_state=0)
pred = np.full(len(y), y.mean())                 # step 1: start from the average
for _ in range(100):
    resid = y - pred                              # step 2: what is still wrong
    tree = DecisionTreeRegressor(max_depth=3).fit(X, resid)   # step 3: learn the errors
    pred += 0.1 * tree.predict(X)                 # step 4: add a small correction
print("hand-made boosting training RMSE:", np.sqrt(np.mean((y - pred) ** 2)).round(2))

hgb = HistGradientBoostingRegressor(learning_rate=0.1, max_iter=300, early_stopping=True)
print("library R² (CV):", cross_val_score(hgb, X, y, cv=5).mean().round(3))''',
  [("What does each new tree in gradient boosting predict?", "The residual errors (negative gradients) of the current ensemble."),
   ("If you lower the learning rate, what else should you usually increase?", "The number of trees.")])

L("m-svm",
  "A support vector machine finds the boundary that separates the classes with the widest possible gap; only the closest points decide it.",
  """SVMs are strong on small and medium datasets with many features (text, genetics), and the idea of a "maximum margin" shows up again in deep learning losses.""",
  """Many lines can separate two classes. The SVM picks the one with the **largest margin**: the widest street between the classes with no points inside.

- The points touching the edge of the street are the **support vectors**; move any other point and the boundary doesn't change.
- Real data overlaps, so a **soft margin** allows some points inside the street or on the wrong side, with a penalty. **C** controls it: large C = few violations allowed (narrow street, may overfit); small C = wider street, more violations (smoother).
- Scale the features first: the margin is measured in distance.""",
  [("Margin by hand",
    """Class A at x = 1 and x = 2; class B at x = 6 and x = 7, on a number line. The best boundary is halfway between the closest points 2 and 6: **x = 4**, margin 2 on each side. The support vectors are 2 and 6; the points 1 and 7 don't matter."""),
   ("Effect of C",
    """With one noisy B point at x = 3, a large C squeezes the boundary to about 2.5 to classify it correctly; a small C keeps the boundary near 4 and accepts one mistake, which generalises better.""")],
  ("If you delete a point that is not a support vector, does the SVM boundary change?",
   "No; only support vectors define the boundary."),
  [("Margin", "the gap between the boundary and the closest points"),
   ("Support vector", "a training point on the edge of the margin"),
   ("Soft margin", "allowing some points to violate the margin"),
   ("C", "penalty for violations; large C fits the training data more tightly")],
  """A linear SVM on scaled data, the number of support vectors, and the effect of C.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True)
for C in [0.01, 1, 100]:
    m = make_pipeline(StandardScaler(), SVC(kernel="linear", C=C))
    print(f"C={C:<6} CV accuracy {cross_val_score(m, X, y, cv=5).mean():.3f}", end="  ")
    print("support vectors:", m.fit(X, y)[-1].n_support_.sum())''',
  [("Which points define an SVM's boundary?", "The support vectors, the points closest to it."),
   ("What does a very large C risk?", "Overfitting: the boundary bends to classify noisy training points.")])

L("m-kernels",
  "The kernel trick lets an SVM draw curved boundaries by measuring similarity as if the data were in a higher dimension, without ever computing that dimension.",
  """Data is often not separable by a straight line. Kernels make linear methods non-linear cheaply, and the idea of "similarity functions" appears again in Gaussian processes and attention.""",
  """Idea: add new features so that a straight line in the bigger space becomes a curve in the original space. Points on a number line at −2, −1 (class A), 0 (class B), 1, 2 (class A)... can't be split by one threshold. Add x²: now B is at height 0 and A at 1 and 4, and a horizontal line separates them.

Computing all those extra features can be expensive or infinite. The SVM only needs **dot products** (similarities) between pairs of points, and a **kernel** computes that similarity directly:
- **Polynomial kernel**: (x·z + 1)^d.
- **RBF (Gaussian) kernel**: exp(−γ ‖x − z‖²): near 1 for close points, near 0 for far ones. **γ** sets how quickly similarity fades; large γ = very wiggly boundary.""",
  [("RBF similarity by hand",
    """γ = 0.5. Points 1 unit apart: exp(−0.5 × 1) = **0.61**. 3 units apart: exp(−0.5 × 9) = **0.011**. Far points barely influence each other."""),
   ("Tune two settings",
    """With RBF you tune C (penalty) and γ (wiggliness) together, e.g. a grid of C ∈ {0.1, 1, 10} and γ ∈ {0.01, 0.1, 1}.""")],
  ("Two identical points: what is their RBF kernel value?",
   "exp(0) = 1, the maximum similarity."),
  [("Kernel", "a function giving the similarity of two points"),
   ("Kernel trick", "using similarities instead of explicitly building extra features"),
   ("RBF / Gaussian kernel", "similarity that decreases with distance"),
   ("γ (gamma)", "how fast RBF similarity fades with distance")],
  """Two moons: a linear SVM struggles, an RBF SVM fits the curve.""",
  r'''from sklearn.datasets import make_moons
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score

X, y = make_moons(n_samples=400, noise=0.2, random_state=0)
for name, m in [("linear", SVC(kernel="linear")), ("poly d=3", SVC(kernel="poly", degree=3)),
                ("rbf", SVC(kernel="rbf", gamma=1, C=1))]:
    print(f"{name:9s}", cross_val_score(m, X, y, cv=5).mean().round(3))''',
  [("What does the kernel trick avoid computing?", "The explicit high-dimensional features; it only computes pairwise similarities."),
   ("What does a very large γ do with an RBF SVM?", "Makes each point's influence very local, so the boundary becomes very wiggly and overfits.")])

L("m-interpretability",
  "Interpretability explains why a model predicts what it does: which features matter overall, and why one specific case got its answer.",
  """Banks must explain loan rejections, doctors won't trust a black box, and you need explanations to debug a model (it might rely on a leaky feature). Interviewers ask how you'd explain a model to a business stakeholder.""",
  """Two levels:

- **Global**: what matters across all predictions. **Permutation importance**: shuffle one feature's column and see how much the score drops; a big drop = important. **Partial dependence**: how the average prediction changes as one feature changes.
- **Local**: why this one prediction. **SHAP values** split a prediction into contributions: base value + each feature's push up or down = the prediction. **LIME** fits a small simple model around the one case.

Simple models (linear, small trees) are interpretable by themselves; complex ones need these tools.""",
  [("Permutation importance by hand",
    """Model accuracy 0.90. Shuffle income → 0.72 (drop 0.18). Shuffle city → 0.89 (drop 0.01). Income matters a lot; city hardly at all."""),
   ("SHAP for one loan",
    """Average predicted default risk 10%. This applicant: income low +12%, missed payments +8%, long employment −5% → **25%**. Each number is that feature's contribution.""")],
  ("Shuffling a feature's column doesn't change the accuracy at all. What does that suggest?",
   "The model doesn't rely on that feature; it could probably be removed."),
  [("Global explanation", "how the model behaves overall"),
   ("Local explanation", "why one particular prediction was made"),
   ("Permutation importance", "score drop when a feature is shuffled"),
   ("SHAP value", "one feature's contribution to one prediction")],
  """Permutation importance on held-out data (it works for any model).""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

data = load_breast_cancer()
Xtr, Xte, ytr, yte = train_test_split(data.data, data.target, random_state=0)
rf = RandomForestClassifier(random_state=0).fit(Xtr, ytr)

r = permutation_importance(rf, Xte, yte, n_repeats=10, random_state=0)   # shuffle each column 10 times
for i in r.importances_mean.argsort()[::-1][:4]:
    print(f"{data.feature_names[i]:22s} accuracy drop {r.importances_mean[i]:.3f}")''',
  [("Why compute permutation importance on validation data?", "On training data it measures what the model memorised, not what helps on new data."),
   ("What do SHAP values of one prediction add up to?", "The prediction minus the average (base) prediction.")])
