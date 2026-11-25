"""Real-data walkthroughs: Deep learning."""
import os
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt

os.environ.setdefault("KERAS_BACKEND", "torch")


def _torch():
    import torch
    torch.manual_seed(0); torch.set_num_threads(2)
    return torch


def _digits():
    from sklearn.model_selection import train_test_split
    dg = D("digits")
    return train_test_split(dg.data / 16, dg.target, test_size=0.3, random_state=0)


def _img(v):
    """An 8x8 digit as a table of 0-16 values."""
    return t(pd.DataFrame(np.asarray(v).reshape(8, 8)).round(0).astype(int))


def _cancer2():
    from sklearn.preprocessing import StandardScaler
    df = D("cancer")
    cols = ["mean radius", "mean concave points"]
    sc = StandardScaler().fit(df[cols])
    return df, cols, sc.transform(df[cols]), (df["target"] == 0).astype(int).values  # 1 = malignant


def _fit_mlp(torch, layers, Xtr, ytr, epochs=30, opt="adam", lr=1e-3, wd=0.0, bs=64, seed=0):
    torch.manual_seed(seed)
    net = torch.nn.Sequential(*layers)
    o = {"adam": torch.optim.Adam, "sgd": torch.optim.SGD}[opt](net.parameters(), lr=lr, weight_decay=wd)
    X = torch.tensor(Xtr, dtype=torch.float32); y = torch.tensor(ytr)
    g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        net.train()
        for idx in torch.randperm(len(X), generator=g).split(bs):
            o.zero_grad(); torch.nn.functional.cross_entropy(net(X[idx]), y[idx]).backward(); o.step()
    net.eval()
    return net


def _acc(torch, net, X, y):
    with torch.no_grad():
        return (net(torch.tensor(X, dtype=torch.float32)).argmax(1).numpy() == y).mean()


@walk("m-dl-intro", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    from sklearn.linear_model import LogisticRegression
    lin = LogisticRegression(max_iter=2000).fit(Xtr, ytr).score(Xte, yte)
    net = _fit_mlp(torch, [nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10)], Xtr, ytr, epochs=60)
    with torch.no_grad():
        p = torch.softmax(net(torch.tensor(Xte[:1], dtype=torch.float32)), 1).numpy()[0]
    top = pd.DataFrame({"digit": range(10), "probability": p}).sort_values("probability", ascending=False).head(3)
    return [
        ("The input is just numbers", f"A real scanned digit (true label **{yte[0]}**) is 64 ink values from 0 to 16:\n\n{_img(Xte[0] * 16)}"),
        ("A network turns pixels into a guess", f"A small network (64 inputs → 64 hidden neurons → 10 outputs) gives a probability for each digit:\n\n{t(top, nd=3)}"),
        ("Does depth help?", f"On {len(yte)} test digits it has never seen: plain logistic regression **{pct(lin, 1)}**, the network with one hidden layer **{pct(_acc(torch, net, Xte, yte), 1)}**."),
    ], "Deep learning stacks simple layers that turn raw numbers (pixels, words, sounds) into a prediction, learning the useful features on the way."


@walk("m-nn-formulation", "cancer")
def _():
    from sklearn.linear_model import LogisticRegression
    df, cols, Z, y = _cancer2()
    m = LogisticRegression().fit(Z, y); w, b = m.coef_[0], m.intercept_[0]
    rows = [0, 19, 40]
    rec = []
    for i in rows:
        z = Z[i] @ w + b
        rec.append({"biopsy": i, cols[0]: df.loc[i, cols[0]], cols[1]: df.loc[i, cols[1]], "x1 (scaled)": Z[i, 0], "x2 (scaled)": Z[i, 1],
                    "z = w1·x1 + w2·x2 + b": z, "σ(z) = P(malignant)": 1 / (1 + np.exp(-z)), "truth": df.loc[i, "diagnosis"]})
    bad = [r for r in rec if (r["σ(z) = P(malignant)"] > 0.5) != (r["truth"] == "malignant")]
    miss = "".join(f" Biopsy {r['biopsy']} is a miss: its two measurements look benign, so one neuron with two inputs can't catch it; more inputs and more neurons help." for r in bad)
    return [
        ("Inputs", f"Two measurements of each biopsy, standardised (0 = average, 1 = one standard deviation above):\n\n{t(pd.DataFrame(rec)[['biopsy', cols[0], cols[1], 'x1 (scaled)', 'x2 (scaled)']])}"),
        ("Learned weights", f"Training on all {len(df)} biopsies gave w1 = **{w[0]:.2f}**, w2 = **{w[1]:.2f}**, b = **{b:.2f}**. Both weights are positive: bigger cells and more concave points push towards malignant."),
        ("Weighted sum, then activation", f"{t(pd.DataFrame(rec)[['biopsy', 'z = w1·x1 + w2·x2 + b', 'σ(z) = P(malignant)', 'truth']], nd=3)}\n\nThe sigmoid σ squeezes any z into a probability between 0 and 1.{miss}"),
    ], "A neuron is a weighted sum of inputs plus a bias, passed through an activation; a network is many of these in layers."


