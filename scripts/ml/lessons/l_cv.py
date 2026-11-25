"""Beginner lessons: Computer vision & speech."""
from lesson_util import L

L("m-cv-overview",
  "Computer vision lets machines understand images and video: name what's there, find and outline objects, read text, track motion, even create images.",
  """Vision is in phones (face unlock, photo search), cars (lane and pedestrian detection), hospitals (scan analysis), shops (shelf monitoring) and factories (defect detection). Knowing the task types tells you which model and labels you need.""",
  """The main tasks, from simplest to hardest:

| Task | Output | Example |
| --- | --- | --- |
| Classification | one label for the image | "cat" |
| Detection | a box + label for each object | 3 cars, 1 person with boxes |
| Semantic segmentation | a class for every pixel | road / sky / car pixels |
| Instance segmentation | a mask per object | car #1, car #2 separately |
| OCR | text in the image | number plate "TN 09 AB 1234" |
| Tracking / action recognition | objects over time / what's happening | "person running" |
| Generation | a new image | text-to-image |

A typical pipeline: **collect and label images → preprocess (resize, normalise) → augment → train (usually fine-tune a pretrained model) → evaluate (accuracy, mAP, IoU) → deploy (often on a phone or edge device)**.""",
  [("Pick the task",
    """A parking app needs to know how many cars are in each photo and where: **object detection** (boxes), not classification."""),
   ("Labels cost",
    """A classification label takes ~1 second per image. A box ~10 seconds per object. A pixel mask can take minutes. The task you choose decides the labelling budget.""")],
  ("A dermatology app must outline the exact border of a skin lesion. Which task?",
   "Segmentation (semantic, or instance if there are several lesions)."),
  [("Classification", "one label per image"),
   ("Bounding box", "a rectangle around an object: x, y, width, height"),
   ("Mask", "a per-pixel yes/no for an object or class"),
   ("Pretrained model", "a network already trained on a big image dataset")],
  """Image classification end to end on the bundled digits images: load, look at one image as numbers, train, evaluate.""",
  r'''from sklearn.datasets import load_digits
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

digits = load_digits()
print(digits.images[0].astype(int))                 # an image is just a grid of numbers (8x8, values 0-16)
X = digits.images.reshape(len(digits.images), -1)    # flatten each image to 64 numbers
Xtr, Xte, ytr, yte = train_test_split(X, digits.target, random_state=0)
clf = SVC(gamma=0.001).fit(Xtr, ytr)
print("classification accuracy:", round(clf.score(Xte, yte), 3))''',
  [("What is the difference between detection and segmentation?", "Detection outputs boxes; segmentation labels every pixel."),
   ("Which task reads a number plate?", "OCR (optical character recognition), usually after detecting the plate.")])

L("m-image-basics",
  "A digital image is a grid of numbers: height × width for grayscale, with 3 colour channels for colour. Vision code starts by loading, resizing and normalising it.",
  """Every vision bug you'll hit early (wrong colours, wrong shapes, a model that sees nothing) comes from these basics: channel order, value ranges and image sizes.""",
  """- A **pixel** is one point. Grayscale: one number, usually 0 (black) to 255 (white).
- Colour: three numbers per pixel, **red, green, blue (RGB)**. Shape **(height, width, 3)**.
- **OpenCV** loads images as **BGR** (blue first). PIL and most models expect RGB, so convert.
- PyTorch models expect **(channels, height, width)**; NumPy/PIL use (height, width, channels).
- Before a model: **resize** to the expected size (e.g. 224 × 224), scale values to 0–1, and often **normalise** each channel: (value − mean) / std.
- Other colour spaces: **grayscale** (one channel), **HSV** (hue, saturation, value: good for colour-based rules like "find red objects").""",
  [("Pixels by hand",
    """A red pixel is (255, 0, 0); white is (255, 255, 255); dark grey is (50, 50, 50). Grayscale from RGB ≈ 0.299R + 0.587G + 0.114B, so pure red becomes **76**."""),
   ("Memory",
    """A 1920 × 1080 colour photo has 1920 × 1080 × 3 ≈ **6.2 million** numbers. That's why models resize to 224 × 224 (150,528 numbers).""")],
  ("An image array has shape (480, 640, 3). What are its height, width and channels? What shape does PyTorch want?",
   "Height 480, width 640, 3 channels. PyTorch wants (3, 480, 640), plus a batch dimension: (1, 3, 480, 640)."),
  [("Pixel", "one point in the image grid"),
   ("Channel", "one colour layer (R, G or B)"),
   ("BGR", "OpenCV's channel order: blue, green, red"),
   ("Normalisation", "rescaling pixel values, e.g. to mean 0 and std 1 per channel")],
  """Make a small colour image with NumPy, convert it to grayscale, resize it with PIL, and prepare it for PyTorch.""",
  r'''import numpy as np
from PIL import Image

img = np.zeros((4, 6, 3), dtype=np.uint8)          # height 4, width 6, RGB
img[:, :3] = [255, 0, 0]                           # left half red
img[:, 3:] = [0, 0, 255]                           # right half blue
gray = (0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]).astype(int)
print("grayscale values:", gray[0])                # red -> 76, blue -> 29

big = np.array(Image.fromarray(img).resize((12, 8)))   # PIL size is (width, height)
print("resized shape:", big.shape)                      # (8, 12, 3)
bgr = img[..., ::-1]                                    # what OpenCV would store
x = (big / 255.0).transpose(2, 0, 1)[None]             # 0..1, channels first, batch dim
print("model input shape:", x.shape)                    # (1, 3, 8, 12)''',
  [("Why do colours look swapped when you show an OpenCV image with matplotlib?", "OpenCV uses BGR order and matplotlib expects RGB."),
   ("What two steps usually happen before feeding an image to a pretrained model?", "Resize to its input size and normalise the pixel values the way it was trained.")])

