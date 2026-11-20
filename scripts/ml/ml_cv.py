"""Module 3: perception — images, speech, CNN architectures, transfer learning, detection, segmentation, video, Siamese nets, GANs."""
from ml_util import M

PRETRAINED = '''
def load_backbone():
    """Pretrained ImageNet weights in Colab/VS Code; random weights if offline (same code path)."""
    from torchvision.models import resnet18, ResNet18_Weights
    try:
        return resnet18(weights=ResNet18_Weights.DEFAULT), True
    except Exception:
        return resnet18(weights=None), False
'''

CV = [
M("m-cv-overview", "Computer vision: tasks, pipeline and where it's used", "Basic",
  "Computer vision lets machines understand images and video — classify them, find and outline objects, read text, track motion, and generate new images.",
  """|Task|Output|Typical models|
|Image classification|one label (or several) per image|ResNet, EfficientNet, ViT|
|Object detection|boxes + labels|YOLO, Faster R-CNN, DETR|
|Semantic / instance segmentation|label per pixel / mask per object|U-Net, DeepLab, Mask R-CNN, SAM|
|Keypoints / pose estimation|body/face landmarks|OpenPose, HRNet, MediaPipe|
|OCR|text in images|Tesseract, CRNN + CTC, TrOCR, vision-language models|
|Face detection / recognition|faces, identities|RetinaFace, ArcFace (Siamese/metric learning)|
|Tracking / video understanding|IDs over time, actions|ByteTrack, 3-D CNNs, video transformers|
|Image generation / editing|new images|GANs, diffusion models|
|Vision-language|captions, visual QA, zero-shot|CLIP, multimodal LLMs|

### Standard project pipeline
Collect and **label** images (bounding boxes/masks) → split by source (avoid near-duplicates across splits) → augment → **fine-tune a pretrained model** → evaluate (accuracy/F1, mAP, IoU) and inspect errors visually → optimise (quantise, export ONNX/TensorRT) → deploy (cloud API, edge device, phone) → monitor drift (new cameras, lighting).

### Applications
Medical imaging, manufacturing defect inspection, retail shelf analytics, agriculture (crop disease), self-driving, security, document processing, food recognition, satellite imagery.""",
  code='''
tasks = {"classification": "label", "detection": "boxes + labels", "segmentation": "pixel masks", "pose": "keypoints", "OCR": "text", "tracking": "IDs over frames"}
for t, out in tasks.items(): print(f"{t:15s} -> {out}")
''',
  say=[("How would you start a defect-detection project on a factory line?",
        "\"Clarify whether we need a pass/fail decision, the defect's location, or its exact outline — that decides classification, detection or segmentation — and the speed and false-reject tolerance. Collect images under consistent lighting, label defects with the quality team, and since defects are rare consider anomaly detection trained on good parts. Fine-tune a pretrained model with augmentation, evaluate recall on defects at an acceptable false-alarm rate, check Grad-CAM, then deploy on an edge GPU and monitor for lighting or camera changes.\"")]),
M("m-image-basics", "Digital images: pixels, channels, colour spaces, OpenCV and PIL", "Basic",
  "A digital image is a grid of numbers: height × width for grayscale, × 3 channels for colour. Everything in computer vision starts by loading, resizing and normalising these arrays.",
  """### Representation
- Pixel values 0–255 (uint8) → scale to [0, 1] floats, then normalise with dataset mean/std (ImageNet: mean [0.485, 0.456, 0.406], std [0.229, 0.224, 0.225]).
- **Channel order**: PIL/Matplotlib RGB; **OpenCV loads BGR**; PyTorch wants (C, H, W), TensorFlow (H, W, C).
- **Colour spaces**: RGB, grayscale, HSV (hue separate from brightness — good for colour thresholding), LAB, YCrCb (skin detection).

### Basic operations
Resize/crop (keep aspect ratio), rotate/flip, blur (Gaussian, median for salt-and-pepper noise), sharpen, threshold (Otsu), morphology (erode/dilate/open/close), histogram equalisation (contrast), edge detection (Sobel, Canny), contours, drawing boxes.

### Libraries
**OpenCV** (`cv2`, fast classic CV and video), **Pillow** (`PIL.Image`), **scikit-image**, **torchvision.transforms** / **Albumentations** for training pipelines, **imageio** for files.""",
  code="""
import numpy as np, cv2
from PIL import Image
img = np.zeros((120, 160, 3), np.uint8)                           # synthetic BGR image: blue sky, green ground, red sun
img[:80] = (230, 160, 60); img[80:] = (40, 160, 40); cv2.circle(img, (120, 35), 18, (40, 40, 230), -1)
print("shape (H, W, C):", img.shape, "dtype:", img.dtype)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
red_mask = cv2.inRange(hsv, (0, 120, 70), (10, 255, 255)) | cv2.inRange(hsv, (170, 120, 70), (180, 255, 255))
cnts, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
x, y, w, h = cv2.boundingRect(cnts[0]); print("red object bounding box (x, y, w, h):", (x, y, w, h))
edges = cv2.Canny(gray, 50, 150); print("edge pixels found by Canny:", int((edges > 0).sum()))
_, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU); print("Otsu threshold splits pixels into", np.unique(otsu).tolist())
small = cv2.resize(img, (80, 60), interpolation=cv2.INTER_AREA)
tensor = (rgb.astype(np.float32) / 255 - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
print("resized:", small.shape, " CHW tensor for PyTorch:", tensor.transpose(2, 0, 1).shape)
Image.fromarray(rgb).save("scene.png"); print("saved with PIL:", Image.open("scene.png").size)
""",
  say=[("What preprocessing do images need before going into a pretrained CNN?",
        "\"Convert to RGB in the channel order the model expects — OpenCV gives BGR — resize or crop to the input size the model was trained on, scale pixels to 0–1, normalise with the same mean and standard deviation used in pretraining, usually ImageNet's, and arrange as channels-first for PyTorch. Using the exact transforms that ship with the pretrained weights avoids silent accuracy loss.\"")]),

M("m-image-features", "Features for perception (images): edges, HOG, SIFT/ORB, LBP, colour histograms", "Intermediate",
  "Before deep learning, vision relied on hand-designed features — edges, gradient histograms, keypoints, textures. They're still useful for small data, fast pipelines and understanding what CNNs learn.",
  """|Feature|What it captures|Classic use|
|Colour histogram|distribution of colours|image retrieval, simple classification|
|Edges (Sobel, Canny)|intensity changes|shape, lane detection|
|HOG (histogram of oriented gradients)|local gradient directions in cells|pedestrian detection (HOG + SVM, Dalal & Triggs 2005)|
|SIFT / SURF / ORB keypoints + descriptors|distinctive corners/blobs invariant to scale/rotation|panorama stitching, object matching, SLAM|
|LBP (local binary patterns)|micro-texture|face recognition, texture classification|
|Haar features|rectangle brightness differences|Viola–Jones face detector (2001)|
|Gabor filters|oriented frequencies|texture; resemble CNN first-layer filters|

**Pipeline**: extract features → (bag of visual words / PCA) → classifier (SVM, random forest). Deep CNNs learn better features end-to-end, but classical features need little data and no GPU.""",
  code="""
import numpy as np, cv2
from skimage.feature import hog, local_binary_pattern
from sklearn.datasets import load_digits
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score

digits = load_digits(); imgs = digits.images
H = np.array([hog(im, orientations=8, pixels_per_cell=(4, 4), cells_per_block=(1, 1)) for im in imgs])
print("HOG feature length per digit:", H.shape[1])
print("raw pixels + linear SVM:", cross_val_score(LinearSVC(max_iter=5000), digits.data, digits.target, cv=3).mean().round(3))
print("HOG + linear SVM:       ", cross_val_score(LinearSVC(max_iter=5000), H, digits.target, cv=3).mean().round(3))

canvas = np.zeros((200, 200), np.uint8); cv2.rectangle(canvas, (40, 40), (120, 110), 255, -1); cv2.circle(canvas, (150, 150), 25, 180, -1)
M_ = cv2.getRotationMatrix2D((100, 100), 30, 1.0); rotated = cv2.warpAffine(canvas, M_, (200, 200))
orb = cv2.ORB_create(200); k1, d1 = orb.detectAndCompute(canvas, None); k2, d2 = orb.detectAndCompute(rotated, None)
matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2)
print(f"ORB keypoints {len(k1)} / {len(k2)}, matches found despite 30 degree rotation: {len(matches)}")
lbp = local_binary_pattern(imgs[0], P=8, R=1, method="uniform"); print("LBP texture histogram:", np.histogram(lbp, bins=10)[0])
""",
  say=[("What is HOG and why did it work for pedestrian detection?",
        "\"Histogram of oriented gradients divides the image into small cells and, in each, builds a histogram of edge directions weighted by gradient strength, normalised over blocks for lighting invariance. A person's silhouette has a characteristic pattern of edge orientations, so HOG plus a linear SVM in a sliding window detected pedestrians well — it was state of the art before CNNs.\"")]),

M("m-speech-features", "Features for perception (speech and audio): sampling, spectrograms, mel scale, MFCCs", "Intermediate",
  "Audio is a 1-D waveform. Converting it to time–frequency features — spectrograms, mel spectrograms, MFCCs — makes speech and sound patterns visible to models.",
  """### From sound to numbers
- **Sampling rate**: samples per second (speech 16 kHz, music 44.1 kHz). Nyquist: you capture frequencies up to half the rate.
- **Framing**: split into short overlapping windows (25 ms frames, 10 ms hop) — speech is roughly stationary within a frame.
- **STFT (short-time Fourier transform)** → **spectrogram**: energy per frequency per frame (magnitude, usually in dB).
- **Mel scale**: warps frequency to match human hearing (fine at low, coarse at high frequencies) → **mel spectrogram** (40–128 mel bands). The standard input for modern speech CNNs/transformers (Whisper uses 80/128 log-mel bands).
- **MFCCs (mel-frequency cepstral coefficients)**: log mel energies → discrete cosine transform → first 13 coefficients (+ deltas). Compact; classic for speech/speaker recognition with GMM-HMMs.
- Other features: zero-crossing rate, energy/RMS, pitch (F0), spectral centroid/rolloff, chroma (music).

### Augmentation
Noise, time shift, speed/pitch perturbation, room reverb, **SpecAugment** (mask time and frequency bands).

### Libraries
librosa, torchaudio, `scipy.signal`; pretrained encoders: wav2vec 2.0, HuBERT, Whisper.""",
  code="""
import numpy as np, librosa
sr = 16000; t = np.arange(int(0.8 * sr)) / sr
low = 0.5 * np.sin(2 * np.pi * 220 * t)                       # 'low voice' tone
high = 0.5 * np.sin(2 * np.pi * 880 * t) * np.exp(-3 * t)    # 'high, fading' tone
for name, y in [("220 Hz tone", low), ("880 Hz fading tone", high)]:
    S = np.abs(librosa.stft(y, n_fft=512, hop_length=160))
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=512, hop_length=160, n_mels=40)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=512, hop_length=160)
    peak_hz = librosa.fft_frequencies(sr=sr, n_fft=512)[S.mean(1).argmax()]
    print(f"{name:18s} spectrogram {S.shape}, log-mel {mel.shape}, MFCC {mfcc.shape}, peak ~{peak_hz:.0f} Hz, "
          f"centroid {librosa.feature.spectral_centroid(y=y, sr=sr).mean():.0f} Hz, RMS {librosa.feature.rms(y=y).mean():.3f}")
f0 = librosa.yin(low, fmin=80, fmax=1000, sr=sr); print("estimated pitch of the low tone:", round(float(np.median(f0)), 1), "Hz")
""",
  say=[("Why do speech models use mel spectrograms instead of raw audio?",
        "\"Raw audio has 16,000 samples a second and the information is in frequencies, not individual samples. A spectrogram shows how energy in each frequency changes over time, and the mel scale compresses high frequencies the way human hearing does, giving a compact image-like representation that CNNs and transformers learn from efficiently. Some models like wav2vec 2.0 do learn from raw waveforms, but with a convolutional front-end that effectively learns similar filters.\"")]),

M("m-cnn-architectures", "Beyond AlexNet: VGG, Inception, ResNet, MobileNet, EfficientNet, ConvNeXt, ViT", "Intermediate",
  "The ImageNet competition drove a series of CNN architectures, each adding an idea — depth, multi-scale filters, skip connections, efficiency — that every vision engineer should know.",
  """|Model (year)|Key idea|Notes|
|LeNet-5 (1998)|conv + pool + dense for digits|the original CNN|
|**AlexNet (2012)**|deep CNN on GPUs, ReLU, dropout, augmentation|won ImageNet by a huge margin — started the deep-learning era|
|VGG (2014)|stacks of 3×3 convs; deeper = better|simple, 138M params, slow|
|GoogLeNet / Inception (2014)|parallel 1×1, 3×3, 5×5 branches; 1×1 bottlenecks|efficient multi-scale|
|**ResNet (2015)**|residual skip connections y = x + F(x)|152 layers, surpassed human-level top-5 error; still the default backbone|
|DenseNet (2017)|each layer connects to all later layers|feature reuse|
|MobileNet (2017–19)|depthwise separable convolutions, inverted residuals|phones / edge|
|SENet|squeeze-and-excitation channel attention|—|
|EfficientNet (2019)|compound scaling of depth, width, resolution|accuracy per FLOP|
|**Vision Transformer, ViT (2020)**|split image into 16×16 patches, transformer encoder|needs big data/pretraining; DeiT, Swin add efficiency|
|ConvNeXt (2022)|CNN modernised with transformer design choices|CNNs remain competitive|
|CLIP, DINOv2, SAM|self-supervised / multimodal foundation backbones|zero-shot and universal features|

**Depthwise separable conv** = per-channel spatial conv + 1×1 pointwise conv: ~8–9× fewer operations than a standard 3×3 conv.""",
  code="""
import torch, torch.nn as nn
from torchvision import models
nets = {"AlexNet": models.alexnet, "VGG16": models.vgg16, "ResNet18": models.resnet18, "ResNet50": models.resnet50,
        "MobileNetV3-S": models.mobilenet_v3_small, "EfficientNet-B0": models.efficientnet_b0, "ViT-B/16": models.vit_b_16}
x = torch.randn(1, 3, 224, 224)
for name, fn in nets.items():
    m = fn(weights=None).eval()
    with torch.no_grad(): out = m(x)
    print(f"{name:16s} params {sum(p.numel() for p in m.parameters()) / 1e6:6.1f} M   output {tuple(out.shape)}")
std = nn.Conv2d(64, 128, 3, padding=1); dws = nn.Sequential(nn.Conv2d(64, 64, 3, padding=1, groups=64), nn.Conv2d(64, 128, 1))
print("3x3 conv params:", sum(p.numel() for p in std.parameters()), " depthwise-separable:", sum(p.numel() for p in dws.parameters()))
""",
  say=[("What made ResNet such a breakthrough?",
        "\"Before ResNet, adding layers beyond about 20 made even training accuracy worse — a degradation problem from optimisation difficulty. ResNet added identity skip connections so each block learns a residual, F(x), added to its input. Gradients flow through the identity paths, and a block can easily learn to do nothing, so networks with 100-plus layers trained well and won ImageNet 2015. Skip connections are now everywhere, including transformers.\"")]),

M("m-transfer-learning", "Transfer learning and fine-tuning pretrained models", "Intermediate",
  "Transfer learning reuses a model trained on a huge dataset (ImageNet, web text) as the starting point for your task. With a few hundred images you can reach accuracy that would need millions from scratch.",
  """### Two strategies
1. **Feature extraction**: freeze the pretrained backbone, replace the final layer with a new head for your classes, train only the head. Fast, works with very little data.
2. **Fine-tuning**: start from pretrained weights and also update some or all backbone layers with a **small learning rate** (e.g. 1e-4 to 1e-5), often unfreezing top layers first (gradual unfreezing) and using lower rates for earlier layers (discriminative learning rates).

### Choosing
|Your data|Similar to pretraining data|Different (medical, satellite)|
|Small|feature extraction|feature extraction from earlier layers, or fine-tune top layers carefully|
|Large|fine-tune top or all layers|fine-tune all layers (or train longer)|

### Recipe
Use the model's own preprocessing; strong augmentation; replace the head; train head with frozen backbone for a few epochs; unfreeze and fine-tune with lower lr + early stopping; keep BatchNorm layers in eval mode when data is tiny.

### Beyond vision
NLP: fine-tune BERT/GPT-style models (Hugging Face); speech: wav2vec 2.0/Whisper; **parameter-efficient fine-tuning** (LoRA, adapters) for big models.""",
  code=PRETRAINED + """
import torch, torch.nn as nn, torch.nn.functional as F
torch.manual_seed(0)
model, pretrained = load_backbone()
print("using", "ImageNet-pretrained" if pretrained else "random (offline) weights", "ResNet-18")
for p in model.parameters(): p.requires_grad = False                    # 1) freeze the backbone
model.fc = nn.Linear(model.fc.in_features, 3)                            # 2) new head for 3 classes
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"trainable params with frozen backbone: {trainable:,} of {sum(p.numel() for p in model.parameters()):,}")

X = torch.randn(24, 3, 128, 128); y = torch.arange(24) % 3; X[y == 1, 0] += 1.0; X[y == 2, 2] += 1.0   # toy images
opt = torch.optim.Adam(model.fc.parameters(), 1e-3); model.train()
for ep in range(15):
    opt.zero_grad(); loss = F.cross_entropy(model(X), y); loss.backward(); opt.step()
print("head-only training loss:", round(loss.item(), 3))
for p in model.layer4.parameters(): p.requires_grad = True                # 3) unfreeze the top block
opt = torch.optim.AdamW([{"params": model.layer4.parameters(), "lr": 1e-5}, {"params": model.fc.parameters(), "lr": 1e-4}])
print("fine-tuning param groups (lr):", [g["lr"] for g in opt.param_groups])
""",
  say=[("You have 500 labelled X-ray images. How would you build a classifier?",
        "\"Transfer learning: start from a backbone pretrained on ImageNet or, better, on medical images, replace the classification head, and first train only the head with heavy but realistic augmentation. Then unfreeze the top layers and fine-tune with a small learning rate and early stopping, using stratified cross-validation because the data is small. I'd check Grad-CAM to make sure it looks at the lungs rather than text markers, and report sensitivity and specificity, not just accuracy.\"")]),

M("m-augmentation", "Image augmentation (and augmentation for audio and text)", "Basic",
  "Augmentation creates realistic variations of training examples — flips, crops, colour changes — so the model learns invariances and overfits less. It's the cheapest way to get 'more data'.",
  """### Image augmentations
- **Geometric**: random crop / resized crop, horizontal flip (not for text or digits like 6/9!), rotation, scale, translate, affine/perspective, elastic distortion.
- **Photometric**: brightness, contrast, saturation, hue jitter, blur, noise, grayscale.
- **Occlusion / mixing**: Cutout / random erasing, **Mixup** (blend two images and labels), **CutMix** (paste a patch).
- **Policies**: AutoAugment, RandAugment, TrivialAugment.
- For **detection/segmentation**, transform boxes and masks together (Albumentations handles this).

### Rules
Augment **training data only** (validation/test get deterministic resize + normalise); augmentations must keep the label valid; match real-world variation (camera angles, lighting). **Test-time augmentation (TTA)**: average predictions over flips/crops.

### Other modalities
Audio: noise, time shift, speed/pitch, SpecAugment. Text: synonym replacement, back-translation, random deletion, LLM paraphrasing. Tabular: SMOTE, noise.""",
  code="""
import torch
from torchvision.transforms import v2
torch.manual_seed(0)
img = torch.zeros(3, 64, 64); img[0, 10:30, 10:50] = 1.0; img[2, 40:60, 20:40] = 0.8      # synthetic image tensor
train_tf = v2.Compose([v2.RandomResizedCrop(48, scale=(0.6, 1.0), antialias=True), v2.RandomHorizontalFlip(), v2.RandomRotation(15),
                       v2.ColorJitter(0.3, 0.3, 0.3, 0.05), v2.RandomErasing(p=0.5), v2.Normalize([0.5] * 3, [0.5] * 3)])
eval_tf = v2.Compose([v2.Resize(56, antialias=True), v2.CenterCrop(48), v2.Normalize([0.5] * 3, [0.5] * 3)])
views = torch.stack([train_tf(img) for _ in range(4)])
print("4 random training views:", tuple(views.shape), " pairwise differences:", [round((views[0] - v).abs().mean().item(), 3) for v in views[1:]])
print("eval transform is deterministic:", torch.equal(eval_tf(img), eval_tf(img)))

x1, x2 = torch.rand(3, 48, 48), torch.rand(3, 48, 48); y1, y2 = torch.tensor([1., 0, 0]), torch.tensor([0., 1, 0])
lam = torch.distributions.Beta(0.4, 0.4).sample().item()
print(f"mixup: lambda={lam:.2f}, mixed label={(lam * y1 + (1 - lam) * y2).numpy().round(2)}")
""",
  say=[("Which augmentations would you avoid for a digit or traffic-sign classifier?",
        "\"Any that change the label: horizontal or vertical flips turn a left-turn sign into a right-turn sign and can confuse 6 with 9, and large rotations do the same. I'd use small rotations, scale and translation, brightness and contrast, blur and noise — variations that occur in real camera captures — and validate that augmentation actually improves the validation score.\"")]),

M("m-object-detection", "Object detection: bounding boxes, IoU, NMS, anchors, YOLO, Faster R-CNN, DETR, mAP", "Advanced",
  "Object detection finds what objects are in an image and where, outputting a class and a bounding box for each. It powers self-driving perception, retail shelf monitoring and security cameras.",
  """### Core concepts
- **Bounding box**: (x_min, y_min, x_max, y_max) or (centre, width, height).
- **IoU (intersection over union)** = overlap area / union area — measures box agreement; 0.5 is the classic "correct" threshold.
- **Non-maximum suppression (NMS)**: keep the highest-scoring box, drop others overlapping it above an IoU threshold, repeat.
- **Anchors**: predefined box shapes the model refines (Faster R-CNN, YOLOv2–v5); many modern detectors are anchor-free.

### Detector families
|Family|Examples|Trade-off|
|Two-stage|R-CNN → Fast R-CNN → **Faster R-CNN** (region proposal network), Mask R-CNN|accurate, slower|
|One-stage|**YOLO** (v1–v11), SSD, RetinaNet (focal loss), FCOS, CenterNet|real-time|
|Transformer|**DETR**, Deformable DETR, RT-DETR|end-to-end, no NMS (bipartite matching)|
|Open-vocabulary|OWL-ViT, Grounding DINO, YOLO-World|detect any text-described class|

### Training and evaluation
Loss = classification (cross-entropy/focal) + box regression (smooth L1 / IoU-based) + objectness. Metric: **mAP** — average precision per class (area under the precision–recall curve at IoU 0.5, or averaged over IoU 0.5:0.95 as in COCO), averaged over classes.

### Practical
Label with tools like CVAT/Label Studio/Roboflow; fine-tune a pretrained detector (Ultralytics YOLO, torchvision, Detectron2) — a few hundred labelled images per class can work.""",
  code="""
import torch
from torchvision.ops import box_iou, nms
def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1])); inter = ix * iy
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1]); return inter / (area(a) + area(b) - inter)
print("IoU from scratch:", round(iou([10, 10, 50, 50], [30, 30, 70, 70]), 3), " torchvision:", round(box_iou(torch.tensor([[10., 10, 50, 50]]), torch.tensor([[30., 30, 70, 70]])).item(), 3))
boxes = torch.tensor([[100, 100, 200, 200], [105, 98, 205, 210], [300, 300, 380, 360], [102, 104, 198, 195.]])
scores = torch.tensor([0.92, 0.85, 0.80, 0.60])
print("boxes kept after NMS (IoU > 0.5 suppressed):", nms(boxes, scores, 0.5).tolist())

from torchvision.models.detection import ssdlite320_mobilenet_v3_large
det = ssdlite320_mobilenet_v3_large(weights=None, weights_backbone=None, num_classes=4).eval()   # use weights="DEFAULT" online
with torch.no_grad(): out = det([torch.rand(3, 320, 320)])[0]
print("detector output keys:", list(out.keys()), " boxes tensor:", tuple(out["boxes"].shape))
det.train()
targets = [{"boxes": torch.tensor([[50., 60, 150, 200]]), "labels": torch.tensor([1])}, {"boxes": torch.tensor([[10., 20, 90, 120], [150, 150, 300, 310]]), "labels": torch.tensor([2, 3])}]
losses = det([torch.rand(3, 320, 320), torch.rand(3, 320, 320)], targets); print("training losses:", {k: round(v.item(), 3) for k, v in losses.items()})
""",
  say=[("Explain IoU and non-maximum suppression.",
        "\"IoU is the area of overlap between two boxes divided by the area of their union — 1 means identical, 0 means no overlap. Detectors output many overlapping boxes for the same object, so NMS sorts boxes by confidence, keeps the best, removes any remaining box of the same class whose IoU with it exceeds a threshold like 0.5, and repeats. IoU is also used to match predictions to ground truth when computing mAP.\"")]),

M("m-segmentation", "Image segmentation: semantic, instance, panoptic; U-Net, Mask R-CNN, SAM", "Advanced",
  "Segmentation labels every pixel. Semantic segmentation gives each pixel a class; instance segmentation also separates individual objects; panoptic does both.",
  """### Types
|Type|Output|Example models|
|Semantic|class per pixel (all cars = 'car')|FCN, **U-Net**, DeepLab (atrous convolutions), SegFormer|
|Instance|mask per object (car #1, car #2)|**Mask R-CNN**, YOLO-seg|
|Panoptic|both (things + stuff)|Panoptic FPN, Mask2Former|
|Promptable / zero-shot|mask for a clicked point or box or text|**SAM / SAM 2** (Segment Anything)|

### U-Net
Encoder (downsampling convs) captures context; decoder (upsampling / transposed convs) recovers resolution; **skip connections** copy encoder features to the decoder for precise boundaries. Works with few images — the standard in medical imaging (and in diffusion models!).

### Losses and metrics
Pixel-wise cross-entropy, **Dice loss** (1 − 2|A∩B|/(|A|+|B|)), focal, combos; metrics: **IoU / Jaccard**, mean IoU over classes, Dice coefficient, pixel accuracy (misleading with large background).

### Applications
Medical (tumours, organs), autonomous driving (road, lanes), satellite (land use), **food image segmentation** (portion and calorie estimation — a capstone option), photo editing.""",
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
torch.manual_seed(0)
def shapes(n, s=32):                                  # synthetic images: a bright disc on noise; mask = disc
    yy, xx = torch.meshgrid(torch.arange(s), torch.arange(s), indexing="ij"); X, Y = [], []
    for _ in range(n):
        cy, cx, r = torch.randint(8, 24, (2,)).tolist() + [torch.randint(4, 8, (1,)).item()]
        m = ((yy - cy) ** 2 + (xx - cx) ** 2 <= r * r).float(); X.append(m * 0.8 + 0.3 * torch.rand(s, s)); Y.append(m)
    return torch.stack(X)[:, None], torch.stack(Y)[:, None]
def block(i, o): return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.ReLU(), nn.Conv2d(o, o, 3, padding=1), nn.ReLU())
class TinyUNet(nn.Module):
    def __init__(self):
        super().__init__(); self.e1, self.e2, self.b = block(1, 16), block(16, 32), block(32, 64)
        self.u2, self.d2 = nn.ConvTranspose2d(64, 32, 2, 2), block(64, 32); self.u1, self.d1 = nn.ConvTranspose2d(32, 16, 2, 2), block(32, 16); self.out = nn.Conv2d(16, 1, 1)
    def forward(self, x):
        e1 = self.e1(x); e2 = self.e2(F.max_pool2d(e1, 2)); b = self.b(F.max_pool2d(e2, 2))
        d2 = self.d2(torch.cat([self.u2(b), e2], 1)); d1 = self.d1(torch.cat([self.u1(d2), e1], 1))   # skip connections
        return self.out(d1)
def dice(logits, y, eps=1.0):
    p = torch.sigmoid(logits); return 1 - (2 * (p * y).sum() + eps) / (p.sum() + y.sum() + eps)
X, Y = shapes(256); Xt, Yt = shapes(64); net = TinyUNet(); opt = torch.optim.Adam(net.parameters(), 2e-3)
for ep in range(12):
    for i in range(0, 256, 32):
        opt.zero_grad(); lo = net(X[i:i + 32]); loss = F.binary_cross_entropy_with_logits(lo, Y[i:i + 32]) + dice(lo, Y[i:i + 32]); loss.backward(); opt.step()
with torch.no_grad():
    P = (torch.sigmoid(net(Xt)) > 0.5).float(); inter = (P * Yt).sum(); union = ((P + Yt) > 0).float().sum()
print(f"test IoU {inter / union:.3f}   Dice {2 * inter / (P.sum() + Yt.sum()):.3f}")
""",
  say=[("Why does U-Net use skip connections?",
        "\"The encoder downsamples to capture context but loses fine spatial detail. The decoder upsamples back to full resolution, and skip connections concatenate the high-resolution encoder features at each scale into the decoder, so it can place boundaries precisely while still knowing what the object is. That's why U-Net segments well even with small datasets, like medical images.\"")]),

M("m-video", "Video processing: frames, optical flow, tracking, action recognition", "Advanced",
  "Video is a sequence of images over time. Models must handle both appearance (what) and motion (how things move) efficiently, since video is huge.",
  """### Reading and processing
OpenCV `cv2.VideoCapture` reads frames (BGR); sample frames (e.g. 1–5 fps) to save compute; resize; batch frames.

### Motion
- **Frame differencing / background subtraction** (MOG2) — simple motion detection for CCTV.
- **Optical flow**: per-pixel motion vectors between frames — Lucas–Kanade (sparse, tracks keypoints), Farnebäck (dense), RAFT (deep).

### Tracking
Detect objects in each frame then associate across frames: **SORT** (Kalman filter + Hungarian matching on IoU), **DeepSORT / ByteTrack** (add appearance embeddings / low-score boxes). Used for counting people/vehicles.

### Video understanding models
- 2-D CNN per frame + temporal pooling or LSTM.
- **Two-stream** networks (RGB + optical flow).
- **3-D CNNs** (C3D, I3D, X3D) convolve over space and time.
- **Video transformers** (TimeSformer, ViViT, VideoMAE); video-language models.
Tasks: action recognition, temporal action detection, video captioning, anomaly detection, video object segmentation (SAM 2).""",
  code="""
import numpy as np, cv2, torch, torch.nn as nn
frames = []
for t in range(10):                                         # synthetic video: a square moving right 3 px per frame
    f = np.zeros((64, 64), np.uint8); cv2.rectangle(f, (5 + 3 * t, 20), (20 + 3 * t, 35), 255, -1); frames.append(f)
diff = cv2.absdiff(frames[5], frames[4]); print("pixels changed between frames 4 and 5:", int((diff > 0).sum()))
flow = cv2.calcOpticalFlowFarneback(frames[4], frames[5], None, 0.5, 3, 9, 3, 5, 1.2, 0)
moving = np.linalg.norm(flow, axis=2) > 0.5
print("mean optical flow on the moving object (dx, dy):", flow[moving].mean(0).round(2), "-> moving right")

bg = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold=16)
for f in frames: fg = bg.apply(f)
print("foreground pixels detected in last frame:", int((fg > 0).sum()))

