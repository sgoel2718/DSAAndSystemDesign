"""Beginner lessons: Neural networks & deep learning."""
from lesson_util import L

L("m-dl-intro",
  "Deep learning uses neural networks with many layers that learn useful features directly from raw data such as pixels, sound and text.",
  """Deep learning powers face unlock, voice assistants, translation and chatbots. Knowing when it's the right tool (and when a simpler model is better) is a standard interview question.""",
  """In classical ML a person designs the features ("number of links in the email"). In deep learning the network **learns the features itself**, layer by layer:

- Early layers learn simple patterns (edges in an image, sounds in audio).
- Middle layers combine them into parts (eyes, wheels, syllables).
- Late layers combine parts into concepts (a face, a car, a word).

**Why now?** Three things arrived together around 2012: huge datasets, fast GPUs, and better training tricks (ReLU, dropout, good initialisation).

**When to use it**: lots of data, raw unstructured inputs (images, audio, text), and enough compute. **When not**: small tabular data (gradient boosting usually wins), or when you need a simple explanation.""",
  [("Layers of features",
    """A cat photo is 224 × 224 × 3 = 150,528 numbers. Layer 1 finds edges; layer 3 finds fur textures and eye shapes; the last layer outputs P(cat) = 0.97. No one told it what an ear looks like."""),
   ("The data rule of thumb",
    """With 500 rows of customer data, gradient boosting will likely beat a neural network. With 1 million photos, a neural network wins by a wide margin.""")],
  ("Predicting churn from a 2,000-row spreadsheet: deep learning or gradient boosting first?",
   "Gradient boosting: small, tabular data; it's usually more accurate, faster and easier to explain."),
  [("Neural network", "a model made of layers of simple connected units"),
   ("Layer", "one stage of computation; each transforms its input"),
   ("GPU", "a processor that does many multiplications in parallel, which speeds up training"),
   ("Representation learning", "the model learning its own features")],
  """A small neural network in scikit-learn learning to read handwritten digits from raw pixels.""",
  r'''from sklearn.datasets import load_digits
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)               # raw 8x8 pixel values, no hand-made features
Xtr, Xte, ytr, yte = train_test_split(X / 16, y, random_state=0)   # scale pixels to 0..1
net = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=0)  # two hidden layers
net.fit(Xtr, ytr)
print("test accuracy:", round(net.score(Xte, yte), 3))''',
  [("What does deep learning do that classical ML usually doesn't?", "It learns features from raw data instead of relying on hand-designed ones."),
   ("Name the three things that made deep learning take off.", "Big datasets, GPUs, and better training techniques.")])

L("m-nn-formulation",
  "To set up a neural network you choose the input shape, the output layer with its activation, and the loss, all decided by the task.",
  """Most neural-network bugs come from mismatching these three pieces (for example softmax output with a regression target). Once you know the standard recipes, setting up any task is quick.""",
  """Decide three things from the task:

| Task | Output layer | Output activation | Loss |
| --- | --- | --- | --- |
| Predict a number (price) | 1 unit | none (linear) | mean squared error |
| Yes / no (spam) | 1 unit | sigmoid | binary cross-entropy |
| One of K classes (digit) | K units | softmax | categorical cross-entropy |
| Several tags at once | K units | sigmoid each | binary cross-entropy per tag |

The **input layer** matches one example's shape: 20 numbers for a table row, (3, 224, 224) for a colour image. The **hidden layers** in between use ReLU-type activations.""",
  [("Pick the pieces",
    """Predicting which of 5 delivery-time buckets an order falls into: output = 5 units, softmax, categorical cross-entropy."""),
   ("Count the weights",
    """Input 20 features → hidden 16 → output 1. Weights: 20 × 16 + 16 biases = 336, then 16 × 1 + 1 = 17. Total **353 parameters**.""")],
  ("Predicting house price: which output activation and loss?",
   "One output unit, no (linear) activation, mean squared error (or MAE/Huber)."),
  [("Input shape", "the size of one example the network receives"),
   ("Output layer", "the last layer, sized for the task"),
   ("Parameters", "all weights and biases the network learns")],
  """The same small network body with three different heads, built in PyTorch, and their parameter counts.""",
  r'''import torch, torch.nn as nn

body = lambda: [nn.Linear(20, 16), nn.ReLU()]                         # shared hidden layer
regression = nn.Sequential(*body(), nn.Linear(16, 1))                 # number: no activation, MSE loss
binary     = nn.Sequential(*body(), nn.Linear(16, 1), nn.Sigmoid())   # yes/no: sigmoid, BCE loss
multiclass = nn.Sequential(*body(), nn.Linear(16, 5))                 # 5 classes: softmax inside CrossEntropyLoss

x = torch.randn(4, 20)                                                # a batch of 4 examples
for name, net in [("regression", regression), ("binary", binary), ("multiclass", multiclass)]:
    n = sum(p.numel() for p in net.parameters())
    print(f"{name:10s} output shape {tuple(net(x).shape)}  parameters {n}")''',
  [("What output activation suits a 10-class problem?", "Softmax over 10 units."),
   ("Why doesn't PyTorch's multiclass head end with softmax?", "nn.CrossEntropyLoss applies log-softmax internally, so the network outputs raw scores (logits).")])

L("m-perceptron",
  "An artificial neuron multiplies its inputs by weights, adds a bias and applies an activation; the perceptron learns those weights by nudging them after each mistake.",
  """Every neural network is built from this one unit. Understanding a single neuron (and why one neuron can't solve XOR) explains why we need layers.""",
  """A neuron computes:

1. **Weighted sum**: z = w₁x₁ + w₂x₂ + … + b.
2. **Activation**: for the original perceptron, output 1 if z ≥ 0, else 0.

**Perceptron learning rule**: for each example, if the prediction is wrong, move the weights toward the right answer:

w ← w + learning_rate × (truth − prediction) × x, and b similarly.

It is guaranteed to find a solution if the classes are **linearly separable** (AND, OR), and never if they aren't (XOR).""",
  [("A neuron computing AND",
    """Weights w₁ = 1, w₂ = 1, bias b = −1.5. Inputs (1, 1): z = 0.5 → 1. Inputs (1, 0): z = −0.5 → 0. (0, 1) → 0, (0, 0) → 0. That's AND."""),
   ("One learning step",
    """Current w = (0, 0), b = 0, learning rate 1. Example (1, 1) with truth 1; z = 0 → prediction 1, correct, no change. Example (1, 0), truth 0; prediction 1 (z = 0), wrong: w ← (0, 0) + (0 − 1) × (1, 0) = (−1, 0), b ← −1.""")],
  ("With w = (2, 2) and b = −1, what does the neuron output for (0, 1)? Which logic function is it?",
   "z = 2 − 1 = 1 ≥ 0 → 1. With (0, 0): z = −1 → 0. It computes OR."),
  [("Weight", "how strongly an input influences the neuron"),
   ("Bias", "a constant that shifts when the neuron fires"),
   ("Activation", "the function applied to the weighted sum"),
   ("Linearly separable", "classes a single straight line can split")],
  """The perceptron rule in a few lines of NumPy: it learns AND and OR, but not XOR.""",
  r'''import numpy as np
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])

def perceptron(y, epochs=20, lr=1):
    w, b = np.zeros(2), 0.0
    for _ in range(epochs):
        for xi, t in zip(X, y):
            pred = int(w @ xi + b >= 0)          # weighted sum, then step activation
            w += lr * (t - pred) * xi             # change only when wrong
            b += lr * (t - pred)
    return [int(w @ xi + b >= 0) for xi in X]

for name, y in [("AND", [0, 0, 0, 1]), ("OR", [0, 1, 1, 1]), ("XOR", [0, 1, 1, 0])]:
    print(name, "target", y, "learned", perceptron(np.array(y)))''',
  [("When does the perceptron rule change the weights?", "Only when the prediction is wrong."),
   ("Why can't one perceptron learn XOR?", "XOR isn't linearly separable, and one neuron can only draw a straight line.")])

