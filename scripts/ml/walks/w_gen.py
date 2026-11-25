"""Real-data walkthroughs: Generative AI, RL, LLM systems, responsible AI, graphs."""
import re, math, collections, json, time
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt
from walks.w_nlp import _sms, _tok, _short, _split, _ngram, _next_probs, _lsa, _search


def _torch():
    import torch
    torch.manual_seed(0); torch.set_num_threads(2)
    return torch


def _digits():
    from sklearn.model_selection import train_test_split
    dg = D("digits")
    return train_test_split(dg.data / 16, dg.target, test_size=0.3, random_state=0)


def _img(v):
    return t(pd.DataFrame(np.asarray(v).reshape(8, 8)).round(0).astype(int) + 0)


def _digit_clf():
    from sklearn.svm import SVC
    Xtr, Xte, ytr, yte = _digits()
    return SVC(probability=True, random_state=0).fit(Xtr, ytr)


@walk("m-vae", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits(); X = torch.tensor(Xtr, dtype=torch.float32)
    enc = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 4)); dec = nn.Sequential(nn.Linear(2, 128), nn.ReLU(), nn.Linear(128, 64), nn.Sigmoid())
    o = torch.optim.Adam(list(enc.parameters()) + list(dec.parameters()), 2e-3); log = []
    for ep in range(1, 201):
        for idx in torch.randperm(len(X)).split(128):
            h = enc(X[idx]); mu, lv = h[:, :2], h[:, 2:]
            z = mu + torch.randn_like(mu) * torch.exp(0.5 * lv); R = dec(z)
            rec = nn.functional.binary_cross_entropy(R, X[idx], reduction="sum") / len(idx); kl = -0.5 * torch.sum(1 + lv - mu ** 2 - lv.exp()) / len(idx)
            o.zero_grad(); (rec + kl).backward(); o.step()
        if ep in (1, 20, 200): log.append({"epoch": ep, "reconstruction loss": rec.item(), "KL (how far from N(0,1))": kl.item()})
    with torch.no_grad():
        mu = enc(torch.tensor(Xte, dtype=torch.float32))[:, :2].numpy()
        cent = pd.DataFrame(mu, columns=["z1", "z2"]).assign(digit=yte).groupby("digit").mean()
        new = dec(torch.randn(200, 2)).numpy()
        a, b = np.where(yte == 0)[0][0], np.where(yte == 1)[0][0]
        path = [dec(torch.tensor(mu[a] * (1 - s) + mu[b] * s, dtype=torch.float32)[None]).numpy()[0] for s in [0, 0.5, 1]]
    clf = _digit_clf(); pn = clf.predict_proba(new)
    pm = clf.predict(np.array(path))
    return [
        ("Encode each digit as a small cloud", f"The encoder maps each real digit to a mean and a spread in a 2-D latent space; we sample a point from that cloud and the decoder rebuilds the 64 pixels. Loss = reconstruction error + KL term (keeps the clouds near a standard normal):\n\n{t(pd.DataFrame(log), nd=2)}"),
        ("Where the digits live", f"Average latent position of each test digit:\n\n{t(cent, nd=2, index=True)}\n\nSimilar-looking digits end up near each other; nobody gave it the labels."),
        ("Generate and morph", f"Decoding 200 random points from N(0, 1) gives new digits; a classifier reads them as {len(set(pn.argmax(1)))} different digits, {pct(pn.max(1).mean())} sure on average. Walking the straight line from a real 0 to a real 1 in latent space, the decoded images read as {', '.join(map(str, pm))}.\n\n{_img(path[1] * 16)}\n\n(the halfway image)"),
    ], "A VAE learns a smooth latent space; sampling from it generates new data and moving through it morphs between examples."


