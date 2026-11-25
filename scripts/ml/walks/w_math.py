"""Real-data walkthroughs: Linear algebra and calculus."""
import math
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt


def _pen():
    pg = D("penguins").dropna().reset_index(drop=True)
    return pg


@walk("m-vectors", "penguins")
def _():
    pg = _pen(); cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]
    a = pg.loc[0, cols].to_numpy(float); b = pg.loc[pg.species.eq("Gentoo").idxmax(), cols].to_numpy(float)
    mean_a = pg[pg.species == "Adelie"][cols].mean().to_numpy()
    return [
        ("A penguin is a vector", f"Each penguin = a list of numbers, one per measurement. An Adelie: **a** = {a.tolist()}; a Gentoo: **g** = {b.tolist()} (bill length, bill depth, flipper length in mm)."),
        ("Add, subtract, scale", f"**g** − **a** = {np.round(b - a, 1).tolist()}: the Gentoo's bill is longer, shallower, and its flipper is {b[2] - a[2]:.0f} mm longer. 0.5 × (**a** + **g**) = {np.round(0.5 * (a + b), 2).tolist()}, the point halfway between them. The average of all Adelie vectors: {np.round(mean_a, 1).tolist()}."),
        ("Dot product and angle", f"**a** · **g** = Σ aᵢgᵢ = {a @ b:,.1f}. cos(angle) = **a**·**g** / (|**a**| |**g**|) = {a @ b / np.linalg.norm(a) / np.linalg.norm(b):.4f}: almost 1, because all penguins point in a similar direction (all measurements positive). Centre the data first (subtract the average penguin) and the cosine becomes {((a - pg[cols].mean().values) @ (b - pg[cols].mean().values)) / np.linalg.norm(a - pg[cols].mean().values) / np.linalg.norm(b - pg[cols].mean().values):.2f}: they point in nearly opposite directions from the average."),
    ], "Data rows are vectors; adding, scaling and dot products are how models combine and compare them."


@walk("m-norms", "penguins")
def _():
    pg = _pen(); cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]
    a = pg.loc[0, cols].to_numpy(float); others = pg[cols].to_numpy(float)
    d = others - a
    l2 = np.linalg.norm(d, axis=1); l1 = np.abs(d).sum(1); linf = np.abs(d).max(1)
    near = pd.DataFrame({"norm": ["L2 (straight-line)", "L1 (sum of absolute differences)", "L∞ (largest single difference)"], "nearest other penguin": [int(np.argsort(v)[1]) for v in (l2, l1, linf)],
                         "its species": [pg.species[int(np.argsort(v)[1])] for v in (l2, l1, linf)], "distance": [np.sort(v)[1] for v in (l2, l1, linf)]})
    v = d[np.argsort(l2)[1]]
    Xa = others; dis = 0
    for i in range(100):
        dd = Xa - Xa[i]; n2 = np.argsort(np.linalg.norm(dd, axis=1))[1]; n1 = np.argsort(np.abs(dd).sum(1))[1]; ni = np.argsort(np.abs(dd).max(1))[1]
        dis += not (n2 == n1 == ni)
    return [
        ("Length of a difference vector", f"Penguin 0 vs its nearest neighbour: difference {np.round(v, 1).tolist()}. L2 = √(Σ dᵢ²) = **{np.linalg.norm(v):.2f}**, L1 = Σ |dᵢ| = **{np.abs(v).sum():.2f}**, L∞ = max |dᵢ| = **{np.abs(v).max():.2f}**."),
        ("Which neighbour each norm picks", f"{t(near, nd=2)}\n\n{'For penguin 0 all three norms agree. ' if len(set(near['nearest other penguin'])) == 1 else ''}Over the first 100 penguins the three norms disagree about the nearest neighbour for **{dis}** of them: L1 cares about the total of all differences, L∞ only about the worst one."),
        ("Norms in ML", f"k-NN and k-means use L2 distances. Regularisation penalises the size of the weight vector: L2 (ridge) shrinks all weights, L1 (lasso) pushes many to exactly zero. Normalising a vector to length 1 (divide by its L2 norm) is what cosine similarity does."),
    ], "A norm measures the size of a vector; the choice of norm decides what 'close' and 'small' mean."


