import os, ssl, time, unittest

from infra.base_page import BasePage
from infra.config_provider import ConfigProvider
from infra.browser_wrapper import BrowserWrapper
from infra.working_with_exel import get_bug_to_tests_map, validate_and_summarize

from logic.work_item import WorkItem
from logic.base_page_app import BasePageApp
from logic.work_items_search import WorkItemsSearch

from utils.report_automation_results import export_automation_results_html
from utils.std_id_validator import validate_std_id, build_result_record
from utils.additional_info_extract_std_tc_id import extract_tc_ids_from_additional_info


class TestBugSTDValidation(unittest.TestCase):
    def setUp(self):
        """
         Initialize test environment: load config, start browser, fetch bug map and Excel violations.
        """
        ssl._create_default_https_context = ssl._create_unverified_context
        self.config = ConfigProvider.load_config_json()
        self.browser = BrowserWrapper()
        self.driver = self.browser.get_driver(self.config["url"])
        self.bug_map_dict = get_bug_to_tests_map(self.config["excel_path"])

        self.last_reproduced_in_config = self.config["current_version"]
        self.iteration_path_config = self.config["iteration_path"]
        self.std_name_config = self.config.get("std_name", "")

        base_page = BasePage(self.driver)
        base_page.navigate_with_retry(self.config["url"])

        time.sleep(3)

    def tearDown(self):
        """
         Clean up after test: close the browser.
        """
        self.browser.close_browser()

    def test_unique_bugs_std_id(self):
        """
         Validate each bug's STD_ID against expected Test Case IDs and generate HTML report.
         """
        results = []
        work_items_search = WorkItemsSearch(self.driver)
        work_item = WorkItem(self.driver)

        # Check if there are no bugs to process
        if not self.bug_map_dict:
            print("No bugs found in the bug map. Exporting an empty report.")
            export_automation_results_html(results)  # Export an empty report
            return

        # --- NEW: Total bugs for progress
        total_bugs = len(self.bug_map_dict)
        print(f"PROGRESS_TOTAL: {total_bugs}", flush=True)

        try:
            # --- NEW: Iterate with index to emit progress ---
            for index, (bug_id, test_ids) in enumerate(self.bug_map_dict.items(), start=1):
                opened = self.process_single_bug(bug_id, test_ids, work_item, work_items_search, results)

                # --- NEW: Emit live progress to stdout ---
                print(f"PROGRESS: {index}/{total_bugs}", flush=True)

                if opened:
                    BasePageApp(self.driver).close_current_bug_button()

        finally:
            if results:
                # Export automation results HTML (separated)
                export_automation_results_html(results)

                # --- Signal C# that iteration is done ---
                print("PROCESS_FINISHED", flush=True)

    def process_single_bug(self, bug_id, test_ids, work_item, work_items_search, results):
        """
        Process a single bug: search it, fetch STD_ID, validate against expected test IDs, and append result.
        Returns True if a bug details view was opened; otherwise False.
        """
        if not bug_id:
            return False

        comment = ""

        expected_test_ids = [str(tid) for tid in test_ids]

        # Validate the BUG ID (digits only)
        bug_id_str = str(bug_id).strip()
        if not bug_id_str.isdigit():
            comment += f"Invalid bug number: {bug_id_str}. "
            results.append(build_result_record(
                bug_id_str,
                test_ids,
                "---",
                "---",
                comment,
                "---",
                "---",
                "---"
            ))
            return False  # No bug opened

        # Try to open the bug details
        work_items_search.fill_bug_id_input_and_press_enter(bug_id_str)

        std_id_field_val = work_item.get_std_id_value()

        ok, std_comment = validate_std_id(std_id_field_val, expected_test_ids)
        comment += std_comment

        status_str = "✅" if ok else "❌"
        last_reproduced_status, iteration_path_status, std_name_status = self.check_fields(work_item)

        if not ok and self.handle_additional_info_std_id(work_item, expected_test_ids):
            std_id_field_val = ", ".join(expected_test_ids)
            status_str = "✅"
            comment = 'Match'

        results.append(build_result_record(
            bug_id_str,
            test_ids,
            std_id_field_val,
            status_str,
            comment,
            last_reproduced_status,
            iteration_path_status,
            std_name_status
        ))

        return True

    @staticmethod
    def handle_additional_info_std_id(work_item, expected_test_ids):
        """
         Check 'Additional Info' tab for STD_ID fallback; return True if IDs match expected list.
        """
        work_item.click_on_additional_info_tab()
        additional_info_text = work_item.get_additional_info_value()
        tc_id_list = extract_tc_ids_from_additional_info("Feather - Unique Functionality STD", additional_info_text)
        return sorted(tc_id_list) == sorted(expected_test_ids)

    def check_fields(self, work_item):
        """
        Compare the Last_reproduced_in, Iteration_path, and STD Name fields to the config.json file
        """
        last_reproduced_in_text = work_item.get_last_reproduce_in_value()
        iteration_path_text = work_item.get_iteration_path_value()
        std_name_text = work_item.get_std_name_value()

        last_reproduced_status = "✅" if last_reproduced_in_text == self.last_reproduced_in_config else "❌"

        # Base comparison for iteration path
        iteration_path_status = "✅" if iteration_path_text == self.iteration_path_config else "❌"

        # Legacy fallback: replace last segment with "Legacy" if iteration path was not found
        if "/" in self.iteration_path_config:
            parts = self.iteration_path_config.rsplit("/", 1)
            iteration_path_config_legacy = parts[0] + "/Legacy"
            if iteration_path_text == iteration_path_config_legacy:
                iteration_path_status = "✅"

        # Compare STD Name field to config
        std_name_status = "✅" if std_name_text == self.std_name_config else "❌"

        return last_reproduced_status, iteration_path_status, std_name_status


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
