import time

import logging
from infra.logger_setup import logger_setup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException, NoSuchElementException


def safe_click(driver, css_selector, retries=3, wait_time=5):
    """
    Safely clicks an element with retries, handling any potential errors.
    :param driver:
    :param css_selector: The CSS Selector of the element to click.
    :param retries: Number of retries if an element is not clickable.
    :param wait_time: Time to wait between retries.
    :return: True if the click was successful, False otherwise.
    """
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            element.click()
            return True  # Success
        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"Attempt {attempt + 1} failed for {css_selector}: {str(e)}")
            time.sleep(wait_time)
    return False  # Failed after retries