L("m-image-features",
  "Before deep learning, vision used hand-designed features (edges, gradient histograms, keypoints, textures, colour histograms); they're still handy for small data and fast matching.",
  """These features still run inside document scanners, panorama stitching, AR tracking and simple industrial checks, and they explain what the first layers of a CNN learn.""",
  """- **Edges**: where brightness changes sharply. The **Sobel** filter measures the change horizontally and vertically; **Canny** cleans this up into thin edge lines.
- **HOG** (histogram of oriented gradients): split the image into small cells and, in each, count which directions the edges point. Good for shapes like people.
- **Keypoints and descriptors (SIFT, ORB)**: find distinctive corners/blobs and describe each one so it can be matched in another photo, even rotated or scaled. Used for stitching and object matching.
- **LBP** (local binary patterns): compare each pixel with its neighbours to describe texture.
- **Colour histograms**: how much of each colour appears; simple and robust to position.""",
  [("Sobel by hand",
    """A 3 × 3 patch with a dark left side and bright right side: [[10, 10, 200], [10, 10, 200], [10, 10, 200]]. The horizontal Sobel filter [[−1, 0, 1], [−2, 0, 2], [−1, 0, 1]] gives (200 − 10) + 2(200 − 10) + (200 − 10) = **760**: a strong vertical edge."""),
   ("A colour histogram",
    """A photo with 70% blue pixels and 20% sand-coloured pixels is probably a beach; the histogram doesn't care where those pixels are.""")],
  ("Which feature family would you use to stitch two overlapping photos into a panorama?",
   "Keypoints with descriptors (SIFT or ORB), matched between the two photos."),
  [("Gradient", "how fast brightness changes, and in which direction"),
   ("Edge", "a line of strong brightness change"),
   ("Keypoint / descriptor", "a distinctive point / a vector describing its surroundings"),
   ("HOG", "histograms of edge directions in small cells")],
  """Sobel edges computed with SciPy, and HOG-style features (edge-direction histograms) used to classify digits.""",
  r'''import numpy as np
from scipy import ndimage
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

patch = np.array([[10, 10, 200]] * 3, float)
print("Sobel response at the centre:", ndimage.sobel(patch, axis=1)[1, 1])   # strong vertical edge

def hog_like(img, bins=8):                    # edge-direction histogram per 4x4 cell
    gx, gy = ndimage.sobel(img, axis=1), ndimage.sobel(img, axis=0)
    mag, ang = np.hypot(gx, gy), np.arctan2(gy, gx) % np.pi
    feats = []
    for i in (0, 4):
        for j in (0, 4):
            h, _ = np.histogram(ang[i:i+4, j:j+4], bins=bins, range=(0, np.pi), weights=mag[i:i+4, j:j+4])
            feats.extend(h)
    return feats

digits = load_digits()
F = np.array([hog_like(im) for im in digits.images])        # 4 cells x 8 bins = 32 features
print("accuracy with edge-direction features:", cross_val_score(LogisticRegression(max_iter=3000), F, digits.target, cv=5).mean().round(3))''',
  [("What does a Sobel filter measure?", "The brightness gradient (change) in one direction, highlighting edges."),
   ("When are hand-crafted features still a good choice?", "Very little data, tight compute limits, or geometric matching tasks like stitching.")])

L("m-cnn-architectures",
  "Each famous CNN added one idea: AlexNet (deep + GPU), VGG (small filters, deep), Inception (several filter sizes), ResNet (skip connections), MobileNet/EfficientNet (efficiency), ViT (transformers for images).",
  """You'll pick a pretrained backbone for almost every vision project, and interviewers ask why ResNet works or which model to use on a phone. Each architecture's key idea answers that.""",
  """| Model (year) | Key idea | Why it mattered |
| --- | --- | --- |
| AlexNet (2012) | deep CNN trained on GPUs, ReLU, dropout | started the deep learning boom |
| VGG (2014) | only 3 × 3 filters, stacked deep | simple and uniform; very heavy |
| Inception / GoogLeNet (2014) | parallel 1 × 1, 3 × 3, 5 × 5 filters | multi-scale features, fewer weights |
| ResNet (2015) | skip connections: out = F(x) + x | trains 50–150+ layers |
| MobileNet (2017) | depthwise-separable convolutions | runs on phones |
| EfficientNet (2019) | scale depth, width and resolution together | best accuracy per compute |
| ViT (2020) | split image into patches, use a transformer | strong with lots of data |
| ConvNeXt (2022) | modernised CNN borrowing transformer tricks | CNN accuracy back on par |

Rule of thumb: **ResNet-50** or **EfficientNet** as a strong default; **MobileNet** for phones; **ViT/ConvNeXt** when you have lots of data and compute.""",
  [("Why two 3 × 3 filters beat one 5 × 5",
    """Same receptive field (5 × 5). Weights per channel pair: 2 × 9 = **18** versus **25**, and you get an extra ReLU in between."""),
   ("Depthwise-separable savings",
    """A normal 3 × 3 conv from 64 to 128 channels: 3 × 3 × 64 × 128 = **73,728** weights. Depthwise (3 × 3 × 64 = 576) + pointwise 1 × 1 (64 × 128 = 8,192) = **8,768**, about 8× fewer.""")],
  ("Which architecture would you start with for an app that must run on a cheap Android phone?",
   "MobileNet (or a small EfficientNet), designed for efficiency."),
  [("Backbone", "the main feature-extracting network, reused for many tasks"),
   ("Skip / residual connection", "adding a block's input to its output"),
   ("Depthwise-separable convolution", "a per-channel filter followed by a 1 × 1 channel mixer"),
   ("Patch", "a small square of the image, a 'word' for a vision transformer")],
  """Build famous architectures from torchvision without downloading weights, and compare their sizes; then a residual block by hand.""",
  r'''import torch, torch.nn as nn
from torchvision import models

for name, ctor in [("vgg16", models.vgg16), ("resnet50", models.resnet50),
                   ("mobilenet_v3_small", models.mobilenet_v3_small), ("efficientnet_b0", models.efficientnet_b0)]:
    m = ctor(weights=None)                                 # architecture only, random weights
    print(f"{name:20s} {sum(p.numel() for p in m.parameters()) / 1e6:6.1f} M parameters")

class Residual(nn.Module):                                 # the ResNet idea in 5 lines
    def __init__(self, c):
        super().__init__(); self.f = nn.Sequential(nn.Conv2d(c, c, 3, padding=1), nn.ReLU(), nn.Conv2d(c, c, 3, padding=1))
    def forward(self, x):
        return torch.relu(self.f(x) + x)                   # skip connection
print(Residual(16)(torch.randn(1, 16, 32, 32)).shape)''',
  [("What problem did ResNet's skip connections solve?", "Training very deep networks, by letting gradients flow back through the identity path."),
   ("What makes MobileNet efficient?", "Depthwise-separable convolutions, which need far fewer weights and multiplications.")])

