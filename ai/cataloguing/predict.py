
"""
KalaSetu - AI Product Vision & Cataloguing
Model 1: Product Image Prediction

Input:
    Image path OR uploaded image bytes

Output:
    Category, material, color, and confidence scores

Research note:
    The model has been trained on a very small dataset.
    Predictions are experimental, not production-validated.
"""

import argparse
import io
import json
from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

from ai.cataloguing.config import (
    DEVICE,
    BEST_MODEL_PATH,
    LABEL_MAP_PATH,
    IMAGE_SIZE,
)
from ai.cataloguing.model import create_model


MODEL_NAME = "EfficientNet-B0"
TRAINING_IMAGE_COUNT = 12


# ============================================================
# IMAGE TRANSFORM
# ============================================================

def get_transform():
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


# ============================================================
# LABEL MAPS
# ============================================================

@lru_cache(maxsize=1)
def load_label_maps():
    label_map_path = Path(LABEL_MAP_PATH)

    if not label_map_path.exists():
        raise FileNotFoundError(
            f"Label map not found: {label_map_path}"
        )

    with label_map_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def reverse_map(label_map):
    return {
        int(index): label
        for label, index in label_map.items()
    }


# ============================================================
# LOAD TRAINED MODEL ONCE PER BACKEND PROCESS
# ============================================================

@lru_cache(maxsize=1)
def load_model():
    model_path = Path(BEST_MODEL_PATH)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained cataloguing model not found: {model_path}"
        )

    # Avoid downloading pretrained weights when loading
    # the already-trained project checkpoint.
    model = create_model(pretrained=False, device=DEVICE)

    # weights_only is supported by modern PyTorch versions.
    # The fallback supports older versions that lack this argument.
    try:
        checkpoint = torch.load(
            model_path,
            map_location=DEVICE,
            weights_only=True,
        )
    except TypeError:
        checkpoint = torch.load(
            model_path,
            map_location=DEVICE,
        )

    if (
        isinstance(checkpoint, dict)
        and "model_state_dict" in checkpoint
    ):
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint

    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()

    return model


# ============================================================
# PREDICTION HELPERS
# ============================================================

def predict_output(logits, index_to_label):
    probabilities = torch.softmax(logits, dim=1)
    confidence, prediction = probabilities.max(dim=1)

    predicted_index = prediction.item()

    if predicted_index not in index_to_label:
        raise ValueError(
            f"Prediction index {predicted_index} is missing "
            "from the label map."
        )

    return {
        "label": index_to_label[predicted_index],
        "confidence": float(confidence.item()),
    }


def predict_pil_image(image):
    """Run cataloguing inference on an already-open PIL image."""

    image = image.convert("RGB")
    image_tensor = get_transform()(image)
    image_tensor = image_tensor.unsqueeze(0).to(DEVICE)

    model = load_model()
    label_maps = load_label_maps()

    category_index_to_label = reverse_map(
        label_maps["category_to_index"]
    )
    material_index_to_label = reverse_map(
        label_maps["material_to_index"]
    )
    color_index_to_label = reverse_map(
        label_maps["color_to_index"]
    )

    with torch.inference_mode():
        outputs = model(image_tensor)

    return {
        "model": MODEL_NAME,
        "category": predict_output(
            outputs["category"],
            category_index_to_label,
        ),
        "material": predict_output(
            outputs["material"],
            material_index_to_label,
        ),
        "color": predict_output(
            outputs["color"],
            color_index_to_label,
        ),
        "experimental": True,
        "training_images": TRAINING_IMAGE_COUNT,
    }


# ============================================================
# FLASK INTEGRATION: UPLOADED IMAGE BYTES
# ============================================================

def predict_image_bytes(image_bytes):
    """
    Accept image bytes from a Flask upload or in-memory buffer.

    Returns predictions without requiring a temporary file.
    Raises ValueError for invalid image data.
    """

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            result = predict_pil_image(image)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(
            "The uploaded file is not a valid supported image."
        ) from exc

    result["status"] = "completed"
    return result


# ============================================================
# COMMAND-LINE IMAGE PREDICTION
# ============================================================

def predict_image(image_path):
    image_path = Path(image_path)

    if not image_path.is_file():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    try:
        with Image.open(image_path) as image:
            result = predict_pil_image(image)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(
            f"Unable to open image: {image_path}"
        ) from exc

    result["image"] = str(image_path)
    return result


# ============================================================
# PRINT RESULTS
# ============================================================

def print_result(result):
    print("\n" + "=" * 60)
    print("KalaSetu AI Product Cataloguing Prediction")
    print("=" * 60)

    if "image" in result:
        print(f"Image: {result['image']}")

    for key, title in (
        ("category", "CATEGORY"),
        ("material", "MATERIAL"),
        ("color", "COLOR"),
    ):
        prediction = result[key]
        print(f"\n{title}")
        print(f"  Prediction : {prediction['label']}")
        print(f"  Confidence : {prediction['confidence']:.2%}")

    print("\n" + "=" * 60)
    print("RESEARCH NOTE")
    print(
        f"The current model has been reported as trained on "
        f"{TRAINING_IMAGE_COUNT} pipeline-testing images."
    )
    print(
        "Predictions are experimental. Confidence scores are "
        "model outputs, not proof of real-world accuracy."
    )
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="KalaSetu Product Cataloguing Prediction"
    )
    parser.add_argument(
        "image",
        help="Path to the product image",
    )
    args = parser.parse_args()

    print_result(predict_image(args.image))


if __name__ == "__main__":
    main()
