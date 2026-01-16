import sys
from src.bootstrap import start

if __name__ == "__main__":
    # python3 -m main -> Chạy mới
    # python3 -m main retry -> Chạy lại các ID lỗi
    mode = "retry" if len(sys.argv) > 1 and sys.argv[1] == "retry" else "full"
    start(mode=mode)