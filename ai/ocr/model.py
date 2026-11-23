
from pathlib import Path
import re

import joblib
import numpy as np
import pytesseract

from .config import (
    MODEL_FILE,
    MODEL_VERSION,
    OCR_LANGUAGE,
    TESSERACT_CMD,
    TESSERACT_OEM,
    TESSERACT_PSM,
    MIN_CONFIDENCE,
    CATEGORY_KEYWORDS,
    MATERIAL_KEYWORDS,
    CRAFT_KEYWORDS,
)


class OCRModel:
    """
    Tesseract-based OCR intelligence wrapper for KalaSetu.

    Complete pipeline:

        Image
          ↓
        OpenCV preprocessing
          ↓
        Tesseract OCR
          ↓
        Text cleaning
          ↓
        Keyword extraction
          ↓
        Category detection
          ↓
        Material detection
          ↓
        Craft-term detection
          ↓
        Structured OCR result

    Note:
        This is an OCR inference/configuration pipeline.
        Tesseract itself is not trained by this project.
    """

    def __init__(
        self,
        tesseract_cmd=TESSERACT_CMD,
        language=OCR_LANGUAGE,
        psm=TESSERACT_PSM,
        oem=TESSERACT_OEM,
    ):
        self.tesseract_cmd = tesseract_cmd
        self.language = language
        self.psm = psm
        self.oem = oem
        self.model_version = MODEL_VERSION

        self.configure()

    # =========================================================
    # TESSERACT CONFIGURATION
    # =========================================================

    def configure(self):
        """
        Configure the Tesseract executable.
        """
        pytesseract.pytesseract.tesseract_cmd = (
            self.tesseract_cmd
        )

    # =========================================================
    # OCR
    # =========================================================

    def extract_text(self, image):
        """
        Extract text from an image using Tesseract.

        Returns:
            str
        """
        self.configure()

        config = (
            f"--oem {self.oem} "
            f"--psm {self.psm}"
        )

        text = pytesseract.image_to_string(
            image,
            lang=self.language,
            config=config,
        )

        return text.strip()

    def extract_data(self, image):
        """
        Extract OCR text and confidence information.

        Returns:
            {
                "text": str,
                "confidence": float
            }
        """
        self.configure()

        config = (
            f"--oem {self.oem} "
            f"--psm {self.psm}"
        )

        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            config=config,
            output_type=pytesseract.Output.DICT,
        )

        confidences = []

        for confidence in data["conf"]:
            try:
                value = float(confidence)

                if value >= 0:
                    confidences.append(value)

            except (ValueError, TypeError):
                continue

        average_confidence = (
            float(np.mean(confidences))
            if confidences
            else 0.0
        )

        text_parts = []

        for word in data["text"]:
            word = word.strip()

            if word:
                text_parts.append(word)

        text = " ".join(text_parts)

        return {
            "text": text.strip(),
            "confidence": round(
                average_confidence,
                2,
            ),
        }

    # =========================================================
    # TEXT CLEANING
    # =========================================================

    @staticmethod
    def clean_text(text):
        """
        Normalize OCR text.
        """

        text = str(text or "")

        # Replace newlines with spaces
        text = text.replace("\n", " ")

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # =========================================================
    # KEYWORD EXTRACTION
    # =========================================================

    @staticmethod
    def extract_keywords(
        text,
        max_keywords=15,
    ):
        """
        Extract useful keywords from OCR text.
        """

        text = OCRModel.clean_text(
            text
        ).lower()

        # Extract words
        words = re.findall(
            r"[a-zA-Z][a-zA-Z\-']+",
            text,
        )

        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "this",
            "that",
            "made",
            "using",
            "are",
            "is",
            "of",
            "in",
            "by",
            "to",
            "a",
            "an",
            "on",
            "as",
            "it",
            "its",
        }

        keywords = []

        for word in words:

            if (
                word not in stop_words
                and len(word) >= 3
                and word not in keywords
            ):
                keywords.append(word)

        return keywords[:max_keywords]

    # =========================================================
    # CATEGORY DETECTION
    # =========================================================

    @staticmethod
    def detect_category(text):
        """
        Detect the most likely craft category.

        Returns:
            {
                "category": str,
                "confidence": float
            }
        """

        text = OCRModel.clean_text(
            text
        ).lower()

        scores = {}

        for category, keywords in (
            CATEGORY_KEYWORDS.items()
        ):

            score = sum(
                1
                for keyword in keywords
                if keyword.lower() in text
            )

            scores[category] = score

        if not scores:
            return {
                "category": "unknown",
                "confidence": 0.0,
            }

        best_category = max(
            scores,
            key=scores.get,
        )

        best_score = scores[
            best_category
        ]

        if best_score == 0:
            return {
                "category": "unknown",
                "confidence": 0.0,
            }

        total = sum(
            scores.values()
        )

        confidence = (
            (best_score / total) * 100
            if total > 0
            else 0.0
        )

        return {
            "category": best_category,
            "confidence": round(
                confidence,
                2,
            ),
        }

    # =========================================================
    # MATERIAL DETECTION
    # =========================================================

    @staticmethod
    def detect_materials(text):
        """
        Detect material mentions.
        """

        text = OCRModel.clean_text(
            text
        ).lower()

        detected = []

        for material in MATERIAL_KEYWORDS:

            if material.lower() in text:
                detected.append(material)

        return detected

    # =========================================================
    # CRAFT TERM DETECTION
    # =========================================================

    @staticmethod
    def detect_craft_terms(text):
        """
        Detect craft-related terminology.
        """

        text = OCRModel.clean_text(
            text
        ).lower()

        detected = []

        for term in CRAFT_KEYWORDS:

            if term.lower() in text:
                detected.append(term)

        return detected

    # =========================================================
    # COMPLETE PREDICTION PIPELINE
    # =========================================================

    def predict(self, image):
        """
        Run the complete OCR intelligence pipeline.

        Pipeline:

            Image
              ↓
            OpenCV preprocessing
              ↓
            Tesseract OCR
              ↓
            Text cleaning
              ↓
            Keyword extraction
              ↓
            Category detection
              ↓
            Material detection
              ↓
            Craft-term detection
              ↓
            Structured result
        """

        # -----------------------------------------------------
        # 1. IMAGE PREPROCESSING
        # -----------------------------------------------------

        from .preprocessing import preprocess_image

        processed_image = preprocess_image(
            image
        )

        # -----------------------------------------------------
        # 2. OCR + CONFIDENCE
        # -----------------------------------------------------

        ocr_result = self.extract_data(
            processed_image
        )

        extracted_text = ocr_result[
            "text"
        ]

        confidence = ocr_result[
            "confidence"
        ]

        # -----------------------------------------------------
        # 3. TEXT CLEANING
        # -----------------------------------------------------

        cleaned_text = self.clean_text(
            extracted_text
        )

        # -----------------------------------------------------
        # 4. KEYWORD EXTRACTION
        # -----------------------------------------------------

        keywords = self.extract_keywords(
            cleaned_text
        )

        # -----------------------------------------------------
        # 5. CATEGORY DETECTION
        # -----------------------------------------------------

        category_result = (
            self.detect_category(
                cleaned_text
            )
        )

        detected_category = (
            category_result["category"]
        )

        category_confidence = (
            category_result["confidence"]
        )

        # -----------------------------------------------------
        # 6. MATERIAL DETECTION
        # -----------------------------------------------------

        detected_materials = (
            self.detect_materials(
                cleaned_text
            )
        )

        # -----------------------------------------------------
        # 7. CRAFT TERM DETECTION
        # -----------------------------------------------------

        craft_terms = (
            self.detect_craft_terms(
                cleaned_text
            )
        )

        # -----------------------------------------------------
        # 8. CONFIDENCE LEVEL
        # -----------------------------------------------------

        confidence_level = (
            self.confidence_level(
                confidence
            )
        )

        # -----------------------------------------------------
        # 9. STRUCTURED RESULT
        # -----------------------------------------------------

        return {
            "text": extracted_text,

            "cleaned_text": cleaned_text,

            "confidence": round(
                float(confidence),
                2,
            ),

            "confidence_level": (
                confidence_level
            ),

            "keywords": keywords,

            "detected_category": (
                detected_category
            ),

            "category_confidence": round(
                float(category_confidence),
                2,
            ),

            "detected_materials": (
                detected_materials
            ),

            "craft_terms": craft_terms,

            "model": "Tesseract OCR",

            "model_version": (
                self.model_version
            ),

            "research_valid": False,

            "note": (
                "Prototype OCR intelligence "
                "using synthetic evaluation data. "
                "Research validity requires a "
                "representative real-world OCR dataset."
            ),
        }

    # =========================================================
    # SAVE
    # =========================================================

    def save(
        self,
        path=MODEL_FILE,
    ):
        """
        Save OCR configuration.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            {
                "tesseract_cmd": (
                    self.tesseract_cmd
                ),

                "language": (
                    self.language
                ),

                "psm": self.psm,

                "oem": self.oem,

                "model_version": (
                    self.model_version
                ),
            },
            path,
        )

    # =========================================================
    # LOAD
    # =========================================================

    @classmethod
    def load(
        cls,
        path=MODEL_FILE,
    ):
        """
        Load saved OCR configuration.
        """

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"OCR model configuration "
                f"not found: {path}"
            )

        saved = joblib.load(
            path
        )

        return cls(
            tesseract_cmd=(
                saved["tesseract_cmd"]
            ),

            language=(
                saved["language"]
            ),

            psm=saved["psm"],

            oem=saved["oem"],
        )

    # =========================================================
    # CONFIDENCE LEVEL
    # =========================================================

    @staticmethod
    def confidence_level(
        confidence
    ):
        """
        Convert numerical OCR confidence
        into a readable level.
        """

        confidence = float(
            confidence
        )

        if confidence >= 80:
            return "HIGH"

        if confidence >= MIN_CONFIDENCE:
            return "MEDIUM"

        return "LOW"
