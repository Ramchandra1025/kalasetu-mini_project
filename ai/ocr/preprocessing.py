from pathlib import Path

import cv2
import numpy as np


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(image):
    """
    Convert different image inputs into an OpenCV BGR image.

    Supported inputs:
        - File path
        - pathlib.Path
        - PIL Image
        - NumPy array

    Returns:
        NumPy ndarray in BGR format.
    """

    # --------------------------------------------------------
    # NumPy image
    # --------------------------------------------------------

    if isinstance(image, np.ndarray):

        if image.size == 0:
            raise ValueError(
                "Input NumPy image is empty."
            )

        return image.copy()

    # --------------------------------------------------------
    # File path
    # --------------------------------------------------------

    if isinstance(
        image,
        (str, Path),
    ):

        image_path = Path(image)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image_array = cv2.imread(
            str(image_path)
        )

        if image_array is None:
            raise ValueError(
                f"Unable to read image: {image_path}"
            )

        return image_array

    # --------------------------------------------------------
    # PIL Image
    # --------------------------------------------------------

    try:
        from PIL import Image

        if isinstance(
            image,
            Image.Image,
        ):

            # Convert PIL image to RGB
            rgb_image = image.convert(
                "RGB"
            )

            # PIL → NumPy
            rgb_array = np.array(
                rgb_image
            )

            # RGB → OpenCV BGR
            bgr_array = cv2.cvtColor(
                rgb_array,
                cv2.COLOR_RGB2BGR,
            )

            return bgr_array

    except ImportError:
        pass

    # --------------------------------------------------------
    # Unsupported input
    # --------------------------------------------------------

    raise TypeError(
        "Unsupported image type: "
        f"{type(image).__name__}. "
        "Expected a file path, PIL Image, "
        "or NumPy array."
    )


# ============================================================
# RESIZE
# ============================================================

def resize_for_ocr(
    image,
    target_width=1600,
):
    """
    Resize image for better OCR performance.

    Small images are enlarged.
    Large images are reduced while preserving aspect ratio.

    Returns:
        Resized OpenCV image.
    """

    image = load_image(
        image
    )

    height, width = image.shape[:2]

    if width <= 0 or height <= 0:
        raise ValueError(
            "Invalid image dimensions."
        )

    # --------------------------------------------------------
    # Calculate scale
    # --------------------------------------------------------

    scale = (
        target_width / width
    )

    # Avoid unnecessarily shrinking very large images.
    if scale < 1.0:
        new_width = target_width
        new_height = int(
            height * scale
        )

    # Enlarge smaller images.
    elif width < target_width:
        new_width = target_width
        new_height = int(
            height * scale
        )

    else:
        new_width = width
        new_height = height

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    resized = cv2.resize(
        image,
        (
            new_width,
            new_height,
        ),
        interpolation=(
            cv2.INTER_CUBIC
        ),
    )

    return resized


# ============================================================
# GRAYSCALE
# ============================================================

def convert_to_grayscale(
    image
):
    """
    Convert BGR image to grayscale.
    """

    image = load_image(
        image
    )

    # Already grayscale
    if len(image.shape) == 2:
        return image

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )


# ============================================================
# DENOISING
# ============================================================

def denoise_image(
    image
):
    """
    Reduce image noise before OCR.
    """

    if image is None:
        raise ValueError(
            "Image cannot be None."
        )

    return cv2.GaussianBlur(
        image,
        (3, 3),
        0,
    )


# ============================================================
# THRESHOLDING
# ============================================================

def threshold_image(
    image
):
    """
    Convert grayscale image into a high-contrast
    binary image using adaptive thresholding.
    """

    if image is None:
        raise ValueError(
            "Image cannot be None."
        )

    # Ensure grayscale
    if len(image.shape) == 3:
        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )

    thresholded = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return thresholded


# ============================================================
# OCR PREPROCESSING PIPELINE
# ============================================================

def preprocess_image(
    image
):
    """
    Complete OCR preprocessing pipeline.

    Pipeline:

        Input image
            ↓
        Load / convert
            ↓
        Resize
            ↓
        Grayscale
            ↓
        Denoise
            ↓
        Adaptive threshold
            ↓
        OCR-ready image

    Returns:
        NumPy ndarray.
    """

    # --------------------------------------------------------
    # 1. Load / normalize input
    # --------------------------------------------------------

    image = load_image(
        image
    )

    # --------------------------------------------------------
    # 2. Resize
    # --------------------------------------------------------

    resized = resize_for_ocr(
        image
    )

    # --------------------------------------------------------
    # 3. Grayscale
    # --------------------------------------------------------

    grayscale = convert_to_grayscale(
        resized
    )

    # --------------------------------------------------------
    # 4. Denoise
    # --------------------------------------------------------

    denoised = denoise_image(
        grayscale
    )

    # --------------------------------------------------------
    # 5. Adaptive threshold
    # --------------------------------------------------------

    thresholded = threshold_image(
        denoised
    )

    return thresholded


# ============================================================
# SAVE PREPROCESSED IMAGE
# ============================================================

def save_preprocessed_image(
    image,
    output_path,
):
    """
    Preprocess and save an image.

    Useful for debugging OCR preprocessing.
    """

    processed = preprocess_image(
        image
    )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    success = cv2.imwrite(
        str(output_path),
        processed,
    )

    if not success:
        raise IOError(
            f"Unable to save image: "
            f"{output_path}"
        )

    return output_path
