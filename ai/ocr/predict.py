import json
import sys
from pathlib import Path

from PIL import Image

from .model import OCRModel


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:"
        )
        print(
            'python -m ai.ocr.predict "IMAGE_PATH"'
        )
        sys.exit(1)

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(
            f"Image not found: {image_path}"
        )
        sys.exit(1)

    try:
        image = Image.open(image_path)
    except Exception as exc:
        print(
            f"Unable to open image: {exc}"
        )
        sys.exit(1)

    model = OCRModel()

    result = model.predict(image)

    result["image_path"] = str(
        image_path
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