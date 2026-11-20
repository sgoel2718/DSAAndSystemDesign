"""Deep layer + end-to-end walkthroughs: Unsupervised learning."""
from deep.util import X

PENGUINS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
HOUSING = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
RETAIL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"
MOVIES = "https://raw.githubusercontent.com/sidooms/MovieTweetings/master/latest/"
RFM = f'''r = pd.read_csv("{RETAIL}", encoding="latin-1").dropna(subset=["CustomerID"])
r = r[(r.Quantity > 0) & (r.UnitPrice > 0)]; r["InvoiceDate"] = pd.to_datetime(r.InvoiceDate, format="mixed"); r["Revenue"] = r.Quantity * r.UnitPrice
now = r.InvoiceDate.max() + pd.Timedelta(days=1)
rfm = r.groupby("CustomerID").agg(recency=("InvoiceDate", lambda d: (now - d.max()).days), frequency=("InvoiceNo", "nunique"), monetary=("Revenue", "sum"))
Z = StandardScaler().fit_transform(np.log1p(rfm))'''
FMNIST = '''import gzip, urllib.request
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
get = lambda f, off: np.frombuffer(gzip.decompress(urllib.request.urlopen(base + f).read()), np.uint8, offset=off)
X = get("t10k-images-idx3-ubyte.gz", 16).reshape(-1, 784) / 255.0; y = get("t10k-labels-idx1-ubyte.gz", 8)'''

X("m-unsup-overview",
  "Unsupervised learning finds structure without labels: **groups** (clustering), **compact representations** (dimensionality reduction), **unusual points** (anomaly detection), **co-occurrence patterns** (association rules) and **similar items** (recommendation). Since there's no ground truth, success is judged by stability, internal metrics and usefulness for a downstream decision.",
  """**Families and objectives.** Clustering: partition to minimise within-cluster distance (k-means), merge closest groups (hierarchical), find dense regions (DBSCAN), fit a mixture density (GMM). Dimensionality reduction: preserve variance (PCA), class separation (LDA, supervised), neighbourhoods (t-SNE/UMAP). Anomaly detection: low density or easy isolation. **Evaluation without labels:** silhouette (cohesion vs separation), Davies–Bouldin, stability across bootstrap samples (ARI between runs), reconstruction error, and — most important — whether the segments/outliers make business sense and drive different actions.""",
  """**Silhouette by hand.** For a point: mean distance to its own cluster a = 2.0, to the nearest other cluster b = 5.0 → s = (b − a)/max(a, b) = 3/5 = **0.6** (well placed). a = 4, b = 4.5 → **0.11** (on the border). Average over points ~0.5+ = clear structure; ~0.2 = weak.""",
  ["Clustering unscaled features", "Believing clusters are 'real' because an algorithm returned them", "Choosing k only by elbow without stability/business checks", "Interpreting t-SNE distances between clusters"],
  ["Segmentation, exploration, pre-processing, monitoring, cold-start problems"], ["When labels exist for the actual objective — use supervised learning"],
  "Online Retail customers (≈4,300) — one dataset through the main unsupervised tasks: RFM features, PCA, k-means segmentation with silhouette and stability, anomaly scores and a segment profile table.",
  ["Build Recency–Frequency–Monetary features per customer", "Log + standardise; PCA to see structure", "k-means for k = 2..8: silhouette and bootstrap stability", "Isolation-forest anomaly scores", "Profile segments and name them"],
  f'''
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
{RFM}
print("customers:", len(rfm)); print(rfm.describe().round(1).loc[["mean", "50%", "max"]])
pca = PCA().fit(Z); print("PCA variance ratio:", pca.explained_variance_ratio_.round(3))
rng = np.random.default_rng(0)
for k in range(2, 8):
    km = KMeans(k, n_init=10, random_state=0).fit(Z)
    aris = [adjusted_rand_score(km.predict(Z), KMeans(k, n_init=10, random_state=s).fit(Z[rng.integers(0, len(Z), len(Z))]).predict(Z)) for s in range(5)]
    print(f"  k={{k}}: silhouette {{silhouette_score(Z, km.labels_, sample_size=3000, random_state=0):.3f}} | bootstrap stability ARI {{np.mean(aris):.2f}}")
k = 4; rfm["segment"] = KMeans(k, n_init=10, random_state=0).fit_predict(Z)
rfm["anomaly"] = IsolationForest(contamination=0.01, random_state=0).fit_predict(Z) == -1
prof = rfm.groupby("segment").agg(customers=("recency", "size"), recency=("recency", "median"), frequency=("frequency", "median"), monetary=("monetary", "median"), anomalies=("anomaly", "sum"))
print(prof.round(0)); print("anomalous customers (top monetary):", rfm[rfm.anomaly].nlargest(3, "monetary")[["recency", "frequency", "monetary"]].round(0).to_dict("records"))
''')

