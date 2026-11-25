"""Beginner lessons: ML foundations & data."""
from lesson_util import L

L("m-ai-overview",
  "AI is the goal, machine learning is the main way to reach it, deep learning and generative AI are kinds of machine learning.",
  """You will hear "AI", "ML", "deep learning" and "GenAI" used as if they mean the same thing. They don't, and interviewers often start with exactly this question. Knowing how they nest tells you which tools belong to which problem.""",
  """Think of four boxes, each inside the one before.

- **Artificial intelligence (AI)** is the big goal: a computer doing something that normally needs human intelligence, such as playing chess, translating or recognising a face.
- **Machine learning (ML)** is one way to get there. Instead of a programmer writing every rule, the computer **learns the rules from examples**.
- **Deep learning (DL)** is machine learning that uses large **neural networks** with many layers. It is what made images, speech and text work so well after about 2012.
- **Generative AI (GenAI)** is deep learning that **creates new content**: text (ChatGPT, Claude), images (Stable Diffusion), audio or code.""",
  [("A rule-based program (AI, but not ML)",
    """A spam filter written by hand: `if "free money" in email: mark as spam`. A person wrote the rule. It works until spammers write "fr3e m0ney"."""),
   ("A learning program (ML)",
    """Give the computer 10,000 emails already marked spam or not spam. It finds for itself that words like "winner", "urgent" and many exclamation marks raise the chance of spam, and it keeps learning when new examples arrive."""),
   ("Deep learning and generative AI",
    """A deep network reads the raw pixels of a photo and says "cat" without anyone describing ears or whiskers. A generative model goes further: you type "a cat wearing sunglasses" and it draws one.""")],
  ("Which box is each one in? (a) a chess program that searches all moves, (b) a model predicting house prices from past sales, (c) a chatbot writing a poem.",
   """(a) AI, but not ML: it follows search rules, it doesn't learn from data. (b) ML: it learns a pattern from examples. (c) Generative AI, which is also deep learning and ML: it creates new text."""),
  [("Model", "the thing that has learned the pattern; you give it an input and it gives an answer"),
   ("Training", "the learning step, where the model looks at examples and adjusts itself"),
   ("Inference / prediction", "using the trained model on new inputs"),
   ("Neural network", "a model built from many simple connected units, loosely inspired by the brain")],
  """The smallest possible machine learning program: we never write the rule "price = 3 × size". We give examples and let the model find it.""",
  r'''from sklearn.linear_model import LinearRegression

sizes  = [[50], [80], [100], [120]]    # input: flat size in square metres (one feature per row)
prices = [150, 240, 300, 360]          # answer we want to learn: price in lakhs

model = LinearRegression()             # an empty model that knows how to fit a straight line
model.fit(sizes, prices)               # training: it finds the pattern in the examples

print(model.predict([[90]]))           # inference: price for a 90 m² flat it has never seen -> about 270
print(model.coef_.round(2), round(model.intercept_, 2))   # the rule it learned: 3 per m², 0 extra''',
  [("What is the difference between AI and ML in one line?", "AI is the goal of intelligent behaviour; ML is achieving it by learning from data instead of hand-written rules."),
   ("Why is ChatGPT called generative AI?", "Because it generates new content (text) rather than only choosing a label like spam or not spam."),
   ("In the code, which line is the learning step?", "`model.fit(sizes, prices)`.")])

L("m-ml-types",
  "Learning types differ by the feedback the model gets: answers, no answers, a few answers, self-made answers, or rewards.",
  """The first question about any ML problem is "what examples do I have?". The answer decides the whole family of methods. Interviewers expect you to name the type quickly from a problem description.""",
  """- **Supervised learning**: every example comes **with the right answer** (a label). Email + "spam". Photo + "cat". The model learns to map input to answer.
- **Unsupervised learning**: **no answers at all**. The model looks for structure by itself, such as groups of similar customers.
- **Semi-supervised learning**: a **few labelled** examples and many unlabelled ones. Labels are expensive, so the model uses both.
- **Self-supervised learning**: the data **makes its own labels**. Hide a word in a sentence and predict it. This is how large language models are trained.
- **Reinforcement learning (RL)**: an agent **acts and gets a reward** or penalty, and learns by trial and error, like a game player.""",
  [("Look at the data",
    """You have 1,000 past loans, each marked "repaid" or "defaulted". There is an answer column, so it is **supervised**. Predicting a category is called **classification**; predicting a number (like a price) is **regression**."""),
   ("No answer column",
    """You have 50,000 shoppers' purchase histories and want "types of customer". There is no answer column, so it is **unsupervised** (clustering)."""),
   ("Rewards instead of answers",
    """A robot learns to walk. Nobody gives the correct motor angles; it only gets +1 for moving forward and −1 for falling. That is **reinforcement learning**.""")],
  ("Name the type: (a) predict tomorrow's temperature from past weather, (b) group news articles by topic with no tags, (c) teach a program to play a video game from the score.",
   "(a) Supervised regression (the answer is a number). (b) Unsupervised clustering. (c) Reinforcement learning."),
  [("Label", "the right answer attached to an example"),
   ("Classification", "supervised learning where the answer is a category"),
   ("Regression", "supervised learning where the answer is a number"),
   ("Clustering", "unsupervised grouping of similar examples"),
   ("Reward", "the score an RL agent tries to maximise")],
  """The same small dataset used two ways: with labels (supervised) and without them (unsupervised).""",
  r'''from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans

X, y = load_iris(return_X_y=True)        # X: flower measurements, y: species label (0, 1, 2)

clf = DecisionTreeClassifier().fit(X, y) # supervised: learns from X AND the answers y
print("supervised guess:", clf.predict(X[:3]))

km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)  # unsupervised: only X, no y
print("unsupervised groups:", km.labels_[:3])  # group numbers it invented itself''',
  [("What makes a problem supervised?", "Each training example comes with the correct answer (label)."),
   ("How do large language models get labels without humans?", "Self-supervised learning: the next word in real text is the label."),
   ("Predicting a house price: classification or regression?", "Regression, because the answer is a number.")])

