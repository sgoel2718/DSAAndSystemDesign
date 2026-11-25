"""Real-data walkthroughs: MLOps, deployment and system design."""
import os, re, io, json, time, tempfile, pickle
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt
from walks.w_nlp import _sms, _split, _short


def _spam_model():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    tr, te = _split()
    return make_pipeline(TfidfVectorizer(sublinear_tf=True), LogisticRegression(max_iter=2000, C=10)).fit(tr["text"], tr["label"]), tr, te


@walk("m-fastapi", "sms")
def _():
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, Field
    model, tr, te = _spam_model()
    app = FastAPI(title="spam-filter")

    class Msg(BaseModel):
        text: str = Field(min_length=1, max_length=1000)

    @app.post("/predict")
    def predict(m: Msg):
        p = float(model.predict_proba([m.text])[0, 1])
        return {"label": "spam" if p > 0.5 else "ham", "p_spam": round(p, 3)}

    @app.get("/health")
    def health(): return {"status": "ok"}
    c = TestClient(app)
    rows = []
    for txt in [te[te.label == "spam"]["text"].iloc[0], te[te.label == "ham"]["text"].iloc[0]]:
        r = c.post("/predict", json={"text": txt}); rows.append({"request body": _short(json.dumps({"text": txt}), 60), "status": r.status_code, "response": json.dumps(r.json())})
    bad = c.post("/predict", json={"text": ""})
    t0 = time.perf_counter()
    for txt in te["text"].head(200): c.post("/predict", json={"text": txt})
    ms = (time.perf_counter() - t0) / 200 * 1000
    return [
        ("Wrap the model in an endpoint", "```python\napp = FastAPI()\nclass Msg(BaseModel):\n    text: str = Field(min_length=1, max_length=1000)\n\n@app.post('/predict')\ndef predict(m: Msg):\n    p = model.predict_proba([m.text])[0, 1]\n    return {'label': 'spam' if p > 0.5 else 'ham', 'p_spam': round(p, 3)}\n```\n\nThe model (TF-IDF + logistic regression trained on real SMS) is loaded once at start-up, not per request."),
        ("Call it with real messages", f"{t(pd.DataFrame(rows))}\n\nAn empty text is rejected automatically by the Pydantic schema with status **{bad.status_code}** (validation error), before the model is ever called."),
        ("How fast is it?", f"200 real test messages sent one by one: **{ms:.1f} ms** per request on this machine (in-process test client). `uvicorn main:app` serves it for real; `/docs` gives an interactive page for free; `/health` lets a load balancer check it is alive."),
    ], "FastAPI turns a model into a web API: a typed request schema, a prediction function and automatic validation and docs."


