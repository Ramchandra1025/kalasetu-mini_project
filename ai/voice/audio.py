
from pathlib import Path
import wave

import numpy as np


SUPPORTED_AUDIO_FORMATS = {
    ".wav",
}


def validate_audio_path(path):
    """
    Validate that an audio file exists and has
    a supported format.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {path}"
        )

    if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"Unsupported audio format: {path.suffix}"
        )

    return path


def load_wav(path):
    """
    Load a WAV file.

    Returns:
        audio_data
        sample_rate
        channels
    """

    path = validate_audio_path(path)

    with wave.open(
        str(path),
        "rb",
    ) as wav:

        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frame_count = wav.getnframes()

        raw_audio = wav.readframes(
            frame_count
        )

    if sample_width == 2:

        dtype = np.int16

    elif sample_width == 1:

        dtype = np.uint8

    elif sample_width == 4:

        dtype = np.int32

    else:

        raise ValueError(
            f"Unsupported sample width: "
            f"{sample_width}"
        )

    audio = np.frombuffer(
        raw_audio,
        dtype=dtype,
    )

    if channels > 1:

        audio = audio.reshape(
            -1,
            channels,
        )

        audio = audio.mean(
            axis=1
        )

    audio = audio.astype(
        np.float32
    )

    max_value = np.max(
        np.abs(audio)
    )

    if max_value > 0:

        audio = audio / max_value

    return (
        audio,
        sample_rate,
        channels,
    )


def audio_duration(
    audio,
    sample_rate,
):
    """
    Return audio duration in seconds.
    """

    if sample_rate <= 0:
        raise ValueError(
            "Sample rate must be positive."
        )

    return len(audio) / sample_rate


def normalize_audio(audio):
    """
    Normalize audio amplitude to [-1, 1].
    """

    audio = np.asarray(
        audio,
        dtype=np.float32,
    )

    max_value = np.max(
        np.abs(audio)
    )

    if max_value == 0:
        return audio

    return audio / max_value


def audio_statistics(
    audio,
    sample_rate,
):
    """
    Return basic audio statistics.
    """

    audio = normalize_audio(
        audio
    )

    return {
        "sample_rate": int(
            sample_rate
        ),
        "duration_seconds": round(
            audio_duration(
                audio,
                sample_rate,
            ),
            3,
        ),
        "samples": int(
            len(audio)
        ),
        "mean_amplitude": round(
            float(np.mean(audio)),
            6,
        ),
        "max_amplitude": round(
            float(np.max(np.abs(audio))),
            6,
        ),
    }
