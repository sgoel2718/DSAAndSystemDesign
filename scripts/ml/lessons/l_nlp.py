"""Beginner lessons: NLP, transformers & LLMs."""
from lesson_util import L

L("m-nlp-tasks",
  "NLP teaches computers to read, understand and write human language; most tasks today are solved by fine-tuning or prompting pretrained transformers.",
  """Search, chatbots, email filters, translation, review analysis and document processing all run on NLP. Being able to name the task type quickly tells you the model, labels and metric.""",
  """The main tasks:

| Task | Input → output | Example |
| --- | --- | --- |
| Text classification | text → label | review → positive |
| Named entity recognition (NER) | text → tag per word | "Shubham works at Hitachi" → PERSON, ORG |
| Question answering | question + text → answer span | "Where does he work?" → "Hitachi" |
| Summarisation | long text → short text | article → 3 sentences |
| Translation | text → text in another language | English → Hindi |
| Generation / chat | prompt → text | "Write an email…" |
| Semantic search | query → most similar documents | "refund policy" → FAQ page |

How they're solved now: **small labelled data** → fine-tune a pretrained encoder (BERT-like); **little or no labelled data** → prompt a large language model; **search** → sentence embeddings. Classical methods (TF-IDF + logistic regression) remain strong, cheap baselines.""",
  [("Name the task",
    """An insurer wants policy number, claim amount and date pulled out of emails: **NER / information extraction**."""),
   ("Choose an approach",
    """5,000 labelled support tickets in 12 categories: fine-tune a BERT-style model (or start with TF-IDF + logistic regression as a baseline). 20 labelled tickets: prompt an LLM with a few examples.""")],
  ("A legal team wants a 5-line summary of each 40-page contract. Which task?",
   "Summarisation (abstractive), usually with an LLM or an encoder–decoder model."),
  [("Token", "a unit of text the model reads: a word or part of a word"),
   ("Corpus", "a collection of documents"),
   ("NER", "finding names of people, places, organisations, dates…"),
   ("Pretrained language model", "a model trained on huge text before your task")],
  """The classic baseline for text classification: TF-IDF features + logistic regression, on a tiny hand-made dataset.""",
  r'''from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

texts = ["loved the food, great service", "terrible wait and cold food", "amazing staff, will return",
         "worst experience, never again", "good value and tasty", "rude waiter and bland dishes"]
labels = ["pos", "neg", "pos", "neg", "pos", "neg"]
clf = make_pipeline(TfidfVectorizer(), LogisticRegression()).fit(texts, labels)
print(clf.predict(["the service was great", "food was cold and bland"]))''',
  [("Which approach suits a task with only 20 labelled examples?", "Prompting a large language model with a few examples (few-shot)."),
   ("What does NER output?", "A tag for each word or span, such as PERSON, ORG, LOCATION, DATE.")])

L("m-text-preprocessing",
  "Classical NLP cleans text and splits it into tokens: lower-casing, removing stop words, and cutting words to their base form (stemming or lemmatisation).",
  """For classical models (TF-IDF, Naive Bayes), clean tokens mean fewer, more meaningful features. For transformers most of this is skipped, and knowing when not to preprocess matters too.""",
  """Typical steps:

1. **Normalise**: lower-case, fix unicode, remove URLs or HTML if irrelevant.
2. **Tokenise**: split into words and punctuation: "I'm happy!" → ["i", "'m", "happy", "!"].
3. **Remove stop words**: very common words that carry little meaning for the task (the, is, and). Careful: "not" matters for sentiment.
4. **Stemming**: chop endings by rules: running, runs → "run"; studies → "studi". Fast, crude.
5. **Lemmatisation**: use a dictionary to get the real base word: better → "good", studies → "study". Slower, accurate.
6. Linguistic annotations (spaCy/NLTK): **POS tags** (noun, verb…) and **NER**.

Transformers use their own subword tokenisers and want the **raw** text; don't remove stop words or stem for them.""",
  [("Stemming vs lemmatisation",
    """"The studies were running better" → stems: studi, were, run, better. Lemmas: study, be, run, good."""),
   ("Stop words and sentiment",
    """"This is not good": removing "not" leaves "good", flipping the meaning. Keep negations for sentiment tasks.""")],
  ("Should you remove stop words before feeding text to BERT?",
   "No: BERT uses its own tokenizer and context; removing words loses information."),
  [("Tokenisation", "splitting text into tokens"),
   ("Stop words", "very common words often removed in classical NLP"),
   ("Stemming", "cutting word endings with rules"),
   ("Lemmatisation", "mapping a word to its dictionary base form"),
   ("POS tag", "part of speech: noun, verb, adjective…")],
  """A small preprocessing pipeline with regex and NLTK's Porter stemmer (no downloads needed).""",
  r'''import re
from nltk.stem import PorterStemmer

STOP = {"the", "is", "a", "an", "and", "were", "was", "to", "of", "this"}   # keep 'not'!
stem = PorterStemmer().stem

def preprocess(text):
    text = text.lower()
    text = re.sub(r"https?://\S+", " ", text)          # drop URLs
    tokens = re.findall(r"[a-z']+", text)               # simple word tokeniser
    return [stem(t) for t in tokens if t not in STOP]

print(preprocess("The studies were RUNNING better, see https://example.com"))
print(preprocess("This is not good"))                   # 'not' survives''',
  [("Which keeps real words: stemming or lemmatisation?", "Lemmatisation."),
   ("Why keep 'not' when removing stop words for sentiment?", "It reverses the meaning of what follows.")])

L("m-web-scraping",
  "Web scraping downloads pages and pulls out the text or data you need (reviews, prices, articles) to build datasets; do it legally and politely.",
  """Many NLP projects need data that no one has packaged for you. Scraping is how you build a custom dataset, and doing it responsibly (robots.txt, rate limits, terms of service, personal data) is part of the job.""",
  """1. **Fetch** a page: `requests.get(url)` returns the HTML.
2. **Parse** it: BeautifulSoup turns HTML into a tree you can search.
3. **Select** what you need with tags and CSS classes: `soup.select("div.review p")`.
4. **Clean and store**: strip whitespace, save to CSV/JSON with the source URL and date.
5. **Paginate**: follow "next page" links in a loop.

Be responsible: check **robots.txt** and the site's terms; prefer an official **API** if one exists; add a delay between requests; identify yourself in the User-Agent; don't collect personal data you don't need. Sites that build content with JavaScript may need a browser tool such as Playwright.""",
  [("Find the data in the HTML",
    """A review looks like `<div class="review"><span class="stars">4</span><p>Great phone</p></div>`. Selector `div.review` gives each review; inside, `span.stars` and `p` give the rating and text."""),
   ("Be polite",
    """Scraping 1,000 pages with a 1-second delay takes about 17 minutes and doesn't overload the server. Sending them all at once might get you blocked.""")],
  ("A site offers a public API for its product data. Should you scrape the HTML instead?",
   "No: use the API. It's more stable, allowed by the site, and returns structured data."),
  [("HTML", "the markup language of web pages"),
   ("Parser", "a tool that turns HTML into a searchable tree"),
   ("CSS selector", "a pattern that picks elements, like div.review p"),
   ("robots.txt", "a file where a site states which paths bots may visit")],
  """Parsing a saved HTML snippet with BeautifulSoup (to fetch a live page you'd use `requests.get(url).text` instead).""",
  r'''from bs4 import BeautifulSoup
import pandas as pd

html = """
<div class="review"><span class="stars">5</span><p>Battery lasts two days. Love it!</p></div>
<div class="review"><span class="stars">2</span><p>Screen cracked in a week.</p></div>
<div class="review"><span class="stars">4</span><p>Good camera, average speaker.</p></div>
<a class="next" href="/reviews?page=2">Next</a>
"""
soup = BeautifulSoup(html, "html.parser")
rows = [{"stars": int(r.select_one("span.stars").text), "text": r.select_one("p").get_text(strip=True)}
        for r in soup.select("div.review")]
print(pd.DataFrame(rows))
print("next page:", soup.select_one("a.next")["href"])      # follow this for pagination''',
  [("What should you check before scraping a site?", "Its robots.txt, terms of service, and whether an official API exists."),
   ("What does BeautifulSoup do?", "Parses HTML into a tree so you can select elements and extract text.")])

