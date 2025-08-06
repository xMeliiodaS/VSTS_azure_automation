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

    # Only rows with valid bug/defect number
    with_bugs = df[df[bug_col].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]

    bug_to_tests = defaultdict(list)
    for _, row in with_bugs.iterrows():
        bug_id = str(int(round(row[bug_col])))  # Make bug_id a string
        test_id = row["ID"]
        bug_to_tests[bug_id].append(test_id)
    return dict(bug_to_tests)


# # Example usage:
bug_map = get_bug_to_tests_map("Book1.xlsx")
print(bug_map)
