from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F

from .config import VERIFICATION_THRESHOLD


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    embedding_a: torch.Tensor,
    embedding_b: torch.Tensor,
) -> float:

    if embedding_a.numel() == 0:
        raise ValueError(
            "Embedding A is empty."
        )

    if embedding_b.numel() == 0:
        raise ValueError(
            "Embedding B is empty."
        )

    # Flatten to one-dimensional vectors.
    embedding_a = embedding_a.flatten()
    embedding_b = embedding_b.flatten()

    if embedding_a.shape != embedding_b.shape:
        raise ValueError(
            "Embedding dimensions do not match. "
            f"A={embedding_a.shape}, "
            f"B={embedding_b.shape}"
        )

    # Normalize before similarity calculation.
    embedding_a = F.normalize(
        embedding_a,
        p=2,
        dim=0,
    )

    embedding_b = F.normalize(
        embedding_b,
        p=2,
        dim=0,
    )

    similarity = torch.dot(
        embedding_a,
        embedding_b,
    )

    return float(
        similarity.item()
    )


# ============================================================
# BATCH SIMILARITY
# ============================================================

def calculate_similarities(
    query_embedding: torch.Tensor,
    reference_embeddings: torch.Tensor,
) -> torch.Tensor:

    if query_embedding.numel() == 0:
        raise ValueError(
            "Query embedding is empty."
        )

    if reference_embeddings.numel() == 0:
        raise ValueError(
            "Reference embeddings are empty."
        )

    query_embedding = query_embedding.flatten()

    if reference_embeddings.ndim != 2:
        raise ValueError(
            "Reference embeddings must have shape "
            "[number_of_images, embedding_dimension]."
        )

    if (
        reference_embeddings.shape[1]
        != query_embedding.shape[0]
    ):
        raise ValueError(
            "Embedding dimensions do not match."
        )

    query_embedding = F.normalize(
        query_embedding,
        p=2,
        dim=0,
    )

    reference_embeddings = F.normalize(
        reference_embeddings,
        p=2,
        dim=1,
    )

    similarities = torch.matmul(
        reference_embeddings,
        query_embedding,
    )

    return similarities


# ============================================================
# FIND BEST MATCH
# ============================================================

def find_best_match(
    query_embedding: torch.Tensor,
    reference_embeddings: torch.Tensor,
    reference_labels: List[str],
    reference_paths: List[str],
) -> Dict:

    if len(reference_labels) != len(
        reference_paths
    ):
        raise ValueError(
            "Reference labels and paths must have "
            "the same length."
        )

    if reference_embeddings.shape[0] != len(
        reference_labels
    ):
        raise ValueError(
            "Number of embeddings and labels do not match."
        )

    if reference_embeddings.shape[0] == 0:
        raise ValueError(
            "No reference embeddings available."
        )

    similarities = calculate_similarities(
        query_embedding,
        reference_embeddings,
    )

    best_index = int(
        torch.argmax(similarities).item()
    )

    best_similarity = float(
        similarities[best_index].item()
    )

    best_label = reference_labels[
        best_index
    ]

    best_path = reference_paths[
        best_index
    ]

    status = (
        "MATCH_CANDIDATE"
        if best_similarity >= VERIFICATION_THRESHOLD
        else "NO_CONFIDENT_MATCH"
    )

    return {
        "detected_craft": best_label,
        "similarity": best_similarity,
        "confidence": None,
        "similarity_is_probability": False,
        "authenticity_proven": False,
        "status": status,
        "reference_image": best_path,
    }


# ============================================================
# CRAFT-LEVEL PROTOTYPE MATCHING
# ============================================================

