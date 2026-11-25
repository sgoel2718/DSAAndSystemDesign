"""Beginner lessons: Unsupervised learning."""
from lesson_util import L

L("m-unsup-overview",
  "Unsupervised learning finds structure in data that has no answer column: groups, simpler summaries, unusual points and patterns.",
  """Most data in the world has no labels, because labelling costs time and money. Unsupervised methods still extract value from it: customer segments, compressed features, fraud alerts, product recommendations.""",
  """Four main jobs, all without labels:

- **Clustering**: put similar examples in the same group (customer segments, grouping news stories).
- **Dimensionality reduction**: describe each example with fewer numbers while keeping most information (for visualisation, speed or noise removal).
- **Anomaly detection**: flag examples that don't look like the rest (fraud, faulty machines).
- **Association and recommendation**: find what goes together ("people who bought X also bought Y").

The hard part: with no answers, there's no simple accuracy. You judge results with internal scores (like the silhouette score), with domain experts, or by how much they help a later task.""",
  [("Clustering example",
    """Shoppers described by (visits per month, average spend): (2, 300), (3, 350), (20, 80), (22, 90). Two obvious groups: "rare big spenders" and "frequent small spenders". Nobody labelled them; the structure is in the data."""),
   ("Dimensionality reduction example",
    """A 28 × 28 image has 784 numbers. PCA can describe handwritten digits with about 50 numbers and still keep about 80% of the variation.""")],
  ("A bank has millions of transactions but only a few confirmed frauds. Which unsupervised job could help?",
   "Anomaly detection: flag transactions that look very different from normal behaviour, then have analysts check them."),
  [("Unlabelled data", "examples without an answer column"),
   ("Cluster", "a group of similar examples"),
   ("Anomaly", "an example that doesn't fit the usual pattern"),
   ("Embedding / representation", "a compact list of numbers describing an example")],
  """Three unsupervised jobs on the same data, in a few lines each.""",
  r'''from sklearn.datasets import load_iris
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest

X = load_iris().data                                    # we ignore the labels completely
groups = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(X)
print("clusters:", groups[:10])

X2 = PCA(n_components=2).fit_transform(X)               # 4 numbers per flower -> 2
print("reduced shape:", X2.shape)

flags = IsolationForest(random_state=0).fit_predict(X)  # -1 = looks unusual
print("unusual flowers:", (flags == -1).sum())''',
  [("Why can't you simply compute accuracy for clustering?", "There are no true labels to compare with."),
   ("Name the four main unsupervised jobs.", "Clustering, dimensionality reduction, anomaly detection, association/recommendation.")])

L("m-kmeans",
  "k-means splits data into k groups by repeating two steps: assign each point to its nearest centre, then move each centre to the average of its points.",
  """k-means is the default clustering method: simple, fast on millions of points, and used for customer segmentation, image colour compression and as a step inside other systems.""",
  """1. Choose **k**, the number of groups.
2. Place k centres (centroids), e.g. at k random points.
3. **Assign**: each point joins its nearest centre.
4. **Update**: move each centre to the mean of the points assigned to it.
5. Repeat 3–4 until the assignments stop changing.

It minimises the **inertia**: the total squared distance from points to their centres.

**Choosing k**: the **elbow method** (plot inertia against k and look for the bend) and the **silhouette score** (how much closer each point is to its own cluster than to the next one; from −1 to 1, higher is better). Scale features first; k-means likes round, similar-sized groups.""",
  [("One round by hand",
    """Points on a line: 1, 2, 10, 11, 12. Start centres at 1 and 2. Assign: {1} to centre 1; {2, 10, 11, 12} to centre 2. Update: centres become 1 and (2 + 10 + 11 + 12)/4 = 8.75."""),
   ("Second round",
    """Assign: 1 and 2 are closer to 1 (2 is 1 away vs 6.75); 10, 11, 12 go to 8.75. Update: centres **1.5** and **11**. Next round nothing changes: converged.""")],
  ("Centres at 0 and 10. Which cluster does the point 4 join, and which does 6 join?",
   "4 is 4 from 0 and 6 from 10, so it joins the 0 cluster. 6 joins the 10 cluster."),
  [("Centroid", "the centre (mean) of a cluster"),
   ("Inertia", "total squared distance from points to their centroids"),
   ("Elbow method", "picking k where adding clusters stops helping much"),
   ("Silhouette score", "how well each point fits its own cluster versus the next")],
  """The hand example, then choosing k on blob data with inertia and silhouette.""",
  r'''import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score

x = np.array([[1], [2], [10], [11], [12]])
print(KMeans(n_clusters=2, n_init=10, random_state=0).fit(x).cluster_centers_.ravel())   # [ 1.5 11. ]

X, _ = make_blobs(n_samples=600, centers=4, random_state=0)
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    print(k, "inertia", round(km.inertia_), " silhouette", round(silhouette_score(X, km.labels_), 3))''',
  [("What two steps does k-means repeat?", "Assign each point to the nearest centre; move each centre to the mean of its points."),
   ("Why scale features before k-means?", "It uses distances, so a feature with large numbers would dominate.")])

