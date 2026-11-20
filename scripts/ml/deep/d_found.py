"""Deep layer + end-to-end walkthroughs: ML foundations."""
from deep.util import X

TITANIC = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
PENGUINS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
MPG = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv"
HOUSING = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
TELCO = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
RETAIL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"
SMS = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
SONAR = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/sonar.csv"
PIMA = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
PIMA_COLS = ["pregnancies", "glucose", "bp", "skin", "insulin", "bmi", "pedigree", "age", "diabetes"]
LOAD_TELCO = f'''df = pd.read_csv("{TELCO}")
df["TotalCharges"] = pd.to_numeric(df.TotalCharges, errors="coerce").fillna(0); y = (df.pop("Churn") == "Yes").astype(int); df = df.drop(columns="customerID")'''

X("m-ai-overview",
  "AI is the broad goal of machines doing tasks that need intelligence. Approaches evolved from **hand-written rules and search** (symbolic AI), to **machine learning** (learn rules from data), to **deep learning** (learn the features too), to **foundation models/LLMs** (pre-train once on huge data, adapt to many tasks). Each layer still has its place.",
  """**How the paradigms differ.** Rules: program = f written by a human; brittle when inputs vary. ML: given examples (x, y), find f in a hypothesis class that minimises a loss — generalises if the class is right and the data representative. DL: f is a deep network; features are learned end-to-end, needs more data/compute. Foundation models: self-supervised pre-training (predict the next token / masked part) on web-scale data, then prompting, fine-tuning or retrieval. **AI ⊃ ML ⊃ DL ⊃ (LLMs as one family)**.""",
  """**Spam filter three ways.** Rule: 'flag if the message contains *free* or *win*' → catches some spam, misses rephrasings, flags 'are you free tonight?'. ML: count words in 5,000 labelled messages, learn weights → ~98% accuracy. LLM: zero-shot prompt 'Is this spam?' → good without training data, but slower and costlier per message.""",
  ["Using ML where simple rules suffice (or rules where data patterns are complex)", "Thinking 'AI' means only LLMs", "Expecting ML to work without representative data"],
  ["Rules: clear, stable logic", "Classical ML: tabular data, moderate size", "DL: images/audio/text at scale", "LLMs: language tasks, few labels"], ["LLMs for deterministic calculations or strict business rules"],
  "SMS Spam Collection — the same task solved by a hand-written rule system and by learned models of increasing capacity, compared on the same test set.",
  ["Load and split the messages", "Write a rule-based classifier", "Train a learned linear model on word counts", "Train a small neural network on the same features", "Compare accuracy, precision/recall and failure examples"],
  f'''
import re, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
df = pd.read_csv("{SMS}", sep="\\t", names=["label", "text"]); y = (df.label == "spam").astype(int)
tr_x, te_x, tr_y, te_y = train_test_split(df.text, y, test_size=0.25, stratify=y, random_state=0)
RULES = [r"\\bfree\\b", r"\\bwin(ner)?\\b", r"\\bprize\\b", r"\\bcall\\b.*\\d{{5,}}", r"\\btxt\\b", r"£\\d+", r"\\burgent\\b"]
rule_pred = te_x.str.lower().apply(lambda t: int(sum(bool(re.search(p, t)) for p in RULES) >= 1))
vec = TfidfVectorizer(min_df=2, ngram_range=(1, 2)); A, B = vec.fit_transform(tr_x), vec.transform(te_x)
models = {{"rules (symbolic)": rule_pred,
          "logistic regression (ML)": LogisticRegression(C=10, max_iter=2000).fit(A, tr_y).predict(B),
          "neural net (DL-style)": MLPClassifier((64,), max_iter=50, random_state=0).fit(A, tr_y).predict(B)}}
for name, pred in models.items():
    p, r, f, _ = precision_recall_fscore_support(te_y, pred, average="binary")
    print(f"{{name:26s}} accuracy {{(pred == te_y).mean():.3f}} precision {{p:.2f}} recall {{r:.2f}} F1 {{f:.2f}}")
fp = te_x[(rule_pred == 1) & (te_y == 0)].head(3).tolist(); print("rule false alarms:", fp)
''')

X("m-ml-types",
  "ML problems come in families defined by what feedback you have: **supervised** (inputs with correct answers — classification, regression), **unsupervised** (inputs only — clustering, dimensionality reduction, anomaly detection), **semi-/self-supervised** (few labels or labels made from the data itself), and **reinforcement learning** (actions with delayed rewards).",
  """**Formal view.** Supervised: learn f: X → Y minimising E[loss(f(x), y)]; Y discrete → classification, continuous → regression. Unsupervised: model p(x) or find structure (clusters minimise within-cluster distance; PCA maximises retained variance). Semi-supervised: use unlabelled data to shape the decision boundary (cluster/smoothness assumption — labels propagate through dense regions). Self-supervised: invent a supervised task from x (predict masked words). RL: learn a policy π(a|s) maximising expected discounted return Σγᵗrₜ, through exploration.""",
  """**Same penguins, four framings.** Predict species from measurements → classification (labels known). Predict body mass → regression. Group birds without species labels → clustering (do 3 clusters match 3 species?). Only 10 labelled birds out of 333 → semi-supervised label spreading. Choose which island to survey to find the most Gentoos, learning from rewards → a bandit (simplest RL).""",
  ["Framing a regression target as classification (or vice versa) without reason", "Expecting clusters to equal your labels", "Calling any adaptive system 'RL'"],
  ["Pick the family from the feedback you actually have"], ["Unsupervised methods when you do have reliable labels for the real goal"],
  "Penguins — solve one dataset as classification, regression, clustering, semi-supervised learning and a multi-armed bandit.",
  ["Classification of species", "Regression of body mass", "K-means clustering and agreement with species (ARI)", "Label spreading with 10 labels", "Epsilon-greedy bandit choosing islands"],
  f'''
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import adjusted_rand_score
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.semi_supervised import LabelSpreading
df = pd.read_csv("{PENGUINS}").dropna(); cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]
X = StandardScaler().fit_transform(df[cols]); y = pd.factorize(df.species)[0]
print("classification accuracy:", cross_val_score(LogisticRegression(), X, y, cv=5).mean().round(3))
print("regression R² (mass):", cross_val_score(LinearRegression(), X, df.body_mass_g, cv=5).mean().round(3))
km = KMeans(3, n_init=10, random_state=0).fit(X); print("clustering vs true species ARI:", round(adjusted_rand_score(y, km.labels_), 3))
rng = np.random.default_rng(0); y_partial = np.full(len(y), -1); idx = rng.choice(len(y), 10, replace=False); y_partial[idx] = y[idx]
ls = LabelSpreading(kernel="knn", n_neighbors=10).fit(X, y_partial); print("semi-supervised with 10 labels:", round((ls.transduction_ == y).mean(), 3))
islands = df.island.unique(); p_gentoo = {{i: (df[df.island == i].species == "Gentoo").mean() for i in islands}}
Q, N, total = dict.fromkeys(islands, 0.0), dict.fromkeys(islands, 0), 0
for t in range(500):
    i = rng.choice(islands) if rng.random() < 0.1 else max(Q, key=Q.get)
    r = float(rng.random() < p_gentoo[i]); N[i] += 1; Q[i] += (r - Q[i]) / N[i]; total += r
print("bandit: visits", N, "| reward", int(total), "| best island", max(p_gentoo, key=p_gentoo.get))
''')