L("m-mlp",
  "A multilayer perceptron stacks layers of neurons with non-linear activations, so it can learn curved boundaries a single neuron can't.",
  """The MLP is the basic deep network; CNNs, RNNs and transformers all contain MLP blocks. Seeing how two layers solve XOR shows what "hidden layers" are for.""",
  """- **Input layer** → one or more **hidden layers** → **output layer**.
- Each hidden neuron computes a weighted sum of all neurons in the previous layer, then a **non-linear activation** (ReLU).
- Each layer transforms the data into a new representation; by the last hidden layer, the problem has become (nearly) linearly separable, and the output layer finishes the job.

Without non-linear activations, stacking layers is pointless: a linear function of a linear function is still linear.

With enough hidden neurons, an MLP can approximate almost any function (the **universal approximation theorem**); in practice depth helps it do so with fewer neurons.""",
  [("XOR with two hidden neurons",
    """Hidden h₁ = OR(x₁, x₂), hidden h₂ = AND(x₁, x₂). Output = h₁ AND NOT h₂. For (1, 1): h₁ = 1, h₂ = 1 → output 0. For (1, 0): h₁ = 1, h₂ = 0 → 1. That's XOR."""),
   ("Why non-linearity matters",
    """Two linear layers: y = 3(2x + 1) + 4 = 6x + 7, still one straight line. Put ReLU between them and the output can bend.""")],
  ("A network has layers 4 → 8 → 3. How many weights (not counting biases) are there?",
   "4 × 8 + 8 × 3 = 32 + 24 = 56."),
  [("Hidden layer", "a layer between input and output"),
   ("Fully connected / dense layer", "every neuron connects to every neuron of the previous layer"),
   ("Universal approximation", "a wide enough network can approximate any continuous function")],
  """An MLP in PyTorch learning XOR, the problem a single neuron couldn't solve.""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)
X = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]]); y = torch.tensor([[0.], [1.], [1.], [0.]])

net = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 1))     # one hidden layer of 8 neurons
opt = torch.optim.Adam(net.parameters(), lr=0.05)
loss_fn = nn.BCEWithLogitsLoss()

for step in range(1000):
    opt.zero_grad()
    loss = loss_fn(net(X), y)       # how wrong are we?
    loss.backward()                 # compute gradients
    opt.step()                      # update weights
print("predictions:", (torch.sigmoid(net(X)) > 0.5).int().ravel().tolist())   # [0, 1, 1, 0]''',
  [("What do hidden layers do?", "Transform the input into new representations where the problem becomes easier, eventually linearly separable."),
   ("What happens if you remove all activation functions?", "The whole network collapses into one linear function.")])

L("m-activations",
  "Activation functions add the bends that let networks learn non-linear patterns; ReLU is the default inside, sigmoid and softmax turn outputs into probabilities.",
  """The wrong activation can stop a network from learning at all (vanishing gradients) or produce outputs of the wrong kind. It's a small choice with big consequences and a common interview question.""",
  """| Function | Formula | Output range | Typical use |
| --- | --- | --- | --- |
| Sigmoid | 1 / (1 + e⁻ᶻ) | 0 to 1 | yes/no output |
| Tanh | (eᶻ − e⁻ᶻ)/(eᶻ + e⁻ᶻ) | −1 to 1 | older RNNs |
| ReLU | max(0, z) | 0 to ∞ | default hidden layers |
| Leaky ReLU | z if z > 0 else 0.01z | −∞ to ∞ | avoids "dead" ReLUs |
| GELU | smooth ReLU-like curve | ≈ −0.17 to ∞ | transformers |
| Softmax | eᶻⁱ / Σ eᶻʲ | 0 to 1, sums to 1 | multiclass output |

Sigmoid and tanh **saturate**: for large |z| their slope is almost 0, so gradients vanish in deep networks. ReLU's slope is exactly 1 for positive inputs, which keeps gradients alive.""",
  [("Evaluate them at z = −2, 0, 3",
    """Sigmoid: 0.12, 0.5, 0.95. Tanh: −0.96, 0, 0.995. ReLU: 0, 0, 3. Leaky ReLU: −0.02, 0, 3."""),
   ("Softmax",
    """Scores (2, 1, 0): e² = 7.39, e¹ = 2.72, e⁰ = 1, total 11.11 → **0.67, 0.24, 0.09**.""")],
  ("What is the slope (gradient) of ReLU for z = −5 and for z = 5?",
   "0 for z = −5, and 1 for z = 5."),
  [("Non-linearity", "a function that isn't a straight line"),
   ("Saturation", "flat regions where the gradient is nearly zero"),
   ("Dead ReLU", "a neuron stuck outputting 0 for every input")],
  """Every activation from the table evaluated on the same inputs with PyTorch.""",
  r'''import torch
z = torch.tensor([-2.0, 0.0, 3.0])
print("sigmoid   ", torch.sigmoid(z).numpy().round(3))
print("tanh      ", torch.tanh(z).numpy().round(3))
print("relu      ", torch.relu(z).numpy())
print("leaky relu", torch.nn.functional.leaky_relu(z, 0.01).numpy())
print("gelu      ", torch.nn.functional.gelu(z).numpy().round(3))
print("softmax   ", torch.softmax(torch.tensor([2.0, 1.0, 0.0]), dim=0).numpy().round(2))''',
  [("Why is ReLU preferred over sigmoid in hidden layers?", "It doesn't saturate for positive inputs, so gradients don't vanish, and it's cheap to compute."),
   ("Which activation would you put on a 10-class output?", "Softmax.")])

L("m-loss-functions",
  "The loss turns 'how wrong is the model' into one number to minimise; choosing it says which mistakes matter most.",
  """The network will optimise exactly what the loss measures and nothing else. A wrong loss (MSE for classification, or a loss that ignores rare classes) gives a model that is "good" at the wrong thing.""",
  """- **MSE** (mean squared error): regression; big errors count a lot.
- **MAE**: regression; robust to outliers.
- **Huber**: MSE for small errors, MAE for big ones: a compromise.
- **Binary cross-entropy**: yes/no with probabilities: −[y log p + (1 − y) log(1 − p)].
- **Categorical cross-entropy**: multiclass: −log(probability given to the true class).
- **Hinge**: max(0, 1 − y·score), the SVM loss.
- **Focal loss**: cross-entropy that down-weights easy examples, for heavy imbalance (object detection).
- **Contrastive / triplet**: pull similar pairs' embeddings together, push different ones apart.""",
  [("Cross-entropy by hand",
    """True class cat. The model gives cat 0.7 → loss −log(0.7) = **0.36**. Gives cat 0.1 → **2.30**. Gives cat 0.99 → **0.01**."""),
   ("MSE vs MAE with an outlier",
    """Errors 1, 1, 10. MSE = (1 + 1 + 100)/3 = **34**; MAE = 12/3 = **4**. MSE is dominated by the single outlier.""")],
  ("Your regression data has a few wildly wrong labels. Which loss is safer than MSE?",
   "MAE or Huber, which grow linearly (not quadratically) for large errors."),
  [("Loss", "a number that is small when predictions are good"),
   ("Cross-entropy", "the loss for predicted probabilities"),
   ("Robust loss", "a loss not dominated by outliers")],
  """The two hand calculations reproduced with PyTorch's built-in losses.""",
  r'''import torch, torch.nn as nn

logits = torch.log(torch.tensor([[0.7, 0.2, 0.1]]))          # model gave cat=0.7
print("cross-entropy:", nn.CrossEntropyLoss()(logits, torch.tensor([0])).item())   # 0.357

pred, true = torch.tensor([1., 1., 10.]), torch.zeros(3)
print("MSE  :", nn.MSELoss()(pred, true).item())             # 34.0
print("MAE  :", nn.L1Loss()(pred, true).item())              # 4.0
print("Huber:", nn.HuberLoss(delta=1.0)(pred, true).item())  # between the two''',
  [("Which loss would you use for a 3-class classifier?", "Categorical cross-entropy."),
   ("What does focal loss change compared with cross-entropy?", "It reduces the weight of easy, well-classified examples so training focuses on hard ones.")])

