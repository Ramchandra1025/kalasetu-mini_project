from pathlib import Path

import joblib

from .config import MODEL_PATH


class NLPModel:

    def __init__(
        self,
        vectorizer=None,
    ):

        self.vectorizer = vectorizer

    def fit(
        self,
        texts,
    ):
        """
        Train TF-IDF representation.
        """

        from sklearn.feature_extraction.text import (
            TfidfVectorizer,
        )

        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            stop_words="english",
        )

        self.vectorizer.fit(
            texts
        )

        return self

    def transform(
        self,
        texts,
    ):
        """
        Transform text using trained vectorizer.
        """

        if self.vectorizer is None:
            raise RuntimeError(
                "NLP model has not been fitted."
            )

        return self.vectorizer.transform(
            texts
        )

    def get_feature_names(self):
        """
        Return learned vocabulary.
        """

        if self.vectorizer is None:
            raise RuntimeError(
                "NLP model has not been fitted."
            )

        return (
            self.vectorizer
            .get_feature_names_out()
        )

    def save(
        self,
        path: str | Path = MODEL_PATH,
    ):
        """
        Save trained NLP model.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            {
                "vectorizer": self.vectorizer,
            },
            path,
        )

    @classmethod
    def load(
        cls,
        path: str | Path = MODEL_PATH,
    ):
        """
        Load trained NLP model.
        """

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"NLP model not found: {path}"
            )

        saved = joblib.load(
            path
        )

        model = cls()

        model.vectorizer = (
            saved["vectorizer"]
        )

        return model