L("m-ml-principles",
  "A model is a function picked from a family of possible functions by making its errors on the data as small as possible.",
  """Every ML algorithm, from a straight line to a huge neural network, follows the same recipe. Once you see the recipe, every new algorithm is just a different choice of ingredients.""",
  """Machine learning has three ingredients:

1. **A family of functions** to choose from (the hypothesis space). For linear regression: all straight lines `y = w·x + b`.
2. **A loss**: a number that says how wrong a function is on the data. Smaller is better.
3. **An optimiser**: a way to search the family for the function with the smallest loss.

"Learning" means: try a function, measure its loss, adjust, repeat. The hope is that the function that fits the examples well will also work on **new** data; this is called **generalisation**.

Every algorithm also carries an **assumption** about what good answers look like (its **inductive bias**): a straight line assumes the pattern is roughly straight. There is **no free lunch**: no algorithm is best for every problem.""",
  [("Pick a family",
    """Data: hours studied → marks: (1, 52), (2, 58), (3, 66). Family: lines `marks = w × hours + b`."""),
   ("Measure the loss",
    """Try w = 5, b = 50. Predictions: 55, 60, 65. Errors: −3, −2, +1. Squared errors: 9, 4, 1. Mean = **4.67**. Try w = 7, b = 45: predictions 52, 59, 66, errors 0, −1, 0, mean = **0.33**. The second line is better."""),
   ("Optimise",
    """The computer keeps adjusting w and b in the direction that lowers the loss until it can't improve. That's training.""")],
  ("A model scores 99% on the examples it trained on but 60% on new examples. Did it generalise?",
   "No. It fitted the training examples (maybe memorised them) but the pattern doesn't carry over to new data. That's overfitting."),
  [("Hypothesis space", "the family of functions the algorithm can choose from"),
   ("Loss", "a number measuring how wrong the model is; training makes it small"),
   ("Generalisation", "doing well on new data, not just the training data"),
   ("Inductive bias", "the built-in assumption an algorithm makes about the pattern"),
   ("No free lunch", "no single algorithm is best for every problem")],
  """Here we do the "try, measure, adjust" loop ourselves for the marks example, so you can see learning is just repeated loss-lowering.""",
  r'''import numpy as np
hours = np.array([1, 2, 3]); marks = np.array([52, 58, 66])

def loss(w, b):                        # mean squared error of the line w*x + b
    return np.mean((w * hours + b - marks) ** 2)

best = None
for w in range(0, 11):                 # the "family": every line with w 0..10 and b 40..60
    for b in range(40, 61):
        if best is None or loss(w, b) < best[0]:
            best = (loss(w, b), w, b)  # keep the line with the smallest loss so far
print("best loss %.2f with w=%d b=%d" % best)   # about w=7, b=45''',
  [("What are the three ingredients of an ML algorithm?", "A family of functions, a loss, and an optimiser that searches the family to minimise the loss."),
   ("What does 'no free lunch' mean in practice?", "You have to try and compare models for your problem; none wins everywhere."),
   ("Why do we care about generalisation more than training score?", "Because the model will be used on new data, not on the examples it already saw.")])

L("m-problem-formulation",
  "Before any model, decide exactly what to predict, from which inputs, how to measure success, and what simple baseline to beat.",
  """Most failed ML projects fail before any code is written: they predict the wrong thing, use data that won't exist at prediction time, or never define success. Interviewers test this step first in ML system design questions.""",
  """Turn a vague business goal into four precise answers:

1. **Target**: what exactly is predicted, and when? ("Will this customer cancel in the next 30 days?")
2. **Inputs**: which information is available **at the moment of prediction**?
3. **Metric**: how is success measured, in model terms and business terms?
4. **Baseline**: what does a simple rule achieve? The model must beat it.

Also ask: is ML even needed? If a simple rule solves it, use the rule.""",
  [("Vague goal",
    """"Reduce customer churn" (customers leaving). Not yet something a model can do."""),
   ("Make it precise",
    """Target: `cancels within 30 days` (yes/no) → binary classification. Inputs: last 3 months of usage, complaints, plan type. Metric: recall on cancellers at 80% precision, and money saved by retention offers."""),
   ("Baseline",
    """Rule: "customers whose usage dropped by 50% will cancel". It catches 40% of cancellers. Your model is only useful if it clearly beats 40%.""")],
  ("A food app wants to 'show better restaurants'. Write a precise target.",
   "For example: 'probability the user orders from this restaurant in this session', a binary classification per (user, restaurant) pair, ranked by that probability; measured by order rate on the top 10 shown."),
  [("Target", "the exact quantity the model predicts"),
   ("Baseline", "a simple method the model must beat to be worth building"),
   ("Business metric", "what the company cares about: money, time, users"),
   ("Proxy metric", "a measurable stand-in used during training, like accuracy")],
  """A baseline in code: before training anything clever, check what "always predict the most common answer" scores.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True)
base = DummyClassifier(strategy="most_frequent")                  # baseline: always say the common class
model = LogisticRegression(max_iter=5000)
print("baseline:", cross_val_score(base, X, y, cv=5).mean().round(3))   # about 0.63
print("model   :", cross_val_score(model, X, y, cv=5).mean().round(3))  # about 0.95: clearly better''',
  [("Why must inputs be 'available at prediction time'?", "Otherwise the model learns from information it won't have when used, and fails in production (leakage)."),
   ("What is a baseline for?", "It shows how much the model really adds; if it can't beat a simple rule, it isn't worth deploying.")])

L("m-intuitive-algos",
  "Simple algorithms like 'predict the majority' or 'nearest class average' give baselines and build intuition before complex models.",
  """Complex models are hard to debug. Simple ones tell you quickly whether the data contains a signal at all, and they set the score that every fancier model must beat.""",
  """Four very simple ideas:

- **Majority class**: always predict the most common answer.
- **Nearest centroid**: compute the average point of each class; a new point gets the class whose average is closest.
- **One rule (1R)**: find the single feature and threshold that splits the classes best ("if petal length < 2.5 → setosa").
- **Nearest neighbour**: copy the answer of the most similar training example.""",
  [("Nearest centroid with numbers",
    """Class A points: (1, 1), (2, 1). Average = (1.5, 1). Class B points: (6, 5), (7, 6). Average = (6.5, 5.5). New point (2, 2): distance to A's average ≈ 1.1, to B's ≈ 5.7 → **class A**."""),
   ("One rule",
    """Exam pass data: students with attendance ≥ 75% passed 90% of the time, below 75% passed 30%. Rule: "attendance ≥ 75% → pass". Simple, explainable, often surprisingly good.""")],
  ("Class A average is (0, 0), class B average is (10, 0). Which class is (4, 3)?",
   "Distance to A = 5, to B = √(36 + 9) ≈ 6.7, so class A."),
  [("Centroid", "the average point of a group"),
   ("Baseline", "a simple method used as a reference score"),
   ("Feature", "one input column, such as age or petal length")],
  """Nearest centroid and majority baseline on the iris flowers dataset.""",
  r'''from sklearn.datasets import load_iris
from sklearn.neighbors import NearestCentroid
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import cross_val_score

X, y = load_iris(return_X_y=True)
for name, m in [("majority", DummyClassifier()), ("nearest centroid", NearestCentroid())]:
    print(name, cross_val_score(m, X, y, cv=5).mean().round(3))   # ~0.33 vs ~0.92''',
  [("What does nearest centroid store after training?", "Just one average point per class."),
   ("Why start with simple algorithms?", "They show whether there is a signal, give a score to beat, and are easy to explain and debug.")])

L("m-search-ai",
  "Not all AI learns from data: search algorithms find best routes and plans, and genetic algorithms optimise by trial and selection.",
  """Maps, delivery routing, game playing and scheduling rely on search, not learning. Your GoldenHour project uses exactly these (Dijkstra, A*), and interviewers like candidates who know AI is wider than ML.""",
  """- **Search** explores possible states step by step to reach a goal. **Dijkstra** finds the cheapest route by always expanding the closest unexplored place. **A\\*** does the same but also uses a guess of the remaining distance, so it heads toward the goal.
- **Optimisation without gradients**: when you can score a solution but can't compute a slope, try many solutions and keep the good ones. A **genetic algorithm** keeps a population, mixes good solutions (crossover), changes them a little (mutation) and keeps the best (selection).""",
  [("Dijkstra by hand",
    """Roads: A→B 4 min, A→C 1, C→B 2, B→D 1. From A: closest is C (1). Through C, B costs 1 + 2 = 3, better than 4. Then D = 3 + 1 = **4 min**, route A→C→B→D."""),
   ("A genetic algorithm step",
    """Goal: a 5-bit string with as many 1s as possible. Population: 10110 (score 3), 01001 (2). Crossover: take 101 + 01 → 10101 (3). Mutation flips a bit → 11101 (4). Keep the best and repeat.""")],
  ("Why does A* usually explore fewer places than Dijkstra?",
   "It adds an estimate of the remaining distance, so it prefers places that are closer to the goal instead of spreading out in every direction."),
  [("State", "one situation in the search, such as 'at junction B'"),
   ("Heuristic", "a quick estimate of how far the goal is"),
   ("Population", "the set of candidate solutions a genetic algorithm keeps"),
   ("Mutation / crossover", "small random changes / mixing two solutions")],
  """Dijkstra on the small road map above, using Python's heap.""",
  r'''import heapq
roads = {"A": {"B": 4, "C": 1}, "C": {"B": 2}, "B": {"D": 1}, "D": {}}

def dijkstra(start):
    dist = {start: 0}
    heap = [(0, start)]                       # (time so far, place)
    while heap:
        d, u = heapq.heappop(heap)            # closest unexplored place
        if d > dist[u]: continue              # an old, worse entry: skip it
        for v, w in roads[u].items():
            if d + w < dist.get(v, 1e9):      # found a faster way to v
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist

print(dijkstra("A"))   # {'A': 0, 'B': 3, 'C': 1, 'D': 4}''',
  [("Is Dijkstra machine learning?", "No. It's classical AI search; it uses no training data."),
   ("When would you use a genetic algorithm?", "When you can score a solution but can't compute gradients, e.g. timetables or designs.")])

