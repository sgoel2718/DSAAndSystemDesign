"""Deep layer + end-to-end walkthroughs: Linear algebra & calculus."""
from deep.util import X

PENGUINS = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
MPG = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv"
HOUSING = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
MOVIES = "https://raw.githubusercontent.com/sidooms/MovieTweetings/master/latest/"

X("m-vectors",
  "A vector is a list of numbers that describes one thing — a house as [rooms, area, age], a word as a 300-number embedding, an image as 784 pixels. Once data are vectors, 'similar' becomes 'close', and the **dot product** measures alignment. Nearly every ML model is built from dot products.",
  """**Operations.** Addition and scaling are element-wise. Dot product a·b = Σ aᵢbᵢ = ‖a‖‖b‖cos θ. **Cosine similarity** = a·b/(‖a‖‖b‖) ∈ [−1, 1] ignores length (good for text/embeddings). Projection of a onto b: (a·b/‖b‖²)·b. A linear model's score is w·x + b — a weighted vote of features; the decision boundary w·x + b = 0 is a hyperplane perpendicular to w.""",
  """**By hand.** a = [1, 2, 2], b = [2, 0, 1]. a·b = 2 + 0 + 2 = 4; ‖a‖ = 3, ‖b‖ = √5 = 2.236 → cos θ = 4/6.71 = **0.596** (θ ≈ 53°). Projection of a on b = (4/5)·[2, 0, 1] = **[1.6, 0, 0.8]**.""",
  ["Comparing vectors on different scales without normalising", "Using Euclidean distance for sparse text vectors (use cosine)", "Confusing row vs column vectors in shapes"],
  ["Similarity search, recommendation, embeddings, linear models"], ["Comparing raw vectors whose features have incomparable units"],
  "MovieTweetings ratings — turn each user into a vector of ratings over popular movies, find similar users by cosine similarity, and recommend via a weighted dot product.",
  ["Load ratings and pick popular movies", "Build user vectors (rows of a user×movie matrix)", "Cosine similarity between users", "Predict ratings with a similarity-weighted dot product", "Check against held-out ratings"],
  f'''
import numpy as np, pandas as pd
r = pd.read_csv("{MOVIES}ratings.dat", sep="::", engine="python", names=["user", "movie", "rating", "ts"])
top = r.movie.value_counts().index[:300]; r = r[r.movie.isin(top)]
active = r.user.value_counts(); r = r[r.user.isin(active[active >= 15].index)]
rng = np.random.default_rng(0); test_mask = rng.random(len(r)) < 0.1
M = r[~test_mask].pivot_table(index="user", columns="movie", values="rating")
mu = M.mean(1); C = M.sub(mu, axis=0).fillna(0).to_numpy()           # mean-centred user vectors
print("user vectors:", C.shape, "| sparsity:", round(M.isna().to_numpy().mean(), 3))
norm = np.linalg.norm(C, axis=1, keepdims=True) + 1e-9; S = (C / norm) @ (C / norm).T   # cosine similarity matrix
u = 0; print("most similar users to user 0:", np.argsort(-S[u])[1:6], "cos =", np.sort(S[u])[::-1][1:6].round(2))
uidx, midx = {{x: i for i, x in enumerate(M.index)}}, {{x: j for j, x in enumerate(M.columns)}}
err_cf, err_mean = [], []
for _, row in r[test_mask].iterrows():
    if row.user not in uidx or row.movie not in midx: continue
    i, j = uidx[row.user], midx[row.movie]; rated = C[:, j] != 0; w = S[i, rated]
    k = np.argsort(-w)[:30]; w, v = w[k], C[rated, j][k]
    pred = mu.iloc[i] + (w @ v) / (np.abs(w).sum() + 1e-9)               # weighted dot product
    err_cf.append((pred - row.rating) ** 2); err_mean.append((mu.iloc[i] - row.rating) ** 2)
print(f"held-out RMSE: user-mean {{np.sqrt(np.mean(err_mean)):.3f}} -> cosine neighbours {{np.sqrt(np.mean(err_cf)):.3f}}")
''')