@walk("m-perceptron", "iris")
def _():
    df = D("iris")
    d = df[df["species"].isin(["setosa", "versicolor"])].sample(frac=1, random_state=1).reset_index(drop=True)
    X = d[["petal length (cm)", "petal width (cm)"]].values; y = np.where(d["species"] == "versicolor", 1, -1)
    w = np.zeros(2); b = 0.0; log = []; epoch_err = []
    for ep in range(20):
        err = 0
        for i in range(len(X)):
            pred = 1 if X[i] @ w + b > 0 else -1
            if pred != y[i]:
                w = w + y[i] * X[i]; b += y[i]; err += 1
                if len(log) < 5:
                    log.append({"flower": d.loc[i, "species"], "petal len": X[i, 0], "petal wid": X[i, 1], "predicted": "versicolor" if pred == 1 else "setosa", "new w1": w[0], "new w2": w[1], "new b": b})
        epoch_err.append(err)
        if err == 0: break
    return [
        ("Task", f"{len(d)} real flowers, two species. Rule: if w1·length + w2·width + b > 0 say versicolor, else setosa. Start with all weights 0."),
        ("Each mistake nudges the weights", f"The first updates, flower by flower:\n\n{t(pd.DataFrame(log))}\n\nWrong on a versicolor → add its measurements; wrong on a setosa → subtract them."),
        ("Until no mistakes remain", f"Mistakes per pass over the data: {', '.join(map(str, epoch_err))}. Final rule: {w[0]:.1f}·length + {w[1]:.1f}·width {'+' if b >= 0 else '−'} {abs(b):.0f} > 0. The two species can be split by a straight line, so the perceptron is guaranteed to stop."),
    ], "The perceptron learns by correcting its weights only when it makes a mistake."


@walk("m-mlp", "cancer")
def _():
    from sklearn.neural_network import MLPClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import cross_val_score
    df = D("cancer"); X = df.drop(columns=["target", "diagnosis"]); y = df["target"]
    rows = [{"model": "no hidden layer (logistic)", "parameters": 31, "accuracy (5-fold)": cross_val_score(make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)), X, y, cv=5).mean()}]
    for h in [(2,), (16,), (64, 64)]:
        m = make_pipeline(StandardScaler(), MLPClassifier(h, max_iter=2000, random_state=0))
        n = 30 * h[0] + h[0] + sum(h[i] * h[i + 1] + h[i + 1] for i in range(len(h) - 1)) + h[-1] + 1
        rows.append({"model": f"hidden layers {h}", "parameters": n, "accuracy (5-fold)": cross_val_score(m, X, y, cv=5).mean()})
    m = make_pipeline(StandardScaler(), MLPClassifier((2,), max_iter=2000, random_state=0)).fit(X, y)
    sc, mlp = m[0], m[1]
    H = np.maximum(0, sc.transform(X.iloc[[0, 19]]) @ mlp.coefs_[0] + mlp.intercepts_[0])
    hid = pd.DataFrame(H, columns=["hidden 1", "hidden 2"]).assign(truth=df["diagnosis"].iloc[[0, 19]].values, **{"P(benign)": m.predict_proba(X.iloc[[0, 19]])[:, 1]})
    return [
        ("30 measurements per biopsy", f"{t(X[['mean radius', 'mean texture', 'mean concave points', 'worst area']], 3)}\n\n…and 26 more columns."),
        ("Inside a tiny MLP (2 hidden neurons)", f"Each hidden neuron computes its own weighted sum of all 30 inputs, then ReLU (negative → 0). For two real biopsies:\n\n{t(hid, nd=3)}\n\nThe output layer reads only these 2 numbers."),
        ("Bigger networks", f"{t(pd.DataFrame(rows), nd=3)}\n\n{"Here the plain logistic model is already the best: the classes are almost separable by a straight line, so hidden layers add nothing." if rows[0]["accuracy (5-fold)"] >= max(r["accuracy (5-fold)"] for r in rows) else "Hidden layers help here, but the gain shrinks as the network grows."} The right size depends on the data."),
    ], "An MLP chains layers of neurons; hidden layers build new features from the inputs before the final decision."


@walk("m-activations", "cancer")
def _():
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler
    df = D("cancer"); X = StandardScaler().fit_transform(df.drop(columns=["target", "diagnosis"]))
    m = MLPClassifier((6,), max_iter=2000, random_state=0).fit(X, df["target"])
    z = X[0] @ m.coefs_[0] + m.intercepts_[0]
    tab = pd.DataFrame({"neuron": range(1, 7), "z (weighted sum)": z, "sigmoid": 1 / (1 + np.exp(-z)), "tanh": np.tanh(z), "ReLU": np.maximum(0, z), "Leaky ReLU (0.01)": np.where(z > 0, z, 0.01 * z)})
    s = 1 / (1 + np.exp(-z))
    grad = pd.DataFrame({"neuron": range(1, 7), "z": z, "sigmoid slope σ(1−σ)": s * (1 - s), "ReLU slope": (z > 0).astype(float)})
    return [
        ("Real weighted sums", f"The 6 hidden neurons of a trained network, for biopsy 0 ({df['diagnosis'][0]}), produce these z values. Each activation function turns z into the neuron's output:\n\n{t(tab, nd=3)}"),
        ("What each does", "Sigmoid: squashes to 0–1. Tanh: squashes to −1 to 1 (centred at 0). ReLU: keeps positives, zeroes negatives. Leaky ReLU: like ReLU but keeps a little of the negatives."),
        ("Slopes decide learning", f"{t(grad, nd=3)}\n\nThe sigmoid's slope is never more than 0.25 and is tiny for large |z|, so gradients shrink layer after layer. ReLU's slope is exactly 1 for positive z, which is why deep networks use it."),
    ], "Activations add the non-linearity that lets networks learn curves; their slopes control how well gradients flow."


