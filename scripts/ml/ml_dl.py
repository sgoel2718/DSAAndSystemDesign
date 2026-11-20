"""Module 2 + Module 3 foundations: neural networks, training, PyTorch, Keras, CNNs, autoencoders, RNNs, time series."""
from ml_util import M

DL = [
M("m-dl-intro", "Introduction to deep learning: what it is, why now, when to use it", "Basic",
  "Deep learning uses neural networks with many layers that learn features directly from raw data — pixels, audio, text. It powers modern vision, speech, language and generative AI.",
  """### What makes it 'deep'
Many stacked layers, each transforming the previous layer's output into a more abstract representation (edges → shapes → objects; characters → words → meaning). Features are **learned**, not hand-engineered.

### Why it took off around 2012
1. **Data**: internet-scale labelled and unlabeled datasets (ImageNet, web text).
2. **Compute**: GPUs (and later TPUs) made huge matrix multiplications cheap.
3. **Algorithms**: ReLU, better initialisation, dropout, batch norm, residual connections, Adam, attention/transformers.
4. **Software**: TensorFlow, PyTorch, Keras, Hugging Face made it accessible.

### When to use deep learning
|Use deep learning|Prefer classical ML|
|images, audio, video, text, multimodal data|small or medium tabular datasets|
|lots of data (or a pretrained model to fine-tune)|need high interpretability|
|complex patterns, end-to-end learning|tight compute/latency budgets without GPUs|
|generation (text, images)|quick strong baseline (gradient boosting)|

### The deep-learning workflow
Define the problem and data → choose an architecture (MLP, CNN, RNN, transformer — or a pretrained model) → loss + optimiser → train with mini-batches on GPU → monitor train/validation curves → regularise and tune → evaluate on test → deploy and monitor.""",
  code='''
import torch, torch.nn as nn
from sklearn.datasets import make_circles
from sklearn.linear_model import LogisticRegression
X, y = make_circles(1000, noise=0.08, factor=0.5, random_state=0)
print("linear model accuracy:", LogisticRegression().fit(X, y).score(X, y))
Xt, yt = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)[:, None]
torch.manual_seed(0); net = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Linear(16, 16), nn.ReLU(), nn.Linear(16, 1))
opt = torch.optim.Adam(net.parameters(), 1e-2)
for _ in range(300): opt.zero_grad(); nn.functional.binary_cross_entropy_with_logits(net(Xt), yt).backward(); opt.step()
print("small deep network accuracy:", ((net(Xt) > 0).float() == yt).float().mean().item())
print("device available:", "GPU" if torch.cuda.is_available() else "CPU (switch Colab runtime to GPU for big models)")
''',
  say=[("When would you not use deep learning?",
        "\"For small or medium tabular datasets, where gradient-boosted trees usually match or beat neural nets with far less tuning; when the model must be fully interpretable, like some regulated credit decisions; when there's little data and no relevant pretrained model; or when latency, cost or hardware constraints rule it out. I'd start with the simplest model that meets the requirement.\"")]),
M("m-nn-formulation", "Problem formulation for neural networks: inputs, outputs, activations, losses", "Basic",
  "To set up a neural network you decide the input shape, the output layer and its activation, and the loss — all driven by the task type.",
  """|Task|Output layer|Activation|Loss|Prediction|
|Regression (one value)|1 unit|none (linear)|MSE / MAE / Huber|the value|
|Regression, positive values|1 unit|softplus / exp|MSE, Poisson|the value|
|Binary classification|1 unit|sigmoid|binary cross-entropy|p ≥ threshold|
|Multiclass (one of K)|K units|softmax|categorical cross-entropy|argmax|
|Multi-label (any of K)|K units|sigmoid each|binary cross-entropy per label|threshold each|
|Bounding box|4 units|linear / sigmoid|smooth L1, IoU loss|box|
|Sequence (next token)|vocab units per step|softmax|cross-entropy|sample / argmax|
|Embedding / similarity|d units|(L2-normalised)|contrastive / triplet|cosine similarity|

### Other formulation decisions
- **Input pipeline**: scaling, encoding, fixed shapes (resize images, pad sequences).
- **Architecture family**: MLP for tabular, CNN for images/grids, RNN/transformer for sequences, GNN for graphs.
- **Capacity**: layers × width; start small and grow until it overfits, then regularise.
- **Metrics** separate from the loss (accuracy, F1, AUC).
- In PyTorch, `CrossEntropyLoss` takes raw **logits** (it applies log-softmax itself) and `BCEWithLogitsLoss` applies the sigmoid — don't add them twice.""",
  code="""
import torch, torch.nn as nn
x = torch.randn(4, 10)                                     # batch of 4, 10 features
heads = {"regression": (nn.Linear(10, 1), nn.MSELoss(), torch.randn(4, 1)),
         "binary": (nn.Linear(10, 1), nn.BCEWithLogitsLoss(), torch.randint(0, 2, (4, 1)).float()),
         "multiclass (5)": (nn.Linear(10, 5), nn.CrossEntropyLoss(), torch.randint(0, 5, (4,))),
         "multi-label (5)": (nn.Linear(10, 5), nn.BCEWithLogitsLoss(), torch.randint(0, 2, (4, 5)).float())}
for name, (layer, loss_fn, target) in heads.items():
    out = layer(x); print(f"{name:16s} output {tuple(out.shape)}  loss {loss_fn(out, target).item():.3f}")
logits = heads["multiclass (5)"][0](x)
print("softmax probs row 0:", torch.softmax(logits, 1)[0].detach().numpy().round(3), " predicted class:", logits.argmax(1).tolist())
""",
  say=[("What output layer and loss would you use for multi-label image tagging?",
        "\"One output unit per tag with a sigmoid on each — not a softmax, because tags aren't mutually exclusive — and binary cross-entropy summed over tags. In PyTorch I'd output raw logits and use BCEWithLogitsLoss for numerical stability, then tune a threshold per tag on validation data.\"")]),

M("m-perceptron", "The neuron and the perceptron", "Basic",
  "An artificial neuron computes a weighted sum of inputs plus a bias and passes it through an activation. The perceptron (1958) learns its weights by nudging them after each mistake.",
  """### A neuron
z = w·x + b, output a = φ(z) where φ is an activation (step, sigmoid, ReLU…). Inspired by biological neurons (dendrites → soma → axon), but only loosely.

### Perceptron learning rule (Rosenblatt)
For each training example with label y ∈ {−1, +1}: if sign(w·x + b) ≠ y, update **w ← w + η·y·x, b ← b + η·y**.
- **Perceptron convergence theorem**: if the data is linearly separable, it finds a separating line in finite steps.
- It **cannot** learn XOR (Minsky & Papert, 1969) → first AI winter. The fix: multiple layers with non-linear activations.

### Relation to other models
Perceptron with sigmoid + cross-entropy = logistic regression; with hinge loss + margin = linear SVM.""",
  demo="perceptron",
  code="""
import numpy as np
def perceptron(X, y, epochs=20, lr=1.0):
    w, b = np.zeros(X.shape[1]), 0.0
    for ep in range(epochs):
        errors = 0
        for xi, yi in zip(X, y):
            if yi * (xi @ w + b) <= 0:
                w += lr * yi * xi; b += lr * yi; errors += 1
        if errors == 0: return w, b, ep + 1
    return w, b, None
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], float)
for name, y in [("AND", [-1, -1, -1, 1]), ("OR", [-1, 1, 1, 1]), ("XOR", [-1, 1, 1, -1])]:
    w, b, ep = perceptron(X, np.array(y))
    print(f"{name}: " + (f"converged in {ep} epochs, w={w}, b={b}" if ep else "never converges (not linearly separable)"))
""",
  say=[("Why can't a single perceptron solve XOR, and how do multi-layer networks fix it?",
        "\"A perceptron draws one straight line, and XOR's positive points sit on opposite corners, so no line separates them. Adding a hidden layer with a non-linear activation lets the network first compute intermediate features — like OR and NAND — and then combine them linearly, which solves XOR. That's the core reason deep networks need non-linear activations.\"")]),

M("m-mlp", "Multilayer perceptrons (MLP) and non-linear solutions", "Basic",
  "An MLP stacks layers of neurons with non-linear activations. Hidden layers transform the input step by step until the problem becomes linearly separable for the output layer.",
  """### Architecture
Input → hidden layer(s) (dense/fully connected + activation) → output layer. Each layer: **h = φ(Wx + b)**.

### Why non-linearity matters
Without activations, any stack of layers collapses to one linear map (W₂W₁x = Wx). Non-linear activations let networks bend the decision boundary.

### Universal approximation theorem
One hidden layer with enough units can approximate any continuous function on a bounded domain — but depth makes it far more *efficient* (fewer units) and learnable.

### Designing an MLP
- Width 32–512, depth 2–4 for tabular data; ReLU in hidden layers.
- Start simple; add capacity until training loss is low; then regularise (dropout, weight decay, early stopping).
- Scale inputs. For tabular data, gradient boosting usually still wins — MLPs shine when combined with embeddings or other modalities.
- scikit-learn has `MLPClassifier` / `MLPRegressor` for quick experiments; PyTorch/Keras for anything serious.""",
  demo="nn",
  code="""
import numpy as np, torch, torch.nn as nn
from sklearn.datasets import make_moons
from sklearn.neural_network import MLPClassifier, MLPRegressor

X, y = make_moons(600, noise=0.2, random_state=0)
print("sklearn MLP (2 hidden layers):", MLPClassifier(hidden_layer_sizes=(32, 32), max_iter=2000, random_state=0).fit(X, y).score(X, y))
x = np.linspace(-3, 3, 200)[:, None]
print("MLP regression of sin(x), R^2:", round(MLPRegressor(hidden_layer_sizes=(64, 64), max_iter=3000, random_state=0).fit(x, np.sin(x).ravel()).score(x, np.sin(x).ravel()), 3))

torch.manual_seed(0)
Xt, yt = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32), torch.tensor([[0], [1], [1], [0]], dtype=torch.float32)
net = nn.Sequential(nn.Linear(2, 4), nn.Tanh(), nn.Linear(4, 1))                  # solves XOR
opt = torch.optim.Adam(net.parameters(), lr=0.05)
for _ in range(1000):
    opt.zero_grad(); loss = nn.functional.binary_cross_entropy_with_logits(net(Xt), yt); loss.backward(); opt.step()
print("XOR predictions:", (torch.sigmoid(net(Xt)) > 0.5).int().ravel().tolist(), " loss", round(loss.item(), 4))
linear_only = nn.Sequential(nn.Linear(2, 4), nn.Linear(4, 1))
W = linear_only[1].weight @ linear_only[0].weight
print("two linear layers collapse to one 1x2 matrix:", tuple(W.shape))
""",
  say=[("What happens if you remove all activation functions from a deep network?",
        "\"It becomes a single linear transformation — the product of the weight matrices — no matter how many layers, so it can only learn linear decision boundaries, like logistic or linear regression. Non-linear activations are what let depth add expressive power.\"")]),

M("m-activations", "Activation functions: sigmoid, tanh, ReLU, Leaky ReLU, GELU, softmax", "Basic",
  "Activation functions add non-linearity. ReLU-family functions are the default in hidden layers; sigmoid and softmax turn outputs into probabilities.",
  """|Activation|Formula|Range|Pros|Cons / use|
|Sigmoid|1/(1+e^−x)|(0, 1)|probability output|saturates ⇒ vanishing gradients; not zero-centred; use for binary outputs and gates|
|Tanh|(eˣ−e^−x)/(eˣ+e^−x)|(−1, 1)|zero-centred|still saturates; RNN hidden states|
|ReLU|max(0, x)|[0, ∞)|cheap, no saturation for x>0, sparse|"dying ReLU" (stuck at 0)|
|Leaky ReLU / PReLU|max(αx, x)|ℝ|fixes dying ReLU|extra hyperparameter|
|ELU / SELU|smooth negative part|ℝ|faster convergence; SELU self-normalises|more compute|
|GELU|x·Φ(x)|ℝ|smooth; used in BERT, GPT, ViT|—|
|Swish / SiLU|x·σ(x)|ℝ|smooth; EfficientNet, LLaMA (SwiGLU)|—|
|Softmax|eᶻᵏ/Σeᶻʲ|probabilities summing to 1|multiclass output|use log-softmax for stability|
|Softplus|log(1+eˣ)|(0, ∞)|smooth ReLU, positive outputs|—|

**Default**: ReLU (or GELU in transformers) for hidden layers; output activation chosen by the task. **Temperature** in softmax (z/T) controls sharpness — used in LLM sampling and distillation.""",
  code="""
import torch, torch.nn.functional as F
x = torch.linspace(-4, 4, 9, requires_grad=True)
for name, fn in [("sigmoid", torch.sigmoid), ("tanh", torch.tanh), ("relu", F.relu), ("leaky_relu", lambda t: F.leaky_relu(t, 0.1)), ("gelu", F.gelu), ("silu", F.silu)]:
    y = fn(x); g, = torch.autograd.grad(y.sum(), x)
    print(f"{name:10s} values {y.detach().numpy().round(2)}\\n{'':10s} grads  {g.numpy().round(2)}")
z = torch.tensor([2.0, 1.0, 0.1])
for T in (0.5, 1.0, 5.0):
    print(f"softmax T={T}:", torch.softmax(z / T, 0).numpy().round(3))
""",
  say=[("Why is ReLU preferred over sigmoid in hidden layers?",
        "\"Sigmoid saturates: for large positive or negative inputs its gradient is nearly zero, and its maximum derivative is only 0.25, so gradients shrink multiplicatively through layers — vanishing gradients. ReLU has gradient 1 for positive inputs, is cheap to compute and gives sparse activations, so deep networks train much faster. Its weakness, dead units, is handled by Leaky ReLU or GELU.\"")]),

M("m-loss-functions", "Loss functions: MSE, MAE, Huber, cross-entropy, hinge, focal, contrastive", "Intermediate",
  "The loss tells the optimiser what 'wrong' means. Choosing it encodes your assumptions about noise, outliers and which mistakes matter.",
  """|Loss|Formula (per sample)|Use|
|MSE (L2)|(y − ŷ)²|regression; Gaussian noise; punishes large errors|
|MAE (L1)|\\|y − ŷ\\||regression robust to outliers; predicts the median|
|Huber / smooth L1|quadratic near 0, linear far away|robust regression, bounding boxes|
|Quantile (pinball)|max(τe, (τ−1)e)|prediction intervals, demand forecasting|
|Binary cross-entropy|−[y log p + (1−y) log(1−p)]|binary / multi-label classification|
|Categorical cross-entropy|−log p(true class)|multiclass, language modelling|
|Label smoothing CE|targets 0.9/0.1 instead of 1/0|reduces over-confidence|
|Focal loss|−(1 − p)^γ log p|class imbalance, object detection (RetinaNet)|
|Hinge|max(0, 1 − y·f(x))|SVMs (margin)|
|KL divergence|Σ p log(p/q)|distillation, VAEs, RLHF penalty|
|Contrastive / triplet / InfoNCE|pull similar pairs together, push others apart|Siamese nets, CLIP, embeddings|
|Dice / IoU loss|1 − overlap|segmentation|

Loss ≠ metric: train with a smooth, differentiable loss; report the business metric.""",
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
y, yhat = torch.tensor([3.0, 5.0, 2.0, 10.0]), torch.tensor([2.5, 5.5, 2.0, 4.0])      # last one is a big miss
print("MSE", nn.MSELoss()(yhat, y).item(), " MAE", nn.L1Loss()(yhat, y).item(), " Huber", round(nn.HuberLoss(delta=1.0)(yhat, y).item(), 3))

logits, target = torch.tensor([[2.0, 0.5, -1.0]]), torch.tensor([0])
print("cross-entropy", round(F.cross_entropy(logits, target).item(), 4), " with label smoothing 0.1:", round(F.cross_entropy(logits, target, label_smoothing=0.1).item(), 4))
def focal(logit, t, gamma=2.0):
    p = torch.sigmoid(logit); pt = torch.where(t == 1, p, 1 - p)
    return (-(1 - pt) ** gamma * torch.log(pt)).mean()
easy, hard = torch.tensor([4.0]), torch.tensor([-1.0]); t1 = torch.tensor([1.0])
print("BCE easy/hard:", round(F.binary_cross_entropy_with_logits(easy, t1).item(), 4), round(F.binary_cross_entropy_with_logits(hard, t1).item(), 4),
      "| focal easy/hard:", round(focal(easy, t1).item(), 5), round(focal(hard, t1).item(), 4))
""",
  say=[("When would you use Huber loss instead of MSE?",
        "\"When the regression targets have outliers or heavy-tailed noise. Huber behaves like MSE for small errors — smooth, well-behaved gradients — but like MAE for large errors, so a few extreme points don't dominate training. It's used for bounding-box regression in detectors and in robust forecasting.\"")]),

M("m-backprop", "Gradient descent and backpropagation", "Intermediate",
  "Backpropagation computes the gradient of the loss with respect to every weight using the chain rule, going backwards through the network. Gradient descent then updates each weight a small step against its gradient.",
  """### Training loop
1. **Forward pass**: compute activations layer by layer and the loss.
2. **Backward pass**: starting from ∂L/∂output, apply the chain rule layer by layer. For a dense layer z = Wa + b, a′ = φ(z): δ = ∂L/∂z = ∂L/∂a′ ⊙ φ′(z); then ∂L/∂W = δ aᵀ, ∂L/∂b = δ, and ∂L/∂a = Wᵀδ is passed to the previous layer.
3. **Update**: W ← W − η ∂L/∂W.

### Gradient descent variants
- **Batch GD**: whole dataset per step — accurate, slow, memory-heavy.
- **Stochastic GD (SGD)**: one sample per step — noisy, can escape shallow minima.
- **Mini-batch GD**: 32–1024 samples per step — the standard; matches GPU parallelism. An **epoch** = one pass over the data.

### Computational graph and autograd
Frameworks record operations in a graph and run reverse-mode automatic differentiation — cost ≈ 2–3× a forward pass regardless of the number of weights. That efficiency is why deep learning is possible.""",
  demo="gd",
  code="""
import numpy as np, torch
rng = np.random.default_rng(0)
X = rng.normal(size=(64, 3)); y = (X[:, :1] - 2 * X[:, 1:2] > 0).astype(float)
W1, b1 = rng.normal(0, 0.5, (3, 8)), np.zeros(8); W2, b2 = rng.normal(0, 0.5, (8, 1)), np.zeros(1)
sig = lambda z: 1 / (1 + np.exp(-z))

def forward_backward(W1, b1, W2, b2):
    z1 = X @ W1 + b1; a1 = np.maximum(z1, 0); z2 = a1 @ W2 + b2; p = sig(z2)
    loss = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    d2 = (p - y) / len(X)                                   # dL/dz2 for sigmoid + BCE
    gW2, gb2 = a1.T @ d2, d2.sum(0); d1 = (d2 @ W2.T) * (z1 > 0)   # chain rule through ReLU
    gW1, gb1 = X.T @ d1, d1.sum(0)
    return loss, (gW1, gb1, gW2, gb2)

loss, grads = forward_backward(W1, b1, W2, b2)
t = [torch.tensor(a, requires_grad=True) for a in (W1, b1, W2, b2)]   # compare with autograd
p = torch.sigmoid(torch.relu(torch.tensor(X) @ t[0] + t[1]) @ t[2] + t[3])
torch.nn.functional.binary_cross_entropy(p, torch.tensor(y)).backward()
print("manual backprop matches autograd:", all(np.allclose(g, ti.grad.numpy()) for g, ti in zip(grads, t)))
for step in range(300):                                    # mini network trained with gradient descent
    loss, (gW1, gb1, gW2, gb2) = forward_backward(W1, b1, W2, b2)
    W1 -= 0.5 * gW1; b1 -= 0.5 * gb1; W2 -= 0.5 * gW2; b2 -= 0.5 * gb2
    if step % 100 == 0: print(f"step {step:3d} loss {loss:.4f}")
print("final loss", round(loss, 4))
""",
  say=[("Walk me through backpropagation.",
        "\"First a forward pass computes each layer's outputs and the loss, caching intermediate values. Then starting from the derivative of the loss with respect to the output, we apply the chain rule backwards: each layer multiplies the incoming gradient by its local derivative to get gradients for its weights and for its input, which becomes the incoming gradient for the previous layer. Finally an optimiser like SGD or Adam updates the weights. Autograd frameworks do exactly this on the computational graph.\"")]),

M("m-optimizers", "Optimisers and learning-rate schedules: SGD, momentum, RMSProp, Adam, AdamW", "Intermediate",
  "Optimisers decide how to use gradients to update weights. Momentum smooths the path; adaptive methods like Adam give each weight its own step size. Schedules change the learning rate over training.",
  """|Optimiser|Update idea|Notes|
|SGD|w −= η g|simple; with tuning generalises very well (vision)|
|SGD + momentum|v = βv + g; w −= ηv|rolls through ravines and small bumps; β ≈ 0.9; Nesterov looks ahead|
|AdaGrad|divide by √(sum of past g²)|good for sparse features; rate decays to zero|
|RMSProp|divide by √(moving average of g²)|fixes AdaGrad decay; RNNs|
|Adam|momentum (1st moment) + RMSProp (2nd moment) + bias correction|default for most deep learning; lr ≈ 1e-3 (3e-4 for transformers)|
|AdamW|Adam with *decoupled* weight decay|standard for transformers/LLMs|
|Lion, Adafactor, LAMB|memory-efficient or large-batch variants|LLM training|

### Learning-rate schedules
Step decay, exponential decay, **cosine annealing**, **linear warm-up** then decay (transformers), one-cycle policy, reduce-on-plateau. A **learning-rate finder** (sweep lr up while watching loss) picks a good start.

### Batch size
Larger batches = smoother gradients and better GPU use but may generalise slightly worse; scale lr roughly with batch size. Gradient accumulation simulates big batches on small GPUs.""",
  code="""
import torch
def rosenbrock(p): x, y = p; return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2
for name, make in [("SGD", lambda p: torch.optim.SGD(p, lr=1e-3)), ("SGD+momentum", lambda p: torch.optim.SGD(p, lr=1e-3, momentum=0.9)),
                   ("RMSprop", lambda p: torch.optim.RMSprop(p, lr=1e-2)), ("Adam", lambda p: torch.optim.Adam(p, lr=2e-2)), ("AdamW", lambda p: torch.optim.AdamW(p, lr=2e-2, weight_decay=0.0))]:
    p = torch.tensor([-1.5, 2.0], requires_grad=True); opt = make([p])
    for _ in range(2000):
        opt.zero_grad(); loss = rosenbrock(p); loss.backward(); opt.step()
    print(f"{name:13s} reached {p.detach().numpy().round(3)} loss {loss.item():.2e}  (minimum at [1, 1])")

w = torch.zeros(1, requires_grad=True); opt = torch.optim.AdamW([w], lr=1e-3)
sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=1e-3, total_steps=100, pct_start=0.1)
lrs = []
for _ in range(100): opt.step(); sched.step(); lrs.append(opt.param_groups[0]["lr"])
print("one-cycle lr at steps 0, 10, 50, 99:", [f"{lrs[i]:.1e}" for i in (0, 10, 50, 99)])
""",
  say=[("How does Adam work, and why AdamW?",
        "\"Adam keeps two exponential moving averages per parameter: of the gradient, like momentum, and of the squared gradient, like RMSProp. It divides the first by the square root of the second, with bias correction for early steps, so each parameter gets an adaptive step size. AdamW fixes how weight decay is applied: in Adam, L2 added to the gradient gets rescaled by the adaptive denominator, so it's inconsistent; AdamW applies decay directly to the weights, which regularises properly and is the standard for transformers.\"")]),

M("m-init-norm", "Weight initialisation, batch normalisation and layer normalisation", "Intermediate",
  "Good initialisation keeps signals and gradients at a healthy scale through deep networks; normalisation layers keep activations stable during training, allowing higher learning rates.",
  """### Initialisation
- All zeros ⇒ every neuron learns the same thing (symmetry). Use small random values with the right variance:
- **Xavier/Glorot**: Var = 2/(fan_in + fan_out) — for tanh/sigmoid.
- **He/Kaiming**: Var = 2/fan_in — for ReLU (PyTorch's default for Linear/Conv uses a Kaiming-uniform variant).
- Pretrained weights are the best initialisation of all (transfer learning).

### Batch normalisation (BatchNorm)
Normalise each feature over the mini-batch to mean 0, var 1, then scale and shift with learned γ, β. Uses running averages at inference (`model.eval()`!). Faster training, higher learning rates, mild regularisation. Weak with tiny batches; standard in CNNs.

### Layer normalisation (LayerNorm)
Normalise across features of each single example — independent of batch size. Standard in transformers and RNNs. **RMSNorm** (LLaMA) drops the mean subtraction.

### Others
Group norm and instance norm (style transfer, small batches); weight normalisation; residual connections + normalisation make very deep nets trainable.""",
  code="""
import torch, torch.nn as nn
torch.manual_seed(0)
def depth_test(init, act):
    x = torch.randn(512, 256)
    for _ in range(30):
        layer = nn.Linear(256, 256, bias=False); init(layer.weight); x = act(layer(x))
    return x.std().item()
print("30 ReLU layers, std of activations:")
print("  small random N(0, 0.01):", f"{depth_test(lambda w: nn.init.normal_(w, 0, 0.01), torch.relu):.2e}  (vanishes)")
print("  Xavier:                 ", f"{depth_test(nn.init.xavier_normal_, torch.relu):.2e}")
print("  He / Kaiming:           ", f"{depth_test(lambda w: nn.init.kaiming_normal_(w, nonlinearity='relu'), torch.relu):.2e}  (stays healthy)")

x = torch.randn(8, 4) * 10 + 5
bn, ln = nn.BatchNorm1d(4), nn.LayerNorm(4)
print("BatchNorm: per-feature mean over batch ~0:", bn(x).mean(0).detach().numpy().round(3))
print("LayerNorm: per-sample mean over features ~0:", ln(x).mean(1).detach().numpy().round(3))
bn.eval(); print("in eval mode BatchNorm uses running stats:", bn.running_mean.numpy().round(2))
""",
  say=[("What's the difference between BatchNorm and LayerNorm, and why do transformers use LayerNorm?",
        "\"BatchNorm normalises each feature across the examples in a mini-batch, so it depends on batch statistics and behaves differently in training and inference. LayerNorm normalises across the features of each individual example, so it's independent of batch size and sequence length — which suits transformers with variable-length sequences, small per-device batches and autoregressive inference one token at a time.\"")]),

M("m-vanishing", "Vanishing and exploding gradients, residual connections and gradient clipping", "Intermediate",
  "In deep or recurrent networks, gradients are products of many terms and can shrink to nothing or blow up. ReLU, careful initialisation, normalisation, residual connections, LSTMs and clipping fix this.",
  """### Why it happens
Backprop multiplies Jacobians layer after layer. If their scale is < 1, gradients **vanish** — early layers stop learning (sigmoid's derivative ≤ 0.25 makes this certain). If > 1, they **explode** — NaN losses, wild updates. RNNs suffer most because the same weight matrix is multiplied at every time step.

### Fixes
|Problem|Fixes|
|Vanishing|ReLU-family activations, He/Xavier init, BatchNorm/LayerNorm, **residual (skip) connections** (ResNet: y = x + F(x) gives gradients a highway), LSTM/GRU gates, shorter paths (attention)|
|Exploding|**gradient clipping** (clip norm to e.g. 1.0), lower learning rate, normalisation, good init|

### Diagnosing
Log gradient norms per layer; watch for loss = NaN; check activations' mean/std; `torch.nn.utils.clip_grad_norm_` returns the total norm.""",
  code="""
import torch, torch.nn as nn
torch.manual_seed(0)
def first_layer_grad(act, residual=False, depth=40):
    layers = [nn.Linear(64, 64) for _ in range(depth)]
    x = torch.randn(32, 64); h = x
    for l in layers:
        h = h + act(l(h)) * 0.1 if residual else act(l(h))
    h.pow(2).mean().backward(); return layers[0].weight.grad.norm().item()
print(f"40 sigmoid layers: first-layer grad norm {first_layer_grad(torch.sigmoid):.2e}  (vanished)")
print(f"40 ReLU layers:    first-layer grad norm {first_layer_grad(torch.relu):.2e}")
print(f"40 residual layers: first-layer grad norm {first_layer_grad(torch.sigmoid, residual=True):.2e}  (residual highway)")

w = nn.Parameter(torch.tensor([1.0])); (w * 1e6).sum().backward()
total = torch.nn.utils.clip_grad_norm_([w], max_norm=1.0)
print("gradient norm before clipping", round(total.item()), "-> after", w.grad.norm().item())
""",
  say=[("How do residual connections help train very deep networks?",
        "\"A residual block outputs x plus F of x, so the gradient flowing back has a direct identity path that skips the layer's transformation — it can't vanish through the block. Each block only has to learn a small correction, and if it's not useful it can learn near zero, so adding layers doesn't hurt. That's how ResNets reached 150-plus layers, and transformers use the same idea around every attention and feed-forward block.\"")]),

M("m-dl-regularization", "Regularising deep networks: dropout, weight decay, early stopping, augmentation", "Intermediate",
  "Deep networks have millions of parameters and memorise easily. Dropout, weight decay, early stopping, data augmentation and other tricks make them generalise.",
  """- **Dropout**: during training, zero each activation with probability p (0.1–0.5) and scale the rest by 1/(1 − p); at inference use all units. It trains an implicit ensemble of thinned networks and prevents co-adaptation. Remember `model.train()` vs `model.eval()`.
- **Weight decay** (L2 / AdamW decay ~0.01–0.1).
- **Early stopping**: monitor validation loss, stop when it hasn't improved for `patience` epochs, restore the best weights.
- **Data augmentation**: flips, crops, rotations, colour jitter, mixup/cutmix (images); noise, time-shift, SpecAugment (audio); back-translation, synonym swap (text).
- **Label smoothing**, **stochastic depth**, **batch norm**.
- **Smaller model / fewer epochs / transfer learning** (fewer parameters to fit from scratch).
- **More data** remains the best regulariser.""",
  code="""
import torch, torch.nn as nn
torch.manual_seed(0)
drop = nn.Dropout(p=0.5); x = torch.ones(1, 10)
drop.train(); print("train mode:", drop(x).numpy())
drop.eval();  print("eval mode: ", drop(x).numpy())

X = torch.randn(200, 20); y = (X[:, 0] + 0.5 * torch.randn(200) > 0).float()[:, None]
Xtr, ytr, Xva, yva = X[:60], y[:60], X[60:], y[60:]                       # tiny training set -> overfits
def train(dropout, wd, patience=None):
    torch.manual_seed(1)
    net = nn.Sequential(nn.Linear(20, 256), nn.ReLU(), nn.Dropout(dropout), nn.Linear(256, 256), nn.ReLU(), nn.Dropout(dropout), nn.Linear(256, 1))
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=wd); lossf = nn.BCEWithLogitsLoss(); best, wait, best_state = 1e9, 0, None
    for ep in range(400):
        net.train(); opt.zero_grad(); lossf(net(Xtr), ytr).backward(); opt.step()
        net.eval()
        with torch.no_grad(): v = lossf(net(Xva), yva).item()
        if v < best: best, wait, best_state = v, 0, {k: t.clone() for k, t in net.state_dict().items()}
        else: wait += 1
        if patience and wait >= patience: break
    if patience: net.load_state_dict(best_state)
    with torch.no_grad(): return ((net(Xva) > 0).float() == yva).float().mean().item(), ep + 1
for name, args in [("no regularisation", (0.0, 0.0)), ("dropout 0.5 + weight decay", (0.5, 0.1)), ("early stopping (patience 20)", (0.0, 0.0, 20))]:
    acc, eps = train(*args); print(f"{name:30s} val accuracy {acc:.3f}  epochs run {eps}")
""",
  say=[("Why does dropout behave differently in training and inference?",
        "\"In training it randomly zeroes units and scales the survivors by one over keep-probability, so each step trains a different thinned network and no unit can rely on specific others. At inference we want a deterministic prediction that approximates averaging all those thinned networks, so dropout is turned off — and because of the scaling during training, the expected activations already match. Forgetting model.eval() is a classic bug.\"")]),

M("m-pytorch", "PyTorch: tensors, autograd, nn.Module, Dataset/DataLoader, training loop, GPU", "Intermediate",
  "PyTorch is the most popular deep-learning framework in research and industry: Pythonic, eager execution, and you write the training loop yourself.",
  """### Building blocks
- **Tensor**: NumPy-like array that can live on a GPU (`.to("cuda")`) and track gradients (`requires_grad=True`).
- **Autograd**: `loss.backward()` fills `.grad` of every parameter.
- **nn.Module**: define layers in `__init__`, computation in `forward`. `nn.Sequential` for simple stacks.
- **Dataset / DataLoader**: `__len__` + `__getitem__`; the DataLoader batches, shuffles and loads in parallel workers.
- **Optimiser** (`torch.optim.AdamW`) and **loss** (`nn.CrossEntropyLoss`).

### The canonical training loop
for each epoch: `model.train()` → for each batch: `optimizer.zero_grad()` → `loss = loss_fn(model(x), y)` → `loss.backward()` → `optimizer.step()`; then `model.eval()` + `torch.no_grad()` for validation.

### Practical
- Device-agnostic code: `device = "cuda" if torch.cuda.is_available() else "cpu"` (Colab: Runtime → Change runtime type → GPU).
- Save: `torch.save(model.state_dict(), "model.pt")`; load into the same class.
- **Mixed precision** (`torch.autocast`) for speed; `torch.compile` for faster graphs.
- Ecosystem: torchvision, torchaudio, PyTorch Lightning, Hugging Face (built on PyTorch).""",
  code="""
import torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.datasets import load_digits

device = "cuda" if torch.cuda.is_available() else "cpu"; torch.manual_seed(0)
class DigitsDataset(Dataset):
    def __init__(self):
        d = load_digits(); self.X = torch.tensor(d.data / 16, dtype=torch.float32); self.y = torch.tensor(d.target)
    def __len__(self): return len(self.y)
    def __getitem__(self, i): return self.X[i], self.y[i]
train_ds, val_ds = random_split(DigitsDataset(), [1500, 297], generator=torch.Generator().manual_seed(0))
train_dl, val_dl = DataLoader(train_ds, batch_size=64, shuffle=True), DataLoader(val_ds, batch_size=256)

class MLP(nn.Module):
    def __init__(self):
        super().__init__(); self.net = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Dropout(0.2), nn.Linear(128, 10))
    def forward(self, x): return self.net(x)
model = MLP().to(device); opt = torch.optim.AdamW(model.parameters(), lr=1e-3); loss_fn = nn.CrossEntropyLoss()
for epoch in range(15):
    model.train()
    for xb, yb in train_dl:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad(); loss = loss_fn(model(xb), yb); loss.backward(); opt.step()
    model.eval(); correct = 0
    with torch.no_grad():
        for xb, yb in val_dl: correct += (model(xb.to(device)).argmax(1).cpu() == yb).sum().item()
    if epoch % 5 == 4: print(f"epoch {epoch + 1}: train loss {loss.item():.3f}  val accuracy {correct / len(val_ds):.3f}")
torch.save(model.state_dict(), "digits_mlp.pt"); m2 = MLP(); m2.load_state_dict(torch.load("digits_mlp.pt")); print("saved and reloaded on", device)
""",
  say=[("What are the steps of a PyTorch training iteration, and what goes wrong if you forget zero_grad?",
        "\"Zero the gradients, forward pass, compute the loss, backward to compute gradients, optimiser step. PyTorch accumulates gradients in .grad by default, so without zero_grad each step uses the sum of all previous gradients and training diverges — though deliberate accumulation over several batches is how we simulate larger batch sizes.\"")]),

M("m-keras", "TensorFlow and Keras: Sequential and functional APIs, compile/fit, callbacks", "Intermediate",
  "Keras is a high-level API: define layers, `compile` with an optimiser and loss, then `fit`. Keras 3 runs on TensorFlow, PyTorch or JAX backends.",
  """### Three ways to build models
1. **Sequential**: a plain stack of layers.
2. **Functional API**: layers as functions on tensors — multiple inputs/outputs, skip connections.
3. **Subclassing** `keras.Model` with a custom `call` — full flexibility.

### Workflow
`model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])` → `model.fit(X, y, validation_split=0.2, epochs=…, batch_size=…, callbacks=[EarlyStopping(...), ModelCheckpoint(...)])` → `model.evaluate` → `model.predict` → `model.save("model.keras")`.

### TensorFlow ecosystem
`tf.data` input pipelines, TensorBoard, TF Serving, **TensorFlow Lite / LiteRT** for mobile and edge, TensorFlow.js for browsers, TPUs on Colab/Google Cloud.

### PyTorch vs TensorFlow/Keras
PyTorch dominates research and LLM work (Hugging Face); Keras is quickest for standard models and education; TensorFlow remains strong in production/mobile. Concepts transfer directly: layers, losses, optimisers, callbacks ≈ training-loop hooks.""",
  code="""
import os; os.environ.setdefault("KERAS_BACKEND", "torch")      # in Colab Keras uses TensorFlow by default; any backend works
import numpy as np, keras
from keras import layers
from sklearn.datasets import load_digits
X, y = load_digits(return_X_y=True); X = (X / 16).astype("float32")
keras.utils.set_random_seed(0)

seq = keras.Sequential([keras.Input((64,)), layers.Dense(128, activation="relu"), layers.Dropout(0.2), layers.Dense(10, activation="softmax")])
seq.compile(optimizer=keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
hist = seq.fit(X, y, validation_split=0.2, epochs=30, batch_size=64, verbose=0,
               callbacks=[keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)])
print("Sequential: epochs run", len(hist.history["loss"]), " best val accuracy", round(max(hist.history["val_accuracy"]), 3))

inp = keras.Input((64,)); h = layers.Dense(64, activation="relu")(inp)
skip = layers.Add()([h, layers.Dense(64, activation="relu")(h)])         # functional API: a skip connection
out_digit = layers.Dense(10, activation="softmax", name="digit")(skip); out_even = layers.Dense(1, activation="sigmoid", name="is_even")(skip)
multi = keras.Model(inp, [out_digit, out_even])
multi.compile("adam", loss={"digit": "sparse_categorical_crossentropy", "is_even": "binary_crossentropy"})
multi.fit(X, {"digit": y, "is_even": (y % 2 == 0).astype("float32")}, epochs=5, verbose=0)
print("functional model outputs:", [o.shape for o in multi.predict(X[:2], verbose=0)])
seq.save("digits.keras"); print("reloaded:", keras.models.load_model("digits.keras").count_params(), "parameters")
""",
  say=[("When would you use the Keras functional API instead of Sequential?",
        "\"Whenever the model isn't a single straight stack: multiple inputs, like an image plus tabular metadata; multiple outputs, like a class and a bounding box; shared layers, like a Siamese network; or skip connections, like ResNet blocks. Sequential is only for one input, one output, layer after layer.\"")]),

M("m-cnn", "Convolutional neural networks (CNN): convolution, pooling, feature maps", "Intermediate",
  "CNNs slide small learnable filters over an image to detect local patterns — edges, textures, parts, objects — sharing the same weights everywhere, which makes them efficient and translation-equivariant.",
  """### Convolution layer
A k×k filter (kernel) slides over the input; at each position it computes a dot product, producing a **feature map**. A layer has many filters (output channels).
- **Stride**: step size (2 halves the size). **Padding**: add a border ("same" keeps size).
- Output size = ⌊(n + 2p − k)/s⌋ + 1.
- Parameters per layer = (k·k·C_in + 1)·C_out — independent of image size (**weight sharing**).

### Pooling
Max or average pooling (2×2, stride 2) downsamples, adding small translation invariance. **Global average pooling** at the end replaces big dense layers.

### Typical architecture
[Conv → BatchNorm → ReLU] × n → Pool → … → Global pool → Dense → Softmax. Channels grow (32→64→128) while spatial size shrinks.

### Why CNNs beat MLPs on images
Local connectivity + weight sharing = far fewer parameters; hierarchy of features; spatial structure preserved. Also used for audio spectrograms, time series (1-D conv), text, and video (3-D conv).

### Receptive field
The input region a unit "sees"; it grows with depth, stride and dilation — deep units see whole objects.""",
  demo="conv",
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
img = torch.zeros(1, 1, 8, 8); img[..., :, 4:] = 1.0                       # left dark, right bright
sobel_x = torch.tensor([[[[-1, 0, 1], [-2, 0, 2], [-1, 0, 1.0]]]])
print("vertical-edge feature map (row 0):", F.conv2d(img, sobel_x, padding=1)[0, 0, 0].tolist())

class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2),
                                      nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.AdaptiveAvgPool2d(1))
        self.head = nn.Linear(32, 10)
    def forward(self, x): return self.head(self.features(x).flatten(1))
d = load_digits(); X = torch.tensor(d.images / 16, dtype=torch.float32)[:, None]; y = torch.tensor(d.target)
torch.manual_seed(0); net = SmallCNN(); opt = torch.optim.Adam(net.parameters(), 3e-3)
print("parameters:", sum(p.numel() for p in net.parameters()), " shape after features:", tuple(net.features(X[:2]).shape))
for epoch in range(8):
    net.train()
    for i in range(0, 1500, 64):
        opt.zero_grad(); F.cross_entropy(net(X[i:i + 64]), y[i:i + 64]).backward(); opt.step()
net.eval()
with torch.no_grad(): print("test accuracy on held-out digits:", round((net(X[1500:]).argmax(1) == y[1500:]).float().mean().item(), 3))
""",
  say=[("Why are CNNs better than fully connected networks for images?",
        "\"Images have local structure and the same pattern can appear anywhere. Convolutions connect each unit only to a small neighbourhood and reuse the same filter across positions, so a CNN has far fewer parameters, is translation-equivariant, and builds a hierarchy from edges to textures to parts to objects. An MLP on a 224 by 224 image would need millions of weights per layer and would have to learn each pattern at every location separately.\"")]),

M("m-cnn-understand", "Appreciating CNNs: what layers learn, receptive fields, visualisation, Grad-CAM", "Intermediate",
  "Looking inside CNNs shows early layers detect edges and colours, middle layers textures and parts, and deep layers whole objects. Visualisation tools explain predictions and reveal shortcuts.",
  """### What each depth learns (Zeiler & Fergus, 2013)
Layer 1: oriented edges, colour blobs (like Gabor filters). Layers 2–3: corners, textures, patterns. Layers 4–5: object parts (eyes, wheels) and whole objects.

### Visualisation techniques
- **Filter visualisation**: plot first-layer weights.
- **Feature maps / activations** for an input image.
- **Activation maximisation**: optimise an input to excite a neuron (DeepDream).
- **Saliency maps**: gradient of the class score w.r.t. pixels.
- **Grad-CAM**: weight the last conv layer's feature maps by the gradient of the class score → heatmap of *where* the model looked.
- **Occlusion sensitivity**: slide a grey patch and watch the score drop.
- **t-SNE of embeddings**: are classes separated?

### Why it matters
Catches **shortcut learning** (a "husky vs wolf" model looking at snow, a medical model reading the hospital's watermark), builds trust, helps debug data. CNNs are also biased toward texture over shape — augmentation helps.

### Key properties
Translation equivariance (conv) → invariance (pooling); not naturally rotation/scale invariant — learned from augmentation.""",
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
torch.manual_seed(0)
# class 1 images contain a bright cross somewhere; class 0 contain a bright square; we check the heatmap lands on the object
def make(n):
    X = 0.1 * torch.randn(n, 1, 16, 16); y = torch.randint(0, 2, (n,)); pos = torch.randint(1, 12, (n, 2))
    for i in range(n):
        r, c = pos[i].tolist()
        if y[i]: X[i, 0, r + 1, c:c + 3] = 1; X[i, 0, r:r + 3, c + 1] = 1
        else: X[i, 0, r:r + 3, c:c + 3] = 1
    return X, y, pos
X, y, pos = make(600)
conv = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.Conv2d(16, 16, 3, padding=1), nn.ReLU())
head = nn.Linear(16, 2); opt = torch.optim.Adam(list(conv.parameters()) + list(head.parameters()), 3e-3)
for ep in range(15):
    for i in range(0, 600, 50):
        opt.zero_grad(); F.cross_entropy(head(conv(X[i:i+50]).amax((2, 3))), y[i:i+50]).backward(); opt.step()
Xt, yt, pt = make(200)
with torch.no_grad(): print("accuracy:", (head(conv(Xt).amax((2,3))).argmax(1) == yt).float().mean().item())
k = (yt == 1).nonzero()[0].item(); x = Xt[k:k+1]; r, c = pt[k].tolist()
fmap = conv(x); fmap.retain_grad(); score = head(fmap.amax((2, 3)))[0, 1]; score.backward()
w = fmap.grad.mean((2, 3), keepdim=True); cam = F.relu((w * fmap).sum(1))[0].detach()
peak = divmod(cam.argmax().item(), 16)
print("object at rows", r, "-", r + 2, "cols", c, "-", c + 2, "| Grad-CAM peak at", peak)
x2 = x.clone().requires_grad_(True); head(conv(x2).amax((2, 3)))[0, 1].backward()
print("saliency peak at", divmod(x2.grad.abs()[0, 0].argmax().item(), 16))
""",
  say=[("How would you check what a trained image classifier is actually looking at?",
        "\"Use Grad-CAM to get a heatmap of the regions driving each prediction, plus occlusion tests and saliency maps, on correct and wrong predictions. If the heat is on background, watermarks or borders instead of the object, the model learned a shortcut — then I'd fix the data with better sampling, augmentation or masking, and re-check.\"")]),

M("m-autoencoder", "Autoencoders: undercomplete, denoising, sparse and their uses", "Intermediate",
  "An autoencoder learns to compress input into a small code (encoder) and reconstruct it (decoder). The bottleneck forces it to keep only the important structure.",
  """### Architecture
x → **encoder** → z (latent code, smaller than x) → **decoder** → x̂. Trained to minimise reconstruction loss ‖x − x̂‖² (or BCE for pixels in [0, 1]) — no labels needed (self-supervised).

### Variants
|Type|Trick|Use|
|Undercomplete|small bottleneck|non-linear dimensionality reduction (linear AE ≈ PCA)|
|Denoising|corrupt input, reconstruct clean|denoising images/audio, robust features|
|Sparse|penalty on code activations|interpretable features (also used to interpret LLMs)|
|Convolutional|conv encoder, transposed-conv/upsample decoder|images, image reconstruction, inpainting|
|Variational (VAE)|probabilistic latent space + KL term|generation (see Module 4)|
|Sequence / LSTM AE|recurrent encoder/decoder|time-series anomalies|

### Applications
Anomaly detection (high reconstruction error on unusual inputs — bearing faults, fraud), compression, denoising, pretraining, image reconstruction and super-resolution, recommendation embeddings.""",
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
torch.manual_seed(0)
X = torch.tensor(load_digits().images / 16, dtype=torch.float32)[:, None]      # 1797 x 1 x 8 x 8
class ConvAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc = nn.Sequential(nn.Conv2d(1, 16, 3, stride=2, padding=1), nn.ReLU(), nn.Flatten(), nn.Linear(16 * 4 * 4, 8))
        self.dec = nn.Sequential(nn.Linear(8, 16 * 4 * 4), nn.ReLU(), nn.Unflatten(1, (16, 4, 4)),
                                 nn.ConvTranspose2d(16, 1, 4, stride=2, padding=1), nn.Sigmoid())
    def forward(self, x): return self.dec(self.enc(x))
ae = ConvAE(); opt = torch.optim.Adam(ae.parameters(), 3e-3)
for epoch in range(40):                                           # denoising: noisy input, clean target
    noisy = (X + 0.3 * torch.randn_like(X)).clamp(0, 1)
    opt.zero_grad(); loss = F.mse_loss(ae(noisy), X); loss.backward(); opt.step()
print("64 pixels -> 8 numbers -> 64 pixels, reconstruction MSE:", round(loss.item(), 4))
with torch.no_grad():
    normal_err = F.mse_loss(ae(X[:100]), X[:100], reduction="none").mean((1, 2, 3))
    weird = torch.rand(100, 1, 8, 8); weird_err = F.mse_loss(ae(weird), weird, reduction="none").mean((1, 2, 3))
print("anomaly detection: mean error on digits", round(normal_err.mean().item(), 4), "vs random noise images", round(weird_err.mean().item(), 4))
""",
  say=[("How can an autoencoder detect anomalies?",
        "\"Train it only on normal data so it learns to reconstruct normal patterns well. At inference, anomalies — which it has never seen — reconstruct poorly, so the reconstruction error is the anomaly score. I'd set the threshold from a high percentile of errors on held-out normal data and validate with any labelled anomalies. It's common for machine vibration, network traffic and transaction data.\"")]),

M("m-rnn", "Recurrent neural networks (RNN) for sequences", "Intermediate",
  "RNNs process sequences one step at a time, carrying a hidden state that summarises what they've seen so far — text, speech, sensor readings, stock prices.",
  """### The recurrence
**hₜ = tanh(Wₓxₜ + Wₕhₜ₋₁ + b)**, output yₜ = W_y hₜ. The **same weights at every time step** (weight sharing over time), so it handles any sequence length.

### Input/output patterns
|Pattern|Example|
|one-to-many|image captioning, music generation|
|many-to-one|sentiment of a review, activity from sensor windows|
|many-to-many (aligned)|part-of-speech tagging, frame labelling|
|many-to-many (seq2seq)|translation, summarisation (encoder–decoder)|

### Training: backpropagation through time (BPTT)
Unroll over time steps and backprop; long sequences ⇒ vanishing/exploding gradients ⇒ plain RNNs forget after ~10–20 steps. Truncated BPTT limits the unroll length.

### Variants
**Bidirectional** RNNs read both directions (good for tagging, not for real-time generation); **stacked** RNNs; **LSTM/GRU** cells for long memory. Transformers have largely replaced RNNs for text, but RNNs remain useful for streaming, small devices and some time series.""",
  code="""
import torch, torch.nn as nn
torch.manual_seed(0)
rnn = nn.RNN(input_size=3, hidden_size=5, batch_first=True)
x = torch.randn(2, 4, 3)                                  # batch 2, 4 time steps, 3 features
out, h = rnn(x); print("outputs per step:", tuple(out.shape), " final hidden:", tuple(h.shape))

Wx, Wh, b = rnn.weight_ih_l0, rnn.weight_hh_l0, rnn.bias_ih_l0 + rnn.bias_hh_l0     # manual unroll matches
ht = torch.zeros(2, 5)
for t in range(4): ht = torch.tanh(x[:, t] @ Wx.T + ht @ Wh.T + b)
print("manual recurrence equals nn.RNN:", torch.allclose(ht, h[0], atol=1e-6))

# many-to-one: are there more 1s than 0s in a 0/1 sequence? (needs memory of the whole sequence)
seqs = torch.randint(0, 2, (3000, 15, 1)).float(); labels = (seqs.sum((1, 2)) > 7).long()
class Majority(nn.Module):
    def __init__(self): super().__init__(); self.rnn = nn.RNN(1, 16, batch_first=True); self.fc = nn.Linear(16, 2)
    def forward(self, x): return self.fc(self.rnn(x)[1][0])
m = Majority(); opt = torch.optim.Adam(m.parameters(), 1e-2)
for ep in range(20):
    for i in range(0, 2500, 100):
        opt.zero_grad(); nn.functional.cross_entropy(m(seqs[i:i + 100]), labels[i:i + 100]).backward(); opt.step()
with torch.no_grad(): print("majority-vote test accuracy:", round((m(seqs[2500:]).argmax(1) == labels[2500:]).float().mean().item(), 3))
""",
  say=[("Why do plain RNNs struggle with long sequences?",
        "\"Gradients flow back through the same recurrent weight matrix at every step, so over many steps they're multiplied repeatedly and either vanish or explode. Vanishing gradients mean the network can't learn dependencies more than a few dozen steps back. LSTMs and GRUs add gates and an additive memory path to fix that, and transformers sidestep it with attention that connects any two positions directly.\"")]),

M("m-lstm-gru", "LSTM and GRU: gated recurrent networks", "Intermediate",
  "LSTMs and GRUs add gates that decide what to remember, forget and output, letting information and gradients flow across long sequences.",
  """### LSTM (long short-term memory)
Keeps a **cell state** cₜ (long-term memory conveyor belt) and hidden state hₜ.
- **Forget gate** fₜ = σ(W_f[hₜ₋₁, xₜ]) — what to erase from memory.
- **Input gate** iₜ and candidate c̃ₜ = tanh(…) — what new information to write.
- Cell update **cₜ = fₜ ⊙ cₜ₋₁ + iₜ ⊙ c̃ₜ** — additive, so gradients flow (the key fix).
- **Output gate** oₜ; hₜ = oₜ ⊙ tanh(cₜ).
4 weight matrices per layer.

### GRU (gated recurrent unit)
Merges cell and hidden state; **update gate** zₜ (how much to keep) and **reset gate** rₜ (how much past to use for the candidate). 3 weight matrices — fewer parameters, faster, often as accurate.

### Choosing
GRU for smaller data/faster training; LSTM for longer dependencies; try both. Add **bidirectional** layers for tagging, **dropout** between layers, gradient clipping. For long text, transformers usually win; LSTMs remain common in time-series forecasting, on-device speech, and as baselines.""",
  code="""
import torch, torch.nn as nn
torch.manual_seed(0)
lstm, gru = nn.LSTM(8, 32, batch_first=True), nn.GRU(8, 32, batch_first=True)
print("LSTM params:", sum(p.numel() for p in lstm.parameters()), " GRU params:", sum(p.numel() for p in gru.parameters()), "(4 vs 3 gate blocks)")

# how much does the output at the last step still depend on the FIRST input? (gradient size, no training needed)
for T in (10, 50, 100):
    row = []
    for name, cell in [("RNN", nn.RNN), ("LSTM", nn.LSTM), ("GRU", nn.GRU)]:
        torch.manual_seed(0); m = cell(1, 32, batch_first=True)
        if name != "RNN":
            with torch.no_grad(): m.bias_ih_l0[32:64].fill_(1.0)      # forget gate (LSTM) / update gate (GRU) bias = 1: "remember by default"
        x = torch.randn(16, T, 1, requires_grad=True)
        g, = torch.autograd.grad(m(x)[0][:, -1].sum(), x)
        row.append(f"{name} {g[:, 0].abs().mean():.1e}")
    print(f"sequence length {T:3d}: d(last output)/d(first input) ->", "  ".join(row))
print("plain RNN gradients vanish exponentially; gated cells keep a far larger signal, so they can learn long-range dependencies")
""",
  say=[("How does an LSTM solve the vanishing gradient problem?",
        "\"Its cell state is updated additively — the old cell times a forget gate plus new information — instead of being pushed through a squashing non-linearity and matrix multiply every step. When the forget gate is near one, information and gradients pass through almost unchanged across many steps. The gates learn when to keep, write and expose memory.\"")]),

M("m-seq2seq", "Sequence-to-sequence models and the encoder–decoder architecture", "Intermediate",
  "Seq2seq models read an input sequence with an encoder and generate an output sequence with a decoder — the architecture behind translation, summarisation and speech recognition.",
  """### Classic RNN seq2seq (2014)
Encoder RNN compresses the source into a context vector; decoder RNN generates the target token by token, feeding back its previous output. Trained with **teacher forcing** (feed the true previous token).

### The bottleneck problem → attention
One fixed-size vector can't hold a long sentence. **Attention** (Bahdanau, 2015) lets the decoder look at all encoder states at every step with learned weights — the stepping stone to transformers.

### Decoding
Greedy, **beam search** (keep the top-k partial sequences), sampling with temperature/top-k/top-p.

### Today
Transformer encoder–decoders (T5, BART, Whisper, original "Attention is all you need" translator) or decoder-only LLMs prompted to transform text. **Exposure bias** (train with teacher forcing, generate from own outputs) is a known issue.""",
  code="""
import torch, torch.nn as nn, random
torch.manual_seed(0); random.seed(0)
V, SOS = 12, 0                                            # task: reverse a sequence of digits 2..11
def batch(n, L=6):
    src = torch.randint(2, V, (n, L)); return src, src.flip(1)
class Seq2Seq(nn.Module):
    def __init__(self, h=64):
        super().__init__(); self.emb = nn.Embedding(V, 32); self.enc = nn.GRU(32, h, batch_first=True); self.dec = nn.GRU(32, h, batch_first=True); self.out = nn.Linear(h, V)
    def forward(self, src, tgt):                          # teacher forcing
        _, hstate = self.enc(self.emb(src))
        dec_in = torch.cat([torch.full((len(tgt), 1), SOS), tgt[:, :-1]], 1)
        return self.out(self.dec(self.emb(dec_in), hstate)[0])
    @torch.no_grad()
    def greedy(self, src, L=6):
        _, hstate = self.enc(self.emb(src)); tok = torch.full((len(src), 1), SOS); outs = []
        for _ in range(L):
            o, hstate = self.dec(self.emb(tok), hstate); tok = self.out(o).argmax(-1); outs.append(tok)
        return torch.cat(outs, 1)
m = Seq2Seq(); opt = torch.optim.Adam(m.parameters(), 3e-3)
for step in range(600):
    src, tgt = batch(64); opt.zero_grad(); loss = nn.functional.cross_entropy(m(src, tgt).reshape(-1, V), tgt.reshape(-1)); loss.backward(); opt.step()
src, tgt = batch(200); pred = m.greedy(src)
print("example:", src[0].tolist(), "->", pred[0].tolist())
print("exact-match accuracy on reversing:", round((pred == tgt).all(1).float().mean().item(), 3))
""",
  say=[("What problem did attention solve in seq2seq models?",
        "\"The original encoder–decoder squeezed the whole input into one fixed-size vector, which lost information for long sentences. Attention lets the decoder, at each output step, compute a weighted combination of all encoder hidden states, focusing on the relevant source words. It improved translation of long sentences dramatically and led directly to the transformer, which uses attention everywhere.\"")]),

M("m-time-series", "Time series analysis and forecasting: decomposition, stationarity, ARIMA, features", "Intermediate",
  "Time series data is ordered in time, so the past predicts the future. You must respect order when validating and handle trend, seasonality and autocorrelation.",
  """### Components
**Trend** (long-term direction), **seasonality** (fixed-period cycles: daily, weekly, yearly), **cycles** (irregular longer waves), **noise**. Decompose additively (y = T + S + R) or multiplicatively.

### Stationarity
Constant mean/variance/autocorrelation over time. Test with **ADF** (augmented Dickey–Fuller). Make stationary by **differencing**, log transform, removing seasonality.

### Classical models
- **Naive / seasonal naive** baselines (always compare!).
- **Moving average, exponential smoothing, Holt–Winters** (level + trend + season).
- **ARIMA(p, d, q)**: autoregression on p lags + d differences + q lagged errors; **SARIMA** adds seasonal terms; **SARIMAX** adds external regressors. Choose p and q from ACF/PACF plots or AIC.
- **Prophet** (trend + seasonality + holidays).

### ML approach
Turn into supervised learning with **lag features**, rolling means, calendar features, holidays, promotions → gradient boosting (often wins competitions like M5). Multi-step forecasting: recursive vs direct strategies.

### Validation
**Walk-forward / rolling-origin** splits only — never shuffle. Metrics: MAE, RMSE, MAPE/sMAPE/WAPE, MASE (vs naive).""",
  code="""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import GradientBoostingRegressor

rng = np.random.default_rng(0); idx = pd.date_range("2024-01-01", periods=400, freq="D")
demand = pd.Series(200 + 0.3 * np.arange(400) + 25 * np.sin(2 * np.pi * np.arange(400) / 7) + rng.normal(0, 8, 400), idx)
dec = seasonal_decompose(demand, period=7); print("weekly seasonal pattern:", dec.seasonal[:7].round(1).tolist())
print("ADF p-value raw:", round(adfuller(demand)[1], 3), " after differencing:", round(adfuller(demand.diff().dropna())[1], 4))

train, test = demand[:-28], demand[-28:]
naive = np.repeat(train[-7:].values[None], 4, 0).ravel()                               # seasonal naive baseline
sar = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 0, 1, 7)).fit(disp=False).forecast(28)
df = pd.DataFrame({"y": demand}); df["dow"] = df.index.dayofweek
for lag in (7, 14, 28): df[f"lag{lag}"] = df["y"].shift(lag)
df["roll7"] = df["y"].shift(7).rolling(7).mean(); df["t"] = np.arange(len(df)); df = df.dropna()
tr, te = df[df.index < test.index[0]], df[df.index >= test.index[0]]
gbr = GradientBoostingRegressor(random_state=0).fit(tr.drop(columns="y"), tr["y"])
for name, pred in [("seasonal naive", naive), ("SARIMA", sar.values), ("GBM with lag features", gbr.predict(te.drop(columns="y")))]:
    print(f"{name:22s} MAE = {np.abs(test.values - pred).mean():.2f}")