L("m-transfer-learning",
  "Transfer learning starts from a model already trained on a huge dataset and adapts it to your task, so a few hundred examples can be enough.",
  """It's how almost all real vision and NLP projects are done: you rarely have millions of labelled images, but someone has already trained on ImageNet. This is the first thing interviewers expect you to propose for a small-data vision problem.""",
  """A pretrained network's early layers already detect edges, textures and shapes that are useful for nearly any image. So:

1. **Load a pretrained model** (e.g. ResNet-50 trained on ImageNet).
2. **Replace the last layer** (the "head") with a new one sized for your classes.
3. **Feature extraction**: freeze all the pretrained layers and train only the new head. Fast; good with very little data.
4. **Fine-tuning**: then unfreeze some or all layers and train with a **small learning rate** (e.g. 1e-4) so you adjust, not destroy, what was learned.
5. Use the same preprocessing (resize, normalisation) the model was trained with.""",
  [("How much data",
    """From scratch, a good dog-breed classifier might need 100,000+ images. Fine-tuning a pretrained model can reach good accuracy with **~100 images per breed**."""),
   ("Trainable parameters",
    """ResNet-50 has about 25 million weights. Frozen, with a new 2048 → 5 head, you train only 2048 × 5 + 5 = **10,245**.""")],
  ("You have 300 X-ray images in 3 classes. Train from scratch or fine-tune? Which layers do you train first?",
   "Fine-tune a pretrained model: first freeze the backbone and train the new head, then optionally unfreeze the top layers with a small learning rate."),
  [("Pretrained", "already trained on a large dataset"),
   ("Head", "the final layer(s), replaced for the new task"),
   ("Freeze", "keep a layer's weights fixed during training"),
   ("Fine-tuning", "continuing training of pretrained layers with a small learning rate")],
  """The real recipe: an ImageNet-pretrained ResNet-18 with a new head, trained on only 500 CIFAR-10 photos, versus the same network from scratch. It downloads the weights and the data, so run it in Colab (a GPU makes it take about two minutes).""",
  r'''import torch, torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader, Subset

device = "cuda" if torch.cuda.is_available() else "cpu"
weights = models.ResNet18_Weights.DEFAULT
prep = weights.transforms()                                  # the resize + normalisation it was trained with
train = Subset(datasets.CIFAR10("data", train=True, download=True, transform=prep), range(500))   # tiny dataset
test = Subset(datasets.CIFAR10("data", train=False, download=True, transform=prep), range(1000))

def run(pretrained):
    model = models.resnet18(weights=weights if pretrained else None)
    if pretrained:
        for p in model.parameters(): p.requires_grad = False   # freeze the backbone
    model.fc = nn.Linear(model.fc.in_features, 10)            # new head for 10 classes (always trainable)
    model = model.to(device)
    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=1e-3)
    for epoch in range(5):
        model.train()
        for x, y in DataLoader(train, batch_size=32, shuffle=True):
            x, y = x.to(device), y.to(device)
            opt.zero_grad(); nn.functional.cross_entropy(model(x), y).backward(); opt.step()
    model.eval(); correct = 0
    with torch.no_grad():
        for x, y in DataLoader(test, batch_size=100):
            correct += (model(x.to(device)).argmax(1).cpu() == y).sum().item()
    return correct / len(test)

print("pretrained + new head:", run(True))    # typically around 0.75-0.85
print("from scratch         :", run(False))   # typically around 0.25-0.35''',
  [("Why use a small learning rate when fine-tuning?", "To adjust the pretrained weights gently instead of overwriting useful features."),
   ("What is replaced when you adapt a pretrained classifier to new classes?", "The final classification layer (the head).")],
  net=True)

L("m-augmentation",
  "Augmentation makes realistic variations of training examples (flips, crops, colour changes; noise and speed for audio; synonyms for text) so the model learns what shouldn't matter.",
  """It's one of the cheapest and strongest ways to reduce overfitting, especially with small datasets. Choosing the right augmentations (and avoiding wrong ones) shows real understanding.""",
  """Each training epoch, apply random changes that **don't change the label**:

- **Images**: horizontal flip, random crop and resize, small rotation, brightness/contrast/colour jitter, blur, cutout (erase a patch), mixup/cutmix (blend two images and their labels).
- **Audio**: add background noise, shift in time, change speed or pitch slightly, mask frequency bands (SpecAugment).
- **Text**: synonym replacement, back-translation (translate to another language and back), random word dropout.

Only augment the **training** data. And don't use changes that alter the meaning: flipping a "6" vertically makes a "9"; flipping a road sign mirror-image may change it.""",
  [("Effective dataset size",
    """1,000 images × 10 random augmentations each epoch, for 30 epochs: the model sees 30,000 slightly different images instead of the same 1,000 thirty times."""),
   ("A bad augmentation",
    """Digit recognition with random 180° rotation: a 6 becomes a 9 and the label is now wrong. Keep rotations small (±15°).""")],
  ("For a medical X-ray classifier, is a horizontal flip a safe augmentation?",
   "Often not: the heart is on a specific side, so flipping can create unrealistic images; small rotations and brightness changes are safer. Check with a domain expert."),
  [("Augmentation", "a random, label-preserving change to a training example"),
   ("Invariance", "the model's output not changing when something irrelevant changes"),
   ("Mixup / cutmix", "blending two examples and their labels"),
   ("SpecAugment", "masking time or frequency bands in audio spectrograms")],
  """A torchvision augmentation pipeline applied to one image, plus simple audio augmentations with NumPy.""",
  r'''import numpy as np, torch
from torchvision import transforms
from PIL import Image

img = Image.fromarray((np.random.default_rng(0).random((64, 64, 3)) * 255).astype(np.uint8))
augment = transforms.Compose([transforms.RandomResizedCrop(48, scale=(0.7, 1.0)),
                              transforms.RandomHorizontalFlip(), transforms.RandomRotation(15),
                              transforms.ColorJitter(brightness=0.3, contrast=0.3), transforms.ToTensor()])
batch = torch.stack([augment(img) for _ in range(4)])     # 4 different random versions of one image
print("augmented batch:", tuple(batch.shape))

audio = np.sin(2 * np.pi * 220 * np.arange(16000) / 16000)
noisy = audio + 0.05 * np.random.default_rng(1).normal(size=audio.size)   # add noise
shifted = np.roll(audio, 1600)                                               # shift by 0.1 s
print("audio variants:", noisy.shape, shifted.shape)''',
  [("Should you augment the test set?", "No (except deliberate test-time augmentation); evaluation must use real, unchanged data."),
   ("Why can random vertical flips hurt digit recognition?", "They can turn one digit into another (6 into 9), so the label becomes wrong.")])

