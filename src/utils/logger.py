# src/utils/logger.py

import logging
import os
from utils.constants import DEBUG

LOG_DIR = "logs"
LOG_FILE = "logs/crawler.log"

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("tiki_crawler")
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Tránh add handler trùng khi reload
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# ===== Helper functions =====

def info(msg: str):
    logger.info(msg)


def warning(msg: str):
    logger.warning(msg)


def error(msg: str):
    logger.error(msg)