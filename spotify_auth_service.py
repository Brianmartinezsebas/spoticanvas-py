import os
import requests
import pyotp
import time
import base64
import threading
from dotenv import load_dotenv

load_dotenv()

SP_DC = os.getenv("SP_DC")
SECRETS_URL = "https://raw.githubusercontent.com/Thereallo1026/spotify-secrets/refs/heads/main/secrets/secretDict.json"

# Variables globales para almacenar la configuración TOTP actual
current_totp = None
current_totp_version = None
last_fetch_time = 0
FETCH_INTERVAL = 60 * 60  # 1 hora en segundos
totp_lock = threading.Lock()

def user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

def create_totp_secret(data):
    """Crea el secreto TOTP a partir de los datos"""
    mapped_data = [value ^ ((index % 33) + 9) for index, value in enumerate(data)]
    hex_data = ''.join(map(str, mapped_data)).encode('utf-8').hex()
    return base64.b32encode(bytes.fromhex(hex_data)).decode('utf-8').rstrip('=')

def fetch_secrets_from_github():
    """Obtiene los secretos desde GitHub"""
    try:
        response = requests.get(
            SECRETS_URL,
            timeout=10,
            headers={
                'User-Agent': user_agent()
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f'Error al obtener secretos desde GitHub: {e}')
        raise e

def find_newest_version(secrets):
    """Encuentra la versión más nueva de los secretos"""
    versions = [int(k) for k in secrets.keys()]
    return str(max(versions))

def use_fallback_secret():
    """Usa el secreto de respaldo hardcodeado"""
    global current_totp, current_totp_version
    
    # Secreto de respaldo (probablemente fallará porque Spotify rota los secretos cada pocos días)
    fallback_data = [99, 111, 47, 88, 49, 56, 118, 65, 52, 67, 50, 104, 117, 101, 55, 94, 95, 75, 94, 49, 69, 36, 85, 64, 74, 60]
    secret_b32 = create_totp_secret(fallback_data)
    
    current_totp = pyotp.TOTP(secret_b32, digits=6, interval=30)
    current_totp_version = "19"  # Versión de respaldo
    print('Usando secreto TOTP de respaldo')

def update_totp_secrets():
    """Actualiza los secretos TOTP"""
    global current_totp, current_totp_version, last_fetch_time
    
    try:
        now = time.time()
        if now - last_fetch_time < FETCH_INTERVAL:
            return  # No obtener muy frecuentemente
        
        print('Obteniendo secretos TOTP actualizados...')
        secrets = fetch_secrets_from_github()
        newest_version = find_newest_version(secrets)
        
        with totp_lock:
            if newest_version and newest_version != current_totp_version:
                secret_data = secrets[newest_version]
                secret_b32 = create_totp_secret(secret_data)
                
                current_totp = pyotp.TOTP(secret_b32, digits=6, interval=30)
                current_totp_version = newest_version
                last_fetch_time = now
                print(f'Secretos TOTP actualizados a la versión {newest_version}')
            else:
                print(f'No se encontraron nuevos secretos TOTP, usando versión {newest_version}')
                
    except Exception as e:
        print(f'Error al actualizar secretos TOTP: {e}')
        # Mantener el TOTP actual si está disponible, sino usar respaldo
        if not current_totp:
            use_fallback_secret()

def initialize_totp_secrets():
    """Inicializa los secretos TOTP al inicio"""
    try:
        update_totp_secrets()
    except Exception as e:
        print(f'Error al inicializar secretos TOTP: {e}')
        # Respaldo al secreto hardcodeado original
        use_fallback_secret()

def generate_totp(timestamp):
    """Genera el código TOTP para un timestamp dado"""
    if not current_totp:
        raise Exception("TOTP no inicializado")
    
    with totp_lock:
        return current_totp.at(int(timestamp // 1000))

def get_server_time():
    """Obtiene el tiempo del servidor de Spotify"""
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
        if not server_time:
            raise Exception("Tiempo de servidor inválido")
        return server_time * 1000
    except Exception:
        return int(time.time() * 1000)

def generate_auth_payload(reason, product_type):
    """Genera el payload de autenticación"""
    local_time = int(time.time() * 1000)
    server_time = get_server_time()
    
    return {
        "reason": reason,
        "productType": product_type,
        "totp": generate_totp(local_time),
        "totpVer": current_totp_version or "19",
        "totpServer": generate_totp(server_time // 30)
    }

def get_token(reason="init", product_type="mobile-web-player"):
    """Obtiene el token de acceso de Spotify"""
    # Asegurar que tenemos una instancia TOTP
    if not current_totp:
        initialize_totp_secrets()
    
    # Verificar si necesitamos actualizar los secretos
    if time.time() - last_fetch_time >= FETCH_INTERVAL:
        try:
            update_totp_secrets()
        except Exception:
            pass  # Continuar con el TOTP actual si la actualización falla
    
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

# Inicializar los secretos TOTP al importar el módulo
initialize_totp_secrets()

# Configurar actualizaciones periódicas en un hilo separado
def periodic_update():
    """Función para actualizaciones periódicas en segundo plano"""
    while True:
        time.sleep(FETCH_INTERVAL)
        try:
            update_totp_secrets()
        except Exception as e:
            print(f'Error en actualización periódica: {e}')

# Iniciar el hilo de actualización periódica
update_thread = threading.Thread(target=periodic_update, daemon=True)
update_thread.start()
