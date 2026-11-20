"""End-to-end projects 27-31: deep-learning bench, sequence forecasting, planning & RL agent, vision toolkit, GNN citations."""
from ml_proj_util import P, S

SUNSPOTS = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-sunspots.csv"
TEMPS = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv"
HAAR = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
GI = "__pycache__/\n.venv/\ndata/\nruns/\n*.pt\n*.keras\n*.png\n.ipynb_checkpoints/\n"
FASHION = '''import gzip, os, urllib.request
import numpy as np

BASE = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
NAMES = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Boot"]


def _get(name, offset):
    os.makedirs("data", exist_ok=True); path = os.path.join("data", name)
    if not os.path.exists(path): urllib.request.urlretrieve(BASE + name, path)
    return np.frombuffer(gzip.open(path).read(), np.uint8, offset=offset)


def load(split="t10k", n=None):
    """split='train' (60k) or 't10k' (10k). Returns float32 images (N,1,28,28) in [0,1] and int64 labels."""
    X = _get(f"{split}-images-idx3-ubyte.gz", 16).reshape(-1, 1, 28, 28).astype(np.float32) / 255.0; y = _get(f"{split}-labels-idx1-ubyte.gz", 8).astype(np.int64)
    return (X[:n], y[:n]) if n else (X, y)
'''

