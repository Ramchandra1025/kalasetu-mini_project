from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from .config import (
    REFERENCE_DIR,
    IMAGE_SIZE,
    IMAGE_MEAN,
    IMAGE_STD,
    CRAFT_CATEGORIES,
)


# ============================================================
# SUPPORTED IMAGE EXTENSIONS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# ============================================================
# IMAGE TRANSFORMS
# ============================================================

image_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=IMAGE_MEAN,
        std=IMAGE_STD
    ),
])


# ============================================================
# REFERENCE IMAGE DATASET
# ============================================================

class CraftReferenceDataset(Dataset):

    def __init__(
        self,
        image_paths: List[Path],
        labels: List[str],
        transform=None,
    ):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

        if len(self.image_paths) != len(self.labels):
            raise ValueError(
                "Number of image paths and labels must match."
            )

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, index):

        image_path = self.image_paths[index]
        label = self.labels[index]

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as exc:
            raise RuntimeError(
                f"Could not load image: {image_path}"
            ) from exc

        if self.transform:
            image = self.transform(image)

        return {
            "image": image,
            "label": label,
            "path": str(image_path),
        }


# ============================================================
# SCAN REFERENCE DIRECTORY
# ============================================================

def scan_reference_images(
    reference_dir: Path = REFERENCE_DIR,
) -> Tuple[List[Path], List[str]]:

    image_paths = []
    labels = []

    if not reference_dir.exists():
        raise FileNotFoundError(
            f"Reference directory does not exist:\n"
            f"{reference_dir}"
        )

    for category in CRAFT_CATEGORIES:

        category_dir = reference_dir / category

        if not category_dir.exists():
            print(
                f"WARNING: Missing category directory: "
                f"{category_dir}"
            )
            continue

        for image_path in sorted(category_dir.iterdir()):

            if not image_path.is_file():
                continue

            if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            # Validate image before adding it.
            try:
                with Image.open(image_path) as image:
                    image.verify()
            except Exception:
                print(
                    f"WARNING: Invalid image skipped: "
                    f"{image_path}"
                )
                continue

            image_paths.append(image_path)
            labels.append(category)

    return image_paths, labels


# ============================================================
# CREATE REFERENCE DATALOADER
# ============================================================

def create_reference_dataloader(
    batch_size: int = 4,
):

    image_paths, labels = scan_reference_images()

    if not image_paths:
        raise RuntimeError(
            "No reference images found.\n\n"
            "Expected structure:\n"
            "ml/datasets/verification/reference/\n"
            "    wood_craft/\n"
            "    textile/\n"
            "    pottery/\n"
            "    metal_craft/\n"
        )

    dataset = CraftReferenceDataset(
        image_paths=image_paths,
        labels=labels,
        transform=image_transform,
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    return loader


# ============================================================
# DATASET SUMMARY
# ============================================================

def print_dataset_summary(
    image_paths: List[Path],
    labels: List[str],
):

    print("=" * 60)
    print("KALASETU - CRAFT VERIFICATION DATASET")
    print("=" * 60)

    print(f"Total reference images: {len(image_paths)}")

    print("\nImages by craft category:")

    for category in CRAFT_CATEGORIES:

        count = labels.count(category)

        print(
            f"  {category:<15}: {count}"
        )

    print("\nReference directory:")
    print(f"  {REFERENCE_DIR}")

    print("\nDataset scan PASSED.")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    paths, labels = scan_reference_images()

    print_dataset_summary(
        paths,
        labels,
    )

    if paths:

        print("\nSample images:")

        for path, label in list(
            zip(paths, labels)
        )[:10]:

            print(
                f"  {label:<15} -> {path.name}"
            )