L("m-text-representation",
  "Models need numbers, so text becomes vectors: bag of words counts words, n-grams keep short phrases, TF-IDF boosts words that are distinctive.",
  """These representations still power fast search engines, spam filters and strong baselines, and they're the stepping stone to understanding embeddings.""",
  """- **One-hot word**: a vector as long as the vocabulary with a single 1.
- **Bag of words (BoW)**: for each document, count how often each vocabulary word appears. Order is lost.
- **N-grams**: also count sequences of n words ("not good" as one feature, a 2-gram/bigram). Brings back a little order.
- **TF-IDF**: term frequency × inverse document frequency. A word gets a high weight if it's **frequent in this document** but **rare across documents**. "the" appears everywhere → low weight; "refund" in one complaint → high.

  tf-idf(word, doc) = count(word in doc) × log(N / number of docs containing the word)

These vectors are long and mostly zeros (**sparse**).""",
  [("Bag of words by hand",
    """Docs: D1 "good food good service", D2 "bad food". Vocabulary [bad, food, good, service]. D1 → **[0, 1, 2, 1]**, D2 → **[1, 1, 0, 0]**."""),
   ("IDF by hand",
    """N = 2 docs. "food" is in both: idf = log(2/2) = **0**. "good" is in one: idf = log(2/1) = **0.69**. So in D1 "good" weighs 2 × 0.69 = 1.39 while "food" weighs 0: it doesn't distinguish the documents.""")],
  ("Why does TF-IDF give 'the' a weight near zero?",
   "It appears in almost every document, so its inverse document frequency is close to log(1) = 0."),
  [("Vocabulary", "the list of all words the vectoriser knows"),
   ("N-gram", "a sequence of n consecutive words"),
   ("TF-IDF", "word count weighted by how rare the word is across documents"),
   ("Sparse vector", "a vector that is mostly zeros")],
  """Bag of words, bigrams and TF-IDF on the two example documents.""",
  r'''from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

docs = ["good food good service", "bad food"]
bow = CountVectorizer()
print(bow.fit_transform(docs).toarray(), bow.get_feature_names_out())      # [[0 1 2 1] [1 1 0 0]]

bi = CountVectorizer(ngram_range=(1, 2))                                   # words and 2-word phrases
print(bi.fit(docs).get_feature_names_out())

tfidf = TfidfVectorizer(smooth_idf=False, norm=None)                       # plain formula, no rescaling
print(tfidf.fit_transform(docs).toarray().round(2), tfidf.get_feature_names_out())''',
  [("What information does bag of words throw away?", "Word order."),
   ("How do n-grams help sentiment analysis?", "They capture short phrases like 'not good' as single features.")])

L("m-word-embeddings",
  "Word embeddings map each word to a short dense vector so that words used in similar contexts get similar vectors, capturing meaning and analogies.",
  """Embeddings replaced sparse word counts and are the basic building block of every modern NLP model: transformers start by looking up an embedding for each token.""",
  """**The idea**: "you shall know a word by the company it keeps". Words that appear around the same neighbours (coffee and tea both near "cup", "drink", "hot") should get nearby vectors.

- **word2vec**: a small network learns vectors by predicting a word from its neighbours (CBOW) or the neighbours from a word (skip-gram).
- **GloVe**: learns vectors from global word co-occurrence counts.
- **fastText**: builds a word's vector from character pieces, so it handles misspellings and unseen words.

Typical vectors have 100–300 numbers. Similarity is measured with **cosine similarity** (1 = same direction). Famous analogy: **king − man + woman ≈ queen**.

Limitation: one vector per word, so "bank" (river) and "bank" (money) share a vector. Contextual models (BERT) fix this.""",
  [("Cosine similarity by hand",
    """coffee = (0.9, 0.8), tea = (0.85, 0.75), car = (−0.2, 0.9). cos(coffee, tea) ≈ **0.999**; cos(coffee, car) = (−0.18 + 0.72) / (1.20 × 0.92) ≈ **0.49**."""),
   ("Analogy arithmetic",
    """With 2-D toy vectors king (5, 5), man (4, 1), woman (4, 3): king − man + woman = (5, 7), which is closest to queen (5, 7) in the toy space.""")],
  ("Why can't word2vec tell apart the two meanings of 'bank'?",
   "It gives each word one fixed vector, regardless of the sentence it appears in."),
  [("Embedding", "a dense vector representing a word (or other item)"),
   ("Cosine similarity", "similarity of direction between two vectors"),
   ("Context window", "how many neighbouring words count as context"),
   ("Contextual embedding", "a vector that depends on the surrounding sentence")],
  """Train tiny word embeddings from co-occurrence counts (the GloVe-style idea) with NumPy and an SVD, then check similarities.""",
  r'''import numpy as np
sentences = ["i drink hot coffee", "i drink hot tea", "coffee in a cup", "tea in a cup",
             "i drive my car", "my car is fast", "i drive a fast car"]
words = sorted({w for s in sentences for w in s.split()}); idx = {w: i for i, w in enumerate(words)}
C = np.zeros((len(words), len(words)))
for s in sentences:                                   # count neighbours within 2 words
    t = s.split()
    for i, w in enumerate(t):
        for j in range(max(0, i - 2), min(len(t), i + 3)):
            if i != j: C[idx[w], idx[t[j]]] += 1

U, S, _ = np.linalg.svd(np.log1p(C))                  # compress counts into dense vectors
vec = U[:, :3] * S[:3]                                # 3-number embedding per word
cos = lambda a, b: vec[idx[a]] @ vec[idx[b]] / np.linalg.norm(vec[idx[a]]) / np.linalg.norm(vec[idx[b]])
print("coffee~tea:", round(cos("coffee", "tea"), 2), "  coffee~car:", round(cos("coffee", "car"), 2))''',
  [("What does cosine similarity measure?", "How closely two vectors point in the same direction."),
   ("What advantage does fastText have for misspelled words?", "It builds vectors from character n-grams, so even unseen or misspelled words get a sensible vector.")])

L("m-text-classification",
  "Text classification assigns a label to a piece of text (spam, topic, sentiment), using anything from word lists to fine-tuned transformers.",
  """It's the most common NLP task in industry: routing tickets, moderating content, tagging reviews, detecting intent in chatbots. It's also the usual first NLP interview problem.""",
  """Approaches, from simplest to strongest:

1. **Lexicon / rules**: count positive and negative words from a list. No training; breaks on sarcasm and negation.
2. **TF-IDF + linear model** (logistic regression, linear SVM, Naive Bayes): fast, strong baseline, needs some labelled data.
3. **Embeddings + classifier**: average word or sentence embeddings, then a small model.
4. **Fine-tuned transformer** (BERT, RoBERTa, DistilBERT): best accuracy with a few thousand labels.
5. **Zero/few-shot LLM prompt**: no or few labels; costlier per prediction.

Evaluate with precision, recall and F1 per class (classes are often imbalanced), and read the mistakes.""",
  [("A lexicon by hand",
    """Positive words {great, love}, negative {bad, slow}. "Great phone but slow charging": +1 − 1 = **0**, neutral. A model trained on labelled reviews might learn "but" shifts weight to the second half."""),
   ("Naive Bayes intuition",
    """P(spam | "free", "winner") is computed from how often each word appears in spam vs normal emails, multiplied together with the prior.""")],
  ("You have 50,000 labelled reviews and need high accuracy. Which approach first, and which as the baseline?",
   "Fine-tune a transformer (e.g. DistilBERT) for accuracy; keep TF-IDF + logistic regression as the baseline."),
  [("Sentiment", "positive, negative or neutral opinion"),
   ("Lexicon", "a list of words with scores"),
   ("Naive Bayes", "a probabilistic classifier that treats words as independent"),
   ("Macro F1", "F1 averaged equally over classes")],
  """A lexicon scorer and a trained Naive Bayes classifier side by side.""",
  r'''from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

POS, NEG = {"great", "love", "excellent", "good"}, {"bad", "slow", "terrible", "broke"}
lexicon = lambda t: sum((w in POS) - (w in NEG) for w in t.lower().split())

train = ["great phone love it", "excellent battery", "terrible screen", "broke after a week",
         "good value", "slow and bad", "love the camera", "bad support"]
y = ["pos", "pos", "neg", "neg", "pos", "neg", "pos", "neg"]
nb = make_pipeline(CountVectorizer(), MultinomialNB()).fit(train, y)

for t in ["great phone but slow charging", "the camera is excellent"]:
    print(f"{t!r}: lexicon score {lexicon(t)}, Naive Bayes -> {nb.predict([t])[0]}")''',
  [("Why do lexicon methods struggle with 'not bad at all'?", "They score words individually and miss negation and context."),
   ("Which metric suits imbalanced text classes?", "Per-class precision/recall and macro F1, not plain accuracy.")])

