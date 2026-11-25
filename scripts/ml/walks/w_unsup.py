"""Real-data walkthroughs: Unsupervised learning."""
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt

PEN = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]

def _pen():
    from sklearn.preprocessing import StandardScaler
    df = D("penguins").dropna().reset_index(drop=True)
    return df, StandardScaler().fit_transform(df[PEN])


@walk("m-unsup-overview", "penguins")
def _():
    df, Z = _pen()
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.ensemble import IsolationForest
    g = KMeans(3, n_init=10, random_state=0).fit_predict(Z)
    ct = pd.crosstab(pd.Series(g, name="cluster"), df["species"])
    pca = PCA(2).fit(Z)
    odd = IsolationForest(contamination=0.02, random_state=0).fit_predict(Z) == -1
    return [
        ("Hide the species column", f"We give the algorithms only the four body measurements of {len(df)} penguins, no species labels.\n\n{t(df[PEN], 4)}"),
        ("Clustering finds groups", f"k-means with 3 clusters, compared afterwards with the real species:\n\n{t(ct, index=True)}\n\nThe groups it invented line up closely with species it was never told about."),
        ("Dimensionality reduction summarises", f"PCA squeezes the 4 measurements into 2 numbers per penguin that keep **{pct(pca.explained_variance_ratio_.sum())}** of the variation, enough to draw all penguins on a flat chart."),
        ("Anomaly detection flags the unusual", f"An Isolation Forest flags {odd.sum()} penguins as unusual:\n\n{t(df.loc[odd, ['species', 'sex'] + PEN])}"),
    ], "Without any labels, the data's own structure gives groups, compact summaries and outliers."


@walk("m-kmeans", "penguins")
def _():
    df, Z = _pen()
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    rows = []
    for k in range(2, 7):
        km = KMeans(k, n_init=10, random_state=0).fit(Z)
        rows.append({"k": k, "inertia": km.inertia_, "silhouette": silhouette_score(Z, km.labels_)})
    best = max(rows, key=lambda r: r["silhouette"])["k"]
    km2 = KMeans(3, n_init=10, random_state=0).fit(Z)
    cent = pd.DataFrame(km2.cluster_centers_ * df[PEN].std(ddof=0).values + df[PEN].mean().values, columns=PEN).round(1)
    cent["penguins"] = np.bincount(km2.labels_)
    ex = df.loc[[0, 150, 300], ["species"] + PEN].assign(cluster=km2.labels_[[0, 150, 300]])
    return [
        ("Choose k", f"{t(pd.DataFrame(rows), nd=3)}\n\nInertia (total squared distance to the centres) always falls as k grows, so it can't pick k alone. The silhouette score is highest at **k = {best}**{" (Gentoos vs the rest, because Adelie and Chinstrap overlap in size); we still use k = 3 because we know there are 3 species. The silhouette is warning us that two of them overlap" if best != 3 else ""}."),
        ("Centres after convergence (k = 3), in real units", f"{t(cent, index=True)}\n\nEach centre is an 'average penguin' of its group: the algorithm repeated 'assign each penguin to its nearest centre, move each centre to the average of its penguins' until nothing changed."),
        ("Where three real penguins land", f"{t(ex)}\n\nEach penguin joins the centre it's closest to."),
    ], "k-means alternates 'assign each point to the nearest centre' and 'move centres to the average' until nothing changes."


