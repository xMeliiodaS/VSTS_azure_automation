import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from logic.base_page_app import BasePageApp
from utils.utils import safe_click, smart_click
from utils.constants import Timeouts, Retries


class WorkItemsSearch(BasePageApp):
    # -----------------Locators Related to Bugs-----------------
    SEARCH_BAR_INPUT = '#l1-search-input'
    SEARCH_ICON_BUTTON = '.search-icon.cursor-pointer'

    BUG_POPUP_INDICATOR = 'ToBeTyped'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def fill_bug_id_input_and_press_enter(self, bug_id: str):
        """
        Clear Search bar and fill the Bug ID then hit Enter.
        Reliable even on slow machines by verifying each step.
        """
        # ensure visible/clickable
        input_el = self.wait_clickable(By.CSS_SELECTOR, self.SEARCH_BAR_INPUT, timeout=Timeouts.SHORT_TIMEOUT)

        safe_click(self._driver, self.SEARCH_BAR_INPUT, retries=Retries.CLICK_RETRIES, wait_time=Timeouts.SHORT_TIMEOUT)

        # clear field robustly
        input_el.send_keys(Keys.CONTROL, "a")
        input_el.send_keys(Keys.DELETE)

        # wait until the field is empty
        WebDriverWait(self._driver, Timeouts.SHORT_TIMEOUT).until(
            lambda d: input_el.get_attribute("value") == ""
        )

        # type the bug id
        input_el.send_keys(str(bug_id))

        # wait until the field contains exactly the bug id
        WebDriverWait(self._driver, Timeouts.SHORT_TIMEOUT).until(
            lambda d: input_el.get_attribute("value") == str(bug_id)
        )

        # now hit Enter
        time.sleep(Timeouts.INPUT_DELAY_SLEEP)

        # force focus, no sleep
        self._driver.execute_script("arguments[0].focus();", input_el)

        # safe_click(self._driver, self.SEARCH_ICON_BUTTON, retries=3, wait_time=10)

        smart_click(
            self._driver,
            self.SEARCH_ICON_BUTTON,
            retries=Retries.CLICK_RETRIES,
            wait_time=Timeouts.SHORT_TIMEOUT,
            post_condition_locator=self.CLOSE_CURRENT_BUG_BUTTON
        )