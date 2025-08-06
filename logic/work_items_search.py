import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from infra.base_page import BasePage


class WorkItemsSearch(BasePage):
    # -----------------Locators Related to Bugs-----------------
    SEARCH_BAR_INPUT = '#l1-search-input'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def fill_bug_id_input_and_press_enter(self, bug_id):
        """
        Clear Search bar and fills the Bug ID on the Search Bar.
        """
        search_bar = WebDriverWait(self._driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.SEARCH_BAR_INPUT)))

        search_bar.click()
        search_bar.send_keys(Keys.CONTROL + "a")
        search_bar.send_keys(Keys.DELETE)

        search_bar.send_keys(bug_id)

        time.sleep(0.2)
        search_bar.send_keys(Keys.ENTER)
