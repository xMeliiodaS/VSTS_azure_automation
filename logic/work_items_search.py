from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from infra.base_page import BasePage


class WorkItemsSearch(BasePage):
    # -----------------Locators Related to Bugs-----------------
    SEARCH_BAR_INPUT = '#__bolt-textfield-input-1'
    BUG_OBJECT = 'a.work-item-title-link'

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def fill_bug_id_input(self, bug_id):
        """
        Clear Search bar and fills the Bug ID on the Search Bar.
        """
        search_bar = WebDriverWait(self._driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.SEARCH_BAR_INPUT)))

        search_bar.click()
        search_bar.send_keys(Keys.CONTROL + "a")
        search_bar.send_keys(Keys.DELETE)

        search_bar.send_keys(bug_id)

    def click_on_searched_bug_row(self):
        """
        Clicks on the bug (work item) row in the search results after searching by bug ID.
        """
        WebDriverWait(self._driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.BUG_OBJECT))).click()


