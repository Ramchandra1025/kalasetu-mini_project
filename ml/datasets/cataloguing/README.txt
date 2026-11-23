KalaSetu AI Product Cataloguing Dataset
Pipeline Testing Dataset

Purpose:
This dataset is intended for testing the KalaSetu AI Product Vision
and Cataloguing ML pipeline.

Model:
EfficientNet-B0 based multi-head image classification.

Tasks:
1. Craft category classification
2. Material classification
3. Color classification

Classes:

Category:
- wood_craft
- textile
- pottery
- metal_craft

Material:
- wood
- cotton
- clay
- metal

Colors:
- brown
- red
- blue
- green
- orange
- white
- gold
- silver
- bronze

Dataset size:
12 images

IMPORTANT:
This is a SMALL PIPELINE-TEST DATASET.
Images are synthetic and are intended only for ML pipeline testing.

It must NOT be used to claim:
- production accuracy
- research-grade accuracy
- generalization performance
- real-world model performance

For actual research experiments, KalaSetu should use a much larger,
properly licensed dataset with documented collection methodology,
train/validation/test splits, class balance analysis, preprocessing,
augmentation, baselines, evaluation metrics, and reproducible
experiments.

Expected project location after extraction:

E:\kalasetu\ml\datasets\cataloguing\

Expected structure:

ml/
└── datasets/
    └── cataloguing/
        ├── cataloguing.csv
        └── images/
            ├── wood_craft/
            ├── textile/
            ├── pottery/
            └── metal_craft/

After copying the dataset into the KalaSetu project, run:

python -m ai.cataloguing.dataset
