"""Beginner lessons: MLOps & deployment."""
from lesson_util import L

L("m-fastapi",
  "FastAPI turns a trained model into a web API: a client sends JSON, the server checks it, runs the model and returns the prediction.",
  """A model in a notebook helps nobody. An API lets a website, app or other service use it. FastAPI is the most popular Python choice for this, and your C#/ASP.NET Web API experience maps onto it directly.""",
  """1. **Train and save** the model once (e.g. with joblib).
2. **Load it once** when the server starts, not on every request.
3. Describe the request with a **Pydantic model**: the fields and their types. FastAPI validates every request and returns a clear 422 error for bad input.
4. Write an endpoint, e.g. `POST /predict`, that turns the request into model features, predicts, and returns JSON (prediction, probability, model version).
5. Run it with **uvicorn**. FastAPI generates interactive docs at `/docs` automatically.
6. Add a `GET /health` endpoint for monitoring, and log requests and latency.

It's the same idea as an ASP.NET Core controller with a request DTO and model validation.""",
  [("Request and response",
    """Request: `{"size_sqft": 1200, "age_years": 5}`. Response: `{"price_lakhs": 61.3, "model_version": "1.2"}`. Sending `{"size_sqft": "big"}` returns 422 with an explanation, before your code runs."""),
   ("Latency budget",
    """Loading the model takes 2 seconds; predicting takes 3 ms. Load per request and every call takes 2 s; load at start-up and calls take a few milliseconds.""")],
  ("Where should the model be loaded in a FastAPI app, and why?",
   "Once at start-up (module level or a lifespan handler), so requests don't pay the loading cost."),
  [("Endpoint", "a URL plus HTTP method the API responds to"),
   ("Pydantic model", "a class describing and validating request/response fields"),
   ("422 error", "FastAPI's response for invalid input"),
   ("uvicorn", "the server that runs a FastAPI app")],
  """A complete prediction API, tested in-process with FastAPI's TestClient (in Colab or VS Code run it for real with `uvicorn app:app`).""",
  r'''import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sklearn.linear_model import LinearRegression

X = np.array([[800, 10], [1200, 5], [1500, 2], [2000, 1]]); y = np.array([30, 60, 80, 110])
model = LinearRegression().fit(X, y)                         # in real life: joblib.load("model.joblib"), once

class House(BaseModel):                                      # the request "DTO", validated automatically
    size_sqft: float = Field(gt=100, lt=20000)
    age_years: float = Field(ge=0, le=100)

app = FastAPI(title="House price API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(h: House):
    price = float(model.predict([[h.size_sqft, h.age_years]])[0])
    return {"price_lakhs": round(price, 1), "model_version": "1.0"}

client = TestClient(app)
print(client.get("/health").json())
print(client.post("/predict", json={"size_sqft": 1300, "age_years": 4}).json())
print(client.post("/predict", json={"size_sqft": "big", "age_years": 4}).status_code)   # 422: invalid input''',
  [("What does FastAPI do with a request that doesn't match the Pydantic model?", "Rejects it with a 422 response describing the problem."),
   ("Why add a /health endpoint?", "So load balancers and monitoring can check the service is alive.")])