@walk("m-loss-functions", ("cancer", "housing"))
def _():
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_predict
    df, cols, Z, y = _cancer2()
    p = cross_val_predict(LogisticRegression(), Z, y, cv=5, method="predict_proba")[:, 1]
    pick = [int(np.argmin(np.where(y == 1, -p, 9))), int(np.argmin(np.where(y == 0, p, 9))), int(np.argmin(np.abs(p - 0.5))), int(np.argmax(np.where(y == 1, -p, -9)))]
    rows = pd.DataFrame({"biopsy": pick, "truth": np.where(y[pick] == 1, "malignant", "benign"), "P(malignant)": p[pick]})
    q = np.where(y[pick] == 1, p[pick], 1 - p[pick])
    rows["P(correct answer)"] = q; rows["log loss −log P"] = -np.log(q); rows["squared error"] = (1 - q) ** 2
    h = D("housing").dropna(); v = h["median_house_value"].values / 1000
    err = v - np.median(v)
    big = np.argsort(-np.abs(err))[:len(err) // 20]
    r2 = pd.DataFrame([{"loss": "MSE (squared, $k²)", "value": np.mean(err ** 2), "share of the loss from the worst 5% of districts": pct(np.sum(err[big] ** 2) / np.sum(err ** 2))},
                       {"loss": "MAE (absolute, $k)", "value": np.mean(np.abs(err)), "share of the loss from the worst 5% of districts": pct(np.sum(np.abs(err[big])) / np.sum(np.abs(err)))}])
    return [
        ("Classification: log loss per biopsy", f"Predictions made on held-out folds:\n\n{t(rows, nd=3)}\n\nA confident correct answer costs almost nothing; a confident **wrong** answer (last row) costs far more under log loss than under squared error. That's why classifiers use log loss (cross-entropy)."),
        ("Regression: errors of a dumb guess", f"Predict every California district's house value as the median (${np.median(v):.0f}k). Errors range from {err.min():.0f}k to +{err.max():.0f}k."),
        ("MSE vs MAE", f"{t(r2, nd=1)}\n\nSquaring makes big errors dominate, so MSE chases outliers; MAE treats every $1k the same. Huber loss is squared for small errors and absolute for big ones."),
    ], "The loss is the single number training tries to make small; choosing it decides which mistakes the model cares about most."


@walk("m-backprop", "cancer")
def _():
    df, cols, Z, y = _cancer2()
    i = 0; x = Z[i]; target = y[i]
    w = np.array([0.1, -0.2]); b = 0.0; lr = 0.5
    z = x @ w + b; a = 1 / (1 + np.exp(-z)); L = -(target * np.log(a) + (1 - target) * np.log(1 - a))
    dz = a - target; dw = dz * x; db = dz
    eps = 1e-5
    num = [(lambda ww: -(target * np.log(1 / (1 + np.exp(-(x @ ww + b)))) + (1 - target) * np.log(1 - 1 / (1 + np.exp(-(x @ ww + b))))))(w + eps * np.eye(2)[k]) for k in range(2)]
    num = [(n - L) / eps for n in num]
    w2 = w - lr * dw; b2 = b - lr * db
    a2 = 1 / (1 + np.exp(-(x @ w2 + b2))); L2 = -(target * np.log(a2) + (1 - target) * np.log(1 - a2))
    fw = pd.DataFrame([{"quantity": "x1, x2 (scaled inputs)", "value": f"{x[0]:.3f}, {x[1]:.3f}"}, {"quantity": "start weights w1, w2, b", "value": "0.1, −0.2, 0"},
                       {"quantity": "z = w·x + b", "value": f"{z:.3f}"}, {"quantity": "a = σ(z) = P(malignant)", "value": f"{a:.3f}"},
                       {"quantity": f"loss (truth = {'malignant' if target else 'benign'})", "value": f"{L:.3f}"}])
    bw = pd.DataFrame([{"gradient": "∂L/∂z = a − y", "value": dz}, {"gradient": "∂L/∂w1 = (a − y)·x1", "value": dw[0]}, {"gradient": "∂L/∂w2 = (a − y)·x2", "value": dw[1]}, {"gradient": "∂L/∂b = a − y", "value": db},
                       {"gradient": "check: nudge w1 by 0.00001", "value": num[0]}, {"gradient": "check: nudge w2 by 0.00001", "value": num[1]}])
    return [
        (f"Forward pass on biopsy {i}", f"{t(fw)}"),
        ("Backward pass: chain rule", f"{t(bw, nd=4)}\n\nThe chain-rule gradients match the slow 'nudge and re-measure' check."),
        ("Update and re-check", f"w ← w − {lr} × gradient gives w1 = {w2[0]:.3f}, w2 = {w2[1]:.3f}, b = {b2:.3f}. New P(malignant) = **{a2:.3f}**, loss {L:.3f} → **{L2:.3f}**."),
    ], "Backprop computes every weight's share of the error with the chain rule, so one step downhill lowers the loss."


@walk("m-optimizers", "housing")
def _():
    torch = _torch(); nn = torch.nn
    from sklearn.preprocessing import StandardScaler
    h = D("housing").dropna()
    cols = ["median_income", "housing_median_age", "total_rooms", "population", "households", "latitude", "longitude"]
    X = torch.tensor(StandardScaler().fit_transform(h[cols]), dtype=torch.float32)
    y = torch.tensor(h["median_house_value"].values / 1e5, dtype=torch.float32)[:, None]
    res = []; curves = {}
    for name, mk in [("SGD lr 0.01", lambda p: torch.optim.SGD(p, lr=0.01)), ("SGD + momentum 0.9", lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9)),
                     ("RMSprop lr 0.01", lambda p: torch.optim.RMSprop(p, lr=0.01)), ("Adam lr 0.01", lambda p: torch.optim.Adam(p, lr=0.01))]:
        torch.manual_seed(0)
        net = nn.Sequential(nn.Linear(7, 32), nn.ReLU(), nn.Linear(32, 1)); o = mk(net.parameters()); c = []
        for ep in range(200):
            o.zero_grad(); L = ((net(X) - y) ** 2).mean(); L.backward(); o.step(); c.append(L.item())
        curves[name] = c
        res.append({"optimizer": name, "after 10 steps": c[9], "after 50": c[49], "after 200": c[-1], "RMSE after 200 ($k)": 100 * c[-1] ** 0.5})
    return [
        ("Same network, same data", f"Predict house value (in $100k) of {len(h):,} districts from 7 columns with a 7 → 32 → 1 network. Only the optimizer changes; each step uses all districts."),
        ("Mean squared error as training goes on", f"{t(pd.DataFrame(res), nd=3)}"),
        ("Why they differ", "Plain SGD takes the same small step everywhere. Momentum keeps rolling in a consistent direction. RMSprop and Adam give each weight its own step size from the size of its recent gradients, so they move fast early."),
    ], "Optimizers decide how big a step each weight takes; adaptive ones like Adam usually get a good answer in fewer steps."


