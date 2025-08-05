import ssl
import time

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

import unittest
from utils.html_reporter import export_html_report

from logic.work_item import WorkItem
from logic.base_page_app import BasePageApp
from logic.std_id_validator import validate_std_id, build_result_record
from logic.work_items_search import WorkItemsSearch

from infra.config_provider import ConfigProvider
from infra.browser_wrapper import BrowserWrapper
from infra.working_with_exel import get_bug_to_tests_map


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
        results = []

        bug_map_dict = get_bug_to_tests_map("../infra/Escort - CARTOSOUND 4D - Clinical WF.xlsx")
        updated_work_items_search = WorkItemsSearch(self.driver)

        work_item = WorkItem(self.driver)

        for bug_id, test_ids in bug_map_dict.items():
            print(f"\n🔍 Checking Bug {bug_id}, linked to Test IDs: {test_ids}")

            # Search for the bug ID in Azure VSTS
            updated_work_items_search.fill_bug_id_input_and_press_enter(bug_id)

            # Fetch STD_ID field from Azure
            field_val = work_item.get_std_id_value()
            field_val_str = str(field_val) if field_val is not None else ''

            print(f"STD ID Value: {field_val}")

            # Prepare expected Test Case IDs as strings
            expected_test_ids = [str(tid) for tid in test_ids]

            ok, comment = validate_std_id(field_val, expected_test_ids)
            status_str = "✅ Valid" if ok else "❌ Invalid"

            # Save result for table (using result builder)
            results.append(build_result_record(bug_id, test_ids, field_val, status_str, comment))


            # Close current bug view and wait
            base_page_app = BasePageApp(self.driver)
            base_page_app.close_current_bug_button()
            time.sleep(4)  # adjust as needed

        if results:
            export_html_report(results)


if __name__ == '__main__':
    unittest.main()
