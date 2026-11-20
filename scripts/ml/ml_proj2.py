"""End-to-end projects 8-12: deep learning, time series, computer vision, detection, speech."""
from ml_proj_util import P, S
from ml_proj1 import GITIGNORE, RETAIL_URL

P8 = P("p-fashion-cnn", "Image classifier in PyTorch: train, evaluate, export to ONNX, serve with Gradio", "dl", "Intermediate", "2–3 days", "Colab (GPU recommended) or VS Code (CPU works, slower)",
  "Train a convolutional neural network on Fashion-MNIST with a proper PyTorch project layout: dataset code, model module, training loop with validation, early stopping and checkpoints, evaluation with a confusion matrix, ONNX export, and a Gradio web app.",
  ["`data.py`: download Fashion-MNIST from GitHub, parse the IDX files, Dataset + DataLoaders with augmentation", "`model.py`: CNN with BatchNorm and Dropout", "`train.py`: training loop, validation, LR schedule, early stopping, best checkpoint, training curves",
   "`evaluate.py`: test accuracy, per-class accuracy, confusion matrix, worst mistakes", "`export.py`: ONNX export + check with ONNX Runtime", "`app.py`: Gradio app that classifies an uploaded clothing image"],
  ["PyTorch Dataset/DataLoader", "CNNs", "training loops", "BatchNorm, Dropout, augmentation", "learning-rate schedules", "early stopping and checkpoints", "ONNX", "Gradio"],
  "Fashion-MNIST: 70,000 28×28 greyscale images of 10 clothing types (Zalando Research, downloaded from their GitHub repository).",
  ["download IDX files", "Dataset + augmentation", "CNN", "train/validate with early stopping", "test evaluation", "ONNX export", "Gradio app"],
  [
   S("Dependencies", "In Colab: Runtime → Change runtime type → T4 GPU.", "requirements.txt", "torch>=2.2\ntorchvision>=0.17\nnumpy>=1.26\nmatplotlib>=3.8\nscikit-learn>=1.4\nonnx\nonnxruntime\ngradio>=4.0", "text"),
   S("Ignore data and checkpoints", "", ".gitignore", GITIGNORE),
   S("Data", """The raw files are gzipped IDX arrays; parsing them yourself shows exactly what a dataset is. Training images get light augmentation (random crop + flip); validation/test images don't. Hold out 10% of training data for validation.""",
     "data.py", '''
import gzip, urllib.request
from pathlib import Path
import numpy as np, torch
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision.transforms import v2

BASE = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
CLASSES = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]


def _read(name):
    p = Path("data") / name; p.parent.mkdir(exist_ok=True)
    if not p.exists(): urllib.request.urlretrieve(BASE + name, p)
    with gzip.open(p) as f: buf = f.read()
    return np.frombuffer(buf, np.uint8, offset=16 if "images" in name else 8)


def arrays(split="train"):
    pre = "train" if split == "train" else "t10k"
    X = _read(f"{pre}-images-idx3-ubyte.gz").reshape(-1, 28, 28); y = _read(f"{pre}-labels-idx1-ubyte.gz")
    return X, y


class FashionDataset(Dataset):
    def __init__(self, X, y, train=False):
        self.X, self.y = torch.tensor(X, dtype=torch.float32).unsqueeze(1) / 255.0, torch.tensor(y, dtype=torch.long)
        self.tf = v2.Compose([v2.RandomCrop(28, padding=2), v2.RandomHorizontalFlip()]) if train else None
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        x = self.X[i]; x = self.tf(x) if self.tf else x
        return (x - 0.286) / 0.353, self.y[i]


def loaders(batch=128, limit=None, seed=0):
    X, y = arrays("train"); Xt, yt = arrays("test")
    if limit: X, y, Xt, yt = X[:limit], y[:limit], Xt[: limit // 5], yt[: limit // 5]
    n_val = len(y) // 10; g = torch.Generator().manual_seed(seed)
    tr_idx, va_idx = random_split(range(len(y)), [len(y) - n_val, n_val], generator=g)
    tr = FashionDataset(X[list(tr_idx)], y[list(tr_idx)], train=True); va = FashionDataset(X[list(va_idx)], y[list(va_idx)])
    return (DataLoader(tr, batch, shuffle=True, num_workers=2), DataLoader(va, 512), DataLoader(FashionDataset(Xt, yt), 512))
'''),
   S("The model", "Two conv blocks (conv-BN-ReLU ×2 + pooling) and a small classifier head. ~0.4M parameters — fast on CPU, ~93% accuracy.", "model.py", '''
import torch.nn as nn


def block(cin, cout):
    return nn.Sequential(nn.Conv2d(cin, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU(),
                         nn.Conv2d(cout, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout(0.25))


class FashionCNN(nn.Module):
    def __init__(self, n_classes=10):
        super().__init__()
        self.features = nn.Sequential(block(1, 32), block(32, 64))
        self.head = nn.Sequential(nn.Flatten(), nn.Linear(64 * 7 * 7, 256), nn.ReLU(), nn.Dropout(0.4), nn.Linear(256, n_classes))
    def forward(self, x): return self.head(self.features(x))
'''),
   S("Training loop", """The canonical loop with everything production code needs: device handling, `model.train()`/`model.eval()`, OneCycle LR schedule, validation each epoch, **early stopping**, saving the best checkpoint, and a CSV log for curves. `--limit` trains on a subset for quick experiments.""",
     "train.py", '''
"""python train.py --epochs 15   (add --limit 6000 for a quick run)"""
import argparse, csv, time
import torch, torch.nn as nn
from data import loaders
from model import FashionCNN

ap = argparse.ArgumentParser(); ap.add_argument("--epochs", type=int, default=15); ap.add_argument("--lr", type=float, default=3e-3)
ap.add_argument("--limit", type=int, default=None); ap.add_argument("--patience", type=int, default=4); args = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"; torch.manual_seed(0)
train_dl, val_dl, _ = loaders(limit=args.limit)
model = FashionCNN().to(dev); opt = torch.optim.AdamW(model.parameters(), args.lr, weight_decay=1e-4); loss_fn = nn.CrossEntropyLoss(label_smoothing=0.05)
sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=args.epochs * len(train_dl))
best, wait, log = 0.0, 0, []
for epoch in range(1, args.epochs + 1):
    t0, total = time.time(), 0.0; model.train()
    for x, y in train_dl:
        x, y = x.to(dev), y.to(dev); opt.zero_grad(); loss = loss_fn(model(x), y); loss.backward(); opt.step(); sched.step(); total += loss.item() * len(y)
    model.eval(); correct = n = 0
    with torch.no_grad():
        for x, y in val_dl: correct += (model(x.to(dev)).argmax(1).cpu() == y).sum().item(); n += len(y)
    acc = correct / n; log.append((epoch, total / len(train_dl.dataset), acc))
    print(f"epoch {epoch:2d}  train loss {total / len(train_dl.dataset):.4f}  val acc {acc:.4f}  ({time.time() - t0:.0f}s)")
    if acc > best: best, wait = acc, 0; torch.save(model.state_dict(), "best.pt")
    else:
        wait += 1
        if wait >= args.patience: print("early stopping"); break
csv.writer(open("training_log.csv", "w", newline="")).writerows([("epoch", "train_loss", "val_acc"), *log])
print(f"best validation accuracy {best:.4f} -> best.pt")
'''),
   S("Evaluate on the test set", "Load the best checkpoint; report accuracy, per-class accuracy and the confusion matrix — shirts vs T-shirts vs pullovers are the hard classes.", "evaluate.py", '''
import numpy as np, torch
from sklearn.metrics import classification_report, confusion_matrix
from data import CLASSES, loaders
from model import FashionCNN
import sys

_, _, test_dl = loaders(limit=int(sys.argv[1]) if len(sys.argv) > 1 else None)
model = FashionCNN(); model.load_state_dict(torch.load("best.pt", map_location="cpu")); model.eval()
preds, ys = [], []
with torch.no_grad():
    for x, y in test_dl: preds.append(model(x).argmax(1).numpy()); ys.append(y.numpy())
p, y = np.concatenate(preds), np.concatenate(ys)
print(f"test accuracy {(p == y).mean():.4f}")
print(classification_report(y, p, target_names=CLASSES, digits=3))
cm = confusion_matrix(y, p); np.fill_diagonal(cm, 0); i, j = np.unravel_index(cm.argmax(), cm.shape)
print(f"most common confusion: {CLASSES[i]} predicted as {CLASSES[j]} ({cm[i, j]} times)")
'''),
   S("Export to ONNX", "ONNX runs in ONNX Runtime on servers, phones and browsers without PyTorch. Always check the exported model gives the same outputs.", "export.py", '''
import numpy as np, onnxruntime as ort, torch
from model import FashionCNN

model = FashionCNN(); model.load_state_dict(torch.load("best.pt", map_location="cpu")); model.eval()
dummy = torch.randn(1, 1, 28, 28)
torch.onnx.export(model, (dummy,), "fashion_cnn.onnx", input_names=["image"], output_names=["logits"], dynamic_axes={"image": {0: "batch"}}, dynamo=False)
sess = ort.InferenceSession("fashion_cnn.onnx"); x = np.random.randn(4, 1, 28, 28).astype(np.float32)
print("ONNX matches PyTorch:", np.allclose(sess.run(None, {"image": x})[0], model(torch.from_numpy(x)).detach().numpy(), atol=1e-4))
'''),
   S("Gradio app", "Uses the ONNX model (no PyTorch needed at serving time). Real photos must be converted to the dataset's style: greyscale, 28×28, light object on dark background.", "app.py", '''
import gradio as gr, numpy as np, onnxruntime as ort
from PIL import Image, ImageOps
from data import CLASSES

sess = ort.InferenceSession("fashion_cnn.onnx")


def classify(img: Image.Image):
    g = ImageOps.invert(img.convert("L")).resize((28, 28))            # photos: dark item on light background -> invert
    x = ((np.asarray(g, np.float32) / 255.0 - 0.286) / 0.353)[None, None]
    logits = sess.run(None, {"image": x})[0][0]; p = np.exp(logits - logits.max()); p /= p.sum()
    return {c: float(v) for c, v in zip(CLASSES, p)}


gr.Interface(classify, gr.Image(type="pil"), gr.Label(num_top_classes=3), title="Fashion classifier").launch()
'''),
   S("Run it", "", None, "python train.py --epochs 15     # ~2 min on a Colab T4, ~10 min on CPU\npython evaluate.py\npython export.py\npython app.py", "bash"),
  ],
  check=["python train.py --epochs 2 --limit 12000", "python evaluate.py 12000", "python export.py"],
  talk=["Your training-loop design: train/eval modes, early stopping on validation accuracy, best checkpoint, OneCycle schedule.", "Error analysis: shirt vs T-shirt confusion and what you'd try (more augmentation, bigger model, higher resolution).",
        "Why ONNX for deployment (no Python ML stack, faster CPU inference)."],
  errors=[("CUDA out of memory", "lower --batch / use a smaller model; in Colab restart the runtime"), ("Validation accuracy stuck at 10%", "labels and images misaligned or learning rate too high — overfit one batch first"),
          ("RuntimeError in DataLoader workers on Windows", "wrap the training code in `if __name__ == '__main__':` or set num_workers=0")],
  extend=["Track runs with TensorBoard or Weights & Biases", "Try a ResNet-style model and mixup", "Quantise the ONNX model to int8"],
  see=["m-pytorch", "m-cnn", "m-dl-regularization", "m-optimizers", "m-compression"])

