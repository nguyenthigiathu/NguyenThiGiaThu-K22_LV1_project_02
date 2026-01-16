import asyncio
import random
from config.settings import *
from src.utils.logger import error

# Danh sách User-Agents đa dạng để tránh bị nhận diện là bot
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
]

async def fetch_product(session, product_id: int):
    url = PRODUCT_DETAIL_API.format(product_id=product_id)

    for attempt in range(1, MAX_RETRIES + 1):
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "X-Source": "local",
            "Referer": "https://tiki.vn/",
        }

        try:
            async with session.get(url, headers=headers, timeout=REQUEST_TIMEOUT) as r:
                if r.status == 200:
                    return await r.json()
                if r.status == 404:
                    return None
                if r.status in (403, 429): # Bị chặn hoặc quá tải
                    # Exponential Backoff: Đợi lâu dần sau mỗi lần lỗi
                    wait_time = BASE_RETRY_DELAY * (2 ** attempt) + random.uniform(0.5, 1.5)
                    await asyncio.sleep(wait_time)
                    continue
        except Exception:
            if attempt == MAX_RETRIES: raise
            await asyncio.sleep(BASE_RETRY_DELAY * attempt)
    return None