import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.utils import safe_click

from infra.base_page import BasePage


class BasePageApp(BasePage):
    # -----------------Locators Related to Bugs-----------------
    CLOSE_CURRENT_BUG_BUTTON = 'button[title="Close"]'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def close_current_bug_button(self):
        """
        Exit the opened window of the current bug.
        """
        time.sleep(0.15)
        safe_click(self._driver, self.CLOSE_CURRENT_BUG_BUTTON, retries=3, wait_time=10)