P9 = P("p-demand-forecast", "Daily demand forecasting: SARIMA vs LightGBM vs LSTM with backtesting", "dl", "Advanced", "3–4 days", "VS Code or Colab (CPU)",
  "Forecast daily revenue of a real online retailer 28 days ahead. Compare a seasonal-naive baseline, SARIMA, LightGBM with lag/calendar features and an LSTM using rolling-origin backtesting, then produce a forecast with prediction intervals.",
  ["`series.py`: build a clean daily series (UK revenue) with holidays and missing-day handling", "`features.py`: lag, rolling and calendar features without leakage", "`backtest.py`: rolling-origin evaluation of 4 models (MAE, WAPE, MASE)",
   "`lstm.py`: a PyTorch LSTM forecaster", "`forecast.py`: final 28-day forecast with LightGBM quantile intervals and a plot"],
  ["time-series EDA", "stationarity", "SARIMA", "lag features", "LightGBM quantile regression", "LSTMs", "walk-forward backtesting", "forecast metrics"],
  "UCI Online Retail transactions aggregated to daily revenue (Dec 2010 – Dec 2011).",
  ["aggregate to daily", "baselines", "features", "backtest 4 models", "pick best", "forecast + intervals"],
  [
   S("Dependencies", "", "requirements.txt", "pandas>=2.0\nnumpy>=1.26\nstatsmodels>=0.14\nlightgbm>=4.0\ntorch>=2.2\nmatplotlib>=3.8", "text"),
   S("Build the daily series", """Real business series have gaps: this shop is closed on Saturdays and over Christmas. Reindex to every day, mark closed days, and keep the closure flag as a feature rather than inventing sales.""",
     "series.py", f'''
from pathlib import Path
import pandas as pd
URL = "{RETAIL_URL}"


def daily() -> pd.DataFrame:
    p = Path("data/retail.csv"); p.parent.mkdir(exist_ok=True)
    if not p.exists(): pd.read_csv(URL, dtype={{"InvoiceNo": str, "StockCode": str}}).to_csv(p, index=False)
    df = pd.read_csv(p, dtype={{"InvoiceNo": str, "StockCode": str}})
    df = df[~df.InvoiceNo.str.startswith("C") & (df.Quantity > 0) & (df.UnitPrice > 0) & (df.Country == "United Kingdom")]
    df["date"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M").dt.normalize()
    s = (df.Quantity * df.UnitPrice).groupby(df["date"]).sum()
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"), fill_value=0.0)
    out = pd.DataFrame({{"y": s}}); out["closed"] = (out.y == 0).astype(int)
    return out.loc["2010-12-06":]


if __name__ == "__main__":
    d = daily(); print(d.describe().round(0)); print("closed days:", d.closed.sum())
'''),
   S("Leakage-free features", "Every feature for day t uses only data up to t−h (h = forecast horizon), so the same features are available when we really forecast.", "features.py", '''
import numpy as np, pandas as pd


def make(d: pd.DataFrame, horizon: int = 28) -> pd.DataFrame:
    f = pd.DataFrame(index=d.index)
    f["dow"], f["dom"], f["month"], f["weekofyear"] = d.index.dayofweek, d.index.day, d.index.month, d.index.isocalendar().week.astype(int).values
    f["closed"] = d["closed"]; f["days_to_xmas"] = np.clip((pd.to_datetime(d.index.year.astype(str) + "-12-25") - d.index).days.to_numpy(), -10, 120)
    y = d["y"]
    for lag in (horizon, horizon + 7, horizon + 14, horizon + 21):       # only ~1 year of history, so no yearly lag
        f[f"lag{lag}"] = y.shift(lag)
    f["roll7"] = y.shift(horizon).rolling(7).mean(); f["roll28"] = y.shift(horizon).rolling(28).mean()
    f["same_dow_mean4"] = sum(y.shift(horizon + 7 * k) for k in range(4)) / 4
    return f
'''),
   S("LSTM forecaster", "A sequence model over the last 56 days that outputs the next 28 at once (direct multi-step). Inputs are scaled with training statistics only.", "lstm.py", '''
import numpy as np, torch, torch.nn as nn


class Net(nn.Module):
    def __init__(self, h=28): super().__init__(); self.lstm = nn.LSTM(2, 64, num_layers=2, batch_first=True, dropout=0.1); self.out = nn.Linear(64, h)
    def forward(self, x): return self.out(self.lstm(x)[0][:, -1])


def fit_predict(y: np.ndarray, closed: np.ndarray, horizon=28, window=56, epochs=150, seed=0):
    torch.manual_seed(seed); mu, sd = y.mean(), y.std() + 1e-9; z = (y - mu) / sd
    X = np.stack([np.stack([z[i:i + window], closed[i:i + window]], 1) for i in range(len(z) - window - horizon + 1)])
    Y = np.stack([z[i + window:i + window + horizon] for i in range(len(z) - window - horizon + 1)])
    X, Y = torch.tensor(X, dtype=torch.float32), torch.tensor(Y, dtype=torch.float32)
    net = Net(horizon); opt = torch.optim.Adam(net.parameters(), 3e-3)
    for _ in range(epochs):
        opt.zero_grad(); loss = nn.functional.mse_loss(net(X), Y); loss.backward(); opt.step()
    last = torch.tensor(np.stack([z[-window:], closed[-window:]], 1)[None], dtype=torch.float32)
    with torch.no_grad(): return net(last)[0].numpy() * sd + mu
'''),
   S("Backtest four models", """Rolling-origin evaluation: for several cut-off dates, train on everything before, forecast the next 28 days, measure error, repeat. **MASE** < 1 means better than the seasonal-naive baseline.""",
     "backtest.py", '''
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from lightgbm import LGBMRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX
import features, lstm
from series import daily

H = 28; d = daily(); F = features.make(d, H)
origins = pd.date_range("2011-08-01", "2011-11-01", freq="31D")


def metrics(y, p, naive_mae):
    mae = np.abs(y - p).mean(); return {"MAE": mae, "WAPE": np.abs(y - p).sum() / np.abs(y).sum(), "MASE": mae / naive_mae}


rows = []
for o in origins:
    train, test = d[d.index < o], d[(d.index >= o) & (d.index < o + pd.Timedelta(days=H))]
    naive = train.y.iloc[-7:].to_numpy(); p_naive = np.resize(naive, H) * (1 - test.closed.to_numpy())
    naive_mae = np.abs(test.y.to_numpy() - p_naive).mean()
    sar = SARIMAX(train.y.iloc[-210:], exog=train.closed.iloc[-210:], order=(1, 0, 1), seasonal_order=(1, 1, 1, 7)).fit(disp=False)
    p_sar = np.clip(sar.forecast(H, exog=test.closed).to_numpy(), 0, None)
    tr = F[F.index < o].dropna(); gbm = LGBMRegressor(n_estimators=400, learning_rate=0.03, num_leaves=15, min_child_samples=10, verbose=-1, random_state=0)
    gbm.fit(tr, d.y.loc[tr.index]); p_gbm = np.clip(gbm.predict(F.loc[test.index].fillna(0)), 0, None)
    p_lstm = np.clip(lstm.fit_predict(train.y.to_numpy(), train.closed.to_numpy(), H), 0, None) * (1 - test.closed.to_numpy())
    for name, p in [("seasonal naive", p_naive), ("SARIMA", p_sar), ("LightGBM", p_gbm), ("LSTM", p_lstm)]:
        rows.append({"origin": o.date(), "model": name, **metrics(test.y.to_numpy(), p, naive_mae)})
res = pd.DataFrame(rows); print(res.groupby("model")[["MAE", "WAPE", "MASE"]].mean().sort_values("MAE").round(3))
'''),
   S("Final forecast with intervals", "Refit on all data and forecast the next 28 days. Use the backtest to choose — on this data SARIMA edges out the others on MAE, so also compare its forecast — but LightGBM with **quantile loss** (10th/50th/90th percentiles) gives a flexible 80% prediction interval. Planners need ranges, not single numbers.", "forecast.py", '''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, pandas as pd
from lightgbm import LGBMRegressor
import features
from series import daily

H = 28; d = daily()
future = pd.date_range(d.index[-1] + pd.Timedelta(days=1), periods=H, freq="D")
ext = pd.concat([d, pd.DataFrame({"y": np.nan, "closed": (future.dayofweek == 5).astype(int)}, index=future)])
F = features.make(ext, H); tr = F.loc[d.index].dropna()
pred = {}
for q, name in [(0.1, "p10"), (0.5, "p50"), (0.9, "p90")]:
    m = LGBMRegressor(objective="quantile", alpha=q, n_estimators=400, learning_rate=0.03, num_leaves=15, verbose=-1, random_state=0).fit(tr, d.y.loc[tr.index])
    pred[name] = np.clip(m.predict(F.loc[future].fillna(0)), 0, None) * (1 - F.loc[future, "closed"].to_numpy())
out = pd.DataFrame(pred, index=future).round(0); out.to_csv("forecast.csv"); print(out.head(10))
fig, ax = plt.subplots(figsize=(11, 4)); d.y.iloc[-120:].plot(ax=ax, label="actual"); out.p50.plot(ax=ax, label="forecast")
ax.fill_between(future, out.p10, out.p90, alpha=0.3, label="80% interval"); ax.legend(); ax.set_title("UK daily revenue: 28-day forecast"); fig.tight_layout(); fig.savefig("forecast.png", dpi=110)
print("saved forecast.csv and forecast.png")
'''),
   S("Run it", "", None, "python series.py\npython backtest.py     # ~3 minutes\npython forecast.py", "bash"),
  ],
  check=["python series.py", "python backtest.py", "python forecast.py"],
  talk=["Rolling-origin backtesting and why random CV is wrong for time series.", "Leakage-safe features: lags at least the horizon away.",
        "Which model won and by how much vs seasonal naive (MASE); why gradient boosting often beats LSTMs on short single series.", "Quantile forecasts for planning safety stock."],
  errors=[("SARIMA ConvergenceWarning", "shorter training window, simpler orders, or ignore if forecasts look sane"), ("Forecast spikes on closed days", "pass the closed-day flag as a feature/exogenous variable")],
  extend=["Forecast per product category (hierarchical forecasting)", "Try Prophet and N-HiTS (neuralforecast)", "Turn forecasts into inventory orders (newsvendor model)"],
  see=["m-time-series", "m-ts-dl", "m-lstm-gru", "m-gradient-boosting", "m-feature-engineering", "m-leakage"])

