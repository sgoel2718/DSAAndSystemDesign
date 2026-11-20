"""Deep layer + end-to-end walkthroughs: Deployment, MLOps & ML system design."""
from deep.util import X

HOUSING = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
TELCO = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
RETAIL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"
LOAD_TELCO = f'''df = pd.read_csv("{TELCO}")
df["TotalCharges"] = pd.to_numeric(df.TotalCharges, errors="coerce").fillna(0); y = (df.pop("Churn") == "Yes").astype(int); df = df.drop(columns="customerID")'''
FM = '''import gzip, urllib.request
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
get = lambda f, off: np.frombuffer(gzip.decompress(urllib.request.urlopen(base + f).read()), np.uint8, offset=off)
X = get("t10k-images-idx3-ubyte.gz", 16).reshape(-1, 1, 28, 28).astype(np.float32) / 255.0; y = get("t10k-labels-idx1-ubyte.gz", 8).astype(np.int64)
torch.manual_seed(0); Xt, yt = torch.tensor(X), torch.tensor(y); tr, te = torch.arange(8000), torch.arange(8000, 10000)'''

X("m-fastapi",
  "FastAPI turns a trained model into a web service: define request/response schemas with Pydantic, load the model once at startup, expose `/predict` (and `/health`), and get automatic validation, JSON handling and interactive docs at `/docs`. It's the most common way to put a Python model behind an HTTP API.",
  """**Pieces.** `app = FastAPI()`; Pydantic models define and validate inputs (types, ranges, enums) → bad requests get a clear 422 error automatically. Load artefacts once (module import or lifespan event), never per request. Endpoints: `GET /health` (liveness), `POST /predict` (single), `POST /predict_batch` (vectorised), `GET /metadata` (model version, features). Use `async def` only for awaitable I/O; CPU-bound model code in plain `def` endpoints runs in a threadpool. Serve with `uvicorn app:app --workers N` (or gunicorn + uvicorn workers) behind a reverse proxy; containerise with Docker. Test with `TestClient` (no server needed). Add logging of inputs/outputs (minus personal data), request IDs, timeouts, auth (API keys/OAuth), rate limits.""",
  """**Throughput by hand.** A model predicts one row in 2 ms (CPU) but batch-of-100 in 10 ms. Serving 500 requests/s one at a time needs 500 × 2 ms = 1 CPU-second per second → ≥ 1 core fully busy plus overhead; micro-batching requests every 20 ms (≈10 rows each) cuts compute to ~5× less. Latency budget: 20 ms batching wait + 3 ms inference + network.""",
  ["Loading the model inside the request handler", "No input validation (garbage in → silent garbage out)", "Different preprocessing in training vs the API", "Blocking CPU work inside async endpoints", "Returning raw exceptions to users"],
  ["Real-time predictions for apps and other services"], ["Large offline scoring jobs (use batch pipelines)"],
  "California housing — train and save a price model, then a complete FastAPI service: Pydantic input schema with ranges and an enum, startup loading, /health, /metadata, /predict and /predict_batch, request logging and timing — tested with FastAPI's TestClient (including a bad request that returns 422).",
  ["Train a pipeline model and save it with joblib + metadata", "Write the FastAPI app with Pydantic schemas", "Load once at startup; implement endpoints", "Test happy path, batch path and validation errors with TestClient", "Measure latency; show the uvicorn/Docker run commands"],
  f'''
import json, logging, time, joblib, numpy as np, pandas as pd
from enum import Enum
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
df = pd.read_csv("{HOUSING}").dropna(); df = df[df.median_house_value < 500001]; target = np.log(df.pop("median_house_value"))
pipe = make_pipeline(make_column_transformer((OneHotEncoder(handle_unknown="ignore"), ["ocean_proximity"]), remainder="passthrough"), HistGradientBoostingRegressor(random_state=0)).fit(df, target)
joblib.dump(pipe, "model.joblib"); json.dump({{"version": "1.0.0", "features": list(df.columns), "trained_rows": len(df)}}, open("metadata.json", "w"))
logging.basicConfig(level=logging.INFO); log = logging.getLogger("api")
class Ocean(str, Enum):
    near_bay = "NEAR BAY"; lt_1h = "<1H OCEAN"; inland = "INLAND"; near_ocean = "NEAR OCEAN"; island = "ISLAND"
class House(BaseModel):
    longitude: float = Field(ge=-125, le=-114); latitude: float = Field(ge=32, le=42.5); housing_median_age: float = Field(ge=0, le=100)
    total_rooms: float = Field(gt=0); total_bedrooms: float = Field(gt=0); population: float = Field(gt=0); households: float = Field(gt=0)
    median_income: float = Field(gt=0, le=20, description="in $10k"); ocean_proximity: Ocean
class Prediction(BaseModel):
    price_usd: float; model_version: str
app = FastAPI(title="House price API"); MODEL, META = joblib.load("model.joblib"), json.load(open("metadata.json"))      # loaded once
@app.get("/health")
def health(): return {{"status": "ok"}}
@app.get("/metadata")
def metadata(): return META
@app.post("/predict", response_model=Prediction)
def predict(h: House):
    t = time.perf_counter(); row = pd.DataFrame([{{**h.model_dump(), "ocean_proximity": h.ocean_proximity.value}}])[META["features"]]
    try: price = float(np.exp(MODEL.predict(row)[0]))
    except Exception: log.exception("prediction failed"); raise HTTPException(500, "prediction failed")
    log.info("predict %.1f ms -> %.0f", 1000 * (time.perf_counter() - t), price); return Prediction(price_usd=round(price, -2), model_version=META["version"])
@app.post("/predict_batch")
def predict_batch(houses: list[House]):
    rows = pd.DataFrame([{{**h.model_dump(), "ocean_proximity": h.ocean_proximity.value}} for h in houses])[META["features"]]; return {{"prices_usd": np.exp(MODEL.predict(rows)).round(-2).tolist()}}
client = TestClient(app); sample = df.iloc[0].to_dict()
print(client.get("/health").json(), client.get("/metadata").json()["version"])
r = client.post("/predict", json=sample); print("predict:", r.status_code, r.json())
print("batch:", client.post("/predict_batch", json=df.head(3).to_dict("records")).json())
bad = client.post("/predict", json={{**sample, "median_income": -3, "ocean_proximity": "MARS"}}); print("bad request:", bad.status_code, [e["loc"][-1] for e in bad.json()["detail"]])
t = time.perf_counter(); [client.post("/predict", json=sample) for _ in range(100)]; print(f"mean latency via TestClient: {{10 * (time.perf_counter() - t):.1f}} ms/request")
print("run for real:  uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2   (docs at http://localhost:8000/docs)")
''')

