"""Real-data walkthroughs: Computer vision and speech."""
import os
import numpy as np, pandas as pd
from walk_util import walk, D, t, pct, fmt, DATA
from walks.w_dl import _torch, _digits, _img, _fit_mlp, _acc


CACHE = os.path.join(DATA, "cache")
EFF_URL = "https://github.com/lukemelas/EfficientNet-PyTorch/releases/download/1.0/efficientnet-b0-355c32eb.pth"
CLS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"


def _effnet():
    """EfficientNet-B0 with real ImageNet weights (downloaded once into data/cache, not committed)."""
    import urllib.request, torch
    from efficientnet_pytorch import EfficientNet
    os.makedirs(CACHE, exist_ok=True)
    for url in (EFF_URL, CLS_URL):
        f = os.path.join(CACHE, os.path.basename(url).replace("efficientnet-b0-355c32eb.pth", "eb0.pth"))
        if not os.path.exists(f): urllib.request.urlretrieve(url, f)
    m = EfficientNet.from_name("efficientnet-b0"); m.load_state_dict(torch.load(os.path.join(CACHE, "eb0.pth"))); m.eval()
    return m, open(os.path.join(CACHE, "imagenet_classes.txt")).read().splitlines()


def _prep(img):
    import torch
    from skimage.transform import resize
    img = resize(img, (224, 224), anti_aliasing=True)
    if img.ndim == 2: img = np.stack([img] * 3, -1)
    mean, std = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])
    return torch.tensor(((img - mean) / std).transpose(2, 0, 1), dtype=torch.float32)


def _coin_mask():
    from scipy import ndimage
    co = D("coins").astype(float); th = _otsu(co)
    return co, th, ndimage.binary_opening(ndimage.binary_fill_holes(co > th), iterations=2)


def _gray(img):
    return (0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2])


def _faces(img, raw=False):
    import cv2
    cc = cv2.CascadeClassifier(os.path.join(DATA, "haarcascade_frontalface_default.xml"))
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return cc.detectMultiScale(g, 1.1, 0 if raw else 5, minSize=(60, 60))


def _otsu(g):
    from skimage.filters import threshold_otsu
    return threshold_otsu(g)


def _small(a, nd=0):
    return t(pd.DataFrame(np.asarray(a)).round(nd) + 0)


def _iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ix = max(0, min(ax + aw, bx + bw) - max(ax, bx)); iy = max(0, min(ay + ah, by + bh) - max(ay, by))
    inter = ix * iy
    return inter / (aw * ah + bw * bh - inter)


@walk("m-cv-overview", ("digits", "photos"))
def _():
    import torch
    from scipy import ndimage
    net, cls = _effnet()
    rows = []
    for name in ["coffee", "chelsea", "camera", "astronaut"]:
        with torch.no_grad(): pr = torch.softmax(net(_prep(D(name))[None]), 1)[0]
        v, i = pr.topk(2)
        rows.append({"photo": name, "top guess": cls[i[0]], "probability": v[0].item(), "2nd guess": cls[i[1]], "prob.": v[1].item()})
    ast = D("astronaut"); faces = _faces(ast)
    co, th, m = _coin_mask()
    lab, n = ndimage.label(m); sizes = np.bincount(lab.ravel())[1:]
    return [
        ("Classification: one label per image", f"EfficientNet-B0, a real network trained on 1.2 million ImageNet photos (1,000 classes), on four real photos:\n\n{t(pd.DataFrame(rows), nd=3)}\n\nThe coffee photo is called espresso and the camera-man photo tripod. The astronaut isn't one of ImageNet's 1,000 classes, so its guess is wrong: a classifier can only choose among the labels it was trained on."),
        ("Detection: where are the objects?", f"A face detector on the {ast.shape[1]} × {ast.shape[0]} astronaut photo returns {len(faces)} box(es) (x, y, width, height): {', '.join(str(tuple(int(v) for v in f)) for f in faces)}."),
        ("Segmentation: a label for every pixel", f"Threshold the {co.shape[1]} × {co.shape[0]} photo of coins into coin vs background, then group touching pixels: **{n}** separate regions, {int((sizes > 500).sum())} of them bigger than 500 pixels; {pct(m.mean())} of the pixels are coin."),
    ], "Vision tasks differ in what they output: one label (classification), boxes (detection) or a label per pixel (segmentation)."


