import json, os, glob
from config.settings import OUTPUT_DIR

class JsonWriter:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        # Tìm index lớn nhất hiện có
        existing_files = glob.glob(f"{OUTPUT_DIR}/products_*.json")
        if existing_files:
            try:
                indices = [int(f.split('_')[-1].split('.')[0]) for f in existing_files]
                self.idx = max(indices)
            except: self.idx = 0
        else:
            self.idx = 0

    def write_batch(self, data):
        if not data: return
        self.idx += 1
        filename = f"{OUTPUT_DIR}/products_{self.idx:04d}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)