X("m-deployment",
  "Deployment is getting predictions to where decisions happen, reliably: **batch** (score a table nightly), **online** (an API answering in milliseconds), **streaming** (events from Kafka), **edge** (on a phone or device). It involves packaging (Docker), portable formats (ONNX), serving infrastructure, safe rollout (shadow, canary, A/B), and rollback.",
  """**Choosing the pattern.** Batch when predictions can be precomputed (daily churn scores, recommendations refreshed hourly) — simplest and cheapest. Online when inputs arrive at request time (fraud check at payment). Streaming for continuous event processing. Edge for privacy/latency/offline needs. **Packaging:** pin dependencies (requirements/lockfile), Docker image with the model artefact or a registry pull at start; **ONNX** exports models (PyTorch, scikit-learn via skl2onnx) to a framework-neutral graph run by ONNX Runtime — often faster and lighter. **Release strategies:** shadow (new model runs silently, compare), canary (5% traffic), blue/green, A/B test for business impact; automatic rollback on error-rate/latency/quality alarms. **Serving platforms:** FastAPI/BentoML/Ray Serve/Triton/TorchServe; managed (SageMaker, Vertex AI, Azure ML); Hugging Face Spaces + Gradio for demos.""",
  """**Batch vs online cost by hand.** 2M customers scored nightly by a batch job: ~4 min on one machine ≈ ₹10/day. Serving the same model online for 50 requests/s 24×7 needs ≥ 2 replicas for availability ≈ 50× the cost — choose online only when freshness truly matters.""",
  ["Training-serving skew (different preprocessing code paths)", "No rollback plan", "Unpinned dependencies ('works on my machine')", "Shipping a model without input validation or monitoring", "Online serving when batch would do"],
  ["Every model that will be used by someone else"], ["Big-bang releases without shadow/canary for important models"],
  "Fashion-MNIST CNN shipped three ways, offline: export to ONNX and verify numerical parity with PyTorch, benchmark ONNX Runtime vs PyTorch latency, write a batch-scoring job, build a Gradio demo interface (not launched), and generate a Dockerfile + requirements for the service; plus a shadow-deployment comparison of two model versions.",
  ["Train a small CNN; save the PyTorch weights", "Export to ONNX (dynamic batch); check outputs match", "Benchmark PyTorch vs ONNX Runtime (batch 1 and 64)", "Batch job to a CSV and a Gradio interface object", "Shadow deployment: compare v1 vs v2 predictions on live-like traffic; write Dockerfile"],
  '''
import time, numpy as np, onnxruntime as ort, pandas as pd, torch, torch.nn as nn
''' + FM + '''
def cnn(): return nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(32 * 49, 10))
def train(epochs):
    torch.manual_seed(0); m = cnn(); opt = torch.optim.Adam(m.parameters(), 1e-3)
    for _ in range(epochs):
        for idx in torch.randperm(8000).split(128): opt.zero_grad(); nn.functional.cross_entropy(m(Xt[idx]), yt[idx]).backward(); opt.step()
    return m.eval()
v1, v2 = train(2), train(5); torch.save(v2.state_dict(), "model_v2.pt")
torch.onnx.export(v2, Xt[:1], "model.onnx", input_names=["image"], output_names=["logits"], dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}}, dynamo=False)
sess = ort.InferenceSession("model.onnx", providers=["CPUExecutionProvider"])
with torch.no_grad(): ref = v2(Xt[te[:64]]).numpy()
onnx_out = sess.run(None, {"image": X[8000:8064]})[0]; print("ONNX matches PyTorch:", np.allclose(ref, onnx_out, atol=1e-4), "| max diff", float(np.abs(ref - onnx_out).max()))
for B in [1, 64]:
    xb = X[8000:8000 + B]; t = time.perf_counter()
    with torch.no_grad():
        for _ in range(50): v2(torch.from_numpy(xb))
    tp = (time.perf_counter() - t) / 50; t = time.perf_counter()
    for _ in range(50): sess.run(None, {"image": xb})
    to = (time.perf_counter() - t) / 50; print(f"  batch {B:2d}: PyTorch {tp * 1000:.2f} ms | ONNX Runtime {to * 1000:.2f} ms")
probs = np.concatenate([sess.run(None, {"image": X[i:i + 500]})[0] for i in range(8000, 10000, 500)])
pd.DataFrame({"item_id": np.arange(8000, 10000), "pred": probs.argmax(1), "score": np.exp(probs).max(1) / np.exp(probs).sum(1)}).to_csv("batch_scores.csv", index=False); print("batch job wrote batch_scores.csv")
import gradio as gr
NAMES = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Boot"]
def classify(img):
    x = np.asarray(img, np.float32).reshape(1, 1, 28, 28) / 255.0; z = sess.run(None, {"image": x})[0][0]; p = np.exp(z - z.max()); p /= p.sum(); return dict(zip(NAMES, p.round(3).tolist()))
demo = gr.Interface(fn=classify, inputs=gr.Image(image_mode="L", width=28, height=28, type="numpy"), outputs=gr.Label(num_top_classes=3), title="Fashion classifier")
print("Gradio interface ready (call demo.launch() to serve); test call:", max(classify((X[8000, 0] * 255).astype(np.uint8)).items(), key=lambda kv: kv[1]))
with torch.no_grad(): p1, p2 = v1(Xt[te]).argmax(1), v2(Xt[te]).argmax(1)
print(f"shadow test: v2 disagrees with v1 on {(p1 != p2).float().mean():.1%} of traffic | accuracy v1 {(p1 == yt[te]).float().mean():.3f} -> v2 {(p2 == yt[te]).float().mean():.3f} -> promote v2 to canary")
open("Dockerfile", "w").write("FROM python:3.11-slim\\nWORKDIR /app\\nCOPY requirements.txt .\\nRUN pip install --no-cache-dir -r requirements.txt\\nCOPY model.onnx app.py ./\\nEXPOSE 8000\\nCMD [\\"uvicorn\\", \\"app:app\\", \\"--host\\", \\"0.0.0.0\\", \\"--port\\", \\"8000\\"]\\n")
open("requirements.txt", "w").write(f"onnxruntime=={ort.__version__}\\nnumpy=={np.__version__}\\nfastapi\\nuvicorn\\n"); print("wrote Dockerfile and requirements.txt")
''')

