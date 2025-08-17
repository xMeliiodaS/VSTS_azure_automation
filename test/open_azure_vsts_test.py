import ssl
import unittest

from infra.config_provider import ConfigProvider
from infra.browser_wrapper import BrowserWrapper
from infra.working_with_exel import get_bug_to_tests_map, validate_and_summarize

from logic.work_item import WorkItem
from logic.base_page_app import BasePageApp
from logic.work_items_search import WorkItemsSearch

from utils.html_reporter import export_html_report, export_std_validation_html
from utils.std_id_validator import validate_std_id, build_result_record
from utils.additional_info_extract_std_tc_id import extract_tc_ids_from_additional_info


class OpenAzureVSTSTest(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before automation.
        """
        ssl._create_default_https_context = ssl._create_unverified_context

        self.browser = BrowserWrapper()
        self.config = ConfigProvider.load_config_json()
        self.driver = self.browser.get_driver(self.config["url"])

        std_excel_path = self.config["excel_path"]
        self.bug_map_dict = get_bug_to_tests_map(std_excel_path)

        violations = validate_and_summarize(std_excel_path)
        export_std_validation_html(violations, report_title="STD Excel Validation Summary")

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.browser.close_browser()

    def test_unique_bugs_std_id(self):
        """
        Validate each bug by checking its STD_ID field, close UI, then output HTML report.
        """
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
        Handles searching and validating in the workflow.
        """
        print(f"\n🔍 Checking Bug {bug_id}, linked to Test IDs: {test_ids} in Excel")

        # Search for the bug ID in Azure VSTS
        work_items_search.fill_bug_id_input_and_press_enter(bug_id)

        # Fetch STD_ID field from Azure
        std_id_field_val = work_item.get_std_id_value()

        # Prepare expected Test Case IDs as strings
        self.expected_test_ids = [str(tid) for tid in test_ids]

        # Validate and build result
        ok, comment = validate_std_id(std_id_field_val, self.expected_test_ids)

        status_str = "✅" if ok else "❌"

        if not ok:
            if self.handle_additional_info_std_id():
                status_str = "✅"

        results.append(build_result_record(bug_id, test_ids, std_id_field_val, status_str, comment))

    def handle_additional_info_std_id(self):
        """
        Handles searching and validating "Additional Info" Tab.
        """
        # Get the STD name
        std_name = self.config["std_name"]

        self.work_item.click_on_additional_info_tab()
        additional_info_text = self.work_item.get_additional_info_value()
        tc_id_list = extract_tc_ids_from_additional_info(std_name, additional_info_text)

        for tc_id in tc_id_list:
            if tc_id == self.expected_test_ids:
                return True  # Found a matching group
        # No match found in any group
        return False


if __name__ == '__main__':
    unittest.main()