L("m-hierarchical",
  "Hierarchical clustering repeatedly merges the two closest groups, building a tree (dendrogram) you can cut at any height to get any number of clusters.",
  """You don't have to choose k in advance, and the tree itself is informative: it shows which groups are close relatives, useful for taxonomies, gene data and document organisation.""",
  """**Agglomerative** (bottom-up) clustering:

1. Start with every point as its own cluster.
2. Find the two closest clusters and merge them.
3. Repeat until one cluster remains.

"Closest" between two clusters is defined by the **linkage**: **single** (closest pair of points), **complete** (farthest pair), **average** (average distance), or **Ward** (merge that increases total variance least, usually the best default).

The merges are drawn as a **dendrogram**: the height of each join is the distance at which it happened. Cut horizontally to get clusters.""",
  [("Merge by hand",
    """Points on a line: 1, 2, 6, 7, 15. Closest pairs: 1–2 (distance 1) and 6–7 (1), merged first. Then {1, 2} with {6, 7} (average linkage: about 5). Last, 15 joins (about 11)."""),
   ("Cut the tree",
    """Cut at height 3 → three clusters: {1, 2}, {6, 7}, {15}. Cut at height 8 → two clusters: {1, 2, 6, 7}, {15}.""")],
  ("Why is hierarchical clustering slow on a million points?",
   "It compares distances between all pairs of clusters, roughly n² memory and time or worse."),
  [("Agglomerative", "bottom-up: start with single points and merge"),
   ("Linkage", "the rule for the distance between two clusters"),
   ("Dendrogram", "the tree diagram of merges"),
   ("Ward linkage", "merges that increase within-cluster variance the least")],
  """The hand example with SciPy: the merge table and cutting into 2 and 3 clusters.""",
  r'''import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster

x = np.array([[1], [2], [6], [7], [15]])
Z = linkage(x, method="average")          # each row: the two clusters merged and the distance
print(Z.round(2))
print("3 clusters:", fcluster(Z, t=3, criterion="maxclust"))
print("2 clusters:", fcluster(Z, t=2, criterion="maxclust"))''',
  [("Do you need to choose the number of clusters before running it?", "No; you cut the dendrogram afterwards."),
   ("What does the height of a merge in the dendrogram show?", "The distance between the two clusters when they were merged.")])

