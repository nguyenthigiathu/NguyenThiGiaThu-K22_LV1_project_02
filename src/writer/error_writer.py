import json
from config.settings import ERROR_FILE

class ErrorWriter:
    def write(self, err):
        with open(ERROR_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(err, ensure_ascii=False) + "\n")