L("m-language-models",
  "A language model gives the probability of the next word given the previous ones; generating text means picking a next word again and again.",
  """ChatGPT and Claude are language models. Starting from simple counting models shows exactly what "predict the next token" means, and how perplexity measures it.""",
  """- A language model estimates **P(next word | previous words)**.
- **N-gram model**: estimate it by counting. A bigram model uses only the previous word: P(w₂ | w₁) = count(w₁ w₂) / count(w₁).
- **Smoothing**: unseen pairs would get probability 0; add-one (Laplace) smoothing adds 1 to every count.
- **Generation**: start with a word, sample the next from the probabilities, repeat.
- **Perplexity** measures how surprised the model is by real text: lower is better. Roughly, a perplexity of 20 means it's as uncertain as choosing among 20 equally likely words each time.
- Neural language models (RNNs, transformers) replace the counts with a network that can use long contexts.""",
  [("Bigram probabilities by hand",
    """Text: "i like tea . i like coffee . i drink tea .". count(i) = 3, count(i like) = 2, count(i drink) = 1. So P(like | i) = **2/3**, P(drink | i) = **1/3**."""),
   ("Perplexity by hand",
    """A model gives the words of a 3-word sentence probabilities 0.5, 0.25, 0.5. Perplexity = (0.5 × 0.25 × 0.5)^(−1/3) = (0.0625)^(−1/3) ≈ **2.52**.""")],
  ("From the text above, what is P(tea | like)?",
   "count(like tea) = 1, count(like) = 2, so 1/2."),
  [("Language model", "a model of P(next token | previous tokens)"),
   ("Bigram", "a pair of consecutive words"),
   ("Smoothing", "giving unseen events a small probability"),
   ("Perplexity", "how surprised a model is by text; lower is better")],
  """A bigram language model built by counting, used to compute probabilities, generate text and measure perplexity.""",
  r'''import random, math
from collections import Counter, defaultdict

text = "i like tea . i like coffee . i drink tea . you like tea .".split()
pairs = Counter(zip(text, text[1:])); firsts = Counter(text[:-1])
nxt = defaultdict(list)
for (a, b), c in pairs.items(): nxt[a] += [b] * c

P = lambda b, a: pairs[(a, b)] / firsts[a]
print("P(like | i) =", round(P("like", "i"), 3))                 # 0.667

random.seed(1); w, out = "i", ["i"]
for _ in range(6):                                              # generate by sampling the next word
    w = random.choice(nxt[w]); out.append(w)
print("generated:", " ".join(out))

sent = "i like tea .".split()
logp = sum(math.log(P(b, a)) for a, b in zip(sent, sent[1:]))
print("perplexity of 'i like tea .':", round(math.exp(-logp / (len(sent) - 1)), 2))''',
  [("What does a bigram model condition on?", "Only the single previous word."),
   ("Is a perplexity of 5 better or worse than 50?", "Better: the model is less surprised by the text.")])

L("m-topic-models",
  "Topic models discover themes in a pile of documents without labels: each topic is a group of words that appear together, and each document is a mix of topics.",
  """Companies use topic models to see what thousands of customer complaints, reviews or news articles are about, without reading them all.""",
  """- **LDA** (latent Dirichlet allocation): assumes each document is a mixture of topics and each topic is a mixture of words, then infers both from word counts. You choose the number of topics.
- **NMF** (non-negative matrix factorisation): factorise the document × word TF-IDF matrix into documents × topics and topics × words, all non-negative. Often cleaner topics on short texts.
- **BERTopic**: embed documents with a sentence model, cluster the embeddings, then describe each cluster by its most distinctive words. Handles meaning, not just word overlap.

Read a topic by its **top words** and give it a name yourself. Check topics with a human; coherence scores help compare settings.""",
  [("Reading topics",
    """Topic 1 top words: delivery, late, courier, days → "delivery delays". Topic 2: refund, money, return, account → "refunds"."""),
   ("A document as a mixture",
    """A complaint "my parcel was late and I still haven't got my refund" might be 60% delivery delays + 40% refunds.""")],
  ("Topic model output: 'battery, charge, hours, drain'. Name the topic.",
   "Battery life (complaints or comments about the battery)."),
  [("Topic", "a set of words that tend to appear together"),
   ("Document–topic mixture", "how much of each topic a document contains"),
   ("LDA (NLP)", "latent Dirichlet allocation, a probabilistic topic model"),
   ("NMF", "non-negative matrix factorisation")],
  """LDA and NMF on a dozen short complaints, printing the top words of each discovered topic.""",
  r'''from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF

docs = ["parcel delivery was late by days", "courier late again delivery slow", "delivery took ten days late",
        "still waiting for my refund money", "refund not received return processed", "money refund to account delayed",
        "battery drains fast phone hot", "battery life poor charge often", "phone battery charge lasts hours",
        "late courier and refund pending", "battery swelling after charge", "return and refund please"]

def show(model, names):
    for k, comp in enumerate(model.components_):
        print(f"  topic {k}:", ", ".join(names[i] for i in comp.argsort()[::-1][:4]))

cv = CountVectorizer(stop_words="english"); X = cv.fit_transform(docs)
print("LDA"); show(LatentDirichletAllocation(n_components=3, random_state=0).fit(X), cv.get_feature_names_out())
tf = TfidfVectorizer(stop_words="english"); T = tf.fit_transform(docs)
print("NMF"); show(NMF(n_components=3, random_state=0).fit(T), tf.get_feature_names_out())''',
  [("Does a topic model need labelled data?", "No; it's unsupervised."),
   ("How does BERTopic differ from LDA?", "It clusters sentence embeddings (meaning) instead of modelling raw word counts.")])

L("m-attention",
  "Attention lets each word look at every other word and take a weighted mix of their information, with weights based on how relevant they are.",
  """Attention is the core of transformers, and therefore of BERT, GPT, Claude and modern vision models. "Explain self-attention" is one of the most common ML interview questions.""",
  """Each token produces three vectors from its embedding (via learned weight matrices):
- **Query (Q)**: what am I looking for?
- **Key (K)**: what do I contain?
- **Value (V)**: what information do I pass on?

Steps for one token:
1. Score it against every token: **score = Q · K**.
2. Divide by **√d** (d = vector size) to keep the numbers in a stable range.
3. **Softmax** the scores into weights that add up to 1.
4. Output = weighted sum of all the **V** vectors.

All at once: **Attention(Q, K, V) = softmax(QKᵀ / √d) V**.

- **Self-attention**: Q, K and V all come from the same sentence.
- **Multi-head attention**: run several attentions in parallel, each learning a different kind of relationship (grammar, coreference…), then combine.
- **Masking**: in GPT-style models a token may only attend to **earlier** tokens (a causal mask), so it can't see the future when predicting the next word.""",
  [("Weights by hand",
    """Sentence "the cat sat". For "sat", scores Q·K with (the, cat, sat) = (1, 4, 2), d = 4 so divide by 2 → (0.5, 2, 1). Softmax → **(0.14, 0.63, 0.23)**: "sat" mostly attends to "cat" (who sat)."""),
   ("Output by hand",
    """With values the = (1, 0), cat = (0, 1), sat = (1, 1): output = 0.14(1, 0) + 0.63(0, 1) + 0.23(1, 1) = **(0.37, 0.86)**.""")],
  ("Why divide the scores by √d?",
   "With large vectors, dot products get large, softmax becomes nearly one-hot and gradients vanish; dividing keeps them in a good range."),
  [("Query / key / value", "what I'm looking for / what I offer to match / what I pass on"),
   ("Attention weights", "softmax of the scores; how much each token is used"),
   ("Multi-head", "several attentions in parallel"),
   ("Causal mask", "blocking attention to future tokens")],
  """Scaled dot-product attention from scratch in NumPy, with the worked example and a causal mask.""",
  r'''import numpy as np
def softmax(x): e = np.exp(x - x.max(-1, keepdims=True)); return e / e.sum(-1, keepdims=True)

def attention(Q, K, V, causal=False):
    scores = Q @ K.T / np.sqrt(K.shape[-1])                  # 1-2. dot products, scaled
    if causal:
        scores = scores + np.triu(np.full(scores.shape, -1e9), k=1)   # hide future tokens
    w = softmax(scores)                                      # 3. weights sum to 1 per row
    return w @ V, w                                          # 4. weighted mix of values

# worked example: the query of 'sat' against the keys of 'the', 'cat', 'sat'
q_sat = np.array([[1.0, 1.0, 0.0, 0.0]])
K = np.array([[1, 0, 0, 0], [2, 2, 0, 0], [1, 1, 0, 0]], float)   # gives scores 1, 4, 2
V = np.array([[1, 0], [0, 1], [1, 1]], float)
out, w = attention(q_sat, K, V)
print("weights for 'sat':", w.round(2), " output:", out.round(2))

rng = np.random.default_rng(0); X = rng.normal(size=(3, 4))       # self-attention: Q=K=V from the same tokens
print("causal weights:\n", attention(X, X, X, causal=True)[1].round(2))   # upper triangle is 0''',
  [("Write the attention formula.", "softmax(QKᵀ / √d) V."),
   ("What does the causal mask prevent?", "A token attending to tokens that come after it.")])

