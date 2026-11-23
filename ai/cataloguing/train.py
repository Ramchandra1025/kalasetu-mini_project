"""
KalaSetu - AI Product Vision & Cataloguing
Model 1: EfficientNet-B0 Multi-Task Training

Tasks:
    1. Product Category Classification
    2. Material Classification
    3. Color Classification

IMPORTANT:
The current 12-image dataset is only for pipeline testing.
Its metrics must NOT be treated as research-grade results.
"""

import json
import random
import time

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from sklearn.metrics import accuracy_score, f1_score, classification_report

from ai.cataloguing.config import (
    DEVICE,
    NUM_EPOCHS,
    LEARNING_RATE,
    WEIGHT_DECAY,
    BEST_MODEL_PATH,
    LABEL_MAP_PATH,
    EXPERIMENT_DIR,
    RESULTS_DIR,
)

from ai.cataloguing.dataset import create_dataloaders
from ai.cataloguing.model import create_model


# ============================================================
# REPRODUCIBILITY
# ============================================================

RANDOM_SEED = 42


def set_seed(seed=RANDOM_SEED):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ============================================================
# SAVE LABEL MAPS
# ============================================================

def save_label_maps(label_maps):

    """
    Save label maps exactly as returned by dataset.py.
    """

    with open(
        LABEL_MAP_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            label_maps,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Label maps saved: {LABEL_MAP_PATH}"
    )


# ============================================================
# TRAIN ONE EPOCH
# ============================================================

def train_one_epoch(
    model,
    loader,
    optimizer,
    criterion
):

    model.train()

    total_loss = 0.0

    category_correct = 0
    material_correct = 0
    color_correct = 0

    total_samples = 0

    for batch in loader:

        # ----------------------------------------------------
        # Dataset returns dictionary
        # ----------------------------------------------------

        images = batch["image"]
        categories = batch["category"]
        materials = batch["material"]
        colors = batch["color"]

        # ----------------------------------------------------
        # Move tensors to device
        # ----------------------------------------------------

        images = images.to(DEVICE)
        categories = categories.to(DEVICE)
        materials = materials.to(DEVICE)
        colors = colors.to(DEVICE)

        # ----------------------------------------------------
        # Clear gradients
        # ----------------------------------------------------

        optimizer.zero_grad()

        # ----------------------------------------------------
        # Model returns dictionary
        # ----------------------------------------------------

        outputs = model(images)

        category_logits = outputs["category"]
        material_logits = outputs["material"]
        color_logits = outputs["color"]

        # ----------------------------------------------------
        # Individual task losses
        # ----------------------------------------------------

        category_loss = criterion(
            category_logits,
            categories
        )

        material_loss = criterion(
            material_logits,
            materials
        )

        color_loss = criterion(
            color_logits,
            colors
        )

        # ----------------------------------------------------
        # Combined multi-task loss
        # ----------------------------------------------------

        loss = (
            category_loss
            + material_loss
            + color_loss
        )

        # ----------------------------------------------------
        # Backpropagation
        # ----------------------------------------------------

        loss.backward()

        optimizer.step()

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        batch_size = images.size(0)

        total_loss += loss.item() * batch_size

        category_predictions = (
            category_logits.argmax(dim=1)
        )

        material_predictions = (
            material_logits.argmax(dim=1)
        )

        color_predictions = (
            color_logits.argmax(dim=1)
        )

        category_correct += (
            category_predictions == categories
        ).sum().item()

        material_correct += (
            material_predictions == materials
        ).sum().item()

        color_correct += (
            color_predictions == colors
        ).sum().item()

        total_samples += batch_size

    # --------------------------------------------------------
    # Prevent division by zero
    # --------------------------------------------------------

    if total_samples == 0:

        return {
            "loss": 0.0,
            "category_accuracy": 0.0,
            "material_accuracy": 0.0,
            "color_accuracy": 0.0
        }

    # --------------------------------------------------------
    # Return metrics
    # --------------------------------------------------------

    return {

        "loss":
            total_loss / total_samples,

        "category_accuracy":
            category_correct / total_samples,

        "material_accuracy":
            material_correct / total_samples,

        "color_accuracy":
            color_correct / total_samples
    }


# ============================================================
# VALIDATION
# ============================================================

