"""Deep layer + end-to-end walkthroughs: Computer vision & speech."""
from deep.util import X

BUS = "https://raw.githubusercontent.com/ultralytics/assets/main/im/bus.jpg"
VIDEO = "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/vtest.avi"
HAAR = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
JFK = "https://raw.githubusercontent.com/openai/whisper/main/tests/jfk.flac"
FM = '''import gzip, urllib.request
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
get = lambda f, off: np.frombuffer(gzip.decompress(urllib.request.urlopen(base + f).read()), np.uint8, offset=off)
X = get("t10k-images-idx3-ubyte.gz", 16).reshape(-1, 1, 28, 28).astype(np.float32) / 255.0; y = get("t10k-labels-idx1-ubyte.gz", 8).astype(np.int64)
NAMES = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Boot"]
torch.manual_seed(0); Xt, yt = torch.tensor(X), torch.tensor(y); tr, te = torch.arange(8000), torch.arange(8000, 10000)'''
TRAIN = '''def fit(model, opt, epochs, Xa, ya, bs=128, tf=None):
    for _ in range(epochs):
        model.train()
        for idx in torch.randperm(len(Xa)).split(bs):
            xb = tf(Xa[idx]) if tf else Xa[idx]; opt.zero_grad(); torch.nn.functional.cross_entropy(model(xb), ya[idx]).backward(); opt.step()
@torch.no_grad()
def acc(model, Xa, ya): model.eval(); return (model(Xa).argmax(1) == ya).float().mean().item()'''

X("m-cv-overview",
  "Computer vision teaches machines to understand images and video. The core tasks form a ladder of detail: **classification** (what is in the image), **detection** (what and where — boxes), **segmentation** (which pixels), plus keypoints/pose, tracking in video, and generation. Modern systems use pretrained CNNs or vision transformers and fine-tune them.",
  """**Pipeline.** Image → tensor (H×W×C, values 0–255 → normalised) → backbone (CNN/ViT) extracts feature maps → task head: global pooling + linear (classification), box regression + class scores per anchor/grid cell + NMS (detection), per-pixel decoder (segmentation). **Metrics:** top-1/top-5 accuracy; IoU, mAP@0.5:0.95 for detection; mask IoU / Dice for segmentation. **Practical recipe:** start from a pretrained model, fine-tune on your labelled images with augmentation, evaluate on held-out images that reflect deployment conditions (lighting, camera, angles).""",
  """**Output sizes for one 640×640 image.** Classification: 1 vector of class probabilities (1,000 for ImageNet). Detection (YOLO): ~8,400 candidate boxes × (4 coords + 80 class scores) → after confidence filtering and NMS maybe 5 boxes. Segmentation: a 640×640 mask per detected instance — 409,600 decisions per object.""",
  ["Training from scratch when a pretrained model exists", "Test images from the same video/session as training images (leakage)", "Ignoring class imbalance and small objects", "Reporting accuracy for detection tasks"],
  ["Pick the task by the decision you need: label, location, or exact shape"], ["Pixel-level segmentation when a box is enough (labelling costs 10×)"],
  "A real street photo (Ultralytics' bus.jpg) through the three core tasks with pretrained YOLO models: image classification (top-5 ImageNet classes), object detection (boxes + confidences) and instance segmentation (masks + pixel areas). Weights download from GitHub releases.",
  ["Download the image; inspect its array", "Classify with YOLO-cls (top-5)", "Detect objects with YOLO (boxes, classes, confidence)", "Segment instances with YOLO-seg (mask areas)", "Save annotated outputs"],
  f'''
import urllib.request, numpy as np, cv2
from ultralytics import YOLO
urllib.request.urlretrieve("{BUS}", "bus.jpg"); img = cv2.imread("bus.jpg"); print("image array:", img.shape, img.dtype, "(H, W, BGR channels)")
cls = YOLO("yolo11n-cls.pt")(img, verbose=False)[0]
print("classification top-5:", [(cls.names[i], round(float(p), 3)) for i, p in zip(cls.probs.top5, cls.probs.top5conf)])
det = YOLO("yolo11n.pt")(img, verbose=False)[0]
for b in det.boxes: print(f"  detected {{det.names[int(b.cls)]:8s}} conf {{float(b.conf):.2f}} box {{b.xyxy[0].int().tolist()}}")
seg = YOLO("yolo11n-seg.pt")(img, verbose=False)[0]
areas = [(seg.names[int(c)], int(m.sum())) for c, m in zip(seg.boxes.cls, seg.masks.data.cpu().numpy())]
print("instance masks (class, pixel area at mask resolution):", areas)
cv2.imwrite("detected.jpg", det.plot()); cv2.imwrite("segmented.jpg", seg.plot()); print("saved detected.jpg and segmented.jpg")
''')

X("m-image-basics",
  "To a computer an image is a grid of numbers: height × width × channels (RGB), usually 0–255 bytes. Everything in vision starts with loading, resizing, cropping, converting colour spaces, normalising, and filtering these arrays — and knowing the conventions (RGB vs BGR, HWC vs CHW, uint8 vs float) avoids silent bugs.",
  """**Representations.** Grayscale H×W; colour H×W×3 (OpenCV loads **BGR**; PyTorch wants **C×H×W** float). Colour spaces: HSV separates hue from brightness (good for colour thresholding); Lab is perceptually uniform; grayscale Y = 0.299R + 0.587G + 0.114B. **Filtering** = convolution with a kernel: box/Gaussian blur (low-pass), Sobel (gradient), Laplacian (edges), sharpening = image + α·(image − blur). **Histogram equalisation** spreads intensities for contrast (CLAHE does it locally). **Resizing** needs interpolation (nearest, bilinear, area for shrinking); keep aspect ratio (letterbox). Normalisation for pretrained nets: (x/255 − mean)/std per channel (ImageNet mean [0.485, 0.456, 0.406]).""",
  """**By hand.** Pixel RGB (200, 100, 50) → gray = 0.299·200 + 0.587·100 + 0.114·50 = 59.8 + 58.7 + 5.7 = **124.2**. ImageNet-normalised red = (200/255 − 0.485)/0.229 = (0.784 − 0.485)/0.229 = **1.31**. A 3×3 box blur of [[10, 10, 10], [10, 100, 10], [10, 10, 10]] at the centre = 180/9 = **20**.""",
  ["Feeding BGR images to RGB-trained models", "uint8 overflow (200 + 100 = 44 in uint8)", "HWC vs CHW confusion", "Stretching images when resizing", "Different preprocessing at training vs serving"],
  ["Every vision pipeline; classical CV for controlled settings"], ["Hand-tuned filters when a learned model is feasible and data exist"],
  "Real photos bundled with scikit-image (astronaut, coffee, coins) — pixel arrays and dtypes, colour-space conversions, histogram equalisation/CLAHE, blur/sharpen/edge filters (OpenCV vs a hand convolution), resizing with letterbox, and tensor conversion for PyTorch.",
  ["Load images; inspect shape, dtype, value range", "RGB↔BGR↔HSV↔gray; colour threshold in HSV", "Histogram equalisation and CLAHE on a low-contrast image", "Filters: Gaussian blur, sharpen, Sobel (check one by hand)", "Letterbox resize and convert to a normalised CHW tensor"],
  '''
import cv2, numpy as np, torch
from skimage import data
rgb = data.astronaut(); coins = data.coins(); coffee = data.coffee()
print("astronaut:", rgb.shape, rgb.dtype, rgb.min(), rgb.max(), "| coins (gray):", coins.shape)
a = np.array([200], np.uint8); print("uint8 overflow: 200+100 =", (a + np.uint8(100))[0], "| safe:", int(a[0]) + 100)
bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR); gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY); hsv = cv2.cvtColor(coffee, cv2.COLOR_RGB2HSV)
r, g, b = rgb[0, 0].astype(float); print("gray by formula", round(0.299 * r + 0.587 * g + 0.114 * b, 1), "vs OpenCV", gray[0, 0])
red_mask = cv2.inRange(hsv, (0, 80, 50), (12, 255, 255)) | cv2.inRange(hsv, (170, 80, 50), (180, 255, 255)); print(f"coffee photo: {red_mask.mean() / 255:.1%} of pixels are red-ish (HSV threshold)")
low = (coins * 0.3 + 80).astype(np.uint8); eq = cv2.equalizeHist(low); cl = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(low)
print("contrast (std) low-contrast", round(low.std(), 1), "-> equalised", round(eq.std(), 1), "-> CLAHE", round(cl.std(), 1))
blur = cv2.GaussianBlur(gray, (5, 5), 1.0); sharp = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
sobel = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3); K = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
i, j = 100, 200; print("Sobel-x at (100,200): OpenCV", sobel[i, j], "| by hand", float((gray[i - 1:i + 2, j - 1:j + 2].astype(np.float32) * K).sum()))
print("sharpness (variance of Laplacian): blurred", round(cv2.Laplacian(blur, cv2.CV_64F).var()), "original", round(cv2.Laplacian(gray, cv2.CV_64F).var()), "sharpened", round(cv2.Laplacian(sharp, cv2.CV_64F).var()))
def letterbox(im, size=320):
    h, w = im.shape[:2]; s = size / max(h, w); rs = cv2.resize(im, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    out = np.full((size, size, 3), 114, np.uint8); y0, x0 = (size - rs.shape[0]) // 2, (size - rs.shape[1]) // 2; out[y0:y0 + rs.shape[0], x0:x0 + rs.shape[1]] = rs; return out
lb = letterbox(coffee); t = torch.from_numpy(lb).permute(2, 0, 1).float() / 255
t = (t - torch.tensor([0.485, 0.456, 0.406])[:, None, None]) / torch.tensor([0.229, 0.224, 0.225])[:, None, None]
print("letterboxed", coffee.shape, "->", lb.shape, "-> tensor", tuple(t.shape), "mean per channel", t.mean((1, 2)).numpy().round(2))
cv2.imwrite("filters.png", np.hstack([gray, blur, sharp, cv2.convertScaleAbs(sobel)])); print("saved filters.png")
''')