L("m-deployment",
  "Deployment puts a model where it creates value; the right pattern (batch or real-time, server, serverless or on-device) depends on speed needs, volume, cost and where the data is.",
  """System design interviews always ask how you'd serve a model. The choice affects cost by orders of magnitude and decides what's possible (an offline phone app can't call a server).""",
  """| Pattern | How | When |
| --- | --- | --- |
| **Batch** | run predictions on a schedule, store results in a table | nightly churn scores, weekly recommendations emails |
| **Real-time API** | a service answers each request in milliseconds | fraud check at payment, search ranking |
| **Streaming** | predict on events from a queue (Kafka) | sensor alerts, live dashboards |
| **Serverless** | functions that start on demand (AWS Lambda, Cloud Run) | spiky, low traffic; small models |
| **Edge / on-device** | the model runs on the phone, browser or machine | offline use, privacy, very low latency |
| **Demo** | Hugging Face Spaces, Streamlit, Gradio | showcasing; portfolio projects |

Packaging: put the code, model and dependencies in a **Docker** image so it runs the same everywhere. Then run it on a VM, Kubernetes, or a managed service (Azure ML, SageMaker, Vertex AI).

Release safely: **shadow mode** (run the new model silently alongside the old one), **canary** (send 5% of traffic to it), and **A/B tests**, with the ability to roll back.""",
  [("Batch vs real-time cost",
    """Scoring 1 million customers once a night takes 10 minutes of compute. Serving the same model in real time means a server running 24/7, even if most customers never visit that day."""),
   ("Choosing",
    """A loan decision while the customer waits on the app → real-time API. Next month's credit-limit review for all customers → batch.""")],
  ("A factory camera must flag defects within 50 ms with an unreliable internet connection. Which deployment pattern?",
   "Edge / on-device deployment, running the model locally next to the camera."),
  [("Latency", "how long one prediction takes"),
   ("Throughput", "how many predictions per second"),
   ("Docker image", "a packaged app with all its dependencies"),
   ("Canary release", "sending a small share of traffic to a new version first"),
   ("Shadow mode", "running a new model in parallel without using its outputs")],
  """Batch scoring and a real-time function side by side, plus the Dockerfile you'd use to package the API (printed, not built).""",
  r'''import time, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression

rng = np.random.default_rng(0)
X_train = rng.normal(size=(1000, 5)); y_train = (X_train[:, 0] + X_train[:, 1] > 0).astype(int)
model = LogisticRegression().fit(X_train, y_train)

customers = pd.DataFrame(rng.normal(size=(100_000, 5)), columns=[f"f{i}" for i in range(5)])
t = time.time()
customers["churn_score"] = model.predict_proba(customers.values)[:, 1]      # batch: all rows at once
print(f"batch scored {len(customers):,} rows in {time.time() - t:.3f}s")

def realtime(features):                                                     # real-time: one request
    return float(model.predict_proba([features])[0, 1])
t = time.time(); realtime([0.2, -1.0, 0.5, 0.0, 1.0])
print(f"one real-time prediction in {(time.time() - t) * 1000:.2f} ms")

print("""Dockerfile:
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py model.joblib ./
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]""")''',
  [("When is batch prediction the better choice?", "When results aren't needed instantly and can be precomputed on a schedule, which is much cheaper."),
   ("What does a canary release protect against?", "A bad new model affecting all users at once; problems show up on a small share of traffic first.")])

L("m-practical-issues",
  "Most ML work happens after launch: data changes, pipelines break and models silently get worse, so you monitor inputs and outputs and retrain when needed.",
  """A model that was 92% accurate at launch can be 75% six months later without any error message. Interviewers ask "how would you know your model is degrading?" in nearly every ML design round.""",
  """Common problems:
- **Data drift**: the inputs change (new customer segments, a new app version, inflation changing prices).
- **Concept drift**: the relationship changes (fraudsters change tactics, COVID changed shopping).
- **Training–serving skew**: features are computed differently in production than in training (a different unit, a missing default, a time-zone bug).
- **Feedback loops**: the model's decisions shape the data it later learns from (only approved loans get repayment labels).
- **Delayed labels**: you only learn whether a prediction was right weeks later.
- **Broken pipelines**: an upstream column becomes all nulls.

Monitoring:
- **Data quality**: missing values, ranges, schema.
- **Input drift**: compare feature distributions with training using **PSI** (population stability index) or a KS test.
- **Output drift**: is the share of positive predictions changing?
- **Performance**: accuracy/recall once labels arrive.
- **System**: latency, errors, cost.

Respond with alerts, investigation, retraining (scheduled or triggered by drift), and fallbacks such as rules.""",
  [("PSI by hand",
    """Two bins. Training shares 50% / 50%, now 70% / 30%. PSI = Σ (now − train) × ln(now/train) = 0.2 × ln(1.4) + (−0.2) × ln(0.6) = 0.067 + 0.102 = **0.17**. Rule of thumb: < 0.1 stable, 0.1–0.25 watch, > 0.25 significant drift."""),
   ("Skew example",
    """Training used income in thousands; the production service sends income in rupees. Every applicant looks 1,000× richer and approvals jump. Monitoring input ranges catches it on day one.""")],
  ("Approval rates suddenly rise from 40% to 70% overnight with no business change. What do you check first?",
   "Input data and features: a pipeline or unit change (training–serving skew), missing values filled wrongly, or a schema change."),
  [("Data drift", "the input distribution changes"),
   ("Concept drift", "the input–output relationship changes"),
   ("Training–serving skew", "features computed differently in training and production"),
   ("PSI", "population stability index, a drift score")],
  """A PSI drift check comparing a feature's training distribution with two production weeks.""",
  r'''import numpy as np
rng = np.random.default_rng(0)

def psi(train, live, bins=10):
    edges = np.quantile(train, np.linspace(0, 1, bins + 1)); edges[0], edges[-1] = -np.inf, np.inf
    a = np.histogram(train, edges)[0] / len(train)
    b = np.histogram(live, edges)[0] / len(live)
    a, b = np.clip(a, 1e-6, None), np.clip(b, 1e-6, None)
    return float(np.sum((b - a) * np.log(b / a)))

train_income = rng.normal(50, 10, 10_000)
week1 = rng.normal(50.5, 10, 2_000)                 # basically the same
week2 = rng.normal(58, 13, 2_000)                   # a new customer segment arrived
for name, live in [("week 1", week1), ("week 2", week2)]:
    v = psi(train_income, live)
    print(f"{name}: PSI {v:.3f} ->", "stable" if v < 0.1 else "watch" if v < 0.25 else "DRIFT: investigate / retrain")''',
  [("What's the difference between data drift and concept drift?", "Data drift: inputs change. Concept drift: the mapping from inputs to the right answer changes."),
   ("Why can't you always monitor accuracy directly?", "True labels often arrive late (or never), so you monitor inputs and outputs as early warnings.")])

