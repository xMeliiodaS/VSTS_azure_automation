"""
Constants module for the VSTS Azure Automation project.
Centralizes all hardcoded values to improve maintainability and clean code practices.
"""

# ============================================================================
# Application Configuration
# ============================================================================
APP_DATA_FOLDER_NAME = "ste_tool_studio"
CONFIG_FILE_NAME = "config.json"
REPORTS_FOLDER_NAME = "reports"

# ============================================================================
# Timeouts and Wait Times (in seconds)
# ============================================================================
class Timeouts:
    """Centralized timeout and wait time constants."""
    # Default timeouts
    DEFAULT_TIMEOUT = 20
    SHORT_TIMEOUT = 10
    LONG_TIMEOUT = 30
    
    # Specific use case timeouts
    ELEMENT_VISIBILITY_TIMEOUT = 30
    ELEMENT_CLICKABLE_TIMEOUT = 10
    FIELD_VALIDATION_TIMEOUT = 20
    
    # Sleep durations
    PAGE_LOAD_SLEEP = 3
    INPUT_DELAY_SLEEP = 0.1
    POLL_FREQUENCY = 0.2

# ============================================================================
# Retry Configuration
# ============================================================================
class Retries:
    """Centralized retry count constants."""
    DEFAULT_RETRIES = 3
    NAVIGATION_RETRIES = 3
    CLICK_RETRIES = 3

# ============================================================================
# Status Symbols and Messages
# ============================================================================
class Status:
    """Status symbols and placeholder values."""
    SUCCESS = "✅"
    FAILURE = "❌"
    PLACEHOLDER = "---"
    MATCH = "Match"
    EMPTY = ""
    
    # Validation status messages
    STD_ID_EMPTY = "STD ID is empty."
    TC_IDS_DONT_MATCH = "TC IDs don't match expected TC IDs."
    ID_COUNT_MISMATCH = "Number of IDs doesn't match expected!"

# ============================================================================
# Browser Configuration
# ============================================================================
class BrowserOptions:
    """Chrome browser options arguments."""
    ARGUMENTS = [
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-infobars",
        "--disable-blink-features=AutomationControlled"
    ]

# ============================================================================
# STD and Validation Constants
# ============================================================================
class STDConstants:
    """Constants related to STD (Standard) validation."""
    # Default STD name for additional info extraction
    DEFAULT_STD_NAME = "Feather - Unique Functionality STD"
    
    # Excel validation result values
    PASS = "pass"
    FAIL = "fail"
    NOT_TESTED = "not tested"
    N_A = "n/a"
    NONE = "none"
    NAN = "nan"
    
    # Actual results validation
    ACTUAL_PASS_VALUE = "Y"
    ACTUAL_FAIL_PREFIX = "N,"

# ============================================================================
# Report Configuration
# ============================================================================
class ReportConfig:
    """Report file names and configuration."""
    AUTOMATION_RESULTS_FILENAME = "automation_results.html"
    VIOLATIONS_REPORT_FILENAME = "rules_violations_report.html"
    
    # Report messages
    NO_BUGS_MESSAGE = "All clear! No bugs found ✅"
    NO_VIOLATIONS_MESSAGE = "No violations found ✅"

# ============================================================================
# Excel Column Mapping
# ============================================================================
COLUMN_MAP = {
    "expected": ["expected_results", "expected_result"],
    "results": ["test_results", "test_result"],
    "bug": ["defect_no", "bug_no", "bugs_no", "bug_number"],
    "comment": ["comment"],
    "id": ["id", "test_id"],
    "actual": ["actual_results", "actual_result"]
}

# ============================================================================
# Excel Validation Rules
# ============================================================================
# Valid Test Results (only these 4 are allowed)
VALID_TEST_RESULTS = ("pass", "fail", "not tested", "n/a")


class ExcelRules:
    """Excel validation rule names and descriptions."""
    RULE_NAMES = {
        "Rule1": "Expected Result is not empty AND Test Results Empty",
        "Rule2": "Test Results is not empty AND Expected Result is Empty",
        "Rule3": "Bug not empty AND Test Results = Pass",
        "Rule4": "Bug Empty AND Results = Fail",
        "Rule5": "Actual Results validation (Pass=Y, Fail=N, Not Tested=N/A, N/A=N/A)",
        "Rule6": "Precondition (Expected=N/A): Test Results, Actual Results, Bug must be empty",
        "Rule7": "Test Result is N/A but Comment is empty",
        "Rule8": "Test Results value is not one of: Pass, Fail, Not Tested, N/A",
    }
    
    RULE_COLUMN_NAME = "Rule"
    TC_ID_COLUMN_NAME = "Test Case ID"
    
    # Precondition row detection
    POSSIBLE_MUST_HAVE_COLUMNS = [
        'id', 'headline', 'test_description', 'test_desc', 
        'description', 'test_details'
    ]

# ============================================================================
# Progress Messages
# ============================================================================
class ProgressMessages:
    """Progress and status messages for console output."""
    PROGRESS_TOTAL_PREFIX = "PROGRESS_TOTAL:"
    PROGRESS_PREFIX = "PROGRESS:"
    PROCESS_FINISHED = "PROCESS_FINISHED"
    NO_BUGS_FOUND = "No bugs found in the bug map. Exporting an empty report."