@walk("m-image-basics", "photos")
def _():
    img = D("astronaut")
    r, c = 120, 230
    patch = img[r:r + 3, c:c + 3]
    px = pd.DataFrame([{"pixel (row, col)": f"({r + i}, {c + j})", "R": patch[i, j, 0], "G": patch[i, j, 1], "B": patch[i, j, 2], "gray = 0.299R + 0.587G + 0.114B": 0.299 * patch[i, j, 0] + 0.587 * patch[i, j, 1] + 0.114 * patch[i, j, 2]} for i in range(2) for j in range(3)])
    g = _gray(img.astype(float))
    hist = pd.DataFrame({"brightness range": [f"{a}–{a + 31}" for a in range(0, 256, 32)], "share of pixels": [pct(((g >= a) & (g < a + 32)).mean()) for a in range(0, 256, 32)]})
    from skimage.transform import resize
    small = resize(g, (8, 8), anti_aliasing=True)
    return [
        ("An image is a grid of numbers", f"The astronaut photo is an array of shape **{img.shape}** = {img.shape[0]} rows × {img.shape[1]} columns × 3 colour channels (red, green, blue), each 0–255 ({img.size:,} numbers in total). Six pixels:\n\n{t(px, nd=1)}"),
        ("Brightness histogram (grayscale)", f"{t(hist)}"),
        ("Resize to 8 × 8", f"Averaging blocks of pixels shrinks it to 64 numbers (like the digit images):\n\n{_small(small)}\n\nThe bright and dark areas of the photo are still visible as big and small numbers, but all detail is gone."),
    ], "Every image is just an array of brightness numbers per channel; vision models start from exactly these arrays."


@walk("m-image-features", "photos")
def _():
    from scipy import ndimage
    from skimage.feature import hog, corner_harris, corner_peaks
    from sklearn.svm import LinearSVC
    from sklearn.model_selection import cross_val_score
    cam = D("camera").astype(float)
    gx = ndimage.sobel(cam, 1); gy = ndimage.sobel(cam, 0); mag = np.hypot(gx, gy)
    r, c = np.unravel_index(mag.argmax(), mag.shape)
    corners = corner_peaks(corner_harris(cam), min_distance=10)
    faces = D("lfw_subset"); y = np.r_[np.ones(100), np.zeros(100)]
    H = np.array([hog(f, orientations=9, pixels_per_cell=(5, 5), cells_per_block=(2, 2)) for f in faces])
    raw = cross_val_score(LinearSVC(max_iter=5000), faces.reshape(200, -1), y, cv=5).mean()
    hg = cross_val_score(LinearSVC(max_iter=5000), H, y, cv=5).mean()
    return [
        ("Edges with the Sobel filter", f"Sobel measures how fast brightness changes left↔right and up↔down. In the {cam.shape[0]} × {cam.shape[1]} camera-man photo the strongest edge is at row {r}, column {c}. Pixel neighbourhood there:\n\n{_small(cam[r - 2:r + 3, c - 2:c + 3])}\n\n{pct((mag > mag.mean() + 2 * mag.std()).mean(), 1)} of pixels are strong edges."),
        ("Corners", f"Harris corner detection finds **{len(corners)}** corners (points where edges in two directions meet). First few (row, col): {', '.join(str(tuple(int(v) for v in k)) for k in corners[:5])}."),
        ("HOG features: face or not?", f"200 real 25 × 25 crops: 100 faces, 100 non-faces. HOG turns each into {H.shape[1]} numbers (histograms of edge directions in small cells). A linear classifier, 5-fold accuracy: raw pixels **{pct(raw, 1)}**, HOG **{pct(hg, 1)}**."),
    ], "Hand-made features (edges, corners, HOG) describe shape in a way that is easier to learn from than raw pixels; CNNs learn similar features automatically."


