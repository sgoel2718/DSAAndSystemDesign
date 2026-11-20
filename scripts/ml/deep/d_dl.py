"""Deep layer + end-to-end walkthroughs: Deep learning."""
from deep.util import X

PENGUINS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
HOUSING = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
SMS = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
SONAR = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/sonar.csv"
TEMPS = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv"
AIR = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
SUNSPOTS = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-sunspots.csv"
FM = '''import gzip, urllib.request
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
get = lambda f, off: np.frombuffer(gzip.decompress(urllib.request.urlopen(base + f).read()), np.uint8, offset=off)
X = get("t10k-images-idx3-ubyte.gz", 16).reshape(-1, 1, 28, 28).astype(np.float32) / 255.0; y = get("t10k-labels-idx1-ubyte.gz", 8).astype(np.int64)
NAMES = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Boot"]
torch.manual_seed(0); Xt, yt = torch.tensor(X), torch.tensor(y); tr, te = torch.arange(8000), torch.arange(8000, 10000)'''
TRAIN = '''def fit(model, opt, epochs, Xa, ya, bs=128, loss_fn=torch.nn.functional.cross_entropy):
    for _ in range(epochs):
        model.train()
        for idx in torch.randperm(len(Xa)).split(bs):
            opt.zero_grad(); loss = loss_fn(model(Xa[idx]), ya[idx]); loss.backward(); opt.step()
    return loss.item()
@torch.no_grad()
def acc(model, Xa, ya): model.eval(); return (model(Xa).argmax(1) == ya).float().mean().item()'''

X("m-dl-intro",
  "Deep learning stacks many simple layers so the network learns its own features: edges → textures → parts → objects for images, characters → words → meaning for text. It wins when data is large and raw (pixels, audio, text); on small tabular data, gradient boosting often still wins.",
  """**Why depth works.** Each layer computes h = σ(Wx + b); composing layers builds hierarchical features, and depth can represent some functions with exponentially fewer units than a shallow net. Training = minimise a loss with stochastic gradient descent, gradients via backprop (automatic differentiation). Enablers since 2012: GPUs, large datasets, ReLU, better initialisation/normalisation, residual connections, Adam, and transformers (2017). **Inductive biases:** CNNs (locality, translation equivariance), RNNs (sequence order), transformers (attention, little bias but huge data), GNNs (graph structure).""",
  """**Parameter count by hand.** Input 784 → 128 → 10: (784·128 + 128) + (128·10 + 10) = 100,480 + 1,290 = **101,770** parameters. A CNN with 32 3×3 filters then 64 3×3 filters uses only (9·1·32 + 32) + (9·32·64 + 64) = 320 + 18,496 = **18,816** conv parameters — weight sharing.""",
  ["Reaching for deep learning on small tabular data", "Training without a baseline", "No validation set / early stopping", "Ignoring compute cost"],
  ["Images, audio, text, large datasets, transfer learning from pretrained models"], ["Small structured datasets where trees win; when interpretability is mandatory"],
  "Fashion-MNIST (10,000 real clothing images) — climb the ladder: logistic regression → MLP → small CNN, comparing accuracy, parameters and training time, and look at which classes improve.",
  ["Load images as tensors and split", "Softmax regression (no hidden layer)", "MLP with one hidden layer", "Small CNN", "Compare accuracy, parameters, time and per-class gains"],
  '''
import time, numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
models = {"logistic (linear)": nn.Sequential(nn.Flatten(), nn.Linear(784, 10)),
          "MLP 784-256-10": nn.Sequential(nn.Flatten(), nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 10)),
          "small CNN": nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(32 * 7 * 7, 10))}
per_class = {}
for name, m in models.items():
    t = time.perf_counter(); fit(m, torch.optim.Adam(m.parameters(), 1e-3), 5, Xt[tr], yt[tr])
    with torch.no_grad(): pred = m(Xt[te]).argmax(1)
    per_class[name] = [(pred[yt[te] == c] == c).float().mean().item() for c in range(10)]
    print(f"  {name:18s} test acc {acc(m, Xt[te], yt[te]):.3f} | params {sum(p.numel() for p in m.parameters()):7,d} | {time.perf_counter() - t:4.1f}s")
gain = np.array(per_class["small CNN"]) - np.array(per_class["logistic (linear)"])
print("biggest CNN gains over linear:", [(NAMES[i], round(float(gain[i]), 2)) for i in np.argsort(-gain)[:3]])
''')

X("m-nn-formulation",
  "A neural network is a function built by composing layers: each layer takes a vector, multiplies by a weight matrix, adds a bias and applies a non-linearity. The output layer and loss match the task (sigmoid + BCE for yes/no, softmax + cross-entropy for classes, linear + MSE for numbers). Training adjusts all weights to minimise the loss.",
  """**Forward pass.** h⁽⁰⁾ = x; z⁽ˡ⁾ = W⁽ˡ⁾h⁽ˡ⁻¹⁾ + b⁽ˡ⁾; h⁽ˡ⁾ = σ(z⁽ˡ⁾); output ŷ = g(z⁽ᴸ⁾). With a batch X (n×d): Z = XWᵀ + b. Without non-linearities the whole network collapses to one linear map (W₃W₂W₁ = W). **Universal approximation:** one hidden layer with enough units approximates any continuous function on a compact set — but depth makes it far more efficient. **Task heads:** regression → identity + MSE (Gaussian likelihood); binary → sigmoid + BCE; multiclass → softmax + CE; multi-label → K sigmoids. Training objective: empirical risk (1/n)Σ L(f(xᵢ; θ), yᵢ) + regulariser.""",
  """**Forward pass by hand.** x = [1, 2]; W₁ = [[0.5, −1], [1, 0.5]], b₁ = [0, 1] → z₁ = [0.5 − 2, 1 + 1 + 1] = [−1.5, 3] → ReLU → h = [0, 3]. W₂ = [[1, 2]], b₂ = −1 → z = 0 + 6 − 1 = 5 → sigmoid → **0.993**.""",
  ["Wrong output activation/loss pair (softmax + BCE, sigmoid + MSE for classes)", "Applying softmax before nn.CrossEntropyLoss (it expects logits)", "Forgetting non-linearities", "Shape mismatches between layers"],
  ["Any differentiable mapping from inputs to outputs; define the head by the task"], ["When a closed-form or classical model suffices"],
  "Penguins — the same network written three ways: NumPy forward pass by hand, PyTorch nn.Module, and nn.Sequential; verify they agree; then train three task heads (species: softmax/CE, Gentoo yes/no: sigmoid/BCE, body mass: linear/MSE) on one shared body.",
  ["Prepare features and three targets", "NumPy forward pass with explicit matrices", "Same weights in a PyTorch module — check outputs match", "Shared body with three heads and the right losses", "Train jointly and report each task's metric"],
  f'''
import numpy as np, pandas as pd, torch, torch.nn as nn
df = pd.read_csv("{PENGUINS}").dropna(); cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]
Xn = ((df[cols] - df[cols].mean()) / df[cols].std()).to_numpy(np.float32)
y_species = torch.tensor(pd.factorize(df.species)[0]); y_gentoo = torch.tensor((df.species == "Gentoo").to_numpy(np.float32)); y_mass = torch.tensor(((df.body_mass_g - 4200) / 800).to_numpy(np.float32))
torch.manual_seed(0); body = nn.Sequential(nn.Linear(3, 16), nn.ReLU(), nn.Linear(16, 16), nn.ReLU())
W1, b1, W2, b2 = (p.detach().numpy() for p in body.parameters())
h = np.maximum(np.maximum(Xn @ W1.T + b1, 0) @ W2.T + b2, 0)                     # forward pass by hand
print("NumPy forward == PyTorch forward:", np.allclose(h, body(torch.tensor(Xn)).detach().numpy(), atol=1e-6), "| hidden shape", h.shape)
class MultiHead(nn.Module):
    def __init__(self, body):
        super().__init__(); self.body = body; self.species = nn.Linear(16, 3); self.gentoo = nn.Linear(16, 1); self.mass = nn.Linear(16, 1)
    def forward(self, x):
        z = self.body(x); return self.species(z), self.gentoo(z).squeeze(1), self.mass(z).squeeze(1)    # logits, logit, value
net = MultiHead(body); opt = torch.optim.Adam(net.parameters(), 1e-2); X = torch.tensor(Xn)
print("parameters:", sum(p.numel() for p in net.parameters()))
for step in range(300):
    s, g, m = net(X)
    loss = nn.functional.cross_entropy(s, y_species) + nn.functional.binary_cross_entropy_with_logits(g, y_gentoo) + nn.functional.mse_loss(m, y_mass)
    opt.zero_grad(); loss.backward(); opt.step()
with torch.no_grad(): s, g, m = net(X)
print(f"species accuracy {{(s.argmax(1) == y_species).float().mean():.3f}} | Gentoo accuracy {{((g > 0).float() == y_gentoo).float().mean():.3f}} | mass RMSE {{800 * torch.sqrt(((m - y_mass) ** 2).mean()):.0f}} g")
print("probabilities for bird 0: species", torch.softmax(s[0], 0).numpy().round(3), "| P(Gentoo)", round(torch.sigmoid(g[0]).item(), 3))
''')

