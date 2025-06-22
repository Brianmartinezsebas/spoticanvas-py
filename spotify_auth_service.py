import os
import requests
import pyotp
import time
import base64
from dotenv import load_dotenv

load_dotenv()
SP_DC = os.getenv("SP_DC")

def user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

def hex_to_base32(hex_str):
    b = bytes.fromhex(hex_str)
    b32 = base64.b32encode(b).decode("utf-8").replace("=", "")
    return b32

def generate_totp(timestamp):
    secret_hex = "35353037313435383533343837343939353932323438363330333239333437"
    secret_b32 = hex_to_base32(secret_hex)
    totp = pyotp.TOTP(secret_b32, digits=6, interval=30)
    return totp.at(int(timestamp // 1000))

def get_server_time():
    try:
        resp = requests.get(
            "https://open.spotify.com/server-time",
            headers={
                "User-Agent": user_agent(),
                "Origin": "https://open.spotify.com/",
                "Referer": "https://open.spotify.com/",
                "Cookie": f"sp_dc={SP_DC}",
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        server_time = int(data.get("serverTime", 0))
        return server_time * 1000
    except Exception:
        return int(time.time() * 1000)

def generate_auth_payload(reason, product_type):
    local_time = int(time.time() * 1000)
    server_time = get_server_time()
    return {
        "reason": reason,
        "productType": product_type,
        "totp": generate_totp(local_time),
        "totpVer": "5",
        "totpServer": generate_totp(server_time // 30),
        "sTime": str(server_time),
        "cTime": str(local_time),
        "buildVer": "web-player_2025-03-20_1742497479926_93656b9",
        "buildDate": "2025-03-20"
    }

def get_token(reason="init", product_type="web-player"):
    payload = generate_auth_payload(reason, product_type)
    url = "https://open.spotify.com/api/token"
    resp = requests.get(
        url,
        params=payload,
        headers={
            "User-Agent": user_agent(),
            "Origin": "https://open.spotify.com/",
            "Referer": "https://open.spotify.com/",
            "Cookie": f"sp_dc={SP_DC}",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("accessToken")