@walk("m-cnn-architectures", ("digits", "photos"))
def _():
    torch = _torch(); nn = torch.nn
    import torchvision.models as tvm
    from skimage.transform import resize
    nets = {"AlexNet": tvm.alexnet(), "VGG-16": tvm.vgg16(), "ResNet-18": tvm.resnet18(), "ResNet-50": tvm.resnet50(), "MobileNet-V3 small": tvm.mobilenet_v3_small(), "EfficientNet-B0": tvm.efficientnet_b0()}
    pc = pd.DataFrame([{"architecture": k, "weights (millions)": sum(p.numel() for p in v.parameters()) / 1e6} for k, v in nets.items()])
    img = resize(D("astronaut"), (224, 224), anti_aliasing=True).astype(np.float32)
    x = torch.tensor(img).permute(2, 0, 1)[None]
    r = nets["ResNet-18"].eval(); shapes = []
    with torch.no_grad():
        a = r.maxpool(r.relu(r.bn1(r.conv1(x)))); shapes.append(("stem (conv 7×7 + pool)", tuple(a.shape[1:])))
        for i in range(1, 5):
            a = getattr(r, f"layer{i}")(a); shapes.append((f"stage {i} (residual blocks)", tuple(a.shape[1:])))
        a = torch.flatten(r.avgpool(a), 1); shapes.append(("global average pool", tuple(a.shape[1:])))
    sh = pd.DataFrame([{"after": k, "channels × height × width": " × ".join(map(str, v))} for k, v in [("input photo", (3, 224, 224))] + shapes])
    Xtr, Xte, ytr, yte = _digits()

    class Res(nn.Module):
        def __init__(s, n, skip):
            super().__init__(); s.l = nn.ModuleList(nn.Linear(64, 64) for _ in range(n)); s.skip = skip; s.inp = nn.Linear(64, 64); s.out = nn.Linear(64, 10)
        def forward(s, x):
            h = torch.relu(s.inp(x))
            for l in s.l: h = (h + torch.relu(l(h))) if s.skip else torch.relu(l(h))
            return s.out(h)
    rows = []
    for skip in [False, True]:
        torch.manual_seed(0); net = Res(20, skip); o = torch.optim.SGD(net.parameters(), lr=0.05)
        X = torch.tensor(Xtr, dtype=torch.float32); Y = torch.tensor(ytr)
        for _ in range(10):
            for idx in torch.randperm(len(X)).split(64):
                o.zero_grad(); nn.functional.cross_entropy(net(X[idx]), Y[idx]).backward(); o.step()
        net.eval(); rows.append({"22-layer net on digits": "with skip connections (ResNet idea)" if skip else "plain stack", "test accuracy after 10 epochs": _acc(torch, net, Xte, yte)})
    return [
        ("The famous architectures, by size", f"{t(pc, nd=1)}\n\nNewer designs (MobileNet, EfficientNet) get similar or better accuracy with far fewer weights."),
        ("A real photo flowing through ResNet-18", f"{t(sh)}\n\nEach stage halves the height and width and adds channels: fewer positions, more kinds of pattern. The last 512 numbers feed the classifier."),
        ("Why ResNet's skip connections matter", f"{t(pd.DataFrame(rows), nd=3)}\n\nAdding each block's input back to its output (h + f(h)) lets gradients flow straight through very deep stacks."),
    ], "CNN architectures are recipes for stacking convolutions; the big ideas are depth (VGG), skip connections (ResNet) and efficiency (MobileNet, EfficientNet)."


@walk("m-transfer-learning", "photos")
def _():
    import torch
    from sklearn.linear_model import LogisticRegression
    net, cls = _effnet()
    F = D("lfw_subset"); y = np.r_[np.ones(100), np.zeros(100)]
    with torch.no_grad():
        E = torch.cat([net.extract_features(torch.stack([_prep(f) for f in F[i:i + 50]])).mean((2, 3)) for i in range(0, 200, 50)]).numpy()
    rng = np.random.default_rng(0); rows = []
    for n in [2, 5, 10, 25]:
        r = {"pix": [], "eff": []}
        for _ in range(30):
            tr = np.r_[rng.choice(100, n, replace=False), 100 + rng.choice(100, n, replace=False)]; te = np.setdiff1d(np.arange(200), tr)
            for k, X in [("pix", F.reshape(200, -1)), ("eff", E)]:
                r[k].append(LogisticRegression(max_iter=3000).fit(X[tr], y[tr]).score(X[te], y[te]))
        rows.append({"labelled examples per class": n, "raw pixels": np.mean(r["pix"]), "pre-trained EfficientNet features": np.mean(r["eff"])})
    return [
        ("Step 1: a network pre-trained on a big dataset", f"EfficientNet-B0 was trained on 1.2 million ImageNet photos. Its last layer before the classifier gives **{E.shape[1]:,}** numbers per image describing what it sees (shapes, textures, parts). It was never trained on our task."),
        ("Step 2: a new task with very few labels", f"Task: tell real 25 × 25 face crops from non-face crops (200 images from Labeled Faces in the Wild). Train a simple logistic regression either on the 625 raw pixels or on the 1,280 pre-trained features, using only a few labelled examples."),
        ("Results on the remaining images (avg of 30 random picks)", f"{t(pd.DataFrame(rows), nd=3)}\n\nWith just {rows[0]['labelled examples per class']} examples per class the borrowed features already reach {pct(rows[0]['pre-trained EfficientNet features'])}. Next step if you have more data: fine-tune the whole network with a small learning rate."),
    ], "Transfer learning reuses features learned on a huge dataset, so a new task needs far fewer labels."


