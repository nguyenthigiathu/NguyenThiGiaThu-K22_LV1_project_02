# API
PRODUCT_DETAIL_API = "https://api.tiki.vn/product-detail/api/v1/products/{product_id}"

# CRAWLER
MAX_CONCURRENT_REQUESTS = 50
BATCH_SIZE = 1000

# RETRY / TIMEOUT
MAX_RETRIES = 5
BASE_RETRY_DELAY = 0.5
REQUEST_TIMEOUT = 10

# AUTO RESTART
MAX_RESTARTS = 999
RESTART_DELAY = 10

# PATH
OUTPUT_DIR = "output"
LOG_DIR = "logs"
CHECKPOINT_FILE = "output/checkpoint.json"
ERROR_FILE = "output/errors.jsonl"

DEBUG = False

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1460846730865020948/PaFNh4KDnPL_gQ2k4RUoCzVm8EpTRc5N3PaQRKBIQe-0DDlvrX-5POvv0GcPTpF_2W6v"