X("m-kmeans",
  "k-means splits data into k groups by repeatedly assigning each point to the nearest centre and moving each centre to the mean of its points. It's fast and simple, and finds compact, roughly spherical, similar-sized clusters — great for customer segmentation, colour quantisation and vector quantisation.",
  """**Objective (inertia).** J = Σᵢ ‖xᵢ − μ_{c(i)}‖². **Lloyd's algorithm:** assignment step (each point to its nearest centre) and update step (each centre to its cluster mean) — each step can only lower J, so it converges, but to a *local* minimum → run several inits (n_init). **k-means++ init:** pick the first centre randomly, then each next centre with probability ∝ D(x)² (squared distance to the nearest chosen centre) — O(log k)-competitive with the optimum. **Choosing k:** elbow of J(k), silhouette, gap statistic, stability, business needs. Mini-batch k-means for large data. Assumes Euclidean geometry and similar variances — scale features, consider log transforms.""",
  """**One iteration by hand.** Points 1, 2, 4, 9, 10 (1-D), k = 2, start centres 1 and 10. Assign: {1, 2, 4} → c₁, {9, 10} → c₂. Update: μ₁ = 7/3 = **2.33**, μ₂ = **9.5**. Re-assign: 4 is 1.67 from 2.33 and 5.5 from 9.5 → stays. Converged; inertia = (1.33² + 0.33² + 1.67²) + (0.5² + 0.5²) = 1.78 + 0.11 + 2.78 + 0.5 = **5.17**.""",
  ["Unscaled or heavy-tailed features", "Trusting a single random initialisation", "Using it on elongated/non-convex clusters", "Picking k only from the elbow"],
  ["Segmentation, compression, initialising other models, large-scale clustering (mini-batch)"], ["Non-spherical clusters, very different cluster sizes/densities, categorical data (use k-modes)"],
  "Online Retail RFM customer features — k-means from scratch with k-means++ initialisation, compare with scikit-learn, choose k with elbow + silhouette, compare random vs k-means++ starts, and run mini-batch k-means.",
  ["Build and scale RFM features", "Implement k-means++ init and Lloyd iterations", "Match sklearn's inertia", "Elbow and silhouette for k = 2..10", "Random vs k-means++ init quality; MiniBatchKMeans speed"],
  f'''
import time, numpy as np, pandas as pd
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
{RFM}
def kmeanspp(A, k, rng):
    C = [A[rng.integers(len(A))]]
    for _ in range(k - 1):
        d2 = ((A[:, None] - np.array(C)[None]) ** 2).sum(-1).min(1); C.append(A[rng.choice(len(A), p=d2 / d2.sum())])
    return np.array(C)
def kmeans(A, k, init="++", seed=0, iters=100):
    rng = np.random.default_rng(seed); C = kmeanspp(A, k, rng) if init == "++" else A[rng.choice(len(A), k, replace=False)]
    for it in range(iters):
        lab = ((A[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        newC = np.array([A[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
        if np.allclose(newC, C): break
        C = newC
    return lab, C, ((A - C[lab]) ** 2).sum(), it + 1
lab, C, J, its = kmeans(Z, 4); sk = KMeans(4, n_init=10, random_state=0).fit(Z)
print(f"from scratch: inertia {{J:.1f}} in {{its}} iterations | sklearn: {{sk.inertia_:.1f}}")
for k in range(2, 11):
    km = KMeans(k, n_init=10, random_state=0).fit(Z); print(f"  k={{k:2d}} inertia {{km.inertia_:8.1f}} silhouette {{silhouette_score(Z, km.labels_, sample_size=3000, random_state=0):.3f}}")
for init in ["random", "++"]:
    Js = [kmeans(Z, 6, init, s)[2] for s in range(10)]; print(f"init {{init:6s}}: inertia best {{min(Js):.1f}} worst {{max(Js):.1f}}")
t = time.perf_counter(); KMeans(6, n_init=3, random_state=0).fit(np.tile(Z, (20, 1))); full = time.perf_counter() - t
t = time.perf_counter(); MiniBatchKMeans(6, batch_size=2048, n_init=3, random_state=0).fit(np.tile(Z, (20, 1))); mb = time.perf_counter() - t
print(f"86k rows: KMeans {{full:.2f}}s vs MiniBatchKMeans {{mb:.2f}}s")
print("segment centres in original units:\\n", pd.DataFrame(np.expm1(StandardScaler().fit(np.log1p(rfm)).inverse_transform(sk.cluster_centers_)), columns=rfm.columns).round(0))
''')

X("m-hierarchical",
  "Hierarchical (agglomerative) clustering starts with every point as its own cluster and repeatedly merges the two closest clusters, producing a **dendrogram** — a tree you can cut at any height to get any number of clusters. You see the structure at every scale, without choosing k up front.",
  """**Linkage = distance between clusters.** Single (closest pair — finds chains, prone to 'chaining'), complete (farthest pair — compact clusters), average (mean pairwise), **Ward** (merge that least increases total within-cluster variance: Δ = (nₐn_b/(nₐ + n_b))‖μₐ − μ_b‖² — like k-means, usually the default). Complexity O(n²) memory, O(n² log n)–O(n³) time → fine for thousands, not millions. **Cophenetic correlation:** correlation between original distances and dendrogram merge heights — how faithfully the tree represents the data. Cut by height (distance threshold) or by number of clusters.""",
  """**By hand (single linkage).** Points A = 0, B = 1, C = 5, D = 6, E = 12. Merge A–B at 1, C–D at 1; then {A, B}–{C, D} at 4 (B to C); then with E at 6 (D to E). Cutting at height 3 gives **{A, B}, {C, D}, {E}**; at height 5 gives {A, B, C, D}, {E}. With complete linkage the last merges happen at 6 and 12 instead.""",
  ["Using single linkage on noisy data (chaining)", "Running on 100k+ points", "Not scaling features", "Reading horizontal order of leaves as meaningful"],
  ["Small/medium data, exploring structure at multiple scales, taxonomies, when k is unknown"], ["Large datasets — use k-means/mini-batch or HDBSCAN"],
  "Penguins — agglomerative clustering with single/complete/average/Ward linkage, cophenetic correlation, a text dendrogram of species-level structure, cluster purity against true species, and cutting by distance threshold.",
  ["Scale the four measurements", "Build linkage matrices for four linkages", "Cophenetic correlation of each", "Cut into 3 clusters; compare to species (ARI, crosstab)", "Cut by distance threshold and print the top of the dendrogram"],
  f'''
import numpy as np, pandas as pd
from scipy.cluster.hierarchy import cophenet, dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler
df = pd.read_csv("{PENGUINS}").dropna(); Z = StandardScaler().fit_transform(df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]])
D = pdist(Z)
for method in ["single", "complete", "average", "ward"]:
    L = linkage(Z, method); c, _ = cophenet(L, D); lab = fcluster(L, 3, "maxclust")
    print(f"  {{method:8s}} cophenetic r {{c:.3f}} | 3-cluster ARI vs species {{adjusted_rand_score(df.species, lab):.3f}} | sizes {{np.bincount(lab)[1:].tolist()}}")
L = linkage(Z, "ward"); print(pd.crosstab(df.species, fcluster(L, 3, "maxclust"), colnames=["cluster"]))
print("last 5 merge heights:", L[-5:, 2].round(2), "-> big jump before 3 clusters suggests k=3")
for h in [5, 10, 20]: print(f"  cut at height {{h}}: {{len(np.unique(fcluster(L, h, 'distance')))}} clusters")
tree = dendrogram(L, truncate_mode="lastp", p=6, no_plot=True); print("top-of-tree leaf groups (sizes):", tree["ivl"])
sk = AgglomerativeClustering(n_clusters=None, distance_threshold=10, linkage="ward").fit(Z); print("sklearn with distance_threshold=10 ->", sk.n_clusters_, "clusters")
''')