L("m-data-processing",
  "Real data is messy: fix types, remove duplicates, fill or drop missing values and handle outliers before any model.",
  """A model can only be as good as its data. In real projects, cleaning usually takes more time than modelling, and a single bad column (prices stored as text, "N/A" as a value) can quietly ruin results.""",
  """Go through the data and fix five common problems:

1. **Wrong types**: numbers stored as text ("1,200"), dates as strings.
2. **Duplicates**: the same row twice, which over-counts it.
3. **Missing values**: blanks. Either drop the row, or **impute** (fill) with the median, the most common value, or a model's guess. Keep a flag column saying it was missing.
4. **Outliers**: extreme values. Check whether they are errors (age = 230) or real (a very rich customer). Fix errors; keep real ones or cap them.
5. **Inconsistent labels**: "Chennai", "chennai ", "CHN" all meaning the same city.""",
  [("A tiny messy table",
    """Ages: 25, 31, missing, 29, 230. The 230 is clearly an error → set it to missing. Median of the valid ones (25, 29, 31) is **29**, so both blanks become 29."""),
   ("Why the median, not the mean?",
    """The mean of 25, 31, 29, 230 is 78.75, pulled up by the error. The median ignores extreme values, so it is a safer fill.""")],
  ("Salaries: 30k, 32k, 35k, 34k, 5000k. Would you fill a missing salary with the mean or the median?",
   "The median (about 34k). The 5000k outlier drags the mean to about 1026k, which is unrealistic."),
  [("Imputation", "filling missing values with a reasonable guess"),
   ("Outlier", "a value far from the rest; may be an error or a rare real case"),
   ("Data type", "what kind of value a column holds: number, text, date"),
   ("NaN", "'not a number', how pandas marks a missing value")],
  """Cleaning the small table with pandas: each line fixes one problem from the list.""",
  r'''import pandas as pd, numpy as np

df = pd.DataFrame({"city": ["Chennai", "chennai ", "Pune", "Pune"],
                   "age":  [25, 31, np.nan, 230],
                   "salary": ["30,000", "32,000", "35,000", "35,000"]})

df["city"] = df["city"].str.strip().str.title()                  # 'chennai ' -> 'Chennai'
df["salary"] = df["salary"].str.replace(",", "").astype(int)     # text -> number
df.loc[df["age"] > 120, "age"] = np.nan                          # impossible age -> missing
df["age_missing"] = df["age"].isna()                             # remember which were missing
df["age"] = df["age"].fillna(df["age"].median())                 # fill with the median (28)
df = df.drop_duplicates()                                        # remove repeated rows
print(df)''',
  [("Why keep an 'age_missing' column after filling?", "Missingness itself can carry information (e.g. people who skip a field behave differently)."),
   ("Is every outlier an error?", "No. Check it; real extreme values should usually be kept or capped, not deleted blindly.")])

L("m-eda",
  "Exploratory data analysis means looking at the data (distributions, relationships, problems) before building any model.",
  """EDA prevents expensive mistakes: you discover that 95% of rows are one class, that a column is mostly empty, or that one feature secretly contains the answer. Every later decision (features, model, metric) depends on it.""",
  """Ask these questions, in this order:

1. **Shape**: how many rows and columns? What does each column mean?
2. **Target**: what does the answer column look like? Balanced or rare?
3. **Each feature alone**: its distribution (histogram), missing values, odd values.
4. **Features vs target**: does the answer change with this feature?
5. **Features vs each other**: correlations, duplicates of the same information.

Write down what you find; each finding becomes a cleaning step, a feature or a warning.""",
  [("Target balance",
    """Fraud data: 9,950 normal, 50 fraud. A model that always says "normal" is 99.5% accurate but useless. You now know to use recall/precision, not accuracy."""),
   ("Feature vs target",
    """Titanic: survival is 74% for women and 19% for men. Sex is clearly a strong feature. Fare also rises with survival, partly because it reflects passenger class.""")],
  ("You find a column 'refund_issued' that is 'yes' for almost every fraud case. Good feature or a warning sign?",
   "A warning sign: refunds happen after fraud is detected, so the column wouldn't exist at prediction time. It leaks the answer."),
  [("Distribution", "how the values of a column are spread out"),
   ("Histogram", "a bar chart of how often values fall in each range"),
   ("Correlation", "how strongly two columns move together, from −1 to +1"),
   ("Class balance", "how many examples each answer has")],
  """A first EDA pass with pandas on a built-in dataset; every line answers one of the questions above.""",
  r'''from sklearn.datasets import load_breast_cancer
df = load_breast_cancer(as_frame=True).frame        # a table with a 'target' column

print(df.shape)                                     # 1. rows and columns
print(df["target"].value_counts(normalize=True))    # 2. class balance (about 63% / 37%)
print(df.isna().sum().sum(), "missing values")      # 3. data quality
print(df[["mean radius", "mean texture", "target"]].describe().round(2))
print(df.corr()["target"].sort_values().head(3))    # 4. features most related to the target''',
  [("What is the first thing to check about the target?", "Its balance: how common each answer is. It decides the metric."),
   ("Why look at feature-to-feature correlation?", "Highly correlated features carry the same information; you may drop one or combine them.")])