def validate(
    model,
    loader,
    criterion
):

    model.eval()

    total_loss = 0.0

    category_correct = 0
    material_correct = 0
    color_correct = 0

    total_samples = 0

    with torch.no_grad():

        for batch in loader:

            # ------------------------------------------------
            # Dataset dictionary
            # ------------------------------------------------

            images = batch["image"]
            categories = batch["category"]
            materials = batch["material"]
            colors = batch["color"]

            # ------------------------------------------------
            # Move tensors
            # ------------------------------------------------

            images = images.to(DEVICE)
            categories = categories.to(DEVICE)
            materials = materials.to(DEVICE)
            colors = colors.to(DEVICE)

            # ------------------------------------------------
            # Model dictionary
            # ------------------------------------------------

            outputs = model(images)

            category_logits = outputs["category"]
            material_logits = outputs["material"]
            color_logits = outputs["color"]

            # ------------------------------------------------
            # Loss
            # ------------------------------------------------

            category_loss = criterion(
                category_logits,
                categories
            )

            material_loss = criterion(
                material_logits,
                materials
            )

            color_loss = criterion(
                color_logits,
                colors
            )

            loss = (
                category_loss
                + material_loss
                + color_loss
            )

            # ------------------------------------------------
            # Metrics
            # ------------------------------------------------

            batch_size = images.size(0)

            total_loss += (
                loss.item() * batch_size
            )

            category_predictions = (
                category_logits.argmax(dim=1)
            )

            material_predictions = (
                material_logits.argmax(dim=1)
            )

            color_predictions = (
                color_logits.argmax(dim=1)
            )

            category_correct += (
                category_predictions == categories
            ).sum().item()

            material_correct += (
                material_predictions == materials
            ).sum().item()

            color_correct += (
                color_predictions == colors
            ).sum().item()

            total_samples += batch_size

    # --------------------------------------------------------
    # Prevent division by zero
    # --------------------------------------------------------

    if total_samples == 0:

        return {
            "loss": 0.0,
            "category_accuracy": 0.0,
            "material_accuracy": 0.0,
            "color_accuracy": 0.0
        }

    return {

        "loss":
            total_loss / total_samples,

        "category_accuracy":
            category_correct / total_samples,

        "material_accuracy":
            material_correct / total_samples,

        "color_accuracy":
            color_correct / total_samples
    }


# ============================================================
# SAVE CHECKPOINT
# ============================================================

def save_checkpoint(
    model,
    optimizer,
    scheduler,
    epoch,
    validation_metrics,
    label_maps
):

    checkpoint = {

        "epoch":
            epoch,

        "model_state_dict":
            model.state_dict(),

        "optimizer_state_dict":
            optimizer.state_dict(),

        "scheduler_state_dict":
            scheduler.state_dict(),

        "validation_metrics":
            validation_metrics,

        "label_maps":
            label_maps,

        "architecture":
            "EfficientNet-B0",

        "model_type":
            "multi_task_cataloguing",

        "tasks": [
            "category",
            "material",
            "color"
        ],

        "device":
            str(DEVICE)
    }

    torch.save(
        checkpoint,
        BEST_MODEL_PATH
    )


# ============================================================
# SAVE TRAINING HISTORY
# ============================================================

def save_training_history(history):

    output_path = (
        RESULTS_DIR /
        "training_history.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Training history saved: {output_path}"
    )


# ============================================================
# SAVE EXPERIMENT SUMMARY
# ============================================================

def save_experiment_summary(
    history,
    label_maps,
    training_time
):

    output_path = (
        EXPERIMENT_DIR /
        "training_summary.json"
    )

    summary = {

        "experiment":
            "KalaSetu Cataloguing Model 1",

        "architecture":
            "EfficientNet-B0",

        "model_type":
            "Multi-task image classification",

        "tasks": [
            "Product Category",
            "Material",
            "Color"
        ],

        "device":
            str(DEVICE),

        "epochs":
            len(history["train"]),

        "training_time_seconds":
            training_time,

        "best_validation_loss":
            history["best_validation_loss"],

        "final_training_metrics":
            history["train"][-1],

        "final_validation_metrics":
            history["validation"][-1],

        "label_maps":
            label_maps,

        "research_warning":
            (
                "The current dataset contains only 12 images "
                "and is suitable for pipeline testing only. "
                "The resulting metrics must not be interpreted "
                "as research-grade generalization performance."
            )
    }

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Experiment summary saved: {output_path}"
    )


