import time

import logging
from infra.logger_setup import logger_setup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException, NoSuchElementException, InvalidSessionIdException, WebDriverException


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