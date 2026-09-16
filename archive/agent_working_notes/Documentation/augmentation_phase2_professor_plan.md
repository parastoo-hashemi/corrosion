# Data Augmentation Work Package
## Corrosion Image Dataset — Deep Learning Pipeline

> **Scope:** Satisfies professor's four goals: (1) identify suitable techniques, (2) Python implementation, (3) dataset expansion factor, (4) integration into repository.
> **Date:** 2026-06-27

---

## Objective

Extend the existing deep learning pipeline (`main_2`) with a principled image augmentation strategy to:

1. Improve robustness of the ResNet18-based image representation on the 791-image corrosion dataset.
2. Enable a fair comparison: **DL with augmentation** vs. **DL without augmentation** vs. **threshold-based red-color baseline** (`main_4` `img_rust_area_ratio_pct`).
3. Produce augmented DL embeddings that can feed downstream into the structural prediction pipeline (`main_4`) for `wire_area_loss_frac` and `ultimate_load_kn`.

---

## Repository Evidence

### Existing Deep Learning Code
**Location:** `main_2/`

The current pipeline uses a **frozen ResNet18** (ImageNet pretrained, `ResNet18_Weights.IMAGENET1K_V1`) as a fixed backbone producing 512-dimensional embeddings. A `RegressionMLP` (Linear 512→256→128→64→1, with BatchNorm and Dropout) is trained on top of those embeddings.

**Critical gap:** `main_2/data.py` `extract_resnet18_embeddings()` (lines 137–175) runs in `backbone.eval()` with `torch.no_grad()`. It extracts embeddings for **all rows in a single pass before training begins** and stores them in memory. No augmentation is applied at any stage. The `transform` used is `weights.transforms()` — the standard ImageNet inference pre-processing (resize to 224×224, normalise with ImageNet mean/std). This is why adding augmentation requires an architectural change to the training loop, not just adding transforms.

**Target:** `B_Peak_Rust_Percentage_[%]` (= `peak_rust_pct` in `main_4`).

**Split logic:** `main_2/data.py` `build_group_splits()` uses `GroupShuffleSplit` keyed on the `specimen` column (lines 57–81), producing train/val/test indices. This correctly prevents specimen leakage.

### Existing Threshold / Red-Color Baseline
**Location:** `main_4/src/corrosion_proxy_rul/image_features.py` + `main_4/configs/features.yaml`

The baseline is a fixed RGB threshold mask:
- Rust pixels: R∈[25,255], G∈[0,100], B∈[0,80]
- `img_rust_area_ratio_pct` = fraction of image pixels classified as rust × 100

This is the "automatic classification approach based only on the quantification of the red color" referenced in the professor's email. It achieves MAE ≈ 0.0002 against the `surface_total_rust_pct` workbook label (because the label was derived from essentially the same threshold applied to the same images). For `peak_rust_pct`, it serves as a strong baseline through the strip-feature system.

### Existing Image Properties
- **Count:** 792 PNG files (791 usable after excluding one corrupted image)
- **Resolution:** 2835 × 650 pixels, RGBA mode
- **Specimens:** 48, with 15–18 images per specimen (longitudinal time series, weeks 0–36)
- **Location:** `Data/Images_dataset/`

### Existing Structural Prediction Pipeline
**Location:** `main_4/src/corrosion_proxy_rul/`

The structural targets (`wire_area_loss_frac`, `ultimate_load_kn`) are modeled from a 48-row terminal feature table. The best-performing feature sets selected are `metadata_only`. DL embeddings are not currently used as structural features. The hook point is `main_4/src/corrosion_proxy_rul/feature_engineering.py` where the full feature table is assembled: augmented DL embeddings could be joined here as an additional feature family.

### Existing Split Logic
**Location:** `main_4/src/corrosion_proxy_rul/splits.py`

Three strategies: `GroupShuffleSplit` (5 folds), `LeaveOneGroupOut` on treatment, `LeaveOneGroupOut` on campaign. All keyed on `specimen_id`. Pre-computed manifests stored as CSVs in `outputs/splits/`. The augmentation pipeline must consume these manifests, not define new splits.

---

## Immediate Image-Level Goal

