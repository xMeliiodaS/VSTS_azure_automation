import ssl

from selenium.webdriver.common.by import By

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

import time
import unittest
from infra.browser_wrapper import BrowserWrapper


class OpenAzureVSTSTest(unittest.TestCase):

    # Before all - Called automatically
    def setUp(self):
        """
        Set up the test environment before each test.

        This method initializes the browser, loads the configuration,
        and navigates to the specified URL.
        """
        self.browser = BrowserWrapper()
        self.driver = self.browser.get_driver("https://bwiiltiadotfs.eu.jnj.com/tfs/BiosenseCollection/Carto3/_workitems/myactivity/")
        self.driver.find_element(By.ID,'__bolt-textfield-input-1' )

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.browser.close_browser()

    @staticmethod
    def test_wait():
        time.sleep(15)


if __name__ == '__main__':
    unittest.main()