X("m-image-features",
  "Before deep learning, vision relied on hand-designed features: **edges** (Canny), **corners** (Harris, FAST), **keypoint descriptors** (SIFT, ORB) for matching, and **HOG** (histograms of gradient orientations) for shape. They're still used for image stitching, AR, visual odometry and low-compute settings — and they explain what CNN filters learn.",
  """**Gradients.** Gx, Gy via Sobel; magnitude √(Gx² + Gy²), orientation atan2(Gy, Gx). **Canny:** blur → gradients → non-maximum suppression → hysteresis thresholds. **Harris:** structure tensor M = Σ w[Gx², GxGy; GxGy, Gy²]; response R = det M − k·(trace M)² — large when both eigenvalues are large (corner). **SIFT:** scale-space extrema (difference of Gaussians), orientation assignment, 128-D gradient-histogram descriptor — invariant to scale/rotation. **ORB:** FAST corners + rotated BRIEF binary descriptors, matched with Hamming distance; fast and free. **Matching:** nearest neighbour + Lowe's ratio test (d₁/d₂ < 0.75) + RANSAC to fit a homography robustly. **HOG:** cells of gradient-orientation histograms, block-normalised → linear SVM (pedestrian detection).""",
  """**Harris by hand.** Flat patch: M ≈ [[0, 0], [0, 0]] → R ≈ 0. Edge: M = [[100, 0], [0, 1]] → det = 100, trace = 101, R = 100 − 0.04·10,201 = **−308** (edge, negative). Corner: M = [[100, 0], [0, 100]] → R = 10,000 − 0.04·40,000 = **8,400** (corner, large positive).""",
  ["Matching without the ratio test or RANSAC (many false matches)", "Thresholds tuned on one image", "Expecting handcrafted features to handle large appearance changes"],
  ["Stitching, AR, SLAM, registration, low-power devices, small datasets"], ["Semantic recognition at scale — CNN/ViT features win"],
  "Real images (scikit-image's camera/astronaut and Fashion-MNIST) — Canny edges, Harris corners checked against the formula, ORB keypoints matched between the photo and a rotated/scaled copy with ratio test + RANSAC homography, and HOG + linear SVM vs raw pixels for clothing classification.",
  ["Edges with Canny at two thresholds", "Harris response and corner count", "ORB features on original vs rotated/scaled image", "Ratio test + RANSAC homography; recover the rotation", "HOG + LinearSVC vs pixels on Fashion-MNIST"],
  '''
import cv2, numpy as np, torch
from skimage import data
from skimage.feature import hog
from sklearn.svm import LinearSVC
''' + FM + '''
cam = data.camera()
for lo, hi in [(50, 150), (100, 250)]: print(f"Canny ({lo},{hi}): {(cv2.Canny(cam, lo, hi) > 0).mean():.1%} edge pixels")
R = cv2.cornerHarris(np.float32(cam), blockSize=2, ksize=3, k=0.04); print("Harris corners (R > 1% of max):", int((R > 0.01 * R.max()).sum()), "| response range", f"{R.min():.1e}..{R.max():.1e}")
img = cv2.cvtColor(data.astronaut(), cv2.COLOR_RGB2GRAY); h, w = img.shape
Mrot = cv2.getRotationMatrix2D((w / 2, h / 2), 30, 0.8); warped = cv2.warpAffine(img, Mrot, (w, h))
orb = cv2.ORB_create(1000); k1, d1 = orb.detectAndCompute(img, None); k2, d2 = orb.detectAndCompute(warped, None)
pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(d1, d2, k=2); good = [m for m, n in pairs if m.distance < 0.75 * n.distance]
src = np.float32([k1[m.queryIdx].pt for m in good]); dst = np.float32([k2[m.trainIdx].pt for m in good])
H, inl = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
print(f"ORB: {len(k1)}/{len(k2)} keypoints, {len(pairs)} raw matches -> {len(good)} after ratio test -> {int(inl.sum())} RANSAC inliers")
print(f"recovered rotation {np.degrees(np.arctan2(H[1, 0], H[0, 0])):.1f}° (true 30°), scale {np.hypot(H[0, 0], H[1, 0]):.2f} (true 0.8)")
F = np.array([hog(x[0], orientations=9, pixels_per_cell=(7, 7), cells_per_block=(2, 2)) for x in X]); print("HOG feature length:", F.shape[1])
for name, A in [("raw pixels", X.reshape(len(X), -1)), ("HOG", F)]:
    print(f"  LinearSVC on {name:10s}: test acc {LinearSVC(C=0.05, max_iter=5000).fit(A[:8000], y[:8000]).score(A[8000:], y[8000:]):.3f}")
''')

X("m-cnn-architectures",
  "CNN architectures evolved through a few big ideas: **LeNet** (conv + pool), **AlexNet** (deep + ReLU + GPU + dropout), **VGG** (stacks of 3×3 convs), **Inception** (parallel multi-scale branches), **ResNet** (residual skip connections → 100+ layers), **MobileNet/EfficientNet** (depthwise-separable convs, compound scaling for efficiency), **ConvNeXt** (modernised CNN), and **Vision Transformers** (patches + attention).",
  """**Key mechanisms.** Two 3×3 convs see a 5×5 region with 2·9C² vs 25C² weights (VGG insight). **Residual block:** y = x + F(x) — identity path lets gradients flow, layers learn corrections. **Bottleneck:** 1×1 reduce → 3×3 → 1×1 expand. **Depthwise-separable conv:** per-channel K×K conv (K²·C) + 1×1 pointwise (C·C′) instead of K²·C·C′ → ~K²× cheaper (8–9× for 3×3). **Squeeze-and-excitation:** channel attention via global pooling + MLP gating. **EfficientNet** scales depth, width and resolution together. **ViT:** split into 16×16 patches, linear embed, transformer encoder; needs lots of data or pretraining; hybrids and ConvNeXt narrow the gap.""",
  """**FLOPs by hand.** Standard 3×3 conv, 128→128 channels on 28×28: 9·128·128·784 ≈ **115.6M** multiply-adds. Depthwise-separable: depthwise 9·128·784 = 0.9M + pointwise 128·128·784 = 12.8M → **13.7M** (8.4× cheaper).""",
  ["Choosing the biggest model by default", "Ignoring latency/memory on target hardware", "Comparing architectures trained with different recipes", "Training ViTs from scratch on small datasets"],
  ["ResNet/EfficientNet/ConvNeXt as reliable backbones; MobileNet for mobile/edge; ViT with pretraining"], ["Designing a new architecture before trying standard pretrained ones"],
  "Fashion-MNIST — build mini versions of the main families (LeNet, VGG-style, ResNet-style with residual blocks, MobileNet-style with depthwise-separable convs) with the same budget; compare parameters, multiply-adds and accuracy; and list parameter counts of real torchvision architectures (no weights needed).",
  ["Define LeNet, VGG-mini, ResNet-mini, MobileNet-mini", "Count parameters and estimate MACs with a forward hook", "Train each for the same epochs", "Compare accuracy per parameter", "Inspect real torchvision architectures' sizes"],
  '''
import time, numpy as np, torch, torch.nn as nn, torchvision
''' + FM + "\n" + TRAIN + '''
def conv_bn(i, o, s=1, g=1, k=3): return nn.Sequential(nn.Conv2d(i, o, k, s, k // 2, groups=g, bias=False), nn.BatchNorm2d(o), nn.ReLU())
class Res(nn.Module):
    def __init__(self, c): super().__init__(); self.f = nn.Sequential(conv_bn(c, c), nn.Conv2d(c, c, 3, 1, 1, bias=False), nn.BatchNorm2d(c))
    def forward(self, x): return torch.relu(x + self.f(x))
def dw_sep(i, o, s=1): return nn.Sequential(conv_bn(i, i, s, g=i), conv_bn(i, o, k=1))
nets = {"LeNet-5": nn.Sequential(nn.Conv2d(1, 6, 5, padding=2), nn.Tanh(), nn.AvgPool2d(2), nn.Conv2d(6, 16, 5), nn.Tanh(), nn.AvgPool2d(2), nn.Flatten(), nn.Linear(400, 120), nn.Tanh(), nn.Linear(120, 84), nn.Tanh(), nn.Linear(84, 10)),
        "VGG-mini": nn.Sequential(conv_bn(1, 32), conv_bn(32, 32), nn.MaxPool2d(2), conv_bn(32, 64), conv_bn(64, 64), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(64 * 49, 10)),
        "ResNet-mini": nn.Sequential(conv_bn(1, 32), Res(32), conv_bn(32, 64, 2), Res(64), conv_bn(64, 128, 2), Res(128), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(128, 10)),
        "MobileNet-mini": nn.Sequential(conv_bn(1, 32), dw_sep(32, 64), dw_sep(64, 128, 2), dw_sep(128, 128), dw_sep(128, 256, 2), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(256, 10))}
def macs(model):
    total = [0]
    def hook(m, i, o):
        if isinstance(m, nn.Conv2d): total[0] += o.numel() * (m.in_channels // m.groups) * m.kernel_size[0] * m.kernel_size[1]
        elif isinstance(m, nn.Linear): total[0] += m.in_features * m.out_features
    hs = [m.register_forward_hook(hook) for m in model.modules()]; model.eval(); model(Xt[:1]); [h.remove() for h in hs]; return total[0]
for name, m in nets.items():
    torch.manual_seed(0); t = time.perf_counter(); fit(m, torch.optim.Adam(m.parameters(), 2e-3), 4, Xt[tr], yt[tr])
    print(f"  {name:15s} params {sum(p.numel() for p in m.parameters()):8,d} | MACs/image {macs(m) / 1e6:6.2f}M | test acc {acc(m, Xt[te], yt[te]):.3f} | {time.perf_counter() - t:4.0f}s")
for name in ["resnet18", "resnet50", "mobilenet_v3_small", "efficientnet_b0", "convnext_tiny", "vit_b_16"]:
    m = getattr(torchvision.models, name)(weights=None); print(f"  torchvision {name:19s} {sum(p.numel() for p in m.parameters()) / 1e6:6.1f}M parameters")
''')