L("m-real-world-data",
  "Every kind of data (tables, text, images, audio, time series, graphs) must become arrays of numbers with a standard shape.",
  """Models only understand numbers arranged in arrays (tensors). Knowing the standard shape for each data type lets you plug any data into any model, and shape errors are the most common beginner bug.""",
  """The usual shapes (the first number is always "how many examples"):

| Data | Shape | Example |
| --- | --- | --- |
| Table | (rows, features) | 1000 customers × 12 columns |
| Text | (documents, tokens) → (documents, tokens, vector size) | 32 sentences × 50 words |
| Grayscale image | (images, height, width) | 64 × 28 × 28 |
| Colour image | (images, height, width, 3) or (images, 3, height, width) | 64 × 224 × 224 × 3 |
| Audio | (clips, samples) | 10 clips × 16,000 samples (1 second at 16 kHz) |
| Time series | (series, time steps, features) | 100 sensors × 60 minutes × 4 readings |
| Graph | node features (nodes, features) + edge list (2, edges) | 500 users, 2000 friendships |""",
  [("An image is a grid of numbers",
    """A 2 × 2 grayscale image might be `[[0, 255], [128, 64]]`: 0 is black, 255 is white. A colour image adds 3 numbers (red, green, blue) per pixel."""),
   ("Text becomes numbers",
    """Vocabulary: {"i": 1, "love": 2, "ml": 3}. The sentence "i love ml" becomes `[1, 2, 3]`. Later each number is replaced by a vector (an embedding).""")],
  ("What is the shape of 16 colour photos of size 32 × 32 in the (N, H, W, C) layout?",
   "(16, 32, 32, 3)."),
  [("Tensor", "an array with any number of dimensions"),
   ("Shape", "the size of each dimension of an array"),
   ("Channel", "one colour layer of an image (R, G or B)"),
   ("Sample rate", "how many audio measurements per second")],
  """Building one fake example of each data type with NumPy and printing its shape.""",
  r'''import numpy as np

table  = np.random.rand(1000, 12)            # 1000 rows, 12 features
image  = np.random.randint(0, 256, (16, 32, 32, 3))   # 16 colour images, 32x32 pixels
audio  = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000)  # 1 second of a 440 Hz tone
series = np.random.rand(100, 60, 4)          # 100 sensors, 60 time steps, 4 readings
vocab  = {"i": 1, "love": 2, "ml": 3}
text   = np.array([[vocab[w] for w in "i love ml".split()]])  # 1 sentence, 3 tokens

for name, a in [("table", table), ("image", image), ("audio", audio), ("series", series), ("text", text)]:
    print(f"{name:7s}", a.shape)''',
  [("Why does the first dimension usually mean 'number of examples'?", "Models process batches of examples, so every input array starts with the batch size."),
   ("How many numbers describe one 224 × 224 colour image?", "224 × 224 × 3 = 150,528.")])

L("m-encoding",
  "Models need numbers, so categories are converted: one-hot for no order, ordinal for ordered levels, target or hashing for many categories.",
  """Columns like city, colour or plan type are text. Converting them badly (for example Chennai = 1, Delhi = 2, Mumbai = 3) silently tells the model that Mumbai is "bigger" than Chennai. The right encoding avoids that.""",
  """- **One-hot encoding**: one new 0/1 column per category. Use when there is **no order** (cities, colours).
- **Ordinal encoding**: numbers that respect a real order: small = 0, medium = 1, large = 2.
- **Target encoding**: replace each category with the average answer for that category (e.g. default rate per pincode). Good for **many categories**, but compute it only on training data to avoid leakage.
- **Hashing**: map categories into a fixed number of buckets with a hash function; handles unseen values.
- **Embeddings**: a learned vector per category inside a neural network.""",
  [("One-hot by hand",
    """City column: Chennai, Delhi, Chennai. Becomes three rows of `is_Chennai, is_Delhi`: (1, 0), (0, 1), (1, 0)."""),
   ("Target encoding by hand",
    """Pincode A: 3 loans, 1 default → 0.33. Pincode B: 4 loans, 0 defaults → 0.0. Each row gets its pincode's rate as a number.""")],
  ("T-shirt sizes S, M, L, XL: one-hot or ordinal?",
   "Ordinal (S = 0, M = 1, L = 2, XL = 3), because the sizes have a natural order."),
  [("Categorical feature", "a column whose values are labels, not quantities"),
   ("Cardinality", "how many different categories a column has"),
   ("One-hot", "one 0/1 column per category"),
   ("Unseen category", "a value at prediction time that wasn't in training data")],
  """One-hot and ordinal encoding with scikit-learn; `handle_unknown` keeps the model from crashing on a new city.""",
  r'''import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

df = pd.DataFrame({"city": ["Chennai", "Delhi", "Chennai"], "size": ["S", "L", "M"]})

oh = OneHotEncoder(handle_unknown="ignore", sparse_output=False)  # unseen city -> all zeros
print(oh.fit_transform(df[["city"]]), oh.get_feature_names_out())

od = OrdinalEncoder(categories=[["S", "M", "L"]])                   # we state the real order
print(od.fit_transform(df[["size"]]).ravel())                        # S=0, L=2, M=1''',
  [("Why not encode cities as 1, 2, 3?", "It invents an order and distances between cities that don't exist."),
   ("What is the main risk of target encoding?", "Leakage: if computed using the row's own answer or test data, it reveals the target.")])