Train a ResNet18 model (fine-tuned or frozen backbone + trained head) on augmented training images and compare its performance on `peak_rust_pct` against:

- **Baseline A:** Threshold red-color approach (`img_rust_area_ratio_pct` from `main_4`)
- **Baseline B:** DL pipeline without augmentation (current `main_2`)
- **Proposed:** DL pipeline with augmentation (new `main_2` extended)

Primary metric: MAE and Spearman correlation for `peak_rust_pct` under specimen-grouped holdout.

---

## Downstream Structural Goal

After training with augmentation, extract per-image DL embeddings from training specimens, aggregate them to specimen level (mean across all time points, or final time point only), and join them as additional features into `main_4`'s 48-row terminal structural table. Evaluate whether augmented DL features improve `ultimate_load_kn` or `wire_area_loss_frac` prediction under grouped holdout and LOCO.

---

## Suitable Augmentations

These are appropriate for corrosion images in the DL context. Unlike the classical feature pipeline (where fixed RGB thresholds are applied), the ResNet18 backbone processes raw RGB pixels and does not use hardcoded color thresholds. All augmentations listed below are safe in this context.

### T1 — Color Jitter (Brightness, Contrast, Saturation)

Randomly perturbs brightness, contrast, and saturation within bounded ranges. Simulates variation in ambient illumination, camera white balance drift, and ageing of the imaging setup across the 36-week protocol.

**Justification:** The images were taken across multiple years (campaign 1: 2022, campaign 2: 2024) under potentially different lighting conditions. Color jitter teaches the model that the absolute color tone is less important than the relative distribution of rust-like pixels.

**Library:** `torchvision.transforms.ColorJitter`

---

### T2 — Gaussian Blur

Applies a Gaussian smoothing kernel to simulate camera focus variation, lens contamination, or slight depth-of-field effects.

**Justification:** Texture features (surface roughness, crack patterns around rust spots) may vary due to focus drift across the imaging sessions. Blur regularises the model against fine-grained noise.

**Library:** `torchvision.transforms.GaussianBlur`

---

### T3 — Random Horizontal Flip

Mirrors the image left-right. Safe for the DL pipeline because ResNet18 processes the image as a grid of patches and does not assume left-right physical specimen orientation.

**Note:** This augmentation is explicitly **NOT safe** for the classical `main_4` pipeline, where strip features encode physical left-right position (`img_strip_peak_location_cm`, `img_rust_center_of_mass_cm`). It is safe only in the DL context.

**Library:** `torchvision.transforms.RandomHorizontalFlip`

---

### T4 — Random Grayscale

Converts the image to grayscale with a configurable probability. Forces the model to learn structure from luminance alone when colour is absent, improving robustness to colour-channel noise.

**Justification:** Teaches the model to not overfit to the specific hue of rust (which is what the threshold baseline does). A good representation should capture shape, texture, and extent — not just colour.

**Library:** `torchvision.transforms.RandomGrayscale`

---

### T5 — Random Resized Crop

Crops a random sub-region of the image and resizes it to the target input resolution (224×224 for ResNet18). Simulates variation in camera distance and specimen framing across sessions.

**Justification:** Crop variation tests whether the model can identify rust patterns from partial views. Given that the images are 2835×650 and ResNet18 resizes to 224×224, a crop of 85–100% of the image still captures the full specimen.

**Crop range:** 80–100% of original area. Aspect ratio range: 0.9–1.1.

**Library:** `torchvision.transforms.RandomResizedCrop`

---

### T6 — Additive Gaussian Noise

Adds pixel-level Gaussian noise to the image tensor after normalisation. Regularises the model against sensor noise inherent in camera capture.

**Justification:** Not available as a single torchvision transform; implemented as a custom transform (see Implementation Plan). Noise standard deviation must be small (σ ≤ 0.05 in [0,1]-normalised space) to avoid visually implausible distortions.

**Library:** Custom `torch.Tensor` operation.

---

## Augmentations to Avoid

