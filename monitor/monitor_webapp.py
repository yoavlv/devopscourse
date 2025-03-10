import json
import requests
import sys
import time
from datetime import datetime

def load_config():
    with open('config.json') as f:
        return json.load(f)

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def monitor_website():
    config = load_config()
    url = config.get("url")
    expected_status = config.get("expected_status", 200)
    timeout = config.get("timeout", 5)
    max_response_time = config.get("max_response_time", 2000)  # in milliseconds
    content_check = config.get("content_check")

    try:
        log(f"Checking website: {url}")
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()

        # Calculate response time in milliseconds
        response_time_ms = int((end_time - start_time) * 1000)
        log(f"Response time: {response_time_ms} ms")

        # Status Code Check
        if response.status_code != expected_status:
            log(f"FAIL: Expected status {expected_status}, got {response.status_code}")
            sys.exit(1)

        # Response Time Check
        if response_time_ms > max_response_time:
            log(f"FAIL: Response time {response_time_ms} ms exceeded max of {max_response_time} ms")
            sys.exit(1)

        # Content Check
        if content_check and content_check not in response.text:
            log(f"FAIL: Content '{content_check}' not found in the response")
            sys.exit(1)

        log("SUCCESS: Website is healthy.")
        sys.exit(0)

    except requests.RequestException as e:
        log(f"FAIL: Website is DOWN! Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    monitor_website()