# ---------------------------------------------------------------- P27
P27 = P("p-dl-bench", "Deep-learning fundamentals bench: perceptron → MLP → autoencoder, in PyTorch and Keras (Fashion-MNIST)", "dl", "Intermediate", "3–4 days", "Colab (GPU optional) or VS Code",
  "A reproducible experiment bench that answers the core deep-learning questions with real measurements: what a perceptron can and can't do, how depth/width, activations, losses, initialisation and normalisation change training, why deep sigmoid nets stop learning (gradient norms per layer), the same model in Keras, and a convolutional autoencoder for compression and anomaly detection.",
  ["`data.py`: cached Fashion-MNIST loader", "`nets.py`: configurable MLP factory (depth, width, activation, init, norm) + perceptron", "`bench.py`: experiment runner writing results.csv (`--quick` for CPU)",
   "`keras_model.py`: the same classifier in Keras 3 with callbacks", "`autoencoder.py`: conv autoencoder, reconstruction vs PCA, anomaly AUC", "`tests/`"],
  ["perceptron rule", "network formulation", "MLPs", "activations", "loss functions", "initialisation & normalisation", "vanishing/exploding gradients", "Keras API", "autoencoders"],
  "Fashion-MNIST (Zalando) from its GitHub repository.",
  ["loader", "network factory", "experiments", "gradient diagnostics", "Keras version", "autoencoder"],
  [
   S("Dependencies", "", "requirements.txt", "torch>=2.2\nkeras>=3.0\nnumpy>=1.26\npandas>=2.0\nscikit-learn>=1.4\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Data", "", "data.py", FASHION),
   S("Network factory", """One function builds every variant so experiments differ in exactly one setting. `Perceptron` implements Rosenblatt's update rule directly.""",
     "nets.py", '''
import math, numpy as np, torch, torch.nn as nn

ACTS = {"sigmoid": nn.Sigmoid, "tanh": nn.Tanh, "relu": nn.ReLU, "gelu": nn.GELU}


def mlp(depth=2, width=128, act="relu", init="default", norm=None, dropout=0.0):
    layers, d = [nn.Flatten()], 784
    for _ in range(depth):
        lin = nn.Linear(d, width)
        if init == "small": nn.init.normal_(lin.weight, 0, 0.01)
        elif init == "xavier": nn.init.xavier_normal_(lin.weight)
        elif init == "he": nn.init.kaiming_normal_(lin.weight, nonlinearity="relu")
        layers += [lin] + ([nn.BatchNorm1d(width)] if norm == "batch" else [nn.LayerNorm(width)] if norm == "layer" else []) + [ACTS[act]()] + ([nn.Dropout(dropout)] if dropout else []); d = width
    return nn.Sequential(*layers, nn.Linear(d, 10))


def grad_norms(model, X, y):
    model.zero_grad(); nn.functional.cross_entropy(model(X), y).backward()
    return [m.weight.grad.norm().item() for m in model if isinstance(m, nn.Linear)][:-1]


class Perceptron:
    def fit(self, X, y, epochs=20):
        X = X.reshape(len(X), -1); t = np.where(y > 0, 1, -1); self.w, self.b, self.mistakes = np.zeros(X.shape[1]), 0.0, []
        for _ in range(epochs):
            m = 0
            for i in np.random.default_rng(len(self.mistakes)).permutation(len(X)):
                if t[i] * (X[i] @ self.w + self.b) <= 0: self.w += t[i] * X[i]; self.b += t[i]; m += 1
            self.mistakes.append(m)
        return self

    def predict(self, X):
        return (X.reshape(len(X), -1) @ self.w + self.b > 0).astype(int)
'''),
   S("The experiment bench", """Each experiment trains with the same budget and seed and appends a row to `results.csv`. `--quick` uses 6,000 images and 2 epochs (CPU-friendly); without it, the full 60k training set.""",
     "bench.py", '''
import argparse, time, numpy as np, pandas as pd, torch, torch.nn as nn
from data import load
from nets import Perceptron, grad_norms, mlp


def train(model, X, y, epochs, loss="ce", lr=1e-3, opt="adam"):
    o = torch.optim.Adam(model.parameters(), lr) if opt == "adam" else torch.optim.SGD(model.parameters(), lr, momentum=0.9)
    for _ in range(epochs):
        model.train()
        for idx in torch.randperm(len(X)).split(128):
            out = model(X[idx])
            l = nn.functional.cross_entropy(out, y[idx]) if loss == "ce" else ((torch.softmax(out, 1) - nn.functional.one_hot(y[idx], 10).float()) ** 2).sum(1).mean()
            o.zero_grad(); l.backward(); o.step()
    return model


@torch.no_grad()
def accuracy(model, X, y): model.eval(); return (model(X).argmax(1) == y).float().mean().item()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--quick", action="store_true"); a = ap.parse_args()
    n, ep = (6000, 2) if a.quick else (None, 8); Xtr, ytr = load("train", n); Xte, yte = load("t10k", 2000)
    Xtr, ytr, Xte, yte = map(torch.tensor, (Xtr, ytr, Xte, yte)); rows = []
    def record(group, name, model, **kw):
        torch.manual_seed(0); t = time.time(); train(model, Xtr, ytr, ep, **kw); rows.append((group, name, accuracy(model, Xte, yte), time.time() - t)); print(f"  {group:12s} {name:24s} acc {rows[-1][2]:.3f}", flush=True)
    two = (ytr == 7) | (ytr == 9); p = Perceptron().fit(Xtr[two].numpy(), (ytr[two] == 9).numpy().astype(int), epochs=10)
    tt = (yte == 7) | (yte == 9); print(f"  perceptron sneaker vs boot: mistakes/epoch {p.mistakes[:5]}... test acc {(p.predict(Xte[tt].numpy()) == (yte[tt] == 9).numpy()).mean():.3f}")
    for d, w in [(0, 0), (1, 32), (1, 256), (3, 256)]:
        torch.manual_seed(0); record("capacity", f"depth {d} width {w}", nn.Sequential(nn.Flatten(), nn.Linear(784, 10)) if d == 0 else mlp(d, w))
    for act in ["sigmoid", "tanh", "relu", "gelu"]: torch.manual_seed(0); record("activation", f"6 layers {act}", mlp(6, 128, act), opt="sgd", lr=0.05)
    for loss in ["ce", "mse"]: torch.manual_seed(0); record("loss", "cross-entropy" if loss == "ce" else "MSE on softmax", mlp(2, 128), loss=loss, opt="sgd", lr=0.1)
    for init, norm in [("small", None), ("xavier", None), ("he", None), ("small", "batch"), ("small", "layer")]:
        torch.manual_seed(0); record("init/norm", f"{init} init, {norm or 'no'} norm", mlp(8, 128, "relu", init, norm), opt="sgd", lr=0.05)
    for act in ["sigmoid", "relu"]:
        torch.manual_seed(0); g = grad_norms(mlp(10, 64, act, "xavier" if act == "sigmoid" else "he"), Xtr[:256], ytr[:256]); print(f"  gradient norm per layer ({act}, 10 layers): first {g[0]:.1e} ... last {g[-1]:.1e}")
    pd.DataFrame(rows, columns=["experiment", "setting", "accuracy", "seconds"]).to_csv("results.csv", index=False); print("wrote results.csv")


if __name__ == "__main__":
    main()
'''),
   S("The same classifier in Keras", "", "keras_model.py", '''
import os, sys
os.environ.setdefault("KERAS_BACKEND", "torch")
import keras, numpy as np
from keras import layers
from data import load

quick = "--quick" in sys.argv; n = 6000 if quick else None
Xtr, ytr = load("train", n); Xte, yte = load("t10k", 2000); Xtr, Xte = Xtr.transpose(0, 2, 3, 1), Xte.transpose(0, 2, 3, 1); keras.utils.set_random_seed(0)
model = keras.Sequential([keras.Input((28, 28, 1)), layers.Conv2D(32, 3, activation="relu", padding="same"), layers.MaxPooling2D(), layers.Conv2D(64, 3, activation="relu", padding="same"),
                          layers.MaxPooling2D(), layers.Flatten(), layers.Dropout(0.3), layers.Dense(128, activation="relu"), layers.Dense(10, activation="softmax")])
model.compile(optimizer=keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
cbs = [keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True), keras.callbacks.ReduceLROnPlateau(patience=1, factor=0.5)]
h = model.fit(Xtr, ytr, validation_split=0.1, epochs=2 if quick else 15, batch_size=128, callbacks=cbs, verbose=0)
print(f"Keras CNN: {model.count_params():,} params | epochs {len(h.history['loss'])} | test accuracy {model.evaluate(Xte, yte, verbose=0)[1]:.3f}")
model.save("data/fashion_cnn.keras"); print("saved data/fashion_cnn.keras")
'''),
   S("Convolutional autoencoder", """Compress each image to 32 numbers and rebuild it. Compare with PCA at the same size; then train only on clothing and use reconstruction error to flag shoes and bags as anomalies.""",
     "autoencoder.py", '''
import sys, numpy as np, torch, torch.nn as nn
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score
from data import load


class AE(nn.Module):
    def __init__(self, k=32):
        super().__init__()
        self.enc = nn.Sequential(nn.Conv2d(1, 16, 3, 2, 1), nn.ReLU(), nn.Conv2d(16, 32, 3, 2, 1), nn.ReLU(), nn.Flatten(), nn.Linear(32 * 49, k))
        self.dec = nn.Sequential(nn.Linear(k, 32 * 49), nn.ReLU(), nn.Unflatten(1, (32, 7, 7)), nn.ConvTranspose2d(32, 16, 4, 2, 1), nn.ReLU(), nn.ConvTranspose2d(16, 1, 4, 2, 1), nn.Sigmoid())

    def forward(self, x):
        return self.dec(self.enc(x))


def fit(X, epochs):
    torch.manual_seed(0); m = AE(); o = torch.optim.Adam(m.parameters(), 2e-3)
    for _ in range(epochs):
        for idx in torch.randperm(len(X)).split(128): o.zero_grad(); nn.functional.mse_loss(m(X[idx]), X[idx]).backward(); o.step()
    return m.eval()


if __name__ == "__main__":
    quick = "--quick" in sys.argv; Xtr, ytr = load("train", 6000 if quick else 30000); Xte, yte = load("t10k", 2000); ep = 3 if quick else 10
    Xtr_t, Xte_t = torch.tensor(Xtr), torch.tensor(Xte); ae = fit(Xtr_t, ep)
    with torch.no_grad(): err_ae = ((ae(Xte_t) - Xte_t) ** 2).mean().item()
    pca = PCA(32).fit(Xtr.reshape(len(Xtr), -1)); R = pca.inverse_transform(pca.transform(Xte.reshape(len(Xte), -1))); print(f"32-number code: autoencoder MSE {err_ae:.4f} | PCA MSE {((R - Xte.reshape(len(Xte), -1)) ** 2).mean():.4f}")
    clothes = np.isin(ytr, [0, 1, 2, 3, 4, 6]); m = fit(Xtr_t[clothes], ep)
    with torch.no_grad(): e = ((m(Xte_t) - Xte_t) ** 2).mean((1, 2, 3)).numpy()
    print(f"anomaly detection (shoes/bags never seen): AUC {roc_auc_score(~np.isin(yte, [0, 1, 2, 3, 4, 6]), e):.3f}")
'''),
   S("Tests", "", "tests/test_bench.py", '''
import numpy as np, torch
from nets import Perceptron, grad_norms, mlp


def test_mlp_shapes_and_params():
    m = mlp(2, 64); assert m(torch.zeros(5, 1, 28, 28)).shape == (5, 10) and sum(p.numel() for p in m.parameters()) == 784 * 64 + 64 + 64 * 64 + 64 + 64 * 10 + 10


def test_sigmoid_gradients_vanish_more_than_relu():
    torch.manual_seed(0); X, y = torch.rand(64, 1, 28, 28), torch.randint(0, 10, (64,))
    gs, gr = grad_norms(mlp(10, 64, "sigmoid", "xavier"), X, y), grad_norms(mlp(10, 64, "relu", "he"), X, y); assert gs[0] / gs[-1] < gr[0] / gr[-1]


def test_perceptron_learns_separable_data():
    rng = np.random.default_rng(0); X = rng.normal(size=(200, 1, 2, 2)); y = (X.reshape(200, -1).sum(1) > 0).astype(int)
    p = Perceptron().fit(X, y, epochs=30); assert (p.predict(X) == y).mean() == 1.0
'''),
   S("Run it", "", None, "python bench.py --quick      # drop --quick on a GPU for the full study\npython keras_model.py --quick\npython autoencoder.py --quick\npytest -q", "bash"),
  ],
  check=["python bench.py --quick", "KERAS_BACKEND=torch python keras_model.py --quick", "python autoencoder.py --quick", "pytest -q"],
  talk=["Which single change (activation, init, normalisation) had the biggest effect, and why.", "How you showed vanishing gradients with numbers, not just a story.", "PyTorch vs Keras: what each makes easy.", "Why the autoencoder beats PCA at the same code size, and how it detects anomalies."],
  errors=[("Keras: No module named tensorflow", "set KERAS_BACKEND=torch before importing keras"), ("MSE loss trains slowly", "expected — softmax saturates; that's the lesson")],
  extend=["Add a learning-rate finder", "Log experiments to MLflow", "Replace the autoencoder with a VAE and sample new images"],
  see=["m-dl-intro", "m-nn-formulation", "m-perceptron", "m-mlp", "m-activations", "m-loss-functions", "m-init-norm", "m-vanishing", "m-keras", "m-autoencoder", "m-pytorch"])

