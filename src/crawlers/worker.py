import aiohttp
from crawlers.fetcher import fetch_product_detail
from utils.normalize import normalize_product
from utils.logger import warning


async def process_product(product_id: int) -> dict:
    # ===== FETCH =====
    try:
        async with aiohttp.ClientSession() as session:
            raw = await fetch_product_detail(session, product_id)
    except Exception as e:
        return {
            "ok": False,
            "error": {
                "product_id": product_id,
                "stage": "fetch",
                "message": str(e)
            }
        }

    if not raw:
        return {
            "ok": False,
            "error": {
                "product_id": product_id,
                "stage": "fetch",
                "message": "Empty response"
            }
        }

    # ===== NORMALIZE =====
    try:
        product = normalize_product(raw)
        return {
            "ok": True,
            "data": product
        }
    except Exception as e:
        return {
            "ok": False,
            "error": {
                "product_id": product_id,
                "stage": "normalize",
                "message": str(e)
            }
        }
