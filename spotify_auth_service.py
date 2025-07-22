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

def generate_totp_secret():
    data = [70, 60, 33, 57, 92, 120, 90, 33, 32, 62, 62, 55, 126, 93, 66, 35, 108, 68]
    mapped_data = [value ^ ((index % 33) + 9) for index, value in enumerate(data)]
    hex_data = ''.join(map(str, mapped_data)).encode('utf-8').hex()
    return base64.b32encode(bytes.fromhex(hex_data)).decode('utf-8').rstrip('=')

def generate_totp(timestamp):
    secret_b32 = generate_totp_secret()
    totp = pyotp.TOTP(secret_b32, digits=6, interval=30)
    return totp.at(int(timestamp // 1000))

def get_server_time():
    try:
        resp = requests.get(
            "https://open.spotify.com/api/server-time",
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
        "totpVer": "8",
        "totpServer": generate_totp(server_time // 30)
    }

def get_token(reason="init", product_type="mobile-web-player"):
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