L("m-dbscan-gmm",
  "DBSCAN finds clusters as dense areas of any shape and marks lonely points as noise; Gaussian mixtures model clusters as overlapping bell curves with soft memberships.",
  """k-means fails on curved or uneven clusters and forces every point into a group. These two methods cover the gaps: DBSCAN for odd shapes plus noise, GMMs when you want probabilities of belonging.""",
  """**DBSCAN**:
- Two settings: **eps** (a radius) and **min_samples**.
- A **core point** has at least min_samples points within eps. Core points close to each other form a cluster, together with their neighbours.
- Points that aren't near any core point are **noise** (label −1).
- No k needed; finds any shape.

**Gaussian mixture model (GMM)**:
- Assumes the data comes from k overlapping bell-shaped (Gaussian) groups, each with its own centre and spread.
- Fitted with the **EM algorithm**: E-step: compute each point's probability of belonging to each group; M-step: update the groups using those probabilities. Repeat.
- Gives **soft** assignments: "70% group A, 30% group B".""",
  [("DBSCAN by hand",
    """eps = 1.5, min_samples = 3, points on a line: 1, 2, 3, 10, 11, 12, 30. Point 2 has 1, 2, 3 within 1.5 → core. Clusters {1, 2, 3} and {10, 11, 12}; 30 has no neighbours → **noise**."""),
   ("GMM soft membership",
    """A point halfway between two groups of equal size and spread gets about **50% / 50%**. k-means would force it into one.""")],
  ("Which method would you use to find ring-shaped clusters with some noise points?",
   "DBSCAN: it follows dense regions of any shape and labels sparse points as noise."),
  [("eps", "DBSCAN's neighbourhood radius"),
   ("Core point", "a point with enough neighbours within eps"),
   ("Noise", "points DBSCAN leaves out of every cluster"),
   ("EM algorithm", "alternating soft assignment (E) and parameter update (M)")],
  """Two moons: k-means cuts them wrongly, DBSCAN finds them; then GMM soft probabilities.""",
  r'''from sklearn.datasets import make_moons, make_blobs
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score

X, y = make_moons(n_samples=400, noise=0.05, random_state=0)
print("k-means agreement:", round(adjusted_rand_score(y, KMeans(2, n_init=10, random_state=0).fit_predict(X)), 2))
print("DBSCAN agreement :", round(adjusted_rand_score(y, DBSCAN(eps=0.2, min_samples=5).fit_predict(X)), 2))

B, _ = make_blobs(n_samples=300, centers=[[0, 0], [3, 0]], random_state=0)
gmm = GaussianMixture(n_components=2, random_state=0).fit(B)
print("soft membership of the midpoint:", gmm.predict_proba([[1.5, 0]]).round(2))''',
  [("What label does DBSCAN give to noise points?", "−1."),
   ("What is the difference between hard and soft clustering?", "Hard puts each point in exactly one cluster; soft gives a probability for each cluster.")])

L("m-curse-dim",
  "With many features, data becomes sparse and distances stop being meaningful, so models need far more data; reducing dimensions helps.",
  """It explains why adding hundreds of columns can make a model worse, why kNN breaks on high-dimensional data, and why we use PCA, embeddings and feature selection.""",
  """Three effects as the number of features (dimensions) grows:

1. **Space explodes**: to cover a line with points 0.1 apart you need 10 points; a square needs 100; a 10-dimensional cube needs 10¹⁰.
2. **Everything is far apart**: most of a high-dimensional cube's volume is near its edges, so data is sparse.
3. **Distances look alike**: the nearest and farthest points end up at almost the same distance, so "nearest neighbour" loses meaning.

Remedies: dimensionality reduction (PCA, embeddings), feature selection, models with regularisation, and more data.""",
  [("Coverage needs",
    """Grid with 10 values per feature: 1 feature = 10 cells, 3 features = 1,000, 10 features = 10,000,000,000 cells. With 10,000 examples, almost every cell is empty."""),
   ("Distance concentration",
    """With 2 random features, the farthest point might be 10 times farther than the nearest. With 1,000 features the ratio is close to 1.1: everyone is about equally far.""")],
  ("Why does kNN suffer more from the curse than a random forest?",
   "kNN relies entirely on distances, which lose meaning in many dimensions; trees split on one feature at a time."),
  [("Dimension", "one feature / one axis of the data space"),
   ("Sparse", "few points for the amount of space"),
   ("Distance concentration", "nearest and farthest distances becoming similar")],
  """Measure how the ratio of farthest to nearest distance shrinks as the number of features grows.""",
  r'''import numpy as np
rng = np.random.default_rng(0)
for d in [2, 10, 100, 1000]:
    X = rng.random((500, d))                    # 500 random points in d dimensions
    dist = np.linalg.norm(X - X[0], axis=1)[1:] # distances from the first point
    print(f"{d:5d} features: farthest / nearest = {dist.max() / dist.min():.2f}")''',
  [("What happens to the farthest/nearest distance ratio as dimensions grow?", "It approaches 1: all points become about equally far."),
   ("Name two remedies.", "Dimensionality reduction (PCA, embeddings) and feature selection; also more data and regularisation.")])