X("m-ml-principles",
  "A few principles explain almost every ML success and failure: **generalisation** (what matters is performance on new data), the **bias–variance trade-off** (too simple vs too flexible), **no free lunch** (no model wins everywhere), **Occam's razor** (prefer the simplest model that works), and **garbage in, garbage out**.",
  """**Bias–variance decomposition** (squared loss): E[(y − f̂(x))²] = Bias[f̂(x)]² + Var[f̂(x)] + σ² (irreducible noise). Bias: error from wrong assumptions (a line fit to a curve). Variance: sensitivity to the particular training sample. More capacity lowers bias, raises variance; more data lowers variance. **Generalisation gap** = test error − train error; it shrinks roughly like √(complexity/n). Learning curves (error vs training size) diagnose which side you're on: high bias → both curves plateau high and close; high variance → big gap that narrows with data.""",
  """**Estimate it.** Fit depth-2 and depth-20 trees on 50 bootstrap samples; at a test point the true value is 2.0. Depth 2 predictions average 2.6 with sd 0.1 → bias² 0.36, variance 0.01. Depth 20 average 2.05 with sd 0.6 → bias² 0.0025, variance 0.36. Both have similar total error for different reasons — fixes differ (more capacity vs more data/regularisation).""",
  ["Judging a model by training accuracy", "Adding complexity when the problem is bad data", "Believing one algorithm is always best"],
  ["Diagnosing models, deciding between more data vs more capacity"], ["Chasing tiny validation gains that are within noise"],
  "California housing — measure bias and variance empirically for models of different capacity, and draw learning curves to decide whether more data or more capacity helps.",
  ["Prepare features and a fixed test set", "Bootstrap-train models of increasing capacity", "Decompose test error into bias², variance and noise", "Learning curves for a simple and a flexible model", "Write the diagnosis"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import learning_curve, train_test_split
from sklearn.tree import DecisionTreeRegressor
df = pd.read_csv("{HOUSING}").dropna(); X = df[["median_income", "housing_median_age", "latitude", "longitude"]].to_numpy(); y = df.median_house_value.to_numpy() / 1e5
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=2000, random_state=0); rng = np.random.default_rng(0)
for name, make in [("linear", LinearRegression), ("tree depth 3", lambda: DecisionTreeRegressor(max_depth=3)),
                   ("tree depth 8", lambda: DecisionTreeRegressor(max_depth=8)), ("tree depth 30", lambda: DecisionTreeRegressor(max_depth=30))]:
    P = np.array([make().fit(Xtr[i], ytr[i]).predict(Xte) for i in (rng.integers(0, len(Xtr), 3000) for _ in range(30))])
    mean = P.mean(0); bias2 = ((mean - yte) ** 2).mean(); var = P.var(0).mean(); mse = ((P - yte) ** 2).mean()
    print(f"{{name:14s}} test MSE {{mse:.3f}} = bias²+noise {{bias2:.3f}} + variance {{var:.3f}}")
for name, m in [("linear", LinearRegression()), ("deep tree", DecisionTreeRegressor(max_depth=30))]:
    sizes, tr, va = learning_curve(m, X, y, train_sizes=[0.05, 0.2, 0.5, 1.0], cv=5, scoring="neg_mean_squared_error")
    print(f"{{name:10s}} train MSE {{(-tr.mean(1)).round(2)}} | validation MSE {{(-va.mean(1)).round(2)}} at sizes {{sizes}}")
print("diagnosis: linear = high bias (curves meet high); deep tree = high variance (big gap) -> regularise or ensemble")
''')

X("m-problem-formulation",
  "Most failed ML projects fail before modelling: the wrong target, the wrong metric, or no baseline. Formulating means translating a business goal into **prediction target + unit of prediction + features available at prediction time + metric + decision rule + baseline**.",
  """**Checklist.** (1) Decision: what action will the prediction trigger? (2) Target: precisely defined, observable label (e.g. 'cancels within 30 days'). (3) Unit and time: one row per customer per month; features only from before the prediction time. (4) Metric tied to cost: e.g. expected profit = TP·(value saved − offer cost) − FP·offer cost. (5) Baseline: majority class, simple rule, or current process. (6) Constraints: latency, interpretability, fairness. A model is useful only if it beats the baseline on the business metric.""",
  """**Churn economics by hand.** Retention offer costs ₹500; a saved customer is worth ₹6,000; the offer saves 30% of true churners. Contacting a true churner yields 0.3·6000 − 500 = **₹1,300**; contacting a non-churner costs **₹500**. So contact if P(churn)·1300 − (1 − P)·500 > 0 ⇒ **P > 0.278** — the threshold comes from economics, not 0.5.""",
  ["Optimising accuracy when costs are asymmetric", "Using features not available at prediction time", "No baseline", "Vague targets ('engaged users')"],
  ["Every project, before any modelling"], ["Skipping it because a dataset already has a 'label' column"],
  "IBM Telco customer churn (7,043 customers) — formulate churn prediction as a profit-maximising decision: baseline, model, threshold from costs, expected profit.",
  ["Define target, unit and decision; inspect the base rate", "Baselines: contact nobody / everybody / rule (month-to-month contracts)", "Train a model", "Derive the threshold from business costs", "Compare expected profit of each policy"],
  f'''
import numpy as np, pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
{LOAD_TELCO}
print(f"unit: one customer | target: churned last month | base rate {{y.mean():.1%}}")
num = ["tenure", "MonthlyCharges", "TotalCharges"]; cat = [c for c in df if c not in num]
Xtr, Xte, ytr, yte = train_test_split(df, y, test_size=0.3, stratify=y, random_state=0)
model = make_pipeline(make_column_transformer((StandardScaler(), num), (OneHotEncoder(handle_unknown="ignore"), cat)), LogisticRegression(max_iter=2000)).fit(Xtr, ytr)
p = model.predict_proba(Xte)[:, 1]
VALUE, OFFER, SAVE_RATE = 6000, 500, 0.3
gain_tp, cost_fp = SAVE_RATE * VALUE - OFFER, OFFER; thr = cost_fp / (gain_tp + cost_fp)
profit = lambda contact: (contact & (yte == 1)).sum() * gain_tp - (contact & (yte == 0)).sum() * cost_fp
policies = {{"contact nobody": np.zeros(len(yte), bool), "contact everybody": np.ones(len(yte), bool),
            "rule: month-to-month": (Xte.Contract == "Month-to-month").to_numpy(), "model @0.5": p > 0.5, f"model @{{thr:.3f}} (cost-based)": p > thr}}
for name, c in policies.items(): print(f"  {{name:28s}} contacts {{c.sum():5d}} profit ₹{{profit(c):>10,.0f}}")
best = max(np.linspace(0.05, 0.9, 50), key=lambda t: profit(p > t)); print(f"empirically best threshold {{best:.2f}} (theory {{thr:.3f}})")
''')

X("m-intuitive-algos",
  "Before fancy models, a few intuitive ideas already learn: **predict the average**, **copy the nearest example**, **one simple rule (1R)**, **a single split (stump)**, **a weighted checklist (linear score)**. They're strong baselines, easy to explain, and every advanced model is a refinement of one of them.",
  """**Each idea formally.** Mean/majority: f(x) = constant minimising loss. Nearest neighbour: f(x) = y of argminᵢ d(x, xᵢ) — no training, all cost at prediction. 1R: for each feature, predict the majority class per value; keep the feature with the fewest errors. Stump: best single threshold split by impurity. Linear score: f(x) = sign(Σwᵢxᵢ + b) with weights from a rule of thumb or learned. Trees = many stumps stacked; forests = many trees; kNN with k > 1 = local averaging; neural networks = stacked linear scores.""",
  """**1R on Titanic.** Sex: female → survive (233/314 right), male → die (468/577 right) → 701/891 = **78.7%**. Pclass: 1 → survive (136/216), 2 → die (97/184), 3 → die (372/491) → 605/891 = 67.9%. 1R picks **Sex**. The majority baseline ('everyone dies') gets 549/891 = **61.6%**.""",
  ["Skipping baselines and celebrating a model that barely beats majority", "Using 1-NN without scaling", "Over-trusting a single rule"],
  ["Baselines, quick prototypes, explainable first models"], ["Final models for complex data without comparing stronger methods"],
  "Titanic — implement majority, 1R, nearest neighbour and a decision stump from scratch, then compare with a full decision tree and logistic regression.",
  ["Prepare simple features", "Majority baseline", "1R from scratch", "1-NN and k-NN from scratch with scaling", "Stump from scratch, then compare with sklearn models"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
df = pd.read_csv("{TITANIC}"); df["Age"] = df.Age.fillna(df.Age.median()); df["Female"] = (df.Sex == "female").astype(int)
df["AgeBand"] = pd.cut(df.Age, [0, 12, 30, 60, 100], labels=False); feats = ["Female", "Pclass", "AgeBand", "SibSp"]
tr, te = train_test_split(df, test_size=0.3, random_state=0, stratify=df.Survived)
acc = lambda pred: round((np.asarray(pred) == te.Survived.to_numpy()).mean(), 3)
print("majority:", acc(np.full(len(te), tr.Survived.mode()[0])))
best = min(feats, key=lambda f: (tr.Survived != tr[f].map(tr.groupby(f).Survived.agg(lambda s: s.mode()[0]))).sum())
rule = tr.groupby(best).Survived.agg(lambda s: s.mode()[0]); print(f"1R picks {{best}}: rule {{rule.to_dict()}} ->", acc(te[best].map(rule).fillna(0)))
num = ["Female", "Pclass", "Age", "SibSp", "Fare"]; mu, sd = tr[num].mean(), tr[num].std()
A, B = ((tr[num] - mu) / sd).to_numpy(), ((te[num] - mu) / sd).to_numpy()
D = ((B[:, None] - A[None]) ** 2).sum(-1)
for k in [1, 15]: print(f"{{k}}-NN from scratch:", acc((tr.Survived.to_numpy()[np.argsort(D, 1)[:, :k]].mean(1) > 0.5).astype(int)))
def gini(s): p = s.mean(); return 2 * p * (1 - p)
cands = [(f, t) for f in num for t in np.unique(tr[f])[:-1]]
f, t = min(cands, key=lambda c: sum(len(g) * gini(g.Survived) for g in (tr[tr[c[0]] <= c[1]], tr[tr[c[0]] > c[1]])))
print(f"stump: split on {{f}} <= {{t}} ->", acc((te[f] > t).astype(int) if tr[tr[f] > t].Survived.mean() > 0.5 else (te[f] <= t).astype(int)))
print("full tree (depth 4):", acc(DecisionTreeClassifier(max_depth=4, random_state=0).fit(tr[num], tr.Survived).predict(te[num])))
print("logistic regression:", acc(LogisticRegression(max_iter=1000).fit(A, tr.Survived).predict(B)))
''')

X("m-search-ai",
  "Classical AI solves problems by **searching** a space of states: puzzles, route planning, game playing, scheduling. Uninformed search (BFS, DFS) explores blindly; **informed search (A\\*)** uses a heuristic estimate of the remaining cost; **adversarial search (minimax + alpha-beta)** plans against an opponent. These ideas live on inside modern AI (beam search in LLM decoding, MCTS in AlphaGo, planning in agents).",
  """**Algorithms.** BFS: FIFO queue, finds the shortest path in unweighted graphs, memory O(bᵈ). DFS: stack, low memory, not optimal. Uniform-cost (Dijkstra): priority queue by path cost g. **A\\***: priority f = g + h where h estimates cost-to-goal; if h never overestimates (*admissible*), A\\* is optimal; the better h, the fewer nodes expanded. For the 8-puzzle, Manhattan distance (sum of each tile's grid distance to its goal) is admissible and dominates 'misplaced tiles'. **Minimax** picks moves maximising your worst-case outcome; **alpha-beta** prunes branches that can't change the decision (same answer, far fewer nodes).""",
  """**Heuristic by hand.** State 1 2 3 / 4 _ 6 / 7 5 8. Misplaced tiles: 5 and 8 → h = 2. Manhattan: 5 is one row below its goal (1), 8 is one column right (1) → h = 2. The true solution: move 5 up, 8 left → 2 moves, so h is exact here. Tic-tac-toe: minimax from the empty board evaluates 549,946 nodes; alpha-beta needs ~20k.""",
  ["Non-admissible heuristics when optimality is needed", "Forgetting a visited set (infinite loops)", "Using DFS when the shortest path matters"],
  ["Route planning, puzzles, scheduling, game AI, decoding"], ["Huge continuous problems where gradient methods or RL scale better"],
  "No dataset: the 8-puzzle solved with BFS vs A\\* (two heuristics) and tic-tac-toe with minimax vs alpha-beta — counting nodes expanded to see why heuristics and pruning matter.",
  ["Define states, actions and goal test", "Implement BFS", "Implement A\\* with misplaced-tiles and Manhattan heuristics", "Compare nodes expanded and path lengths", "Minimax vs alpha-beta on tic-tac-toe"],
  '''
import heapq, random
from collections import deque
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
def moves(s):
    i = s.index(0); r, c = divmod(i, 3)
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if 0 <= r + dr < 3 and 0 <= c + dc < 3:
            j = (r + dr) * 3 + c + dc; t = list(s); t[i], t[j] = t[j], t[i]; yield tuple(t)
def bfs(start):
    seen, q = {start: 0}, deque([start])
    while q:
        s = q.popleft()
        if s == GOAL: return seen[s], len(seen)
        for n in moves(s):
            if n not in seen: seen[n] = seen[s] + 1; q.append(n)
def astar(start, h):
    g, pq, expanded = {start: 0}, [(h(start), start)], 0
    while pq:
        _, s = heapq.heappop(pq); expanded += 1
        if s == GOAL: return g[s], expanded
        for n in moves(s):
            if g[s] + 1 < g.get(n, 1e9): g[n] = g[s] + 1; heapq.heappush(pq, (g[n] + h(n), n))
misplaced = lambda s: sum(1 for i, v in enumerate(s) if v and v != GOAL[i])
manhattan = lambda s: sum(abs(i // 3 - (v - 1) // 3) + abs(i % 3 - (v - 1) % 3) for i, v in enumerate(s) if v)
random.seed(0); s = GOAL
for _ in range(60): s = random.choice(list(moves(s)))
print("start:", s)
print("BFS          (length, nodes):", bfs(s))
print("A* misplaced (length, nodes):", astar(s, misplaced))
print("A* manhattan (length, nodes):", astar(s, manhattan))
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
def winner(b): return next((b[i] for i, j, k in LINES if b[i] and b[i] == b[j] == b[k]), None)
count = [0]
def minimax(b, player, alpha=-2, beta=2, prune=False):
    count[0] += 1; w = winner(b)
    if w: return 1 if w == "X" else -1
    if all(b): return 0
    best = -2 if player == "X" else 2
    for i in range(9):
        if not b[i]:
            b[i] = player; v = minimax(b, "O" if player == "X" else "X", alpha, beta, prune); b[i] = None
            if player == "X": best = max(best, v); alpha = max(alpha, v)
            else: best = min(best, v); beta = min(beta, v)
            if prune and alpha >= beta: break
    return best
for prune in [False, True]:
    count[0] = 0; v = minimax([None] * 9, "X", prune=prune); print(f"tic-tac-toe value {v} (draw) | {'alpha-beta' if prune else 'minimax   '} nodes {count[0]:,}")
''')

