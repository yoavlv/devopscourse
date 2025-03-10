import json
import os
import shutil
import sys
import time
import zipfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ✅ Load JSON Configuration
try:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
except Exception as e:
    print(f"[ERROR] Failed to load config.json: {e}")
    sys.exit(1)

# ✅ Extract config variables
BASE_URL = config.get("base_url")
EXPECTED_HOME_TITLE = config.get("expected_home_title")
EXPECTED_ABOUT_TEXT = config.get("expected_about_text")
TEST_USERNAME = config.get("test_username")
EXPECTED_GREETING = config.get("expected_greeting")

CHROMEDRIVER_URL = config.get("chromedriver_url")
CHROMEDRIVER_DIR = config.get("chromedriver_dir")
CHROMEDRIVER_ZIP = "chromedriver.zip"
CHROME_BINARY_PATH = config.get("chrome_binary_path")

CHROMEDRIVER_EXE = os.path.join(CHROMEDRIVER_DIR, "chromedriver.exe")

# ✅ PRE-TEST: Download and extract ChromeDriver
def download_and_extract_chromedriver():
    if not os.path.exists(CHROMEDRIVER_DIR):
        os.makedirs(CHROMEDRIVER_DIR)

    print(f"[INFO] Downloading ChromeDriver from {CHROMEDRIVER_URL}...")
    try:
        response = requests.get(CHROMEDRIVER_URL, stream=True)
        with open(CHROMEDRIVER_ZIP, "wb") as zip_file:
            for chunk in response.iter_content(chunk_size=8192):
                zip_file.write(chunk)
        print("[INFO] Download complete.")

        print("[INFO] Extracting ChromeDriver...")
        with zipfile.ZipFile(CHROMEDRIVER_ZIP, 'r') as zip_ref:
            zip_ref.extractall(CHROMEDRIVER_DIR)

        # Move chromedriver.exe up one level
        extracted_driver = os.path.join(CHROMEDRIVER_DIR, "chromedriver-win64", "chromedriver.exe")
        if os.path.exists(extracted_driver):
            final_driver_path = os.path.join(CHROMEDRIVER_DIR, "chromedriver.exe")
            shutil.move(extracted_driver, final_driver_path)
            shutil.rmtree(os.path.join(CHROMEDRIVER_DIR, "chromedriver-win64"))
            print(f"[INFO] ChromeDriver moved to {final_driver_path}")
        else:
            print("[ERROR] ChromeDriver executable not found after extraction!")
            sys.exit(1)

        # Remove the zip file after extraction (optional cleanup)
        os.remove(CHROMEDRIVER_ZIP)
        print("[INFO] Cleanup complete.")

    except Exception as e:
        print(f"[ERROR] Failed to download or extract ChromeDriver: {e}")
        sys.exit(1)

def verify_chromedriver():
    if not os.path.exists(CHROMEDRIVER_EXE):
        print("[ERROR] ChromeDriver not found! Exiting.")
        sys.exit(1)
    else:
        print(f"[INFO] ChromeDriver is ready at {CHROMEDRIVER_EXE}")

# ✅ Run pre-test setup
try:
    download_and_extract_chromedriver()
except Exception as e:
    print(f"[ERROR] ChromeDriver download failed: {e}")
    sys.exit(1)

try:
    verify_chromedriver()
except Exception as e:
    print(f"[ERROR] ChromeDriver verification failed: {e}")
    sys.exit(1)

# ✅ Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")                # Headless mode
chrome_options.add_argument("--no-sandbox")              # For Jenkins
chrome_options.add_argument("--disable-gpu")             # Disable GPU rendering
chrome_options.add_argument("--disable-dev-shm-usage")   # Overcome limited resources
chrome_options.add_argument("--window-size=1920x1080")   # Standard window size

# If Jenkins can't find Chrome, specify the binary location
chrome_options.binary_location = CHROME_BINARY_PATH

# ✅ Setup ChromeDriver service (using downloaded driver)
service = Service(CHROMEDRIVER_EXE)

# ✅ Initialize WebDriver
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    print(f"[ERROR] Failed to start Chrome WebDriver: {e}")
    sys.exit(1)

# ✅ Pre-test ping (basic health check before Selenium)
print(f"[INFO] Checking if {BASE_URL} is reachable...")
try:
    response = requests.get(BASE_URL, timeout=5)
    if response.status_code != 200:
        print(f"[ERROR] Pre-test failed! {BASE_URL} returned status code: {response.status_code}")
        driver.quit()
        sys.exit(1)
    else:
        print(f"[INFO] Pre-test passed! {BASE_URL} is reachable.")
except requests.RequestException as e:
    print(f"[ERROR] Pre-test failed! Error: {e}")
    driver.quit()
    sys.exit(1)

# ✅ Start Selenium Tests
try:
    # 1️⃣ Verify Home Page Loads
    print("[INFO] Opening Home Page...")
    driver.get(BASE_URL + "/")
    assert EXPECTED_HOME_TITLE in driver.title
    print("[SUCCESS] Home page loaded successfully.")

    # 2️⃣ Verify Input Box Exists
    input_box = driver.find_element(By.NAME, "username")
    assert input_box is not None
    print("[SUCCESS] Username input box found.")

    # 3️⃣ Submit Form (simulate user input)
    input_box.send_keys(TEST_USERNAME)
    input_box.send_keys(Keys.RETURN)
    time.sleep(1)

    # Verify greeting
    assert EXPECTED_GREETING in driver.page_source
    print("[SUCCESS] Form submission successful.")

    # 4️⃣ Verify About Page Loads Correctly
    print("[INFO] Opening About Page...")
    driver.get(BASE_URL + "/about.jsp")
    assert EXPECTED_ABOUT_TEXT in driver.page_source
    print("[SUCCESS] About page loaded successfully.")

except AssertionError as e:
    print("[FAIL] TEST FAILED (Assertion Error)!")
    driver.quit()
    sys.exit(1)

except Exception as e:
    print(f"[ERROR] Error during test execution: {e}")
    driver.quit()
    sys.exit(1)

else:
    print("[SUCCESS] ALL TESTS PASSED!")

finally:
    driver.quit()
    sys.exit(0)