P10 = P("p-food-transfer", "Food image classifier with transfer learning (EfficientNet) + Grad-CAM + Hugging Face Space", "cv", "Intermediate", "2–3 days", "Colab with T4 GPU",
  "Fine-tune an ImageNet-pretrained EfficientNet on Food-101 classes, compare frozen-backbone vs full fine-tuning, explain predictions with Grad-CAM, and publish a web demo on Hugging Face Spaces.",
  ["`data.py`: load Food-101 (Hugging Face Datasets), choose N classes, train/val/test splits, the model's own preprocessing + augmentation", "`train.py`: two-stage training (head only → unfreeze), mixed precision, checkpoints",
   "`gradcam.py`: heat-maps of where the model looks", "`app.py`: Gradio app + `README.md` header for a Hugging Face Space"],
  ["transfer learning", "fine-tuning strategies", "data augmentation", "mixed precision on GPU", "Grad-CAM", "Hugging Face Datasets & Spaces"],
  "Food-101 (101,000 images, 101 dishes) via `datasets.load_dataset('ethz/food101')`; default uses 10 classes so it trains in ~10 minutes on a T4.",
  ["load + subset classes", "transforms", "stage 1: train head", "stage 2: fine-tune top blocks", "evaluate", "Grad-CAM", "Space"],
  [
   S("Dependencies", "", "requirements.txt", "torch>=2.2\ntorchvision>=0.17\ndatasets>=2.18\nnumpy>=1.26\nmatplotlib>=3.8\ngradio>=4.0", "text"),
   S("Data", """`--smoke` swaps in random images so you can test the whole pipeline in seconds before spending GPU time. Use the pretrained weights' own transforms (resize, crop, normalise) — mismatched preprocessing silently costs accuracy.""",
     "data.py", '''
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import v2

CLASSES = ["pizza", "sushi", "ramen", "samosa", "chicken_curry", "ice_cream", "french_fries", "pancakes", "fried_rice", "donuts"]
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
train_tf = v2.Compose([v2.RandomResizedCrop(224, scale=(0.6, 1.0)), v2.RandomHorizontalFlip(), v2.ColorJitter(0.2, 0.2, 0.2), v2.ToImage(), v2.ToDtype(torch.float32, scale=True), v2.Normalize(MEAN, STD)])
eval_tf = v2.Compose([v2.Resize(256), v2.CenterCrop(224), v2.ToImage(), v2.ToDtype(torch.float32, scale=True), v2.Normalize(MEAN, STD)])


class HFImages(Dataset):
    def __init__(self, ds, tf, label_map): self.ds, self.tf, self.map = ds, tf, label_map
    def __len__(self): return len(self.ds)
    def __getitem__(self, i): r = self.ds[i]; return self.tf(r["image"].convert("RGB")), self.map[r["label"]]


class FakeImages(Dataset):                       # --smoke: random tensors, same shapes
    def __init__(self, n): self.n = n
    def __len__(self): return self.n
    def __getitem__(self, i): return torch.randn(3, 224, 224), i % len(CLASSES)


def loaders(batch=64, smoke=False):
    if smoke:
        return [DataLoader(FakeImages(n), 8, shuffle=s) for n, s in ((32, True), (16, False), (16, False))]
    from datasets import load_dataset
    ds = load_dataset("ethz/food101"); names = ds["train"].features["label"].names
    keep = {names.index(c): k for k, c in enumerate(CLASSES)}
    tr = ds["train"].filter(lambda r: r["label"] in keep).train_test_split(test_size=0.1, seed=0)
    te = ds["validation"].filter(lambda r: r["label"] in keep)
    mk = lambda d, tf, sh: DataLoader(HFImages(d, tf, keep), batch, shuffle=sh, num_workers=2, pin_memory=True)
    return mk(tr["train"], train_tf, True), mk(tr["test"], eval_tf, False), mk(te, eval_tf, False)
'''),
   S("Two-stage fine-tuning", """Stage 1: freeze the backbone, train only the new classifier (fast, safe). Stage 2: unfreeze the last blocks with a 10× smaller learning rate. Mixed precision (`torch.autocast`) roughly doubles speed on GPU.""",
     "train.py", '''
"""python train.py            (add --smoke to test the pipeline without downloading data/weights)"""
import argparse, torch, torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from data import CLASSES, loaders

ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--epochs1", type=int, default=3); ap.add_argument("--epochs2", type=int, default=4)
args = ap.parse_args(); dev = "cuda" if torch.cuda.is_available() else "cpu"
model = efficientnet_b0(weights=None if args.smoke else EfficientNet_B0_Weights.DEFAULT)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(CLASSES)); model.to(dev)
train_dl, val_dl, test_dl = loaders(smoke=args.smoke)
if args.smoke: args.epochs1 = args.epochs2 = 1
scaler = torch.amp.GradScaler(enabled=dev == "cuda"); loss_fn = nn.CrossEntropyLoss(label_smoothing=0.1)


def run(epochs, params, lr):
    opt = torch.optim.AdamW(params, lr, weight_decay=0.01); best = 0
    for ep in range(epochs):
        model.train()
        for x, y in train_dl:
            x, y = x.to(dev), y.to(dev); opt.zero_grad()
            with torch.autocast(dev, enabled=dev == "cuda"): loss = loss_fn(model(x), y)
            scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
        acc = accuracy(val_dl); print(f"  epoch {ep + 1}: val accuracy {acc:.3f}")
        if acc >= best: best = acc; torch.save(model.state_dict(), "food_effnet.pt")


@torch.no_grad()
def accuracy(dl):
    model.eval(); c = n = 0
    for x, y in dl: c += (model(x.to(dev)).argmax(1).cpu() == y).sum().item(); n += len(y)
    return c / n


for p in model.features.parameters(): p.requires_grad = False
print("stage 1: head only"); run(args.epochs1, model.classifier.parameters(), 1e-3)
for p in model.features[-3:].parameters(): p.requires_grad = True
print("stage 2: fine-tune last 3 blocks"); run(args.epochs2, [{"params": model.features[-3:].parameters(), "lr": 1e-4}, {"params": model.classifier.parameters(), "lr": 3e-4}], 1e-4)
model.load_state_dict(torch.load("food_effnet.pt", map_location=dev)); print(f"test accuracy {accuracy(test_dl):.3f}")
'''),
   S("Grad-CAM", "Hook the last conv layer, weight its feature maps by the gradient of the predicted class, and overlay the heat-map. Check it highlights the food, not the plate or background.", "gradcam.py", '''
import sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, torch, torch.nn as nn, torch.nn.functional as F
from torchvision.models import efficientnet_b0
from PIL import Image
from data import CLASSES, eval_tf

model = efficientnet_b0(); model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(CLASSES))
model.load_state_dict(torch.load("food_effnet.pt", map_location="cpu")); model.eval()
acts = {}
model.features[-1].register_forward_hook(lambda m, i, o: acts.__setitem__("a", o))
img = Image.open(sys.argv[1]).convert("RGB") if len(sys.argv) > 1 else Image.new("RGB", (300, 300), (200, 120, 60))
x = eval_tf(img)[None]; logits = model(x); c = logits.argmax(1).item()
a = acts["a"]; g = torch.autograd.grad(logits[0, c], a)[0]
cam = F.relu((g.mean((2, 3), keepdim=True) * a).sum(1))[0].detach(); cam = F.interpolate(cam[None, None], (224, 224), mode="bilinear")[0, 0]
cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-9)
fig, ax = plt.subplots(); ax.imshow(img.resize((224, 224))); ax.imshow(cam, alpha=0.45, cmap="jet"); ax.set_title(f"{CLASSES[c]} {logits.softmax(1)[0, c]:.0%}"); ax.axis("off")
fig.savefig("gradcam.png", dpi=110); print("predicted", CLASSES[c], "-> gradcam.png")
'''),
   S("Gradio app", "", "app.py", '''
import gradio as gr, torch, torch.nn as nn
from torchvision.models import efficientnet_b0
from data import CLASSES, eval_tf

model = efficientnet_b0(); model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(CLASSES))
model.load_state_dict(torch.load("food_effnet.pt", map_location="cpu")); model.eval()


def predict(img):
    with torch.no_grad(): p = model(eval_tf(img.convert("RGB"))[None]).softmax(1)[0]
    return {c.replace("_", " "): float(v) for c, v in zip(CLASSES, p)}


gr.Interface(predict, gr.Image(type="pil"), gr.Label(num_top_classes=3), title="What's on the plate?").launch()
'''),
   S("Hugging Face Space card", """Create a Space (SDK: Gradio) on huggingface.co, then push `app.py`, `data.py`, `requirements.txt`, `food_effnet.pt` and this README (the YAML header configures the Space). Use Git LFS for the .pt file or upload it in the web UI.""",
     "README.md", '''
---
title: Food Classifier
emoji: 🍕
colorFrom: yellow
colorTo: red
sdk: gradio
app_file: app.py
pinned: false
---
# Food classifier
EfficientNet-B0 fine-tuned on 10 Food-101 classes. Test accuracy: (fill in). Grad-CAM shows it attends to the dish.''', "markdown"),
   S("Run it", "", None, "python train.py --smoke     # 1-minute pipeline test\npython train.py             # real run on a Colab T4 (~10 min)\npython gradcam.py my_photo.jpg\npython app.py", "bash"),
  ],
  check=["python train.py --smoke", "python gradcam.py"],
  verify="smoke",
  talk=["Why two-stage fine-tuning with discriminative learning rates.", "Using the pretrained model's preprocessing; augmentation choices for food photos.", "Grad-CAM as a sanity check against shortcut learning.", "Mixed precision and GPU memory trade-offs."],
  errors=[("CUDA out of memory", "batch 32 or smaller, keep autocast on"), ("Accuracy ~10% after training", "labels not remapped to 0..N-1 or wrong normalisation"), ("Space build fails", "pin versions in requirements.txt; upload the model file with LFS")],
  extend=["All 101 classes", "Swap in ConvNeXt or ViT via `timm`", "Add calorie estimation with a portion-size regressor"],
  see=["m-transfer-learning", "m-augmentation", "m-cnn-architectures", "m-cnn-understand", "m-cv-overview"])