L("m-transformer",
  "The transformer replaced step-by-step recurrence with attention, so every token looks at every other token in parallel; stacked attention and feed-forward blocks build understanding.",
  """Since 2017 transformers have taken over NLP, then vision, speech and protein biology. Every LLM is a transformer, so you need to be able to sketch one block.""",
  """**Input**: token embeddings + **positional encodings** (attention has no sense of order by itself, so position information is added).

**One transformer block**:
1. **Multi-head self-attention**: each token gathers information from the others.
2. **Add & normalise**: a residual connection (x + attention(x)) and layer normalisation.
3. **Feed-forward network**: the same small MLP applied to every token separately (expands to ~4× the size, then back).
4. **Add & normalise** again.

Stack N blocks (12 in BERT-base, ~100 in large LLMs).

**Three layouts**:
- **Encoder-only** (BERT): bidirectional attention; for understanding.
- **Decoder-only** (GPT, Claude, Llama): causal attention; for generating.
- **Encoder–decoder** (original transformer, T5): the decoder also attends to the encoder (**cross-attention**); for translation and summarisation.

Why it won: training runs in parallel over all tokens (fast on GPUs), and any token can reach any other in one step (long-range context).""",
  [("Shapes through a block",
    """Batch of 8 sentences, 32 tokens, model size 512 → input (8, 32, 512). Attention and feed-forward keep (8, 32, 512); the feed-forward's inner size is 2,048."""),
   ("Why positional encodings",
    """Without them, "dog bites man" and "man bites dog" contain the same tokens and attention would treat them identically.""")],
  ("Which transformer layout would you use to generate text, and which to classify it?",
   "Generate: decoder-only (GPT-style). Classify: encoder-only (BERT-style), or a decoder with a classification head."),
  [("Positional encoding", "added information about each token's position"),
   ("Residual connection", "adding a sub-layer's input to its output"),
   ("Feed-forward network", "an MLP applied to each token"),
   ("Cross-attention", "decoder tokens attending to encoder outputs")],
  """One transformer block written with PyTorch building blocks, run on a batch, plus PyTorch's ready-made encoder layer.""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)

class Block(nn.Module):
    def __init__(self, d=64, heads=4):
        super().__init__()
        self.attn = nn.MultiheadAttention(d, heads, batch_first=True)
        self.ff = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
    def forward(self, x, mask=None):
        a, _ = self.attn(x, x, x, attn_mask=mask)       # 1. self-attention
        x = self.n1(x + a)                               # 2. add & norm
        return self.n2(x + self.ff(x))                   # 3-4. feed-forward, add & norm

tokens = torch.randint(0, 1000, (8, 32))                 # 8 sentences, 32 token ids
emb, pos = nn.Embedding(1000, 64), nn.Embedding(32, 64)
x = emb(tokens) + pos(torch.arange(32))                  # token + position information
causal = torch.triu(torch.ones(32, 32, dtype=torch.bool), 1)   # True = not allowed (future)
print("decoder-style block output:", tuple(Block()(x, causal).shape))
print("built-in encoder layer     :", tuple(nn.TransformerEncoderLayer(64, 4, batch_first=True)(x).shape))''',
  [("Why do transformers need positional encodings?", "Attention by itself ignores word order."),
   ("Name the two sub-layers of a transformer block.", "Multi-head self-attention and a position-wise feed-forward network (each with residual + layer norm).")])

L("m-tokenization",
  "Transformers read text as tokens, usually pieces of words; the tokenizer decides how rare words are split and how many tokens (and how much cost) a text uses.",
  """Tokens are what LLMs are billed by, what context windows are measured in, and the reason models sometimes can't count letters. Every LLM application must handle them.""",
  """Why not whole words? The vocabulary would be huge and new words ("GoldenHour") would be unknown. Why not characters? Sequences would be very long.

**Subword tokenisers** sit in between: common words stay whole, rare words split into pieces: "unbelievably" → "un", "believ", "ably".

- **BPE** (byte-pair encoding, GPT models): start from characters, then repeatedly **merge the most frequent adjacent pair** into a new token, until the vocabulary reaches the target size (e.g. 50,000–200,000).
- **WordPiece** (BERT): similar, choosing merges that most increase the likelihood of the data; continuation pieces are marked "##".
- **SentencePiece** (T5, Llama): works on raw text including spaces, so it suits any language.

Rules of thumb for English: 1 token ≈ 4 characters ≈ ¾ of a word. A **context window** of 200,000 tokens is roughly 150,000 words.""",
  [("BPE merges by hand",
    """Corpus: "low lower lowest" as characters. The most common pair is "l o" → merge to "lo". Then "lo w" → "low". Now "lower" is "low" + "e" + "r", and further merges might create "er"."""),
   ("Token budget",
    """A 3,000-word report ≈ 4,000 tokens. With a 128k-token context window you could fit about 30 such reports in one prompt.""")],
  ("Roughly how many tokens is a 600-word English email?",
   "About 800 tokens (600 ÷ 0.75)."),
  [("Token", "a unit of text the model reads, often a word piece"),
   ("Vocabulary size", "how many different tokens the tokenizer has"),
   ("BPE", "building tokens by repeatedly merging frequent pairs"),
   ("Context window", "the maximum number of tokens a model can read at once")],
  """Byte-pair encoding learned from scratch on a tiny corpus, then used to tokenise a new word.""",
  r'''from collections import Counter

corpus = ["low", "lower", "lowest", "newest", "widest", "low", "lower"]
words = [list(w) + ["</w>"] for w in corpus]                 # start from characters (+ end marker)

def merge_once(words):
    pairs = Counter(p for w in words for p in zip(w, w[1:]))
    best = max(pairs, key=pairs.get)                         # most frequent adjacent pair
    new = []
    for w in words:
        out, i = [], 0
        while i < len(w):
            if i < len(w) - 1 and (w[i], w[i + 1]) == best: out.append(w[i] + w[i + 1]); i += 2
            else: out.append(w[i]); i += 1
        new.append(out)
    return new, best

merges = []
for _ in range(8):
    words, m = merge_once(words); merges.append(m)
print("learned merges:", ["".join(m) for m in merges])

def tokenize(word):
    toks = list(word) + ["</w>"]
    for a, b in merges:                                       # apply merges in the learned order
        i = 0
        while i < len(toks) - 1:
            if (toks[i], toks[i + 1]) == (a, b): toks[i:i + 2] = [a + b]
            else: i += 1
    return toks
print("'lowest' ->", tokenize("lowest"), "  'slower' ->", tokenize("slower"))''',
  [("What does each BPE step merge?", "The most frequent pair of adjacent tokens in the corpus."),
   ("Why do LLMs struggle to count letters in a word?", "They see subword tokens, not individual characters.")])

L("m-bert-gpt-t5",
  "BERT reads text in both directions to understand it, GPT predicts the next token to generate text, and T5 turns every task into text-in, text-out.",
  """Choosing the right family for a task (classification, generation, translation) is a common interview and design question, and it explains why chatbots are GPT-style.""",
  """| | BERT | GPT | T5 |
| --- | --- | --- | --- |
| Layout | encoder only | decoder only | encoder–decoder |
| Attention | bidirectional (sees left and right) | causal (left only) | encoder bidirectional, decoder causal |
| Pretraining task | **masked language modelling**: hide 15% of tokens, predict them | **next-token prediction** | **span corruption**: hide spans, generate them |
| Best at | classification, NER, search embeddings | generation, chat, reasoning | translation, summarisation, any text-to-text |

- BERT example: "The [MASK] barked at the mailman" → "dog".
- GPT example: "The dog barked at the" → "mailman".
- T5 example: input "summarize: <article>" → output a summary. Every task is phrased as text.

Today's large chat models (GPT-4, Claude, Llama) are **decoder-only**: next-token prediction scales well and covers understanding tasks too.""",
  [("Pick a model",
    """Tagging 100,000 support tickets cheaply and fast: fine-tune a small BERT (e.g. DistilBERT). Writing replies to those tickets: a GPT-style model."""),
   ("Why BERT can't generate fluently",
    """It was trained to fill blanks using both sides of the text; it never learned to produce text left to right.""")],
  ("Which family uses masked-token prediction during pretraining?",
   "BERT (encoder-only)."),
  [("Masked language modelling", "predicting hidden tokens from both sides"),
   ("Causal language modelling", "predicting the next token from the left side only"),
   ("Text-to-text", "framing every task as input text → output text (T5)")],
  """Create the inputs and targets of the three pretraining tasks for one sentence, as plain Python (the real models apply this to billions of sentences).""",
  r'''import random
random.seed(3)
tokens = "the dog barked at the mailman".split()

# BERT: masked language modelling (hide ~15%, at least one token)
i = random.randrange(len(tokens))
print("BERT input :", " ".join(t if j != i else "[MASK]" for j, t in enumerate(tokens)), "-> target:", tokens[i])

# GPT: next-token prediction at every position
for k in range(1, len(tokens)):
    print("GPT  input :", " ".join(tokens[:k]), "-> next:", tokens[k])

# T5: span corruption (replace a span with a sentinel; the target is the span)
s, e = 2, 4
print("T5   input :", " ".join(tokens[:s] + ["<X>"] + tokens[e:]), "-> target: <X>", " ".join(tokens[s:e]))''',
  [("Which family is used for chatbots like Claude?", "Decoder-only (GPT-style)."),
   ("What makes BERT 'bidirectional'?", "Each token can attend to tokens on both its left and right.")])