X("m-practical-issues",
  "Models fail in production for reasons that never show up in a notebook: **data drift** (inputs change), **concept drift** (the input→output relationship changes), **training–serving skew**, broken upstream pipelines, delayed or missing labels, feedback loops, and silent quality decay. Practical ML means monitoring for these and having a plan to retrain or roll back.",
  """**Detect.** Input drift per feature: Population Stability Index PSI = Σ (aᵢ − eᵢ)·ln(aᵢ/eᵢ) over bins (< 0.1 stable, 0.1–0.25 moderate, > 0.25 major); KS test for continuous; chi-square for categorical; multivariate: a **domain classifier** (can a model tell old from new data? AUC ≫ 0.5 → drift). Prediction drift (score distribution). Performance monitoring when labels arrive (often delayed) — proxy metrics meanwhile. **Data quality checks:** schema, ranges, null rates, duplicates (Great Expectations/pandera). **Respond:** alert → investigate (pipeline bug vs real-world change) → retrain on recent data / reweight / recalibrate → validate → redeploy; scheduled retraining with champion–challenger evaluation. Watch **feedback loops** (model decisions shape future training data).""",
  """**PSI by hand.** Income bins expected (train) [30%, 40%, 30%], actual (new) [20%, 40%, 40%]. PSI = (0.2 − 0.3)ln(0.2/0.3) + 0 + (0.4 − 0.3)ln(0.4/0.3) = 0.0405 + 0.0288 = **0.069** → stable-ish. If actual were [10%, 30%, 60%]: 0.220 + 0.029 + 0.208 = **0.457** → major drift.""",
  ["Only monitoring infrastructure (CPU, latency), not data or quality", "Alerting on every statistically significant KS test with huge n", "Retraining automatically on corrupted data", "Ignoring delayed labels when measuring performance"],
  ["Every deployed model; especially in fast-changing domains (fraud, pricing, demand)"], ["Assuming a model validated once stays valid"],
  "California housing as a deployment simulation: train on coastal districts, then 'deploy' to inland districts (real geographic distribution shift) — PSI and KS per feature, a domain-classifier drift score, prediction drift, performance decay once labels arrive, a training-serving-skew bug reproduced, and recovery by retraining on recent data.",
  ["Split by geography into 'training period' and 'production' data", "PSI + KS per feature; flag drifted features", "Domain classifier AUC as a multivariate drift score", "Measure performance decay; reproduce a units bug (skew) and catch it with a schema check", "Retrain with a sample of new labelled data and compare"],
  f'''
import numpy as np, pandas as pd
from scipy.stats import ks_2samp
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_percentage_error, roc_auc_score
from sklearn.model_selection import cross_val_predict
df = pd.read_csv("{HOUSING}").dropna(); df = df[df.median_house_value < 500001]
feats = ["median_income", "housing_median_age", "total_rooms", "population", "households", "latitude", "longitude"]
train, prod = df[df.ocean_proximity != "INLAND"], df[df.ocean_proximity == "INLAND"]; print(f"training rows {{len(train)}} (coastal) | production rows {{len(prod)}} (inland)")
def psi(e, a, bins=10):
    edges = np.unique(np.quantile(e, np.linspace(0, 1, bins + 1))); edges[0], edges[-1] = -np.inf, np.inf
    pe, pa = np.histogram(e, edges)[0] / len(e) + 1e-6, np.histogram(a, edges)[0] / len(a) + 1e-6; return float(((pa - pe) * np.log(pa / pe)).sum())
report = pd.DataFrame({{f: {{"PSI": psi(train[f], prod[f]), "KS": ks_2samp(train[f], prod[f]).statistic}} for f in feats}}).T.round(3)
report["status"] = pd.cut(report.PSI, [-1, 0.1, 0.25, 99], labels=["stable", "moderate", "MAJOR"]); print(report)
both = pd.concat([train[feats].assign(is_new=0), prod[feats].sample(len(prod), random_state=0).assign(is_new=1)])
p = cross_val_predict(HistGradientBoostingClassifier(random_state=0), both[feats], both.is_new, cv=5, method="predict_proba")[:, 1]
print(f"domain-classifier drift AUC {{roc_auc_score(both.is_new, p):.3f}} (0.5 = indistinguishable)")
model = HistGradientBoostingRegressor(random_state=0).fit(train[feats], np.log(train.median_house_value))
pred_train, pred_prod = np.exp(model.predict(train[feats])), np.exp(model.predict(prod[feats]))
print(f"prediction drift: median predicted ${{np.median(pred_train):,.0f}} -> ${{np.median(pred_prod):,.0f}} | PSI {{psi(pred_train, pred_prod):.2f}}")
print(f"when labels arrive: MAPE on held-out coastal {{mean_absolute_percentage_error(train.median_house_value.sample(2000, random_state=1), np.exp(model.predict(train[feats].sample(2000, random_state=1)))):.1%}} vs inland {{mean_absolute_percentage_error(prod.median_house_value, pred_prod):.1%}}")
bug = prod[feats].copy(); bug["median_income"] *= 10000                                   # upstream sends dollars instead of $10k units
SCHEMA = {{"median_income": (0, 20), "housing_median_age": (0, 100), "latitude": (32, 43)}}
viol = {{c: float(((bug[c] < lo) | (bug[c] > hi)).mean()) for c, (lo, hi) in SCHEMA.items()}}; print("schema check on a buggy batch (share out of range):", viol, "-> block the batch, alert the data owner")
recent = prod.sample(frac=0.3, random_state=0); holdout = prod.drop(recent.index)
re = HistGradientBoostingRegressor(random_state=0).fit(pd.concat([train, recent])[feats], np.log(pd.concat([train, recent]).median_house_value))
print(f"after retraining with 30% of new labelled data: inland MAPE {{mean_absolute_percentage_error(holdout.median_house_value, np.exp(re.predict(holdout[feats]))):.1%}} (was {{mean_absolute_percentage_error(holdout.median_house_value, np.exp(model.predict(holdout[feats]))):.1%}})")
''')