X("m-perceptron",
  "The perceptron is the original artificial neuron: a weighted sum of inputs, then a step function (fire or not). It learns by nudging weights toward misclassified examples. It can only draw straight-line boundaries — its failure on XOR motivated multi-layer networks.",
  """**Rule.** ŷ = sign(w·x + b). For each mistake (yᵢ(w·xᵢ + b) ≤ 0): w ← w + η·yᵢxᵢ, b ← b + η·yᵢ. Geometrically each update rotates w toward the misclassified point. **Convergence theorem (Novikoff):** if data are separable with margin γ and ‖x‖ ≤ R, the perceptron makes at most (R/γ)² mistakes. On non-separable data it never settles — use the **averaged** or **pocket** perceptron. It is SGD on the loss max(0, −y(w·x + b)); replacing it with the hinge max(0, 1 − y(w·x + b)) gives a linear SVM, with the logistic loss gives logistic regression.""",
  """**Updates by hand.** w = [0, 0], b = 0, η = 1. Point x = [2, 1], y = +1: score 0 → mistake → w = [2, 1], b = 1. Point x = [1, 3], y = −1: score 2 + 3 + 1 = 6 > 0 → mistake → w = [1, −2], b = 0. Point [2, 1] again: 2 − 2 + 0 = 0 → mistake → w = [3, −1], b = 1. Check [1, 3]: 3 − 3 + 1 = 1 > 0, still wrong → w = [2, −4], b = 0. Now [2, 1] scores 0 again… the boundary keeps being pushed toward each error until both sides are satisfied (here after a few more updates: e.g. w = [4, −3], b = 0 gives +5 and −5).""",
  ["Expecting convergence on non-separable data", "Unscaled features (slow convergence)", "Reading the perceptron's score as a probability"],
  ["Teaching, online learning on separable streams, as a building block of intuition"], ["Real classification tasks — use logistic regression/SVM"],
  "Sonar returns (rock vs mine) and penguins — perceptron from scratch with mistake counting, averaged perceptron, comparison with sklearn Perceptron and logistic regression, and the separable vs non-separable behaviour.",
  ["Prepare data with labels ±1", "Perceptron from scratch; count mistakes per epoch", "Averaged perceptron for non-separable data", "Separable case (Adelie vs Gentoo) converges", "Compare with sklearn Perceptron/LogisticRegression"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
def perceptron(A, t, epochs=50, average=False):
    w, b, ws, bs, history = np.zeros(A.shape[1]), 0.0, np.zeros(A.shape[1]), 0.0, []
    for _ in range(epochs):
        mistakes = 0
        for i in np.random.default_rng(len(history)).permutation(len(A)):
            if t[i] * (A[i] @ w + b) <= 0: w += t[i] * A[i]; b += t[i]; mistakes += 1
            ws += w; bs += b
        history.append(mistakes)
    return (ws / (epochs * len(A)), bs / (epochs * len(A)), history) if average else (w, b, history)
pg = pd.read_csv("{PENGUINS}").dropna(); pg = pg[pg.species.isin(["Adelie", "Gentoo"])]
A = StandardScaler().fit_transform(pg[["bill_depth_mm", "flipper_length_mm"]]); t = np.where(pg.species == "Gentoo", 1, -1)
w, b, hist = perceptron(A, t, 20); print("separable penguins: mistakes per epoch", hist[:8], "... ->", hist[-1])
df = pd.read_csv("{SONAR}", header=None); Xs, ys = df.iloc[:, :60].to_numpy(), np.where(df[60] == "M", 1, -1)
Xtr, Xte, ytr, yte = train_test_split(Xs, ys, test_size=0.3, stratify=ys, random_state=0); sc = StandardScaler().fit(Xtr); Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
w, b, hist = perceptron(Xtr, ytr, 50); print("sonar (not separable): mistakes per epoch", hist[::10], "-> never reaches 0")
print("last-weights perceptron test acc:", round((np.sign(Xte @ w + b) == yte).mean(), 3))
wa, ba, _ = perceptron(Xtr, ytr, 50, average=True); print("averaged perceptron test acc:", round((np.sign(Xte @ wa + ba) == yte).mean(), 3))
print("sklearn Perceptron:", round(Perceptron(random_state=0).fit(Xtr, ytr).score(Xte, yte), 3), "| logistic regression:", round(LogisticRegression(C=0.1, max_iter=2000).fit(Xtr, ytr).score(Xte, yte), 3))
''')

X("m-mlp",
  "A multi-layer perceptron stacks fully connected layers with non-linear activations, so it can model curved decision boundaries and interactions. It's the basic deep network for tabular features, embeddings, and the 'feed-forward' block inside every transformer.",
  """**Capacity and shape.** Width (units per layer) and depth (layers) set capacity; parameters ≈ Σ(dₗ₋₁·dₗ + dₗ). Each ReLU unit adds a 'hinge', so a ReLU MLP is a piecewise-linear function whose number of linear regions grows exponentially with depth. **Training recipe:** standardise inputs; He init; Adam (lr ≈ 1e-3); batch 32–256; early stopping; dropout/weight decay; BatchNorm/LayerNorm for deeper nets. On tabular data, MLPs need careful tuning and usually trail gradient boosting; with embeddings for categoricals and enough data they become competitive.""",
  """**Regions by hand.** One hidden layer with 2 ReLU units on 1-D input: h₁ = max(0, x), h₂ = max(0, x − 1); output = h₁ − 2h₂ → slope 1 up to x = 1, then slope −1: a tent shape from just two hinges. **Params:** 784 → 512 → 256 → 10 = 401,920 + 131,328 + 2,570 = **535,818**.""",
  ["Not scaling inputs", "Too large learning rate / no early stopping", "Very wide nets on small data (memorisation)", "Comparing against no baseline"],
  ["Medium/large tabular data, embeddings, as a head on pretrained features"], ["Small tabular datasets (use boosting), images/sequences (use CNNs/transformers)"],
  "Fashion-MNIST (images as 784 features) and California housing (tabular) — study width and depth, train with a validation split and early stopping in PyTorch, and compare the housing MLP with gradient boosting.",
  ["Load and standardise", "MLPs of different widths/depths on Fashion-MNIST", "Training loop with validation-based early stopping", "MLP on housing vs HistGradientBoosting", "Report parameters vs accuracy"],
  '''
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
''' + FM + "\n" + TRAIN + '''
def mlp(sizes): layers = [nn.Flatten()]; [layers.extend([nn.Linear(a, b), nn.ReLU()]) for a, b in zip(sizes[:-2], sizes[1:-1])]; return nn.Sequential(*layers, nn.Linear(sizes[-2], sizes[-1]))
for sizes in [[784, 32, 10], [784, 256, 10], [784, 256, 256, 10], [784, 512, 256, 128, 10]]:
    m = mlp(sizes); fit(m, torch.optim.Adam(m.parameters(), 1e-3), 6, Xt[tr], yt[tr])
    print(f"  {'-'.join(map(str, sizes)):18s} params {sum(p.numel() for p in m.parameters()):7,d} | test acc {acc(m, Xt[te], yt[te]):.3f}")
h = pd.read_csv("HOUSING").dropna(); yv = np.log(h.pop("median_house_value")).to_numpy(np.float32); Xh = pd.get_dummies(h, dtype=float).to_numpy(np.float32)
A, B, ya, yb = train_test_split(Xh, yv, test_size=0.2, random_state=0); A, V, ya, yv2 = train_test_split(A, ya, test_size=0.15, random_state=0)
sc = StandardScaler().fit(A); A, V, B = (torch.tensor(sc.transform(M), dtype=torch.float32) for M in (A, V, B)); ya, yv2 = torch.tensor(ya), torch.tensor(yv2)
net = nn.Sequential(nn.Linear(A.shape[1], 128), nn.ReLU(), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 1)); opt = torch.optim.Adam(net.parameters(), 1e-3)
best, bad, state = 1e9, 0, None
for epoch in range(200):
    fit(net, opt, 1, A, ya, bs=256, loss_fn=lambda p, t: nn.functional.mse_loss(p.squeeze(1), t))
    with torch.no_grad(): v = nn.functional.mse_loss(net(V).squeeze(1), yv2).item()
    if v < best - 1e-4: best, bad, state = v, 0, {k: x.clone() for k, x in net.state_dict().items()}
    else: bad += 1
    if bad == 15: break
net.load_state_dict(state)
with torch.no_grad(): rm = float(np.sqrt(((net(B).squeeze(1).numpy() - yb) ** 2).mean()))
gb = HistGradientBoostingRegressor(random_state=0).fit(sc.inverse_transform(A.numpy()), ya.numpy())
print(f"housing: MLP stopped at epoch {epoch + 1}, test RMSE {rm:.3f} (log $) | gradient boosting {np.sqrt(((gb.predict(sc.inverse_transform(B.numpy())) - yb) ** 2).mean()):.3f}")
'''.replace('"HOUSING"', '"' + HOUSING + '"'))

X("m-activations",
  "Activation functions add the non-linearity that lets networks learn curves. **Sigmoid/tanh** squash values and saturate (tiny gradients); **ReLU** is cheap and keeps gradients alive for positive inputs but can 'die'; **Leaky ReLU, ELU, GELU, SiLU/Swish** smooth or fix those issues. Output activations (sigmoid, softmax, identity) are chosen by the task.",
  """**Formulas and derivatives.** σ(z) = 1/(1 + e^(−z)), σ′ = σ(1 − σ) ≤ 0.25. tanh′ = 1 − tanh² ≤ 1 (zero-centred). ReLU = max(0, z), derivative 1 or 0 — if a unit's input is always negative it never updates ('dead ReLU'). Leaky ReLU: max(αz, z). ELU: z if z > 0 else α(eᶻ − 1). **GELU** = z·Φ(z) (used in BERT/GPT); **SiLU/Swish** = z·σ(z) (used in modern CNNs and LLaMA's SwiGLU). Through L sigmoid layers the gradient is multiplied by ≤ 0.25ᴸ — the vanishing-gradient problem; ReLU-family activations avoid that for active units.""",
  """**By hand at z = 2 and z = −2.** sigmoid 0.881 / 0.119, derivative 0.105 both. tanh 0.964 / −0.964, derivative 0.071. ReLU 2 / 0, derivative 1 / **0**. Leaky (0.01) −0.02 at −2, derivative 0.01. GELU(2) = 2·0.977 = **1.95**; GELU(−2) = −2·0.0228 = **−0.046**.""",
  ["Sigmoid/tanh in deep hidden stacks", "High learning rates causing many dead ReLUs", "Applying softmax inside the model and again in the loss", "ReLU at the output of a regression that needs negatives"],
  ["ReLU/GELU/SiLU for hidden layers; sigmoid/softmax/identity at the output by task"], ["Sigmoid in deep hidden layers (except gates in LSTMs/attention)"],
  "Fashion-MNIST — the same 6-layer MLP with sigmoid, tanh, ReLU, Leaky ReLU, GELU and SiLU: compare accuracy after equal training, gradient size reaching the first layer, and the fraction of dead ReLU units at a high learning rate.",
  ["Tabulate activation values and derivatives", "Build the same deep MLP with each activation", "Train equally; compare accuracy", "Measure first-layer gradient norm", "Count dead ReLUs after high-LR training"],
  '''
import numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
z = torch.tensor([-2.0, 0.0, 2.0], requires_grad=True)
for name, f in [("sigmoid", torch.sigmoid), ("tanh", torch.tanh), ("relu", torch.relu), ("gelu", nn.functional.gelu), ("silu", nn.functional.silu)]:
    out = f(z); g, = torch.autograd.grad(out.sum(), z); print(f"  {name:8s} f={out.detach().numpy().round(3)} f'={g.numpy().round(3)}")
ACTS = {"sigmoid": nn.Sigmoid, "tanh": nn.Tanh, "relu": nn.ReLU, "leaky_relu": nn.LeakyReLU, "gelu": nn.GELU, "silu": nn.SiLU}
def deep(act): layers = [nn.Flatten(), nn.Linear(784, 128), act()]; [layers.extend([nn.Linear(128, 128), act()]) for _ in range(5)]; return nn.Sequential(*layers, nn.Linear(128, 10))
for name, act in ACTS.items():
    torch.manual_seed(0); m = deep(act); opt = torch.optim.SGD(m.parameters(), 0.05)
    m.train(); loss = nn.functional.cross_entropy(m(Xt[tr[:512]]), yt[tr[:512]]); loss.backward(); g1 = m[1].weight.grad.norm().item(); opt.zero_grad()
    fit(m, opt, 4, Xt[tr], yt[tr]); print(f"  {name:10s} first-layer grad norm at init {g1:.2e} | test acc after 4 epochs (SGD) {acc(m, Xt[te], yt[te]):.3f}")
torch.manual_seed(0); m = deep(nn.ReLU); fit(m, torch.optim.SGD(m.parameters(), 0.8), 2, Xt[tr], yt[tr])
with torch.no_grad():
    h, dead = Xt[te].flatten(1), []
    for layer in list(m)[1:-1]:
        h = layer(h)
        if isinstance(layer, nn.ReLU): dead.append(round(((h > 0).sum(0) == 0).float().mean().item(), 2))
print("dead-ReLU fraction per layer after lr=0.8 training:", dead)
''')

X("m-loss-functions",
  "The loss turns 'how wrong is the model?' into a number to minimise, and choosing it is choosing what the model optimises: MSE chases the mean and punishes big errors, MAE chases the median and shrugs off outliers, Huber blends both, cross-entropy trains calibrated class probabilities, and specialised losses handle ranking, imbalance (focal), quantiles and similarity (contrastive/triplet).",
  """**Maximum-likelihood view.** MSE = Gaussian noise; MAE = Laplace noise; cross-entropy = categorical likelihood; Poisson loss = count data. Gradients: MSE ∂/∂ŷ = 2(ŷ − y) (grows with error); MAE sign(ŷ − y) (constant); Huber_δ: quadratic for |e| ≤ δ, linear beyond. **Cross-entropy with softmax:** ∂L/∂z = p − y (simple, well-scaled); MSE on probabilities gives tiny gradients when confidently wrong. **Focal loss** −(1 − pₜ)^γ log pₜ down-weights easy examples (dense detection, imbalance). **Pinball** loss trains quantiles. **Contrastive/triplet**: max(0, d(a, p) − d(a, n) + m) learns embeddings.""",
  """**Outlier by hand.** Targets [10, 11, 12, 50]: the constant minimising MSE is the mean **20.75**; MAE → median **11.5**; Huber (δ = 2) → ≈ 11.7. **CE vs MSE on a confident mistake:** p(true) = 0.01 → CE = 4.6 with gradient on the logit ≈ −0.99; MSE on probability = 0.98 but gradient through the saturated sigmoid ≈ 2·0.99·0.0099 = **0.02** — learning stalls.""",
  ["MSE when outliers are present and shouldn't dominate", "Applying softmax before nn.CrossEntropyLoss", "MSE for classification", "Forgetting class weights / focal loss for heavy imbalance"],
  ["Pick the loss that matches the business cost and noise model"], ["Optimising one loss but judging the model by an unrelated metric"],
  "California housing with 3% corrupted labels (regression: MSE vs MAE vs Huber, by error on clean test data) and Fashion-MNIST (classification: cross-entropy vs MSE on probabilities vs focal loss; learning speed and calibration).",
  ["Corrupt a few housing labels", "Train the same network with MSE, MAE, Huber; evaluate on clean data", "Classification with CE vs MSE-on-softmax", "Focal loss implementation", "Compare accuracy and confidence calibration"],
  '''
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
''' + FM + "\n" + TRAIN + '''
h = pd.read_csv("HOUSING").dropna(); yv = (h.pop("median_house_value") / 1e5).to_numpy(np.float32); Xh = StandardScaler().fit_transform(pd.get_dummies(h, dtype=float)).astype(np.float32)
A, B, ya, yb = train_test_split(Xh, yv, test_size=0.25, random_state=0); rng = np.random.default_rng(0); bad = rng.choice(len(ya), len(ya) * 3 // 100, replace=False); ya = ya.copy(); ya[bad] *= 10
A, B, ya, yb = map(torch.tensor, (A, B, ya, yb))
for name, lf in [("MSE", nn.functional.mse_loss), ("MAE", nn.functional.l1_loss), ("Huber δ=1", nn.functional.huber_loss)]:
    torch.manual_seed(0); net = nn.Sequential(nn.Linear(A.shape[1], 64), nn.ReLU(), nn.Linear(64, 1))
    fit(net, torch.optim.Adam(net.parameters(), 3e-3), 20, A, ya, bs=256, loss_fn=lambda p, t: lf(p.squeeze(1), t))
    with torch.no_grad(): e = net(B).squeeze(1) - yb
    print(f"  regression with {name:9s}: clean-test MAE ${e.abs().mean() * 1e5:,.0f} | median error ${e.median() * 1e5:+,.0f}")
def focal(logits, t, gamma=2.0):
    logp = torch.log_softmax(logits, 1).gather(1, t[:, None]).squeeze(1); return (-(1 - logp.exp()) ** gamma * logp).mean()
losses = {"cross-entropy": nn.functional.cross_entropy, "MSE on softmax": lambda z, t: ((torch.softmax(z, 1) - nn.functional.one_hot(t, 10).float()) ** 2).sum(1).mean(), "focal γ=2": focal}
for name, lf in losses.items():
    torch.manual_seed(0); m = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10)); fit(m, torch.optim.SGD(m.parameters(), 0.1), 2, Xt[tr], yt[tr], loss_fn=lf)
    with torch.no_grad(): p = torch.softmax(m(Xt[te]), 1); conf, pred = p.max(1)
    print(f"  {name:15s} acc {(pred == yt[te]).float().mean():.3f} | mean confidence {conf.mean():.3f} (gap to accuracy = calibration error)")
