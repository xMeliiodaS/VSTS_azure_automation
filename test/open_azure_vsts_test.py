import ssl

from logic.base_page_app import BasePageApp
from logic.work_items_search import WorkItemsSearch

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

import unittest
from infra.browser_wrapper import BrowserWrapper
from infra.working_with_exel import get_bug_to_tests_map
from infra.config_provider import ConfigProvider
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
        self.config = ConfigProvider.load_config_json()

        self.driver = self.browser.get_driver(self.config["url"])

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.browser.close_browser()

    def test_unique_bugs_std_id(self):
        bug_map_dict = get_bug_to_tests_map("../infra/Escort - CARTOSOUND 4D - Clinical WF.xlsx")
        updated_work_items_search = WorkItemsSearch(self.driver)

        work_item = WorkItem(self.driver)

        for bug_id, test_ids in bug_map_dict.items():
            print(f"\n🔍 Checking Bug {bug_id}, linked to Test IDs: {test_ids}")

            # Search for the bug ID in Azure VSTS
            updated_work_items_search.fill_bug_id_input_and_press_enter(bug_id)

            # Check if the STD ID field is empty or matches any related Test ID
            std_id_empty = work_item.check_std_id_is_empty()
            field_val = work_item.get_std_id_value()

            print(f"STD ID Value: {field_val}")

            expected_test_ids = [str(tid) for tid in test_ids]
            field_val_str = str(field_val)

            matches = [tid for tid in expected_test_ids if tid in field_val_str]
            ok = std_id_empty or bool(matches)
            self.assertTrue(ok,
                            f"Bug {bug_id}: STD ID field invalid! Value: '{field_val}' | Expected: empty or contains one of {test_ids}")

            base_page_app = BasePageApp(self.driver)
            base_page_app.close_current_bug_button()


if __name__ == '__main__':
    unittest.main()