X("m-compression",
  "Model compression makes models smaller and faster with little accuracy loss, so they fit phones, browsers, edge devices or cheaper servers. The main tools: **quantisation** (fewer bits per weight), **pruning** (remove unimportant weights/neurons), **knowledge distillation** (a small student learns from a big teacher's soft outputs), and **efficient architectures**/low-rank factorisation.",
  """**Quantisation.** Map floats to int8: q = round(x/s) + z with scale s = (max − min)/255; dynamic (weights int8, activations quantised on the fly — good for linear/LSTM layers), static (calibrate activation ranges), quantisation-aware training (simulate rounding during training). LLMs: 4-bit GPTQ/AWQ/NF4. **Pruning:** magnitude pruning zeros the smallest |w| (unstructured — needs sparse kernels to speed up), structured pruning removes whole channels/heads (real speed-ups); iterative prune → fine-tune. **Distillation:** loss = α·CE(y, student) + (1 − α)·T²·KL(softmax(teacher/T) ‖ softmax(student/T)); temperature T > 1 exposes 'dark knowledge' (which wrong classes are similar). **Low-rank:** W ≈ UV via SVD. Always re-measure accuracy, latency on target hardware, and memory.""",
  """**Int8 by hand.** Weights in [−0.8, 1.2] → scale = 2.0/255 = 0.00784, zero point z = round(0.8/0.00784) = 102. w = 0.5 → q = round(0.5/0.00784) + 102 = 64 + 102 = **166**; dequantised (166 − 102)·0.00784 = **0.502** (error 0.002). Model size: fp32 → int8 = **4×** smaller.""",
  ["Measuring size but not accuracy (or latency on the real device)", "Unstructured pruning expecting speed-ups on dense hardware", "Quantising without calibration data that matches production", "Distilling with T = 1 (loses soft-label information)"],
  ["Mobile/edge, browser, high-QPS serving, LLMs on consumer GPUs"], ["When the large model's accuracy is required and cost isn't an issue"],
  "Fashion-MNIST — a teacher CNN compressed four ways: dynamic int8 quantisation, magnitude pruning at 50/80/95% sparsity (with and without fine-tuning), low-rank factorisation of the dense layer, and knowledge distillation into a much smaller student; reporting size, accuracy and CPU latency for each.",
  ["Train a teacher CNN; baseline size/accuracy/latency", "Dynamic int8 quantisation", "Global magnitude pruning + short fine-tune", "SVD low-rank replacement of the big Linear layer", "Distil into a small student (T = 4) vs training it alone"],
  '''
import copy, io, time, numpy as np, torch, torch.nn as nn
import torch.nn.utils.prune as prune
''' + FM + '''
def fit(m, epochs, lossf=None):
    opt = torch.optim.Adam(m.parameters(), 1e-3)
    for _ in range(epochs):
        m.train()
        for idx in torch.randperm(8000).split(128): opt.zero_grad(); (lossf(m, idx) if lossf else nn.functional.cross_entropy(m(Xt[idx]), yt[idx])).backward(); opt.step()
    return m.eval()
@torch.no_grad()
def report(name, m):
    acc = (m(Xt[te]).argmax(1) == yt[te]).float().mean().item(); buf = io.BytesIO(); torch.save(m.state_dict(), buf); t = time.perf_counter()
    for _ in range(20): m(Xt[te[:64]])
    nz = sum(int((p != 0).sum()) for p in m.parameters()); print(f"  {name:28s} acc {acc:.3f} | file {len(buf.getvalue()) / 1e6:5.2f} MB | non-zero params {nz:8,d} | {(time.perf_counter() - t) / 20 * 1000:5.2f} ms/batch")
torch.manual_seed(0); teacher = fit(nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(64 * 49, 256), nn.ReLU(), nn.Linear(256, 10)), 4)
report("teacher fp32", teacher)
report("dynamic int8 (Linear)", torch.ao.quantization.quantize_dynamic(copy.deepcopy(teacher), {nn.Linear}, dtype=torch.qint8))
for amount in [0.5, 0.8, 0.95]:
    p = copy.deepcopy(teacher); params = [(mod, "weight") for mod in p if isinstance(mod, (nn.Conv2d, nn.Linear))]
    prune.global_unstructured(params, pruning_method=prune.L1Unstructured, amount=amount); report(f"pruned {int(amount * 100)}% (no fine-tune)", p)
    fit(p, 1); [prune.remove(mod, n) for mod, n in params]; report(f"pruned {int(amount * 100)}% + 1 epoch fine-tune", p)
lr = copy.deepcopy(teacher); W = lr[7].weight.data; U, S, Vh = torch.linalg.svd(W, full_matrices=False); r = 32
lr[7] = nn.Sequential(nn.Linear(W.shape[1], r, bias=False), nn.Linear(r, W.shape[0])); lr[7][0].weight.data = Vh[:r]; lr[7][1].weight.data = U[:, :r] * S[:r]; lr[7][1].bias.data = teacher[7].bias.data
report(f"low-rank r={r} dense layer", lr)
def student(): return nn.Sequential(nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(16 * 49, 10))
torch.manual_seed(0); report("small student alone", fit(student(), 4))
with torch.no_grad(): soft = teacher(Xt)
T, alpha = 4.0, 0.3
kd = lambda m, idx: alpha * nn.functional.cross_entropy(m(Xt[idx]), yt[idx]) + (1 - alpha) * T * T * nn.functional.kl_div(nn.functional.log_softmax(m(Xt[idx]) / T, 1), nn.functional.softmax(soft[idx] / T, 1), reduction="batchmean")
torch.manual_seed(0); report("small student distilled (T=4)", fit(student(), 4, kd))
''')