""",
  say=[("How would you validate a forecasting model?",
        "\"Never with random splits — that leaks the future. I'd use walk-forward validation: train on data up to time t, forecast the next horizon, roll forward and repeat, averaging errors across origins. I'd compare against a seasonal naive baseline using MASE or WAPE, and make sure every feature, like rolling means, only uses information available at forecast time.\"")]),

M("m-ts-dl", "Deep learning for time series: LSTM, 1-D CNN, temporal transformers", "Advanced",
  "Neural networks forecast and classify time series by learning from sliding windows; they shine with many related series, multivariate sensors and long contexts.",
  """### Data preparation
Scale each series (fit on training period), create windows: input = last L steps (+ covariates), target = next h steps. Shape (batch, L, features).

### Architectures
- **LSTM/GRU** encoders, seq2seq for multi-step.
- **1-D CNN / TCN** (temporal convolutional network, dilated causal convolutions) — fast, long receptive fields.
- **Transformers**: Temporal Fusion Transformer (interpretable, covariates), Informer, PatchTST; **N-BEATS / N-HiTS** (pure MLP stacks).
- **Foundation models** pretrained on many series: TimesFM, Chronos, Moirai — zero-shot forecasting.
- **Probabilistic** outputs: DeepAR (predicts a distribution), quantile losses for intervals.