@walk("m-matrices", "tips")
def _():
    df = D("tips"); X = df[["total_bill", "size"]].head(4).to_numpy(float)
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression().fit(df[["total_bill", "size"]], df["tip"])
    w, b = lr.coef_, lr.intercept_
    pred = X @ w + b
    tab = pd.DataFrame({"bill": X[:, 0], "size": X[:, 1], "X @ w + b = predicted tip": pred, "real tip": df["tip"].head(4).values})
    G = X.T @ X
    return [
        ("A table is a matrix", f"4 real bills × 2 features → X has shape {X.shape}:\n\n{t(pd.DataFrame(X, columns=['bill', 'size']))}"),
        ("Matrix × vector = predictions for every row at once", f"A linear model fitted on all 244 bills has weights **w** = [{w[0]:.4f}, {w[1]:.4f}] and bias b = {b:.3f}. One matrix product gives all predictions:\n\n{t(tab, nd=2)}\n\nRow 1: {X[0, 0]} × {w[0]:.4f} + {X[0, 1]:.0f} × {w[1]:.4f} + {b:.3f} = {pred[0]:.2f}."),
        ("Transpose and matrix × matrix", f"Xᵀ has shape {X.T.shape}. XᵀX (shape {G.shape}) = \n\n{t(pd.DataFrame(G, index=['bill', 'size'], columns=['bill', 'size']), nd=1, index=True)}\n\nIt holds sums of squares and cross-products; it appears in the least-squares formula and in PCA. A neural network layer is the same product with a bigger W."),
    ], "Matrices hold whole datasets; one matrix multiplication applies a model to every row."


@walk("m-lin-indep", "housing")
def _():
    h = D("housing").dropna()
    cols = ["total_rooms", "households", "population", "total_bedrooms"]
    X = h[cols].to_numpy(float)
    X2 = np.c_[X, X[:, 0] + X[:, 3]]
    r1, r2 = np.linalg.matrix_rank(X), np.linalg.matrix_rank(X2)
    sv = np.linalg.svd((X - X.mean(0)) / X.std(0), compute_uv=False)
    from sklearn.linear_model import LinearRegression
    y = h["median_house_value"].values
    fits = []
    for s in [0, 1]:
        rng = np.random.default_rng(s); idx = rng.choice(len(h), len(h), replace=True)
        fits.append(LinearRegression().fit(h[cols].iloc[idx], y[idx]).coef_)
    co = pd.DataFrame(fits, columns=cols, index=["bootstrap sample 1", "bootstrap sample 2"]).round(1)
    return [
        ("Exact dependence", f"Columns {cols} of the real housing data: rank **{r1}** (all 4 independent). Add a 5th column = total_rooms + total_bedrooms: rank stays **{r2}**. The new column adds no new information; it is a linear combination of others, and XᵀX can no longer be inverted."),
        ("Near dependence (multicollinearity)", f"These four counts all grow with the size of the district, so they are *almost* dependent. Singular values of the standardised columns: {', '.join(f'{v:.1f}' for v in sv)}. The last ones are small compared with the first: some combination of columns is nearly constant."),
        ("Why it matters", f"Fit house value on these columns twice on resampled data:\n\n{t(co, index=True)}\n\nThe weights shift between samples, and some get signs that are hard to believe (more bedrooms *lowering* value, holding the other counts fixed) because the model can trade one nearly-duplicate column off against another. Fix: drop or combine columns (e.g. rooms per household) or use ridge regression."),
    ], "Columns are linearly dependent when one can be built from others; near-dependence makes model weights unstable."


