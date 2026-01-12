# src/crawlers/scheduler.py

import asyncio

from crawlers.worker import process_product
from writer.json_writer import JsonWriter
from writer.error_writer import ErrorWriter
from writer.checkpoint import Checkpoint
from utils.logger import info, error
from utils.constants import (
    BATCH_SIZE,
    MAX_CONCURRENT_REQUESTS
)


async def run_scheduler(product_ids: list[int]):
    """
    Điều phối crawl toàn bộ product_ids theo batch
    - Ghi product OK ra JSON
    - Ghi product lỗi ra errors.jsonl
    - Hỗ trợ resume bằng checkpoint
    """

    info("Scheduler started")

    # ===== INIT =====
    checkpoint = Checkpoint()
    writer = JsonWriter()
    error_writer = ErrorWriter()

    # ===== RESUME =====
    start_index = checkpoint.get_processed_count()
    product_ids = product_ids[start_index:]

    info(f"Resume from index {start_index}")
    info(f"TOTAL IDS TO PROCESS: {len(product_ids)}")

    if not product_ids:
        info("No product_ids to process. Exit scheduler.")
        return

    # ===== CONCURRENCY CONTROL =====
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def bounded_task(product_id: int):
        async with semaphore:
            try:
                return await process_product(product_id)
            except Exception as e:
                error(f"Worker crash product_id={product_id}: {e}")
                return {
                    "ok": False,
                    "error": {
                        "product_id": product_id,
                        "stage": "worker",
                        "message": str(e)
                    }
                }

    # ===== MAIN LOOP =====
    total_batches = (len(product_ids) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_no in range(total_batches):
        start = batch_no * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = product_ids[start:end]

        info(
            f"Running batch {batch_no + 1}/{total_batches}, "
            f"size={len(batch)}"
        )

        # Tạo tasks cho batch
        tasks = [
            asyncio.create_task(bounded_task(pid))
            for pid in batch
        ]

        # Chờ batch hoàn thành
        results = await asyncio.gather(*tasks)

        # ===== TÁCH SUCCESS / ERROR =====
        success_products = []
        failed_products = []

        for r in results:
            if not r:
                continue

            if r.get("ok") is True:
                success_products.append(r["data"])
            else:
                failed_products.append(r["error"])

        # ===== WRITE OUTPUT =====
        writer.write_batch(success_products)

        for err in failed_products:
            error_writer.write(err)

        # ===== SAVE CHECKPOINT =====
        checkpoint.save(
            batch_index=writer.index,
            processed=start_index + writer.index * BATCH_SIZE
        )

        info(
            f"Finished batch {batch_no + 1}, "
            f"success={len(success_products)}, "
            f"failed={len(failed_products)}"
        )

    info("Scheduler finished ALL batches")