L("m-feature-engineering",
  "Feature engineering creates new input columns (ratios, date parts, totals, combinations) that make the pattern easy for a model to see.",
  """Better features often improve a model more than a better algorithm. Domain knowledge turned into a column ("debt divided by income") can do in one step what a model would need thousands of examples to discover.""",
  """Common ways to create features:

- **Ratios**: debt ÷ income, clicks ÷ views.
- **Date parts**: day of week, hour, month, "is weekend", days since last purchase.
- **Aggregates**: a customer's average order value, number of orders in the last 30 days.
- **Transformations**: log of a skewed value like income; scaling to a common range.
- **Interactions**: price × quantity, or "is new customer AND large order".""",
  [("A ratio beats raw numbers",
    """Two people: A earns 100k with 50k debt, B earns 20k with 15k debt. Raw debt says A is riskier (50k > 15k). Debt-to-income says B is riskier: **0.75 vs 0.50**."""),
   ("Date parts",
    """Order time "2026-11-21 21:30" becomes day_of_week = Saturday, hour = 21, is_weekend = 1. A food app's demand depends on these, not on the raw timestamp.""")],
  ("For predicting electricity use, what features would you make from a timestamp?",
   "Hour of day, day of week, month or season, is_weekend, is_holiday; maybe the temperature at that time if you have it."),
  [("Feature", "an input column the model uses"),
   ("Aggregate", "a summary over many rows, such as an average per customer"),
   ("Log transform", "taking the logarithm to squash very large values"),
   ("Interaction", "a feature made by combining two others")],
  """Creating ratio, date and aggregate features with pandas.""",
  r'''import pandas as pd, numpy as np

orders = pd.DataFrame({"customer": ["a", "a", "b"],
                       "time": pd.to_datetime(["2026-11-21 21:30", "2026-11-24 13:00", "2026-11-22 09:15"]),
                       "amount": [500, 300, 1200], "income": [40000, 40000, 90000]})

orders["hour"] = orders["time"].dt.hour                          # date part
orders["is_weekend"] = orders["time"].dt.dayofweek >= 5          # Saturday=5, Sunday=6
orders["amount_to_income"] = orders["amount"] / orders["income"] # ratio
orders["log_amount"] = np.log1p(orders["amount"])                # squash big values
orders["cust_avg"] = orders.groupby("customer")["amount"].transform("mean")  # aggregate
print(orders.drop(columns="time"))''',
  [("Why can a ratio help more than the two raw columns?", "It encodes the relationship directly, so the model doesn't have to learn division from data."),
   ("What must you be careful about with aggregates?", "Only use data from before the prediction time, or you leak the future.")])

L("m-feature-selection",
  "Feature selection keeps the useful inputs and drops noisy or duplicate ones, giving simpler, faster and often more accurate models.",
  """More columns isn't always better. Useless columns add noise, slow training, make overfitting easier and make the model harder to explain. Dropping them is often a free improvement.""",
  """Three families:

- **Filter methods**: score each feature alone, before modelling (correlation with the target, mutual information, chi-square). Fast.
- **Wrapper methods**: try subsets of features with a model and keep the best subset (forward selection, recursive feature elimination). Slower, more accurate.
- **Embedded methods**: the model selects while it trains. L1 (Lasso) regularisation pushes useless weights to exactly zero; tree models report feature importance.""",
  [("Filter with numbers",
    """Correlation with house price: size 0.8, rooms 0.7, owner's favourite colour 0.01. The filter keeps size and rooms and drops colour."""),
   ("Duplicates",
    """Size in square feet and size in square metres have correlation 1.0. Keep one; the second adds nothing.""")],
  ("Recursive feature elimination: what does it repeat?",
   "Train a model, remove the least important feature, and repeat until the wanted number of features remains."),
  [("Filter / wrapper / embedded", "select before the model / using model runs / inside training"),
   ("Mutual information", "how much knowing a feature reduces uncertainty about the target"),
   ("L1 regularisation", "a penalty that drives unhelpful weights to zero")],
  """A filter method (SelectKBest) and an embedded one (L1 logistic regression), comparing how many features each keeps.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)          # 30 features
X = StandardScaler().fit_transform(X)                # same scale for every feature

best5 = SelectKBest(mutual_info_classif, k=5).fit(X, y)          # filter: top 5 by score
print("filter keeps columns:", best5.get_support(indices=True))

l1 = LogisticRegression(penalty="l1", C=0.1, solver="liblinear").fit(X, y)  # embedded
print("L1 keeps", (l1.coef_ != 0).sum(), "of 30 features")''',
  [("Why can removing features improve accuracy?", "Noisy features let the model fit random patterns (overfitting); fewer, better features generalise better."),
   ("Which method is fastest: filter, wrapper or embedded?", "Filter, because it doesn't train models on subsets.")])

L("m-feature-extraction",
  "Feature extraction turns raw text, images or audio into numeric vectors, either with hand-made recipes or with pretrained networks.",
  """You can't feed a paragraph or a photo straight into most models. Extraction is the bridge, and choosing a good extractor often matters more than the model on top.""",
  """- **Text**: counts of words (bag of words), TF-IDF weights, or embeddings from a language model.
- **Images**: colour histograms, edge features, or the output vector of a pretrained CNN.
- **Audio**: spectrograms and MFCCs (which frequencies are loud over time).
- **Signals and time series**: summary statistics over windows (mean, max, trend).

Hand-crafted features need domain knowledge and little data. Learned features (from pretrained models) need little effort and usually work better.""",
  [("Text into numbers",
    """Vocabulary: [cheap, meeting, offer]. "Cheap offer, cheap!" → counts **[2, 0, 1]**. "Meeting tomorrow" → [0, 1, 0]."""),
   ("A signal into numbers",
    """A heart-rate window of 5 readings 70, 72, 75, 90, 71 becomes features: mean 75.6, max 90, range 20.""")],
  ("Vocabulary [good, bad, movie]. What are the counts for 'good good movie'?",
   "[2, 0, 1]."),
  [("Feature vector", "the list of numbers describing one example"),
   ("Hand-crafted feature", "a recipe designed by a person"),
   ("Learned feature / embedding", "a vector produced by a trained network")],
  """Text to count vectors with scikit-learn, and a time window to summary features with NumPy.""",
  r'''from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

docs = ["cheap offer cheap", "meeting tomorrow", "cheap meeting"]
cv = CountVectorizer()
X = cv.fit_transform(docs)                  # each document -> word counts
print(cv.get_feature_names_out())           # ['cheap' 'meeting' 'offer' 'tomorrow']
print(X.toarray())

window = np.array([70, 72, 75, 90, 71])
print(float(window.mean()), int(window.max()), int(np.ptp(window)))   # mean 75.6, max 90, range 20''',
  [("Hand-crafted or learned features with very little data?", "Hand-crafted or pretrained-learned features; training a feature extractor from scratch needs lots of data."),
   ("What does a bag-of-words vector lose?", "Word order: 'dog bites man' and 'man bites dog' look identical.")])