X("m-mlops",
  "MLOps applies software-engineering discipline to ML: **version** data, code and models; **track experiments**; **automate** training and evaluation pipelines; **register** and promote models through stages; **test** data and models in CI; **deploy** reproducibly; **monitor** and retrain. The goal is that anyone can reproduce a model and ship a better one safely.",
  """**Building blocks.** Experiment tracking (MLflow, Weights & Biases): parameters, metrics, artefacts, code version. **Data versioning** (DVC, lakeFS, Delta tables): content hashes so a model points to the exact data. **Model registry:** versions, stages/aliases (staging → production), lineage, signatures. **Pipelines/orchestration** (Airflow, Prefect, Kubeflow, GitHub Actions): ingest → validate → train → evaluate → register → deploy. **Testing:** unit tests for features, data validation (schema, ranges), model tests (minimum accuracy, invariance — e.g. changing a name doesn't change the prediction, directional expectations), fairness checks, performance budget. **Reproducibility:** seeds, pinned environments, containers. **Maturity levels** (Google): manual → automated training pipeline → automated CI/CD of pipelines.""",
  """**Promotion rule by hand.** Champion AUC 0.842 (CI ±0.006 on 7,000 holdout rows). Challenger 0.851 ± 0.006; paired bootstrap of the difference: mean +0.009, 95% CI [+0.004, +0.014] → excludes 0 → promote, provided latency (12 ms vs budget 20 ms) and fairness gaps (≤ 0.05) also pass.""",
  ["Notebook-only models nobody can reproduce", "No data version linked to the model", "Promoting models on a single unrepeated metric", "No automated tests before deployment", "Manual, undocumented retraining"],
  ["Any model that will be retrained, shared, audited or kept in production"], ["Heavy platform tooling for a one-off analysis"],
  "IBM Telco churn as a mini MLOps pipeline, offline: data validation and a content hash (data version), MLflow experiment tracking for three model configurations, automated quality gates (minimum AUC, invariance and directional tests), model registration with an alias, and loading the 'champion' by alias for scoring — plus a pytest-style test file.",
  ["Validate the dataset and compute its hash", "Track runs in MLflow (params, metrics, data hash, model artefact)", "Pick the best run; run quality gates (threshold, invariance, directional)", "Register the model and set the 'champion' alias", "Load by alias and score; write tests for CI"],
  f'''
import hashlib, os, mlflow, numpy as np, pandas as pd
from mlflow.tracking import MlflowClient
from sklearn.compose import make_column_transformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
{LOAD_TELCO}
assert set(y.unique()) == {{0, 1}} and df.tenure.between(0, 100).all() and df.MonthlyCharges.gt(0).all(), "data validation failed"
data_hash = hashlib.sha256(pd.util.hash_pandas_object(df.assign(y=y), index=False).values.tobytes()).hexdigest()[:12]; print("data version:", data_hash)
num = ["tenure", "MonthlyCharges", "TotalCharges"]; cat = [c for c in df if c not in num]
Xtr, Xte, ytr, yte = train_test_split(df, y, test_size=0.3, stratify=y, random_state=0)
mlflow.set_tracking_uri("sqlite:///mlflow.db"); mlflow.set_experiment("telco-churn")
configs = {{"logreg": LogisticRegression(C=0.5, max_iter=3000), "forest": RandomForestClassifier(300, min_samples_leaf=5, random_state=0, n_jobs=-1), "hgb": HistGradientBoostingClassifier(learning_rate=0.05, random_state=0)}}
for name, est in configs.items():
    with mlflow.start_run(run_name=name):
        pipe = make_pipeline(make_column_transformer((StandardScaler(), num), (OneHotEncoder(handle_unknown="ignore"), cat)), est).fit(Xtr, ytr)
        auc = roc_auc_score(yte, pipe.predict_proba(Xte)[:, 1])
        mlflow.log_params({{"model": name, "data_version": data_hash, **{{k: v for k, v in est.get_params().items() if isinstance(v, (int, float, str)) and k in ("C", "n_estimators", "min_samples_leaf", "learning_rate")}}}})
        mlflow.log_metric("test_auc", auc); mlflow.sklearn.log_model(pipe, name="model", input_example=Xte.head(2), serialization_format="cloudpickle"); print(f"  run {{name:7s}} AUC {{auc:.4f}}")
best = mlflow.search_runs(order_by=["metrics.test_auc DESC"]).iloc[0]; print("best run:", best["tags.mlflow.runName"], round(best["metrics.test_auc"], 4))
model = mlflow.sklearn.load_model(f"runs:/{{best.run_id}}/model")
gates = {{"AUC >= 0.80": best["metrics.test_auc"] >= 0.80}}
x0 = Xte.head(200); flipped = x0.assign(gender=np.where(x0.gender == "Male", "Female", "Male"))
gates["invariance: gender flip changes P(churn) < 0.05"] = float(np.abs(model.predict_proba(x0)[:, 1] - model.predict_proba(flipped)[:, 1]).mean()) < 0.05
longer = x0.assign(Contract="Two year"); gates["directional: two-year contract lowers churn risk"] = (model.predict_proba(longer)[:, 1] <= model.predict_proba(x0)[:, 1] + 1e-9).mean() > 0.9
for g, ok in gates.items(): print(f"  gate {{'PASS' if ok else 'FAIL'}}: {{g}}")
if all(gates.values()):
    mv = mlflow.register_model(f"runs:/{{best.run_id}}/model", "telco-churn"); MlflowClient().set_registered_model_alias("telco-churn", "champion", mv.version)
    champ = mlflow.sklearn.load_model("models:/telco-churn@champion"); print(f"registered version {{mv.version}} as champion; scoring 3 customers ->", champ.predict_proba(Xte.head(3))[:, 1].round(3).tolist())
open("test_model.py", "w").write("""import mlflow, pandas as pd
def test_champion_loads_and_scores():
    mlflow.set_tracking_uri("sqlite:///mlflow.db"); m = mlflow.sklearn.load_model("models:/telco-churn@champion")
    assert hasattr(m, "predict_proba")
""")
print("wrote test_model.py for CI (run: pytest -q)")
''')

