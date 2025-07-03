from selenium import webdriver
from infra.config_provider import ConfigProvider
from selenium import common as c
import undetected_chromedriver as uc


class BrowserWrapper:
    """
    Wrapper class for managing browser interactions using Selenium WebDriver.
    """

    def __init__(self):
        """
        Initialize the BrowserWrapper and load the configuration.
        """
        self._driver = None
        self.config = ConfigProvider().load_config_json()

    def get_driver(self, url):
        """
        Initialize the WebDriver based on the configuration and navigate to the specified URL.

        :param url: The URL to navigate to.
        :return: The WebDriver instance.
        """
        try:
            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            if self.config["browser"] == "Chrome":
                self._driver = uc.Chrome(options=options)
            elif self.config["browser"] == "Firefox":
                self._driver = webdriver.Firefox()
            elif self.config["browser"] == "Edge":
                self._driver = webdriver.Edge()
            else:
                print("Browser does not exist")

            self._driver.get(url)
            self._driver.maximize_window()
            return self._driver

        except c.WebDriverException as e:
            print("Could not find web driver:", e)

    def close_browser(self):
        """
        Close the browser and quit the WebDriver.
        """
        self._driver.quit()