L("m-imbalance",
  "When one class is rare (fraud, disease), accuracy misleads; use recall and precision, class weights, resampling and a tuned threshold.",
  """Many valuable problems are imbalanced: 1 fraud in 1,000 payments, 1 sick patient in 100. A model that ignores the rare class still scores 99.9% accuracy, so you need different tools to measure and fix it.""",
  """1. **Measure properly**: precision (of the cases flagged, how many were real), recall (of the real cases, how many were caught), and PR-AUC.
2. **Class weights**: tell the model that a mistake on the rare class costs more (`class_weight="balanced"`).
3. **Resampling**: duplicate rare examples (oversampling, SMOTE creates synthetic ones) or drop some common ones (undersampling). Only resample the **training** data.
4. **Move the threshold**: the default 0.5 isn't sacred. Flag fraud at probability 0.2 if missing fraud is expensive.""",
  [("Accuracy fools you",
    """1,000 payments, 10 fraud. A model that always says "not fraud": accuracy 990/1000 = **99%**, recall = 0/10 = **0%**. It catches nothing."""),
   ("Threshold trade-off",
    """At threshold 0.5 a model flags 8 cases, 6 are fraud: precision 6/8 = 75%, recall 6/10 = 60%. At threshold 0.2 it flags 20, 9 are fraud: precision 45%, recall 90%. Pick based on the cost of each mistake.""")],
  ("Cancer screening: would you prefer high precision or high recall?",
   "High recall: missing a sick patient is far worse than a false alarm that leads to another test."),
  [("Precision", "of the cases the model flagged, the share that were truly positive"),
   ("Recall", "of the truly positive cases, the share the model caught"),
   ("Class weight", "a multiplier that makes mistakes on a class count more"),
   ("SMOTE", "creating new synthetic rare examples between existing ones")],
  """Training the same model with and without class weights on an imbalanced dataset, and comparing recall.""",
  r'''from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score, precision_score

X, y = make_classification(n_samples=5000, weights=[0.98], random_state=0)   # 2% positives
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0)

for cw in [None, "balanced"]:
    m = LogisticRegression(class_weight=cw, max_iter=1000).fit(Xtr, ytr)
    p = m.predict(Xte)
    print(cw, "recall", round(recall_score(yte, p), 2), "precision", round(precision_score(yte, p), 2))''',
  [("Why resample only the training data?", "The test set must reflect real-world proportions, or your reported scores are unrealistic."),
   ("Name two fixes that don't change the data.", "Class weights and moving the decision threshold.")])

L("m-train-val-test",
  "Train on one part of the data, tune on a second, and report on a third that the model never saw; cross-validation reuses data for steadier estimates.",
  """If you test a model on the same data it learned from, it looks better than it really is. Proper splits are the only honest way to know how a model will do on new data, and interviewers check this habit constantly.""",
  """- **Training set** (e.g. 70%): the model learns from it.
- **Validation set** (15%): you compare models and settings on it.
- **Test set** (15%): used **once**, at the very end, to report the final score.

**k-fold cross-validation**: split the training data into k parts (folds). Train on k − 1 and validate on the remaining one, k times, and average. Every example is used for validation once.

For time-ordered data, always train on the past and validate on the future.""",
  [("5-fold cross-validation",
    """100 examples, 5 folds of 20. Round 1 validates on rows 1–20 and trains on 21–100; round 2 validates on 21–40; and so on. Scores 0.81, 0.79, 0.84, 0.80, 0.81 → average **0.81**, spread small, so the estimate is reliable."""),
   ("Why a separate test set",
    """If you try 50 settings and keep the best validation score, that score is slightly lucky. The untouched test set gives the honest number.""")],
  ("Predicting next month's sales: may you shuffle the rows randomly before splitting?",
   "No. Use a time split (train on earlier months, validate on later ones); shuffling lets the model peek at the future."),
  [("Validation set", "data for choosing models and settings"),
   ("Test set", "data used once for the final, honest score"),
   ("Fold", "one of the k parts in cross-validation"),
   ("Stratified split", "a split that keeps class proportions the same in every part")],
  """A train/test split plus 5-fold cross-validation on the training part only.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)  # lock the test set away

model = RandomForestClassifier(random_state=0)
scores = cross_val_score(model, Xtr, ytr, cv=5)          # 5 rounds, only on training data
print("CV scores:", scores.round(3), "mean", scores.mean().round(3))

model.fit(Xtr, ytr)                                       # final model on all training data
print("test score (reported once):", round(model.score(Xte, yte), 3))''',
  [("What is the validation set for?", "Choosing between models and settings without touching the test set."),
   ("What does a large spread between fold scores tell you?", "The estimate is unstable; the model or the data split is sensitive, so be careful trusting one number.")])

L("m-leakage",
  "Leakage is when information that won't exist at prediction time sneaks into training, giving great offline scores and failure in real use.",
  """Leakage is the most common reason a model that looked brilliant in a notebook fails in production. It's hard to spot because nothing errors; the scores just look too good.""",
  """Three common kinds:

1. **Target leakage**: a feature is created after (or because of) the answer. "Account closed" predicting churn; "treatment given" predicting disease.
2. **Train–test contamination**: preprocessing (scaling, filling missing values, selecting features) fitted on all data before splitting, so the training step "sees" test data.
3. **Time leakage**: using future data to predict the past, e.g. random splits on time series or averages that include future rows.

Rule: for every feature ask, **"would I know this value at the moment I make the prediction?"**""",
  [("A score that's too good",
    """A hospital model predicts pneumonia with 99% accuracy. One feature is "antibiotics prescribed". Doctors prescribe antibiotics **after** diagnosing pneumonia, so the model reads the diagnosis, not the symptoms. In real use it drops to 70%."""),
   ("Scaling leak",
    """You compute the average income over all 10,000 rows, then split. The training rows now carry information about the test rows' incomes. Fix: fit the scaler on the training rows only, using a pipeline.""")],
  ("Predicting loan default, you have 'number of collection calls made'. Leak or not?",
   "Leak: collection calls happen after the customer has stopped paying, so the value isn't known when deciding the loan."),
  [("Target leakage", "a feature that contains the answer or is caused by it"),
   ("Contamination", "test data influencing training through preprocessing"),
   ("Pipeline", "a chain of steps fitted only on training data, preventing contamination")],
  """The safe pattern: put preprocessing inside a Pipeline, so cross-validation fits the scaler on each training fold only.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True)

# Wrong: StandardScaler().fit_transform(X) before splitting would let test rows shape the scaling.
pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))   # scaler is refit inside each fold
print(cross_val_score(pipe, X, y, cv=5).mean().round(3))''',
  [("What one question catches most leakage?", "'Would I know this feature's value at the moment of prediction?'"),
   ("How does a pipeline prevent contamination?", "It fits preprocessing only on the training part of each split, then applies it to the validation part.")])

L("m-overfitting",
  "Underfitting means too simple to catch the pattern; overfitting means memorising noise. The goal is the sweet spot in between.",
  """This idea explains why models fail on new data and what to do about it. Almost every technique you'll meet later (regularisation, dropout, more data, simpler models) exists to manage it.""",
  """- **Underfitting (high bias)**: the model is too simple. It is wrong on training data and new data. Example: a straight line through a curved pattern.
- **Overfitting (high variance)**: the model is too flexible. It is nearly perfect on training data but bad on new data, because it learned the noise.
- **Good fit**: training and validation errors are both low and close to each other.

How to tell: compare training error with validation error.

| Training error | Validation error | Diagnosis | Fix |
| --- | --- | --- | --- |
| High | High | Underfitting | more features, more flexible model |
| Low | High | Overfitting | more data, regularisation, simpler model |
| Low | Low | Good | ship it |""",
  [("Three models on the same 10 points",
    """A flat line: training error 20, validation error 21 → underfit. A gentle curve (degree 2): 3 and 4 → good. A wiggly degree-9 curve through every point: 0 and 35 → overfit."""),
   ("The bias–variance idea",
    """**Bias** is the error from wrong assumptions (too simple). **Variance** is the error from being too sensitive to the particular training sample. Making a model more flexible lowers bias but raises variance.""")],
  ("Training accuracy 99%, validation 72%. What is happening and name two fixes.",
   "Overfitting. Get more data, add regularisation, reduce model complexity, or use early stopping."),
  [("Bias", "error from a model being too simple"),
   ("Variance", "error from a model reacting too much to the training sample"),
   ("Generalisation gap", "the difference between training and validation scores"),
   ("Capacity", "how flexible a model is")],
  """Fitting polynomials of degree 1, 3 and 15 to noisy data: watch training error fall while validation error rises at degree 15.""",
  r'''import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

rng = np.random.default_rng(0)
x = rng.uniform(0, 1, 40).reshape(-1, 1)
y = np.sin(2 * np.pi * x).ravel() + rng.normal(0, 0.2, 40)   # true curve + noise
xtr, ytr, xva, yva = x[:25], y[:25], x[25:], y[25:]

for degree in [1, 3, 15]:
    m = make_pipeline(PolynomialFeatures(degree), LinearRegression()).fit(xtr, ytr)
    print(degree, "train %.3f  valid %.3f" % (mean_squared_error(ytr, m.predict(xtr)),
                                              mean_squared_error(yva, m.predict(xva))))''',
  [("How do you detect overfitting?", "Training score much better than validation score."),
   ("Does more data help underfitting?", "Usually not much; an underfit model needs more capacity or better features.")])

