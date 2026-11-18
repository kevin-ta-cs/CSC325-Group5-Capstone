import json
import logging
import os
import warnings
from io import BytesIO

import httpx2
from django.core.files.uploadedfile import UploadedFile
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from PIL import Image, UnidentifiedImageError

from .forms import FoundItemForm
from .matching import GEMINI_MODEL


logger = logging.getLogger(__name__)
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
IMAGE_MIME_TYPES = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}
ALLOWED_CATEGORIES = tuple(
    value
    for value, _ in FoundItemForm.base_fields["category"].choices
    if value
)
PHOTO_ANALYSIS_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "item_count": {"type": "INTEGER"},
        "items": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "item_name": {"type": "STRING"},
                    "category": {
                        "type": "STRING",
                        "enum": list(ALLOWED_CATEGORIES),
                    },
                    "color": {"type": "STRING"},
                    "description": {"type": "STRING"},
                },
                "required": ["item_name", "category", "color", "description"],
            },
        },
    },
    "required": ["item_count", "items"],
}


class PhotoAnalysisError(Exception):
    """Raised when an uploaded photo cannot be analyzed."""


def _read_valid_image(uploaded_image):
    if not isinstance(uploaded_image, UploadedFile):
        raise PhotoAnalysisError("Upload a valid JPEG, PNG, or WebP image.")
    if uploaded_image.size > MAX_IMAGE_SIZE:
        raise PhotoAnalysisError("The image must be 5 MB or smaller.")

    original_position = uploaded_image.tell()
    try:
        uploaded_image.seek(0)
        image_bytes = uploaded_image.read()
    finally:
        uploaded_image.seek(original_position)

    if not image_bytes or len(image_bytes) > MAX_IMAGE_SIZE:
        raise PhotoAnalysisError("Upload a valid JPEG, PNG, or WebP image.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(BytesIO(image_bytes))
            image_format = image.format
            width, height = image.size
            image.verify()
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        UnidentifiedImageError,
    ) as error:
        raise PhotoAnalysisError(
            "Upload a valid JPEG, PNG, or WebP image."
        ) from error

    mime_type = IMAGE_MIME_TYPES.get(image_format)
    if (
        mime_type is None
        or uploaded_image.content_type != mime_type
        or width * height > MAX_IMAGE_PIXELS
    ):
        raise PhotoAnalysisError("Upload a valid JPEG, PNG, or WebP image.")

    return image_bytes, mime_type


def analyze_item_photo(uploaded_image):
    image_bytes, mime_type = _read_valid_image(uploaded_image)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise PhotoAnalysisError("AI photo analysis is not configured.")

    prompt = (
        "Analyze the uploaded item photo for a campus lost-and-found report. "
        "Identify each distinct item that a student could reasonably report as "
        "lost or found. Ignore background objects, furniture, hands, people, and "
        "other incidental details unless clearly the intended reportable item. "
        "Return an items array with one separate entry per reportable item and an "
        "item_count equal to the array length. Never combine multiple items into "
        "one description. If exactly one item is reportable, return one entry. If "
        "none is clear, return an empty array and item_count 0. For each item, "
        "return its visible name, one category from the allowed category list, "
        "visible color, and an item-only description. Focus on item type, color, "
        "clearly visible brand or logo, patterns, and distinguishing features. "
        "Keep each description to one concise sentence of about 10-20 words. Do "
        "not invent details that are not clearly visible, including brands, "
        "ownership, locations, or dates. Leave unclear string details empty. "
        "Choose a category only when supported by the visible item.\n"
        f"Allowed categories: {', '.join(ALLOWED_CATEGORIES)}"
    )

    try:
        with genai.Client(api_key=api_key) as client:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PHOTO_ANALYSIS_SCHEMA,
                ),
            )
    except (genai_errors.APIError, httpx2.HTTPError) as error:
        logger.exception("Gemini photo analysis request failed")
        raise PhotoAnalysisError(
            "AI photo analysis is temporarily unavailable."
        ) from error

    try:
        result = json.loads(response.text)
    except (AttributeError, json.JSONDecodeError, TypeError) as error:
        raise PhotoAnalysisError(
            "AI photo analysis returned an invalid response."
        ) from error

    if not isinstance(result, dict) or set(result) != {"item_count", "items"}:
        raise PhotoAnalysisError("AI photo analysis returned an invalid response.")

    fields = ("item_name", "category", "color", "description")
    items = result["items"]
    item_count = result["item_count"]
    if (
        isinstance(item_count, bool)
        or not isinstance(item_count, int)
        or not isinstance(items, list)
        or item_count != len(items)
    ):
        raise PhotoAnalysisError("AI photo analysis returned an invalid response.")

    normalized_items = []
    for item in items:
        if (
            not isinstance(item, dict)
            or set(item) != set(fields)
            or any(not isinstance(item[field], str) for field in fields)
        ):
            raise PhotoAnalysisError(
                "AI photo analysis returned an invalid response."
            )

        normalized_item = {field: item[field].strip() for field in fields}
        if (
            not normalized_item["item_name"]
            or normalized_item["category"] not in ALLOWED_CATEGORIES
            or len(normalized_item["item_name"]) > 120
            or len(normalized_item["color"]) > 64
        ):
            raise PhotoAnalysisError(
                "AI photo analysis returned an invalid response."
            )
        normalized_items.append(normalized_item)

    return {"item_count": item_count, "items": normalized_items}