'''.replace('"HOUSING"', '"' + HOUSING + '"'))

X("m-backprop",
  "Backpropagation computes how much every weight contributed to the loss by applying the chain rule backwards through the network, reusing intermediate results. One forward pass plus one backward pass gives all gradients at roughly the cost of two forward passes — the reason training million-parameter models is feasible.",
  """**Derivation for a 2-layer net.** z₁ = W₁x + b₁, h = ReLU(z₁), z₂ = W₂h + b₂, p = softmax(z₂), L = −log p_y. Backward: δ₂ = ∂L/∂z₂ = p − onehot(y); ∂L/∂W₂ = δ₂hᵀ, ∂L/∂b₂ = δ₂; ∂L/∂h = W₂ᵀδ₂; δ₁ = (W₂ᵀδ₂) ⊙ 1[z₁ > 0]; ∂L/∂W₁ = δ₁xᵀ, ∂L/∂b₁ = δ₁. Batched: average over rows (ΔW = δᵀX/n). **Reverse-mode autodiff** generalises this to any computational graph: each op stores what it needs in the forward pass and multiplies the upstream gradient by its local Jacobian. Always verify custom gradients with a **finite-difference check** (relative error ~1e-7 in float64).""",
  """**Scalar example.** x = 2, w₁ = 0.5, w₂ = −3, y = 1, L = ½(ŷ − y)² with ŷ = w₂·ReLU(w₁x). Forward: z = 1, h = 1, ŷ = −3, L = 8. Backward: ∂L/∂ŷ = −4; ∂L/∂w₂ = −4·h = **−4**; ∂L/∂h = −4·w₂ = 12; ∂L/∂z = 12·1 = 12; ∂L/∂w₁ = 12·x = **24**.""",
  ["Forgetting the activation derivative mask", "Not averaging over the batch", "Wrong transpose in weight gradients", "Skipping gradient checks for hand-written layers"],
  ["Understanding/debugging training; writing custom layers"], ["Hand-deriving gradients in production — use autograd"],
  "Penguins species classification — a 2-layer network trained with backprop written entirely in NumPy; gradient check against finite differences and against PyTorch autograd; training curve and accuracy.",
  ["Prepare inputs and one-hot labels", "Forward pass that caches intermediates", "Backward pass with the chain rule", "Gradient check (finite differences + autograd)", "Train with gradient descent; report accuracy"],
  f'''
import numpy as np, pandas as pd, torch
df = pd.read_csv("{PENGUINS}").dropna(); cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
X = ((df[cols] - df[cols].mean()) / df[cols].std()).to_numpy(); y = pd.factorize(df.species)[0]; Y = np.eye(3)[y]
rng = np.random.default_rng(0); P = {{"W1": rng.normal(0, 0.5, (16, 4)), "b1": np.zeros(16), "W2": rng.normal(0, 0.5, (3, 16)), "b2": np.zeros(3)}}
def forward(P, X):
    z1 = X @ P["W1"].T + P["b1"]; h = np.maximum(z1, 0); z2 = h @ P["W2"].T + P["b2"]
    e = np.exp(z2 - z2.max(1, keepdims=True)); p = e / e.sum(1, keepdims=True); return p, (z1, h)
def loss(P, X, Y): return -np.mean(np.log(forward(P, X)[0][Y.astype(bool)]))
def backward(P, X, Y):
    p, (z1, h) = forward(P, X); n = len(X); d2 = (p - Y) / n                           # dL/dz2
    d1 = (d2 @ P["W2"]) * (z1 > 0)                                                    # dL/dz1 (ReLU mask)
    return {{"W2": d2.T @ h, "b2": d2.sum(0), "W1": d1.T @ X, "b1": d1.sum(0)}}
G = backward(P, X, Y); eps = 1e-6; worst = 0
for k in P:
    for idx in [tuple(rng.integers(0, s) for s in P[k].shape) for _ in range(5)]:
        old = P[k][idx]; P[k][idx] = old + eps; up = loss(P, X, Y); P[k][idx] = old - eps; dn = loss(P, X, Y); P[k][idx] = old
        worst = max(worst, abs((up - dn) / (2 * eps) - G[k][idx]) / (abs(G[k][idx]) + 1e-12))
print(f"finite-difference check: worst relative error {{worst:.1e}}")
T = {{k: torch.tensor(v, requires_grad=True) for k, v in P.items()}}
z = torch.relu(torch.tensor(X) @ T["W1"].T + T["b1"]) @ T["W2"].T + T["b2"]; torch.nn.functional.cross_entropy(z, torch.tensor(y)).backward()
print("matches PyTorch autograd:", all(np.allclose(G[k], T[k].grad.numpy(), atol=1e-10) for k in P))
for step in range(1, 501):
    G = backward(P, X, Y); P = {{k: P[k] - 0.5 * G[k] for k in P}}
    if step in (1, 10, 100, 500): print(f"  step {{step:3d}}: loss {{loss(P, X, Y):.4f}} accuracy {{(forward(P, X)[0].argmax(1) == y).mean():.3f}}")
''')

X("m-optimizers",
  "Optimisers decide how to turn gradients into weight updates. Plain **SGD** takes steps proportional to the gradient; **momentum** builds up speed in consistent directions; **RMSprop/Adam** adapt the step size per parameter; **AdamW** fixes weight decay for Adam. Learning-rate **schedules** (warm-up, cosine, one-cycle) often matter as much as the optimiser.",
  """**Updates.** SGD: θ ← θ − ηg. Momentum: v ← βv + g; θ ← θ − ηv (β ≈ 0.9; Nesterov looks ahead). RMSprop: s ← ρs + (1−ρ)g²; θ ← θ − ηg/(√s + ε). **Adam:** m ← β₁m + (1−β₁)g; s ← β₂s + (1−β₂)g²; bias-corrected m̂ = m/(1−β₁ᵗ), ŝ = s/(1−β₂ᵗ); θ ← θ − η m̂/(√ŝ + ε) (defaults 0.9, 0.999, 1e-8). **AdamW:** θ ← θ − η(m̂/(√ŝ+ε) + λθ) — decoupled decay (L2 inside Adam gets rescaled and weakens). Schedules: linear warm-up avoids early instability (essential for transformers); cosine decay to ~0; one-cycle. SGD+momentum often generalises slightly better for CNNs; Adam/AdamW is the default for transformers.""",
  """**First Adam step by hand.** g = 0.2, η = 0.001. m = 0.1·0.2 = 0.02 → m̂ = 0.02/0.1 = 0.2; s = 0.001·0.04 = 0.00004 → ŝ = 0.04 → step = 0.001·0.2/0.2 = **0.001** — Adam's first step has size ≈ η regardless of gradient scale. Momentum with constant g: v → g/(1 − β) = **10g** (effective lr ×10).""",
  ["Same learning rate for every optimiser", "L2 penalty with Adam instead of AdamW", "No warm-up for large/transformer models", "Never trying a learning-rate range test"],
  ["AdamW as a default; SGD+momentum for CNNs when tuning time allows; always a schedule"], ["Changing optimiser before checking the learning rate"],
  "Fashion-MNIST MLP — SGD, momentum, Nesterov, RMSprop, Adam and AdamW at sensible learning rates; loss after each epoch; one-cycle and cosine schedules; and Adam implemented by hand on a 2-D function to watch the bias correction.",
  ["Fix a model, data and budget", "Train with each optimiser; record epoch losses", "Add cosine and one-cycle schedules", "Implement Adam by hand on the Rosenbrock function", "Compare final test accuracies"],
  '''
import numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
def model(): torch.manual_seed(0); return nn.Sequential(nn.Flatten(), nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 10))
OPTS = {"SGD lr0.05": lambda p: torch.optim.SGD(p, 0.05), "momentum": lambda p: torch.optim.SGD(p, 0.05, momentum=0.9), "nesterov": lambda p: torch.optim.SGD(p, 0.05, momentum=0.9, nesterov=True),
        "RMSprop": lambda p: torch.optim.RMSprop(p, 1e-3), "Adam": lambda p: torch.optim.Adam(p, 1e-3), "AdamW wd0.05": lambda p: torch.optim.AdamW(p, 1e-3, weight_decay=0.05)}
for name, make in OPTS.items():
    m = model(); opt = make(m.parameters()); losses = [round(fit(m, opt, 1, Xt[tr], yt[tr]), 3) for _ in range(4)]
    print(f"  {name:13s} batch loss per epoch {losses} | test acc {acc(m, Xt[te], yt[te]):.3f}")
for name in ["cosine", "one-cycle"]:
    m = model(); opt = torch.optim.SGD(m.parameters(), 0.05, momentum=0.9); steps = 4 * len(tr.split(128))
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps) if name == "cosine" else torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=0.2, total_steps=steps)
    for _ in range(4):
        for idx in torch.randperm(len(tr)).split(128):
            opt.zero_grad(); nn.functional.cross_entropy(m(Xt[tr][idx]), yt[tr][idx]).backward(); opt.step(); sch.step()
    print(f"  momentum + {name:9s} schedule: test acc {acc(m, Xt[te], yt[te]):.3f}")
f = lambda x, y: (1 - x) ** 2 + 100 * (y - x * x) ** 2
grad = lambda x, y: np.array([-2 * (1 - x) - 400 * x * (y - x * x), 200 * (y - x * x)])
th, m_, s_ = np.array([-1.5, 2.0]), np.zeros(2), np.zeros(2)
for t in range(1, 5001):
    g = grad(*th); m_ = 0.9 * m_ + 0.1 * g; s_ = 0.999 * s_ + 0.001 * g * g
    th -= 0.02 * (m_ / (1 - 0.9 ** t)) / (np.sqrt(s_ / (1 - 0.999 ** t)) + 1e-8)
    if t in (1, 100, 1000, 5000): print(f"  hand-written Adam on Rosenbrock, step {t:4d}: θ={th.round(3)} f={f(*th):.4f}")
''')

X("m-init-norm",
  "How you **initialise** weights decides whether signals and gradients survive many layers; **normalisation** layers (BatchNorm, LayerNorm, GroupNorm, RMSNorm) keep activations in a healthy range during training. Together they make deep networks trainable with higher learning rates and less fiddling.",
  """**Variance preservation.** For z = Σᵢ wᵢxᵢ with n inputs, Var(z) = n·Var(w)·Var(x). Keep Var(z) ≈ Var(x): **Xavier/Glorot** Var(w) = 2/(n_in + n_out) for tanh/sigmoid; **He/Kaiming** Var(w) = 2/n_in for ReLU (ReLU zeroes half the signal). Too small → activations shrink to 0 layer by layer; too large → explode. **BatchNorm:** x̂ = (x − μ_B)/√(σ²_B + ε), y = γx̂ + β, batch statistics in training, running averages at inference; allows larger learning rates; depends on batch size. **LayerNorm:** normalise across features of each example (transformers, RNNs, batch-size independent). **RMSNorm:** divide by RMS only (LLaMA). Residual connections + normalisation enable 100+ layers.""",
  """**Variance by hand.** n = 256 inputs with Var(x) = 1. Weights N(0, 0.01²): Var(z) = 256·0.0001 = **0.0256** → std shrinks ~6× per layer → after 5 layers ~1e-4. He: Var(w) = 2/256 → Var(z) = 2, ReLU halves it → **1** — stable at any depth.""",
  ["Default tiny-normal init in deep nets", "Forgetting model.eval() (BatchNorm uses batch stats at test time)", "BatchNorm with batch size 2", "Normalising the test set with its own statistics"],
  ["He init for ReLU nets, Xavier for tanh; BatchNorm in CNNs; LayerNorm/RMSNorm in transformers/RNNs"], ["BatchNorm with tiny or highly variable batches (use GroupNorm/LayerNorm)"],
  "Fashion-MNIST — a 10-layer ReLU MLP: activation standard deviation per layer under small-normal, Xavier and He initialisation, then training curves without normalisation, with BatchNorm and with LayerNorm; plus the train/eval BatchNorm pitfall.",
  ["Build a 10-layer MLP and initialise three ways", "Track activation std through the layers", "Train each init (no normalisation)", "Add BatchNorm and LayerNorm; compare", "Show the train() vs eval() difference for BatchNorm"],
  '''
import numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
def deep(norm=None, depth=10):
    layers, d = [nn.Flatten(), nn.Linear(784, 256)], 256
    for _ in range(depth - 1): layers += ([norm(d)] if norm else []) + [nn.ReLU(), nn.Linear(d, d)]
    return nn.Sequential(*layers, nn.ReLU(), nn.Linear(d, 10))
def init(m, how):
    for l in m:
        if isinstance(l, nn.Linear):
            {"small normal": lambda w: nn.init.normal_(w, 0, 0.01), "xavier": nn.init.xavier_normal_, "he": lambda w: nn.init.kaiming_normal_(w, nonlinearity="relu")}[how](l.weight); nn.init.zeros_(l.bias)
    return m
for how in ["small normal", "xavier", "he"]:
    torch.manual_seed(0); m = init(deep(), how); h, stds = Xt[te[:512]].flatten(1), []
    with torch.no_grad():
        for l in list(m)[1:]:
            h = l(h)
            if isinstance(l, nn.ReLU): stds.append(round(h.std().item(), 4))
    fit(m, torch.optim.SGD(m.parameters(), 0.05, momentum=0.9), 3, Xt[tr], yt[tr])
    print(f"  {how:12s} activation std per layer {stds[:3]}...{stds[-2:]} | test acc after training {acc(m, Xt[te], yt[te]):.3f}")
for name, norm in [("BatchNorm", nn.BatchNorm1d), ("LayerNorm", nn.LayerNorm)]:
    torch.manual_seed(0); m = init(deep(norm), "small normal"); fit(m, torch.optim.SGD(m.parameters(), 0.05, momentum=0.9), 3, Xt[tr], yt[tr])
    print(f"  small-normal init + {name}: test acc {acc(m, Xt[te], yt[te]):.3f}  (normalisation rescues bad init)")
torch.manual_seed(0); m = init(deep(nn.BatchNorm1d), "he"); fit(m, torch.optim.SGD(m.parameters(), 0.05, momentum=0.9), 2, Xt[tr], yt[tr])
with torch.no_grad(): m.eval(); ev = (m(Xt[te]).argmax(1) == yt[te]).float().mean().item(); m.train(); trm = (m(Xt[te[:32]]).argmax(1) == yt[te[:32]]).float().mean().item()
print(f"BatchNorm eval() accuracy {ev:.3f} vs train-mode on a batch of 32 {trm:.3f} (always call model.eval() for inference)")
''')

X("m-vanishing",
  "In deep or recurrent networks the gradient is a long product of factors; if they're mostly < 1 it **vanishes** (early layers stop learning), if > 1 it **explodes** (training blows up). Fixes: ReLU-family activations, good initialisation, normalisation, **residual connections**, gating (LSTM/GRU) and **gradient clipping**.",
  """**Why.** By the chain rule ∂L/∂h₁ = ∂L/∂h_L · Πₗ (∂hₗ₊₁/∂hₗ) with each Jacobian = Wₗ·diag(σ′(zₗ)). With sigmoid σ′ ≤ 0.25, 20 layers give ≤ 0.25²⁰ ≈ 10⁻¹² (unless weights compensate). In RNNs the same W is multiplied T times: its largest singular value > 1 → explosion, < 1 → vanishing. **Residual block** h_{l+1} = h_l + F(h_l) gives Jacobian I + ∂F/∂h, so a direct gradient path exists ('gradient highway'). **Clipping by norm:** if ‖g‖ > c then g ← c·g/‖g‖ — keeps the direction, bounds the step.""",
  """**Product by hand.** 10 layers each multiplying the gradient by 0.5 → 0.5¹⁰ ≈ **0.001**; by 1.5 → 1.5¹⁰ ≈ **57.7**. With a residual path each factor becomes 1 + 0.5 or 1 − 0.5 around 1 — gradients stay O(1). **Clipping:** g = [30, 40] (norm 50), max norm 5 → **[3, 4]**.""",
  ["Deep sigmoid/tanh stacks without residuals", "Not monitoring gradient norms", "Clipping by value (changes direction) when by-norm was intended", "Huge learning rates mistaken for 'exploding gradients'"],
  ["Diagnose with per-layer gradient norms; fix with ReLU/He/residuals/normalisation/clipping"], ["Plain RNNs for long dependencies — use LSTM/GRU or transformers"],
  "Fashion-MNIST — 30-layer plain sigmoid network vs plain ReLU vs residual ReLU: gradient norm at every layer and training progress; then an exploding case (large init) rescued by gradient-norm clipping.",
  ["Build plain and residual 30-layer networks", "Measure gradient norm per layer on one batch", "Train each for the same budget", "Create exploding gradients with a large init", "Apply clip_grad_norm_ and compare"],
  '''
import numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
import math
class Net(nn.Module):
    def __init__(self, act, residual, depth=30, gain=1.0):
        super().__init__(); self.inp = nn.Linear(784, 64); self.layers = nn.ModuleList(nn.Linear(64, 64) for _ in range(depth)); self.out = nn.Linear(64, 10)
        self.act, self.res, self.alpha = act, residual, 1 / math.sqrt(depth)
        for l in self.layers: nn.init.normal_(l.weight, 0, gain / math.sqrt(64)); nn.init.zeros_(l.bias)
    def forward(self, x):
        h = self.act(self.inp(x.flatten(1)))
        for l in self.layers: h = h + self.alpha * self.act(l(h)) if self.res else self.act(l(h))      # residual: identity path + scaled branch
        return self.out(h)
for name, act, res, gain in [("plain sigmoid", torch.sigmoid, False, 1.0), ("plain ReLU, gain 1", torch.relu, False, 1.0), ("plain ReLU, He gain √2", torch.relu, False, 2 ** 0.5), ("residual ReLU", torch.relu, True, 2 ** 0.5)]:
    torch.manual_seed(0); m = Net(act, res, gain=gain); nn.functional.cross_entropy(m(Xt[tr[:256]]), yt[tr[:256]]).backward()
    g = [l.weight.grad.norm().item() for l in m.layers]; m.zero_grad()
    fit(m, torch.optim.Adam(m.parameters(), 1e-3), 3, Xt[tr], yt[tr])
    print(f"  {name:23s} grad norm layer1 {g[0]:.1e} | layer15 {g[14]:.1e} | layer30 {g[-1]:.1e} | acc after 3 epochs {acc(m, Xt[te], yt[te]):.3f}")
for clip in [None, 1.0]:                                  # high learning rate -> gradient spikes; clipping keeps steps bounded
    torch.manual_seed(0); m = Net(torch.relu, False, gain=2 ** 0.5); opt = torch.optim.SGD(m.parameters(), 0.1, momentum=0.9); norms = []
    for idx in torch.randperm(len(tr))[:3840].split(128):
        opt.zero_grad(); loss = nn.functional.cross_entropy(m(Xt[tr][idx]), yt[tr][idx]); loss.backward()
        norms.append(nn.utils.clip_grad_norm_(m.parameters(), clip if clip else float("inf")).item()); opt.step()
    print(f"  SGD lr 0.1, clip={clip}: largest grad norm seen {max(norms):.1e} | final loss {loss.item():.3f} | acc {acc(m, Xt[te], yt[te]):.3f}")
''')

X("m-dl-regularization",
  "Deep networks have enough capacity to memorise their training set, so they need regularisation: **weight decay** (small weights), **dropout** (randomly silence units), **data augmentation** (more varied data), **early stopping** (stop when validation stops improving), **label smoothing**, and simply **more data**. Usually several are combined.",
  """**Mechanisms.** Weight decay adds λ‖θ‖² (with AdamW: decoupled decay). **Dropout:** during training multiply each activation by Bernoulli(1 − p)/(1 − p) (inverted dropout keeps the expected value), at test time use all units — approximates an ensemble of 2ⁿ thinned networks and prevents co-adaptation. **Early stopping:** effective regulariser equivalent to limiting how far weights travel from init (≈ L2 for linear models). **Augmentation** encodes invariances (flips, crops, noise). **Label smoothing:** target 1 − ε for the true class, ε/(K−1) others → less over-confident. **Mixup** trains on convex combinations of examples.""",
  """**Inverted dropout by hand.** p = 0.5, activations [2, 4, 6, 8], mask [1, 0, 1, 0] → [2, 0, 6, 0]/0.5 = **[4, 0, 12, 0]**; expected value of each unit stays the same as without dropout. **Label smoothing** ε = 0.1, K = 10: target vector = 0.9 for the true class, 0.0111 for each other.""",
  ["Dropout left on at inference (forgetting model.eval())", "Augmentations that change the label (flipping digits 6/9)", "Early stopping on the test set", "Stacking every regulariser at maximum strength (underfit)"],
  ["Small or medium datasets, large models, any time train ≫ validation accuracy"], ["Already underfitting models"],
  "Fashion-MNIST with only 1,000 training images (to force overfitting) — baseline vs dropout vs weight decay vs augmentation vs label smoothing vs all combined, with early stopping on a validation set, comparing the train–test gap.",
  ["Take a small training subset, a validation set and a test set", "Baseline MLP/CNN overfits", "Add each regulariser separately", "Combine them; early stopping on validation", "Report train accuracy, test accuracy and the gap"],
  '''
import numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
small, val = tr[:1000], tr[6000:8000]
def cnn(p=0.0): return nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Dropout(p), nn.Linear(64 * 49, 128), nn.ReLU(), nn.Dropout(p), nn.Linear(128, 10))
def augment(x):                                   # random shifts up to 2 px + horizontal flips (clothes stay clothes)
    x = torch.roll(x, shifts=(int(np.random.randint(-2, 3)), int(np.random.randint(-2, 3))), dims=(2, 3)); return torch.where(torch.rand(len(x), 1, 1, 1) < 0.5, x.flip(3), x)
def run(p=0.0, wd=0.0, aug=False, smooth=0.0, epochs=40):
    torch.manual_seed(0); np.random.seed(0); m = cnn(p); opt = torch.optim.AdamW(m.parameters(), 1e-3, weight_decay=wd); best, state = 0, None
    for ep in range(epochs):
        m.train()
        for idx in small[torch.randperm(len(small))].split(64):
            xb = augment(Xt[idx]) if aug else Xt[idx]; opt.zero_grad(); nn.functional.cross_entropy(m(xb), yt[idx], label_smoothing=smooth).backward(); opt.step()
        v = acc(m, Xt[val], yt[val])
        if v > best: best, state, best_ep = v, {k: t.clone() for k, t in m.state_dict().items()}, ep
    m.load_state_dict(state); return acc(m, Xt[small], yt[small]), acc(m, Xt[te], yt[te]), best_ep + 1
for name, kw in [("baseline", {}), ("dropout 0.5", {"p": 0.5}), ("weight decay 0.1", {"wd": 0.1}), ("augmentation", {"aug": True}), ("label smoothing", {"smooth": 0.1}),
                 ("all combined", {"p": 0.5, "wd": 0.1, "aug": True, "smooth": 0.1})]:
    a, b, ep = run(**kw); print(f"  {name:17s} train {a:.3f} | test {b:.3f} | gap {a - b:.3f} | best epoch {ep}")
