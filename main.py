#!/usr/bin/env python3
# streaming_scraper.py
import csv
import json
import os
import string
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

# ---------- Config ----------
BASE_URL = "https://www.webmd.com/drugs/2/alpha/"
CSV_PATH = "drugs_list.csv"
NDJSON_PATH = "drugs_list.ndjson"  # streaming-friendly JSON lines
WAIT_SECONDS = 2
PAUSE_AFTER_LOAD = 0.5
HEADLESS = True
# ----------------------------


def make_driver(headless=True):
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def normalize_link(href: str) -> str:
    if not href:
        return ""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return "https://www.webmd.com" + href
    return "https://www.webmd.com/" + href.lstrip("/")


def open_output_files(csv_path, ndjson_path):
    # Open CSV in append mode and write header if file is new
    new_csv = not Path(csv_path).exists()
    csv_f = open(csv_path, "a", newline="", encoding="utf-8-sig")
    csv_writer = csv.writer(csv_f)
    if new_csv:
        csv_writer.writerow(["Alphabet", "Drug Name", "Link"])
        csv_f.flush()
        os.fsync(csv_f.fileno())
    # NDJSON (append mode)
    ndjson_f = open(ndjson_path, "a", encoding="utf-8")
    return csv_f, csv_writer, ndjson_f


def flush_files(*files):
    for f in files:
        try:
            f.flush()
            os.fsync(f.fileno())
        except Exception:
            try:
                # fallback to flush only
                f.flush()
            except Exception:
                pass


def stream_scrape(driver):
    seen_global = set()
    csv_f, csv_writer, ndjson_f = open_output_files(CSV_PATH, NDJSON_PATH)

    try:
        for first in string.ascii_lowercase:
            for second in string.ascii_lowercase:
                sub = f"{first}{second}"
                url = f"{BASE_URL}{first}/{sub}"
                print(f"[{first}] Visiting: {url}", flush=True)
                try:
                    driver.get(url)
                except WebDriverException as e:
                    print("  ! webdriver error:", e)
                    continue

                time.sleep(PAUSE_AFTER_LOAD)
                try:
                    WebDriverWait(driver, WAIT_SECONDS).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "a.alpha-drug-name")
                        )
                    )
                except TimeoutException:
                    # no items on this page
                    continue

                elems = driver.find_elements(By.CSS_SELECTOR, "a.alpha-drug-name")
                added = 0
                for e in elems:
                    try:
                        name = e.text.strip()
                        href = e.get_attribute("href") or ""
                        href = normalize_link(href)
                    except Exception:
                        continue
                    if not name:
                        continue
                    key = f"{name}||{href}"
                    if key in seen_global:
                        continue
                    seen_global.add(key)

                    # write CSV immediately
                    csv_writer.writerow([first, name, href])
                    # write NDJSON immediately
                    ndjson_f.write(
                        json.dumps(
                            {"alpha": first, "name": name, "link": href},
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                    # flush both files so external readers see updates instantly
                    flush_files(csv_f, ndjson_f)

                    # also print a small live message
                    print(f"   + [{first}] {name}", flush=True)
                    added += 1

                if added:
                    print(f"   ↳ collected {added} new items on {sub}")

        # Handle '0' page (only main)
        print("\n[0] Visiting:", BASE_URL + "0", flush=True)
        try:
            driver.get(BASE_URL + "0")
            time.sleep(PAUSE_AFTER_LOAD)
            try:
                WebDriverWait(driver, WAIT_SECONDS).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "a.alpha-drug-name")
                    )
                )
            except TimeoutException:
                pass
            elems = driver.find_elements(By.CSS_SELECTOR, "a.alpha-drug-name")
            added = 0
            for e in elems:
                name = e.text.strip()
                href = normalize_link(e.get_attribute("href") or "")
                if not name:
                    continue
                key = f"{name}||{href}"
                if key in seen_global:
                    continue
                seen_global.add(key)
                csv_writer.writerow(["0", name, href])
                ndjson_f.write(
                    json.dumps(
                        {"alpha": "0", "name": name, "link": href}, ensure_ascii=False
                    )
                    + "\n"
                )
                flush_files(csv_f, ndjson_f)
                print(f"   + [0] {name}", flush=True)
                added += 1
            if added:
                print(f"   ↳ collected {added} items on 0", flush=True)
        except WebDriverException as e:
            print("  ! webdriver error on 0:", e, flush=True)

    finally:
        csv_f.close()
        ndjson_f.close()


def main():
    driver = make_driver(headless=HEADLESS)
    try:
        stream_scrape(driver)
        print("\nDone. Outputs:", CSV_PATH, NDJSON_PATH, flush=True)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
