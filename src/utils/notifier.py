import aiohttp
import requests
from config.settings import DISCORD_WEBHOOK_URL
from src.utils.logger import error, info

async def send_alert(msg: str):
    """Gửi thông báo bất đồng bộ (Async)"""
    # Luôn in ra terminal để người dùng biết
    info(f"[Discord Alert]: {msg}")
    
    if not DISCORD_WEBHOOK_URL: 
        return
    try:
        async with aiohttp.ClientSession() as s:
            payload = {"content": f"**Tiki Bot**: {msg}"}
            async with s.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5) as r:
                pass
    except Exception as e:
        error(f"Discord lỗi (Async): {e}")

def send_alert_sync(msg: str):
    """Gửi thông báo đồng bộ (Sync)"""
    # Luôn in ra terminal
    print(f"[*] {msg}")
    
    if not DISCORD_WEBHOOK_URL: 
        return
    try:
        payload = {"content": f"**Tiki System**: {msg}"}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        error(f"Discord lỗi (Sync): {e}")