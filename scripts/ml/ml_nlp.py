"""Module 3: NLP — text processing, representations, embeddings, attention, transformers, BERT/GPT/T5,
Hugging Face, fine-tuning, LLMs, APIs, prompting, vector search, RAG, LangChain."""
from ml_util import M

TINY_TOK = '''
from tokenizers import Tokenizer, models, trainers, pre_tokenizers
from transformers import PreTrainedTokenizerFast
def tiny_tokenizer(corpus, vocab=200):
    """Offline stand-in for AutoTokenizer.from_pretrained(...): trains a WordPiece tokenizer on our corpus."""
    tok = Tokenizer(models.WordPiece(unk_token="[UNK]")); tok.pre_tokenizer = pre_tokenizers.Whitespace()
    tok.train_from_iterator(corpus, trainers.WordPieceTrainer(vocab_size=vocab, special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]))
    return PreTrainedTokenizerFast(tokenizer_object=tok, pad_token="[PAD]", unk_token="[UNK]", cls_token="[CLS]", sep_token="[SEP]", mask_token="[MASK]")
'''

NLP = [
M("m-nlp-tasks", "Natural language processing: the main tasks and how they're solved today", "Basic",
  "NLP teaches computers to read, understand and generate human language. Most tasks are now solved by fine-tuning or prompting pretrained transformers, but classical pipelines remain useful baselines.",
  """|Task|Example|Classical approach|Modern approach|
|Text classification|sentiment, spam, topic, intent|TF-IDF + logistic regression / Naive Bayes|fine-tuned BERT; LLM zero-shot|
|Token classification|named entity recognition (NER), part-of-speech (POS) tagging|CRF, HMM|BERT token classifier|
|Sentence-pair tasks|duplicate questions (Quora), entailment (NLI), similarity|feature engineering + GBM|cross-encoder / Siamese sentence-transformers|
|Question answering|extract answer span; open-domain QA|IR + rules|BERT span QA; RAG with LLMs|
|Summarisation|news, meeting notes|extractive (TextRank)|BART/T5/LLMs (abstractive)|
|Machine translation|English → Hindi|phrase-based statistical MT|transformer seq2seq, LLMs|
|Text generation / dialogue|chatbots, code|n-gram, rules|GPT-style LLMs|
|Information extraction|invoices, resumes → structured fields|regex + rules|LLM with structured output|
|Topic modelling|themes in reviews|LDA, NMF|BERTopic (embeddings + clustering)|
|Search / retrieval|semantic search|BM25|dense embeddings, hybrid search, re-rankers|

### Why language is hard
Ambiguity ("bank"), context, sarcasm, long-range dependencies, many languages and code-mixing (Hinglish), spelling noise, world knowledge.""",
  code="""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
intents = [("what's my account balance", "balance"), ("how much money do I have", "balance"), ("send 500 to mom", "transfer"),
           ("transfer money to my brother", "transfer"), ("block my debit card", "card"), ("i lost my credit card", "card"),
           ("show balance please", "balance"), ("pay rahul 200 rupees", "transfer"), ("card stolen help", "card")]
clf = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000)).fit(*zip(*intents))
for q in ["how much is in my account", "my card is missing", "send money to priya"]:
    print(f"{q!r:32s} -> intent: {clf.predict([q])[0]}")
""",
  say=[("How would you approach a new text classification problem today?",
        "\"Start with a fast baseline — TF-IDF with logistic regression — to understand the data and get a reference score. Then try an LLM zero- or few-shot to see how far prompting gets, and if I have a few thousand labels, fine-tune a small transformer like DistilBERT or DeBERTa, which is usually the best accuracy-cost trade-off for production. The choice depends on labels available, latency, cost and privacy.\"")]),

M("m-text-preprocessing", "Text preprocessing with NLTK and spaCy: tokenisation, stop words, stemming, lemmatisation, POS, NER", "Basic",
  "Before classical NLP models can use text, it is cleaned and split into tokens, often lower-cased, with stop words removed and words reduced to base forms.",
  """### Steps (choose what your task needs)
1. **Cleaning**: lowercase, remove HTML, URLs, emojis (or map them), normalise unicode, expand contractions.
2. **Tokenisation**: split into words/sentences (`nltk.word_tokenize`, `sent_tokenize`, spaCy). Transformers use **subword** tokenisers instead.
3. **Stop-word removal**: drop very common words (the, is, and) — helps bag-of-words models, hurts sentiment if you drop "not"!
4. **Stemming**: chop suffixes with rules (Porter: "studies" → "studi") — fast, crude.
5. **Lemmatisation**: dictionary-based base form ("studies" → "study", "better" → "good" with POS) — accurate, slower.
6. **POS tagging** (noun, verb…), **NER** (person, organisation, location, date), dependency parsing.
7. **Regular expressions** for patterns: emails, phone numbers, amounts.

### Libraries
**NLTK** (teaching, classic algorithms, corpora — run `nltk.download(...)` once in Colab), **spaCy** (fast industrial pipelines, `en_core_web_sm`), Hugging Face tokenizers, `re`.

### Modern note
For transformer models, do minimal preprocessing — the model's tokenizer handles text and the model needs stop words and punctuation for context.""",
  code="""
import re, nltk
for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "averaged_perceptron_tagger_eng", "maxent_ne_chunker_tab", "words"]:
    nltk.download(pkg, quiet=True)
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
text = "Dr. Asha Rao joined Infosys in Bengaluru on 3 March 2024. She isn't happy with the studies she's running! Mail: asha.rao@example.com"
print("sentences:", nltk.sent_tokenize(text))
tokens = nltk.word_tokenize(text.lower()); print("tokens:", tokens[:12])
stops = set(stopwords.words("english")) - {"not", "no", "nor"}
content = [t for t in tokens if t.isalpha() and t not in stops]; print("without stop words:", content)
stem, lem = PorterStemmer(), WordNetLemmatizer()
for w in ["studies", "running", "happier", "better"]:
    print(f"{w:8s} stem={stem.stem(w):7s} lemma(verb)={lem.lemmatize(w, 'v'):7s} lemma(adj)={lem.lemmatize(w, 'a')}")
tagged = nltk.pos_tag(nltk.word_tokenize(text)); print("POS:", tagged[:6])
tree = nltk.ne_chunk(tagged); print("named entities:", [(" ".join(w for w, _ in st.leaves()), st.label()) for st in tree.subtrees() if st.label() != "S"])
print("emails via regex:", re.findall(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+", text))
""",
  say=[("Stemming or lemmatisation?",
        "\"Stemming chops suffixes with rules — fast but can produce non-words like 'studi'. Lemmatisation uses a vocabulary and part of speech to return the dictionary form — 'studies' becomes 'study', 'better' becomes 'good' — more accurate but slower. For search and bag-of-words baselines stemming is often fine; for anything user-facing or where meaning matters I'd lemmatise. With transformers I'd skip both.\"")]),

M("m-web-scraping", "Web scraping and text data collection", "Basic",
  "Web scraping downloads web pages and extracts the text or data you need — reviews, prices, articles, tweets — to build datasets. Do it legally and politely.",
  """### Tools
- **requests** (download HTML) + **BeautifulSoup** (parse and select elements with CSS selectors).
- **Scrapy** for large crawls; **Selenium / Playwright** when content is rendered by JavaScript.
- **APIs first**: official APIs (X/Twitter, Reddit, news APIs) are more stable and legal than scraping. Use `pandas.read_html` for HTML tables.

### Workflow
1. Inspect the page (browser dev tools) to find the HTML structure.
2. Fetch with a timeout and a descriptive User-Agent; handle errors and pagination.
3. Parse and extract fields; clean text; store as CSV/JSON/database.
4. Respect **robots.txt**, terms of service, rate limits (sleep between requests), copyright and personal-data laws (GDPR, India's DPDP Act). Never scrape behind logins without permission.

### For real-time tweet analytics (capstone)
Stream posts through the platform API → clean (handles, hashtags, URLs, emojis) → sentiment/topic models → aggregate over time windows → dashboard.""",
  code="""
from bs4 import BeautifulSoup
import pandas as pd
html = '''<html><body><h1>Phone reviews</h1>
<div class="review"><span class="user">Ravi</span><span class="stars">5</span><p>Battery lasts two days, love it!</p></div>
<div class="review"><span class="user">Meera</span><span class="stars">2</span><p>Camera is <b>blurry</b> at night.</p></div>
<div class="review"><span class="user">Imran</span><span class="stars">4</span><p>Good value. Charging is fast.</p></div>
<a href="/reviews?page=2">next</a></body></html>'''
# Online you would do:  html = requests.get(url, headers={"User-Agent": "study-bot"}, timeout=10).text
soup = BeautifulSoup(html, "html.parser")
rows = [{"user": r.select_one(".user").text, "stars": int(r.select_one(".stars").text), "text": r.p.get_text(" ", strip=True)} for r in soup.select("div.review")]
df = pd.DataFrame(rows); print(df); print("next page link:", soup.find("a", string="next")["href"])
print("average rating:", df["stars"].mean().round(2))
""",
  say=[("What do you check before scraping a website for training data?",
        "\"Whether there's an official API or dataset first; the site's terms of service and robots.txt; copyright and whether the content includes personal data, which brings privacy law into play; and then I scrape politely — rate limits, caching, identifying user agent — and document the data's source and licence for the model card.\"")]),

M("m-text-representation", "Representing text: bag of words, n-grams, TF-IDF, one-hot", "Basic",
  "Models need numbers, so text is turned into vectors. Bag-of-words counts words, n-grams keep short phrases, and TF-IDF up-weights words that are distinctive for a document.",
  """### One-hot and bag of words (BoW)
Build a vocabulary; a document = vector of word counts (or 0/1). Ignores order ("dog bites man" = "man bites dog"), sparse and high-dimensional, but strong for classification.

### n-grams
Include sequences of n words ("not good", "new york") to capture some order. Character n-grams handle typos and morphology.

### TF-IDF
**tf-idf(t, d) = tf(t, d) × log(N / df(t))** (+ smoothing). Words frequent in this document but rare across the corpus score high; "the" scores ~0. Rows are usually L2-normalised so **cosine similarity** compares documents. Behind classic search engines and the BM25 ranking function.

### Limitations → embeddings
No notion of meaning ("car" and "automobile" are unrelated dimensions), vocabulary explosion, out-of-vocabulary words. **Dense embeddings** (word2vec, BERT) fix this.

### Practical
scikit-learn `CountVectorizer` / `TfidfVectorizer` (`ngram_range`, `min_df`, `max_df`, `max_features`, `sublinear_tf`); `HashingVectorizer` for streams; keep matrices sparse.""",
  code="""
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
docs = ["the movie was good", "the movie was not good", "the film was great fun", "stock markets fell sharply today"]
bow = CountVectorizer(); B = bow.fit_transform(docs)
print("vocabulary:", list(bow.get_feature_names_out())); print("bag of words:\\n", B.toarray())
bi = CountVectorizer(ngram_range=(1, 2)).fit(docs); print("with bigrams, e.g.:", [f for f in bi.get_feature_names_out() if " " in f][:5])
tfidf = TfidfVectorizer(); T = tfidf.fit_transform(docs)
row = dict(zip(tfidf.get_feature_names_out(), T.toarray()[1].round(2))); print("tf-idf of doc 2:", {k: v for k, v in row.items() if v})
print("cosine similarity matrix:\\n", cosine_similarity(T).round(2))
""",
  say=[("What's the weakness of TF-IDF compared with embeddings?",
        "\"TF-IDF treats every word as an independent dimension, so synonyms like 'car' and 'automobile' have zero similarity, word order and context are mostly lost, and unseen words are ignored. It's still a fast, strong baseline for classification and keyword search, and hybrid search often combines BM25 with dense embeddings to get the best of both.\"")]),

M("m-word-embeddings", "Word embeddings: word2vec, GloVe, fastText", "Intermediate",
  "Word embeddings map each word to a dense vector (e.g. 300 numbers) so that words used in similar contexts get similar vectors — capturing meaning, synonyms and analogies.",
  """### Distributional hypothesis
"You shall know a word by the company it keeps" — words appearing in similar contexts have similar meanings.

### word2vec (Mikolov et al., 2013)
A shallow network trained on a fake task: **Skip-gram** predicts context words from the centre word; **CBOW** predicts the centre from context. Negative sampling makes it fast. The learned weights are the embeddings.
Famous property: **king − man + woman ≈ queen**.

### GloVe
Factorises the global word co-occurrence matrix — similar results.

### fastText
Represents words as sums of character n-grams ⇒ handles rare and misspelled words and rich morphology (useful for Indian languages).

### Limitations → contextual embeddings
One vector per word regardless of context ("bank" of a river vs money). **ELMo** and then **BERT** produce contextual embeddings that change with the sentence. Embedding ideas live on in every transformer's input layer, recommendation systems (item2vec) and graph embeddings (node2vec).""",
  demo="embed",
  code="""
from gensim.models import Word2Vec, FastText
import numpy as np
royal = ["the king rules the kingdom", "the queen rules the kingdom", "the prince is the son of the king", "the princess is the daughter of the queen",
         "a man and a woman walk", "the man is a king", "the woman is a queen", "the boy will be a man", "the girl will be a woman",
         "the king and the man are male", "the queen and the woman are female", "the prince and the boy are male", "the princess and the girl are female"]
stop = {"the", "a", "is", "and", "are", "will", "be", "of"}
sents = [[w for w in s.split() if w not in stop] for s in royal] * 300          # drop stop words so content words drive similarity
w2v = Word2Vec(sents, vector_size=30, window=3, min_count=1, sg=1, negative=5, epochs=5, seed=0, workers=1)
print("vector size:", w2v.wv["king"].shape)
print("most similar to 'king':", [w for w, _ in w2v.wv.most_similar("king", topn=3)])
print("king - man + woman =", w2v.wv.most_similar(positive=["king", "woman"], negative=["man"], topn=2))
print("similarity(boy, girl) =", round(float(w2v.wv.similarity("boy", "girl")), 2), " similarity(boy, kingdom) =", round(float(w2v.wv.similarity("boy", "kingdom")), 2))
ft = FastText(sents, vector_size=30, window=3, min_count=1, epochs=5, seed=0, workers=1)
print("fastText handles an unseen misspelling 'kingg':", [w for w, _ in ft.wv.most_similar("kingg", topn=2)])
# Pretrained vectors online: import gensim.downloader as api; glove = api.load("glove-wiki-gigaword-100")
""",
  say=[("What's the difference between word2vec embeddings and BERT embeddings?",
        "\"word2vec gives each word one fixed vector learned from co-occurrence, so 'bank' has the same vector in 'river bank' and 'bank loan'. BERT produces contextual embeddings: each token's vector is computed by a transformer from the whole sentence, so the same word gets different vectors in different contexts. BERT also uses subword tokens, so it handles unseen words.\"")]),

M("m-text-classification", "Text classification and sentiment analysis", "Basic",
  "Sentiment analysis classifies text as positive, negative or neutral. It's the 'hello world' of NLP with approaches from lexicons to fine-tuned transformers.",
  """### Approaches, simplest first
1. **Lexicon / rule-based**: VADER (social media, handles emojis, "!!!", negation) — no training data.
2. **Classical ML**: TF-IDF (word + character n-grams) → logistic regression / linear SVM / Naive Bayes. Fast, interpretable, strong.
3. **Embeddings + classifier**: average word vectors or sentence embeddings → logistic regression.
4. **Fine-tuned transformer**: DistilBERT/RoBERTa/DeBERTa, multilingual (XLM-R, MuRIL for Indian languages). Best accuracy with a few thousand labels.
5. **LLM zero/few-shot** prompting — no labels needed, higher cost/latency.

### Challenges
Negation ("not bad"), sarcasm, aspect-based sentiment ("great camera, terrible battery"), domain shift, class imbalance, code-mixed text.

### Evaluation
Macro-F1, confusion matrix; inspect errors.""",
  code="""
import nltk; nltk.download("vader_lexicon", quiet=True)
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union
from sklearn.model_selection import cross_val_score
vader = SentimentIntensityAnalyzer()
for t in ["The food was good.", "The food was not good.", "The food was GOOD!!! :)", "Great camera but terrible battery"]:
    print(f"{t:36s} VADER compound={vader.polarity_scores(t)['compound']:+.2f}")
pos = ["loved it", "great acting and story", "brilliant film, must watch", "really enjoyable", "not bad at all, quite good", "superb music", "wonderful and moving", "best movie this year"]
neg = ["hated it", "boring and too long", "worst film ever", "not good at all", "terrible acting", "waste of money", "awful script, dull", "fell asleep, so boring"]
X, y = pos * 5 + neg * 5, [1] * 40 + [0] * 40
model = make_pipeline(make_union(TfidfVectorizer(ngram_range=(1, 2)), TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))), LogisticRegression(max_iter=1000))
print("TF-IDF (word + char n-grams) + logistic regression CV accuracy:", cross_val_score(model, X, y, cv=5).mean())
model.fit(X, y); tests = ["what a brilliant story", "so dull and boring", "not good"]
print("predictions:", {t: int(p) for t, p in zip(tests, model.predict(tests))})
""",
  say=[("How would you handle negation in a bag-of-words sentiment model?",
        "\"Keep negation words — don't drop 'not' with the stop words — and add bigrams so 'not good' becomes its own feature; a classic trick also marks words after a negation, like 'not good_NEG'. Character n-grams help with variations. Transformers handle negation much better because they model context, so if negation errors dominate I'd move to a fine-tuned transformer.\"")]),

M("m-language-models", "Language models, n-grams, perplexity and text generation", "Intermediate",
  "A language model assigns probabilities to sequences of words — P(next word | previous words). Generating text means repeatedly sampling the next word. LLMs are giant neural language models.",
  """### Chain rule
P(w₁…wₙ) = Π P(wᵢ | w₁…wᵢ₋₁). Every LM approximates these conditional probabilities.

### n-gram models
Markov assumption: only the last n − 1 words matter. Estimate by counting; **smoothing** (add-one/Laplace, Kneser–Ney) handles unseen n-grams; backoff/interpolation combine orders. Simple but sparse and short memory.

### Neural LMs
Embeddings + RNN/LSTM (2010s) → **transformer decoders** (GPT): predict the next token over a context of thousands of tokens.

### Perplexity
PPL = exp(average negative log-likelihood per token) — "effective number of choices"; lower is better. Compare only with the same tokenizer and test set.

### Generation (decoding)
Greedy, beam search, sampling with temperature, top-k, top-p — see the decoding card.

### Applications
Autocomplete, spelling correction, speech recognition rescoring, machine translation, and every chatbot.""",
  code="""
import math, random
from collections import Counter, defaultdict
corpus = ("i like machine learning . i like deep learning . deep learning is fun . machine learning is useful . "
          "i like to learn . learning is fun .").split()
bigrams = Counter(zip(corpus, corpus[1:])); unigrams = Counter(corpus); V = len(unigrams)
def p(w2, w1, k=1.0): return (bigrams[(w1, w2)] + k) / (unigrams[w1] + k * V)        # add-k (Laplace) smoothing
def perplexity(sentence):
    toks = sentence.split(); nll = -sum(math.log(p(b, a)) for a, b in zip(toks, toks[1:])); return math.exp(nll / (len(toks) - 1))
for s in ["i like deep learning .", "learning like i deep ."]:
    print(f"perplexity {perplexity(s):6.2f}  <- {s!r}")
nxt = defaultdict(Counter)
for a, b in bigrams: nxt[a][b] = bigrams[(a, b)]
random.seed(3); w, out = "i", ["i"]
for _ in range(8):
    words, counts = zip(*nxt[w].items()); w = random.choices(words, weights=counts)[0]; out.append(w)
print("sampled text:", " ".join(out))
""",
  say=[("What is perplexity?",
        "\"It's the exponential of the average negative log-likelihood the model assigns to each token in held-out text — intuitively, how many equally likely choices the model is torn between at each step. Lower is better. It's only comparable between models using the same tokenizer and test data, and low perplexity doesn't guarantee helpful or truthful outputs.\"")]),

M("m-topic-models", "Topic modelling: LDA, NMF and BERTopic", "Intermediate",
  "Topic models discover themes in a collection of documents without labels — each topic is a group of words that tend to appear together, and each document is a mix of topics.",
  """- **LDA (latent Dirichlet allocation)**: a generative model — each document is a mixture of topics, each topic a distribution over words; fitted with variational inference or Gibbs sampling on bag-of-words counts.
- **NMF (non-negative matrix factorisation)**: factorise the TF-IDF matrix into document–topic × topic–word matrices; often crisper topics.
- **BERTopic**: sentence embeddings → UMAP → HDBSCAN clustering → class-based TF-IDF for topic words — better on short texts like tweets and reviews.
- Choose the number of topics with coherence scores and human judgement.
- Uses: understanding customer feedback, tweet trends, research literature, routing support tickets.""",
  code="""
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
docs = ["the batsman hit a century in the cricket match", "the bowler took five wickets in the test match", "cricket fans cheered the winning team",
        "the stock market rallied as shares rose", "investors sold shares after the market fell", "the bank raised interest rates for investors",
        "the team won the match by six wickets", "shares and bonds fell as rates rose"]
cv = CountVectorizer(stop_words="english"); X = cv.fit_transform(docs)
lda = LatentDirichletAllocation(n_components=2, random_state=0).fit(X); words = cv.get_feature_names_out()
for k, comp in enumerate(lda.components_): print(f"LDA topic {k}:", [words[i] for i in comp.argsort()[::-1][:5]])
print("topic mix of doc 0:", lda.transform(X[:1]).round(2))
tf = TfidfVectorizer(stop_words="english"); T = tf.fit_transform(docs); nmf = NMF(2, random_state=0, init="nndsvd").fit(T)
for k, comp in enumerate(nmf.components_): print(f"NMF topic {k}:", [tf.get_feature_names_out()[i] for i in comp.argsort()[::-1][:5]])
""",
  say=[("How would you find the main complaints in 100,000 customer reviews?",
        "\"Filter to negative reviews with a sentiment model, then run topic modelling — BERTopic on sentence embeddings works well for short reviews, or NMF on TF-IDF as a fast baseline — and label the topics with their top words and example reviews. An LLM can summarise each cluster. Then track topic volumes over time to spot new issues.\"")]),

M("m-attention", "Attention: scaled dot-product, self-attention, multi-head attention, masking", "Advanced",
  "Attention lets each token look at every other token and take a weighted mix of their information, with weights computed from how relevant they are. It is the core operation of transformers.",
  """### Queries, keys and values
Each token's vector x is projected into a **query** q = xW_Q (what am I looking for?), a **key** k = xW_K (what do I contain?) and a **value** v = xW_V (what do I pass on?).

### Scaled dot-product attention
**Attention(Q, K, V) = softmax(QKᵀ / √d_k) V**
- QKᵀ: similarity of every query with every key (an n × n matrix).
- ÷ √d_k keeps scores from growing with dimension (otherwise softmax saturates).
- softmax → weights summing to 1 per query; multiply by V → context-aware output.

### Self-attention vs cross-attention
Self: Q, K, V from the same sequence. Cross: queries from the decoder, keys/values from the encoder (translation, image captioning, RAG-style fusion).

### Masking
**Causal mask** hides future tokens in decoders (GPT can't peek at the answer). **Padding mask** ignores pad tokens.

### Multi-head attention
Run h attention heads in parallel on smaller projections (d_model/h each); different heads learn different relations (syntax, coreference, position); concatenate and project.

### Cost
O(n²) time and memory in sequence length → long-context tricks: FlashAttention (exact, IO-aware), sparse/sliding-window attention, linear attention, KV caching at inference.""",
  demo="attention",
  code="""
import torch, torch.nn.functional as F, math
torch.manual_seed(0)
def attention(Q, K, V, mask=None):
    scores = Q @ K.transpose(-2, -1) / math.sqrt(Q.size(-1))
    if mask is not None: scores = scores.masked_fill(mask == 0, float("-inf"))
    w = torch.softmax(scores, dim=-1); return w @ V, w
tokens = ["the", "cat", "sat", "down"]; d = 8
X = torch.randn(4, d); Wq, Wk, Wv = (torch.randn(d, d) / math.sqrt(d) for _ in range(3))
out, w = attention(X @ Wq, X @ Wk, X @ Wv)
print("attention weights (rows = queries, sum to 1):\\n", w.detach().numpy().round(2))
causal = torch.tril(torch.ones(4, 4)); _, wc = attention(X @ Wq, X @ Wk, X @ Wv, causal)
print("causal mask -> 'sat' can attend to:", {t: round(v, 2) for t, v in zip(tokens, wc[2].tolist())})
ref = F.scaled_dot_product_attention((X @ Wq)[None], (X @ Wk)[None], (X @ Wv)[None])
print("matches torch's fused attention:", torch.allclose(ref[0], out, atol=1e-5))
mha = torch.nn.MultiheadAttention(embed_dim=8, num_heads=2, batch_first=True)
o, aw = mha(X[None], X[None], X[None]); print("multi-head output", tuple(o.shape), "weights", tuple(aw.shape))
""",
  say=[("Why divide by the square root of d_k in attention?",
        "\"Dot products of random vectors grow in magnitude with their dimension — the variance is about d_k. Large scores push softmax into saturation where one weight is nearly 1 and gradients are tiny. Dividing by root d_k keeps the scores at unit variance so the softmax stays in a range where it can learn.\"")]),

M("m-transformer", "The transformer architecture", "Advanced",
  "The transformer (2017) replaced recurrence with attention: every token attends to every other token in parallel. Stacked blocks of attention + feed-forward layers with residuals and normalisation power BERT, GPT, ViT and Whisper.",
  """### Building blocks
1. **Token embeddings** + **positional information** (sinusoidal or learned absolute positions; modern LLMs use **RoPE** rotary embeddings or ALiBi) — attention alone has no sense of order.
2. **Encoder block** ×N: multi-head self-attention → add & LayerNorm → position-wise feed-forward network (two linear layers, 4× width, GELU/SwiGLU) → add & LayerNorm.
3. **Decoder block** ×N: *masked* self-attention → cross-attention to encoder output → feed-forward.
4. Output linear layer + softmax over the vocabulary.
Modern models use **pre-LayerNorm** (normalise before each sub-layer) for stable deep training.

### Why it won
Parallel training over all positions (RNNs are sequential); direct paths between any two tokens (long-range dependencies); scales predictably with data and compute (scaling laws).

### Three families
Encoder-only (BERT — understanding), decoder-only (GPT, Llama, Claude — generation), encoder–decoder (T5, BART, Whisper — transformation).

### Sizes
BERT-base: 12 layers, d_model 768, 12 heads, 110M params. GPT-3: 96 layers, 12,288 dims, 175B. Parameter count ≈ 12 × layers × d_model².""",
  code="""
import torch, torch.nn as nn, math
torch.manual_seed(0)
class PositionalEncoding(nn.Module):
    def __init__(self, d, max_len=512):
        super().__init__(); pos = torch.arange(max_len)[:, None]; div = torch.exp(torch.arange(0, d, 2) * (-math.log(10000.0) / d))
        pe = torch.zeros(max_len, d); pe[:, 0::2] = torch.sin(pos * div); pe[:, 1::2] = torch.cos(pos * div); self.register_buffer("pe", pe)
    def forward(self, x): return x + self.pe[: x.size(1)]
class TransformerClassifier(nn.Module):
    def __init__(self, vocab, d=64, heads=4, layers=2, classes=2):
        super().__init__(); self.emb = nn.Embedding(vocab, d); self.pos = PositionalEncoding(d)
        block = nn.TransformerEncoderLayer(d, heads, dim_feedforward=4 * d, batch_first=True, norm_first=True, activation="gelu")
        self.enc = nn.TransformerEncoder(block, layers); self.cls = nn.Linear(d, classes)
    def forward(self, ids, pad_mask): return self.cls(self.enc(self.pos(self.emb(ids)), src_key_padding_mask=pad_mask).mean(1))
# task: does token 7 appear BEFORE token 3? (order matters, so positions are essential)
def make(n, L=12):
    ids = torch.randint(10, 30, (n, L)); y = torch.randint(0, 2, (n,))
    for i in range(n):
        a, b = sorted(torch.randperm(L)[:2].tolist()); ids[i, a], ids[i, b] = (7, 3) if y[i] else (3, 7)
    return ids, y
X, y = make(3000); model = TransformerClassifier(30); opt = torch.optim.AdamW(model.parameters(), 1e-3); pad = torch.zeros_like(X, dtype=torch.bool)
for ep in range(6):
    for i in range(0, 2500, 100):
        opt.zero_grad(); nn.functional.cross_entropy(model(X[i:i + 100], pad[i:i + 100]), y[i:i + 100]).backward(); opt.step()
model.eval()
with torch.no_grad(): print("order-sensitive task accuracy:", round((model(X[2500:], pad[2500:]).argmax(1) == y[2500:]).float().mean().item(), 3))
print("parameters:", sum(p.numel() for p in model.parameters()))
""",
  say=[("What advantages do transformers have over RNNs?",
        "\"They process all tokens in parallel during training instead of one step at a time, so they use GPUs efficiently and scale to huge data. Attention connects any two positions directly, so long-range dependencies don't have to survive many recurrent steps — no vanishing gradients through time. The downside is quadratic cost in sequence length, which long-context techniques address.\"")]),

M("m-tokenization", "Subword tokenisation: BPE, WordPiece, SentencePiece, tokens and context windows", "Intermediate",
  "Transformers read text as tokens — usually subword pieces, not whole words. Tokenisation decides vocabulary size, how rare words are handled and how many tokens (and dollars) your text costs.",
  """### Why subwords
Word-level vocabularies explode and can't handle unseen words; character-level sequences are too long. Subwords: frequent words stay whole ("the"), rare words split into pieces ("tokenisation" → "token", "isation").

### Algorithms
- **BPE (byte-pair encoding)**: start from characters/bytes, repeatedly merge the most frequent adjacent pair — GPT-2/3/4, Llama 3 (byte-level BPE, tiktoken).
- **WordPiece**: merges that maximise likelihood; continuation pieces marked "##" — BERT.
- **Unigram LM / SentencePiece**: language-independent, treats spaces as symbols "▁" — T5, Llama 2, multilingual models.

### Special tokens
[CLS], [SEP], [PAD], [MASK] (BERT); <s>, </s>, <|endoftext|>; chat templates with role markers.

### Practical consequences
- ~1 token ≈ ¾ English word; Hindi and other scripts often cost several times more tokens per word.
- **Context window** (e.g. 8k–1M tokens) limits prompt + output length; API **pricing** is per token.
- Tokenisation quirks explain LLM weaknesses with spelling, counting letters and arithmetic on long numbers.
- Always use the tokenizer that matches the model.""",
  code="""
from tokenizers import Tokenizer, models, trainers, pre_tokenizers
corpus = ["low lower lowest newer newest", "the newest model is lower cost", "tokenization splits rare words", "new models tokenize words"] * 50
bpe = Tokenizer(models.BPE(unk_token="[UNK]")); bpe.pre_tokenizer = pre_tokenizers.Whitespace()
bpe.train_from_iterator(corpus, trainers.BpeTrainer(vocab_size=60, special_tokens=["[UNK]", "[PAD]"]))
wp = Tokenizer(models.WordPiece(unk_token="[UNK]")); wp.pre_tokenizer = pre_tokenizers.Whitespace()
wp.train_from_iterator(corpus, trainers.WordPieceTrainer(vocab_size=60, special_tokens=["[UNK]", "[PAD]"]))
for text in ["lowest newest tokenization", "slowest"]:
    print(f"{text!r}\\n  BPE      : {bpe.encode(text).tokens}\\n  WordPiece: {wp.encode(text).tokens}")
ids = bpe.encode("newer models").ids; print("token ids:", ids, "->", bpe.decode(ids))
# Real model tokenizers (online): AutoTokenizer.from_pretrained("bert-base-uncased") / tiktoken.get_encoding("o200k_base")
""",
  say=[("Why do LLMs struggle to count the letters in a word?",
        "\"They don't see letters — they see subword tokens. 'strawberry' may be two or three tokens, so the model has to have memorised how each token is spelled to count characters. That's a tokenisation artefact, not a reasoning failure; asking it to spell the word out letter by letter first, or using code, fixes it.\"")]),

M("m-bert-gpt-t5", "BERT, GPT and T5: encoder, decoder and encoder–decoder transformers", "Advanced",
  "BERT reads text bidirectionally to understand it; GPT predicts the next token to generate text; T5 converts every task into text-to-text. Knowing their pre-training objectives explains what each is good at.",
  """|Model|Architecture|Pre-training objective|Best at|Descendants|
|**BERT** (Google, 2018)|encoder-only, bidirectional|**masked language modelling** (predict 15% masked tokens) + next-sentence prediction|classification, NER, extractive QA, embeddings, re-ranking|RoBERTa, ALBERT, DistilBERT, DeBERTa, ModernBERT, sentence-transformers|
|**GPT** (OpenAI, 2018–)|decoder-only, causal (left-to-right)|**next-token prediction** (causal LM)|generation, few-shot learning, chat, code|GPT-2/3/4/5, Llama, Mistral, Claude, Gemini, Qwen|
|**T5** (Google, 2019)|encoder–decoder|**span corruption** (fill in masked spans), everything as "text-to-text"|translation, summarisation, structured transformations|mT5, Flan-T5, BART (denoising autoencoder)|

### How they're used
- BERT: add a small head on the [CLS] token (classification) or each token (NER); fine-tune.
- GPT: prompt it, or fine-tune on instruction data (SFT), align with RLHF/DPO.
- T5: input "summarize: …", "translate English to German: …" → output text.

### Why decoder-only won for LLMs
Simple objective that uses all text, scales smoothly, naturally supports generation and in-context learning; with instruction tuning it does classification too.""",
  code=TINY_TOK + """
import torch
from transformers import BertConfig, BertForMaskedLM, GPT2Config, GPT2LMHeadModel, T5Config, T5ForConditionalGeneration
torch.manual_seed(0)
tok = tiny_tokenizer(["the cat sat on the mat", "the dog sat on the log", "a cat and a dog played"] * 20)
batch = tok(["the cat sat on the mat"], return_tensors="pt")
bert = BertForMaskedLM(BertConfig(vocab_size=tok.vocab_size, hidden_size=32, num_hidden_layers=2, num_attention_heads=2, intermediate_size=64))
labels = batch["input_ids"].clone(); masked = batch["input_ids"].clone(); masked[0, 2] = tok.mask_token_id           # MLM: hide one token
labels[masked != tok.mask_token_id] = -100
print("BERT masked-LM loss:", round(bert(input_ids=masked, attention_mask=batch["attention_mask"], labels=labels).loss.item(), 3))
gpt = GPT2LMHeadModel(GPT2Config(vocab_size=tok.vocab_size, n_embd=32, n_layer=2, n_head=2))
print("GPT next-token loss:", round(gpt(input_ids=batch["input_ids"], labels=batch["input_ids"]).loss.item(), 3), "(labels shifted inside the model)")
t5 = T5ForConditionalGeneration(T5Config(vocab_size=tok.vocab_size, d_model=32, d_ff=64, num_layers=2, num_heads=2, d_kv=16, decoder_start_token_id=tok.pad_token_id, pad_token_id=tok.pad_token_id))
src, tgt = tok(["the cat sat"], return_tensors="pt"), tok(["on the mat"], return_tensors="pt")
print("T5 text-to-text loss:", round(t5(input_ids=src["input_ids"], labels=tgt["input_ids"]).loss.item(), 3))
for name, m in [("BERT", bert), ("GPT", gpt), ("T5", t5)]: print(f"{name} (tiny config) params: {sum(p.numel() for p in m.parameters()):,}")
# Real checkpoints: BertForMaskedLM.from_pretrained("bert-base-uncased"), GPT2LMHeadModel.from_pretrained("gpt2"), T5ForConditionalGeneration.from_pretrained("t5-small")
""",
  say=[("Would you use BERT or GPT for a classification task?",
        "\"For a dedicated classifier with a few thousand labels, a fine-tuned encoder like DeBERTa or a BERT variant is usually more accurate per dollar and much faster at inference, because it reads the whole input bidirectionally. A GPT-style LLM is attractive when I have few labels — zero- or few-shot prompting — or the label set changes often. In production I sometimes use an LLM to label data, then distil it into a small BERT model.\"")]),

M("m-huggingface", "Hugging Face: pipelines, Auto classes, tokenizers, datasets, the Hub", "Intermediate",
  "Hugging Face is the hub of open models and the `transformers` library — load thousands of pretrained models for text, vision and audio with a few lines, then fine-tune them.",
  """### Key pieces
- **Hub** (huggingface.co): models, datasets and Spaces (demos) with model cards and licences.
- **pipeline()**: one-line inference — `pipeline("sentiment-analysis")`, "ner", "question-answering", "summarization", "translation", "zero-shot-classification", "text-generation", "automatic-speech-recognition", "image-classification", "object-detection".
- **Auto classes**: `AutoTokenizer`, `AutoModel`, `AutoModelForSequenceClassification`, `AutoModelForCausalLM`… pick the right architecture from a checkpoint name.
- **datasets**: load/stream datasets, `map` tokenisation in batches, Arrow-backed.
- **Trainer** / `TrainingArguments`: training loop with evaluation, checkpoints, mixed precision.
- **PEFT** (LoRA), **accelerate** (multi-GPU), **bitsandbytes** (8/4-bit), **TRL** (SFT, DPO, RLHF), **sentence-transformers**, **diffusers**, **evaluate**.
- `model.push_to_hub()` to share; `HF_TOKEN` for gated models (Llama).

### Workflow
`tokenizer = AutoTokenizer.from_pretrained(ckpt)` → `model = AutoModelForX.from_pretrained(ckpt)` → `inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")` → `outputs = model(**inputs)` → logits → softmax.""",
  net=True,
  code="""
# Run in Colab or VS Code (downloads models from the Hugging Face Hub)
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
print(clf(["I love this phone!", "The battery is a disaster."]))

zsc = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print(zsc("My card was charged twice for one order", candidate_labels=["billing", "delivery", "technical issue"]))

ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
print(ner("Sundar Pichai visited Google's office in Hyderabad."))

qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
print(qa(question="Where is the Taj Mahal?", context="The Taj Mahal is a white marble mausoleum in Agra, India."))

ckpt = "distilbert-base-uncased-finetuned-sst-2-english"                       # the same thing, step by step
tok = AutoTokenizer.from_pretrained(ckpt); model = AutoModelForSequenceClassification.from_pretrained(ckpt)
inputs = tok(["not bad at all"], return_tensors="pt", padding=True, truncation=True)
with torch.no_grad(): probs = model(**inputs).logits.softmax(-1)
print({model.config.id2label[i]: round(p, 3) for i, p in enumerate(probs[0].tolist())})
""",
  say=[("What happens inside a Hugging Face pipeline call?",
        "\"Three steps: the tokenizer converts text to token ids with attention masks, padding and truncation; the model runs a forward pass to produce logits; and post-processing turns logits into human-readable output — softmax and label names for classification, span extraction for QA, decoding for generation. Doing those steps manually with AutoTokenizer and AutoModel gives more control for batching and deployment.\"")]),

M("m-finetune-bert", "Fine-tuning BERT for classification with Hugging Face Trainer", "Advanced",
  "Fine-tuning adds a classification head on top of a pretrained encoder and trains the whole model briefly on your labelled data with a small learning rate. It's the standard way to get state-of-the-art text classifiers.",
  """### Recipe
1. Load a dataset (`datasets`) and split train/validation/test.
2. Tokenise with the model's tokenizer (`truncation=True`, max_length 128–512); pad dynamically per batch (`DataCollatorWithPadding`).
3. `AutoModelForSequenceClassification.from_pretrained(ckpt, num_labels=K, id2label=…)` — a randomly initialised head on the [CLS] representation.
4. `TrainingArguments`: learning rate **2e-5 to 5e-5**, batch 16–32, **2–4 epochs**, weight decay 0.01, warm-up, evaluation each epoch, `load_best_model_at_end`, fp16 on GPU.
5. `Trainer(model, args, train_dataset, eval_dataset, compute_metrics)` → `trainer.train()` → `evaluate()` → `save_model()`.

### Tips
Start with DistilBERT (fast) then try RoBERTa/DeBERTa-v3; use multilingual models (XLM-R, MuRIL, IndicBERT) for Indian languages; handle imbalance with class weights; watch for overfitting on small data (few epochs, early stopping); for sentence pairs (Quora duplicates) feed both texts: `tokenizer(q1, q2)`.

The runnable code below uses a tiny randomly initialised BERT and a self-trained tokenizer so it works offline; swap in `from_pretrained("distilbert-base-uncased")` in Colab for real accuracy.""",
  code=TINY_TOK + """
import numpy as np, torch
from datasets import Dataset
from transformers import BertConfig, BertForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
torch.manual_seed(0)
pos = ["great movie loved it", "wonderful acting and story", "brilliant and fun", "really enjoyed this film", "superb music great cast"]
neg = ["boring movie hated it", "terrible acting and story", "dull and slow", "really disliked this film", "awful music bad cast"]
data = Dataset.from_dict({"text": pos * 20 + neg * 20, "label": [1] * 100 + [0] * 100}).shuffle(seed=0).train_test_split(test_size=0.2, seed=0)
tok = tiny_tokenizer(pos + neg)                       # online: tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
enc = data.map(lambda b: tok(b["text"], truncation=True, max_length=32), batched=True)
model = BertForSequenceClassification(BertConfig(vocab_size=tok.vocab_size, hidden_size=64, num_hidden_layers=2, num_attention_heads=2,
                                                 intermediate_size=128, num_labels=2, id2label={0: "NEG", 1: "POS"}, label2id={"NEG": 0, "POS": 1}))
# online: model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2, id2label=..., label2id=...)
def metrics(p): return {"accuracy": float((np.argmax(p.predictions, -1) == p.label_ids).mean())}
args = TrainingArguments("bert-sentiment", learning_rate=1e-3, per_device_train_batch_size=16, num_train_epochs=8, weight_decay=0.01,
                         eval_strategy="no", save_strategy="no", logging_strategy="no", report_to=[], disable_tqdm=True, seed=0)
trainer = Trainer(model=model, args=args, train_dataset=enc["train"], eval_dataset=enc["test"], data_collator=DataCollatorWithPadding(tok), compute_metrics=metrics)
trainer.train(); print("eval:", {k: round(v, 3) for k, v in trainer.evaluate().items() if k in ("eval_loss", "eval_accuracy")})
inputs = tok(["great story loved it", "boring film hated it"], return_tensors="pt", padding=True)
with torch.no_grad(): print("predictions:", [model.config.id2label[i] for i in model(**inputs).logits.argmax(-1).tolist()])
""",
  say=[("What learning rate and how many epochs would you use to fine-tune BERT, and why so small?",
        "\"Typically 2e-5 to 5e-5 for 2 to 4 epochs with warm-up and weight decay. The pretrained weights already encode a lot of language knowledge; a large learning rate or many epochs would overwrite it — catastrophic forgetting — and overfit small datasets. The new classification head is the only part starting from scratch.\"")]),

M("m-finetune-gpt", "Fine-tuning GPT-style models: causal LM training, instruction tuning, generation", "Advanced",
  "Fine-tuning a decoder (GPT-2, Llama, Mistral) continues next-token training on your text — domain documents, or instruction/response pairs — so the model adopts your style, format or knowledge.",
  """### Types of fine-tuning for decoders
- **Continued pre-training**: raw domain text (legal, medical) → better domain fluency.
- **Supervised fine-tuning (SFT) / instruction tuning**: (prompt, ideal response) pairs formatted with the model's **chat template**; loss usually only on response tokens.
- **Preference tuning**: RLHF or **DPO** on (chosen, rejected) responses — see Module 4.

### Practicalities
- Full fine-tuning of billion-parameter models needs lots of GPU memory → **LoRA / QLoRA** (train small adapters; 4-bit base model) with PEFT + TRL's `SFTTrainer`.
- Data quality beats quantity: a few thousand clean, diverse examples go far.
- Evaluate with held-out prompts, task metrics and human/LLM-judge review; watch for forgetting general abilities.

### When *not* to fine-tune
If the model just needs **knowledge** (company documents) → use **RAG**. If it needs a format/behaviour → try prompting first. Fine-tune for consistent style/format, specialised tasks, lower latency/cost with a smaller model, or distilling a big model.""",
  code=TINY_TOK + """
import torch
from transformers import GPT2Config, GPT2LMHeadModel
torch.manual_seed(0)
pairs = [("capital of france", "paris"), ("capital of india", "new delhi"), ("capital of japan", "tokyo"), ("capital of italy", "rome")]
texts = [f"question : {q} answer : {a} [SEP]" for q, a in pairs]
tok = tiny_tokenizer(texts * 10, vocab=120)               # online: AutoTokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel(GPT2Config(vocab_size=tok.vocab_size, n_embd=64, n_layer=2, n_head=2, n_positions=64))   # online: from_pretrained("gpt2")
batch = tok(texts, return_tensors="pt", padding=True)
labels = batch["input_ids"].clone(); labels[batch["attention_mask"] == 0] = -100
ans_start = [len(tok(f"question : {q} answer :")["input_ids"]) for q, _ in pairs]
for i, s in enumerate(ans_start): labels[i, :s] = -100      # SFT: compute loss only on the answer tokens
opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
for step in range(150):
    out = model(**batch, labels=labels); opt.zero_grad(); out.loss.backward(); opt.step()
print("final SFT loss:", round(out.loss.item(), 4))
model.eval()
for q, _ in pairs[:3]:
    prompt = tok(f"question : {q} answer :", return_tensors="pt")
    gen = model.generate(**prompt, max_new_tokens=4, do_sample=False, pad_token_id=tok.pad_token_id, eos_token_id=tok.sep_token_id)
    print(q, "->", tok.decode(gen[0, prompt["input_ids"].shape[1]:], skip_special_tokens=True).replace(" ##", ""))
""",
  say=[("When would you fine-tune an LLM instead of using RAG?",
        "\"RAG is for knowledge: facts that change or must be cited, like company documents — it's cheaper to update and reduces hallucination. Fine-tuning is for behaviour: a consistent format or tone, a specialised task, or getting a smaller, cheaper model to match a bigger one. Often the answer is both — a fine-tuned model that is good at using retrieved context.\"")]),

M("m-decoding", "Decoding strategies: greedy, beam search, temperature, top-k, top-p", "Intermediate",
  "A language model outputs a probability for every next token; the decoding strategy decides which one to pick. It trades off quality, diversity and determinism.",
  """|Strategy|How|Good for|Problems|
|Greedy|always the most likely token|short factual answers, deterministic output|repetitive, dull; misses better sequences|
|Beam search (width k)|keep k best partial sequences by total log-prob|translation, summarisation, ASR|bland/generic in open-ended chat; slower|
|Sampling with **temperature** T|divide logits by T then sample: T < 1 sharper, T > 1 flatter, T → 0 = greedy|creative writing (0.7–1.0), code (0.0–0.3)|high T → nonsense|
|**Top-k**|sample only from the k most likely tokens|cuts the long tail|fixed k ignores how confident the model is|
|**Top-p (nucleus)**|sample from the smallest set whose probabilities sum to p (0.9)|adaptive; default in many APIs|—|
|Min-p, typical sampling|other tail-cutting rules|—|—|
|Repetition / frequency penalties|down-weight already-used tokens|avoid loops|can hurt required repetition|

Other knobs: max tokens, stop sequences, seeds; **structured decoding** constrains output to valid JSON/grammar; **speculative decoding** speeds up generation with a small draft model.""",
  demo="sampling",
  code="""
import numpy as np
rng = np.random.default_rng(0)
vocab = np.array(["mat", "sofa", "floor", "roof", "moon", "banana"])
logits = np.array([3.0, 2.2, 2.0, 1.0, -1.0, -3.0])
def softmax(z): e = np.exp(z - z.max()); return e / e.sum()
for T in (0.3, 1.0, 2.0):
    print(f"temperature {T}: probs", dict(zip(vocab, softmax(logits / T).round(3))))
def top_k(logits, k): z = logits.copy(); z[np.argsort(z)[:-k]] = -np.inf; return softmax(z)
def top_p(logits, p):
    probs = softmax(logits); order = np.argsort(probs)[::-1]; keep = order[: np.searchsorted(np.cumsum(probs[order]), p) + 1]
    z = np.full_like(logits, -np.inf); z[keep] = logits[keep]; return softmax(z)
print("top-k=2 keeps:", vocab[top_k(logits, 2) > 0].tolist(), " top-p=0.9 keeps:", vocab[top_p(logits, 0.9) > 0].tolist())
print("greedy:", vocab[logits.argmax()], "| 10 samples at T=1, top-p=0.9:", rng.choice(vocab, 10, p=top_p(logits, 0.9)).tolist())
""",
  say=[("What temperature would you use for a code assistant versus a story writer?",
        "\"Low — around 0 to 0.2 — for code, SQL or extraction, where there's one right answer and I want determinism. Higher — 0.7 to 1.0 with top-p around 0.9 — for creative writing or brainstorming, where diversity matters. I'd still evaluate a few settings on real prompts because the best value varies by model.\"")]),

M("m-llms", "Large language models (LLMs): how they're built, what they can and can't do", "Intermediate",
  "LLMs are huge decoder-only transformers trained on trillions of tokens to predict the next token, then tuned to follow instructions and be helpful and safe. Scale gives them broad knowledge and in-context learning.",
  """### Training stages
1. **Pre-training**: next-token prediction on web pages, books, code (trillions of tokens, thousands of GPUs, weeks–months). Produces a base model with knowledge and language skill.
2. **Supervised fine-tuning (SFT)** on instruction–response demonstrations → follows instructions.
3. **Preference alignment**: RLHF (reward model + PPO), DPO, Constitutional AI / RLAIF → helpful, honest, harmless; refusal behaviour.
4. Optional: tool use, reasoning training with reinforcement learning on verifiable tasks (math, code), long-context and multimodal extension.

### Scaling laws
Loss falls predictably as a power law with parameters, data and compute; **Chinchilla**: ~20 tokens per parameter is compute-optimal (modern models train far longer for cheaper inference).

### Capabilities
In-context (few-shot) learning, instruction following, reasoning (improved by chain-of-thought and "thinking" models), coding, summarisation, translation, tool use, multimodality.

### Limitations
**Hallucination** (fluent but false), knowledge cutoff, context window limits, sensitivity to prompt wording, bias, prompt injection, cost/latency, non-determinism. Mitigate with RAG, tools, verification, evaluation and guardrails.

### Landscape (as of mid-2026)
Closed APIs: OpenAI GPT models, Anthropic **Claude**, Google **Gemini**. Open-weight: Meta **Llama**, Mistral, Qwen, DeepSeek, Gemma — run locally with Ollama, llama.cpp, vLLM or Hugging Face. Small language models (1–8B) for edge and cost-sensitive tasks.""",
  code="""
# Parameter count of a decoder-only transformer ~ 12 * layers * d_model^2 (+ embeddings)
def params(layers, d, vocab): return 12 * layers * d ** 2 + vocab * d
for name, L, d, V in [("GPT-2 small", 12, 768, 50257), ("GPT-2 XL", 48, 1600, 50257), ("Llama-style 7B", 32, 4096, 32000), ("GPT-3", 96, 12288, 50257)]:
    print(f"{name:15s} ~{params(L, d, V) / 1e9:6.2f} B parameters")
# Memory to just hold the weights at different precisions
for bits in (32, 16, 8, 4):
    print(f"7B model at {bits:2d}-bit: {7e9 * bits / 8 / 1e9:5.1f} GB")
# Chinchilla rule of thumb: ~20 training tokens per parameter; training FLOPs ~ 6 * N * D
N = 7e9; D = 20 * N; print(f"compute-optimal tokens for 7B: {D / 1e9:.0f} B, training FLOPs ~ {6 * N * D:.1e}")
""",
  say=[("Why do LLMs hallucinate, and how do you reduce it?",
        "\"They're trained to produce plausible continuations, not to verify facts, so when knowledge is missing or fuzzy they still generate fluent text. To reduce it: ground answers in retrieved documents with RAG and require citations, let the model use tools like search or calculators, lower temperature for factual tasks, allow and encourage 'I don't know', add verification steps, and evaluate faithfulness systematically.\"")]),

M("m-llm-api", "Using LLMs through APIs: OpenAI, Anthropic Claude, Llama (local), chat format, tokens, streaming, structured output", "Intermediate",
  "Most LLM applications call a model through an API: send a list of messages, get a completion. Understanding roles, tokens, parameters and costs is essential for building with ChatGPT, Claude or open models.",
  """### Chat format
A list of messages with roles: **system** (instructions, persona, rules), **user**, **assistant** (previous replies). The API is stateless — you resend the conversation each time (manage history length!).

### Key parameters
model, max tokens, temperature/top-p, stop sequences, **tools / function calling** (model returns a structured call your code executes), **structured output / JSON schema**, streaming (tokens as they're generated), seed.

### Costs and limits
Priced per input and output token; context window limits; rate limits (requests and tokens per minute) → retries with exponential backoff, caching (prompt caching), batching, smaller models for easy tasks.

### Open models
Run **Llama**, Mistral, Qwen locally via **Ollama** (`ollama run llama3.2`), llama.cpp, vLLM or Hugging Face `transformers` — privacy, no per-token cost, needs GPU/RAM. Many local servers expose an OpenAI-compatible API.

### Security
Keep API keys in environment variables / secret managers (never in code or Git); treat model output as untrusted (validate before executing); log and monitor usage.""",
  net=True,
  code="""
# Needs an API key: set OPENAI_API_KEY / ANTHROPIC_API_KEY as environment variables (Colab: Secrets panel). Never hard-code keys.
import os, json

# --- OpenAI ---
from openai import OpenAI
client = OpenAI()                                          # reads OPENAI_API_KEY
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": "You are a concise ML tutor."},
              {"role": "user", "content": "Explain overfitting in two sentences."}],
    temperature=0.2, max_tokens=120)
print(resp.choices[0].message.content, resp.usage.total_tokens, "tokens")

# --- Anthropic Claude (streaming) ---
import anthropic
claude = anthropic.Anthropic()                             # reads ANTHROPIC_API_KEY
with claude.messages.stream(model="claude-haiku-5-5", max_tokens=200, system="You are a concise ML tutor.",
                            messages=[{"role": "user", "content": "What is a learning rate?"}]) as stream:
    for text in stream.text_stream: print(text, end="", flush=True)

# --- Structured output via a JSON schema-like instruction + validation ---
review = "Battery is great but the camera is blurry at night."
resp = client.chat.completions.create(model="gpt-4o-mini", response_format={"type": "json_object"},
    messages=[{"role": "user", "content": f"Return JSON with keys aspects (list of {{aspect, sentiment}}). Review: {review}"}])
print(json.loads(resp.choices[0].message.content))

# --- Local Llama with Ollama (OpenAI-compatible endpoint): `ollama pull llama3.2` first ---
local = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
print(local.chat.completions.create(model="llama3.2", messages=[{"role": "user", "content": "Hi!"}]).choices[0].message.content)
""",
  say=[("How do you keep LLM API costs under control in production?",
        "\"Route easy requests to smaller, cheaper models and reserve large models for hard ones; trim prompts and conversation history; use prompt caching for repeated system prompts and documents; cache full responses for repeated queries; cap max output tokens; batch offline jobs with batch APIs; and monitor tokens per feature with alerts. Sometimes fine-tuning or distilling into a small model is cheaper at scale.\"")]),

M("m-prompt-engineering", "Prompt engineering: zero-shot, few-shot, chain-of-thought, structure and evaluation", "Intermediate",
  "Prompt engineering is designing the instructions and context you give an LLM so it reliably does the task. Clear, specific, structured prompts with examples beat clever tricks.",
  """### Core techniques
- **Be explicit**: task, audience, constraints, output format, length, what to do when unsure.
- **Role / system prompt**: "You are a careful financial analyst…".
- **Context and delimiters**: put documents inside clear tags (<document>…</document>) and separate them from instructions.
- **Zero-shot** (just instructions) vs **few-shot** (2–5 input→output examples covering edge cases; keep them consistent and diverse).
- **Chain-of-thought (CoT)**: ask the model to reason step by step before answering (or use reasoning models); **self-consistency**: sample several reasoning paths and vote.
- **Decomposition / prompt chaining**: split a complex task into steps, each its own prompt.
- **Structured output**: JSON schema, XML tags; validate and retry.
- **ReAct**: interleave reasoning and tool calls (agents).
- Give the model an "out" ("If the answer isn't in the document, say so") to reduce hallucination.

### Prompting is engineering
Version prompts, build an **evaluation set** of real inputs with expected outputs, measure changes, watch for regressions when models update. Guard against **prompt injection** when inserting untrusted text.""",
  code="""
from string import Template
few_shot = Template('''You classify customer messages for an Indian bank.
Labels: card_issue, loan_query, account_balance, other. Reply with JSON: {"label": ..., "confidence": 0-1}.
If the message is unclear, use "other".

<examples>
Message: "my debit card is not working at ATMs" -> {"label": "card_issue", "confidence": 0.95}
Message: "what is the interest rate on a home loan" -> {"label": "loan_query", "confidence": 0.9}
Message: "hello?" -> {"label": "other", "confidence": 0.6}
</examples>

<message>
$message
</message>''')
print(few_shot.substitute(message="How much money is left in my savings account?"))
cot = ("Q: A train leaves at 14:35 and the trip takes 2 h 50 min. When does it arrive?\\n"
       "Think step by step inside <thinking> tags, then give only the final time inside <answer> tags.")
print("\\n" + cot)
""",
  say=[("How do you make an LLM-based feature reliable?",
        "\"Write clear, specific prompts with structured output, examples covering edge cases, and an explicit fallback when information is missing. Then treat it like software: build an evaluation set from real inputs, measure accuracy and failure modes, validate outputs against a schema with retries, ground facts with retrieval, add guardrails and monitoring in production, and re-run evals whenever the prompt or model changes.\"")]),

M("m-embeddings-vectordb", "Sentence embeddings, semantic search and vector databases", "Intermediate",
  "Embedding models turn whole sentences or documents into vectors where similar meanings are close. A vector database stores millions of them and finds the nearest ones fast — the retrieval engine behind RAG and semantic search.",
  """### Embedding models
Sentence-transformers (all-MiniLM, BGE, E5, GTE), OpenAI/Cohere/Voyage embedding APIs, multilingual models. Trained contrastively so paraphrases are close. Typical size 384–3072 dimensions; normalise and use cosine/dot product.

### Similarity search
Exact search compares the query with every vector (fine up to ~100k). **Approximate nearest neighbour (ANN)** indexes trade a little recall for huge speed:
- **HNSW** (hierarchical navigable small-world graphs) — most popular.
- **IVF** (cluster vectors, search only nearby clusters) + **PQ** (product quantisation compresses vectors).
- Libraries: **FAISS**, Annoy, ScaNN, hnswlib.

### Vector databases
Pinecone, Weaviate, Qdrant, Milvus, Chroma, pgvector (Postgres), Elasticsearch/OpenSearch — add metadata filtering, persistence, updates, hybrid search, scaling.

### Hybrid search and re-ranking
Combine keyword **BM25** (exact terms, names, codes) with dense vectors (meaning) via reciprocal rank fusion; then re-rank the top results with a **cross-encoder** for precision.""",
  code="""
import numpy as np, faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from rank_bm25 import BM25Okapi
docs = ["How to reset my password", "Steps to change account password", "Refund policy for cancelled orders", "How long do refunds take",
        "Update the delivery address", "Track my order shipment", "Cancel an order before shipping", "Payment failed but money deducted"]
# offline stand-in for a sentence-embedding model: LSA (TF-IDF + SVD) vectors, L2-normalised
tf = TfidfVectorizer().fit(docs); svd = TruncatedSVD(6, random_state=0).fit(tf.transform(docs))
embed = lambda texts: (lambda v: v / np.linalg.norm(v, axis=1, keepdims=True))(svd.transform(tf.transform(texts)).astype("float32"))
# online: from sentence_transformers import SentenceTransformer; embed = SentenceTransformer("all-MiniLM-L6-v2").encode
E = embed(docs); index = faiss.IndexFlatIP(E.shape[1]); index.add(E)                 # inner product on unit vectors = cosine
q = "I forgot my password"; scores, ids = index.search(embed([q]), 3)
print("dense top-3:", [(docs[i], round(float(s), 2)) for i, s in zip(ids[0], scores[0])])
bm25 = BM25Okapi([d.lower().split() for d in docs]); b = bm25.get_scores(q.lower().split())
print("BM25 top-3: ", [docs[i] for i in np.argsort(b)[::-1][:3]])
hnsw = faiss.IndexHNSWFlat(E.shape[1], 16); hnsw.add(E); print("HNSW (approximate) top-1:", docs[hnsw.search(embed([q]), 1)[1][0][0]])
rrf = {}
for ranking in (list(ids[0]), list(np.argsort(b)[::-1][:3])):
    for r, i in enumerate(ranking): rrf[i] = rrf.get(i, 0) + 1 / (60 + r)
print("hybrid (reciprocal rank fusion) best:", docs[max(rrf, key=rrf.get)])
""",
  say=[("Why use hybrid search instead of only vector search in RAG?",
        "\"Dense embeddings capture meaning and paraphrases but can miss exact matches — product codes, names, error messages, rare terms. BM25 keyword search is great at those but misses synonyms. Combining them, for example with reciprocal rank fusion, and then re-ranking the top candidates with a cross-encoder gives noticeably better retrieval, which directly improves RAG answers.\"")]),

M("m-rag", "Retrieval-augmented generation (RAG)", "Advanced",
  "RAG answers questions using your own documents: retrieve the most relevant chunks, put them in the prompt, and have the LLM answer from them with citations. It adds fresh, private knowledge without retraining and reduces hallucinations.",
  """### Pipeline
**Indexing (offline)**: load documents (PDF, HTML, wikis) → clean → **chunk** (e.g. 300–800 tokens with overlap, respecting headings) → **embed** each chunk → store vectors + metadata in a vector DB.
**Query time**: user question → (rewrite/expand) → embed → retrieve top-k chunks (dense, BM25 or hybrid) → **re-rank** → build a prompt with instructions + chunks + question → LLM generates an answer **grounded in and citing** the chunks.

### Design decisions
Chunk size/overlap, embedding model, k, hybrid search, re-ranker, metadata filters (date, department, access control!), prompt that says "answer only from context; say you don't know otherwise", citations.

### Evaluating RAG
- **Retrieval**: recall@k, MRR, nDCG on question→relevant-chunk pairs.
- **Generation**: faithfulness/groundedness (is every claim supported?), answer relevance, correctness — human review or LLM-as-judge (RAGAS, TruLens, DeepEval).

### Common failure modes
Wrong chunk retrieved (bad chunking/embeddings), relevant info split across chunks, too much irrelevant context ("lost in the middle"), stale index, ignoring permissions, prompt injection inside documents. Advanced RAG techniques (Module 4) address these.""",
  code="""
import numpy as np, re
from sklearn.feature_extraction.text import TfidfVectorizer
handbook = '''Leave policy. Employees get 24 days of paid leave per year. Unused leave up to 10 days carries over to the next year.
Work from home. Staff may work from home two days per week with manager approval. Fully remote work needs HR approval.
Expenses. Travel expenses must be submitted within 30 days with receipts. Meals are reimbursed up to 1500 rupees per day.
Laptops. Laptops are replaced every three years. Lost laptops must be reported to IT within 24 hours.'''
def chunk(text, size=2):                                     # chunk by sentences with 1 sentence overlap
    sents = re.split(r"(?<=\\.)\\s+", text.strip()); return [" ".join(sents[i:i + size]) for i in range(0, len(sents) - 1, size - 1)]
chunks = chunk(handbook); print(len(chunks), "chunks, e.g.:", chunks[0])
vec = TfidfVectorizer(stop_words="english").fit(chunks); C = vec.transform(chunks)  # online: sentence-transformer embeddings + vector DB
def retrieve(q, k=2):
    s = (C @ vec.transform([q]).T).toarray().ravel(); top = np.argsort(s)[::-1][:k]; return [(int(i), chunks[i], round(float(s[i]), 3)) for i in top]
def build_prompt(q, hits):
    ctx = "\\n".join(f"[{i}] {c}" for i, c, _ in hits)
    return f'''Answer the question using ONLY the context. Cite chunk numbers like [2]. If the answer is not in the context, say "I don't know".
<context>
{ctx}
</context>
Question: {q}'''
q = "How many leave days can I carry forward?"
hits = retrieve(q); print("retrieved:", [(i, s) for i, _, s in hits]); print(build_prompt(q, hits))
# online: answer = client.chat.completions.create(model=..., messages=[{"role": "user", "content": build_prompt(q, hits)}])
""",
  say=[("Walk me through designing a RAG system for a company's internal documents.",
        "\"Ingest documents with metadata and access permissions, chunk them along headings with some overlap, embed with a strong embedding model and store in a vector database with hybrid BM25 search. At query time, optionally rewrite the question, retrieve top candidates filtered by the user's permissions, re-rank with a cross-encoder, and prompt the LLM to answer only from the context with citations and to say when it doesn't know. Evaluate retrieval recall and answer faithfulness on a test set, monitor in production, and keep the index fresh.\"")]),

M("m-langchain", "LangChain and LlamaIndex: building LLM applications (prompts, chains, retrievers, agents)", "Intermediate",
  "LangChain provides building blocks — prompt templates, model wrappers, output parsers, retrievers, tools — and composes them into chains and agents. LlamaIndex focuses on indexing and querying your data for RAG.",
  """### LangChain concepts
- **Chat models / LLMs**: one interface over OpenAI, Anthropic, Google, Ollama, Hugging Face.
- **Prompt templates**: parameterised prompts (`ChatPromptTemplate`).
- **Output parsers / structured output**: turn text into Python objects (`with_structured_output(PydanticModel)`).
- **LCEL (LangChain Expression Language)**: compose with `|` — `prompt | model | parser`; supports streaming, batching, async.
- **Document loaders, text splitters** (`RecursiveCharacterTextSplitter`), **embeddings**, **vector stores** (FAISS, Chroma, Pinecone), **retrievers**.
- **Tools and agents**: functions the model can call; **LangGraph** for stateful, controllable multi-step agents (graphs with loops, memory, human approval).
- **LangSmith**: tracing, debugging and evaluation.

### LlamaIndex
Data connectors, node parsers, index types (vector, summary, knowledge graph), query engines, routers, and agents — very quick to stand up RAG.

### Should you use a framework?
Great for prototypes and standard patterns; for production, many teams keep the core logic thin (plain SDK calls) and adopt only the pieces they need — abstractions can hide prompts and make debugging harder.""",
  code="""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
text = ("Refunds are processed within 7 working days. Cancelled orders are refunded to the original payment method. "
        "Delivery takes 3 to 5 days in metro cities. Remote areas may take up to 10 days.")
splits = RecursiveCharacterTextSplitter(chunk_size=80, chunk_overlap=10).split_documents([Document(page_content=text, metadata={"source": "faq.txt"})])
print(len(splits), "chunks:", [d.page_content for d in splits])
def retriever(question):                                    # stand-in for vector_store.as_retriever(k=2)
    words = set(question.lower().split()); return sorted(splits, key=lambda d: -len(words & set(d.page_content.lower().split())))[:2]
prompt = ChatPromptTemplate.from_messages([("system", "Answer only from the context. Context:\\n{context}"), ("human", "{question}")])
llm = FakeListChatModel(responses=["Refunds are processed within 7 working days [faq.txt]."])   # online: ChatOpenAI(model=...) or ChatAnthropic(model=...)
chain = ({"context": RunnableLambda(retriever) | RunnableLambda(lambda docs: "\\n".join(d.page_content for d in docs)), "question": RunnablePassthrough()}
         | prompt | llm | StrOutputParser())
print("answer:", chain.invoke("how long do refunds take"))
print("prompt sent to the model:\\n", prompt.invoke({"context": "\\n".join(d.page_content for d in retriever("how long do refunds take")), "question": "how long do refunds take"}).to_string())
""",
  say=[("What does LCEL's pipe syntax give you in LangChain?",
        "\"Composable runnables: prompt, model, retriever and parser each implement the same interface, so piping them builds a chain that automatically supports invoke, batch, stream and async, with tracing in LangSmith. It makes RAG pipelines short and swappable — I can switch the model or retriever without changing the rest — though for complex agent control flow I'd use LangGraph.\"")]),
]
