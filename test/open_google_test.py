import time
import unittest
from infra.browser_wrapper import BrowserWrapper


class OpenGoogleTest(unittest.TestCase):

    # Before all - Called automatically
    def setUp(self):
        """
        Set up the test environment before each test.

        This method initializes the browser, loads the configuration,
        and navigates to the specified URL.
        """
        self.browser = BrowserWrapper()
        self.driver = self.browser.get_driver("https://www.google.com/")

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.browser.close_browser()

    def test_add_board_to_favorites(self):
        time.sleep(5)


if __name__ == '__main__':
    unittest.main()
