import logging
import os
from config.settings import LOG_DIR, DEBUG

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("etl")
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

if not logger.handlers:
    fh = logging.FileHandler(f"{LOG_DIR}/etl.log", encoding="utf-8")
    ch = logging.StreamHandler()
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)

def info(m): logger.info(m)
def error(m): logger.error(m)