from pathlib import Path
import random

import numpy as np
import pandas as pd
import torch

from PIL import Image, UnidentifiedImageError

from torch.utils.data import Dataset, DataLoader

from torchvision import transforms

from sklearn.model_selection import train_test_split

from .config import (
    DATASET_CSV,
    IMAGE_DIR,
    IMAGE_SIZE,
    BATCH_SIZE,
    TRAIN_RATIO,
    VALIDATION_RATIO,
    TEST_RATIO,
    RANDOM_SEED,
)


# ============================================================
# KalaSetu
# AI Product Vision & Cataloguing
#
# Dataset Pipeline
# ============================================================


# ------------------------------------------------------------
# Reproducibility
# ------------------------------------------------------------

def set_seed(seed=RANDOM_SEED):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ------------------------------------------------------------
# Image normalization
# ------------------------------------------------------------

IMAGENET_MEAN = [
    0.485,
    0.456,
    0.406,
]

IMAGENET_STD = [
    0.229,
    0.224,
    0.225,
]


# ------------------------------------------------------------
# Training transformations
# ------------------------------------------------------------

def get_train_transform():

    return transforms.Compose([

        transforms.Resize(
            (IMAGE_SIZE, IMAGE_SIZE)
        ),

        transforms.RandomHorizontalFlip(
            p=0.5
        ),

        transforms.RandomRotation(
            degrees=10
        ),

        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
        ),

        transforms.ToTensor(),

        transforms.Normalize(
            mean=IMAGENET_MEAN,
            std=IMAGENET_STD,
        ),
    ])


# ------------------------------------------------------------
# Validation / test transformations
# ------------------------------------------------------------

def get_eval_transform():

    return transforms.Compose([

        transforms.Resize(
            (IMAGE_SIZE, IMAGE_SIZE)
        ),

        transforms.ToTensor(),

        transforms.Normalize(
            mean=IMAGENET_MEAN,
            std=IMAGENET_STD,
        ),
    ])


# ============================================================
# Dataset validation
# ============================================================

REQUIRED_COLUMNS = [
    "image",
    "category",
    "material",
    "color",
]


def load_and_validate_dataframe():

    print()
    print("=" * 60)
    print("Loading KalaSetu Cataloguing Dataset")
    print("=" * 60)


    # --------------------------------------------------------
    # Check CSV
    # --------------------------------------------------------

    if not DATASET_CSV.exists():

        raise FileNotFoundError(
            f"\nDataset CSV was not found:\n"
            f"{DATASET_CSV}\n\n"
            f"Create the CSV before continuing."
        )


    dataframe = pd.read_csv(
        DATASET_CSV
    )


    print(
        f"CSV loaded: {len(dataframe)} rows"
    )


    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]


    if missing_columns:

        raise ValueError(
            "\nMissing required columns:\n"
            + "\n".join(
                f"  - {column}"
                for column in missing_columns
            )
        )


    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    dataframe = dataframe.dropna(
        subset=REQUIRED_COLUMNS
    ).copy()


    # --------------------------------------------------------
    # Clean whitespace
    # --------------------------------------------------------

    for column in REQUIRED_COLUMNS:

        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
        )


    # --------------------------------------------------------
    # Validate image paths
    # --------------------------------------------------------

    missing_images = []

    invalid_images = []

    valid_rows = []


    for index, row in dataframe.iterrows():

        relative_path = Path(
            row["image"]
        )

        image_path = (
            IMAGE_DIR
            / relative_path
        )


        # --------------------------------------------
        # File existence
        # --------------------------------------------

        if not image_path.exists():

            missing_images.append(
                str(image_path)
            )

            continue


        if not image_path.is_file():

            missing_images.append(
                str(image_path)
            )

            continue


        # --------------------------------------------
        # Try opening the image
        # --------------------------------------------

        try:

            with Image.open(image_path) as image:

                image.verify()


        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ):

            invalid_images.append(
                str(image_path)
            )

            continue


        valid_rows.append(index)


    # --------------------------------------------------------
    # Report missing images
    # --------------------------------------------------------

    if missing_images:

        print()
        print(
            f"WARNING: {len(missing_images)} image(s) "
            f"were not found."
        )

        for path in missing_images:

            print(
                f"  Missing: {path}"
            )


    # --------------------------------------------------------
    # Report invalid images
    # --------------------------------------------------------

    if invalid_images:

        print()
        print(
            f"WARNING: {len(invalid_images)} "
            f"invalid image(s) found."
        )

        for path in invalid_images:

            print(
                f"  Invalid: {path}"
            )


    # --------------------------------------------------------
    # Keep only valid images
    # --------------------------------------------------------

    dataframe = dataframe.loc[
        valid_rows
    ].reset_index(drop=True)


    if len(dataframe) == 0:

        raise ValueError(
            "\nNo valid images remain in the dataset."
        )


    # --------------------------------------------------------
    # Check labels
    # --------------------------------------------------------

    for column in [
        "category",
        "material",
        "color",
    ]:

        unique_values = sorted(
            dataframe[column]
            .unique()
            .tolist()
        )

        print(
            f"{column.capitalize():10}: "
            f"{len(unique_values)} classes"
        )

        for value in unique_values:

            count = (
                dataframe[column] == value
            ).sum()

            print(
                f"    {value}: {count}"
            )


    print()
    print(
        f"Valid images: {len(dataframe)}"
    )

    print("=" * 60)
    print()


    return dataframe


