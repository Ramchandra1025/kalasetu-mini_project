"""
KalaSetu - AI Product Vision & Cataloguing
EfficientNet-B0 Multi-Head Model

Heads:
    1. Category
    2. Material
    3. Color
"""

import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

from .config import (
    CATEGORIES,
    MATERIALS,
    COLORS,
    DROPOUT,
    PRETRAINED,
    DEVICE,
)


class CataloguingModel(nn.Module):
    """
    EfficientNet-B0 backbone with three classification heads.

    Input:
        [batch_size, 3, 224, 224]

    Outputs:
        category_logits
        material_logits
        color_logits
    """

    def __init__(
        self,
        num_categories=None,
        num_materials=None,
        num_colors=None,
        pretrained=PRETRAINED,
        dropout=DROPOUT,
    ):
        super().__init__()

        num_categories = (
            num_categories
            if num_categories is not None
            else len(CATEGORIES)
        )

        num_materials = (
            num_materials
            if num_materials is not None
            else len(MATERIALS)
        )

        num_colors = (
            num_colors
            if num_colors is not None
            else len(COLORS)
        )

        # ---------------------------------------------------------
        # EfficientNet-B0 backbone
        # ---------------------------------------------------------
        if pretrained:
            try:
                weights = EfficientNet_B0_Weights.DEFAULT
                backbone = efficientnet_b0(weights=weights)
                print("Loaded EfficientNet-B0 pretrained weights.")
            except Exception as error:
                print()
                print("WARNING: Could not load pretrained weights.")
                print(f"Reason: {error}")
                print("Falling back to randomly initialized weights.")
                print()
                backbone = efficientnet_b0(weights=None)
        else:
            backbone = efficientnet_b0(weights=None)

        # EfficientNet-B0 classifier input size
        feature_dim = backbone.classifier[1].in_features

        # Remove original ImageNet classifier
        backbone.classifier = nn.Identity()

        self.backbone = backbone

        self.dropout = nn.Dropout(dropout)

        # ---------------------------------------------------------
        # Classification heads
        # ---------------------------------------------------------
        self.category_head = nn.Linear(
            feature_dim,
            num_categories
        )

        self.material_head = nn.Linear(
            feature_dim,
            num_materials
        )

        self.color_head = nn.Linear(
            feature_dim,
            num_colors
        )

        self.feature_dim = feature_dim

        self.num_categories = num_categories
        self.num_materials = num_materials
        self.num_colors = num_colors

    def forward(self, x):
        """
        Forward pass.

        Returns:
            Dictionary containing logits for all three tasks.
        """

        features = self.backbone(x)

        features = self.dropout(features)

        category_logits = self.category_head(features)
        material_logits = self.material_head(features)
        color_logits = self.color_head(features)

        return {
            "category": category_logits,
            "material": material_logits,
            "color": color_logits,
        }

    def extract_features(self, x):
        """
        Extract the shared EfficientNet feature representation.
        Useful later for:
            - craft verification
            - similarity search
            - buyer recommendation
            - product embeddings
        """

        features = self.backbone(x)

        return features


def create_model(pretrained=PRETRAINED, device=DEVICE):
    """
    Create and move the cataloguing model to the selected device.
    """

    model = CataloguingModel(
        num_categories=len(CATEGORIES),
        num_materials=len(MATERIALS),
        num_colors=len(COLORS),
        pretrained=pretrained,
        dropout=DROPOUT,
    )

    model = model.to(device)

    return model


def count_parameters(model):
    """
    Count total and trainable parameters.
    """

    total = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return total, trainable


def test_model():
    """
    Basic architecture test.
    """

    print()
    print("=" * 60)
    print("Testing KalaSetu Cataloguing Model")
    print("=" * 60)

    print()
    print("Creating model...")

    model = create_model(
        pretrained=PRETRAINED,
        device=DEVICE,
    )

    model.eval()

    total_params, trainable_params = count_parameters(model)

    print()
    print("Model Information")
    print("-" * 60)
    print(f"Architecture       : EfficientNet-B0")
    print(f"Feature dimension   : {model.feature_dim}")
    print(f"Category classes    : {model.num_categories}")
    print(f"Material classes    : {model.num_materials}")
    print(f"Color classes       : {model.num_colors}")
    print(f"Device              : {DEVICE}")
    print(f"Total parameters    : {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")

    # ---------------------------------------------------------
    # Dummy image
    # ---------------------------------------------------------
    print()
    print("Testing forward pass...")

    dummy_input = torch.randn(
        2,
        3,
        224,
        224,
        device=DEVICE,
    )

    with torch.no_grad():
        outputs = model(dummy_input)

    print()
    print("Input shape")
    print(f"  {tuple(dummy_input.shape)}")

    print()
    print("Output shapes")

    print(
        f"  Category : "
        f"{tuple(outputs['category'].shape)}"
    )

    print(
        f"  Material : "
        f"{tuple(outputs['material'].shape)}"
    )

    print(
        f"  Color    : "
        f"{tuple(outputs['color'].shape)}"
    )

    # ---------------------------------------------------------
    # Verify expected dimensions
    # ---------------------------------------------------------
    assert outputs["category"].shape == (
        2,
        len(CATEGORIES),
    )

    assert outputs["material"].shape == (
        2,
        len(MATERIALS),
    )

    assert outputs["color"].shape == (
        2,
        len(COLORS),
    )

    print()
    print("=" * 60)
    print("MODEL TEST PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    test_model()