X("m-norms",
  "A norm measures a vector's size; a distance is the norm of a difference. **L2** (straight line), **L1** (city blocks), **L∞** (largest coordinate). Norms define nearest neighbours, regularisation penalties (L1 → sparse, L2 → small weights) and gradient clipping.",
  """**Definitions.** ‖x‖ₚ = (Σ|xᵢ|ᵖ)^(1/p). L1 = Σ|xᵢ|, L2 = √Σxᵢ², L∞ = max|xᵢ|. Always ‖x‖∞ ≤ ‖x‖₂ ≤ ‖x‖₁. Unit balls: L2 circle, L1 diamond, L∞ square — the diamond's corners on the axes are why **L1 regularisation sets weights exactly to zero** (the loss contours first touch the ball at a corner). **Mahalanobis distance** √((x−μ)ᵀΣ⁻¹(x−μ)) accounts for scale and correlation. In high dimensions all pairwise distances concentrate (ratio of farthest/nearest → 1).""",
  """**By hand.** x = [3, −4, 1]: L1 = 8, L2 = √26 = **5.10**, L∞ = 4. Distance between [1, 1] and [4, 5]: L2 = 5, L1 = 7, L∞ = 4. Gradient clipping with max norm 1: g = [3, 4] (‖g‖ = 5) → g·(1/5) = **[0.6, 0.8]**.""",
  ["Using Euclidean distance on unscaled features", "Expecting L2 regularisation to zero out features", "Ignoring correlation (use Mahalanobis or whitening)"],
  ["kNN metric choice, Lasso vs Ridge, outlier scoring, clipping"], ["Very high-dimensional raw features with L2 kNN (distances lose meaning)"],
  "Penguins + MPG — compare L1/L2/L∞/Mahalanobis for kNN, see L1 vs L2 regularisation paths (sparsity), and spot outliers by Mahalanobis distance.",
  ["Compute the three norms on real rows", "kNN accuracy with different metrics", "Lasso vs Ridge coefficients as penalty grows", "Mahalanobis outlier detection", "Distance concentration in high dimension"],
  f'''
import numpy as np, pandas as pd
from scipy.spatial.distance import mahalanobis
from sklearn.linear_model import Lasso, Ridge
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
pg = pd.read_csv("{PENGUINS}").dropna(); X = pg[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]].to_numpy(); y = pg.species
d = X[0] - X[1]; print("row0-row1 distance  L1 %.1f  L2 %.1f  Linf %.1f" % (np.abs(d).sum(), np.linalg.norm(d), np.abs(d).max()))
for metric in ["manhattan", "euclidean", "chebyshev"]:
    raw = cross_val_score(KNeighborsClassifier(5, metric=metric), X, y, cv=5).mean()
    sc = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier(5, metric=metric)), X, y, cv=5).mean()
    print(f"  kNN {{metric:9s}} raw {{raw:.3f}} scaled {{sc:.3f}}")
mpg = pd.read_csv("{MPG}").dropna(); F = StandardScaler().fit_transform(mpg[["cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year"]])
for a in [0.01, 0.1, 0.5]:
    print(f"  alpha {{a}}: Lasso coefs {{Lasso(alpha=a).fit(F, mpg.mpg).coef_.round(2)}} | Ridge {{Ridge(alpha=a * 100).fit(F, mpg.mpg).coef_.round(2)}}")
mu, VI = X.mean(0), np.linalg.inv(np.cov(X.T)); md = np.array([mahalanobis(x, mu, VI) for x in X])
print("Mahalanobis outliers (top 3 rows):", pg.iloc[np.argsort(-md)[:3]][["species", "bill_depth_mm", "body_mass_g"]].to_dict("records"))
for dim in [2, 100, 10000]:
    Z = np.random.default_rng(0).random((200, dim)); dist = np.linalg.norm(Z[1:] - Z[0], axis=1); print(f"  dim {{dim:5d}}: farthest/nearest = {{dist.max() / dist.min():.2f}}")
''')

X("m-matrices",
  "A matrix is a table of numbers that is also a *function*: multiplying by it transforms vectors. A whole dataset is a matrix (rows = samples, columns = features), a neural-network layer is a matrix, and 'training on a batch' is one matrix multiplication.",
  """**Rules.** (m×n)(n×p) → (m×p): entry (i, j) = row i · column j. Not commutative (AB ≠ BA), associative, (AB)ᵀ = BᵀAᵀ. Identity I, inverse A⁻¹ (exists iff det ≠ 0 / full rank). Batched linear layer: Y = XWᵀ + b with X (batch × in), W (out × in). Gram matrix XᵀX (features × features) ∝ covariance when X is centred. Cost of multiplying n×n matrices ≈ 2n³ flops — why GPUs matter. Never compute A⁻¹b explicitly; solve Ax = b (more stable, faster).""",
  """**By hand.** A = [[1, 2], [3, 4]], x = [1, 1] → Ax = [3, 7]. A⁻¹ = (1/det)[[4, −2], [−3, 1]] with det = 4 − 6 = −2 → **[[−2, 1], [1.5, −0.5]]**; check A⁻¹[3, 7] = [−6+7, 4.5−3.5] = [1, 1] ✓. A layer with 784 inputs and 128 outputs on a batch of 64: (64×784)(784×128) → 64×128, ≈ 12.8M multiply-adds.""",
  ["Shape mismatches (transpose confusion)", "`*` (element-wise) vs `@` (matrix product)", "Computing inverses explicitly", "Python loops instead of one batched matmul"],
  ["Batch prediction, covariance, layers, linear systems"], ["Explicit inverses of ill-conditioned matrices"],
  "California housing (20,640 districts) — the dataset as a matrix, covariance as XᵀX, batch prediction as one matmul, solving a linear system, and timing loops vs @.",
  ["Load data into a feature matrix", "Covariance via centred XᵀX/(n−1) vs np.cov", "A random 'layer' applied to a batch with @", "Solve normal equations with solve vs inv", "Benchmark loop vs matmul"],
  f'''
import time, numpy as np, pandas as pd
df = pd.read_csv("{HOUSING}").dropna()
cols = ["median_income", "housing_median_age", "total_rooms", "population", "latitude", "longitude"]
X = df[cols].to_numpy(); y = df.median_house_value.to_numpy() / 1e5
print("data matrix:", X.shape)
Xc = X - X.mean(0); cov = Xc.T @ Xc / (len(X) - 1)
print("covariance via XᵀX matches np.cov:", np.allclose(cov, np.cov(X.T)))
Xs = Xc / X.std(0); W = np.random.default_rng(0).normal(0, 0.1, (16, 6)); b = np.zeros(16)
H = np.maximum(Xs @ W.T + b, 0); print("batched layer output:", H.shape, "(20k rows in one @)")
A = np.c_[np.ones(len(Xs)), Xs]; G, r = A.T @ A, A.T @ y
w1 = np.linalg.solve(G, r); w2 = np.linalg.inv(G) @ r
print("solve vs inv agree:", np.allclose(w1, w2), "| cond(AᵀA) =", f"{{np.linalg.cond(G):.1f}}", "| weights:", w1.round(3))
print("R² of linear fit:", round(1 - ((A @ w1 - y) ** 2).sum() / ((y - y.mean()) ** 2).sum(), 3))
n = 2000; t = time.perf_counter(); out = [[sum(Xs[i, k] * W[j, k] for k in range(6)) for j in range(16)] for i in range(n)]; tl = time.perf_counter() - t
t = time.perf_counter(); out2 = Xs[:n] @ W.T; tm = time.perf_counter() - t
print(f"same: {{np.allclose(out, out2)}} | python loops {{tl * 1000:.0f}} ms vs @ {{tm * 1000:.3f}} ms")
''')