X("m-transfer-learning",
  "Transfer learning reuses a model pretrained on a huge dataset (ImageNet, or web-scale for CLIP/DINOv2) as a starting point. Its early layers already detect edges, textures and parts, so with a few hundred labelled images per class you can reach accuracy that would need tens of thousands from scratch. Two modes: **feature extraction** (freeze the backbone, train a new head) and **fine-tuning** (unfreeze some/all layers with a small learning rate).",
  """**Recipe.** Load pretrained backbone + its exact preprocessing (resize, ImageNet normalisation). Replace the classifier head with one sized for your classes. Stage 1: freeze backbone, train the head (higher LR, e.g. 1e-3). Stage 2: unfreeze the last blocks (or all) and fine-tune with a lower LR (1e-4–1e-5), often **discriminative learning rates** (smaller for earlier layers) and warm-up; keep BatchNorm in eval mode for tiny batches. Use augmentation. **When it transfers:** source and target domains should share low-level statistics; for very different domains (medical, satellite) fine-tune more layers or use domain-specific pretraining. Linear-probe accuracy is a quick measure of feature quality.""",
  """**Parameter budget by hand.** ResNet-18 has 11.2M parameters. Feature extraction trains only the new head: 512·C + C → for 10 classes **5,130** parameters (0.05%) — trainable on CPU in seconds and hard to overfit. Full fine-tuning updates all 11.2M — needs more data/regularisation but adapts deeper features.""",
  ["Wrong preprocessing (not the backbone's normalisation/size)", "Fine-tuning everything with a large learning rate (destroys pretrained features)", "Forgetting model.eval() for frozen BatchNorm", "Data leakage between near-duplicate train/test images"],
  ["Any image task with limited labelled data — the default starting point"], ["Domains wildly unlike the pretraining data with lots of in-domain data available (consider domain-specific pretraining)"],
  "Fashion-MNIST with only 50 labelled images per class (500 total) — train a CNN from scratch vs ResNet-18 pretrained on ImageNet used as a frozen feature extractor (logistic regression on embeddings) vs fine-tuning the last block. Run in Colab (downloads torchvision weights).",
  ["Build a small labelled set (500 images) and a test set", "Baseline CNN from scratch", "Pretrained ResNet-18: resize to 224, 3 channels, ImageNet normalisation", "Frozen features + logistic regression (linear probe)", "Fine-tune layer4 + new head with a small learning rate; compare"],
  '''
import numpy as np, torch, torch.nn as nn, torchvision
from sklearn.linear_model import LogisticRegression
''' + FM + "\n" + TRAIN + '''
device = "cuda" if torch.cuda.is_available() else "cpu"
small = torch.cat([torch.nonzero(yt[tr] == c)[:50, 0] for c in range(10)]); test = te[:1000]
scratch = nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(64 * 49, 10))
fit(scratch, torch.optim.Adam(scratch.parameters(), 1e-3), 30, Xt[small], yt[small]); print("CNN from scratch (500 labels):", round(acc(scratch, Xt[test], yt[test]), 3))
weights = torchvision.models.ResNet18_Weights.IMAGENET1K_V1                      # downloads ~45 MB (works in Colab)
mean, std = torch.tensor([0.485, 0.456, 0.406])[:, None, None], torch.tensor([0.229, 0.224, 0.225])[:, None, None]
prep = lambda x: (nn.functional.interpolate(x, size=224, mode="bilinear").repeat(1, 3, 1, 1) - mean) / std
backbone = torchvision.models.resnet18(weights=weights).to(device).eval(); backbone.fc = nn.Identity()
@torch.no_grad()
def embed(idx): return torch.cat([backbone(prep(Xt[b]).to(device)).cpu() for b in idx.split(100)]).numpy()
probe = LogisticRegression(max_iter=3000, C=0.5).fit(embed(small), yt[small].numpy()); print("pretrained frozen features + logistic regression:", round(probe.score(embed(test), yt[test].numpy()), 3))
model = torchvision.models.resnet18(weights=weights); model.fc = nn.Linear(512, 10); model = model.to(device)
for name, p in model.named_parameters(): p.requires_grad = name.startswith(("layer4", "fc"))
opt = torch.optim.AdamW([{"params": model.layer4.parameters(), "lr": 1e-4}, {"params": model.fc.parameters(), "lr": 1e-3}], weight_decay=1e-4)
for epoch in range(8):
    model.train()
    for b in small[torch.randperm(len(small))].split(32):
        opt.zero_grad(); nn.functional.cross_entropy(model(prep(Xt[b]).to(device)), yt[b].to(device)).backward(); opt.step()
model.eval()
with torch.no_grad(): pred = torch.cat([model(prep(Xt[b]).to(device)).argmax(1).cpu() for b in test.split(100)])
print("fine-tuned layer4 + head:", round((pred == yt[test]).float().mean().item(), 3), "| trainable params:", sum(p.numel() for p in model.parameters() if p.requires_grad))
''', net=True)

X("m-augmentation",
  "Data augmentation creates new training examples by transforming existing ones in ways that don't change the label — flips, crops, rotations, colour jitter, noise, cutout, mixup. It teaches the model the invariances you care about and is one of the most effective regularisers, especially with little data.",
  """**Families.** Geometric: random resized crop, flip, rotate, affine, perspective. Photometric: brightness/contrast/saturation/hue jitter, blur, noise. Occlusion: Cutout/Random Erasing. Mixing: **Mixup** x̃ = λxᵢ + (1 − λ)xⱼ, ỹ = λyᵢ + (1 − λ)yⱼ, λ ~ Beta(α, α); **CutMix** pastes a patch and mixes labels by area. Policies: AutoAugment, RandAugment (N ops at magnitude M), TrivialAugment. **Rules:** only label-preserving transforms (no vertical flips for text or digits 6/9; boxes/masks must be transformed together for detection/segmentation); apply only on training data; test-time augmentation (TTA) averages predictions over a few augmented views.""",
  """**Mixup by hand.** λ = 0.7, image A is a 'shirt' (one-hot class 6), image B a 'coat' (class 4) → pixels 0.7A + 0.3B, target 0.7 on class 6 and 0.3 on class 4. Cross-entropy with soft targets = 0.7·CE(shirt) + 0.3·CE(coat).""",
  ["Augmenting the validation/test set", "Transforms that change the label", "Forgetting to transform boxes/masks with the image", "Too-strong augmentation on tiny models (underfitting)"],
  ["Small/medium image datasets, any vision model; speech (SpecAugment) and text (back-translation) have analogues"], ["Transforms that break the physics of your data (e.g. flipping medical images with laterality)"],
  "Fashion-MNIST with 2,000 training images — torchvision v2 transforms (flip, random-resized-crop, rotation, random erasing) visualised on a real photo, then training the same CNN with no augmentation, standard augmentation, mixup, and test-time augmentation.",
  ["Show v2 transforms on a scikit-image photo (shapes stay consistent)", "Train baseline CNN on 2,000 images", "Train with flip + crop + erasing", "Train with mixup (soft labels)", "Evaluate with test-time augmentation"],
  '''
import numpy as np, torch, torch.nn as nn
from skimage import data
from torchvision.transforms import v2
''' + FM + "\n" + TRAIN + '''
photo = torch.from_numpy(data.astronaut()).permute(2, 0, 1)
pipe = v2.Compose([v2.RandomResizedCrop(224, scale=(0.5, 1.0)), v2.RandomHorizontalFlip(), v2.ColorJitter(0.3, 0.3, 0.3), v2.RandomRotation(15), v2.ToDtype(torch.float32, scale=True), v2.RandomErasing(p=0.5)])
views = torch.stack([pipe(photo) for _ in range(4)]); print("augmented views of a real photo:", tuple(views.shape), "| per-view mean brightness", views.mean((1, 2, 3)).numpy().round(3))
aug = v2.Compose([v2.RandomHorizontalFlip(), v2.RandomResizedCrop(28, scale=(0.8, 1.0), antialias=True), v2.RandomErasing(p=0.3, scale=(0.02, 0.1))])
small = tr[:2000]
def net(): torch.manual_seed(0); return nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Dropout(0.3), nn.Linear(64 * 49, 10))
base = net(); fit(base, torch.optim.Adam(base.parameters(), 1e-3), 25, Xt[small], yt[small]); print("no augmentation:", round(acc(base, Xt[te], yt[te]), 3))
augm = net(); fit(augm, torch.optim.Adam(augm.parameters(), 1e-3), 25, Xt[small], yt[small], tf=lambda x: torch.stack([aug(i) for i in x])); print("flip + crop + erasing:", round(acc(augm, Xt[te], yt[te]), 3))
mix = net(); opt = torch.optim.Adam(mix.parameters(), 1e-3); beta = torch.distributions.Beta(0.4, 0.4)
for epoch in range(25):
    mix.train()
    for idx in torch.randperm(len(small)).split(128):
        xb, yb = Xt[small][idx], yt[small][idx]; lam = beta.sample().item(); perm = torch.randperm(len(xb)); out = mix(lam * xb + (1 - lam) * xb[perm])
        loss = lam * nn.functional.cross_entropy(out, yb) + (1 - lam) * nn.functional.cross_entropy(out, yb[perm]); opt.zero_grad(); loss.backward(); opt.step()
print("mixup:", round(acc(mix, Xt[te], yt[te]), 3))
augm.eval()
with torch.no_grad(): tta = (torch.softmax(augm(Xt[te]), 1) + torch.softmax(augm(Xt[te].flip(3)), 1)).argmax(1)
print("augmented model + test-time augmentation (orig + flip):", round((tta == yt[te]).float().mean().item(), 3))
''')