clip = torch.tensor(np.stack(frames), dtype=torch.float32)[None, None] / 255     # (batch, channels, time, H, W)
conv3d = nn.Conv3d(1, 8, kernel_size=(3, 3, 3), padding=1); print("3-D conv over time:", tuple(clip.shape), "->", tuple(conv3d(clip).shape))
""",
  say=[("How would you count vehicles crossing a line in a traffic video?",
        "\"Run a pretrained detector like YOLO on sampled frames to get vehicle boxes, track them across frames with a tracker such as ByteTrack or DeepSORT so each vehicle keeps an ID, and count an ID once when its track crosses the virtual line in the right direction. I'd tune frame rate for speed, handle occlusions with the tracker, and validate counts against a manually labelled clip.\"")]),

M("m-face-emotion", "Face detection and emotion recognition from faces and speech", "Advanced",
  "Emotion recognition detects a face (or a voice), extracts features and classifies expressions like happy, sad, angry. It combines detection, alignment and classification — and raises real ethical questions.",
  """### Face pipeline
1. **Detect** faces: Haar cascades (Viola–Jones, fast, weak), HOG + SVM (dlib), deep detectors (MTCNN, RetinaFace, YuNet, MediaPipe).
2. **Align**: landmarks (eyes, nose, mouth — 5 or 68 points) → rotate/crop to a canonical pose.
3. **Classify expression**: CNN or ViT trained on FER-2013 (48×48 grayscale, 7 emotions), AffectNet, RAF-DB; or regress **valence/arousal**. Action units (FACS) for fine-grained analysis.

