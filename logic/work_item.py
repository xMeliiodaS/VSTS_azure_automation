from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.utils import safe_click
from utils.constants import Timeouts
from infra.base_page import BasePage


class WorkItem(BasePage):
    # -----------------Locators Related to Bugs-----------------
    STD_ID_FIELD = 'input[aria-label="STD ID"]'
    STD_NAME_FIELD = 'input[aria-label="STDName"]'
    ADDITIONAL_INFO_FILED = 'div[aria-label="AdditionalInfo:"]'
    ADDITIONAL_INFO_BUTTON = 'li.work-item-form-tab[aria-label="Additional Information"]'

    LAST_REPRODUCED_IN_FIELD = 'input[aria-label="LastRepreducedIn"]'
    ITERATION_PATH_FIELD = 'input.treepicker-item-title-input[readonly][aria-label="Iteration Path"]'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def get_std_id_value(self):
        """
        Wait for the STD_ID input field to be visible and return its current value attribute.
        """
        field = self.wait_visible(By.CSS_SELECTOR, self.STD_ID_FIELD, timeout=Timeouts.ELEMENT_VISIBILITY_TIMEOUT)
        return field.get_attribute("value")

    def get_std_name_value(self):
        """
        Wait for the STD Name input field to be visible and return its current value attribute.
        """
        field = self.wait_visible(By.CSS_SELECTOR, self.STD_NAME_FIELD, timeout=Timeouts.ELEMENT_VISIBILITY_TIMEOUT)
        return field.get_attribute("value")

    def get_last_reproduce_in_value(self):
        """
        Wait for the Last_Reproduced_In input field to be visible and return its current value attribute.
        """
        field = self.wait_visible(By.CSS_SELECTOR, self.LAST_REPRODUCED_IN_FIELD, timeout=Timeouts.ELEMENT_VISIBILITY_TIMEOUT)
        return field.get_attribute("value")

    def get_iteration_path_value(self):
        """
        Wait for the Iteration_Path input field to be visible and return its current value attribute.
        """
        field = self.wait_visible(By.CSS_SELECTOR, self.ITERATION_PATH_FIELD, timeout=Timeouts.ELEMENT_VISIBILITY_TIMEOUT)
        return field.get_attribute("value")

    def check_std_id_is_empty(self):
        """
        Checks whether the STD ID input field is empty, unset, or set to the string "None" (case-insensitive).
        """
        field = WebDriverWait(self._driver, Timeouts.FIELD_VALIDATION_TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.STD_ID_FIELD)))
        value = field.get_attribute("value")
        return value is None or value == "" or value.strip().lower() == "none"

    def click_on_additional_info_tab(self):
        """
        Click on the Additional Info Tab inside the work item.
        """
        safe_click(self._driver, self.ADDITIONAL_INFO_BUTTON)

    def get_additional_info_value(self):
        """
        Wait for the 'Additional Info' field to be visible and return its text content.
        """
        field = WebDriverWait(self._driver, Timeouts.FIELD_VALIDATION_TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.ADDITIONAL_INFO_FILED)))
        return field.text
