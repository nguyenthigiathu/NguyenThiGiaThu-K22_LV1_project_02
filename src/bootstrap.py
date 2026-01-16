import time
import asyncio
import signal
import sys
import os
import glob
import json

# Import các hằng số từ settings
from config.settings import (
    MAX_RESTARTS, 
    RESTART_DELAY, 
    OUTPUT_DIR, 
    ERROR_FILE, 
    CHECKPOINT_FILE,
    BATCH_SIZE
)
# Import pipeline và các công cụ hỗ trợ
from etl.load.load_data import run_pipeline
from src.utils.logger import info, error
from src.utils.notifier import send_alert_sync

# --- 1. XỬ LÝ TÍN HIỆU DỪNG (CTRL+C) ---
def handle_exit(sig, frame):
    """Hàm xử lý khi người dùng nhấn Ctrl+C hoặc hệ thống gửi SIGTERM"""
    msg = "Bot đã bị dừng thủ công hoặc đột ngột."
    print(f"\n[!] {msg}")
    send_alert_sync(msg)
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# --- 2. CÁC HÀM TIỆN ÍCH HỆ THỐNG ---

def get_current_checkpoint():
    """Lấy vị trí đã xử lý từ file checkpoint"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                # Đồng bộ key 'processed' với class Checkpoint
                return json.load(f).get("processed", 0)
        except Exception as e:
            error(f"Lỗi đọc checkpoint: {e}")
            return 0
    return 0

def load_ids():
    """Đọc 200k ID từ file CSV"""
    path = "products-ids.csv"
    if not os.path.exists(path):
        print(f"[!] LỖI: Không tìm thấy file {path}")
        return []
    try:
        with open(path, "r") as f:
            # Lấy tất cả các dòng là số
            ids = [int(line.strip()) for line in f if line.strip().isdigit()]
            return ids
    except Exception as e:
        error(f"Lỗi đọc file ID: {e}")
        return []

def load_failed_ids():
    """Lấy danh sách ID bị lỗi để chạy lại (mode retry)"""
    if not os.path.exists(ERROR_FILE):
        return []
    failed_ids = set()
    try:
        with open(ERROR_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        failed_ids.add(int(data["product_id"]))
                    except: continue
        
        if failed_ids:
            # Đổi tên file lỗi cũ để không bị ghi đè chồng chéo
            timestamp = int(time.time())
            os.rename(ERROR_FILE, f"{ERROR_FILE}.{timestamp}.bak")
            # Reset checkpoint để chạy lại từ đầu danh sách lỗi
            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
        return list(failed_ids)
    except Exception as e:
        error(f"Lỗi load ID thất bại: {e}")
        return []

def print_final_report(start_time, total_target):
    """In bảng thống kê sau khi hoàn thành lượt chạy"""
    end_time = time.time()
    duration = max(end_time - start_time, 1)
    
    # Đếm số lỗi thực tế trong file log lỗi
    new_errors = 0
    if os.path.exists(ERROR_FILE):
        with open(ERROR_FILE, "r", encoding="utf-8") as f:
            new_errors = sum(1 for line in f if line.strip())

    success = max(total_target - new_errors, 0)
    json_files = glob.glob(f"{OUTPUT_DIR}/products_*.json")
    total_size_mb = sum(os.path.getsize(f) for f in json_files) / (1024 * 1024)

    summary = {
        "Tổng ID mục tiêu": f"{total_target:,}",
        "Thành công": f"{success:,}",
        "Thất bại (Lỗi)": f"{new_errors:,}",
        "Thời gian chạy": f"{duration/60:.2f} phút",
        "Tốc độ TB": f"{success/duration:.2f} SP/giây",
        "Tổng dung lượng": f"{total_size_mb:.1f} MB"
    }

    # ===== build report_str =====
    max_key_len = max(len(k) for k in summary)

    lines = []
    lines.append("BÁO CÁO HOÀN THÀNH TIKI CRAWLING PROJECT")
    lines.append("-" * 30)

    for k, v in summary.items():
        lines.append(f"{k:<{max_key_len}} : {v}")

    report_str = "\n".join(lines)

    # ===== print ra console =====
    print("\n" + "=" * 30)
    print(report_str)
    print("=" * 30)

    # ===== lưu báo cáo =====
    with open(os.path.join(OUTPUT_DIR, "last_report.txt"), "w", encoding="utf-8") as f:
        f.write(report_str)

    # ===== gửi alert =====
    send_alert_sync(
        f"Hoàn tất lượt chạy!\n```\n{report_str}\n```"
    )

# --- 3. HÀM KHỞI CHẠY CHÍNH (ENTRY POINT) ---

def start(mode="full"):
    """Điều phối toàn bộ quy trình Crawl"""
    print("\n[*] Đang khởi tạo hệ thống...")
    
    # 1. Load dữ liệu
    if mode == "retry":
        pids = load_failed_ids()
        checkpoint_idx = 0
        print(f"[*] Chế độ: RETRY (Chạy lại các ID lỗi)")
    else:
        pids = load_ids()
        checkpoint_idx = get_current_checkpoint()
        print(f"[*] Chế độ: FULL (Tải mới/Tiếp tục)")

    if not pids:
        print("[!] Không có dữ liệu để xử lý. Vui lòng kiểm tra lại nguồn cấp ID.")
        return

    total_all = len(pids)
    
    # 2. Kiểm tra hoàn thành
    if mode == "full" and checkpoint_idx >= total_all:
        msg = f"Dữ liệu đã hoàn thành 100% ({total_all:,} sản phẩm). Không có gì để làm."
        send_alert_sync(msg)
        return

    # 3. Thông báo trạng thái trước khi vào vòng lặp nặng
    ids_to_run = total_all - checkpoint_idx
    start_time = time.time()
    
    status_msg = f"Bắt đầu chạy. Vị trí: {checkpoint_idx:,}/{total_all:,}. Cần xử lý: {ids_to_run:,} SP."
    
    # Đảm bảo thông báo này hiện ra trước khi chạy asyncio
    send_alert_sync(status_msg)

    # 4. Cơ chế tự động chạy lại nếu gặp lỗi hệ thống (Crash)
    for attempt in range(MAX_RESTARTS):
        try:
            print(f"[*] Đang thực thi Pipeline (Lần thử {attempt + 1})...")
            # Chạy vòng lặp sự kiện Async
            asyncio.run(run_pipeline(pids))
            
            # Nếu chạy đến đây tức là pipeline đã hoàn thành mảng pids mà không crash
            print_final_report(start_time, ids_to_run)
            break
            
        except Exception as e:
            error_msg = f"Hệ thống gặp sự cố nghiêm trọng: {str(e)}"
            error(error_msg)
            send_alert_sync(f"CẢNH BÁO: {error_msg}")
            
            if attempt < MAX_RESTARTS - 1:
                print(f"[!] Restart sau {RESTART_DELAY} giây...")
                time.sleep(RESTART_DELAY)
            else:
                print("[!] Đã đạt giới hạn Restart tối đa. Dừng Bot.")