| Augmentation | Reason |
|---|---|
| **Vertical flip** | Specimen images are oriented with the long axis horizontal; vertical flip creates physically implausible images (the concrete surface would face downward) |
| **Large rotation (>10°)** | The specimen is photographed with its length axis horizontal; large rotations create orientation-inconsistent images that the model would never see at inference time |
| **CutOut / random erasing (large patches)** | Erasing large regions removes actual corrosion from the image; if a rust spot is erased, the image no longer corresponds to its label |
| **Aggressive hue shift (>0.1 hue factor)** | Large hue shifts can convert rust-coloured pixels to non-rust colours, making the augmented image inconsistent with its label |
| **Elastic deformation** | Distorts the spatial distribution of rust patterns; changes morphological features the model should learn |
| **Colour inversion / solarise** | Produces images with no visual correspondence to corrosion; not seen during inference |

---

## Recommended Parameter Ranges

| Transform | Parameter | Recommended Range |
|---|---|---|
| `ColorJitter` | `brightness` | 0.2 (factor range [0.8, 1.2]) |
| `ColorJitter` | `contrast` | 0.2 (factor range [0.8, 1.2]) |
| `ColorJitter` | `saturation` | 0.2 (factor range [0.8, 1.2]) |
| `ColorJitter` | `hue` | 0.05 (shift range [−0.05, +0.05]) |
| `GaussianBlur` | `kernel_size` | 5 (fixed) |
| `GaussianBlur` | `sigma` | (0.1, 1.5) |
| `RandomHorizontalFlip` | `p` | 0.5 |
| `RandomGrayscale` | `p` | 0.1 |
| `RandomResizedCrop` | `scale` | (0.80, 1.00) |
| `RandomResizedCrop` | `ratio` | (0.90, 1.10) |
| Gaussian Noise | `sigma` | 0.03 (in normalised [0,1] space) |

All ranges are conservative. Start with these values; tighten if validation MAE worsens.

---

## Recommended Dataset Expansion Factor

### Dataset size context

- Total images: 791 (usable)
- Training set (80% of specimens, ~38 of 48): approximately 630 images
- Validation set (~4 specimens): approximately 65 images
- Test set (~6 specimens): approximately 96 images

### Literature basis

For medical image analysis and material inspection datasets of comparable size (500–2000 images), the literature consistently supports augmentation factors of **3× to 10×**, with diminishing returns typically observed beyond 5× for frozen backbone approaches and beyond 10× for fine-tuned models.

For datasets of this specific size (≈630 training images) with a frozen ImageNet backbone:
- **3× factor** (2 augmented copies per image, 1890 effective training images) is conservative and appropriate as a starting point.
- **5× factor** (4 augmented copies per image, 3150 effective training images) is the recommended target.
- **10× factor** (9 augmented copies per image) is likely excessive for a frozen backbone where the backbone weights do not update.

### Practical recommendation

**Use online augmentation (random per epoch), not offline pre-generated copies.**

Online augmentation produces effectively unlimited diversity because each epoch generates different random transforms. The "expansion factor" then corresponds to the number of training epochs: at 5× effective expansion with 120 epochs, the model sees approximately 600 distinct augmented versions of each image. This is preferable to saving 5× copies to disk (which would require 5× storage and reduce randomness).

**Recommended configuration:** 120 epochs, online augmentation applied at each batch, no pre-saved augmented images.

---

## Python Libraries

| Library | Purpose | Already in requirements |
|---|---|---|
| `torchvision.transforms.v2` | All primary augmentation transforms | Yes (`torchvision>=0.19` in `main_2/requirements.txt`) |
| `torch.utils.data.Dataset` | Custom dataset class with per-sample transforms | Yes |
| `PIL` (Pillow) | Image loading | Yes (`pillow>=11.0`) |
| `albumentations` | Optional: richer augmentation if `torchvision` is insufficient | No — add if needed |

No new library installations are required for the recommended augmentation set. All transforms (`ColorJitter`, `GaussianBlur`, `RandomHorizontalFlip`, `RandomGrayscale`, `RandomResizedCrop`) are available in `torchvision.transforms`.

---

## Implementation Plan

The current `main_2` architecture pre-extracts all embeddings before training. Augmentation requires changing this so that images are loaded and augmented on-the-fly during each training batch. Four files need changes; two new files need to be created.

### Step 1 — Create `main_2/augmentation.py` (new file)