X("m-object-detection",
  "Object detection finds every object in an image and draws a labelled box around it. Detectors predict many candidate boxes with class scores, then keep the best with **non-maximum suppression**. Families: two-stage (Faster R-CNN — propose regions, then classify), one-stage (YOLO, SSD, RetinaNet — predict densely in one pass), and transformer-based (DETR, RT-DETR).",
  """**Building blocks.** **IoU** = area(A ∩ B)/area(A ∪ B). Box encoding: centre (x, y), width, height, often predicted as offsets from anchors or grid cells. **Loss** = classification (BCE/focal) + box regression (L1, GIoU/CIoU) + objectness. **NMS:** sort by score; keep the top box; drop others of the same class with IoU > threshold (e.g. 0.5); repeat. **Evaluation:** a prediction is a true positive if IoU ≥ t with an unmatched ground-truth box; precision–recall curve per class → AP; **mAP@0.5** and **mAP@0.5:0.95** (COCO, averaging t = 0.5…0.95). Small objects: higher resolution, feature pyramids (FPN), tiling.""",
  """**IoU by hand.** A = [0, 0, 4, 4] (area 16), B = [2, 2, 6, 6] (area 16). Intersection [2, 2, 4, 4] = 4; union = 16 + 16 − 4 = 28 → IoU = **0.143**. **NMS:** boxes with scores 0.9 (A), 0.8 (A shifted by 1 px, IoU 0.62), 0.7 (far away) → keep 0.9, suppress 0.8, keep 0.7.""",
  ["Evaluating with accuracy instead of mAP", "Wrong box format (xyxy vs xywh, normalised vs pixels)", "NMS threshold too low (merges adjacent objects) or high (duplicates)", "Train/val images from the same video sequence"],
  ["Counting, tracking, safety, retail shelves, traffic, inspection"], ["When you only need 'is X present?' (classification) or exact outlines (segmentation)"],
  "Pretrained YOLO on real COCO images (coco8 sample + bus.jpg): IoU and NMS implemented from scratch and checked against torchvision, raw vs NMS-filtered predictions, a confidence-threshold sweep, and mAP evaluation on the labelled coco8 validation set — then a short fine-tune.",
  ["IoU and NMS from scratch; compare with torchvision.ops", "Detect objects on a real photo; count raw vs kept boxes", "Sweep confidence thresholds", "Validate the pretrained model on coco8 (mAP50, mAP50-95)", "Fine-tune for a few epochs and re-validate"],
  f'''
import os, urllib.request, numpy as np, torch, torchvision
from ultralytics import YOLO
def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]); inter = max(0, x2 - x1) * max(0, y2 - y1)
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)
def nms(boxes, scores, thr=0.5):
    order, keep = list(np.argsort(-scores)), []
    while order:
        i = order.pop(0); keep.append(i); order = [j for j in order if iou(boxes[i], boxes[j]) <= thr]
    return keep
print("IoU([0,0,4,4],[2,2,6,6]) =", round(iou([0, 0, 4, 4], [2, 2, 6, 6]), 3))
urllib.request.urlretrieve("{BUS}", "bus.jpg"); model = YOLO("yolo11n.pt")
raw = model("bus.jpg", conf=0.05, iou=0.99, verbose=False)[0]                     # almost no NMS -> many overlapping candidates
b, s = raw.boxes.xyxy.numpy(), raw.boxes.conf.numpy()
mine = sorted(nms(b, s, 0.5)); ref = sorted(torchvision.ops.nms(torch.tensor(b), torch.tensor(s), 0.5).tolist())
print(f"candidates {{len(b)}} -> after my NMS {{len(mine)}} | torchvision NMS agrees: {{mine == ref}}")
for c in [0.1, 0.25, 0.5, 0.75]:
    r = model("bus.jpg", conf=c, verbose=False)[0]; print(f"  conf ≥ {{c}}: {{len(r.boxes)}} boxes {{sorted(r.names[int(k)] for k in r.boxes.cls)}}")
m = model.val(data="coco8.yaml", imgsz=640, batch=4, plots=False, verbose=False, project=os.path.abspath("runs"), name="val")
print(f"pretrained on coco8 val: mAP50 {{m.box.map50:.3f}} | mAP50-95 {{m.box.map:.3f}}")
ft = YOLO("yolo11n.pt"); ft.train(data="coco8.yaml", epochs=3, imgsz=320, batch=4, workers=0, plots=False, verbose=False, project=os.path.abspath("runs"), name="ft")
m2 = ft.val(data="coco8.yaml", imgsz=320, batch=4, plots=False, verbose=False, project=os.path.abspath("runs"), name="val2"); print(f"after 3-epoch fine-tune at 320 px: mAP50 {{m2.box.map50:.3f}} | mAP50-95 {{m2.box.map:.3f}}")
''')

X("m-segmentation",
  "Segmentation labels every pixel. **Semantic** segmentation gives each pixel a class (road, sky); **instance** segmentation separates individual objects (person 1, person 2); **panoptic** does both. Classical methods (thresholding, watershed) work in controlled settings; deep models (U-Net, DeepLab, Mask R-CNN, YOLO-seg, SAM) handle real-world images.",
  """**Classical.** Otsu picks the threshold maximising between-class variance of the intensity histogram; morphology (opening/closing) cleans masks; distance transform + **watershed** splits touching objects; connected components count them. **Deep.** Encoder–decoder (**U-Net**: downsampling path + upsampling path with **skip connections** to recover detail); dilated/atrous convolutions + ASPP (DeepLab); Mask R-CNN adds a mask head to a detector; SAM is a promptable foundation model. **Losses:** per-pixel cross-entropy, **Dice** = 2|A ∩ B|/(|A| + |B|) (handles class imbalance), focal. **Metrics:** IoU/Jaccard per class, mean IoU, Dice.""",
  """**Dice and IoU by hand.** Predicted mask 50 pixels, true mask 40, overlap 30. IoU = 30/(50 + 40 − 30) = **0.50**; Dice = 2·30/(50 + 40) = **0.667**. Dice = 2·IoU/(1 + IoU) always. **Otsu:** for a histogram with two clear peaks at 40 and 200, the threshold lands in the valley (~120).""",
  ["Pixel accuracy on imbalanced masks (background dominates)", "Resizing masks with bilinear interpolation (creates invalid labels — use nearest)", "Augmenting images without the masks", "Ignoring boundary quality"],
  ["Medical imaging, autonomous driving, satellite/agriculture, photo editing, measurement"], ["When boxes suffice (much cheaper labels)"],
  "Real images: scikit-image 'coins' (classical pipeline — Otsu, morphology, distance transform, watershed, counting and measuring coins) and bus.jpg with a pretrained YOLO-seg model (instance masks, areas, IoU/Dice between overlapping masks), plus a tiny U-Net trained to segment garments in Fashion-MNIST.",
  ["Classical: Otsu threshold, morphology, connected components", "Watershed to split touching coins; measure areas", "Deep instance segmentation on a street photo", "Dice/IoU utilities", "Tiny U-Net with skip connections trained on garment masks"],
  f'''
import urllib.request, numpy as np, torch, torch.nn as nn
from scipy import ndimage as ndi
from skimage import data, filters, measure, morphology, segmentation
from skimage.feature import peak_local_max
from ultralytics import YOLO
coins = data.coins(); t = filters.threshold_otsu(coins); mask = morphology.remove_small_objects(ndi.binary_fill_holes(morphology.opening(coins > t, morphology.disk(2))), 100)
print(f"Otsu threshold {{t:.0f}} | foreground {{mask.mean():.1%}} | connected components {{measure.label(mask).max()}}")
dist = ndi.distance_transform_edt(mask); peaks = peak_local_max(dist, min_distance=12, labels=measure.label(mask)); markers = np.zeros_like(dist, int); markers[tuple(peaks.T)] = np.arange(1, len(peaks) + 1)
ws = segmentation.watershed(-dist, markers, mask=mask); areas = [r.area for r in measure.regionprops(ws)]
print(f"watershed coins: {{ws.max()}} | area range {{min(areas)}}-{{max(areas)}} px | median {{int(np.median(areas))}} px")
def dice(a, b): return 2 * (a & b).sum() / (a.sum() + b.sum() + 1e-9)
def iou(a, b): return (a & b).sum() / ((a | b).sum() + 1e-9)
urllib.request.urlretrieve("{BUS}", "bus.jpg"); r = YOLO("yolo11n-seg.pt")("bus.jpg", verbose=False)[0]; M = r.masks.data.numpy() > 0.5
for c, m in zip(r.boxes.cls, M): print(f"  instance {{r.names[int(c)]:7s}} mask area {{m.mean():.1%}} of image")
people = [i for i, c in enumerate(r.boxes.cls) if r.names[int(c)] == "person"]
if len(people) > 1: print(f"  overlap between two person masks: IoU {{iou(M[people[0]], M[people[1]]):.3f}} Dice {{dice(M[people[0]], M[people[1]]):.3f}}")
import gzip
base = "https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/master/data/fashion/"
Xf = np.frombuffer(gzip.decompress(urllib.request.urlopen(base + "t10k-images-idx3-ubyte.gz").read()), np.uint8, offset=16).reshape(-1, 1, 28, 28) / 255.0
Xi = torch.tensor(Xf[:3000], dtype=torch.float32); Yi = (Xi > 0.05).float(); Xi = (Xi + 0.15 * torch.randn_like(Xi)).clamp(0, 1)   # noisy image -> clean garment mask
class UNet(nn.Module):
    def __init__(self):
        super().__init__(); c = lambda i, o: nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.ReLU(), nn.Conv2d(o, o, 3, padding=1), nn.ReLU())
        self.d1, self.d2, self.mid = c(1, 16), c(16, 32), c(32, 64); self.u2, self.c2 = nn.ConvTranspose2d(64, 32, 2, 2), c(64, 32); self.u1, self.c1 = nn.ConvTranspose2d(32, 16, 2, 2), c(32, 16); self.out = nn.Conv2d(16, 1, 1)
    def forward(self, x):
        a = self.d1(x); b = self.d2(nn.functional.max_pool2d(a, 2)); m = self.mid(nn.functional.max_pool2d(b, 2))
        b2 = self.c2(torch.cat([self.u2(m), b], 1)); return self.out(self.c1(torch.cat([self.u1(b2), a], 1)))      # skip connections
torch.manual_seed(0); unet = UNet(); opt = torch.optim.Adam(unet.parameters(), 2e-3)
for epoch in range(3):
    for idx in torch.randperm(2500).split(64):
        p = unet(Xi[idx]); soft = torch.sigmoid(p); dl = 1 - (2 * (soft * Yi[idx]).sum() + 1) / (soft.sum() + Yi[idx].sum() + 1)
        opt.zero_grad(); (nn.functional.binary_cross_entropy_with_logits(p, Yi[idx]) + dl).backward(); opt.step()
with torch.no_grad(): pr = (unet(Xi[2500:]) > 0).numpy(); gt = Yi[2500:].numpy() > 0
print(f"U-Net garment masks: Dice {{dice(pr, gt):.3f}} | IoU {{iou(pr, gt):.3f}} | pixel accuracy {{(pr == gt).mean():.3f}}")
''')