X("m-data-processing",
  "Raw data is messy: wrong types, duplicates, inconsistent spellings, impossible values, missing entries. Data processing turns it into a clean, documented table you can trust — and it should be a **repeatable script or pipeline**, not manual edits.",
  """**Steps.** Parse types (dates, numbers, categories) → remove exact/near duplicates → standardise text (case, whitespace, spellings) → validate ranges and business rules (quantity > 0, price ≥ 0) → handle missing values → derive clean columns → save with a data dictionary. **Missingness types:** MCAR (random), MAR (depends on observed columns), MNAR (depends on the missing value itself) — only MCAR makes dropping rows unbiased. Every cleaning rule should be logged with how many rows it affected.""",
  """**Retail rules.** 541,909 invoice lines. Negative quantities = cancellations ('C' invoices) → separate them. Unit price 0 = free samples/adjustments → drop for revenue analysis. Missing CustomerID ≈ 25% → keep for product-level analysis, drop for customer-level. Revenue = quantity × unit price per line.""",
  ["Cleaning by hand in Excel (not reproducible)", "Dropping all rows with any missing value", "Silently fixing values without logging counts", "Cleaning test data with statistics from all data"],
  ["Every project; build it as functions/pipelines"], ["Over-cleaning away real but rare behaviour"],
  "Online Retail (541,909 real invoice lines from a UK retailer) — parse, deduplicate, validate, separate cancellations, handle missing customers, and log every rule's effect.",
  ["Load and inspect types and issues", "Parse dates, strip text, remove duplicates", "Validate business rules and separate cancellations", "Handle missing CustomerID by use-case", "Save the clean table and a cleaning log"],
  f'''
import pandas as pd
log = []
def step(name, before, after): log.append((name, before - after)); return after
raw = pd.read_csv("{RETAIL}", encoding="latin-1"); n = len(raw); print("raw:", raw.shape, raw.dtypes.to_dict())
df = raw.copy(); df["InvoiceDate"] = pd.to_datetime(df.InvoiceDate, format="mixed"); df["Description"] = df.Description.str.strip().str.upper()
df = df.drop_duplicates(); n = step("exact duplicates", n, len(df))
cancel = df.InvoiceNo.astype(str).str.startswith("C"); cancellations = df[cancel]; df = df[~cancel]; n = step("cancellations (kept separately)", n, len(df))
df = df[df.UnitPrice > 0]; n = step("non-positive prices", n, len(df))
df = df[df.Quantity > 0]; n = step("non-positive quantities", n, len(df))
df = df[~df.StockCode.astype(str).str.fullmatch(r"POST|DOT|M|BANK CHARGES|AMAZONFEE|CRUK|D|S|B|PADS|C2")]; n = step("non-product codes", n, len(df))
df["Revenue"] = df.Quantity * df.UnitPrice
customers = df.dropna(subset=["CustomerID"]).astype({{"CustomerID": int}})
for name, k in log: print(f"  rule {{name:32s}} removed {{k:7,d}}")
print(f"clean lines {{len(df):,}} | with customer id {{len(customers):,}} ({{len(customers) / len(df):.0%}}) | cancellations {{len(cancellations):,}}")
print("revenue by country (top 5):", df.groupby("Country").Revenue.sum().nlargest(5).round(0).to_dict())
df.to_parquet("retail_clean.parquet"); print("saved retail_clean.parquet")
''')

X("m-eda",
  "Exploratory data analysis is interviewing your data before modelling: what's in each column, how values are distributed, how features relate to the target and each other, what's missing or odd. Good EDA produces **hypotheses and cleaning/feature decisions**, not just plots.",
  """**Structure.** Univariate (distribution, missingness, cardinality, outliers) → bivariate with target (rates by category, distributions by class, correlation/MI) → multivariate (interactions, segments, correlations among features) → data quality (leaky columns, duplicates, drift over time). Quantify what you see: churn rate per segment with counts and CIs; mutual information ranks non-linear relationships. Write findings as decisions: 'tenure strongly related → keep; TotalCharges ≈ tenure × MonthlyCharges → redundant'.""",
  """**Reading a segment table.** Month-to-month contracts: 3,875 customers, 42.7% churn; two-year: 1,695, 2.8%. Difference ≈ 40 points with ±1.6-point CIs → a real, huge effect. A segment with 30 customers at 60% churn has a ±18-point CI — interesting, not conclusive.""",
  ["Plotting everything without questions", "Ignoring counts behind rates", "Doing EDA on the test set", "Not writing decisions down"],
  ["Every new dataset"], ["Endless EDA without moving to a baseline model"],
  "IBM Telco churn — a structured EDA: profile, target rates by segment with CIs, numeric distributions by class, mutual information ranking, redundancy check, saved figure, and a written findings list.",
  ["Profile columns (types, missing, cardinality)", "Churn rate by each categorical with counts and CIs", "Numeric features by churn class", "Rank all features by mutual information", "Check redundancy and write findings"],
  f'''
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd
from sklearn.feature_selection import mutual_info_classif
{LOAD_TELCO}
prof = pd.DataFrame({{"dtype": df.dtypes.astype(str), "missing": df.isna().sum(), "unique": df.nunique()}}); print(prof.T.iloc[:, :8])
cats = [c for c in df if not pd.api.types.is_numeric_dtype(df[c])]
for c in ["Contract", "InternetService", "PaymentMethod"]:
    g = y.groupby(df[c]).agg(["size", "mean"]); g["ci95"] = 1.96 * np.sqrt(g["mean"] * (1 - g["mean"]) / g["size"]); print(g.round(3))
print(df.assign(churn=y).groupby("churn")[["tenure", "MonthlyCharges"]].median())
enc = df.copy(); enc[cats] = enc[cats].apply(lambda s: pd.factorize(s)[0])
mi = pd.Series(mutual_info_classif(enc, y, discrete_features=[c in cats for c in enc], random_state=0), enc.columns).sort_values(ascending=False)
print("mutual information ranking:", mi.head(6).round(3).to_dict())
print("TotalCharges vs tenure×MonthlyCharges correlation:", round(np.corrcoef(df.TotalCharges, df.tenure * df.MonthlyCharges)[0, 1], 3))
fig, ax = plt.subplots(1, 2, figsize=(10, 4)); y.groupby(df.Contract).mean().plot.bar(ax=ax[0], title="churn rate by contract")
[ax[1].hist(df.tenure[y == k], bins=30, alpha=0.6, label=f"churn={{k}}") for k in (0, 1)]; ax[1].legend(); ax[1].set_title("tenure by class"); fig.tight_layout(); fig.savefig("eda.png")
print("FINDINGS: contract type & tenure dominate; TotalCharges redundant with tenure×MonthlyCharges; fibre users churn more")
''')