@walk("m-augmentation", "digits")
def _():
    torch = _torch(); nn = torch.nn
    from scipy import ndimage
    Xtr, Xte, ytr, yte = _digits()
    rng = np.random.default_rng(0)

    def aug(x):
        im = x.reshape(8, 8)
        im = ndimage.rotate(im, rng.uniform(-15, 15), reshape=False, order=1)
        im = ndimage.shift(im, rng.integers(-1, 2, 2), order=0)
        return np.clip(im, 0, 1).ravel()
    sub = slice(0, 200)
    Xa = np.concatenate([Xtr[sub]] + [np.array([aug(x) for x in Xtr[sub]]) for _ in range(9)]); ya = np.tile(ytr[sub], 10)
    Xshift = np.array([ndimage.shift(x.reshape(8, 8), (0, 1), order=0).ravel() for x in Xte])
    cnn = lambda: [nn.Unflatten(1, (1, 8, 8)), nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(128, 10)]
    rows = []
    for name, X, y, ep in [("200 originals", Xtr[sub], ytr[sub], 100), ("200 originals + 1,800 augmented copies", Xa, ya, 10)]:
        net = _fit_mlp(torch, cnn(), X, y, epochs=ep)
        rows.append({"training set": name, "test accuracy": _acc(torch, net, Xte, yte), "test digits shifted 1 pixel right": _acc(torch, net, Xshift, yte)})
    return [
        ("One real digit and a random variation", f"Original (label {ytr[0]}):\n\n{_img(Xtr[0] * 16)}\n\nRotated up to ±15° and shifted up to 1 pixel:\n\n{_img(aug(Xtr[0]) * 16)}"),
        ("Why", "A slightly rotated 0 is still a 0. Making such copies teaches the network that the label doesn't change under these transformations, without collecting new data."),
        ("Train a CNN on only 200 digits", f"{t(pd.DataFrame(rows), nd=3)}\n\n{'Augmentation barely changes accuracy on ordinary test digits here' if abs(rows[1]['test accuracy'] - rows[0]['test accuracy']) < 0.03 else 'On ordinary test digits the two are different'}, but on shifted digits it is the difference between {pct(rows[0]['test digits shifted 1 pixel right'])} and {pct(rows[1]['test digits shifted 1 pixel right'])}: the network learned that position doesn't change the digit."),
    ], "Augmentation creates label-preserving variations of real examples, which helps most when data is scarce or test images vary."


@walk("m-object-detection", "photos")
def _():
    img = D("astronaut")
    raw = _faces(img, raw=True); final = _faces(img)
    best = final[0] if len(final) else raw[0]
    ious = sorted([_iou(best, r) for r in raw], reverse=True)
    keep = []
    for b in sorted(raw, key=lambda b: -b[2] * b[3]):
        if all(_iou(b, k) < 0.3 for k in keep): keep.append(b)
    tab = pd.DataFrame([{"box": i + 1, "x": int(b[0]), "y": int(b[1]), "width": int(b[2]), "height": int(b[3]), "IoU with final box": _iou(best, b)} for i, b in enumerate(raw[:6])])
    return [
        ("Many candidate boxes", f"A face detector slides windows of many sizes over the photo. Before cleaning up it returns **{len(raw)}** candidate boxes, mostly heaps around the same face. First six:\n\n{t(tab, nd=2)}"),
        ("IoU: how much two boxes overlap", f"IoU = area of overlap ÷ area of union (1 = identical, 0 = disjoint). Against the final face box, {sum(i > 0.5 for i in ious)} of the {len(raw)} candidates have IoU > 0.5."),
        ("Non-maximum suppression", f"Keep a box, drop all boxes overlapping it by IoU ≥ 0.3, repeat: **{len(raw)} → {len(keep)}** boxes, {sum(_iou(best, k) > 0.3 for k in keep)} on the face and {sum(_iou(best, k) <= 0.3 for k in keep)} lone false alarms elsewhere. A confidence threshold removes those (OpenCV requires several overlapping hits). OpenCV's own grouping gives the final answer: {', '.join(str(tuple(int(v) for v in f)) for f in final)}. Detection models like YOLO do the same clean-up on their predictions."),
    ], "Detectors propose many scored boxes; IoU measures overlap and non-maximum suppression keeps one box per object."