@walk("m-deployment", "sms")
def _():
    import joblib
    model, tr, te = _spam_model()
    d = tempfile.mkdtemp(); f = os.path.join(d, "spam_model.joblib"); joblib.dump(model, f)
    size = os.path.getsize(f)
    t0 = time.perf_counter(); m2 = joblib.load(f); load = time.perf_counter() - t0
    same = (m2.predict(te["text"]) == model.predict(te["text"])).mean()
    lat = []
    for txt in te["text"].head(300):
        t0 = time.perf_counter(); m2.predict_proba([txt]); lat.append((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter(); m2.predict_proba(te["text"].tolist()); batch = (time.perf_counter() - t0) / len(te) * 1000
    lat = np.array(lat)
    import sklearn
    req = f"scikit-learn=={sklearn.__version__}\nfastapi\nuvicorn\njoblib"
    return [
        ("Save the trained pipeline as one file", f"`joblib.dump(model, 'spam_model.joblib')` → **{size / 1e3:.0f} kB** (vectorizer vocabulary + weights). Loading takes {load * 1000:.0f} ms and gives identical predictions on {pct(same)} of the {len(te):,} test messages. Pin library versions, because a model saved with one scikit-learn version may not load in another:\n\n```\n{req}\n```"),
        ("Measure latency before you promise it", f"300 single-message predictions: median **{np.median(lat):.2f} ms**, 95th percentile {np.percentile(lat, 95):.2f} ms, worst {lat.max():.2f} ms. In a batch of {len(te):,}: {batch:.3f} ms per message. Batch scoring is far cheaper per message when real-time isn't needed."),
        ("Package and roll out", "Docker image = code + pinned requirements + model file, so it runs the same everywhere. Roll out gradually: shadow mode (score but don't act), then a canary (5% of traffic), compare metrics, then 100%; keep the old version ready for rollback."),
    ], "Deployment = save the exact trained pipeline, pin its environment, measure latency, and release it gradually with a way back."


@walk("m-practical-issues", ("sms", "housing"))
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.metrics import recall_score, precision_score
    tr, te = _split()
    vec = TfidfVectorizer(sublinear_tf=True); X = vec.fit_transform(tr["text"]); Xt = vec.transform(te["text"])
    rows = [{"model": "always say ham", "accuracy": (te["label"] == "ham").mean(), "spam recall": 0.0, "spam precision": float("nan")}]
    for name, cw in [("logistic regression", None), ("logistic regression, class_weight='balanced'", "balanced")]:
        m = LogisticRegression(max_iter=2000, class_weight=cw).fit(X, tr["label"]); p = m.predict(Xt)
        rows.append({"model": name, "accuracy": (p == te["label"]).mean(), "spam recall": recall_score(te["label"], p, pos_label="spam"), "spam precision": precision_score(te["label"], p, pos_label="spam")})
    h = D("housing").dropna().reset_index(drop=True)
    cols = ["median_income", "housing_median_age", "total_rooms", "population", "households"]
    south = h["ocean_proximity"] == "INLAND"
    m = LinearRegression().fit(h.loc[south, cols], h.loc[south, "median_house_value"])
    err = lambda msk: np.sqrt(np.mean((m.predict(h.loc[msk, cols]) - h.loc[msk, "median_house_value"]) ** 2)) / 1000
    from sklearn.model_selection import train_test_split
    a, b = train_test_split(h[south], test_size=0.3, random_state=0); m2 = LinearRegression().fit(a[cols], a["median_house_value"])
    in_err = np.sqrt(np.mean((m2.predict(b[cols]) - b["median_house_value"]) ** 2)) / 1000
    drift = pd.DataFrame({"feature": cols + ["median_house_value"], "inland average": h.loc[south, cols + ["median_house_value"]].mean().values, "coastal average": h.loc[~south, cols + ["median_house_value"]].mean().values})
    return [
        ("Imbalanced classes", f"Only {pct((tr['label'] == 'spam').mean())} of messages are spam, so a useless model is already {pct(rows[0]['accuracy'], 1)} accurate:\n\n{t(pd.DataFrame(rows), nd=3)}\n\nJudge by recall/precision, not accuracy; class weights trade precision for recall."),
        ("Data drift", f"Train a house-price model only on inland California districts, then use it on coastal ones, where the same income buys much less house:\n\n{t(drift, nd=1)}\n\nError (RMSE): **${in_err:.0f}k** on held-out inland districts, **${err(~south):.0f}k** on coastal ones. The inputs look similar, but the relationship between them and the price has changed. Monitor input statistics in production and retrain when they move."),
        ("Leakage and other traps", "Leakage: a feature that secretly contains the answer (e.g. 'reply to premium number' logged only after a message was flagged as spam) gives great offline scores and fails live. Also watch for duplicates across train and test (spam campaigns repeat the same text), and labels that change meaning over time."),
    ], "Real projects fail on imbalance, drift and leakage more often than on the choice of algorithm; check for each explicitly."


@walk("m-compression", "digits")
def _():
    import torch, copy
    torch.manual_seed(0); torch.set_num_threads(2); nn = torch.nn
    from sklearn.model_selection import train_test_split
    dg = D("digits"); Xtr, Xte, ytr, yte = train_test_split(dg.data / 16, dg.target, test_size=0.3, random_state=0)
    X = torch.tensor(Xtr, dtype=torch.float32); Y = torch.tensor(ytr); XT = torch.tensor(Xte, dtype=torch.float32)
    big = nn.Sequential(nn.Linear(64, 512), nn.ReLU(), nn.Linear(512, 512), nn.ReLU(), nn.Linear(512, 10))
    o = torch.optim.Adam(big.parameters(), 1e-3)
    for _ in range(40):
        for idx in torch.randperm(len(X)).split(64):
            o.zero_grad(); nn.functional.cross_entropy(big(X[idx]), Y[idx]).backward(); o.step()
    big.eval()
    acc = lambda m: (m(XT).argmax(1).numpy() == yte).mean()
    size = lambda m: sum(p.numel() for p in m.parameters()) * 4 / 1e3
    rows = [{"model": "original (float32)", "size (kB)": size(big), "test accuracy": acc(big)}]
    q = torch.ao.quantization.quantize_dynamic(copy.deepcopy(big), {nn.Linear}, dtype=torch.qint8)
    buf = io.BytesIO(); torch.save(q.state_dict(), buf); qsize = buf.getbuffer().nbytes / 1e3
    buf2 = io.BytesIO(); torch.save(big.state_dict(), buf2)
    rows.append({"model": "int8 dynamic quantisation", "size (kB)": round(qsize * size(big) / (buf2.getbuffer().nbytes / 1e3)), "test accuracy": acc(q)})
    for frac in [0.8, 0.95]:
        p = copy.deepcopy(big)
        for mod in p:
            if isinstance(mod, nn.Linear):
                w = mod.weight.data; th = w.abs().flatten().kthvalue(int(frac * w.numel())).values; w[w.abs() < th] = 0
        rows.append({"model": f"prune {int(frac * 100)}% smallest weights", "size (kB)": round(size(big) * (1 - frac)), "test accuracy": acc(p)})
    small = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 10)); o = torch.optim.Adam(small.parameters(), 1e-3)
    with torch.no_grad(): soft = torch.softmax(big(X) / 3, 1)
    for _ in range(80):
        for idx in torch.randperm(len(X)).split(64):
            lo = small(X[idx]); l = 0.5 * nn.functional.cross_entropy(lo, Y[idx]) + 0.5 * 9 * nn.functional.kl_div(torch.log_softmax(lo / 3, 1), soft[idx], reduction="batchmean")
            o.zero_grad(); l.backward(); o.step()
    small.eval(); rows.append({"model": "distilled student (64 → 32 → 10)", "size (kB)": size(small), "test accuracy": acc(small)})
    return [
        ("A big model on real digits", f"A 64 → 512 → 512 → 10 network: {sum(p.numel() for p in big.parameters()):,} weights, {size(big):.0f} kB as 32-bit floats, {pct(rows[0]['test accuracy'], 1)} on {len(yte)} test digits."),
        ("Three ways to shrink it", "**Quantisation**: store weights as 8-bit integers. **Pruning**: set the smallest weights to zero (stored sparsely, they cost nothing). **Distillation**: train a much smaller student to copy the big model's softened probabilities."),
        ("Size vs accuracy", f"{t(pd.DataFrame(rows), nd=3)}\n\nSizes for pruned models assume sparse storage. Big networks are very redundant, which is why phones can run compressed versions of them."),
    ], "Quantisation, pruning and distillation make models much smaller and faster, usually for a small loss in accuracy."