@walk("m-hierarchical", "mpg")
def _():
    df = D("mpg").dropna()
    picks = df[df["name"].isin(["toyota corolla", "honda civic", "ford pinto", "chevrolet impala", "ford galaxie 500", "buick skylark", "datsun 510", "plymouth fury iii"])].drop_duplicates("name")
    from scipy.cluster.hierarchy import linkage, fcluster
    from sklearn.preprocessing import StandardScaler
    cols = ["mpg", "horsepower", "weight"]
    Z = StandardScaler().fit_transform(picks[cols]); L = linkage(Z, "ward")
    names = picks["name"].tolist()
    lab = lambda i: names[int(i)] if i < len(names) else f"group {int(i) - len(names) + 1}"
    merges = pd.DataFrame([{"step": k + 1, "merge": lab(a), "with": lab(b), "distance": d} for k, (a, b, d, _) in enumerate(L)])
    out = picks[["name"] + cols].assign(cluster_2=fcluster(L, 2, "maxclust"), cluster_3=fcluster(L, 3, "maxclust"))
    g3 = out.groupby("cluster_3").agg(cars=("name", ", ".join), avg_mpg=("mpg", "mean"), avg_weight=("weight", "mean")).round(1)
    return [
        ("Eight real cars", f"{t(picks[['name'] + cols])}"),
        ("Merge the closest pair, again and again", f"{t(merges, nd=2)}\n\n'group n' means the cluster created at step n."),
        ("Cut the tree", f"{t(out)}\n\nThe three groups when cut into 3:\n\n{t(g3, index=True)}\n\nThe last, biggest merge (step 7) joins the heavy, powerful cars to everything else: that's the natural 2-group cut."),
    ], "Hierarchical clustering builds a full family tree of merges; you choose the number of clusters afterwards by where you cut."


@walk("m-dbscan-gmm", "penguins")
def _():
    df, Z = _pen()
    from sklearn.cluster import DBSCAN
    from sklearn.mixture import GaussianMixture
    from sklearn.preprocessing import StandardScaler
    Zb = StandardScaler().fit_transform(df[["bill_length_mm", "bill_depth_mm"]])
    db = DBSCAN(eps=0.35, min_samples=10).fit_predict(Zb)
    ct = pd.crosstab(pd.Series(np.where(db == -1, "noise", "cluster " + db.astype(str)), name="DBSCAN"), df["species"])
    sens = pd.DataFrame([{"eps (radius)": e, "clusters found": len(set(l) - {-1}), "noise points": (l == -1).sum()} for e in [0.25, 0.35, 0.5] for l in [DBSCAN(eps=e, min_samples=10).fit_predict(Zb)]])
    g = GaussianMixture(3, random_state=0).fit(Z)
    P = g.predict_proba(Z)
    unsure = np.argsort(P.max(1))[:4]
    ex = df.loc[unsure, ["species", "bill_length_mm", "flipper_length_mm"]].reset_index(drop=True)
    ex = pd.concat([ex, pd.DataFrame(P[unsure], columns=[f"P(group {i})" for i in range(3)]).round(2)], axis=1)
    return [
        ("DBSCAN on bill length + bill depth", f"A penguin with at least 10 neighbours within radius 0.35 (in standardised units) is a core point; connected core points form a cluster; the rest is noise:\n\n{t(ct, index=True)}\n\nNobody told it there are 3 groups: it found {len(set(db) - {-1})}."),
        ("The radius matters a lot", f"{t(sens)}\n\nToo small: lots of penguins are thrown away as noise. Too big: everything merges into one blob."),
        ("Gaussian mixture: soft memberships", f"Most penguins belong almost 100% to one group. These four are the least certain:\n\n{t(ex)}\n\nk-means would force each of them into one group; the mixture says how unsure it is."),
        ("When to use which", "DBSCAN: unknown number of groups, odd shapes, want noise marked. Gaussian mixture: overlapping groups and you want probabilities of belonging."),
    ], "DBSCAN follows dense regions and labels outliers; Gaussian mixtures give each point a probability per group."


@walk("m-curse-dim", "digits")
def _():
    dg = D("digits"); X = dg.data / 16
    rng = np.random.default_rng(0)
    rows = []
    for d in [2, 8, 32, 64]:
        cols = rng.choice(64, d, replace=False)
        dist = np.linalg.norm(X[:, cols] - X[0, cols], axis=1)[1:]
        rows.append({"pixels used": d, "nearest distance": dist.min(), "average distance": dist.mean(), "farthest distance": dist.max(), "nearest as % of average": pct(dist.min() / dist.mean())})
    noise = rng.random((1797, 1000))
    dn = np.linalg.norm(noise - noise[0], axis=1)[1:]
    return [
        ("Distances between real digit images", f"From the first scanned digit to all 1,796 others, using a random subset of pixels:\n\n{t(pd.DataFrame(rows), nd=2)}\n\nWith only 2 pixels some other image matches exactly (distance 0). With 8–64 pixels the nearest real digit stays at about {min(r['nearest as % of average'] for r in rows[1:])}–{max(r['nearest as % of average'] for r in rows[1:])} of the average distance: neighbours are still clearly closer than everything else."),
        ("Pure noise in 1,000 dimensions", f"Random points with 1,000 features: nearest {dn.min():.1f}, average {dn.mean():.1f}, farthest {dn.max():.1f}; the nearest point is **{pct(dn.min() / dn.mean())}** of the average distance. Everything is almost equally far, so 'nearest neighbour' means almost nothing."),
        ("Why real data survives", "Real images are not random: pixels are strongly related, so the digits actually live on a much lower-dimensional surface. That's why PCA and embeddings work."),
    ], "In many dimensions, random points are all about equally far apart; real data escapes this only because it has structure."


