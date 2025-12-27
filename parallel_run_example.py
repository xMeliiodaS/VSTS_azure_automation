"""
Production-ready example script for parallel item processing.

This script demonstrates how to use the parallel_item_processor module
to process multiple item URLs simultaneously with configurable workers.

Usage:
    python parallel_run_example.py

Or with custom configuration:
    python parallel_run_example.py --workers 4 --urls "url1,url2,url3"
"""

import os
import sys
import argparse
from typing import List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infra.config_provider import ConfigProvider
from infra.working_with_exel import get_bug_to_tests_map
from logic.parallel_item_processor import (
    process_items_parallel,
    create_item_tasks_from_urls,
    ItemTask
)
from utils.report_automation_results import export_automation_results_html
from utils.constants import APP_DATA_FOLDER_NAME, CONFIG_FILE_NAME, ProgressMessages


def main():
    """Main entry point for parallel item processing."""
    parser = argparse.ArgumentParser(
        description="Process multiple item URLs in parallel using multiprocessing"
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (defaults to CPU count)'
    )
    parser.add_argument(
        '--urls',
        type=str,
        default=None,
        help='Comma-separated list of item URLs to process'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config.json file (defaults to AppData location)'
    )
    parser.add_argument(
        '--excel',
        type=str,
        default=None,
        help='Path to Excel file for bug-to-test mapping'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = ConfigProvider.load_config_json(args.config)
    
    # Determine item URLs
    item_urls = []
    if args.urls:
        # Use provided URLs
        item_urls = [url.strip() for url in args.urls.split(',') if url.strip()]
    elif config.get("item_urls"):
        # Use URLs from config
        item_urls = config.get("item_urls", [])
    else:
        # Fallback: try to construct URLs from bug map (if Excel is available)
        excel_path = args.excel or config.get("excel_path")
        if excel_path:
            try:
                bug_map = get_bug_to_tests_map(excel_path)
                base_url = config.get("url", "").rstrip('/')
                if base_url:
                    # Construct item URLs (adjust this pattern based on your URL structure)
                    # Example: if base_url is "https://example.com/_workitems", 
                    # item URLs might be "https://example.com/_workitems/edit/123456"
                    item_base = base_url.replace('/_workitems', '/_workitems/edit')
                    if not item_base.endswith('/'):
                        item_base += '/'
                    item_urls = [f"{item_base}{bug_id}" for bug_id in bug_map.keys()]
                    print(f"Constructed {len(item_urls)} URLs from bug map")
            except Exception as e:
                print(f"Error constructing URLs from Excel: {e}")
                sys.exit(1)
        else:
            print("Error: No URLs provided and no Excel file available.")
            print("Please provide URLs using --urls or configure excel_path in config.json")
            sys.exit(1)
    
    if not item_urls:
        print("No item URLs to process.")
        sys.exit(0)
    
    # Load bug-to-test mapping from Excel if available
    test_ids_map = {}
    excel_path = args.excel or config.get("excel_path")
    if excel_path:
        try:
            test_ids_map = get_bug_to_tests_map(excel_path)
            print(f"Loaded bug-to-test mapping for {len(test_ids_map)} bugs")
        except Exception as e:
            print(f"Warning: Could not load Excel mapping: {e}")
    
    # Create item tasks from URLs
    item_tasks = create_item_tasks_from_urls(
        item_urls=item_urls,
        test_ids_map=test_ids_map,
        use_direct_navigation=True  # Set to False to use search-based navigation
    )
    
    if not item_tasks:
        print("No items to process.")
        sys.exit(0)
    
    # Print progress info
    print(f"{ProgressMessages.PROGRESS_TOTAL_PREFIX} {len(item_tasks)}")
    
    # Process items in parallel
    try:
        results = process_items_parallel(
            item_tasks=item_tasks,
            config=config,
            num_workers=args.workers
        )
        
        # Export results to HTML report
        if results:
            export_automation_results_html(results)
            print(f"Results exported to HTML report")
        
        print(ProgressMessages.PROCESS_FINISHED, flush=True)
        
        # Print summary
        success_count = sum(1 for r in results if r.get("Test Case ID Status") == "✅")
        failure_count = len(results) - success_count
        print(f"\nSummary: {success_count} succeeded, {failure_count} failed out of {len(results)} total")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during parallel processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