L("m-pca",
  "PCA rotates the data onto new axes ordered by how much they vary, so you can keep the first few and drop the rest with little information lost.",
  """PCA is the standard tool to compress features, remove noise, speed up models and draw high-dimensional data in 2-D. It's also a frequent interview question because it ties together variance, covariance and eigenvectors.""",
  """1. **Centre** the data (subtract each feature's mean) and usually **scale** it.
2. Find the direction along which the data **varies most**: that's **principal component 1 (PC1)**.
3. Find the next direction of most variance that is **perpendicular** to PC1: PC2. And so on.
4. **Project** each point onto the first k components: each point is now described by k numbers.

The **explained variance ratio** tells how much of the total variation each component keeps. Mathematically the components are the **eigenvectors** of the covariance matrix, and their eigenvalues are the variances.""",
  [("Two correlated features",
    """Height and weight are strongly correlated: the points form a long diagonal cloud. PC1 runs along the diagonal ("overall size") and might keep **95%** of the variance; PC2 ("heavy for one's height") keeps 5%. Keeping only PC1 halves the data with little loss."""),
   ("Choose k",
    """Explained variance: 0.55, 0.25, 0.10, 0.05, … Cumulative: 0.55, 0.80, 0.90. To keep 90%, use **3 components**.""")],
  ("PCA on 10 features gives explained variance 0.6, 0.3, 0.05, … How many components keep at least 90%?",
   "Two (0.6 + 0.3 = 0.9)."),
  [("Principal component", "a new axis, a mix of the original features"),
   ("Explained variance ratio", "share of total variation one component keeps"),
   ("Projection", "the coordinates of a point on the new axes"),
   ("Eigenvector", "a direction the covariance matrix only stretches, not rotates")],
  """PCA on the digits dataset: how many of the 64 pixels' worth of components you need for 90% of the variance.""",
  r'''import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

X = StandardScaler().fit_transform(load_digits().data)     # 64 features per image
pca = PCA().fit(X)
cum = np.cumsum(pca.explained_variance_ratio_)
print("first 3 components keep:", pca.explained_variance_ratio_[:3].round(3))
print("components needed for 90%:", np.argmax(cum >= 0.90) + 1)

X10 = PCA(n_components=10).fit_transform(X)                # compress 64 -> 10 numbers
print(X.shape, "->", X10.shape)''',
  [("Why centre the data before PCA?", "Components are directions of variance around the mean; without centring the first component points at the mean instead."),
   ("Is PCA supervised?", "No; it never looks at labels.")])

