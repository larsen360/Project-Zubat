import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import time
import os
import random
import subprocess
import json
import zipfile
import requests

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # til Linux (Raspberry Pi)

SCREENSHOT_DIR = 'screenshots'
SEEN_FILE_PREFIX = 'seen_'  # hver shop får sin egen historikfil
TARGETS_FILE = 'targets.json'
CHROME_DRIVER_URL = "https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.70/win64/chrome-win64.zip"
CHROME_DRIVER_ZIP = "chrome-win64.zip"
CHROME_DRIVER_DIR = "chrome-win64"

if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

def ensure_chrome_driver():
    if not os.path.exists(CHROME_DRIVER_DIR):
        print("⬇️ Downloader Chrome-driver...")
        r = requests.get(CHROME_DRIVER_URL)
        with open(CHROME_DRIVER_ZIP, 'wb') as f:
            f.write(r.content)
        with zipfile.ZipFile(CHROME_DRIVER_ZIP, 'r') as zip_ref:
            zip_ref.extractall('.')
        print("✅ Chrome-driver hentet og udpakket.")


def load_targets():
    if not os.path.exists(TARGETS_FILE):
        raise FileNotFoundError(f"Konfigurationsfil '{TARGETS_FILE}' findes ikke.")
    with open(TARGETS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_seen_products(site_name):
    filename = f"{SEEN_FILE_PREFIX}{site_name.replace(' ', '_').lower()}.txt"
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen_product(site_name, product):
    filename = f"{SEEN_FILE_PREFIX}{site_name.replace(' ', '_').lower()}.txt"
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(product + '\n')

def try_accept_cookies(driver):
    try:
        time.sleep(1.5)
        accept_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Accepter alle') or contains(text(), 'Accepter') or contains(text(), 'Accept all') or contains(text(), 'Godkend alle') or contains(text(), 'Tillad alle') or contains(text(), 'OK')]")
        for button in accept_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)
                print("🟢 Accepterede cookies.")
                time.sleep(1.5)
                break
            except Exception:
                continue
    except Exception:
        pass

def get_html_with_selenium(url, scrolls=1, site_name="screenshot"):
    options = uc.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.binary_location = os.path.abspath(f"{CHROME_DRIVER_DIR}/chrome.exe") if os.name == 'nt' else None
    driver = uc.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(random.uniform(2.5, 4.5))

        try_accept_cookies(driver)

        for _ in range(scrolls):
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
            time.sleep(random.uniform(0.4, 0.8))

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_name = f"{SCREENSHOT_DIR}/{site_name.replace(' ', '_').lower()}_{timestamp}.png"
        driver.save_screenshot(screenshot_name)
        print(f"📸 Screenshot gemt: {screenshot_name}")
        html = driver.page_source
    except Exception as e:
        print(f"⚠️ Fejl ved hentning af {url}: {e}")
        html = ""
    finally:
        driver.quit()

    return html, screenshot_name

def notify(site, match):
    print(f"🔔 {site}: Nyt match fundet – '{match}'")

def check_site(site):
    name = site["name"]
    url = site["url"]
    keywords = site["match_keywords"]
    scrolls = site.get("scroll_downs", 1)

    seen = load_seen_products(name)
    html, screenshot_path = get_html_with_selenium(url, scrolls, name)

    if not html:
        # OCR fallback
        try:
            image = Image.open(screenshot_path)
            text = pytesseract.image_to_string(image)
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    if keyword not in seen:
                        notify(name, keyword)
                        save_seen_product(name, keyword)
        except Exception as e:
            print(f"🧨 OCR-fejl for {name}: {e}")
        return

    # HTML analyse
    soup = BeautifulSoup(html, 'html.parser')
    found_any = False
    for keyword in keywords:
        if keyword.lower() in soup.get_text().lower():
            if keyword not in seen:
                notify(name, keyword)
                save_seen_product(name, keyword)
                found_any = True

    if not found_any:
        print(f"✅ {name}: Ingen nye matches.")

if __name__ == '__main__':
    ensure_chrome_driver()
    targets = load_targets()
    while True:
        for site in targets:
            print(f"\n🌐 Tjekker: {site['name']}")
            check_site(site)
        time.sleep(60 * 5)  # Tjek hvert 5. minut
