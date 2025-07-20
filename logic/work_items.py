from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from infra.base_page import BasePage


class WorkItems(BasePage):
    # Locators
    SEARCH_BAR_INPUT = '#\_\_bolt-textfield-input-1'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def fill_bug_id_input(self, bug_id):
        """
        Fills the Bug ID on the Search Bar.
        """
        WebDriverWait(self._driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.SEARCH_BAR_INPUT))).send_keys(bug_id)


