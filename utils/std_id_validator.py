def validate_std_id(field_val, expected_test_ids):
    """
    Validates that the STD_ID field (from Azure) matches the expected test IDs from Excel.
    - field_val: The string from the STD_ID field in Azure
    - expected_test_ids: List of expected test IDs
    Returns:
        ok: True if all IDs match and count is correct, False otherwise
        comment: Explanation string for UI/report
    """
    # Convert field value to comma-separated string, handle None as empty
    field_val_str = str(field_val) if field_val is not None else ''

    # Split by commas and strip whitespace to get list of IDs
    field_std_ids = [id.strip() for id in field_val_str.split(',') if id.strip()]

    # Ensure expected_test_ids is also all strings (for reliable comparison)
    expected_test_ids = [str(tid) for tid in expected_test_ids]

    # If nothing in the STD_ID field, that's a fail
    if not field_std_ids:
        return False, "STD_ID is empty."
    # If the set of IDs doesn't match (any out of place or wrong/extra), fail
    elif set(field_std_ids) != set(expected_test_ids):
        return False, (
            f"Test Case IDs don't match! Found: {field_std_ids}, "
            f"Expected: {expected_test_ids}")
    # If the number of IDs is wrong (e.g., duplicates or missing), fail
    elif len(field_std_ids) != len(expected_test_ids):
        return False, (
            f"Number of Test Case IDs doesn't match! "
            f"Found: {len(field_std_ids)}, Expected: {len(expected_test_ids)}")
    else:
        # Perfect match!
        return True, "STD_ID matches Test Case IDs from Excel."


def build_result_record(bug_id, test_ids, field_val, status_str, comment):
    """
    Builds a dictionary representing a single validation result for reporting.
    - bug_id: The Azure Bug ID
    - test_ids: List of test IDs linked to this bug
    - field_val: Value from the STD_ID field in Azure VSTS
    - status_str: Validation status
    - comment: Detailed message for users/reports about why it passed/failed

    Returns:
        dict with all information for this bug, for tabular/HTML/CSV reporting
    """
    return {
        "Bug ID": bug_id,
        "Linked Test IDs": ", ".join([str(tid) for tid in test_ids]),
        "STD_ID in Azure": field_val,
        "Status": status_str,
        "Comments": comment
    }
