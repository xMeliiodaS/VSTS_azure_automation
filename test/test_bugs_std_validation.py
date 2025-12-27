import os, ssl, time, unittest

from infra.base_page import BasePage
from infra.config_provider import ConfigProvider
from infra.browser_wrapper import BrowserWrapper
from infra.working_with_exel import get_bug_to_tests_map, validate_and_summarize

from logic.work_item import WorkItem
from logic.base_page_app import BasePageApp
from logic.work_items_search import WorkItemsSearch
from logic.parallel_item_processor import ItemTask

from utils.report_automation_results import export_automation_results_html
from utils.std_id_validator import validate_std_id, build_result_record
from utils.additional_info_extract_std_tc_id import extract_tc_ids_from_additional_info
from utils.constants import (
    Timeouts, Status, STDConstants, APP_DATA_FOLDER_NAME, 
    CONFIG_FILE_NAME, ProgressMessages
)


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

        time.sleep(Timeouts.PAGE_LOAD_SLEEP)

    def tearDown(self):
        """
         Clean up after test: close the browser.
        """
        self.browser.close_browser()

    def test_unique_bugs_std_id(self):
        """
         Validate each bug's STD_ID against expected Test Case IDs and generate HTML report.
         Uses parallel processing if configured, otherwise sequential.
        """
        # Check if parallel processing is enabled
        use_parallel = self.config.get("use_parallel_processing", False)
        
        if use_parallel:
            # Use parallel version
            self.test_unique_bugs_std_id_parallel()
            return
        
        # Original sequential version
        results = []
        work_items_search = WorkItemsSearch(self.driver)
        work_item = WorkItem(self.driver)

        # Check if there are no bugs to process
        if not self.bug_map_dict:
            print(ProgressMessages.NO_BUGS_FOUND)
            export_automation_results_html(results)  # Export an empty report
            return

        # --- NEW: Total bugs for progress
        total_bugs = len(self.bug_map_dict)
        print(f"{ProgressMessages.PROGRESS_TOTAL_PREFIX} {total_bugs}", flush=True)

        try:
            # --- NEW: Iterate with index to emit progress ---
            for index, (bug_id, test_ids) in enumerate(self.bug_map_dict.items(), start=1):
                opened = self.process_single_bug(bug_id, test_ids, work_item, work_items_search, results)

                # --- NEW: Emit live progress to stdout ---
                print(f"{ProgressMessages.PROGRESS_PREFIX} {index}/{total_bugs}", flush=True)

                if opened:
                    BasePageApp(self.driver).close_current_bug_button()

        finally:
            if results:
                # Export automation results HTML (separated)
                export_automation_results_html(results)

                # --- Signal C# that iteration is done ---
                print(ProgressMessages.PROCESS_FINISHED, flush=True)

    def test_unique_bugs_std_id_parallel(self):
        """
        Parallel version: Validate each bug's STD_ID using multiprocessing with direct URL navigation.
        Much faster than sequential processing.
        """
        from logic.parallel_item_processor import (
            process_items_parallel,
            build_item_url
        )
        
        # Check if there are no bugs to process
        if not self.bug_map_dict:
            print(ProgressMessages.NO_BUGS_FOUND)
            export_automation_results_html([])
            return
        
        total_bugs = len(self.bug_map_dict)
        print(f"{ProgressMessages.PROGRESS_TOTAL_PREFIX} {total_bugs}", flush=True)
        
        # Build item URLs from bug IDs using base URL
        base_url = self.config["url"]
        item_tasks = []
        for bug_id, test_ids in self.bug_map_dict.items():
            bug_id_str = str(bug_id).strip()
            item_url = build_item_url(base_url, bug_id_str)
            item_tasks.append(ItemTask(
                url=item_url,
                bug_id=bug_id_str,
                test_ids=test_ids,
                use_direct_navigation=True
            ))
        
        # Get number of workers from config, or use default (CPU count)
        num_workers = self.config.get("parallel_workers", None)
        
        # Process in parallel
        results = process_items_parallel(
            item_tasks=item_tasks,
            config=self.config,
            num_workers=num_workers
        )
        
        # Export results
        if results:
            export_automation_results_html(results)
        
        print(ProgressMessages.PROCESS_FINISHED, flush=True)

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
                Status.PLACEHOLDER,
                Status.PLACEHOLDER,
                comment,
                Status.PLACEHOLDER,
                Status.PLACEHOLDER,
                Status.PLACEHOLDER
            ))
            return False  # No bug opened

        # Try to open the bug details
        work_items_search.fill_bug_id_input_and_press_enter(bug_id_str)

        std_id_field_val = work_item.get_std_id_value()

        ok, std_comment = validate_std_id(std_id_field_val, expected_test_ids)
        comment += std_comment

        status_str = Status.SUCCESS if ok else Status.FAILURE
        last_reproduced_status, iteration_path_status, std_name_status = self.check_fields(work_item)

        if not ok and self.handle_additional_info_std_id(work_item, expected_test_ids):
            std_id_field_val = ", ".join(expected_test_ids)
            status_str = Status.SUCCESS
            comment = Status.MATCH

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
        tc_id_list = extract_tc_ids_from_additional_info(STDConstants.DEFAULT_STD_NAME, additional_info_text)
        return sorted(tc_id_list) == sorted(expected_test_ids)

    def check_fields(self, work_item):
        """
        Compare the Last_reproduced_in, Iteration_path, and STD Name fields to the config.json file
        """
        last_reproduced_in_text = work_item.get_last_reproduce_in_value()
        iteration_path_text = work_item.get_iteration_path_value()
        std_name_text = work_item.get_std_name_value()

        last_reproduced_status = Status.SUCCESS if last_reproduced_in_text == self.last_reproduced_in_config else Status.FAILURE

        # Base comparison for iteration path
        iteration_path_status = Status.SUCCESS if iteration_path_text == self.iteration_path_config else Status.FAILURE

        # Legacy fallback: replace last segment with "Legacy" if iteration path was not found
        if "/" in self.iteration_path_config:
            parts = self.iteration_path_config.rsplit("/", 1)
            iteration_path_config_legacy = parts[0] + "/Legacy"
            if iteration_path_text == iteration_path_config_legacy:
                iteration_path_status = Status.SUCCESS

        # Compare STD Name field to config
        std_name_status = Status.SUCCESS if std_name_text == self.std_name_config else Status.FAILURE

        return last_reproduced_status, iteration_path_status, std_name_status


if __name__ == "__main__":
    appdata_folder = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
        APP_DATA_FOLDER_NAME
    )
    config_path = os.path.join(appdata_folder, CONFIG_FILE_NAME)

    config = ConfigProvider.load_config_json(config_path)

    suite = unittest.TestSuite()
    suite.addTest(TestBugSTDValidation('test_unique_bugs_std_id'))
    unittest.TextTestRunner(verbosity=2).run(suite)
