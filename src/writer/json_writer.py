# src/writer/json_writer.py

import json
import os
from utils.logger import info

OUTPUT_DIR = "output"


class JsonWriter:
    """
    Ghi dữ liệu product ra file JSON theo batch
    Mỗi file ~1000 sản phẩm
    """

    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.index = 0  # số batch đã ghi

    def write_batch(self, products: list[dict]):
        """
        Ghi 1 batch product ra file:
        output/products_0001.json
        """
        if not products:
            info("Empty batch, skip writing")
            return

        self.index += 1

        filename = f"products_{self.index:04d}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        info(f"Wrote {len(products)} products to {filename}")