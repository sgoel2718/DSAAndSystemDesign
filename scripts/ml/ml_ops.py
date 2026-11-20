"""Module 3/4: deployment, FastAPI, practical issues, compression, MLOps, ML system design, industry case studies."""
from ml_util import M

OPS = [
M("m-fastapi", "Serving models with FastAPI", "Intermediate",
  "FastAPI turns a trained model into a web API: clients send JSON, the server validates it, runs the model and returns predictions. It's fast, type-checked and generates interactive docs automatically.",
  """### Why FastAPI
Pydantic validation of inputs/outputs, automatic OpenAPI docs at `/docs`, async support, high performance (Starlette + Uvicorn), simple Python.

### Serving pattern
1. Train and save the model (joblib for scikit-learn, `torch.save` / ONNX / TorchScript for PyTorch, `.keras` for Keras).
2. **Load once at startup** (lifespan event or module import), not per request.
3. Define request/response schemas with Pydantic (types, ranges, examples).
4. `POST /predict` endpoint → preprocess → predict → return JSON (+ model version, probabilities).
5. `GET /health` for load balancers; log requests and latencies.
6. Run with `uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2`; containerise with Docker.

### Production concerns
Batch endpoints for throughput; timeouts; input size limits; authentication (API keys/OAuth); rate limiting; CPU-bound models in worker processes (not blocking the event loop); GPU servers (Triton, TorchServe, vLLM) for heavy models; versioned endpoints (`/v1/predict`).""",
  code="""
import joblib, numpy as np
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

data = load_iris(); joblib.dump(LogisticRegression(max_iter=1000).fit(data.data, data.target), "iris.joblib")    # 1) train + save

app = FastAPI(title="Iris classifier", version="1.0")
MODEL = joblib.load("iris.joblib")                                   # 2) load once at startup
class Flower(BaseModel):                                              # 3) validated input schema
    sepal_length: float = Field(gt=0, lt=10); sepal_width: float = Field(gt=0, lt=10)
    petal_length: float = Field(gt=0, lt=10); petal_width: float = Field(gt=0, lt=10)
class Prediction(BaseModel):
    species: str; probability: float; model_version: str
@app.get("/health")
def health(): return {"status": "ok"}
@app.post("/predict", response_model=Prediction)
def predict(f: Flower):
    x = np.array([[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]]); p = MODEL.predict_proba(x)[0]
    if p.max() < 0.4: raise HTTPException(422, "low-confidence input")
    return Prediction(species=data.target_names[p.argmax()], probability=round(float(p.max()), 3), model_version="1.0")

client = TestClient(app)                                              # test without starting a server
print(client.get("/health").json())
print(client.post("/predict", json={"sepal_length": 6.7, "sepal_width": 3.0, "petal_length": 5.2, "petal_width": 2.3}).json())
print("invalid input ->", client.post("/predict", json={"sepal_length": -1, "sepal_width": 3, "petal_length": 5, "petal_width": 2}).status_code)
# Run for real:  uvicorn app:app --reload   then open http://127.0.0.1:8000/docs
""",
  say=[("How would you deploy a scikit-learn model as a REST API?",
        "\"Save the whole fitted pipeline — preprocessing plus model — with joblib, load it once at startup in a FastAPI app, define Pydantic request and response schemas, and expose a predict endpoint plus a health check. Write tests with TestClient, package it in a Docker image with pinned dependencies, run it behind a load balancer with several workers, and add logging, monitoring of latency and prediction distributions, and model versioning.\"")]),

M("m-deployment", "Deployment patterns: batch vs real-time, Docker, cloud, serverless, edge, demos", "Intermediate",
  "Deployment puts a model where it creates value. The right pattern depends on latency needs, volume, cost and where the data lives.",
  """|Pattern|How|Use when|
|**Batch / offline**|scheduled job scores many rows, writes results to a table|daily churn scores, recommendations precomputed overnight|
|**Online / real-time API**|REST/gRPC service answers each request in milliseconds|fraud check at payment time, search ranking|
|**Streaming**|consume events (Kafka) and score continuously|real-time tweet analytics, IoT anomalies|
|**Embedded / edge**|model runs on the phone or device (TFLite, Core ML, ONNX Runtime Mobile)|offline use, privacy, low latency (keyboard, camera)|
|**Serverless**|functions (AWS Lambda, Cloud Run) scale to zero|spiky low-volume traffic, small models|
|**Managed platforms**|SageMaker, Vertex AI, Azure ML, Databricks, Hugging Face Inference Endpoints|teams wanting hosted training + serving|

### Packaging
**Docker** image with pinned dependencies and the model artifact (or pull from a model registry); Kubernetes for scaling; GPUs for deep models.

### Release strategies
Shadow deployment (run silently, compare), canary (small % of traffic), A/B tests, blue–green with instant rollback.

### Quick demos and internal tools
**Gradio** and **Streamlit** build web UIs in a few lines; Hugging Face Spaces hosts them for free — perfect for capstone presentations.""",
  code="""
dockerfile = '''FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py iris.joblib ./
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]'''
requirements = "fastapi==0.115.*\\nuvicorn[standard]\\nscikit-learn==1.5.*\\njoblib\\nnumpy"
gradio_app = '''import gradio as gr, joblib
model = joblib.load("iris.joblib")
def predict(sl, sw, pl, pw): return {n: float(p) for n, p in zip(["setosa", "versicolor", "virginica"], model.predict_proba([[sl, sw, pl, pw]])[0])}
gr.Interface(predict, [gr.Slider(4, 8), gr.Slider(2, 4.5), gr.Slider(1, 7), gr.Slider(0.1, 2.5)], gr.Label()).launch()'''
for name, text in [("Dockerfile", dockerfile), ("requirements.txt", requirements), ("gradio_demo.py", gradio_app)]:
    open(name, "w").write(text); print(f"--- {name} ---\\n{text}\\n")
print("build & run:  docker build -t iris-api . && docker run -p 8000:8000 iris-api")
""",
  say=[("Batch or real-time inference — how do you decide?",
        "\"By when the prediction is needed and how fresh the inputs must be. If predictions can be computed ahead of time — daily churn scores, nightly recommendations — batch is simpler, cheaper and easier to monitor. If the decision depends on information available only at request time — a payment being made, a search query — I need an online service with latency budgets. Many systems combine them: batch-precomputed candidates and features with a light real-time re-ranker.\"")]),

M("m-practical-issues", "Practical issues in production ML: drift, monitoring, training–serving skew, feedback loops", "Intermediate",
  "Most ML work happens after the first model ships. Data changes, pipelines break and models silently degrade — monitoring and retraining keep them healthy.",
  """### What goes wrong
- **Data drift (covariate shift)**: input distributions change (new users, new products, seasons, a pandemic).
- **Concept drift**: the relationship between inputs and target changes (fraudsters adapt).
- **Label shift**: class proportions change.
- **Training–serving skew**: features computed differently in training (SQL in a notebook) and serving (Java service) → mismatches. Fix with shared feature code / a **feature store**.
- **Data quality issues**: missing columns, unit changes, schema changes, upstream bugs.
- **Feedback loops**: the model influences its own future training data (recommendations, predictive policing).
- **Delayed labels**: you learn whether a loan defaulted months later.

### Monitoring
Service metrics (latency, errors, throughput); data metrics (missing rates, ranges, distribution drift — PSI, KS tests); prediction distribution; model metrics once labels arrive; business KPIs; alerts and dashboards (Evidently, WhyLabs, Arize, Prometheus/Grafana).

### Responding
Retrain on a schedule or when drift triggers; keep the previous model for rollback; validate new models offline + shadow/canary before full release.

### Other practical concerns
Latency and cost budgets, reproducibility (seeds, versions, data snapshots), security of model endpoints, documentation (model cards), stakeholder trust.""",
  code="""
import numpy as np
def psi(expected, actual, bins=10):
    cuts = np.quantile(expected, np.linspace(0, 1, bins + 1)); cuts[0], cuts[-1] = -np.inf, np.inf
    e = np.histogram(expected, cuts)[0] / len(expected); a = np.histogram(actual, cuts)[0] / len(actual)
    e, a = np.clip(e, 1e-6, None), np.clip(a, 1e-6, None); return float(((a - e) * np.log(a / e)).sum())
rng = np.random.default_rng(0)
train_income = rng.lognormal(10, 0.5, 20000)
for month, shift in [("Jan", 0.0), ("Feb", 0.05), ("Mar", 0.3)]:
    prod = rng.lognormal(10 + shift, 0.5, 5000); v = psi(train_income, prod)
    status = "stable" if v < 0.1 else "moderate drift - investigate" if v < 0.25 else "major drift - retrain"
    print(f"{month}: PSI = {v:.3f} -> {status}")
schema = {"age": (18, 100), "income": (0, 1e8)}
row = {"age": 230, "income": 52000}
print("data-quality violations:", [k for k, (lo, hi) in schema.items() if not lo <= row[k] <= hi])
""",
  say=[("Your model's accuracy dropped three months after launch. What do you do?",
        "\"First confirm it's real — check label delays and the evaluation itself. Then look for pipeline problems: schema changes, missing features, training–serving skew. Then compare input and prediction distributions to training data per feature to find drift, and slice errors by segment to see where it degraded. Depending on the cause: fix the pipeline, retrain on recent data, add features for the new patterns, or redesign. Afterwards add monitoring and drift alerts so it's caught earlier next time.\"")]),

M("m-compression", "Model compression: quantisation, pruning, knowledge distillation, ONNX", "Advanced",
  "Compression makes models smaller and faster — for phones, browsers, cheaper servers and lower latency — usually with little accuracy loss.",
  """### Quantisation
Store weights (and activations) in fewer bits: float32 → float16/bfloat16 → **int8** → 4-bit. 2–8× smaller, faster on supporting hardware.
- **Post-training quantisation (PTQ)**: dynamic (weights int8, activations quantised on the fly — great for linear/LSTM layers), static (calibrate activation ranges on sample data).
- **Quantisation-aware training (QAT)**: simulate quantisation during training for best accuracy.
- LLM-specific: GPTQ, AWQ, bitsandbytes NF4, GGUF.

### Pruning
Remove weights near zero (**unstructured** — sparse matrices) or whole channels/heads/layers (**structured** — real speed-ups). Prune → fine-tune → repeat. Lottery-ticket hypothesis.

### Knowledge distillation
A small **student** learns to match a big **teacher**'s soft probabilities (with temperature T) plus the true labels: L = α·CE(y, student) + (1 − α)·T²·KL(teacher_T ‖ student_T). DistilBERT keeps ~97% of BERT's performance at 60% size and is 60% faster.

### Efficient architectures and runtimes
MobileNet/EfficientNet, low-rank factorisation, weight sharing; export to **ONNX** and run with ONNX Runtime, TensorRT, OpenVINO, TFLite, Core ML; `torch.compile`.

Always measure accuracy, latency and size on the target hardware.""",
  code="""
import os, torch, torch.nn as nn, torch.nn.functional as F, numpy as np
from sklearn.datasets import load_digits
torch.manual_seed(0)
d = load_digits(); X = torch.tensor(d.data / 16, dtype=torch.float32); y = torch.tensor(d.target); Xtr, ytr, Xte, yte = X[:1400], y[:1400], X[1400:], y[1400:]
def train(model, loss_fn, epochs=40):
    opt = torch.optim.Adam(model.parameters(), 2e-3)
    for _ in range(epochs):
        for i in range(0, 1400, 100): opt.zero_grad(); loss_fn(model, Xtr[i:i + 100], ytr[i:i + 100]).backward(); opt.step()
    return model
acc = lambda m: (m(Xte).argmax(1) == yte).float().mean().item()
size_kb = lambda m: (torch.save(m.state_dict(), "m.pt"), os.path.getsize("m.pt") / 1024)[1]
teacher = train(nn.Sequential(nn.Linear(64, 512), nn.ReLU(), nn.Linear(512, 512), nn.ReLU(), nn.Linear(512, 10)), lambda m, x, t: F.cross_entropy(m(x), t))
print(f"teacher: acc {acc(teacher):.3f}, {size_kb(teacher):.0f} KB")
q = torch.ao.quantization.quantize_dynamic(teacher, {nn.Linear}, dtype=torch.qint8)
print(f"int8 dynamic quantised teacher: acc {acc(q):.3f}, {size_kb(q):.0f} KB")
pruned = train(nn.Sequential(nn.Linear(64, 512), nn.ReLU(), nn.Linear(512, 512), nn.ReLU(), nn.Linear(512, 10)), lambda m, x, t: F.cross_entropy(m(x), t))
import torch.nn.utils.prune as prune
for layer in [pruned[0], pruned[2]]: prune.l1_unstructured(layer, "weight", amount=0.8)
print(f"80% of weights pruned: acc {acc(pruned):.3f}")
T, alpha = 4.0, 0.3
def distill_loss(m, x, t):
    with torch.no_grad(): soft = F.softmax(teacher(x) / T, 1)
    return alpha * F.cross_entropy(m(x), t) + (1 - alpha) * T * T * F.kl_div(F.log_softmax(m(x) / T, 1), soft, reduction="batchmean")
student = train(nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10)), distill_loss)
print(f"distilled student: acc {acc(student):.3f}, {size_kb(student):.0f} KB")
torch.onnx.export(student, (Xte[:1],), "student.onnx", input_names=["x"], output_names=["logits"], dynamic_axes={"x": {0: "batch"}}, dynamo=False)
import onnxruntime as ort
sess = ort.InferenceSession("student.onnx"); out = sess.run(None, {"x": Xte[:5].numpy()})[0]
print("ONNX Runtime predictions match PyTorch:", np.allclose(out, student(Xte[:5]).detach().numpy(), atol=1e-5))
""",
  say=[("How does knowledge distillation work?",
        "\"A small student model is trained to imitate a large teacher. Besides the true labels, the student matches the teacher's softened output probabilities — logits divided by a temperature — which carry 'dark knowledge' about how classes relate, like a 3 looking a bit like an 8. The loss is a weighted sum of normal cross-entropy and the KL divergence to the teacher's soft targets. The student often gets close to the teacher's accuracy at a fraction of the size and latency.\"")]),

M("m-mlops", "MLOps: experiment tracking, versioning, model registry, CI/CD, feature stores, pipelines", "Intermediate",
  "MLOps applies DevOps practices to machine learning so models can be built, reproduced, deployed and updated reliably by teams.",
  """### Building blocks
- **Experiment tracking**: log parameters, metrics, artifacts and code version for every run — **MLflow**, Weights & Biases, Neptune.
- **Data and model versioning**: DVC, lakeFS, Delta Lake time travel; model registry with stages (staging → production) and lineage.
- **Pipelines / orchestration**: Airflow, Prefect, Dagster, Kubeflow, ZenML, Vertex/SageMaker Pipelines — ingest → validate → features → train → evaluate → register → deploy.
- **Feature store** (Feast, Tecton, Databricks): one definition of features for training (offline) and serving (online) → no training–serving skew; point-in-time correct joins.
- **CI/CD/CT**: tests for data (Great Expectations, schema checks), code (unit tests), and models (performance thresholds, fairness, latency) on every change; **continuous training** when new data arrives.
- **Serving and monitoring**: see deployment and practical issues.

### Maturity levels (Google)
0: manual notebooks → 1: automated training pipeline → 2: automated CI/CD of the pipeline itself.

### LLMOps additions
Prompt versioning, eval suites, tracing (LangSmith, Langfuse), guardrails, cost tracking, vector-index refresh.""",
  code="""
import os; os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
import mlflow, numpy as np, tempfile
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
mlflow.set_tracking_uri("sqlite:///" + os.path.join(tempfile.mkdtemp(), "mlflow.db"))   # local SQLite store; in teams this is an MLflow server
mlflow.set_experiment("cancer-classifier")
X, y = load_breast_cancer(return_X_y=True)
for depth in (2, 4, 8):
    with mlflow.start_run(run_name=f"rf-depth-{depth}"):
        params = {"n_estimators": 100, "max_depth": depth}; mlflow.log_params(params)
        score = cross_val_score(RandomForestClassifier(**params, random_state=0), X, y, cv=5).mean()
        mlflow.log_metric("cv_accuracy", score); print(f"logged run depth={depth}: cv_accuracy={score:.4f}")
runs = mlflow.search_runs(order_by=["metrics.cv_accuracy DESC"])
print("best run:", runs.iloc[0]["tags.mlflow.runName"], round(runs.iloc[0]["metrics.cv_accuracy"], 4))
def test_model_quality(score, threshold=0.93): assert score >= threshold, "model below quality gate - block deployment"
test_model_quality(runs.iloc[0]["metrics.cv_accuracy"]); print("CI quality gate passed")
""",
  say=[("What is a feature store and what problem does it solve?",
        "\"It's a central system that defines, computes and serves features consistently for both training and inference. It solves training–serving skew — the same feature code produces offline training data with point-in-time correctness and low-latency online values — and it lets teams reuse and discover features instead of re-implementing them. Examples are Feast, Tecton and the feature stores in Databricks, SageMaker and Vertex.\"")]),

M("m-ml-system-design", "ML system design interviews: a framework with an example", "Advanced",
  "ML system design interviews ask you to design an end-to-end ML product — a feed ranker, fraud detector, search or RAG assistant. Interviewers look for structured thinking across problem framing, data, modelling, serving and monitoring.",
  """### Framework (45 minutes)
1. **Clarify requirements** (5 min): business goal, users, scale (QPS, items), latency, what decision the model drives, constraints (privacy, fairness).
2. **Frame as ML** (5 min): task type, label definition, offline and online metrics, baseline (heuristic).
3. **Data** (5–8 min): sources, labelling (implicit/explicit), class imbalance, sampling, train/validation split strategy (time-based!), privacy.
4. **Features** (5 min): user, item, context, cross features, embeddings; freshness; feature store.
5. **Model** (8 min): start simple (logistic regression / GBDT), then deep models (two-tower retrieval + ranker); loss; trade-offs; how to handle cold start.
6. **Serving architecture** (8 min): candidate generation → ranking → re-ranking (diversity, business rules); batch vs online; caching; latency budget.
7. **Evaluation and launch** (3 min): offline metrics, A/B test design, guardrail metrics.
8. **Monitoring and iteration** (3 min): drift, feedback loops, retraining cadence, failure modes, fairness.

### Example: "Design YouTube-style video recommendations"
Goal: watch time and satisfaction. Candidate generation from millions of videos via two-tower embeddings + ANN, co-watch, subscriptions → ranking model (GBDT or deep multi-task model predicting click, watch time, like) → re-rank for diversity/freshness and policy → log impressions and outcomes → retrain daily; A/B test on watch time with guardrails (satisfaction surveys, creator diversity).""",
  code="""
design = {
    "requirements": ["~500M daily users", "p99 latency < 200 ms", "optimise long-term satisfaction, not just clicks"],
    "ml_framing": {"task": "rank candidate videos per user", "labels": ["click", "watch_time", "like"], "offline": ["NDCG@10", "AUC"], "online": ["watch time", "DAU", "survey score"]},
    "pipeline": ["candidate generation (two-tower + ANN, ~1000)", "ranking (multi-task deep model, ~100)", "re-ranking (diversity, freshness, policy)"],
    "features": ["user history embeddings", "video metadata + content embeddings", "context: time, device", "cross: user-topic affinity"],
    "risks": ["clickbait feedback loop", "cold start for new videos", "popularity bias", "training-serving skew"],
}
for k, v in design.items(): print(f"{k:12s}: {v}")
budget = {"feature fetch": 30, "candidate retrieval (ANN)": 40, "ranking model": 70, "re-ranking + business rules": 20, "network/serialisation": 30}
print("latency budget used:", sum(budget.values()), "ms of 200 ms ->", budget)
""",
  say=[("How would you design a fraud detection system for UPI payments?",
        "\"Clarify: real-time decision within about 100 milliseconds, fraud rate well under 1%, cost of blocking a genuine payment versus missing fraud. Frame it as imbalanced binary classification with labels from chargebacks and reports, which arrive late. Features: transaction amount and time, device and location changes, velocity counts over sliding windows, payee history, graph features about shared devices and accounts — served from a low-latency feature store. Model: gradient-boosted trees for the real-time score, plus rules for known patterns and graph models offline to find rings. Decision thresholds by risk tier — approve, step-up authentication, block — with human review queues. Evaluate on time-based splits with precision at fixed recall and money saved, shadow deploy, then monitor drift because fraudsters adapt, retraining frequently.\"")]),

M("m-industry-cases", "Industry talks: how companies use ML (case studies)", "Intermediate",
  "Real deployments teach lessons textbooks skip: simple models with great data often win, latency and cost shape architecture, and monitoring matters as much as modelling.",
  """|Company / product|Problem|Approach and lesson|
|Netflix|recommendations, artwork personalisation|ensembles of collaborative + content models; contextual bandits choose thumbnails; A/B testing culture — optimise retention, not just clicks|
|YouTube|video recommendations|two-stage deep candidate generation + ranking (2016 paper); optimise watch time with satisfaction signals|
|Uber|ETA prediction, fraud, pricing|Michelangelo ML platform: feature store, standard pipelines; ETA corrections with deep models on top of routing engines|
|Google Maps|traffic and ETA|graph neural networks over road segments (with DeepMind) improved ETA accuracy|
|Amazon|item-to-item recommendations, demand forecasting|item-based collaborative filtering (2003) scaled better than user-based; DeepAR probabilistic forecasting|
|Swiggy / Zomato|delivery-time prediction, food image tagging|gradient boosting + deep models with real-time features (rider location, restaurant load); CV for dish recognition|
|Banks / UPI apps|fraud detection, credit scoring|GBDT with velocity features, graph analysis, explainability for regulators (RBI)|
|Spotify|Discover Weekly|collaborative filtering + audio embeddings + NLP on playlists|
|Tesla / Waymo|autonomous driving perception|multi-camera transformers ("occupancy networks"), auto-labelling fleets of data, simulation|
|GitHub Copilot / coding assistants|code completion|LLMs with repository context retrieval; latency engineering; acceptance-rate metrics|
|Customer support (many firms)|LLM assistants|RAG over help-centre content, human hand-off, evaluation on resolution rate|

### Recurring lessons
Start simple and ship; data quality and labels beat model tweaks; build platforms for repeatability; measure online impact with experiments; consider latency, cost and failure modes from day one; humans stay in the loop for high-stakes decisions.""",
  code="""
lessons = ["define the business metric first", "baseline before deep learning", "invest in data/labels", "offline metric != online impact - A/B test",
           "design for latency and cost", "monitor drift and feedback loops", "keep humans in the loop for high stakes"]
for i, l in enumerate(lessons, 1): print(f"{i}. {l}")
""",
  say=[("Tell me about an ML system at a well-known company and what you learned from it.",
        "\"YouTube's recommender is a great example: a two-stage architecture where a candidate-generation network narrows millions of videos to hundreds using user and video embeddings, then a ranking network scores them with richer features, trained to predict expected watch time rather than clicks to avoid clickbait. The lessons I take are: split retrieval and ranking for scale, choose the objective carefully because the system optimises exactly what you measure, and validate with online experiments.\"")]),
]