X("m-video",
  "Video is a sequence of images over time, so vision tasks gain a temporal dimension: **motion detection**, **optical flow**, **object tracking** (keep identities across frames), **action recognition** and video understanding. Practical systems combine per-frame detection with tracking and temporal smoothing, and must keep up with the frame rate.",
  """**Techniques.** Frame differencing |Iₜ − Iₜ₋₁| > τ; **background subtraction** (MOG2 models each pixel as a Gaussian mixture, adapting over time). **Optical flow:** brightness constancy I(x, y, t) = I(x + u, y + v, t + 1) → Ixu + Iyv + It = 0; Lucas–Kanade solves it for sparse points in a window (least squares); Farnebäck gives dense flow. **Tracking-by-detection:** detect each frame, associate with tracks via IoU/appearance (Hungarian matching) and a motion model (Kalman filter) — SORT, DeepSORT, ByteTrack. **Action recognition:** 3D convolutions (C3D, I3D), two-stream (RGB + flow), (2+1)D, video transformers (TimeSformer, VideoMAE). Throughput: process every n-th frame, resize, batch.""",
  """**Flow constraint by hand.** At a pixel Ix = 2, Iy = 0, It = −4 → 2u = 4 → **u = 2 px/frame** to the right (v undetermined by this pixel alone — the aperture problem; Lucas–Kanade uses a window of pixels to pin down both). At 25 fps, 2 px/frame = 50 px/s.""",
  ["Processing every full-resolution frame when not needed", "Train/test frames from the same clip (near-duplicates)", "Ignoring identity switches when evaluating tracking", "Not handling variable frame rates"],
  ["Surveillance, sports analytics, traffic counting, robotics, video search"], ["When single key frames answer the question"],
  "OpenCV's real pedestrian video (vtest.avi, 795 frames) — read frames, MOG2 background subtraction to count moving blobs, dense Farnebäck optical flow for average motion, Lucas–Kanade sparse tracking, and YOLO + ByteTrack person tracking with unique IDs; writes an annotated clip.",
  ["Open the video; read FPS, size, frame count", "Background subtraction + contours = moving-object counts", "Dense optical flow: average motion direction", "Sparse Lucas–Kanade feature tracks", "YOLO tracking (ByteTrack) on the first 120 frames; count unique people; save video"],
  f'''
import os, urllib.request, cv2, numpy as np
from ultralytics import YOLO
urllib.request.urlretrieve("{VIDEO}", "vtest.avi"); cap = cv2.VideoCapture("vtest.avi")
fps, W, H, N = cap.get(cv2.CAP_PROP_FPS), int(cap.get(3)), int(cap.get(4)), int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); print(f"video {{W}}x{{H}} @ {{fps:.0f}} fps, {{N}} frames")
mog = cv2.createBackgroundSubtractorMOG2(history=200, detectShadows=True); counts, flows, prev = [], [], None
lk_pts, tracks_len = None, []
for i in range(300):
    ok, frame = cap.read()
    if not ok: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY); fg = mog.apply(frame); fg = cv2.morphologyEx((fg == 255).astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    counts.append(sum(cv2.contourArea(c) > 300 for c in cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]))
    if prev is not None:
        flow = cv2.calcOpticalFlowFarneback(prev, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0); mag = np.linalg.norm(flow, axis=2); moving = mag > 1
        flows.append(flow[moving].mean(0) if moving.any() else np.zeros(2))
        if lk_pts is None or len(lk_pts) < 20: lk_pts = cv2.goodFeaturesToTrack(prev, 100, 0.01, 10)
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, gray, lk_pts, None); lk_pts = nxt[st[:, 0] == 1].reshape(-1, 1, 2); tracks_len.append(len(lk_pts))
    prev = gray
print(f"moving blobs per frame (after warm-up): mean {{np.mean(counts[50:]):.1f}}, max {{max(counts[50:])}}")
f = np.array(flows[50:]); print(f"mean motion of moving pixels (u, v) = {{[round(float(v), 2) for v in f.mean(0)]}} px/frame -> mostly {{'horizontal' if abs(f.mean(0)[0]) > abs(f.mean(0)[1]) else 'vertical'}}")
print("Lucas-Kanade points still tracked (sampled):", tracks_len[::50])
# tracking uses the `lap` package (ultralytics installs it automatically; otherwise: pip install lap)
model = YOLO("yolo11n.pt"); ids = set(); out = cv2.VideoWriter("tracked.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
for k, r in enumerate(model.track("vtest.avi", tracker="bytetrack.yaml", classes=[0], stream=True, verbose=False, imgsz=480)):
    if r.boxes.id is not None: ids.update(r.boxes.id.int().tolist())
    out.write(r.plot())
    if k == 119: break
out.release(); print(f"YOLO + ByteTrack over 120 frames: {{len(ids)}} unique person IDs | saved tracked.mp4 ({{os.path.getsize('tracked.mp4') // 1024}} KB)")
''')