X("m-dbscan-gmm",
  "**DBSCAN** groups points that sit in dense regions and labels isolated points as noise — it finds arbitrarily shaped clusters and doesn't need k. **Gaussian mixture models (GMM)** describe data as a blend of k Gaussian blobs and give each point a **probability** of belonging to each cluster (soft clustering), with elliptical shapes.",
  """**DBSCAN.** Parameters ε (radius) and minPts. Core point: ≥ minPts neighbours within ε; border: within ε of a core; noise: neither. Clusters = connected core points + borders. Choose ε from the 'knee' of the sorted k-distance plot (k = minPts). Struggles with varying densities → **HDBSCAN** (hierarchy over ε). **GMM.** p(x) = Σₖ πₖ N(x | μₖ, Σₖ). Fit by **EM**: E-step responsibilities γᵢₖ = πₖN(xᵢ|k)/Σⱼπⱼ N(xᵢ|j); M-step πₖ = mean γ, μₖ = weighted mean, Σₖ = weighted covariance. Each step increases likelihood. Choose k (and covariance type) by **BIC** = −2 log L + params·log n. k-means is the limit of a GMM with equal spherical covariances and hard assignments.""",
  """**E-step by hand (1-D).** Two components N(0, 1) and N(4, 1), π = 0.5 each. Point x = 1: densities φ(1) = 0.242 and φ(−3) = 0.0044 → γ = 0.242/(0.242 + 0.0044) = **0.982** for the first. Point x = 2: φ(2) = 0.054 both → **0.5/0.5**. DBSCAN with ε = 1, minPts = 3 on points 0, 0.5, 0.9, 5: the first three are core points (each has 3 points within 1 including itself) → one cluster; 5 is **noise**.""",
  ["DBSCAN ε chosen without a k-distance plot", "DBSCAN on data with very different densities", "GMM with full covariances on tiny clusters (singular)", "Forgetting GMM needs scaled features and several inits"],
  ["DBSCAN: geographic hotspots, arbitrary shapes, outlier removal", "GMM: soft membership, elliptical clusters, density estimation"], ["DBSCAN in high dimensions; GMM with strongly non-Gaussian clusters"],
  "California housing locations (DBSCAN finds dense urban areas and labels sparse districts as noise; HDBSCAN handles varying density) and penguins (GMM with BIC choosing k and covariance type, soft probabilities, EM from scratch in 1-D).",
  ["k-distance plot to pick ε for lat/lon (in km)", "DBSCAN and HDBSCAN on district locations", "GMM BIC over k and covariance types on penguins", "Soft membership for ambiguous birds", "1-D EM from scratch on flipper length"],
  f'''
import numpy as np, pandas as pd
from sklearn.cluster import DBSCAN, HDBSCAN
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
h = pd.read_csv("{HOUSING}"); km = np.c_[h.latitude * 111, h.longitude * 111 * np.cos(np.radians(36))]
kd = np.sort(NearestNeighbors(n_neighbors=20).fit(km).kneighbors(km)[0][:, -1]); print("20-NN distance percentiles (km) 50/90/99:", np.percentile(kd, [50, 90, 99]).round(1))
db = DBSCAN(eps=6, min_samples=20).fit(km); lab = db.labels_
big = pd.Series(lab[lab >= 0]).value_counts().head(3)
print(f"DBSCAN: {{lab.max() + 1}} dense clusters, noise {{(lab == -1).mean():.1%}}; largest cluster centres:",
      [(round(float(h.latitude[lab == c].mean()), 2), round(float(h.longitude[lab == c].mean()), 2), int(n)) for c, n in big.items()])
hd = HDBSCAN(min_cluster_size=100).fit(km); print(f"HDBSCAN: {{hd.labels_.max() + 1}} clusters, noise {{(hd.labels_ == -1).mean():.1%}}")
p = pd.read_csv("{PENGUINS}").dropna(); Z = StandardScaler().fit_transform(p[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]])
bic = {{(k, cv): GaussianMixture(k, covariance_type=cv, n_init=3, random_state=0).fit(Z).bic(Z) for k in range(1, 7) for cv in ["spherical", "diag", "full"]}}
best = min(bic, key=bic.get); print("GMM best by BIC:", best, "| BIC by k (full):", {{k: round(bic[(k, "full")]) for k in range(1, 7)}})
g = GaussianMixture(*[best[0]], covariance_type=best[1], n_init=5, random_state=0).fit(Z); post = g.predict_proba(Z)
print("ARI vs species:", round(adjusted_rand_score(p.species, g.predict(Z)), 3), "| most ambiguous birds' memberships:", post[np.argsort(post.max(1))[:3]].round(2).tolist())
x = p.flipper_length_mm.to_numpy(); pi, mu, sd = np.array([0.5, 0.5]), np.array([185.0, 215.0]), np.array([10.0, 10.0])
norm = lambda x, m, s: np.exp(-0.5 * ((x - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))
for it in range(100):
    R = pi * norm(x[:, None], mu, sd); ll = np.log(R.sum(1)).sum(); R /= R.sum(1, keepdims=True)          # E-step
    pi, mu = R.mean(0), (R * x[:, None]).sum(0) / R.sum(0); sd = np.sqrt((R * (x[:, None] - mu) ** 2).sum(0) / R.sum(0))   # M-step
print(f"1-D EM on flipper length: means {{mu.round(1)}}, sds {{sd.round(1)}}, weights {{pi.round(2)}}, log-lik {{ll:.1f}}")
''')