X("m-real-world-data",
  "Real datasets break textbook assumptions: values are **missing**, **capped**, **skewed**, **outlying**, **inconsistent**, **imbalanced**, and they **drift over time**. Recognising these patterns and choosing a principled fix (instead of deleting rows) is a core practical skill.",
  """**Missing data strategies.** Drop (only if MCAR and few), simple impute (median/mode — shrinks variance), group-wise impute, model-based (KNN/iterative imputer), plus a **missing-indicator** column (missingness can be informative). **Censoring/capping:** values clipped at a maximum (e.g. house value capped at 500,001) bias regression — model separately or drop. **Skew:** log/Box-Cox for heavy right tails. **Outliers:** verify; cap (winsorise) or use robust models. Always fit imputers inside the pipeline on training folds.""",
  """**Capping by hand.** 965 California districts have value exactly 500,001 (the cap). Their true values are ≥ 500k, so a model trained on them learns 'max = 500k' and under-predicts expensive areas. Fix options: remove capped rows for training (and flag such predictions), or treat as censored.""",
  ["Mean imputation before the train/test split", "Dropping rows with any NaN", "Ignoring capped/censored targets", "Treating sentinel values (0, -1, 999) as real numbers"],
  ["Any real dataset"], ["Imputing the target variable"],
  "California housing — find the real-world issues (missing bedrooms, capped target and age, skewed counts, sentinel-like values, geographic clusters) and compare fixes inside cross-validated pipelines.",
  ["Audit missing values, caps and skew", "Compare imputation strategies (median, KNN, iterative, + indicator)", "Handle the capped target", "Log-transform skewed counts", "Measure the effect of each fix with CV"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
df = pd.read_csv("{HOUSING}"); y = df.pop("median_house_value"); df = df.drop(columns="ocean_proximity")
print("missing:", df.isna().sum()[lambda s: s > 0].to_dict(), "| capped target rows:", int((y >= 500001).sum()), "| capped age rows:", int((df.housing_median_age == 52).sum()))
print("skew of counts:", df[["total_rooms", "population", "households"]].skew().round(1).to_dict())
cv = lambda pipe, X, t: -cross_val_score(pipe, X, t, cv=5, scoring="neg_root_mean_squared_error").mean()
log = FunctionTransformer(np.log1p, feature_names_out="one-to-one")
for name, imp in [("median", SimpleImputer(strategy="median")), ("median+indicator", SimpleImputer(strategy="median", add_indicator=True)),
                  ("KNN", KNNImputer(n_neighbors=5)), ("iterative", IterativeImputer(random_state=0))]:
    print(f"  imputer {{name:17s}} Ridge RMSE ${{cv(make_pipeline(imp, StandardScaler(), Ridge()), df, y):,.0f}}")
print(f"  + log1p on skewed counts  Ridge RMSE ${{cv(make_pipeline(SimpleImputer(strategy='median'), log, StandardScaler(), Ridge()), df.clip(lower=0), y):,.0f}}")
keep = y < 500001
print(f"  gradient boosting all rows RMSE ${{cv(HistGradientBoostingRegressor(random_state=0), df, y):,.0f}} | uncapped rows only ${{cv(HistGradientBoostingRegressor(random_state=0), df[keep], y[keep]):,.0f}}")
''')

X("m-encoding",
  "Models need numbers, so categories must be encoded. **One-hot** for nominal categories, **ordinal** for ordered ones, **target/mean encoding** for high-cardinality columns, **hashing** for huge or open vocabularies, **embeddings** in neural networks. The right choice depends on cardinality, model type and leakage risk.",
  """**Details.** One-hot: K binary columns (drop one with an intercept in linear models; keep all for trees). Ordinal: integers preserving order (low < medium < high) — wrong for nominal data in linear models (implies distances). **Target encoding:** replace category with the smoothed target mean: enc(c) = (nₖ·ȳₖ + m·ȳ)/(nₖ + m) — must be computed *out-of-fold*, otherwise it leaks the label (sklearn's TargetEncoder does cross-fitting). Hashing: column = hash(category) mod D, collisions tolerated. Trees handle ordinal/integer codes well; linear models need one-hot.""",
  """**Smoothed target encoding by hand.** City A: 5 customers, 4 churned (ȳ = 0.8); overall rate 0.26; m = 10. enc(A) = (5·0.8 + 10·0.26)/15 = (4 + 2.6)/15 = **0.44** — pulled toward the global mean because 5 rows aren't much evidence. City B with 500 customers at 0.3 → (150 + 2.6)/510 = **0.299**.""",
  ["Ordinal-encoding nominal categories for linear models", "Target encoding without out-of-fold fitting (leakage)", "One-hot on 10,000 categories (huge sparse matrices)", "Crashing on unseen categories at prediction time"],
  ["One-hot: low cardinality", "Target encoding: high cardinality", "Ordinal: true orders, tree models"], ["Label encoding nominal features for linear/kNN models"],
  "IBM Telco churn — compare one-hot, ordinal, target and hashing encoders with linear and tree models; demonstrate the leakage of naive target encoding on a high-cardinality ID-like column.",
  ["Split columns into numeric/categorical", "Build pipelines with each encoder", "Cross-validate with logistic regression and gradient boosting", "Show naive target encoding leaks with a random high-cardinality column", "Handle unseen categories"],
  f'''
import numpy as np, pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction import FeatureHasher
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler, TargetEncoder
{LOAD_TELCO}
num = ["tenure", "MonthlyCharges", "TotalCharges"]; cat = [c for c in df if c not in num]
hasher = FunctionTransformer(lambda X: FeatureHasher(64, input_type="string").transform([[f"{{c}}={{v}}" for c, v in zip(cat, row)] for row in np.asarray(X)]))
encoders = {{"one-hot": OneHotEncoder(handle_unknown="ignore"), "ordinal": OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
            "target (cross-fit)": TargetEncoder(random_state=0), "hashing (64)": hasher}}
for name, enc in encoders.items():
    for mname, m in [("logistic", LogisticRegression(max_iter=3000)), ("boosting", HistGradientBoostingClassifier(random_state=0))]:
        pipe = make_pipeline(make_column_transformer((StandardScaler(), num), (enc, cat), sparse_threshold=0), m)
        print(f"  {{name:18s}} {{mname:8s}} AUC {{cross_val_score(pipe, df, y, cv=5, scoring='roc_auc').mean():.4f}}")
rng = np.random.default_rng(0); noise = pd.Series(rng.integers(0, 3000, len(df)).astype(str))      # pure-noise, high-cardinality column
naive = noise.map(y.groupby(noise).mean())                                                         # target mean computed on ALL rows -> leak
print("naive target-encoded noise column AUC:", cross_val_score(LogisticRegression(), naive.to_frame(), y, cv=5, scoring="roc_auc").mean().round(3), "(fake signal!)")
print("cross-fitted TargetEncoder on same noise AUC:", cross_val_score(make_pipeline(TargetEncoder(random_state=0), LogisticRegression()), noise.to_frame(), y, cv=5, scoring="roc_auc").mean().round(3))
''')

X("m-feature-engineering",
  "Feature engineering puts domain knowledge into the inputs: ratios, differences, aggregates, time features, interactions, binned or transformed values. A well-chosen feature often beats a fancier model, especially for linear models and small data.",
  """**Families.** Ratios/rates (rooms per household), differences (price − average price in area), group aggregates (customer's mean order value via groupby-transform), date parts and cyclic encodings (sin/cos of hour so 23:00 is near 00:00), interactions (x₁·x₂ for linear models), binning (non-linear effects for linear models), log transforms, text/geo features (distance to city centre, cluster id). **Rule:** features must use only information available at prediction time and be computed inside the CV pipeline when they depend on data statistics.""",
  """**Why ratios help a linear model.** Value depends on rooms *per household*. A district with 2,000 rooms and 400 households (5/household) vs 2,000 rooms and 1,000 households (2/household) look identical on total_rooms. A linear model can't divide two features — you must hand it the ratio. Trees can approximate it, but with many splits.""",
  ["Features computed on the full dataset before splitting", "Using future information (e.g. 'total purchases this year' to predict a purchase in March)", "Engineering hundreds of features without validation", "Cyclic features as plain integers"],
  ["Linear models, small/medium tabular data, domain-rich problems"], ["Raw perceptual data (images/audio) — deep learning learns features"],
  "California housing — engineer ratios, geo-distance to major cities, location clusters, cyclic-like interactions and log transforms, and measure each group's contribution with cross-validation for linear and boosted models.",
  ["Baseline with raw features", "Add ratio features", "Add distance-to-city and location-cluster features (fit inside pipeline)", "Add log transforms and interactions", "Compare CV RMSE for each stage and both model types"],
  f'''
import numpy as np, pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
df = pd.read_csv("{HOUSING}").dropna(); df = df[df.median_house_value < 500001]; y = np.log(df.pop("median_house_value"))
raw = df.drop(columns="ocean_proximity")
def ratios(d): return d.assign(rooms_per_hh=d.total_rooms / d.households, bedrooms_ratio=d.total_bedrooms / d.total_rooms, people_per_hh=d.population / d.households)
CITIES = {{"LA": (34.05, -118.24), "SF": (37.77, -122.42), "SD": (32.72, -117.16), "SAC": (38.58, -121.49)}}
def geo(d): return d.assign(**{{f"km_{{k}}": 111 * np.hypot(d.latitude - a, (d.longitude - b) * np.cos(np.radians(a))) for k, (a, b) in CITIES.items()}}).assign(km_min=lambda t: t.filter(like="km_").min(1))
class GeoClusters(BaseEstimator, TransformerMixin):          # fitted inside CV -> no leakage
    def __init__(self, k=20): self.k = k
    def fit(self, X, y=None): self.km_ = KMeans(self.k, n_init=4, random_state=0).fit(X[["latitude", "longitude"]]); self.oh_ = OneHotEncoder().fit(self.km_.labels_[:, None]); return self
    def transform(self, X): return np.c_[X.to_numpy(), self.oh_.transform(self.km_.predict(X[["latitude", "longitude"]])[:, None]).toarray()]
def logs(d): return d.assign(**{{c: np.log1p(d[c]) for c in ["total_rooms", "total_bedrooms", "population", "households"]}}).assign(inc_x_rooms=lambda t: t.median_income * t.rooms_per_hh)
stages = {{"raw": raw, "+ratios": ratios(raw), "+geo distances": geo(ratios(raw)), "+logs & interaction": logs(geo(ratios(raw)))}}
rmse = lambda pipe, X: -cross_val_score(pipe, X, y, cv=5, scoring="neg_root_mean_squared_error").mean()
for name, Xs in stages.items():
    print(f"  {{name:20s}} Ridge {{rmse(make_pipeline(StandardScaler(), Ridge()), Xs):.4f}} | Ridge+clusters {{rmse(make_pipeline(GeoClusters(), StandardScaler(), Ridge()), Xs):.4f}} | boosting {{rmse(HistGradientBoostingRegressor(random_state=0), Xs):.4f}}")
print("(RMSE in log-dollars; 0.10 ≈ 10% typical error)")
''')

X("m-feature-selection",
  "Feature selection keeps the inputs that help and drops the ones that add noise, cost or leakage risk. Methods: **filter** (score each feature alone), **wrapper** (search subsets with a model, e.g. RFE), **embedded** (the model selects while training, e.g. L1, tree importance), plus **permutation importance** on validation data.",
  """**How each works.** Filter: ANOVA F, chi², mutual information — fast, ignores interactions. Wrapper: recursive feature elimination drops the weakest feature by model coefficient/importance and refits; or sequential forward/backward selection by CV score — expensive, can overfit the selection. Embedded: L1 drives weights to exactly zero; tree importances rank by impurity decrease (biased toward high-cardinality features). Permutation importance: drop in validation score when a column is shuffled — model-agnostic. **Selection must be inside cross-validation**; selecting on all data first gives optimistic scores (selection leakage).""",
  """**Leakage of selection by hand.** 200 random noise features, 60 rows, random labels. Pick the 10 features most correlated with the labels on all data → CV accuracy ~75%, despite pure noise. Put selection inside the CV pipeline → ~50% (chance) — the honest number.""",
  ["Selecting features on the full dataset before CV", "Trusting impurity importance for high-cardinality/continuous features", "Dropping correlated features one by one without checking interactions"],
  ["Many features relative to rows, costly features, interpretability needs"], ["When regularised models with all features already do best and cost isn't an issue"],
  "Sonar (208 sonar returns × 60 frequency-band energies: rock vs mine) — compare filter, RFE, L1, forest importance and permutation importance, all inside cross-validation, plus the selection-leakage trap on noise.",
  ["Load data; baseline with all 60 features", "Filter: SelectKBest (ANOVA/MI) for several k", "Wrapper: RFECV", "Embedded: L1 logistic and random-forest importance", "Permutation importance and the leakage demonstration"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFECV, SelectFromModel, SelectKBest, f_classif, mutual_info_classif
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
df = pd.read_csv("{SONAR}", header=None); X, y = df.iloc[:, :60].to_numpy(), (df[60] == "M").astype(int).to_numpy()
cv = StratifiedKFold(5, shuffle=True, random_state=0); lr = lambda: LogisticRegression(C=1.0, max_iter=5000)
score = lambda pipe: cross_val_score(pipe, X, y, cv=cv).mean().round(3)
print("all 60 features:", score(make_pipeline(StandardScaler(), lr())))
for k in [5, 15, 30]: print(f"filter ANOVA k={{k}}:", score(make_pipeline(StandardScaler(), SelectKBest(f_classif, k=k), lr())), "| MI:", score(make_pipeline(StandardScaler(), SelectKBest(mutual_info_classif, k=k), lr())))
rfe = RFECV(lr(), step=5, cv=cv).fit(StandardScaler().fit_transform(X), y); print("RFECV keeps", rfe.n_features_, "features")
print("embedded L1:", score(make_pipeline(StandardScaler(), SelectFromModel(LogisticRegression(penalty="l1", C=0.5, solver="liblinear")), lr())))
rf = RandomForestClassifier(300, random_state=0); print("random forest all:", score(rf), "| top-15 by importance:", score(make_pipeline(SelectFromModel(RandomForestClassifier(300, random_state=0), max_features=15, threshold=-np.inf), rf)))
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0); m = RandomForestClassifier(300, random_state=0).fit(Xtr, ytr)
pi = permutation_importance(m, Xte, yte, n_repeats=20, random_state=0); print("top permutation features (band index):", np.argsort(-pi.importances_mean)[:8])
rng = np.random.default_rng(0); N, Yn = rng.normal(size=(60, 2000)), rng.integers(0, 2, 60)
top = SelectKBest(f_classif, k=10).fit(N, Yn).get_support()
print("noise, selection BEFORE CV:", cross_val_score(lr(), N[:, top], Yn, cv=5).mean().round(2), "| selection INSIDE CV:", cross_val_score(make_pipeline(SelectKBest(f_classif, k=10), lr()), N, Yn, cv=5).mean().round(2))
''')

X("m-feature-extraction",
  "Feature extraction *creates* a smaller set of new features from raw inputs — e.g. PCA components from pixels, TF-IDF vectors from text, frequency bands from signals, embeddings from a pretrained network. Unlike selection (keep some columns), extraction transforms all of them.",
  """**Main tools.** PCA: project onto top-k eigenvectors of the covariance — linear, unsupervised, keeps maximum variance. LDA: supervised projection maximising class separation (≤ classes − 1 dims). Random projections: Johnson–Lindenstrauss — distances roughly preserved with k = O(log n/ε²) dims. Domain transforms: Fourier/wavelets for signals, HOG/edges for images, TF-IDF for text. Learned: autoencoder bottlenecks, pretrained CNN/transformer embeddings (usually the strongest today). Fit extractors on training data only.""",
  """**Compression by hand.** 8×8 digit images = 64 pixel features. PCA keeps 90% of variance with ~21 components → 3× fewer features; kNN accuracy barely drops (98.6% → 98.4%) while prediction gets faster. With 2 components you can plot all 10 digits on a page (but accuracy falls to ~60%).""",
  ["Fitting PCA on train+test", "Forgetting to scale before PCA when units differ", "Expecting PCA components to be interpretable"],
  ["High-dimensional raw data, visualisation, speeding up models, signals/text/images"], ["When original features must stay interpretable — prefer selection"],
  "Handwritten digits (1,797 real 8×8 scans bundled with scikit-learn) — extract features with PCA, LDA, random projection and simple hand-crafted image features, comparing accuracy, speed and dimensionality.",
  ["Load digits and split", "PCA: explained variance and accuracy vs number of components", "LDA (supervised) to 9 dims", "Gaussian random projection", "Hand-crafted features (row/column ink profiles) and comparison table"],
  '''
import time, numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.random_projection import GaussianRandomProjection
X, y = load_digits(return_X_y=True); Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
pca = PCA().fit(Xtr); print("components for 90% / 95% variance:", np.searchsorted(np.cumsum(pca.explained_variance_ratio_), [0.9, 0.95]) + 1)
def run(name, extractor):
    pipe = make_pipeline(extractor, KNeighborsClassifier(3)) if extractor is not None else KNeighborsClassifier(3)
    t = time.perf_counter(); pipe.fit(Xtr, ytr); acc = pipe.score(Xte, yte); dims = pipe[:-1].transform(Xte[:1]).shape[1] if extractor is not None else 64
    print(f"  {name:24s} dims {dims:3d} accuracy {acc:.3f} time {1000 * (time.perf_counter() - t):5.0f} ms")
run("raw pixels", None)
for k in [2, 10, 21]: run(f"PCA {k}", PCA(k))
run("LDA 9 (supervised)", LinearDiscriminantAnalysis(n_components=9))
run("random projection 21", GaussianRandomProjection(21, random_state=0))
from sklearn.preprocessing import FunctionTransformer
profiles = FunctionTransformer(lambda A: np.c_[A.reshape(-1, 8, 8).sum(1), A.reshape(-1, 8, 8).sum(2), (A.reshape(-1, 8, 8) > 8).sum((1, 2))])
run("ink profiles (hand-made)", profiles)
''')

X("m-imbalance",
  "When one class is rare (fraud, churn, disease), accuracy becomes misleading and models drift toward the majority. Handling imbalance means **choosing the right metric**, then using **class weights**, **resampling** (under/over/SMOTE), and **threshold tuning** based on costs.",
  """**Why it matters.** With 2% positives, predicting 'negative' always gives 98% accuracy and 0 recall. Use precision/recall, PR-AUC (baseline = positive rate), F-β, or expected cost. **Class weights** multiply each class's loss by w_c (e.g. n/(K·n_c)) — equivalent in expectation to oversampling. **SMOTE** creates synthetic positives by interpolating between a positive and one of its k nearest positive neighbours: x_new = x + u·(x_nn − x), u ~ U(0,1). Resampling must happen **only on training folds** (imblearn Pipeline). Resampling/weights distort predicted probabilities — recalibrate or adjust the threshold. Often, threshold tuning alone does as well as resampling.""",
  """**Threshold by hand.** Missing a churner costs 5× a false alarm. Optimal threshold for calibrated probabilities = c_FP/(c_FP + c_FN) = 1/(1 + 5) = **0.167**. With class weights 5:1 you'd shift the model instead; doing both double-counts.""",
  ["Reporting accuracy on imbalanced data", "Oversampling before splitting (duplicates leak into validation)", "Using weights AND a shifted threshold (double correction)", "Trusting probabilities after resampling"],
  ["Rare-event detection: fraud, churn, defects, disease"], ["Mildly imbalanced data (60/40) — usually just pick the right metric"],
  "IBM Telco churn (26.5% churners) made harder by subsampling churners to 5% — compare doing nothing, class weights, random over/under-sampling, SMOTE and threshold tuning on PR-AUC, recall and cost.",
  ["Create a strongly imbalanced version of the data", "Baseline model and why accuracy misleads", "Class weights", "Resampling inside imblearn pipelines (over, under, SMOTE)", "Cost-based threshold tuning and comparison table"],
  f'''
import numpy as np, pandas as pd
from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.pipeline import make_pipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
{LOAD_TELCO}
rng = np.random.default_rng(0); keep = (y == 0) | (rng.random(len(y)) < 0.15); df, y = df[keep], y[keep]
print(f"positives: {{y.mean():.1%}} of {{len(y)}} -> 'always no churn' accuracy {{1 - y.mean():.3f}}")
num = ["tenure", "MonthlyCharges", "TotalCharges"]; prep = make_column_transformer((StandardScaler(), num), (OneHotEncoder(handle_unknown="ignore"), [c for c in df if c not in num]))
Xtr, Xte, ytr, yte = train_test_split(df, y, test_size=0.3, stratify=y, random_state=0)
C_FN, C_FP = 5, 1
cost = lambda pred: ((pred == 0) & (yte == 1)).sum() * C_FN + ((pred == 1) & (yte == 0)).sum() * C_FP
variants = {{"nothing": [], "class weights": "w", "random oversample": [RandomOverSampler(random_state=0)], "random undersample": [RandomUnderSampler(random_state=0)], "SMOTE": [SMOTE(random_state=0)]}}
for name, v in variants.items():
    clf = LogisticRegression(max_iter=3000, class_weight="balanced" if v == "w" else None)
    pipe = make_pipeline(prep, *(v if isinstance(v, list) else []), clf).fit(Xtr, ytr); p = pipe.predict_proba(Xte)[:, 1]
    print(f"  {{name:18s}} PR-AUC {{average_precision_score(yte, p):.3f}} | @0.5 recall {{recall_score(yte, p > 0.5):.2f}} cost {{cost((p > 0.5).astype(int)):4d}}")
    if name == "nothing": base_p = p
t = C_FP / (C_FP + C_FN); print(f"  nothing + cost threshold {{t:.3f}}: recall {{recall_score(yte, base_p > t):.2f}} cost {{cost((base_p > t).astype(int)):4d}}  <- often all you need")
''')

X("m-train-val-test",
  "To estimate how a model will do on new data, you must evaluate it on data it never learned from. The **training set** fits parameters, the **validation set** (or cross-validation) picks models and hyperparameters, and the **test set** is touched once at the end for an honest estimate.",
  """**Schemes.** Hold-out (e.g. 60/20/20). **k-fold CV:** k models, each validated on one fold; average score ± sd; variance of the estimate falls with k, cost rises. **Stratified** folds preserve class ratios. **Group k-fold** keeps all rows of a patient/customer in one fold (else the model memorises the person). **Time series split:** always train on the past, validate on the future (expanding window). **Nested CV:** inner loop tunes, outer loop estimates — the honest estimate when tuning. Each time you look at the test set and change something, it becomes a validation set.""",
  """**Variance of a hold-out.** Test set of 200 with 80% accuracy → SE = √(0.8·0.2/200) = 2.8 points; two random splits can differ by ±5 points. 5-fold CV uses all 1,000 rows for validation → SE ≈ 1.3 points. That's why small datasets need CV.""",
  ["Tuning on the test set", "Random splits for time-ordered data", "Same person/customer in train and test", "Preprocessing on all data before splitting"],
  ["Every supervised project"], ["Plain random k-fold for grouped or temporal data"],
  "California housing (random + stratified + geographic groups) and airline passengers (time) — compare hold-out variability, k-fold, stratified, group and time-series splits, and nested CV.",
  ["Hold-out variability across seeds", "k-fold CV and stratification on income category", "Group k-fold by location block (spatial leakage)", "Time-series split on a real series", "Nested CV for an honest tuned estimate"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, GroupKFold, KFold, StratifiedKFold, TimeSeriesSplit, cross_val_score, train_test_split
df = pd.read_csv("{HOUSING}").dropna().sample(6000, random_state=0); y = df.median_house_value / 1e5
X = df[["median_income", "housing_median_age", "total_rooms", "population", "latitude", "longitude"]]
rf = RandomForestRegressor(100, min_samples_leaf=3, n_jobs=-1, random_state=0)
holdout = [rf.fit(*train_test_split(X, y, random_state=s)[0::2]).score(*train_test_split(X, y, random_state=s)[1::2]) for s in range(5)]
print("hold-out R² across 5 seeds:", np.round(holdout, 3))
print("5-fold R²: %.3f ± %.3f" % (lambda s: (s.mean(), s.std()))(cross_val_score(rf, X, y, cv=KFold(5, shuffle=True, random_state=0))))
inc_cat = pd.cut(df.median_income, [0, 1.5, 3, 4.5, 6, np.inf], labels=False)
print("stratified folds keep income mix:", [np.bincount(inc_cat.iloc[te], minlength=5).round(-1).tolist() for _, te in StratifiedKFold(3, shuffle=True, random_state=0).split(X, inc_cat)])
blocks = (df.latitude // 0.5).astype(str) + "_" + (df.longitude // 0.5).astype(str)
print("random KFold R² %.3f vs GroupKFold by location block %.3f (spatial leakage inflates random CV)" % (cross_val_score(rf, X, y, cv=KFold(5, shuffle=True, random_state=0)).mean(), cross_val_score(rf, X, y, cv=GroupKFold(5), groups=blocks).mean()))
air = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"); s = air.Passengers.to_numpy(float)
lags = pd.DataFrame({{f"lag{{k}}": np.roll(s, k) for k in (1, 2, 12)}})[12:]; target = s[12:]
for name, cv in [("shuffled KFold (wrong)", KFold(5, shuffle=True, random_state=0)), ("TimeSeriesSplit", TimeSeriesSplit(5))]:
    print(f"  airline {{name:22s}} MAE {{-cross_val_score(Ridge(), lags, target, cv=cv, scoring='neg_mean_absolute_error').mean():.1f}}")
inner = GridSearchCV(Ridge(), {{"alpha": [0.1, 1, 10, 100]}}, cv=3)
print("nested CV R² (tune inside, estimate outside): %.3f" % cross_val_score(inner, X, y, cv=KFold(5, shuffle=True, random_state=1)).mean())
''')

X("m-leakage",
  "Data leakage is when information that won't be available at prediction time sneaks into training — through features, preprocessing or splits. It produces wonderful validation scores and terrible real-world performance. It is the most common serious bug in applied ML.",
  """**Kinds.** (1) **Target leakage:** a feature that is a consequence of the label (e.g. 'refund issued' to predict churn; 'TotalCharges' at the end of contract). (2) **Train–test contamination:** scaling/imputing/selecting/encoding using all data before the split. (3) **Temporal leakage:** random splits on time data, features using future values (rolling means centred in time). (4) **Group leakage:** the same entity in train and test (patients, images of the same object, near-duplicate rows). **Detection:** suspiciously high scores, one feature dominating importance, big gap between offline and online performance. **Prevention:** pipelines, split first, time-aware features, group splits, a 'feature timestamp ≤ prediction timestamp' rule.""",
  """**Spot it.** A hospital readmission model has AUC 0.99; its top feature is 'discharge_followup_scheduled', which nurses fill in *after* deciding the patient is high-risk. The model learned the nurses' decision, not the risk — at prediction time that field is empty.""",
  ["fit_transform on the full dataset", "Target/mean encoding without cross-fitting", "Shuffled CV on time series", "Duplicate or near-duplicate rows across splits", "Features recorded after the outcome"],
  ["Audit every project for it — especially when results look too good"], ["Assuming a high score means a good model"],
  "Pima diabetes and Titanic — reproduce four leak types (preprocessing before split, feature selection before CV, target leakage via a post-outcome feature, duplicate rows across splits) and show the honest numbers after fixing each.",
  ["Honest baseline with a pipeline", "Leak 1: selection on all data with added noise features", "Leak 2: a post-outcome feature", "Leak 3: duplicates across folds", "Fix each with pipelines/group splits and compare"],
  f'''
import numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
df = pd.read_csv("{PIMA}", names={PIMA_COLS}); X, y = df.drop(columns="diabetes"), df.diabetes
lr = lambda: LogisticRegression(max_iter=5000); cv = KFold(5, shuffle=True, random_state=0)
print("honest pipeline AUC:", cross_val_score(make_pipeline(StandardScaler(), lr()), X, y, cv=cv, scoring="roc_auc").mean().round(3))
rng = np.random.default_rng(0); Xn = np.c_[StandardScaler().fit_transform(X), rng.normal(size=(len(X), 3000))]
sel = SelectKBest(f_classif, k=30).fit(Xn, y).get_support()
print("LEAK selection before CV:", cross_val_score(lr(), Xn[:, sel], y, cv=cv, scoring="roc_auc").mean().round(3), "| fixed:", cross_val_score(make_pipeline(SelectKBest(f_classif, k=30), lr()), Xn, y, cv=cv, scoring="roc_auc").mean().round(3))
post = X.assign(on_metformin=(y == 1) & (rng.random(len(y)) < 0.7))           # recorded AFTER diagnosis
print("LEAK post-outcome feature:", cross_val_score(make_pipeline(StandardScaler(), lr()), post, y, cv=cv, scoring="roc_auc").mean().round(3), "-> drop features recorded after the label")
patients = np.arange(len(X)); idx = np.r_[patients, rng.choice(patients, 400)]                # 400 duplicated visits of the same patients
Xd, yd, groups = X.iloc[idx].reset_index(drop=True), y.iloc[idx].reset_index(drop=True), idx
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(300, random_state=0)
print("LEAK duplicates across folds (RF):", cross_val_score(rf, Xd, yd, cv=cv, scoring="roc_auc").mean().round(3), "| GroupKFold by patient:", cross_val_score(rf, Xd, yd, cv=GroupKFold(5), groups=groups, scoring="roc_auc").mean().round(3))
''')

X("m-overfitting",
  "Overfitting = the model memorises training data quirks (noise) instead of the pattern, so it does great on training data and worse on new data. Underfitting = the model is too simple to capture the pattern at all. The goal is the sweet spot, found with validation curves.",
  """**Signals.** Train score ≫ validation score (overfit); both low and close (underfit). **Validation curve:** score vs a complexity knob (tree depth, polynomial degree, k in kNN, epochs). **Remedies for overfitting:** more data, simpler model, regularisation (L1/L2, dropout, weight decay), early stopping, data augmentation, ensembling/bagging, feature selection. **Remedies for underfitting:** more features/capacity, less regularisation, longer training. Also: overfitting the *validation set* through many experiments — keep a final test set.""",
  """**Polynomial by hand.** 10 noisy points from a curve. Degree 1: train MSE 4.0, val 4.2 (underfit). Degree 3: 1.1 / 1.3 (good). Degree 9: train 0.0 (passes through every point), val 25 (wild oscillations) — perfect memory, no generalisation.""",
  ["Celebrating training accuracy", "Reusing the test set until it looks good", "Early stopping on the test set", "Comparing models whose validation scores differ by less than noise"],
  ["Always plot train vs validation as complexity grows"], ["Assuming deep nets always overfit — with enough data and regularisation they generalise"],
  "MPG cars (horsepower → mpg) and Titanic — validation curves for polynomial degree, tree depth and kNN k; detect over/underfitting; fix overfitting with regularisation and early stopping on a neural network.",
  ["Polynomial degrees 1–12: train vs validation error", "Tree depth validation curve on Titanic", "kNN k from 1 to 100", "Neural net with and without early stopping", "Pick the sweet spot and confirm on a held-out test set"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, validation_curve
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.tree import DecisionTreeClassifier
mpg = pd.read_csv("{MPG}").dropna().sample(60, random_state=1); x, t = mpg[["horsepower"]], mpg.mpg
deg = [1, 2, 3, 6, 10, 14]; tr, va = validation_curve(make_pipeline(StandardScaler(), PolynomialFeatures(), LinearRegression()), x, t, param_name="polynomialfeatures__degree", param_range=deg, cv=5, scoring="neg_mean_squared_error")
for d, a, b in zip(deg, -tr.mean(1), -va.mean(1)): print(f"  degree {{d:2d}}: train MSE {{a:7.1f}} | validation MSE {{b:12.1f}}")
ti = pd.read_csv("{TITANIC}"); ti["Age"] = ti.Age.fillna(ti.Age.median()); ti["Female"] = (ti.Sex == "female").astype(int)
X, y = ti[["Female", "Pclass", "Age", "SibSp", "Parch", "Fare"]], ti.Survived
depths = [1, 2, 3, 5, 8, 12, 20]; tr, va = validation_curve(DecisionTreeClassifier(random_state=0), X, y, param_name="max_depth", param_range=depths, cv=5)
print("tree depth:", {{d: (round(float(a), 3), round(float(b), 3)) for d, a, b in zip(depths, tr.mean(1), va.mean(1))}})
ks = [1, 5, 15, 50, 150]; tr, va = validation_curve(make_pipeline(StandardScaler(), KNeighborsClassifier()), X, y, param_name="kneighborsclassifier__n_neighbors", param_range=ks, cv=5)
print("kNN k (train, val):", {{k: (round(float(a), 3), round(float(b), 3)) for k, a, b in zip(ks, tr.mean(1), va.mean(1))}})
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
for es in [False, True]:
    nn = make_pipeline(StandardScaler(), MLPClassifier((256, 256), alpha=0 if not es else 1e-3, max_iter=2000, early_stopping=es, random_state=0)).fit(Xtr, ytr)
    print(f"  MLP early_stopping={{es}}: train {{nn.score(Xtr, ytr):.3f}} test {{nn.score(Xte, yte):.3f}} epochs {{nn[-1].n_iter_}}")
''')

X("m-regularization",
  "Regularisation adds a preference for simpler models to the training objective, trading a little training fit for better generalisation. **L2 (Ridge)** shrinks all weights, **L1 (Lasso)** sets some to exactly zero, **Elastic Net** mixes both; in deep learning, weight decay, dropout, early stopping and augmentation play the same role.",
  """**Objectives.** Ridge: min ‖Xw − y‖² + λ‖w‖₂² → closed form w = (XᵀX + λI)⁻¹Xᵀy; shrinks along directions with small singular values most (σ²/(σ² + λ) factor) — stabilises collinear features. Lasso: min ½‖Xw − y‖² + λ‖w‖₁ → no closed form; coordinate descent with **soft-thresholding** wⱼ = S(ρⱼ, λ)/zⱼ where S(ρ, λ) = sign(ρ)·max(|ρ| − λ, 0) — weights inside ±λ become exactly 0. Bayesian view: L2 = Gaussian prior, L1 = Laplace prior on weights. λ (alpha) is chosen by CV; features must be scaled so the penalty treats them equally.""",
  """**Soft-thresholding by hand.** λ = 1. A coordinate with ρ = 3 → 3 − 1 = **2**; ρ = −0.5 → **0** (killed); ρ = −2.5 → **−1.5**. **Ridge shrink factor:** a direction with σ² = 100 and λ = 10 keeps 100/110 = 91% of its coefficient; one with σ² = 1 keeps 1/11 = 9%.""",
  ["Regularising without scaling features", "Penalising the intercept", "Choosing λ on the test set", "Interpreting Lasso's chosen subset as 'the true' features when they're correlated"],
  ["Many/correlated features, small data, polynomial expansions, all neural nets"], ["When you need unbiased coefficient estimates for inference (use proper statistical models)"],
  "California housing with degree-3 polynomial features (~200 columns) — unregularised regression vs Ridge, Lasso and Elastic Net across α, coefficient paths, CV-chosen α, and Lasso via soft-thresholding coordinate descent from scratch.",
  ["Create a high-capacity polynomial feature set", "Overfit with plain least squares", "Ridge/Lasso/ElasticNet with CV-chosen α", "Coefficient sparsity along the Lasso path", "Implement Lasso coordinate descent and match sklearn"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import ElasticNetCV, Lasso, LassoCV, LinearRegression, RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
df = pd.read_csv("{HOUSING}").dropna().sample(3000, random_state=0); y = np.log(df.median_house_value)
X = df[["median_income", "housing_median_age", "total_rooms", "total_bedrooms", "population", "households", "latitude", "longitude"]]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0)
poly = make_pipeline(PolynomialFeatures(3, include_bias=False), StandardScaler()).fit(Xtr); A, B = poly.transform(Xtr), poly.transform(Xte); print("features:", A.shape[1])
rmse = lambda m: np.sqrt(np.mean((m.predict(B) - yte) ** 2))
models = {{"no regularisation": LinearRegression(), "RidgeCV": RidgeCV(np.logspace(-3, 3, 13)), "LassoCV": LassoCV(alphas=30, cv=5, max_iter=20000, random_state=0),
          "ElasticNetCV": ElasticNetCV(l1_ratio=[0.2, 0.5, 0.9], alphas=30, cv=5, max_iter=20000, random_state=0)}}
for name, m in models.items():
    m.fit(A, ytr); nz = int((np.abs(m.coef_) > 1e-6).sum()); print(f"  {{name:18s}} train RMSE {{np.sqrt(np.mean((m.predict(A) - ytr) ** 2)):.3f}} test RMSE {{rmse(m):.3f}} non-zero coefs {{nz:3d}} alpha {{round(float(getattr(m, 'alpha_', 0)), 4) or '-'}}")
for a in [1e-4, 1e-3, 1e-2, 1e-1]: print(f"  Lasso alpha {{a:g}}: non-zero {{int((Lasso(alpha=a, max_iter=50000).fit(A, ytr).coef_ != 0).sum())}}")
def lasso_cd(Xm, t, lam, iters=3000):
    n, p = Xm.shape; w = np.zeros(p); b = t.mean(); z = (Xm ** 2).sum(0) / n; r = t - b
    for _ in range(iters):
        for j in range(p):
            r += Xm[:, j] * w[j]; rho = Xm[:, j] @ r / n
            w[j] = np.sign(rho) * max(abs(rho) - lam, 0) / z[j]; r -= Xm[:, j] * w[j]
    return w
S = A[:, :20]; mine = lasso_cd(S, ytr.to_numpy(), 0.01); ref = Lasso(alpha=0.01, max_iter=100000, tol=1e-10).fit(S, ytr).coef_
print("soft-thresholding coordinate descent matches sklearn:", np.allclose(mine, ref, atol=1e-4), "| zeros:", int((mine == 0).sum()), "of 20")
''')

X("m-metrics-clf",
  "Classification metrics answer different questions: **accuracy** (overall right), **precision** (when we say yes, how often right), **recall** (of real yeses, how many caught), **F1** (balance), **ROC-AUC** (ranking quality), **PR-AUC** (ranking for the rare class), **log-loss/Brier** and **calibration** (are probabilities trustworthy). Pick by the cost of each mistake.",
  """**Definitions** from the confusion matrix (TP, FP, FN, TN): precision = TP/(TP+FP); recall (sensitivity, TPR) = TP/(TP+FN); specificity = TN/(TN+FP); FPR = 1 − specificity; F_β = (1+β²)PR/(β²P + R) (β > 1 favours recall). ROC curve: TPR vs FPR over thresholds; AUC = P(random positive scored above random negative); insensitive to class balance — can look great on rare classes while precision is poor, so also use PR-AUC. **Multiclass:** macro (average per class, treats classes equally) vs weighted vs micro. **Calibration:** among cases predicted 0.7, ~70% should be positive; check with reliability curves; fix with Platt/isotonic.""",
  """**By hand.** 1,000 patients, 100 sick. Model flags 120: 80 sick (TP) + 40 healthy (FP); misses 20 (FN); TN = 860. Accuracy = 940/1000 = **94%**; precision = 80/120 = **0.667**; recall = 80/100 = **0.80**; F1 = 2·0.667·0.8/1.467 = **0.727**; specificity = 860/900 = 0.956.""",
  ["Accuracy on imbalanced data", "Comparing F1 at different thresholds without saying so", "Using ROC-AUC alone for rare positives", "Treating scores as calibrated probabilities"],
  ["Precision when false alarms are costly; recall when misses are costly; AUC for ranking; log-loss/Brier for probabilities"], ["A single number without the confusion matrix"],
  "Pima diabetes — full evaluation of a classifier: confusion matrix and every metric by hand vs sklearn, threshold sweep, ROC and PR curves, calibration curve and isotonic recalibration, plus a multiclass report on penguins.",
  ["Train a model and get test probabilities", "Confusion matrix and metrics by hand", "Threshold sweep: precision/recall/F1 trade-off", "ROC-AUC, PR-AUC, log-loss, Brier, calibration", "Multiclass macro vs weighted metrics"],
  f'''
import numpy as np, pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, classification_report, confusion_matrix, f1_score, log_loss, roc_auc_score
from sklearn.model_selection import cross_val_predict, train_test_split
df = pd.read_csv("{PIMA}", names={PIMA_COLS}); X, y = df.drop(columns="diabetes"), df.diabetes
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
rf = RandomForestClassifier(300, min_samples_leaf=3, random_state=0).fit(Xtr, ytr); p = rf.predict_proba(Xte)[:, 1]
tn, fp, fn, tp = confusion_matrix(yte, p > 0.5).ravel(); P, R = tp / (tp + fp), tp / (tp + fn)
print(f"TP {{tp}} FP {{fp}} FN {{fn}} TN {{tn}} | accuracy {{(tp + tn) / len(yte):.3f}} precision {{P:.3f}} recall {{R:.3f}} F1 {{2 * P * R / (P + R):.3f}} (sklearn F1 {{f1_score(yte, p > 0.5):.3f}})")
for t in [0.2, 0.35, 0.5, 0.65]:
    tn, fp, fn, tp = confusion_matrix(yte, p > t).ravel(); print(f"  threshold {{t}}: precision {{tp / (tp + fp):.2f}} recall {{tp / (tp + fn):.2f}} flagged {{tp + fp}}")
print(f"ROC-AUC {{roc_auc_score(yte, p):.3f}} | PR-AUC {{average_precision_score(yte, p):.3f}} (baseline {{yte.mean():.3f}}) | log-loss {{log_loss(yte, p):.3f}} | Brier {{brier_score_loss(yte, p):.3f}}")
frac, mean_pred = calibration_curve(yte, p, n_bins=5); print("calibration (predicted -> observed):", list(zip(mean_pred.round(2).tolist(), frac.round(2).tolist())))
cal = CalibratedClassifierCV(RandomForestClassifier(300, min_samples_leaf=3, random_state=0), method="isotonic", cv=5).fit(Xtr, ytr)
print(f"after isotonic calibration: Brier {{brier_score_loss(yte, cal.predict_proba(Xte)[:, 1]):.3f}}")
pg = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv").dropna()
pred = cross_val_predict(LogisticRegression(max_iter=3000), pg[["bill_depth_mm", "flipper_length_mm"]], pg.species, cv=5)
print(classification_report(pg.species, pred, digits=3))
''')

X("m-metrics-reg",
  "Regression metrics measure how far predictions are from the truth: **MAE** (typical absolute error), **RMSE** (punishes big errors), **R²** (share of variance explained), **MAPE/sMAPE** (relative error), and quantile/pinball loss for intervals. Choose the one that matches how errors cost money, and always look at residuals.",
  """**Definitions.** MAE = mean|y − ŷ| (optimal constant: median). RMSE = √mean(y − ŷ)² (optimal constant: mean); RMSE ≥ MAE, and a big ratio indicates heavy-tailed errors. R² = 1 − SS_res/SS_tot — 0 means 'as good as predicting the mean', negative is worse. MAPE = mean|y − ŷ|/|y| — explodes near zero, asymmetric. RMSLE = RMSE on log(1 + y) — relative errors, for targets spanning orders of magnitude. **Pinball loss** for quantile q: q·(y − ŷ) if y ≥ ŷ else (1 − q)(ŷ − y) — training with it gives prediction intervals. Report metrics per segment; averages hide failures.""",
  """**By hand.** y = [100, 200, 300], ŷ = [110, 190, 360]. Errors 10, −10, 60. MAE = 80/3 = **26.7**; RMSE = √((100 + 100 + 3600)/3) = √1267 = **35.6**; MAPE = (10% + 5% + 20%)/3 = **11.7%**; ȳ = 200, SS_tot = 20000, SS_res = 3800 → R² = **0.81**.""",
  ["Using MAPE with values near zero", "Reporting R² on training data", "Comparing RMSE across different target scales", "Ignoring residual patterns (heteroscedasticity, bias by segment)"],
  ["MAE for interpretable typical error, RMSE when big misses hurt, RMSLE for multiplicative targets, pinball for intervals"], ["R² alone (a model can have high R² and be useless where it matters)"],
  "California housing — train a model and compute MAE/RMSE/R²/MAPE/RMSLE by hand and with sklearn, inspect residuals by segment, and build an 80% prediction interval with quantile (pinball) gradient boosting.",
  ["Train a model on log-price", "Compute every metric by hand and verify", "Residuals by income segment and by price level", "Quantile models for 10th/90th percentiles", "Check interval coverage and width"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_pinball_loss, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
df = pd.read_csv("{HOUSING}").dropna(); df = df[df.median_house_value < 500001]; y = df.pop("median_house_value"); X = pd.get_dummies(df, dtype=float)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0)
m = HistGradientBoostingRegressor(random_state=0).fit(Xtr, np.log(ytr)); pred = np.exp(m.predict(Xte)); e = yte - pred
print(f"MAE  ${{np.abs(e).mean():,.0f}} (sklearn {{mean_absolute_error(yte, pred):,.0f}})")
print(f"RMSE ${{np.sqrt((e ** 2).mean()):,.0f}} (sklearn {{root_mean_squared_error(yte, pred):,.0f}}) -> RMSE/MAE = {{np.sqrt((e ** 2).mean()) / np.abs(e).mean():.2f}}")
print(f"R²   {{1 - (e ** 2).sum() / ((yte - yte.mean()) ** 2).sum():.3f}} (sklearn {{r2_score(yte, pred):.3f}}) | MAPE {{mean_absolute_percentage_error(yte, pred):.1%}} | RMSLE {{np.sqrt(np.mean((np.log1p(pred) - np.log1p(yte)) ** 2)):.3f}}")
seg = pd.qcut(Xte.median_income, 4, labels=["low", "mid-low", "mid-high", "high"])
print(pd.DataFrame({{"MAE": np.abs(e), "bias": e, "APE": np.abs(e) / yte}}).groupby(seg, observed=True).mean().round(3))
q = {{a: HistGradientBoostingRegressor(loss="quantile", quantile=a, random_state=0).fit(Xtr, ytr).predict(Xte) for a in (0.1, 0.9)}}
print(f"80% interval coverage {{((yte >= q[0.1]) & (yte <= q[0.9])).mean():.1%}} | median width ${{np.median(q[0.9] - q[0.1]):,.0f}} | pinball@0.9 {{mean_pinball_loss(yte, q[0.9], alpha=0.9):,.0f}}")
''')

X("m-hyperparams",
  "Hyperparameters are the settings you choose before training (tree depth, learning rate, regularisation strength). Tuning searches for good values using validation data: **grid search**, **random search**, **successive halving** and **Bayesian optimisation** (Optuna). Good tuning is systematic, cross-validated and budgeted.",
  """**Why random beats grid:** if only 2 of 6 hyperparameters matter, a 64-point grid tests just 8 distinct values of each; 64 random points test 64 distinct values of each. **Successive halving:** start many configs on a small budget (data/iterations), keep the best 1/η, multiply budget by η — Hyperband runs several such brackets. **Bayesian optimisation (TPE in Optuna):** model which regions gave good scores and sample there more; with pruning of bad trials. Search learning rates and regularisation on a **log scale**. Final estimate must come from data not used for tuning (nested CV or test set).""",
  """**Budget by hand.** Grid of 5 depths × 5 learning rates × 4 leaf sizes = 100 configs × 5-fold = 500 fits. Successive halving with η = 3 starting from 81 configs on 1/27 of the data: 81 → 27 → 9 → 3 → 1, total work ≈ 4 full-data equivalents per survivor round — roughly 10× cheaper for a similar result.""",
  ["Tuning on the test set", "Linear grids for learning rates", "Huge grids with no budget", "Not fixing seeds / ignoring score variance between configs"],
  ["After a baseline works; tune the few parameters that matter most"], ["Spending days tuning before fixing data and features"],
  "IBM Telco churn — tune gradient boosting with grid search, random search, successive halving and Optuna (TPE) under similar budgets; compare best CV AUC, time and the final held-out test score.",
  ["Prepare a leak-free pipeline", "Grid search", "Random search with log-uniform distributions", "HalvingRandomSearchCV", "Optuna TPE; final evaluation on the test set"],
  f'''
import time, numpy as np, pandas as pd, optuna
from scipy.stats import loguniform, randint
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.experimental import enable_halving_search_cv  # noqa: F401
from sklearn.model_selection import GridSearchCV, HalvingRandomSearchCV, RandomizedSearchCV, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder
{LOAD_TELCO}
cat = [c for c in df if not pd.api.types.is_numeric_dtype(df[c])]; Xtr, Xte, ytr, yte = train_test_split(df, y, test_size=0.25, stratify=y, random_state=0)
pipe = make_pipeline(make_column_transformer((OrdinalEncoder(), cat), remainder="passthrough"), HistGradientBoostingClassifier(random_state=0))
P = "histgradientboostingclassifier__"; results = {{}}
def run(name, search):
    t = time.perf_counter(); search.fit(Xtr, ytr); results[name] = (search.best_score_, time.perf_counter() - t, search.best_estimator_)
run("grid (27)", GridSearchCV(pipe, {{P + "learning_rate": [0.03, 0.1, 0.3], P + "max_depth": [3, 6, None], P + "min_samples_leaf": [20, 50, 100]}}, cv=3, scoring="roc_auc"))
dist = {{P + "learning_rate": loguniform(0.01, 0.5), P + "max_depth": randint(2, 10), P + "min_samples_leaf": randint(10, 200), P + "l2_regularization": loguniform(1e-4, 10)}}
run("random (27)", RandomizedSearchCV(pipe, dist, n_iter=27, cv=3, scoring="roc_auc", random_state=0))
run("halving random (81→1)", HalvingRandomSearchCV(pipe, dist, n_candidates=81, factor=3, min_resources=400, cv=3, scoring="roc_auc", random_state=0))
optuna.logging.set_verbosity(optuna.logging.WARNING)
def objective(trial):
    pipe.set_params(**{{P + "learning_rate": trial.suggest_float("lr", 0.01, 0.5, log=True), P + "max_depth": trial.suggest_int("depth", 2, 10),
                       P + "min_samples_leaf": trial.suggest_int("leaf", 10, 200), P + "l2_regularization": trial.suggest_float("l2", 1e-4, 10, log=True)}})
    return cross_val_score(pipe, Xtr, ytr, cv=3, scoring="roc_auc").mean()
t = time.perf_counter(); study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0)); study.optimize(objective, n_trials=27)
objective(study.best_trial); results["optuna TPE (27)"] = (study.best_value, time.perf_counter() - t, pipe.fit(Xtr, ytr))
for name, (cvs, secs, est) in results.items():
    print(f"  {{name:16s}} CV AUC {{cvs:.4f}} | {{secs:5.1f}} s | test AUC {{__import__('sklearn.metrics', fromlist=['x']).roc_auc_score(yte, est.predict_proba(Xte)[:, 1]):.4f}}")
print("optuna best params:", {{k: round(v, 4) if isinstance(v, float) else v for k, v in study.best_params.items()}})
''')

X("m-separability",
  "Two classes are **linearly separable** if a straight line (hyperplane) can split them perfectly. When they aren't, you can (a) transform features so they become separable (polynomials, kernels, learned hidden layers), or (b) accept a soft boundary with some errors. This single idea explains perceptrons, SVM kernels and why neural networks need hidden layers.",
  """**Formally.** Separable ⇔ ∃ w, b: yᵢ(w·xᵢ + b) > 0 ∀i. The perceptron converges in ≤ (R/γ)² updates on separable data (R = data radius, γ = margin) and never converges otherwise. **XOR** is the classic non-separable case: no line splits (0,0),(1,1) from (0,1),(1,0); adding the product feature x₁x₂ makes it separable in 3-D. **Cover's theorem:** mapping data to a higher-dimensional space makes linear separation more likely. Kernels do this implicitly; hidden layers learn the mapping.""",
  """**XOR by hand.** Add z = x₁·x₂: points become (0,0,0)→0, (1,1,1)→0, (0,1,0)→1, (1,0,0)→1. The plane x₁ + x₂ − 2z = 0.5 separates them: class-1 points give 1 > 0.5, class-0 points give 0 and 0 (1 + 1 − 2 = 0) < 0.5 ✓.""",
  ["Assuming more epochs will fix a non-separable perceptron", "Adding huge polynomial expansions without regularisation", "Confusing 'not separable' with 'not learnable'"],
  ["Diagnosing whether you need non-linear features/models"], ["Forcing a hard-margin classifier on noisy, overlapping data"],
  "Penguins — check which species pairs are linearly separable in 2 features (perceptron convergence), then a real non-linear case: species from bill measurements as XOR-like structure, solved with feature maps, an RBF kernel and an MLP.",
  ["Pick 2-D feature pairs and test separability with a perceptron", "Measure margin with a hard-margin linear SVM", "Create a non-separable task (Chinstrap vs rest)", "Fix with polynomial features, RBF SVM and an MLP", "Compare decision accuracy"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.model_selection import cross_val_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.svm import SVC
df = pd.read_csv("{PENGUINS}").dropna(); f2 = ["bill_length_mm", "bill_depth_mm"]
for a, b in [("Adelie", "Gentoo"), ("Adelie", "Chinstrap"), ("Chinstrap", "Gentoo")]:
    d = df[df.species.isin([a, b])]; X = StandardScaler().fit_transform(d[f2]); y = (d.species == a).astype(int)
    p = Perceptron(max_iter=1000, tol=None, random_state=0).fit(X, y); svm = SVC(kernel="linear", C=1e6).fit(X, y)
    print(f"{{a:9s}} vs {{b:9s}}: perceptron train acc {{p.score(X, y):.3f}} | hard-margin SVM acc {{svm.score(X, y):.3f}}, margin {{2 / np.linalg.norm(svm.coef_):.3f}}")
X = df[f2]; y = (df.species == "Chinstrap").astype(int)        # Chinstrap sits 'between' the others: long bill AND deep bill
print("Chinstrap vs rest (XOR-like):")
for name, m in [("linear logistic", make_pipeline(StandardScaler(), LogisticRegression())),
                ("+ product feature", make_pipeline(StandardScaler(), PolynomialFeatures(2, interaction_only=True), LogisticRegression())),
                ("polynomial degree 3", make_pipeline(StandardScaler(), PolynomialFeatures(3), LogisticRegression(max_iter=5000))),
                ("RBF-kernel SVM", make_pipeline(StandardScaler(), SVC(C=10))), ("MLP 16 hidden", make_pipeline(StandardScaler(), MLPClassifier((16,), max_iter=3000, random_state=0)))]:
    print(f"  {{name:20s}} CV accuracy {{cross_val_score(m, X, y, cv=5).mean():.3f}}")
Xx = np.array([[0, 0], [1, 1], [0, 1], [1, 0]]); yx = np.array([0, 0, 1, 1])
print("XOR perceptron:", Perceptron(max_iter=1000, tol=None).fit(Xx, yx).score(Xx, yx), "| with x1*x2:", Perceptron(max_iter=1000, tol=None).fit(np.c_[Xx, Xx[:, 0] * Xx[:, 1]], yx).score(np.c_[Xx, Xx[:, 0] * Xx[:, 1]], yx))
''')