print("note: every regulariser shrinks the train-test gap; stacking all at full strength can underfit -> tune their strengths on validation data")
''')

X("m-pytorch",
  "PyTorch is the most widely used deep-learning framework: **tensors** (NumPy-like arrays on CPU/GPU) with **autograd**, building blocks in **torch.nn**, optimisers in **torch.optim**, and **Dataset/DataLoader** for batching. Every project follows the same skeleton: data → model → loss → optimiser → training loop → evaluation → save/load.",
  """**Core mechanics.** A tensor with requires_grad=True records operations in a dynamic graph; loss.backward() fills .grad of leaf tensors; optimizer.step() updates; optimizer.zero_grad() resets (gradients accumulate by default — useful for gradient accumulation). nn.Module registers parameters and submodules; model.train()/model.eval() toggle dropout/BatchNorm; torch.no_grad() (or inference_mode) disables graph building for evaluation. Device handling: model.to(device), tensors .to(device). Save the **state_dict** (weights), not the whole object. Mixed precision (torch.autocast) and torch.compile speed up training on GPUs.""",
  """**Autograd by hand.** x = tensor(3., requires_grad=True); y = x² + 2x → dy/dx = 2x + 2 = **8**; after y.backward(), x.grad = 8. Call backward again on a new y without zeroing → x.grad = **16** (accumulated) — why zero_grad() is in every loop.""",
  ["Forgetting zero_grad()", "Forgetting model.eval() / torch.no_grad() at evaluation", "Mixing devices (CPU tensor + GPU model)", "Saving the whole model object instead of state_dict", "Calling .item() inside hot loops excessively"],
  ["Research and production deep learning; custom models and training loops"], ["Simple tabular problems where scikit-learn is enough"],
  "California housing as a full PyTorch project: custom Dataset, DataLoader, nn.Module, training/validation loops with device handling, learning-rate scheduler, checkpointing the best model, reloading it and predicting for new houses.",
  ["Dataset and DataLoader from a DataFrame", "Model as an nn.Module", "Training and validation loops (device-aware)", "Scheduler + checkpoint the best state_dict", "Reload and predict; report test error in dollars"],
  f'''
import numpy as np, pandas as pd, torch, torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
device = "cuda" if torch.cuda.is_available() else "cpu"; torch.manual_seed(0)
df = pd.read_csv("{HOUSING}").dropna(); df = df[df.median_house_value < 500001]; df = pd.get_dummies(df, dtype=float)
tr_df, te_df = train_test_split(df, test_size=0.2, random_state=0); tr_df, va_df = train_test_split(tr_df, test_size=0.15, random_state=0)
feats = [c for c in df if c != "median_house_value"]; mu, sd = tr_df[feats].mean(), tr_df[feats].std() + 1e-9
class Houses(Dataset):
    def __init__(self, d): self.X = torch.tensor(((d[feats] - mu) / sd).to_numpy(), dtype=torch.float32); self.y = torch.tensor(np.log(d.median_house_value.to_numpy()), dtype=torch.float32)
    def __len__(self): return len(self.y)
    def __getitem__(self, i): return self.X[i], self.y[i]
loaders = {{k: DataLoader(Houses(d), batch_size=256, shuffle=(k == "train")) for k, d in [("train", tr_df), ("val", va_df), ("test", te_df)]}}
class Regressor(nn.Module):
    def __init__(self, d):
        super().__init__(); self.net = nn.Sequential(nn.Linear(d, 128), nn.ReLU(), nn.Dropout(0.1), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, x): return self.net(x).squeeze(-1)
model = Regressor(len(feats)).to(device); opt = torch.optim.AdamW(model.parameters(), 3e-3, weight_decay=1e-4)
sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, factor=0.5, patience=3); loss_fn = nn.MSELoss(); best = float("inf")
def evaluate(loader):
    model.eval(); tot = 0.0
    with torch.no_grad():
        for xb, yb in loader: tot += loss_fn(model(xb.to(device)), yb.to(device)).item() * len(yb)
    return tot / len(loader.dataset)
for epoch in range(40):
    model.train()
    for xb, yb in loaders["train"]:
        xb, yb = xb.to(device), yb.to(device); opt.zero_grad(); loss = loss_fn(model(xb), yb); loss.backward(); opt.step()
    v = evaluate(loaders["val"]); sched.step(v)
    if v < best: best = v; torch.save(model.state_dict(), "best.pt")
    if epoch % 10 == 9: print(f"  epoch {{epoch + 1}}: val MSE {{v:.4f}} lr {{opt.param_groups[0]['lr']:.1e}}")
reloaded = Regressor(len(feats)).to(device); reloaded.load_state_dict(torch.load("best.pt", map_location=device)); model = reloaded
print(f"test RMSE (log $) {{np.sqrt(evaluate(loaders['test'])):.4f}}")
new = te_df.head(3); xb = torch.tensor(((new[feats] - mu) / sd).to_numpy(), dtype=torch.float32, device=device)
with torch.no_grad(): print("predicted vs actual $:", list(zip(np.exp(model(xb).cpu().numpy()).round(-3).tolist(), new.median_house_value.round(-3).tolist())))
''')

X("m-keras",
  "Keras is the high-level deep-learning API: define a model with **Sequential** or the **functional API**, `compile` it with an optimiser, loss and metrics, then `fit` with callbacks. Keras 3 runs on TensorFlow, JAX or PyTorch backends, so the same code works everywhere — ideal for quick, readable models.",
  """**Workflow.** model = keras.Sequential([...]) or inputs → layers → keras.Model(inputs, outputs) for multi-input/multi-output/branching graphs. compile(optimizer, loss, metrics) → fit(x, y, validation_split, epochs, batch_size, callbacks) → evaluate → predict → save(".keras"). **Callbacks:** EarlyStopping(restore_best_weights=True), ModelCheckpoint, ReduceLROnPlateau, TensorBoard. **Preprocessing layers** (Normalization, Rescaling, data augmentation) live inside the model so serving uses identical preprocessing. Sparse vs categorical cross-entropy: integer labels vs one-hot. Custom training via subclassing Model and overriding train_step when needed.""",
  """**Params by hand** for Dense(128) after Flatten(28×28): 784·128 + 128 = **100,480**; Dense(10): 1,290. model.summary() lists exactly these — a quick sanity check that shapes are what you intended.""",
  ["sparse_categorical_crossentropy with one-hot labels (or vice versa)", "Normalising outside the model and forgetting at serving time", "No EarlyStopping(restore_best_weights=True)", "Mixing tf.keras (Keras 2) tutorials with Keras 3"],
  ["Fast prototyping, standard architectures, teaching, multi-backend portability"], ["Highly custom research training loops (PyTorch is more natural)"],
  "Fashion-MNIST with Keras 3 (PyTorch backend) — Sequential CNN with in-model rescaling and augmentation, compile/fit with EarlyStopping and ReduceLROnPlateau, a functional-API two-output model (class + 'is footwear'), evaluation and save/load in the .keras format.",
  ["Load data as NumPy arrays", "Sequential CNN with preprocessing layers inside the model", "fit with callbacks and validation split", "Functional API with two outputs", "Evaluate, save as .keras, reload and predict"],
  '''
import os; os.environ.setdefault("KERAS_BACKEND", "torch")
import gzip, urllib.request, numpy as np, keras
from keras import layers
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
get = lambda f, off: np.frombuffer(gzip.decompress(urllib.request.urlopen(base + f).read()), np.uint8, offset=off)
X = get("t10k-images-idx3-ubyte.gz", 16).reshape(-1, 28, 28, 1).astype("float32"); y = get("t10k-labels-idx1-ubyte.gz", 8).astype("int64")
Xtr, ytr, Xte, yte = X[:8000], y[:8000], X[8000:], y[8000:]; keras.utils.set_random_seed(0)
model = keras.Sequential([keras.Input((28, 28, 1)), layers.Rescaling(1 / 255), layers.RandomTranslation(0.08, 0.08), layers.Conv2D(32, 3, activation="relu", padding="same"), layers.MaxPooling2D(),
                          layers.Conv2D(64, 3, activation="relu", padding="same"), layers.MaxPooling2D(), layers.Flatten(), layers.Dropout(0.3), layers.Dense(10, activation="softmax")])
model.compile(optimizer=keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
cbs = [keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True), keras.callbacks.ReduceLROnPlateau(patience=1, factor=0.5)]
hist = model.fit(Xtr, ytr, validation_split=0.15, epochs=8, batch_size=128, callbacks=cbs, verbose=0)
print("params:", model.count_params(), "| epochs run:", len(hist.history["loss"]), "| best val acc:", round(max(hist.history["val_accuracy"]), 3))
print("test [loss, acc]:", np.round(model.evaluate(Xte, yte, verbose=0), 3))
inp = keras.Input((28, 28, 1)); h = layers.Rescaling(1 / 255)(inp); h = layers.Conv2D(32, 3, activation="relu")(h); h = layers.GlobalAveragePooling2D()(h)
out_cls = layers.Dense(10, activation="softmax", name="cls")(h); out_shoe = layers.Dense(1, activation="sigmoid", name="footwear")(h)
two = keras.Model(inp, [out_cls, out_shoe]); two.compile("adam", loss={"cls": "sparse_categorical_crossentropy", "footwear": "binary_crossentropy"}, metrics={"cls": ["accuracy"], "footwear": ["accuracy"]})
shoe = np.isin(ytr, [5, 7, 9]).astype("float32"); two.fit(Xtr, {"cls": ytr, "footwear": shoe}, epochs=3, batch_size=128, verbose=0)
res = two.evaluate(Xte, {"cls": yte, "footwear": np.isin(yte, [5, 7, 9]).astype("float32")}, verbose=0, return_dict=True); print("two-output model:", {k: round(v, 3) for k, v in res.items() if "acc" in k})
model.save("fashion_cnn.keras"); again = keras.models.load_model("fashion_cnn.keras")
print("reloaded model gives identical predictions:", np.allclose(again.predict(Xte[:5], verbose=0), model.predict(Xte[:5], verbose=0), atol=1e-5))
''')

X("m-cnn",
  "Convolutional neural networks slide small learned filters over an image, so the same pattern detector (an edge, a texture, an eye) is reused everywhere. Stacking convolutions and pooling builds features from local to global with few parameters — the standard approach for images, and also used for audio spectrograms and 1-D signals.",
  """**Convolution.** Output(i, j) = Σₘ Σₙ Σ_c K(m, n, c)·X(i + m, j + n, c) + b (deep-learning 'convolution' is cross-correlation). Output size = ⌊(N + 2P − K)/S⌋ + 1. Parameters per layer = K·K·C_in·C_out + C_out — independent of image size (**weight sharing**); **translation equivariance**: shift the input, the feature map shifts. **Pooling** (max/average) downsamples and adds small translation invariance; strided convs do the same learnably. **Receptive field** grows with depth: after L 3×3 layers it's (2L + 1)×(2L + 1), faster with pooling/stride/dilation. Global average pooling replaces big dense layers. 1×1 convs mix channels cheaply.""",
  """**Convolution by hand.** Input 4×4 = [[1,2,0,1],[0,1,3,1],[2,1,0,0],[1,0,1,2]], vertical-edge kernel [[1,0,−1],[1,0,−1],[1,0,−1]], no padding, stride 1 → 2×2 output. Top-left: (1 + 0 + 2) − (0 + 3 + 0) = **0**; top-right: (2 + 1 + 1) − (1 + 1 + 0) = **2**. Output size (4 − 3)/1 + 1 = 2 ✓. A 3×3×64→128 conv layer has 9·64·128 + 128 = **73,856** parameters.""",
  ["Wrong output-size arithmetic (shape errors)", "Huge dense layers after flattening", "Not normalising pixel values", "Training deep CNNs from scratch on small datasets instead of transfer learning"],
  ["Images, spectrograms, any grid-like data with local patterns"], ["Tabular data; tasks needing global context from the start (transformers may do better at scale)"],
  "Fashion-MNIST — convolution computed by hand in NumPy and checked against PyTorch, output-shape arithmetic, a CNN trained with BatchNorm and global average pooling, parameter comparison with an MLP, and a test of translation robustness.",
  ["Manual convolution vs torch conv2d", "Shape and parameter arithmetic per layer", "Train a CNN (Conv-BN-ReLU-Pool blocks + GAP)", "Compare with an MLP of similar size", "Shift test images by 3 px and compare robustness"],
  '''
import numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
img = np.array([[1, 2, 0, 1], [0, 1, 3, 1], [2, 1, 0, 0], [1, 0, 1, 2]], float); K = np.array([[1, 0, -1]] * 3, float)
manual = np.array([[(img[i:i + 3, j:j + 3] * K).sum() for j in range(2)] for i in range(2)])
torch_out = nn.functional.conv2d(torch.tensor(img)[None, None], torch.tensor(K)[None, None])[0, 0].numpy()
print("manual conv:", manual.tolist(), "| torch:", torch_out.tolist())
def block(i, o): return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(), nn.MaxPool2d(2))
cnn = nn.Sequential(block(1, 32), block(32, 64), block(64, 128), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(128, 10))
x = Xt[:1]
for layer in cnn: x = layer(x); print(f"  {type(layer).__name__:18s} -> {tuple(x.shape)}") if not isinstance(layer, nn.Sequential) else print(f"  conv block          -> {tuple(x.shape)} params {sum(p.numel() for p in layer.parameters()):,}")
mlp = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))
for name, m in [("CNN", cnn), ("MLP", mlp)]:
    torch.manual_seed(0); fit(m, torch.optim.Adam(m.parameters(), 1e-3), 6, Xt[tr], yt[tr])
    shifted = torch.roll(Xt[te], shifts=3, dims=3)
    print(f"  {name}: params {sum(p.numel() for p in m.parameters()):,} | test acc {acc(m, Xt[te], yt[te]):.3f} | images shifted 3 px right {acc(m, shifted, yt[te]):.3f}")
''')

X("m-cnn-understand",
  "CNNs aren't black boxes: you can look at the **filters** (early ones are edge/colour detectors), the **feature maps** (where each filter fires), **saliency maps** (which pixels change the prediction most) and **Grad-CAM** heatmaps (which regions a class decision relied on). These tools catch shortcut learning — e.g. a model that looks at the background instead of the object.",
  """**Methods.** Filters: weights of the first conv layer reshaped as tiny images. Feature maps: activations after each layer for an input. **Saliency:** |∂y_c/∂x| — gradient of the class score w.r.t. input pixels. **Grad-CAM:** for the last conv feature maps Aᵏ, weights αₖ = mean over pixels of ∂y_c/∂Aᵏ; heatmap = ReLU(Σₖ αₖAᵏ), upsampled to the image — class-discriminative and coarse. **Occlusion sensitivity:** slide a grey patch and measure the drop in class score — model-agnostic and intuitive. Also: maximally activating images per filter; t-SNE of penultimate-layer embeddings.""",
  """**Grad-CAM by hand.** Two 2×2 feature maps A¹ = [[1, 0], [0, 0]], A² = [[0, 0], [0, 2]], gradients average α₁ = 0.5, α₂ = −0.25 → 0.5A¹ − 0.25A² = [[0.5, 0], [0, −0.5]] → ReLU → [[**0.5**, 0], [0, 0]]: the top-left region supports the class.""",
  ["Reading saliency noise as meaning (use smoothing / several methods)", "Visualising only correct predictions", "Ignoring that heatmaps are coarse (last conv resolution)"],
  ["Debugging, detecting shortcuts/leakage, explaining predictions to stakeholders"], ["As proof of causal reasoning by the model"],
  "Fashion-MNIST CNN — first-layer filters, feature-map activity, gradient saliency, Grad-CAM and occlusion sensitivity for real test images, checking that the model looks at the garment (e.g. the heel of a boot, the sleeves of a shirt). Saves a figure.",
  ["Train a CNN", "Extract first-layer filters and feature maps with hooks", "Gradient saliency for a test image", "Grad-CAM from the last conv block", "Occlusion sensitivity map; save a panel figure"],
  '''
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
torch.manual_seed(0)
model = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(64, 10))
fit(model, torch.optim.Adam(model.parameters(), 2e-3), 6, Xt[tr], yt[tr]); model.eval(); print("test acc:", round(acc(model, Xt[te], yt[te]), 3))
filters = model[0].weight.detach()[:, 0]; print("first-layer filter shapes:", tuple(filters.shape), "| mean |weight| per filter:", filters.abs().mean((1, 2)).numpy().round(2)[:6])
acts = {}
model[7].register_forward_hook(lambda m, i, o: acts.__setitem__("last", o))
i = int((yt[te] == 9).nonzero()[0]); x = Xt[te][i:i + 1].clone().requires_grad_(True); out = model(x); c = out.argmax(1).item()
out[0, c].backward(); sal = x.grad.abs()[0, 0]
A = acts["last"].detach()[0]; x2 = Xt[te][i:i + 1]
A_ = model[:8](x2); A_.retain_grad(); score = model[8:](A_)[0, c]; score.backward()
cam = torch.relu((A_.grad[0].mean((1, 2))[:, None, None] * A_[0]).sum(0)).detach(); cam = nn.functional.interpolate(cam[None, None], size=(28, 28), mode="bilinear")[0, 0]
occ = np.zeros((28, 28)); base = torch.softmax(model(x2), 1)[0, c].item()
with torch.no_grad():
    for r in range(0, 28, 4):
        for s in range(0, 28, 4):
            xo = x2.clone(); xo[..., r:r + 6, s:s + 6] = 0; occ[r:r + 4, s:s + 4] = base - torch.softmax(model(xo), 1)[0, c].item()
print(f"image {i}: true {NAMES[yt[te][i]]}, predicted {NAMES[c]} ({base:.2f}) | feature maps {tuple(A.shape)}")
print("rows with most Grad-CAM mass (top=0):", torch.topk(cam.sum(1), 3).indices.tolist(), "| most occlusion-sensitive rows:", np.argsort(-occ.sum(1))[:3].tolist())
fig, ax = plt.subplots(1, 4, figsize=(12, 3))
for a, (t, im) in zip(ax, [("image", x2[0, 0]), ("saliency", sal), ("Grad-CAM", cam), ("occlusion", occ)]): a.imshow(np.asarray(im), cmap="gray" if t == "image" else "jet"); a.set_title(t); a.axis("off")
fig.savefig("explain_cnn.png"); print("saved explain_cnn.png")
''')

X("m-autoencoder",
  "An autoencoder learns to compress its input into a small **code** (encoder) and rebuild it (decoder). Because the bottleneck forces it to keep only what matters, it's used for dimensionality reduction, **denoising**, **anomaly detection** (things it can't rebuild well are unusual) and as the basis of generative models (VAEs).",
  """**Objective.** min ‖x − g(f(x))‖² (or BCE for [0, 1] pixels), with encoder f: x → z (dim k ≪ d) and decoder g. A linear autoencoder with MSE learns the same subspace as PCA; non-linear layers learn curved manifolds. **Variants:** denoising (input x + noise, target clean x → learns robust features), sparse (L1 on the code), contractive, convolutional (for images), variational (probabilistic code, can generate). **Anomaly detection:** train on normal data; score = reconstruction error; threshold at a high percentile of validation errors.""",
  """**Compression by hand.** 784 pixels → 32-number code → 784: compression **24.5×**. If normal images reconstruct with MSE ≈ 0.010 ± 0.003 and you threshold at the 99th percentile ≈ 0.018, an unseen class reconstructing at 0.030 is flagged.""",
  ["Too large a bottleneck (learns identity)", "Evaluating anomaly detection on classes seen in training", "Using MSE on heavy-tailed data without scaling", "Expecting an AE to generate new samples (use a VAE)"],
  ["Compression, denoising, anomaly detection, pre-training representations"], ["When PCA already reconstructs well (simpler, faster)"],
  "Fashion-MNIST — convolutional autoencoder with a 32-dim code: reconstruction vs PCA at the same size, a denoising autoencoder, and anomaly detection by training only on clothing and flagging bags/footwear by reconstruction error.",
  ["Build a conv encoder/decoder", "Train and compare reconstruction error with PCA-32", "Denoising: train on noisy inputs, clean targets", "Anomaly detection: train on 6 clothing classes only", "Score unseen classes; report AUC and threshold hit-rate"],
  '''
import numpy as np, torch, torch.nn as nn
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score
''' + FM + '''
class AE(nn.Module):
    def __init__(self, k=32):
        super().__init__()
        self.enc = nn.Sequential(nn.Conv2d(1, 16, 3, 2, 1), nn.ReLU(), nn.Conv2d(16, 32, 3, 2, 1), nn.ReLU(), nn.Flatten(), nn.Linear(32 * 49, k))
        self.dec = nn.Sequential(nn.Linear(k, 32 * 49), nn.ReLU(), nn.Unflatten(1, (32, 7, 7)), nn.ConvTranspose2d(32, 16, 4, 2, 1), nn.ReLU(), nn.ConvTranspose2d(16, 1, 4, 2, 1), nn.Sigmoid())
    def forward(self, x): return self.dec(self.enc(x))
def train_ae(Xa, epochs=8, noise=0.0):
    torch.manual_seed(0); m = AE(); opt = torch.optim.Adam(m.parameters(), 2e-3)
    for _ in range(epochs):
        for idx in torch.randperm(len(Xa)).split(128):
            xb = Xa[idx]; inp = (xb + noise * torch.randn_like(xb)).clamp(0, 1); opt.zero_grad(); nn.functional.mse_loss(m(inp), xb).backward(); opt.step()
    return m.eval()
err = lambda m, Xa: ((m(Xa) - Xa) ** 2).mean((1, 2, 3)).detach().numpy()
ae = train_ae(Xt[tr]); pca = PCA(32).fit(X[:8000].reshape(8000, -1)); P = pca.inverse_transform(pca.transform(X[8000:].reshape(2000, -1)))
print(f"reconstruction MSE with 32 numbers: conv autoencoder {err(ae, Xt[te]).mean():.4f} | PCA {((P - X[8000:].reshape(2000, -1)) ** 2).mean():.4f}")
noisy = (Xt[te] + 0.3 * torch.randn_like(Xt[te])).clamp(0, 1); dae = train_ae(Xt[tr], noise=0.3)
with torch.no_grad(): print(f"denoising: noisy MSE {((noisy - Xt[te]) ** 2).mean():.4f} -> plain AE {((ae(noisy) - Xt[te]) ** 2).mean():.4f} -> denoising AE {((dae(noisy) - Xt[te]) ** 2).mean():.4f}")
normal = torch.tensor([0, 1, 2, 3, 4, 6]); is_norm = torch.isin(yt, normal); amb = train_ae(Xt[tr][is_norm[tr]])
e = err(amb, Xt[te]); lab = (~is_norm[te]).numpy(); thr = np.percentile(err(amb, Xt[tr][is_norm[tr]]), 99)
print(f"anomaly detection (sandals/sneakers/bags/boots unseen): AUC {roc_auc_score(lab, e):.3f} | flagged at 99th-pct threshold: anomalies {(e[lab] > thr).mean():.2f}, normals {(e[~lab] > thr).mean():.2f}")
''')

X("m-rnn",
  "A recurrent neural network reads a sequence one step at a time, carrying a **hidden state** that summarises what it has seen so far. The same weights are reused at every step, so it handles any sequence length — the classic model for time series, text and audio before transformers.",
  """**Recurrence.** hₜ = tanh(W_x xₜ + W_h hₜ₋₁ + b); output yₜ = W_y hₜ. Parameters are shared over time. Training = **backpropagation through time (BPTT)**: unroll for T steps and backprop; gradient w.r.t. early states contains Πₜ W_hᵀ diag(1 − hₜ²) → vanishes/explodes depending on W_h's spectrum → plain RNNs struggle beyond ~10–20 steps; use gradient clipping and gated cells (LSTM/GRU). Truncated BPTT limits the unroll for long streams. **Shapes in PyTorch:** input (batch, time, features) with batch_first=True; output (batch, time, hidden); h_n (layers, batch, hidden). Patterns: many-to-one (classification), many-to-many (tagging), seq2seq.""",
  """**Two steps by hand.** W_x = 0.5, W_h = 0.8, b = 0, h₀ = 0, inputs [1, 2]. h₁ = tanh(0.5) = **0.462**; h₂ = tanh(1 + 0.8·0.462) = tanh(1.370) = **0.879**. ∂h₂/∂h₁ = (1 − 0.879²)·0.8 = **0.182** — each step shrinks the gradient; after 20 such steps ≈ 0.182²⁰ ≈ 10⁻¹⁵.""",
  ["Shuffling time steps or leaking future values into inputs", "No gradient clipping", "Wrong tensor layout (time vs batch first)", "Expecting long-range memory from a vanilla RNN"],
  ["Short sequences, streaming/online inference, small models"], ["Long-range dependencies — LSTM/GRU or transformers"],
  "Daily minimum temperatures in Melbourne (1981–1990, 3,650 days) — an RNN cell computed by hand vs nn.RNN, then next-day forecasting from 30-day windows compared with persistence and seasonal baselines, and a gradient-through-time measurement showing why long memory fails.",
  ["Load and scale the series; build 30-day windows (time-ordered split)", "Verify a manual RNN step against nn.RNN", "Train a many-to-one RNN forecaster with clipping", "Compare with persistence and climatology baselines", "Measure gradient size w.r.t. each past input"],
  f'''