L("m-eigenfaces",
  "Eigenfaces applies PCA to face photos: each component looks like a ghostly face, and any face is a weighted mix of them, a compact code used for recognition.",
  """It's the classic real example of PCA and shows what "a component" means visually. It's also an early face-recognition system and a good story for interviews about dimensionality reduction.""",
  """1. Flatten each face image into one long row of pixel values (64 × 64 → 4,096 numbers).
2. Run PCA on all faces. The **mean face** is the average image. Each component, reshaped back into an image, is an **eigenface**: a pattern of light and dark (lighting direction, nose shape, glasses).
3. Describe any face by its weights on the first ~100 eigenfaces: 4,096 numbers → about 100.
4. To recognise a person, compare these short codes (for example with nearest neighbour or an SVM).""",
  [("Reconstruct a face",
    """face ≈ mean face + 0.8 × eigenface₁ − 0.3 × eigenface₂ + 0.1 × eigenface₃ + … The more components you keep, the sharper the reconstruction."""),
   ("Why it works",
    """Faces are very similar to each other: most pixel combinations never look like a face. So a few directions describe almost all the variation between real faces.""")],
  ("What does the first eigenface often capture?",
   "The biggest source of variation across the photos, often overall lighting or brightness."),
  [("Mean face", "the average of all face images"),
   ("Eigenface", "a principal component shown as an image"),
   ("Face code", "a face's weights on the eigenfaces")],
  """Eigenfaces in miniature on the bundled 8 × 8 digit images (the same method as faces, but no download needed): compress, reconstruct, classify.""",
  r'''import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)                     # each image flattened to 64 pixels
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
pca = PCA(n_components=20, whiten=True).fit(Xtr)        # 20 "eigen-images"
print("mean image shape:", pca.mean_.reshape(8, 8).shape, " component 1 shape:", pca.components_[0].reshape(8, 8).shape)

recon = pca.inverse_transform(pca.transform(Xte[:1]))   # code -> image again
print("reconstruction error:", np.abs(recon - Xte[:1]).mean().round(2))
clf = SVC().fit(pca.transform(Xtr), ytr)                # recognise using the 20-number codes
print("accuracy with 20 numbers per image:", round(clf.score(pca.transform(Xte), yte), 3))''',
  [("How many numbers describe each face after eigenfaces with 100 components?", "100 (its weights on the eigenfaces)."),
   ("Why do faces compress so well with PCA?", "Faces are similar, so most variation lies along a few directions.")])

L("m-lda",
  "Linear discriminant analysis finds the direction that best separates known classes: class means far apart, each class tightly packed.",
  """PCA keeps variance but ignores labels, so it may keep directions that don't separate classes at all. LDA uses the labels, making it a strong supervised way to reduce dimensions and a simple, fast classifier.""",
  """LDA looks for a projection that **maximises**:

(distance between class means)² ÷ (spread within each class)

- Big numerator: classes far apart.
- Small denominator: each class compact.

With C classes it gives at most **C − 1** useful directions (3 classes → 2 dimensions). It also works directly as a classifier by assuming each class is a bell curve with the same spread.

Not to be confused with LDA in NLP (latent Dirichlet allocation, a topic model).""",
  [("PCA vs LDA",
    """Two classes form two long parallel cigars side by side. The biggest variance runs **along** the cigars, so PCA picks that and mixes the classes. LDA picks the direction **across** the cigars, separating them perfectly."""),
   ("The score by hand",
    """Projection A: means 2 and 8, within-class spread 4 → (6²)/4 = **9**. Projection B: means 3 and 5, spread 1 → 4/1 = **4**. LDA prefers A.""")],
  ("How many LDA components can you get with 10 classes?",
   "At most 9 (classes − 1)."),
  [("Between-class scatter", "how far apart the class means are"),
   ("Within-class scatter", "how spread out each class is"),
   ("Supervised dimensionality reduction", "reducing dimensions using the labels")],
  """PCA and LDA both reduce the wine data to 2 numbers; compare how well a simple classifier does on each.""",
  r'''from sklearn.datasets import load_wine
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

X, y = load_wine(return_X_y=True)                  # 13 features, 3 classes
for name, red in [("PCA 2-D", PCA(2)), ("LDA 2-D", LinearDiscriminantAnalysis(n_components=2))]:
    pipe = make_pipeline(StandardScaler(), red, KNeighborsClassifier())
    print(name, cross_val_score(pipe, X, y, cv=5).mean().round(3))''',
  [("What does LDA use that PCA doesn't?", "The class labels."),
   ("What does LDA maximise?", "The separation of class means relative to the spread within classes.")])

