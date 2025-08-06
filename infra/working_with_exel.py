import pandas as pd
from collections import defaultdict

def get_bug_to_tests_map(excel_path):
    df = pd.read_excel(excel_path)

    # Auto-detect bug/defect column
    bug_col = None
    for col in df.columns:
        col_lower = col.lower()
        if "bug" in col_lower or "defect" in col_lower:
            bug_col = col
            break

    if bug_col is None:
        raise ValueError(
            f"No column containing 'Bug' or 'Defect' found! Columns in file: {list(df.columns)}"
        )

    # Keep rows with valid bug/defect numbers
    with_bugs = df[df[bug_col].apply(lambda x: isinstance(x, (int, float, str)) and not pd.isna(x))]

    bug_to_tests = defaultdict(list)
    for _, row in with_bugs.iterrows():
        raw_bug_val = str(row[bug_col])  # could be "273427" or "273427, 273421"
        test_id = row["ID"]

        # Split by comma, strip whitespace, and handle each bug ID
        bug_ids = [bug.strip() for bug in raw_bug_val.split(",") if bug.strip()]

        for bug_id in bug_ids:
            # Only add if it's a number (might contain junk in Excel)
            if bug_id.isdigit():
                bug_to_tests[bug_id].append(test_id)
            # You might want to add a warning if bug_id is not all digits

    return dict(bug_to_tests)



# # Example usage:
# bug_map = get_bug_to_tests_map("Book1.xlsx")
# print(bug_map)