L("m-backprop",
  "Backpropagation computes how much each weight contributed to the error using the chain rule, going backwards; gradient descent then nudges every weight to reduce it.",
  """This is how every neural network learns. Interviewers often ask you to explain it simply or compute one tiny step by hand.""",
  """1. **Forward pass**: feed the input through the network and compute the loss.
2. **Backward pass (backpropagation)**: for each weight, compute the **gradient**: how much the loss would change if that weight increased a little. The **chain rule** lets you compute this layer by layer, from the output back to the input, reusing results.
3. **Gradient descent update**: w ← w − learning_rate × gradient. Moving against the gradient lowers the loss.
4. Repeat over many batches of data.

The learning rate matters: too small = very slow; too large = the loss jumps around or explodes.""",
  [("One weight by hand",
    """Model ŷ = w × x, with x = 2, truth y = 10, start w = 3. Forward: ŷ = 6, loss = (6 − 10)² = 16. Gradient: d loss / dw = 2(ŷ − y) × x = 2 × (−4) × 2 = **−16**. Update with learning rate 0.05: w = 3 − 0.05 × (−16) = **3.8**. New ŷ = 7.6, loss = 5.76: better."""),
   ("The chain rule in one line",
    """If loss depends on ŷ and ŷ depends on w, then d loss/dw = (d loss/dŷ) × (dŷ/dw) = 2(ŷ − y) × x. Deep networks just chain more of these factors.""")],
  ("Continue the example: from w = 3.8, compute the next gradient and the new w.",
   "ŷ = 7.6, gradient = 2 × (7.6 − 10) × 2 = −9.6, w = 3.8 + 0.05 × 9.6 = 4.28 (heading to the true value 5)."),
  [("Gradient", "the direction and amount the loss changes when a weight changes"),
   ("Chain rule", "multiplying derivatives through a chain of functions"),
   ("Learning rate", "the step size of each update"),
   ("Epoch", "one full pass over the training data")],
  """The hand example, then PyTorch's autograd computing the same gradient automatically.""",
  r'''import torch
x, y = 2.0, 10.0
w = 3.0
for step in range(5):                      # by hand
    yhat = w * x
    grad = 2 * (yhat - y) * x               # chain rule
    w -= 0.05 * grad                        # gradient descent
    print(f"step {step}: w={w:.3f} loss={(w * x - y) ** 2:.3f}")

wt = torch.tensor(3.0, requires_grad=True) # autograd does the backward pass for us
loss = (wt * x - y) ** 2
loss.backward()
print("autograd gradient at w=3:", wt.grad.item())   # -16.0, same as by hand''',
  [("What does the backward pass compute?", "The gradient of the loss with respect to every weight."),
   ("What happens if the learning rate is far too large?", "Updates overshoot; the loss bounces around or blows up.")])

L("m-optimizers",
  "Optimisers decide how gradients become weight updates: momentum smooths the path, Adam gives each weight its own step size, schedules change the step over time.",
  """Plain gradient descent is slow and gets stuck on difficult surfaces. Choosing the optimiser and learning-rate schedule often decides whether a deep network trains in an hour or not at all.""",
  """- **SGD** (stochastic gradient descent): update on small random batches: w ← w − lr × gradient. Noisy but cheap.
- **Momentum**: keep a running average of past gradients ("velocity") and move along it. It speeds up in consistent directions and damps zig-zags.
- **RMSProp**: divide each weight's step by the recent size of its gradients, so steep directions take smaller steps.
- **Adam**: momentum + RMSProp together; the most common default (lr ≈ 0.001).
- **AdamW**: Adam with weight decay applied correctly; standard for transformers.

**Schedules**: start with a short **warm-up**, then reduce the learning rate over training (step decay, cosine decay). **Batch size**: larger batches give smoother gradients but need more memory.""",
  [("Momentum by hand",
    """β = 0.9, gradients 1, 1, 1. Velocity: v₁ = 1, v₂ = 0.9 × 1 + 1 = 1.9, v₃ = 0.9 × 1.9 + 1 = 2.71. Steps grow while the direction stays consistent."""),
   ("Zig-zag damping",
    """Gradients alternate +1, −1, +1. Velocity: 1, 0.9 × 1 − 1 = −0.1, 0.9 × (−0.1) + 1 = 0.91 … the back-and-forth mostly cancels.""")],
  ("Which optimiser would you try first for a new deep network, and with what learning rate?",
   "Adam (or AdamW) with a learning rate around 1e-3, then tune."),
  [("Batch", "a small group of examples used for one update"),
   ("Momentum", "carrying part of the previous update forward"),
   ("Adaptive learning rate", "a separate step size per weight"),
   ("Learning-rate schedule", "changing the learning rate during training")],
  """Minimise the same badly-shaped function f(x, y) = x² + 25y² with SGD, momentum and Adam, and compare where each ends after 100 steps.""",
  r'''import torch
def run(make_opt, steps=100):
    p = torch.tensor([3.0, 1.0], requires_grad=True)
    opt = make_opt([p])
    for _ in range(steps):
        opt.zero_grad()
        loss = p[0] ** 2 + 25 * p[1] ** 2       # a long narrow valley
        loss.backward(); opt.step()
    return round(loss.item(), 6)

print("SGD     ", run(lambda ps: torch.optim.SGD(ps, lr=0.01)))
print("momentum", run(lambda ps: torch.optim.SGD(ps, lr=0.01, momentum=0.9)))
print("Adam    ", run(lambda ps: torch.optim.Adam(ps, lr=0.1)))''',
  [("What does Adam combine?", "Momentum and per-weight adaptive step sizes (RMSProp)."),
   ("Why warm up the learning rate?", "Early gradients are unreliable; small steps at the start prevent the model from being thrown off.")])