L("m-regularization",
  "Regularisation is anything that stops a model fitting noise: weight penalties, early stopping, dropout, augmentation or simpler models.",
  """Flexible models overfit. Regularisation lets you keep a powerful model while forcing it to prefer simple explanations, which is how most real models are made to generalise.""",
  """The main idea: **add a cost for complexity** to the loss, so the model only uses large weights when they really help.

- **L2 (Ridge)**: adds `λ × (sum of squared weights)`. Shrinks all weights a little.
- **L1 (Lasso)**: adds `λ × (sum of absolute weights)`. Pushes some weights to exactly 0, so it also selects features.
- **λ (lambda, called `alpha` or `1/C` in scikit-learn)** controls the strength: 0 = no regularisation; very large = everything near 0 (underfit).

Other forms: **early stopping** (stop training when validation error starts rising), **dropout** (randomly switch off neurons), **data augmentation**, and limits like a maximum tree depth.""",
  [("The penalty with numbers",
    """Two models have the same data error, 10. Model A weights (2, −1), model B weights (8, −7). L2 penalty with λ = 0.1: A pays 0.1 × (4 + 1) = **0.5**, B pays 0.1 × (64 + 49) = **11.3**. Regularised loss prefers A: same fit, simpler."""),
   ("Choosing λ",
    """Try λ = 0.01, 0.1, 1, 10 with cross-validation and keep the one with the best validation score.""")],
  ("What happens if λ is set extremely high?",
   "All weights are forced close to zero, the model becomes too simple and underfits."),
  [("Ridge (L2)", "penalty on squared weights; shrinks them"),
   ("Lasso (L1)", "penalty on absolute weights; can make some exactly zero"),
   ("λ / alpha", "how strong the penalty is"),
   ("Early stopping", "stop training when validation error stops improving")],
  """Ridge and Lasso on data where only 3 of 20 features matter: Lasso sets most useless weights to exactly zero.""",
  r'''import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso

rng = np.random.default_rng(0)
X = rng.normal(size=(60, 20))
y = 3 * X[:, 0] - 2 * X[:, 1] + X[:, 2] + rng.normal(0, 0.5, 60)   # only 3 features matter

for name, m in [("plain", LinearRegression()), ("ridge", Ridge(alpha=5)), ("lasso", Lasso(alpha=0.1))]:
    m.fit(X, y)
    print(f"{name:6s} zero weights: {np.sum(np.abs(m.coef_) < 1e-6):2d}   biggest: {np.round(m.coef_[:3], 2)}")''',
  [("Which regulariser also does feature selection?", "L1 (Lasso), because it drives some weights to exactly zero."),
   ("How do you pick the regularisation strength?", "Try several values and compare them with cross-validation.")])

L("m-metrics-clf",
  "Accuracy hides which mistakes a classifier makes; the confusion matrix, precision, recall, F1 and AUC show the trade-offs.",
  """A model that's "90% accurate" might miss every fraud or every sick patient. Picking the right metric is a business decision, and interviewers always ask which metric you'd use and why.""",
  """Start from the **confusion matrix** for a yes/no problem:

| | Predicted yes | Predicted no |
| --- | --- | --- |
| **Actually yes** | True positive (TP) | False negative (FN) |
| **Actually no** | False positive (FP) | True negative (TN) |

- **Accuracy** = (TP + TN) / all.
- **Precision** = TP / (TP + FP): when it says yes, how often is it right?
- **Recall** = TP / (TP + FN): of all real yes cases, how many did it find?
- **F1** = the harmonic mean of precision and recall: one number balancing both.
- **ROC-AUC**: how well the model ranks positives above negatives across all thresholds (0.5 = random, 1 = perfect). **PR-AUC** is better when positives are rare.
- **Log loss**: punishes confident wrong probabilities.""",
  [("Compute from a matrix",
    """TP = 40, FN = 10, FP = 20, TN = 930. Accuracy = 970/1000 = **97%**. Precision = 40/60 = **67%**. Recall = 40/50 = **80%**. F1 = 2 × 0.67 × 0.80 / (0.67 + 0.80) ≈ **0.73**."""),
   ("Which metric?",
    """Spam filter: high precision (don't hide real emails). Disease screening: high recall (don't miss patients). Balanced need: F1.""")],
  ("TP = 30, FP = 10, FN = 30. What are precision and recall?",
   "Precision = 30/40 = 75%. Recall = 30/60 = 50%."),
  [("False positive", "the model said yes, the truth was no (false alarm)"),
   ("False negative", "the model said no, the truth was yes (missed case)"),
   ("Threshold", "the probability above which the model says yes"),
   ("AUC", "area under a curve; a threshold-free ranking score")],
  """Computing every metric from the step above with scikit-learn on a real dataset.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0)
m = LogisticRegression(max_iter=5000).fit(Xtr, ytr)

pred = m.predict(Xte)                      # yes/no answers (threshold 0.5)
prob = m.predict_proba(Xte)[:, 1]          # probabilities, needed for AUC
print(confusion_matrix(yte, pred))         # [[TN FP] [FN TP]]
print(classification_report(yte, pred, digits=3))
print("ROC-AUC", round(roc_auc_score(yte, prob), 3))''',
  [("When is accuracy misleading?", "When classes are imbalanced: predicting the common class gets high accuracy with zero usefulness."),
   ("What does raising the threshold usually do?", "Raises precision and lowers recall.")])

L("m-metrics-reg",
  "Regression metrics measure how far predicted numbers are from the true ones; choose by how you want large errors and relative errors treated.",
  """"Our model is off by 10" means nothing until you know which metric and what's typical. Picking MAE vs RMSE vs MAPE changes which model wins, so you need to know what each one rewards.""",
  """For errors e = prediction − truth:

- **MAE** (mean absolute error): average of |e|. Easy to explain: "off by ₹2,000 on average".
- **MSE**: average of e². Punishes big errors heavily. **RMSE** = √MSE, back in the original units.
- **R²**: share of the variation explained, from 1 (perfect) down to 0 (as good as predicting the mean) or below.
- **MAPE**: average of |e| / truth, as a percentage. Good for "we're off by 5%", but breaks when the truth is near 0.

Always also look at **residuals** (errors) plotted against predictions: a pattern means the model is missing something.""",
  [("Compute all of them",
    """True: 100, 200, 300. Predicted: 110, 190, 360. Errors: 10, −10, 60. MAE = 80/3 = **26.7**. MSE = (100 + 100 + 3600)/3 = **1266.7**, RMSE = **35.6**. The single big miss (60) pushes RMSE well above MAE."""),
   ("MAPE",
    """Percentage errors: 10%, 5%, 20% → MAPE = **11.7%**.""")],
  ("Two models: A has errors 5, 5, 5, 5; B has 0, 0, 0, 20. Which has the better MAE? Better RMSE?",
   "Both MAE = 5. RMSE: A = 5, B = 10. RMSE prefers A because it hates the single large error."),
  [("Residual", "the error for one example: prediction minus truth"),
   ("RMSE", "root mean squared error, in the target's units"),
   ("R²", "fraction of the target's variation the model explains")],
  """The numbers from the steps, computed with scikit-learn.""",
  r'''import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error

y_true = np.array([100, 200, 300]); y_pred = np.array([110, 190, 360])
print("MAE ", mean_absolute_error(y_true, y_pred))                 # 26.67
print("RMSE", np.sqrt(mean_squared_error(y_true, y_pred)))         # 35.59
print("MAPE", mean_absolute_percentage_error(y_true, y_pred))      # 0.117 = 11.7%
print("R2  ", r2_score(y_true, y_pred))                            # 0.81''',
  [("Which metric should you use if one big error is very costly?", "RMSE (or MSE), because it squares errors."),
   ("What does R² = 0 mean?", "The model does no better than always predicting the average.")])

