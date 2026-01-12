import json
import os
from utils.logger import warning

ERROR_FILE = "output/errors.jsonl"


class ErrorWriter:
    """
    Ghi lỗi dạng JSON Lines (mỗi dòng 1 error)
    An toàn cho file lớn
    """

    def __init__(self):
        os.makedirs("output", exist_ok=True)

    def write(self, error_record: dict):
        with open(ERROR_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_record, ensure_ascii=False) + "\n")

        warning(
            f"Saved error product_id={error_record.get('product_id')}, "
            f"stage={error_record.get('stage')}"
        )