L("m-huggingface",
  "Hugging Face hosts hundreds of thousands of open models and datasets; the transformers library loads them for text, vision and audio in a few lines.",
  """It's where you'll find a pretrained model for almost any task, and its pipeline, tokenizer and Auto classes are the standard way to use and fine-tune open models. You also deploy demos there (Spaces), like your GoldenHour live demo.""",
  """- **The Hub** (huggingface.co): models, datasets and Spaces (hosted demos), each with a model card.
- **pipeline**: the quickest way to use a model: `pipeline("sentiment-analysis")("I love this")`. It handles tokenising, the model and post-processing.
- **AutoTokenizer / AutoModel…**: load any model by name: `AutoTokenizer.from_pretrained("distilbert-base-uncased")`, `AutoModelForSequenceClassification.from_pretrained(...)`. The tokenizer returns `input_ids` and an `attention_mask`.
- **datasets**: `load_dataset("imdb")` gives ready-to-use, memory-efficient datasets.
- Models download once and are cached; check the **licence** before commercial use.""",
  [("What a tokenizer returns",
    """"I love ML" → input_ids like [101, 1045, 2293, 19875, 102] (101/102 are BERT's start/end tokens) and attention_mask [1, 1, 1, 1, 1]. Padding adds 0s to the mask."""),
   ("Choosing a model",
    """Search the Hub for task "text-classification", filter by language and size; read the model card for training data, accuracy and licence.""")],
  ("What does the attention_mask tell the model?",
   "Which positions are real tokens (1) and which are padding to ignore (0)."),
  [("Hub", "Hugging Face's library of models, datasets and Spaces"),
   ("pipeline", "a one-line wrapper for using a model on a task"),
   ("Auto classes", "load the right model/tokenizer class from a model name"),
   ("Model card", "documentation of a model's data, use and limits")],
  """Standard Hugging Face usage. It downloads small models the first time, so run it in Colab (internet needed).""",
  r'''from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
print(clf(["I love this phone", "The battery is terrible"]))       # labels with scores

name = "distilbert-base-uncased-finetuned-sst-2-english"
tok = AutoTokenizer.from_pretrained(name)
model = AutoModelForSequenceClassification.from_pretrained(name)
batch = tok(["I love this phone", "Bad"], padding=True, return_tensors="pt")
print(batch["input_ids"], batch["attention_mask"])                 # padded ids and mask
with torch.no_grad():
    probs = model(**batch).logits.softmax(-1)
print(probs.round(decimals=3), model.config.id2label)''',
  [("What is the quickest way to try a model on a task?", "transformers.pipeline with the task (and optionally a model name)."),
   ("What should you check on a model card before using a model in a product?", "Its licence, training data, intended use and known limitations.")],
  net=True)

L("m-finetune-bert",
  "Fine-tuning BERT adds a small classification layer on top of the pretrained encoder and trains the whole thing briefly on your labelled examples with a small learning rate.",
  """This is the standard way to get high accuracy on a custom text task (intent detection, ticket routing, toxicity) with a few thousand labels, at a fraction of an LLM's running cost.""",
  """1. **Tokenise** your texts with the model's tokenizer (truncate/pad to e.g. 128 tokens).
2. **Load** `AutoModelForSequenceClassification` with `num_labels` = your number of classes. It's BERT + a new linear layer on the [CLS] token's vector.
3. **Train** for 2–4 epochs with a **small learning rate** (2e-5 to 5e-5), AdamW, a short warm-up and weight decay. More epochs usually overfit.
4. **Evaluate** on a held-out set with accuracy/F1; keep the best checkpoint.
5. Use the **Trainer** API (or a plain PyTorch loop) to handle batches, evaluation and saving.

Tips: start with a smaller model (DistilBERT) for speed; use a multilingual model for mixed languages; watch class imbalance.""",
  [("Sizes",
    """BERT-base has ~110 million parameters. The new head for 5 classes adds 768 × 5 + 5 = **3,845**. All of them are fine-tuned, gently."""),
   ("Training budget",
    """10,000 examples, batch size 16, 3 epochs → about 1,875 steps; minutes on a free Colab GPU.""")],
  ("Why use a learning rate like 2e-5 rather than 1e-3 when fine-tuning BERT?",
   "A large rate would overwrite the pretrained knowledge (catastrophic forgetting) and make training unstable."),
  [("[CLS] token", "a special first token whose vector summarises the input"),
   ("Classification head", "the new linear layer on top"),
   ("Trainer", "Hugging Face's training loop wrapper"),
   ("Catastrophic forgetting", "losing pretrained knowledge by training too hard")],
  """Fine-tune DistilBERT on a small slice of IMDB reviews with the Trainer (run in Colab with a GPU; it downloads the model and data).""",
  r'''from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np

name = "distilbert-base-uncased"
ds = load_dataset("imdb")
train = ds["train"].shuffle(seed=0).select(range(2000)); test = ds["test"].shuffle(seed=0).select(range(500))
tok = AutoTokenizer.from_pretrained(name)
enc = lambda b: tok(b["text"], truncation=True, max_length=128, padding="max_length")
train, test = train.map(enc, batched=True), test.map(enc, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=2)   # BERT + new head
args = TrainingArguments("out", learning_rate=2e-5, num_train_epochs=2, per_device_train_batch_size=16,
                         weight_decay=0.01, warmup_ratio=0.1, eval_strategy="epoch", report_to=[])
acc = lambda p: {"accuracy": (np.argmax(p.predictions, -1) == p.label_ids).mean()}
trainer = Trainer(model=model, args=args, train_dataset=train, eval_dataset=test, compute_metrics=acc)
trainer.train()
print(trainer.evaluate())''',
  [("What is added on top of BERT for classification?", "A linear classification head on the [CLS] representation."),
   ("How many epochs are typical for fine-tuning BERT?", "2–4.")],
  net=True)