L("m-manifold",
  "Manifold methods assume high-dimensional data lies on a curved low-dimensional surface and 'unroll' it; t-SNE and UMAP are used to visualise it.",
  """PCA only finds flat directions. Real data (images, embeddings, single-cell biology) often lies on curved shapes. t-SNE and UMAP plots are how people look at clusters in embeddings, and you'll be asked how to read them correctly.""",
  """Picture a rolled-up sheet of paper (a "Swiss roll") in 3-D. Two points on neighbouring layers are close in 3-D but far apart along the paper. A **manifold** method measures distance **along** the sheet and unrolls it flat.

- **ISOMAP**: distances along a neighbour graph, then lay out the points to match them.
- **LLE**: each point is rebuilt from its neighbours; keep those recipes in 2-D.
- **t-SNE**: keeps each point's **neighbours** together in 2-D. Great pictures of clusters.
- **UMAP**: similar to t-SNE, faster, keeps a bit more global structure, and can transform new points.

Reading t-SNE/UMAP plots: cluster **sizes and distances between clusters are not meaningful**; only "which points are neighbours" is. Results change with the **perplexity** / **n_neighbors** setting.""",
  [("PCA vs t-SNE on digits",
    """PCA in 2-D shows the ten digit classes heavily overlapping. t-SNE in 2-D shows ten fairly clean islands, because it only cares about keeping neighbours together."""),
   ("A misreading to avoid",
    """Two islands far apart on a t-SNE plot are not necessarily more different than two close islands.""")],
  ("Should you train a classifier on t-SNE coordinates?",
   "Usually not: t-SNE is for visualisation; it can't place new points consistently and distorts global distances. Use PCA, UMAP or embeddings for features."),
  [("Manifold", "a curved low-dimensional surface inside a high-dimensional space"),
   ("Perplexity", "t-SNE's setting for roughly how many neighbours each point considers"),
   ("n_neighbors", "the similar setting in UMAP and ISOMAP")],
  """A Swiss roll unrolled by ISOMAP, and t-SNE on the digits.""",
  r'''from sklearn.datasets import make_swiss_roll, load_digits
from sklearn.manifold import Isomap, TSNE
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

X, t = make_swiss_roll(n_samples=800, random_state=0)   # 3-D rolled sheet; t = position along the sheet
flat = Isomap(n_neighbors=10, n_components=2).fit_transform(X)
print("Isomap axis 1 tracks position along the sheet: corr =", round(abs(__import__("numpy").corrcoef(flat[:, 0], t)[0, 1]), 2))

D, y = load_digits(return_X_y=True)
for name, Z in [("PCA", PCA(2).fit_transform(D)), ("t-SNE", TSNE(2, perplexity=30, random_state=0).fit_transform(D))]:
    print(name, "2-D neighbours agree with labels:", cross_val_score(KNeighborsClassifier(), Z, y, cv=3).mean().round(2))''',
  [("What do t-SNE plots preserve well?", "Local neighbourhoods: which points are near each other."),
   ("Name one advantage of UMAP over t-SNE.", "Faster, keeps more global structure, and can transform new points.")])

