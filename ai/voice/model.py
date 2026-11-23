
from pathlib import Path

import joblib
import speech_recognition as sr

from .config import (
    MODEL_NAME,
    MODEL_VERSION,
)
from .language import (
    language_intelligence,
)


class VoiceLanguageModel:
    """
    KalaSetu Voice & Language AI.

    Baseline:
        SpeechRecognition
        +
        Google Speech Recognition
        +
        language detection
        +
        KalaSetu intent detection
    """

    def __init__(self):

        self.model_name = MODEL_NAME

        self.model_version = (
            MODEL_VERSION
        )

        self.recognizer = (
            sr.Recognizer()
        )


    def transcribe_audio(
        self,
        audio_path,
        language="en-IN",
    ):
        """
        Convert WAV audio to text.

        Google Speech Recognition is used
        as the prototype speech-to-text
        backend.
        """

        audio_path = Path(
            audio_path
        )

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: "
                f"{audio_path}"
            )

        with sr.AudioFile(
            str(audio_path)
        ) as source:

            audio = (
                self.recognizer.record(
                    source
                )
            )

        try:

            text = (
                self.recognizer.recognize_google(
                    audio,
                    language=language,
                )
            )

            return text

        except sr.UnknownValueError:

            return ""

        except sr.RequestError as error:

            raise RuntimeError(
                "Speech recognition service "
                f"request failed: {error}"
            )


    def analyze_text(
        self,
        text,
    ):
        """
        Analyze already-transcribed text.
        """

        result = language_intelligence(
            text
        )

        result.update({
            "model": self.model_name,
            "model_version": self.model_version,
            "research_valid": False,
        })

        return result


    def predict(
        self,
        audio_path,
        language="en-IN",
    ):
        """
        Complete voice prediction pipeline.
        """

        text = self.transcribe_audio(
            audio_path,
            language=language,
        )

        result = self.analyze_text(
            text
        )

        result["audio_path"] = str(
            audio_path
        )

        result["input_language"] = (
            language
        )

        result["note"] = (
            "Prototype voice and language "
            "intelligence. Speech recognition "
            "uses an external baseline service; "
            "research validation requires a "
            "representative multilingual dataset "
            "and comparison with stronger ASR models."
        )

        return result


    def save(self, path):
        """
        Save model configuration.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            {
                "model_name": self.model_name,
                "model_version": self.model_version,
            },
            path,
        )


    @classmethod
    def load(cls, path):
        """
        Load model configuration.
        """

        path = Path(path)

        if not path.exists():

            raise FileNotFoundError(
                f"Model not found: {path}"
            )

        saved = joblib.load(
            path
        )

        model = cls()

        model.model_name = saved[
            "model_name"
        ]

        model.model_version = saved[
            "model_version"
        ]

        return model
