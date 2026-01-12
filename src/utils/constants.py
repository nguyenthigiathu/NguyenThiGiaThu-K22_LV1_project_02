# ==============================
# API CONFIG
# ==============================

PRODUCT_DETAIL_API = "https://api.tiki.vn/product-detail/api/v1/products/{product_id}"

# ==============================
# CRAWLER SETTINGS
# ==============================

MAX_CONCURRENT_REQUESTS = 50     # scheduler semaphore
BATCH_SIZE = 1000               # products per file

# ==============================
# RETRY / TIMEOUT
# ==============================

MAX_RETRIES = 5
BASE_RETRY_DELAY = 0.5           # seconds
REQUEST_TIMEOUT = 10             # seconds

# ==============================
# PATHS
# ==============================

OUTPUT_DIR = "output"
LOG_DIR = "logs"
CHECKPOINT_FILE = "output/checkpoint.json"

DEBUG = False