X("m-curse-dim",
  "In high dimensions, space is mostly empty and all points become roughly equally far apart, so distances, densities and neighbourhoods lose meaning. Data needed to cover the space grows exponentially. This 'curse' explains why kNN, clustering and density estimation degrade with many raw features — and why dimensionality reduction and good representations matter.",
  """**Facts.** To capture 10% of uniformly spread data with a hypercube neighbourhood in d dims, its edge must be 0.1^(1/d): 0.1 in 1-D, 0.32 in 2-D, **0.79** in 10-D, 0.98 in 100-D — 'local' neighbourhoods span almost the whole range. The volume of a unit ball relative to its bounding cube → 0; most volume of a ball lies near its surface. For i.i.d. coordinates, ‖x − y‖² concentrates: its relative spread shrinks like 1/√d, so (max − min)/min of distances → 0. **Blessings:** real data usually lie near a low-dimensional manifold, and linear separability is easier in high dimension (Cover's theorem).""",
  """**Sample size by hand.** Covering [0, 1]^d with a grid of spacing 0.1 needs 10^d cells: 100 cells in 2-D, 10¹⁰ in 10-D. With 10,000 samples in 10-D, the average cell is empty — every point is 'far' from every other.""",
  ["kNN or k-means on hundreds of raw, mostly irrelevant features", "Assuming more features always help", "Density estimation (KDE) in high dimension"],
  ["Reasoning about when to reduce dimensions or learn embeddings"], ["Panicking about dimension when data lie on a low-dimensional manifold (images, text embeddings)"],
  "Fashion-MNIST and synthetic uniform data — measure distance concentration as dimension grows, kNN accuracy as irrelevant noise dimensions are added, the neighbourhood-edge formula, and recovery via PCA.",
  ["Distance contrast (max/min) for uniform data in 2…10,000 dims", "Edge length needed to capture 10% of data", "kNN on Fashion-MNIST + increasing noise features", "Same with PCA first (recovering the signal)", "Intrinsic dimension estimate from PCA variance"],
  '''
import numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
''' + FMNIST + '''
rng = np.random.default_rng(0)
for d in [2, 10, 100, 1000, 10000]:
    U = rng.random((500, d)); dist = np.linalg.norm(U[1:] - U[0], axis=1)
    print(f"  d={d:5d}: (max-min)/min distance = {(dist.max() - dist.min()) / dist.min():6.2f} | edge to capture 10% = {0.1 ** (1 / d):.3f}")
Xs, ys = X[:4000], y[:4000]; Xtr, Xte, ytr, yte = train_test_split(Xs, ys, test_size=0.3, random_state=0, stratify=ys)
for extra in [0, 200, 1000, 5000]:
    N1, N2 = rng.random((len(Xtr), extra)), rng.random((len(Xte), extra))
    A, B = np.c_[Xtr, N1], np.c_[Xte, N2]
    raw = KNeighborsClassifier(5).fit(A, ytr).score(B, yte)
    pc = make_pipeline(PCA(30, random_state=0), KNeighborsClassifier(5)).fit(A, ytr).score(B, yte)
    print(f"  784 pixels + {extra:4d} noise dims: kNN {raw:.3f} | PCA-30 then kNN {pc:.3f}")
v = np.cumsum(PCA().fit(Xtr).explained_variance_ratio_); print("Fashion-MNIST: dims for 90/95/99% variance:", np.searchsorted(v, [0.9, 0.95, 0.99]) + 1, "of 784 -> data live on a much lower-dimensional manifold")
''')

X("m-pca",
  "Principal component analysis rotates the data to new axes ordered by how much variance they capture; keeping the first few gives a compact summary that preserves most of the information. Used for visualisation, compression, de-noising, de-correlating features and speeding up models.",
  """**Derivation.** Centre X. Find unit w maximising Var(Xw) = wᵀΣw s.t. ‖w‖ = 1 → Lagrangian wᵀΣw − λ(wᵀw − 1) → Σw = λw: the best direction is the top **eigenvector** of the covariance, with variance λ. Subsequent components are the next eigenvectors (orthogonal). In practice use the **SVD** X = USVᵀ: components = rows of Vᵀ, variances = s²/(n − 1), scores = US. Equivalently PCA minimises reconstruction error ‖X − X_k‖² (Eckart–Young: the rank-k SVD truncation is optimal). Explained variance ratio λᵢ/Σλ guides k. Standardise when units differ; PCA is linear and unsupervised (may discard class-relevant low-variance directions).""",
  """**2-D by hand.** Covariance Σ = [[2, 1.2], [1.2, 1]]. Eigenvalues: λ² − 3λ + (2 − 1.44) = 0 → λ = (3 ± √(9 − 2.24))/2 = (3 ± 2.6)/2 → **2.8** and **0.2**. PC1 keeps 2.8/3.0 = **93%** of variance; its direction solves (2 − 2.8)w₁ + 1.2w₂ = 0 → w ∝ [1.5, 1] → normalised [0.83, 0.55].""",
  ["Not centring/scaling", "Fitting PCA on train+test", "Interpreting components as real-world factors without care", "Using PCA before trees (rotations hurt axis-aligned splits)"],
  ["Visualisation, compression, noise reduction, collinearity, speeding up kNN/SVM"], ["Strongly non-linear manifolds (use UMAP/autoencoders), when the low-variance directions carry the signal"],
  "Fashion-MNIST — PCA from scratch via SVD, check against scikit-learn, scree/explained variance, reconstruct images from k components, de-noise images, and use PCA features for a classifier.",
  ["Centre data; SVD; components and explained variance", "Match sklearn's PCA (up to sign)", "Reconstruction error vs k", "De-noising: project noisy images onto top components", "Accuracy/speed of a classifier on PCA features"],
  '''
import time, numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
''' + FMNIST + '''
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
mu = Xtr.mean(0); U, S, Vt = np.linalg.svd(Xtr - mu, full_matrices=False); var = S ** 2 / (len(Xtr) - 1); ratio = var / var.sum()
sk = PCA(50).fit(Xtr)
print("explained variance ratio (first 5):", ratio[:5].round(3), "| sklearn:", sk.explained_variance_ratio_[:5].round(3))
print("components match up to sign:", np.allclose(np.abs(Vt[:50]), np.abs(sk.components_), atol=1e-6))
for k in [5, 20, 50, 150]:
    R = (Xte - mu) @ Vt[:k].T @ Vt[:k] + mu; print(f"  k={k:3d}: variance kept {ratio[:k].sum():.3f} | reconstruction MSE {((Xte - R) ** 2).mean():.4f}")
rng = np.random.default_rng(0); noisy = np.clip(Xte + rng.normal(0, 0.25, Xte.shape), 0, 1)
den = (noisy - mu) @ Vt[:40].T @ Vt[:40] + mu
print(f"de-noising: MSE noisy {((noisy - Xte) ** 2).mean():.4f} -> PCA-40 projection {((den - Xte) ** 2).mean():.4f}")
for name, A, B in [("784 pixels", Xtr, Xte), ("50 PCA features", sk.transform(Xtr), sk.transform(Xte))]:
    t = time.perf_counter(); m = LogisticRegression(max_iter=300).fit(A, ytr); print(f"  {name:16s} accuracy {m.score(B, yte):.3f} | fit {time.perf_counter() - t:.1f}s")
''')

