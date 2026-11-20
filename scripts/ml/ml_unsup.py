"""Module 1 (part C): unsupervised learning, clustering, dimensionality reduction, manifold learning, anomalies, recommenders."""
from ml_util import M

UNSUP = [
M("m-unsup-overview", "Unsupervised learning: what it's for", "Basic",
  "Unsupervised learning finds structure in unlabeled data: groups (clustering), compact representations (dimensionality reduction), unusual points (anomaly detection) and co-occurrence rules.",
  """|Task|Question|Algorithms|Example|
|Clustering|which items naturally group together?|k-means, hierarchical, DBSCAN, GMM|customer segmentation|
|Dimensionality reduction|can we describe data with fewer numbers?|PCA, SVD, LDA*, t-SNE, UMAP, autoencoders|visualise 784-pixel digits in 2-D|
|Manifold learning|what low-dimensional surface is the data on?|ISOMAP, LLE, t-SNE, UMAP|unrolling a 'Swiss roll'|
|Density estimation|how likely is this point?|KDE, GMM, normalising flows|anomaly scores|
|Anomaly detection|what's unusual?|isolation forest, LOF, one-class SVM, autoencoders|fraud, machine faults|
|Association rules|what items appear together?|Apriori, FP-growth|market-basket analysis|
|Representation learning|what features describe the data well?|autoencoders, contrastive / self-supervised learning|image embeddings|
(*LDA, linear discriminant analysis, actually uses labels.)

### The challenge: no ground truth
Evaluation uses internal metrics (silhouette, reconstruction error), stability across runs, and above all **usefulness** to the business — do the segments lead to different actions?""",
  code="""
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
X, y = load_digits(return_X_y=True)
Z = PCA(n_components=2).fit_transform(X)
print("64 pixel features ->", Z.shape[1], "PCA components for plotting")
clusters = KMeans(10, n_init=10, random_state=0).fit_predict(X)
print("k-means agreement with true digit labels (ARI, 1 = perfect):", round(adjusted_rand_score(y, clusters), 3))
""",
  say=[("How do you evaluate a clustering when you have no labels?",
        "\"Internal metrics like silhouette score or Davies–Bouldin, stability across random seeds and subsamples, and most importantly whether the clusters are interpretable and actionable — profiling each cluster's feature averages with the business. If a few labels exist, I'd also check adjusted Rand index against them.\"")]),

M("m-kmeans", "k-means clustering, elbow method and silhouette score", "Basic",
  "k-means splits data into k groups by repeatedly assigning each point to the nearest centre and moving each centre to the mean of its points.",
  """### Lloyd's algorithm
1. Pick k initial centroids (**k-means++** spreads them out smartly).
2. **Assign** every point to its nearest centroid.
3. **Update** each centroid to the mean of its points.
4. Repeat until assignments stop changing. Minimises **inertia** (within-cluster sum of squared distances). Converges to a local optimum — run several inits (`n_init`).

### Choosing k
- **Elbow method**: plot inertia vs k; pick the bend.
- **Silhouette score** s = (b − a)/max(a, b), where a = mean distance to own cluster, b = to the nearest other cluster; ranges −1…1, higher is better.
- Gap statistic, domain knowledge, business usefulness.

### Assumptions and limits
Spherical, similar-size clusters; needs scaling; sensitive to outliers; must choose k; fails on moons/rings (use DBSCAN or spectral clustering). **Mini-batch k-means** for big data; **k-medoids** for robustness; k-means also does vector quantisation (colour compression).""",
  demo="kmeans",
  code="""
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

X, _ = make_blobs(600, centers=4, cluster_std=1.0, random_state=42); X = StandardScaler().fit_transform(X)
for k in range(2, 8):
    km = KMeans(k, n_init=10, random_state=0).fit(X)
    print(f"k={k}  inertia={km.inertia_:7.1f}  silhouette={silhouette_score(X, km.labels_):.3f}")

rng = np.random.default_rng(0); C = X[rng.choice(len(X), 4, replace=False)]   # from scratch
for it in range(20):
    lab = np.argmin(((X[:, None] - C[None]) ** 2).sum(-1), axis=1)
    newC = np.array([X[lab == j].mean(0) for j in range(4)])
    if np.allclose(newC, C): break
    C = newC
print("from-scratch k-means converged after", it, "iterations; cluster sizes", np.bincount(lab))
""",
  say=[("What are the limitations of k-means?",
        "\"You must choose k; it assumes roughly spherical, similar-sized clusters because it uses Euclidean distance to centroids; it's sensitive to feature scaling, outliers and initialisation, finding only a local optimum. For odd shapes or noise I'd use DBSCAN or HDBSCAN, for overlapping elliptical clusters a Gaussian mixture, and for categorical data k-modes.\"")]),

M("m-hierarchical", "Hierarchical clustering and dendrograms", "Intermediate",
  "Hierarchical clustering builds a tree of clusters by repeatedly merging the closest pair (agglomerative). Cutting the tree at a height gives any number of clusters.",
  """### Agglomerative algorithm
Start with every point as its own cluster → merge the two closest clusters → repeat until one cluster remains. The merge history is a **dendrogram**.

### Linkage (how to measure distance between clusters)
|Linkage|Distance|Behaviour|
|Single|closest pair of points|finds chains/odd shapes; sensitive to noise|
|Complete|farthest pair|compact clusters|
|Average|mean of all pairs|compromise|
|Ward|increase in within-cluster variance|compact, similar sizes (most popular, Euclidean only)|

### Pros and cons
No need to fix k in advance; dendrogram shows structure at all levels (taxonomies, gene expression). But O(n²) memory / O(n² log n)+ time ⇒ fine for thousands of points, not millions; merges are never undone. **Divisive** clustering works top-down instead.""",
  code="""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import make_blobs, make_moons
from sklearn.metrics import adjusted_rand_score

X, y = make_blobs(60, centers=3, random_state=1)
Z = linkage(X, method="ward")
print("last 3 merges (cluster a, cluster b, distance, size):\\n", Z[-3:].round(2))
print("cut into 3 clusters, sizes:", np.bincount(fcluster(Z, t=3, criterion="maxclust"))[1:])
d = dendrogram(Z, no_plot=True); print("dendrogram leaves order (first 10):", d["ivl"][:10])

Xm, ym = make_moons(300, noise=0.04, random_state=0)
for link in ("single", "complete", "average", "ward"):
    lab = AgglomerativeClustering(2, linkage=link).fit_predict(Xm)
    print(f"moons, {link:8s} linkage ARI = {adjusted_rand_score(ym, lab):.2f}")
""",
  say=[("When would you choose hierarchical clustering over k-means?",
        "\"When I don't know the number of clusters and want to see structure at several levels — the dendrogram shows that — or when clusters are nested, like a product taxonomy. Single linkage can also follow non-spherical shapes. For large datasets k-means or mini-batch k-means is the practical choice because hierarchical clustering is quadratic.\"")]),

M("m-dbscan-gmm", "DBSCAN, HDBSCAN and Gaussian mixture models (EM)", "Intermediate",
  "DBSCAN finds clusters as dense regions of any shape and labels sparse points as noise. Gaussian mixture models assume data comes from several overlapping bell curves and give soft (probabilistic) assignments.",
  """### DBSCAN (density-based spatial clustering of applications with noise)
Parameters **eps** (neighbourhood radius) and **min_samples**. Core points have ≥ min_samples neighbours within eps; clusters grow by connecting core points; points reachable from none are **noise (−1)**. Finds arbitrary shapes, no k needed, robust to outliers. Struggles with varying densities — **HDBSCAN** fixes that. Choose eps from the "knee" of the k-distance plot.

### Gaussian mixture models (GMM)
p(x) = Σ πₖ N(x | μₖ, Σₖ). Fitted with **Expectation–Maximisation (EM)**:
- **E-step**: compute each point's responsibility (probability it belongs to each component).
- **M-step**: update weights, means and covariances using those responsibilities.
Soft clustering, elliptical clusters (full covariance), gives density for anomaly scores; choose k with **BIC/AIC**. k-means is a special case (hard assignments, spherical equal covariances).""",
  code="""
import numpy as np
from sklearn.datasets import make_moons, make_blobs
from sklearn.cluster import DBSCAN, KMeans, HDBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score

X, y = make_moons(400, noise=0.06, random_state=0)
X = np.vstack([X, np.random.default_rng(0).uniform(-1.5, 2.5, (20, 2))]); y = np.r_[y, [-1] * 20]
db = DBSCAN(eps=0.2, min_samples=5).fit_predict(X)
print("DBSCAN clusters:", len(set(db) - {-1}), " noise points:", (db == -1).sum(), " ARI:", round(adjusted_rand_score(y, db), 2))
print("k-means ARI on moons:", round(adjusted_rand_score(y, KMeans(2, n_init=10, random_state=0).fit_predict(X)), 2))
print("HDBSCAN clusters:", len(set(HDBSCAN(min_cluster_size=15, copy=True).fit_predict(X)) - {-1}))

Xb, _ = make_blobs(500, centers=3, cluster_std=[1.0, 2.0, 0.5], random_state=3)
for k in (1, 2, 3, 4, 5):
    print(f"GMM k={k}  BIC={GaussianMixture(k, random_state=0).fit(Xb).bic(Xb):.0f}")
g = GaussianMixture(3, random_state=0).fit(Xb)
print("soft assignment of one point:", g.predict_proba(Xb[:1]).round(3), " log-density:", g.score_samples(Xb[:1]).round(2))
""",
  say=[("How does the EM algorithm work for Gaussian mixtures?",
        "\"It alternates two steps. In the E-step, given current Gaussians, it computes for each point the probability that it came from each component. In the M-step, it re-estimates each component's weight, mean and covariance as responsibility-weighted averages. Each iteration never decreases the likelihood, so it converges to a local optimum — I run several initialisations and pick k with BIC.\"")]),

M("m-curse-dim", "The curse of dimensionality", "Intermediate",
  "As the number of features grows, data becomes sparse, distances lose meaning and models need exponentially more data. Dimensionality reduction and feature selection fight this.",
  """### What goes wrong in high dimensions
- **Sparsity**: to cover a unit cube with the same density, you need exponentially more points as d grows.
- **Distance concentration**: the nearest and farthest neighbours become almost equally far, so kNN, k-means and RBF kernels weaken.
- **Volume in the corners/shell**: most of a high-dimensional ball's volume lies near its surface.
- **Overfitting**: with more features than samples, models can fit noise perfectly.

### Remedies
Feature selection, dimensionality reduction (PCA, autoencoders), regularisation, more data, models with good inductive biases (CNNs share weights), and domain knowledge. Real data often lies on a **low-dimensional manifold** — that's why ML works at all.""",
  code="""
import numpy as np
rng = np.random.default_rng(0)
for d in (2, 10, 100, 1000, 10000):
    X = rng.uniform(size=(500, d)); q = rng.uniform(size=d)
    dist = np.linalg.norm(X - q, axis=1)
    print(f"d={d:6d}  (farthest - nearest) / nearest = {(dist.max() - dist.min()) / dist.min():.3f}")
print("fraction of a 100-D unit cube's volume within the central cube of side 0.9:", 0.9 ** 100)
""",
  say=[("What is the curse of dimensionality?",
        "\"As features increase, the space grows exponentially, so data becomes sparse and you need far more samples to learn reliably. Distances between points also become nearly equal, which hurts distance-based methods like kNN and clustering. The fixes are feature selection, dimensionality reduction like PCA, regularisation and more data.\"")]),

M("m-pca", "Principal component analysis (PCA)", "Intermediate",
  "PCA rotates the data to new axes (principal components) ordered by how much variance they capture, so you can keep the first few and drop the rest with minimal information loss.",
  """### Steps
1. **Standardise** features (PCA is scale-sensitive).
2. Compute the covariance matrix Σ = XᵀX/(n − 1) of centred data.
3. **Eigendecomposition** of Σ (or SVD of X): eigenvectors = principal components (directions), eigenvalues = variance along them.
4. Sort by eigenvalue; project onto the top k: Z = X·W_k.
5. **Explained variance ratio** = λᵢ/Σλ — keep enough components for ~90–95% (scree plot).

### Uses
Visualisation (2-D/3-D), compression, noise reduction (reconstruct from top components), speeding up models, removing multicollinearity, **EigenFaces**.

### Limitations
Linear only (use kernel PCA, t-SNE, UMAP, autoencoders for curved structure); components can be hard to interpret; maximises variance, not class separation (use LDA for that); sensitive to outliers (robust PCA).

### Variants
Incremental PCA (streams), randomized PCA (fast), sparse PCA (interpretable), kernel PCA (non-linear).""",
  demo="pca",
  code="""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(0)
x = rng.normal(size=500); X2 = np.column_stack([x, 0.8 * x + 0.3 * rng.normal(size=500)])
Xc = X2 - X2.mean(0); vals, vecs = np.linalg.eigh(np.cov(Xc.T))           # from scratch
order = vals.argsort()[::-1]; print("eigenvalues", vals[order].round(3), " first PC", vecs[:, order[0]].round(3))
print("sklearn PCA explained variance ratio:", PCA().fit(X2).explained_variance_ratio_.round(3))

X, y = load_digits(return_X_y=True); Xs = StandardScaler().fit_transform(X)
pca = PCA().fit(Xs); cum = np.cumsum(pca.explained_variance_ratio_)
print("components needed for 90% / 95% variance:", np.argmax(cum >= 0.9) + 1, "/", np.argmax(cum >= 0.95) + 1, "of 64")
p10 = PCA(10).fit(Xs); recon = p10.inverse_transform(p10.transform(Xs))
print("reconstruction error with 10 components:", round(((Xs - recon) ** 2).mean(), 3))
""",
  say=[("Explain PCA to someone without maths.",
        "\"Imagine photographing a 3-D object to show it in 2-D: you rotate it to the angle that shows the most detail. PCA does that for data — it finds the directions along which the data varies most, then describes each point by its position along the first few of those directions, throwing away directions with little variation, which are mostly noise.\"")]),

M("m-eigenfaces", "PCA EigenFaces: face recognition with principal components", "Intermediate",
  "EigenFaces applies PCA to face images: each principal component is a ghostly 'eigenface', and any face is approximated as a weighted mix of them. The weights become compact features for recognition.",
  """### Pipeline (Turk & Pentland, 1991)
1. Collect aligned, same-size grayscale face images; flatten each to a vector (e.g. 62×47 = 2,914 pixels).
2. Subtract the **mean face**.
3. PCA → top k eigenvectors (**eigenfaces**), typically 50–150.
4. Represent each face by its k projection coefficients.
5. Recognise by nearest neighbour or an SVM on these coefficients.
6. Reconstruct a face = mean face + Σ coefficientᵢ × eigenfaceᵢ.

### Tricks
With n images ≪ pixels, compute eigenvectors of the small n×n matrix XXᵀ (or use randomised SVD). **Whitening** (scale each component to unit variance) often helps SVMs.

### Limitations and successors
Sensitive to lighting, pose and alignment. **Fisherfaces** (LDA on PCA features) maximise class separation; modern systems use deep CNN embeddings (FaceNet, ArcFace) trained with triplet/angular losses — see Siamese networks.""",
  code="""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_olivetti_faces
from sklearn.pipeline import make_pipeline
try:
    faces = fetch_olivetti_faces(); X, y, shape = faces.data, faces.target, (64, 64)    # 400 faces, 40 people
except Exception:
    rng = np.random.default_rng(0)                                                       # offline fallback: synthetic 'faces'
    protos = rng.random((40, 32 * 32)); X = np.repeat(protos, 10, 0) + 0.15 * rng.normal(size=(400, 1024)); y = np.repeat(np.arange(40), 10); shape = (32, 32)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
pca = PCA(n_components=60, whiten=True, random_state=0).fit(Xtr)
print("eigenfaces shape:", pca.components_.shape, "-> each is a", shape, "image")
print("variance kept by 60 eigenfaces:", round(pca.explained_variance_ratio_.sum(), 3))
clf = make_pipeline(PCA(60, whiten=True, random_state=0), SVC(C=10, gamma=0.001 if shape == (64, 64) else "scale")).fit(Xtr, ytr)
print("EigenFaces + SVM recognition accuracy:", round(clf.score(Xte, yte), 3))
coef = pca.transform(Xte[:1]); recon = pca.inverse_transform(coef)
print("reconstruction error of a test face:", round(float(((Xte[:1] - recon) ** 2).mean()), 4))
""",
  say=[("How do EigenFaces work, and why aren't they used today?",
        "\"PCA on aligned face images gives eigenfaces — the main directions of variation across faces. Each face is described by its coordinates along the top components, and recognition is nearest neighbour or an SVM in that compact space. They're very sensitive to lighting, pose and alignment because PCA is linear on raw pixels; modern face recognition uses deep CNN embeddings trained with metric-learning losses like triplet or ArcFace.\"")]),

M("m-lda", "Linear discriminant analysis (LDA) for classification and supervised dimensionality reduction", "Intermediate",
  "LDA finds the projection that best separates known classes — maximising distance between class means relative to spread within classes. Unlike PCA, it uses labels.",
  """- Objective: maximise **between-class scatter / within-class scatter** (Fisher's criterion).
- Gives at most **C − 1** components for C classes.
- As a classifier: assumes each class is Gaussian with a **shared covariance** ⇒ linear boundaries. **QDA** allows separate covariances ⇒ quadratic boundaries.
- Good for small data, fast, provides probabilities; used before kNN/SVM as a supervised reducer (Fisherfaces).
- Don't confuse with **Latent Dirichlet Allocation** (also "LDA"), a topic model for text.""",
  code="""
from sklearn.datasets import load_wine
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_wine(return_X_y=True)
print("LDA classifier CV:", cross_val_score(LinearDiscriminantAnalysis(), X, y, cv=5).mean().round(3))
print("QDA classifier CV:", cross_val_score(QuadraticDiscriminantAnalysis(), X, y, cv=5).mean().round(3))
for name, red in [("PCA (2D)", PCA(2)), ("LDA (2D)", LinearDiscriminantAnalysis(n_components=2))]:
    s = cross_val_score(make_pipeline(StandardScaler(), red, KNeighborsClassifier(5)), X, y, cv=5).mean()
    print(f"kNN after {name}: {s:.3f}")
""",
  say=[("PCA vs LDA?",
        "\"PCA is unsupervised and keeps the directions of maximum variance, whatever the labels. LDA is supervised and keeps the directions that best separate the classes — maximum between-class versus within-class variance — giving at most classes minus one components. For classification preprocessing LDA often works better; for compression or visualising unlabeled data, PCA.\"")]),

M("m-manifold", "Manifold learning: ISOMAP, LLE, t-SNE and UMAP", "Advanced",
  "Manifold learning assumes high-dimensional data lies on a curved low-dimensional surface and 'unrolls' it. t-SNE and UMAP are the standard tools for visualising embeddings.",
  """### The manifold hypothesis
Images of a rotating object vary along one angle even though they have thousands of pixels. Linear PCA can't unroll curved structures like the **Swiss roll**.

|Method|Idea|Preserves|Notes|
|ISOMAP|kNN graph → shortest-path (geodesic) distances → classical MDS|global geometry|sensitive to noise and n_neighbors|
|LLE (locally linear embedding)|reconstruct each point from its neighbours, keep weights in low-D|local linear patches|fast; can collapse|
|MDS (multidimensional scaling)|preserve pairwise distances|distances|classical MDS = PCA on distances|
|t-SNE|match neighbour probabilities (Gaussian in high-D, Student-t in low-D)|local clusters|great pictures; slow; non-parametric (can't transform new points); cluster sizes/distances not meaningful; tune perplexity (5–50)|
|UMAP|fuzzy topological graph, optimised layout|local + more global structure|faster, scales, can transform new data|
|Spectral embedding|eigenvectors of the graph Laplacian|connectivity|basis of spectral clustering|

### Practical tips
Run PCA to ~50 dims first; try several perplexities/seeds; don't over-interpret distances between t-SNE clusters; use these for **visualisation and exploration**, not as model features (except UMAP sometimes).""",
  code="""
import numpy as np
from sklearn.datasets import make_swiss_roll, load_digits
from sklearn.manifold import Isomap, LocallyLinearEmbedding, TSNE, trustworthiness
from sklearn.decomposition import PCA
from scipy.stats import spearmanr

X, t = make_swiss_roll(1000, noise=0.05, random_state=0)       # t = position along the roll
for name, m in [("PCA", PCA(2)), ("ISOMAP", Isomap(n_neighbors=10, n_components=2)), ("LLE", LocallyLinearEmbedding(n_neighbors=12, n_components=2, random_state=0))]:
    Z = m.fit_transform(X)
    best = max(abs(spearmanr(Z[:, i], t).statistic) for i in range(2))
    print(f"{name:7s} recovers the roll position (|spearman| up to 1): {best:.2f}")

Xd, yd = load_digits(return_X_y=True)
Z = TSNE(2, perplexity=30, init="pca", random_state=0).fit_transform(PCA(30).fit_transform(Xd))
print("t-SNE trustworthiness (neighbour preservation):", round(trustworthiness(Xd, Z, n_neighbors=10), 3))
""",
  say=[("What should you be careful about when reading a t-SNE plot?",
        "\"t-SNE preserves local neighbourhoods, not global geometry, so cluster sizes and distances between clusters aren't meaningful, and results change with perplexity and the random seed — you can even see clusters in random noise. I'd run several settings, use PCA initialisation, and treat it as exploration, confirming any finding with proper metrics.\"")]),

M("m-anomaly", "Anomaly and outlier detection", "Intermediate",
  "Anomaly detection finds rare, unusual points — fraud, intrusions, failing machines — often with few or no labelled examples of the anomalies.",
  """### Approaches
|Method|Idea|
|Statistical|z-score, IQR, Mahalanobis distance, control charts|
|Isolation Forest|anomalies are isolated with fewer random splits ⇒ shorter path length|
|Local Outlier Factor (LOF)|point's density vs its neighbours' density|
|One-Class SVM|learn a boundary around normal data|
|GMM / KDE|low probability density ⇒ anomaly|
|Autoencoder|trained on normal data; high reconstruction error ⇒ anomaly|
|Forecast residuals|time series: actual far from predicted|
|Supervised classifier|when you have enough labelled anomalies (treat as imbalanced classification)|

### Setting the threshold
Use a contamination estimate or a percentile of scores on normal data; validate with whatever labelled anomalies exist (precision@k, PR-AUC).

### Types
Point anomalies, **contextual** (30°C is normal in May, not December), **collective** (a sequence is unusual). Concept drift means "normal" changes — retrain regularly.""",
  code="""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.metrics import roc_auc_score

rng = np.random.default_rng(0)
normal = rng.normal(0, 1, (950, 2)); anomalies = rng.uniform(-6, 6, (50, 2))
X = np.vstack([normal, anomalies]); y = np.r_[np.zeros(950), np.ones(50)]
iso = IsolationForest(contamination=0.05, random_state=0).fit(X)
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
ocs = OneClassSVM(nu=0.05, gamma=0.1).fit(normal)
scores = {"Isolation Forest": -iso.score_samples(X), "LOF": (lof.fit_predict(X), -lof.negative_outlier_factor_)[1], "One-Class SVM": -ocs.score_samples(X)}
for name, s in scores.items():
    print(f"{name:17s} ROC-AUC = {roc_auc_score(y, s):.3f}")
mu, cov = normal.mean(0), np.cov(normal.T); d = X - mu
maha = np.sqrt(np.einsum("ij,jk,ik->i", d, np.linalg.inv(cov), d))
print(f"{'Mahalanobis':17s} ROC-AUC = {roc_auc_score(y, maha):.3f}")
""",
  say=[("How does Isolation Forest detect anomalies?",
        "\"It builds many random trees that split on random features at random thresholds. Anomalies are few and different, so they get isolated into their own leaf after only a few splits, while normal points need many. The average path length across trees becomes the anomaly score — short path means anomalous. It's fast, scales well and needs no distance computations.\"")]),

M("m-recsys", "Recommendation systems: content-based, collaborative filtering, matrix factorisation, two-tower", "Intermediate",
  "Recommenders predict what a user will like. Content-based uses item features; collaborative filtering uses patterns of what similar users liked; modern systems combine both with deep learning.",
  """### Approaches
|Approach|Idea|Pros|Cons|
|Popularity|recommend top items|simple baseline, cold start|not personal|
|Content-based|items similar to what the user liked (genres, TF-IDF, embeddings)|works for new items, explainable|filter bubble; needs item features|
|User-based CF|users similar to you liked X|no item features needed|sparse, slow for many users|
|Item-based CF|items co-liked with your items (Amazon's 'customers also bought')|stable, scalable|cold start for new items|
|Matrix factorisation (SVD, ALS)|ratings ≈ user vectors · item vectors (latent factors)|captures hidden tastes, Netflix Prize|cold start|
|Two-tower / deep retrieval|neural user and item encoders, dot product, ANN search|uses all features, scales to billions|needs lots of data|
|Hybrid + ranking|retrieve candidates → rank with a GBDT/deep model → re-rank for diversity|industry standard (YouTube, Netflix)|complex|

### Data
**Explicit** feedback (ratings) vs **implicit** (clicks, watch time, purchases — far more common; treat missing as weak negatives).

### Problems
Cold start (new users/items), sparsity, popularity bias, filter bubbles, evaluation (offline: precision@k, recall@k, NDCG, MAP; online: A/B tests on CTR, watch time).""",
  code="""
import numpy as np
R = np.array([[5, 4, 0, 1, 0], [4, 0, 0, 1, 1], [1, 1, 0, 5, 4], [0, 1, 5, 4, 0], [5, 5, 4, 0, 1.0]])   # users x movies, 0 = unrated
movies = ["Action1", "Action2", "Drama1", "Drama2", "Drama3"]
mask = R > 0

# item-based collaborative filtering: cosine similarity between movie columns
norm = np.linalg.norm(R, axis=0); S = (R.T @ R) / np.outer(norm, norm)
print("most similar to Action1:", movies[np.argsort(S[0])[::-1][1]])

# matrix factorisation with gradient descent: R ~ P Q^T
rng = np.random.default_rng(0); k = 2; P = 0.1 * rng.normal(size=(5, k)); Q = 0.1 * rng.normal(size=(5, k))
for epoch in range(3000):
    E = mask * (R - P @ Q.T)
    P += 0.01 * (E @ Q - 0.02 * P); Q += 0.01 * (E.T @ P - 0.02 * Q)
pred = P @ Q.T
print("training RMSE:", round(float(np.sqrt((E ** 2).sum() / mask.sum())), 3))
u = 1; unseen = np.where(~mask[u])[0]
print(f"user {u} predicted ratings for unseen movies:", {movies[i]: round(float(pred[u, i]), 2) for i in unseen})
""",
  say=[("How would you handle the cold-start problem in recommendations?",
        "\"For new users: popular or trending items, onboarding questions, and context like location or device, switching to personalised results as interactions arrive. For new items: content-based features or embeddings from text and images so they can be matched without interaction history, plus some exploration traffic, like a bandit, to collect feedback quickly. Hybrid and two-tower models that use features handle cold start naturally.\"")]),

M("m-assoc-rules", "Association rules and market-basket analysis (Apriori)", "Intermediate",
  "Association rule mining finds 'if A then B' patterns in transactions, like {bread, butter} → {milk}, measured by support, confidence and lift.",
  """- **Support**(A) = fraction of transactions containing A.
- **Confidence**(A → B) = support(A ∪ B)/support(A) = P(B | A).
- **Lift**(A → B) = confidence / support(B); > 1 means A makes B more likely than usual, = 1 independent, < 1 negative association.
- **Apriori** algorithm: any subset of a frequent itemset is frequent ⇒ grow itemsets level by level, pruning infrequent ones. **FP-Growth** is faster (no candidate generation).
- Uses: product placement, bundles, cross-sell, web-page navigation, medical co-occurrences.""",
  code="""
from itertools import combinations
from collections import Counter
baskets = [{"bread", "milk"}, {"bread", "butter", "milk"}, {"butter", "milk"}, {"bread", "butter"}, {"bread", "butter", "milk", "eggs"},
           {"eggs", "milk"}, {"bread", "butter", "milk"}, {"bread", "eggs"}]
n = len(baskets)
sup = lambda items: sum(items <= b for b in baskets) / n
counts = Counter(frozenset(c) for b in baskets for r in (1, 2) for c in combinations(sorted(b), r))
frequent = {s for s, c in counts.items() if c / n >= 0.3}
print("frequent itemsets:", sorted([sorted(s) for s in frequent], key=len))
for s in [x for x in frequent if len(x) == 2]:
    a, b = sorted(s)
    for A, B in ((a, b), (b, a)):
        conf = sup({A, B}) / sup({A}); lift = conf / sup({B})
        print(f"{A:6s} -> {B:6s} support={sup({A, B}):.2f} confidence={conf:.2f} lift={lift:.2f}")
""",
  say=[("Why is lift more useful than confidence for association rules?",
        "\"Confidence can be high just because the consequent is popular — almost everything 'predicts' milk if most baskets contain milk. Lift divides by the baseline popularity of the consequent, so lift above 1 shows a genuine positive association rather than popularity.\"")]),
]
