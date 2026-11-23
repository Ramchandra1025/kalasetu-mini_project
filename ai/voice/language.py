
import re
import unicodedata

from langdetect import (
    detect,
    detect_langs,
    LangDetectException,
)

from .config import (
    LANGUAGE_KEYWORDS,
    SUPPORTED_LANGUAGES,
)


def clean_text(text):
    """
    Normalize recognized speech text.
    """

    if text is None:
        return ""

    text = str(text)

    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def detect_language(text):
    """
    Detect the language of text.

    Returns:
        language code
        language name
        confidence
    """

    text = clean_text(text)

    if not text:
        return {
            "language_code": "unknown",
            "language": "Unknown",
            "confidence": 0.0,
        }

    try:

        detected = detect(
            text
        )

        probabilities = detect_langs(
            text
        )

        confidence = 0.0

        for item in probabilities:

            if item.lang == detected:

                confidence = (
                    float(item.prob)
                    * 100
                )

                break

        language_name = (
            SUPPORTED_LANGUAGES.get(
                detected,
                detected,
            )
        )

        return {
            "language_code": detected,
            "language": language_name,
            "confidence": round(
                confidence,
                2,
            ),
        }

    except LangDetectException:

        return {
            "language_code": "unknown",
            "language": "Unknown",
            "confidence": 0.0,
        }


def detect_kalasetu_keywords(text):
    """
    Detect KalaSetu-related keywords
    across supported languages.
    """

    text = clean_text(
        text
    ).lower()

    results = {}

    for language, keywords in (
        LANGUAGE_KEYWORDS.items()
    ):

        matches = []

        for keyword in keywords:

            if keyword.lower() in text:

                matches.append(
                    keyword
                )

        if matches:

            results[language] = matches

    return results


def detect_intent(text):
    """
    Detect a basic KalaSetu voice intent.
    """

    text = clean_text(
        text
    ).lower()

    if not text:

        return "unknown"

    pricing_terms = [
        "price",
        "cost",
        "कीमत",
        "ಬೆಲೆ",
        "किंमत",
    ]

    market_terms = [
        "market",
        "बाज़ार",
        "बाजार",
        "ಮಾರುಕಟ್ಟೆ",
    ]

    product_terms = [
        "product",
        "craft",
        "artisan",
        "हस्तशिल्प",
        "ಕರಕುಶಲ",
        "कारीगर",
        "ಕುಶಲಕರ್ಮಿ",
    ]

    for term in pricing_terms:

        if term in text:
            return "pricing"

    for term in market_terms:

        if term in text:
            return "market"

    for term in product_terms:

        if term in text:
            return "product_information"

    return "general"


def language_intelligence(text):
    """
    Complete text-level language intelligence.
    """

    text = clean_text(
        text
    )

    language = detect_language(
        text
    )

    keywords = (
        detect_kalasetu_keywords(
            text
        )
    )

    intent = detect_intent(
        text
    )

    return {
        "text": text,
        "language_code": language[
            "language_code"
        ],
        "language": language[
            "language"
        ],
        "language_confidence": language[
            "confidence"
        ],
        "kalasetu_keywords": keywords,
        "intent": intent,
    }