X("m-eigenfaces",
  "EigenFaces applies PCA to aligned face images: each principal component is itself an image (a 'ghostly face') capturing a common way faces vary — lighting, face shape, glasses. Any face ≈ average face + a weighted sum of eigenfaces, so a face becomes a short vector of weights used for recognition.",
  """**Method.** Flatten each 64×64 face to 4,096 pixels; centre by the mean face; PCA. With n images ≪ pixels, compute eigenvectors of the small n×n Gram matrix XXᵀ (Turk & Pentland trick): if XXᵀu = λu then Xᵀu is an eigenvector of XᵀX — or simply use randomised SVD. Project faces onto k eigenfaces (with **whitening** = divide by √λ to equalise components) and classify with nearest neighbour or an SVM. **Fisherfaces:** PCA to n − c dims, then LDA to c − 1 dims, robust to lighting. Distance from the face space (reconstruction error) detects non-faces.""",
  """**Gram trick by hand.** 300 training faces × 4,096 pixels: the pixel covariance is 4,096×4,096 (16.8M entries); the Gram matrix XXᵀ is 300×300 (90k entries) — same non-zero eigenvalues, ~190× smaller problem. Keeping 100 eigenfaces compresses each face from 4,096 numbers to **100** (41×).""",
  ["Unaligned faces (PCA captures pose instead of identity)", "Not whitening before SVM", "Including test faces in PCA fitting", "Expecting robustness to lighting changes"],
  ["Teaching PCA on images, small controlled face datasets, compression"], ["Real-world face recognition — use deep embeddings (FaceNet/ArcFace)"],
  "Olivetti faces (400 photos of 40 people, AT&T Labs; downloaded by scikit-learn) — mean face, eigenfaces via the Gram-matrix trick vs SVD, reconstruction with k components, recognition with nearest neighbour and whitened SVM, and Fisherfaces.",
  ["Load faces and split per person", "Mean face and eigenfaces via the n×n Gram matrix", "Check against sklearn PCA; reconstruction error vs k", "Recognition: 1-NN and whitened PCA + SVM, tune k", "Fisherfaces (PCA + LDA) and a saved image grid of eigenfaces"],
  '''
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from sklearn.datasets import fetch_olivetti_faces
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
faces = fetch_olivetti_faces(); X, y = faces.data, faces.target                     # 400 x 4096, 40 people
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
mean = Xtr.mean(0); A = Xtr - mean
lam, U = np.linalg.eigh(A @ A.T); lam, U = lam[::-1], U[:, ::-1]                  # small 300x300 Gram matrix
E = (A.T @ U[:, :100]).T; E /= np.linalg.norm(E, axis=1, keepdims=True)           # eigenfaces = Aᵀu, normalised
sk = PCA(100, svd_solver="full").fit(Xtr)
print("Gram-trick eigenfaces match PCA (|cos| of first 5):", np.abs((E[:5] * sk.components_[:5]).sum(1)).round(4))
for k in [10, 50, 100]:
    R = (Xte - mean) @ E[:k].T @ E[:k] + mean; print(f"  k={k:3d}: variance kept {sk.explained_variance_ratio_[:k].sum():.3f} | test reconstruction MSE {((R - Xte) ** 2).mean():.5f}")
print("1-NN on raw pixels:", KNeighborsClassifier(1).fit(Xtr, ytr).score(Xte, yte))
for k in [20, 50, 100]:
    m = make_pipeline(PCA(k, whiten=True, random_state=0), SVC(C=10, gamma="scale")).fit(Xtr, ytr); print(f"  eigenfaces k={k:3d} + SVM accuracy {m.score(Xte, yte):.3f}")
fisher = make_pipeline(PCA(len(Xtr) - 40, random_state=0), LinearDiscriminantAnalysis(), KNeighborsClassifier(1)).fit(Xtr, ytr); print("Fisherfaces + 1-NN accuracy:", round(fisher.score(Xte, yte), 3))
fig, ax = plt.subplots(2, 5, figsize=(10, 4))
for i, a in enumerate(ax.flat): a.imshow((mean if i == 0 else E[i - 1]).reshape(64, 64), cmap="gray"); a.set_title("mean face" if i == 0 else f"eigenface {i}"); a.axis("off")
fig.savefig("eigenfaces.png"); print("saved eigenfaces.png")
''')

X("m-lda",
  "Linear discriminant analysis projects data onto the directions that best **separate known classes**: far-apart class means, tight classes. It's both a fast linear classifier (assuming Gaussian classes with shared covariance) and a supervised dimensionality reducer to at most (classes − 1) dimensions.",
  """**Fisher's criterion.** Maximise J(w) = (wᵀS_B w)/(wᵀS_W w), with between-class scatter S_B = Σₖ nₖ(μₖ − μ)(μₖ − μ)ᵀ and within-class scatter S_W = Σₖ Σ_{i∈k}(xᵢ − μₖ)(xᵢ − μₖ)ᵀ. Solution: generalised eigenproblem S_B w = λS_W w → eigenvectors of S_W⁻¹S_B; rank(S_B) ≤ C − 1. **As a classifier:** p(x|k) = N(μₖ, Σ) with shared Σ → log-posterior linear in x: δₖ(x) = xᵀΣ⁻¹μₖ − ½μₖᵀΣ⁻¹μₖ + log πₖ. **QDA** allows Σₖ per class → quadratic boundaries, more parameters. Shrinkage LDA regularises Σ when p is large vs n.""",
  """**Two classes in 1-D by hand.** Class A: mean 2, class B: mean 6, shared variance 1, equal priors. Boundary where δ_A = δ_B → x = (2 + 6)/2 = **4**. With priors π_A = 0.8, π_B = 0.2 the boundary shifts toward B: x = 4 + (σ²/(μ_B − μ_A))·ln(π_A/π_B) = 4 + 0.25·1.386 = **4.35**.""",
  ["Confusing it with latent Dirichlet allocation (topic model)", "Expecting more than C − 1 components", "Using plain LDA when p > n (use shrinkage)", "Strongly non-Gaussian, multimodal classes"],
  ["Fast linear classification, supervised visualisation, pre-processing for kNN (Fisherfaces)"], ["Non-linear class boundaries — use QDA, kernels, trees"],
  "Penguins (3 species) — LDA from scratch via the scatter matrices, compare projections with PCA (separation ratio), LDA/QDA/shrinkage as classifiers, and the effect of class priors.",
  ["Compute class means, S_W and S_B", "Solve the generalised eigenproblem; project to 2-D", "Compare class separation in LDA vs PCA space", "LDA vs QDA vs shrinkage-LDA classifiers with CV", "Change priors and observe predictions"],
  f'''
import numpy as np, pandas as pd
from scipy.linalg import eigh
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
df = pd.read_csv("{PENGUINS}").dropna(); Z = StandardScaler().fit_transform(df[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]]); y = df.species.to_numpy()
mu = Z.mean(0); classes = np.unique(y)
SW = sum((Z[y == c] - Z[y == c].mean(0)).T @ (Z[y == c] - Z[y == c].mean(0)) for c in classes)
SB = sum((y == c).sum() * np.outer(Z[y == c].mean(0) - mu, Z[y == c].mean(0) - mu) for c in classes)
lam, W = eigh(SB, SW); W = W[:, ::-1][:, :2]; print("generalised eigenvalues (top 3):", lam[::-1][:3].round(3), "-> only C-1 = 2 non-zero")
def separation(P): return sum((y == c).sum() * ((P[y == c].mean(0) - P.mean(0)) ** 2).sum() for c in classes) / sum(((P[y == c] - P[y == c].mean(0)) ** 2).sum() for c in classes)
P_lda, P_pca = Z @ W, PCA(2).fit_transform(Z)
print(f"between/within ratio in 2-D: LDA {{separation(P_lda):.2f}} vs PCA {{separation(P_pca):.2f}}")
sk = LinearDiscriminantAnalysis(n_components=2).fit(Z, y); print("sklearn LDA explained ratio:", sk.explained_variance_ratio_.round(3))
for name, m in [("LDA", LinearDiscriminantAnalysis()), ("QDA", QuadraticDiscriminantAnalysis()), ("shrinkage LDA", LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"))]:
    print(f"  {{name:14s}} CV accuracy {{cross_val_score(m, Z, y, cv=5).mean():.3f}}")
amb = np.argsort(sk.predict_proba(Z).max(1))[:3]
for pri in [None, [0.1, 0.1, 0.8]]:
    m = LinearDiscriminantAnalysis(priors=pri).fit(Z, y); print(f"  priors {{pri}}: predictions for 3 most ambiguous birds {{m.predict(Z[amb]).tolist()}} (true {{y[amb].tolist()}})")
''')