L("m-init-norm",
  "Good starting weights and normalisation layers keep the numbers flowing through a deep network at a healthy size, so it trains fast and stably.",
  """If signals grow or shrink at every layer, after 50 layers they are huge or zero and the network stops learning. Initialisation and normalisation are why very deep networks are trainable.""",
  """**Initialisation**:
- All weights zero → every neuron learns the same thing. Never do that.
- Random weights that are too big or too small → activations explode or vanish with depth.
- **Xavier/Glorot** (for tanh/sigmoid) and **He/Kaiming** (for ReLU) pick a random scale based on the number of inputs (variance ≈ 2/n_in for He), keeping the spread of activations roughly constant from layer to layer.

**Normalisation layers**:
- **Batch normalisation**: for each feature, subtract the batch mean and divide by the batch standard deviation, then apply a learned scale and shift. Speeds up training; common in CNNs. Behaves differently at training and inference time.
- **Layer normalisation**: normalises across the features of each single example; doesn't depend on the batch. Standard in transformers and RNNs.""",
  [("Normalise a batch by hand",
    """One feature's values in a batch: 2, 4, 6, 8. Mean 5, standard deviation ≈ 2.24. Normalised: **−1.34, −0.45, 0.45, 1.34**. Then y = γ × x̂ + β with learned γ and β."""),
   ("Why scale matters",
    """If each layer multiplies the signal's size by 1.5, after 20 layers it's 1.5²⁰ ≈ **3,300** times bigger; at 0.7 per layer it shrinks to **0.0008**.""")],
  ("Why shouldn't you initialise all weights to zero?",
   "All neurons in a layer would compute the same output and get the same gradient, so they'd stay identical and the layer would act like one neuron."),
  [("Xavier / He initialisation", "random starting weights scaled to the layer size"),
   ("Batch normalisation", "normalising each feature using batch statistics"),
   ("Layer normalisation", "normalising each example across its features")],
  """Push data through 30 ReLU layers with too-small, too-large and He initial weights and watch the signal size.""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)
x = torch.randn(256, 512)

for name, init in [("too small", lambda w: nn.init.normal_(w, std=0.01)),
                   ("too large", lambda w: nn.init.normal_(w, std=0.2)),
                   ("He      ", lambda w: nn.init.kaiming_normal_(w, nonlinearity="relu"))]:
    h = x
    for _ in range(30):
        layer = nn.Linear(512, 512, bias=False); init(layer.weight)
        h = torch.relu(layer(h))
    print(name, "signal std after 30 layers:", f"{h.std().item():.3g}")

print("batch-norm output mean/std:", nn.BatchNorm1d(512)(x * 50 + 7).mean().item().__round__(3), "/ ~1")''',
  [("Which initialisation suits ReLU networks?", "He (Kaiming) initialisation."),
   ("Why do transformers use layer norm rather than batch norm?", "Layer norm works per example, independent of batch size and sequence padding.")])

L("m-vanishing",
  "In deep or recurrent networks gradients are products of many numbers, so they can shrink to nothing or blow up; ReLU, good initialisation, normalisation, skip connections and clipping fix it.",
  """Vanishing gradients are why early deep networks wouldn't train, and why ResNets and LSTMs were invented. Exploding gradients cause sudden NaN losses. Both come up often in interviews.""",
  """During backpropagation, the gradient for an early layer is a **product** of one factor per later layer.

- If most factors are **below 1** (sigmoid's slope is at most 0.25), the product **vanishes**: early layers barely learn.
- If most are **above 1**, it **explodes**: updates become huge and the loss becomes NaN.

Fixes:
- **ReLU** activations (slope 1 for positive inputs).
- **Good initialisation** (He/Xavier) and **normalisation** layers.
- **Residual (skip) connections**: output = layer(x) + x. The "+ x" gives the gradient a direct path backwards. This made 100+ layer ResNets possible.
- **Gated RNNs** (LSTM, GRU) for long sequences.
- **Gradient clipping**: if the gradient's size exceeds a limit (e.g. 1.0), scale it down. The standard fix for exploding gradients.""",
  [("The product by hand",
    """20 layers with sigmoid, each contributing at most 0.25: 0.25²⁰ ≈ **9 × 10⁻¹³**. The first layer's gradient is essentially zero. With factors of 1.2: 1.2²⁰ ≈ **38**, and growing."""),
   ("Clipping by hand",
    """Gradient (6, 8) has size 10. Clip to size 1: multiply by 1/10 → **(0.6, 0.8)**. Same direction, safe size.""")],
  ("A model's loss suddenly becomes NaN after a few steps. What would you try first?",
   "Lower the learning rate and add gradient clipping; also check for bad inputs (inf/NaN) and normalisation."),
  [("Vanishing gradient", "gradients so small that early layers stop learning"),
   ("Exploding gradient", "gradients so large that training diverges"),
   ("Residual / skip connection", "adding a layer's input to its output"),
   ("Gradient clipping", "capping the size of the gradient")],
  """Compare the first layer's gradient in a deep sigmoid network, a deep ReLU network with skip connections, and show clipping.""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)

def first_layer_grad(act, residual, depth=30):
    layers = nn.ModuleList([nn.Linear(64, 64) for _ in range(depth)])
    h = torch.randn(32, 64)
    for l in layers:
        h = act(l(h)) + (h if residual else 0)      # optional skip connection
    h.sum().backward()
    return layers[0].weight.grad.abs().mean().item()

print("sigmoid, no skips:", f"{first_layer_grad(torch.sigmoid, False):.2e}")
print("relu + skips     :", f"{first_layer_grad(torch.relu, True):.2e}")

p = torch.nn.Parameter(torch.zeros(2)); p.grad = torch.tensor([6.0, 8.0])
torch.nn.utils.clip_grad_norm_([p], max_norm=1.0)
print("clipped gradient:", [round(g, 3) for g in p.grad.tolist()])   # [0.6, 0.8]''',
  [("Why do skip connections help gradients flow?", "The '+ x' path passes the gradient straight back without being multiplied by the layer's weights."),
   ("What does gradient clipping preserve and what does it change?", "It keeps the gradient's direction and limits its size.")])

L("m-dl-regularization",
  "Deep networks memorise easily; dropout, weight decay, early stopping and data augmentation make them generalise to new data.",
  """A network with millions of weights can memorise a training set perfectly, even random labels. These techniques are what turn that memoriser into a model that works on new data.""",
  """- **Dropout**: during training, randomly switch off a share of neurons (e.g. 20–50%) at each step. The network can't rely on any single neuron, so it learns redundant, robust features. Turned off at prediction time.
- **Weight decay (L2)**: add a penalty on large weights; in AdamW it's applied directly to the weights.
- **Early stopping**: watch the validation loss and stop (keeping the best weights) when it stops improving.
- **Data augmentation**: create varied copies of training examples (flips, crops, noise); one of the strongest regularisers for images and audio.
- Also: smaller models, label smoothing, more data.""",
  [("Dropout by hand",
    """A layer outputs (2, 4, 6, 8). With dropout 0.5, one random mask might keep positions 1 and 3: (2, 0, 6, 0), then scale by 1/0.5 = 2 → **(4, 0, 12, 0)**, so the average size stays the same."""),
   ("Early stopping",
    """Validation loss by epoch: 0.90, 0.70, 0.61, 0.58, 0.59, 0.62, 0.66. Best at epoch 4. With patience 2 you'd stop at epoch 6 and restore epoch 4's weights.""")],
  ("Why is dropout turned off when making predictions?",
   "At prediction time you want the full, deterministic network; the scaling during training keeps the outputs on the same scale."),
  [("Dropout rate", "the share of neurons switched off each training step"),
   ("Weight decay", "shrinking weights a little at every step"),
   ("Patience", "how many epochs without improvement before early stopping")],
  """Dropout in training versus evaluation mode, and early stopping on a toy validation curve.""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)
drop = nn.Dropout(p=0.5)
x = torch.tensor([2.0, 4.0, 6.0, 8.0])
drop.train(); print("training mode :", drop(x).tolist())   # random zeros, survivors doubled
drop.eval();  print("evaluation    :", drop(x).tolist())   # unchanged