@walk("m-lin-transform", "penguins")
def _():
    pg = _pen(); cols = ["bill_length_mm", "flipper_length_mm"]
    X = pg[cols].to_numpy(float); Xc = X - X.mean(0)
    th = np.deg2rad(30); R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]); S = np.diag([1 / X.std(0)[0], 1 / X.std(0)[1]])
    C = np.cov(Xc.T); vals, vecs = np.linalg.eigh(C); P = vecs[:, ::-1]
    rows = pd.DataFrame({"penguin": [0, 1], "centred (bill, flipper)": [str(np.round(Xc[i], 1).tolist()) for i in [0, 1]], "rotated 30°": [str(np.round(R @ Xc[i], 1).tolist()) for i in [0, 1]], "scaled (÷ sd)": [str(np.round(S @ Xc[i], 2).tolist()) for i in [0, 1]], "onto eigenvectors (PCA)": [str(np.round(P.T @ Xc[i], 1).tolist()) for i in [0, 1]]})
    return [
        ("A matrix moves points", f"Multiplying every penguin vector by a 2 × 2 matrix transforms the whole cloud. Rotation R (30°) = {np.round(R, 3).tolist()}; scaling S = diag(1/sd) = {np.round(S, 4).tolist()}."),
        ("The same two real penguins, transformed", t(rows)),
        ("Eigenvectors: directions a matrix only stretches", f"The covariance matrix of (bill, flipper) is {np.round(C, 1).tolist()}. Its eigenvectors {np.round(P.T, 3).tolist()} have eigenvalues {np.round(vals[::-1], 1).tolist()}: the cloud spreads {vals[-1] / vals[0]:.0f}× more along the first direction. Projecting onto them is exactly PCA. Rotations keep lengths (det R = {np.linalg.det(R):.0f}); S changes them."),
    ], "Matrices are transformations (rotate, scale, project); eigenvectors are the directions they only stretch."


@walk("m-least-squares", "tips")
def _():
    df = D("tips"); X = np.c_[np.ones(len(df)), df[["total_bill", "size"]].to_numpy(float)]; y = df["tip"].to_numpy(float)
    w = np.linalg.solve(X.T @ X, X.T @ y)
    wl = np.linalg.lstsq(X, y, rcond=None)[0]
    r = y - X @ w
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression().fit(df[["total_bill", "size"]], y)
    tab = pd.DataFrame({"bill": df.total_bill.head(4), "size": df["size"].head(4), "real tip": y[:4], "fitted": (X @ w)[:4], "residual": r[:4]})
    return [
        ("Set up y ≈ Xw", f"X = [1, bill, size] for all {len(df)} real bills (shape {X.shape}), y = tips. We want the w that makes the squared errors Σ(y − Xw)² as small as possible."),
        ("Solve the normal equations", f"XᵀX w = Xᵀy → w = **[{w[0]:.4f}, {w[1]:.4f}, {w[2]:.4f}]** (intercept, per $ of bill, per person). `np.linalg.lstsq` gives {np.round(wl, 4).tolist()}; scikit-learn gives intercept {lr.intercept_:.4f}, weights {np.round(lr.coef_, 4).tolist()}: the same answer three ways."),
        ("Residuals", f"{t(tab, nd=2)}\n\nThe residuals are perpendicular to every column of X: Xᵀr = {np.round(X.T @ r, 8).tolist()} (≈ 0). RMSE = {np.sqrt(np.mean(r ** 2)):.3f} dollars; R² = {1 - (r ** 2).sum() / ((y - y.mean()) ** 2).sum():.3f}."),
    ], "Least squares finds the weights that minimise squared errors; the solution satisfies XᵀXw = Xᵀy and leaves residuals orthogonal to the features."