# ---------------------------------------------------------------- P28
P28 = P("p-seq-forecast", "Sequence models for forecasting: RNN, LSTM and an attention seq2seq (temperatures & sunspots)", "dl", "Advanced", "3 days", "Colab or VS Code (CPU is fine)",
  "Forecast two real series with sequence models and an honest backtest: next-day Melbourne temperatures with a vanilla RNN vs LSTM vs GRU (and the gradient-through-time diagnostic), and 24-month sunspot forecasts with an encoder–decoder GRU with attention, teacher forcing during training and autoregressive decoding at test time — all compared with seasonal baselines.",
  ["`series.py`: download, scale (train-only statistics), windowing", "`models.py`: RNN/LSTM/GRU forecaster and Seq2Seq with dot-product attention", "`next_day.py`: walk-forward evaluation of next-day forecasts",
   "`multi_step.py`: 24-month sunspot forecasts, teacher forcing vs autoregressive", "`tests/`"],
  ["sequence windows without leakage", "BPTT and gradient flow", "RNN vs LSTM vs GRU", "encoder–decoder", "attention", "teacher forcing / exposure bias", "baselines"],
  "Daily minimum temperatures in Melbourne (1981–1990) and monthly sunspot numbers (1749–1983) from Jason Brownlee's datasets repository.",
  ["data + windows", "next-day models", "gradient diagnostic", "seq2seq", "attention", "backtest vs baselines"],
  [
   S("Dependencies", "", "requirements.txt", "torch>=2.2\nnumpy>=1.26\npandas>=2.0\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Series and windows", "", "series.py", f'''
import numpy as np, pandas as pd

TEMPS, SUNSPOTS = "{TEMPS}", "{SUNSPOTS}"


def load(which):
    if which == "temps":
        s = pd.read_csv(TEMPS, parse_dates=["Date"]).set_index("Date")["Temp"].astype(float); return s, (s.index < "1989-01-01").sum()
    s = pd.read_csv(SUNSPOTS)["Sunspots"].astype(float); return np.sqrt(s), 2200          # sqrt stabilises the variance of counts


def windows(z, n_in, n_out, start=0):
    idx = np.arange(start, len(z) - n_in - n_out + 1); X = np.stack([z[i:i + n_in] for i in idx]); Y = np.stack([z[i + n_in:i + n_in + n_out] for i in idx]); return X, Y, idx


def scaler(train_values):
    mu, sd = float(np.mean(train_values)), float(np.std(train_values)); return (lambda v: (np.asarray(v) - mu) / sd), (lambda v: np.asarray(v) * sd + mu)
'''),
   S("Models", "", "models.py", '''
import torch, torch.nn as nn


class Forecaster(nn.Module):
    def __init__(self, kind="LSTM", hidden=64, out=1):
        super().__init__(); self.rnn = getattr(nn, kind)(1, hidden, batch_first=True); self.head = nn.Linear(hidden, out)
        if kind == "LSTM":
            for name, p in self.rnn.named_parameters():
                if "bias" in name: p.data[hidden:2 * hidden] = 1.0                     # forget-gate bias = 1

    def forward(self, x):
        o, _ = self.rnn(x.unsqueeze(-1)); return self.head(o[:, -1])


class Seq2Seq(nn.Module):
    def __init__(self, hidden=64, attention=True):
        super().__init__(); self.enc = nn.GRU(1, hidden, batch_first=True); self.dec = nn.GRUCell(1, hidden); self.attn = attention; self.out = nn.Linear(2 * hidden if attention else hidden, 1)

    def forward(self, x, n_out, y=None):
        H, h = self.enc(x.unsqueeze(-1)); h, prev, outs, weights = h[0], x[:, -1:], [], []
        for t in range(n_out):
            h = self.dec(prev, h); feat = h
            if self.attn:
                a = torch.softmax((H @ h.unsqueeze(2)).squeeze(2) / H.shape[-1] ** 0.5, 1); weights.append(a); feat = torch.cat([h, (a.unsqueeze(2) * H).sum(1)], 1)
            o = self.out(feat); outs.append(o); prev = y[:, t:t + 1] if y is not None else o           # teacher forcing only when y is given
        return torch.cat(outs, 1), (torch.stack(weights, 1) if weights else None)


def fit(model, X, Y, epochs=10, lr=3e-3, seq2seq=False):
    torch.manual_seed(0); opt = torch.optim.Adam(model.parameters(), lr); X, Y = torch.tensor(X, dtype=torch.float32), torch.tensor(Y, dtype=torch.float32)
    for _ in range(epochs):
        for b in torch.randperm(len(X)).split(64):
            pred = model(X[b], Y.shape[1], Y[b])[0] if seq2seq else model(X[b]); loss = nn.functional.mse_loss(pred, Y[b])
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    return model.eval()
'''),
   S("Next-day temperature forecasts", "", "next_day.py", '''
import sys, numpy as np, torch
from models import Forecaster, fit
from series import load, scaler, windows

if __name__ == "__main__":
    epochs = 4 if "--quick" in sys.argv else 15; s, cut = load("temps"); fwd, back = scaler(s.iloc[:cut]); z = fwd(s.to_numpy()); W = 30
    X, Y, idx = windows(z, W, 1); tr = idx + W < cut; te = ~tr; truth = back(Y[te, 0])
    print(f"persistence (yesterday) MAE {np.abs(back(X[te, -1]) - truth).mean():.2f} °C")
    clim = s.iloc[:cut].groupby(s.index[:cut].dayofyear).mean(); print(f"climatology MAE {np.abs(clim.reindex(s.index[idx[te] + W].dayofyear).to_numpy() - truth).mean():.2f} °C")
    for kind in ["RNN", "LSTM", "GRU"]:
        m = fit(Forecaster(kind), X[tr], Y[tr], epochs)
        with torch.no_grad(): p = back(m(torch.tensor(X[te], dtype=torch.float32))[:, 0].numpy())
        x = torch.tensor(X[te][:16], dtype=torch.float32, requires_grad=True); m(x).sum().backward(); g = x.grad.abs().mean(0).numpy()
        print(f"  {kind:4s} MAE {np.abs(p - truth).mean():.2f} °C | input sensitivity 1 vs 29 days back: {g[-1]:.1e} vs {g[0]:.1e}")
'''),
   S("Multi-step sunspot forecasts with attention", "", "multi_step.py", '''
import sys, numpy as np, torch
from models import Seq2Seq, fit
from series import load, scaler, windows

if __name__ == "__main__":
    epochs = 3 if "--quick" in sys.argv else 15; s, cut = load("sunspots"); fwd, back = scaler(s[:cut]); z = fwd(s.to_numpy()); IN, OUT = 144, 24
    X, Y, idx = windows(z, IN, OUT); tr = idx + IN + OUT <= cut; te = (idx >= cut - IN) & (np.arange(len(idx)) % 6 == 0)
    real = lambda a: back(a) ** 2; truth = real(Y[te])
    print(f"baselines: repeat last value MAE {np.abs(real(np.repeat(X[te, -1:], OUT, 1)) - truth).mean():.1f} | repeat 11-year cycle MAE {np.abs(real(X[te, IN - 132:IN - 132 + OUT]) - truth).mean():.1f}")
    for att in [False, True]:
        m = fit(Seq2Seq(attention=att), X[tr], Y[tr], epochs, seq2seq=True); xt = torch.tensor(X[te], dtype=torch.float32)
        with torch.no_grad(): auto, w = m(xt, OUT); tf, _ = m(xt, OUT, torch.tensor(Y[te], dtype=torch.float32))
        print(f"  seq2seq{' + attention' if att else '            '} MAE autoregressive {np.abs(real(auto.numpy()) - truth).mean():.1f} | teacher-forced (optimistic) {np.abs(real(tf.numpy()) - truth).mean():.1f}")
    print("most-attended input months (months back):", (IN - np.argsort(-w.mean((0, 1)).numpy())[:5]).tolist())
'''),
   S("Tests", "", "tests/test_seq.py", '''
import numpy as np, torch
from models import Forecaster, Seq2Seq
from series import scaler, windows


def test_windows_never_overlap_the_target():
    X, Y, idx = windows(np.arange(20.0), 5, 2); assert (X[:, -1] + 1 == Y[:, 0]).all() and X.shape == (14, 5)


def test_scaler_round_trip():
    f, b = scaler([1.0, 2.0, 3.0]); assert np.allclose(b(f([5.0, 7.0])), [5.0, 7.0])


def test_shapes_and_teacher_forcing_switch():
    m = Seq2Seq(16); x, y = torch.randn(3, 20), torch.randn(3, 4); out_tf, w = m(x, 4, y); out_ar, _ = m(x, 4)
    assert out_tf.shape == (3, 4) and w.shape == (3, 4, 20) and not torch.allclose(out_tf, out_ar)
    assert Forecaster("GRU")(x).shape == (3, 1)
'''),
   S("Run it", "", None, "python next_day.py\npython multi_step.py\npytest -q", "bash"),
  ],
  check=["python next_day.py --quick", "python multi_step.py --quick", "pytest -q"],
  talk=["How your windows avoid leakage and why scaling uses training statistics only.", "Why teacher-forced error is optimistic (exposure bias).", "What the attention weights focused on and whether that makes physical sense (11-year cycle)."],
  errors=[("Model predicts a flat line", "learning rate or epochs too low; check scaling"), ("Great validation, bad future", "you shuffled across time — split by date")],
  extend=["Add a Temporal Fusion Transformer or N-BEATS via darts/neuralforecast", "Quantile outputs for intervals", "Scheduled sampling to reduce exposure bias"],
  see=["m-rnn", "m-lstm-gru", "m-seq2seq", "m-time-series", "m-ts-dl", "m-attention"])