val_loss = [0.90, 0.70, 0.61, 0.58, 0.59, 0.62, 0.66, 0.70]
best, wait, patience = float("inf"), 0, 2
for epoch, v in enumerate(val_loss, 1):
    if v < best: best, best_epoch, wait = v, epoch, 0     # improvement: remember it
    else: wait += 1
    if wait >= patience:
        print(f"stop at epoch {epoch}, restore epoch {best_epoch} (loss {best})"); break''',
  [("What does dropout prevent the network from doing?", "Relying on any single neuron (co-adaptation), which encourages robust features."),
   ("Name the regulariser that needs no change to the model or the loss.", "Data augmentation (or early stopping).")])

L("m-pytorch",
  "PyTorch gives you tensors that run on GPUs, automatic gradients, building blocks for networks, and a training loop you write yourself.",
  """PyTorch is the most used deep-learning framework in research and industry (it runs most open LLMs). Interviewers expect you to write a basic training loop from memory.""",
  """The five pieces:

1. **Tensors**: NumPy-like arrays that can live on a GPU (`.to("cuda")`).
2. **Autograd**: set `requires_grad=True`; after `loss.backward()`, every parameter has a `.grad`.
3. **nn.Module**: define a network as a class with layers in `__init__` and the computation in `forward`.
4. **Dataset / DataLoader**: serve the data in shuffled mini-batches.
5. **The training loop**, repeated every batch:
   `optimizer.zero_grad()` → `pred = model(x)` → `loss = loss_fn(pred, y)` → `loss.backward()` → `optimizer.step()`.

Use `model.train()` while training and `model.eval()` plus `torch.no_grad()` while evaluating.""",
  [("Why zero the gradients?",
    """PyTorch **adds** new gradients to old ones. Without `zero_grad()`, each step would use the sum of all past gradients."""),
   ("Batches",
    """1,000 examples with batch size 50 → 20 updates per epoch. 10 epochs → 200 updates.""")],
  ("Put these in order: loss.backward(), optimizer.step(), optimizer.zero_grad(), loss = loss_fn(model(x), y).",
   "optimizer.zero_grad() → loss = loss_fn(model(x), y) → loss.backward() → optimizer.step()."),
  [("Tensor", "PyTorch's array type"),
   ("Autograd", "automatic computation of gradients"),
   ("nn.Module", "the base class for every network or layer"),
   ("DataLoader", "serves batches of data, optionally shuffled")],
  """A complete PyTorch workflow on the bundled digits data: Dataset, DataLoader, a Module, the training loop and evaluation.""",
  r'''import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(torch.tensor(X / 16, dtype=torch.float32), torch.tensor(y), random_state=0)
loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)
device = "cuda" if torch.cuda.is_available() else "cpu"

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 10))
    def forward(self, x):
        return self.layers(x)

model = Net().to(device)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()
for epoch in range(15):
    model.train()
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad(); loss = loss_fn(model(xb), yb); loss.backward(); opt.step()

model.eval()
with torch.no_grad():
    acc = (model(Xte.to(device)).argmax(1).cpu() == yte).float().mean()
print("test accuracy:", round(acc.item(), 3))''',
  [("What does loss.backward() do?", "Computes gradients of the loss for every parameter and stores them in .grad."),
   ("Why use torch.no_grad() during evaluation?", "It skips gradient tracking, saving memory and time.")])

L("m-keras",
  "Keras builds networks from layers, then compile (choose optimiser and loss) and fit (train) in a few lines; Keras 3 runs on TensorFlow, PyTorch or JAX.",
  """Keras is the fastest way to build a standard network, and many companies' production models are TensorFlow/Keras. Knowing both Keras and PyTorch makes you comfortable in any team.""",
  """Three steps:

1. **Define the model**:
   - **Sequential API**: a plain stack of layers.
   - **Functional API**: connect layers like a graph (several inputs or outputs, skip connections).
2. **compile**: choose the optimiser, the loss and the metrics.
3. **fit**: train for some epochs with a batch size and validation data. Keras writes the training loop for you.

**Callbacks** add behaviour during training: `EarlyStopping`, `ModelCheckpoint` (save the best model), `ReduceLROnPlateau`. Then `evaluate` and `predict`.""",
  [("Sequential vs functional",
    """Sequential: input → Dense(64) → Dense(10). Functional: an image branch and a text branch merged into one output; needs the functional API."""),
   ("Reading the fit log",
    """Epoch 5: loss 0.21, accuracy 0.94, val_loss 0.25, val_accuracy 0.92. Training and validation are close, so no strong overfitting yet.""")],
  ("Which callback stops training when the validation loss stops improving?",
   "EarlyStopping (usually with restore_best_weights=True)."),
  [("compile", "set the optimiser, loss and metrics"),
   ("fit", "train the model"),
   ("Callback", "code that runs at points during training"),
   ("Functional API", "building models as graphs of layers")],
  """The digits model in Keras with early stopping. In Colab this uses TensorFlow; it also runs with the PyTorch backend.""",
  r'''import keras
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X / 16, y, random_state=0)

model = keras.Sequential([keras.Input(shape=(64,)),
                          keras.layers.Dense(128, activation="relu"),
                          keras.layers.Dropout(0.2),
                          keras.layers.Dense(10, activation="softmax")])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
stop = keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True)
model.fit(Xtr, ytr, validation_split=0.2, epochs=50, batch_size=64, callbacks=[stop], verbose=0)
print("test accuracy:", round(model.evaluate(Xte, yte, verbose=0)[1], 3))''',
  [("What does compile set?", "The optimiser, the loss and the metrics."),
   ("When do you need the functional API?", "For non-linear graphs: several inputs/outputs, shared layers or skip connections.")])

L("m-cnn",
  "A CNN slides small learnable filters across an image to detect local patterns, reusing the same filter everywhere, then pools to shrink the map.",
  """CNNs made computers good at seeing: medical scans, self-driving cameras, quality inspection, face unlock. Their two ideas (local filters, shared weights) are why they need far fewer weights than a fully connected network.""",
  """- A **filter (kernel)** is a small grid of weights, e.g. 3 × 3. Slide it over the image; at each position multiply element-wise and sum. The result is a **feature map** that is large where the pattern appears.
- **Weight sharing**: the same filter is used at every position, so an edge detector works anywhere in the image.
- **Stride**: how many pixels the filter moves each step. **Padding**: adding a border so the output keeps its size.
- **Pooling** (e.g. 2 × 2 max pooling): keep the largest value in each small block, halving width and height.
- A typical CNN: [conv → ReLU → pool] × several, then flatten → dense layers → output.

Output size = (input − filter + 2 × padding) / stride + 1.""",
  [("One convolution step",
    """Image patch [[1, 2, 0], [0, 1, 3], [2, 1, 0]] and a vertical-edge filter [[1, 0, −1], [1, 0, −1], [1, 0, −1]]. Sum of products = (1 + 0 + 2) − (0 + 3 + 0) = **0**."""),
   ("Output size",
    """28 × 28 input, 3 × 3 filter, no padding, stride 1 → 26 × 26. Then 2 × 2 max pooling → **13 × 13**."""),
   ("Why fewer weights",
    """A 3 × 3 filter on a colour image has 3 × 3 × 3 + 1 = **28** weights, whatever the image size. A dense layer from a 224 × 224 × 3 image to 100 neurons needs about **15 million**.""")],
  ("A 32 × 32 image, 5 × 5 filter, padding 2, stride 1. What is the output size?",
   "(32 − 5 + 4)/1 + 1 = 32, so 32 × 32 (the padding keeps the size)."),
  [("Filter / kernel", "a small grid of weights slid across the image"),
   ("Feature map", "the output of one filter"),
   ("Stride / padding", "step size / border added around the input"),
   ("Pooling", "shrinking a feature map by summarising small blocks")],
  """The hand convolution, then a small CNN trained on 8 × 8 digit images in PyTorch.""",
  r'''import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits

patch = torch.tensor([[1., 2, 0], [0, 1, 3], [2, 1, 0]]).view(1, 1, 3, 3)
edge = torch.tensor([[1., 0, -1], [1, 0, -1], [1, 0, -1]]).view(1, 1, 3, 3)
print("hand example:", F.conv2d(patch, edge).item())                  # 0.0