# ============================================================
# PRINT METRICS
# ============================================================

def print_metrics(
    epoch,
    train_metrics,
    validation_metrics,
    learning_rate
):

    print()
    print(
        f"Epoch {epoch} Results"
    )

    print("-" * 60)

    print(
        f"Learning Rate       : "
        f"{learning_rate:.8f}"
    )

    print(
        f"Train Loss          : "
        f"{train_metrics['loss']:.4f}"
    )

    print(
        f"Train Category Acc  : "
        f"{train_metrics['category_accuracy']:.4f}"
    )

    print(
        f"Train Material Acc  : "
        f"{train_metrics['material_accuracy']:.4f}"
    )

    print(
        f"Train Color Acc     : "
        f"{train_metrics['color_accuracy']:.4f}"
    )

    print(
        f"Validation Loss     : "
        f"{validation_metrics['loss']:.4f}"
    )

    print(
        f"Validation Category : "
        f"{validation_metrics['category_accuracy']:.4f}"
    )

    print(
        f"Validation Material : "
        f"{validation_metrics['material_accuracy']:.4f}"
    )

    print(
        f"Validation Color    : "
        f"{validation_metrics['color_accuracy']:.4f}"
    )

    print("-" * 60)


# ============================================================
# UNTOUCHED TEST-SET EVALUATION
# ============================================================