@walk("m-diffusion", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits(); X = torch.tensor(Xtr * 2 - 1, dtype=torch.float32)
    T = 100; beta = torch.linspace(1e-4, 0.12, T); ab = torch.cumprod(1 - beta, 0)
    x0 = X[0]; rows = []
    g = torch.Generator().manual_seed(0); eps = torch.randn(64, generator=g)
    for tt in [0, 10, 30, 60, 99]:
        xt = ab[tt].sqrt() * x0 + (1 - ab[tt]).sqrt() * eps
        rows.append({"step t": tt, "signal kept √ᾱ": ab[tt].sqrt().item(), "noise added √(1−ᾱ)": (1 - ab[tt]).sqrt().item(), "correlation with the original": np.corrcoef(xt.numpy(), x0.numpy())[0, 1]})
    net = nn.Sequential(nn.Linear(64 + 16, 256), nn.SiLU(), nn.Linear(256, 256), nn.SiLU(), nn.Linear(256, 64))
    temb = lambda tt: torch.cat([torch.sin(tt[:, None] * torch.exp(-torch.arange(8) * 0.8)), torch.cos(tt[:, None] * torch.exp(-torch.arange(8) * 0.8))], 1)
    o = torch.optim.Adam(net.parameters(), 2e-3)
    for step in range(4000):
        idx = torch.randint(0, len(X), (128,)); tt = torch.randint(0, T, (128,)); e = torch.randn(128, 64)
        xt = ab[tt].sqrt()[:, None] * X[idx] + (1 - ab[tt]).sqrt()[:, None] * e
        loss = ((net(torch.cat([xt, temb(tt.float())], 1)) - e) ** 2).mean(); o.zero_grad(); loss.backward(); o.step()
    with torch.no_grad():
        x = torch.randn(200, 64)
        for tt in reversed(range(T)):
            tv = torch.full((200,), float(tt)); e = net(torch.cat([x, temb(tv)], 1))
            x = (x - beta[tt] / (1 - ab[tt]).sqrt() * e) / (1 - beta[tt]).sqrt()
            if tt > 0: x = x + beta[tt].sqrt() * torch.randn_like(x)
        gen = ((x.clamp(-1, 1) + 1) / 2).numpy()
    clf = _digit_clf(); p = clf.predict_proba(gen)
    return [
        ("Forward: add noise step by step", f"Take a real digit (a {ytr[0]}) and mix in Gaussian noise over 100 steps:\n\n{t(pd.DataFrame(rows), nd=3)}\n\nBy the last step only {rows[-1]['signal kept √ᾱ']:.2f} of the signal is left: it is practically pure noise."),
        ("Learn to predict the noise", f"A network sees a noisy digit plus the step number and guesses the noise that was added. Trained on the 1,257 real digits for 4,000 batches; final loss {loss.item():.3f} (predicting zero noise would score about 1)."),
        ("Reverse: start from noise, remove it 100 times", f"{_img(gen[0] * 16)}\n\nA digit classifier reads this one as a **{p[0].argmax()}** ({pct(p[0].max())} sure); over 200 samples it sees {len(set(p.argmax(1)))} different digits and is {pct(p.max(1).mean())} sure on average. Stable Diffusion does the same in a compressed latent space, guided by a text prompt."),
    ], "Diffusion models learn to undo noise; generating means starting from pure noise and denoising step by step."


@walk("m-self-supervised", "digits")
def _():
    torch = _torch(); nn = torch.nn
    from scipy import ndimage
    from sklearn.linear_model import LogisticRegression
    Xtr, Xte, ytr, yte = _digits(); rng = np.random.default_rng(0)

    def aug(B):
        out = []
        for x in B:
            im = ndimage.rotate(x.reshape(8, 8), rng.uniform(-20, 20), reshape=False, order=1)
            im = ndimage.shift(im, rng.integers(-1, 2, 2), order=0) * rng.uniform(0.7, 1.0)
            out.append(np.clip(im, 0, 1).ravel())
        return torch.tensor(np.array(out), dtype=torch.float32)
    mk = lambda: nn.Sequential(nn.Linear(64, 256), nn.ReLU(), nn.Linear(256, 64))
    head = nn.Sequential(nn.ReLU(), nn.Linear(64, 32))
    torch.manual_seed(0); rand_enc = mk(); enc = mk()
    o = torch.optim.Adam(list(enc.parameters()) + list(head.parameters()), 1e-3)
    for step in range(600):
        b = Xtr[rng.choice(len(Xtr), 256, replace=False)]
        z1 = nn.functional.normalize(head(enc(aug(b))), dim=1); z2 = nn.functional.normalize(head(enc(aug(b))), dim=1)
        logits = z1 @ z2.T / 0.2
        loss = nn.functional.cross_entropy(logits, torch.arange(len(b))); o.zero_grad(); loss.backward(); o.step()
    with torch.no_grad():
        F = {"raw pixels": (Xtr, Xte), "random (untrained) encoder": (rand_enc(torch.tensor(Xtr, dtype=torch.float32)).numpy(), rand_enc(torch.tensor(Xte, dtype=torch.float32)).numpy()),
             "self-supervised encoder": (enc(torch.tensor(Xtr, dtype=torch.float32)).numpy(), enc(torch.tensor(Xte, dtype=torch.float32)).numpy())}
    rows = []
    for n in [2, 10]:
        r = {k: [] for k in F}
        for rep in range(10):
            sel = np.concatenate([rng.choice(np.where(ytr == d)[0], n, replace=False) for d in range(10)])
            for k, (A, B) in F.items():
                r[k].append(LogisticRegression(max_iter=3000).fit(A[sel], ytr[sel]).score(B, yte))
        rows.append({"labels per digit": n, **{k: np.mean(v) for k, v in r.items()}})
    best = max(rows[0], key=lambda k: rows[0][k] if k != "labels per digit" else -1)
    return [
        ("Make labels from the data itself", "Take an unlabelled digit, make two random variations (rotate, shift, fade). Task: from a batch of 256 such pairs, recognise which two images came from the same original (contrastive learning, as in SimCLR). No digit labels are used."),
        ("Train the encoder", f"600 batches on the 1,257 training images; the contrastive loss falls to {loss.item():.2f} (random guessing among 256 would be {math.log(256):.2f})."),
        ("Then learn the real task with very few labels", f"Freeze the encoder and train a logistic regression on its outputs (avg of 10 random label picks, {len(yte)} test digits):\n\n{t(pd.DataFrame(rows), nd=3)}\n\nWith 2 labels per digit the best features here are: **{best}**.{" Tiny 8 × 8 digits are so simple that raw pixels are already good features; self-supervision beats the random encoder clearly, and pays off most on large, complex images and text." if best == "raw pixels" else ""} Large models (BERT, GPT, CLIP, DINO) are pre-trained this way on huge unlabelled data."),
    ], "Self-supervised learning invents a training task from unlabelled data, producing features that make the real task need fewer labels."


@walk("m-peft-lora", "digits")
def _():
    torch = _torch(); nn = torch.nn
    from scipy import ndimage
    Xtr, Xte, ytr, yte = _digits()
    rot = lambda A: np.array([np.clip(ndimage.rotate(x.reshape(8, 8), 35, reshape=False, order=1), 0, 1).ravel() for x in A])
    Rtr, Rte = rot(Xtr), rot(Xte)
    torch.manual_seed(0)
    base = nn.Sequential(nn.Linear(64, 256), nn.ReLU(), nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 10))
    o = torch.optim.Adam(base.parameters(), 1e-3); X = torch.tensor(Xtr, dtype=torch.float32); Y = torch.tensor(ytr)
    for _ in range(60):
        for idx in torch.randperm(len(X)).split(64):
            o.zero_grad(); nn.functional.cross_entropy(base(X[idx]), Y[idx]).backward(); o.step()
    acc = lambda m, A, y: (m(torch.tensor(A, dtype=torch.float32)).argmax(1).numpy() == y).mean()

    class LoRA(nn.Module):
        def __init__(s, lin, r):
            super().__init__(); s.lin = lin; s.A = nn.Parameter(torch.randn(r, lin.in_features) * 0.01); s.B = nn.Parameter(torch.zeros(lin.out_features, r))
            for p in s.lin.parameters(): p.requires_grad = False
        def forward(s, x): return s.lin(x) + x @ s.A.T @ s.B.T
    import copy
    n_lab = 200; sel = np.random.default_rng(0).choice(len(Rtr), n_lab, replace=False)
    XR = torch.tensor(Rtr[sel], dtype=torch.float32); YR = torch.tensor(ytr[sel])
    rows = []
    with torch.no_grad(): rows.append({"method": "base model, no adaptation", "trainable weights": 0, "rotated test accuracy": acc(base, Rte, yte), "original test accuracy": acc(base, Xte, yte)})
    for name in ["full fine-tune", "LoRA rank 4", "LoRA rank 1"]:
        m = copy.deepcopy(base)
        if name.startswith("LoRA"):
            r = int(name[-1])
            for i in [0, 2, 4]: m[i] = LoRA(m[i], r)
        params = [p for p in m.parameters() if p.requires_grad]; o = torch.optim.Adam(params, 3e-3 if name.startswith("LoRA") else 1e-3)
        for _ in range(300):
            o.zero_grad(); nn.functional.cross_entropy(m(XR), YR).backward(); o.step()
        with torch.no_grad(): rows.append({"method": name, "trainable weights": sum(p.numel() for p in params), "rotated test accuracy": acc(m, Rte, yte), "original test accuracy": acc(m, Xte, yte)})
    return [
        ("A trained base model and a new task", f"Base network ({sum(p.numel() for p in base.parameters()):,} weights) trained on real digits. New task: the same digits **rotated 35°**, with only {n_lab} labelled examples. The base model does badly on them out of the box (first row below)."),
        ("LoRA: freeze W, learn a small correction B·A", "For each layer y = W·x, keep W frozen and add a low-rank update: y = W·x + B·(A·x), where A is r × inputs and B is outputs × r. With r = 1 or 4 that's a tiny fraction of the weights. B starts at 0, so training starts exactly from the base model."),
        ("Results", f"{t(pd.DataFrame(rows), nd=3)}\n\nLoRA reaches most of full fine-tuning's gain while training a few percent of the weights. Both forget some of the original task while adapted, but with LoRA the base weights are untouched: remove the adapter and you are back to the base model's {pct(rows[0]['original test accuracy'], 1)}, and one base can be shared by many adapters. That's how big LLMs are customised on one GPU."),
    ], "Parameter-efficient fine-tuning (LoRA) adapts a big frozen model by training small low-rank add-on matrices."