X, y = load_digits(return_X_y=True)
X = torch.tensor(X / 16, dtype=torch.float32).view(-1, 1, 8, 8); y = torch.tensor(y)   # (N, channels, H, W)
cnn = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),        # 8x8 -> 4x4
                    nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),       # 4x4 -> 2x2
                    nn.Flatten(), nn.Linear(32 * 2 * 2, 10))
opt = torch.optim.Adam(cnn.parameters(), lr=1e-2)
for epoch in range(30):
    opt.zero_grad(); loss = F.cross_entropy(cnn(X[:1400]), y[:1400]); loss.backward(); opt.step()
print("held-out accuracy:", (cnn(X[1400:]).argmax(1) == y[1400:]).float().mean().item().__round__(3))''',
  [("What does weight sharing mean in a CNN?", "The same filter weights are used at every position of the image."),
   ("What does 2 × 2 max pooling do to a 16 × 16 feature map?", "Shrinks it to 8 × 8, keeping the largest value of each 2 × 2 block.")])

L("m-cnn-understand",
  "Inside a CNN, early layers detect edges and colours, middle layers textures and parts, deep layers whole objects; tools like Grad-CAM show where it looked.",
  """You must be able to trust and debug a vision model: maybe it recognises "wolf" by the snow in the background. Visualisation reveals this, and the receptive field explains what each layer can "see".""",
  """- **Layer hierarchy**: layer 1 filters look like edge and colour detectors; middle layers respond to textures (fur, stripes) and parts (eyes, wheels); deep layers to whole objects.
- **Receptive field**: the region of the input a neuron depends on. Each 3 × 3 conv adds 2 pixels: after 3 such layers a neuron sees 7 × 7 pixels; pooling makes it grow faster. Deep neurons see most of the image.
- **Visualisation tools**:
  - Look at the learned filters and feature maps.
  - **Saliency maps**: gradient of the class score with respect to the pixels.
  - **Grad-CAM**: weight the last conv layer's feature maps by the gradient of the class score, giving a heat map of where the model looked.""",
  [("Receptive field by hand",
    """Three 3 × 3 convs, stride 1: 1 + 2 + 2 + 2 = **7** pixels wide. Add a 2 × 2 pool and another 3 × 3 conv: 7 + (3 − 1) × 2 = **11**."""),
   ("A Grad-CAM story",
    """A husky-vs-wolf model was 90% accurate. Grad-CAM showed it looked at the background: wolves were always photographed on snow. The model was a snow detector.""")],
  ("Grad-CAM shows your X-ray model focuses on a hospital's text marker in the corner. What does that suggest?",
   "Shortcut learning or leakage: the model uses where the image came from, not the disease; fix the data (crop markers, balance sources)."),
  [("Receptive field", "the input area that affects one neuron"),
   ("Saliency map", "which pixels most change the class score"),
   ("Grad-CAM", "a heat map from the last conv layer showing where the model looked"),
   ("Shortcut learning", "the model using an easy, wrong cue")],
  """A tiny Grad-CAM: train a small CNN on digits, then compute which areas of one image drove its prediction.""",
  r'''import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
torch.manual_seed(0)
X, y = load_digits(return_X_y=True)
X = torch.tensor(X / 16, dtype=torch.float32).view(-1, 1, 8, 8); y = torch.tensor(y)

conv = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.Conv2d(16, 16, 3, padding=1), nn.ReLU())
head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(16, 10))
opt = torch.optim.Adam(list(conv.parameters()) + list(head.parameters()), lr=1e-2)
for _ in range(60):
    opt.zero_grad(); F.cross_entropy(head(conv(X)), y).backward(); opt.step()

img = X[:1]
fmap = conv(img); fmap.retain_grad()                    # last conv feature maps
score = head(fmap)[0, y[0]]; score.backward()          # gradient of the true class score
weights = fmap.grad.mean(dim=(2, 3), keepdim=True)     # importance of each feature map
cam = torch.relu((weights * fmap).sum(1))[0]           # weighted sum -> heat map
print("digit", y[0].item(), "heat map (8x8):"); print((cam / cam.max()).detach().numpy().round(1))''',
  [("What do the first convolution layers typically detect?", "Edges, simple colour blobs and gradients."),
   ("What does Grad-CAM use to weight the feature maps?", "The gradient of the class score with respect to each map, averaged over positions.")])

L("m-autoencoder",
  "An autoencoder learns to squeeze an input into a small code and rebuild it; the bottleneck forces it to keep only what matters.",
  """Autoencoders give compact features without labels, remove noise from images and signals, detect anomalies (bad reconstructions), and lead directly to VAEs and diffusion models.""",
  """- **Encoder**: compresses the input (e.g. 784 pixels) into a short **code** (e.g. 32 numbers).
- **Decoder**: reconstructs the input from the code.
- **Loss**: reconstruction error (e.g. MSE between input and output). No labels needed: the input is its own target.

Variants:
- **Undercomplete**: code smaller than the input (the usual kind).
- **Denoising**: feed a noisy input, ask for the clean one; learns robust features.
- **Sparse**: penalise how many code units are active.

Uses: compression and features, denoising, anomaly detection (normal data rebuilds well, anomalies don't).""",
  [("Sizes",
    """64-pixel digit → encoder 64 → 16 → **4** → decoder 4 → 16 → 64. Each digit is summarised by 4 numbers."""),
   ("Anomaly detection",
    """Trained only on normal heartbeats, reconstruction error is about 0.02 for normal beats and 0.30 for an irregular one. Threshold 0.1 flags it.""")],
  ("What is the training target of an autoencoder?",
   "The input itself (for a denoising autoencoder, the clean version of the input)."),
  [("Encoder / decoder", "compresses / reconstructs"),
   ("Bottleneck / code / latent", "the small middle representation"),
   ("Reconstruction error", "how different the output is from the input")],
  """An autoencoder compressing 64-pixel digits to 4 numbers, and its reconstruction error.""",
  r'''import torch, torch.nn as nn
from sklearn.datasets import load_digits
torch.manual_seed(0)
X = torch.tensor(load_digits().data / 16, dtype=torch.float32)

encoder = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 4))       # 64 -> 4
decoder = nn.Sequential(nn.Linear(4, 32), nn.ReLU(), nn.Linear(32, 64), nn.Sigmoid())
opt = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=1e-2)

for epoch in range(300):
    opt.zero_grad()
    loss = ((decoder(encoder(X)) - X) ** 2).mean()   # input is its own target
    loss.backward(); opt.step()