L("m-hyperparams",
  "Hyperparameters (tree depth, learning rate, k) are settings you choose, by trying combinations and scoring each with cross-validation.",
  """The same algorithm can go from poor to excellent depending on its settings. Tuning them properly, without fooling yourself, is a core everyday skill.""",
  """- **Parameters** are learned from data (the weights of a line).
- **Hyperparameters** are chosen by you before training (the depth of a tree, k in kNN, the regularisation strength).

Ways to search:
- **Grid search**: try every combination of a list of values.
- **Random search**: try random combinations; usually finds good settings faster.
- **Bayesian search** (e.g. Optuna): uses past results to pick promising next settings.

Score every candidate with cross-validation on the training data, and put preprocessing in a **pipeline** so each fold is clean.""",
  [("Grid size",
    """max_depth ∈ {3, 5, 10} and min_samples_leaf ∈ {1, 5}: 3 × 2 = **6 combinations**. With 5-fold CV that's 30 model fits."""),
   ("Reading the result",
    """Scores: depth 3 → 0.91, depth 5 → 0.94, depth 10 → 0.92. Depth 10 starts to overfit; depth 5 wins.""")],
  ("Is the number of neighbours k in kNN a parameter or a hyperparameter?",
   "A hyperparameter: you choose it; it isn't learned from the data."),
  [("Hyperparameter", "a setting chosen before training"),
   ("Grid search", "trying every combination from lists of values"),
   ("Random search", "trying random combinations from ranges"),
   ("Pipeline", "preprocessing + model treated as one object")],
  """Grid search over a pipeline: every combination is scored with 5-fold cross-validation.""",
  r'''from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

X, y = load_breast_cancer(return_X_y=True)
pipe = Pipeline([("scale", StandardScaler()), ("knn", KNeighborsClassifier())])
grid = {"knn__n_neighbors": [1, 3, 5, 11, 21], "knn__weights": ["uniform", "distance"]}  # 10 combos

search = GridSearchCV(pipe, grid, cv=5).fit(X, y)
print(search.best_params_, round(search.best_score_, 3))''',
  [("Why is random search often better than grid search?", "It tries more distinct values of the important hyperparameters for the same budget."),
   ("Why put the scaler inside the pipeline?", "So each cross-validation fold scales using only its own training part (no leakage).")])

L("m-separability",
  "A classifier splits feature space into regions; the border is the decision boundary, and some data can be split by a straight line while some can't.",
  """Picturing the decision boundary explains why some models fail on some data: a straight-line model can never separate a ring of points inside another ring, while a tree or a neural network can.""",
  """Plot each example as a point using two features, coloured by class.

- The **decision boundary** is where the model switches from one class to the other.
- **Linearly separable** data can be split perfectly by a straight line (in more dimensions, a flat plane called a **hyperplane**).
- **Not linearly separable** data needs a curved boundary: XOR patterns, circles, spirals.

Solutions: use a non-linear model (trees, kNN, kernel SVM, neural networks), or create new features that make it linear, e.g. adding x² + y² turns two rings into two separate heights.""",
  [("XOR",
    """Points (0,0) and (1,1) are class A; (0,1) and (1,0) are class B. Try any straight line: it always leaves one point on the wrong side. Not linearly separable."""),
   ("A new feature fixes it",
    """Add the feature x × y: A points give 0 and 1... still mixed. Add instead "x ≠ y": A → 0, B → 1, now one number separates them. Choosing features changes the geometry.""")],
  ("Two rings: inner ring class A (radius 1), outer ring class B (radius 3). Which single feature makes them separable by a threshold?",
   "The distance from the centre, √(x² + y²): A ≈ 1, B ≈ 3, so 'distance < 2' separates them."),
  [("Decision boundary", "the border where the predicted class changes"),
   ("Linearly separable", "classes that a straight line or plane can split perfectly"),
   ("Hyperplane", "the higher-dimensional version of a straight line")],
  """Two rings: a linear model fails, the same model with the distance feature succeeds.""",
  r'''import numpy as np
from sklearn.datasets import make_circles
from sklearn.linear_model import LogisticRegression

X, y = make_circles(n_samples=400, factor=0.4, noise=0.05, random_state=0)
print("straight line on x, y:", LogisticRegression().fit(X, y).score(X, y))        # about 0.5

r = np.sqrt((X ** 2).sum(axis=1)).reshape(-1, 1)          # new feature: distance from centre
print("straight line on distance:", LogisticRegression().fit(r, y).score(r, y))   # about 1.0''',
  [("Is XOR linearly separable?", "No."),
   ("Two ways to handle non-separable data?", "Use a non-linear model, or engineer features that make the classes linearly separable.")])