def create_craft_prototypes(
    embeddings: torch.Tensor,
    labels: List[str],
) -> Dict[str, torch.Tensor]:

    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must have shape "
            "[number_of_images, embedding_dimension]."
        )

    if embeddings.shape[0] != len(labels):
        raise ValueError(
            "Number of embeddings and labels do not match."
        )

    prototypes = {}

    unique_labels = sorted(
        set(labels)
    )

    for label in unique_labels:

        indices = [
            index
            for index, current_label
            in enumerate(labels)
            if current_label == label
        ]

        class_embeddings = embeddings[
            indices
        ]

        prototype = class_embeddings.mean(
            dim=0
        )

        prototype = F.normalize(
            prototype,
            p=2,
            dim=0,
        )

        prototypes[label] = prototype

    return prototypes


# ============================================================
# MATCH AGAINST CRAFT PROTOTYPES
# ============================================================

def match_craft_prototypes(
    query_embedding: torch.Tensor,
    prototypes: Dict[str, torch.Tensor],
) -> Dict:

    if not prototypes:
        raise ValueError(
            "No craft prototypes available."
        )

    results = []

    for label, prototype in prototypes.items():

        similarity = cosine_similarity(
            query_embedding,
            prototype,
        )

        results.append(
            (
                label,
                similarity,
            )
        )

    results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    best_label, best_similarity = results[0]

    status = (
        "MATCH_CANDIDATE"
        if best_similarity >= VERIFICATION_THRESHOLD
        else "NO_CONFIDENT_MATCH"
    )

    return {
        "detected_craft": best_label,
        "similarity": best_similarity,
        "confidence": None,
        "similarity_is_probability": False,
        "authenticity_proven": False,
        "status": status,
        "all_scores": dict(results),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("KALASETU - CRAFT VERIFICATION SIMILARITY ENGINE")
    print("=" * 60)

    embedding_dimension = 1280

    # --------------------------------------------------------
    # Create synthetic embeddings.
    # --------------------------------------------------------

    query = torch.randn(
        embedding_dimension
    )

    reference = torch.randn(
        4,
        embedding_dimension
    )

    labels = [
        "wood_craft",
        "textile",
        "pottery",
        "metal_craft",
    ]

    paths = [
        "wood_001.jpg",
        "textile_001.jpg",
        "pottery_001.jpg",
        "metal_001.jpg",
    ]

    # --------------------------------------------------------
    # Single similarity test.
    # --------------------------------------------------------

    score = cosine_similarity(
        query,
        reference[0],
    )

    print(
        f"\nSingle cosine similarity: "
        f"{score:.6f}"
    )

    # --------------------------------------------------------
    # Batch similarity test.
    # --------------------------------------------------------

    scores = calculate_similarities(
        query,
        reference,
    )

    print(
        f"Number of reference scores: "
        f"{len(scores)}"
    )

    # --------------------------------------------------------
    # Best reference match.
    # --------------------------------------------------------

    result = find_best_match(
        query,
        reference,
        labels,
        paths,
    )

    print("\nBest Reference Match")
    print(
        f"  Craft      : "
        f"{result['detected_craft']}"
    )

    print(
        f"  Similarity : "
        f"{result['similarity']:.4f}"
    )

    print(
        f"  Status     : "
        f"{result['status']}"
    )

    # --------------------------------------------------------
    # Prototype test.
    # --------------------------------------------------------

    prototype_labels = [
        "wood_craft",
        "wood_craft",
        "textile",
        "textile",
        "pottery",
        "pottery",
        "metal_craft",
        "metal_craft",
    ]

    prototype_embeddings = torch.randn(
        8,
        embedding_dimension,
    )

    prototypes = create_craft_prototypes(
        prototype_embeddings,
        prototype_labels,
    )

    print(
        f"\nCraft prototypes created: "
        f"{len(prototypes)}"
    )

    prototype_result = match_craft_prototypes(
        query,
        prototypes,
    )

    print("\nBest Craft Prototype Match")

    print(
        f"  Craft      : "
        f"{prototype_result['detected_craft']}"
    )

    print(
        f"  Similarity : "
        f"{prototype_result['similarity']:.4f}"
    )

    print(
        f"  Status     : "
        f"{prototype_result['status']}"
    )

    print(
        "\nSimilarity engine test PASSED."
    )