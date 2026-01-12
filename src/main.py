# src/main.py

import asyncio
from crawlers.scheduler import run_scheduler
from utils.logger import info, error


def load_product_ids(path: str) -> list[int]:
    """
    Load danh sách product_id từ file text
    Mỗi dòng 1 product_id
    """
    product_ids = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.isdigit():
                product_ids.append(int(line))

    return product_ids


def main():
    info("🚀 Tiki crawler started")

    try:
        product_ids = load_product_ids("products-ids.csv")
        info(f"Loaded {len(product_ids)} product_ids")

        asyncio.run(run_scheduler(product_ids))

    except Exception as e:
        error(f"Fatal error: {e}")
        raise

    info("✅ Tiki crawler finished")


if __name__ == "__main__":
    main()