print("code for first digit:", encoder(X[:1]).detach().numpy().round(2))
print("mean reconstruction error:", round(loss.item(), 4))''',
  [("Why does an autoencoder need a bottleneck?", "Otherwise it could copy the input straight through without learning anything useful."),
   ("How can it detect anomalies?", "Trained on normal data, it reconstructs unusual inputs badly, so high error flags them.")])

L("m-rnn",
  "An RNN reads a sequence one step at a time and carries a hidden state, a running memory of what it has seen so far.",
  """Language, speech, sensor readings and prices are sequences where order matters. RNNs were the first networks built for this, and understanding their memory (and its limits) explains why LSTMs and transformers came next.""",
  """At each time step t the RNN takes the current input xₜ and the previous hidden state hₜ₋₁:

**hₜ = tanh(W_x · xₜ + W_h · hₜ₋₁ + b)**

- The **same weights** are used at every step, so it handles sequences of any length.
- The final hidden state (or each step's state) feeds an output layer: classify the whole sequence (sentiment) or predict at every step (next word).
- Training unrolls the sequence and backpropagates through all steps (**backpropagation through time**).

Limitation: gradients pass through many multiplications, so plain RNNs forget things from far back (vanishing gradients).""",
  [("Two steps by hand",
    """Scalar RNN with W_x = 0.5, W_h = 0.8, b = 0, h₀ = 0. Inputs 1, then 2. h₁ = tanh(0.5) = **0.46**. h₂ = tanh(0.5 × 2 + 0.8 × 0.46) = tanh(1.37) = **0.88**. h₂ carries information from both inputs."""),
   ("Shapes",
    """A batch of 32 sentences, 20 words each, 50-number word vectors: input (32, 20, 50). Hidden size 64 → outputs (32, 20, 64), final state (1, 32, 64).""")],
  ("Why can an RNN process a 10-word sentence and a 100-word sentence with the same model?",
   "It applies the same weights at every step, so the number of steps doesn't change the parameters."),
  [("Hidden state", "the RNN's memory vector, updated at every step"),
   ("Time step", "one position in the sequence"),
   ("Backpropagation through time", "backprop over the unrolled sequence")],
  """The hand calculation, then PyTorch's RNN learning to average a sequence of numbers.""",
  r'''import math, torch, torch.nn as nn
h = 0.0
for x in [1, 2]:
    h = math.tanh(0.5 * x + 0.8 * h)          # same weights at every step
    print("h =", round(h, 2))                   # 0.46, then 0.88

torch.manual_seed(0)
X = torch.rand(2000, 10, 1); y = X.mean(dim=1)  # task: output the average of 10 numbers
rnn, out = nn.RNN(1, 32, batch_first=True), nn.Linear(32, 1)
opt = torch.optim.Adam(list(rnn.parameters()) + list(out.parameters()), lr=1e-2)
for epoch in range(300):
    opt.zero_grad()
    _, h_last = rnn(X)                          # h_last: (1, batch, 32), the final memory
    loss = ((out(h_last[0]) - y) ** 2).mean()
    loss.backward(); opt.step()
print("error:", f"{loss.item():.6f}", " vs always guessing the mean:", f"{y.var().item():.6f}")''',
  [("What does the hidden state represent?", "A summary of the sequence seen so far."),
   ("Why do plain RNNs struggle with long sequences?", "Gradients vanish (or explode) through many time steps, so early information is forgotten.")])

L("m-lstm-gru",
  "LSTMs and GRUs add gates that decide what to keep, forget and output, so information and gradients survive across long sequences.",
  """Before transformers, LSTMs powered Google Translate, speech recognition and keyboard prediction, and they're still used for time series and on small devices. "How does an LSTM solve vanishing gradients?" is a classic question.""",
  """An **LSTM** keeps two states: the hidden state h and a **cell state** c (a long-term memory "conveyor belt"). At every step three **gates**, each a sigmoid giving values between 0 (block) and 1 (pass), control it:

- **Forget gate** f: how much of the old memory to keep.
- **Input gate** i: how much new information to write.
- **Output gate** o: how much of the memory to show as h.

Cell update: **cₜ = f × cₜ₋₁ + i × (new candidate)**. Because c is updated by **addition** and can pass through with f ≈ 1, gradients flow back many steps without vanishing.

A **GRU** merges these into two gates (update and reset) and one state: fewer parameters, often similar accuracy.""",
  [("The cell update by hand",
    """Old memory c = 5. Forget gate 0.9, input gate 0.1, candidate 2. New c = 0.9 × 5 + 0.1 × 2 = **4.7**: mostly kept, a little written."""),
   ("Forgetting on purpose",
    """When a sentence's subject changes, the forget gate drops near 0 and the old subject is cleared: c = 0.05 × 5 + 0.9 × 3 = **2.95**.""")],
  ("Which gate would you expect to be near 1 when the model must remember something for a long time?",
   "The forget gate (keep the old cell state)."),
  [("Cell state", "the LSTM's long-term memory"),
   ("Gate", "a sigmoid between 0 and 1 controlling information flow"),
   ("GRU", "a simpler gated RNN with update and reset gates")],
  """A long-memory test: the answer is the first number of a 100-step sequence. The plain RNN mostly forgets it; the LSTM remembers.""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)
T = 100
X = torch.randn(256, T, 1); y = X[:, 0, :]            # must remember the FIRST value for 100 steps
Xtest = torch.randn(256, T, 1)

def train(cell):
    torch.manual_seed(0)
    rnn, out = cell(1, 32, batch_first=True), nn.Linear(32, 1)
    if cell is nn.LSTM:                                 # common trick: start with the forget gate open
        for name, p in rnn.named_parameters():
            if "bias" in name: p.data[32:64] = 1.0
    opt = torch.optim.Adam(list(rnn.parameters()) + list(out.parameters()), lr=1e-2)
    for _ in range(300):
        opt.zero_grad()
        seq, _ = rnn(X)
        loss = ((out(seq[:, -1]) - y) ** 2).mean(); loss.backward(); opt.step()
    with torch.no_grad():
        seq, _ = rnn(Xtest)
        return round(((out(seq[:, -1]) - Xtest[:, 0, :]) ** 2).mean().item(), 3)

print("plain RNN test error:", train(nn.RNN))     # about 0.2: it mostly forgot
print("LSTM test error     :", train(nn.LSTM))    # about 0.01: it remembered''',
  [("Why does the cell state help gradients?", "It's updated by addition with a forget gate near 1, so gradients pass back without being repeatedly shrunk."),
   ("How does a GRU differ from an LSTM?", "Two gates instead of three and no separate cell state, so fewer parameters.")])