L("m-object-detection",
  "Object detection outputs a box and a class for every object; IoU measures box overlap, NMS removes duplicate boxes, and mAP scores the whole detector.",
  """Detection powers self-driving perception, retail shelf counts, traffic cameras and medical lesion finding. IoU, NMS and mAP are asked about in almost every vision interview.""",
  """- A **bounding box** is (x1, y1, x2, y2). The model predicts many candidate boxes, each with a class and a confidence score.
- **IoU** (intersection over union) = area of overlap ÷ area of union. 1 = identical boxes, 0 = no overlap. A prediction usually counts as correct if IoU ≥ 0.5 with a true box.
- **NMS** (non-maximum suppression): sort boxes by confidence; keep the best; delete others of the same class that overlap it with IoU > a threshold (e.g. 0.5); repeat.
- **mAP**: for each class, compute average precision across recall levels (area under the precision–recall curve), then average over classes.

Families:
- **Two-stage** (Faster R-CNN): propose regions, then classify them. Accurate.
- **One-stage** (YOLO, SSD, RetinaNet): predict boxes on a grid in one pass. Fast, real-time.
- **Anchors**: preset box shapes the model adjusts. **DETR**: a transformer that predicts a set of boxes directly, no NMS.""",
  [("IoU by hand",
    """Box A (0, 0, 4, 4), area 16. Box B (2, 2, 6, 6), area 16. Overlap (2, 2, 4, 4) = 4. Union = 16 + 16 − 4 = 28. **IoU = 4/28 ≈ 0.14**: not a match."""),
   ("NMS by hand",
    """Three "car" boxes with scores 0.9, 0.8, 0.3. Box 2 overlaps box 1 with IoU 0.7 > 0.5 → removed. Box 3 overlaps box 1 with IoU 0.1 → kept (a second car). Result: **2 cars**.""")],
  ("Box A (0, 0, 2, 2) and box B (1, 0, 3, 2). What is their IoU?",
   "Overlap (1, 0, 2, 2) = 2; each box has area 4; union = 4 + 4 − 2 = 6; IoU = 2/6 ≈ 0.33."),
  [("Bounding box", "the rectangle around an object"),
   ("IoU", "overlap area divided by union area"),
   ("NMS", "removing duplicate boxes for the same object"),
   ("mAP", "mean average precision over classes"),
   ("Anchor", "a preset box shape the detector adjusts")],
  """IoU and NMS written from scratch, checked against torchvision's built-in NMS.""",
  r'''import torch
from torchvision.ops import nms, box_iou

def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
    return inter / (area(a) + area(b) - inter)

print("IoU:", round(iou((0, 0, 4, 4), (2, 2, 6, 6)), 3))            # 0.143

boxes = [(10, 10, 50, 50), (12, 12, 52, 52), (100, 100, 140, 140)]
scores = [0.9, 0.8, 0.3]
def my_nms(boxes, scores, thr=0.5):
    order, keep = sorted(range(len(boxes)), key=lambda i: -scores[i]), []
    while order:
        best = order.pop(0); keep.append(best)
        order = [i for i in order if iou(boxes[best], boxes[i]) <= thr]   # drop heavy overlaps
    return keep
print("my NMS keeps:", my_nms(boxes, scores))
print("torchvision :", nms(torch.tensor(boxes, dtype=torch.float), torch.tensor(scores), 0.5).tolist())''',
  [("What IoU threshold usually counts a detection as correct?", "0.5 (stricter benchmarks average over 0.5–0.95)."),
   ("Why is NMS needed?", "Detectors predict several overlapping boxes for one object; NMS keeps only the best one.")])