# ============================================================
# Label mappings
# ============================================================

def create_label_maps(dataframe):

    categories = sorted(
        dataframe["category"]
        .unique()
        .tolist()
    )

    materials = sorted(
        dataframe["material"]
        .unique()
        .tolist()
    )

    colors = sorted(
        dataframe["color"]
        .unique()
        .tolist()
    )


    category_to_index = {
        label: index
        for index, label in enumerate(
            categories
        )
    }


    material_to_index = {
        label: index
        for index, label in enumerate(
            materials
        )
    }


    color_to_index = {
        label: index
        for index, label in enumerate(
            colors
        )
    }


    index_to_category = {
        index: label
        for label, index
        in category_to_index.items()
    }


    index_to_material = {
        index: label
        for label, index
        in material_to_index.items()
    }


    index_to_color = {
        index: label
        for label, index
        in color_to_index.items()
    }


    return {
        "category_to_index": category_to_index,
        "material_to_index": material_to_index,
        "color_to_index": color_to_index,

        "index_to_category": index_to_category,
        "index_to_material": index_to_material,
        "index_to_color": index_to_color,
    }


# ============================================================
# PyTorch Dataset
# ============================================================

class CataloguingDataset(Dataset):

    def __init__(
        self,
        dataframe,
        label_maps,
        training=False,
    ):

        self.dataframe = (
            dataframe
            .reset_index(drop=True)
        )

        self.label_maps = label_maps

        self.training = training


        if training:

            self.transform = (
                get_train_transform()
            )

        else:

            self.transform = (
                get_eval_transform()
            )


    def __len__(self):

        return len(
            self.dataframe
        )


    def __getitem__(self, index):

        row = self.dataframe.iloc[
            index
        ]


        image_path = (
            IMAGE_DIR
            / row["image"]
        )


        try:

            image = Image.open(
                image_path
            ).convert("RGB")

        except Exception as error:

            raise RuntimeError(
                f"Unable to load image:\n"
                f"{image_path}\n"
                f"Error: {error}"
            )


        image = self.transform(
            image
        )


        category_index = (
            self.label_maps[
                "category_to_index"
            ][
                row["category"]
            ]
        )


        material_index = (
            self.label_maps[
                "material_to_index"
            ][
                row["material"]
            ]
        )


        color_index = (
            self.label_maps[
                "color_to_index"
            ][
                row["color"]
            ]
        )


        return {
            "image": image,

            "category": torch.tensor(
                category_index,
                dtype=torch.long,
            ),

            "material": torch.tensor(
                material_index,
                dtype=torch.long,
            ),

            "color": torch.tensor(
                color_index,
                dtype=torch.long,
            ),
        }


# ============================================================
# Dataset splitting
# ============================================================

