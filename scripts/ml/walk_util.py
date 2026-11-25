"""Real-data walkthroughs for the ML concept cards.

Every walkthrough follows a few actual rows of a real dataset through the method, step by step, so the reader
sees what happens to real records instead of abstract numbers. All numbers in the text are computed here from
the data (never typed by hand). Run `python3 generate_walks.py` to rebuild walks.json, which the board build reads.
"""
import os, functools
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
WALKS = {}

SOURCES = {
    "titanic": "**Titanic passengers** — 891 real passengers of the 1912 sinking, with class, sex, age, fare and whether they survived ([Kaggle / Data Science Dojo](https://github.com/datasciencedojo/datasets)).",
    "housing": "**California housing** — real 1990 US census districts: median income, house age, rooms, population, location and median house value (3,000-district sample of the 20,640; [StatLib via *Hands-On ML*](https://github.com/ageron/handson-ml2)).",
    "sms": "**SMS Spam Collection** — 5,572 real text messages from the UK and Singapore, each labelled spam or ham (normal) ([UCI](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)).",
    "mpg": "**Auto MPG** — 398 real cars from 1970–82 with cylinders, horsepower, weight, origin and fuel efficiency in miles per gallon ([UCI](https://archive.ics.uci.edu/dataset/9/auto+mpg)).",
    "penguins": "**Palmer penguins** — 344 real penguins measured in Antarctica: species, island, bill length/depth, flipper length, body mass ([palmerpenguins](https://allisonhorst.github.io/palmerpenguins/)).",
    "flights": "**Airline passengers** — real monthly international airline passengers (thousands), 1949–1960 (Box & Jenkins).",
    "tips": "**Restaurant tips** — 244 real restaurant bills recorded by a waiter: total bill, tip, day, time, party size.",
    "digits": "**Handwritten digits** — 1,797 real scanned handwritten digits, 8 × 8 pixels each, values 0–16 ([UCI](https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits)).",
    "cancer": "**Breast cancer (Wisconsin)** — 569 real biopsies: 30 measurements of cell nuclei and whether the tumour was malignant or benign ([UCI](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic)).",
    "wine": "**Wine** — 178 real Italian wines from three cultivars, with 13 chemical measurements ([UCI](https://archive.ics.uci.edu/dataset/109/wine)).",
    "iris": "**Iris** — 150 real iris flowers of three species with sepal and petal sizes (Fisher, 1936).",
    "books": "**Goodreads ratings** — real 1–5 star ratings from 600 Goodreads readers of the 40 most-rated books ([goodbooks-10k](https://github.com/zygmuntz/goodbooks-10k)).",
    "spoken": "**Free Spoken Digit Dataset** — real recordings of 6 people saying the digits 0–9 (8 kHz); 600 of the 3,000 clips are used ([FSDD](https://github.com/Jakobovski/free-spoken-digit-dataset)).",
    "photos": "**Real photographs** bundled with scikit-image: astronaut Eileen Collins (NASA), a camera-man photo, Greek coins, a cup of coffee, and 200 small face / non-face crops from Labeled Faces in the Wild ([skimage.data](https://scikit-image.org/docs/stable/api/skimage.data.html)).",
    "frozenlake": "**FrozenLake** — the classic 4 × 4 slippery-ice grid world from Gymnasium, a standard reinforcement-learning test environment ([Gymnasium](https://gymnasium.farama.org/environments/toy_text/frozen_lake/)).",
    "karate": "**Zachary's karate club** — the real friendship network of 34 members of a university karate club that split into two groups (Zachary, 1977).",
    "speech": "**Speech recording** — a real 14-second clip of read English speech at 16 kHz (LibriSpeech, via the [librosa sample data](https://github.com/librosa/data)).",
}


