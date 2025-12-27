"""
Parallel Item Processor Module

This module provides parallel processing of multiple item URLs using multiprocessing.
Each worker gets its own ChromeDriver instance and processes one item URL independently.
"""

import os
import ssl
import time
import logging
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from infra.base_page import BasePage
from infra.config_provider import ConfigProvider
from logic.work_item import WorkItem
from logic.base_page_app import BasePageApp
from logic.work_items_search import WorkItemsSearch
from utils.std_id_validator import validate_std_id, build_result_record
from utils.additional_info_extract_std_tc_id import extract_tc_ids_from_additional_info
from utils.constants import (
    Timeouts, Status, STDConstants, BrowserOptions
)

# Configure logging for multiprocessing
# Each worker process will use this logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y - %H:%M:%S'
)


@dataclass
class ItemTask:
    """Represents a single item to process."""
    url: str
    bug_id: str
    test_ids: List[int]
    # Optional: if True, navigate directly to URL; if False, use search (default: True)
    use_direct_navigation: bool = True


def create_chrome_driver(base_url: Optional[str] = None) -> webdriver.Chrome:
    """
    Create and configure a Chrome WebDriver instance.
    Each worker process will call this to get its own driver.
    
    :param base_url: Optional base URL to navigate to initially
    :return: Configured Chrome WebDriver instance
    """
    try:
        options = webdriver.ChromeOptions()
        
        for arg in BrowserOptions.ARGUMENTS:
            options.add_argument(arg)
        
        # Install/update ChromeDriver
        driver_path = chromedriver_autoinstaller.install()
        service = Service(driver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        
        # Navigate to base URL if provided
        if base_url:
            driver.get(base_url)
            time.sleep(Timeouts.PAGE_LOAD_SLEEP)
        
        return driver
    
    except Exception as e:
        logging.error(f"Failed to create ChromeDriver: {e}")
        raise RuntimeError(f"Failed to create ChromeDriver: {e}")


def process_single_item(task: ItemTask, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single item URL. This is the worker function that runs in each process.
    
    Each worker:
    1. Creates its own ChromeDriver instance
    2. Navigates to the item URL (or uses search)
    3. Performs the automation flow
    4. Returns results
    5. Cleans up the driver
    
    :param task: ItemTask containing URL, bug_id, and test_ids
    :param config: Configuration dictionary with validation settings
    :return: Result dictionary matching the format of build_result_record
    """
    driver = None
    try:
        # Setup SSL context (if needed)
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Get config values
        base_url = config.get("url", "")
        last_reproduced_in_config = config.get("current_version", "")
        iteration_path_config = config.get("iteration_path", "")
        std_name_config = config.get("std_name", "")
        
        # Create driver and navigate to base URL first (for authentication/context)
        driver = create_chrome_driver(base_url)
        base_page = BasePage(driver)
        
        # Navigate to base URL if not already there
        if base_url and driver.current_url != base_url:
            base_page.navigate_with_retry(base_url)
            time.sleep(Timeouts.PAGE_LOAD_SLEEP)
        
        # Initialize page objects
        work_items_search = WorkItemsSearch(driver)
        work_item = WorkItem(driver)
        
        # Prepare result variables
        bug_id_str = str(task.bug_id).strip()
        expected_test_ids = [str(tid) for tid in task.test_ids]
        comment = ""
        
        # Validate bug ID format
        if not bug_id_str.isdigit():
            comment += f"Invalid bug number: {bug_id_str}. "
            return build_result_record(
                bug_id_str,
                task.test_ids,
                Status.PLACEHOLDER,
                Status.PLACEHOLDER,
                comment,
                Status.PLACEHOLDER,
                Status.PLACEHOLDER,
                Status.PLACEHOLDER
            )
        
        # Navigate to the item page
        if task.use_direct_navigation:
            # Direct URL navigation approach
            try:
                base_page.navigate_with_retry(task.url)
                time.sleep(Timeouts.PAGE_LOAD_SLEEP)
            except Exception as e:
                logging.warning(f"Direct navigation to {task.url} failed: {e}. Falling back to search.")
                # Fallback to search if direct navigation fails
                work_items_search.fill_bug_id_input_and_press_enter(bug_id_str)
        else:
            # Search-based approach (original method)
            work_items_search.fill_bug_id_input_and_press_enter(bug_id_str)
        
        # Get STD ID value
        try:
            std_id_field_val = work_item.get_std_id_value()
        except Exception as e:
            logging.error(f"Failed to get STD ID for bug {bug_id_str}: {e}")
            std_id_field_val = ""
            comment += f"Failed to read STD ID field: {str(e)}. "
        
        # Validate STD ID
        ok, std_comment = validate_std_id(std_id_field_val, expected_test_ids)
        comment += std_comment
        
        status_str = Status.SUCCESS if ok else Status.FAILURE
        
        # Check other fields
        try:
            last_reproduced_status, iteration_path_status, std_name_status = check_fields(
                work_item, last_reproduced_in_config, iteration_path_config, std_name_config
            )
        except Exception as e:
            logging.error(f"Failed to check fields for bug {bug_id_str}: {e}")
            last_reproduced_status = Status.FAILURE
            iteration_path_status = Status.FAILURE
            std_name_status = Status.FAILURE
            comment += f"Field validation error: {str(e)}. "
        
        # Check Additional Info tab as fallback if STD ID validation failed
        if not ok:
            try:
                if handle_additional_info_std_id(work_item, expected_test_ids):
                    std_id_field_val = ", ".join(expected_test_ids)
                    status_str = Status.SUCCESS
                    comment = Status.MATCH
            except Exception as e:
                logging.warning(f"Additional info check failed for bug {bug_id_str}: {e}")
        
        # Build and return result
        result = build_result_record(
            bug_id_str,
            task.test_ids,
            std_id_field_val,
            status_str,
            comment,
            last_reproduced_status,
            iteration_path_status,
            std_name_status
        )
        
        return result
    
    except Exception as e:
        # Handle any unexpected errors
        logging.error(f"Error processing item {task.bug_id} ({task.url}): {e}")
        return build_result_record(
            str(task.bug_id),
            task.test_ids,
            Status.PLACEHOLDER,
            Status.FAILURE,
            f"Processing error: {str(e)}",
            Status.PLACEHOLDER,
            Status.PLACEHOLDER,
            Status.PLACEHOLDER
        )
    
    finally:
        # Always clean up the driver
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.warning(f"Error closing driver for bug {task.bug_id}: {e}")


def check_fields(
    work_item: WorkItem,
    last_reproduced_in_config: str,
    iteration_path_config: str,
    std_name_config: str
) -> Tuple[str, str, str]:
    """
    Compare the Last_reproduced_in, Iteration_path, and STD Name fields to config values.
    This is extracted from the original TestBugSTDValidation.check_fields method.
    """
    try:
        last_reproduced_in_text = work_item.get_last_reproduce_in_value()
        iteration_path_text = work_item.get_iteration_path_value()
        std_name_text = work_item.get_std_name_value()
    except Exception as e:
        logging.error(f"Failed to get field values: {e}")
        return Status.FAILURE, Status.FAILURE, Status.FAILURE
    
    last_reproduced_status = Status.SUCCESS if last_reproduced_in_text == last_reproduced_in_config else Status.FAILURE
    
    # Base comparison for iteration path
    iteration_path_status = Status.SUCCESS if iteration_path_text == iteration_path_config else Status.FAILURE
    
    # Legacy fallback: replace last segment with "Legacy" if iteration path was not found
    if iteration_path_status == Status.FAILURE and "/" in iteration_path_config:
        parts = iteration_path_config.rsplit("/", 1)
        iteration_path_config_legacy = parts[0] + "/Legacy"
        if iteration_path_text == iteration_path_config_legacy:
            iteration_path_status = Status.SUCCESS
    
    # Compare STD Name field to config
    std_name_status = Status.SUCCESS if std_name_text == std_name_config else Status.FAILURE
    
    return last_reproduced_status, iteration_path_status, std_name_status


def handle_additional_info_std_id(work_item: WorkItem, expected_test_ids: List[str]) -> bool:
    """
    Check 'Additional Info' tab for STD_ID fallback; return True if IDs match expected list.
    This is extracted from the original TestBugSTDValidation.handle_additional_info_std_id method.
    """
    try:
        work_item.click_on_additional_info_tab()
        additional_info_text = work_item.get_additional_info_value()
        tc_id_list = extract_tc_ids_from_additional_info(STDConstants.DEFAULT_STD_NAME, additional_info_text)
        return sorted(tc_id_list) == sorted(expected_test_ids)
    except Exception as e:
        logging.warning(f"Additional info check failed: {e}")
        return False


def process_items_parallel(
    item_tasks: List[ItemTask],
    config: Dict[str, Any],
    num_workers: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Process multiple item URLs in parallel using multiprocessing.
    
    :param item_tasks: List of ItemTask objects to process
    :param config: Configuration dictionary
    :param num_workers: Number of parallel workers (defaults to CPU count)
    :return: List of result dictionaries
    """
    if not item_tasks:
        return []
    
    # Determine number of workers
    if num_workers is None:
        num_workers = cpu_count()
    
    # Limit workers to number of tasks to avoid unnecessary overhead
    num_workers = min(num_workers, len(item_tasks))
    
    print(f"Processing {len(item_tasks)} items with {num_workers} parallel workers")
    logging.info(f"Processing {len(item_tasks)} items with {num_workers} parallel workers")
    
    # Prepare arguments for worker function
    # We need to pass both task and config to each worker
    worker_args = [(task, config) for task in item_tasks]
    
    # Process items in parallel
    # Note: On Windows, multiprocessing uses 'spawn' by default which is what we want
    with Pool(processes=num_workers) as pool:
        results = pool.starmap(process_single_item, worker_args)
    
    print(f"Completed processing {len(results)} items")
    logging.info(f"Completed processing {len(results)} items")
    return results


def build_item_url(base_url: str, bug_id: str) -> str:
    """
    Construct the direct URL for a work item/bug from the base URL and bug ID.
    
    Azure DevOps URL patterns:
    - https://{org}.visualstudio.com/{project}/_workitems/edit/{id}
    - https://dev.azure.com/{org}/{project}/_workitems/edit/{id}
    
    :param base_url: Base URL (could be search page or project page)
    :param bug_id: Bug/work item ID
    :return: Direct URL to the work item
    """
    base_url = base_url.rstrip('/')
    bug_id = str(bug_id).strip()
    
    # If base_url already contains /_workitems/, construct edit URL
    if '/_workitems' in base_url:
        # Replace /_workitems/query or /_workitems with /_workitems/edit
        if '/_workitems/edit/' in base_url:
            # Already has edit, just replace the ID
            parts = base_url.rsplit('/', 1)
            return f"{parts[0]}/{bug_id}"
        elif '/_workitems/query' in base_url or '/_workitems' in base_url:
            return base_url.split('/_workitems')[0] + f'/_workitems/edit/{bug_id}'
    
    # Otherwise, try to append /_workitems/edit/{id}
    # This handles cases where base_url is the project root
    if base_url.endswith('.visualstudio.com') or 'dev.azure.com' in base_url:
        if '/_workitems/edit/' not in base_url:
            # Extract org and project from base_url if possible
            return f"{base_url}/_workitems/edit/{bug_id}"
    
    # Fallback: append /_workitems/edit/{id}
    return f"{base_url}/_workitems/edit/{bug_id}"


def create_item_tasks_from_urls(
    item_urls: List[str],
    bug_ids: Optional[List[str]] = None,
    test_ids_map: Optional[Dict[str, List[int]]] = None,
    use_direct_navigation: bool = True
) -> List[ItemTask]:
    """
    Create ItemTask objects from a list of URLs or bug IDs.
    
    :param item_urls: List of item URLs to process, OR list with one base URL
    :param bug_ids: Optional list of bug IDs (if provided and only one URL, URLs will be constructed)
    :param test_ids_map: Optional dictionary mapping bug_id -> list of test_ids (required for validation)
    :param use_direct_navigation: Whether to navigate directly to URLs or use search
    :return: List of ItemTask objects
    """
    tasks = []
    
    # If bug_ids provided and only one URL (base URL), construct URLs for each bug
    if bug_ids and len(item_urls) == 1:
        base_url = item_urls[0]
        for bug_id in bug_ids:
            item_url = build_item_url(base_url, bug_id)
            test_ids = test_ids_map.get(bug_id, []) if test_ids_map else []
            tasks.append(ItemTask(
                url=item_url,
                bug_id=bug_id,
                test_ids=test_ids,
                use_direct_navigation=use_direct_navigation
            ))
        return tasks
    
    # Otherwise, process as provided URLs
    for i, url in enumerate(item_urls):
        # Extract bug ID from URL if not provided
        if bug_ids and i < len(bug_ids):
            bug_id = bug_ids[i]
        else:
            # Try to extract bug ID from URL (assumes format like .../item/123456 or .../123456)
            import re
            match = re.search(r'/(\d+)/?$', url.rstrip('/'))
            if match:
                bug_id = match.group(1)
            else:
                # Fallback: use index or extract any number from URL
                numbers = re.findall(r'\d+', url)
                bug_id = numbers[-1] if numbers else str(i)
        
        # Get test IDs for this bug
        test_ids = test_ids_map.get(bug_id, []) if test_ids_map else []
        
        tasks.append(ItemTask(
            url=url,
            bug_id=bug_id,
            test_ids=test_ids,
            use_direct_navigation=use_direct_navigation
        ))
    
    return tasks