L("m-finetune-gpt",
  "Fine-tuning a GPT-style model continues next-token training on your own text (domain documents or instruction/response pairs) so it writes in your style or follows your format.",
  """When prompting isn't enough (a strict output format, a domain's jargon, a company's tone, or a cheaper small model that should behave like a big one), you fine-tune a decoder model.""",
  """- **Causal LM fine-tuning**: feed your text; the loss is next-token prediction, exactly as in pretraining. Teaches style and domain vocabulary.
- **Instruction tuning (SFT)**: train on pairs formatted with the model's **chat template**: "### Instruction: … ### Response: …". The loss is usually computed **only on the response tokens** (mask the prompt), so the model learns to answer, not to repeat questions.
- **Data** matters more than anything: a few thousand clean, consistent examples beat 100,000 noisy ones.
- **Efficiency**: full fine-tuning of a 7B model needs lots of GPU memory; **LoRA/QLoRA** trains small adapter matrices instead (see the PEFT lesson).
- **Generation settings** at the end: max new tokens, temperature, top-p.

Try prompting (and retrieval) first; fine-tune when you need consistent behaviour or lower cost.""",
  [("Loss masking",
    """Example: prompt 40 tokens + response 60 tokens. With masking, the loss uses only the 60 response tokens; prompt positions get label −100 (ignored)."""),
   ("When to fine-tune",
    """A bank needs every answer in a fixed JSON schema with its own risk categories. After prompting fails 8% of the time, fine-tuning on 3,000 examples brings failures under 1%.""")],
  ("Why mask the prompt tokens out of the loss in instruction tuning?",
   "So the model is trained to produce good responses rather than to predict the user's question text."),
  [("SFT", "supervised fine-tuning on instruction/response pairs"),
   ("Chat template", "the exact text format a model expects for messages"),
   ("Label −100", "PyTorch/HF convention for 'ignore this position in the loss'"),
   ("LoRA", "fine-tuning small low-rank adapters instead of all weights")],
  """Instruction-tuning data preparation and a real (tiny) causal-LM training step: a small GPT-style model built from scratch learns one instruction format, with the prompt masked out of the loss.""",
  r'''import torch, torch.nn as nn, torch.nn.functional as F
torch.manual_seed(0)
pairs = [("capital of france?", "paris"), ("capital of india?", "new delhi"), ("capital of japan?", "tokyo")]
text = lambda q, a: f"### Q: {q} ### A: {a}."
chars = sorted({c for q, a in pairs for c in text(q, a)}); stoi = {c: i for i, c in enumerate(chars)}

def example(q, a):
    ids = [stoi[c] for c in text(q, a)]
    n_prompt = len(f"### Q: {q} ### A: ")
    labels = ids[1:] + [-100]
    labels = [-100] * (n_prompt - 1) + labels[n_prompt - 1:]       # only learn the answer part
    return torch.tensor(ids), torch.tensor(labels)

class TinyGPT(nn.Module):                                           # embeddings + causal transformer + LM head
    def __init__(self, V, d=64):
        super().__init__(); self.emb, self.pos = nn.Embedding(V, d), nn.Embedding(64, d)
        self.block = nn.TransformerEncoderLayer(d, 4, 128, batch_first=True, dropout=0.0); self.head = nn.Linear(d, V)
    def forward(self, ids):
        T = ids.shape[1]; mask = torch.triu(torch.ones(T, T, dtype=torch.bool), 1)
        return self.head(self.block(self.emb(ids) + self.pos(torch.arange(T)), src_mask=mask))

model = TinyGPT(len(chars)); opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
for step in range(400):
    loss = sum(F.cross_entropy(model(i[None])[0], l, ignore_index=-100) for i, l in map(lambda p: example(*p), pairs))
    opt.zero_grad(); loss.backward(); opt.step()

prompt = "### Q: capital of japan? ### A: "; ids = [stoi[c] for c in prompt]
for _ in range(6):                                                   # greedy generation
    ids.append(model(torch.tensor([ids]))[0, -1].argmax().item())
print(repr("".join(chars[i] for i in ids[len(prompt):])))''',
  [("What is the training objective when fine-tuning a GPT-style model?", "Next-token prediction (causal language modelling), usually only on response tokens for instruction data."),
   ("What should you try before fine-tuning?", "Better prompting and retrieval (RAG).")])

L("m-decoding",
  "A language model gives a probability for every possible next token; the decoding strategy picks one, trading accuracy, variety and repeatability.",
  """The same model can sound robotic, creative or nonsensical depending on decoding settings. You'll set temperature and top-p in every LLM application.""",
  """- **Greedy**: always take the most likely token. Deterministic; can be repetitive.
- **Beam search**: keep the k best partial sequences at each step and choose the best complete one. Good for translation; dull for chat.
- **Sampling with temperature T**: divide the scores (logits) by T before softmax. T < 1 sharpens (safer), T > 1 flattens (more random). T → 0 behaves like greedy.
- **Top-k**: sample only among the k most likely tokens.
- **Top-p (nucleus)**: sample among the smallest set of tokens whose probabilities add up to p (e.g. 0.9). Adapts to how confident the model is.
- Also: **repetition penalties**, **max tokens** and **stop sequences**.

Low temperature for factual or structured output (code, JSON, extraction); higher for brainstorming and creative writing.""",
  [("Temperature by hand",
    """Logits for (tea, coffee, juice) = (2, 1, 0). T = 1 → probabilities **0.67, 0.24, 0.09**. T = 0.5 → logits (4, 2, 0) → **0.87, 0.12, 0.02**. T = 2 → (1, 0.5, 0) → **0.51, 0.31, 0.19**."""),
   ("Top-p by hand",
    """Sorted probabilities 0.50, 0.30, 0.15, 0.05. With p = 0.8: 0.50 + 0.30 = 0.80, so only the first two tokens can be sampled (renormalised to 0.625, 0.375).""")],
  ("You need an LLM to extract invoice fields into JSON reliably. High or low temperature?",
   "Low (near 0), for consistent, deterministic output."),
  [("Logits", "the raw scores before softmax"),
   ("Temperature", "rescales logits to make choices sharper or flatter"),
   ("Top-k / top-p", "limit sampling to the k best / the smallest set covering probability p"),
   ("Beam search", "keeping several best partial sequences")],
  """Temperature, top-k and top-p implemented on one next-token distribution.""",
  r'''import numpy as np
rng = np.random.default_rng(0)
tokens = np.array(["tea", "coffee", "juice", "water", "soda"])
logits = np.array([2.0, 1.0, 0.0, -0.5, -1.0])
softmax = lambda z: np.exp(z - z.max()) / np.exp(z - z.max()).sum()

for T in [0.5, 1.0, 2.0]:
    print(f"T={T}:", dict(zip(tokens, softmax(logits / T).round(2))))

def top_k(p, k):  q = np.where(p >= np.sort(p)[-k], p, 0); return q / q.sum()
def top_p(p, pp):
    order = np.argsort(p)[::-1]; keep = order[: np.searchsorted(np.cumsum(p[order]), pp) + 1]
    q = np.zeros_like(p); q[keep] = p[keep]; return q / q.sum()

p = softmax(logits)
print("greedy:", tokens[p.argmax()])
print("top-2 :", dict(zip(tokens, top_k(p, 2).round(2))))
print("top-p 0.8:", dict(zip(tokens, top_p(p, 0.8).round(2))))
print("10 samples at T=1:", [str(t) for t in rng.choice(tokens, 10, p=p)])''',
  [("What does temperature below 1 do?", "Sharpens the distribution, making the most likely tokens even more likely."),
   ("How is top-p different from top-k?", "Top-p keeps as many tokens as needed to reach probability p, so the set size adapts; top-k always keeps k.")])

L("m-llms",
  "LLMs are huge decoder-only transformers trained to predict the next token on trillions of tokens, then tuned to follow instructions; powerful, but they can be confidently wrong.",
  """LLMs are now part of most software products. Knowing how they're built explains both what they're good at (language, reasoning, code) and their failure modes (hallucination, stale knowledge, prompt injection), which interviewers always probe.""",
  """**How they're built**:
1. **Pretraining**: next-token prediction on a huge mix of web pages, books and code. The model learns grammar, facts, reasoning patterns and coding. Costs millions of dollars of compute.
2. **Supervised fine-tuning (SFT)**: train on example conversations showing how a helpful assistant answers.
3. **Preference tuning** (RLHF, DPO, constitutional AI): learn from comparisons of better and worse answers, for helpfulness, honesty and safety.

**Scale**: billions to trillions of parameters; context windows of 100k+ tokens.

**Strengths**: writing, summarising, translating, coding, extracting structure, multi-step reasoning, tool use.

**Limits**: **hallucination** (fluent but false statements), a **knowledge cutoff** (no knowledge of recent events without tools), sensitivity to prompt wording, cost and latency, and security risks (prompt injection). Fixes: retrieval (RAG), tools, validation, human review.""",
  [("Training data scale",
    """A modern model may train on ~15 trillion tokens. Reading at 300 words per minute, a person would need over 80,000 years to read that much."""),
   ("A hallucination",
    """Asked for a court case's citation, a model invents a plausible-looking but non-existent case. With RAG over a legal database and a "cite only retrieved sources" rule, this mostly stops.""")],
  ("A user asks an LLM about yesterday's cricket score. Why might it get it wrong, and what's the fix?",
   "Its knowledge stops at its training cutoff; give it a search tool or retrieved up-to-date data."),
  [("Pretraining", "learning next-token prediction on huge text"),
   ("Instruction tuning / SFT", "training on example conversations"),
   ("RLHF / DPO", "tuning on human preferences between answers"),
   ("Hallucination", "a confident, fluent, false statement"),
   ("Knowledge cutoff", "the date after which the model has no training data")],
  """The loop every LLM runs to answer: predict the next token, append it, repeat. Here a tiny character-level 'LLM' (a bigram table learned from text) shows the same loop and also why it can produce fluent nonsense.""",
  r'''import numpy as np
rng = np.random.default_rng(0)
corpus = "the model predicts the next token. the next token is chosen. the answer is generated token by token. "
chars = sorted(set(corpus)); idx = {c: i for i, c in enumerate(chars)}
counts = np.full((len(chars), len(chars)), 1e-3)             # tiny smoothing
for a, b in zip(corpus, corpus[1:]): counts[idx[a], idx[b]] += 1
probs = counts / counts.sum(1, keepdims=True)                # "pretraining": P(next char | char)

out = "th"
for _ in range(60):                                          # generation loop: predict, sample, append
    p = probs[idx[out[-1]]]
    out += chars[rng.choice(len(chars), p=p)]
print(out)   # looks word-like, means nothing: fluency is not truth''',
  [("Name the three training stages of a chat LLM.", "Pretraining, supervised fine-tuning, preference tuning (RLHF/DPO)."),
   ("What is the main way to reduce hallucination about your company's data?", "Retrieval-augmented generation: give the model the relevant documents and ask it to answer from them.")])