import numpy as np, pandas as pd, torch, torch.nn as nn
s = pd.read_csv("{TEMPS}", parse_dates=["Date"]).set_index("Date")["Temp"].astype(float)
mu, sd = s[:"1988"].mean(), s[:"1988"].std(); z = ((s - mu) / sd).to_numpy(np.float32); W = 30
Xw = np.stack([z[i:i + W] for i in range(len(z) - W)])[..., None]; yw = z[W:]; split = (s.index[W:] < "1989-01-01").sum()
Xtr, ytr, Xte, yte = map(torch.tensor, (Xw[:split], yw[:split], Xw[split:], yw[split:]))
torch.manual_seed(0); rnn = nn.RNN(1, 1, batch_first=True); Wx, Wh, bx, bh = (p.item() for p in rnn.parameters())
x = Xtr[0, :2, 0].numpy(); h1 = np.tanh(Wx * x[0] + bx + bh); h2 = np.tanh(Wx * x[1] + bx + Wh * h1 + bh)
print("manual h2 =", round(float(h2), 6), "| nn.RNN h2 =", round(rnn(Xtr[:1, :2])[0][0, -1, 0].item(), 6))
class Forecaster(nn.Module):
    def __init__(self): super().__init__(); self.rnn = nn.RNN(1, 32, batch_first=True); self.head = nn.Linear(32, 1)
    def forward(self, x): out, _ = self.rnn(x); return self.head(out[:, -1]).squeeze(1)
m = Forecaster(); opt = torch.optim.Adam(m.parameters(), 3e-3)
for epoch in range(15):
    for idx in torch.randperm(len(Xtr)).split(64):
        opt.zero_grad(); loss = nn.functional.mse_loss(m(Xtr[idx]), ytr[idx]); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
with torch.no_grad(): pred = m(Xte).numpy() * sd + mu
truth = yte.numpy() * sd + mu; persistence = Xte[:, -1, 0].numpy() * sd + mu
clim = s[:"1988"].groupby(s[:"1988"].index.dayofyear).mean().reindex(s.index[W:][split:].dayofyear).to_numpy()
for name, p in [("climatology (day-of-year mean)", clim), ("persistence (yesterday)", persistence), ("RNN 30-day window", pred)]: print(f"  {{name:31s}} MAE {{np.abs(p - truth).mean():.2f}} °C")
x = Xte[:1].clone().requires_grad_(True); m(x).sum().backward(); g = x.grad[0, :, 0].abs().numpy()
print("gradient of forecast w.r.t. input k days back (k=1,5,10,20,30):", [f"{{g[-k]:.1e}}" for k in (1, 5, 10, 20, 30)])
''')

X("m-lstm-gru",
  "LSTMs and GRUs are recurrent cells with **gates** — small learned switches that decide what to remember, forget and output. The gated, mostly-additive memory path lets gradients flow across long sequences, fixing the vanishing-gradient problem of plain RNNs. They powered translation, speech and text models before transformers and are still great for streaming and small data.",
  """**LSTM.** fₜ = σ(W_f[hₜ₋₁, xₜ] + b_f) (forget), iₜ = σ(W_i·) (input), c̃ₜ = tanh(W_c·) (candidate), **cₜ = fₜ ⊙ cₜ₋₁ + iₜ ⊙ c̃ₜ** (additive cell update), oₜ = σ(W_o·), hₜ = oₜ ⊙ tanh(cₜ). ∂cₜ/∂cₜ₋₁ = fₜ — if the forget gate stays near 1, gradients pass almost unchanged ('constant error carousel'); init forget bias to 1. **GRU:** zₜ (update) and rₜ (reset) gates, hₜ = (1 − zₜ)hₜ₋₁ + zₜh̃ₜ — fewer parameters (3 vs 4 weight blocks), similar accuracy. Bidirectional variants read both directions (not for forecasting); stacking layers adds depth; packing handles variable lengths.""",
  """**One LSTM step by hand (scalar).** cₜ₋₁ = 2, f = 0.9, i = 0.3, c̃ = 0.5, o = 0.8 → cₜ = 0.9·2 + 0.3·0.5 = **1.95**; hₜ = 0.8·tanh(1.95) = **0.770**. **Parameters:** LSTM with input 64, hidden 128: 4·(128·(64 + 128) + 128) = **98,816**; GRU: 3·(…) ≈ 74,112 (PyTorch adds a second bias set).""",
  ["Using bidirectional LSTMs for forecasting (peeks at the future)", "Padding without masking/packing", "Huge hidden sizes on small data", "Comparing against no simple baseline"],
  ["Streaming sequences, small/medium text or sensor data, on-device models"], ["Large-scale language tasks — transformers dominate"],
  "SMS Spam Collection — text classification with an embedding + RNN vs LSTM vs GRU (packed variable-length sequences), compared with TF-IDF logistic regression; then a gradient-flow test showing how far back each cell type can 'feel' its inputs. Includes a hand-computed LSTM step checked against nn.LSTMCell.",
  ["Tokenise SMS messages and build a vocabulary", "Manual LSTM step vs nn.LSTMCell", "Train RNN, LSTM, GRU classifiers with packing", "Baseline: TF-IDF + logistic regression", "Gradient flow over 100 steps: plain RNN vs LSTM (forget bias 1) vs GRU"],
  f'''
import re, numpy as np, pandas as pd, torch, torch.nn as nn
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from torch.nn.utils.rnn import pack_padded_sequence, pad_sequence
df = pd.read_csv("{SMS}", sep="\\t", names=["label", "text"]).sample(frac=1, random_state=0); y = (df.label == "spam").to_numpy()
tok = lambda s: re.findall(r"[a-z0-9£$']+", s.lower())[:60]; cut = int(0.8 * len(df))
vocab = {{w: i + 2 for i, (w, _) in enumerate(Counter(w for t in df.text[:cut] for w in tok(t)).most_common(8000))}}
seqs = [torch.tensor([vocab.get(w, 1) for w in tok(t)] or [1]) for t in df.text]; lens = torch.tensor([len(s) for s in seqs]); Xp = pad_sequence(seqs, batch_first=True); Y = torch.tensor(y, dtype=torch.float32)
torch.manual_seed(0); cell = nn.LSTMCell(1, 1); W_ih, W_hh, b_ih, b_hh = (p.detach().numpy().ravel() for p in cell.parameters()); sig = lambda v: 1 / (1 + np.exp(-v))
x, h, c = 0.7, 0.1, 2.0; g = W_ih * x + W_hh * h + b_ih + b_hh; i_, f_, c_hat, o_ = sig(g[0]), sig(g[1]), np.tanh(g[2]), sig(g[3]); c_new = f_ * c + i_ * c_hat
print("manual LSTM step h =", round(float(o_ * np.tanh(c_new)), 6), "| LSTMCell h =", round(cell(torch.tensor([[x]]), (torch.tensor([[h]]), torch.tensor([[c]])))[0].item(), 6))
class Clf(nn.Module):
    def __init__(self, kind):
        super().__init__(); self.emb = nn.Embedding(len(vocab) + 2, 64, padding_idx=0); self.rnn = getattr(nn, kind)(64, 64, batch_first=True); self.out = nn.Linear(64, 1)
    def forward(self, x, l):
        _, h = self.rnn(pack_padded_sequence(self.emb(x), l, batch_first=True, enforce_sorted=False)); h = h[0] if isinstance(h, tuple) else h; return self.out(h[-1]).squeeze(1)
for kind in ["RNN", "LSTM", "GRU"]:
    torch.manual_seed(0); m = Clf(kind); opt = torch.optim.Adam(m.parameters(), 2e-3)
    for epoch in range(4):
        for idx in torch.randperm(cut).split(64):
            opt.zero_grad(); nn.functional.binary_cross_entropy_with_logits(m(Xp[idx], lens[idx]), Y[idx]).backward(); nn.utils.clip_grad_norm_(m.parameters(), 1); opt.step()
    with torch.no_grad(): p = (m(Xp[cut:], lens[cut:]) > 0).numpy()
    print(f"  {{kind:4s}} spam F1 {{f1_score(y[cut:], p):.3f}} | params {{sum(q.numel() for q in m.parameters()):,}}")
tf = TfidfVectorizer(min_df=2).fit(df.text[:cut]); print(f"  TF-IDF + logistic baseline F1 {{f1_score(y[cut:], LogisticRegression(C=10, max_iter=2000).fit(tf.transform(df.text[:cut]), y[:cut]).predict(tf.transform(df.text[cut:]))):.3f}}")
L = 100                                                                           # gradient flow: how much does the LAST state depend on each earlier input?
for kind in ["RNN", "LSTM", "GRU"]:
    res = []
    for seed in range(5):
        torch.manual_seed(seed); rnn = getattr(nn, kind)(16, 32, batch_first=True)
        if kind == "LSTM":
            for name, p in rnn.named_parameters():
                if "bias" in name: p.data[32:64] = 1.0                                   # forget-gate bias = 1 (standard trick)
        x = torch.randn(8, L, 16, requires_grad=True); o, _ = rnn(x); o[:, -1].sum().backward(); g = x.grad.norm(dim=(0, 2)); res.append([g[-1].item(), g[-11].item(), g[-51].item(), g[0].item()])
    print(f"  {{kind:4s}} |∂h_T/∂x_t| for t = T, T-10, T-50, T-99: {{['%.1e' % v for v in np.mean(res, 0)]}}")
''')

X("m-seq2seq",
  "Sequence-to-sequence models map an input sequence to an output sequence of possibly different length: an **encoder** reads the input into a representation, a **decoder** generates the output step by step. Used for translation, summarisation, speech recognition and multi-step forecasting; **attention** lets the decoder look back at all encoder states instead of one fixed vector.",
  """**Architecture.** Encoder RNN → final state (context). Decoder RNN initialised with the context generates y₁…y_T, each step fed the previous output. **Teacher forcing:** during training feed the ground-truth previous token (fast, stable) — causes exposure bias at inference; scheduled sampling mixes in model outputs. **Bottleneck:** one fixed vector for a long input loses information → **Bahdanau/Luong attention:** at decoder step t compute scores eₜᵢ = score(sₜ, hᵢ), weights αₜ = softmax(eₜ), context cₜ = Σᵢ αₜᵢhᵢ. Transformers keep the encoder–decoder idea but replace recurrence with attention everywhere (T5, BART, Whisper). Decoding: greedy, beam search.""",
  """**Attention by hand.** Encoder states h₁ = [1, 0], h₂ = [0, 1], h₃ = [1, 1]; decoder state s = [2, 0]; dot scores [2, 0, 2] → softmax [0.468, 0.063, 0.468] → context = 0.468[1, 0] + 0.063[0, 1] + 0.468[1, 1] = **[0.936, 0.531]** — mostly from states aligned with s.""",
  ["Teacher forcing at evaluation time (overly optimistic scores)", "No attention for long inputs", "Leaking future targets into encoder inputs for forecasting", "Greedy decoding when beam search is cheap and better"],
  ["Variable-length input→output tasks: translation, summarisation, speech, multi-step forecasting"], ["Fixed-size outputs — simpler heads suffice"],
  "Monthly sunspot numbers (1749–1983, 2,820 months) — encoder–decoder GRU that reads 12 years and forecasts the next 24 months, trained with teacher forcing and evaluated autoregressively; then with Luong attention; compared with a seasonal-cycle baseline and a direct MLP.",
  ["Scale the series; make (144-month input, 24-month output) windows; split by time", "Encoder–decoder GRU with teacher forcing", "Autoregressive evaluation (no teacher forcing)", "Add dot-product attention over encoder states", "Compare MAE with baselines; inspect attention focus"],
  f'''
import numpy as np, pandas as pd, torch, torch.nn as nn
s = pd.read_csv("{SUNSPOTS}")["Sunspots"].to_numpy(np.float32); z = np.sqrt(s); mu, sd = z[:2200].mean(), z[:2200].std(); z = (z - mu) / sd
IN, OUT = 144, 24; idx = np.arange(len(z) - IN - OUT); Xw = np.stack([z[i:i + IN] for i in idx])[..., None]; Yw = np.stack([z[i + IN:i + IN + OUT] for i in idx])[..., None]
tr = idx + IN + OUT <= 2200; Xtr, Ytr, Xte, Yte = (torch.tensor(a) for a in (Xw[tr], Yw[tr], Xw[~tr][::6], Yw[~tr][::6]))
class Seq2Seq(nn.Module):
    def __init__(self, attention):
        super().__init__(); self.enc = nn.GRU(1, 64, batch_first=True); self.dec = nn.GRUCell(1, 64); self.attn = attention; self.out = nn.Linear(128 if attention else 64, 1)
    def forward(self, x, y=None):
        H, h = self.enc(x); h = h[0]; prev = x[:, -1]; outs, weights = [], []
        for t in range(OUT):
            h = self.dec(prev, h)
            if self.attn:
                a = torch.softmax((H @ h.unsqueeze(2)).squeeze(2) / 8, 1); weights.append(a); feat = torch.cat([h, (a.unsqueeze(2) * H).sum(1)], 1)
            else: feat = h
            o = self.out(feat); outs.append(o); prev = y[:, t] if y is not None else o            # teacher forcing only when targets are given
        return torch.stack(outs, 1), (torch.stack(weights, 1) if weights else None)