L("m-seq2seq",
  "A sequence-to-sequence model reads an input sequence with an encoder and writes an output sequence with a decoder, as in translation and summarisation.",
  """Translation, summarisation, speech-to-text and chatbots all map one sequence to another of different length. The encoder–decoder pattern behind them is the direct ancestor of the transformer.""",
  """1. **Encoder**: reads the whole input ("I love tea") and summarises it into vectors.
2. **Decoder**: generates the output one token at a time ("J'", "aime", "le", "thé", end), each step using the encoder's summary and the tokens produced so far.
3. Generation stops at a special **end-of-sequence** token.

**Teacher forcing**: during training, the decoder is fed the **true** previous token rather than its own guess, which makes training faster and stable.

**Attention** fixed the main weakness: instead of squeezing the whole input into one vector, the decoder looks back at all encoder states at every step and focuses on the relevant words. This led to transformers.""",
  [("Lengths differ",
    """Input: 3 English words. Output: 4 French tokens. Seq2seq handles this because the decoder decides when to stop."""),
   ("Teacher forcing",
    """True output "J' aime le thé". At step 3 the decoder receives "J' aime" (the truth), even if it predicted "J' adore" at step 2.""")],
  ("Why was a single fixed-size encoder vector a problem for long sentences?",
   "All information had to fit in one vector, so details of long inputs were lost; attention lets the decoder look at every input position."),
  [("Encoder", "reads and summarises the input sequence"),
   ("Decoder", "generates the output sequence step by step"),
   ("Teacher forcing", "feeding the true previous token during training"),
   ("End-of-sequence token", "a special token that means 'stop'")],
  """A tiny GRU encoder–decoder that learns to reverse sequences of digits (a stand-in for translation), trained with teacher forcing.""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)
V, L, START = 10, 5, 10                                   # digits 0-9, length 5, token 10 = start
src = torch.randint(0, V, (3000, L)); tgt = src.flip(1)  # task: output the sequence reversed

emb = nn.Embedding(V + 1, 32)
enc, dec = nn.GRU(32, 64, batch_first=True), nn.GRU(32, 64, batch_first=True)
out = nn.Linear(64, V)
params = [*emb.parameters(), *enc.parameters(), *dec.parameters(), *out.parameters()]
opt = torch.optim.Adam(params, lr=5e-3)

dec_in = torch.cat([torch.full((3000, 1), START), tgt[:, :-1]], 1)    # teacher forcing: true previous tokens
for epoch in range(150):
    opt.zero_grad()
    _, h = enc(emb(src))                                  # encoder summary
    y, _ = dec(emb(dec_in), h)
    loss = nn.functional.cross_entropy(out(y).reshape(-1, V), tgt.reshape(-1)); loss.backward(); opt.step()

with torch.no_grad():                                     # generate one token at a time
    s = torch.tensor([[3, 1, 4, 1, 5]]); _, h = enc(emb(s)); tok = torch.tensor([[START]]); res = []
    for _ in range(L):
        y, h = dec(emb(tok), h); tok = out(y).argmax(-1); res.append(tok.item())
print("input [3, 1, 4, 1, 5] -> output", res)''',
  [("What does teacher forcing feed the decoder during training?", "The true previous output token."),
   ("Which idea removed the single-vector bottleneck?", "Attention.")])

L("m-time-series",
  "Time series data is ordered in time, so the past predicts the future; respect that order when validating, and handle trend, seasonality and lag effects.",
  """Sales forecasts, demand planning, stock levels, energy load and server traffic are all time series, and they're full of traps (random splits, future leakage) that interviewers look for.""",
  """A series is often viewed as **trend** (long-term direction) + **seasonality** (repeating pattern: weekly, yearly) + **noise**.

- **Stationarity**: mean and spread don't change over time. Many classical models need it; **differencing** (today − yesterday) often achieves it.
- **Autocorrelation**: how today relates to yesterday, last week, etc.
- **Models**:
  - Naive baselines: tomorrow = today; or = same day last week (seasonal naive).
  - **ARIMA / SARIMA**: AutoRegressive (past values) + Integrated (differencing) + Moving Average (past errors), with a seasonal part.
  - **ML with lag features**: give a gradient-boosting model columns like "sales 1, 7 and 14 days ago" and "7-day average".
- **Validation**: always train on the past and test on the future (rolling or expanding windows), never random splits.""",
  [("Seasonal naive baseline",
    """Daily sales with a weekly pattern. Forecast for next Monday = last Monday's sales. Any fancy model must beat this."""),
   ("Lag features",
    """For 21 Nov: lag_1 = sales on 20 Nov, lag_7 = sales on 14 Nov, rolling_7 = mean of 14–20 Nov. These turn forecasting into ordinary regression.""")],
  ("Why is a random train/test split wrong for forecasting?",
   "It lets the model train on future days and test on past ones, leaking information it would never have in real use."),
  [("Trend / seasonality", "long-term direction / repeating pattern"),
   ("Stationary", "statistical properties that don't change over time"),
   ("Lag feature", "a past value used as an input"),
   ("Walk-forward validation", "repeatedly training on the past and testing on the next period")],
  """A synthetic sales series: seasonal-naive baseline versus gradient boosting on lag features, with a time-ordered split.""",
  r'''import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

rng = np.random.default_rng(0)
days = pd.date_range("2024-01-01", periods=730)
sales = 100 + 0.05 * np.arange(730) + 15 * (days.dayofweek >= 5) + rng.normal(0, 5, 730)   # trend + weekends + noise
df = pd.DataFrame({"sales": sales}, index=days)
for lag in [1, 7, 14]:
    df[f"lag_{lag}"] = df["sales"].shift(lag)               # past values only
df["roll_7"] = df["sales"].shift(1).rolling(7).mean()
df["dow"] = df.index.dayofweek
df = df.dropna()

train, test = df[:"2025-09-30"], df["2025-10-01":]         # past -> future, no shuffling
model = HistGradientBoostingRegressor().fit(train.drop(columns="sales"), train["sales"])
print("seasonal naive MAE:", round(mean_absolute_error(test["sales"], test["lag_7"]), 2))
print("model MAE         :", round(mean_absolute_error(test["sales"], model.predict(test.drop(columns="sales"))), 2))''',
  [("Name a good baseline for daily data with a weekly pattern.", "Seasonal naive: the value on the same weekday last week."),
   ("Why use .shift() when making rolling features?", "So each row's feature only uses earlier days, not the current one (no leakage).")])

L("m-ts-dl",
  "Neural networks forecast time series by learning from sliding windows of past values; they shine with many related series, many sensors and long histories.",
  """For a single short series, classical methods or gradient boosting usually win. With thousands of products, many sensors or rich patterns (energy grids, traffic, demand at Amazon scale), deep models such as LSTMs, 1-D CNNs and temporal transformers pull ahead.""",
  """1. **Make windows**: from a long series, cut (input window, target) pairs: the past 30 values → the next 1 (or next 7) values.
2. **Scale** each series (e.g. standardise), using statistics from the training period only.
3. **Choose a model**:
   - **LSTM/GRU**: reads the window step by step.
   - **1-D CNN**: filters slide along time, catching local shapes; fast.
   - **Temporal transformers** (e.g. Temporal Fusion Transformer, PatchTST): attention over the window plus extra inputs (holidays, prices).
4. Validate with **time-ordered** splits, and compare with the seasonal-naive and gradient-boosting baselines.""",
  [("Windowing by hand",
    """Series 10, 12, 13, 15, 16, 18 with window 3: inputs (10, 12, 13) → 15, (12, 13, 15) → 16, (13, 15, 16) → 18. Six values give 3 training pairs."""),
   ("Global models",
    """Instead of one model per product, train one network on windows from all 5,000 products. Patterns learned on popular products help rare ones.""")],
  ("With window length 30 and a 1,000-day series predicting 1 day ahead, how many training windows can you make?",
   "1,000 − 30 = 970."),
  [("Sliding window", "a fixed-length chunk of past values used as input"),
   ("Horizon", "how far ahead you forecast"),
   ("Global model", "one model trained on many related series"),
   ("1-D convolution", "a filter sliding along the time axis")],
  """Windowing a seasonal series and training a small 1-D CNN on it, compared with the naive baseline.""",
  r'''import numpy as np, torch, torch.nn as nn
torch.manual_seed(0); rng = np.random.default_rng(0)
t = np.arange(1200)
series = np.sin(2 * np.pi * t / 50) + 0.1 * rng.normal(size=t.size)     # repeating pattern + noise

W = 60
X = np.stack([series[i:i + W] for i in range(len(series) - W)]); y = series[W:]   # windows -> next value
X = torch.tensor(X, dtype=torch.float32).unsqueeze(1); y = torch.tensor(y, dtype=torch.float32)
split = 1000                                                                    # time-ordered split
model = nn.Sequential(nn.Conv1d(1, 16, 5, padding=2), nn.ReLU(), nn.AdaptiveAvgPool1d(8), nn.Flatten(), nn.Linear(128, 1))
opt = torch.optim.Adam(model.parameters(), lr=1e-2)
for epoch in range(300):
    opt.zero_grad(); loss = ((model(X[:split]).squeeze(1) - y[:split]) ** 2).mean(); loss.backward(); opt.step()

with torch.no_grad():
    mae = (model(X[split:]).squeeze(1) - y[split:]).abs().mean().item()
naive = np.abs(series[W + split:] - series[W + split - 1:-1]).mean()          # tomorrow = today
print("1-D CNN MAE:", round(mae, 3), "  naive MAE:", round(naive, 3))''',
  [("What is a sliding window in forecasting?", "A fixed-length chunk of past values used as one training input."),
   ("When do deep models beat classical forecasting?", "With many related series, many input variables and long histories.")])