### Tips
Global models trained across many series beat one model per series; always compare with seasonal naive and gradient boosting; deep models need lots of data.""",
  code="""
import numpy as np, torch, torch.nn as nn
torch.manual_seed(0); rng = np.random.default_rng(0)
t = np.arange(1200); series = np.sin(2 * np.pi * t / 50) + 0.5 * np.sin(2 * np.pi * t / 13) + 0.1 * rng.normal(size=t.size)
L, H = 60, 10
X = np.stack([series[i:i + L] for i in range(len(series) - L - H)]); Y = np.stack([series[i + L:i + L + H] for i in range(len(series) - L - H)])
split = 900; Xtr, Ytr, Xte, Yte = [torch.tensor(a, dtype=torch.float32) for a in (X[:split], Y[:split], X[split:], Y[split:])]

class LSTMForecaster(nn.Module):
    def __init__(self): super().__init__(); self.lstm = nn.LSTM(1, 64, batch_first=True); self.head = nn.Linear(64, H)
    def forward(self, x): return self.head(self.lstm(x[..., None])[0][:, -1])
class TCN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(*[m for d in (1, 2, 4, 8) for m in (nn.Conv1d(1 if d == 1 else 32, 32, 3, dilation=d, padding=2 * d), nn.ReLU())])
        self.head = nn.Linear(32, H)
    def forward(self, x): return self.head(self.net(x[:, None])[..., L - 1])
for name, model in [("LSTM", LSTMForecaster()), ("dilated 1-D CNN", TCN())]:
    opt = torch.optim.Adam(model.parameters(), 3e-3)
    for ep in range(60):
        perm = torch.randperm(split)
        for i in range(0, split, 64):
            b = perm[i:i + 64]; opt.zero_grad(); nn.functional.mse_loss(model(Xtr[b]), Ytr[b]).backward(); opt.step()
    with torch.no_grad(): mae = (model(Xte) - Yte).abs().mean().item()
    print(f"{name:16s} 10-step forecast MAE {mae:.3f}")
print(f"{'repeat last value':16s} 10-step forecast MAE {np.abs(Y[split:] - X[split:, -1:]).mean():.3f}")
""",
  say=[("Would you use an LSTM or gradient boosting for retail demand forecasting?",
        "\"I'd start with gradient boosting on lag, rolling, calendar, price and promotion features — it's strong, fast and was the winning approach in the M5 competition — benchmarked against seasonal naive. With thousands of related series and lots of history, a global deep model like an LSTM, N-HiTS or Temporal Fusion Transformer may add accuracy, especially for probabilistic forecasts. I'd let walk-forward validation decide.\"")]),
]