@walk("m-init-norm", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    X = torch.tensor(Xtr, dtype=torch.float32)

    def build(std=None, bn=False):
        torch.manual_seed(0); L = []
        d = 64
        for _ in range(6):
            lin = nn.Linear(d, 64)
            if std is not None: nn.init.normal_(lin.weight, 0, std); nn.init.zeros_(lin.bias)
            L += [lin] + ([nn.BatchNorm1d(64)] if bn else []) + [nn.ReLU()]; d = 64
        return nn.Sequential(*L, nn.Linear(64, 10))

    rows = []; spread = {}
    for name, kw in [("tiny random (std 0.01)", dict(std=0.01)), ("He init (std √(2/64))", dict(std=(2 / 64) ** 0.5)), ("tiny random + BatchNorm", dict(std=0.01, bn=True))]:
        net = build(**kw); net.train(); s = []; a = X
        with torch.no_grad():
            for m in net:
                a = m(a)
                if isinstance(m, nn.ReLU): s.append(a.std().item())
        spread[name] = s
        net = build(**kw)
        o = torch.optim.SGD(net.parameters(), lr=0.1)
        for _ in range(15):
            for idx in torch.randperm(len(X)).split(64):
                o.zero_grad(); nn.functional.cross_entropy(net(X[idx]), torch.tensor(ytr)[idx]).backward(); o.step()
        net.eval(); rows.append({"setup": name, "test accuracy after 15 epochs (SGD)": _acc(torch, net, Xte, yte)})
    sp = pd.DataFrame(spread, index=[f"layer {i + 1}" for i in range(6)]).T
    return [
        ("Push real digits through an untrained 6-layer net", f"Spread (standard deviation) of the activations after each layer:\n\n{t(sp, nd=4, index=True)}"),
        ("Read the table", "With tiny weights the signal shrinks towards 0 layer by layer, so the output barely depends on the input. He initialisation scales weights so the spread stays steady. BatchNorm re-scales every layer's outputs, fixing the spread even with bad weights."),
        ("Effect on training", f"{t(pd.DataFrame(rows), nd=3)}"),
    ], "Good initial weights and normalisation keep signals at a healthy size through deep networks so they can start learning."


@walk("m-vanishing", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    X = torch.tensor(Xtr, dtype=torch.float32); Y = torch.tensor(ytr)
    rows = []
    for act in ["Sigmoid", "ReLU"]:
        torch.manual_seed(0)
        L = []
        for i in range(10): L += [nn.Linear(64, 64), getattr(nn, act)()]
        net = nn.Sequential(*L, nn.Linear(64, 10))
        nn.functional.cross_entropy(net(X), Y).backward()
        g = [m.weight.grad.norm().item() for m in net if isinstance(m, nn.Linear)]
        net.zero_grad()
        o = torch.optim.Adam(net.parameters(), lr=1e-3)
        for _ in range(20):
            for idx in torch.randperm(len(X)).split(64):
                o.zero_grad(); nn.functional.cross_entropy(net(X[idx]), Y[idx]).backward(); o.step()
        net.eval()
        rows.append({"activation": act, "gradient size, layer 1": g[0], "gradient size, layer 10": g[9], "layer 1 is smaller by": f"{g[-1] / g[0]:,.0f}×", "test accuracy after 20 epochs": _acc(torch, net, Xte, yte)})
    r = pd.DataFrame(rows)
    return [
        ("A 10-layer network on real digits", "Same data, same depth, same optimizer; only the activation differs."),
        ("Measure the gradient at each end", f"{t(r[['activation', 'gradient size, layer 1', 'gradient size, layer 10', 'layer 1 is smaller by']].assign(**{'gradient size, layer 1': r['gradient size, layer 1'].map(lambda v: f'{v:.1e}'), 'gradient size, layer 10': r['gradient size, layer 10'].map(lambda v: f'{v:.1e}')}))}\n\nGradients shrink on the way back in both, but far more with sigmoid: each sigmoid multiplies the gradient by at most 0.25."),
        ("Effect on learning", f"{t(r[['activation', 'test accuracy after 20 epochs']], nd=3)}"),
    ], "In deep sigmoid networks the gradient fades on its way back, so early layers barely learn; ReLU, good initialisation, normalisation and skip connections fix this."


@walk("m-dl-regularization", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    Xs, ys = Xtr[:150], ytr[:150]
    rows = []
    for name, drop, wd in [("no regularisation", 0, 0), ("dropout 0.5", 0.5, 0), ("weight decay 1e-2", 0, 1e-2), ("both", 0.5, 1e-2)]:
        accs = []
        for seed in range(3):
            net = _fit_mlp(torch, [nn.Linear(64, 256), nn.ReLU(), nn.Dropout(drop), nn.Linear(256, 256), nn.ReLU(), nn.Dropout(drop), nn.Linear(256, 10)], Xs, ys, epochs=200, wd=wd, seed=seed, opt="adam")
            accs.append((_acc(torch, net, Xs, ys), _acc(torch, net, Xte, yte)))
        a = np.mean(accs, 0)
        rows.append({"setup": name, "train accuracy": a[0], "test accuracy": a[1], "gap": a[0] - a[1]})
    r = pd.DataFrame(rows); best = r.loc[r["test accuracy"].idxmax(), "setup"]
    return [
        ("Too little data for a big network", f"Only 150 real digits for training a network with ~{64 * 256 + 256 * 256 + 2570:,} weights, tested on {len(yte)} unseen digits (averaged over 3 runs)."),
        ("Results", f"{t(r, nd=3)}"),
        ("Read it", f"Every setup gets the training digits right; the gap shows how much was memorised. The best test score here came from **{best}**{"; the differences are small (under 2 points), so on this easy dataset the network generalises fairly well even without help" if r["test accuracy"].max() - r["test accuracy"].min() < 0.02 else ""}."),
    ], "Regularisation (dropout, weight decay, early stopping, more data) trades a little training fit for better results on new data."


@walk("m-pytorch", "housing")
def _():
    torch = _torch(); nn = torch.nn
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    h = D("housing").dropna().reset_index(drop=True)
    cols = ["median_income", "housing_median_age", "latitude", "longitude"]
    tr, te = train_test_split(h, test_size=0.2, random_state=0)
    sc = StandardScaler().fit(tr[cols])
    Xtr = torch.tensor(sc.transform(tr[cols]), dtype=torch.float32); ytr = torch.tensor(tr["median_house_value"].values / 1e5, dtype=torch.float32)[:, None]
    Xte = torch.tensor(sc.transform(te[cols]), dtype=torch.float32)
    net = nn.Sequential(nn.Linear(4, 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 1))
    o = torch.optim.Adam(net.parameters(), lr=1e-2); log = []
    for ep in range(1, 301):
        o.zero_grad(); L = nn.functional.mse_loss(net(Xtr), ytr); L.backward(); o.step()
        if ep in (1, 10, 50, 100, 300): log.append({"epoch": ep, "training MSE": L.item(), "RMSE ($k)": 100 * L.item() ** 0.5})
    with torch.no_grad(): p = net(Xte).numpy()[:, 0] * 1e5
    show = te[cols + ["median_house_value"]].head(4).assign(predicted=p[:4].round(-2))
    rmse = np.sqrt(np.mean((p - te["median_house_value"].values) ** 2))
    return [
        ("Rows become tensors", f"`torch.tensor(...)` turns {len(tr):,} training districts × 4 columns into a {tuple(Xtr.shape)} tensor. The first rows after scaling:\n\n{t(pd.DataFrame(Xtr[:3].numpy(), columns=cols), nd=3)}"),
        ("The training loop: zero_grad → forward → loss → backward → step", f"{t(pd.DataFrame(log), nd=4)}"),
        ("Predict unseen districts", f"{t(show)}\n\nTest RMSE on {len(te)} unseen districts: **${rmse / 1000:.0f}k**."),
    ], "PyTorch is tensors + automatic gradients + a loop you write yourself, which makes every step visible."


@walk("m-keras", "cancer")
def _():
    import keras
    keras.utils.set_random_seed(0)
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    df = D("cancer"); X = df.drop(columns=["target", "diagnosis"]).values; y = df["target"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
    sc = StandardScaler().fit(Xtr); Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
    m = keras.Sequential([keras.Input((30,)), keras.layers.Dense(16, activation="relu"), keras.layers.Dropout(0.2), keras.layers.Dense(1, activation="sigmoid")])
    m.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    hist = m.fit(Xtr, ytr, epochs=30, batch_size=32, validation_split=0.2, verbose=0).history
    hh = pd.DataFrame({"epoch": range(1, 31), "loss": hist["loss"], "accuracy": hist["accuracy"], "val_loss": hist["val_loss"], "val_accuracy": hist["val_accuracy"]}).iloc[[0, 4, 9, 19, 29]]
    loss, acc = m.evaluate(Xte, yte, verbose=0)
    p = m.predict(Xte[:4], verbose=0)[:, 0]
    show = pd.DataFrame({"truth": np.where(yte[:4] == 1, "benign", "malignant"), "P(benign)": p})
    return [
        ("Define and compile", f"`Sequential([Dense(16, relu), Dropout(0.2), Dense(1, sigmoid)])`, `compile(optimizer='adam', loss='binary_crossentropy')`: {m.count_params()} weights, for {len(Xtr)} training biopsies with 30 measurements each."),
        ("model.fit prints this every epoch", f"{t(hh, nd=3)}\n\n`val_` columns are measured on 20% of the training data held aside."),
        ("Evaluate and predict", f"`model.evaluate` on {len(yte)} unseen biopsies: accuracy **{pct(acc, 1)}**. `model.predict` on four of them:\n\n{t(show, nd=3)}"),
    ], "Keras hides the training loop behind compile/fit/evaluate/predict; the computation underneath is the same as in PyTorch (here Keras even runs on PyTorch)."


@walk("m-cnn", "digits")
def _():
    torch = _torch(); nn = torch.nn
    from scipy.signal import correlate2d
    Xtr, Xte, ytr, yte = _digits()
    img = (Xte[0] * 16).reshape(8, 8)
    k = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
    out = correlate2d(img, k, mode="valid")
    cnn = lambda: [nn.Unflatten(1, (1, 8, 8)), nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(32 * 4, 10)]
    mlp = lambda: [nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10)]
    rows = []
    for name, L in [("MLP (64 → 128 → 10)", mlp), ("CNN (2 conv layers)", cnn)]:
        for n in [100, len(Xtr)]:
            net = _fit_mlp(torch, L(), Xtr[:n], ytr[:n], epochs=int(60 * len(Xtr) / n) if n < len(Xtr) else 60)
            rows.append({"model": name, "training digits": n, "weights": sum(p.numel() for p in net.parameters()), "test accuracy": _acc(torch, net, Xte, yte)})
    return [
        ("A real digit", f"True label **{yte[0]}**:\n\n{_img(img)}"),
        ("Slide a 3 × 3 vertical-edge filter", f"Filter = [−1 0 1] in each row: at each position, sum(right column) − sum(left column). Result (6 × 6):\n\n{t(pd.DataFrame(out).astype(int))}\n\nBig positive = ink starts to the right; big negative = ink ends. A CNN **learns** dozens of such filters."),
        ("CNN vs plain MLP", f"{t(pd.DataFrame(rows), nd=3)}\n\nThe CNN reuses the same small filters everywhere in the image, so it has fewer weights for its size."),
    ], "A CNN slides small learned filters over the image, so it detects the same pattern wherever it appears."


@walk("m-cnn-understand", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    net = _fit_mlp(torch, [nn.Unflatten(1, (1, 8, 8)), nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(128, 10)], Xtr, ytr, epochs=60)
    i = int(np.where(yte == 0)[0][0]); x = torch.tensor(Xte[i:i + 1], dtype=torch.float32)
    with torch.no_grad():
        base = torch.softmax(net(x), 1)[0, 0].item(); s0 = net(x)[0, 0].item()
        occ = np.zeros((6, 6)); ink = np.zeros((6, 6))
        for r in range(6):
            for c in range(6):
                z = x.clone().view(8, 8); ink[r, c] = z[r:r + 3, c:c + 3].sum().item(); z[r:r + 3, c:c + 3] = 0
                occ[r, c] = s0 - net(z.view(1, 64))[0, 0].item()
        inky = occ[ink > np.median(ink)].mean(); blank = occ[ink <= np.median(ink)].mean()
        f1 = net[2](net[1](net[0](x)))[0]
    xg = x.clone().requires_grad_(True); net(xg)[0, 0].backward()
    sal = xg.grad.abs().view(8, 8).numpy()
    strongest = int(f1.sum((1, 2)).argmax())
    return [
        (f"A real '0' and the CNN's confidence", f"{_img(Xte[i] * 16)}\n\nP(digit = 0) = **{base:.3f}**."),
        ("Occlusion: hide a 3 × 3 patch, measure the drop", f"The network's raw score for '0' is {s0:.1f}. Each cell = how much that score falls when the 3 × 3 patch starting there is blacked out:\n\n{t(pd.DataFrame(occ).round(1) + 0.0)}\n\nAverage drop when the patch covers a lot of ink: **{inky:.1f}**; when it covers mostly blank paper: **{blank:.1f}**. Biggest drop: patch at row {np.unravel_index(occ.argmax(), occ.shape)[0]}, column {np.unravel_index(occ.argmax(), occ.shape)[1]} ({occ.max():.1f}); smallest: row {np.unravel_index(occ.argmin(), occ.shape)[0]}, column {np.unravel_index(occ.argmin(), occ.shape)[1]} ({occ.min():.1f}). Compare with the image above to see which strokes the network leans on."),
        ("Inside the first layer", f"Filter {strongest} responds most to this image. Its 8 × 8 activation map (×10):\n\n{t(pd.DataFrame((f1[strongest].numpy() * 10).round(0)).astype(int))}\n\nGradient saliency (which single pixels move the score most) peaks at pixel row {np.unravel_index(sal.argmax(), sal.shape)[0]}, column {np.unravel_index(sal.argmax(), sal.shape)[1]}."),
    ], "Occlusion, saliency and feature maps show which parts of the input the CNN actually uses."


@walk("m-autoencoder", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    X = torch.tensor(Xtr, dtype=torch.float32); Xt = torch.tensor(Xte, dtype=torch.float32)
    rows = []; keep = {}
    for k in [2, 8, 16]:
        torch.manual_seed(0)
        enc = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, k)); dec = nn.Sequential(nn.Linear(k, 32), nn.ReLU(), nn.Linear(32, 64), nn.Sigmoid())
        o = torch.optim.Adam(list(enc.parameters()) + list(dec.parameters()), lr=3e-3)
        for _ in range(150):
            for idx in torch.randperm(len(X)).split(128):
                o.zero_grad(); ((dec(enc(X[idx])) - X[idx]) ** 2).mean().backward(); o.step()
        with torch.no_grad():
            R = dec(enc(Xt)); e = ((R - Xt) ** 2).mean(1).numpy(); code = enc(Xt[:1]).numpy()[0]
        rows.append({"code size": k, "compression": f"64 → {k}", "avg pixel error (0-16 scale)": 16 * (R - Xt).abs().mean().item()})
        keep[k] = (R.numpy(), e, code)
    R, e, code = keep[8]
    worst = np.argsort(-e)[:3]
    return [
        ("Squeeze and rebuild", f"Encoder: 64 pixels → small code. Decoder: code → 64 pixels. Trained only to copy its input. The 8-number code of the first test digit (a {yte[0]}): {', '.join(f'{c:.2f}' for c in code)}.\n\n{t(pd.DataFrame(rows), nd=2)}"),
        ("Original vs rebuilt (code size 8)", f"Original:\n\n{_img(Xte[0] * 16)}\n\nRebuilt from 8 numbers:\n\n{_img(R[0] * 16)}"),
        ("Hardest digits to rebuild", f"Test digits with the largest rebuild error are the unusual ones: true labels {', '.join(str(yte[w]) for w in worst)}. Rebuild error is a common anomaly score.\n\n{_img(Xte[worst[0]] * 16)}"),
    ], "An autoencoder learns a compact code by trying to reproduce its input; what it can't reproduce well is unusual."


def _flights():
    f = D("flights"); s = f["passengers"].values.astype(float)
    return f, s


def _windows(s, w):
    X = np.array([s[i:i + w] for i in range(len(s) - w)]); y = s[w:]
    return X, y


def _seq_model(torch, kind, w, s, epochs=400, seed=0):
    nn = torch.nn
    torch.manual_seed(seed)
    ls = np.log(s); mu, sd = ls[:-12].mean(), ls[:-12].std(); z = (ls - mu) / sd
    X, y = _windows(z, w); ntr = len(X) - 12
    Xt = torch.tensor(X, dtype=torch.float32)[:, :, None]; yt = torch.tensor(y, dtype=torch.float32)[:, None]
    cell = {"RNN": nn.RNN, "LSTM": nn.LSTM, "GRU": nn.GRU}[kind](1, 32, batch_first=True); head = nn.Linear(32, 1)
    o = torch.optim.Adam(list(cell.parameters()) + list(head.parameters()), lr=5e-3)
    for _ in range(epochs):
        o.zero_grad(); out, _h = cell(Xt[:ntr]); ((head(out[:, -1]) - yt[:ntr]) ** 2).mean().backward(); o.step()
    with torch.no_grad():
        out, _h = cell(Xt[ntr:]); p = head(out[:, -1]).numpy()[:, 0]
    return np.exp(p * sd + mu)


@walk("m-rnn", "flights")
def _():
    torch = _torch()
    f, s = _flights()
    h = np.zeros(1); W = 0.5; U = 0.01
    trace = []
    for m in range(6):
        h = np.tanh(W * h + U * (s[m] - s[:12].mean()))
        trace.append({"month": f"{f['month'][m][:3]} {f['year'][m]}", "passengers (k)": int(s[m]), "hidden state h": h[0]})
    p = _seq_model(torch, "RNN", 12, s)
    act = s[-12:]
    tab = pd.DataFrame({"month": f["month"].values[-12:], "actual 1960": act.astype(int), "RNN forecast": p.round(0).astype(int), "last year's value": s[-24:-12].astype(int)})
    mape = lambda a, b: np.mean(np.abs(a - b) / a)
    return [
        ("Read one month at a time", f"An RNN keeps a hidden state h and updates it with every new value: h = tanh(W·h_prev + U·x). With toy weights W = 0.5, U = 0.01 on the real 1949 numbers:\n\n{t(pd.DataFrame(trace), nd=3)}\n\nh is a running summary of what it has read so far."),
        ("Train on 1949–1959", "A real RNN (32 hidden units) reads 12 months (log scale) and predicts month 13. It is trained on every 12-month window up to Dec 1959."),
        ("Forecast 1960 one month ahead", f"{t(tab)}\n\nAverage error: RNN **{pct(mape(act, p), 1)}**, 'same as last year' **{pct(mape(act, s[-24:-12]), 1)}**."),
    ], "An RNN reads a sequence step by step, carrying a hidden state that summarises everything so far."


@walk("m-lstm-gru", "flights")
def _():
    torch = _torch()
    f, s = _flights(); act = s[-12:]
    mape = lambda p: np.mean(np.abs(act - p) / act)
    rows = []
    for kind in ["RNN", "LSTM", "GRU"]:
        for w in [12, 36]:
            errs = [mape(_seq_model(torch, kind, w, s, seed=sd)) for sd in range(2)]
            rows.append({"cell": kind, "months read": w, "1960 error (avg of 2 runs)": pct(np.mean(errs), 1)})
    return [
        ("The problem with plain RNNs", "Every step multiplies the hidden state by the same weights, so information from many steps ago fades (vanishing gradients)."),
        ("Gates fix it", "LSTM adds a separate memory cell with a **forget gate** (keep or erase), an **input gate** (what to write) and an **output gate** (what to reveal). GRU merges these into two gates and is a bit smaller."),
        ("All three on the airline data", f"{t(pd.DataFrame(rows))}\n\nOn a short, smooth series like this the differences are small and can go either way: gated cells matter most when the useful information is far back, as in long sentences."),
    ], "LSTM and GRU add gates that decide what to keep, so they remember over longer stretches than a plain RNN."


@walk("m-seq2seq", "flights")
def _():
    torch = _torch(); nn = torch.nn
    f, s = _flights()
    ls = np.log(s); mu, sd = ls[:-12].mean(), ls[:-12].std(); z = (ls - mu) / sd
    W, H = 24, 12
    X = np.array([z[i:i + W] for i in range(len(z) - W - H + 1)]); Y = np.array([z[i + W:i + W + H] for i in range(len(z) - W - H + 1)])
    Xtr, Ytr = X[:-1], Y[:-1]
    torch.manual_seed(0)
    enc = nn.GRU(1, 32, batch_first=True); dec = nn.GRU(1, 32, batch_first=True); head = nn.Linear(32, 1)
    ps = list(enc.parameters()) + list(dec.parameters()) + list(head.parameters()); o = torch.optim.Adam(ps, lr=5e-3)
    xt = torch.tensor(Xtr, dtype=torch.float32)[:, :, None]; yt = torch.tensor(Ytr, dtype=torch.float32)[:, :, None]

    def run(x, y=None):
        _, h = enc(x); inp = x[:, -1:, :]; outs = []
        for k in range(H):
            out, h = dec(inp, h); p = head(out); outs.append(p)
            inp = y[:, k:k + 1, :] if y is not None else p
        return torch.cat(outs, 1)

    for _ in range(400):
        o.zero_grad(); ((run(xt, yt) - yt) ** 2).mean().backward(); o.step()
    with torch.no_grad():
        p = run(torch.tensor(X[-1:], dtype=torch.float32)[:, :, None]).numpy()[0, :, 0]
    p = np.exp(p * sd + mu); act = s[-12:]
    tab = pd.DataFrame({"month": f["month"].values[-12:], "actual 1960": act.astype(int), "seq2seq forecast (made in Dec 1959)": p.round(0).astype(int)})
    return [
        ("Encoder reads the input sequence", "The encoder GRU reads the 24 months Jan 1958 – Dec 1959 and compresses them into one hidden vector (32 numbers)."),
        ("Decoder writes the output sequence", "The decoder starts from that vector and produces 12 months, feeding each prediction back in as the next input. During training it was fed the true previous month instead (teacher forcing)."),
        ("All of 1960 in one go", f"{t(tab)}\n\nAverage error over 12 months ahead: **{pct(np.mean(np.abs(act - p) / act), 1)}**. Translation models work the same way: encoder reads a sentence, decoder writes the translation word by word."),
    ], "Seq2seq maps a whole input sequence to a whole output sequence through an encoder and a decoder."


@walk("m-time-series", "flights")
def _():
    from statsmodels.tsa.seasonal import seasonal_decompose
    f, s = _flights()
    ser = pd.Series(s, index=pd.period_range("1949-01", periods=len(s), freq="M").to_timestamp())
    dc = seasonal_decompose(np.log(ser), model="additive", period=12)
    seas = pd.Series(np.exp(dc.seasonal.values[:12]), index=f["month"].values[:12]).rename("seasonal factor")
    yr = f.groupby("year")["passengers"].sum()
    train, act = s[:-12], s[-12:]
    naive = np.repeat(train[-1], 12); snaive = train[-12:]
    growth = (train[-12:].sum() / train[-24:-12].sum()); sg = train[-12:] * growth
    mape = lambda p: np.mean(np.abs(act - p) / act)
    fc = pd.DataFrame([{"method": "naive (repeat Dec 1959)", "1960 error": pct(mape(naive), 1)}, {"method": "seasonal naive (repeat 1959)", "1960 error": pct(mape(snaive), 1)},
                       {"method": f"seasonal naive × last year's growth ({growth:.2f})", "1960 error": pct(mape(sg), 1)}])
    return [
        ("Trend", f"Yearly totals (thousands): {', '.join(f'{y}: {v:,}' for y, v in yr.items())}. Steady growth every year."),
        ("Seasonality", f"After removing the trend, each month's typical level relative to the year (log-additive decomposition):\n\n{t(seas.to_frame(), nd=3, index=True)}\n\nJuly and August are the summer peak; November is the low."),
        ("Simple forecasts for 1960 (trained on 1949–59)", f"{t(fc)}\n\nUsing both seasonality and trend beats ignoring them. Always compare fancy models with these baselines."),
    ], "A time series is trend + seasonality + noise; good forecasts model the first two and are checked on later data only."


@walk("m-ts-dl", "flights")
def _():
    torch = _torch(); nn = torch.nn
    f, s = _flights(); act = s[-12:]
    ls = np.log(s)
    X, y = _windows(ls, 12); ntr = len(X) - 12
    d = np.diff(ls); Xd, yd = _windows(d, 12)
    mape = lambda p: np.mean(np.abs(act - p) / act)
    rows = []
    torch.manual_seed(0)
    net = nn.Sequential(nn.Linear(12, 32), nn.ReLU(), nn.Linear(32, 1)); o = torch.optim.Adam(net.parameters(), lr=3e-3)
    Xt = torch.tensor(Xd, dtype=torch.float32); yt = torch.tensor(yd, dtype=torch.float32)[:, None]; n2 = len(Xd) - 12
    for _ in range(1500):
        o.zero_grad(); ((net(Xt[:n2]) - yt[:n2]) ** 2).mean().backward(); o.step()
    with torch.no_grad(): pd_ = net(Xt[n2:]).numpy()[:, 0]
    p_mlp = np.exp(ls[-13:-1] + pd_)
    p_lstm = _seq_model(torch, "LSTM", 12, s)
    g = np.array([s[i - 12] * s[i - 12:i].sum() / s[i - 24:i - 12].sum() for i in range(len(s) - 12, len(s))])
    rows = [{"model": "seasonal naive (same month last year)", "1960 error": pct(mape(s[-24:-12]), 1)},
            {"model": "same month last year × last 12 months' growth", "1960 error": pct(mape(g), 1)},
            {"model": "MLP on last 12 monthly changes", "1960 error": pct(mape(p_mlp), 1)},
            {"model": "LSTM on last 12 months (log level)", "1960 error": pct(mape(p_lstm), 1)}]
    win = pd.DataFrame({"input month": [f"{m[:3]} {y}" for m, y in zip(f["month"].values[-24:-12], f["year"].values[-24:-12])], "passengers": s[-24:-12].astype(int)})
    return [
        ("Turn the series into a supervised table", f"Each training row = 12 consecutive months as input, the next month as the answer. The last window before 1960:\n\n{t(win.T.reset_index(drop=True).set_axis(range(12), axis=1).iloc[[1]])}\n\n→ answer: Jan 1960 = {int(s[-12])}."),
        ("Make it easier to learn", "Take logs (growth becomes additive) and, for the MLP, predict the month-to-month change instead of the raw level. Train only on windows ending before 1960."),
        ("One-month-ahead forecasts for 1960", f"{t(pd.DataFrame(rows))}\n\n{"A one-line growth-adjusted baseline beats both networks here." if mape(g) < min(mape(p_mlp), mape(p_lstm)) else "The networks beat the simple baselines here."} With only ~130 training windows that's normal: deep models shine on long series or many related series."),
    ], "Deep time-series models learn from sliding windows; with little data, always check them against simple seasonal baselines."