@functools.lru_cache(None)
def D(name):
    """Load a dataset as a DataFrame (or a dict for images/graph/audio)."""
    if name == "titanic":
        df = pd.read_csv(os.path.join(DATA, "titanic.csv"))
        df["Who"] = df["Name"].str.replace(r"\s*\(.*\)", "", regex=True).str.replace('"', "").str.slice(0, 28)
        return df
    if name == "housing":
        return pd.read_csv(os.path.join(DATA, "housing.csv")).reset_index(drop=True)
    if name == "sms":
        return pd.read_csv(os.path.join(DATA, "sms.tsv"), sep="\t", header=None, names=["label", "text"])
    if name == "spoken":
        z = np.load(os.path.join(DATA, "spoken_digits.npz")); o = z["offsets"]
        return dict(clips=[z["audio"][o[i]:o[i + 1]].astype(float) / 32768 for i in range(len(o) - 1)], label=z["label"], speaker=z["speaker"], sr=8000)
    if name in ("astronaut", "camera", "coins", "coffee", "chelsea", "lfw_subset"):
        import skimage.data as sd; return getattr(sd, name)()
    if name == "books":
        return pd.read_csv(os.path.join(DATA, "books_ratings.csv"))
    if name in ("mpg", "penguins", "flights", "tips"):
        return pd.read_csv(os.path.join(DATA, name + ".csv"))
    from sklearn import datasets
    if name == "digits":
        return datasets.load_digits()
    if name == "cancer":
        b = datasets.load_breast_cancer(as_frame=True); df = b.frame.copy()
        df["diagnosis"] = np.where(df["target"] == 0, "malignant", "benign"); return df
    if name == "wine":
        b = datasets.load_wine(as_frame=True); df = b.frame.copy(); df["cultivar"] = "C" + (df["target"] + 1).astype(str); return df
    if name == "iris":
        b = datasets.load_iris(as_frame=True); df = b.frame.copy(); df["species"] = np.array(b.target_names)[b.target]; return df
    if name == "karate":
        import networkx as nx; return nx.karate_club_graph()
    if name == "speech":
        import soundfile as sf; x, sr = sf.read(os.path.join(DATA, "speech.ogg")); return x, sr
    raise KeyError(name)


def fmt(v, nd=2):
    if isinstance(v, (bool, np.bool_)): return "yes" if v else "no"
    if isinstance(v, (int, np.integer)): return f"{int(v):,}"
    if isinstance(v, (float, np.floating)):
        if np.isnan(v): return "missing"
        if abs(v) >= 1000: return f"{v:,.0f}"
        return f"{v:.{nd}f}".rstrip("0").rstrip(".") if nd else f"{v:.0f}"
    return str(v).replace("|", "/")


def t(df, n=None, nd=2, index=False):
    """A markdown table of a DataFrame (all rows if n is None)."""
    if isinstance(df, pd.Series): df = df.to_frame()
    if n is not None: df = df.head(n)
    cols = ([df.index.name or ""] if index else []) + [str(c) for c in df.columns]
    rows = []
    for idx, r in df.iterrows():
        rows.append(([fmt(idx, nd)] if index else []) + [fmt(v, nd) for v in r.values])
    out = "| " + " | ".join(cols) + " |\n| " + " | ".join("---" for _ in cols) + " |\n"
    return out + "\n".join("| " + " | ".join(r) + " |" for r in rows)


def pct(x, nd=0): return f"{100 * x:.{nd}f}%"


def walk(cid, data):
    """Register a walkthrough generator. The function returns (steps, takeaway); steps = [(heading, markdown)]."""
    def deco(fn):
        assert cid not in WALKS, cid
        WALKS[cid] = (data, fn)
        return fn
    return deco


def build_all(only=None):
    """Build every registered walkthrough (or only those defined in the modules named in `only`)."""
    out = {}
    for cid, (data, fn) in list(WALKS.items()):
        if only and fn.__module__ not in only: continue
        np.random.seed(0)
        steps, takeaway = fn()
        assert len(steps) >= 3, cid
        srcs = [data] if isinstance(data, str) else list(data)
        out[cid] = dict(data=" ".join(SOURCES[s] for s in srcs), steps=[dict(h=h, md=m.strip()) for h, m in steps], takeaway=takeaway.strip())
    return out