L("m-segmentation",
  "Segmentation labels every pixel: semantic gives each pixel a class, instance also separates individual objects, panoptic does both; U-Net, Mask R-CNN and SAM are the key models.",
  """Pixel-level outputs are needed for tumour outlines, road-area detection in cars, satellite land use and photo editing (background removal).""",
  """- **Semantic segmentation**: every pixel gets a class (road, car, sky). Two touching cars are one "car" region.
- **Instance segmentation**: a separate mask for each object (car 1, car 2).
- **Panoptic**: both: every pixel has a class, and countable things are also split into instances.

Models:
- **U-Net**: an encoder shrinks the image to capture context, a decoder grows it back to full size, and **skip connections** copy fine details from encoder to decoder. Standard in medical imaging.
- **Mask R-CNN**: a detector that also predicts a mask inside each box (instance segmentation).
- **SAM** (Segment Anything): a foundation model that outlines any object from a click or a box.

Metrics: **IoU** per class (also called the Jaccard index) and **Dice** = 2 × overlap / (size A + size B).""",
  [("Dice and IoU by hand",
    """True mask has 100 pixels, predicted mask 80, overlap 60. IoU = 60 / (100 + 80 − 60) = **0.50**. Dice = 2 × 60 / (100 + 80) = **0.67**."""),
   ("U-Net shapes",
    """Input 256 × 256 → encoder 128, 64, 32, 16 → decoder 32, 64, 128, 256. The output has one score per class for each of the 65,536 pixels.""")],
  ("Counting how many separate cells are in a microscope image: semantic or instance segmentation?",
   "Instance segmentation, because touching cells must be separated to be counted."),
  [("Mask", "a per-pixel yes/no map"),
   ("Semantic / instance / panoptic", "class per pixel / separate objects / both"),
   ("Dice coefficient", "2 × overlap ÷ total size of both masks"),
   ("Encoder–decoder with skips", "shrink for context, grow back with copied details (U-Net)")],
  """Dice and IoU on two masks, and a tiny U-Net-style network checked for the right output shape.""",
  r'''import numpy as np, torch, torch.nn as nn

truth = np.zeros((10, 10), bool); truth[2:8, 2:8] = True        # 36-pixel square
pred = np.zeros((10, 10), bool);  pred[3:9, 3:9] = True         # shifted by one pixel
inter = (truth & pred).sum()
print("IoU :", round(inter / (truth | pred).sum(), 3))
print("Dice:", round(2 * inter / (truth.sum() + pred.sum()), 3))

class TinyUNet(nn.Module):
    def __init__(self, classes=3):
        super().__init__()
        self.down = nn.Sequential(nn.Conv2d(3, 16, 3, padding=1), nn.ReLU())
        self.bottom = nn.Sequential(nn.MaxPool2d(2), nn.Conv2d(16, 32, 3, padding=1), nn.ReLU())
        self.up = nn.ConvTranspose2d(32, 16, 2, stride=2)                # grow back to full size
        self.out = nn.Conv2d(32, classes, 1)                              # 32 = 16 (skip) + 16 (up)
    def forward(self, x):
        d = self.down(x)
        u = self.up(self.bottom(d))
        return self.out(torch.cat([u, d], dim=1))                         # skip connection: copy details
print("per-pixel class scores:", tuple(TinyUNet()(torch.randn(1, 3, 64, 64)).shape))   # (1, 3, 64, 64)''',
  [("What do U-Net's skip connections provide?", "Fine spatial details from the encoder, so the output masks have sharp edges."),
   ("Which metric is 2 × overlap ÷ (size A + size B)?", "The Dice coefficient.")])

L("m-video",
  "Video is a sequence of images over time; models must capture both what is in each frame and how things move, while coping with huge amounts of data.",
  """CCTV analytics, sports tracking, video moderation and driver monitoring all need video understanding. The core challenges, motion and cost, shape every design choice.""",
  """- A video is **frames** at some rate (e.g. 30 frames per second). One minute at 1080p is 1,800 images.
- **Sampling**: models rarely look at every frame; take, say, 8–16 frames spread over a clip.
- **Motion**:
  - **Frame differencing**: subtract consecutive frames; changed pixels = movement. Simple motion detection.
  - **Optical flow**: for each pixel, estimate how far it moved between frames (a small arrow per pixel).
- **Tracking**: detect objects in each frame, then link detections across frames (e.g. with IoU matching and a Kalman filter, as in SORT/DeepSORT).
- **Action recognition**: 2-D CNN per frame + averaging, **3-D CNNs** (filters over height, width and time), two-stream networks (frames + optical flow), or **video transformers**.""",
  [("Frame differencing by hand",
    """A pixel is 50 in frame 1 and 52 in frame 2: change 2, ignore (noise). Another goes 50 → 180: change 130 > threshold 30 → **motion**."""),
   ("Data size",
    """10 seconds at 30 fps, 224 × 224 colour: 300 × 150,528 ≈ **45 million** numbers. Sampling 16 frames cuts it to 2.4 million.""")],
  ("How would you link 'person' detections across frames into one track?",
   "Match each new detection to the existing track with the highest IoU (or appearance similarity), optionally predicting motion with a Kalman filter."),
  [("Frame rate", "frames per second"),
   ("Optical flow", "per-pixel motion between frames"),
   ("Tracking", "following the same object across frames"),
   ("3-D convolution", "a filter that slides over space and time")],
  """A synthetic video of a moving square: detect motion by frame differencing and track the square's centre.""",
  r'''import numpy as np
frames = []
for t in range(5):                              # 5 frames, a 4x4 bright square moving right by 3 px each frame
    f = np.zeros((20, 30)); f[8:12, 2 + 3 * t: 6 + 3 * t] = 255; frames.append(f)

for t in range(1, len(frames)):
    moved = np.abs(frames[t] - frames[t - 1]) > 30          # frame differencing
    ys, xs = np.nonzero(frames[t])                           # simple "detection": bright pixels
    print(f"frame {t}: {moved.sum():2d} changed pixels, square centre at x={xs.mean():.1f}")''',
  [("What does optical flow estimate?", "How far and in which direction each pixel moved between frames."),
   ("Why do video models sample frames?", "Consecutive frames are very similar and full video is huge; sampling saves compute with little loss.")])