@walk("m-rlhf-dpo", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer
    tr, te = _split()
    vec = TfidfVectorizer(sublinear_tf=True, min_df=2).fit(tr["text"])
    rng = np.random.default_rng(0)

    def pairs(df, n):
        h = df[df.label == "ham"]["text"].values; s = df[df.label == "spam"]["text"].values
        return [(h[rng.integers(len(h))], s[rng.integers(len(s))]) for _ in range(n)]
    P = pairs(tr, 2000); Pt = pairs(te, 500)
    A = vec.transform([a for a, b in P]); B = vec.transform([b for a, b in P])
    w = np.zeros(A.shape[1]); lr = 1.0
    for ep in range(30):
        d = (A - B); s = d @ w; p = 1 / (1 + np.exp(-s))
        w += lr * (d.T @ (1 - p)) / len(P) - 1e-4 * w
    r = lambda texts: vec.transform(texts) @ w
    acc = np.mean(r([a for a, b in Pt]) > r([b for a, b in Pt]))
    ex = pd.DataFrame({"message": [_short(x, 60) for x in te["text"].head(6)], "reward": r(te["text"].head(6).tolist())}).sort_values("reward", ascending=False)
    uni, bi, tri, ctx1, ctx2 = _ngram()

    def gen(seed):
        rg = np.random.default_rng(seed); wds = ["<s>", "<s>"]
        while wds[-1] != "</s>" and len(wds) < 20:
            c = _next_probs(wds[-2], wds[-1]); ws, ps = zip(*c); ps = np.array(ps) / sum(ps); wds.append(ws[rg.choice(len(ws), p=ps)])
        return " ".join(x for x in wds[2:] if x != "</s>")
    cands = [gen(s) for s in range(16)]; rc = r(cands)
    spamlike = lambda xs: np.mean([any(k in x for k in ["free", "txt", "claim", "prize", "win", "call"]) for x in xs])
    best = [cands[i] for i in np.argsort(-rc)[:4]]
    return [
        ("Preference pairs", f"RLHF starts from people choosing the better of two responses. As a stand-in we use real labels: in each pair the chosen text is a real personal message, the rejected one a real spam message. 2,000 training pairs, e.g.:\n\n- chosen: “{_short(P[0][0], 80)}”\n- rejected: “{_short(P[0][1], 80)}”"),
        ("Train a reward model (Bradley–Terry)", f"Learn a score r(text) so that P(chosen beats rejected) = σ(r(chosen) − r(rejected)). On 500 unseen pairs it picks the chosen message **{pct(acc, 1)}** of the time. Scores of real messages:\n\n{t(ex, nd=2)}"),
        ("Optimise the generator towards high reward", f"Sample 16 messages from an SMS language model; {pct(spamlike(cands))} contain spam words. Keep the 4 the reward model likes best (best-of-n, the simplest form of RLHF): {pct(spamlike(best))} contain spam words.\n\n" + "\n".join(f"- “{b}”" for b in best[:2]) + "\n\nPPO trains the model itself to get high reward (with a penalty for drifting from the original); **DPO** skips the reward model and directly raises log P(chosen) − log P(rejected) relative to a reference model."),
    ], "RLHF/DPO turn human preferences into a training signal that steers a model towards answers people prefer."


@walk("m-rl-basics", "frozenlake")
def _():
    import gymnasium as gym
    env = gym.make("FrozenLake-v1", is_slippery=True); nS, nA = env.observation_space.n, env.action_space.n
    Q = np.zeros((nS, nA)); rng = np.random.default_rng(0); alpha, gamma = 0.1, 0.99
    hist = []; wins = 0
    for ep in range(1, 20001):
        s, _ = env.reset(seed=int(rng.integers(1e9))); eps = max(0.05, 1 - ep / 10000); done = False
        while not done:
            a = int(rng.integers(nA)) if rng.random() < eps else int(Q[s].argmax())
            s2, rwd, term, trunc, _ = env.step(a); done = term or trunc
            Q[s, a] += alpha * (rwd + gamma * Q[s2].max() * (not term) - Q[s, a]); s = s2
            wins += rwd
        if ep % 5000 == 0: hist.append({"episodes so far": ep, "goal reached in the last 5,000": pct(wins / 5000)}); wins = 0
    def evaluate(policy, n=2000):
        w = 0
        for i in range(n):
            s, _ = env.reset(seed=i); done = False
            while not done:
                s, rwd, term, trunc, _ = env.step(policy(s)); done = term or trunc; w += rwd
        return w / n
    learned = evaluate(lambda s: int(Q[s].argmax())); rand = evaluate(lambda s: int(rng.integers(nA)))
    arrows = np.array(["←", "↓", "→", "↑"])[Q.argmax(1)].reshape(4, 4)
    grid = np.array([list(r) for r in env.unwrapped.desc.astype(str)])
    show = np.where(np.isin(grid, ["H", "G"]), grid, arrows)
    return [
        ("The environment", "FrozenLake: a 4 × 4 frozen lake. Start top-left (S), goal bottom-right (G), holes (H) end the episode. The ice is slippery: the agent only moves the way it chose 1/3 of the time. Reward 1 for reaching G, else 0."),
        ("Q-learning: learn the value of each move by trial and error", f"After every step: Q(s, a) ← Q(s, a) + 0.1 · [reward + 0.99 · max Q(next) − Q(s, a)]. Explore randomly at first, then exploit more and more:\n\n{t(pd.DataFrame(hist))}"),
        ("The learned policy", f"Best action in each square:\n\n{t(pd.DataFrame(show))}\n\nOver 2,000 test episodes it reaches the goal **{pct(learned)}** of the time, vs {pct(rand)} for random moves. Some squares point away from the goal: on slippery ice, the safest move is often the one that can't slide you into a hole."),
    ], "Reinforcement learning learns which action is worth most in each state from rewards alone, by trying things and updating value estimates."


@walk("m-llm-inference", "sms")
def _():
    torch = _torch()
    from transformers import GPT2Config, GPT2LMHeadModel
    cfg = GPT2Config(vocab_size=2000, n_positions=256, n_embd=256, n_layer=4, n_head=4)
    m = GPT2LMHeadModel(cfg).eval()
    from walks.w_nlp import _bpe_bytes
    tk = _bpe_bytes(); msg = _sms()["text"][2]
    ids = torch.tensor([tk.encode(msg).ids])

    def gen(use_cache, n=64):
        t0 = time.perf_counter()
        with torch.no_grad(): m.generate(ids, max_new_tokens=n, min_new_tokens=n, do_sample=False, use_cache=use_cache, pad_token_id=0)
        return time.perf_counter() - t0
    gen(True, 4)
    a, b = gen(False), gen(True)
    sizes = []
    for bs in [1, 8]:
        x = ids.repeat(bs, 1); t0 = time.perf_counter()
        with torch.no_grad(): m.generate(x, max_new_tokens=32, min_new_tokens=32, do_sample=False, pad_token_id=0)
        sizes.append({"batch size": bs, "tokens generated": 32 * bs, "tokens per second": 32 * bs / (time.perf_counter() - t0)})
    W = m.transformer.h[0].mlp.c_fc.weight.detach().numpy()
    q = np.round(W / (np.abs(W).max() / 127)).clip(-127, 127); deq = q * (np.abs(W).max() / 127)
    nparam = sum(p.numel() for p in m.parameters())
    return [
        ("Prompt → tokens → one token at a time", f"Prompt: a real SMS of {ids.shape[1]} tokens. A {nparam / 1e6:.1f}M-weight GPT-2-style model (random weights, so the words are nonsense, but the speed is real) generates 64 new tokens; each needs a full pass through the network."),
        ("KV cache", f"Without a cache, every step recomputes attention keys/values for the whole sequence: **{a:.2f} s**. With the KV cache (store them, compute only the new token): **{b:.2f} s**, {a / b:.1f}× faster on this CPU."),
        ("Batching and quantisation", f"{t(pd.DataFrame(sizes), nd=0)}\n\nBatching shares each weight load across requests, so throughput goes up. Int8 quantisation of one weight matrix: 4× smaller than float32, average error {np.abs(W - deq).mean():.5f} on weights of typical size {np.abs(W).mean():.4f}. Serving systems (vLLM, TGI) combine all three."),
    ], "Fast LLM serving relies on caching past keys/values, batching requests and storing weights in fewer bits."


def _bm25(docs):
    toks = [_tok(d) for d in docs]; N = len(toks); avg = np.mean([len(x) for x in toks])
    df = collections.Counter(w for x in toks for w in set(x)); tf = [collections.Counter(x) for x in toks]
    idf = {w: math.log(1 + (N - n + 0.5) / (n + 0.5)) for w, n in df.items()}

    def score(q):
        qs = _tok(q); out = np.zeros(N)
        for i, (c, x) in enumerate(zip(tf, toks)):
            s = 0
            for w in qs:
                if w in c: s += idf[w] * c[w] * 2.2 / (c[w] + 1.2 * (0.25 + 0.75 * len(x) / avg))
            out[i] = s
        return out
    return score


@walk("m-advanced-rag", "sms")
def _():
    df, vec, svd, E = _lsa(); docs = df["text"].tolist(); bm = _bm25(docs)
    rng = np.random.default_rng(0)
    cand = [i for i in range(len(docs)) if len(_tok(docs[i])) >= 12]
    qs = rng.choice(cand, 60, replace=False); recs = {"BM25 (keywords)": [], "dense (LSA vectors)": [], "hybrid (reciprocal rank fusion)": []}
    ex = None
    for i in qs:
        w = _tok(docs[i]); q = " ".join(rng.choice(w, 4, replace=False))
        s1 = bm(q); qe = svd.transform(vec.transform([q]))[0]; s2 = E @ (qe / max(np.linalg.norm(qe), 1e-9))
        r1 = np.argsort(-s1); r2 = np.argsort(-s2)
        rank1 = np.empty(len(docs)); rank1[r1] = np.arange(len(docs)); rank2 = np.empty(len(docs)); rank2[r2] = np.arange(len(docs))
        rrf = 1 / (60 + rank1) + 1 / (60 + rank2); r3 = np.argsort(-rrf)
        key = re.sub(r"\W+", "", docs[i].lower())[:40]
        hit = lambda r: any(re.sub(r"\W+", "", docs[j].lower())[:40] == key for j in r[:5])
        recs["BM25 (keywords)"].append(hit(r1)); recs["dense (LSA vectors)"].append(hit(r2)); recs["hybrid (reciprocal rank fusion)"].append(hit(r3))
        if ex is None: ex = (q, docs[i], int(rank1[i]) + 1, int(rank2[i]) + 1, int(np.where(r3 == i)[0][0]) + 1)
    res = pd.DataFrame([{"retriever": k, "recall@5 (60 test queries)": np.mean(v)} for k, v in recs.items()])
    return [
        ("Build a test set", f"Pick 60 real messages; for each, the query is 4 random words from it, and the goal is to find that message among all {len(docs):,}. Example: query “{ex[0]}” → target “{_short(ex[1], 80)}”."),
        ("Two retrievers, then fuse them", f"BM25 scores exact keyword matches (rare words count more); dense search compares meaning vectors. Reciprocal rank fusion adds 1/(60 + rank) from each list. For the example, the target was ranked {ex[2]} by BM25, {ex[3]} by dense, {ex[4]} by hybrid."),
        ("Measure, don't guess", f"{t(res, nd=3)}\n\n{"Here plain BM25 wins: the queries are exact words from the message, which is what keyword search is built for, and fusing it with a weaker retriever drags it down. With paraphrased questions dense search would do better. " if res.iloc[0, 1] > res.iloc[2, 1] else ""}Other upgrades (query rewriting, re-ranking the top 20 with a cross-encoder, smarter chunking, metadata filters) should be judged the same way: on a labelled set of queries."),
    ], "Advanced RAG improves retrieval with hybrid search, fusion and re-ranking, and checks each change with retrieval metrics."


def _tools():
    df = _sms()
    def search(q, k=3): return _search(q, k)[["label", "message"]].to_dict("records")
    def count(word=None, label=None):
        d = df
        if word: d = d[d["text"].str.lower().str.contains(r"\b" + re.escape(word) + r"\b")]
        if label: d = d[d["label"] == label]
        return int(len(d))
    def calc(expr): return round(eval(expr, {"__builtins__": {}}), 1)
    return {"search_messages": search, "count_messages": count, "calculator": calc}


@walk("m-agents", "sms")
def _():
    T = _tools()
    plan = [("I need how many messages contain 'free', and how many of those are spam.", "count_messages", {"word": "free"}),
            ("Now count only the spam ones.", "count_messages", {"word": "free", "label": "spam"}),
            (None, "calculator", None),
            ("Let me look at an example to check the word is used as expected.", "search_messages", {"q": "free", "k": 2})]
    trace = []; obs = {}
    for i, (thought, tool, args) in enumerate(plan):
        if tool == "calculator":
            args = {"expr": f"100 * {obs[1]} / {obs[0]}"}; thought = "Compute the percentage."
        out = T[tool](**args); obs[i] = out
        trace.append({"step": i + 1, "thought": thought, "action": f"{tool}({', '.join(f'{k}={v!r}' for k, v in args.items())})", "observation": _short(json.dumps(out, ensure_ascii=False), 110)})
    return [
        ("Tools the agent can call", "`search_messages(q, k)`: vector search over the 5,572 real SMS · `count_messages(word, label)`: exact counts · `calculator(expr)`. Each tool has a name, a description and typed arguments; the model sees these descriptions."),
        ("The loop: think → act → observe", f"Question: “What percentage of messages containing 'free' are spam?” (The thoughts below are scripted to show the format; an LLM writes them in a real agent. The tool results are real.)\n\n{t(pd.DataFrame(trace))}"),
        ("Answer and safeguards", f"Final answer: **{obs[2]}%** of the {obs[0]} messages containing 'free' are spam. Real agents add a step limit, validate tool arguments, ask before irreversible actions, and log every step so mistakes can be traced."),
    ], "An agent is an LLM in a loop that decides which tool to call, reads the result and continues until it can answer."


@walk("m-agent-systems", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    tr, te = _split()
    vec = TfidfVectorizer(sublinear_tf=True); clf = LogisticRegression(max_iter=2000, C=10).fit(vec.fit_transform(tr["text"]), tr["label"])
    batch = pd.concat([te[te.label == "spam"].head(3), te[te.label == "ham"].head(3)])
    rows = []; t_route = 0
    for m in batch["text"]:
        p = clf.predict_proba(vec.transform([m]))[0, 1]
        route = "spam analyst" if p > 0.8 else ("human review" if p > 0.2 else "reply drafter")
        if route == "spam analyst":
            out = f"numbers: {re.findall(r'0\d{9,10}', m) or '-'}; amounts: {re.findall(r'£\s?\d[\d,]*', m) or '-'}"
        elif route == "reply drafter":
            out = "draft a short friendly reply"
        else: out = "unsure → queue for a person"
        rows.append({"message": _short(m, 50), "router P(spam)": p, "sent to": route, "specialist output": _short(out, 60)})
    r = pd.DataFrame(rows)
    allp = clf.predict_proba(vec.transform(te["text"]))[:, 1]
    share = pd.Series(np.where(allp > 0.8, "spam analyst", np.where(allp > 0.2, "human review", "reply drafter"))).value_counts(normalize=True).map(pct)
    return [
        ("Split the job into roles", "A **router** decides who handles each incoming SMS; a **spam analyst** extracts phone numbers and amounts for blocking; a **reply drafter** helps with personal messages; unclear cases go to a **human**. Each role can be a separate prompt, model or tool set."),
        ("Real messages through the system", f"{t(r, nd=2)}"),
        ("Check the routing on all 1,393 test messages", f"{t(share.rename('share of messages').to_frame(), index=True)}\n\nMulti-agent designs help when roles need different tools or permissions, but every hand-off can lose information, so keep the number of agents small and log the hand-offs."),
    ], "Agent systems split work across specialised roles with a router or orchestrator, plus a path to a human for unclear cases."


@walk("m-hitl", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    tr, te = _split(); vec = TfidfVectorizer(sublinear_tf=True, min_df=2).fit(tr["text"])
    X = vec.transform(tr["text"]); y = (tr["label"] == "spam").values.astype(int); Xt = vec.transform(te["text"]); yt = (te["label"] == "spam").values.astype(int)
    budgets = [20, 60, 100, 200]; res = {"random": [], "uncertainty (least sure first)": []}
    for rep in range(5):
        rng = np.random.default_rng(rep)
        start = list(np.r_[rng.choice(np.where(y == 1)[0], 5, replace=False), rng.choice(np.where(y == 0)[0], 5, replace=False)])
        for strat in res:
            lab = list(start); scores = []
            while len(lab) < max(budgets):
                m = LogisticRegression(max_iter=2000, C=10).fit(X[lab], y[lab])
                if len(lab) in budgets: scores.append(f1_score(yt, m.predict(Xt)))
                pool = np.setdiff1d(np.arange(X.shape[0]), lab)
                if strat == "random": pick = rng.choice(pool, 10, replace=False)
                else: pr = m.predict_proba(X[pool])[:, 1]; pick = pool[np.argsort(np.abs(pr - 0.5))[:10]]
                lab += list(pick)
            m = LogisticRegression(max_iter=2000, C=10).fit(X[lab], y[lab]); scores.append(f1_score(yt, m.predict(Xt)))
            res[strat].append(scores)
    tab = pd.DataFrame({"labels given by a human": budgets, **{k: np.mean(v, 0) for k, v in res.items()}})
    m = LogisticRegression(max_iter=2000, C=10).fit(X[:30], y[:30]); pr = m.predict_proba(X)[:, 1]
    q = np.argsort(np.abs(pr - 0.5))[:3]
    ask = pd.DataFrame({"message the model asks about": [_short(tr["text"].values[i], 70) for i in q], "its P(spam)": pr[q]})
    return [
        ("Start small", f"Labelling costs human time. Start with 10 labelled messages (5 spam, 5 ham) out of {X.shape[0]:,}; the rest are unlabelled."),
        ("Ask about the most confusing messages", f"After each round the model picks the 10 messages it is least sure about (P(spam) closest to 0.5) and a person labels them. Examples it would ask about:\n\n{t(ask, nd=2)}"),
        ("Spam F1 on the test set (avg of 5 runs)", f"{t(tab, nd=3)}\n\n{'Asking about uncertain messages beats random picking for the same labelling effort.' if tab.iloc[1, 2] > tab.iloc[1, 1] else 'Here random picking keeps up with uncertainty sampling.'} Human-in-the-loop also covers reviewing low-confidence predictions in production and feeding corrections back into training."),
    ], "Human-in-the-loop puts people where they add most value: labelling the hardest examples and reviewing uncertain predictions."


@walk("m-llm-eval", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    tr, te = _split(); y = (te["label"] == "spam").values
    A = LogisticRegression(max_iter=2000, C=10); va = TfidfVectorizer(sublinear_tf=True); A.fit(va.fit_transform(tr["text"]), tr["label"] == "spam"); pa = A.predict(va.transform(te["text"]))
    B = MultinomialNB(); vb = CountVectorizer(); B.fit(vb.fit_transform(tr["text"]), tr["label"] == "spam"); pb = B.predict(vb.transform(te["text"]))
    ca, cb = pa == y, pb == y
    rng = np.random.default_rng(0); diffs = []
    for _ in range(2000):
        i = rng.integers(0, len(y), len(y)); diffs.append(ca[i].mean() - cb[i].mean())
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    L = te["text"].str.len().values
    sl = pd.DataFrame([{"slice": name, "messages": int(msk.sum()), "version A accuracy": ca[msk].mean(), "version B accuracy": cb[msk].mean()} for name, msk in [("short (< 40 chars)", L < 40), ("medium", (L >= 40) & (L < 120)), ("long (≥ 120 chars)", L >= 120), ("spam only", y), ("ham only", ~y)]])
    return [
        ("A fixed, labelled test set", f"{len(y):,} real messages the systems never saw. Version A = logistic regression on TF-IDF, version B = Naive Bayes (think: two prompt or model versions). Accuracy: A **{pct(ca.mean(), 2)}**, B **{pct(cb.mean(), 2)}**."),
        ("Is the difference real?", f"Bootstrap: resample the test set 2,000 times and recompute A − B. 95% interval: **{lo * 100:+.2f} to {hi * 100:+.2f}** percentage points. {'It includes 0, so we cannot say which is better.' if lo < 0 < hi else 'It excludes 0, so the difference is probably real.'} They disagree on {(pa != pb).sum()} messages: read those."),
        ("Slice the results", f"{t(sl, nd=3)}\n\nAverages hide weak spots. For generative LLMs the same discipline applies: fixed test prompts, a scoring rule (exact match, rubric or LLM-as-judge checked against humans), confidence intervals and slices."),
    ], "Evaluation needs a fixed labelled set, a clear metric, a check that differences aren't noise, and per-slice results."


@walk("m-guardrails", "sms")
def _():
    df = _sms()
    phone = re.compile(r"\b0\d{9,10}\b"); url = re.compile(r"(?:https?://|www\.)\S+", re.I); short = re.compile(r"\b\d{5}\b")
    red = lambda s: short.sub("[SHORTCODE]", url.sub("[URL]", phone.sub("[PHONE]", s)))
    hits = pd.DataFrame([{"pattern": n, "messages containing it": int(df["text"].str.contains(p).sum())} for n, p in [("phone number", phone), ("web address", url), ("5-digit short code", short)]])
    ex = sorted(df[df["text"].str.contains(phone)]["text"].tolist(), key=len)[:2]
    schema = {"label": {"spam", "ham"}}

    def validate(out):
        try:
            d = json.loads(out)
        except Exception: return "rejected: not valid JSON"
        if set(d) != {"label"}: return "rejected: wrong fields"
        if d["label"] not in schema["label"]: return "rejected: label not allowed"
        return "accepted"
    outs = ['{"label": "spam"}', '{"label": "maybe"}', 'Sure! It is spam.', '{"label": "ham", "note": "call 07123456789"}']
    v = pd.DataFrame({"model output": outs, "validator": [validate(o) for o in outs]})
    inj = [m for m in df["text"] if re.search(r"ignore (all|previous)|disregard", m, re.I)]
    return [
        ("Input guardrail: find and mask personal data", f"Before text reaches a model or a log, detect personal data with rules:\n\n{t(hits)}\n\nExample: “{ex[0]}” → “{red(ex[0])}”"),
        ("Output guardrail: validate before using", f"Require a strict format and reject anything else:\n\n{t(v)}"),
        ("Policy and injection checks", f"Also check for prompt injection ('ignore previous instructions…' inside user text; {len(inj)} of the 5,572 real messages contain such phrases), topics you refuse, and rate limits. Rules catch the obvious cases; classifiers and human review catch the rest."),
    ], "Guardrails are checks around a model: clean and mask inputs, validate outputs, and block unsafe or off-policy requests."


@walk("m-responsible-ai", "titanic")
def _():
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_predict
    df = D("titanic").copy(); df["Age"] = df["Age"].fillna(df["Age"].median())
    X = pd.get_dummies(df[["Pclass", "Age", "SibSp", "Parch", "Fare", "Sex"]], drop_first=True).astype(float); y = df["Survived"].values
    p = cross_val_predict(LogisticRegression(max_iter=2000), X, y, cv=5, method="predict_proba")[:, 1]; pred = p > 0.5
    g = df["Sex"].values
    rows = []
    for grp in ["female", "male"]:
        m = g == grp
        rows.append({"group": grp, "passengers": int(m.sum()), "actually survived": y[m].mean(), "predicted to survive": pred[m].mean(), "true positive rate (survivors found)": pred[m & (y == 1)].mean(), "accuracy": (pred[m] == y[m]).mean()})
    r = pd.DataFrame(rows)
    X2 = X.drop(columns=["Sex_male"]); p2 = cross_val_predict(LogisticRegression(max_iter=2000), X2, y, cv=5, method="predict_proba")[:, 1]; pred2 = p2 > 0.5
    r2 = pd.DataFrame([{"model": name, "accuracy": (pr == y).mean(), "female predicted survival": pr[g == "female"].mean(), "male predicted survival": pr[g == "male"].mean()} for name, pr in [("with sex", pred), ("sex column removed", pred2)]])
    return [
        ("Measure outcomes per group", f"A survival model on real Titanic passengers (cross-validated predictions):\n\n{t(r, nd=2)}\n\nThe model mirrors history: women were prioritised for lifeboats. Here that's the point of the analysis, but the same pattern in a loan or hiring model would be unacceptable."),
        ("Removing the sensitive column isn't enough", f"{t(r2, nd=3)}\n\nWithout the sex column the gap {'shrinks but does not disappear' if abs(r2.iloc[1, 2] - r2.iloc[1, 3]) > 0.05 else 'mostly disappears'}: other columns (fare, class, family) still carry part of the information. Fairness must be measured, not assumed."),
        ("A responsible-AI checklist", "Document the data and intended use (datasheets, model cards); measure error rates per group; explain decisions to the people affected; keep a human in the loop for high-stakes cases; protect privacy; monitor after launch."),
    ], "Responsible AI means checking who a model helps or harms, measuring it per group, and building in transparency and human oversight."


@walk("m-gnn", "karate")
def _():
    import networkx as nx
    G = D("karate"); n = G.number_of_nodes()
    truth = np.array([0 if G.nodes[i]["club"] == "Mr. Hi" else 1 for i in range(n)])
    A = nx.to_numpy_array(G) + np.eye(n); dinv = np.diag(1 / np.sqrt(A.sum(1))); Ah = dinv @ A @ dinv
    torch = _torch(); nn = torch.nn
    At = torch.tensor(Ah, dtype=torch.float32); Xf = torch.eye(n)
    W1 = nn.Linear(n, 16); W2 = nn.Linear(16, 2); o = torch.optim.Adam(list(W1.parameters()) + list(W2.parameters()), 0.01, weight_decay=5e-4)
    lab = [0, 33]; yt = torch.tensor(truth[lab])
    for _ in range(200):
        h = torch.relu(At @ W1(Xf)); out = At @ W2(h)
        o.zero_grad(); nn.functional.cross_entropy(out[lab], yt).backward(); o.step()
    pred = out.argmax(1).numpy()
    deg = dict(G.degree())
    nb = pd.DataFrame([{"member": i, "friends": deg[i], "friends in Mr. Hi's club": sum(truth[j] == 0 for j in G[i]), "real club": "Mr. Hi" if truth[i] == 0 else "Officer", "GNN prediction": "Mr. Hi" if pred[i] == 0 else "Officer"} for i in [0, 2, 8, 19, 33]])
    return [
        ("A real social network", f"{n} karate club members, {G.number_of_edges()} friendships. The club split in two: {int((truth == 0).sum())} followed the instructor (Mr. Hi, member 0), {int((truth == 1).sum())} the officer (member 33). We tell the model only the clubs of members 0 and 33."),
        ("Message passing", "A graph convolution updates each member's vector as the (degree-normalised) average of their own and their friends' vectors, then applies a learned weight matrix. Two layers = information from friends of friends."),
        ("Predict everyone's side", f"{t(nb)}\n\nAccuracy on all {n} members: **{pct((pred == truth).mean(), 1)}** from just 2 labels. Members with friends in both groups (like 2, 8 and 19) are the hardest."),
    ], "Graph neural networks learn from connections: each node aggregates its neighbours' information, so labels spread through the network."