L("m-anomaly",
  "Anomaly detection flags rare, unusual examples (fraud, intrusions, failing machines), usually with few or no labelled anomalies.",
  """Anomalies are where the money and risk are: one fraudulent payment, one overheating machine. Labels are rare, so most methods learn what "normal" looks like and flag what doesn't fit.""",
  """Common approaches:

- **Statistical**: flag values far from the mean, e.g. |z-score| > 3, or outside 1.5 × IQR from the quartiles.
- **Isolation Forest**: build random trees that split at random values. Unusual points get isolated in **few splits** (short paths) because they're far from the crowd.
- **Local Outlier Factor (LOF)**: a point in a much sparser neighbourhood than its neighbours is an outlier.
- **One-class SVM**: learn a boundary around normal data.
- **Autoencoders**: trained on normal data, they reconstruct anomalies badly; high reconstruction error = anomaly.

Then tune a threshold on the anomaly score using the few known cases and business cost.""",
  [("z-score by hand",
    """Daily payments mean ₹2,000, standard deviation ₹500. A payment of ₹4,200: z = (4,200 − 2,000)/500 = **4.4** > 3 → flag."""),
   ("Isolation intuition",
    """Points: 10, 11, 12, 11, 95. A random split between 12 and 95 isolates 95 in **one** cut; isolating 11 needs several cuts. Short path → anomaly.""")],
  ("Mean 50, standard deviation 5. Is 62 an anomaly by the |z| > 3 rule?",
   "z = 12/5 = 2.4, so no."),
  [("Anomaly score", "a number saying how unusual an example is"),
   ("z-score", "how many standard deviations from the mean"),
   ("Isolation Forest", "random trees where unusual points are isolated quickly"),
   ("Contamination", "the expected share of anomalies, used to set a threshold")],
  """Plant 10 anomalies among 500 normal points and see what Isolation Forest and LOF catch.""",
  r'''import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

rng = np.random.default_rng(0)
normal = rng.normal(0, 1, (500, 2))
weird = rng.uniform(5, 8, (10, 2)) * rng.choice([-1, 1], (10, 2))   # far away points
X = np.vstack([normal, weird]); truth = np.r_[np.zeros(500), np.ones(10)]

iso = IsolationForest(contamination=0.02, random_state=0).fit_predict(X)   # -1 = anomaly
lof = LocalOutlierFactor(contamination=0.02).fit_predict(X)
for name, p in [("IsolationForest", iso), ("LOF", lof)]:
    print(name, "caught", int(((p == -1) & (truth == 1)).sum()), "of 10 planted anomalies")''',
  [("Why do unusual points get short paths in an Isolation Forest?", "They're far from others, so a random split separates them early."),
   ("How can an autoencoder detect anomalies?", "Train it on normal data; anomalies reconstruct badly, so a high reconstruction error flags them.")])

L("m-recsys",
  "Recommenders predict what a user will like: from item features (content-based), from similar users' behaviour (collaborative), or from learned user and item vectors.",
  """Recommendations drive a large share of what people watch, buy and read on Netflix, Amazon, Flipkart and YouTube. Recommender design is one of the most common ML system design interview questions.""",
  """- **Content-based**: recommend items similar to what the user liked, using item features (genre, description). Works for new items; can be narrow.
- **Collaborative filtering**: "users who liked what you liked also liked X". Needs no item features but suffers from **cold start** (new users or items have no history).
- **Matrix factorisation**: fill the users × items rating table by learning a small vector for each user and each item; predicted rating = their **dot product**.
- **Two-tower models** (industry standard): one network encodes users, another items; fast nearest-neighbour search retrieves candidates, then a ranking model orders them.""",
  [("Dot product prediction",
    """User vector (likes action 0.9, likes romance 0.1). Movie A (action 0.8, romance 0.2): 0.9 × 0.8 + 0.1 × 0.2 = **0.74**. Movie B (0.1, 0.9): 0.09 + 0.09 = **0.18**. Recommend A."""),
   ("Collaborative filtering intuition",
    """Asha and Ravi both rated the same 10 movies highly. Ravi loved a movie Asha hasn't seen → recommend it to Asha.""")],
  ("Why is cold start a problem for collaborative filtering?",
   "A brand-new user or item has no ratings, so there's no behaviour to compare; you need content features or popularity as a fallback."),
  [("Cold start", "no history for a new user or item"),
   ("Implicit feedback", "behaviour like clicks and watch time instead of ratings"),
   ("Matrix factorisation", "learning user and item vectors whose dot products predict ratings"),
   ("Retrieval / ranking", "quickly finding candidates, then carefully ordering them")],
  """Matrix factorisation of a tiny ratings table with plain NumPy gradient descent.""",
  r'''import numpy as np
R = np.array([[5, 4, 0, 1], [4, 0, 0, 1], [1, 1, 0, 5], [0, 1, 5, 4]], float)  # users x movies, 0 = not rated
mask = R > 0
rng = np.random.default_rng(0)
U, V = rng.normal(0, 0.1, (4, 2)), rng.normal(0, 0.1, (4, 2))     # 2 hidden "taste" numbers each

for _ in range(3000):
    err = (U @ V.T - R) * mask                    # error only where a rating exists
    U -= 0.01 * (err @ V + 0.02 * U)              # gradient step for users (with a little L2)
    V -= 0.01 * (err.T @ U + 0.02 * V)            # gradient step for movies
print((U @ V.T).round(1))                         # filled table: predictions for the 0 cells too''',
  [("Name the cold-start problem's usual fix.", "Use content features, popularity or onboarding questions until behaviour data exists."),
   ("How does matrix factorisation predict a rating?", "The dot product of the user's vector and the item's vector.")])