Define training and inference transform pipelines:

```python
from torchvision import transforms

def get_train_transforms(image_size: int = 224) -> transforms.Compose:
    return transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.80, 1.00), ratio=(0.90, 1.10)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.RandomGrayscale(p=0.1),
        transforms.GaussianBlur(kernel_size=5, sigma=(0.1, 1.5)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        GaussianNoise(sigma=0.03),   # custom — see below
    ])

def get_inference_transforms(image_size: int = 224) -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

class GaussianNoise:
    def __init__(self, sigma: float = 0.03):
        self.sigma = sigma
    def __call__(self, tensor):
        return tensor + torch.randn_like(tensor) * self.sigma
```

---

### Step 2 — Create `main_2/dataset.py` (new file)

A `torch.utils.data.Dataset` that loads images on-the-fly and applies transforms per-sample. This replaces the current batch pre-extraction approach:

```python
class CorrosionImageDataset(Dataset):
    def __init__(self, image_paths, tabular_features, labels, transform):
        self.image_paths = image_paths
        self.tabular_features = tabular_features  # np.ndarray, shape (N, D)
        self.labels = labels                       # np.ndarray, shape (N,)
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert("RGB")
        img_tensor = self.transform(img)
        tab = torch.tensor(self.tabular_features[idx], dtype=torch.float32)
        label = torch.tensor(self.labels[idx], dtype=torch.float32)
        return img_tensor, tab, label
```

The `DataLoader` built from this dataset automatically applies a **different random augmentation** to each image at each epoch, giving online diversity without pre-saving files.

---

### Step 3 — Modify `main_2/data.py`

Replace `extract_resnet18_embeddings()` with two functions:

- `build_backbone(device)` → returns the frozen ResNet18 backbone
- `extract_embeddings_batch(backbone, image_tensors, device)` → used inside the training loop per-batch

The backbone remains frozen; only the MLP head trains. Per-batch embedding extraction inside the training loop allows augmented images to produce different embeddings each epoch.

---

### Step 4 — Modify `main_2/train_phase2.py`

Replace the pre-extraction pattern:

```python
# OLD (no augmentation, all embeddings computed once)
embeddings, corrupted_ids = extract_resnet18_embeddings(df, ...)
x_train = embeddings[idx_train]

# NEW (online augmentation, embeddings computed per-batch from augmented images)
train_dataset = CorrosionImageDataset(
    image_paths=df.iloc[idx_train]["image_path"].tolist(),
    tabular_features=tab_arr[idx_train],
    labels=y[idx_train],
    transform=get_train_transforms(),
)
val_dataset = CorrosionImageDataset(
    image_paths=df.iloc[idx_val]["image_path"].tolist(),
    tabular_features=tab_arr[idx_val],
    labels=y[idx_val],
    transform=get_inference_transforms(),     # no augmentation
)
test_dataset = CorrosionImageDataset(
    image_paths=df.iloc[idx_test]["image_path"].tolist(),
    tabular_features=tab_arr[idx_test],
    labels=y[idx_test],
    transform=get_inference_transforms(),     # no augmentation
)
```

The training loop calls `backbone(img_tensor_batch)` per-batch, passes resulting embeddings to the MLP, and backpropagates only through the MLP.

---

### Step 5 — Add `--no-augment` flag to `train_phase2.py`

This enables a clean ablation: run the same script twice, once with augmentation (`--augment`) and once without (`--no-augment`), to produce the DL-with/without comparison required by the professor.

```bash
# Without augmentation (current behaviour reproduced)
python -m main_2.train_phase2 --no-augment

# With augmentation (new)
python -m main_2.train_phase2 --augment
```

---

### Step 6 — Add `main_2/configs/augmentation.yaml`

Store all augmentation hyperparameters in a config file rather than hardcoding them:

```yaml
enabled: true
random_resized_crop:
  scale_min: 0.80
  scale_max: 1.00
  ratio_min: 0.90
  ratio_max: 1.10
horizontal_flip_p: 0.5
color_jitter:
  brightness: 0.2
  contrast: 0.2
  saturation: 0.2
  hue: 0.05
random_grayscale_p: 0.1
gaussian_blur:
  kernel_size: 5
  sigma_min: 0.1
  sigma_max: 1.5
gaussian_noise_sigma: 0.03
```