@walk("m-pca", "penguins")
def _():
    df, Z = _pen()
    from sklearn.decomposition import PCA
    p = PCA().fit(Z)
    load = pd.DataFrame(p.components_[:2].T, index=PEN, columns=["PC1", "PC2"]).round(2)
    ev = pd.DataFrame({"component": [f"PC{i + 1}" for i in range(4)], "share of variation": p.explained_variance_ratio_, "cumulative": np.cumsum(p.explained_variance_ratio_)})
    proj = pd.DataFrame(p.transform(Z)[:, :2], columns=["PC1", "PC2"]).round(2)
    ex = pd.concat([df[["species"]], proj], axis=1).loc[[0, 150, 300]]
    means = pd.concat([df[["species"]], proj], axis=1).groupby("species").mean().round(2)
    return [
        ("How much each new axis keeps", f"{t(ev, nd=3)}"),
        ("What the new axes mean", f"{t(load, index=True)}\n\nPC1 mixes flipper length, body mass and bill length (with bill depth the other way): it's roughly **overall size**. PC2 is mostly bill shape."),
        ("Real penguins on the new axes", f"{t(ex)}\n\nSpecies averages on PC1/PC2:\n\n{t(means, index=True)}\n\nGentoos sit far along PC1 (big birds); Adelie and Chinstrap separate on PC2 (bill shape)."),
    ], "PCA finds new axes ordered by how much the data varies along them; the first few often have a clear meaning."


@walk("m-eigenfaces", "digits")
def _():
    dg = D("digits")
    from sklearn.decomposition import PCA
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
    Xtr, Xte, ytr, yte = train_test_split(dg.data, dg.target, random_state=0)
    rows = []
    for k in [2, 5, 10, 20, 40]:
        p = PCA(k, whiten=True).fit(Xtr)
        err = np.abs(p.inverse_transform(p.transform(Xte)) - Xte).mean()
        rows.append({"components kept": k, "numbers per image": k, "avg pixel error after rebuild (0-16)": err, "digit accuracy": SVC().fit(p.transform(Xtr), ytr).score(p.transform(Xte), yte)})
    raw = SVC().fit(Xtr, ytr).score(Xte, yte)
    p = PCA(10).fit(Xtr)
    mean_img = pd.DataFrame(p.mean_.reshape(8, 8)).round(0).astype(int)
    return [
        ("The mean image", f"The average of all training digits (an 8 × 8 'ghost' digit):\n\n{t(mean_img)}"),
        ("Every digit = mean + a mix of component images", "Each principal component reshaped to 8 × 8 is an 'eigen-digit' (for faces, an eigenface). A digit is described by how much of each it contains."),
        ("How many components are enough?", f"{t(pd.DataFrame(rows), nd=3)}\n\nWith all 64 raw pixels the same classifier scores **{pct(raw, 1)}**. 20 numbers per image instead of 64 rebuild the digits closely and score {pct(rows[3]["digit accuracy"], 1)}."),
    ], "Eigenfaces/eigen-digits compress images into a short code of component weights that still identifies them."


