import ssl
# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

import time
import unittest
from infra.browser_wrapper import BrowserWrapper
from logic.work_items_search import WorkItemsSearch
from logic.work_item import WorkItem

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


    def test_found_bug_and_check_std_id(self):
        """
            Searches for a bug by its ID and clicks on the corresponding work item row in Azure DevOps.
        """
        work_items_search = WorkItemsSearch(self.driver)

        # Send the bug ID to the search input
        work_items_search.fill_bug_id_input("275641") # 275641 - True

        # Click on the Bug Row found in the search results
        work_items_search.click_on_searched_bug_row()

        work_item = WorkItem(self.driver)

        is_std_id_empty = work_item.check_std_id_is_empty()
        print(is_std_id_empty)


        time.sleep(5)


if __name__ == '__main__':
    unittest.main()
