import argparse
import json

from .model import VoiceLanguageModel


def main():

    parser = argparse.ArgumentParser(
        description=(
            "KalaSetu Voice & Language AI"
        )
    )

    parser.add_argument(
        "audio",
        help="Path to WAV audio file",
    )

    parser.add_argument(
        "--language",
        default="en-IN",
        help=(
            "Speech recognition language "
            "code, e.g. en-IN, hi-IN, kn-IN"
        ),
    )

    args = parser.parse_args()

    model = VoiceLanguageModel()

    result = model.predict(
        args.audio,
        language=args.language,
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