@walk("m-segmentation", "photos")
def _():
    from scipy import ndimage
    from skimage.segmentation import watershed
    from skimage.feature import peak_local_max
    co, th, m = _coin_mask()
    lab, n = ndimage.label(m); sizes = np.bincount(lab.ravel())[1:]
    dist = ndimage.distance_transform_edt(m)
    pk = peak_local_max(dist, min_distance=12, labels=lab)
    mk = np.zeros_like(lab); mk[tuple(pk.T)] = np.arange(1, len(pk) + 1)
    ws = watershed(-dist, mk, mask=m); ws_sizes = np.bincount(ws.ravel())[1:]
    cy, cx = map(int, ndimage.center_of_mass(lab == 1 + int(np.argsort(-sizes)[1])))
    r = cy; cols = [c for c in range(cx - 40, cx + 41, 10) if 0 <= c < co.shape[1]]
    row = pd.DataFrame({"column": cols, "brightness": co[r, cols].astype(int), "label": np.where(co[r, cols] > th, "coin", "background")})
    return [
        ("Pick a threshold", f"Otsu's method picks the brightness that best splits the {co.shape[1]} × {co.shape[0]} coins photo into two groups: **{th:.0f}**. Along row {r}:\n\n{t(row)}"),
        ("Clean up and count regions", f"Fill holes, remove specks, then label connected regions: **{n}** regions, sizes {', '.join(map(str, sorted(sizes, reverse=True)[:6]))}, … pixels. Touching coins merge into one region."),
        ("Watershed splits touching objects", f"Distance-to-background peaks mark coin centres ({len(pk)} found); 'flooding' from them splits the mask into **{len(ws_sizes)}** pieces (the photo shows 24 coins, so a few textured coins get split in two: watershed needs tuning). Deep models (U-Net, Mask R-CNN) learn this per-pixel labelling directly."),
    ], "Segmentation labels every pixel; counting and separating objects then works on those labels."


@walk("m-video", "photos")
def _():
    import cv2
    g = cv2.cvtColor(D("astronaut"), cv2.COLOR_RGB2GRAY)
    shifts = [(0, 0), (3, 0), (6, 2), (9, 4), (12, 6)]
    frames = [g[100 + dy:356 + dy, 100 + dx:356 + dx] for dx, dy in shifts]
    rows = []
    for i in range(1, len(frames)):
        diff = np.abs(frames[i].astype(int) - frames[i - 1].astype(int))
        flow = cv2.calcOpticalFlowFarneback(frames[i - 1], frames[i], None, 0.5, 3, 15, 3, 5, 1.2, 0)
        tdx, tdy = shifts[i][0] - shifts[i - 1][0], shifts[i][1] - shifts[i - 1][1]
        rows.append({"frames": f"{i} → {i + 1}", "true camera move (x, y)": f"({tdx}, {tdy})", "pixels that changed > 20": pct((diff > 20).mean()), "optical flow, median (x, y)": f"({-np.median(flow[..., 0]):.1f}, {-np.median(flow[..., 1]):.1f})"})
    still = np.abs(frames[0].astype(int) - frames[0].astype(int)).mean()
    return [
        ("A video is a stack of images", f"We make a 5-frame clip by moving a 256 × 256 window across the real astronaut photo (a camera panning). The clip is an array of shape (5, 256, 256): frames × height × width."),
        ("Frame differencing", f"Subtracting consecutive frames shows where something changed (a still scene gives {still:.0f} everywhere). Simple motion detectors and CCTV alarms work this way."),
        ("Optical flow recovers the motion", f"{t(pd.DataFrame(rows))}\n\nFarneback optical flow estimates how far each pixel moved; its median matches the camera move we made. Video models add this time dimension (3-D convolutions, or a CNN per frame plus an RNN/transformer)."),
    ], "Video = images over time; frame differences and optical flow measure motion, which video models learn to use."


@walk("m-face-emotion", "photos")
def _():
    from skimage.feature import hog
    from sklearn.svm import LinearSVC
    from sklearn.model_selection import cross_val_predict
    img = D("astronaut"); f = _faces(img)[0]; x, y, w, h = map(int, f)
    import cv2
    crop = cv2.resize(cv2.cvtColor(img[y:y + h, x:x + w], cv2.COLOR_RGB2GRAY), (48, 48))
    faces = D("lfw_subset"); lab = np.r_[np.ones(100), np.zeros(100)]
    H = np.array([hog(q, pixels_per_cell=(5, 5), cells_per_block=(2, 2)) for q in faces])
    pr = cross_val_predict(LinearSVC(max_iter=5000), H, lab, cv=5)
    return [
        ("Step 1: find the face", f"A face detector on the astronaut photo returns the box x={x}, y={y}, width={w}, height={h}."),
        ("Step 2: crop, grey, resize to 48 × 48", f"Emotion datasets such as FER-2013 use 48 × 48 grey faces. The crop's average brightness is {crop.mean():.0f}; a few pixels from the centre:\n\n{_small(crop[20:25, 20:25])}"),
        ("Step 3: classify", f"A CNN trained on labelled faces outputs one probability per emotion (angry, happy, sad, …). We have no emotion labels offline, so here the same HOG + classifier pipeline answers a simpler question, 'face or not?', on 200 real crops: {pct((pr == lab).mean(), 1)} correct. Emotion models are often only 65–75% accurate even on clean data, and they can be biased across groups of people: use with care."),
    ], "Face-emotion systems are a pipeline: detect, align and crop the face, then classify the expression; each step can fail."


