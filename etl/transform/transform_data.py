import re

def normalize(raw: dict) -> dict:
    """Chuẩn hoá dữ liệu theo yêu cầu: id, name, url_key, price, description, images url"""
    if not raw:
        return {}
    
    # Chuẩn hoá Description: Xoá HTML tags và thu gọn khoảng trắng
    desc = raw.get("description", "")
    if desc:
        # Xoá các thẻ HTML
        desc = re.sub(r'<[^>]*>', '', desc)
        # Thay thế thực thể HTML cơ bản (nếu có) và xoá khoảng trắng thừa
        desc = re.sub(r'\s+', ' ', desc).strip()

    # Lấy danh sách URL ảnh từ mảng images
    images = [img.get("base_url") for img in raw.get("images", []) if img.get("base_url")]

    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "url_key": raw.get("url_key"),
        "price": raw.get("price"),
        "description": desc,
        "images_url": images
    }