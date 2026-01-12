# src/utils/normalize.py

import re
from html import unescape


def clean_description(text: str) -> str:
    """
    Chuẩn hoá description:
    - remove HTML
    - remove extra whitespace
    - unescape HTML entities
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Unescape HTML entities
    text = unescape(text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_product(raw: dict) -> dict:
    """
    Chuẩn hoá product data từ API Tiki
    """
    if not raw:
        raise ValueError("Empty raw product")

    product_id = raw.get("id")
    name = raw.get("name")
    url_key = raw.get("url_key")

    # Giá
    price = raw.get("price") or 0

    # Description
    description_raw = raw.get("description", "")
    description = clean_description(description_raw)

    # Images
    images = []
    for img in raw.get("images", []):
        url = img.get("base_url")
        if url:
            images.append(url)

    # Validate tối thiểu
    if not product_id or not name:
        raise ValueError("Missing required fields")

    return {
        "id": product_id,
        "name": name,
        "url_key": url_key,
        "price": price,
        "description": description,
        "images": images,
    }