L("m-face-emotion",
  "Emotion recognition finds a face (or a voice), extracts features and classifies the expression; it chains detection, alignment and classification, and it's sensitive to bias and privacy.",
  """It appears in driver-drowsiness alerts, customer-experience analytics and accessibility tools, and it's a good example of a multi-stage pipeline. It also comes with real ethical limits that interviewers expect you to mention.""",
  """**From faces**:
1. **Detect** the face (a box), e.g. with a CNN detector.
2. **Align**: find landmarks (eyes, nose, mouth corners) and rotate/scale the face to a standard position.
3. **Classify** the expression (happy, sad, angry, surprised, neutral …) with a CNN fine-tuned on labelled faces (e.g. FER-2013).

**From speech**: extract features such as pitch, loudness (energy), speaking rate and MFCCs, then classify.

Caveats: expressions don't reliably reveal inner feelings, accuracy varies across ages, skin tones and cultures, and face data is sensitive personal data; get consent and test for bias.""",
  [("Pipeline shapes",
    """Photo 1280 × 720 → face box 180 × 180 → aligned and resized to 48 × 48 grayscale → CNN → 7 probabilities, e.g. happy 0.81."""),
   ("Speech cues",
    """Angry speech is often louder with higher, more varied pitch; sad speech slower, quieter and lower. Those become features.""")],
  ("Why align faces before classifying expressions?",
   "So eyes and mouth are always in the same place; the classifier then focuses on expression, not on head angle or position."),
  [("Face detection", "finding where faces are"),
   ("Landmarks", "key points like eye corners and mouth corners"),
   ("Alignment", "rotating and scaling a face to a standard pose"),
   ("Prosody", "the melody of speech: pitch, loudness, rhythm")],
  """Speech-emotion style classification on synthetic clips: compute pitch-like and energy features with NumPy, then classify "calm" vs "excited".""",
  r'''import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
rng = np.random.default_rng(0); sr = 8000

def clip(excited):
    f0 = rng.uniform(220, 320) if excited else rng.uniform(100, 160)       # pitch
    amp = rng.uniform(0.7, 1.0) if excited else rng.uniform(0.2, 0.5)       # loudness
    t = np.arange(sr) / sr
    return amp * np.sin(2 * np.pi * f0 * t) + 0.05 * rng.normal(size=sr)

def features(x):
    spectrum = np.abs(np.fft.rfft(x)); freqs = np.fft.rfftfreq(len(x), 1 / sr)
    return [freqs[spectrum.argmax()], np.sqrt(np.mean(x ** 2))]            # dominant pitch, RMS energy

y = np.array([0, 1] * 100)
X = np.array([features(clip(e)) for e in y])
print("example features (pitch Hz, energy):", X[:2].round(2))
print("accuracy:", cross_val_score(LogisticRegression(max_iter=1000), X / X.max(0), y, cv=5).mean())''',
  [("Name the three stages of a face-emotion pipeline.", "Detect the face, align it, classify the expression."),
   ("Name one ethical concern with emotion recognition.", "Bias across demographic groups, privacy/consent, or the false assumption that expressions reveal true feelings.")])

L("m-siamese",
  "A Siamese network passes two inputs through the same encoder and compares their embeddings, learning 'how similar' instead of fixed classes; good for faces, signatures and search.",
  """Face verification ("is this the same person?"), duplicate detection and image search must handle people and items the model never saw in training. Learning a similarity space does that; fixed classes can't.""",
  """- One **encoder** (shared weights) turns any input into an **embedding** vector.
- Compare two embeddings with a **distance** (Euclidean) or **cosine similarity**. Small distance = same identity.
- **Contrastive loss** (pairs): same-identity pairs should be close; different pairs at least a **margin** apart.
- **Triplet loss**: an anchor A, a positive P (same identity) and a negative N (different): loss = max(0, d(A, P) − d(A, N) + margin). It pushes P closer than N by at least the margin.
- At use time: store embeddings of known people; a new face matches the closest stored one if the distance is below a threshold. New people just need one reference photo, no retraining.""",
  [("Triplet loss by hand",
    """d(A, P) = 0.4, d(A, N) = 0.6, margin 0.5: loss = max(0, 0.4 − 0.6 + 0.5) = **0.3**: not yet separated enough. If d(A, N) = 1.2: loss = max(0, −0.3) = **0**: done."""),
   ("Verification",
    """Threshold 0.8. A new selfie is 0.35 from the stored ID photo → same person. 1.4 → different.""")],
  ("d(A, P) = 1.0, d(A, N) = 1.1, margin 0.2. What is the triplet loss?",
   "max(0, 1.0 − 1.1 + 0.2) = 0.1."),
  [("Embedding", "a vector representation of an input"),
   ("Shared weights", "both inputs go through the exact same network"),
   ("Margin", "the minimum gap wanted between positive and negative distances"),
   ("Verification vs identification", "'same person?' vs 'which person?'")],
  """Train an embedding with triplet loss on digits 0–6, then verify digits 7–9 that the network never saw.""",
  r'''import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
torch.manual_seed(0)
X, y = load_digits(return_X_y=True); X = torch.tensor(X / 16, dtype=torch.float32); y = torch.tensor(y)
enc = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 16))
opt = torch.optim.Adam(enc.parameters(), lr=1e-3)
seen = torch.nonzero(y < 7).ravel()

for step in range(1500):
    a = seen[torch.randint(len(seen), (128,))]
    p = torch.stack([seen[y[seen] == y[i]][torch.randint((y[seen] == y[i]).sum(), (1,))][0] for i in a])
    n = torch.stack([seen[y[seen] != y[i]][torch.randint((y[seen] != y[i]).sum(), (1,))][0] for i in a])
    e = lambda idx: F.normalize(enc(X[idx]), dim=1)
    loss = F.triplet_margin_loss(e(a), e(p), e(n), margin=0.5)
    opt.zero_grad(); loss.backward(); opt.step()

new = torch.nonzero(y >= 7).ravel()[:300]                       # classes never seen in training
E = F.normalize(enc(X[new]), dim=1).detach(); d = torch.cdist(E, E); same = y[new][:, None] == y[new][None]
print("avg distance same digit:", d[same].mean().item().__round__(2), " different digit:", d[~same].mean().item().__round__(2))''',
  [("Why can a Siamese face system recognise a new employee without retraining?", "It only needs to store their embedding; matching uses distances, not fixed classes."),
   ("What does triplet loss push apart and pull together?", "Pulls the anchor and positive together; pushes the anchor and negative apart by at least the margin.")])