X("m-face-emotion",
  "Face analysis is a pipeline: **detect** faces, **align/crop** them, then **classify** (emotion, age, mask) or **embed** (identity). Emotion recognition maps a face crop to categories like happy/sad/angry/surprised/neutral. It's popular in demos but scientifically and ethically fraught — expressions don't reliably reveal inner feelings, and accuracy varies across groups.",
  """**Detection:** Viola–Jones Haar cascades (fast, frontal faces, many misses), HOG + SVM (dlib), deep detectors (MTCNN, RetinaFace, YuNet, MediaPipe) — more robust to pose/lighting. **Alignment:** landmarks (eyes, nose) → similarity transform to a canonical crop. **Classification:** CNN/ViT fine-tuned on datasets like FER-2013 (48×48 grayscale, 7 classes, ~65–75% accuracy; human agreement is also limited) or AffectNet. **Evaluation:** per-class recall and confusion (fear vs surprise is commonly confused), and per-demographic performance. **Responsible use:** the EU AI Act prohibits emotion recognition in workplaces and schools (with narrow exceptions); never use it for hiring, policing or surveillance decisions; get consent and disclose.""",
  """**Haar features by hand.** A two-rectangle feature = (sum of pixels in the white rectangle) − (sum in the black one). With an integral image II, any rectangle sum = II(D) − II(B) − II(C) + II(A): **4 lookups**, whatever the size — that's why Viola–Jones runs in real time. The eye region is darker than the cheeks below → a strong response.""",
  ["Treating predicted emotion as ground truth about feelings", "Deploying without per-group evaluation", "Using emotion AI in hiring, education or policing", "Running a frontal-face cascade on profile faces"],
  ["Consent-based UX research, accessibility aids, media analytics with aggregate reporting"], ["Any high-stakes decision about a person; covert surveillance"],
  "A real photo (scikit-image astronaut, Eileen Collins — public-domain NASA image) — Haar-cascade face detection and an integral-image check, aligned crop, and emotion classification with a pretrained ViT from Hugging Face (Colab: downloads the model). Prints probabilities and a responsible-use note.",
  ["Load the image; build an integral image and verify a rectangle sum", "Detect faces with OpenCV's Haar cascade", "Crop and pad the face", "Classify expression with a pretrained model (top-3 probabilities)", "Report with uncertainty and limitations"],
  f'''
import urllib.request, cv2, numpy as np
from PIL import Image
from skimage import data
from transformers import pipeline
rgb = data.astronaut(); gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
ii = cv2.integral(gray); y0, x0, y1, x1 = 50, 100, 90, 160
print("rectangle sum by integral image:", int(ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0]), "| direct:", int(gray[y0:y1, x0:x1].sum()))
urllib.request.urlretrieve("{HAAR}", "haar.xml"); faces = cv2.CascadeClassifier("haar.xml").detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
print("faces found:", [tuple(int(v) for v in f) for f in faces])
x, y, w, h = max(faces, key=lambda f: f[2] * f[3]); pad = int(0.2 * w)
crop = Image.fromarray(rgb[max(0, y - pad):y + h + pad, max(0, x - pad):x + w + pad])
clf = pipeline("image-classification", model="trpakov/vit-face-expression")        # downloads from Hugging Face (works in Colab)
for p in clf(crop, top_k=3): print(f"  {{p['label']:9s}} {{p['score']:.2f}}")
print("Note: this is the model's guess about a facial expression in one photo, not a measurement of how the person feels.")
''', net=True)

X("m-siamese",
  "A Siamese network uses the **same** encoder on two (or three) inputs and compares their embeddings. Instead of learning fixed classes, it learns a **similarity space** where same-identity items are close — so it can verify faces, signatures or products it has never seen, from one example each (one-shot learning).",
  """**Losses.** Contrastive: L = y·d² + (1 − y)·max(0, m − d)² for pairs (y = 1 same). **Triplet:** L = max(0, d(a, p) − d(a, n) + m) with anchor, positive, negative; **hard-negative mining** picks negatives that are close. Modern face systems use angular-margin softmax (ArcFace/CosFace) on normalised embeddings — easier to train. **Inference:** verification = threshold on distance/cosine; identification = nearest neighbour in a gallery of enrolled embeddings (vector search). **Evaluation:** ROC on same/different pairs, TAR @ FAR (true accept rate at a fixed false accept rate), Rank-1 accuracy on identities unseen in training.""",
  """**Triplet loss by hand.** Margin 0.5. d(a, p) = 0.4, d(a, n) = 1.2 → max(0, 0.4 − 1.2 + 0.5) = **0** (already satisfied). d(a, n) = 0.6 → max(0, 0.4 − 0.6 + 0.5) = **0.3** → gradients push n away and p closer. Easy triplets give zero loss — why mining matters.""",
  ["Evaluating on identities seen in training", "Random triplets only (mostly zero loss)", "Unnormalised embeddings with cosine thresholds", "One threshold for all conditions without calibration"],
  ["Face/signature verification, product matching, duplicate detection, few-shot classification"], ["Fixed small label sets with plenty of examples per class (plain classification is simpler)"],
  "Olivetti faces (40 people; downloaded by scikit-learn) — train a small CNN embedding with triplet loss on 30 people, then verify and identify the 10 **unseen** people: pair ROC-AUC, best threshold, and one-shot Rank-1 identification, compared with raw-pixel distances.",
  ["Split identities: 30 for training, 10 unseen for testing", "CNN encoder producing L2-normalised 64-d embeddings", "Triplet training with batch-hard negative mining", "Verification on unseen pairs: ROC-AUC and threshold", "One-shot identification (gallery of one image per person)"],
  '''
import numpy as np, torch, torch.nn as nn
from sklearn.datasets import fetch_olivetti_faces
from sklearn.metrics import roc_auc_score
faces = fetch_olivetti_faces(); X = torch.tensor(faces.images[:, None], dtype=torch.float32); y = torch.tensor(faces.target)
train_ids, test_ids = torch.arange(30), torch.arange(30, 40); trm, tem = torch.isin(y, train_ids), torch.isin(y, test_ids)
enc = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(4), nn.Flatten(), nn.Linear(1024, 64))
embed = lambda x: nn.functional.normalize(enc(x), dim=1)
torch.manual_seed(0); opt = torch.optim.Adam(enc.parameters(), 1e-3); Xtr, ytr = X[trm], y[trm]
for step in range(300):
    ids = train_ids[torch.randperm(30)[:8]]; idx = torch.cat([torch.nonzero(ytr == i)[torch.randperm(10)[:4], 0] for i in ids])
    e, lab = embed(Xtr[idx]), ytr[idx]; D = torch.cdist(e, e); same = lab[:, None] == lab[None]
    hardest_pos = (D * same).max(1).values; hardest_neg = (D + 10 * same).min(1).values             # batch-hard mining
    loss = torch.relu(hardest_pos - hardest_neg + 0.3).mean(); opt.zero_grad(); loss.backward(); opt.step()
    if step % 100 == 0: print(f"  step {step}: triplet loss {loss.item():.3f}")
enc.eval()
with torch.no_grad(): E = embed(X[tem]).numpy()
P, lab = X[tem].flatten(1).numpy(), y[tem].numpy(); i, j = np.triu_indices(len(lab), 1); same = lab[i] == lab[j]
sim_emb = (E[i] * E[j]).sum(1); sim_pix = -np.linalg.norm(P[i] - P[j], axis=1)
print(f"verification on 10 unseen people: ROC-AUC embeddings {roc_auc_score(same, sim_emb):.3f} vs raw pixels {roc_auc_score(same, sim_pix):.3f}")
ths = np.linspace(-1, 1, 201); best = ths[np.argmax([((sim_emb > t) == same).mean() for t in ths])]; print(f"best cosine threshold {best:.2f}: pair accuracy {((sim_emb > best) == same).mean():.3f}")
gallery = np.array([np.nonzero(lab == p)[0][0] for p in np.unique(lab)]); probes = np.setdiff1d(np.arange(len(lab)), gallery)
pred = lab[gallery][np.argmax(E[probes] @ E[gallery].T, 1)]; print(f"one-shot identification (1 enrolled photo/person) Rank-1: {(pred == lab[probes]).mean():.3f}")
''')

