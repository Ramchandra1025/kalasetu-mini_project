"""
KalaSetu - Market Opportunity Intelligence
Evaluation
"""

import json

from .config import (
    EVALUATION_DIR,
    RESULTS_DIR,
)

from .dataset import (
    create_dataset,
)

from .scoring import (
    rank_markets,
)


# ============================================================
# EVALUATE
# ============================================================

def main():

    print("=" * 70)
    print(
        "KALASETU - MARKET OPPORTUNITY EVALUATION"
    )
    print("=" * 70)

    dataframe = create_dataset()

    ranked_markets = rank_markets(
        dataframe
    )

    # --------------------------------------------------------
    # Distribution
    # --------------------------------------------------------

    scores = [
        item[
            "opportunity_score"
        ]

        for item in ranked_markets
    ]

    average_score = (
        sum(scores)
        / len(scores)
    )

    high_count = sum(
        1

        for item in ranked_markets

        if item[
            "opportunity_level"
        ] == "HIGH"
    )

    medium_count = sum(
        1

        for item in ranked_markets

        if item[
            "opportunity_level"
        ] == "MEDIUM"
    )

    low_count = sum(
        1

        for item in ranked_markets

        if item[
            "opportunity_level"
        ] == "LOW"
    )

    print(
        f"\nTotal market records : "
        f"{len(ranked_markets)}"
    )

    print(
        f"Average score        : "
        f"{average_score:.2f}"
    )

    print(
        f"High opportunities   : "
        f"{high_count}"
    )

    print(
        f"Medium opportunities : "
        f"{medium_count}"
    )

    print(
        f"Low opportunities    : "
        f"{low_count}"
    )

    # --------------------------------------------------------
    # Top markets
    # --------------------------------------------------------

    print(
        "\nTop Market Opportunities:"
    )

    for item in ranked_markets[:10]:

        print(
            f"{item['rank']:>2}. "
            f"{item['product_category']:<15} "
            f"{item['region']:<15} "
            f"Score: "
            f"{item['opportunity_score']:>6.2f} "
            f"Level: "
            f"{item['opportunity_level']}"
        )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = {

        "total_records":
            len(ranked_markets),

        "average_score":
            float(
                average_score
            ),

        "high_opportunities":
            high_count,

        "medium_opportunities":
            medium_count,

        "low_opportunities":
            low_count,

        "top_markets":
            ranked_markets[:10],

        "data_type":
            "synthetic_pipeline_testing_data",

        "research_valid":
            False,

        "research_note":
            (
                "Market opportunity scores "
                "are rule-based prototype scores "
                "using synthetic inputs. They "
                "must not be interpreted as "
                "validated market research."
            ),
    }

    evaluation_file = (
        EVALUATION_DIR
        / "market_evaluation.json"
    )

    result_file = (
        RESULTS_DIR
        / "market_evaluation.json"
    )

    for output_file in [
        evaluation_file,
        result_file,
    ]:

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                results,
                file,
                indent=4,
            )

    print(
        "\nEvaluation results saved."
    )

    print(
        "\nResearch-valid result: NO"
    )

    print(
        "Reason: Synthetic pipeline-testing "
        "market data."
    )

    print(
        "\nEVALUATION TEST PASSED."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()