L("m-gan",
  "A GAN trains two networks against each other: a generator turns noise into fake samples, a discriminator tries to spot fakes, and both improve until fakes look real.",
  """GANs created the first photo-realistic generated faces, and are still used for super-resolution, image-to-image translation and data augmentation. The adversarial idea is a favourite interview topic.""",
  """- **Generator G**: takes random noise z and outputs a fake sample G(z) (e.g. an image).
- **Discriminator D**: takes a sample and outputs the probability that it's real.
- Training alternates:
  1. Train D to give real samples a high score and G's fakes a low score.
  2. Train G to make D score its fakes as real (to fool D).
- At the balance point, G's samples look like the real data and D can only guess.

Problems: unstable training, and **mode collapse** (G produces only a few kinds of output). Fixes include careful architectures (DCGAN), Wasserstein loss and spectral normalisation. Today, **diffusion models** have largely replaced GANs for image generation, but GANs remain fast at sampling.""",
  [("The game by hand",
    """Round 1: D scores real 0.9, fake 0.2 (easily spotted). G improves; round 50: real 0.6, fake 0.5. Near the end both ≈ 0.5: D can't tell them apart."""),
   ("Mode collapse",
    """Training on digits 0–9, G learns to make only perfect 1s. D is fooled for a while, but the output has no variety.""")],
  ("What does the discriminator output at the ideal end of training?",
   "About 0.5 for every input: it can't tell real from fake."),
  [("Generator", "turns random noise into samples"),
   ("Discriminator", "classifies samples as real or fake"),
   ("Adversarial", "two models trained against each other"),
   ("Mode collapse", "the generator producing only a few kinds of output")],
  """A tiny GAN that learns to generate numbers from a bell curve centred at 4 (starting from noise centred at 0).""",
  r'''import torch, torch.nn as nn
torch.manual_seed(0)
real = lambda n: 4 + 1.25 * torch.randn(n, 1)                         # target data: mean 4, std 1.25
G = nn.Sequential(nn.Linear(4, 32), nn.LeakyReLU(0.2), nn.Linear(32, 1))   # 4 noise numbers -> 1 sample
D = nn.Sequential(nn.Linear(1, 32), nn.LeakyReLU(0.2), nn.Linear(32, 1))   # sample -> real/fake score
optG = torch.optim.Adam(G.parameters(), 1e-3, betas=(0.5, 0.999))
optD = torch.optim.Adam(D.parameters(), 1e-3, betas=(0.5, 0.999))
bce = nn.BCEWithLogitsLoss()

for step in range(4000):
    x, z = real(128), torch.randn(128, 4)
    lossD = bce(D(x), torch.ones(128, 1)) + bce(D(G(z).detach()), torch.zeros(128, 1))   # 1. train D
    optD.zero_grad(); lossD.backward(); optD.step()
    lossG = bce(D(G(z)), torch.ones(128, 1))                                              # 2. G tries to fool D
    optG.zero_grad(); lossG.backward(); optG.step()

fake = G(torch.randn(5000, 4)).detach()     # started near 0; should now be centred close to 4
print(f"generated mean {fake.mean():.2f} (target 4), std {fake.std():.2f} (target 1.25)")''',
  [("What is the generator's training goal?", "To make the discriminator classify its fake samples as real."),
   ("What is mode collapse?", "The generator producing only a small variety of outputs.")])

L("m-super-resolution",
  "Image restoration recovers a clean or sharper image from a degraded one; networks learn the mapping from pairs of low-quality and high-quality images.",
  """Phone cameras, medical scans, satellite images, old-photo restoration and video streaming all use learned denoising and super-resolution.""",
  """- **Make training pairs**: take high-quality images and degrade them yourself (shrink, blur, add noise, compress). The network learns degraded → original.
- **Denoising**: remove noise while keeping edges.
- **Super-resolution (SR)**: produce a higher-resolution image, e.g. 2× or 4× more pixels per side.
  - **Baseline**: bicubic interpolation (smooth but blurry).
  - **SRCNN**: a small CNN that sharpens an upscaled image.
  - **SRGAN / ESRGAN**: add a GAN (adversarial) loss and a **perceptual loss** (compare deep features, not pixels) to produce realistic textures.
- **Metrics**: **PSNR** (pixel accuracy, in dB, higher is better) and **SSIM** (structural similarity, up to 1). Perceptually sharp GAN outputs can score lower PSNR than blurry ones, so also look at the images.""",
  [("Pixel counts",
    """4× super-resolution from 256 × 256 to 1024 × 1024: the model must invent 15 of every 16 pixels."""),
   ("PSNR by hand",
    """With pixel values 0–255 and mean squared error 100: PSNR = 10 × log₁₀(255² / 100) = 10 × log₁₀(650.25) ≈ **28.1 dB**.""")],
  ("Why can an ESRGAN image look sharper but have lower PSNR than a bicubic one?",
   "PSNR rewards matching pixels exactly; invented realistic textures don't match pixel-for-pixel, while blur stays 'safely' close on average."),
  [("Degradation", "the damage applied to create low-quality inputs"),
   ("Interpolation", "estimating new pixels from neighbours (bicubic)"),
   ("Perceptual loss", "comparing deep-network features instead of raw pixels"),
   ("PSNR / SSIM", "pixel-error and structure-similarity quality scores")],
  """A tiny SRCNN: learn to restore 8 × 8 digits from 4 × 4 versions, compared with plain upscaling, scored by PSNR.""",
  r'''import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
torch.manual_seed(0)
hi = torch.tensor(load_digits().images / 16, dtype=torch.float32).unsqueeze(1)     # (N, 1, 8, 8) originals
lo = F.avg_pool2d(hi, 2)                                                           # degrade: 4x4
up = F.interpolate(lo, scale_factor=2, mode="bicubic", align_corners=False)        # baseline upscaling

srcnn = nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, 16, 3, padding=1), nn.ReLU(), nn.Conv2d(16, 1, 3, padding=1))
opt = torch.optim.Adam(srcnn.parameters(), lr=1e-3)
tr, te = slice(0, 1500), slice(1500, None)
for step in range(800):
    opt.zero_grad(); loss = F.mse_loss(up[tr] + srcnn(up[tr]), hi[tr]); loss.backward(); opt.step()   # learn the missing detail

psnr = lambda a, b: (10 * torch.log10(1 / F.mse_loss(a, b))).item()
with torch.no_grad():
    print("bicubic PSNR:", round(psnr(up[te], hi[te]), 2), "dB   SRCNN PSNR:", round(psnr(up[te] + srcnn(up[te]), hi[te]), 2), "dB")''',
  [("How are training pairs usually made for super-resolution?", "By degrading high-quality images (downscale, blur, noise) and learning to undo it."),
   ("What does a perceptual loss compare?", "Features from a pretrained network rather than raw pixels.")])