@walk("m-mlops", "sms")
def _():
    import mlflow, logging
    logging.getLogger("mlflow").setLevel(logging.ERROR)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    tr, te = _split()
    d = tempfile.mkdtemp(); mlflow.set_tracking_uri("sqlite:///" + os.path.join(d, "mlflow.db")); mlflow.set_experiment("spam-filter")
    runs = []
    for C in [0.1, 1, 10]:
        for ngram in [(1, 1), (1, 2)]:
            with mlflow.start_run() as r:
                vec = TfidfVectorizer(sublinear_tf=True, ngram_range=ngram); m = LogisticRegression(max_iter=2000, C=C).fit(vec.fit_transform(tr["text"]), tr["label"])
                f1 = f1_score(te["label"], m.predict(vec.transform(te["text"])), pos_label="spam")
                mlflow.log_params({"C": C, "ngram_range": str(ngram)}); mlflow.log_metric("spam_f1", f1)
    df = mlflow.search_runs(order_by=["metrics.spam_f1 DESC"])[["run_id", "params.C", "params.ngram_range", "metrics.spam_f1"]]
    df["run_id"] = df["run_id"].str[:8]
    best = df.iloc[0]
    return [
        ("Track every experiment", "Each training run logs its parameters and metrics to an MLflow tracking store (a local SQLite file here):\n\n```python\nwith mlflow.start_run():\n    mlflow.log_params({'C': C, 'ngram_range': str(ngram)})\n    mlflow.log_metric('spam_f1', f1)\n```"),
        ("Compare runs", f"6 real runs on the SMS data, sorted by spam F1:\n\n{t(df, nd=4)}\n\nBest: C = {best['params.C']}, n-grams {best['params.ngram_range']}. Without tracking, this kind of result lives only in someone's notebook."),
        ("The rest of the loop", "Register the best model with a version number; deploy it through CI/CD with automatic tests (does it load, is F1 above a floor on a fixed test set); monitor live inputs and predictions; retrain on fresh labelled data when quality drops, and log that run too."),
    ], "MLOps makes ML repeatable: tracked experiments, versioned models, automated tests and deployment, monitoring and retraining."


