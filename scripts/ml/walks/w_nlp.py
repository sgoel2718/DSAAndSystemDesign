"""Real-data walkthroughs: NLP and LLMs (all on the real SMS Spam Collection)."""
import re, math, collections, functools, json
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt


def _sms():
    df = D("sms").copy(); df["text"] = df["text"].astype(str); return df


def _tok(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def _short(s, n=70):
    s = s.replace("|", "/")
    return s if len(s) <= n else s[:n - 1] + "…"


@functools.lru_cache(None)
def _split():
    from sklearn.model_selection import train_test_split
    df = _sms()
    return train_test_split(df, test_size=0.25, random_state=0, stratify=df["label"])


@functools.lru_cache(None)
def _ngram():
    tr, te = _split()
    uni = collections.Counter(); bi = collections.Counter(); tri = collections.Counter()
    for s in tr["text"]:
        w = ["<s>", "<s>"] + _tok(s) + ["</s>"]
        uni.update(w[2:]); bi.update(zip(w[1:], w[2:])); tri.update(zip(w, w[1:], w[2:]))
    ctx1 = collections.Counter(); ctx2 = collections.Counter()
    for (a, b), c in bi.items(): ctx1[a] += c
    for (a, b, c_), c in tri.items(): ctx2[(a, b)] += c
    return uni, bi, tri, ctx1, ctx2


def _next_probs(prev2, prev1, k=None):
    uni, bi, tri, ctx1, ctx2 = _ngram()
    if ctx2[(prev2, prev1)] > 0:
        cand = {c: n / ctx2[(prev2, prev1)] for (a, b, c), n in tri.items() if a == prev2 and b == prev1}
    else:
        cand = {b: n / ctx1[prev1] for (a, b), n in bi.items() if a == prev1}
    out = sorted(cand.items(), key=lambda x: -x[1])
    return out[:k] if k else out


@functools.lru_cache(None)
def _V():
    return len({w for s in _sms()["text"] for w in _tok(s)}) + 1


def _bigram_pp(texts, uni, bi, ctx1, V=None, lam=0.7):
    """Perplexity of an interpolated bigram model: 0.7·P(word | previous word) + 0.3·P(word) (add-one smoothed unigram)."""
    V = _V(); N = sum(uni.values()); lp = 0; n = 0
    for s in texts:
        w = ["<s>"] + _tok(s) + ["</s>"]
        for a, b in zip(w, w[1:]):
            pb = bi[(a, b)] / ctx1[a] if ctx1[a] else 0
            lp += math.log(lam * pb + (1 - lam) * (uni[b] + 1) / (N + V)); n += 1
    return math.exp(-lp / n)


@functools.lru_cache(None)
def _lsa():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    df = _sms()
    vec = TfidfVectorizer(sublinear_tf=True, min_df=2)
    X = vec.fit_transform(df["text"])
    svd = TruncatedSVD(100, random_state=0).fit(X)
    E = svd.transform(X); E = E / np.linalg.norm(E, axis=1, keepdims=True).clip(1e-9)
    return df, vec, svd, E


def _search(q, k=4):
    df, vec, svd, E = _lsa()
    qe = svd.transform(vec.transform([q]))[0]; qe = qe / max(np.linalg.norm(qe), 1e-9)
    s = E @ qe; seen = set(); idx = []
    for i in np.argsort(-s):
        key = re.sub(r"\W+", "", df["text"].values[i].lower())[:40]
        if key in seen: continue
        seen.add(key); idx.append(i)
        if len(idx) == k: break
    idx = np.array(idx)
    return pd.DataFrame({"score": s[idx], "label": df["label"].values[idx], "message": [_short(m) for m in df["text"].values[idx]]})


@walk("m-nlp-tasks", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    tr, te = _split()
    vec = TfidfVectorizer(sublinear_tf=True); m = LogisticRegression(max_iter=2000, C=10).fit(vec.fit_transform(tr["text"]), tr["label"])
    ex = pd.concat([te[te.label == "ham"].head(2), te[te.label == "spam"].head(2)]).copy(); ex["predicted"] = m.predict(vec.transform(ex["text"])); ex["message"] = ex["text"].map(_short)
    df = _sms()
    phones = df["text"].str.findall(r"\b0\d{9,10}\b"); money = df["text"].str.findall(r"£\s?\d[\d,]*")
    has = df.assign(phone=phones.str.len() > 0, money=money.str.len() > 0).groupby("label")[["phone", "money"]].mean().map(lambda v: pct(v, 1))
    first = df[money.str.len() > 0].iloc[0]
    return [
        ("Text classification", f"Label a whole message. Spam filter trained on {len(tr):,} real SMS, applied to new ones:\n\n{t(ex[['message', 'label', 'predicted']])}\n\nAccuracy on {len(te):,} test messages: **{pct(m.score(vec.transform(te['text']), te['label']), 1)}**."),
        ("Information extraction", f"Pull structured facts out of text, here phone numbers and £ amounts. Example: “{_short(first['text'], 90)}” → amounts {money[first.name]}, phones {phones[first.name]}. Share of messages containing each:\n\n{t(has, index=True)}"),
        ("Search / similarity", f"Find messages that mean something similar to a query. Query “are we still meeting for dinner tonight”:\n\n{t(_search('are we still meeting for dinner tonight', 3), nd=2)}\n\nOther tasks (translation, summarisation, question answering, chat) build on the same pieces."),
    ], "NLP tasks differ in what they output: a label, extracted fields, similar documents or new text."


@walk("m-text-preprocessing", "sms")
def _():
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    df = _sms(); sw = set(stopwords.words("english")); ps = PorterStemmer()
    msg = df[df["label"] == "spam"]["text"].iloc[3]
    steps = []
    low = msg.lower(); steps.append(("lowercase", low))
    toks = _tok(msg); steps.append(("split into tokens", " · ".join(toks)))
    nos = [w for w in toks if w not in sw]; steps.append(("remove stop words", " · ".join(nos)))
    st = [ps.stem(w) for w in nos]; steps.append(("stem (Porter)", " · ".join(st)))
    allt = [w for s in df["text"] for w in _tok(s)]
    v0 = len(set(re.findall(r"\S+", " ".join(df["text"])))); v1 = len(set(allt)); v2 = len(set(w for w in allt if w not in sw)); v3 = len({ps.stem(w) for w in set(allt) if w not in sw})
    vocab = pd.DataFrame([{"after": "raw (split on spaces)", "distinct tokens": v0}, {"after": "lowercase + strip punctuation", "distinct tokens": v1}, {"after": "remove stop words", "distinct tokens": v2}, {"after": "stemming", "distinct tokens": v3}])
    return [
        ("A real spam message", f"“{msg}”"),
        ("Step by step", t(pd.DataFrame(steps, columns=["step", "result"]))),
        ("Effect on the whole collection", f"{t(vocab)}\n\nEach step merges variants (FREE / free / free!) so a model sees them as one word. Modern subword tokenisers skip most of this and keep the original text."),
    ], "Preprocessing normalises messy text into clean tokens; it shrinks the vocabulary but can also throw away useful signals (spam loves CAPITALS and '!')."


@walk("m-web-scraping", "sms")
def _():
    from bs4 import BeautifulSoup
    df = _sms().head(5)
    html = "<html><body><h1>Inbox</h1><ul>" + "".join(f'<li class="msg" data-label="{r.label}"><span class="text">{r.text.replace("<", "&lt;").replace(">", "&gt;")}</span> <a href="/msg/{i}">open</a></li>' for i, r in df.iterrows()) + "</ul></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("li.msg")
    out = pd.DataFrame([{"label (from data-label)": li["data-label"], "text (from span.text)": _short(li.select_one("span.text").get_text(), 60), "link (from a href)": li.a["href"]} for li in items])
    return [
        ("The page", f"Five real messages placed on a simple web page ({len(html):,} characters of HTML). The start of it:\n\n`{html[:180]}…`"),
        ("Find the elements", f"BeautifulSoup parses the HTML into a tree; the CSS selector `li.msg` finds **{len(items)}** message items. From each we read an attribute, a child's text and a link:\n\n{t(out)}"),
        ("Be a good citizen", "On real sites: read robots.txt and the terms of use, prefer an official API, add delays between requests, identify your scraper, and never collect personal data you don't have the right to."),
    ], "Scraping = download HTML, parse it into a tree, select the elements you need and save them as rows."


@walk("m-text-representation", "sms")
def _():
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    df = _sms()
    docs = [df["text"][i] for i in [0, 2, 5]]
    cv = CountVectorizer(); X = cv.fit_transform(docs)
    voc = cv.get_feature_names_out()
    keep = [w for w in ["free", "entry", "win", "call", "the", "you", "to", "go", "now"] if w in voc][:7]
    bow = pd.DataFrame(X.toarray(), columns=voc)[keep]; bow.index = ["msg 1", "msg 2", "msg 3"]
    tv = TfidfVectorizer().fit(df["text"])
    idf = pd.DataFrame({"word": keep, "in how many of 5,572 messages": [int((CountVectorizer(vocabulary=[w]).fit_transform(df['text']).toarray() > 0).sum()) for w in keep], "IDF weight": [tv.idf_[tv.vocabulary_[w]] for w in keep]})
    from sklearn.metrics.pairwise import cosine_similarity
    T = tv.transform(docs); S = pd.DataFrame(cosine_similarity(T), index=["msg 1", "msg 2", "msg 3"], columns=["msg 1", "msg 2", "msg 3"])
    return [
        ("Three real messages", "\n".join(f"{i + 1}. “{_short(d, 110)}”" for i, d in enumerate(docs))),
        ("Bag of words: count each word", f"The 3 messages use {len(voc)} distinct words, so each becomes a vector of {len(voc)} counts (mostly 0). Some columns:\n\n{t(bow, index=True)}"),
        ("TF-IDF: weight rare words up", f"{t(idf, nd=2)}\n\nCommon words like 'to' and 'you' get low weight; rarer, more telling words get high weight. Cosine similarity of the TF-IDF vectors:\n\n{t(S, nd=2, index=True)}"),
    ], "Text must become numbers: bag-of-words counts words, TF-IDF weights them by how rare they are, embeddings (next) capture meaning."


@walk("m-word-embeddings", "sms")
def _():
    from gensim.models import Word2Vec
    df = _sms(); sents = [_tok(s) for s in df["text"]]
    m = Word2Vec(sents, vector_size=50, window=4, min_count=5, sg=1, epochs=30, seed=0, workers=1)
    rows = []
    for w in ["free", "love", "tomorrow", "pls"]:
        if w in m.wv: rows.append({"word": w, "nearest words (cosine similarity)": ", ".join(f"{a} {b:.2f}" for a, b in m.wv.most_similar(w, topn=5))})
    pairs = pd.DataFrame([{"pair": f"{a} – {b}", "similarity": m.wv.similarity(a, b)} for a, b in [("call", "phone"), ("prize", "cash"), ("love", "prize"), ("tomorrow", "today")] if a in m.wv and b in m.wv])
    return [
        ("Learn from context", f"Word2Vec reads all {len(df):,} messages ({sum(map(len, sents)):,} words) and learns a 50-number vector per word so that words used in similar contexts get similar vectors. Vocabulary (words seen ≥ 5 times): {len(m.wv):,}."),
        ("Nearest neighbours", t(pd.DataFrame(rows))),
        ("Similarity of word pairs", f"{t(pairs, nd=2)}\n\nNobody told it what any word means; this small corpus is enough to group SMS slang and spam vocabulary. Big models trained on billions of words give much cleaner neighbours."),
    ], "Word embeddings place words with similar usage close together in a vector space."


@walk("m-text-classification", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix, precision_score, recall_score
    tr, te = _split()
    rows = []; models = {}
    for name, vec, clf in [("Naive Bayes on word counts", CountVectorizer(), MultinomialNB()), ("Logistic regression on TF-IDF", TfidfVectorizer(sublinear_tf=True), LogisticRegression(max_iter=2000, C=10))]:
        X = vec.fit_transform(tr["text"]); clf.fit(X, tr["label"]); p = clf.predict(vec.transform(te["text"])); models[name] = (vec, clf, p)
        rows.append({"model": name, "accuracy": (p == te["label"]).mean(), "spam precision": precision_score(te["label"], p, pos_label="spam"), "spam recall": recall_score(te["label"], p, pos_label="spam")})
    vec, clf, p = models["Logistic regression on TF-IDF"]
    coef = pd.Series(clf.coef_[0], index=vec.get_feature_names_out()).sort_values()
    cm = pd.DataFrame(confusion_matrix(te["label"], p, labels=["ham", "spam"]), index=["true ham", "true spam"], columns=["predicted ham", "predicted spam"])
    miss = te[(p != te["label"])].head(3).assign(predicted=p[(p != te["label"])][:3], message=lambda d: d["text"].map(_short))
    return [
        ("Two classic models", f"{t(pd.DataFrame(rows), nd=3)}\n\nPrecision: of messages flagged spam, how many really are. Recall: of real spam, how much was caught."),
        ("What the model learned", f"Most spam-like words: {', '.join(coef.index[-8:][::-1])}. Most ham-like: {', '.join(coef.index[:8])}.\n\n{t(cm, index=True)}"),
        ("Look at the mistakes", f"{t(miss[['message', 'label', 'predicted']])}\n\nMissed spam usually looks chatty; that's where better features or a transformer help."),
    ], "Text classifiers turn messages into word features and learn which words point to which label; check precision, recall and the actual mistakes."


@walk("m-language-models", "sms")
def _():
    uni, bi, tri, ctx1, ctx2 = _ngram(); tr, te = _split()
    nxt = pd.DataFrame([{"after": f"“{a} {b}”", "most likely next words": ", ".join(f"{w} {p:.2f}" for w, p in _next_probs(a, b, 4))} for a, b in [("<s>", "i"), ("i", "will"), ("call", "me"), ("you", "have"), ("have", "won")]]).replace("“<s> i”", "“(start) i”")
    V = len(uni) + 1
    pp = pd.DataFrame([{"test messages": lab, "perplexity (lower = less surprised)": _bigram_pp(te[te.label == lab]["text"], uni, bi, ctx1)} for lab in ["ham", "spam"]])
    rng = np.random.default_rng(3); outs = []
    for _ in range(3):
        w = ["<s>", "<s>"]
        while w[-1] != "</s>" and len(w) < 22:
            c = _next_probs(w[-2], w[-1]); ws, ps = zip(*c); ps = np.array(ps) / sum(ps)
            w.append(ws[rng.choice(len(ws), p=ps)])
        outs.append(" ".join(x for x in w[2:] if x != "</s>"))
    return [
        ("Count what follows what", f"A trigram model counts, over {len(tr):,} training messages, which word follows each pair of words:\n\n{t(nxt)}"),
        ("Score new text", f"{t(pp, nd=1)}\n\nPerplexity ≈ how many words the model is choosing between at each step (scored with a smoothed word-pair model). {"Spam surprises it more: 87% of its training messages were ham." if pp.iloc[1, 1] > pp.iloc[0, 1] else "Spam surprises it less, even though 87% of its training messages were ham: spam reuses the same few templates over and over."}"),
        ("Generate by sampling", "\n".join(f"- “{o}”" for o in outs) + "\n\nLocally fluent, globally nonsense: three words of context aren't enough. GPT-style models do the same job (predict the next token) with thousands of tokens of context."),
    ], "A language model assigns probabilities to the next word; it can score text and generate new text one word at a time."


@walk("m-topic-models", "sms")
def _():
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    df = _sms()
    cv = CountVectorizer(stop_words="english", min_df=5, max_df=0.3, token_pattern=r"(?u)\b[a-zA-Z]{3,}\b")
    X = cv.fit_transform(df["text"]); voc = cv.get_feature_names_out()
    lda = LatentDirichletAllocation(6, random_state=0, max_iter=30, learning_method="batch").fit(X)
    Th = lda.transform(X)
    topics = pd.DataFrame([{"topic": k + 1, "top words": ", ".join(voc[np.argsort(-lda.components_[k])[:8]]), "share of spam among its messages": pct((df["label"][Th.argmax(1) == k] == "spam").mean())} for k in range(6)])
    i = int(np.argmax(Th.max(1) < 0.7) if (Th.max(1) < 0.7).any() else 0)
    mix = ", ".join(f"topic {k + 1}: {v:.0%}" for k, v in sorted(enumerate(Th[i]), key=lambda x: -x[1])[:3])
    return [
        ("Words only, no labels", f"LDA sees each of the {len(df):,} messages as a bag of words ({len(voc):,}-word vocabulary, stop words removed) and assumes each message mixes a few topics, each topic being a mix of words."),
        ("Six topics it found", f"{t(topics)}\n\nThe topics are just word lists; a human gives them names (e.g. a prize/claim topic is clearly spam)."),
        ("Messages are mixtures", f"“{_short(df['text'][i], 100)}” → {mix}."),
    ], "Topic models discover groups of words that tend to appear together and describe each document as a mix of them."


@walk("m-attention", "sms")
def _():
    from gensim.models import Word2Vec
    df = _sms(); sents = [_tok(s) for s in df["text"]]
    m = Word2Vec(sents, vector_size=32, window=4, min_count=3, sg=1, epochs=20, seed=0, workers=1)
    words = [w for w in _tok("Free entry to win a cash prize call now") if w in m.wv]
    E = np.array([m.wv[w] for w in words]); E = E / np.linalg.norm(E, axis=1, keepdims=True)
    S = 4 * (E @ E.T)  # cosine similarity × 4 (a fixed temperature)
    A = np.exp(S - S.max(1, keepdims=True)); A /= A.sum(1, keepdims=True)
    tab = pd.DataFrame(A, index=words, columns=words)
    q = words.index("prize") if "prize" in words else 0
    return [
        ("Each word asks: who should I listen to?", f"Sentence (built from common spam words): “{' '.join(words)}”. Each word has a vector (from Word2Vec on the SMS data). Attention score between two words = dot product of their vectors (here query = key = the word vector, scaled)."),
        ("Softmax turns scores into weights", f"Each row sums to 1: how much each word attends to every other word.\n\n{t(tab, nd=2, index=True)}"),
        ("New representation = weighted average", f"'{words[q]}' gives most weight to: {', '.join(f'{w} ({tab.loc[words[q], w]:.2f})' for w in tab.loc[words[q]].sort_values(ascending=False).index[:3])}. Its new vector is that weighted mix of word vectors, so it now carries context. A transformer learns separate query, key and value projections and uses many such heads in parallel."),
    ], "Attention lets every word build its representation from the words most relevant to it, weighted by similarity."


def _vocab_ids(texts, V=3000, L=40):
    c = collections.Counter(w for s in texts for w in _tok(s))
    itos = ["<pad>", "<unk>"] + [w for w, _ in c.most_common(V - 2)]; stoi = {w: i for i, w in enumerate(itos)}
    enc = lambda s: ([stoi.get(w, 1) for w in _tok(s)] + [0] * L)[:L]
    return itos, stoi, enc


@walk("m-transformer", "sms")
def _():
    import torch
    torch.manual_seed(0); torch.set_num_threads(2); nn = torch.nn
    tr, te = _split(); itos, stoi, enc = _vocab_ids(tr["text"])
    Xtr = torch.tensor([enc(s) for s in tr["text"]]); ytr = torch.tensor((tr["label"] == "spam").values.astype(int))
    Xte = torch.tensor([enc(s) for s in te["text"]]); yte = (te["label"] == "spam").values.astype(int)

    class TF(nn.Module):
        def __init__(s):
            super().__init__(); s.emb = nn.Embedding(3000, 64, padding_idx=0); s.pos = nn.Embedding(40, 64)
            s.enc = nn.TransformerEncoder(nn.TransformerEncoderLayer(64, 4, 128, dropout=0.1, batch_first=True), 2); s.out = nn.Linear(64, 2)
        def forward(s, x):
            mask = x == 0; h = s.emb(x) + s.pos(torch.arange(x.shape[1]))[None]
            h = s.enc(h, src_key_padding_mask=mask); h = h.masked_fill(mask[..., None], 0).sum(1) / (~mask).sum(1, keepdim=True).clamp(min=1)
            return s.out(h)
    torch.manual_seed(0); net = TF(); o = torch.optim.Adam(net.parameters(), 1e-3)
    for ep in range(4):
        net.train()
        for idx in torch.randperm(len(Xtr)).split(64):
            o.zero_grad(); nn.functional.cross_entropy(net(Xtr[idx]), ytr[idx]).backward(); o.step()
    net.eval()
    with torch.no_grad(): p = net(Xte).argmax(1).numpy()
    ex = te["text"].iloc[0]; ids = enc(ex)
    n = sum(p_.numel() for p_ in net.parameters())
    return [
        ("Text → token ids → vectors", f"Keep the 3,000 most common words; every message becomes 40 ids (padded with 0). “{_short(ex, 60)}” → {ids[:12]}… Each id looks up a 64-number embedding, plus a learned **position** embedding (attention alone doesn't know word order)."),
        ("The encoder", f"2 transformer layers, each: 4-head self-attention (every word looks at every word) → small feed-forward network, both with residual connections and layer normalisation. Then average the word vectors and classify. {n:,} weights in total."),
        ("Trained from scratch for 4 epochs", f"Test accuracy **{pct((p == yte).mean(), 1)}** on {len(te):,} messages; spam caught {pct((p[yte == 1] == 1).mean())}. Similar to TF-IDF + logistic regression on this easy task: transformers pay off with more data, longer text and pre-training."),
    ], "A transformer turns tokens into vectors, adds positions, and refines them with stacked self-attention and feed-forward layers."


@functools.lru_cache(None)
def _bpe(vocab_size=1000):
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers
    tr, te = _split()
    tk = Tokenizer(models.BPE(unk_token="[UNK]")); tk.pre_tokenizer = pre_tokenizers.Whitespace()
    tk.train_from_iterator(tr["text"].tolist(), trainers.BpeTrainer(vocab_size=vocab_size, special_tokens=["[UNK]", "[PAD]", "[CLS]", "[SEP]", "[MASK]"]))
    return tk


@functools.lru_cache(None)
def _bpe_bytes(vocab_size=2000):
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders
    tr, te = _split()
    tk = Tokenizer(models.BPE()); tk.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False); tk.decoder = decoders.ByteLevel()
    tk.train_from_iterator(tr["text"].tolist(), trainers.BpeTrainer(vocab_size=vocab_size, special_tokens=["<pad>", "<s>", "</s>"], initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
    return tk


@walk("m-tokenization", "sms")
def _():
    tr, te = _split()
    msg = te[te.label == "spam"]["text"].iloc[0]
    rows = []
    for v in [300, 1000, 5000]:
        tk = _bpe(v); toks = tk.encode(msg).tokens
        total = sum(len(tk.encode(s).ids) for s in te["text"].head(500))
        rows.append({"BPE vocabulary": v, "tokens for this message": len(toks), "avg tokens per message (500 test msgs)": total / 500, "first tokens": " · ".join(toks[:10])})
    words = _tok(msg)
    tk = _bpe(1000)
    rare = [w for w in ["congratulations", "lol", "xxx", "txt", "ringtone"] if w]
    split = pd.DataFrame([{"word": w, "BPE pieces (1,000 vocab)": " · ".join(tk.encode(w).tokens)} for w in rare])
    return [
        ("A real message", f"“{msg}”\n\nWord-level: {len(words)} words. Character-level: {len(msg)} characters."),
        ("Byte-pair encoding learned from the SMS data", f"Start from characters, then repeatedly merge the most frequent adjacent pair into a new token, until the vocabulary has the chosen size:\n\n{t(pd.DataFrame(rows), nd=1)}\n\nBigger vocabulary → fewer, longer tokens."),
        ("How words get split", f"{t(split)}\n\nCommon words stay whole; rare words break into reusable pieces, so nothing is ever 'unknown'. GPT and BERT tokenisers work this way with 30k–200k tokens."),
    ], "Subword tokenisers like BPE balance vocabulary size and sequence length, and can encode any text."


@walk("m-bert-gpt-t5", "sms")
def _():
    df = _sms(); msg = df["text"][0]; w = _tok(msg)[:12]
    rng = np.random.default_rng(0)
    mask = sorted(rng.choice(len(w), max(1, round(0.15 * len(w))), replace=False))
    bert_in = " ".join("[MASK]" if i in mask else x for i, x in enumerate(w)); bert_out = ", ".join(w[i] for i in mask)
    gpt = pd.DataFrame([{"input (everything so far)": " ".join(w[:k]), "target (next word)": w[k]} for k in range(1, 5)])
    s0, s1 = 3, 6
    t5_in = " ".join(w[:s0] + ["<X>"] + w[s1:]); t5_out = "<X> " + " ".join(w[s0:s1])
    return [
        ("BERT: fill in the blanks (encoder)", f"From the real message “{' '.join(w)} …”, hide ~15% of the words:\n\n- input: `{bert_in}`\n- target: `{bert_out}`\n\nBERT sees words on **both sides**, so it is great for understanding tasks (classification, search, NER), not for writing text."),
        ("GPT: predict the next word (decoder)", f"The same message gives many training examples:\n\n{t(gpt)}\n\nGPT only looks **left**, so it can generate text word by word."),
        ("T5: text in, text out (encoder-decoder)", f"Replace a span with a sentinel and ask for it back:\n\n- input: `{t5_in}`\n- target: `{t5_out}`\n\nT5 frames every task as text-to-text (e.g. input 'classify: …' → output 'spam')."),
    ], "BERT, GPT and T5 share the transformer but are pre-trained with different objectives, which decides what they're good at."


def _tiny_bert(n_labels=2):
    from transformers import BertConfig, BertForSequenceClassification, BertForMaskedLM
    cfg = BertConfig(vocab_size=1000, hidden_size=64, num_hidden_layers=2, num_attention_heads=4, intermediate_size=128, max_position_embeddings=48, num_labels=n_labels)
    return cfg


@walk("m-huggingface", "sms")
def _():
    import torch
    from transformers import PreTrainedTokenizerFast, BertForSequenceClassification
    from datasets import Dataset
    tr, te = _split()
    tok = PreTrainedTokenizerFast(tokenizer_object=_bpe(1000), unk_token="[UNK]", pad_token="[PAD]", cls_token="[CLS]", sep_token="[SEP]", mask_token="[MASK]")
    ds = Dataset.from_pandas(tr[["text", "label"]].reset_index(drop=True)).map(lambda b: {"labels": [int(l == "spam") for l in b["label"]]}, batched=True)
    ds = ds.map(lambda b: tok(b["text"], truncation=True, max_length=48, padding="max_length"), batched=True)
    enc = tok(te["text"].iloc[0], truncation=True, max_length=48)
    torch.manual_seed(0)
    model = BertForSequenceClassification(_tiny_bert())
    with torch.no_grad():
        out = model(**{k: torch.tensor([v]) for k, v in enc.items()})
    return [
        ("datasets: rows → a Dataset", f"`Dataset.from_pandas(...)` holds {ds.num_rows:,} real training messages; `.map()` adds columns in batches. Columns now: {', '.join(ds.column_names)}."),
        ("Tokenizer: text → input_ids + attention_mask", f"“{_short(te['text'].iloc[0], 60)}” → `input_ids` {enc['input_ids'][:12]}… and `attention_mask` (1 = real token). Tokens: {' · '.join(tok.convert_ids_to_tokens(enc['input_ids'])[:10])} …"),
        ("Model: ids → logits", f"`BertForSequenceClassification` (a tiny 2-layer config here, {sum(p.numel() for p in model.parameters()):,} weights) returns `logits` of shape {tuple(out.logits.shape)}: one score per class. In real use you'd write `AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')` and get weights pre-trained on billions of words; the rest of the code is the same."),
    ], "Hugging Face gives the same three building blocks for every model: datasets, a tokenizer and a model, connected by input_ids and logits."


@walk("m-finetune-bert", "sms")
def _():
    import torch
    from transformers import BertForMaskedLM, BertForSequenceClassification, PreTrainedTokenizerFast, DataCollatorForLanguageModeling
    torch.manual_seed(0); torch.set_num_threads(2)
    tr, te = _split()
    tok = PreTrainedTokenizerFast(tokenizer_object=_bpe(1000), unk_token="[UNK]", pad_token="[PAD]", cls_token="[CLS]", sep_token="[SEP]", mask_token="[MASK]")
    cfg = _tiny_bert()
    enc = lambda s: tok(list(s), truncation=True, max_length=48, padding="max_length", return_tensors="pt")
    allx = enc(pd.concat([tr["text"], te["text"]]).tolist())
    mlm = BertForMaskedLM(cfg); col = DataCollatorForLanguageModeling(tok, mlm_probability=0.15)
    o = torch.optim.AdamW(mlm.parameters(), 2e-3); losses = []
    ids = allx["input_ids"]
    for ep in range(3):
        for b in torch.randperm(len(ids)).split(64):
            batch = col([{"input_ids": i} for i in ids[b]])
            o.zero_grad(); l = mlm(input_ids=batch["input_ids"], attention_mask=(batch["input_ids"] != tok.pad_token_id).long(), labels=batch["labels"]).loss; l.backward(); o.step(); losses.append(l.item())
    Xtr = enc(tr["text"].tolist()); ytr = torch.tensor((tr["label"] == "spam").values.astype(int)); Xte = enc(te["text"].tolist()); yte = (te["label"] == "spam").values.astype(int)
    rng = np.random.default_rng(0); rows = []
    for n in [40, 200]:
        res = {}
        for name in ["from scratch", "pre-trained with MLM, then fine-tuned"]:
            accs = []
            for seed in range(2):
                torch.manual_seed(seed)
                sel = np.r_[rng.choice(np.where(ytr.numpy() == 1)[0], n // 4, replace=False), rng.choice(np.where(ytr.numpy() == 0)[0], n - n // 4, replace=False)]
                clf = BertForSequenceClassification(cfg)
                if name.startswith("pre"): clf.bert.load_state_dict(mlm.bert.state_dict(), strict=False)
                oc = torch.optim.AdamW(clf.parameters(), 1e-3)
                for _ in range(40):
                    oc.zero_grad(); clf(input_ids=Xtr["input_ids"][sel], attention_mask=Xtr["attention_mask"][sel], labels=ytr[sel]).loss.backward(); oc.step()
                clf.eval()
                with torch.no_grad(): p = clf(input_ids=Xte["input_ids"], attention_mask=Xte["attention_mask"]).logits.argmax(1).numpy()
                f1 = 2 * ((p == 1) & (yte == 1)).sum() / max(1, (p == 1).sum() + (yte == 1).sum())
                accs.append(f1)
            res[name] = np.mean(accs)
        rows.append({"labelled messages": n, **{f"spam F1, {k}": v for k, v in res.items()}})
    return [
        ("Step 1: pre-train on unlabelled text", f"A tiny BERT (2 layers) learns masked-word prediction on all {len(ids):,} messages, labels ignored. MLM loss: {np.mean(losses[:20]):.2f} at the start → {np.mean(losses[-20:]):.2f} after 3 passes. (Real BERT does this on billions of words for days.)"),
        ("Step 2: fine-tune with few labels", "Add a classification head on the [CLS] position and train everything on a small labelled set (25% spam), with a small learning rate. Compare with the same network trained from random weights."),
        ("Results on 1,393 test messages (avg of 2 runs)", f"{t(pd.DataFrame(rows), nd=3)}\n\nF1 balances spam precision and recall (1 = perfect). Whatever the size of the gain here, real pre-trained BERT checkpoints make it much bigger because they have seen vastly more text."),
    ], "Fine-tuning starts from a model pre-trained on lots of unlabelled text and adapts it to your task with a few labelled examples."


@walk("m-finetune-gpt", "sms")
def _():
    import torch
    from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast
    torch.manual_seed(0); torch.set_num_threads(2)
    tr, te = _split()
    tok = PreTrainedTokenizerFast(tokenizer_object=_bpe_bytes(), pad_token="<pad>", eos_token="</s>", bos_token="<s>")
    cfg = GPT2Config(vocab_size=2000, n_positions=48, n_embd=128, n_layer=2, n_head=4, bos_token_id=tok.bos_token_id, eos_token_id=tok.eos_token_id)
    m = GPT2LMHeadModel(cfg)
    enc = lambda s: tok(["<s>" + x + "</s>" for x in s], truncation=True, max_length=48, padding="max_length", return_tensors="pt")
    ham = enc(tr[tr.label == "ham"]["text"].tolist()); spam = enc(tr[tr.label == "spam"]["text"].tolist()); spam_te = enc(te[te.label == "spam"]["text"].tolist())

    def train(X, epochs, lr):
        o = torch.optim.AdamW(m.parameters(), lr)
        for _ in range(epochs):
            for b in torch.randperm(len(X["input_ids"])).split(64):
                ids = X["input_ids"][b]; lab = ids.clone(); lab[X["attention_mask"][b] == 0] = -100
                o.zero_grad(); m(input_ids=ids, attention_mask=X["attention_mask"][b], labels=lab).loss.backward(); o.step()

    def ppl(X):
        m.eval(); ids = X["input_ids"]; lab = ids.clone(); lab[X["attention_mask"] == 0] = -100
        with torch.no_grad(): l = m(input_ids=ids, attention_mask=X["attention_mask"], labels=lab).loss.item()
        m.train(); return math.exp(l)

    def sample(seed):
        torch.manual_seed(seed); m.eval()
        out = m.generate(torch.tensor([[tok.bos_token_id]]), max_new_tokens=30, do_sample=True, top_k=20, temperature=0.8, pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
        m.train(); return tok.decode(out[0][1:], skip_special_tokens=True)
    train(ham, 8, 2e-3)
    before = ppl(spam_te); s_before = [sample(i) for i in range(2)]
    train(spam, 4, 1e-3)
    after = ppl(spam_te); s_after = [sample(i) for i in range(2)]
    return [
        ("Base model: trained on normal messages", f"A tiny GPT-2 (2 layers, {sum(p.numel() for p in m.parameters()) / 1e6:.1f} million weights; real GPT-2 has 124 million and up) learns next-token prediction on {len(ham['input_ids']):,} real ham messages. Samples:\n\n" + "\n".join(f"- “{s}”" for s in s_before)),
        ("Fine-tune on a new style", f"Continue training the same weights on only {len(spam['input_ids'])} spam messages (smaller learning rate). Perplexity on unseen spam: **{before:.1f} → {after:.1f}** (lower = the model finds spam less surprising)."),
        ("Samples after fine-tuning", "\n".join(f"- “{s}”" for s in s_after) + "\n\nThe text is rough because the model is tiny, but the vocabulary has shifted towards spam. Same model, new style. Instruction-tuning a big GPT works the same way with (instruction, good answer) pairs."),
    ], "Fine-tuning a GPT continues next-token training on your own text so it adopts that domain's words and style."


@walk("m-decoding", "sms")
def _():
    uni, bi, tri, ctx1, ctx2 = _ngram()

    def greedy(start, n=10):
        w = ["<s>"] + start.split()
        for _ in range(n):
            c = _next_probs(w[-2], w[-1], 1)
            if not c or c[0][0] == "</s>": break
            w.append(c[0][0])
        return " ".join(w[1:])

    def beam(start, B=3, n=8):
        beams = [(0.0, ["<s>"] + start.split())]
        for _ in range(n):
            new = []
            for lp, w in beams:
                if w[-1] == "</s>": new.append((lp, w)); continue
                for x, p in _next_probs(w[-2], w[-1], B): new.append((lp + math.log(p), w + [x]))
            beams = sorted(new, key=lambda z: -z[0])[:B]
        return " ".join(x for x in beams[0][1][1:] if x != "</s>"), beams[0][0]

    def sample(start, temp, k=None, seed=0, n=10):
        rng = np.random.default_rng(seed); w = ["<s>"] + start.split()
        for _ in range(n):
            c = _next_probs(w[-2], w[-1], k)
            ws, ps = zip(*c); lg = np.log(ps) / temp; p = np.exp(lg - lg.max()); p /= p.sum()
            x = ws[rng.choice(len(ws), p=p)]
            if x == "</s>": break
            w.append(x)
        return " ".join(w[1:])
    start = "i will"
    probs = _next_probs("i", "will", 6)
    b, lp = beam(start)
    rows = pd.DataFrame([{"method": "greedy (always the top word)", "output": greedy(start)}, {"method": "beam search (keep 3 best)", "output": b},
                         {"method": "sampling, temperature 0.5", "output": sample(start, 0.5)}, {"method": "sampling, temperature 1.0", "output": sample(start, 1.0)},
                         {"method": "sampling, temperature 1.5, top-k 20", "output": sample(start, 1.5, 20)}])
    temp = pd.DataFrame({"next word": [w for w, _ in probs], "T = 0.5": None, "T = 1": [p for _, p in probs], "T = 2": None})
    p = np.array([p for _, p in probs])
    for T, col in [(0.5, "T = 0.5"), (2, "T = 2")]:
        q = p ** (1 / T); temp[col] = q / q.sum()
    temp["T = 1"] = p / p.sum()
    return [
        ("The model's options after “i will”", f"Next-word probabilities from a trigram model of the SMS messages (top 6, renormalised), and how temperature reshapes them:\n\n{t(temp, nd=3)}\n\nLow temperature sharpens the distribution; high temperature flattens it."),
        ("Five decoding strategies, same model", t(rows)),
        ("Trade-off", "Greedy and beam search are safe but repetitive; sampling is varied but can wander. Chat models typically use temperature ~0.7 with top-p (nucleus) sampling."),
    ], "Decoding turns next-word probabilities into text; the strategy (greedy, beam, temperature, top-k/top-p) changes the output a lot."


@walk("m-llms", "sms")
def _():
    tr, te = _split()
    rows = []
    for frac in [0.05, 0.2, 0.5, 1.0]:
        sub = tr["text"].iloc[: int(len(tr) * frac)]
        uni = collections.Counter(); bi = collections.Counter(); ctx1 = collections.Counter()
        for s in sub:
            w = ["<s>"] + _tok(s) + ["</s>"]; uni.update(w[1:]); bi.update(zip(w, w[1:]))
        for (a, b), c in bi.items(): ctx1[a] += c
        rows.append({"training messages": len(sub), "words seen": sum(uni.values()), "bigram parameters (pairs stored)": len(bi), "test perplexity": _bigram_pp(te["text"], uni, bi, ctx1)})
    sizes = pd.DataFrame([{"model": "GPT-2 small (2019)", "parameters": "124 million"}, {"model": "GPT-2 XL (2019)", "parameters": "1.5 billion"}, {"model": "GPT-3 (2020)", "parameters": "175 billion"}, {"model": "Llama 3 (2024)", "parameters": "8 / 70 / 405 billion"}])
    return [
        ("An LLM is a next-token predictor", "Exactly like our SMS language model, but a transformer with billions of weights, trained on trillions of tokens, with thousands of tokens of context."),
        ("More data → better predictions (on real SMS)", f"{t(pd.DataFrame(rows), nd=1)}\n\n{"Perplexity falls steadily as data grows." if all(a["test perplexity"] > b["test perplexity"] for a, b in zip(rows, rows[1:])) else "Perplexity mostly falls as data grows."} The same trend, followed over many orders of magnitude of data and model size, is the 'scaling law' that drove LLMs."),
        ("Scale of real models", f"{t(sizes)}\n\nAfter pre-training, LLMs are instruction-tuned and aligned with human feedback so they follow requests instead of just continuing text."),
    ], "LLMs are giant next-token predictors; more data and parameters steadily lower their prediction error, which unlocks new abilities."


def _prompt_msgs(msgs):
    return [{"role": "system", "content": "You label SMS messages as spam or ham. Reply with JSON: {\"label\": \"spam\"|\"ham\", \"reason\": \"<10 words\"}."},
            {"role": "user", "content": "Messages:\n" + "\n".join(f"{i + 1}. {m}" for i, m in enumerate(msgs))}]


@walk("m-llm-api", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    tr, te = _split(); msgs = te["text"].head(3).tolist()
    req = {"model": "<model-name>", "max_tokens": 200, "temperature": 0, "messages": _prompt_msgs(msgs)}
    tk = _bpe(5000)
    n_in = sum(len(tk.encode(m["content"]).ids) for m in req["messages"])
    vec = TfidfVectorizer(sublinear_tf=True); clf = LogisticRegression(max_iter=2000, C=10).fit(vec.fit_transform(tr["text"]), tr["label"])
    pr = clf.predict_proba(vec.transform(msgs))[:, 1]
    resp = [{"label": "spam" if p > 0.5 else "ham", "reason": "local stand-in model"} for p in pr]
    parsed = pd.DataFrame({"message": [_short(m, 50) for m in msgs], "parsed label": [r["label"] for r in resp], "true label": te["label"].head(3).values})
    return [
        ("Build the request", f"An API call is an HTTPS POST with JSON. For 3 real test messages:\n\n```json\n{json.dumps(req, indent=1)[:700]}\n```\n\nThe API key goes in a header from an environment variable, never in code."),
        ("Count tokens = cost and limits", f"With a BPE tokenizer trained on SMS, this request is about **{n_in}** input tokens. Providers charge per million input and output tokens and limit tokens per minute, so: batch messages, keep prompts short, set max_tokens, cache repeated prompts."),
        ("Parse and validate the reply", f"Ask for JSON, then parse and check it before trusting it. Here a local spam model stands in for the LLM's reply (no network calls from this course):\n\n{t(parsed)}\n\nAlso handle errors: retry with backoff on rate limits (HTTP 429) and timeouts."),
    ], "Calling an LLM API = build a JSON request, watch token counts, then parse and validate the structured reply."


@walk("m-prompt-engineering", "sms")
def _():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    tr, te = _split(); q = te[te.label == "spam"]["text"].iloc[1]
    vec = TfidfVectorizer().fit(tr["text"]); s = cosine_similarity(vec.transform([q]), vec.transform(tr["text"]))[0]
    idx = np.argsort(-s)[:3]
    shots = tr.iloc[idx]
    zero = f"Is this SMS spam or ham?\n{q}"
    few = "Label each SMS as spam or ham.\n\n" + "\n\n".join(f"SMS: {_short(r.text, 90)}\nLabel: {r.label}" for r in shots.itertuples()) + f"\n\nSMS: {_short(q, 90)}\nLabel:"
    structured = "You are a careful spam filter for a mobile carrier.\nRules: spam = unsolicited marketing, prizes, premium-rate numbers. Personal messages are ham even if they mention money.\nThink step by step, then answer ONLY with JSON {\"label\": ..., \"evidence\": [words from the message]}.\n\nSMS: " + _short(q, 90)
    return [
        ("Zero-shot", f"Just ask:\n\n```\n{zero}\n```\n\nWorks for easy cases, but the output format and the definition of 'spam' are left to the model."),
        ("Few-shot with retrieved examples", f"Show labelled examples, picked as the 3 training messages most similar to the new one (TF-IDF cosine {', '.join(f'{v:.2f}' for v in s[idx])}; spam campaigns reuse templates, so near-copies are common):\n\n```\n{few}\n```"),
        ("Role, rules, reasoning, format", f"```\n{structured}\n```\n\nClear criteria, a fixed output format and room to reason usually help most. Always test prompt versions on a labelled sample (like our test set) instead of judging by one example."),
    ], "Prompt engineering = giving the model the task definition, good examples and an exact output format, then measuring which version works best."


@walk("m-embeddings-vectordb", "sms")
def _():
    import faiss, time
    df, vec, svd, E = _lsa()
    idx = faiss.IndexFlatIP(E.shape[1]); idx.add(E.astype(np.float32))
    q = "you have won a free prize, call now to claim"
    qe = svd.transform(vec.transform([q])).astype(np.float32); qe /= np.linalg.norm(qe)
    D_, I = idx.search(qe, 4)
    res = pd.DataFrame({"similarity": D_[0], "label": df["label"].values[I[0]], "message": [_short(df["text"].values[i]) for i in I[0]]})
    q2 = "sorry i will be late, stuck in traffic"
    hnsw = faiss.IndexHNSWFlat(E.shape[1], 16); hnsw.add(E.astype(np.float32))
    _, I1 = idx.search(E[:200].astype(np.float32), 5); _, I2 = hnsw.search(E[:200].astype(np.float32), 5)
    recall = np.mean([len(set(a) & set(b)) / 5 for a, b in zip(I1, I2)])
    return [
        ("Turn every message into a vector", f"TF-IDF + SVD (LSA) gives each of the {len(df):,} messages a {E.shape[1]}-number embedding, normalised to length 1. Similar meaning → similar direction. (Neural embedding models do this better; the steps are the same.)"),
        ("Store and search", f"A FAISS index holds all vectors. Query “{q}”:\n\n{t(res, nd=2)}\n\nQuery “{q2}”:\n\n{t(_search(q2, 3), nd=2)}"),
        ("Approximate search for scale", f"With millions of vectors, exact search is slow, so vector databases use approximate indexes. An HNSW graph index here finds **{pct(recall)}** of the exact top-5 neighbours for 200 queries, much faster at large scale."),
    ], "A vector database stores embeddings and finds the nearest ones to a query, exactly or approximately."


@walk("m-rag", "sms")
def _():
    df, vec, svd, E = _lsa()
    q = "What do spam texts promise people to get them to reply?"
    hits = _search("won prize claim cash award reply call", 5)
    prize = df["text"][df["label"] == "spam"].str.extract(r"(£\s?\d[\d,]*)")[0].dropna()
    ctx = "\n".join(f"[{i + 1}] {m}" for i, m in enumerate(hits["message"]))
    prompt = f"Answer using ONLY the sources below and cite them like [1].\nQuestion: {q}\nSources:\n{ctx}"
    return [
        ("1. Retrieve", f"Question: “{q}”. Search the SMS collection (vector search):\n\n{t(hits, nd=2)}"),
        ("2. Augment the prompt", f"```\n{prompt}\n```"),
        ("3. Generate, grounded in the sources", f"The LLM writes an answer from these sources with citations (e.g. 'They promise cash or prizes and ask you to call a number [1][2]'). Check against the data: {prize.size} spam messages mention a £ amount, most often {', '.join(prize.str.replace(' ', '').value_counts().index[:3])}. If retrieval misses the right messages, the answer will be wrong however good the LLM is."),
    ], "RAG retrieves relevant documents, pastes them into the prompt and asks the model to answer from them with citations."


@walk("m-langchain", "sms")
def _():
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    df = _sms()
    doc = "\n".join(df["text"].head(40))
    sp = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = sp.split_text(doc)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    v = TfidfVectorizer().fit(chunks); q = "free entry competition"
    s = cosine_similarity(v.transform([q]), v.transform(chunks))[0]; best = int(s.argmax())
    from langchain_core.prompts import ChatPromptTemplate
    tmpl = ChatPromptTemplate.from_messages([("system", "Answer from the context only."), ("human", "Context:\n{context}\n\nQuestion: {question}")])
    msgs = tmpl.format_messages(context=_short(next((ln for ln in chunks[best].splitlines() if any(w in ln.lower() for w in q.split())), chunks[best]), 160), question="What competition is mentioned?")
    return [
        ("Load and split", f"40 real messages joined into one document ({len(doc):,} characters). `RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)` cuts it into **{len(chunks)}** chunks, splitting at line breaks first so messages stay whole; neighbouring chunks overlap by up to 50 characters."),
        ("Embed and retrieve", f"Each chunk is embedded and stored; the retriever returns the best chunk for “{q}” (chunk {best + 1} of {len(chunks)}, similarity {s[best]:.2f}). Its matching line: “{_short(next((ln for ln in chunks[best].splitlines() if any(w in ln.lower() for w in q.split())), chunks[best]), 120)}”"),
        ("Prompt template → model → parser", f"`ChatPromptTemplate` fills the slots:\n\n" + "\n".join(f"- **{m.type}**: {_short(m.content.replace(chr(10), ' '), 150)}" for m in msgs) + "\n\nIn LangChain these pieces are chained as `retriever | prompt | llm | parser`; each is a step you could also write by hand."),
    ], "LangChain packages the usual LLM-app steps (load, split, embed, retrieve, prompt, call, parse) as composable components."