X("m-manifold",
  "Manifold learning maps high-dimensional data into 2–3 dimensions while keeping **neighbourhoods** intact, so you can *see* clusters and structure that linear PCA flattens. t-SNE and UMAP are the standard tools for visualising embeddings, images and single-cell data; Isomap and LLE are the classic methods.",
  """**t-SNE.** High-dim similarities pⱼ|ᵢ ∝ exp(−‖xᵢ − xⱼ‖²/2σᵢ²) with σᵢ set so the effective number of neighbours = **perplexity**; low-dim similarities use a heavy-tailed Student-t qᵢⱼ ∝ (1 + ‖yᵢ − yⱼ‖²)⁻¹ (avoids crowding); minimise KL(P‖Q) by gradient descent. Preserves local neighbourhoods, **not** global distances or cluster sizes. **UMAP:** fuzzy k-NN graph in high dimension, optimise a low-dim graph with cross-entropy; faster, keeps more global structure, can transform new points. **Isomap:** geodesic (graph shortest-path) distances + classical MDS. Evaluate with **trustworthiness** (are low-dim neighbours true neighbours?).""",
  """**Perplexity intuition.** Perplexity 30 ≈ each point considers ~30 effective neighbours. If a point's distances to its 30 nearest neighbours are all ~1 and the rest ≫ 1, σ settles near 1. Perplexity 5 → very local, fragmented clusters; perplexity 500 on 1,800 points → blurs local detail.""",
  ["Reading distances between t-SNE clusters or cluster sizes as meaningful", "A single perplexity/seed", "Clustering on t-SNE output", "Using t-SNE to embed new points (it can't)"],
  ["Visualising embeddings, images, documents, cells"], ["As features for downstream models (except UMAP with care), or for quantitative distance claims"],
  "Handwritten digits (1,797 images) — PCA vs Isomap vs t-SNE (several perplexities) vs UMAP, scored by trustworthiness and by how well a kNN classifier works in the 2-D map, and a saved comparison figure.",
  ["Load and scale digits", "Embed with PCA, Isomap, t-SNE (perplexity 5/30/100), UMAP", "Trustworthiness of each map", "kNN accuracy in 2-D as a neighbourhood-quality check", "Plot all maps side by side"],
  '''
import matplotlib; matplotlib.use("Agg")
import time, matplotlib.pyplot as plt, numpy as np, umap
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, Isomap, trustworthiness
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
X, y = load_digits(return_X_y=True); Xs = StandardScaler().fit_transform(X)
methods = {"PCA": PCA(2, random_state=0), "Isomap": Isomap(n_neighbors=10), "t-SNE perp 5": TSNE(perplexity=5, random_state=0), "t-SNE perp 30": TSNE(perplexity=30, random_state=0),
           "t-SNE perp 100": TSNE(perplexity=100, random_state=0), "UMAP": umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=0)}
maps = {}
for name, m in methods.items():
    t = time.perf_counter(); E = m.fit_transform(Xs); maps[name] = E
    print(f"  {name:15s} trustworthiness {trustworthiness(Xs, E, n_neighbors=10):.3f} | 2-D kNN accuracy {cross_val_score(KNeighborsClassifier(5), E, y, cv=5).mean():.3f} | {time.perf_counter() - t:4.1f}s")
fig, ax = plt.subplots(2, 3, figsize=(13, 8))
for a, (name, E) in zip(ax.flat, maps.items()): a.scatter(E[:, 0], E[:, 1], c=y, cmap="tab10", s=4); a.set_title(name); a.set_xticks([]); a.set_yticks([])
fig.tight_layout(); fig.savefig("manifolds.png"); print("saved manifolds.png (remember: t-SNE gaps and sizes are not distances)")
''')