---

## Experimental Comparison

Three conditions must be evaluated and reported in the paper:

| Condition | Description | Expected output |
|---|---|---|
| **Baseline A** | Threshold red-color (`img_rust_area_ratio_pct`) from `main_4` | Already computed: MAE ≈ 0.0002 for `surface_total_rust_pct` (tautological), strip-based MAE ≈ 1.097 for `peak_rust_pct` |
| **Baseline B** | DL (ResNet18 frozen + MLP) without augmentation | Run `main_2/train_phase2.py --no-augment`. Current code produces this. |
| **Proposed** | DL (ResNet18 frozen + MLP) with augmentation | Run `main_2/train_phase2.py --augment`. New code. |

Primary metrics: **MAE**, **RMSE**, **R²**, **Spearman** for `peak_rust_pct`.

Secondary metrics (if downstream structural experiment runs): MAE and Spearman for `ultimate_load_kn` and `wire_area_loss_frac` under grouped holdout.

All three conditions must be evaluated under the **same specimen-grouped split** to ensure the comparison is fair. Report results for both grouped holdout (within-campaign) and LOCO (cross-campaign).

---

## Leakage Prevention

Augmentation introduces a specific leakage risk that must be explicitly controlled.

**Rule:** Augmented images must be derived only from training-fold specimens. Test-fold and validation-fold specimens must be evaluated using **only the original, unaugmented images** with the inference transform.

**Implementation:**
- The `CorrosionImageDataset` is instantiated separately for train, val, and test using indices from `build_group_splits()` in `main_2/data.py`.
- The train dataset receives `get_train_transforms()` (includes augmentation).
- The val and test datasets receive `get_inference_transforms()` (no augmentation).
- Augmented images from specimen X (train fold) never appear in the evaluation of specimen X's test-fold rows, because the two datasets are constructed from non-overlapping specimen indices.

**Embedding extraction for downstream use:** When extracting final embeddings to feed into `main_4`'s structural pipeline, use `get_inference_transforms()` (no augmentation) for all specimens, applied consistently. This ensures that the embeddings used for structural prediction are deterministic and not fold-dependent.

---

## How Augmented DL Features Could Feed Structural Prediction

### The connection

The `main_4` structural pipeline models `wire_area_loss_frac` and `ultimate_load_kn` from a 48-row terminal feature table (one row per specimen). These 48 rows currently use metadata-only features because image features did not improve LOCO performance.

DL embeddings represent a **different type of image feature** from the hand-crafted ones in `main_4`: instead of 77 explicit scalar features (rust area, texture, histograms), ResNet18 produces a 512-dimensional learned representation of the full image. After training with augmentation, this representation should capture structural patterns the threshold-based features miss.

### Integration path

1. After training the augmented DL model on surface targets, run `extract_embeddings_batch()` using `get_inference_transforms()` (no augmentation) on all 791 images to produce a 791×512 embedding matrix.

2. Aggregate embeddings to specimen level. Two strategies:
   - **Final time point only:** Take the embedding from the last available observation (week 28 or 36) for each specimen. This gives a 48×512 matrix matching the terminal structural table. Interpretable: "the appearance of the specimen just before structural testing."
   - **Mean across all time points:** Average the embeddings across all weeks per specimen. This gives a temporally integrated representation.

3. Apply PCA or a truncation to reduce 512 dimensions to a manageable number (e.g., top 20–50 components explaining ≥90% of variance) before joining to the structural feature table. With only 48 training rows, feeding 512 raw embedding dimensions would cause severe overfitting.

4. Join the reduced embedding features to `main_4`'s `terminal_structural_table.csv` on `specimen_id`.

5. Run the existing `train_hidden_damage_models.py` evaluation with a new feature set called `dl_embedding` (or `dl_metadata`) alongside the existing ablation sets.

### Hook point in `main_4`

`main_4/src/corrosion_proxy_rul/feature_engineering.py` — the `HIDDEN_DAMAGE_FEATURE_SETS` dictionary at the top of the file. Add a new entry:

