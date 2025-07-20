import ssl
# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

import time
import unittest
from infra.browser_wrapper import BrowserWrapper
from logic.work_items import WorkItems

class OpenAzureVSTSTest(unittest.TestCase):

    # Before all - Called automatically
    def setUp(self):
        """
        Set up the test environment before each test.

        This method initializes the browser, loads the configuration,
        and navigates to the specified URL.
        """
        self.browser = BrowserWrapper()
        self.driver = self.browser.get_driver(
            "https://bwiiltiadotfs.eu.jnj.com/tfs/BiosenseCollection/Carto3/_workitems/myactivity/")

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.browser.close_browser()


    def test_wait(self):
        a = WorkItems(self.driver)
        a.fill_bug_id_input("TEST")
        time.sleep(5)


if __name__ == '__main__':
    unittest.main()