X("m-anomaly",
  "Anomaly detection finds rare observations that don't fit the normal pattern — fraud, faults, intrusions, data errors. Methods score how *unusual* each point is: statistical rules (z-score, IQR), distance/density (kNN, LOF), isolation (Isolation Forest), boundaries (One-Class SVM), and reconstruction error (PCA/autoencoders).",
  """**Scores.** Robust z = (x − median)/(1.4826·MAD). **Isolation Forest:** random splits isolate anomalies in few steps; score s = 2^(−E[h(x)]/c(n)), where h = path length and c(n) ≈ 2H(n−1) − 2(n−1)/n normalises; s near 1 = anomaly. **LOF:** ratio of a point's local density to its neighbours' (≫ 1 = outlier relative to its neighbourhood — handles varying densities). **One-Class SVM:** smallest region containing a fraction 1 − ν of data. **Reconstruction:** fit PCA/autoencoder on normal data; anomalies reconstruct poorly. Setting the threshold = choosing a contamination rate or an alert budget; evaluate on labelled incidents with precision@k / PR-AUC.""",
  """**Path length by hand.** In a tree built on 256 points, a typical point needs ~c(256) ≈ 2(ln 255 + 0.577) − 2 ≈ **10.2** splits to isolate; an outlier isolated after 3 splits on average scores 2^(−3/10.2) = **0.82** (anomalous), a normal point at 10 splits scores 2^(−1) ≈ 0.51.""",
  ["Using plain z-scores on skewed data", "One global threshold when densities vary (use LOF)", "Training on data already full of anomalies without robust methods", "No evaluation on known incidents"],
  ["Fraud, monitoring, data quality, sensor faults"], ["When labelled anomalies are plentiful — use supervised classification"],
  "Online Retail invoices — build invoice-level features, inject 50 realistic anomalies (bulk/price errors) as ground truth, and compare robust z-score, Isolation Forest, LOF, One-Class SVM and PCA reconstruction by precision@50 and PR-AUC.",
  ["Aggregate lines to invoices (items, quantity, value, unit-price stats)", "Inject labelled anomalies", "Score with five detectors", "Evaluate precision@k and PR-AUC", "Inspect the top flagged real invoices"],
  f'''
import numpy as np, pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
r = pd.read_csv("{RETAIL}", encoding="latin-1"); r = r[(r.Quantity > 0) & (r.UnitPrice > 0)]; r["value"] = r.Quantity * r.UnitPrice
inv = r.groupby("InvoiceNo").agg(lines=("StockCode", "size"), qty=("Quantity", "sum"), value=("value", "sum"), max_price=("UnitPrice", "max"), mean_price=("UnitPrice", "mean"))
inv = inv.sample(8000, random_state=0); inv["label"] = 0
rng = np.random.default_rng(0); fake = inv.sample(50, random_state=1).copy()
fake["qty"] *= rng.uniform(20, 60, 50); fake["value"] = fake.qty * fake.mean_price * rng.uniform(0.5, 1.5, 50); fake.loc[fake.index[:20], "max_price"] *= 100; fake["label"] = 1
data = pd.concat([inv, fake]); F = np.log1p(data.drop(columns="label")); Z = StandardScaler().fit_transform(F); y = data.label.to_numpy()
med, mad = np.median(F, 0), np.median(np.abs(F - np.median(F, 0)), 0) * 1.4826
pca = PCA(2).fit(Z)
scores = {{"robust z (max)": (np.abs(F - med) / mad).max(1).to_numpy(), "IsolationForest": -IsolationForest(n_estimators=300, random_state=0).fit(Z).score_samples(Z),
          "LOF": -LocalOutlierFactor(n_neighbors=35).fit(Z).negative_outlier_factor_, "One-Class SVM": -OneClassSVM(nu=0.01, gamma="scale").fit(Z).score_samples(Z),
          "PCA reconstruction": ((Z - pca.inverse_transform(pca.transform(Z))) ** 2).sum(1)}}
for name, s in scores.items(): print(f"  {{name:19s}} precision@50 {{y[np.argsort(-s)[:50]].mean():.2f}} | PR-AUC {{average_precision_score(y, s):.3f}}")
top = data[y == 0].assign(score=scores["IsolationForest"][y == 0]).nlargest(3, "score"); print("top real invoices flagged:\\n", top.round(1))
''')

X("m-recsys",
  "Recommender systems predict what a user will like from past behaviour. **Popularity** is the baseline, **content-based** uses item features, **collaborative filtering** uses patterns of who liked what (user–user, item–item), and **matrix factorisation** learns latent taste vectors for users and items. Modern systems add two-tower neural retrieval and re-ranking.",
  """**Matrix factorisation.** Ratings r_ui ≈ μ + b_u + b_i + p_u·q_i with k-dim latent vectors; minimise Σ(r_ui − r̂_ui)² + λ(‖p_u‖² + ‖q_i‖² + b²) over *observed* ratings only, by SGD (e_ui = r_ui − r̂; p_u ← p_u + η(e·q_i − λp_u), q_i ← q_i + η(e·p_u − λq_i)) or ALS. **Item–item CF:** sim(i, j) = cosine of mean-centred rating columns; predict r̂_ui = Σ_j sim(i, j)·r_uj / Σ|sim|. **Evaluation:** RMSE for ratings; ranking metrics (precision@k, recall@k, NDCG, hit rate) on held-out interactions — usually split by time. **Problems:** cold start (new users/items → content features), popularity bias, sparsity (99%+ missing), feedback loops.""",
  """**Prediction by hand.** μ = 3.5, user bias b_u = +0.3 (rates high), item bias b_i = −0.2, p_u = [1.0, 0.5], q_i = [0.4, −0.2] → r̂ = 3.5 + 0.3 − 0.2 + (0.4 − 0.1) = **3.9**. One SGD step with true rating 5, η = 0.1, λ = 0: e = 1.1 → p_u ← [1.0 + 0.044, 0.5 − 0.022] = [1.044, 0.478].""",
  ["Random splits instead of time-based", "Evaluating only RMSE when the product shows top-k lists", "Ignoring popularity bias (recommending what everyone already sees)", "Treating missing ratings as zeros in factorisation"],
  ["E-commerce, media, content feeds, any user–item interaction data"], ["Tiny catalogues where simple rules or editorial picks work"],
  "MovieTweetings (real IMDb ratings tweeted by users) — time-based split, popularity and bias baselines, item–item collaborative filtering, matrix factorisation by SGD from scratch, and evaluation by RMSE and hit-rate@10.",
  ["Load ratings and split by time", "Baselines: global mean, user/item biases, popularity top-10", "Item–item cosine CF", "Matrix factorisation with biases (SGD)", "Evaluate RMSE and hit-rate@10; show recommendations for a user"],
  f'''
import numpy as np, pandas as pd
r = pd.read_csv("{MOVIES}ratings.dat", sep="::", engine="python", names=["user", "movie", "rating", "ts"])
names = pd.read_csv("{MOVIES}movies.dat", sep="::", engine="python", names=["movie", "title", "genre"], encoding="latin-1").drop_duplicates("movie").set_index("movie").title
r = r[r.movie.isin(r.movie.value_counts()[lambda s: s >= 20].index)]; r = r[r.user.isin(r.user.value_counts()[lambda s: s >= 10].index)]
r = r.sort_values("ts"); cut = r.ts.quantile(0.9); tr, te = r[r.ts <= cut], r[r.ts > cut]
te = te[te.user.isin(tr.user) & te.movie.isin(tr.movie)]; print(f"train {{len(tr):,}} test {{len(te):,}} ratings | users {{tr.user.nunique():,}} movies {{tr.movie.nunique():,}}")
rmse = lambda p: np.sqrt(np.mean((p - te.rating.to_numpy()) ** 2)); mu = tr.rating.mean()
bi = tr.groupby("movie").rating.apply(lambda s: (s - mu).sum() / (len(s) + 10)); bu = tr.assign(d=tr.rating - mu - tr.movie.map(bi)).groupby("user").d.apply(lambda s: s.sum() / (len(s) + 10))
base = mu + te.user.map(bu).fillna(0).to_numpy() + te.movie.map(bi).fillna(0).to_numpy(); print(f"RMSE global mean {{rmse(np.full(len(te), mu)):.4f}} | biases {{rmse(base):.4f}}")
U, M = {{u: i for i, u in enumerate(tr.user.unique())}}, {{m: j for j, m in enumerate(tr.movie.unique())}}
ui, mi, rv = tr.user.map(U).to_numpy(), tr.movie.map(M).to_numpy(), tr.rating.to_numpy(float)
k, lam, eta, rng = 20, 0.05, 0.01, np.random.default_rng(0)
P, Q, bU, bM = rng.normal(0, 0.1, (len(U), k)), rng.normal(0, 0.1, (len(M), k)), np.zeros(len(U)), np.zeros(len(M))
for epoch in range(15):
    for t in rng.permutation(len(rv)):
        u, m = ui[t], mi[t]; e = rv[t] - (mu + bU[u] + bM[m] + P[u] @ Q[m])
        bU[u] += eta * (e - lam * bU[u]); bM[m] += eta * (e - lam * bM[m]); P[u], Q[m] = P[u] + eta * (e * Q[m] - lam * P[u]), Q[m] + eta * (e * P[u] - lam * Q[m])
tu, tm = te.user.map(U).to_numpy(), te.movie.map(M).to_numpy(); mf = mu + bU[tu] + bM[tm] + (P[tu] * Q[tm]).sum(1); print(f"RMSE matrix factorisation (k={{k}}) {{rmse(mf):.4f}}")
R = np.zeros((len(U), len(M))); R[ui, mi] = rv - mu; norms = np.linalg.norm(R, axis=0) + 1e-9; S = (R.T @ R) / np.outer(norms, norms)
liked = te[te.rating >= 8]; pop = tr.movie.value_counts().index[:10]; hits = {{"popularity": 0, "item-item CF": 0, "matrix factorisation": 0}}
for u, grp in liked.groupby("user"):
    seen = tr.movie[tr.user == u].map(M).to_numpy(); target = set(grp.movie.map(M))
    cf = S[:, seen] @ R[U[u], seen]; mfs = bM + Q @ P[U[u]]
    for name, sc in [("item-item CF", cf), ("matrix factorisation", mfs)]: sc = sc.copy(); sc[seen] = -np.inf; hits[name] += bool(target & set(np.argsort(-sc)[:10]))
    hits["popularity"] += bool(target & set(M[m] for m in pop if M[m] not in set(seen)))
print("hit-rate@10:", {{k: round(v / liked.user.nunique(), 3) for k, v in hits.items()}})
u0 = liked.user.iloc[0]; sc = bM + Q @ P[U[u0]]; sc[tr.movie[tr.user == u0].map(M).to_numpy()] = -np.inf; inv = {{j: m for m, j in M.items()}}
print("MF recommendations for a test user:", [names.get(inv[j], inv[j]) for j in np.argsort(-sc)[:5]])
''')