L("m-compression",
  "Compression makes models smaller and faster (for phones, browsers and cheaper servers) with little accuracy loss: quantisation, pruning, knowledge distillation and efficient export formats like ONNX.",
  """Latency and serving cost often decide whether a model ships. Making a model 4× smaller and 3× faster with 1% accuracy loss is a common, valued engineering task.""",
  """- **Quantisation**: store weights (and sometimes activations) with fewer bits: 32-bit float → 8-bit integer is 4× smaller and often 2–4× faster on CPUs. **Post-training quantisation** is quick; **quantisation-aware training** keeps more accuracy. LLMs often use 4-bit.
- **Pruning**: remove weights (or whole neurons, channels or heads) that matter least, e.g. the smallest in absolute value, then fine-tune briefly. Structured pruning (whole channels) gives real speed-ups on normal hardware.
- **Knowledge distillation**: train a small **student** to match a big **teacher's** output probabilities (its "soft labels"), which carry more information than hard labels. DistilBERT is 40% smaller than BERT and keeps ~97% of its performance.
- **Efficient formats and runtimes**: export to **ONNX** and run with ONNX Runtime, TensorRT, OpenVINO, TFLite or Core ML.
- Always measure the accuracy drop and the real latency on the target device.""",
  [("Size by hand",
    """A model with 25 million parameters: float32 = 25M × 4 bytes = **100 MB**; int8 = **25 MB**; 4-bit = **12.5 MB**."""),
   ("Soft labels",
    """For a cat photo, the teacher says cat 0.80, fox 0.15, car 0.05. The student learns not just "cat" but also "cats look a bit like foxes and nothing like cars".""")],
  ("Which technique trains a small model to imitate a large one?",
   "Knowledge distillation."),
  [("Quantisation", "fewer bits per number"),
   ("Pruning", "removing unimportant weights or structures"),
   ("Distillation", "a small student learning from a big teacher's outputs"),
   ("ONNX", "an open, portable format for trained models")],
  """Dynamic int8 quantisation, magnitude pruning and distillation on one small PyTorch model, with size and accuracy measured each time.""",
  r'''import io, torch, torch.nn as nn, torch.nn.functional as F
import torch.nn.utils.prune as prune
from sklearn.datasets import load_digits
torch.manual_seed(0)
X, y = load_digits(return_X_y=True); X = torch.tensor(X / 16, dtype=torch.float32); y = torch.tensor(y)
tr, te = slice(0, 1400), slice(1400, None)

def fit(model, target=None, T=4.0, steps=400):
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    for _ in range(steps):
        out = model(X[tr])
        loss = F.cross_entropy(out, y[tr]) if target is None else \
               F.kl_div(F.log_softmax(out / T, 1), F.softmax(target / T, 1), reduction="batchmean") * T * T
        opt.zero_grad(); loss.backward(); opt.step()
    return model
acc = lambda m: (m(X[te]).argmax(1) == y[te]).float().mean().item()
size_kb = lambda m: len((b := io.BytesIO(), torch.save(m.state_dict(), b))[0].getvalue()) / 1024

teacher = fit(nn.Sequential(nn.Linear(64, 512), nn.ReLU(), nn.Linear(512, 512), nn.ReLU(), nn.Linear(512, 10)))
print(f"teacher      acc {acc(teacher):.3f}  size {size_kb(teacher):6.0f} KB")
q = torch.ao.quantization.quantize_dynamic(teacher, {nn.Linear}, dtype=torch.qint8)   # int8 weights
print(f"int8         acc {acc(q):.3f}  size {size_kb(q):6.0f} KB")
for layer in [teacher[0], teacher[2]]: prune.l1_unstructured(layer, "weight", amount=0.7)   # drop 70% smallest
print(f"70% pruned   acc {acc(teacher):.3f}")
with torch.no_grad(): soft = teacher(X[tr])
student = fit(nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10)), target=soft)  # learn from soft labels
print(f"student      acc {acc(student):.3f}  size {size_kb(student):6.0f} KB")''',
  [("Roughly how much smaller is an int8 model than a float32 one?", "About 4 times smaller."),
   ("Why do soft labels help distillation?", "They show how the teacher relates classes (which wrong answers are 'close'), giving the student more information per example.")])