@walk("m-derivatives", "tips")
def _():
    df = D("tips"); x, y = df["total_bill"].values, df["tip"].values
    L = lambda k: np.mean((y - k * x) ** 2)
    k0 = 0.1; h = 1e-4
    num = (L(k0 + h) - L(k0 - h)) / (2 * h); ana = np.mean(-2 * x * (y - k0 * x))
    ks = pd.DataFrame({"slope k (tip = k × bill)": [0.10, 0.12, 0.14, 0.16, 0.18], "loss L(k) = mean (tip − k·bill)²": [L(k) for k in [0.10, 0.12, 0.14, 0.16, 0.18]], "derivative dL/dk": [np.mean(-2 * x * (y - k * x)) for k in [0.10, 0.12, 0.14, 0.16, 0.18]]})
    kbest = (x @ y) / (x @ x)
    return [
        ("A loss that depends on one number", f"Model: tip = k × bill (no intercept), on the 244 real bills. For each k the mean squared error is different:\n\n{t(ks, nd=4)}"),
        ("The derivative is the slope of the loss", f"At k = {k0}: nudging k by ±{h} gives a slope (L(k+h) − L(k−h)) / 2h = **{num:.4f}**. The calculus rule gives dL/dk = mean(−2 · bill · (tip − k · bill)) = **{ana:.4f}**: the same. Negative slope → increase k to go downhill."),
        ("Zero derivative = the minimum", f"Setting dL/dk = 0 gives k = Σ bill·tip / Σ bill² = **{kbest:.4f}**: tips are about {100 * kbest:.1f}% of the bill. The table shows the derivative changing sign between 0.14 and 0.16, right where the loss is smallest."),
    ], "A derivative measures how fast the loss changes when one parameter moves; at the best value it is zero."


@walk("m-gradients", "housing")
def _():
    h = D("housing").dropna()
    from sklearn.preprocessing import StandardScaler
    cols = ["median_income", "housing_median_age"]
    X = StandardScaler().fit_transform(h[cols]); X = np.c_[np.ones(len(X)), X]; y = h["median_house_value"].values / 1e5
    w = np.zeros(3); lr = 0.1; log = []
    for it in range(101):
        r = X @ w - y; g = 2 * X.T @ r / len(y); L = np.mean(r ** 2)
        if it in (0, 1, 2, 5, 20, 100): log.append({"step": it, "w (bias, income, age)": str(np.round(w, 3).tolist()), "gradient": str(np.round(g, 3).tolist()), "loss (MSE)": L})
        w = w - lr * g
    exact = np.linalg.lstsq(X, y, rcond=None)[0]
    return [
        ("Many parameters → a gradient", f"Predict house value (in $100k) from standardised income and house age for {len(y):,} real districts: ŷ = w₀ + w₁·income + w₂·age. The gradient ∇L = (∂L/∂w₀, ∂L/∂w₁, ∂L/∂w₂) = 2Xᵀ(Xw − y)/n points uphill."),
        ("Gradient descent: step against it", f"w ← w − 0.1 × ∇L, starting from 0:\n\n{t(pd.DataFrame(log), nd=4)}"),
        ("Where it ends up", f"After 100 steps w = {np.round(w, 3).tolist()}; the exact least-squares answer is {np.round(exact, 3).tolist()}. The gradient shrinks as we approach the minimum, so steps get smaller on their own. Neural networks do the same with millions of weights, using backpropagation to compute the gradient."),
    ], "The gradient collects all partial derivatives; stepping against it lowers the loss, which is how models are trained."


