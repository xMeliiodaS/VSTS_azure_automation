# Parallel Item Processing Guide

This guide explains how to use the parallel item processor to process multiple item URLs simultaneously using multiprocessing.

## Overview

The `parallel_item_processor` module provides true parallel execution using Python's `multiprocessing` library. Each worker process gets its own ChromeDriver instance and processes one item URL independently.

### Key Features

- ✅ True parallel execution using multiprocessing (not threading)
- ✅ One ChromeDriver per worker process
- ✅ Configurable number of parallel workers
- ✅ Isolated failures (one item failing doesn't stop others)
- ✅ Clean driver startup and shutdown
- ✅ Production-ready and maintainable code

## Integration with test_bugs_std_validation.py

The parallel processing is now **fully integrated** into your existing test file! You can enable it via configuration.

### Enable Parallel Processing

Add these options to your `config.json`:

```json
{
  "url": "https://yourorg.visualstudio.com/YourProject/_workitems",
  "excel_path": "path/to/excel.xlsx",
  "current_version": "...",
  "iteration_path": "...",
  "std_name": "...",
  
  // New options for parallel processing:
  "use_parallel_processing": true,     // Set to true to use parallel, false for sequential
  "parallel_workers": 4                // Optional: number of workers (defaults to CPU count)
}
```

### Running the Test

Just run your test as before:

```bash
python test/test_bugs_std_validation.py
```

The test will automatically use parallel processing if `use_parallel_processing: true` is set in your config.

### How It Works

- **Sequential mode** (`use_parallel_processing: false`): Uses the original code, one bug at a time
- **Parallel mode** (`use_parallel_processing: true`): Uses multiprocessing with direct URL navigation, much faster!

The parallel version:
1. Constructs direct URLs for each bug (e.g., `.../_workitems/edit/123456`)
2. Spawns multiple worker processes (one ChromeDriver per worker)
3. Each worker processes bugs independently
4. Results are collected and exported the same way

## Quick Start

### Basic Usage (Standalone)

```python
from logic.parallel_item_processor import (
    process_items_parallel,
    create_item_tasks_from_urls,
    ItemTask
)
from infra.config_provider import ConfigProvider

# Load configuration
config = ConfigProvider.load_config_json()

# Define item URLs to process
item_urls = [
    "https://example.com/item/123456",
    "https://example.com/item/234567",
    "https://example.com/item/345678",
]

# Create item tasks (with bug-to-test mapping if available)
item_tasks = create_item_tasks_from_urls(
    item_urls=item_urls,
    test_ids_map={},  # Optional: map bug_id -> list of test_ids
    use_direct_navigation=True
)

# Process items in parallel with 4 workers
results = process_items_parallel(
    item_tasks=item_tasks,
    config=config,
    num_workers=4  # Optional: defaults to CPU count
)
```

### Using the Example Script

```bash
# Process URLs from command line
python parallel_run_example.py --workers 4 --urls "https://example.com/item/123456,https://example.com/item/234567"

# Or let it read from config.json
python parallel_run_example.py --workers 4
```

## Architecture

### Worker Function

Each worker process runs `process_single_item()` which:

1. Creates its own ChromeDriver instance
2. Navigates to the base URL (for authentication/context)
3. Navigates to the item URL (or uses search if direct navigation fails)
4. Performs the automation flow:
   - Extracts STD ID
   - Validates against expected test IDs
   - Checks other fields (Last Reproduced In, Iteration Path, STD Name)
   - Checks Additional Info tab as fallback
5. Returns a result dictionary
6. Cleans up the driver

### Data Flow

```
Main Process
    ├── Creates ItemTask objects (URL + bug_id + test_ids)
    ├── Spawns worker processes (multiprocessing.Pool)
    │   ├── Worker 1: process_single_item(task1, config) -> result1
    │   ├── Worker 2: process_single_item(task2, config) -> result2
    │   ├── Worker 3: process_single_item(task3, config) -> result3
    │   └── ...
    └── Collects all results -> List[Dict]
```

## Configuration

### Number of Workers

The number of parallel workers can be configured:

- **Default**: Number of CPU cores (`cpu_count()`)
- **Manual**: Pass `num_workers` parameter
- **Automatic limit**: Workers are limited to the number of items to process

```python
# Use default (CPU count)
results = process_items_parallel(item_tasks, config)

# Use 4 workers
results = process_items_parallel(item_tasks, config, num_workers=4)

# Use 8 workers
results = process_items_parallel(item_tasks, config, num_workers=8)
```

### Navigation Mode

You can choose between direct URL navigation or search-based navigation:

```python
# Direct navigation (default) - navigates directly to item URL
item_tasks = create_item_tasks_from_urls(
    item_urls=urls,
    use_direct_navigation=True
)

# Search-based navigation - uses the search interface (original method)
item_tasks = create_item_tasks_from_urls(
    item_urls=urls,
    use_direct_navigation=False
)
```

## ItemTask Structure

Each `ItemTask` contains:

```python
@dataclass
class ItemTask:
    url: str                          # Item URL to process
    bug_id: str                       # Bug/item ID
    test_ids: List[int]               # Expected test case IDs for validation
    use_direct_navigation: bool = True  # Navigation method
```

## Integration with Existing Code

### From Bug Map (Excel-based)

If you have a bug-to-test mapping from Excel:

```python
from infra.working_with_exel import get_bug_to_tests_map
from logic.parallel_item_processor import ItemTask, process_items_parallel

# Load bug map from Excel
bug_map = get_bug_to_tests_map("path/to/excel.xlsx")
# bug_map = {"123456": [1, 2, 3], "234567": [4, 5]}

# Construct item URLs
base_url = "https://example.com/item"
item_tasks = [
    ItemTask(
        url=f"{base_url}/{bug_id}",
        bug_id=bug_id,
        test_ids=test_ids,
        use_direct_navigation=True
    )
    for bug_id, test_ids in bug_map.items()
]

# Process in parallel
config = ConfigProvider.load_config_json()
results = process_items_parallel(item_tasks, config, num_workers=4)
```

### Combining with Original Test Structure

You can integrate parallel processing into your existing test structure:

```python
from test.test_bugs_std_validation import TestBugSTDValidation

class TestBugSTDValidationParallel(TestBugSTDValidation):
    def test_unique_bugs_std_id_parallel(self):
        """Parallel version of the original test."""
        config = ConfigProvider.load_config_json()
        bug_map = get_bug_to_tests_map(config["excel_path"])
        
        # Create item tasks
        base_url = config["url"].rstrip('/')
        item_tasks = [
            ItemTask(
                url=f"{base_url}/{bug_id}",
                bug_id=bug_id,
                test_ids=test_ids,
                use_direct_navigation=False  # Use search like original
            )
            for bug_id, test_ids in bug_map.items()
        ]
        
        # Process in parallel
        results = process_items_parallel(
            item_tasks=item_tasks,
            config=config,
            num_workers=4
        )
        
        # Export results (same format as original)
        export_automation_results_html(results)
```

## Error Handling

### Isolation

Failures are isolated per worker:

- If one item fails, other items continue processing
- Each worker catches exceptions and returns an error result
- The driver is always cleaned up in a `finally` block

### Result Format

Each result follows the same format as the original code:

```python
{
    "Bug ID": "123456",
    "STD ID in DOORS": "1, 2, 3",
    "STD ID in VSTS": "1, 2, 3",
    "STD Name Status": "✅",
    "Test Case ID Status": "✅",
    "Last Reproduced In Status": "✅",
    "Iteration Path Status": "✅",
    "Comments": "Match"
}
```

On error:

```python
{
    "Bug ID": "123456",
    "STD ID in DOORS": "1, 2, 3",
    "STD ID in VSTS": "---",
    "Test Case ID Status": "❌",
    "Comments": "Processing error: ...",
    ...
}
```

## Performance Considerations

### Speed Improvement

Parallel processing can significantly reduce execution time:

- **Sequential**: If each item takes 10 seconds, 100 items = 1000 seconds (~16.7 minutes)
- **Parallel (4 workers)**: 100 items = ~250 seconds (~4.2 minutes) - **4x faster**
- **Parallel (8 workers)**: 100 items = ~125 seconds (~2.1 minutes) - **8x faster**

### Resource Usage

- Each worker uses its own ChromeDriver instance
- Memory usage scales with the number of workers
- CPU usage is distributed across workers
- Recommended: Start with `num_workers = CPU count`, adjust based on system performance

### Best Practices

1. **Start with CPU count**: Use `num_workers=None` (defaults to CPU count)
2. **Monitor system resources**: Watch CPU and memory usage
3. **Adjust workers**: Reduce if system becomes overloaded, increase if system has capacity
4. **Test with small batches first**: Process 5-10 items before running on full dataset

## Troubleshooting

### Driver Creation Failures

If workers fail to create drivers:

- Check ChromeDriver installation
- Verify Chrome browser is installed
- Check browser options compatibility
- Review logs for specific error messages

### Navigation Failures

If direct navigation fails:

- Set `use_direct_navigation=False` to use search-based navigation
- Verify URL format matches your application
- Check if authentication/login is required before navigation

### Multiprocessing Issues on Windows

On Windows, multiprocessing uses 'spawn' method by default, which should work correctly. If you encounter issues:

- Ensure all imports are at the top level
- Avoid global state in worker functions
- Use proper serialization for config data

## Example: Complete Workflow

```python
import os
from infra.config_provider import ConfigProvider
from infra.working_with_exel import get_bug_to_tests_map
from logic.parallel_item_processor import (
    process_items_parallel,
    create_item_tasks_from_urls
)
from utils.report_automation_results import export_automation_results_html
from utils.constants import APP_DATA_FOLDER_NAME, CONFIG_FILE_NAME, ProgressMessages

def main():
    # 1. Load configuration
    appdata_folder = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
        APP_DATA_FOLDER_NAME
    )
    config_path = os.path.join(appdata_folder, CONFIG_FILE_NAME)
    config = ConfigProvider.load_config_json(config_path)
    
    # 2. Load bug-to-test mapping from Excel
    bug_map = get_bug_to_tests_map(config["excel_path"])
    
    # 3. Construct item URLs
    base_url = config.get("url", "").rstrip('/')
    item_urls = [f"{base_url}/{bug_id}" for bug_id in bug_map.keys()]
    
    # 4. Create item tasks
    item_tasks = create_item_tasks_from_urls(
        item_urls=item_urls,
        test_ids_map=bug_map,
        use_direct_navigation=True
    )
    
    # 5. Process in parallel
    print(f"{ProgressMessages.PROGRESS_TOTAL_PREFIX} {len(item_tasks)}")
    results = process_items_parallel(
        item_tasks=item_tasks,
        config=config,
        num_workers=4
    )
    
    # 6. Export results
    if results:
        export_automation_results_html(results)
    
    print(ProgressMessages.PROCESS_FINISHED)

if __name__ == "__main__":
    main()
```

## Files

- **`logic/parallel_item_processor.py`**: Core parallel processing module
- **`parallel_run_example.py`**: Production-ready example script with CLI
- **`test/test_parallel_items.py`**: Additional examples and integration patterns