@walk("m-lda", "wine")
def _():
    df = D("wine")
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    X = df.drop(columns=["target", "cultivar"]); y = df["cultivar"]
    Z = StandardScaler().fit_transform(X)
    lda = LinearDiscriminantAnalysis(n_components=2).fit(Z, y)
    pts = pd.DataFrame(lda.transform(Z), columns=["LD1", "LD2"]); pts["cultivar"] = y
    means = pts.groupby("cultivar").agg(LD1_mean=("LD1", "mean"), LD1_spread=("LD1", "std"), LD2_mean=("LD2", "mean")).round(2)
    a = cross_val_score(make_pipeline(StandardScaler(), PCA(2), KNeighborsClassifier()), X, y, cv=5).mean()
    b = cross_val_score(make_pipeline(StandardScaler(), LinearDiscriminantAnalysis(n_components=2), KNeighborsClassifier()), X, y, cv=5).mean()
    return [
        ("13 chemical measurements, 3 cultivars", f"{t(df[['alcohol', 'malic_acid', 'color_intensity', 'proline', 'cultivar']], 4)}"),
        ("LDA projects onto 2 'discriminant' axes", f"Chosen so the cultivars' averages are far apart and each cultivar is tight:\n\n{t(means, index=True)}"),
        ("Compare with PCA (which ignores labels)", f"Reduce to 2 numbers, then classify with nearest neighbours: PCA **{pct(a, 1)}**, LDA **{pct(b, 1)}**."),
    ], "LDA uses the labels to find the directions that best separate the classes."


@walk("m-manifold", "digits")
def _():
    dg = D("digits")
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score
    X, y = dg.data[:1000], dg.target[:1000]
    rows = []
    for name, Z in [("PCA to 2-D", PCA(2).fit_transform(X)), ("t-SNE to 2-D", TSNE(2, perplexity=30, random_state=0).fit_transform(X))]:
        rows.append({"method": name, "neighbours share the same digit": cross_val_score(KNeighborsClassifier(5), Z, y, cv=5).mean()})
    return [
        ("64-dimensional data", "Each digit image has 64 pixel values, impossible to look at directly."),
        ("Squash to 2 dimensions two ways", f"A good 2-D map keeps similar digits next to each other. Measure it by asking how often a point's 5 nearest neighbours on the map are the same digit:\n\n{t(pd.DataFrame(rows), nd=3)}"),
        ("Read the map carefully", "t-SNE gives ten clean islands, one per digit, because it only tries to keep neighbours together. The sizes of the islands and the distances between them don't mean anything."),
    ], "Manifold methods like t-SNE and UMAP keep neighbourhoods, which makes clusters visible in 2-D."


@walk("m-anomaly", ("housing", "titanic"))
def _():
    df = D("housing").dropna().reset_index(drop=True)
    df["rooms_per_household"] = df["total_rooms"] / df["households"]
    z = (df["rooms_per_household"] - df["rooms_per_household"].mean()) / df["rooms_per_household"].std()
    top = df.assign(z=z).nlargest(4, "z")[["rooms_per_household", "population", "households", "ocean_proximity", "z"]]
    from sklearn.ensemble import IsolationForest
    cols = ["median_income", "rooms_per_household", "population", "median_house_value"]
    flag = IsolationForest(contamination=0.01, random_state=0).fit_predict(df[cols]) == -1
    tf = D("titanic"); q = tf["Fare"].quantile([0.25, 0.75]); iqr = q.iloc[1] - q.iloc[0]
    hi = tf["Fare"] > q.iloc[1] + 1.5 * iqr
    first = (tf.loc[hi, "Pclass"] == 1).mean()
    return [
        ("z-scores on rooms per household", f"Most districts have 4–7 rooms per household. The most extreme:\n\n{t(top, nd=1)}\n\nA z-score above 3 means 'more than 3 standard deviations from the average'. Tiny populations with huge numbers of rooms per household: most likely holiday-home areas, or a data quirk worth checking. Either way, a human should look."),
        ("Isolation Forest on several columns", f"It flags {flag.sum()} of {len(df):,} districts (1%), e.g.:\n\n{t(df.loc[flag, cols], 5, nd=1)}"),
        ("IQR rule on Titanic fares", f"Fares above Q3 + 1.5 × IQR = £{q.iloc[1] + 1.5 * iqr:.0f} count as outliers: {hi.sum()} passengers, {pct(first)} of them first class. Outliers aren't errors; they are rare cases to look at."),
    ], "Anomaly detection learns what normal looks like and flags what doesn't fit; a human decides if it's an error, fraud or just rare."