# ---------------------------------------------------------------- P29
P29 = P("p-planning-agent", "Warehouse robot: search, planning and reinforcement learning on a grid world", "gen", "Intermediate", "2–3 days", "VS Code or Colab (CPU)",
  "A delivery robot must reach pick-up points in a warehouse map. Solve it four ways and compare: uninformed search (BFS), informed search (A* with an admissible heuristic), dynamic programming with a known model (value iteration on a slippery floor), and model-free learning (Q-learning vs SARSA) — then a bandit chooses which charging station to use. A small tour of how 'AI' spans symbolic search and learning.",
  ["`world.py`: warehouse map, moves, rewards, slip probability", "`search.py`: BFS and A* with node counts", "`dp.py`: value iteration with the known transition model", "`rl.py`: Q-learning and SARSA with ε-greedy", "`bandit.py`: ε-greedy vs UCB vs Thompson", "`compare.py`: one table", "`tests/`"],
  ["state spaces", "BFS vs A*", "admissible heuristics", "MDPs and Bellman equations", "value iteration", "Q-learning vs SARSA", "exploration", "bandits", "symbolic vs learning AI"],
  "A hand-designed warehouse map (in the code) — no download needed.",
  ["world", "search", "planning", "learning", "bandit", "comparison"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\npandas>=2.0\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("The warehouse world", "", "world.py", '''
import numpy as np

MAP = """
S . . . # . . . . .
. # # . # . # # # .
. # . . . . . . # .
. # . # # # # . # .
. . . . . . # . . .
# # # # . . # # # .
. . . . . # . . . .
. # # # . # . # # .
. . . # . . . # G .
""".split("\\n")[1:-1]
GRID = np.array([row.split() for row in MAP]); H, W = GRID.shape
START, GOAL = tuple(np.argwhere(GRID == "S")[0]), tuple(np.argwhere(GRID == "G")[0])
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]; ARROWS = "↑→↓←"


def free(r, c): return 0 <= r < H and 0 <= c < W and GRID[r, c] != "#"


def neighbours(s):
    for dr, dc in MOVES:
        if free(s[0] + dr, s[1] + dc): yield (s[0] + dr, s[1] + dc)


class Env:
    """Each step costs -1; reaching G gives +20. With probability `slip` the robot moves sideways."""

    def __init__(self, slip=0.0, seed=0):
        self.slip, self.rng = slip, np.random.default_rng(seed); self.states = [(r, c) for r in range(H) for c in range(W) if free(r, c)]

    def transitions(self, s, a):
        if s == GOAL: return [(1.0, s, 0.0, True)]
        out = []
        for prob, move in [(1 - self.slip, a), (self.slip / 2, (a + 1) % 4), (self.slip / 2, (a + 3) % 4)]:
            if prob == 0: continue
            n = (s[0] + MOVES[move][0], s[1] + MOVES[move][1]); n = n if free(*n) else s
            out.append((prob, n, 20.0 if n == GOAL else -1.0, n == GOAL))
        return out

    def step(self, s, a):
        t = self.transitions(s, a); i = self.rng.choice(len(t), p=[p for p, *_ in t]); _, n, r, done = t[i]; return n, r, done
'''),
   S("Search: BFS vs A*", "", "search.py", '''
import heapq
from collections import deque
from world import GOAL, START, neighbours


def bfs(start=START, goal=GOAL):
    parent, q, expanded = {start: None}, deque([start]), 0
    while q:
        s = q.popleft(); expanded += 1
        if s == goal: break
        for n in neighbours(s):
            if n not in parent: parent[n] = s; q.append(n)
    return path(parent, goal), expanded


def manhattan(s, goal=GOAL): return abs(s[0] - goal[0]) + abs(s[1] - goal[1])      # admissible: never overestimates on a grid


def astar(start=START, goal=GOAL, h=manhattan):
    g, parent, pq, expanded = {start: 0}, {start: None}, [(h(start), start)], 0
    while pq:
        _, s = heapq.heappop(pq); expanded += 1
        if s == goal: break
        for n in neighbours(s):
            if g[s] + 1 < g.get(n, 1e9): g[n] = g[s] + 1; parent[n] = s; heapq.heappush(pq, (g[n] + h(n), n))
    return path(parent, goal), expanded


def path(parent, goal):
    out, s = [], goal
    while s is not None: out.append(s); s = parent[s]
    return out[::-1]


if __name__ == "__main__":
    for name, fn in [("BFS", bfs), ("A* (Manhattan)", astar), ("A* (h=0, i.e. Dijkstra)", lambda: astar(h=lambda s: 0))]:
        p, n = fn(); print(f"  {name:24s} path length {len(p) - 1} | nodes expanded {n}")
'''),
   S("Planning with a known model: value iteration", "", "dp.py", '''
import numpy as np
from world import ARROWS, GOAL, GRID, START, Env


def value_iteration(env, gamma=0.95, tol=1e-8):
    V = {s: 0.0 for s in env.states}
    for sweep in range(1000):
        delta = 0
        for s in env.states:
            best = max(sum(p * (r + gamma * V[n] * (not d)) for p, n, r, d in env.transitions(s, a)) for a in range(4)); delta = max(delta, abs(best - V[s])); V[s] = best
        if delta < tol: break
    policy = {s: int(np.argmax([sum(p * (r + gamma * V[n] * (not d)) for p, n, r, d in env.transitions(s, a)) for a in range(4)])) for s in env.states}
    return V, policy, sweep


def show(policy):
    g = GRID.copy()
    for s, a in policy.items():
        if s != GOAL and GRID[s] != "S": g[s] = ARROWS[a]
    return "\\n".join(" ".join(r) for r in g)


if __name__ == "__main__":
    for slip in [0.0, 0.2]:
        V, pi, sweeps = value_iteration(Env(slip)); print(f"slip {slip}: converged in {sweeps} sweeps, V(start) = {V[START]:.2f}\\n{show(pi)}\\n")
'''),
   S("Learning without a model: Q-learning vs SARSA", "", "rl.py", '''
import numpy as np
from world import GOAL, START, Env


def learn(method="q", episodes=3000, alpha=0.2, gamma=0.95, eps=0.2, slip=0.2, seed=0):
    env, rng = Env(slip, seed), np.random.default_rng(seed); Q = {s: np.zeros(4) for s in env.states}; returns = []
    act = lambda s: int(rng.integers(4)) if rng.random() < eps else int(Q[s].argmax())
    for ep in range(episodes):
        s, a, G = START, act(START), 0.0
        for t in range(200):
            n, r, done = env.step(s, a); a2 = act(n); G += r
            target = r + (0 if done else gamma * (Q[n].max() if method == "q" else Q[n][a2])); Q[s][a] += alpha * (target - Q[s][a]); s, a = n, a2
            if done: break
        returns.append(G)
    return Q, np.array(returns)


def evaluate(Q, slip=0.2, runs=500, max_steps=60):
    """Mean return and the share of runs that reach G within `max_steps` moves."""
    env, total, reached = Env(slip, 123), [], []
    for _ in range(runs):
        s, G, done = START, 0.0, False
        for t in range(max_steps):
            s, r, done = env.step(s, int(Q[s].argmax())); G += r
            if done: break
        total.append(G); reached.append(done)
    return float(np.mean(total)), float(np.mean(reached))


if __name__ == "__main__":
    for m in ["q", "sarsa"]:
        Q, R = learn(m); print(f"  {'Q-learning' if m == 'q' else 'SARSA':10s} return while learning (last 300) {R[-300:].mean():6.2f} | greedy policy: mean return {evaluate(Q)[0]:.2f}, success {evaluate(Q)[1]:.0%}")
'''),
   S("Bandit: which charging station?", "", "bandit.py", '''
import numpy as np

P_FAST = np.array([0.55, 0.62, 0.48, 0.70])        # probability each station has a free fast charger (unknown to the robot)


def run(strategy, T=5000, seed=0):
    rng = np.random.default_rng(seed); wins, n, regret = np.zeros(4), np.zeros(4), 0.0
    for t in range(1, T + 1):
        if strategy == "epsilon": a = int(rng.integers(4)) if rng.random() < 0.1 else int(np.argmax(wins / np.maximum(n, 1)))
        elif strategy == "ucb": a = int(np.argmax(np.where(n == 0, np.inf, wins / np.maximum(n, 1) + np.sqrt(2 * np.log(t) / np.maximum(n, 1)))))
        else: a = int(np.argmax(rng.beta(1 + wins, 1 + n - wins)))
        r = rng.random() < P_FAST[a]; wins[a] += r; n[a] += 1; regret += P_FAST.max() - P_FAST[a]
    return regret, n.astype(int)


if __name__ == "__main__":
    for s in ["epsilon", "ucb", "thompson"]: r, n = run(s); print(f"  {s:9s} regret {r:6.1f} | visits per station {n.tolist()}")
'''),
   S("One comparison table", "", "compare.py", '''
from dp import value_iteration
from rl import evaluate, learn
from search import astar, bfs
from world import Env

if __name__ == "__main__":
    p_b, n_b = bfs(); p_a, n_a = astar(); _, pi, _ = value_iteration(Env(0.2)); Q, _ = learn("q")
    import numpy as np
    Qpi = {s: np.eye(4)[a] for s, a in pi.items()}
    rows = [("BFS (symbolic search)", f"optimal length {len(p_b) - 1}", f"{n_b} nodes", "needs the map"), ("A* (heuristic search)", f"optimal length {len(p_a) - 1}", f"{n_a} nodes", "needs the map + heuristic"),
            ("value iteration (planning)", f"success {evaluate(Qpi)[1]:.0%} on slippery floor", "all states x sweeps", "needs the transition model"),
            ("Q-learning (RL)", f"success {evaluate(Q)[1]:.0%} on slippery floor", "3000 episodes", "learns from experience only")]
    for r in rows: print(f"  {r[0]:28s} | {r[1]:34s} | {r[2]:20s} | {r[3]}")
'''),
   S("Tests", "", "tests/test_agent.py", '''
from dp import value_iteration
from search import astar, bfs, manhattan
from world import GOAL, START, Env


def test_astar_matches_bfs_and_expands_fewer_nodes():
    (pb, nb), (pa, na) = bfs(), astar(); assert len(pb) == len(pa) and na <= nb and pa[0] == START and pa[-1] == GOAL


def test_heuristic_is_admissible():
    for s in Env().states:
        p, _ = astar(start=s); assert manhattan(s) <= len(p) - 1


def test_value_iteration_reaches_goal_deterministically():
    V, pi, _ = value_iteration(Env(0.0)); s, steps = START, 0; env = Env(0.0)
    while s != GOAL and steps < 100: s, _, _ = env.step(s, pi[s]); steps += 1
    assert s == GOAL and steps == len(astar()[0]) - 1
'''),
   S("Run it", "", None, "python search.py\npython dp.py\npython rl.py\npython bandit.py\npython compare.py\npytest -q", "bash"),
  ],
  check=["python search.py", "python dp.py", "python rl.py", "python bandit.py", "python compare.py", "pytest -q"],
  talk=["Why A* with Manhattan distance is optimal here and expands fewer nodes.", "What changes when the floor is slippery (stochastic transitions) and why search no longer suffices.", "Q-learning vs SARSA, and exploration in bandits."],
  errors=[("Q-learning never reaches G", "episodes too short or ε too small — raise exploration"), ("A* returns a longer path", "your heuristic overestimates (not admissible)")],
  extend=["Add Gymnasium's FrozenLake/CliffWalking", "Deep Q-network for a larger map", "Multi-robot planning with reservations"],
  see=["m-ai-overview", "m-ml-types", "m-search-ai", "m-rl-basics"])