X("m-gan",
  "A generative adversarial network trains two networks against each other: a **generator** turns random noise into fake samples, and a **discriminator** tries to tell fakes from real data. As each improves, the generator learns to produce realistic samples. GANs created the first photorealistic synthetic faces (StyleGAN) and power image-to-image translation (pix2pix, CycleGAN).",
  """**Minimax game.** min_G max_D E_x[log D(x)] + E_z[log(1 − D(G(z)))]. For a fixed G the optimal discriminator is D* = p_data/(p_data + p_g), and the generator then minimises 2·JS(p_data‖p_g) − log 4. In practice G uses the **non-saturating** loss −log D(G(z)) (stronger gradients early). **DCGAN rules:** strided convs/transposed convs, BatchNorm, ReLU in G, LeakyReLU in D, Adam(2e-4, β₁ = 0.5). **Failure modes:** mode collapse (G produces few varieties), oscillation, D too strong (vanishing G gradients). Fixes: WGAN-GP (Wasserstein distance + gradient penalty), spectral norm, two-timescale learning rates. **Evaluation:** FID (distance between Inception-feature Gaussians of real vs fake), precision/recall for generative models, human inspection.""",
  """**Equilibrium by hand.** If G is perfect, p_g = p_data → D* = 0.5 everywhere → value = log 0.5 + log 0.5 = **−1.386** (= −log 4). Discriminator loss (BCE, real + fake) at that point = 2·0.693 = **1.386** — a stable GAN's D loss hovers near there.""",
  ["Judging progress by loss values alone (look at samples, FID)", "D much stronger than G", "Mode collapse unnoticed (check diversity)", "Forgetting tanh output range ↔ data scaled to [−1, 1]"],
  ["Image synthesis, super-resolution, style transfer, data augmentation research"], ["When stable likelihood-based or diffusion models are acceptable (diffusion now dominates quality)"],
  "Fashion-MNIST — a DCGAN trained on CPU for a few minutes: discriminator/generator losses, D's accuracy on real vs fake, a diversity check against mode collapse (classifier-predicted class distribution of generated images), a nearest-real-neighbour check (memorisation) and a saved sample grid.",
  ["Scale images to [−1, 1]; define DCGAN generator and discriminator", "Alternate D and G updates with BCE (non-saturating G loss)", "Track losses and D(real)/D(fake)", "Diversity: classify 1,000 fakes with a pretrained classifier", "Memorisation check and sample grid"],
  '''
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, torch, torch.nn as nn
''' + FM + "\n" + TRAIN + '''
real = Xt * 2 - 1; Z = 64
G = nn.Sequential(nn.Linear(Z, 128 * 7 * 7), nn.BatchNorm1d(128 * 7 * 7), nn.ReLU(), nn.Unflatten(1, (128, 7, 7)), nn.ConvTranspose2d(128, 64, 4, 2, 1), nn.BatchNorm2d(64), nn.ReLU(), nn.ConvTranspose2d(64, 1, 4, 2, 1), nn.Tanh())
D = nn.Sequential(nn.Conv2d(1, 64, 4, 2, 1), nn.LeakyReLU(0.2), nn.Conv2d(64, 128, 4, 2, 1), nn.BatchNorm2d(128), nn.LeakyReLU(0.2), nn.Flatten(), nn.Linear(128 * 49, 1))
oG, oD = torch.optim.Adam(G.parameters(), 2e-4, betas=(0.5, 0.999)), torch.optim.Adam(D.parameters(), 2e-4, betas=(0.5, 0.999)); bce = nn.functional.binary_cross_entropy_with_logits
for epoch in range(6):
    for idx in torch.randperm(len(real)).split(128):
        xr = real[idx]; xf = G(torch.randn(len(idx), Z))
        dr, df = D(xr), D(xf.detach()); lossD = bce(dr, torch.full_like(dr, 0.9)) + bce(df, torch.zeros_like(df))        # one-sided label smoothing
        oD.zero_grad(); lossD.backward(); oD.step()
        gl = D(xf); lossG = bce(gl, torch.ones_like(gl)); oG.zero_grad(); lossG.backward(); oG.step()                   # non-saturating generator loss
    print(f"  epoch {epoch + 1}: D loss {lossD.item():.3f} G loss {lossG.item():.3f} | D(real) {torch.sigmoid(dr).mean():.2f} D(fake) {torch.sigmoid(df).mean():.2f}")
judge = nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(64 * 49, 10))
fit(judge, torch.optim.Adam(judge.parameters(), 1e-3), 3, Xt[tr], yt[tr]); judge.eval(); G.eval()
with torch.no_grad(): fakes = (G(torch.randn(1000, Z)) + 1) / 2; cls = judge(fakes).argmax(1)
print("generated class mix (no mode collapse if spread):", {NAMES[k]: int(v) for k, v in zip(*np.unique(cls.numpy(), return_counts=True))})
d = torch.cdist(fakes[:100].flatten(1), Xt.flatten(1)).min(1).values; dd = torch.cdist(Xt[te[:100]].flatten(1), Xt[tr].flatten(1)).min(1).values
print(f"nearest-real distance: fakes {d.mean():.2f} vs real test images {dd.mean():.2f} (similar = not memorising)")
fig, ax = plt.subplots(4, 8, figsize=(8, 4)); [a.imshow(f[0], cmap="gray") or a.axis("off") for a, f in zip(ax.flat, fakes[:32])]; fig.savefig("gan_samples.png"); print("saved gan_samples.png")
''')

X("m-super-resolution",
  "Super-resolution reconstructs a sharp high-resolution image from a low-resolution one, hallucinating plausible detail learned from data. It's used to upscale photos and video, enhance satellite and medical images, and in phone cameras. Models range from SRCNN (3 conv layers) to EDSR/ESRGAN (GAN-based, sharper textures) and diffusion upscalers.",
  """**Setup.** Make training pairs by downsampling HR images (bicubic ×s, plus blur/noise/JPEG for realism). **SRCNN:** upsample with bicubic, then 3 convs (patch extraction → non-linear mapping → reconstruction) learn the residual detail. Modern nets work in LR space and upsample at the end with **sub-pixel convolution (PixelShuffle)**: produce C·s² channels and rearrange into s× larger maps. **Losses:** L1/L2 → high PSNR but blurry; perceptual loss (VGG features) and adversarial loss → sharper but may invent details. **Metrics:** PSNR = 10·log₁₀(MAX²/MSE) (dB), SSIM (structural similarity), LPIPS (learned perceptual). Never use SR outputs as evidence (forensics/medical) without care — details can be fabricated.""",
  """**PSNR by hand.** 8-bit image, MSE = 100 → PSNR = 10·log₁₀(255²/100) = 10·log₁₀(650.25) = **28.1 dB**. Halving MSE adds **3 dB**. PixelShuffle ×2: a 64×64 map with 4 channels → 128×128 with 1 channel.""",
  ["Training only on clean bicubic downsampling, then failing on real camera images", "Judging by PSNR alone (blurry outputs score well)", "Evaluating on training images", "Using SR detail as factual evidence"],
  ["Photo/video upscaling, satellite and microscopy enhancement, game rendering"], ["Forensic or diagnostic decisions based on invented detail"],
  "Real photos from scikit-image and scikit-learn (astronaut, coffee, chelsea, china, flower, camera…) — create ×2 low/high-resolution patch pairs, compare nearest/bicubic upsampling, train an SRCNN-style residual model and an ESPCN model with PixelShuffle, and report PSNR/SSIM on a held-out photo; saves a comparison image.",
  ["Load photos; hold one out for testing; grayscale luminance", "Make LR inputs by downscaling ×2 (area) and patch pairs", "Baselines: nearest and bicubic", "Train SRCNN (on bicubic input, residual) and ESPCN (PixelShuffle)", "PSNR/SSIM on the held-out photo; save crops"],
  '''
import cv2, numpy as np, torch, torch.nn as nn
from skimage import data
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
from sklearn.datasets import load_sample_image
to_y = lambda im: cv2.cvtColor(im, cv2.COLOR_RGB2YCrCb)[..., 0] if im.ndim == 3 else im
imgs = [to_y(i) for i in [data.astronaut(), data.coffee(), data.chelsea(), load_sample_image("china.jpg"), data.rocket(), data.camera()]]; test_hr = to_y(load_sample_image("flower.jpg"))
def pair(hr):
    hr = hr[:hr.shape[0] // 2 * 2, :hr.shape[1] // 2 * 2]; lr = cv2.resize(hr, (hr.shape[1] // 2, hr.shape[0] // 2), interpolation=cv2.INTER_AREA); return lr, hr
rng = np.random.default_rng(0); L, Hh = [], []
for im in imgs:
    lr, hr = pair(im)
    for _ in range(300):
        y0, x0 = rng.integers(0, lr.shape[0] - 24), rng.integers(0, lr.shape[1] - 24); L.append(lr[y0:y0 + 24, x0:x0 + 24]); Hh.append(hr[2 * y0:2 * y0 + 48, 2 * x0:2 * x0 + 48])
L, Hh = (torch.tensor(np.array(a)[:, None], dtype=torch.float32) / 255 for a in (L, Hh)); up = lambda t: nn.functional.interpolate(t, scale_factor=2, mode="bicubic")
lr_t, hr_t = pair(test_hr); lr_ten = torch.tensor(lr_t, dtype=torch.float32)[None, None] / 255
score = lambda out: (psnr(hr_t, out, data_range=255), ssim(hr_t, out, data_range=255))
for name, interp in [("nearest", cv2.INTER_NEAREST), ("bicubic", cv2.INTER_CUBIC)]: print("  %-8s PSNR %.2f dB  SSIM %.3f" % ((name,) + score(cv2.resize(lr_t, hr_t.shape[::-1], interpolation=interp))))
class SRCNN(nn.Module):
    def __init__(self): super().__init__(); self.f = nn.Sequential(nn.Conv2d(1, 64, 9, padding=4), nn.ReLU(), nn.Conv2d(64, 32, 5, padding=2), nn.ReLU(), nn.Conv2d(32, 1, 5, padding=2))
    def forward(self, lr): b = up(lr); return b + self.f(b)                          # learn the residual detail
class ESPCN(nn.Module):
    def __init__(self): super().__init__(); self.f = nn.Sequential(nn.Conv2d(1, 64, 5, padding=2), nn.Tanh(), nn.Conv2d(64, 32, 3, padding=1), nn.Tanh(), nn.Conv2d(32, 4, 3, padding=1), nn.PixelShuffle(2))
    def forward(self, lr): return up(lr) + self.f(lr)
for name, m in [("SRCNN", SRCNN()), ("ESPCN", ESPCN())]:
    torch.manual_seed(0); opt = torch.optim.Adam(m.parameters(), 1e-3)
    for epoch in range(15):
        for idx in torch.randperm(len(L)).split(32): opt.zero_grad(); nn.functional.l1_loss(m(L[idx]), Hh[idx]).backward(); opt.step()
    with torch.no_grad(): out = (m(lr_ten)[0, 0].clamp(0, 1) * 255).numpy().astype(np.uint8)
    print("  %-8s PSNR %.2f dB  SSIM %.3f" % ((name,) + score(out)))
cv2.imwrite("sr_compare.png", np.hstack([cv2.resize(lr_t, hr_t.shape[::-1], interpolation=cv2.INTER_NEAREST)[100:250, 200:400], out[100:250, 200:400], hr_t[100:250, 200:400]])); print("saved sr_compare.png (nearest | ESPCN | original)")
''')