P11 = P("p-yolo-detection", "Custom object detection with YOLO (Ultralytics): train, evaluate mAP, count objects in video", "cv", "Intermediate", "2–3 days", "Colab with GPU (CPU fine for the 8-image demo)",
  "Train a YOLO detector on a labelled dataset, evaluate mAP, tune the confidence threshold, run it on images and video with tracking and line-crossing counts, and export it for deployment.",
  ["`prepare.md`: how to label your own data (Roboflow/CVAT) and the YOLO folder format", "`train.py`: fine-tune a COCO-pretrained YOLO11n", "`evaluate.py`: mAP50, mAP50-95, precision/recall per class",
   "`count_video.py`: track objects across frames and count those crossing a line", "export to ONNX"],
  ["object detection", "YOLO format labels", "transfer learning for detection", "mAP and IoU", "confidence/NMS thresholds", "multi-object tracking"],
  "Ultralytics' COCO8 sample (downloads automatically) for the walkthrough; swap in your own dataset — e.g. vehicles, helmets, PPE, retail shelves — exported from Roboflow in YOLO format.",
  ["label data", "data.yaml", "fine-tune", "validate (mAP)", "predict + track", "export"],
  [
   S("Dependencies", "", "requirements.txt", "ultralytics>=8.3\nopencv-python\nnumpy>=1.26", "text"),
   S("Your own dataset (format guide)", """YOLO expects `images/train`, `images/val`, `labels/train`, `labels/val`; each label file has one line per object: `class x_center y_center width height`, all normalised to 0–1. Label 100–300 images per class to start; include hard cases (night, occlusion, small objects).""",
     "data_example.yaml", '''
# my_data.yaml  (point train.py at this for your own dataset)
path: datasets/helmets
train: images/train
val: images/val
names:
  0: helmet
  1: no_helmet''', "yaml"),
   S("Train", "Start from COCO-pretrained weights (transfer learning). `imgsz`, `epochs` and the model size (n/s/m) are the main knobs.", "train.py", '''
"""python train.py --data coco8.yaml --epochs 50   (use your own data.yaml)"""
import argparse, os
from ultralytics import YOLO

ap = argparse.ArgumentParser(); ap.add_argument("--data", default="coco8.yaml"); ap.add_argument("--epochs", type=int, default=50)
ap.add_argument("--imgsz", type=int, default=640); ap.add_argument("--model", default="yolo11n.pt"); args = ap.parse_args()
model = YOLO(args.model)                                   # downloads COCO-pretrained weights
model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, batch=16, patience=15, project=os.path.abspath("runs"), name="exp", exist_ok=True, plots=True)   # -> runs/exp/weights/best.pt
print("best weights:", model.trainer.best)
'''),
   S("Evaluate", "mAP50-95 averages over IoU thresholds 0.5…0.95 (COCO metric); per-class AP shows which classes need more data.", "evaluate.py", '''
import sys
from ultralytics import YOLO

model = YOLO(sys.argv[1] if len(sys.argv) > 1 else "runs/exp/weights/best.pt")
m = model.val(data=sys.argv[2] if len(sys.argv) > 2 else "coco8.yaml", plots=False, verbose=False)
print(f"mAP50 {m.box.map50:.3f}  mAP50-95 {m.box.map:.3f}  precision {m.box.mp:.3f}  recall {m.box.mr:.3f}")
for i, ap in zip(m.box.ap_class_index, m.box.maps[m.box.ap_class_index]):
    print(f"  {model.names[int(i)]:15s} AP50-95 {ap:.3f}")
'''),
   S("Count objects crossing a line in a video", """`model.track` runs detection + ByteTrack so each object keeps an ID; we count an ID once when its centre crosses the line. Works on a file or a webcam (`source=0`).""",
     "count_video.py", '''
"""python count_video.py traffic.mp4 [weights]   -> counted.mp4"""
import sys, cv2
from ultralytics import YOLO

src = sys.argv[1] if len(sys.argv) > 1 else "demo.mp4"; model = YOLO(sys.argv[2] if len(sys.argv) > 2 else "yolo11n.pt")
cap = cv2.VideoCapture(src); w, h = int(cap.get(3)), int(cap.get(4)); fps = cap.get(5) or 25
out = cv2.VideoWriter("counted.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)); line_y = h // 2
last_y, counted = {}, set()
while True:
    ok, frame = cap.read()
    if not ok: break
    r = model.track(frame, persist=True, conf=0.35, verbose=False)[0]
    if r.boxes.id is not None:
        for box, tid, cls in zip(r.boxes.xyxy.tolist(), r.boxes.id.int().tolist(), r.boxes.cls.int().tolist()):
            cy = (box[1] + box[3]) / 2
            if tid in last_y and last_y[tid] < line_y <= cy: counted.add(tid)
            last_y[tid] = cy
    frame = r.plot(); cv2.line(frame, (0, line_y), (w, line_y), (0, 255, 255), 2)
    cv2.putText(frame, f"count: {len(counted)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3); out.write(frame)
cap.release(); out.release(); print("objects crossed the line:", len(counted), "-> counted.mp4")
'''),
   S("Make a test video (optional)", "Creates a short clip from a sample image so the counting script can be tried without your own footage.", "make_demo_video.py", '''
import cv2, numpy as np, urllib.request
urllib.request.urlretrieve("https://ultralytics.com/images/bus.jpg", "bus.jpg")
img = cv2.imread("bus.jpg"); h, w = img.shape[:2]; out = cv2.VideoWriter("demo.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 10, (w, h))
for t in range(20):
    M = np.float32([[1, 0, 0], [0, 1, -60 + 6 * t]]); out.write(cv2.warpAffine(img, M, (w, h)))
out.release(); print("demo.mp4 written")
'''),
   S("Export", "", None, "yolo export model=runs/exp/weights/best.pt format=onnx   # or engine (TensorRT), tflite, coreml", "bash"),
   S("Run it", "", None, "python train.py --data coco8.yaml --epochs 30\npython evaluate.py runs/exp/weights/best.pt coco8.yaml\npython make_demo_video.py && python count_video.py demo.mp4 runs/exp/weights/best.pt", "bash"),
  ],
  check=["python train.py --data coco8.yaml --epochs 1 --imgsz 320", "python evaluate.py runs/exp/weights/best.pt coco8.yaml"],
  talk=["The YOLO label format, why pretrained COCO weights speed up convergence.", "mAP50 vs mAP50-95 and how you picked the confidence threshold for the use case.", "Tracking + line crossing for counting; failure modes (occlusion, ID switches)."],
  errors=[("Training finds no labels", "label .txt files must mirror image file names and folder structure (images/ ↔ labels/)"), ("Low mAP on small objects", "increase imgsz, use a bigger model, add tiled/close-up images")],
  extend=["Helmet/PPE detection for a factory", "Deploy on a Raspberry Pi / Jetson with the exported model", "Instance segmentation with yolo11n-seg"],
  see=["m-object-detection", "m-video", "m-transfer-learning"])