L("m-mlops",
  "MLOps applies DevOps habits to ML: track experiments, version data and models, register and promote models, test and deploy automatically, and keep features consistent, so teams can rebuild and update models reliably.",
  """"It worked on my laptop" doesn't scale. Companies need to know which data and code produced the model in production, reproduce it, and ship updates safely. This is a large part of senior ML engineering roles.""",
  """The building blocks:

- **Experiment tracking** (MLflow, Weights & Biases): log every run's parameters, metrics, code version and artefacts so you can compare and reproduce.
- **Data and model versioning** (DVC, lakeFS, registry versions): know exactly which data and code made which model.
- **Model registry**: a catalogue of trained models with stages (staging → production → archived) and approval.
- **Pipelines / orchestration** (Airflow, Kubeflow, Azure ML pipelines): automated steps: ingest → validate → features → train → evaluate → register → deploy.
- **CI/CD for ML**: on every change run unit tests, data-validation checks and a training smoke test; deploy automatically only if the new model beats the current one on a fixed evaluation set.
- **Feature store** (Feast, Tecton): compute features once and serve the same values to training and to production, avoiding training–serving skew.
- **Monitoring** and **retraining triggers** close the loop.

Maturity grows from manual notebooks → automated training pipelines → fully automated CI/CD with monitoring-triggered retraining.""",
  [("Reproducibility",
    """Six months later an auditor asks why a loan was rejected. With tracking you find model v14, trained on data snapshot 2026-05-01 with commit a1b2c3, and can rebuild it exactly."""),
   ("Promotion gate",
    """New model F1 0.83 vs production 0.81 on the frozen test set, and no group's recall drops more than 1 point → promote to staging, then canary.""")],
  ("What problem does a feature store mainly solve?",
   "Training–serving skew: it serves the same, consistently computed feature values for training and for online predictions."),
  [("Experiment tracking", "recording parameters, metrics and artefacts of each run"),
   ("Model registry", "a versioned catalogue of models with stages"),
   ("CI/CD", "continuous integration and delivery: automatic tests and deployment"),
   ("Feature store", "a shared system that computes and serves features")],
  """Experiment tracking with MLflow (logged to a local folder): three runs with different settings, then the best one is picked by its logged metric.""",
  r'''import mlflow, tempfile
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

mlflow.set_tracking_uri("sqlite:///" + tempfile.mkdtemp() + "/mlflow.db")   # local tracking database
mlflow.set_experiment("cancer-rf")
X, y = load_breast_cancer(return_X_y=True)

for depth in [2, 5, None]:
    with mlflow.start_run():
        mlflow.log_param("max_depth", depth)                    # what we tried
        score = cross_val_score(RandomForestClassifier(max_depth=depth, random_state=0), X, y, cv=5).mean()
        mlflow.log_metric("cv_accuracy", score)                 # how it did

runs = mlflow.search_runs(order_by=["metrics.cv_accuracy DESC"])
print(runs[["params.max_depth", "metrics.cv_accuracy"]])
print("best run:", runs.iloc[0]["run_id"][:8], "-> register and promote this one")''',
  [("What should an experiment tracker record for each run?", "Parameters, metrics, code version, data version and output artefacts."),
   ("What check should gate an automatic deployment?", "The new model must beat (or match) the production model on a fixed evaluation set, including per-group checks.")])