X("m-speech-features",
  "Speech models don't usually read raw waveforms directly; they use time–frequency representations. A waveform is chopped into short overlapping frames, each turned into a spectrum (FFT); a **mel spectrogram** warps frequencies to match human hearing, and **MFCCs** compress it further. These are the 'images' that speech CNNs and transformers (Whisper) consume.",
  """**Pipeline.** Sample at 16 kHz → pre-emphasis → frames of 25 ms (400 samples) every 10 ms (160 samples), Hann window → |FFT|² power spectrum (n_fft 512 → 257 bins) → **mel filterbank** (e.g. 80 triangular filters, mel(f) = 2595·log₁₀(1 + f/700)) → log → **log-mel spectrogram** (Whisper input: 80 bins × 3,000 frames = 30 s). **MFCC** = DCT of log-mel → keep first 13 coefficients (decorrelated, compact; classic for GMM-HMM). Plus deltas (velocity), energy, zero-crossing rate, pitch (f0 via YIN/pYIN). **Nyquist:** you can only represent frequencies up to sample_rate/2. Augmentation: SpecAugment (mask time/frequency bands), speed/pitch perturbation, noise.""",
  """**Frame arithmetic.** 11 s of audio at 16 kHz = 176,000 samples; hop 160 → 176,000/160 + 1 = **1,101 frames**; each log-mel frame has 80 numbers → 88,080 values. **Mel by hand:** 1,000 Hz → 2595·log₁₀(1 + 1000/700) = 2595·0.385 = **1,000 mel** (by design); 4,000 Hz → 2,146 mel — high frequencies get compressed.""",
  ["Mismatched sample rates between training and inference", "Forgetting the log (huge dynamic range)", "Leaking speaker identity across train/test splits", "Too-short FFT windows for pitch analysis"],
  ["Speech recognition, speaker ID, keyword spotting, emotion/music analysis"], ["End-to-end models that learn from raw waveforms (wav2vec 2.0) — but they still benefit from this understanding"],
  "A real speech clip (John F. Kennedy's 'ask not what your country can do for you', 11 s, from the Whisper repository) — waveform statistics, STFT by hand vs librosa, mel filterbank, log-mel spectrogram, MFCCs + deltas, pitch track and voice-activity segments; saves a spectrogram figure.",
  ["Load audio at 16 kHz; duration and loudness (RMS)", "Frame + window + FFT by hand; compare with librosa.stft", "80-band log-mel spectrogram (Whisper-style)", "13 MFCCs + deltas; pitch with pYIN", "Voice-activity segments from energy; save figure"],
  f'''
import matplotlib; matplotlib.use("Agg")
import io, urllib.request, librosa, librosa.display, matplotlib.pyplot as plt, numpy as np, soundfile as sf
wav, sr0 = sf.read(io.BytesIO(urllib.request.urlopen("{JFK}").read())); wav = wav.mean(1) if wav.ndim > 1 else wav; y = librosa.resample(wav.astype(np.float32), orig_sr=sr0, target_sr=16000); sr = 16000
print(f"audio: {{len(y)}} samples @ {{sr}} Hz = {{len(y) / sr:.2f}} s | peak {{np.abs(y).max():.2f}} | RMS {{np.sqrt(np.mean(y ** 2)):.3f}}")
n_fft, hop = 400, 160; win = np.hanning(n_fft + 1)[:-1]; frame = y[16000:16000 + n_fft] * win
mine = np.abs(np.fft.rfft(frame)); lib = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop, window="hann", center=False))[:, 16000 // hop]
print("hand FFT matches librosa.stft:", np.allclose(mine, lib, atol=1e-3), "| bins:", len(mine), "| frequency resolution", sr / n_fft, "Hz")
mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft, hop_length=hop, n_mels=80); logmel = np.log10(np.maximum(mel, 1e-10))
print("log-mel spectrogram:", logmel.shape, "(80 mel bands x frames) | mel(1000 Hz) =", round(2595 * np.log10(1 + 1000 / 700)))
mfcc = librosa.feature.mfcc(S=librosa.power_to_db(mel), n_mfcc=13); d1 = librosa.feature.delta(mfcc); print("MFCC + delta features:", np.vstack([mfcc, d1]).shape)
f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=300, sr=sr, frame_length=1024, hop_length=hop); print(f"median pitch {{np.nanmedian(f0):.0f}} Hz | voiced frames {{np.mean(voiced):.0%}}")
rms = librosa.feature.rms(y=y, frame_length=n_fft, hop_length=hop)[0]; speech = rms > 0.3 * rms.mean()
edges = np.flatnonzero(np.diff(speech.astype(int))); segs = [(round(float(a) * hop / sr, 2), round(float(b) * hop / sr, 2)) for a, b in zip(edges[::2], edges[1::2]) if (b - a) * hop / sr > 0.2]
print("speech segments (s):", segs[:8])
fig, ax = plt.subplots(2, 1, figsize=(10, 5)); ax[0].plot(np.arange(len(y)) / sr, y, lw=0.5); ax[0].set_title("waveform")
librosa.display.specshow(librosa.power_to_db(mel, ref=np.max), sr=sr, hop_length=hop, x_axis="time", y_axis="mel", ax=ax[1]); ax[1].set_title("log-mel spectrogram"); fig.tight_layout(); fig.savefig("speech_features.png"); print("saved speech_features.png")
''')

X("m-speech-recognition",
  "Automatic speech recognition (ASR) converts audio to text. Classic systems chained acoustic models (GMM/DNN-HMM), pronunciation lexicons and n-gram language models; modern systems are end-to-end neural networks trained with **CTC**, **RNN-Transducer** or **attention encoder–decoders** — e.g. OpenAI **Whisper**, trained on 680k hours of multilingual audio, which also translates and timestamps.",
  """**Approaches.** **CTC:** the network outputs a distribution over characters + a blank at each frame; P(text) sums over all alignments that collapse (merge repeats, drop blanks) to the text — computed with dynamic programming; decoding greedy or beam search + language model. **RNN-T:** adds a prediction network for streaming. **Attention encoder–decoder (Whisper):** log-mel → transformer encoder → decoder generates tokens autoregressively, with special tokens for language, task and timestamps; 30-second windows, long audio chunked. **Evaluation:** Word Error Rate WER = (S + D + I)/N from the edit-distance alignment; CER for character-based languages. Fine-tune on domain audio/accents; add a vocabulary prompt for names and jargon.""",
  """**WER by hand.** Reference 'ask not what your country can do for you' (9 words); hypothesis 'ask what your country can do for you too' → 1 deletion ('not') + 1 insertion ('too') = 2 errors → WER = 2/9 = **22.2%**. **CTC collapse:** frames 'a a _ s s _ k' → merge repeats 'a _ s _ k' → drop blanks → **'ask'**.""",
  ["Comparing WER without the same text normalisation (case, punctuation, numbers)", "Feeding 44.1 kHz audio to a 16 kHz model", "Ignoring hallucinations on silence/noise (Whisper)", "Evaluating on speakers seen in fine-tuning"],
  ["Transcription, captions, voice interfaces, call analytics, meeting notes"], ["Sensitive recordings without consent; high-stakes legal transcripts without human review"],
  "The JFK speech clip transcribed with Whisper (tiny and base, via Hugging Face in Colab): text normalisation, WER computed by hand with edit distance and with jiwer, word-level timestamps, a CTC collapse function, and a noisy-audio robustness test.",
  ["Load and resample the audio to 16 kHz", "Transcribe with whisper-tiny and whisper-base", "Normalise text; WER by dynamic programming (S/D/I) and jiwer", "Word timestamps", "Add noise at 5 dB SNR and re-measure WER"],
  f'''
import io, re, urllib.request, librosa, numpy as np, soundfile as sf
from transformers import pipeline
wav, sr0 = sf.read(io.BytesIO(urllib.request.urlopen("{JFK}").read())); wav = wav.mean(1) if wav.ndim > 1 else wav; audio = librosa.resample(wav.astype(np.float32), orig_sr=sr0, target_sr=16000)
REF = "And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country."
norm = lambda s: re.sub(r"[^a-z' ]", "", s.lower()).split()
def wer(ref, hyp):
    r, h = norm(ref), norm(hyp); D = np.zeros((len(r) + 1, len(h) + 1), int); D[:, 0] = range(len(r) + 1); D[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1): D[i, j] = min(D[i - 1, j] + 1, D[i, j - 1] + 1, D[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return D[-1, -1] / len(r)
def ctc_collapse(frames, blank="_"):
    out, prev = [], None
    for f in frames:
        if f != prev and f != blank: out.append(f)
        prev = f
    return "".join(out)
print("CTC collapse of 'aa_ss_k':", ctc_collapse("aa_ss_k"), "| hand WER example:", round(wer("ask not what your country can do for you", "ask what your country can do for you too"), 3))
noise = np.random.default_rng(0).normal(0, 1, len(audio)).astype(np.float32); noisy = audio + noise * np.sqrt(np.mean(audio ** 2) / 10 ** (5 / 10)) / noise.std()
for size in ["tiny", "base"]:
    asr = pipeline("automatic-speech-recognition", model=f"openai/whisper-{{size}}")              # downloads from Hugging Face (works in Colab)
    out = asr({{"raw": audio, "sampling_rate": 16000}}, return_timestamps="word"); noisy_out = asr({{"raw": noisy, "sampling_rate": 16000}})
    print(f"whisper-{{size}}: '{{out['text'].strip()}}' | WER {{wer(REF, out['text']):.1%}} | at 5 dB SNR {{wer(REF, noisy_out['text']):.1%}}")
    print("  first word timestamps:", [(c["text"].strip(), c["timestamp"]) for c in out["chunks"][:4]])
try:
    import jiwer; print("jiwer WER (same normalisation):", round(jiwer.wer(" ".join(norm(REF)), " ".join(norm(out["text"]))), 3))
except ImportError:
    print("pip install jiwer to cross-check WER")
''', net=True)