### Speech emotion recognition
Features: pitch (F0) mean/variance, energy, speaking rate, MFCCs, spectral features → SVM/CNN/LSTM; or fine-tune wav2vec 2.0/HuBERT. Datasets: RAVDESS, CREMA-D, IEMOCAP. **Multimodal** fusion (face + voice + text) is more accurate.

### Caveats
Expressions ≠ felt emotions; cultural differences; dataset bias (age, skin tone); privacy and consent. The EU AI Act restricts emotion recognition in workplaces and schools. Report per-group accuracy.""",
  code="""
import numpy as np, cv2
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import os
path = os.path.join(getattr(cv2, "data", None).haarcascades if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades") else "", "haarcascade_frontalface_default.xml")
if os.path.exists(path):                                      # bundled with OpenCV 4.x (Colab)
    cascade = cv2.CascadeClassifier(path); blank = np.full((200, 200), 128, np.uint8)
    print("Haar face detector loaded; faces in a blank image:", len(cascade.detectMultiScale(blank, 1.1, 5)))
else:
    print("Haar cascade files not bundled with this OpenCV build; deep alternative available:", hasattr(cv2, "FaceDetectorYN"))
# usage on a photo: faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5); crop -> resize 48x48 -> emotion CNN

# Speech emotion toy: 'excited' speech has higher, more variable pitch and energy than 'calm' speech
rng = np.random.default_rng(0); sr = 8000
def utterance(excited):
    t = np.arange(sr) / sr; f0 = (220 if excited else 140) + (60 if excited else 15) * np.sin(2 * np.pi * rng.uniform(2, 5) * t)
    amp = (0.8 if excited else 0.4) * (1 + 0.5 * np.sin(2 * np.pi * rng.uniform(3, 6) * t))
    return amp * np.sin(2 * np.pi * np.cumsum(f0) / sr) + 0.05 * rng.normal(size=sr)
def feats(y):
    frames = y[: len(y) // 200 * 200].reshape(-1, 200); energy = (frames ** 2).mean(1)
    zcr = (np.diff(np.sign(frames), axis=1) != 0).mean(1)                        # zero-crossing rate tracks pitch
    return [energy.mean(), energy.std(), zcr.mean(), zcr.std()]
X = np.array([feats(utterance(e)) for e in [0, 1] * 60]); y = np.array([0, 1] * 60)
print("speech emotion (calm vs excited) CV accuracy:", cross_val_score(RandomForestClassifier(random_state=0), X, y, cv=5).mean().round(3))
""",
  say=[("What are the risks of deploying emotion recognition?",
        "\"Facial expressions don't reliably reveal inner emotions and vary across cultures and individuals, models are often less accurate for some demographic groups, and using it for hiring, policing or monitoring employees can be discriminatory and invasive — several regulations, like the EU AI Act, restrict it. If deployed, it needs consent, transparency, per-group evaluation and a human in the loop, and should only inform low-stakes decisions.\"")]),

M("m-siamese", "Siamese networks, metric learning, contrastive and triplet loss", "Advanced",
  "A Siamese network passes two inputs through the same encoder and compares their embeddings. It learns similarity rather than fixed classes — ideal for face verification, signature checking, duplicate detection and one-shot learning.",
  """### Architecture
Twin encoders with **shared weights** → embeddings f(x₁), f(x₂) → distance (Euclidean or cosine) → same / different.

### Losses
- **Contrastive loss**: similar pairs pulled together; dissimilar pairs pushed apart until at least a margin m: L = y·d² + (1 − y)·max(0, m − d)².
- **Triplet loss** (FaceNet): anchor a, positive p, negative n: L = max(0, d(a, p) − d(a, n) + margin). **Hard-negative mining** is crucial.
- **InfoNCE / NT-Xent** (contrastive learning with many negatives — SimCLR, CLIP), **ArcFace** (angular margin softmax for faces).

### Why it's powerful
New identities need no retraining — enrol one photo (**one-shot learning**) and compare embeddings. Same idea powers sentence-transformers (duplicate questions, e.g. Quora question pairs), image search, recommendation two-tower models and RAG retrievers.""",
  code="""
import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.datasets import load_digits
torch.manual_seed(0)
d = load_digits(); X = torch.tensor(d.data / 16, dtype=torch.float32); y = torch.tensor(d.target)
seen, unseen = y < 7, y >= 7                                  # train on digits 0-6 only; test on never-seen 7, 8, 9
enc = nn.Sequential(nn.Linear(64, 128), nn.ReLU(), nn.Linear(128, 32))
opt = torch.optim.Adam(enc.parameters(), 1e-3); Xs, ys = X[seen], y[seen]
for step in range(600):                                       # triplet loss with random triplets
    a = torch.randint(0, len(ys), (128,)); lab = ys[a]
    p = torch.stack([torch.nonzero(ys == l)[torch.randint(0, (ys == l).sum().item(), (1,))].squeeze() for l in lab])
    n = torch.stack([torch.nonzero(ys != l)[torch.randint(0, (ys != l).sum().item(), (1,))].squeeze() for l in lab])
    ea, ep, en = (F.normalize(enc(Xs[i]), dim=1) for i in (a, p, n))
    loss = F.triplet_margin_loss(ea, ep, en, margin=0.3); opt.zero_grad(); loss.backward(); opt.step()
with torch.no_grad(): E = F.normalize(enc(X[unseen]), dim=1); yu = y[unseen]
support = torch.stack([E[yu == c][0] for c in (7, 8, 9)])    # ONE example per new class
pred = torch.tensor([7, 8, 9])[(E @ support.T).argmax(1)]
print(f"one-shot accuracy on unseen digits 7/8/9: {(pred == yu).float().mean():.3f} (chance 0.333)")
same = (E[yu == 8][1] @ E[yu == 8][2]).item(); diff = (E[yu == 8][1] @ E[yu == 9][0]).item()
print(f"cosine similarity same digit {same:.2f} vs different digit {diff:.2f}")
""",
  say=[("How does face verification work without retraining for every new employee?",
        "\"It uses a Siamese or metric-learning model: a network trained with triplet or ArcFace loss maps any face to an embedding where the same person's faces are close and different people are far apart. To enrol someone you store the embedding of one or a few photos; to verify, you embed the new photo and compare cosine similarity against a threshold tuned for the false-accept and false-reject rates you need. New people never require retraining.\"")]),

M("m-gan", "Generative adversarial networks (GANs)", "Advanced",
  "A GAN pits two networks against each other: a generator makes fake samples from random noise, a discriminator tries to tell fakes from real data. Competing, the generator learns to produce realistic data.",
  """### Training game
- **Generator G(z)**: noise z → fake sample.
- **Discriminator D(x)**: probability x is real.
- Alternate: train D to classify real vs fake (BCE); train G to fool D (maximise log D(G(z)) — the "non-saturating" loss).
min_G max_D E[log D(x)] + E[log(1 − D(G(z)))]. At equilibrium G matches the data distribution.

### Difficulties
**Mode collapse** (G produces few varieties), unstable training, vanishing D gradients. Fixes: DCGAN design rules (strided convs, BatchNorm, LeakyReLU), **Wasserstein GAN** with gradient penalty, spectral normalisation, two-timescale learning rates, label smoothing.

### Famous variants
DCGAN, **conditional GAN** (generate a requested class), **Pix2Pix** (paired image translation), **CycleGAN** (unpaired: horse ↔ zebra), **StyleGAN** (photorealistic faces, style control), **SRGAN / ESRGAN** (super-resolution with perceptual + adversarial loss — a capstone option), BigGAN.

### Evaluation
FID (Fréchet inception distance, lower is better), Inception Score, precision/recall for generative models, human judgement. Diffusion models have largely overtaken GANs for image quality and diversity, but GANs are faster at inference.""",
  code="""
import torch, torch.nn as nn, math
torch.manual_seed(0)
def real_batch(n):                                            # target: 8 Gaussians on a ring
    k = torch.randint(0, 8, (n,)).float() * (2 * math.pi / 8)
    return torch.stack([2 * torch.cos(k), 2 * torch.sin(k)], 1) + 0.05 * torch.randn(n, 2)
G = nn.Sequential(nn.Linear(4, 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 2))
D = nn.Sequential(nn.Linear(2, 64), nn.LeakyReLU(0.2), nn.Linear(64, 64), nn.LeakyReLU(0.2), nn.Linear(64, 1))
oG, oD = torch.optim.Adam(G.parameters(), 1e-3, betas=(0.5, 0.999)), torch.optim.Adam(D.parameters(), 1e-3, betas=(0.5, 0.999))
bce = nn.BCEWithLogitsLoss()
for step in range(3001):
    real, fake = real_batch(256), G(torch.randn(256, 4))
    lossD = bce(D(real), torch.ones(256, 1)) + bce(D(fake.detach()), torch.zeros(256, 1))
    oD.zero_grad(); lossD.backward(); oD.step()
    lossG = bce(D(fake), torch.ones(256, 1))                  # generator wants D to say 'real'
    oG.zero_grad(); lossG.backward(); oG.step()
    if step % 1000 == 0: print(f"step {step:4d}  D loss {lossD.item():.3f}  G loss {lossG.item():.3f}")
with torch.no_grad(): s = G(torch.randn(2000, 4))
angles = torch.atan2(s[:, 1], s[:, 0]); modes = ((angles % (2 * math.pi)) / (2 * math.pi / 8) + 0.5).long() % 8
print("generated radius ~2:", round(s.norm(dim=1).mean().item(), 2), "| modes covered:", len(torch.unique(modes[(s.norm(dim=1) - 2).abs() < 0.5])), "of 8")
""",
  say=[("What is mode collapse in GANs and how do you mitigate it?",
        "\"The generator finds a few outputs that fool the discriminator and keeps producing only those, ignoring the rest of the data distribution — for example generating the same face. Mitigations include Wasserstein loss with gradient penalty, minibatch discrimination or diversity terms, spectral normalisation, unrolled or two-timescale updates, and conditional GANs. Diffusion models largely avoid the problem, which is one reason they've replaced GANs for many tasks.\"")]),

M("m-super-resolution", "Image reconstruction, denoising and super-resolution (SRCNN, SRGAN, ESRGAN)", "Advanced",
  "Image reconstruction recovers a clean or high-resolution image from a degraded one. Models learn the mapping from low-quality to high-quality pairs, created by degrading good images.",
  """### Tasks
Denoising, deblurring, inpainting (fill holes), colourisation, **super-resolution** (×2/×4 upscaling), JPEG artifact removal.

### Building training pairs
Take high-resolution (HR) images, synthesise low-resolution (LR) inputs by downsampling (bicubic), blurring, adding noise/compression — Real-ESRGAN uses a realistic degradation pipeline.

### Models
- **SRCNN (2014)**: 3 conv layers on a bicubic-upsampled input.
- **ESPCN**: learn in LR space, upsample with **pixel shuffle** (sub-pixel convolution) — fast.
- **EDSR / RCAN**: deep residual networks (+ channel attention).
- **SRGAN / ESRGAN**: adversarial + **perceptual loss** (VGG feature distance) → sharp, realistic textures instead of blurry averages.
- **SwinIR** (transformer), **diffusion-based** SR (SR3, Stable Diffusion upscalers).

### Metrics
**PSNR** (peak signal-to-noise ratio, dB) and **SSIM** (structural similarity) reward pixel fidelity; MSE-trained models win PSNR but look blurry; GAN/diffusion outputs look sharper but score lower — use LPIPS / human studies too.""",
  code="""
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
torch.manual_seed(0)
def scenes(n, s=32):                                                               # sharp-edged synthetic images
    imgs = torch.zeros(n, 1, s, s)
    for i in range(n):
        for _ in range(4):
            x0, y0 = torch.randint(0, s - 6, (2,)).tolist(); w, h = torch.randint(3, 14, (2,)).tolist()
            imgs[i, 0, y0:y0 + h, x0:x0 + w] = torch.rand(1).item()
        if i % 2: imgs[i, 0, :, torch.randint(0, s, (1,)).item()] = 1.0                 # thin lines = fine detail
    return imgs
hr = scenes(1600)                                                                   # 32x32 'high-res'
lr = F.avg_pool2d(hr, 2)                                                           # 16x16 'low-res'
class ESPCN(nn.Module):                                                            # sub-pixel convolution super-resolution
    def __init__(self, r=2):
        super().__init__(); self.body = nn.Sequential(nn.Conv2d(1, 32, 5, padding=2), nn.Tanh(), nn.Conv2d(32, 16, 3, padding=1), nn.Tanh(), nn.Conv2d(16, r * r, 3, padding=1))
        self.shuffle = nn.PixelShuffle(r)
    def forward(self, x): return self.shuffle(self.body(x)) + F.interpolate(x, scale_factor=2, mode="bicubic", align_corners=False)
net = ESPCN(); opt = torch.optim.Adam(net.parameters(), 2e-3)
for ep in range(30):
    for i in range(0, 1400, 100):
        opt.zero_grad(); F.mse_loss(net(lr[i:i + 100]), hr[i:i + 100]).backward(); opt.step()
with torch.no_grad():
    test_lr, test_hr = lr[1400:], hr[1400:]
    bic = F.interpolate(test_lr, scale_factor=2, mode="bicubic", align_corners=False).clamp(0, 1); sr = net(test_lr).clamp(0, 1)
def score(a):
    return np.mean([psnr(h[0].numpy(), x[0].numpy(), data_range=1) for h, x in zip(test_hr, a)]), np.mean([ssim(h[0].numpy(), x[0].numpy(), data_range=1) for h, x in zip(test_hr, a)])
print("bicubic upscaling : PSNR %.2f dB  SSIM %.3f" % score(bic))
print("ESPCN (learned)   : PSNR %.2f dB  SSIM %.3f" % score(sr))
""",
  say=[("Why do super-resolution models trained with MSE look blurry, and how do SRGAN/ESRGAN fix it?",
        "\"Many high-resolution images are consistent with one low-resolution input; minimising MSE makes the model predict their average, which is blurry even though it maximises PSNR. SRGAN and ESRGAN add a perceptual loss on VGG features and an adversarial loss, which push outputs toward the manifold of realistic images with sharp textures — better-looking results at a slightly lower PSNR.\"")]),

M("m-speech-recognition", "Speech recognition and synthesis: CTC, wav2vec 2.0, Whisper, TTS", "Advanced",
  "Automatic speech recognition (ASR) turns audio into text; text-to-speech (TTS) does the reverse. Modern systems are end-to-end neural networks trained on thousands of hours of speech.",
  """### Evolution
GMM-HMM with MFCCs (decades) → hybrid DNN-HMM → **end-to-end**:
- **CTC (connectionist temporal classification)**: the model outputs a character per audio frame including a "blank"; CTC loss sums over all alignments, decoding collapses repeats and removes blanks (DeepSpeech, wav2vec 2.0 fine-tuning).
- **Attention encoder–decoder / RNN-T (transducer)**: streaming on-device ASR (Google, Apple).
- **wav2vec 2.0 / HuBERT**: self-supervised pretraining on raw audio, fine-tune with little labelled speech.
- **Whisper** (OpenAI, 2022): transformer encoder–decoder on log-mel spectrograms, trained on 680k hours of weakly-supervised multilingual data — robust transcription, translation and language ID.

### Metrics
**WER (word error rate)** = (substitutions + deletions + insertions) / reference words; CER for characters.

### Related speech tasks
Speaker identification/verification (x-vectors, ECAPA-TDNN), diarisation (who spoke when), keyword spotting, speech emotion, speech translation.

### TTS
Text → phonemes → acoustic model (Tacotron 2, FastSpeech) → mel spectrogram → vocoder (WaveNet, HiFi-GAN) → audio; modern end-to-end (VITS) and zero-shot voice cloning models — with consent and misuse concerns.""",
  code="""
import torch, torch.nn as nn
def wer(ref, hyp):
    r, h = ref.split(), hyp.split(); d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1): d[i][0] = i
    for j in range(len(h) + 1): d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1][-1] / len(r)
