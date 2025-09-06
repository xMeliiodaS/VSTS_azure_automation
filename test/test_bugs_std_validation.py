import os, ssl, time, unittest
from infra.config_provider import ConfigProvider
from infra.browser_wrapper import BrowserWrapper
from infra.working_with_exel import get_bug_to_tests_map, validate_and_summarize
from logic.work_item import WorkItem
from logic.base_page_app import BasePageApp
from logic.work_items_search import WorkItemsSearch
from utils.std_id_validator import validate_std_id, build_result_record
from utils.additional_info_extract_std_tc_id import extract_tc_ids_from_additional_info
from utils.report_automation_results import export_automation_results_html  # <-- new import


class TestBugSTDValidation(unittest.TestCase):
    def setUp(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        self.config = ConfigProvider.load_config_json()
        self.browser = BrowserWrapper()
        self.driver = self.browser.get_driver(self.config["url"])
        self.bug_map_dict = get_bug_to_tests_map(self.config["excel_path"])

        # Keep violations loaded for reporting consistency
        self.violations = validate_and_summarize(self.config["excel_path"])
        time.sleep(3)

    def tearDown(self):
        self.browser.close_browser()

    def test_unique_bugs_std_id(self):
        """Validate each bug's STD_ID against expected Test Case IDs and generate HTML report."""
        results = []
        work_items_search = WorkItemsSearch(self.driver)
        work_item = WorkItem(self.driver)

        try:
            for bug_id, test_ids in self.bug_map_dict.items():
                self.process_single_bug(bug_id, test_ids, work_item, work_items_search, results)
                BasePageApp(self.driver).close_current_bug_button()
        finally:
            if results:
                # Export automation results HTML (separated)
                export_automation_results_html(results)

    def process_single_bug(self, bug_id, test_ids, work_item, work_items_search, results):
        if not bug_id:
            return
        work_items_search.fill_bug_id_input_and_press_enter(bug_id)
        std_id_field_val = work_item.get_std_id_value()

        expected_test_ids = [str(tid) for tid in test_ids]
        ok, comment = validate_std_id(std_id_field_val, expected_test_ids)
        status_str = "✅" if ok else "❌"

        if not ok and self.handle_additional_info_std_id(work_item, expected_test_ids):
            std_id_field_val = ", ".join(expected_test_ids)
            status_str = "✅"

        print(f"\n🔍 Checked Bug {bug_id}, linked to Test IDs: {test_ids} in Excel")
        results.append(build_result_record(bug_id, test_ids, std_id_field_val, status_str, comment))

    def handle_additional_info_std_id(self, work_item, expected_test_ids):
        work_item.click_on_additional_info_tab()
        additional_info_text = work_item.get_additional_info_value()
        tc_id_list = extract_tc_ids_from_additional_info("Feather - Unique Functionality STD", additional_info_text)
        return sorted(tc_id_list) == sorted(expected_test_ids)


if __name__ == "__main__":
    appdata_folder = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
        'AT_baseline_verifier'
    )
    config_path = os.path.join(appdata_folder, 'config.json')

    config = ConfigProvider.load_config_json(config_path)

    suite = unittest.TestSuite()
    suite.addTest(TestBugSTDValidation('test_unique_bugs_std_id'))
    unittest.TextTestRunner(verbosity=2).run(suite)