def evaluate_test_set(model, test_loader, label_maps):
    """Evaluate the best validation checkpoint exactly once on held-out test data."""
    try:
        checkpoint = torch.load(
            BEST_MODEL_PATH,
            map_location=DEVICE,
            weights_only=True,
        )
    except TypeError:
        checkpoint = torch.load(
            BEST_MODEL_PATH,
            map_location=DEVICE,
        )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    targets = {"category": [], "material": [], "color": []}
    predictions = {"category": [], "material": [], "color": []}
    with torch.inference_mode():
        for batch in test_loader:
            images = batch["image"].to(DEVICE)
            outputs = model(images)
            for task in targets:
                target = batch[task].cpu().numpy().tolist()
                predicted = outputs[task].argmax(dim=1).cpu().numpy().tolist()
                targets[task].extend(target)
                predictions[task].extend(predicted)

    report = {}
    for task in targets:
        report[task] = {
            "accuracy": float(accuracy_score(targets[task], predictions[task])),
            "macro_f1": float(f1_score(
                targets[task], predictions[task], average="macro", zero_division=0
            )),
            "classification_report": classification_report(
                targets[task], predictions[task], output_dict=True, zero_division=0
            ),
        }

    result = {
        "evaluation_type": "held_out_test_set",
        "dataset_images": sum(len(v) for v in targets.values()) // 3,
        "metrics": report,
        "research_valid": False,
        "warning": (
            "Current dataset is only a 12-image pipeline test. "
            "These metrics are not evidence of generalization or real-world accuracy."
        ),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "held_out_test_evaluation.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)
    print(f"Held-out test evaluation saved: {output_path}")
    print(json.dumps({
        task: {"accuracy": values["accuracy"], "macro_f1": values["macro_f1"]}
        for task, values in report.items()
    }, indent=2))
    return result


# ============================================================
# MAIN TRAINING
# ============================================================

def train():

    print()
    print("=" * 60)
    print("KalaSetu Cataloguing Model Training")
    print("=" * 60)

    print()
    print(
        f"Device        : {DEVICE}"
    )

    print(
        f"Epochs        : {NUM_EPOCHS}"
    )

    print(
        f"Learning Rate : {LEARNING_RATE}"
    )

    print(
        f"Weight Decay  : {WEIGHT_DECAY}"
    )

    print()
    print("IMPORTANT:")

    print(
        "The current 12-image dataset is for "
        "pipeline testing only."
    )

    print(
        "Do not use these results as research-grade "
        "accuracy claims."
    )

    # --------------------------------------------------------
    # Reproducibility
    # --------------------------------------------------------

    set_seed()

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Loading Dataset")
    print("=" * 60)

    (
        train_loader,
        val_loader,
        test_loader,
        label_maps
    ) = create_dataloaders()

    # --------------------------------------------------------
    # Save label maps
    # --------------------------------------------------------

    save_label_maps(
        label_maps
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Creating Model")
    print("=" * 60)

    model = create_model()

    model = model.to(DEVICE)

    # --------------------------------------------------------
    # Loss function
    # --------------------------------------------------------

    criterion = nn.CrossEntropyLoss()

    # --------------------------------------------------------
    # Optimizer
    # --------------------------------------------------------

    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    # --------------------------------------------------------
    # Scheduler
    # --------------------------------------------------------

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=2
    )

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------

    history = {

        "train": [],

        "validation": [],

        "best_validation_loss": None
    }

    best_validation_loss = float("inf")

    # --------------------------------------------------------
    # Timer
    # --------------------------------------------------------

    start_time = time.time()

    # --------------------------------------------------------
    # Epoch loop
    # --------------------------------------------------------

    for epoch in range(
        1,
        NUM_EPOCHS + 1
    ):

        print()
        print("-" * 60)

        print(
            f"Epoch {epoch}/{NUM_EPOCHS}"
        )

        print("-" * 60)

        # ----------------------------------------------------
        # Train
        # ----------------------------------------------------

        train_metrics = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            criterion=criterion
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        validation_metrics = validate(
            model=model,
            loader=val_loader,
            criterion=criterion
        )

        # ----------------------------------------------------
        # Scheduler
        # ----------------------------------------------------

        scheduler.step(
            validation_metrics["loss"]
        )

        # ----------------------------------------------------
        # Current LR
        # ----------------------------------------------------

        current_lr = (
            optimizer.param_groups[0]["lr"]
        )

        # ----------------------------------------------------
        # History
        # ----------------------------------------------------

        history["train"].append(
            train_metrics
        )

        history["validation"].append(
            validation_metrics
        )

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        print_metrics(
            epoch=epoch,
            train_metrics=train_metrics,
            validation_metrics=validation_metrics,
            learning_rate=current_lr
        )

        # ----------------------------------------------------
        # Best checkpoint
        # ----------------------------------------------------

        current_validation_loss = (
            validation_metrics["loss"]
        )

        if current_validation_loss < best_validation_loss:

            best_validation_loss = (
                current_validation_loss
            )

            history["best_validation_loss"] = (
                best_validation_loss
            )

            save_checkpoint(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                epoch=epoch,
                validation_metrics=validation_metrics,
                label_maps=label_maps
            )

            print()
            print(
                "✓ New best model saved."
            )

            print(
                f"  Validation loss: "
                f"{best_validation_loss:.4f}"
            )

            print(
                f"  Path: {BEST_MODEL_PATH}"
            )

    # Evaluate the best validation-selected checkpoint on the untouched test set.
    test_evaluation = evaluate_test_set(model, test_loader, label_maps)

    # --------------------------------------------------------
    # Training complete
    # --------------------------------------------------------

    training_time = (
        time.time() -
        start_time
    )

    print()
    print("=" * 60)
    print("Training Completed")
    print("=" * 60)

    print(
        f"Training time: "
        f"{training_time:.2f} seconds"
    )

    print(
        f"Best validation loss: "
        f"{best_validation_loss:.4f}"
    )

    # --------------------------------------------------------
    # Save history
    # --------------------------------------------------------

    save_training_history(
        history
    )

    # --------------------------------------------------------
    # Save experiment summary
    # --------------------------------------------------------

    save_experiment_summary(
        history=history,
        label_maps=label_maps,
        training_time=training_time
    )

    # --------------------------------------------------------
    # Generated files
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Generated Files")
    print("=" * 60)

    print(
        f"Best model : {BEST_MODEL_PATH}"
    )

    print(
        f"Label maps : {LABEL_MAP_PATH}"
    )

    print(
        f"History    : "
        f"{RESULTS_DIR / 'training_history.json'}"
    )

    print(
        f"Summary    : "
        f"{EXPERIMENT_DIR / 'training_summary.json'}"
    )

    print()
    print("=" * 60)
    print("RESEARCH NOTE")
    print("=" * 60)

    print(
        "The current dataset contains only 12 images."
    )

    print(
        "Successful training means the ML pipeline works."
    )

    print(
        "It does NOT establish real-world model accuracy."
    )

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    train()