from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

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
        WebDriverWait(self._driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.CLOSE_CURRENT_BUG_BUTTON))).click()