@walk("m-siamese", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    torch.manual_seed(0)
    emb = nn.Sequential(nn.Unflatten(1, (1, 8, 8)), nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(128, 32))
    X = torch.tensor(Xtr, dtype=torch.float32); o = torch.optim.Adam(emb.parameters(), lr=1e-3)
    tr = ytr < 7; Xa, ya = X[tr], ytr[tr]; Ya = torch.tensor(ya); rng = np.random.default_rng(0)
    by = {d: np.where(ya == d)[0] for d in range(7)}
    for _ in range(3000):
        i = torch.randint(0, len(Xa), (128,)); j = torch.randint(0, len(Xa), (128,))
        j[:64] = torch.tensor([rng.choice(by[int(ya[k])]) for k in i[:64]])
        same = (Ya[i] == Ya[j]).float(); d = (emb(Xa[i]) - emb(Xa[j])).norm(dim=1)
        loss = (same * d ** 2 + (1 - same) * torch.clamp(2.0 - d, min=0) ** 2).mean()
        o.zero_grad(); loss.backward(); o.step()
    with torch.no_grad():
        E = emb(torch.tensor(Xte, dtype=torch.float32)).numpy()
    rows = []
    for name, idx in [("digits 0–6 (seen in training)", np.where(yte < 7)[0]), ("digits 7–9 (never seen)", np.where(yte >= 7)[0])]:
        Dm = np.linalg.norm(E[idx][:, None] - E[idx][None], axis=2); S = yte[idx][:, None] == yte[idx][None]; off = ~np.eye(len(idx), dtype=bool)
        rows.append({"test pairs": name, "avg distance, same digit": Dm[S & off].mean(), "avg distance, different digits": Dm[~S].mean()})
    new = np.where(yte >= 7)[0]; accs = []
    for r in range(20):
        sup = {d: rng.choice(new[yte[new] == d]) for d in [7, 8, 9]}
        q = [k for k in new if k not in sup.values()]
        pred = np.array([min(sup, key=lambda d: np.linalg.norm(E[k] - E[sup[d]])) for k in q]); accs.append((pred == yte[q]).mean())
    return [
        ("Learn a distance, not classes", "Two copies of the same small CNN turn two images into 32-number embeddings. Training (contrastive loss) pulls same-digit pairs together and pushes different-digit pairs at least 2 apart. Trained only on digits **0–6**."),
        ("Distances on test digits", f"{t(pd.DataFrame(rows), nd=2)}\n\nOn digits it never saw, same-digit pairs are still closer than different-digit pairs, but less clearly than on the trained digits."),
        ("One-shot recognition", f"Give it **one** example each of 7, 8 and 9, then label all the other 7/8/9 test digits by the nearest example: **{pct(np.mean(accs), 1)}** correct on average over 20 random choices of examples (chance 33%). Face unlock uses the same idea with networks trained on millions of faces, which is what makes it reliable."),
    ], "Siamese networks learn a similarity measure, so they can recognise new classes from a single example; how well depends on how much and how varied the training data was."


@walk("m-gan", "digits")
def _():
    torch = _torch(); nn = torch.nn
    Xtr, Xte, ytr, yte = _digits()
    X = torch.tensor(Xtr * 2 - 1, dtype=torch.float32)
    torch.manual_seed(0)
    G = nn.Sequential(nn.Linear(16, 128), nn.ReLU(), nn.Linear(128, 64), nn.Tanh())
    Dn = nn.Sequential(nn.Linear(64, 128), nn.LeakyReLU(0.2), nn.Linear(128, 1))
    og = torch.optim.Adam(G.parameters(), 2e-3, betas=(0.5, 0.999)); od = torch.optim.Adam(Dn.parameters(), 2e-3, betas=(0.5, 0.999))
    bce = nn.functional.binary_cross_entropy_with_logits; log = []
    for step in range(1, 3001):
        real = X[torch.randint(0, len(X), (64,))]; fake = G(torch.randn(64, 16))
        ld = bce(Dn(real), torch.ones(64, 1)) + bce(Dn(fake.detach()), torch.zeros(64, 1)); od.zero_grad(); ld.backward(); od.step()
        lg = bce(Dn(fake), torch.ones(64, 1)); og.zero_grad(); lg.backward(); og.step()
        if step in (1, 500, 1500, 3000):
            with torch.no_grad():
                log.append({"step": step, "discriminator loss": ld.item(), "generator loss": lg.item(), "D's P(real) on fakes": torch.sigmoid(Dn(fake)).mean().item()})
    from sklearn.svm import SVC
    clf = SVC(probability=True).fit(Xtr, ytr)
    with torch.no_grad(): fakes = ((G(torch.randn(200, 16)) + 1) / 2).numpy()
    pf = clf.predict_proba(fakes); conf = pf.max(1)
    near = np.min(((Xtr[None] - fakes[:1, None]) ** 2).sum(2))
    return [
        ("Two networks play a game", "The generator turns 16 random numbers into a fake 8 × 8 digit. The discriminator sees real digits and fakes and says real or fake. Each trains to beat the other."),
        ("Training on 1,257 real digits", f"{t(pd.DataFrame(log), nd=3)}\n\nNeither loss goes to zero: when it's working, the two stay in balance."),
        ("A generated digit", f"{_img(fakes[0] * 16)}\n\nA digit classifier trained on real data reads it as a **{pf[0].argmax()}** ({pct(conf[0])} sure). Over 200 fakes it is on average {pct(conf.mean())} sure, and they cover {len(set(pf.argmax(1)))} of the 10 digits. The fake is not a copy: the nearest real training digit is {near:.1f} away (squared pixel distance)."),
    ], "A GAN learns to generate realistic samples by training a generator against a discriminator that tries to spot fakes."


@walk("m-super-resolution", "photos")
def _():
    torch = _torch(); nn = torch.nn
    from skimage.transform import resize
    from skimage.metrics import peak_signal_noise_ratio as psnr
    from skimage.color import rgb2gray
    cam = D("camera").astype(np.float32) / 255
    low = resize(cam, (128, 128), anti_aliasing=True)
    up = {name: resize(low, cam.shape, order=o) for name, o in [("nearest neighbour", 0), ("bilinear", 1), ("bicubic", 3)]}
    train = [rgb2gray(D(n)).astype(np.float32) for n in ["astronaut", "coffee", "chelsea"]]
    Xs, Ys = [], []
    for im in train:
        im = resize(im, (512, int(512 * im.shape[1] / im.shape[0])), anti_aliasing=True)[:, :512]
        lo = resize(resize(im, (128, 128), anti_aliasing=True), im.shape, order=3); Xs.append(lo); Ys.append(im)
    X = torch.tensor(np.array(Xs))[:, None]; Y = torch.tensor(np.array(Ys))[:, None]
    torch.manual_seed(0)
    net = nn.Sequential(nn.Conv2d(1, 32, 9, padding=4), nn.ReLU(), nn.Conv2d(32, 16, 5, padding=2), nn.ReLU(), nn.Conv2d(16, 1, 5, padding=2))
    o = torch.optim.Adam(net.parameters(), 1e-3)
    for _ in range(300):
        i = np.random.randint(0, 512 - 64, 2)
        xb = X[:, :, i[0]:i[0] + 64, i[1]:i[1] + 64]; yb = Y[:, :, i[0]:i[0] + 64, i[1]:i[1] + 64]
        o.zero_grad(); ((xb + net(xb) - yb) ** 2).mean().backward(); o.step()
    with torch.no_grad():
        sr = (torch.tensor(up["bicubic"])[None, None] + net(torch.tensor(up["bicubic"], dtype=torch.float32)[None, None]))[0, 0].numpy()
    rows = [{"method": k, "PSNR (dB, higher = closer to original)": psnr(cam, np.clip(v, 0, 1), data_range=1)} for k, v in up.items()]
    rows.append({"method": "bicubic + small CNN (SRCNN-style, trained on 3 other photos)", "PSNR (dB, higher = closer to original)": psnr(cam, np.clip(sr, 0, 1), data_range=1)})
    return [
        ("Make a low-resolution copy", f"Shrink the real 512 × 512 camera-man photo to 128 × 128 (16× fewer pixels). The task: get back the 512 × 512 image."),
        ("Classic upscaling", "Nearest neighbour copies each pixel into a 4 × 4 block (blocky). Bilinear and bicubic blend neighbouring pixels (smooth but blurry)."),
        ("Compare with the original", f"{t(pd.DataFrame(rows), nd=2)}\n\nA network trained on *other* photos learns to add back sharp detail that blurring removes. Modern models (ESRGAN, diffusion upscalers) go much further."),
    ], "Super-resolution learns the missing high-frequency detail from examples of low/high-resolution pairs."


@walk("m-speech-features", "speech")
def _():
    import librosa
    x, sr = D("speech")
    x = x if x.ndim == 1 else x.mean(1)
    fl, hop = int(0.025 * sr), int(0.010 * sr)
    E = librosa.feature.rms(y=x, frame_length=fl, hop_length=hop)[0]
    loud, quiet = int(E.argmax()), int(E.argmin())
    spec = np.abs(np.fft.rfft(x[loud * hop:loud * hop + fl] * np.hanning(fl)))
    freqs = np.fft.rfftfreq(fl, 1 / sr)
    top = pd.DataFrame({"frequency (Hz)": freqs[np.argsort(-spec)[:4]].round(0), "strength": np.sort(spec)[::-1][:4]})
    mel = librosa.feature.melspectrogram(y=x, sr=sr, n_fft=512, win_length=fl, hop_length=hop, n_mels=40)
    mf = librosa.feature.mfcc(S=librosa.power_to_db(mel), n_mfcc=13)
    mft = pd.DataFrame(mf[:5, [loud, quiet]].T, columns=[f"MFCC {i + 1}" for i in range(5)], index=["loudest frame", "quietest frame"])
    return [
        ("Raw audio", f"{len(x) / sr:.1f} s of real speech at {sr:,} samples per second = **{len(x):,}** numbers between −1 and 1. Cut into 25 ms frames every 10 ms → {len(E)} frames. Loudness (RMS) ranges from {E.min():.4f} (pause) to {E.max():.3f} (frame {loud}, at {loud * hop / sr:.2f} s)."),
        ("Spectrum of the loudest frame", f"A Fourier transform shows which frequencies are present:\n\n{t(top, nd=2)}\n\nVoiced speech has energy at the voice's pitch and its harmonics, mostly below 1,000 Hz."),
        ("Mel spectrogram → MFCCs", f"40 mel bands (spaced like human hearing) per frame give a {mel.shape[0]} × {mel.shape[1]} image of the sound. Taking the log and a cosine transform gives 13 MFCCs per frame:\n\n{t(mft, nd=1, index=True)}\n\nMFCC 1 tracks overall loudness; the others describe the shape of the spectrum, i.e. which sound is being made."),
    ], "Speech is turned into features by framing the waveform, taking spectra, warping them to the mel scale and compressing to MFCCs."


@walk("m-speech-recognition", "spoken")
def _():
    import librosa
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.metrics import confusion_matrix
    S = D("spoken"); sr = S["sr"]

    def feat(c):
        m = librosa.feature.mfcc(y=c, sr=sr, n_mfcc=13, n_fft=256, hop_length=80, n_mels=40)
        parts = np.array_split(m, 4, axis=1)
        return np.concatenate([p.mean(1) for p in parts] + [m.std(1)])
    F = np.array([feat(c) for c in S["clips"]]); y = S["label"]; spk = S["speaker"]
    ex = pd.DataFrame([{"clip": f"'{y[i]}' by {spk[i]}", "length (s)": len(S["clips"][i]) / sr, "MFCC frames": 1 + len(S["clips"][i]) // 80} for i in [0, 10, 300]])
    rows = []; cms = None
    for held in sorted(set(spk)):
        tr, te = spk != held, spk == held
        m = make_pipeline(StandardScaler(), SVC(C=10)).fit(F[tr], y[tr]); p = m.predict(F[te])
        rows.append({"test speaker (never heard in training)": held, "digits recognised": (p == y[te]).mean()})
        cm = confusion_matrix(y[te], p, labels=range(10)); cms = cm if cms is None else cms + cm
    r = pd.DataFrame(rows)
    off = cms - np.diag(np.diag(cms)); a, b = np.unravel_index(off.argmax(), off.shape)
    return [
        ("Real recordings", f"{len(y)} clips of 6 people saying 0–9:\n\n{t(ex, nd=2)}"),
        ("Audio → MFCC features → classifier", f"Each clip becomes 13 MFCCs per 10 ms frame; we summarise them as averages over 4 time segments + overall spread (65 numbers), then train a support-vector classifier."),
        ("Test on a voice it has never heard", f"{t(r, nd=3)}\n\nAverage **{pct(r['digits recognised'].mean(), 1)}**. Most common confusion: '{a}' heard as '{b}' ({off[a, b]} times). Full speech recognisers (e.g. Whisper) replace this with a network that turns MFCC/mel frames into characters or words, trained on thousands of hours."),
    ], "Speech recognition maps audio features to words; generalising to new voices is the hard part."