@walk("m-recsys", "books")
def _():
    r = D("books")
    R = r.pivot_table(index="user_id", columns="title", values="rating")
    me = R.notna().sum(1).idxmin()
    known = R.loc[me].dropna()
    from sklearn.model_selection import train_test_split
    tr, te = train_test_split(r, test_size=0.2, random_state=0)
    Rt = tr.pivot_table(index="user_id", columns="title", values="rating").reindex(index=R.index, columns=R.columns)
    M = Rt.notna().values; mu = np.nanmean(Rt.values); Y = np.nan_to_num(Rt.values - mu)
    rng = np.random.default_rng(0); U = rng.normal(0, .1, (len(R), 5)); V = rng.normal(0, .1, (R.shape[1], 5))
    for _ in range(300):
        E = (U @ V.T - Y) * M
        U -= 0.05 * (E @ V + 0.5 * U) / 10; V -= 0.05 * (E.T @ U + 0.5 * V) / 10
    P = pd.DataFrame(U @ V.T + mu, index=R.index, columns=R.columns).clip(1, 5)
    tp = np.array([P.loc[u, b] for u, b in zip(te.user_id, te.title)])
    base = tr.groupby("title").rating.mean().reindex(te.title).fillna(mu).values
    rm = lambda p: np.sqrt(np.mean((p - te.rating.values) ** 2))
    C = R.sub(R.mean(1), axis=0)
    sims = C.T.corr(min_periods=8).loc[me].drop(me).dropna().sort_values(ascending=False)
    unseen = P.loc[me][R.loc[me].isna()].sort_values(ascending=False)
    return [
        ("Real ratings: most cells are empty", f"{len(r):,} ratings from {len(R)} readers on {R.shape[1]} books; **{pct(R.isna().values.mean())}** of the reader × book table is blank. Reader {me} rated {len(known)} books, e.g.:\n\n{t(known.sort_values(ascending=False).rename('stars').to_frame(), 6, index=True)}"),
        ("Find readers with similar taste", f"Correlate reader {me}'s ratings with every other reader on the books both rated (at least 8 in common):\n\n{t(sims.rename('similarity').to_frame(), 5, index=True)}"),
        ("Learn hidden taste vectors", f"Matrix factorisation gives every reader and every book 5 numbers so that reader · book ≈ rating. Tested on 20% of ratings it never saw: error (RMSE) **{rm(tp):.2f} stars**, vs **{rm(base):.2f}** for 'just predict the book's average'."),
        (f"Recommendations for reader {me}", f"Highest predicted ratings among books they haven't rated:\n\n{t(unseen.rename('predicted stars').to_frame(), 5, index=True)}"),
    ], "Recommenders fill the empty cells of a ratings table using people with similar taste or learned reader and item vectors."


@walk("m-assoc-rules", "tips")
def _():
    df = D("tips")
    rows = []
    items = {"Sunday": df["day"] == "Sun", "Dinner": df["time"] == "Dinner", "Smoker": df["smoker"] == "Yes", "Party of 4+": df["size"] >= 4, "Big tip (≥ 20%)": df["tip"] / df["total_bill"] >= 0.2, "Big bill (> $30)": df["total_bill"] > 30}
    for a in items:
        for b in items:
            if a == b: continue
            A, B = items[a], items[b]
            sup = (A & B).mean()
            if sup < 0.05: continue
            conf = sup / A.mean(); lift = conf / B.mean()
            rows.append({"if": a, "then": b, "support": sup, "confidence": conf, "lift": lift})
    r = pd.DataFrame(rows).sort_values("lift", ascending=False)
    return [
        ("Each bill as a 'basket' of properties", f"{len(df)} real restaurant bills, turned into yes/no properties such as Sunday, Dinner, Smoker, Party of 4+, Big tip, Big bill."),
        ("Strongest rules by lift", f"{t(r.head(5), nd=2)}"),
        ("Weakest / negative links", f"{t(r.tail(3), nd=2)}\n\nLift above 1: the 'if' part makes the 'then' part more likely; below 1, less likely."),
    ], "Association rules turn co-occurrence counts into 'if A then B' rules, ranked by support, confidence and lift."
