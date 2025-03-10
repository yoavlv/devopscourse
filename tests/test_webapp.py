import json
import os
import sys
import time

import requests  # Used for the pre-test ping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service  # <-- ADD THIS
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # Load config.json
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # Extract values from config
    base_url = config['base_url']
    expected_home_title = config['expected_home_title']
    expected_about_text = config['expected_about_text']
    test_username = config['test_username']
    expected_greeting = config['expected_greeting']

    # Pre-test ping (basic health check before Selenium)
    print(f"🔍 Pre-test: Checking if {base_url} is reachable...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Pre-test failed! {base_url} returned status code: {response.status_code}")
            sys.exit(1)
        else:
            print(f"✅ Pre-test passed! {base_url} is reachable.")
    except requests.RequestException as e:
        print(f"❌ Pre-test failed! Error: {e}")
        sys.exit(1)

    # Setup WebDriver (Chrome)
    driver = webdriver.Chrome()

    # 1️⃣ Verify Home Page Loads
    driver.get(base_url + "/")
    assert expected_home_title in driver.title
    print("✅ Home page loaded successfully.")

    # 2️⃣ Verify Input Box Exists
    input_box = driver.find_element(By.NAME, "username")
    assert input_box is not None
    print("✅ Username input box found.")

    # 3️⃣ Submit Form (simulate user input)
    input_box.send_keys(test_username)
    input_box.send_keys(Keys.RETURN)
    time.sleep(1)

    # Verify greeting
    assert expected_greeting in driver.page_source
    print("✅ Form submission successful.")

    # 4️⃣ Verify About Page Loads Correctly
    driver.get(base_url + "/about.jsp")
    assert expected_about_text in driver.page_source
    print("✅ About page loaded successfully.")

except AssertionError as e:
    print("❌ TEST FAILED!")
    driver.quit()
    sys.exit(1)

except Exception as e:
    print(f"❌ ERROR: {e}")
    driver.quit()
    sys.exit(1)

else:
    print("🎉 ALL TESTS PASSED!")

finally:
    driver.quit()
    sys.exit(0)
