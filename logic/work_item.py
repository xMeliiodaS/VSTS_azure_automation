from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from infra.base_page import BasePage


class WorkItem(BasePage):
    # -----------------Locators Related to Bugs-----------------
    STD_ID_FIELD = 'input[aria-label="STD ID"]'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def get_std_id_value(self):
        field = WebDriverWait(self._driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.STD_ID_FIELD)))
        return field.get_attribute("value")

    def fill_std_id_input(self, std_id_list):
        """
        Fills the STD ID field according to the given list.
        """
        WebDriverWait(self._driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.STD_ID_FIELD))).send_keys(std_id_list)

    def check_std_id_is_empty(self):
        """
        Checks whether the STD ID input field is empty, unset, or set to the string "None" (case-insensitive).
        """
        field = WebDriverWait(self._driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.STD_ID_FIELD)))
        value = field.get_attribute("value")
        return value is None or value == "" or value.strip().lower() == "none"