def train(m):
    torch.manual_seed(0); opt = torch.optim.Adam(m.parameters(), 2e-3)
    for epoch in range(12):
        for b in torch.randperm(len(Xtr)).split(64):
            opt.zero_grad(); nn.functional.mse_loss(m(Xtr[b], Ytr[b])[0], Ytr[b]).backward(); nn.utils.clip_grad_norm_(m.parameters(), 1); opt.step()
    return m.eval()
back = lambda a: (np.asarray(a) * sd + mu) ** 2; truth = back(Yte[..., 0])
res = {{}}
for name, att in [("seq2seq GRU", False), ("seq2seq GRU + attention", True)]:
    torch.manual_seed(0); m = train(Seq2Seq(att))
    with torch.no_grad(): p_tf, _ = m(Xte, Yte); p, w = m(Xte)
    res[name] = w; print(f"  {{name:24s}} MAE autoregressive {{np.abs(back(p[..., 0]) - truth).mean():5.1f}} | with teacher forcing (cheating) {{np.abs(back(p_tf[..., 0]) - truth).mean():5.1f}}")
cycle = back(Xte[:, IN - 132:IN - 132 + OUT, 0]); print(f"  baseline: repeat 11-year cycle MAE {{np.abs(cycle - truth).mean():5.1f}} | repeat last value {{np.abs(back(Xte[:, -1:, 0]).repeat(OUT, 1) - truth).mean():5.1f}}")
w = res["seq2seq GRU + attention"].mean((0, 1)).numpy(); print("months back that the decoder attends to most:", (IN - np.argsort(-w)[:5]).tolist(), "(recent months + roughly one solar cycle ago)")
''')

X("m-time-series",
  "Time-series forecasting predicts future values from past ones, exploiting **trend**, **seasonality** and **autocorrelation**. Classical models (naive baselines, exponential smoothing, ARIMA/SARIMA) are strong, interpretable starting points, and evaluation must respect time order (backtesting).",
  """**Components.** yₜ = trend + seasonal + residual (additive) or × (multiplicative → log transform). **Stationarity:** constant mean/variance/autocorrelation; test with ADF (H₀: unit root); fix by differencing (∇yₜ = yₜ − yₜ₋₁, seasonal ∇₁₂). **ACF/PACF** reveal MA/AR orders. **ARIMA(p,d,q):** AR terms on past values, MA terms on past errors after d differences; **SARIMA** adds seasonal (P,D,Q)ₛ. **ETS / Holt-Winters:** level ℓₜ = α(yₜ − sₜ₋ₘ) + (1−α)(ℓₜ₋₁ + bₜ₋₁), trend and seasonal smoothing similarly. **Evaluation:** rolling-origin backtests; MAE/MAPE/MASE (scaled by seasonal-naive error); prediction intervals. Always beat **seasonal naive** first.""",
  """**Exponential smoothing by hand.** α = 0.5, ℓ₀ = 100; observations 110, 120 → ℓ₁ = 0.5·110 + 0.5·100 = 105; ℓ₂ = 0.5·120 + 0.5·105 = **112.5** = forecast for next period. **Seasonal naive:** forecast for Jan 1961 = Jan 1960 value. **MASE** = MAE/MAE(seasonal naive) — below 1 means you beat the baseline.""",
  ["Random train/test splits", "Not log-transforming multiplicative seasonality", "Over-differencing", "Reporting in-sample fit as accuracy", "Forgetting prediction intervals"],
  ["Demand, traffic, finance, energy — any univariate/seasonal series; baselines before ML"], ["Series driven mostly by external events without those features"],
  "Airline passengers (monthly, 1949–1960) — decomposition, stationarity tests and differencing, ACF/PACF, then a 24-month holdout comparing naive, seasonal naive, Holt-Winters, SARIMA(1,1,1)(0,1,1)₁₂ (the classic 'airline model') with prediction intervals, plus a rolling-origin backtest.",
  ["Load series; log transform; seasonal decomposition", "ADF test before/after differencing; ACF/PACF", "Fit baselines, Holt-Winters and SARIMA on 1949–1958", "Forecast 1959–1960 with intervals; MAE/MAPE/MASE", "Rolling-origin backtest of the best model"],
  f'''
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import acf, adfuller, pacf
y = pd.read_csv("{AIR}", parse_dates=["Month"], index_col="Month")["Passengers"].asfreq("MS").astype(float); ly = np.log(y)
dec = seasonal_decompose(ly, period=12); print("seasonal effect by month (log, +=above trend):", dec.seasonal[:12].round(2).tolist())
for name, s in [("log level", ly), ("1st difference", ly.diff()), ("1st + seasonal difference", ly.diff().diff(12))]: print(f"  ADF p-value {{name:26s}} {{adfuller(s.dropna())[1]:.3f}}")
d = ly.diff().diff(12).dropna(); print("ACF lags 1,12:", acf(d, nlags=12)[[1, 12]].round(2), "| PACF lags 1,12:", pacf(d, nlags=12)[[1, 12]].round(2), "-> MA(1) and seasonal MA(1)")
train, test = ly[:"1958"], y["1959":]; h = len(test)
mae = lambda f: np.abs(f - test.values).mean(); yv = y[:"1958"].values; snaive_mae_in = np.abs(yv[12:] - yv[:-12]).mean()
fc = {{"naive": np.repeat(y[:"1958"].iloc[-1], h), "seasonal naive": np.tile(y["1958"].values, 2),
      "Holt-Winters": np.exp(ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=12).fit().forecast(h).values)}}
sar = SARIMAX(train, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False); f = sar.get_forecast(h); fc["SARIMA airline"] = np.exp(f.predicted_mean.values); ci = np.exp(f.conf_int(alpha=0.05).values)
for name, p in fc.items(): print(f"  {{name:15s}} MAE {{mae(p):6.1f}} | MAPE {{np.mean(np.abs(p - test.values) / test.values):.1%}} | MASE {{mae(p) / snaive_mae_in:.2f}}")
print(f"SARIMA 95% interval coverage on 1959-60: {{((test.values >= ci[:, 0]) & (test.values <= ci[:, 1])).mean():.0%}}")
errs = []
for origin in pd.date_range("1956-12-01", "1959-12-01", freq="6MS"):
    m = SARIMAX(ly[:origin], order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False); p = np.exp(m.forecast(12)); actual = y[p.index.intersection(y.index)]
    errs.append(np.abs(p[actual.index] - actual).mean())
print("rolling-origin 12-month MAE per origin:", np.round(errs, 1).tolist())
''')

X("m-ts-dl",
  "Deep-learning forecasters (MLPs on lag windows, 1-D CNNs, LSTMs/GRUs, Temporal Fusion Transformers, N-BEATS, PatchTST, foundation models like Chronos/TimesFM) shine with many related series, long histories and rich covariates. On a single short series they often lose to classical models — always compare against seasonal naive and ETS/ARIMA under the same backtest.",
  """**Framing.** Supervised windows: inputs yₜ₋ₗ₊₁…yₜ (+ calendar/covariates) → targets yₜ₊₁…yₜ₊ₕ. **Multi-step strategies:** recursive (feed predictions back; error accumulates), direct (one output per horizon), MIMO (one network outputs the whole horizon). **Scaling** per series (standardise or divide by mean) is critical for global models trained across many series. **Architectures:** 1-D causal/dilated convolutions (TCN) see long windows cheaply; LSTMs carry state; transformers with patching handle long contexts. Probabilistic forecasts via quantile (pinball) loss or distribution heads (DeepAR). **Validation:** walk-forward splits; never shuffle across time; fit scalers on training spans only.""",
  """**Window count by hand.** 3,650 days, window 60, horizon 7 → 3,650 − 60 − 7 + 1 = **3,584** training examples from one series. A global model over 500 store-item series gets ~1.8M examples — that's where deep models pull ahead.""",
  ["Shuffled or overlapping leakage between train/test windows", "Scaling with statistics from the whole series", "No classical baseline", "Recursive forecasting without checking error growth over the horizon"],
  ["Many related series, long histories, covariates, probabilistic forecasts at scale"], ["One short series with clear seasonality — ETS/ARIMA usually win"],
  "Daily minimum temperatures (Melbourne, 10 years) — 7-day-ahead forecasts from 60-day windows with a direct MLP, 1-D CNN and LSTM (MIMO outputs) plus a quantile-loss LSTM for intervals, compared with seasonal-naive and climatology baselines on the final year, with error per horizon.",
  ["Create windows (60 in, 7 out) with a time-based split and train-only scaling", "Baselines: persistence and climatology", "MLP, 1-D CNN and LSTM with multi-output heads", "Quantile (pinball) loss for 10–90% intervals", "MAE by horizon day and interval coverage"],
  f'''
import numpy as np, pandas as pd, torch, torch.nn as nn
s = pd.read_csv("{TEMPS}", parse_dates=["Date"]).set_index("Date")["Temp"].astype(float)
L, H = 60, 7; train_end = (s.index < "1990-01-01").sum(); mu, sd = s[:train_end].mean(), s[:train_end].std(); z = ((s - mu) / sd).to_numpy(np.float32)
doy = s.index.dayofyear.to_numpy(); cal = np.stack([np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)], 1).astype(np.float32)
starts = np.arange(len(z) - L - H + 1); tr = starts + L + H <= train_end; te = starts + L >= train_end
mk = lambda st: (torch.tensor(np.stack([np.c_[z[i:i + L], cal[i:i + L]] for i in st])), torch.tensor(np.stack([z[i + L:i + L + H] for i in st])))
Xtr, Ytr = mk(starts[tr]); Xte, Yte = mk(starts[te]); truth = Yte.numpy() * sd + mu
class CNN(nn.Module):
    def __init__(self): super().__init__(); self.c = nn.Sequential(nn.Conv1d(3, 32, 5, padding=2), nn.ReLU(), nn.Conv1d(32, 32, 5, padding=4, dilation=2), nn.ReLU(), nn.AdaptiveAvgPool1d(8)); self.h = nn.Linear(256, H)
    def forward(self, x): return self.h(self.c(x.transpose(1, 2)).flatten(1))
class LSTM(nn.Module):
    def __init__(self, out=H): super().__init__(); self.r = nn.LSTM(3, 64, batch_first=True); self.h = nn.Linear(64, out)
    def forward(self, x): return self.h(self.r(x)[0][:, -1])
models = {{"MLP": nn.Sequential(nn.Flatten(), nn.Linear(L * 3, 128), nn.ReLU(), nn.Linear(128, H)), "1-D CNN": CNN(), "LSTM": LSTM()}}
def train(m, loss_fn, epochs=15):
    torch.manual_seed(0); opt = torch.optim.Adam(m.parameters(), 2e-3)
    for _ in range(epochs):
        for b in torch.randperm(len(Xtr)).split(64): opt.zero_grad(); loss_fn(m(Xtr[b]), Ytr[b]).backward(); opt.step()
    return m.eval()
clim = s[:train_end].groupby(s.index[:train_end].dayofyear).mean()
base = {{"persistence": np.repeat(Xte[:, -1:, 0].numpy() * sd + mu, H, 1), "climatology": np.stack([clim.reindex(doy[i + L:i + L + H]).to_numpy() for i in starts[te]])}}
for name, p in base.items(): print(f"  {{name:12s}} MAE {{np.abs(p - truth).mean():.2f}} °C | by horizon {{np.abs(p - truth).mean(0).round(2).tolist()}}")
for name, m in models.items():
    torch.manual_seed(0); m = train(m, nn.functional.mse_loss)
    with torch.no_grad(): p = m(Xte).numpy() * sd + mu
    print(f"  {{name:12s}} MAE {{np.abs(p - truth).mean():.2f}} °C | by horizon {{np.abs(p - truth).mean(0).round(2).tolist()}}")
qs = torch.tensor([0.1, 0.5, 0.9])
def pinball(pred, t): e = t.unsqueeze(2) - pred.view(len(t), H, 3); return torch.maximum(qs * e, (qs - 1) * e).mean()
qm = train(LSTM(out=H * 3), pinball)
with torch.no_grad(): q = qm(Xte).view(-1, H, 3).numpy() * sd + mu
print(f"quantile LSTM: 10-90% interval coverage {{((truth >= q[..., 0]) & (truth <= q[..., 2])).mean():.1%}} | mean width {{(q[..., 2] - q[..., 0]).mean():.1f}} °C")
''')