L("m-ml-system-design",
  "ML system design interviews ask you to design an end-to-end ML product; use a framework: clarify, frame the ML task, data, features, model, evaluation, serving, monitoring.",
  """This round is standard for ML and senior engineering roles at Google, Microsoft, Amazon, Flipkart and others. A clear structure matters as much as the model choice.""",
  """A 7-step framework (spend about 5 minutes on each):

1. **Clarify requirements**: the business goal, users, scale (requests per second, number of items), latency limit, constraints (privacy, cost).
2. **Frame as an ML task**: what exactly is predicted (e.g. P(click) for a user–item pair), input and output, and the **offline metric** (AUC, NDCG) and **online metric** (CTR, revenue, retention).
3. **Data**: sources, labels (explicit or implicit like clicks), how to sample negatives, class imbalance, data freshness.
4. **Features**: user, item, context and cross features; embeddings; how they're computed and served (feature store).
5. **Model**: start with a simple baseline (logistic regression, popularity), then a stronger model (gradient boosting, two-tower + ranker). Often **two stages**: fast **candidate retrieval** (thousands from millions) then precise **ranking** (top hundreds).
6. **Evaluation**: offline (time-based split, the chosen metrics, slices by user group), then online A/B test.
7. **Serving and monitoring**: batch vs real-time, latency budget, caching, fallbacks; monitor drift and metrics; retraining schedule; fairness and abuse.""",
  [("Funnel numbers",
    """A video feed: 10 million videos → retrieval picks 1,000 per user in ~20 ms using embeddings → a ranker scores those 1,000 in ~50 ms → business rules and diversity → top 20 shown."""),
   ("Metrics pair",
    """Offline: AUC 0.78 → 0.80 on next week's data. Online: A/B test shows +2% watch time with no rise in "not interested" clicks. Both must agree before launch.""")],
  ("Why do recommender systems split retrieval and ranking?",
   "Scoring millions of items with a heavy model per request is too slow; a fast retriever narrows to a few thousand, then an accurate ranker orders them."),
  [("Offline / online metric", "measured on stored data / measured on live users"),
   ("Candidate retrieval", "quickly finding a shortlist from a huge catalogue"),
   ("Ranking", "precisely ordering the shortlist"),
   ("A/B test", "comparing versions on randomly split live users")],
  """A two-stage recommender in miniature: embedding retrieval narrows 5,000 items to 100, then a ranking model orders them; latency is measured for each stage.""",
  r'''import time, numpy as np
from sklearn.linear_model import LogisticRegression
rng = np.random.default_rng(0)
n_items, d = 5000, 16
item_emb = rng.normal(size=(n_items, d)); item_pop = rng.random(n_items)       # embeddings + popularity
user = rng.normal(size=d)

# training data for the ranker: (similarity, popularity) -> clicked?
sims_tr, pop_tr = rng.normal(size=5000), rng.random(5000)
clicked = (0.8 * sims_tr + 1.5 * pop_tr + rng.normal(0, 0.5, 5000) > 1.2).astype(int)
ranker = LogisticRegression().fit(np.column_stack([sims_tr, pop_tr]), clicked)

t = time.time()
scores = item_emb @ user / np.sqrt(d)                                        # stage 1: retrieval
candidates = np.argpartition(-scores, 100)[:100]
t1 = time.time()
feats = np.column_stack([scores[candidates], item_pop[candidates]])         # stage 2: ranking
top = candidates[np.argsort(-ranker.predict_proba(feats)[:, 1])][:10]
t2 = time.time()
print(f"retrieval {1000 * (t1 - t):.2f} ms -> 100 candidates; ranking {1000 * (t2 - t1):.2f} ms -> top 10: {top[:5]}...")''',
  [("Name the 7 steps of the framework.", "Clarify, frame the ML task, data, features, model, evaluation, serving and monitoring."),
   ("Why report both offline and online metrics?", "Offline metrics are cheap proxies; only online tests show the real business effect.")])

