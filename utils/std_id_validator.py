def validate_std_id(field_val, expected_test_ids):
    field_val_str = str(field_val) if field_val is not None else ''
    field_std_ids = [id.strip() for id in field_val_str.split(',') if id.strip()]
    expected_test_ids = [str(tid) for tid in expected_test_ids]

    if not field_std_ids:
        return False, "STD_ID is empty."
    elif set(field_std_ids) != set(expected_test_ids):
        return False, (
            f"Test Case IDs don't match! Found: {field_std_ids}, "
            f"Expected: {expected_test_ids}")
    elif len(field_std_ids) != len(expected_test_ids):
        return False, (
            f"Number of Test Case IDs doesn't match! "
            f"Found: {len(field_std_ids)}, Expected: {len(expected_test_ids)}")
    else:
        return True, "STD_ID matches Test Case IDs from Excel."


# File: logic/results_builder.py

def build_result_record(bug_id, test_ids, field_val, status_str, comment):
    return {
        "Bug ID": bug_id,
        "Linked Test IDs": ", ".join([str(tid) for tid in test_ids]),
        "STD_ID in Azure": field_val,
        "Status": status_str,
        "Comments": comment
    }