@walk("m-integration", "penguins")
def _():
    from scipy import stats, integrate
    pg = _pen(); f = pg[pg.species == "Gentoo"]["body_mass_g"]; mu, sd = f.mean(), f.std()
    pdf = lambda x: stats.norm.pdf(x, mu, sd)
    a, b = 4500, 5500
    xs = np.linspace(a, b, 11); trap = np.trapezoid(pdf(xs), xs) if hasattr(np, "trapezoid") else np.trapz(pdf(xs), xs)
    quad = integrate.quad(pdf, a, b)[0]
    rng = np.random.default_rng(0); mc = np.mean((lambda s: (s > a) & (s < b))(rng.normal(mu, sd, 100000)))
    ex = integrate.quad(lambda x: x * pdf(x), mu - 8 * sd, mu + 8 * sd)[0]
    return [
        ("Probability = area under the curve", f"Body mass of {len(f)} real Gentoo penguins ≈ normal with mean {mu:.0f} g, sd {sd:.0f} g. P({a} g < mass < {b} g) = ∫ pdf(x) dx from {a} to {b}."),
        ("Three ways to compute the area", f"- Trapezoid rule with 10 slices: **{trap:.4f}**\n- `scipy.integrate.quad` (adaptive): **{quad:.4f}**\n- Monte Carlo (share of 100,000 simulated penguins in range): **{mc:.4f}**\n- Exact via the CDF: {stats.norm.cdf(b, mu, sd) - stats.norm.cdf(a, mu, sd):.4f}\n\nReal data: {((f > a) & (f < b)).mean():.4f} of the penguins.{" The gap is the model's fault, not the integral's: Gentoo mass mixes lighter females and heavier males, so its real shape has two bumps, not one bell." if abs(((f > a) & (f < b)).mean() - quad) > 0.05 else ""}"),
        ("Expected value is an integral too", f"E[X] = ∫ x · pdf(x) dx = **{ex:.1f}** g, equal to the mean, as it should be. Integrals appear in ML as expectations: expected loss, the KL term in VAEs, and areas under ROC curves."),
    ], "Integration adds up a quantity over a range; in ML it gives probabilities, expectations and areas like AUC."


@walk("m-optim-math", "housing")
def _():
    h = D("housing").dropna()
    from sklearn.preprocessing import StandardScaler
    X = StandardScaler().fit_transform(h[["median_income", "housing_median_age", "total_rooms"]]); X = np.c_[np.ones(len(X)), X]; y = h["median_house_value"].values / 1e5
    L = lambda w: np.mean((X @ w - y) ** 2); G = lambda w: 2 * X.T @ (X @ w - y) / len(y)
    H = 2 * X.T @ X / len(y); eig = np.linalg.eigvalsh(H)
    rows = []
    for lr in [0.05, 0.5, 2 / eig.max() * 0.99, 2 / eig.max() * 1.05]:
        w = np.zeros(4)
        for _ in range(50): w = w - lr * G(w)
        rows.append({"learning rate": lr, "loss after 50 steps": L(w) if np.isfinite(L(w)) else float("inf")})
    w = np.zeros(4); rng = np.random.default_rng(0)
    for _ in range(200):
        i = rng.choice(len(y), 32); w = w - 0.05 * 2 * X[i].T @ (X[i] @ w - y[i]) / 32
    w_n = np.linalg.solve(H, -G(np.zeros(4))) + 0
    return [
        ("The shape of the loss: the Hessian", f"For linear regression on 3 standardised housing features, the Hessian (matrix of second derivatives) is constant: H = 2XᵀX/n. Its eigenvalues {np.round(eig, 3).tolist()} are all positive, so the loss is a convex bowl with one minimum. Largest/smallest = {eig.max() / eig.min():.1f}, the condition number: 1 means a round bowl, large values mean a long narrow valley where gradient descent zig-zags. Standardising the features is what keeps it small here."),
        ("Learning rate vs curvature", f"Gradient descent is stable only if learning rate < 2 / largest eigenvalue = {2 / eig.max():.3f}:\n\n{t(pd.DataFrame(rows), nd=3)}\n\nJust above the limit, the loss explodes instead of shrinking."),
        ("Other optimisers", f"Newton's method uses the Hessian and jumps to the minimum in one step here: loss {L(w_n):.4f}. Mini-batch SGD (32 districts per step, 200 steps) reaches {L(w):.4f} while looking at a fraction of the data each step. Deep nets aren't convex, but the same ideas (step size vs curvature, noise from mini-batches) explain how Adam and friends behave."),
    ], "Optimisation theory links the loss surface's curvature to how fast and how safely gradient methods converge."