P12 = P("p-meeting-transcriber", "Meeting transcriber: speech-to-text (Whisper) + speaker-friendly summary with an LLM", "cv", "Intermediate", "2 days", "Colab with GPU (CPU works for short files)",
  "Upload an audio recording, transcribe it with Whisper (timestamps, language detection), then summarise it with an LLM into decisions, action items and owners — in a Gradio app. Includes word-error-rate evaluation.",
  ["`transcribe.py`: Whisper via Hugging Face transformers pipeline with chunking for long audio", "`summarize.py`: provider-agnostic LLM summariser (OpenAI, Anthropic, or local Ollama) with a structured JSON output", "`wer.py`: evaluate transcription accuracy", "`app.py`: Gradio app"],
  ["speech recognition", "audio preprocessing (16 kHz mono)", "long-audio chunking", "WER", "LLM prompting with structured output", "Gradio"],
  "Your own recordings (MP3/WAV/M4A); a sample clip is downloaded from the Whisper GitHub repository.",
  ["load audio (16 kHz)", "Whisper ASR with timestamps", "clean transcript", "LLM summary (JSON)", "evaluate WER", "app"],
  [
   S("Dependencies", "", "requirements.txt", "transformers>=4.40\ntorch>=2.2\naccelerate\nlibrosa\nsoundfile\njiwer\nopenai>=1.0\nanthropic>=0.30\ngradio>=4.0", "text"),
   S("Transcribe", """`chunk_length_s=30` lets Whisper handle hour-long audio; `return_timestamps=True` gives segments you can show next to the text. Use `whisper-small` on CPU, `whisper-large-v3` (or `-turbo`) on a GPU.""",
     "transcribe.py", '''
"""python transcribe.py audio.mp3"""
import sys, torch
from transformers import pipeline

MODEL = "openai/whisper-small"          # "openai/whisper-large-v3-turbo" on a GPU
dev = 0 if torch.cuda.is_available() else -1
asr = pipeline("automatic-speech-recognition", model=MODEL, device=dev, torch_dtype=torch.float16 if dev == 0 else torch.float32)


def transcribe(path: str) -> dict:
    out = asr(path, chunk_length_s=30, batch_size=8, return_timestamps=True, generate_kwargs={"task": "transcribe"})
    segments = [{"start": c["timestamp"][0], "end": c["timestamp"][1], "text": c["text"].strip()} for c in out["chunks"]]
    return {"text": out["text"].strip(), "segments": segments}


if __name__ == "__main__":
    r = transcribe(sys.argv[1])
    for s in r["segments"][:10]: print(f"[{s['start']:6.1f}s] {s['text']}")
'''),
   S("Summarise with any LLM", """One function, three providers. Ask for **JSON** with a fixed schema so the app can render it, and tell the model not to invent owners or dates that weren't said.""",
     "summarize.py", '''
import json, os

PROMPT = """You summarise meeting transcripts. Return ONLY JSON:
{"summary": "3-5 sentences", "decisions": ["..."], "action_items": [{"task": "...", "owner": "name or null", "due": "date or null"}], "open_questions": ["..."]}
Use only information in the transcript. If an owner or date is not stated, use null.
<transcript>
%s
</transcript>"""


def summarize(transcript: str, provider: str = None) -> dict:
    provider = provider or os.getenv("LLM_PROVIDER", "openai"); prompt = PROMPT % transcript[:60000]
    if provider == "openai":
        from openai import OpenAI
        r = OpenAI().chat.completions.create(model="gpt-4o-mini", response_format={"type": "json_object"}, temperature=0, messages=[{"role": "user", "content": prompt}])
        text = r.choices[0].message.content
    elif provider == "anthropic":
        import anthropic
        r = anthropic.Anthropic().messages.create(model="claude-haiku-5-5", max_tokens=1500, messages=[{"role": "user", "content": prompt}])
        text = r.content[0].text
    else:                                                     # local model via Ollama's OpenAI-compatible API
        from openai import OpenAI
        r = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama").chat.completions.create(model="llama3.2", messages=[{"role": "user", "content": prompt}])
        text = r.choices[0].message.content
    return json.loads(text[text.find("{"): text.rfind("}") + 1])
'''),
   S("Measure transcription quality", "Word error rate against a human transcript. Normalise case and punctuation first or WER will be inflated.", "wer.py", '''
import re, sys, urllib.request
import jiwer
from transcribe import transcribe

norm = lambda s: re.sub(r"[^a-z0-9' ]", " ", s.lower()).split()
urllib.request.urlretrieve("https://raw.githubusercontent.com/openai/whisper/main/tests/jfk.flac", "jfk.flac")
ref = "And so my fellow Americans ask not what your country can do for you ask what you can do for your country"
hyp = transcribe(sys.argv[1] if len(sys.argv) > 1 else "jfk.flac")["text"]
print("hypothesis:", hyp); print("WER:", round(jiwer.wer(" ".join(norm(ref)), " ".join(norm(hyp))), 3))
'''),
   S("Gradio app", "", "app.py", '''
import gradio as gr
from summarize import summarize
from transcribe import transcribe


def run(audio, provider):
    t = transcribe(audio); s = summarize(t["text"], provider)
    items = "\\n".join(f"- [ ] {a['task']} — {a.get('owner') or 'unassigned'}" + (f" (due {a['due']})" if a.get("due") else "") for a in s.get("action_items", []))
    md = f"### Summary\\n{s.get('summary', '')}\\n\\n### Decisions\\n" + "\\n".join("- " + d for d in s.get("decisions", [])) + f"\\n\\n### Action items\\n{items}"
    return md, "\\n".join(f"[{x['start']:.0f}s] {x['text']}" for x in t["segments"])


gr.Interface(run, [gr.Audio(type="filepath"), gr.Radio(["openai", "anthropic", "ollama"], value="openai", label="LLM")],
             [gr.Markdown(), gr.Textbox(lines=15, label="Transcript")], title="Meeting notes").launch()
'''),
   S("Run it", "Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (Colab: Secrets), or install Ollama for a free local model.", None, "python wer.py\npython transcribe.py meeting.mp3\npython app.py", "bash"),
  ],
  verify="static",
  talk=["How Whisper works (log-mel encoder–decoder transformer, 30-second windows) and how chunking handles long audio.", "Evaluating ASR with WER; normalisation.", "Prompting for structured JSON and preventing invented owners/dates."],
  errors=[("ffmpeg not found", "install ffmpeg (Colab has it; Windows: winget install ffmpeg)"), ("JSONDecodeError from the LLM", "use JSON mode / lower temperature and extract the {...} block (done in summarize.py)")],
  extend=["Speaker diarisation with pyannote.audio (who said what)", "Translate Hindi meetings to English with task='translate'", "Store meetings and search them with RAG"],
  see=["m-speech-recognition", "m-speech-features", "m-llm-api", "m-prompt-engineering"])

PROJECTS_2 = [P8, P9, P10, P11, P12]
