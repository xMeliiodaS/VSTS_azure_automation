import os
import chromedriver_autoinstaller

from selenium import webdriver
from selenium import common as c
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Disable SSL verification via environment variable
os.environ['WDM_SSL_VERIFY'] = '0'


class BrowserWrapper:
    """
    Wrapper class for managing browser interactions using Selenium WebDriver.
    """

    def __init__(self):
        """
        Initialize the BrowserWrapper and load the configuration.
        """
        self._driver = None

    def get_driver(self, url):
        """
        Initialize the WebDriver based on the configuration and navigate to the specified URL.

        :param url: The URL to navigate to.
        :return: The WebDriver instance.
        """
        try:
            options = webdriver.ChromeOptions()

            # options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-blink-features=AutomationControlled")

            # Install once, reuse every time
            driver_path = chromedriver_autoinstaller.install()
            service = Service(driver_path)

            self._driver = webdriver.Chrome(service=service, options=options)
            self._driver.get(url)
            self._driver.maximize_window()
            return self._driver

        except c.WebDriverException as e:
            raise RuntimeError("Failed to obtain a working WebDriver after multiple attempts")

    def close_browser(self):
        """Close the browser and quit the WebDriver."""
        if self._driver:
            try:
                self._driver.quit()
            finally:
                self._driver = None
