"""Module 1 (part A): AI/ML overview, principles, data processing, features, metrics, generalisation."""
from ml_util import M

FOUND = [
M("m-ai-overview", "What are AI, ML, deep learning and generative AI?", "Basic",
  "AI is the goal (machines doing tasks that need intelligence); ML is the main way we get there (learning from data); deep learning is ML with large neural networks; generative AI creates new content.",
  """### The nested circles
**AI ⊃ Machine Learning ⊃ Deep Learning ⊃ Generative AI / LLMs** (roughly).
- **Artificial Intelligence**: any technique that makes computers act intelligently — includes hand-written rules, search (chess engines, route planning), logic and ML.
- **Machine Learning**: programs that improve with data instead of explicit rules. *Traditional programming*: rules + data → answers. *ML*: data + answers → rules (a model).
- **Deep Learning**: ML with multi-layer neural networks that learn features automatically from raw pixels, audio or text.
- **Generative AI**: models that produce new text, images, audio, code (GPT, Llama, Claude, Stable Diffusion).
- **Agentic AI**: LLM-based systems that plan, call tools and take multi-step actions toward a goal.

### A short history
1950 Turing test → 1956 Dartmouth "AI" → 1958 perceptron → 1970s/80s AI winters, expert systems → 1986 backpropagation → 1990s SVMs, random forests → 2012 **AlexNet** wins ImageNet (deep learning boom) → 2014 GANs → 2017 **Transformer** ("Attention is all you need") → 2018 BERT, GPT → 2020 GPT-3 → 2022 ChatGPT, diffusion models → 2023+ open LLMs (Llama), multimodal models, RAG and agents.

### When to use ML (and when not)
Use ML when rules are too complex to write (recognising faces), patterns change (fraud), or you need personalisation at scale. Don't use it when a simple rule works, there's no data, or mistakes are unacceptable and must be explained exactly.""",
  analogy="Traditional programming is giving a cook a recipe. Machine learning is giving the cook hundreds of dishes and their tastes and letting them work out the recipe.",
  example="Gmail spam filtering (classification), Netflix recommendations, Google Maps arrival times (regression), Face ID (deep learning), ChatGPT and Claude (generative AI).",
  code="""
# Rules vs learning: a tiny spam detector both ways
emails = ["win cash now", "lunch at 1?", "cash prize waiting", "project update", "you win a prize", "notes from meeting"]
labels = [1, 0, 1, 0, 1, 0]

rule_based = [int(any(w in e for w in ("win", "cash"))) for e in emails]       # hand-written rule
print("rule-based:", rule_based)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
vec = CountVectorizer(); X = vec.fit_transform(emails)
model = LogisticRegression().fit(X, labels)                                       # learned rule
print("learned:   ", model.predict(X).tolist())
weights = sorted(zip(model.coef_[0], vec.get_feature_names_out()), reverse=True)[:3]
print("words the model learned are spammy:", [w for _, w in weights])
""",
  say=[("How would you explain the difference between AI, ML and deep learning to a non-technical person?",
        "\"AI is the broad goal of making machines do smart things. Machine learning is the most successful way to do it today: instead of writing rules, we show the computer lots of examples and it learns the pattern. Deep learning is a kind of machine learning that uses large neural networks and shines on images, speech and language — it's what powers ChatGPT and face unlock.\"")]),

M("m-ml-types", "Types of learning: supervised, unsupervised, semi-supervised, self-supervised, reinforcement", "Basic",
  "Learning types differ by what feedback the model gets: labels (supervised), none (unsupervised), a few labels (semi-supervised), labels made from the data itself (self-supervised) or rewards (reinforcement).",
  """|Type|Data|Goal|Examples|Algorithms|
|Supervised|inputs + labels|predict label for new inputs|spam, price, diagnosis|linear/logistic regression, trees, SVM, neural nets|
|Unsupervised|inputs only|find structure|customer segments, anomalies, compression|k-means, DBSCAN, PCA, autoencoders|
|Semi-supervised|few labels + many unlabeled|use unlabeled data to help|medical images with few annotations|self-training, label propagation|
|Self-supervised|labels created from the data|learn representations|predict next word (GPT), masked word (BERT), contrastive images (SimCLR)|transformers, contrastive learning|
|Reinforcement|states, actions, rewards|maximise long-term reward|games, robotics, RLHF for chatbots|Q-learning, policy gradients, PPO|

### Supervised sub-types
- **Regression**: continuous target (price, temperature).
- **Classification**: categories — binary (spam/not), multiclass (digit 0–9), multi-label (several tags).
- Also ranking (search results), sequence labelling (NER), structured prediction.

### Other ways to slice it
- **Batch vs online learning** (all data at once vs streaming updates).
- **Instance-based** (kNN — memorises) vs **model-based** (learns parameters).
- **Parametric** (fixed number of parameters) vs **non-parametric** (grows with data).
- **Discriminative** (models P(y | x)) vs **generative** (models P(x, y) or P(x) — can create samples).""",
  code="""
from sklearn.datasets import make_blobs
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.semi_supervised import SelfTrainingClassifier
import numpy as np

X, y = make_blobs(n_samples=300, centers=3, random_state=42)
print("supervised accuracy:", LogisticRegression(max_iter=500).fit(X, y).score(X, y))

clusters = KMeans(3, n_init=10, random_state=0).fit_predict(X)            # no labels used
print("unsupervised cluster sizes:", np.bincount(clusters))

y_partial = y.copy(); rng = np.random.default_rng(0)
y_partial[rng.random(len(y)) < 0.95] = -1                                  # hide 95% of labels
semi = SelfTrainingClassifier(LogisticRegression(max_iter=500)).fit(X, y_partial)
print("labels used:", (y_partial != -1).sum(), " semi-supervised accuracy:", semi.score(X, y))
""",
  say=[("What is self-supervised learning and why is it important?",
        "\"The model creates its own labels from raw data — predicting the next word, a masked word, or whether two augmented images come from the same photo. It lets us pre-train on huge unlabeled datasets and then fine-tune with few labels. GPT and BERT are self-supervised; it's the reason foundation models exist.\"")]),

M("m-ml-principles", "Principles of ML: learning as optimisation, hypothesis space, inductive bias, no free lunch", "Basic",
  "A model is a function chosen from a family (hypothesis space) by minimising a loss on data, hoping it generalises to new data. Every algorithm makes assumptions (inductive bias).",
  """### The recipe behind every ML algorithm
1. **Model / hypothesis space**: a family of functions f(x; θ) — lines, trees, neural nets.
2. **Loss function**: how wrong a prediction is (MSE, cross-entropy).
3. **Optimiser**: how to search for the best θ (closed form, gradient descent, greedy splits).
4. **Data**: samples assumed i.i.d. from the same distribution as future data.
**Empirical risk minimisation**: choose θ that minimises average training loss (+ regularisation).

### Generalisation is the real goal
Doing well on training data is easy (memorise it); doing well on *unseen* data is what matters. Hence held-out test sets.

### Inductive bias
The assumptions that let a model generalise: linear models assume linear relationships; kNN assumes nearby points share labels; CNNs assume local patterns and translation invariance; transformers assume tokens can attend to each other.

### No Free Lunch theorem
No algorithm is best for every problem. You must try several and validate — and use domain knowledge.

### Occam's razor
Prefer the simplest model that explains the data well — simpler models generalise better and are easier to debug.

### Parameters vs hyperparameters
**Parameters** are learned (weights). **Hyperparameters** are set by you before training (learning rate, tree depth, k in kNN) and tuned with validation data.""",
  code="""
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.datasets import make_moons, make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# No free lunch: the best model depends on the data's shape
datasets = {"linear-ish": make_classification(400, 5, n_informative=3, random_state=0),
            "moons (curvy)": make_moons(400, noise=0.25, random_state=0)}
models = {"logistic": LogisticRegression(max_iter=1000), "kNN": KNeighborsClassifier(15), "tree": DecisionTreeClassifier(max_depth=5, random_state=0)}
for dname, (X, y) in datasets.items():
    print(dname, {m: float(round(cross_val_score(est, X, y, cv=5).mean(), 3)) for m, est in models.items()})
""",
  say=[("What is inductive bias? Give examples.",
        "\"It's the set of assumptions a learning algorithm uses to generalise beyond the training data. Linear regression assumes a linear relationship, kNN assumes similar inputs have similar outputs, CNNs assume local, translation-invariant patterns, and regularisation assumes simpler functions are more likely. Without some bias, learning from finite data is impossible.\"")]),

M("m-problem-formulation", "Problem formulation: turning a business problem into an ML problem", "Basic",
  "Before choosing a model, define exactly what to predict, from what inputs, how success is measured and what the baseline is. Most failed ML projects fail here.",
  """### Questions to answer first
1. **Business goal**: what decision will the prediction drive? (reduce churn, approve loans)
2. **Is ML needed?** Could a rule or SQL query do it?
3. **Target (label)**: what exactly is y, at what time? ("will cancel within 30 days" — not "cancelled ever").
4. **Task type**: regression, binary/multiclass/multi-label classification, ranking, clustering, forecasting, generation.
5. **Inputs available at prediction time**: only features known *before* the event (avoid leakage).
6. **Unit of prediction**: per user? per transaction? per day?
7. **Metric**: offline (F1, RMSE, AUC) tied to a business metric (revenue saved); what errors cost more — false positives or false negatives?
8. **Baseline**: majority class, last value, simple rule — your model must beat it.
9. **Constraints**: latency, interpretability, fairness, privacy, data volume, retraining frequency.

### Examples of formulation choices
|Business ask|Formulation|
|"Which customers will leave?"|binary classification: churn in next 30 days|
|"How many units will we sell?"|regression / time-series forecasting per store per day|
|"Show better products"|ranking / recommendation (learning to rank)|
|"Group our customers"|clustering, then profile clusters|
|"Detect machine failures"|anomaly detection (few failure labels) or classification|
|"Are these two questions duplicates?"|pairwise classification on question pairs (Siamese / cross-encoder)|""",
  code="""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score

# 'Will the customer churn?' -> imbalanced binary classification. Always compare to a baseline.
X, y = make_classification(5000, 10, weights=[0.9], random_state=1)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0)
for name, m in [("baseline: always 'stays'", DummyClassifier(strategy="most_frequent")), ("logistic regression", LogisticRegression(max_iter=1000))]:
    p = m.fit(Xtr, ytr).predict(Xte)
    print(f"{name:26s} accuracy={accuracy_score(yte, p):.3f}  F1(churn)={f1_score(yte, p, zero_division=0):.3f}")
""",
  say=[("You're asked to 'use ML to reduce customer churn'. How do you start?",
        "\"First clarify the decision: who gets a retention offer and at what cost. Then define the label precisely — say, cancels within the next 30 days — and the prediction time, so I only use features available then. Pick metrics that reflect the cost trade-off, like recall at a fixed budget of offers or expected profit, set a simple baseline, and check data availability and constraints. Only then start modelling.\"")]),

M("m-data-processing", "Data collection and cleaning: missing values, duplicates, outliers, types", "Basic",
  "Real data is messy. Cleaning — fixing types, duplicates, missing values, outliers and inconsistent labels — usually takes most of the project time and matters more than the model.",
  """### Sources of data
Databases (SQL), CSV/Excel, APIs, logs, sensors, **web scraping** (requests + BeautifulSoup, respecting robots.txt and terms), public datasets (Kaggle, UCI, Hugging Face Datasets), labelling tools.

### Cleaning checklist
1. **Types**: numbers stored as text, dates as strings → convert (`pd.to_numeric`, `pd.to_datetime`).
2. **Duplicates**: exact and near-duplicates (`drop_duplicates`) — duplicates across train and test inflate scores.
3. **Missing values**: understand *why* (MCAR — completely at random, MAR — at random given other features, MNAR — not at random). Options: drop rows/columns, impute mean/median/mode, group-wise imputation, KNN/iterative imputation, add a missing-indicator.
4. **Outliers**: detect (IQR, z-score, isolation forest), then decide — data error (fix/remove) or real rare event (keep; maybe cap/winsorise or log-transform).
5. **Inconsistent categories**: "Delhi", "delhi ", "New Delhi" → standardise text.
6. **Label noise**: check a sample of labels by hand.
7. **Units and scales**: mixed currencies, cm vs inches.

### Golden rules
Never modify raw data in place — keep a reproducible cleaning script. Fit imputers on training data only.""",
  code="""
import pandas as pd, numpy as np
from sklearn.impute import SimpleImputer, KNNImputer

raw = pd.DataFrame({
    "city": ["Delhi", "delhi ", "Mumbai", "Mumbai", "Pune", None],
    "age": ["34", "29", "n/a", "41", "41", "38"],
    "income": [52000, 48000, 61000, 9_900_000, 9_900_000, 58000],
})
df = raw.copy()
df["city"] = df["city"].str.strip().str.title()
df["age"] = pd.to_numeric(df["age"], errors="coerce")             # 'n/a' -> NaN
df = df.drop_duplicates()
q1, q3 = df["income"].quantile([0.25, 0.75]); cap = q3 + 1.5 * (q3 - q1)
df["income_capped"] = df["income"].clip(upper=cap)
df["age_missing"] = df["age"].isna().astype(int)
df["age"] = SimpleImputer(strategy="median").fit_transform(df[["age"]]).ravel()
df["city"] = df["city"].fillna("Unknown")
print(df)
print("KNN imputation example:", KNNImputer(n_neighbors=2).fit_transform([[1, 2], [np.nan, 3], [7, 6]]).round(2).tolist())
""",
  say=[("Your dataset has 30% missing values in an important column. What do you do?",
        "\"Find out why it's missing — if missingness depends on something, it's informative, so I add an is-missing indicator. Then impute: median or group-wise median for a baseline, or model-based imputation like KNN or iterative imputation, fitted on training data only. Tree models like XGBoost can also handle missing values natively. I'd compare options with cross-validation rather than guess.\"")]),

M("m-eda", "Exploratory data analysis (EDA) and visualisation", "Basic",
  "EDA is looking at the data before modelling: distributions, relationships, imbalance, quality problems and leakage. It guides every later decision.",
  """### A standard EDA routine
1. **Shape and types**: rows, columns, dtypes, memory (`df.info()`).
2. **Target**: distribution — class balance for classification, skew for regression.
3. **Univariate**: histograms/box plots for numeric features; bar charts for categories; summary stats (`describe`).
4. **Missing values and duplicates** per column.
5. **Bivariate**: each feature vs target (box plots per class, scatter, mean target per category).
6. **Correlations**: heatmap; spot redundant features and suspiciously perfect predictors (leakage!).
7. **Time**: trends and seasonality if there is a date.
8. **Segments**: does behaviour differ by region, device…?
9. Write down hypotheses and cleaning/feature ideas.

### Tools
Pandas + Matplotlib/Seaborn; automatic reports (ydata-profiling, Sweetviz); dimensionality reduction plots (PCA, t-SNE) for high-dimensional data.""",
  code="""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns, pandas as pd
from sklearn.datasets import load_breast_cancer

data = load_breast_cancer(as_frame=True); df = data.frame
print(df.shape, "| target balance:", df["target"].value_counts(normalize=True).round(2).to_dict())
print(df.iloc[:, :4].describe().T[["mean", "std", "min", "max"]].round(2))
corr = df.corr()["target"].drop("target").sort_values()
print("most negatively correlated with benign:", corr.head(3).round(2).to_dict())

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
sns.boxplot(data=df, x="target", y="mean radius", ax=ax[0]); ax[0].set_title("Radius by class (0 = malignant)")
sns.heatmap(df.iloc[:, :8].corr(), cmap="vlag", center=0, ax=ax[1]); ax[1].set_title("Feature correlations")
fig.tight_layout(); fig.savefig("eda.png", dpi=100); print("saved eda.png")
""",
  say=[("What do you look for in EDA before building a model?",
        "\"Target distribution and imbalance, missing values and duplicates, feature distributions and outliers, relationships between features and the target, correlated features, and any feature that's suspiciously predictive — usually leakage. If there's time, trends and seasonality. EDA tells me what cleaning, transformations and validation strategy I need.\"")]),

M("m-encoding", "Encoding categorical data: one-hot, ordinal, target, hashing, embeddings", "Basic",
  "Models need numbers. Categorical features are converted with one-hot encoding (no order), ordinal encoding (ordered), target encoding (high cardinality) or learned embeddings.",
  """|Method|How|Good for|Watch out|
|One-hot|one 0/1 column per category|nominal, low cardinality (colour, city with few values)|many columns for high cardinality; drop one for linear models (dummy trap)|
|Ordinal / label|map to 0, 1, 2… in order|ordered categories (low < medium < high); tree models|implies order for nominal data in linear models|
|Target (mean) encoding|replace category with mean target|high cardinality (zip codes, product ids)|leakage — compute out-of-fold with smoothing|
|Frequency / count|category → how often it appears|high cardinality|different categories may collide|
|Hashing trick|hash to a fixed number of columns|huge/unknown vocabularies, streaming|collisions; not invertible|
|Binary encoding|category index in binary bits|medium cardinality|less interpretable|
|Embeddings|learned dense vectors|deep learning, recommenders (user/item ids)|needs a neural net and data|

Always handle **unseen categories** at prediction time (`handle_unknown="ignore"`).""",
  code="""
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, TargetEncoder
df = pd.DataFrame({"size": ["S", "M", "L", "M", "S", "L"], "city": ["Pune", "Delhi", "Pune", "Agra", "Delhi", "Pune"], "bought": [0, 1, 1, 0, 0, 1]})

oh = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(df[["city"]])
print(oh.get_feature_names_out(), "\\n", oh.transform(pd.DataFrame({"city": ["Pune", "Mysore"]})))   # unseen -> all zeros
print("ordinal:", OrdinalEncoder(categories=[["S", "M", "L"]]).fit_transform(df[["size"]]).ravel())
te = TargetEncoder(target_type="binary", cv=3, random_state=0)                                 # out-of-fold encoding
print("target-encoded city:", te.fit_transform(df[["city"]], df["bought"]).ravel().round(2))
print(pd.get_dummies(df["city"], prefix="city", drop_first=True, dtype=int).head(3))
""",
  say=[("How do you encode a categorical feature with 50,000 unique values?",
        "\"One-hot would explode the dimensions, so I'd use target encoding computed out-of-fold with smoothing, frequency encoding, the hashing trick, or a learned embedding if I'm using a neural network. Tree libraries like CatBoost and LightGBM also handle high-cardinality categories natively. And I'd group rare categories into 'other'.\"")]),

M("m-feature-engineering", "Feature engineering and transformation", "Intermediate",
  "Feature engineering creates inputs that make patterns easy for the model to learn — ratios, date parts, aggregates, interactions and domain knowledge. It often beats switching models.",
  """### Common transformations
- **Mathematical**: log (skewed money/count data), square root, Box-Cox/Yeo-Johnson, powers.
- **Binning**: age → age bands; helps linear models capture non-linear effects.
- **Interactions / ratios**: price per square foot, debt-to-income, clicks/impressions (CTR).
- **Polynomial features**: x², x·y to let linear models fit curves.
- **Date/time**: year, month, day of week, hour, is_weekend, is_holiday, time since last event; **cyclical encoding** with sin/cos for hour and month (23:00 is close to 00:00).
- **Aggregates**: per-user averages, counts in the last 7 days, rolling statistics (careful to use only past data).
- **Lag features** for time series: yesterday's sales, last week's sales.
- **Text**: length, word counts, TF-IDF, embeddings. **Images**: CNN embeddings. **Geo**: distance to city centre, clustering of coordinates.
- **Domain features**: medical ratios, financial indicators.

### Principles
Create features available at prediction time only; validate every new feature with cross-validation; deep learning automates feature learning for images, audio and text, but tabular data still benefits from hand-crafted features.""",
  code="""
import numpy as np, pandas as pd
from sklearn.preprocessing import PolynomialFeatures, PowerTransformer
rng = np.random.default_rng(0)
df = pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=6, freq="7h"),
                   "price": [2.5e6, 4.0e6, 1.2e7, 3.1e6, 8.0e5, 5.5e6], "area_sqft": [900, 1200, 2600, 1000, 450, 1500],
                   "user": ["a", "b", "a", "a", "b", "c"]})
df["price_per_sqft"] = df["price"] / df["area_sqft"]
df["log_price"] = np.log1p(df["price"])
df["hour"] = df["timestamp"].dt.hour
df["hour_sin"], df["hour_cos"] = np.sin(2 * np.pi * df["hour"] / 24), np.cos(2 * np.pi * df["hour"] / 24)
df["dow"] = df["timestamp"].dt.dayofweek
df["user_listings_so_far"] = df.groupby("user").cumcount()            # uses only the past
print(df.drop(columns=["timestamp"]).round(2))
print(PolynomialFeatures(2, include_bias=False).fit([[1, 2]]).get_feature_names_out(["x", "y"]))
print("Yeo-Johnson skew fix:", PowerTransformer().fit_transform(df[["price"]]).ravel().round(2))
""",
  say=[("Why encode hour of day with sine and cosine?",
        "\"Because time is cyclical: as plain numbers, 23 and 0 look far apart though they're an hour apart. Mapping hour to sin and cos of 2-pi-hour over 24 puts the hours on a circle, so neighbouring hours are close and the model sees the wrap-around. The same applies to day of week and month.\"")]),

M("m-feature-selection", "Feature selection: filter, wrapper and embedded methods", "Intermediate",
  "Feature selection keeps the useful inputs and drops noisy or redundant ones, giving simpler, faster and often more accurate models.",
  """### Why select features
Less overfitting (curse of dimensionality), faster training and inference, cheaper data collection, easier explanations.

### Three families
|Family|How|Examples|Pros / cons|
|Filter|score each feature independently of the model|variance threshold, correlation, chi-square, ANOVA F-test, mutual information|fast; ignores interactions|
|Wrapper|search feature subsets by training models|forward selection, backward elimination, recursive feature elimination (RFE)|considers interactions; slow|
|Embedded|selection happens during training|Lasso (L1), tree feature importance, gradient boosting gain|good balance|

### Also
- **Permutation importance**: shuffle a feature on validation data and measure the drop — model-agnostic and honest.
- **SHAP values** for importance and direction.
- Remove one of each highly correlated pair.
- Do selection **inside cross-validation**, otherwise it leaks information and inflates scores.

### Selection vs extraction
Selection keeps a subset of original features (interpretable); **extraction** creates new combined features (PCA, autoencoders, embeddings).""",
  code="""
from sklearn.datasets import make_classification
from sklearn.feature_selection import VarianceThreshold, SelectKBest, mutual_info_classif, RFE, SelectFromModel
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

X, y = make_classification(600, 12, n_informative=4, n_redundant=2, shuffle=False, random_state=0)  # first 4 informative
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
print("filter (mutual info) keeps:", SelectKBest(mutual_info_classif, k=4).fit(Xtr, ytr).get_support(indices=True))
print("wrapper (RFE) keeps:      ", RFE(LogisticRegression(max_iter=1000), n_features_to_select=4).fit(Xtr, ytr).get_support(indices=True))
l1 = LogisticRegression(penalty="l1", C=0.05, solver="liblinear")
print("embedded (L1) keeps:      ", SelectFromModel(l1).fit(Xtr, ytr).get_support(indices=True))
rf = RandomForestClassifier(200, random_state=0).fit(Xtr, ytr)
pi = permutation_importance(rf, Xte, yte, n_repeats=10, random_state=0)
print("permutation importance top 4:", pi.importances_mean.argsort()[::-1][:4])
""",
  say=[("Why must feature selection be done inside cross-validation?",
        "\"If I select features using the whole dataset, the selection has already seen the validation folds' labels, so the cross-validation score is optimistically biased — this is a classic leak, especially with many features and few samples. Putting the selector inside a Pipeline means it's refit on each training fold only.\"")]),

M("m-feature-extraction", "Feature extraction for different data types", "Intermediate",
  "Feature extraction turns raw data — text, images, audio, signals — into numeric vectors a model can use, either with hand-crafted methods or learned embeddings.",
  """|Data|Classical features|Learned features|
|Tabular|ratios, aggregates, encodings|entity embeddings, autoencoders|
|Text|bag of words, n-grams, TF-IDF, counts|word2vec, sentence-transformer / BERT embeddings|
|Images|colour histograms, edges (Sobel, Canny), HOG, SIFT/ORB keypoints, texture (LBP)|CNN / ViT embeddings (penultimate layer)|
|Audio / speech|spectrogram, MFCCs, zero-crossing rate, pitch, energy|wav2vec 2.0, Whisper encoder embeddings|
|Signals / vibration|mean, RMS, kurtosis, peak-to-peak, FFT band energies|1-D CNN, autoencoder|
|Time series|lags, rolling stats, trend/seasonality decomposition|RNN/transformer encoders|
|Graphs|degree, PageRank, clustering coefficient|node2vec, graph neural networks|

**Dimensionality-reduction extraction**: PCA, LDA, autoencoders compress many features into a few informative ones.

**Transfer learning as feature extraction**: run data through a pretrained network and use its embeddings with a simple classifier — strong results with little data.""",
  code="""
import numpy as np
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer

# text -> TF-IDF features
docs = ["the battery life is great", "battery died fast", "great camera and screen"]
tf = TfidfVectorizer().fit(docs); print(tf.get_feature_names_out()[:6], tf.transform(docs).shape)

# vibration signal -> statistical + frequency features
rng = np.random.default_rng(0); fs = 2000; t = np.arange(0, 1, 1 / fs)
healthy = np.sin(2 * np.pi * 50 * t) + 0.2 * rng.normal(size=t.size)
faulty = healthy + 0.8 * (rng.random(t.size) < 0.01) * rng.normal(5, 1, t.size)       # impulsive spikes
def feats(x):
    spec = np.abs(np.fft.rfft(x)); f = np.fft.rfftfreq(x.size, 1 / fs)
    return {"rms": np.sqrt((x ** 2).mean()).round(3), "kurtosis": round(stats.kurtosis(x), 2),
            "peak2peak": np.ptp(x).round(2), "energy_>200Hz": spec[f > 200].sum().round(0)}
print("healthy:", feats(healthy)); print("faulty: ", feats(faulty))

# image -> colour histogram + gradient (edge) energy
img = rng.random((32, 32, 3))
hist = np.concatenate([np.histogram(img[..., c], bins=4, range=(0, 1))[0] for c in range(3)])
gy, gx = np.gradient(img.mean(axis=2)); print("colour hist:", hist, " edge energy:", np.hypot(gx, gy).mean().round(3))
""",
  say=[("How would you build features for detecting faulty bearings from vibration data?",
        "\"Window the signal and compute time-domain features — RMS, peak-to-peak, crest factor, kurtosis, which jumps with impacts — and frequency-domain features from the FFT, especially energy around the bearing's characteristic fault frequencies. Then train an anomaly detector on healthy windows, or a classifier if I have fault labels. A 1-D CNN or autoencoder on raw windows is the deep-learning alternative.\"")]),

M("m-real-world-data", "Representing real-world data: tabular, text, images, audio, time series, graphs", "Basic",
  "Every kind of data must become tensors (arrays of numbers) with a sensible shape. Knowing the standard shapes lets you plug any data into any model.",
  """|Data|Typical representation|Shape|
|Tabular row|feature vector (scaled numbers + encoded categories)|(n_samples, n_features)|
|Grayscale image|pixel intensities 0–255 (scaled to 0–1)|(n, H, W) or (n, 1, H, W)|
|Colour image|RGB channels|PyTorch (n, 3, H, W); TensorFlow (n, H, W, 3)|
|Video|frames of images|(n, T, C, H, W)|
|Text|token ids → embeddings|(n, sequence_length) → (n, L, d_model)|
|Audio|waveform samples (16 kHz) or spectrogram|(n, samples) or (n, freq_bins, time)|
|Time series|windows of past values (+ features)|(n, timesteps, features)|
|Graph|node features + adjacency matrix / edge list|(n_nodes, f), (2, n_edges)|
|Sets / point clouds|unordered vectors|(n, points, 3)|

### Practical issues of real data
Class imbalance, missing values, noise and label errors, mixed types, high cardinality, concept drift over time, privacy (PII must be removed or anonymised), and bias in how data was collected.""",
  code="""
import numpy as np
rng = np.random.default_rng(0)
tabular = rng.normal(size=(32, 10))                       # 32 rows, 10 features
images_torch = rng.random((32, 3, 64, 64)).astype("float32")   # N, C, H, W
images_tf = images_torch.transpose(0, 2, 3, 1)             # N, H, W, C
vocab = {"<pad>": 0, "i": 1, "love": 2, "ml": 3}
tokens = np.array([[vocab[w] for w in "i love ml".split()] + [0, 0]])   # padded token ids
audio = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000)              # 1 second at 16 kHz
series = np.arange(100.0); window = 7
X_ts = np.stack([series[i:i + window] for i in range(len(series) - window)]); y_ts = series[window:]
edges = np.array([[0, 1, 1, 2], [1, 0, 2, 1]])                          # graph edge list
for name, a in [("tabular", tabular), ("images (torch)", images_torch), ("images (tf)", images_tf), ("tokens", tokens), ("audio", audio), ("time-series X", X_ts), ("graph edges", edges)]:
    print(f"{name:15s} {a.shape}")
""",
  say=[("How would you represent a time series for a supervised model?",
        "\"With a sliding window: each sample is the last k observations plus calendar and external features, and the target is the next value or next h values. For tree models I flatten it into lag and rolling features; for an LSTM or transformer I keep it 3-D — samples, timesteps, features. And I always split by time, never randomly.\"")]),

M("m-imbalance", "Class imbalance: resampling, class weights, thresholds, metrics", "Intermediate",
  "When one class is rare (fraud, disease, churn), accuracy is misleading and models ignore the rare class. Fix it with the right metrics, class weights, resampling and threshold tuning.",
  """### Symptoms
99% accuracy by predicting "not fraud" every time. Look at **recall, precision, F1, PR-AUC** instead.

### Remedies
1. **Metrics**: precision/recall/F1 for the rare class, PR-AUC (better than ROC-AUC under heavy imbalance), cost-based metrics.
2. **Class weights**: penalise mistakes on the rare class more (`class_weight="balanced"`, `scale_pos_weight` in XGBoost, weighted loss in PyTorch).
3. **Resampling** (on the training set only!): random undersampling of the majority, random oversampling of the minority, **SMOTE** (synthesises new minority points between neighbours), ADASYN.
4. **Threshold tuning**: the default 0.5 is arbitrary; choose the threshold that maximises F1 or meets a recall target on validation data.
5. **Collect more rare examples** or treat as **anomaly detection**.
6. Use **stratified** splits so each fold keeps the class ratio.
7. **Focal loss** in deep learning down-weights easy examples.""",
  code="""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, recall_score, precision_score, average_precision_score, precision_recall_curve

X, y = make_classification(20000, 10, n_informative=4, weights=[0.98], class_sep=1.5, flip_y=0.005, random_state=3)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0)
def report(name, m, thr=0.5):
    p = m.predict_proba(Xte)[:, 1]; pred = (p >= thr).astype(int)
    print(f"{name:22s} P={precision_score(yte, pred, zero_division=0):.2f} R={recall_score(yte, pred):.2f} F1={f1_score(yte, pred):.2f} PR-AUC={average_precision_score(yte, p):.2f}")
plain = LogisticRegression(max_iter=1000).fit(Xtr, ytr); report("plain", plain)
weighted = LogisticRegression(max_iter=1000, class_weight="balanced").fit(Xtr, ytr); report("class_weight=balanced", weighted)

rng = np.random.default_rng(0); pos = np.where(ytr == 1)[0]                     # simple random oversampling
idx = np.concatenate([np.arange(len(ytr)), rng.choice(pos, len(pos) * 10)])
report("oversampled x10", LogisticRegression(max_iter=1000).fit(Xtr[idx], ytr[idx]))

pr, rc, th = precision_recall_curve(ytr, plain.predict_proba(Xtr)[:, 1])          # tune threshold on training/validation
best = th[np.argmax(2 * pr[:-1] * rc[:-1] / (pr[:-1] + rc[:-1] + 1e-9))]
report(f"plain, threshold={best:.2f}", plain, best)
""",
  say=[("You have 1% fraud. How do you build and evaluate the model?",
        "\"Stratified splits, and metrics focused on the fraud class — precision, recall and PR-AUC, ideally a cost-based metric. In training I'd use class weights or resampling on the training folds only, gradient-boosted trees as a strong baseline, and then tune the decision threshold on validation data to match the business trade-off — for example the recall we need at a precision the review team can handle.\"")]),

M("m-train-val-test", "Train / validation / test splits and cross-validation", "Basic",
  "Split data so you train on one part, tune on another and report on a final untouched part. Cross-validation reuses data efficiently for reliable estimates.",
  """### The three sets
- **Training set** (~60–80%): fit model parameters.
- **Validation set** (~10–20%): choose hyperparameters, features, models, thresholds; early stopping.
- **Test set** (~10–20%): touch **once** at the end for an unbiased estimate. If you tune on it, it stops being a test.

### Cross-validation (CV)
- **k-fold**: split into k folds; train on k − 1, validate on 1, rotate; average scores (k = 5 or 10).
- **Stratified k-fold**: keeps class proportions — default for classification.
- **Group k-fold**: keeps all rows of one patient/user in the same fold (otherwise leakage).
- **Time-series split**: always train on the past and validate on the future (expanding or sliding window).
- **Leave-one-out**: k = n; for tiny datasets.
- **Nested CV**: inner loop tunes hyperparameters, outer loop estimates performance.

### Choosing split sizes
Large datasets (millions): 98/1/1 is fine. Small datasets: use CV. Make the validation/test distribution match what you'll see in production.""",
  code="""
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, TimeSeriesSplit, GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X, y = load_breast_cancer(return_X_y=True)
X_trval, X_test, y_trval, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
X_tr, X_val, y_tr, y_val = train_test_split(X_trval, y_trval, test_size=0.25, stratify=y_trval, random_state=42)
print("train/val/test sizes:", len(X_tr), len(X_val), len(X_test))

model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
scores = cross_val_score(model, X_trval, y_trval, cv=StratifiedKFold(5, shuffle=True, random_state=0))
print("5-fold CV accuracy: %.3f ± %.3f" % (scores.mean(), scores.std()))
print("final test accuracy:", round(model.fit(X_trval, y_trval).score(X_test, y_test), 3))

for tr, va in TimeSeriesSplit(n_splits=3).split(np.arange(12)):
    print("time split  train", tr.tolist(), "-> validate", va.tolist())
groups = np.repeat(np.arange(4), 3)
print("group k-fold validation groups:", [sorted(set(groups[va].tolist())) for _, va in GroupKFold(4).split(np.zeros(12), groups=groups)])
""",
  say=[("Why do we need a separate validation set if we have a test set?",
        "\"Because every decision made by looking at a dataset — hyperparameters, features, model choice, early stopping — fits that dataset a little. If I tune on the test set, the reported score is optimistically biased. The validation set or cross-validation absorbs that tuning, and the test set is used once at the end for an honest estimate.\"")]),

M("m-leakage", "Data leakage: the silent killer of ML projects", "Intermediate",
  "Leakage is when information that won't be available at prediction time sneaks into training, giving great offline scores and terrible real-world performance.",
  """### Common forms
- **Target leakage**: a feature is a consequence of the target — "account_closed_date" when predicting churn; "treatment given" when predicting diagnosis.
- **Train–test contamination**: scaling, imputing, selecting features or oversampling on the full dataset before splitting.
- **Temporal leakage**: random splits on time series, using future data (e.g. rolling means that include the current/future value).
- **Group leakage**: the same patient, user or near-duplicate image appears in both train and test.
- **Duplicate rows** across splits.
- **Leaky IDs**: row order or IDs correlated with the label.

### How to spot it
Scores that look too good to be true; one feature dominates importance; performance collapses in production.

### How to prevent it
Split first; put all preprocessing in a `Pipeline`; for each feature ask "would I know this at prediction time?"; use time-based and group-based splits; deduplicate.""",
  code="""
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
X = rng.normal(size=(100, 5000)); y = rng.integers(0, 2, 100)       # pure noise: true accuracy is 50%

X_leaky = SelectKBest(f_classif, k=20).fit_transform(X, y)          # WRONG: selection saw all labels
print("leaky CV accuracy:  ", cross_val_score(LogisticRegression(max_iter=1000), X_leaky, y, cv=5).mean().round(2))
pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000))   # RIGHT
print("correct CV accuracy:", cross_val_score(pipe, X, y, cv=5).mean().round(2))
""",
  say=[("Your model has 99% validation accuracy but fails in production. What happened?",
        "\"My first suspect is leakage: a feature that encodes the label or is only known after the event, preprocessing fitted on all data, random splits on time-ordered data, or the same entities in train and validation. I'd check feature importances for a suspicious dominant feature, re-split by time and group, and verify every feature is available at prediction time. Then I'd also look for training-serving skew and data drift.\"")]),

M("m-overfitting", "Overfitting, underfitting, generalisation and the bias–variance trade-off", "Basic",
  "Underfitting = too simple to capture the pattern (high bias). Overfitting = memorising noise in the training data (high variance). The goal is the sweet spot that generalises.",
  """### Diagnose with train vs validation error
|Train error|Validation error|Diagnosis|Fix|
|high|high|underfitting (high bias)|more complex model, more/better features, train longer, less regularisation|
|low|high|overfitting (high variance)|more data, regularisation, simpler model, dropout, early stopping, augmentation, feature selection|
|low|low (close)|good fit|ship it (after the test set)|

### Bias–variance decomposition
Expected error = **bias²** (systematic error from wrong assumptions) + **variance** (sensitivity to the particular training sample) + **irreducible noise**. Increasing complexity lowers bias and raises variance.

### Learning curves
Plot train and validation score vs training-set size: a big persistent gap ⇒ variance (more data helps); both low and converged ⇒ bias (more data won't help).

### Validation curves
Score vs a hyperparameter (tree depth, polynomial degree, regularisation strength).

### Modern twist: double descent
Very over-parameterised deep nets can generalise well again past the interpolation point — but regularisation and validation still matter.""",
  demo="overfit",
  code="""
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error

rng = np.random.default_rng(1)
x = np.sort(rng.uniform(0, 1, 30)); y = np.sin(2 * np.pi * x) + rng.normal(0, 0.2, 30)
xv = np.sort(rng.uniform(0, 1, 200)); yv = np.sin(2 * np.pi * xv) + rng.normal(0, 0.2, 200)
for deg in (1, 4, 15):
    m = make_pipeline(PolynomialFeatures(deg), LinearRegression()).fit(x[:, None], y)
    tr, va = mean_squared_error(y, m.predict(x[:, None])), mean_squared_error(yv, m.predict(xv[:, None]))
    label = "underfit" if deg == 1 else "good" if deg == 4 else "overfit"
    print(f"degree {deg:2d}: train MSE {tr:.3f}  validation MSE {va:.3f}  -> {label}")
m = make_pipeline(PolynomialFeatures(15), Ridge(alpha=1e-3)).fit(x[:, None], y)
print("degree 15 + Ridge: validation MSE", round(mean_squared_error(yv, m.predict(xv[:, None])), 3), "(regularisation tames it)")
""",
  say=[("How do you know if your model is overfitting, and what do you do?",
        "\"Training performance is much better than validation performance, and the gap grows with more training. Fixes: get more data or augment it, add regularisation — L1/L2, dropout, early stopping — reduce model complexity or features, and use cross-validation to tune. A learning curve tells me whether more data would actually help.\"")]),

M("m-regularization", "Regularisation techniques (overview)", "Intermediate",
  "Regularisation is anything that discourages a model from fitting noise: penalties on weights, early stopping, dropout, data augmentation, simpler models and ensembles.",
  """|Technique|Where|Idea|
|L2 (Ridge, weight decay)|linear models, neural nets|penalty λΣw²: small, spread-out weights|
|L1 (Lasso)|linear models|penalty λΣ|w|: sparse weights, feature selection|
|Elastic Net|linear models|mix of L1 and L2|
|Early stopping|iterative training (GD, boosting, neural nets)|stop when validation loss stops improving|
|Dropout|neural nets|randomly zero activations during training ⇒ no co-adaptation|
|Data augmentation|images, audio, text|create varied copies ⇒ more effective data|
|Pruning / max depth / min samples per leaf|trees|limit tree complexity|
|Shrinkage (learning rate) and subsampling|boosting|smaller, noisier steps|
|Batch normalisation, label smoothing|neural nets|mild regularising effects|
|Ensembling (bagging)|any|averaging reduces variance|
|Noise injection, mixup, cutout|neural nets|robustness|

λ (or C = 1/λ in scikit-learn's logistic regression and SVM) is a hyperparameter — tune it with cross-validation. Bayesian view: L2 = Gaussian prior on weights, L1 = Laplace prior (MAP estimation).""",
  code="""
import numpy as np
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV, LinearRegression
from sklearn.model_selection import cross_val_score
rng = np.random.default_rng(0)
X = rng.normal(size=(60, 40)); y = X[:, :3] @ np.array([3.0, -2, 1.5]) + rng.normal(0, 1, 60)   # 37 useless features
for name, m in [("plain OLS", LinearRegression()), ("RidgeCV", RidgeCV(alphas=np.logspace(-3, 3, 20))),
                ("LassoCV", LassoCV(cv=5, random_state=0)), ("ElasticNetCV", ElasticNetCV(cv=5, random_state=0))]:
    print(f"{name:12s} CV R^2 = {cross_val_score(m, X, y, cv=5, scoring='r2').mean():.3f}")
print("Lasso non-zero weights:", np.count_nonzero(LassoCV(cv=5, random_state=0).fit(X, y).coef_), "of 40")
""",
  say=[("What is regularisation, in one sentence, and name a few types.",
        "\"Regularisation is any technique that limits model complexity to improve generalisation — like L1 and L2 weight penalties, dropout, early stopping, data augmentation, and limiting tree depth.\"")]),

M("m-metrics-clf", "Classification metrics: confusion matrix, precision, recall, F1, ROC-AUC, PR-AUC, log loss", "Basic",
  "Accuracy alone hides what kind of mistakes a model makes. The confusion matrix and metrics built from it — precision, recall, F1, AUC — show the trade-offs.",
  """### Confusion matrix (binary)
| |Predicted positive|Predicted negative|
|Actual positive|TP (true positive)|FN (false negative, Type II)|
|Actual negative|FP (false positive, Type I)|TN (true negative)|

### Metrics
- **Accuracy** = (TP + TN)/all — misleading with imbalance.
- **Precision** = TP/(TP + FP): of everything flagged, how much was right? (cost of false alarms — spam filter moving real email).
- **Recall / sensitivity / TPR** = TP/(TP + FN): of all real positives, how many did we catch? (cancer screening, fraud).
- **Specificity / TNR** = TN/(TN + FP). **FPR** = 1 − specificity.
- **F1** = 2PR/(P + R): harmonic mean; **Fβ** weights recall β times more.
- **ROC curve**: TPR vs FPR across thresholds; **ROC-AUC** = probability a random positive scores above a random negative (0.5 random, 1 perfect).
- **PR curve / PR-AUC (average precision)**: better for rare positives.
- **Log loss**: penalises confident wrong probabilities; measures **calibration** too (also Brier score, calibration curves).
- **MCC** (Matthews correlation coefficient) and **Cohen's kappa**: balanced single numbers for imbalance.

### Multiclass
Per-class precision/recall, then **macro** average (each class equal), **weighted** (by support) or **micro** (pool all decisions). Top-k accuracy for many classes.

### Threshold choice
Probabilities → labels needs a threshold; choose it from the business cost of FP vs FN.""",
  demo="roc",
  code="""
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (confusion_matrix, classification_report, roc_auc_score, average_precision_score, log_loss, matthews_corrcoef)

X, y = load_breast_cancer(return_X_y=True); y = 1 - y                  # 1 = malignant (the positive class)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0)
m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(Xtr, ytr)
p = m.predict_proba(Xte)[:, 1]
for thr in (0.5, 0.2):
    pred = (p >= thr).astype(int); tn, fp, fn, tp = confusion_matrix(yte, pred).ravel()
    print(f"threshold {thr}: TP={tp} FP={fp} FN={fn} TN={tn}  precision={tp/(tp+fp):.3f} recall={tp/(tp+fn):.3f}")
print(classification_report(yte, (p >= 0.5).astype(int), target_names=["benign", "malignant"], digits=3))
print(f"ROC-AUC={roc_auc_score(yte, p):.4f}  PR-AUC={average_precision_score(yte, p):.4f}  log loss={log_loss(yte, p):.4f}  MCC={matthews_corrcoef(yte, p >= 0.5):.3f}")
""",
  say=[("Precision vs recall — which matters more for cancer screening and for a spam filter?",
        "\"For cancer screening, recall: missing a cancer — a false negative — is far worse than a false alarm that leads to another test, so I'd lower the threshold. For a spam filter, precision: putting a real email in spam is costly, so I only flag when confident. In general I pick the threshold from the relative cost of false positives and false negatives.\"")]),

M("m-metrics-reg", "Regression metrics: MAE, MSE, RMSE, R², MAPE and residual analysis", "Basic",
  "Regression metrics measure how far predictions are from true values. Choose based on how you want to treat large errors and whether you need relative or absolute error.",
  """|Metric|Formula|Notes|
|MAE (mean absolute error)|mean |y − ŷ||same units, robust to outliers, easy to explain|
|MSE (mean squared error)|mean (y − ŷ)²|punishes big errors; differentiable training loss|
|RMSE|√MSE|same units as y; sensitive to outliers|
|R² (coefficient of determination)|1 − SS_res/SS_tot|fraction of variance explained; 1 perfect, 0 = predicting the mean, can be negative|
|Adjusted R²|penalises extra features|for comparing linear models with different feature counts|
|MAPE (mean absolute percentage error)|mean |y − ŷ|/|y||relative; breaks when y ≈ 0; asymmetric|
|sMAPE / WAPE|symmetric / weighted versions|common in demand forecasting|
|RMSLE|RMSE of log(1 + y)|for targets spanning orders of magnitude; penalises under-prediction more|
|Huber / quantile (pinball) loss|robust / predicts percentiles|prediction intervals|

### Residual analysis
Plot residuals (y − ŷ) vs predictions: random cloud = good; funnel shape = heteroscedasticity (try log target); curve = missed non-linearity.""",
  code="""
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
y_true = np.array([100, 150, 200, 250, 300, 1000.0])
y_good = np.array([110, 140, 210, 240, 310, 980.0])
y_outlier_miss = np.array([102, 149, 199, 251, 299, 600.0])
for name, yp in [("small errors everywhere", y_good), ("one big miss", y_outlier_miss)]:
    print(f"{name:24s} MAE={mean_absolute_error(y_true, yp):6.1f}  RMSE={mean_squared_error(y_true, yp) ** 0.5:6.1f}  "
          f"R2={r2_score(y_true, yp):.3f}  MAPE={mean_absolute_percentage_error(y_true, yp):.1%}")
""",
  say=[("When would you prefer MAE over RMSE?",
        "\"MAE when every unit of error costs the same and I don't want a few outliers to dominate — it's also easier to explain to business users. RMSE when large errors are disproportionately bad, like under-forecasting demand for critical stock, because squaring penalises them more. Reporting both and their ratio shows whether errors are concentrated in a few big misses.\"")]),

M("m-hyperparams", "Hyperparameter tuning: grid, random, Bayesian search, pipelines", "Intermediate",
  "Hyperparameters (depth, learning rate, C, k) are chosen by searching combinations and scoring each with cross-validation. Pipelines keep preprocessing inside the search to avoid leakage.",
  """### Search strategies
- **Grid search**: every combination — simple, explodes combinatorially.
- **Random search**: random combinations — finds good regions faster when only a few hyperparameters matter (Bergstra & Bengio).
- **Bayesian optimisation** (Optuna, Hyperopt, scikit-optimize): models score vs hyperparameters and picks promising ones next.
- **Successive halving / Hyperband**: give many configs a small budget, keep the best, increase budget.
- Search learning rates and regularisation on a **log scale**.

### scikit-learn Pipelines and ColumnTransformer
`ColumnTransformer` applies different preprocessing to numeric and categorical columns; `Pipeline` chains preprocessing + model so `fit` / `predict` / CV / search treat it as one estimator. Parameters are addressed as `step__param`.

### Good practice
Fix random seeds; use the right CV (stratified/group/time); keep the test set out of tuning; prefer simpler models when scores tie.""",
  code="""
import numpy as np, pandas as pd
from scipy.stats import loguniform, randint
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

rng = np.random.default_rng(0); n = 600
df = pd.DataFrame({"age": rng.integers(18, 70, n).astype(float), "income": rng.lognormal(10, 0.5, n),
                   "plan": rng.choice(["basic", "pro", "max"], n), "region": rng.choice(["N", "S", "E", "W"], n)})
df.loc[rng.random(n) < 0.1, "age"] = np.nan
y = ((df["plan"] == "basic") & (df["income"] < 25000) | (rng.random(n) < 0.1)).astype(int)

pre = ColumnTransformer([("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), ["age", "income"]),
                         ("cat", OneHotEncoder(handle_unknown="ignore"), ["plan", "region"])])
pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
grid = GridSearchCV(pipe, {"clf__C": [0.01, 0.1, 1, 10]}, cv=5, scoring="roc_auc").fit(df, y)
print("grid best:", grid.best_params_, round(grid.best_score_, 3))

pipe_rf = Pipeline([("pre", pre), ("clf", RandomForestClassifier(random_state=0))])
rs = RandomizedSearchCV(pipe_rf, {"clf__n_estimators": randint(50, 300), "clf__max_depth": randint(2, 12), "clf__max_features": loguniform(0.1, 1)},
                        n_iter=10, cv=5, scoring="roc_auc", random_state=0).fit(df, y)
print("random search best:", {k: round(float(v), 3) if isinstance(v, float) else int(v) for k, v in rs.best_params_.items()}, round(rs.best_score_, 3))
""",
  say=[("Grid search or random search?",
        "\"Random search for most cases: with the same budget it explores more distinct values of each hyperparameter, and usually only a few hyperparameters matter. For expensive models I'd go further with Bayesian optimisation like Optuna plus early pruning of bad trials. Grid search is fine for one or two hyperparameters with a few values.\"")]),

M("m-separability", "Decision boundaries and linear separability", "Basic",
  "A classifier divides feature space into regions; the border is the decision boundary. Linearly separable data can be split by a straight line (hyperplane); otherwise you need non-linear features or models.",
  """- **Linear classifiers** (logistic regression, linear SVM, perceptron) draw a hyperplane w·x + b = 0.
- **Linearly separable**: some hyperplane puts every class on its own side (AND, OR). **Not separable**: XOR, concentric circles, two moons.
- **Ways to handle non-separable data**: (1) add non-linear features (x², x·y, polar radius) — the data may become linearly separable in a higher dimension (Cover's theorem); (2) **kernels** (SVM with RBF kernel) do this implicitly; (3) non-linear models: kNN, decision trees, neural networks (hidden layers learn the transformation).
- **Margin**: distance from the boundary to the nearest points; larger margins generalise better (SVM idea).
- **Separability check**: train a linear SVM with huge C — 100% training accuracy ⇒ separable.""",
  demo="knn",
  code="""
import numpy as np
from sklearn.datasets import make_circles
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

X, y = make_circles(400, factor=0.4, noise=0.05, random_state=0)
print("linear on raw (x, y):       ", LogisticRegression().fit(X, y).score(X, y))
r2 = (X ** 2).sum(axis=1, keepdims=True)                      # add radius^2 feature
print("linear on (x, y, x^2+y^2):  ", LogisticRegression().fit(np.hstack([X, r2]), y).score(np.hstack([X, r2]), y))
print("RBF kernel SVM on raw:      ", SVC(kernel="rbf").fit(X, y).score(X, y))

xor_X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]]); xor_y = np.array([0, 1, 1, 0])
print("XOR, linear SVM (C huge):   ", SVC(kernel="linear", C=1e6).fit(xor_X, xor_y).score(xor_X, xor_y), "-> not separable")
""",
  say=[("What can you do if your classes aren't linearly separable?",
        "\"Map the data into a space where they are: add polynomial or domain features, use a kernel SVM which does it implicitly, or use an inherently non-linear model like gradient-boosted trees or a neural network whose hidden layers learn the transformation. I'd pick based on data size and interpretability needs.\"")]),

M("m-intuitive-algos", "Intuitive simple algorithms: baselines, nearest centroid, 1-rule, distance-based", "Basic",
  "Before complex models, simple algorithms — predict the majority, nearest class average, a single best rule — give baselines and build intuition.",
  """- **Majority / mean baseline**: always predict the most common class or the mean value. Any model must beat this.
- **Nearest centroid**: compute each class's average point; classify a new point by the closest centroid. Fast, works when classes are blob-like.
- **1R (one rule)**: pick the single feature whose simple rule ("if income < 30k then default") makes fewest errors. Surprisingly strong.
- **k-nearest neighbours**: vote among the k most similar training examples.
- **Decision stump**: a one-split tree (the weak learner in AdaBoost).
- **Linear rule of thumb**: weighted sum of a few features with hand-picked weights (credit scores started this way).
- **Seasonal naive** for forecasting: predict the value from the same time last week/year.

These are interpretable, fast and catch data problems: if a stump scores 99%, look for leakage.""",
  code="""
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.dummy import DummyClassifier
from sklearn.neighbors import NearestCentroid, KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

X, y = load_iris(return_X_y=True)
for name, m in [("majority class", DummyClassifier()), ("decision stump (1 rule)", DecisionTreeClassifier(max_depth=1)),
                ("nearest centroid", NearestCentroid()), ("kNN (k=5)", KNeighborsClassifier(5))]:
    print(f"{name:24s} {cross_val_score(m, X, y, cv=5).mean():.3f}")
stump = DecisionTreeClassifier(max_depth=1).fit(X, y)
print("the stump's rule: feature", stump.tree_.feature[0], "<=", round(stump.tree_.threshold[0], 2))
""",
  say=[("Why should you always build a simple baseline first?",
        "\"It tells me whether the problem is learnable and what 'good' means — a model at 92% accuracy is useless if predicting the majority class gives 95%. Baselines also catch bugs and leakage early, are cheap to deploy, and give a reference to justify the cost of complex models.\"")]),

M("m-search-ai", "Classical AI: search, optimal routes and optimisation (A*, Dijkstra, genetic algorithms)", "Intermediate",
  "Not all AI is learning. Search algorithms find optimal routes and plans; metaheuristics like genetic algorithms and simulated annealing optimise when there is no gradient.",
  """### Uninformed and informed search
- **BFS** (fewest steps), **DFS**, **Dijkstra** (cheapest path with non-negative weights), **A*** = Dijkstra + a heuristic h(n) estimating remaining cost; optimal if h never overestimates (admissible), e.g. straight-line distance on maps.
- Used in route planning (Google Maps), games, robotics, puzzle solving.

### Optimisation without gradients
- **Travelling salesman / vehicle routing**: NP-hard; solved approximately with heuristics (nearest neighbour, 2-opt), OR-Tools, or metaheuristics.
- **Hill climbing, simulated annealing** (accept worse moves with decreasing probability to escape local optima), **genetic algorithms** (population, selection, crossover, mutation), **ant colony**, **particle swarm**.
- **Constraint satisfaction** (scheduling, Sudoku) and **adversarial search** (minimax with alpha-beta pruning, Monte Carlo tree search in AlphaGo).

### Link to ML
Reinforcement learning learns policies when the environment is unknown; ML can learn heuristics for search (AlphaZero combines MCTS with neural nets).""",
  code="""
import heapq, math, random

grid = ["S..#......", ".#.#.####.", ".#...#....", ".####.#.#.", "......#.#G"]
R, C = len(grid), len(grid[0]); start = (0, 0); goal = (4, 9)
def astar():
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])          # Manhattan heuristic (admissible)
    pq, best, parent = [(h(start), 0, start)], {start: 0}, {}
    while pq:
        f, g, cur = heapq.heappop(pq)
        if cur == goal:
            path = [cur]
            while cur in parent: cur = parent[cur]; path.append(cur)
            return g, path[::-1]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = cur[0] + dr, cur[1] + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != "#" and g + 1 < best.get((nr, nc), 1e9):
                best[(nr, nc)] = g + 1; parent[(nr, nc)] = cur; heapq.heappush(pq, (g + 1 + h((nr, nc)), g + 1, (nr, nc)))
cost, path = astar(); print("A* shortest path length:", cost)

random.seed(0)
cities = [(random.random(), random.random()) for _ in range(12)]
dist = lambda a, b: math.dist(cities[a], cities[b]); tour_len = lambda t: sum(dist(t[i], t[(i + 1) % len(t)]) for i in range(len(t)))
tour = list(range(12)); T = 1.0; cur = tour_len(tour)
for step in range(20000):                                          # simulated annealing with 2-opt moves
    i, j = sorted(random.sample(range(12), 2)); new = tour[:i] + tour[i:j + 1][::-1] + tour[j + 1:]
    d = tour_len(new) - cur
    if d < 0 or random.random() < math.exp(-d / T): tour, cur = new, cur + d
    T *= 0.9995
print("TSP tour length after simulated annealing:", round(cur, 3))
""",
  say=[("When is A* optimal?",
        "\"When its heuristic is admissible — it never overestimates the true remaining cost — and, for graph search without re-opening nodes, consistent. Straight-line or Manhattan distance on a grid are classic admissible heuristics. With h equal to zero, A* becomes Dijkstra.\"")]),
]