print("WER:", round(wer("turn on the kitchen lights", "turn the kitchen light on"), 3))

def ctc_greedy_decode(frame_ids, blank=0, alphabet="_abcdefghijklmnopqrstuvwxyz '"):
    out, prev = [], None
    for i in frame_ids:
        if i != prev and i != blank: out.append(alphabet[i])
        prev = i
    return "".join(out)
frames = [8, 8, 0, 5, 5, 12, 0, 12, 12, 15, 0]                 # h h _ e e l _ l l o _
print("CTC decode:", ctc_greedy_decode(frames))

T, N, C = 50, 2, 29                                            # CTC loss in PyTorch: (time, batch, classes)
log_probs = torch.randn(T, N, C).log_softmax(2).requires_grad_()
targets = torch.randint(1, C, (N, 10)); loss = nn.CTCLoss(blank=0)(log_probs, targets, torch.full((N,), T), torch.full((N,), 10))
loss.backward(); print("CTC loss on random predictions:", round(loss.item(), 2))
# Whisper (needs internet to download weights):
# from transformers import pipeline; asr = pipeline("automatic-speech-recognition", model="openai/whisper-small"); asr("speech.wav")["text"]
""",
  say=[("What is CTC and why is it needed for speech recognition?",
        "\"Audio has many more frames than the transcript has characters, and we don't know which frames correspond to which character. CTC lets the network output a character or a blank at every frame and defines the loss as the total probability of all frame-level paths that collapse to the correct transcript, computed efficiently with dynamic programming. So we can train end-to-end without frame-level alignments.\"")]),
]
