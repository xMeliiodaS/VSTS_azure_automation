import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from infra.base_page import BasePage
from utils.utils import safe_click


class WorkItemsSearch(BasePage):
    # -----------------Locators Related to Bugs-----------------
    SEARCH_BAR_INPUT = '#l1-search-input'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def fill_bug_id_input_and_press_enter(self, bug_id: str):
        """
        Clear Search bar and fill the Bug ID then hit Enter.
        """
        # ensure visible/clickable
        input_el = self.wait_clickable(By.CSS_SELECTOR, self.SEARCH_BAR_INPUT, timeout=10)

        safe_click(self._driver, self.SEARCH_BAR_INPUT, retries=3, wait_time=10)

        input_el.send_keys(Keys.CONTROL, "a")
        input_el.send_keys(Keys.DELETE)
        input_el.send_keys(str(bug_id))
        input_el.send_keys(Keys.ENTER)

        # optional: wait for results to load (generic heuristic)
        self.wait_present(By.CSS_SELECTOR, self.SEARCH_BAR_INPUT, timeout=10)