X("m-assoc-rules",
  "Association rule mining discovers 'customers who buy X also buy Y' patterns in transactions. **Apriori** and **FP-Growth** find frequent itemsets; rules are ranked by **support**, **confidence** and **lift**. Used for cross-selling, store layout, bundles and 'frequently bought together' widgets.",
  """**Measures.** support(X) = fraction of baskets containing X. confidence(X → Y) = support(X ∪ Y)/support(X) = P(Y|X). **lift** = confidence/support(Y) = P(Y|X)/P(Y): > 1 positive association, 1 independent, < 1 substitutes. Leverage = support(X ∪ Y) − support(X)·support(Y); conviction = (1 − supp(Y))/(1 − conf). **Apriori principle:** every subset of a frequent itemset is frequent ⇒ generate candidates of size k + 1 only from frequent size-k sets (pruning). **FP-Growth** compresses transactions into a prefix tree and mines without candidate generation — much faster. High-confidence rules with lift ≈ 1 are useless (Y is just popular).""",
  """**By hand.** 1,000 baskets: tea in 200, cake in 100, both in 60. support(tea, cake) = **0.06**; confidence(cake → tea) = 60/100 = **0.6**; lift = 0.6/0.2 = **3.0** — cake buyers are 3× more likely than average to buy tea. confidence(tea → cake) = 60/200 = 0.3, lift also 3.0 (lift is symmetric).""",
  ["Ranking by confidence only (popular items dominate)", "Too-low support thresholds (explosion of spurious rules)", "Reading rules as causal ('placing X next to Y will raise sales')", "Ignoring that many rules are tested (some will look strong by chance)"],
  ["Basket analysis, cross-selling, catalogue bundles, co-occurrence exploration"], ["Personalised recommendations at scale — use collaborative filtering"],
  "Online Retail (France customers' invoices) — build a basket matrix, mine frequent itemsets with Apriori and FP-Growth, compute support/confidence/lift by hand for one rule, and rank actionable rules.",
  ["Filter invoices and build the one-hot basket matrix", "Frequent itemsets with Apriori vs FP-Growth (time)", "Generate rules; filter by lift and confidence", "Verify one rule's metrics by hand", "Print top rules as 'bundle suggestions'"],
  f'''
import time, pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
r = pd.read_csv("{RETAIL}", encoding="latin-1"); r = r[(r.Country == "France") & (r.Quantity > 0) & ~r.InvoiceNo.astype(str).str.startswith("C")]
r = r[r.Description.notna() & (r.Description.str.strip() != "POSTAGE")]
basket = pd.crosstab(r.InvoiceNo, r.Description.str.strip()).gt(0); print("baskets x products:", basket.shape)
t = time.perf_counter(); fa = apriori(basket, min_support=0.05, use_colnames=True); ta = time.perf_counter() - t
t = time.perf_counter(); ff = fpgrowth(basket, min_support=0.05, use_colnames=True); tf = time.perf_counter() - t
print(f"frequent itemsets: apriori {{len(fa)}} in {{ta:.2f}}s | FP-growth {{len(ff)}} in {{tf:.2f}}s")
rules = association_rules(ff, metric="lift", min_threshold=1.0)
good = rules[(rules.confidence >= 0.6) & (rules.lift >= 3)].sort_values("lift", ascending=False)
row = good.iloc[0]; A, B = list(row.antecedents), list(row.consequents)
sA, sB, sAB = basket[A].all(1).mean(), basket[B].all(1).mean(), basket[A + B].all(1).mean()
print(f"check {{A}} -> {{B}}: support {{sAB:.3f}} ({{row.support:.3f}}), confidence {{sAB / sA:.3f}} ({{row.confidence:.3f}}), lift {{sAB / sA / sB:.2f}} ({{row.lift:.2f}})")
print(f"{{len(good)}} strong rules; top bundle suggestions:")
for _, x in good.head(6).iterrows(): print(f"  {{', '.join(x.antecedents)}} -> {{', '.join(x.consequents)}} | conf {{x.confidence:.2f}} lift {{x.lift:.1f}}")
''')