X("m-ml-system-design",
  "ML system design is the interview-and-real-world skill of turning a vague product goal ('reduce churn', 'recommend videos', 'detect fraud') into a working system: clarify requirements, define the ML task and metrics, design data and features, choose models, plan training and serving, estimate scale, evaluate offline and online, and plan monitoring and iteration.",
  """**Framework.** (1) Requirements: business goal, users, latency/throughput, scale, constraints (privacy, explainability). (2) Framing: prediction target, label source, offline metric (AUC, NDCG) **and** online metric (retention, revenue). (3) Data: sources, labelling, sampling, leakage risks, feature store (offline/online consistency). (4) Model: baseline → stronger models; for recommendations a **two-stage** design — candidate generation (embeddings/ANN, recall) → ranking (gradient boosting/deep, precision) → re-ranking (business rules, diversity). (5) Serving: batch vs online, caching, latency budget per stage. (6) Evaluation: offline backtests, then **A/B tests** with power analysis; guardrail metrics. (7) Monitoring, retraining cadence, feedback loops, fairness. Back-of-envelope maths for QPS, storage and cost.""",
  """**Back-of-envelope.** 10M daily users × 20 feed requests = 200M requests/day ≈ **2,300 QPS** average, ~3× at peak ≈ 7k QPS. Ranking 500 candidates per request = 3.5M model scores/s → needs batching and cheap models; precompute user embeddings daily (10M × 128 floats × 4 B = **5 GB**). **A/B power:** detect +1% relative lift on a 20% conversion (0.2 → 0.202) at 80% power: n ≈ 16·p(1−p)/δ² = 16·0.16/0.002² = **640k users per arm**.""",
  ["Jumping to a model before defining the metric and labels", "Offline metric improvements that don't move online metrics", "Ignoring latency and cost per request", "No plan for cold start, feedback loops or monitoring", "Under-powered A/B tests"],
  ["Designing any production ML feature; ML interviews"], ["Over-engineering a v1 — start with a simple baseline system end to end"],
  "A miniature end-to-end churn-prevention system on IBM Telco data: requirements and economics as code, a feature pipeline shared by training and serving (no skew), a calibrated model, a capacity-limited retention campaign (rank by expected value), offline evaluation of the policy, and an A/B test design with power analysis and a simulated result.",
  ["Write requirements/assumptions as constants (costs, capacity, latency)", "One feature function used by both training and serving", "Train + calibrate; offline AUC and calibration", "Policy: contact the top-K customers by expected value under capacity", "A/B test plan: sample size for the target lift; simulate and analyse"],
  f'''
import numpy as np, pandas as pd
from scipy import stats
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest
REQ = {{"monthly_capacity_calls": 300, "offer_cost": 500, "save_rate_if_contacted": 0.30, "months_of_value_saved": 12, "latency_budget_ms": 50}}
{LOAD_TELCO}
def features(d: pd.DataFrame) -> pd.DataFrame:                         # the ONLY feature code — imported by the training job and by the API
    f = pd.DataFrame(index=d.index)
    f["tenure"] = d.tenure; f["monthly"] = d.MonthlyCharges; f["avg_monthly"] = d.TotalCharges / d.tenure.clip(lower=1)
    f["month_to_month"] = (d.Contract == "Month-to-month").astype(int); f["fiber"] = (d.InternetService == "Fiber optic").astype(int)
    f["echeck"] = (d.PaymentMethod == "Electronic check").astype(int); f["n_services"] = (d[["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]] == "Yes").sum(1)
    f["senior"] = d.SeniorCitizen; return f
F = features(df); Ftr, Fte, ytr, yte, dtr, dte = train_test_split(F, y, df, test_size=0.3, stratify=y, random_state=0)
model = CalibratedClassifierCV(HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, random_state=0), method="isotonic", cv=5).fit(Ftr, ytr)
p = model.predict_proba(Fte)[:, 1]; print(f"offline: AUC {{roc_auc_score(yte, p):.3f}} | Brier {{brier_score_loss(yte, p):.3f}} | base rate {{yte.mean():.3f}}")
value = dte.MonthlyCharges.to_numpy() * REQ["months_of_value_saved"]
ev = p * REQ["save_rate_if_contacted"] * value - REQ["offer_cost"]                         # expected value of calling each customer
K = REQ["monthly_capacity_calls"]
def realised(order): pick = order[:K]; return (yte.to_numpy()[pick] * REQ["save_rate_if_contacted"] * value[pick]).sum() - K * REQ["offer_cost"]
rng = np.random.default_rng(0)
for name, order in [("random", rng.permutation(len(p))), ("highest churn probability", np.argsort(-p)), ("highest expected value", np.argsort(-ev))]: print(f"  policy {{name:26s}} expected campaign value ₹{{realised(order):>10,.0f}}")
p0 = 0.265; p1 = p0 * 0.85                                                                   # goal: cut churn by 15% relative among targeted customers
n = NormalIndPower().solve_power(proportion_effectsize(p0, p1), alpha=0.05, power=0.8); print(f"A/B test: need {{n:,.0f}} customers per arm to detect {{p0:.3f}} -> {{p1:.3f}}")
ctrl, treat = rng.random(int(n)) < p0, rng.random(int(n)) < p1
z, pval = proportions_ztest([treat.sum(), ctrl.sum()], [len(treat), len(ctrl)]); diff = treat.mean() - ctrl.mean(); se = np.sqrt(treat.mean() * (1 - treat.mean()) / len(treat) + ctrl.mean() * (1 - ctrl.mean()) / len(ctrl))
print(f"simulated result: churn {{ctrl.mean():.3f}} -> {{treat.mean():.3f}} | diff {{diff:+.3f}} (95% CI {{diff - 1.96 * se:+.3f}} to {{diff + 1.96 * se:+.3f}}) | p = {{pval:.4f}}")
import time; t = time.perf_counter(); model.predict_proba(features(df.head(1))); print(f"serving latency for one customer: {{(time.perf_counter() - t) * 1000:.1f}} ms (budget {{REQ['latency_budget_ms']}} ms)")
''')

