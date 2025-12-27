"""
Example script demonstrating parallel processing of multiple item URLs.

This script shows how to use the parallel_item_processor module to process
multiple item URLs simultaneously using multiprocessing.
"""

import os
import sys
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infra.config_provider import ConfigProvider
from infra.working_with_exel import get_bug_to_tests_map
from logic.parallel_item_processor import (
    process_items_parallel,
    create_item_tasks_from_urls,
    ItemTask
)
from utils.report_automation_results import export_automation_results_html
from utils.constants import APP_DATA_FOLDER_NAME, CONFIG_FILE_NAME, ProgressMessages


def process_items_from_urls(
    item_urls: List[str],
    config_path: str = None,
    num_workers: int = None,
    excel_path: str = None
) -> List[Dict[str, Any]]:
    """
    Process multiple item URLs in parallel.
    
    :param item_urls: List of item URLs to process (e.g., ['https://example.com/item/123456', ...])
    :param config_path: Optional path to config.json file
    :param num_workers: Number of parallel workers (defaults to CPU count)
    :param excel_path: Optional path to Excel file to get bug-to-test mapping
    :return: List of result dictionaries
    """
    # Load configuration
    config = ConfigProvider.load_config_json(config_path)
    
    # Load bug-to-test mapping from Excel if provided
    test_ids_map = {}
    if excel_path:
        try:
            test_ids_map = get_bug_to_tests_map(excel_path)
        except Exception as e:
            print(f"Warning: Could not load Excel mapping: {e}")
    
    # If no Excel path provided, try to get it from config
    if not test_ids_map and config.get("excel_path"):
        try:
            test_ids_map = get_bug_to_tests_map(config["excel_path"])
        except Exception as e:
            print(f"Warning: Could not load Excel mapping from config: {e}")
    
    # Create item tasks from URLs
    # Extract bug IDs from URLs and map them to test IDs
    item_tasks = create_item_tasks_from_urls(
        item_urls=item_urls,
        test_ids_map=test_ids_map,
        use_direct_navigation=True  # Set to False if you prefer search-based navigation
    )
    
    if not item_tasks:
        print("No items to process.")
        return []
    
    # Print progress info
    print(f"{ProgressMessages.PROGRESS_TOTAL_PREFIX} {len(item_tasks)}")
    
    # Process items in parallel
    results = process_items_parallel(
        item_tasks=item_tasks,
        config=config,
        num_workers=num_workers
    )
    
    # Export results to HTML report
    if results:
        export_automation_results_html(results)
    
    print(ProgressMessages.PROCESS_FINISHED, flush=True)
    
    return results


def process_items_from_bug_map(
    bug_map: Dict[str, List[int]],
    base_url: str,
    config_path: str = None,
    num_workers: int = None
) -> List[Dict[str, Any]]:
    """
    Process items using a bug-to-test mapping dictionary.
    Constructs URLs from bug IDs and processes them in parallel.
    
    :param bug_map: Dictionary mapping bug_id -> list of test_ids
                     (e.g., {'123456': [1, 2, 3], '234567': [4, 5]})
    :param base_url: Base URL pattern (e.g., 'https://example.com/item/{bug_id}')
                    or just 'https://example.com/item/' (bug_id will be appended)
    :param config_path: Optional path to config.json file
    :param num_workers: Number of parallel workers (defaults to CPU count)
    :return: List of result dictionaries
    """
    # Build URLs from bug IDs
    item_urls = []
    for bug_id in bug_map.keys():
        if base_url.endswith('/'):
            url = f"{base_url}{bug_id}"
        elif '{' in base_url:
            url = base_url.format(bug_id=bug_id)
        else:
            url = f"{base_url}/{bug_id}"
        item_urls.append(url)
    
    # Create item tasks
    item_tasks = [
        ItemTask(
            url=url,
            bug_id=bug_id,
            test_ids=bug_map[bug_id],
            use_direct_navigation=True
        )
        for url, bug_id in zip(item_urls, bug_map.keys())
    ]
    
    # Load configuration
    config = ConfigProvider.load_config_json(config_path)
    
    if not item_tasks:
        print("No items to process.")
        return []
    
    # Print progress info
    print(f"{ProgressMessages.PROGRESS_TOTAL_PREFIX} {len(item_tasks)}")
    
    # Process items in parallel
    results = process_items_parallel(
        item_tasks=item_tasks,
        config=config,
        num_workers=num_workers
    )
    
    # Export results to HTML report
    if results:
        export_automation_results_html(results)
    
    print(ProgressMessages.PROCESS_FINISHED, flush=True)
    
    return results


def main():
    """
    Main function demonstrating different usage patterns.
    """
    # Example 1: Process items from a list of URLs
    item_urls = [
        "https://example.com/item/123456",
        "https://example.com/item/234567",
        "https://example.com/item/345678",
    ]
    
    # Load config
    appdata_folder = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
        APP_DATA_FOLDER_NAME
    )
    config_path = os.path.join(appdata_folder, CONFIG_FILE_NAME)
    
    # Option 1: Process from URLs directly
    # results = process_items_from_urls(
    #     item_urls=item_urls,
    #     config_path=config_path,
    #     num_workers=4  # Use 4 parallel workers
    # )
    
    # Option 2: Process from bug map (like the original code)
    config = ConfigProvider.load_config_json(config_path)
    if config.get("excel_path"):
        bug_map = get_bug_to_tests_map(config["excel_path"])
        base_url = config.get("url", "").rstrip('/')
        
        # If base_url is a search page, construct item URLs
        # You may need to adjust this based on your URL pattern
        if base_url:
            # Construct item URLs (adjust pattern as needed)
            item_base = base_url.replace('/_workitems', '/_workitems/edit')
            item_base = item_base.split('/_workitems')[0] + '/_workitems/edit'
            
            results = process_items_from_bug_map(
                bug_map=bug_map,
                base_url=f"{item_base}/",
                config_path=config_path,
                num_workers=4
            )
        else:
            print("No base URL configured. Please update config.json with the correct URL pattern.")
    else:
        print("No Excel path configured. Please update config.json with excel_path.")


if __name__ == "__main__":
    main()