# ---------------------------------------------------------------- P30
P30 = P("p-vision-toolkit", "Classical + generative vision toolkit: segmentation, faces, super-resolution and a GAN", "cv", "Advanced", "3–4 days", "Colab (GPU recommended) or VS Code",
  "Four mini-apps that cover the rest of computer vision: classical segmentation and measurement (coins), face detection with an optional emotion classifier (responsible-use notes included), single-image super-resolution (ESPCN with PixelShuffle, PSNR/SSIM), and a DCGAN that generates clothing images with a diversity check.",
  ["`segment.py`: Otsu + morphology + watershed, object counts and sizes", "`faces.py`: Haar-cascade detection + optional HF emotion model (`--smoke` skips the download)",
   "`superres.py`: ESPCN trained on real photos; PSNR/SSIM vs bicubic", "`gan.py`: DCGAN on Fashion-MNIST; losses, samples, diversity", "`tests/`"],
  ["image arrays, colour, filters", "thresholding, morphology, watershed", "face detection pipeline", "emotion recognition and its limits", "super-resolution, PSNR/SSIM", "GAN training dynamics"],
  "scikit-image sample photos (coins, astronaut, coffee, …), OpenCV's Haar cascade, Fashion-MNIST.",
  ["segmentation", "faces", "super-resolution", "GAN"],
  [
   S("Dependencies", "", "requirements.txt", "numpy>=1.26\nscipy>=1.11\nscikit-image>=0.22\nopencv-python>=4.8\ntorch>=2.2\ntransformers>=4.40\npillow>=10.0\nmatplotlib>=3.8\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("Data", "", "data.py", FASHION),
   S("Segmentation and measurement", "", "segment.py", '''
import numpy as np
from scipy import ndimage as ndi
from skimage import data, filters, measure, morphology, segmentation
from skimage.feature import peak_local_max


def segment_coins(img=None):
    img = data.coins() if img is None else img; t = filters.threshold_otsu(img)
    mask = morphology.remove_small_objects(ndi.binary_fill_holes(morphology.opening(img > t, morphology.disk(2))), 100)
    dist = ndi.distance_transform_edt(mask); lab = measure.label(mask); peaks = peak_local_max(dist, min_distance=12, labels=lab)
    markers = np.zeros_like(lab); markers[tuple(peaks.T)] = np.arange(1, len(peaks) + 1)
    return segmentation.watershed(-dist, markers, mask=mask), t


def dice(a, b): return 2 * (a & b).sum() / (a.sum() + b.sum() + 1e-9)


if __name__ == "__main__":
    ws, t = segment_coins(); props = measure.regionprops(ws); areas = np.array([p.area for p in props])
    print(f"Otsu threshold {t:.0f} | coins found {ws.max()} | area median {np.median(areas):.0f}px (range {areas.min()}-{areas.max()})")
    big = areas > np.median(areas) * 1.3; print(f"large coins: {big.sum()} | small coins: {(~big).sum()}")
'''),
   S("Face detection and (optional) emotion", """Detection is classical (Haar cascade). Emotion classification uses a pretrained ViT from Hugging Face — **read the limitations**: expressions are not feelings, accuracy varies across groups, and the EU AI Act bans emotion recognition at work and in schools.""",
     "faces.py", f'''
import os, sys, urllib.request, cv2, numpy as np
from skimage import data

HAAR = "{HAAR}"


def detect(rgb):
    if not os.path.exists("data/haar.xml"): os.makedirs("data", exist_ok=True); urllib.request.urlretrieve(HAAR, "data/haar.xml")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY); return cv2.CascadeClassifier("data/haar.xml").detectMultiScale(gray, 1.1, 5, minSize=(60, 60))


def crop(rgb, box, pad=0.2):
    x, y, w, h = box; p = int(pad * w); return rgb[max(0, y - p):y + h + p, max(0, x - p):x + w + p]


if __name__ == "__main__":
    img = data.astronaut(); faces = detect(img); print("faces:", [tuple(int(v) for v in f) for f in faces])
    face = crop(img, max(faces, key=lambda f: f[2] * f[3])); print("face crop:", face.shape)
    if "--smoke" in sys.argv:
        print("smoke mode: skipping the emotion model download")
    else:
        from PIL import Image
        from transformers import pipeline
        clf = pipeline("image-classification", model="trpakov/vit-face-expression")
        for p in clf(Image.fromarray(face), top_k=3): print(f"  {{p['label']:9s}} {{p['score']:.2f}}")
        print("A model's guess about one facial expression — not a measurement of feelings. Do not use for decisions about people.")
'''),
   S("Super-resolution", "", "superres.py", '''
import sys, cv2, numpy as np, torch, torch.nn as nn
from skimage import data
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim

to_y = lambda im: cv2.cvtColor(im, cv2.COLOR_RGB2YCrCb)[..., 0] if im.ndim == 3 else im


def pair(hr):
    hr = hr[:hr.shape[0] // 2 * 2, :hr.shape[1] // 2 * 2]; return cv2.resize(hr, (hr.shape[1] // 2, hr.shape[0] // 2), interpolation=cv2.INTER_AREA), hr


class ESPCN(nn.Module):
    def __init__(self):
        super().__init__(); self.f = nn.Sequential(nn.Conv2d(1, 64, 5, padding=2), nn.Tanh(), nn.Conv2d(64, 32, 3, padding=1), nn.Tanh(), nn.Conv2d(32, 4, 3, padding=1), nn.PixelShuffle(2))

    def forward(self, lr):
        return nn.functional.interpolate(lr, scale_factor=2, mode="bicubic") + self.f(lr)


def patches(images, n=300, s=24, seed=0):
    rng = np.random.default_rng(seed); L, H = [], []
    for im in images:
        lr, hr = pair(im)
        for _ in range(n):
            y, x = rng.integers(0, lr.shape[0] - s), rng.integers(0, lr.shape[1] - s); L.append(lr[y:y + s, x:x + s]); H.append(hr[2 * y:2 * y + 2 * s, 2 * x:2 * x + 2 * s])
    return (torch.tensor(np.array(a)[:, None], dtype=torch.float32) / 255 for a in (L, H))


if __name__ == "__main__":
    epochs = 3 if "--smoke" in sys.argv else 20; train_imgs = [to_y(getattr(data, n)()) for n in ["astronaut", "coffee", "chelsea", "rocket", "camera"]]; lr_t, hr_t = pair(to_y(data.immunohistochemistry()))
    L, H = patches(train_imgs); torch.manual_seed(0); m = ESPCN(); opt = torch.optim.Adam(m.parameters(), 1e-3)
    for _ in range(epochs):
        for idx in torch.randperm(len(L)).split(32): opt.zero_grad(); nn.functional.l1_loss(m(L[idx]), H[idx]).backward(); opt.step()
    with torch.no_grad(): out = (m(torch.tensor(lr_t, dtype=torch.float32)[None, None] / 255)[0, 0].clamp(0, 1) * 255).numpy().astype(np.uint8)
    bic = cv2.resize(lr_t, hr_t.shape[::-1], interpolation=cv2.INTER_CUBIC)
    for name, im in [("bicubic", bic), ("ESPCN", out)]: print(f"  {name:8s} PSNR {psnr(hr_t, im, data_range=255):.2f} dB | SSIM {ssim(hr_t, im, data_range=255):.3f}")
'''),
   S("DCGAN", "", "gan.py", '''
import sys, numpy as np, torch, torch.nn as nn
from data import load

Z = 64


def nets():
    G = nn.Sequential(nn.Linear(Z, 128 * 49), nn.BatchNorm1d(128 * 49), nn.ReLU(), nn.Unflatten(1, (128, 7, 7)), nn.ConvTranspose2d(128, 64, 4, 2, 1), nn.BatchNorm2d(64), nn.ReLU(), nn.ConvTranspose2d(64, 1, 4, 2, 1), nn.Tanh())
    D = nn.Sequential(nn.Conv2d(1, 64, 4, 2, 1), nn.LeakyReLU(0.2), nn.Conv2d(64, 128, 4, 2, 1), nn.BatchNorm2d(128), nn.LeakyReLU(0.2), nn.Flatten(), nn.Linear(128 * 49, 1))
    return G, D


def train(real, epochs):
    torch.manual_seed(0); G, D = nets(); oG, oD = (torch.optim.Adam(m.parameters(), 2e-4, betas=(0.5, 0.999)) for m in (G, D)); bce = nn.functional.binary_cross_entropy_with_logits
    for ep in range(epochs):
        for idx in torch.randperm(len(real)).split(128):
            fake = G(torch.randn(len(idx), Z)); dr, df = D(real[idx]), D(fake.detach())
            lD = bce(dr, torch.full_like(dr, 0.9)) + bce(df, torch.zeros_like(df)); oD.zero_grad(); lD.backward(); oD.step()
            g = D(fake); lG = bce(g, torch.ones_like(g)); oG.zero_grad(); lG.backward(); oG.step()
        print(f"  epoch {ep + 1}: D {lD.item():.3f} G {lG.item():.3f} | D(real) {torch.sigmoid(dr).mean():.2f} D(fake) {torch.sigmoid(df).mean():.2f}", flush=True)
    return G.eval()


if __name__ == "__main__":
    smoke = "--smoke" in sys.argv; X, y = load("t10k" if smoke else "train"); real = torch.tensor(X) * 2 - 1; G = train(real, 2 if smoke else 20)
    with torch.no_grad(): fakes = (G(torch.randn(500, Z)) + 1) / 2
    d = torch.cdist(fakes[:100].flatten(1), torch.tensor(X[:3000]).flatten(1)).min(1).values; print(f"mean distance to nearest real image {d.mean():.2f} (0 would mean memorising)")
    print(f"diversity: mean pairwise distance between fakes {torch.pdist(fakes[:200].flatten(1)).mean():.2f} vs real {torch.pdist(torch.tensor(X[:200]).flatten(1)).mean():.2f}")
    torch.save(G.state_dict(), "data/generator.pt")
'''),
   S("Tests", "", "tests/test_vision.py", '''
import numpy as np, torch
from gan import Z, nets
from segment import dice, segment_coins
from superres import ESPCN


def test_coin_count_is_plausible():
    ws, _ = segment_coins(); assert 20 <= ws.max() <= 30


def test_dice():
    a = np.zeros((4, 4), bool); a[:2] = True; b = np.zeros((4, 4), bool); b[1:3] = True; assert abs(dice(a, b) - 0.5) < 1e-9


def test_shapes():
    assert ESPCN()(torch.zeros(1, 1, 24, 24)).shape == (1, 1, 48, 48)
    G, D = nets(); G.eval(); assert G(torch.randn(2, Z)).shape == (2, 1, 28, 28) and D(torch.zeros(2, 1, 28, 28)).shape == (2, 1)
'''),
   S("Run it", "", None, "python segment.py\npython faces.py            # downloads the emotion model from Hugging Face\npython superres.py\npython gan.py\npytest -q", "bash"),
  ],
  check=["python segment.py", "python faces.py --smoke", "python superres.py --smoke", "python gan.py --smoke", "pytest -q"], verify="smoke",
  talk=["When classical segmentation is enough and when you need a U-Net.", "Why PSNR alone is a poor measure of perceived sharpness.", "How you'd tell a GAN is collapsing or memorising.", "The ethics and limits of emotion recognition."],
  errors=[("Haar finds no faces", "faces must be frontal and big enough — try minSize smaller or a DNN detector"), ("GAN outputs noise", "check images are scaled to [-1, 1] and the generator ends with tanh")],
  extend=["Replace Otsu with a U-Net on your own masks", "Train ESPCN on a larger photo set (DIV2K)", "Turn the GAN into a conditional GAN"],
  see=["m-image-basics", "m-segmentation", "m-face-emotion", "m-super-resolution", "m-gan", "m-responsible-ai"])

# ---------------------------------------------------------------- P31
P31 = P("p-gnn-citations", "Citation intelligence with graph neural networks (Cora)", "gen", "Advanced", "2–3 days", "Colab or VS Code (CPU is fine)",
  "Use the citation graph of 2,708 machine-learning papers to (1) classify each paper's topic from its words **and** its citations, (2) recommend missing citations with link prediction, and (3) flag papers whose links disagree with their content — comparing a feature-only MLP, a hand-written GCN and PyTorch Geometric's GCN/GraphSAGE/GAT.",
  ["`graph.py`: load Cora, statistics, homophily", "`node_class.py`: MLP vs scratch GCN vs GCNConv/SAGEConv/GATConv; over-smoothing by depth", "`links.py`: link prediction with negative sampling and recommendations", "`odd_nodes.py`: neighbourhood-disagreement anomaly score", "`tests/`"],
  ["graphs as data", "message passing", "GCN normalisation", "GraphSAGE, GAT", "over-smoothing", "link prediction", "graph-based anomaly signals"],
  "Cora (Planetoid split) downloaded automatically by PyTorch Geometric from GitHub.",
  ["load + statistics", "node classification", "depth study", "link prediction", "anomalies"],
  [
   S("Dependencies", "", "requirements.txt", "torch>=2.2\ntorch_geometric>=2.5\nscikit-learn>=1.4\nnumpy>=1.26\npytest>=8.0", "text"),
   S("Ignore generated files", "", ".gitignore", GI, "text"),
   S("The graph", "", "graph.py", '''
import torch
from torch_geometric.datasets import Planetoid
from torch_geometric.utils import degree, to_dense_adj


def load():
    return Planetoid("data", "Cora")[0]


def norm_adj(data):
    A = to_dense_adj(data.edge_index, max_num_nodes=data.num_nodes)[0] + torch.eye(data.num_nodes); d = A.sum(1); return A / torch.sqrt(d[:, None] * d[None, :])


def homophily(data):
    s, t = data.edge_index; return (data.y[s] == data.y[t]).float().mean().item()


if __name__ == "__main__":
    g = load(); deg = degree(g.edge_index[0], g.num_nodes)
    print(f"nodes {g.num_nodes} | edges {g.num_edges // 2} (undirected) | features {g.num_features} | classes {int(g.y.max()) + 1}")
    print(f"degree median {deg.median():.0f}, max {deg.max():.0f} | edge homophily {homophily(g):.2f} (share of citations within the same topic)")
'''),
   S("Node classification", "", "node_class.py", '''
import sys, torch, torch.nn as nn
from torch_geometric.nn import GATConv, GCNConv, SAGEConv
from graph import load, norm_adj


class MLP(nn.Module):
    def __init__(s, i, h, o): super().__init__(); s.f = nn.Sequential(nn.Dropout(0.5), nn.Linear(i, h), nn.ReLU(), nn.Dropout(0.5), nn.Linear(h, o))
    def forward(s, x, ei): return s.f(x)


class ScratchGCN(nn.Module):
    def __init__(s, A, i, h, o, layers=2):
        super().__init__(); s.A = A; dims = [i] + [h] * (layers - 1) + [o]; s.lins = nn.ModuleList(nn.Linear(a, b) for a, b in zip(dims, dims[1:]))
    def forward(s, x, ei):
        for k, lin in enumerate(s.lins):
            x = s.A @ lin(nn.functional.dropout(x, 0.5, s.training)); x = torch.relu(x) if k < len(s.lins) - 1 else x
        return x


class PyG(nn.Module):
    def __init__(s, kind, i, h, o):
        super().__init__(); s.kind = kind
        s.c1, s.c2 = {"gcn": (GCNConv(i, h), GCNConv(h, o)), "sage": (SAGEConv(i, h), SAGEConv(h, o)), "gat": (GATConv(i, 8, heads=8, dropout=0.6), GATConv(64, o, dropout=0.6))}[kind]
    def forward(s, x, ei): return s.c2(nn.functional.dropout(torch.relu(s.c1(nn.functional.dropout(x, 0.5, s.training), ei)), 0.5, s.training), ei)


def fit(model, g, epochs=200):
    torch.manual_seed(0); opt = torch.optim.Adam(model.parameters(), 0.01, weight_decay=5e-4); best = (0, 0)
    for _ in range(epochs):
        model.train(); opt.zero_grad(); nn.functional.cross_entropy(model(g.x, g.edge_index)[g.train_mask], g.y[g.train_mask]).backward(); opt.step()
        model.eval(); p = model(g.x, g.edge_index).argmax(1); acc = lambda m: (p[m] == g.y[m]).float().mean().item()
        if acc(g.val_mask) > best[0]: best = (acc(g.val_mask), acc(g.test_mask))
    return best[1]


if __name__ == "__main__":
    g = load(); A = norm_adj(g); ep = 60 if "--quick" in sys.argv else 200
    for name, m in [("MLP (words only)", MLP(g.num_features, 64, 7)), ("GCN from scratch", ScratchGCN(A, g.num_features, 64, 7)), ("PyG GCNConv", PyG("gcn", g.num_features, 64, 7)),
                    ("PyG GraphSAGE", PyG("sage", g.num_features, 64, 7)), ("PyG GAT", PyG("gat", g.num_features, 64, 7))]:
        torch.manual_seed(0); print(f"  {name:18s} test accuracy {fit(m, g, ep):.3f}", flush=True)
    for L in [2, 4, 8]: torch.manual_seed(0); print(f"  scratch GCN depth {L}: test accuracy {fit(ScratchGCN(A, g.num_features, 64, 7, L), g, ep):.3f}  (deeper -> over-smoothing)")
'''),
   S("Link prediction: recommend citations", "", "links.py", '''
import sys, torch, torch.nn as nn
from sklearn.metrics import roc_auc_score
from torch_geometric.nn import GCNConv
from torch_geometric.transforms import RandomLinkSplit
from torch_geometric.utils import negative_sampling
from graph import load


class Encoder(nn.Module):
    def __init__(s, i, h=128, o=64): super().__init__(); s.c1, s.c2 = GCNConv(i, h), GCNConv(h, o)
    def forward(s, x, ei): return s.c2(torch.relu(s.c1(x, ei)), ei)


def train(epochs):
    g = load(); tr, va, te = RandomLinkSplit(num_val=0.05, num_test=0.1, is_undirected=True, add_negative_train_samples=False)(g)
    torch.manual_seed(0); enc = Encoder(g.num_features); opt = torch.optim.Adam(enc.parameters(), 0.01)
    for _ in range(epochs):
        enc.train(); z = enc(tr.x, tr.edge_index); neg = negative_sampling(tr.edge_index, num_nodes=g.num_nodes, num_neg_samples=tr.edge_label_index.shape[1])
        ei = torch.cat([tr.edge_label_index, neg], 1); lab = torch.cat([torch.ones(tr.edge_label_index.shape[1]), torch.zeros(neg.shape[1])])
        loss = nn.functional.binary_cross_entropy_with_logits((z[ei[0]] * z[ei[1]]).sum(1), lab); opt.zero_grad(); loss.backward(); opt.step()
    enc.eval(); return enc, tr, te


if __name__ == "__main__":
    enc, tr, te = train(40 if "--quick" in sys.argv else 200)
    with torch.no_grad(): z = enc(te.x, te.edge_index)
    s = (z[te.edge_label_index[0]] * z[te.edge_label_index[1]]).sum(1); print(f"hidden-citation AUC {roc_auc_score(te.edge_label.numpy(), s.numpy()):.3f}")
    paper = 0; known = set(tr.edge_index[1][tr.edge_index[0] == paper].tolist()) | {paper}; scores = z @ z[paper]
    recs = [int(i) for i in torch.argsort(scores, descending=True) if int(i) not in known][:5]; print(f"recommended citations for paper {paper}: {recs} (same topic: {[int(te.y[r]) == int(te.y[paper]) for r in recs]})")
'''),
   S("Odd papers: links vs content", """A simple, explainable graph anomaly signal: for each paper, the share of its neighbours whose predicted topic differs from its own. High disagreement = mislabelled, interdisciplinary or spam-like citation patterns worth a human look.""",
     "odd_nodes.py", '''
import torch
from torch_geometric.utils import to_undirected
from graph import load
from node_class import MLP, fit

if __name__ == "__main__":
    g = load(); m = MLP(g.num_features, 64, 7); fit(m, g, 100); m.eval()
    with torch.no_grad(): pred = m(g.x, g.edge_index).argmax(1)
    ei = to_undirected(g.edge_index); disagree = torch.zeros(g.num_nodes); deg = torch.zeros(g.num_nodes)
    deg.index_add_(0, ei[0], torch.ones(ei.shape[1])); disagree.index_add_(0, ei[0], (pred[ei[0]] != pred[ei[1]]).float()); score = disagree / deg.clamp(min=1)
    top = torch.argsort(score * (deg >= 3), descending=True)[:5]
    print("most 'odd' papers (node, degree, disagreement, true label == predicted):", [(int(i), int(deg[i]), round(float(score[i]), 2), bool(g.y[i] == pred[i])) for i in top])
    print(f"label errors among top-50 odd papers: {(g.y[torch.argsort(score * (deg >= 3), descending=True)[:50]] != pred[torch.argsort(score * (deg >= 3), descending=True)[:50]]).float().mean():.0%} vs overall {(g.y != pred).float().mean():.0%}")
'''),
   S("Tests", "", "tests/test_graph.py", '''
import torch
from graph import homophily, load, norm_adj


def test_normalised_adjacency_is_symmetric_with_self_loops():
    g = load(); A = norm_adj(g); assert torch.allclose(A, A.T, atol=1e-6) and (A.diagonal() > 0).all()


def test_cora_is_homophilous():
    assert homophily(load()) > 0.7
'''),
   S("Run it", "", None, "python graph.py\npython node_class.py\npython links.py\npython odd_nodes.py\npytest -q", "bash"),
  ],
  check=["python graph.py", "python node_class.py --quick", "python links.py --quick", "python odd_nodes.py", "pytest -q"],
  talk=["Why a GCN beats a words-only MLP on Cora (homophily).", "How the normalised adjacency works and why depth causes over-smoothing.", "How you'd evaluate citation recommendations without leakage."],
  errors=[("Download fails", "Planetoid fetches from GitHub; run in Colab if your network blocks it"), ("Accuracy ~30%", "you forgot the train mask or the self-loops/normalisation")],
  extend=["Graph classification on molecules (TUDataset MUTAG)", "Fraud rings: build a customer-device-card graph", "Neighbour sampling for large graphs (NeighborLoader)"],
  see=["m-gnn", "m-anomaly", "m-recsys"])

PROJECTS_5 = [P27, P28, P29, P30, P31]