X("m-industry-cases",
  "Industry ML follows recurring patterns: **fraud detection** (rare events, adversaries, real-time), **demand forecasting** (hierarchies, promotions, uncertainty), **recommendations** (two-stage retrieval + ranking), **credit risk** (regulation, explainability, fairness), **predictive maintenance**, **search ranking**, **document AI**, **LLM assistants**. Each pairs a technical core with business metrics and constraints — studying cases teaches you which trade-offs matter.",
  """**Case anatomy.** Problem & decision → data & labels (how they arrive, delays) → baseline → model → offline metric tied to money → deployment constraints → online evaluation → risks. Examples: *Fraud:* class imbalance (~0.1%), cost-sensitive thresholds, graph features (shared devices/cards), velocity features, real-time scoring < 100 ms, adversarial drift, human review queues. *Demand forecasting:* many SKUs × stores, intermittent demand, promotions/holidays as covariates, quantile forecasts for safety stock (newsvendor: order at the critical fractile c_u/(c_u + c_o)). *Recommendations:* implicit feedback, candidate generation + ranking, diversity, cold start. *Credit:* scorecards, reason codes, fairness audits, regulatory model validation.""",
  """**Newsvendor by hand.** A product costs ₹60, sells for ₹100 (understock cost c_u = ₹40 lost margin), leftover salvage ₹30 (overstock cost c_o = ₹30). Critical fractile = 40/(40 + 30) = **0.571** → order the 57th percentile of the demand forecast, not the mean. With forecast median 200 and q57 = 212 units → order **212**.""",
  ["Optimising a generic metric instead of the business cost", "Ignoring how labels arrive (delays, selection bias)", "Copying a case's solution without its constraints", "Point forecasts where decisions need quantiles"],
  ["Learning reusable patterns for new projects and interviews"], ["Assuming another company's numbers transfer to your setting"],
  "Two real-data cases end to end. **Retail demand** (Online Retail): daily product demand, a quantile gradient-boosting forecaster with calendar and lag features, and the newsvendor decision — profit vs ordering the mean. **Fraud-style anomaly triage** on the same retailer's invoices: velocity features, an isolation-forest risk score, a review-capacity threshold and the value caught per analyst hour.",
  ["Aggregate daily units for the top products; lag/calendar features", "Train P10/P50/P90 quantile models; check calibration", "Newsvendor ordering at the critical fractile vs ordering the median", "Invoice risk features (velocity, unusual quantities, new customer)", "Rank by risk under analyst capacity; report business metrics"],
  f'''
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, IsolationForest
r = pd.read_csv("{RETAIL}", encoding="latin-1"); r = r[(r.Quantity > 0) & (r.UnitPrice > 0)]; r["InvoiceDate"] = pd.to_datetime(r.InvoiceDate, format="mixed"); r["day"] = r.InvoiceDate.dt.normalize()
top = r.groupby("StockCode").Quantity.sum().nlargest(20).index
daily = r[r.StockCode.isin(top)].groupby(["StockCode", "day"]).Quantity.sum().unstack(0).asfreq("D").fillna(0).stack().rename("units").reset_index().sort_values(["StockCode", "day"])
g = daily.groupby("StockCode").units
for lag in (1, 7, 14): daily[f"lag{{lag}}"] = g.shift(lag)
daily["roll7"] = g.transform(lambda s: s.shift(1).rolling(7).mean()); daily["dow"] = daily.day.dt.dayofweek; daily["month"] = daily.day.dt.month; daily["item"] = daily.StockCode.astype("category").cat.codes
daily = daily.dropna(); cut = daily.day.quantile(0.8); trn, tst = daily[daily.day <= cut], daily[daily.day > cut]; feats = ["lag1", "lag7", "lag14", "roll7", "dow", "month", "item"]
Q = {{q: HistGradientBoostingRegressor(loss="quantile", quantile=q, max_iter=300, random_state=0).fit(trn[feats], trn.units).predict(tst[feats]).clip(0) for q in (0.1, 0.5, 0.571, 0.9)}}
print(f"forecast calibration: actual below P10 {{(tst.units < Q[0.1]).mean():.0%}} | below P50 {{(tst.units < Q[0.5]).mean():.0%}} | below P90 {{(tst.units < Q[0.9]).mean():.0%}}")
price, cost, salvage = 100, 60, 30; cu, co = price - cost, cost - salvage; fractile = cu / (cu + co); print(f"newsvendor critical fractile = {{cu}}/({{cu}}+{{co}}) = {{fractile:.3f}}")
def profit(order, demand): sold = np.minimum(order, demand); return (sold * price + (order - sold) * salvage - order * cost).sum()
naive = tst.lag7.to_numpy()
for name, order in [("order = last week's demand", naive), ("order = P50 forecast", Q[0.5]), (f"order = P{{fractile * 100:.0f}} (critical fractile)", Q[0.571])]: print(f"  {{name:34s}} profit ₹{{profit(order, tst.units.to_numpy()):>12,.0f}}")
inv = r.groupby("InvoiceNo").agg(customer=("CustomerID", "first"), time=("InvoiceDate", "first"), qty=("Quantity", "sum"), value=("UnitPrice", lambda s: (s * r.loc[s.index, "Quantity"]).sum()), lines=("StockCode", "size"), max_price=("UnitPrice", "max")).dropna(subset=["customer"]).sort_values("time")
inv["cust_invoices_so_far"] = inv.groupby("customer").cumcount(); inv["hours_since_prev"] = inv.groupby("customer").time.diff().dt.total_seconds().div(3600).fillna(1e4)
inv["value_vs_customer_median"] = inv.value / inv.groupby("customer").value.transform(lambda s: s.expanding().median().shift(1)).fillna(inv.value.median())
F = np.log1p(inv[["qty", "value", "lines", "max_price", "cust_invoices_so_far", "hours_since_prev", "value_vs_customer_median"]].clip(lower=0))
inv["risk"] = -IsolationForest(n_estimators=300, random_state=0).fit(F).score_samples(F)
capacity = 40 * 5                                                                                     # 40 invoices per analyst-day, 5 days
queue = inv.nlargest(capacity, "risk"); print(f"review queue: {{capacity}} of {{len(inv):,}} invoices ({{capacity / len(inv):.1%}}) cover {{queue.value.sum() / inv.value.sum():.1%}} of revenue at risk")
print(queue[["qty", "value", "lines", "cust_invoices_so_far", "value_vs_customer_median"]].head(5).round(1).to_string())
''')
