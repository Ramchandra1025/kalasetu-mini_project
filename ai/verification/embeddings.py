from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms

from .config import (
    DEVICE,
    IMAGE_SIZE,
    IMAGE_MEAN,
    IMAGE_STD,
    MODEL_NAME,
    PRETRAINED,
    EMBEDDING_DIMENSION,
)


# ============================================================
# IMAGE TRANSFORM
# ============================================================

embedding_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=IMAGE_MEAN,
        std=IMAGE_STD,
    ),
])


# ============================================================
# EFFICIENTNET-B0 EMBEDDING ENCODER
# ============================================================

class CraftEmbeddingEncoder(nn.Module):

    def __init__(
        self,
        pretrained: bool = PRETRAINED,
    ):
        super().__init__()

        if MODEL_NAME != "efficientnet_b0":
            raise ValueError(
                f"Unsupported model: {MODEL_NAME}"
            )

        # Use the same pretrained EfficientNet-B0
        # family used by Model 1.
        weights = (
            models.EfficientNet_B0_Weights.DEFAULT
            if pretrained
            else None
        )

        backbone = models.efficientnet_b0(
            weights=weights
        )

        # EfficientNet feature extractor.
        self.features = backbone.features

        # EfficientNet-B0 uses adaptive average pooling
        # before the classifier.
        self.pool = backbone.avgpool

        # Remove the original classification layer.
        self.classifier = nn.Identity()

        self.embedding_dimension = (
            EMBEDDING_DIMENSION
        )

    def forward(self, x):

        x = self.features(x)

        x = self.pool(x)

        x = torch.flatten(
            x,
            start_dim=1
        )

        # L2 normalization makes cosine similarity
        # more stable and directly usable.
        x = F.normalize(
            x,
            p=2,
            dim=1,
        )

        return x


# ============================================================
# LOAD ENCODER
# ============================================================

def create_encoder():

    encoder = CraftEmbeddingEncoder(
        pretrained=PRETRAINED
    )

    encoder = encoder.to(DEVICE)

    encoder.eval()

    return encoder


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(
    image_path: str | Path,
) -> torch.Tensor:

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found:\n{image_path}"
        )

    try:
        image = Image.open(
            image_path
        ).convert("RGB")

    except Exception as exc:

        raise RuntimeError(
            f"Could not load image:\n{image_path}"
        ) from exc

    image = embedding_transform(
        image
    )

    # Add batch dimension.
    image = image.unsqueeze(0)

    return image.to(DEVICE)


# ============================================================
# GENERATE SINGLE IMAGE EMBEDDING
# ============================================================

@torch.no_grad()
def generate_embedding(
    encoder: CraftEmbeddingEncoder,
    image_path: str | Path,
) -> torch.Tensor:

    image = load_image(
        image_path
    )

    embedding = encoder(
        image
    )

    return embedding.squeeze(0).cpu()


# ============================================================
# GENERATE EMBEDDINGS FOR MULTIPLE IMAGES
# ============================================================

@torch.no_grad()
def generate_embeddings(
    encoder: CraftEmbeddingEncoder,
    image_paths: List[Path],
) -> torch.Tensor:

    if not image_paths:
        return torch.empty(
            (0, EMBEDDING_DIMENSION)
        )

    images = []

    for image_path in image_paths:

        image = Image.open(
            image_path
        ).convert("RGB")

        image = embedding_transform(
            image
        )

        images.append(image)

    batch = torch.stack(
        images
    ).to(DEVICE)

    embeddings = encoder(
        batch
    )

    return embeddings.cpu()


# ============================================================
# EMBEDDING INFORMATION
# ============================================================

def print_embedding_info(
    embedding: torch.Tensor,
):

    print("=" * 60)
    print("KALASETU - CRAFT EMBEDDING")
    print("=" * 60)

    print(
        f"Embedding shape : "
        f"{tuple(embedding.shape)}"
    )

    print(
        f"Embedding size  : "
        f"{embedding.numel()}"
    )

    print(
        f"Minimum value   : "
        f"{embedding.min().item():.6f}"
    )

    print(
        f"Maximum value   : "
        f"{embedding.max().item():.6f}"
    )

    norm = torch.norm(
        embedding,
        p=2,
    ).item()

    print(
        f"L2 norm         : "
        f"{norm:.6f}"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("KALASETU - CRAFT VERIFICATION EMBEDDING ENGINE")
    print("=" * 60)

    print(
        f"Model  : {MODEL_NAME}"
    )

    print(
        f"Device : {DEVICE}"
    )

    print(
        f"Pretrained : {PRETRAINED}"
    )

    print(
        "\nLoading encoder..."
    )

    encoder = create_encoder()

    print(
        "Encoder loaded successfully."
    )

    print(
        f"Embedding dimension: "
        f"{encoder.embedding_dimension}"
    )

    # --------------------------------------------------------
    # Create a synthetic test tensor.
    # This avoids requiring a real dataset image.
    # --------------------------------------------------------

    print(
        "\nRunning forward-pass test..."
    )

    dummy_image = torch.randn(
        1,
        3,
        IMAGE_SIZE,
        IMAGE_SIZE,
    ).to(DEVICE)

    with torch.no_grad():

        embedding = encoder(
            dummy_image
        )

    print_embedding_info(
        embedding
    )

    # --------------------------------------------------------
    # Verify output shape.
    # --------------------------------------------------------

    expected_shape = (
        1,
        EMBEDDING_DIMENSION
    )

    actual_shape = tuple(
        embedding.shape
    )

    if actual_shape != expected_shape:

        raise RuntimeError(
            f"Unexpected embedding shape. "
            f"Expected {expected_shape}, "
            f"got {actual_shape}"
        )

    print(
        "\nEmbedding engine test PASSED."
    )