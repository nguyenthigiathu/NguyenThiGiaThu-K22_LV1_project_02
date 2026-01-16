import asyncio
import aiohttp
from config.settings import *
from etl.extract.extract_data import fetch_product
from etl.transform.transform_data import normalize
from src.writer.json_writer import JsonWriter
from src.writer.error_writer import ErrorWriter
from src.writer.checkpoint import Checkpoint
from src.utils.logger import info, error
from src.utils.notifier import send_alert

async def run_pipeline(product_ids: list[int]):
    writer = JsonWriter()
    err_writer = ErrorWriter()
    cp = Checkpoint()

    start_idx = cp.get()
    current_ids = product_ids[start_idx:]
    if not current_ids: return

    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    total_in_list = len(product_ids)

    async def fetch_and_process(session, pid):
        async with sem:
            try:
                raw = await fetch_product(session, pid)
                if not raw:
                    return {"ok": False, "pid": pid, "msg": "404 Not Found"}
                return {"ok": True, "data": normalize(raw)}
            except Exception as e:
                return {"ok": False, "pid": pid, "msg": str(e)}

    async with aiohttp.ClientSession() as session:
        # BATCH_SIZE nên là 1000
        for i in range(0, len(current_ids), BATCH_SIZE):
            batch = current_ids[i:i+BATCH_SIZE]
            
            tasks = [fetch_and_process(session, pid) for pid in batch]
            results = await asyncio.gather(*tasks)

            ok_data = [r["data"] for r in results if r["ok"]]
            fails = [r for r in results if not r["ok"]]

            # Ghi file .json (mỗi file 1000 SP)
            writer.write_batch(ok_data)
            
            for f in fails:
                err_writer.write({"product_id": f["pid"], "message": f["msg"]})

            # Cập nhật checkpoint chính xác
            new_idx = start_idx + i + len(batch)
            cp.save(new_idx)
            
            info(f"Tiến độ: {new_idx}/{total_in_list} (Batch: {len(ok_data)} OK)")

            # Alert Discord mỗi 10 file (10,000 SP)
            if (new_idx // BATCH_SIZE) % 10 == 0:
                await send_alert(f"Đã xử lý: {new_idx}/{total_in_list} SP ({(new_idx/total_in_list*100):.2f}%)")