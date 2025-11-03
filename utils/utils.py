import time

import logging
from infra.logger_setup import logger_setup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException, NoSuchElementException, InvalidSessionIdException, WebDriverException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException


def safe_click(driver, css_selector: str, retries: int = 3, wait_time: int = 5) -> bool:
    """
    Safely clicks an element with retries, scrolling into view and handling common Selenium errors.
    """
    for attempt in range(1, retries + 1):
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            element.click()
            return True
        except (TimeoutException, NoSuchElementException, InvalidSessionIdException, WebDriverException) as e:
            logging.error(f"Attempt {attempt} failed for {css_selector}: {str(e)}")
            if attempt == retries:
                return False
    return False


def smart_click(driver, locator, retries=3, wait_time=20, post_condition_locator=None, js_fallback=True):
    """
    Clicks an element safely with retries and optional post-click verification.

    :param driver: Selenium WebDriver instance
    :param locator: Tuple or CSS selector string
    :param retries: Number of retry attempts if click fails
    :param wait_time: Seconds to wait for element to be clickable
    :param post_condition_locator: Optional locator to verify action succeeded
    :param js_fallback: If True, fallback to JS click if normal click fails
    :return: True if clicked and post-condition met (if any), else False
    """
    # normalize locator if string
    if isinstance(locator, str):
        locator = (By.CSS_SELECTOR, locator)

    attempt = 0
    while attempt < retries:
        try:
            # wait for element to be clickable
            el = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable(locator))

            try:
                el.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                if js_fallback:
                    driver.execute_script("arguments[0].click();", el)
                else:
                    raise

            # if post-condition is provided, wait for it
            if post_condition_locator:
                if isinstance(post_condition_locator, str):
                    post_condition_locator = (By.CSS_SELECTOR, post_condition_locator)
                WebDriverWait(driver, wait_time).until(
                    EC.visibility_of_element_located(post_condition_locator)
                )
            return True
        except TimeoutException:
            print(f"[WARN] Attempt {attempt + 1} failed: element not clickable or post-condition not met.")
            attempt += 1
        except Exception as e:
            print(f"[ERROR] Attempt {attempt + 1} failed: {e}")
            attempt += 1
    return False


def wait_until_element_present(driver, by, selector, timeout=10, poll_frequency=0.2):
    start = time.time()
    while True:
        try:
            if driver.find_element(by, selector):
                return True
        except Exception:
            pass
        if time.time() - start > timeout:
            return False
        time.sleep(poll_frequency)


import os
import shutil


def save_report_copy(report_path: str):
    """Copies a generated report into AppData for persistence."""
    app_data_folder = os.path.join(
        os.getenv("APPDATA"),
        "AT_baseline_verifier"
    )
    os.makedirs(app_data_folder, exist_ok=True)

    report_filename = os.path.basename(report_path)
    target_path = os.path.join(app_data_folder, report_filename)
    shutil.copy(report_path, target_path)