def split_dataframe(dataframe):

    if len(dataframe) < 3:

        raise ValueError(
            "At least 3 valid images are required "
            "to create train/validation/test splits."
        )


    train_size = TRAIN_RATIO

    validation_size = VALIDATION_RATIO

    test_size = TEST_RATIO


    total = (
        train_size
        + validation_size
        + test_size
    )


    if not np.isclose(
        total,
        1.0,
    ):

        raise ValueError(
            "TRAIN_RATIO + VALIDATION_RATIO "
            "+ TEST_RATIO must equal 1.0"
        )


    # --------------------------------------------------------
    # First split:
    #
    # train
    # validation + test
    # --------------------------------------------------------

    try:

        train_df, temporary_df = (
            train_test_split(
                dataframe,
                test_size=(
                    validation_size
                    + test_size
                ),
                random_state=RANDOM_SEED,
                shuffle=True,
                stratify=dataframe[
                    "category"
                ],
            )
        )

    except ValueError as error:

        print()
        print(
            "WARNING: Stratified splitting "
            "could not be performed."
        )

        print(
            f"Reason: {error}"
        )

        print(
            "Using random splitting instead."
        )

        train_df, temporary_df = (
            train_test_split(
                dataframe,
                test_size=(
                    validation_size
                    + test_size
                ),
                random_state=RANDOM_SEED,
                shuffle=True,
            )
        )


    # --------------------------------------------------------
    # Second split:
    #
    # validation
    # test
    # --------------------------------------------------------

    relative_test_size = (
        test_size
        / (
            validation_size
            + test_size
        )
    )


    try:

        validation_df, test_df = (
            train_test_split(
                temporary_df,
                test_size=relative_test_size,
                random_state=RANDOM_SEED,
                shuffle=True,
                stratify=temporary_df[
                    "category"
                ],
            )
        )

    except ValueError as error:

        print()
        print(
            "WARNING: Validation/test "
            "stratification could not be performed."
        )

        print(
            f"Reason: {error}"
        )

        print(
            "Using random splitting instead."
        )

        validation_df, test_df = (
            train_test_split(
                temporary_df,
                test_size=relative_test_size,
                random_state=RANDOM_SEED,
                shuffle=True,
            )
        )


    return (
        train_df.reset_index(drop=True),
        validation_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


# ============================================================
# DataLoader creation
# ============================================================

def create_dataloaders():

    set_seed()


    dataframe = (
        load_and_validate_dataframe()
    )


    label_maps = (
        create_label_maps(
            dataframe
        )
    )


    train_df, validation_df, test_df = (
        split_dataframe(
            dataframe
        )
    )


    print()
    print("=" * 60)
    print("Dataset Split")
    print("=" * 60)

    print(
        f"Total      : {len(dataframe)}"
    )

    print(
        f"Training   : {len(train_df)}"
    )

    print(
        f"Validation : {len(validation_df)}"
    )

    print(
        f"Testing    : {len(test_df)}"
    )

    print("=" * 60)
    print()


    train_dataset = CataloguingDataset(
        dataframe=train_df,
        label_maps=label_maps,
        training=True,
    )


    validation_dataset = CataloguingDataset(
        dataframe=validation_df,
        label_maps=label_maps,
        training=False,
    )


    test_dataset = CataloguingDataset(
        dataframe=test_df,
        label_maps=label_maps,
        training=False,
    )


    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )


    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )


    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=torch.cuda.is_available(),
    )


    return (
        train_loader,
        validation_loader,
        test_loader,
        label_maps,
    )


# ============================================================
# Dataset test
# ============================================================

def test_dataset():

    print()
    print("=" * 60)
    print("Testing Dataset Pipeline")
    print("=" * 60)


    (
        train_loader,
        validation_loader,
        test_loader,
        label_maps,
    ) = create_dataloaders()


    print(
        f"Train batches      : {len(train_loader)}"
    )

    print(
        f"Validation batches : {len(validation_loader)}"
    )

    print(
        f"Test batches       : {len(test_loader)}"
    )


    # --------------------------------------------------------
    # Try reading one batch
    # --------------------------------------------------------

    if len(train_loader) > 0:

        batch = next(
            iter(train_loader)
        )


        print()
        print("First training batch:")

        print(
            f"Images shape : "
            f"{batch['image'].shape}"
        )

        print(
            f"Category     : "
            f"{batch['category']}"
        )

        print(
            f"Material     : "
            f"{batch['material']}"
        )

        print(
            f"Color        : "
            f"{batch['color']}"
        )


    print()
    print("Dataset pipeline test completed.")
    print("=" * 60)
    print()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    test_dataset()