X("m-lin-indep",
  "Vectors are linearly independent if none can be built from the others. The **rank** of a data matrix is how many genuinely different directions it has. Duplicate or derived features (total = a + b) reduce rank, which breaks linear regression's unique solution and inflates coefficients — the root of multicollinearity.",
  """**Definitions.** {v₁..vₖ} independent ⇔ c₁v₁ + … + cₖvₖ = 0 only for all cᵢ = 0. Span = all combinations; basis = independent spanning set; dimension = basis size. rank(X) = number of independent columns = number of non-zero singular values. If rank < #features, XᵀX is singular: infinitely many least-squares solutions. Numerically, near-dependence shows up as tiny singular values and a huge **condition number** σ_max/σ_min — small data changes swing the coefficients. Fixes: drop features, Ridge (adds λI, making XᵀX + λI invertible), PCA.""",
  """**By hand.** v₁ = [1, 2, 3], v₂ = [2, 4, 6] → v₂ = 2v₁, rank 1. Add v₃ = [0, 1, 1]: is there c with c₁v₁ + c₃v₃ = 0? From the first entry c₁ = 0, then c₃ = 0 → independent, rank **2**. One-hot encoding all K categories plus an intercept: the K columns sum to the intercept column → rank deficit 1 ('dummy trap').""",
  ["Keeping all one-hot columns plus an intercept", "Including a feature and its exact sum/difference", "Trusting coefficients when the condition number is huge"],
  ["Diagnosing multicollinearity, choosing features, understanding PCA"], ["Interpreting individual coefficients of highly collinear features"],
  "MPG cars — add a derived feature and a full one-hot encoding to create dependence, measure rank, singular values and condition number, and see coefficients explode vs Ridge.",
  ["Build a clean feature matrix; compute rank and singular values", "Add an exactly dependent column and the dummy trap; recompute", "Fit least squares and observe unstable coefficients", "Fix with drop_first and Ridge", "Bootstrap coefficient stability"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
df = pd.read_csv("{MPG}").dropna()
base = df[["weight", "horsepower", "displacement"]].astype(float); base = (base - base.mean()) / base.std()
def report(name, M):
    s = np.linalg.svd(M, compute_uv=False); print(f"{{name:28s}} rank {{np.linalg.matrix_rank(M)}}/{{M.shape[1]}}  smallest σ {{s[-1]:.2e}}  cond {{s[0] / s[-1]:.1e}}")
report("clean", base.to_numpy())
dep = base.assign(w_plus_hp=base.weight + base.horsepower); report("+ weight+horsepower", dep.to_numpy())
onehot = pd.get_dummies(df.origin, dtype=float); trap = np.c_[np.ones(len(df)), base, onehot]; report("intercept + all one-hot (trap)", trap)
report("drop_first", np.c_[np.ones(len(df)), base, pd.get_dummies(df.origin, drop_first=True, dtype=float)])
noisy = base.assign(w2=base.weight + np.random.default_rng(0).normal(0, 0.01, len(base))); report("near-duplicate", noisy.to_numpy())
rng = np.random.default_rng(1)
for model in [LinearRegression(), Ridge(alpha=10)]:
    coefs = []
    for _ in range(50):
        i = rng.integers(0, len(df), len(df)); coefs.append(model.fit(noisy.iloc[i], df.mpg.iloc[i]).coef_)
    c = np.array(coefs); print(f"{{type(model).__name__:16s}} weight/w2 coef mean {{c[:, [0, 3]].mean(0).round(1)}} sd {{c[:, [0, 3]].std(0).round(1)}}")
''')

X("m-lin-transform",
  "A matrix moves space: it can rotate, stretch, shear, project or reflect vectors. **Eigenvectors** are the special directions that only get stretched (by their eigenvalue). They reveal what a transformation 'really does' — and power PCA, PageRank, spectral clustering and stability analysis of RNNs.",
  """**Eigen-decomposition.** Av = λv. Solve det(A − λI) = 0 for λ. A symmetric matrix (like a covariance) has real eigenvalues and orthogonal eigenvectors: A = QΛQᵀ. **SVD** works for any matrix: A = UΣVᵀ (rotate → scale → rotate); singular values σᵢ = √eig(AᵀA). Determinant = product of eigenvalues = volume scaling. **Power iteration**: repeatedly multiply by A and normalise → converges to the top eigenvector (rate |λ₂/λ₁|) — how PageRank is computed. Repeatedly applying a matrix with |λ| > 1 explodes, < 1 vanishes (the RNN gradient story).""",
  """**By hand.** A = [[2, 1], [1, 2]]. det(A − λI) = (2−λ)² − 1 = 0 → λ = **3** and **1**. For λ = 3: (A − 3I)v = 0 → −v₁ + v₂ = 0 → v = [1, 1]/√2. For λ = 1: v = [1, −1]/√2. So A stretches the diagonal direction by 3 and leaves the anti-diagonal unchanged; det = 3·1 = 3.""",
  ["Assuming every matrix is diagonalisable or has real eigenvalues", "Forgetting eigenvectors are only defined up to sign/scale", "Using eig instead of eigh for symmetric matrices"],
  ["PCA, PageRank, spectral methods, stability analysis, low-rank approximation"], ["Huge sparse matrices with dense eig — use iterative solvers (scipy.sparse.linalg.eigsh)"],
  "Two real examples: the penguins covariance matrix (eigen-directions = principal components) and a Wikipedia-style link graph built from MovieTweetings co-ratings, ranked by power iteration (PageRank).",
  ["Eigen-decompose the covariance of penguin measurements", "Verify Av = λv and QΛQᵀ = A", "Transform data into the eigenbasis (decorrelation)", "Build a movie co-rating graph and run power iteration", "Compare with numpy's top eigenvector"],
  f'''
import numpy as np, pandas as pd
pg = pd.read_csv("{PENGUINS}").dropna(); X = pg[["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]].to_numpy()
Z = (X - X.mean(0)) / X.std(0); C = np.cov(Z.T)
lam, Q = np.linalg.eigh(C); lam, Q = lam[::-1], Q[:, ::-1]
print("eigenvalues:", lam.round(3), "| variance share:", (lam / lam.sum()).round(3))
print("Av = λv:", np.allclose(C @ Q[:, 0], lam[0] * Q[:, 0]), "| QΛQᵀ = C:", np.allclose(Q @ np.diag(lam) @ Q.T, C))
P = Z @ Q; print("covariance in eigenbasis is diagonal:", np.allclose(np.cov(P.T), np.diag(lam)), "| det =", round(np.linalg.det(C), 4), "= Πλ", round(lam.prod(), 4))
r = pd.read_csv("{MOVIES}ratings.dat", sep="::", engine="python", names=["user", "movie", "rating", "ts"])
top = r.movie.value_counts().index[:200]; r = r[r.movie.isin(top)]
B = pd.crosstab(r.user, r.movie).clip(upper=1).to_numpy().astype(float)
A = B.T @ B; np.fill_diagonal(A, 0); T = A / A.sum(0, keepdims=True)          # column-stochastic transition matrix
d, v = 0.85, np.ones(len(T)) / len(T)
for it in range(100):
    nv = d * T @ v + (1 - d) / len(T)
    if np.abs(nv - v).sum() < 1e-10: break
    v = nv
ev, evec = np.linalg.eig(d * T + (1 - d) / len(T)); top_vec = np.abs(evec[:, ev.real.argmax()].real); top_vec /= top_vec.sum()
print(f"power iteration converged in {{it}} steps; matches eig: {{np.allclose(v, top_vec, atol=1e-6)}}")
names = pd.read_csv("{MOVIES}movies.dat", sep="::", engine="python", names=["movie", "title", "genre"], encoding="latin-1").drop_duplicates("movie").set_index("movie").title
print("most 'central' movies:", [names.get(m, m) for m in np.array(sorted(top))[np.argsort(-v)[:5]]])
''')

X("m-least-squares",
  "Least squares finds the line (or hyperplane) whose predictions have the smallest total squared error. It's linear regression, the basis of many curve fits, and a clean example of turning a learning problem into linear algebra — the prediction is the **projection** of y onto the space spanned by the features.",
  """**Derivation.** Minimise L(w) = ‖Xw − y‖² = (Xw − y)ᵀ(Xw − y). Gradient: ∇L = 2Xᵀ(Xw − y). Set to 0 → **normal equations XᵀXw = Xᵀy** → w = (XᵀX)⁻¹Xᵀy (if full rank). Geometrically the residual y − Xw is orthogonal to every column of X (Xᵀr = 0), so ŷ = X(XᵀX)⁻¹Xᵀy = Hy is the projection of y. In practice solve with QR or SVD (`lstsq`) for stability; with Ridge: w = (XᵀX + λI)⁻¹Xᵀy. Under Gaussian noise, least squares = maximum likelihood.""",
  """**By hand.** Points (1, 1), (2, 3), (3, 2). X = [[1,1],[1,2],[1,3]] (intercept + x). XᵀX = [[3, 6], [6, 14]], Xᵀy = [6, 13]. det = 42 − 36 = 6 → inverse (1/6)[[14, −6], [−6, 3]] → w = (1/6)[84 − 78, −36 + 39] = **[1, 0.5]**: ŷ = 1 + 0.5x → predictions 1.5, 2, 2.5; residuals −0.5, 1, −0.5 sum to 0 ✓.""",
  ["Using the explicit inverse for ill-conditioned X", "Forgetting the intercept column", "Treating least squares as robust to outliers (it isn't — use Huber)"],
  ["Linear regression, calibration, polynomial and basis-function fits"], ["Heavy outliers or non-Gaussian noise — use robust losses"],
  "California housing — solve least squares four ways (normal equations, QR, SVD/lstsq, scikit-learn), verify residual orthogonality, add polynomial features, and compare to a robust fit with outliers.",
  ["Build the design matrix with an intercept", "Solve via normal equations, QR, lstsq and sklearn; compare", "Check Xᵀr = 0 and R²", "Polynomial basis for a curved relation", "Show outlier sensitivity vs HuberRegressor"],
  f'''
import numpy as np, pandas as pd
from sklearn.linear_model import HuberRegressor, LinearRegression
df = pd.read_csv("{HOUSING}").dropna()
cols = ["median_income", "housing_median_age", "latitude", "longitude"]
Xr = df[cols].to_numpy(); Xs = (Xr - Xr.mean(0)) / Xr.std(0); y = df.median_house_value.to_numpy() / 1e5
X = np.c_[np.ones(len(Xs)), Xs]
w_ne = np.linalg.solve(X.T @ X, X.T @ y)
Q, R = np.linalg.qr(X); w_qr = np.linalg.solve(R, Q.T @ y)
w_ls = np.linalg.lstsq(X, y, rcond=None)[0]
sk = LinearRegression().fit(Xs, y); w_sk = np.r_[sk.intercept_, sk.coef_]
print("normal eq:", w_ne.round(4)); print("all four agree:", all(np.allclose(w_ne, w, atol=1e-6) for w in [w_qr, w_ls, w_sk]))
r = y - X @ w_ne; print("residuals orthogonal to features (max |Xᵀr|):", f"{{np.abs(X.T @ r).max():.1e}}", "| R²:", round(1 - r @ r / ((y - y.mean()) ** 2).sum(), 3))
inc = df.median_income.to_numpy()
for deg in [1, 2, 3]:
    P = np.vander((inc - inc.mean()) / inc.std(), deg + 1); w = np.linalg.lstsq(P, y, rcond=None)[0]
    print(f"  income polynomial degree {{deg}}: R² {{1 - ((y - P @ w) ** 2).sum() / ((y - y.mean()) ** 2).sum():.3f}}")
s = df.sample(300, random_state=0); xs, ys = s[["median_income"]].to_numpy(), s.median_house_value.to_numpy() / 1e5
ys_bad = ys.copy(); ys_bad[np.argsort(xs[:, 0])[-10:]] = 0.1                 # 10 corrupted labels at high income
print("slope clean OLS %.3f | corrupted OLS %.3f | corrupted Huber %.3f" % (LinearRegression().fit(xs, ys).coef_[0], LinearRegression().fit(xs, ys_bad).coef_[0], HuberRegressor().fit(xs, ys_bad).coef_[0]))
''')

X("m-derivatives",
  "A derivative is the slope of a function at a point — how much the output changes per tiny change in the input. Training a model is 'move each weight a little in the direction that lowers the loss', and the derivative tells you which direction and how steep.",
  """**Definition.** f′(x) = lim_{h→0} (f(x+h) − f(x))/h. Rules: (xⁿ)′ = nxⁿ⁻¹; (eˣ)′ = eˣ; (ln x)′ = 1/x; product (uv)′ = u′v + uv′; **chain rule** (f(g(x)))′ = f′(g(x))·g′(x) — the heart of backpropagation. Useful ML derivatives: sigmoid σ′ = σ(1 − σ) (max 0.25 → vanishing gradients); tanh′ = 1 − tanh²; ReLU′ = 1 if x > 0 else 0; d/dz of −log σ(z) = σ(z) − 1. Numerically, the **central difference** (f(x+h) − f(x−h))/2h has error O(h²) vs O(h) for the forward difference — used for gradient checking.""",
  """**By hand.** f(x) = (3x + 1)². Chain rule: f′ = 2(3x + 1)·3 → f′(1) = 2·4·3 = **24**. Check numerically with h = 0.001: (f(1.001) − f(0.999))/0.002 = (16.024009 − 15.976009)/0.002 = **24.0**. Sigmoid at z = 0: σ = 0.5, σ′ = 0.25; at z = 5: σ = 0.9933, σ′ = **0.0066** (saturated).""",
  ["Forward difference with too large/small h (truncation vs round-off)", "Forgetting the inner derivative in the chain rule", "Assuming ReLU is differentiable at 0 (frameworks pick 0)"],
  ["Gradient checks, understanding activations, sensitivity analysis"], ["Non-smooth objectives where derivatives don't exist — use subgradients or derivative-free methods"],
  "Real fit on the MPG data: logistic 'is this car efficient (mpg > 25)?' with one feature (weight). Derive dLoss/dw by hand, check it against finite differences and PyTorch autograd, then use it to train.",
  ["Define the loss of a 1-feature logistic model", "Derive the derivative with the chain rule", "Gradient check with central differences at several h", "Compare with torch autograd", "Train with the derivative and report accuracy"],
  f'''
import numpy as np, pandas as pd, torch
df = pd.read_csv("{MPG}").dropna(); x = ((df.weight - df.weight.mean()) / df.weight.std()).to_numpy(); y = (df.mpg > 25).astype(float).to_numpy()
sig = lambda z: 1 / (1 + np.exp(-z))
def loss(w, b): p = sig(w * x + b); return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
def grad(w, b):                                   # chain rule: dL/dz = p - y, dz/dw = x, dz/db = 1
    p = sig(w * x + b); return np.mean((p - y) * x), np.mean(p - y)
w0, b0 = 0.3, -0.2; gw, gb = grad(w0, b0)
for h in [1e-1, 1e-4, 1e-8, 1e-12]:
    num = (loss(w0 + h, b0) - loss(w0 - h, b0)) / (2 * h); print(f"  h={{h:.0e}}: numeric {{num:.10f}} | analytic {{gw:.10f}} | rel err {{abs(num - gw) / abs(gw):.1e}}")
wt, bt = torch.tensor(w0, requires_grad=True), torch.tensor(b0, requires_grad=True)
torch.nn.functional.binary_cross_entropy_with_logits(wt * torch.tensor(x) + bt, torch.tensor(y)).backward()
print("autograd:", round(wt.grad.item(), 10), round(bt.grad.item(), 10), "| ours:", round(gw, 10), round(gb, 10))
w, b = 0.0, 0.0
for step in range(300):
    gw, gb = grad(w, b); w, b = w - 0.5 * gw, b - 0.5 * gb
print(f"trained: w={{w:.2f}} b={{b:.2f}} loss={{loss(w, b):.3f}} accuracy={{((sig(w * x + b) > 0.5) == y).mean():.3f}}")
print("weight (kg-ish) where P(efficient)=0.5:", round(df.weight.mean() + (-b / w) * df.weight.std()), "lbs")
''')

X("m-gradients",
  "With many weights, the derivative becomes a **gradient** — a vector of partial derivatives pointing uphill. Gradient descent steps the opposite way. The Jacobian (for vector outputs) and Hessian (curvature) extend the idea; backprop is the chain rule applied to these.",
  """**Definitions.** ∇f(w) = [∂f/∂w₁, …, ∂f/∂wₙ]. Direction of steepest ascent; its norm is the slope. **Gradient descent:** w ← w − η∇f(w). For MSE linear regression L = (1/n)‖Xw − y‖², ∇L = (2/n)Xᵀ(Xw − y). For softmax + cross-entropy, ∂L/∂z = p − onehot(y). **Hessian** H = matrix of second derivatives; its eigenvalues are curvatures: the step size must satisfy η < 2/λ_max for stability, and the condition number λ_max/λ_min sets how slow GD crawls along flat directions. Mini-batch gradients are unbiased noisy estimates of the full gradient.""",
  """**By hand.** f(w₁, w₂) = w₁² + 10w₂². ∇f = [2w₁, 20w₂]; at (1, 1): [2, 20]. Hessian diag(2, 20): η must be < 2/20 = 0.1. With η = 0.09 a step gives w = (1 − 0.18, 1 − 1.8) = **(0.82, −0.8)** — oscillating in w₂; with η = 0.11 the w₂ coordinate grows (|1 − 2.2| = 1.2 > 1) → diverges.""",
  ["Step size too large for the curvature (divergence)", "Unscaled features → ill-conditioned Hessian → slow zig-zag", "Forgetting to average gradients over the batch"],
  ["Training any differentiable model"], ["Discrete/non-differentiable objectives — use search, RL, or surrogate losses"],
  "California housing — derive the MSE gradient, check it numerically, run full-batch vs mini-batch gradient descent, and show how feature scaling changes the Hessian condition number and convergence.",
  ["Write loss and analytic gradient for linear regression", "Gradient-check a few coordinates", "Compute Hessian eigenvalues → max stable learning rate", "Run GD on raw vs standardised features", "Run mini-batch SGD and compare"],
  f'''
import numpy as np, pandas as pd
df = pd.read_csv("{HOUSING}").dropna()
Xraw = df[["median_income", "housing_median_age", "total_rooms", "latitude"]].to_numpy(); y = df.median_house_value.to_numpy() / 1e5
def design(M): return np.c_[np.ones(len(M)), M]
L = lambda w, X: np.mean((X @ w - y) ** 2); G = lambda w, X: 2 / len(X) * X.T @ (X @ w - y)
Xs = design((Xraw - Xraw.mean(0)) / Xraw.std(0)); w = np.random.default_rng(0).normal(size=5); g = G(w, Xs)
num = [(L(w + e, Xs) - L(w - e, Xs)) / 2e-6 for e in np.eye(5) * 1e-6]; print("gradient check max rel err:", f"{{np.max(np.abs(num - g) / np.abs(g)):.1e}}")
for name, X in [("raw", design(Xraw)), ("standardised", Xs)]:
    lam = np.linalg.eigvalsh(2 / len(X) * X.T @ X); eta = 1.9 / lam.max(); w = np.zeros(5)
    for _ in range(500): w -= eta * G(w, X)
    print(f"{{name:12s}} condition number {{lam.max() / lam.min():.1e}} | max stable lr {{2 / lam.max():.1e}} | loss after 500 GD steps {{L(w, X):.4f}}")
best = np.linalg.lstsq(Xs, y, rcond=None)[0]; print("optimum loss:", round(L(best, Xs), 4))
rng = np.random.default_rng(0); w = np.zeros(5)
for epoch in range(5):
    for idx in np.array_split(rng.permutation(len(Xs)), len(Xs) // 64):
        w -= 0.02 * 2 / len(idx) * Xs[idx].T @ (Xs[idx] @ w - y[idx])      # gradient on 64 rows only
    print(f"  mini-batch SGD epoch {{epoch + 1}}: loss {{L(w, Xs):.4f}}")
''')

X("m-integration",
  "Integration adds up infinitely many tiny pieces — the area under a curve. In ML it gives probabilities from densities, expectations (average loss over the data distribution), the AUC metric, and normalising constants in Bayesian models. When integrals are too hard, we estimate them by **sampling** (Monte Carlo).",
  """**Key facts.** ∫ₐᵇ f(x)dx = F(b) − F(a) where F′ = f. Expectation E[g(X)] = ∫ g(x)p(x)dx. **Numerical:** trapezoid rule error O(h²); Simpson O(h⁴). **Monte Carlo:** E[g(X)] ≈ (1/N)Σg(xᵢ) with xᵢ ~ p; error ∝ σ/√N **independent of dimension** — why sampling beats grids in high dimension. **Importance sampling:** draw from q and weight by p/q. ROC-AUC = ∫₀¹ TPR d(FPR) = P(score of random positive > random negative).""",
  """**By hand.** ∫₀¹ x² dx = 1/3. Trapezoid with h = 0.5: 0.5·(0 + 0.25)/2 + 0.5·(0.25 + 1)/2 = 0.0625 + 0.3125 = **0.375** (error 0.042). Monte Carlo with 4 samples 0.1, 0.4, 0.7, 0.9 → mean of x² = (0.01 + 0.16 + 0.49 + 0.81)/4 = **0.3675**. **AUC:** with positive scores {0.9, 0.6} and negatives {0.7, 0.2}, 3 of 4 pairs are ordered correctly → AUC = **0.75**.""",
  ["Thinking a density value is a probability", "Too few Monte Carlo samples without reporting the error", "Computing AUC with a coarse threshold grid"],
  ["AUC, expected loss/risk, Bayesian marginal likelihoods, probabilities from PDFs"], ["Low-dimensional smooth integrals where quadrature is exact and cheaper than sampling"],
  "Pima diabetes model — compute ROC-AUC three ways (trapezoid on the ROC curve, pairwise probability, sklearn), integrate a fitted glucose density to get a probability, and estimate an expected cost by Monte Carlo.",
  ["Train a classifier and get test scores", "AUC by trapezoid integration of the ROC curve", "AUC as P(pos > neg) by counting pairs", "Integrate a KDE to get P(glucose > 140) vs counting", "Monte Carlo expected cost of a screening policy with error bars"],
  f'''
import numpy as np, pandas as pd
from scipy import integrate, stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
cols = ["pregnancies", "glucose", "bp", "skin", "insulin", "bmi", "pedigree", "age", "diabetes"]
df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv", names=cols)
Xtr, Xte, ytr, yte = train_test_split(df.drop(columns="diabetes"), df.diabetes, test_size=0.3, random_state=0, stratify=df.diabetes)
s = LogisticRegression(max_iter=5000).fit(Xtr, ytr).predict_proba(Xte)[:, 1]; yte = yte.to_numpy()
fpr, tpr, _ = roc_curve(yte, s)
pairs = (s[yte == 1][:, None] > s[yte == 0][None]).mean() + 0.5 * (s[yte == 1][:, None] == s[yte == 0][None]).mean()
print(f"AUC trapezoid {{np.trapezoid(tpr, fpr):.4f}} | P(pos>neg) {{pairs:.4f}} | sklearn {{roc_auc_score(yte, s):.4f}}")
g = df.glucose[df.glucose > 0].to_numpy(); kde = stats.gaussian_kde(g)
area, err = integrate.quad(lambda t: kde(t)[0], 140, 300); print(f"P(glucose>140): integral of KDE {{area:.3f}} (±{{err:.0e}}) vs counting {{(g > 140).mean():.3f}}")
print("total density integrates to", round(integrate.quad(lambda t: kde(t)[0], 0, 400)[0], 4))
rng = np.random.default_rng(0)
def cost(threshold, n):                      # missed case costs 10, unnecessary follow-up costs 1
    i = rng.integers(0, len(s), n); flag = s[i] > threshold
    return np.where(flag & (yte[i] == 0), 1, 0) + np.where(~flag & (yte[i] == 1), 10, 0)
for t in [0.2, 0.5]:
    c = cost(t, 100000); print(f"threshold {{t}}: expected cost per patient {{c.mean():.3f}} ± {{1.96 * c.std() / np.sqrt(len(c)):.3f}}")
''')

X("m-optim-math",
  "Optimisation is the engine of learning: define a loss, then search for the parameters that minimise it. Understanding convexity, step sizes, momentum, constraints (Lagrange multipliers) and second-order methods explains why some models train reliably and others need careful tuning.",
  """**Convexity.** f is convex if f(λa + (1−λ)b) ≤ λf(a) + (1−λ)f(b); then every local minimum is global (linear/logistic regression, SVM). Neural nets are non-convex but SGD finds good minima. **Methods:** GD w ← w − η∇f; momentum v ← βv + ∇f, w ← w − ηv (smooths zig-zags); **Newton** w ← w − H⁻¹∇f (quadratic convergence, expensive); quasi-Newton **L-BFGS** approximates H⁻¹ from gradient history (scikit-learn's default for logistic regression). **Constraints:** minimise f subject to g(w) = 0 → Lagrangian ℒ = f + λg, set ∇ℒ = 0 (SVM dual, max-entropy). **Learning-rate schedules** (step, cosine, warm-up) trade early progress vs final precision.""",
  """**Newton by hand.** f(w) = w² − 4w + 5 (minimum at 2). f′ = 2w − 4, f″ = 2. From w = 10: Newton step w − f′/f″ = 10 − 16/2 = **2** in one step. GD with η = 0.1: 10 − 0.1·16 = 8.4, then 7.12, … (geometric 0.8 factor). **Lagrange:** maximise xy s.t. x + y = 10 → ℒ = xy − λ(x + y − 10) → y = λ, x = λ → x = y = **5**.""",
  ["Learning rate too high (divergence) or too low (stalls)", "Assuming a non-convex problem has a unique answer (use seeds/restarts)", "Newton's method on huge models (Hessian is n×n)", "Not checking convergence warnings"],
  ["Choosing solvers, tuning learning rates, understanding SVM/regularisation as constrained problems"], ["Hand-rolled optimisers in production — use library solvers"],
  "Pima diabetes logistic regression — minimise the same convex loss with GD, momentum, Newton's method and SciPy's L-BFGS; compare iterations-to-converge; then solve a constrained problem (budget allocation) with a Lagrange multiplier / SLSQP.",
  ["Write the logistic loss, gradient and Hessian", "Run GD and momentum", "Run Newton's method", "Run scipy.optimize.minimize (L-BFGS)", "Constrained optimisation with SLSQP and check against the Lagrange solution"],
  '''
import numpy as np, pandas as pd
from scipy.optimize import minimize
cols = ["pregnancies", "glucose", "bp", "skin", "insulin", "bmi", "pedigree", "age", "diabetes"]
df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv", names=cols)
X = df.drop(columns="diabetes").to_numpy(float); X = np.c_[np.ones(len(X)), (X - X.mean(0)) / X.std(0)]; y = df.diabetes.to_numpy()
sig = lambda z: 1 / (1 + np.exp(-z))
f = lambda w: -np.mean(y * np.log(sig(X @ w)) + (1 - y) * np.log(1 - sig(X @ w)))
g = lambda w: X.T @ (sig(X @ w) - y) / len(y)
H = lambda w: (X * (sig(X @ w) * (1 - sig(X @ w)))[:, None]).T @ X / len(y)
opt = minimize(f, np.zeros(9), jac=g, method="L-BFGS-B"); target = opt.fun + 1e-6
def run(name, step):
    w, v = np.zeros(9), np.zeros(9)
    for i in range(1, 20001):
        w, v = step(w, v)
        if f(w) < target: break
    print(f"  {name:10s} reached optimum loss {f(w):.5f} in {i:5d} iterations")
run("GD", lambda w, v: (w - 1.0 * g(w), v))
run("momentum", lambda w, v: (w - 0.4 * (0.8 * v + g(w)), 0.8 * v + g(w)))
run("Newton", lambda w, v: (w - np.linalg.solve(H(w), g(w)), v))
print(f"  L-BFGS     reached {opt.fun:.5f} in {opt.nit} iterations (convex: Hessian eigenvalues all > 0: {bool((np.linalg.eigvalsh(H(opt.x)) > 0).all())})")
# constrained: split a 100-unit budget over 3 channels with diminishing returns a*log(1+x); maximise total return
a = np.array([3.0, 2.0, 1.0])
res = minimize(lambda x: -(a * np.log1p(x)).sum(), np.full(3, 100 / 3), method="SLSQP", bounds=[(0, 100)] * 3, constraints={"type": "eq", "fun": lambda x: x.sum() - 100})
lam = (a.sum()) / (100 + 3); analytic = a / lam - 1        # from d/dx [a log(1+x)] = λ for every channel
print("SLSQP allocation:", res.x.round(2), "| Lagrange solution:", analytic.round(2))
''')
