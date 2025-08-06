from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from infra.base_page import BasePage


class WorkItem(BasePage):
    # -----------------Locators Related to Bugs-----------------
    STD_ID_FIELD = 'input[aria-label="STD ID"]'
    ADDITIONAL_INFO_BUTTON = 'li.work-item-form-tab[aria-label="Additional Information"]'
    ADDITIONAL_INFO_FILED = 'div[aria-label="AdditionalInfo:"]'

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

    def check_std_id_is_empty(self):
        """
        Checks whether the STD ID input field is empty, unset, or set to the string "None" (case-insensitive).
        """
        field = WebDriverWait(self._driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.STD_ID_FIELD)))
        value = field.get_attribute("value")
        return value is None or value == "" or value.strip().lower() == "none"

    def click_on_additional_info_tab(self):
        """
        Click on the Additional Info Tab inside the work item.
        """
        WebDriverWait(self._driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADDITIONAL_INFO_BUTTON))).click()

    def get_additional_info_value(self):
        field = WebDriverWait(self._driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADDITIONAL_INFO_FILED)))
        return field.text