L("m-llm-api",
  "Most LLM apps call a model over an API: send a list of messages with roles, get a reply; you manage tokens, cost, streaming and structured output.",
  """Almost every GenAI feature you'll build (chat, summarise, extract, classify) is an API call. Knowing the message format, parameters and costs is basic professional knowledge.""",
  """**A request contains**:
- **model**: which model (bigger = smarter, slower, pricier).
- **system** prompt: the assistant's role and rules.
- **messages**: the conversation, alternating **user** and **assistant** turns. The API is **stateless**: you resend the history every time.
- **max_tokens**, **temperature**, and optional **stop sequences**.

**The response** has the generated content and **usage** (input and output token counts). You pay per token; output tokens usually cost more than input.

**Useful features**: **streaming** (show tokens as they arrive), **structured output / tool use** (ask for JSON matching a schema, or let the model call your functions), and **prompt caching** for long repeated context.

**Engineering**: keep API keys in environment variables (never in code), retry with backoff on rate limits, set timeouts, log token usage, and validate outputs.

Open models (Llama, Mistral, Qwen) can run locally with tools like Ollama or vLLM behind a similar API.""",
  [("Cost by hand",
    """A summary call uses 3,000 input tokens and 300 output tokens. At $3 per million input and $15 per million output: 3,000 × 3/1M + 300 × 15/1M = $0.009 + $0.0045 = **$0.0135**. 10,000 calls a day ≈ $135."""),
   ("Statelessness",
    """Turn 3 of a chat must send turns 1 and 2 again. Long chats get more expensive per turn; summarise old turns to save tokens.""")],
  ("Where should your API key live?",
   "In an environment variable or a secrets manager, never in the source code or a notebook you share."),
  [("System prompt", "instructions that set the assistant's role and rules"),
   ("Role", "who wrote a message: user or assistant"),
   ("Stateless", "the server doesn't remember past calls; you resend history"),
   ("Streaming", "receiving the reply token by token"),
   ("Structured output", "the model returning data in a defined schema, e.g. JSON")],
  """A real call with the Anthropic Python SDK, including a system prompt, history, token usage and streaming. Set `ANTHROPIC_API_KEY` in your environment first (in Colab: Secrets).""",
  r'''import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])   # key from the environment, never hard-coded

history = [{"role": "user", "content": "Explain overfitting in one sentence."}]
reply = client.messages.create(model="claude-sonnet-4-5", max_tokens=200, temperature=0.2,
                               system="You are a concise ML tutor.", messages=history)
print(reply.content[0].text)
print("tokens in/out:", reply.usage.input_tokens, reply.usage.output_tokens)

history += [{"role": "assistant", "content": reply.content[0].text},      # stateless: resend the history
            {"role": "user", "content": "Now give a real-life example."}]
with client.messages.stream(model="claude-sonnet-4-5", max_tokens=200, messages=history) as stream:
    for piece in stream.text_stream:                                      # streaming: print as it arrives
        print(piece, end="", flush=True)''',
  [("Why must you resend earlier messages in every call?", "The API is stateless; the model only sees what's in the current request."),
   ("Which costs more per token, input or output?", "Usually output tokens.")],
  net=True)

L("m-prompt-engineering",
  "Prompt engineering is writing clear instructions and context (role, task, examples, format) so an LLM reliably does what you need, then testing prompts like code.",
  """A better prompt is often the cheapest way to fix an LLM feature. Teams treat prompts as code: versioned, tested on examples and measured.""",
  """Ingredients of a good prompt:

1. **Role and goal**: "You are a support agent for an electronics shop. Classify the customer's email."
2. **Context**: the data the model needs (the email, policy text, retrieved documents), clearly delimited, e.g. inside `<email>…</email>` tags.
3. **Precise instructions and constraints**: what to do, what not to do, what to say if unsure.
4. **Examples (few-shot)**: 2–5 input → output pairs showing the exact format and edge cases.
5. **Output format**: "Answer with JSON: {"category": …, "urgency": 1–3}".
6. **Reasoning**: for multi-step problems, ask it to think step by step before the final answer (chain-of-thought), and put the final answer in a separate tag.

Then **evaluate**: build a test set of 50–200 real inputs with expected outputs, measure accuracy and format errors, change one thing at a time.""",
  [("Zero-shot vs few-shot",
    """Zero-shot: "Classify the sentiment: 'The delivery was okay I guess'." Few-shot adds examples: "'Loved it' → positive; 'Never again' → negative; 'It works' → neutral". Few-shot fixes borderline cases like "okay I guess" → neutral."""),
   ("Measuring a change",
    """Prompt v1: 82% correct on 100 test emails, 6 invalid JSONs. Adding the JSON schema and two examples: 91%, 0 invalid. Keep v2.""")],
  ("A model sometimes answers with extra chatty text around your JSON. Name two prompt fixes.",
   "Specify 'Return only JSON' with the exact schema and an example; or use the API's structured-output / tool feature; validate and retry on failure."),
  [("Zero-shot / few-shot", "no examples / a few examples in the prompt"),
   ("Chain-of-thought", "asking the model to reason step by step"),
   ("Delimiters", "tags or markers separating instructions from data"),
   ("Prompt evaluation set", "test inputs with expected outputs for measuring a prompt")],
  """Building a structured few-shot prompt and an evaluation harness in plain Python; `fake_llm` stands in for a real API call so you can test the harness offline.""",
  r'''import json

EXAMPLES = [("My order arrived broken!!", {"category": "damaged", "urgency": 3}),
            ("Can I change my delivery address?", {"category": "delivery", "urgency": 2})]

def build_prompt(email):
    shots = "\n".join(f"<email>{e}</email>\n{json.dumps(o)}" for e, o in EXAMPLES)
    return ("You classify customer emails for an electronics shop.\n"
            "Return ONLY JSON: {\"category\": damaged|delivery|refund|other, \"urgency\": 1-3}.\n"
            "If unsure, use category \"other\".\n\n" + shots + f"\n\n<email>{email}</email>\n")

def fake_llm(prompt):                       # replace with a real API call (see the LLM API lesson)
    text = prompt.rsplit("<email>", 1)[1].lower()
    cat = "refund" if "refund" in text else "damaged" if "broken" in text or "cracked" in text else "other"
    return json.dumps({"category": cat, "urgency": 3 if "!" in text else 1})

tests = [("I want a refund now!", "refund"), ("Screen cracked on arrival", "damaged"), ("Do you sell cables?", "other")]
ok = bad_json = 0
for email, expected in tests:
    try: ok += json.loads(fake_llm(build_prompt(email)))["category"] == expected
    except (json.JSONDecodeError, KeyError): bad_json += 1
print(build_prompt("Where is my parcel?")[:220], "...")
print(f"accuracy {ok}/{len(tests)}, invalid JSON {bad_json}")''',
  [("What do few-shot examples mainly teach the model?", "The exact output format and how to handle edge cases."),
   ("How do you know a prompt change actually helped?", "Measure it on a fixed evaluation set before and after.")])