L("m-assoc-rules",
  "Association rules find 'if A then B' patterns in shopping baskets, scored by support, confidence and lift.",
  """Retailers use it for shelf layout, bundles and "frequently bought together" offers. The three metrics are a classic interview question.""",
  """For a rule **{A} → {B}** over many transactions:

- **Support(A, B)**: share of all baskets containing both A and B. Is the pattern common enough to matter?
- **Confidence(A → B)**: of baskets with A, the share that also have B = support(A, B) / support(A).
- **Lift(A → B)**: confidence ÷ support(B). Lift > 1 means A **raises** the chance of B; lift = 1 means unrelated.

**Apriori** finds frequent itemsets efficiently using one rule: if an itemset is rare, every larger set containing it is rare too, so skip them.""",
  [("Compute the metrics",
    """100 baskets: 20 have bread, 25 have butter, 15 have both. Support = 15/100 = **0.15**. Confidence(bread → butter) = 15/20 = **0.75**. Lift = 0.75 / 0.25 = **3**: buying bread triples the chance of butter."""),
   ("Why lift matters",
    """Milk is in 80% of baskets. A rule {anything} → {milk} has high confidence just because milk is everywhere. Lift reveals it: confidence 0.8 / support 0.8 = 1, no real link.""")],
  ("Support(A) = 0.4, support(B) = 0.5, support(A and B) = 0.2. What is the lift of A → B?",
   "Confidence = 0.2/0.4 = 0.5; lift = 0.5/0.5 = 1, so A and B are independent."),
  [("Itemset", "a set of products bought together"),
   ("Support", "how often an itemset appears"),
   ("Confidence", "how often B appears when A does"),
   ("Lift", "how much A raises the chance of B compared with chance")],
  """Computing support, confidence and lift for every pair of items with pandas (no extra library needed).""",
  r'''import pandas as pd
from itertools import permutations

baskets = [{"bread", "butter"}, {"bread", "butter", "milk"}, {"milk"}, {"bread", "jam"},
           {"bread", "butter"}, {"milk", "jam"}, {"butter", "milk"}, {"bread", "butter", "jam"}]
items = sorted(set().union(*baskets)); n = len(baskets)
sup = lambda *s: sum(set(s) <= b for b in baskets) / n         # share of baskets containing all of s

rows = []
for a, b in permutations(items, 2):
    if sup(a, b) >= 0.25:                                       # keep reasonably common pairs
        conf = sup(a, b) / sup(a)
        rows.append((a, b, sup(a, b), round(conf, 2), round(conf / sup(b), 2)))
print(pd.DataFrame(rows, columns=["if", "then", "support", "confidence", "lift"]).sort_values("lift", ascending=False))''',
  [("What does a lift below 1 mean?", "Buying A makes B less likely than usual."),
   ("What trick makes Apriori efficient?", "If an itemset is infrequent, all its supersets are infrequent, so they're never counted.")])