```python
"dl_embedding_metadata": [
    # metadata features (already defined in metadata_only set)
    ...existing metadata_only columns...,
    # PCA-reduced DL embedding components
    "dl_emb_pc_0", "dl_emb_pc_1", ..., "dl_emb_pc_19",
]
```

The embedding components would be pre-computed and saved as additional columns in the terminal feature table, loaded by `data_loading.py` or joined in `feature_engineering.py`.

---

## Expected Results

### Surface targets (`peak_rust_pct`)

The ResNet18 without augmentation already has access to rich pretrained features. With augmentation:
- Grouped holdout MAE: modest improvement over no-augmentation DL baseline (5–15% reduction in MAE is typical for this dataset size).
- LOCO MAE: possible improvement, though campaign design confounding will limit gains.
- Comparison vs. threshold baseline: DL is expected to be competitive with or better than the strip-based threshold approach on `peak_rust_pct`, particularly for specimens with complex spatial rust distributions.

### Structural targets (`ultimate_load_kn`, `wire_area_loss_frac`)

Honest expectation: marginal improvement, if any, under LOCO. The 3.24× LOCO collapse for `ultimate_load_kn` is driven by campaign design confounding (n_steel_mesh, NaCl), not by feature quality. DL embeddings, regardless of augmentation, will learn the same campaign-correlated patterns. If DL embedding features improve grouped holdout but not LOCO, the interpretation is that the embeddings learned campaign-specific texture patterns. This is still a useful finding to report.

---

## Risks and Limitations

**Risk 1 — Per-batch backbone forward pass is slow without GPU.**
With the frozen ResNet18 called per-batch during training, training time increases significantly on CPU. On MPS (Apple Silicon) or CUDA, this is manageable (≈30–60 minutes per run for 120 epochs). On CPU it may take several hours. Mitigation: cache backbone embeddings for the unaugmented version and only recompute for augmented passes, or limit augmentation to a subset of epochs.

**Risk 2 — Augmented DL features may not improve structural LOCO.**
If the augmented DL embedding features are joined to the structural table and evaluated under LOCO, the same campaign confounding that limits classical features will also limit DL features. This is not a failure — it is an expected and scientifically meaningful result. Plan: report it honestly and note that the confounding is experimental, not methodological.

**Risk 3 — PCA truncation of embeddings may discard discriminative information.**
With 48 training samples for structural targets, PCA must be fit on the training fold only (not all 48 specimens), which leaves very few samples. If 20 PCA components are retained from 512 dimensions with only 38 training specimens, the components explain training-set variance, not necessarily structurally relevant variance. Mitigation: use a very conservative truncation (top 5–10 components) or a linear model (Ridge regression) on the full embedding — Ridge handles high-dimensional inputs with few samples better than tree-based models.

**Risk 4 — Augmentation may hurt the surface models if colour/hue jitter is too aggressive.**
If hue jitter pushes rust-coloured pixels outside the visually rust-like range, the augmented images may appear implausible. The DL model would then learn from inconsistent training examples. Mitigation: keep `hue=0.05` (small shift), validate that augmented images visually resemble realistic corrosion at varying stages.

---

## Final Checklist

Before running any experiment, verify:

- [ ] Images load correctly as RGBA and convert to RGB (`img.convert("RGB")`) — RGBA has transparency channel that must be removed before ResNet18 processing
- [ ] Training transforms are applied only to training-fold images (verified by checking that `get_inference_transforms()` is used for val and test `CorrosionImageDataset` instances)
- [ ] `build_group_splits()` in `main_2/data.py` is called before any dataset is constructed, so that indices are specimen-grouped
- [ ] The `--no-augment` and `--augment` runs use the same split (same `random_state`) for a valid comparison
- [ ] PCA for DL embedding reduction is fit on training specimens only and applied to test specimens — not fit on all 48
- [ ] LOCO results are reported alongside grouped-holdout results in all tables — never report grouped-holdout alone as the primary metric
- [ ] `main_2/configs/augmentation.yaml` exists and all transform parameters are read from config, not hardcoded
- [ ] Augmented images are never saved to disk in `Data/Images_dataset/` — augmentation is online only and never modifies the source dataset
