import asyncio
import random
import aiohttp

from utils.constants import (
    PRODUCT_DETAIL_API,
    MAX_RETRIES,
    BASE_RETRY_DELAY,
    REQUEST_TIMEOUT,
)
from utils.logger import info, warning, error


async def fetch_product_detail(session: aiohttp.ClientSession, product_id: int):
    url = PRODUCT_DETAIL_API.format(product_id=product_id)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(url, timeout=REQUEST_TIMEOUT) as resp:
                # ---------- SUCCESS ----------
                if resp.status == 200:
                    data = await resp.json()
                    if not data:
                        warning(f"Empty response for product_id={product_id}")
                        return None
                    return data

                # ---------- RATE LIMIT ----------
                if resp.status == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        delay = float(retry_after)
                    else:
                        # Exponential backoff + jitter
                        delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                        delay += random.uniform(0, delay * 0.3)

                    warning(
                        f"HTTP 429 product_id={product_id}, "
                        f"attempt={attempt}, sleep={delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                    continue

                # ---------- NOT FOUND ----------
                if resp.status == 404:
                    warning(f"HTTP 404 product_id={product_id}")
                    return None

                # ---------- OTHER HTTP ----------
                warning(
                    f"HTTP {resp.status} product_id={product_id}, attempt={attempt}"
                )

        except asyncio.TimeoutError:
            delay = BASE_RETRY_DELAY * attempt
            delay += random.uniform(0, delay * 0.2)
            warning(
                f"Timeout product_id={product_id}, attempt={attempt}, sleep={delay:.2f}s"
            )
            await asyncio.sleep(delay)

        except Exception as e:
            error(f"Fetch error product_id={product_id}: {e}")
            return None

    warning(f"Max retries exceeded for product_id={product_id}")
    return None