L("m-industry-cases",
  "Real deployments teach lessons textbooks skip: good data and simple models often win, latency and cost shape the design, and monitoring matters as much as modelling.",
  """Interviewers love candidates who can say "here's how company X solved this and why". Case studies also stop you over-engineering: most production ML is simpler than research papers.""",
  """Recurring lessons from published case studies:

- **Data beats algorithms**: better labels and features usually help more than a fancier model. Many teams report bigger gains from fixing data pipelines than from new architectures.
- **Start simple**: Google's "Rules of ML" advises launching a simple, well-instrumented model first, then iterating.
- **Two-stage systems at scale**: YouTube, Pinterest and Instagram recommendations use fast candidate generation followed by heavier ranking models.
- **Latency and cost decide**: models must fit a millisecond budget; distillation, caching and batch precomputation are common.
- **Feedback loops and bias**: recommenders and credit models shape their own future data; teams deliberately add exploration and fairness checks.
- **Monitoring and retraining**: fraud models (PayPal, Stripe) retrain often because attackers adapt.
- **Human + model**: content moderation and medical tools route hard cases to people.
- **Measure real outcomes**: A/B tests on business metrics, not just offline accuracy (Netflix famously didn't deploy the full Netflix Prize winning ensemble because the engineering cost outweighed the accuracy gain).

When you read a case study, note: the problem, the metric, the data, the model, the serving constraints, and what went wrong.""",
  [("Reading a case like an engineer",
    """Uber's ETA prediction: problem = arrival time; metric = mean absolute error plus share of trips within tolerance; data = GPS traces and maps; model = road-network routing combined with ML corrections; constraint = millions of requests with low latency. That's the same shape as your GoldenHour project."""),
   ("The Netflix Prize lesson",
    """A 10% offline improvement from a giant ensemble wasn't worth running in production; a couple of simpler components captured most of the value.""")],
  ("A new model improves offline AUC by 0.3% but doubles latency and serving cost. What would you do?",
   "Probably not ship it as is: test the business impact online if cheap, or distil/simplify it; small offline gains often don't justify large cost and latency increases."),
  [("Case study", "a write-up of a real deployed system"),
   ("Rules of ML", "Google's guide to practical ML engineering"),
   ("Exploration", "deliberately showing some new or random items to learn more"),
   ("Cost–benefit", "comparing a model's gains with its engineering and serving costs")],
  """A worked cost–benefit check: does a slower, more accurate model pay for itself? (Numbers are illustrative.)""",
  r'''requests_per_day = 5_000_000
value_per_point_auc = 40_000                 # extra revenue per day per +1.0 AUC point (from past A/B tests)

models = {"current (GBM)":      {"auc": 0.800, "ms": 8,  "cost_per_1k": 0.002},
          "new (big ensemble)": {"auc": 0.803, "ms": 19, "cost_per_1k": 0.006},
          "new (distilled)":    {"auc": 0.802, "ms": 9,  "cost_per_1k": 0.0025}}
base = models["current (GBM)"]
for name, m in models.items():
    gain = (m["auc"] - base["auc"]) * 100 * value_per_point_auc
    extra_cost = (m["cost_per_1k"] - base["cost_per_1k"]) * requests_per_day / 1000
    ok = m["ms"] <= 15
    print(f"{name:20s} gain/day {gain:8.0f}  extra cost/day {extra_cost:6.0f}  latency {m['ms']:2d} ms  "
          f"{'within budget' if ok else 'TOO SLOW'}")''',
  [("Name two recurring lessons from industry ML.", "Data quality beats model complexity; start simple; latency/cost shape the design; monitoring and retraining matter."),
   ("What should you note when reading a case study?", "Problem, metric, data, model, serving constraints and what went wrong.")])
