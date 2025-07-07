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

    def get_driver(self, url):
        """
        Initialize the WebDriver based on the configuration and navigate to the specified URL.

        :param url: The URL to navigate to.
        :return: The WebDriver instance.
        """
        try:
            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            self._driver = uc.Chrome(options=options)

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