@walk("m-ml-system-design", "sms")
def _():
    model, tr, te = _spam_model()
    p = model.predict_proba(te["text"])[:, 1]; y = (te["label"] == "spam").values
    rows = []
    for th in [0.3, 0.5, 0.8, 0.95]:
        f = p >= th
        rows.append({"block if P(spam) ≥": th, "spam caught": f[y].mean(), "normal messages wrongly blocked": f[~y].mean(), f"wrongly blocked (of {(~y).sum():,})": int(f[~y].sum())})
    t0 = time.perf_counter(); model.predict_proba(te["text"].tolist()); per = (time.perf_counter() - t0) / len(te)
    return [
        ("1. Clarify the goal and the costs", f"Carrier spam filter. In the real data {pct(y.mean())} of messages are spam. A blocked personal message is much worse than a spam that gets through, so the business metric is 'spam caught while keeping false blocks very rare', not accuracy."),
        ("2. Pick the operating point with real numbers", f"{t(pd.DataFrame(rows), nd=3)}\n\nZero wrong blocks in {(~y).sum():,} test messages only shows the rate is probably below ~1 in 400; a real carrier needs millions of test messages to promise 'less than 1 in a million'. A strict threshold protects normal messages; borderline ones can be sent to a 'possible spam' folder instead of being dropped."),
        ("3. Size the system", f"The model scores a message in about {per * 1e6:.0f} µs in batch on one CPU core here, i.e. roughly {1 / per / 1e3:.0f} thousand messages per second per core. Add the rest of the design: feature pipeline, a blocklist of known spam numbers for instant decisions, feedback ('report spam') as new labels, monitoring of spam rate and complaints, and periodic retraining."),
    ], "ML system design starts from the business cost of each error, chooses the operating point with real numbers, then sizes and monitors the whole pipeline."


@walk("m-industry-cases", ("sms", "books", "housing"))
def _():
    model, tr, te = _spam_model()
    acc = (model.predict(te["text"]) == te["label"]).mean()
    r = D("books"); pop = r.groupby("title")["rating"].agg(["count", "mean"]).sort_values("count", ascending=False)
    h = D("housing").dropna()
    cor = h.select_dtypes("number").corr()["median_house_value"].drop("median_house_value"); top = cor.abs().idxmax()
    from sklearn.ensemble import IsolationForest
    flag = IsolationForest(contamination=0.01, random_state=0).fit_predict(h[["median_income", "total_rooms", "population", "median_house_value"]]) == -1
    cases = pd.DataFrame([
        {"case": "Spam / fraud filtering (telecom, email, payments)", "real-data result here": f"{pct(acc, 1)} accuracy on SMS", "what matters in industry": "false positives cost trust; attackers adapt, so retrain often"},
        {"case": "Recommendations (e-commerce, streaming)", "real-data result here": f"most-rated book: {pop.index[0][:40]} ({pop['count'].iloc[0]} ratings)", "what matters in industry": "popularity bias, cold start for new items, A/B testing on clicks and retention"},
        {"case": "Pricing / valuation (real estate, insurance)", "real-data result here": f"strongest single predictor of house value: {top} (correlation {cor[top]:.2f})", "what matters in industry": "explainability for customers and regulators, drift with the market"},
        {"case": "Anomaly detection (monitoring, fraud)", "real-data result here": f"{flag.sum()} unusual districts flagged out of {len(h):,}", "what matters in industry": "few labels, alert fatigue, a human reviews the alerts"},
    ])
    return [
        ("Four common industry problems, on real data", t(cases)),
        ("What they have in common", "A clear business metric (not just accuracy), a simple baseline shipped first, data pipelines that dominate the work, monitoring after launch, and humans in the loop for costly decisions."),
        ("How to talk about a case in an interview", "Problem and metric → data and labels → baseline → model and features → offline evaluation → online test (A/B) → deployment and monitoring → what went wrong and what you'd change. Use numbers you actually measured, like the ones in this course."),
    ], "Industry ML cases are mostly about the problem framing, the data and the feedback loop; the model is one part of the system."
