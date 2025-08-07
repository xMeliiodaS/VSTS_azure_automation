# File: test/open_azure_vsts_test.py

import ssl
import unittest

from infra.config_provider import ConfigProvider
from infra.browser_wrapper import BrowserWrapper
from infra.working_with_exel import get_bug_to_tests_map

from logic.work_item import WorkItem
from logic.base_page_app import BasePageApp
from logic.work_items_search import WorkItemsSearch

from utils.html_reporter import export_html_report
from utils.std_id_validator import validate_std_id, build_result_record


class OpenAzureVSTSTest(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test.
        """
        ssl._create_default_https_context = ssl._create_unverified_context

        self.browser = BrowserWrapper()
        self.config = ConfigProvider.load_config_json()
        self.driver = self.browser.get_driver(self.config["url"])
        self.bug_map_dict = get_bug_to_tests_map("../infra/Book1.xlsx")

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.browser.close_browser()

    def test_unique_bugs_std_id(self):
        results = []
        work_items_search = WorkItemsSearch(self.driver)
        self.work_item = WorkItem(self.driver)

        for bug_id, test_ids in self.bug_map_dict.items():
            self.process_single_bug(bug_id, test_ids, self.work_item, work_items_search, results)

            # Close current bug view
            base_page_app = BasePageApp(self.driver)
            base_page_app.close_current_bug_button()

        if results:
            export_html_report(results)

    def process_single_bug(self, bug_id, test_ids, work_item, work_items_search, results):
        """
        Handles searching, validating, saving results, and closing a bug in the workflow.
        """
        print(f"\n🔍 Checking Bug {bug_id}, linked to Test IDs: {test_ids} in Excel")

        # Search for the bug ID in Azure VSTS
        work_items_search.fill_bug_id_input_and_press_enter(bug_id)

        # Fetch STD_ID field from Azure
        std_id_field_val = work_item.get_std_id_value()

        # Prepare expected Test Case IDs as strings
        expected_test_ids = [str(tid) for tid in test_ids]

        # Validate and build result
        ok, comment = validate_std_id(std_id_field_val, expected_test_ids)

        status_str = "✅" if ok else "❌"

        # Handling Additional info if
        self.handle_additional_info_std_id()

        results.append(build_result_record(bug_id, test_ids, std_id_field_val, status_str, comment))

    def handle_additional_info_std_id(self):
        """
        Handles searching, validating, saving results, and closing a bug in the "Additional Info" Tab.
        """
        self.work_item.click_on_additional_info_tab()
        a = self.work_item.get_additional_info_value()
        print(a)


if __name__ == '__main__':
    unittest.main()
