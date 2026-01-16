import json, os
from config.settings import CHECKPOINT_FILE

class Checkpoint:
    def __init__(self):
        self.n = 0
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE) as f:
                self.n = json.load(f).get("processed", 0)

    def save(self, n):
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump({"processed": n}, f)

    def get(self):
        return self.n