L("m-embeddings-vectordb",
  "Embedding models turn sentences into vectors where similar meanings are close; a vector database stores millions of them and finds the nearest ones fast.",
  """This is how semantic search, recommendation by meaning, duplicate detection and the retrieval part of RAG work. It's a core building block of LLM applications.""",
  """- A **sentence embedding model** (e.g. all-MiniLM, BGE, OpenAI/Voyage embeddings) maps a whole text to a vector (384–3,072 numbers). "How do I get my money back?" and "refund process" end up close even with no shared words.
- **Similarity**: cosine similarity (or dot product on normalised vectors).
- **Semantic search**: embed all documents once; at query time embed the query and return the closest documents.
- **Vector database** (FAISS, Chroma, Pinecone, Weaviate, pgvector): stores vectors with metadata and uses **approximate nearest neighbour (ANN)** indexes such as HNSW to search millions of vectors in milliseconds, trading a tiny bit of accuracy for big speed.
- **Hybrid search**: combine keyword search (BM25) with vector search; keywords catch exact names and codes that embeddings blur.""",
  [("Nearest neighbour by hand",
    """Normalised vectors: query (0.8, 0.6). Doc A (0.6, 0.8) → cosine 0.96. Doc B (1, 0) → 0.8. Doc C (0, −1) → −0.6. Ranking: **A, B, C**."""),
   ("Why ANN",
    """10 million documents × 768 dimensions: exact search compares 7.7 billion numbers per query. An HNSW index checks only a few thousand vectors and still finds ~99% of the true top results.""")],
  ("Query 'invoice INV-20931 status'. Why might pure vector search miss the right document, and what fixes it?",
   "Embeddings blur exact IDs like INV-20931; add keyword (BM25) search in a hybrid retriever."),
  [("Sentence embedding", "a vector representing a whole text's meaning"),
   ("Vector database", "a store optimised for finding nearest vectors"),
   ("ANN / HNSW", "approximate nearest-neighbour search / a popular graph index for it"),
   ("Hybrid search", "combining keyword and vector search")],
  """A tiny semantic search: TF-IDF + SVD vectors stand in for an embedding model so it runs offline; the commented lines show the sentence-transformers version you'd use for real.""",
  r'''import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors

docs = ["How to request a refund for a damaged item", "Refund money back to card within 7 days",
        "Track your parcel with the tracking number", "Change the delivery address of an order",
        "Battery replacement and warranty claims", "Return an item and get your money back"]
tfidf = TfidfVectorizer().fit(docs)
svd = TruncatedSVD(n_components=4, random_state=0).fit(tfidf.transform(docs))
embed = lambda texts: (v := svd.transform(tfidf.transform(texts))) / np.linalg.norm(v, axis=1, keepdims=True)
# Real embeddings:  from sentence_transformers import SentenceTransformer
#                   embed = SentenceTransformer("all-MiniLM-L6-v2").encode

index = NearestNeighbors(n_neighbors=2, metric="cosine").fit(embed(docs))   # the "vector database"
dist, ids = index.kneighbors(embed(["how do I get my money back"]))
for d, i in zip(dist[0], ids[0]):
    print(f"similarity {1 - d:.2f}  {docs[i]}")''',
  [("What does a vector database optimise?", "Fast (approximate) nearest-neighbour search over many vectors, with metadata filters."),
   ("Why combine keyword and vector search?", "Keywords catch exact terms and IDs; vectors catch meaning and paraphrases.")])

L("m-rag",
  "Retrieval-augmented generation answers questions from your own documents: find the most relevant chunks, put them in the prompt, and have the LLM answer only from them, with citations.",
  """RAG is the most common way companies use LLMs on their own data (policies, manuals, contracts, tickets). It reduces hallucination and needs no fine-tuning. Expect to design one in an interview.""",
  """**Indexing (done once)**:
1. Load documents (PDFs, pages, tickets).
2. **Chunk** them into passages of ~200–500 tokens with some overlap, keeping titles/metadata.
3. **Embed** each chunk and store it in a vector database.

**Answering (each question)**:
4. Embed the question and **retrieve** the top-k (e.g. 3–5) most similar chunks.
5. Build a prompt: instructions + the retrieved chunks (labelled with their source) + the question.
6. The LLM **generates** an answer using only those chunks, citing sources, and says "I don't know" if the answer isn't there.

**Evaluate both parts**: retrieval (did the right chunk come back? recall@k) and generation (is the answer faithful to the chunks and correct?).""",
  [("Chunk counts",
    """A 60-page handbook ≈ 30,000 words ≈ 40,000 tokens. With 400-token chunks and 50-token overlap: about **115 chunks**."""),
   ("A grounded answer",
    """Question: "How many days to return an item?" Retrieved chunk [policy.pdf p3]: "Items can be returned within 30 days of delivery." Answer: "Within 30 days of delivery [policy.pdf p3]".""")],
  ("RAG gives a wrong answer. What two places should you check first?",
   "Retrieval (were the right chunks retrieved at all?) and generation (did the model follow the chunks, or did the prompt allow guessing?)."),
  [("Chunk", "a passage of a document stored for retrieval"),
   ("Retriever", "the component that finds relevant chunks"),
   ("Grounding", "answering only from provided sources"),
   ("Recall@k", "share of questions whose correct chunk is in the top k retrieved"),
   ("Faithfulness", "whether the answer is supported by the retrieved text")],
  """A complete mini RAG pipeline offline: chunk, index with TF-IDF vectors, retrieve, and build the grounded prompt. Swap `answer_with_llm` for a real API call to finish it.""",
  r'''import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import PorterStemmer

handbook = {"policy.pdf": "Items can be returned within 30 days of delivery. Refunds go to the original card within 7 days. "
                          "Damaged items are replaced free of charge. Gift cards cannot be refunded.",
            "shipping.pdf": "Standard delivery takes 3 to 5 days. Express delivery takes 1 day in metro cities. "
                            "You can change the delivery address before the item is shipped."}

chunks = [(src, s.strip() + ".") for src, text in handbook.items() for s in text.split(".") if s.strip()]  # 1 sentence per chunk
stem = PorterStemmer().stem                                        # 'returned'/'return' and 'items'/'item' match
vec = TfidfVectorizer(tokenizer=lambda t: [stem(w) for w in re.findall(r"[a-z0-9]+", t.lower())], token_pattern=None)
M = vec.fit_transform([c for _, c in chunks])

def retrieve(q, k=2):
    sims = (M @ vec.transform([q]).T).toarray().ravel()
    return [chunks[i] for i in sims.argsort()[::-1][:k]]

def build_prompt(q):
    ctx = "\n".join(f"[{src}] {text}" for src, text in retrieve(q))
    return ("Answer using ONLY the sources below and cite them like [file]. "
            "If the answer is not in the sources, say \"I don't know.\"\n\n" + ctx + f"\n\nQuestion: {q}\nAnswer:")

def answer_with_llm(prompt):          # replace with a real LLM call; here we return the top source line
    return prompt.split("\n")[2]

q = "How many days do I have to return an item?"
print(build_prompt(q)); print("->", answer_with_llm(build_prompt(q)))''',
  [("What are the two stages of answering in RAG?", "Retrieve relevant chunks, then generate an answer grounded in them."),
   ("Why chunk documents instead of embedding whole files?", "Smaller passages give more precise retrieval and fit in the prompt.")])

L("m-langchain",
  "LangChain and LlamaIndex give ready-made building blocks (prompt templates, model wrappers, output parsers, retrievers, tools) and connect them into chains and agents.",
  """Many companies prototype LLM apps with these frameworks, and job descriptions name them. Knowing what they abstract (and when plain code is simpler) is what interviewers look for.""",
  """**LangChain** pieces:
- **Prompt templates**: prompts with placeholders, filled at run time.
- **Chat models**: a common wrapper over Anthropic, OpenAI, local models…
- **Output parsers**: turn the model's text into strings, JSON or typed objects.
- **Retrievers**: fetch documents from a vector store.
- **Chains** with the pipe syntax (LCEL): `prompt | model | parser`. Each part is a "Runnable" with `.invoke()`, `.batch()` and `.stream()`.
- **Agents and tools** (with LangGraph for stateful, multi-step flows).

**LlamaIndex** focuses on data: loading, indexing and querying documents for RAG in a few lines.

Use them to move fast and swap providers; use plain code when the flow is simple and you want full control.""",
  [("A chain in words",
    """Template "Summarise for a {audience}: {text}" → chat model → string parser. Calling it with audience = "manager" fills the template, calls the model and returns plain text."""),
   ("Swapping models",
    """Changing the model wrapper from one provider to another leaves the rest of the chain unchanged.""")],
  ("In `prompt | model | parser`, what does each part receive?",
   "The prompt receives your input variables; the model receives the filled prompt; the parser receives the model's message and returns clean output."),
  [("Runnable", "any LangChain component with invoke/batch/stream"),
   ("LCEL", "LangChain Expression Language: composing with the | pipe"),
   ("Output parser", "converts model output to a usable format"),
   ("LlamaIndex", "a framework focused on indexing and querying data for LLMs")],
  """A real LangChain chain (prompt | model | parser). A fake model is used so it runs offline; replace it with `ChatAnthropic(model=...)` from `langchain_anthropic` for real answers.""",
  r'''from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.runnables import RunnableLambda

prompt = ChatPromptTemplate.from_messages([("system", "You summarise text for a {audience} in one line."),
                                           ("human", "{text}")])
model = FakeListChatModel(responses=["Sales rose 12% because of the festival offers."])   # stand-in model
# from langchain_anthropic import ChatAnthropic; model = ChatAnthropic(model="claude-sonnet-4-5")
chain = prompt | model | StrOutputParser()                     # LCEL pipe: template -> model -> text

print(prompt.invoke({"audience": "manager", "text": "Q3 report ..."}).to_messages()[0].content)
print(chain.invoke({"audience": "manager", "text": "Q3 report: sales up 12 percent, driven by Diwali offers."}))

shout = chain | RunnableLambda(lambda s: s.upper())            # chains compose like functions
print(shout.invoke({"audience": "manager", "text": "..."}))''',
  [("What does the | operator do in LangChain?", "Connects runnables so one component's output becomes the next one's input."),
   ("When might plain Python be better than LangChain?", "For simple flows where you want full control and fewer dependencies.")])
