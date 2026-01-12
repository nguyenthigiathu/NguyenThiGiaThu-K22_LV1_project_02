# src/writer/checkpoint.py

import json
import os
from utils.logger import info

CHECKPOINT_FILE = "output/checkpoint.json"


class Checkpoint:
    def __init__(self):
        os.makedirs("output", exist_ok=True)
        self.data = {
            "last_batch": 0,
            "processed": 0
        }
        self._load()

    def _load(self):
        if os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    info(f"Checkpoint loaded: {self.data}")
            except Exception:
                info("Checkpoint corrupted, starting fresh")

    def save(self, batch_index: int, processed: int):
        self.data["last_batch"] = batch_index
        self.data["processed"] = processed

        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_processed_count(self) -> int:
        return self.data.get("processed", 0)

    def get_last_batch(self) -> int:
        return self.data.get("last_batch", 0)