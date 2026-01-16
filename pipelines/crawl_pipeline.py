from src.utils.logger import info, error # Import từ logger bạn đã viết

async def run_pipeline(product_ids: list[int]):
    writer = JsonWriter()
    err_writer = ErrorWriter()
    cp = Checkpoint()

    start_idx = cp.get()
    current_ids = product_ids[start_idx:]
    info(f"Bắt đầu chạy từ sản phẩm thứ {start_idx}")

    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(current_ids), BATCH_SIZE):
            batch = current_ids[i:i+BATCH_SIZE]
            
            async def wrapped_fetch(pid):
                async with sem:
                    try:
                        raw = await fetch_product(session, pid)
                        if raw:
                            return {"ok": True, "data": normalize(raw)}
                        return {"ok": False, "pid": pid, "msg": "404 Not Found"}
                    except Exception as e:
                        return {"ok": False, "pid": pid, "msg": str(e)}

            tasks = [wrapped_fetch(pid) for pid in batch]
            results = await asyncio.gather(*tasks)

            ok_data = [r["data"] for r in results if r["ok"]]
            fails = [r for r in results if not r["ok"]]

            writer.write_batch(ok_data)
            for f in fails:
                err_writer.write({"product_id": f["pid"], "message": f["msg"]})

            # Checkpoint quan trọng: Phải cộng dồn với start_idx
            new_checkpoint = start_idx + i + len(batch)
            cp.save(new_checkpoint)
            info(f"Đã lưu batch {(i//BATCH_SIZE)+1}, tổng cộng: {new_checkpoint}/{len(product_ids)}")