L("m-speech-features",
  "Audio is a long list of air-pressure samples; turning it into time–frequency pictures (spectrograms, mel spectrograms, MFCCs) makes speech patterns visible to models.",
  """Speech recognition, voice assistants, music tagging and machine-sound monitoring all start by converting raw audio into these features. Most audio models are really image models on spectrograms.""",
  """- **Sampling**: audio is recorded as numbers many times per second. Speech is often **16,000 samples per second (16 kHz)**. By the Nyquist rule, the sample rate must be at least twice the highest frequency you want to keep.
- **Frames**: cut the audio into short overlapping windows, e.g. 25 ms every 10 ms.
- **Spectrogram**: apply a Fourier transform to each frame to see how loud each frequency is → a 2-D image (time × frequency).
- **Mel scale**: group frequencies the way human hearing does (fine detail at low pitches, coarse at high). A **mel spectrogram** usually has 40–128 mel bands, often on a log (dB) scale.
- **MFCCs**: a further compression of the log-mel spectrum into ~13 numbers per frame, a classic speech feature.""",
  [("Frame count",
    """1 second at 16 kHz = 16,000 samples. Frames of 400 samples (25 ms) every 160 samples (10 ms): about (16,000 − 400)/160 + 1 ≈ **98 frames**."""),
   ("Reading a frequency",
    """A pure 440 Hz tone (the note A) makes a bright horizontal line at 440 Hz across the whole spectrogram.""")],
  ("To keep frequencies up to 8 kHz, what is the minimum sample rate?",
   "16 kHz (twice the highest frequency)."),
  [("Sample rate", "audio measurements per second"),
   ("Spectrogram", "loudness of each frequency over time"),
   ("Mel scale", "a frequency scale matching human pitch perception"),
   ("MFCC", "compact coefficients summarising a frame's log-mel spectrum")],
  """A 1-second tone that jumps from 440 Hz to 880 Hz: compute its spectrogram with SciPy and find the loudest frequency in each half.""",
  r'''import numpy as np
from scipy.signal import spectrogram

sr = 16000
t = np.arange(sr) / sr
audio = np.where(t < 0.5, np.sin(2 * np.pi * 440 * t), np.sin(2 * np.pi * 880 * t))   # 440 Hz then 880 Hz

freqs, times, S = spectrogram(audio, fs=sr, nperseg=400, noverlap=240)   # 25 ms frames every 10 ms
print("spectrogram shape (frequencies x frames):", S.shape)
first, second = S[:, times < 0.5].mean(1), S[:, times > 0.5].mean(1)
print("loudest frequency, first half :", round(freqs[first.argmax()]), "Hz")
print("loudest frequency, second half:", round(freqs[second.argmax()]), "Hz")''',
  [("Why use the mel scale for speech?", "It spaces frequencies the way humans hear them, putting detail where speech information is."),
   ("What are the two axes of a spectrogram?", "Time and frequency (the value is loudness).")])

L("m-speech-recognition",
  "Speech recognition turns audio into text and text-to-speech does the reverse; modern systems are end-to-end networks such as wav2vec 2.0 and Whisper trained on huge amounts of audio.",
  """Voice search, call-centre transcription, captions and voice assistants depend on ASR. The CTC idea (how to align audio frames to letters without labelled timings) is a classic interview topic.""",
  """**ASR (speech → text)**:
- Input: audio or its mel spectrogram, ~100 frames per second. Output: characters or subword tokens, far fewer.
- **CTC** (connectionist temporal classification) solves the alignment problem: the model predicts a symbol or a special **blank** for every frame; decoding **merges repeats and removes blanks**. "hh_e_ll_ll_oo" → "hello".
- **wav2vec 2.0**: learns speech representations from unlabelled audio (self-supervised), then fine-tunes with CTC on a little labelled data.
- **Whisper**: an encoder–decoder transformer trained on 680,000 hours of multilingual audio; robust and can translate.
- Metric: **word error rate (WER)** = (substitutions + deletions + insertions) / number of words in the reference.

**TTS (text → speech)**: a model predicts a mel spectrogram from text (e.g. Tacotron, FastSpeech), and a **vocoder** (e.g. HiFi-GAN) turns it into a waveform.""",
  [("CTC decoding by hand",
    """Frame outputs: c c _ a a _ _ t t. Merge repeats → c _ a _ t. Remove blanks → **cat**. For a double letter you need a blank between: l _ l → "ll"."""),
   ("WER by hand",
    """Reference "turn on the lights" (4 words); output "turn the light". One deletion ("on") and one substitution ("lights" → "light"): WER = 2/4 = **50%**.""")],
  ("Decode with CTC: h h _ e _ l l _ l o o.",
   "Merge repeats: h _ e _ l _ l o; remove blanks: 'hello'."),
  [("ASR", "automatic speech recognition (speech to text)"),
   ("CTC blank", "a special 'no symbol' output used for alignment"),
   ("WER", "word error rate"),
   ("Vocoder", "turns a spectrogram into an audio waveform")],
  """CTC greedy decoding and word error rate written from scratch (Whisper itself needs a model download; see the note in the reference card).""",
  r'''def ctc_decode(frames, blank="_"):
    out, prev = [], None
    for s in frames:
        if s != prev and s != blank:      # keep a symbol only when it changes and isn't blank
            out.append(s)
        prev = s
    return "".join(out)

print(ctc_decode("cc_aa__tt"))           # cat
print(ctc_decode("hh_e_ll_lloo"))        # hello

def wer(ref, hyp):                       # edit distance on words
    r, h = ref.split(), hyp.split()
    d = [[i + j if i * j == 0 else 0 for j in range(len(h) + 1)] for i in range(len(r) + 1)]
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (r[i-1] != h[j-1]))
    return d[-1][-1] / len(r)
print("WER:", wer("turn on the lights", "turn the light"))   # 0.5''',
  [("What two steps turn CTC frame outputs into text?", "Merge repeated symbols, then remove blanks."),
   ("What does a vocoder do in text-to-speech?", "Converts the predicted spectrogram into an audio waveform.")])
