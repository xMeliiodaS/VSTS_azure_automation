import selenium
from selenium.webdriver.common import by
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from infra.base_page import BasePage
class OpenAzureAstsTest(BasePage):
    # Locators

    def __init__(self, driver):
        """
        Initializes the BoardPage with the provided WebDriver instance.
        :param driver: The WebDriver instance to use for browser interactions.
        """
        super().__init__(driver)

    def click_on_search(self):
        """
        Clicks the search bar.
        """

