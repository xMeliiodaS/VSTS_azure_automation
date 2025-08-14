import pandas as pd
from collections import defaultdict


def get_bug_to_tests_map(excel_path):
    """
    Map bug IDs to test case IDs from an STD Excel.
    Handles multiple bug IDs in one cell.
    """
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


# =========================
# Baseline Validation Rules
# =========================
COLUMN_MAP = {
    "expected": ["expected_results", "expected_result"],
    "results": ["test_results", "test_result"],
    "bug": ["defect_no", "bug_no", "bugs_no", "bug_number"],
    "comment": ["comment"],
    "id": ["id", "test_id"]
}


def normalize_columns(df):
    """Normalize column names: lowercase + replace spaces with underscores."""
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df


def get_column(df, key):
    """
    Return the first column name in df.columns that contains
    any of the expected variants for the given key.
    Raises an error if none found.
    """
    variants = COLUMN_MAP[key]
    for variant in variants:
        for col in df.columns:
            if variant in col:
                return col
    raise ValueError(f"Missing required column for key '{key}': variants {variants}")


def get_bug_to_tests_map(excel_path):
    """
    Map bug IDs to test case IDs from an STD Excel.
    Handles multiple bug IDs in one cell.
    """
    df = pd.read_excel(excel_path)
    df = normalize_columns(df)

    bug_col = get_column(df, "bug")
    id_col = get_column(df, "id") if "id" in df.columns else None
    if id_col is None:
        raise ValueError("No ID column found. Make sure your file has an ID column.")

    with_bugs = df[df[bug_col].apply(lambda x: isinstance(x, (int, float, str)) and not pd.isna(x))]

    bug_to_tests = defaultdict(list)
    for _, row in with_bugs.iterrows():
        raw_bug_val = str(row[bug_col])
        test_id = row[id_col]

        bug_ids = [bug.strip() for bug in raw_bug_val.split(",") if bug.strip()]

        for bug_id in bug_ids:
            if bug_id.isdigit():
                bug_to_tests[bug_id].append(test_id)

    return dict(bug_to_tests)


def is_precondition_row(row, df):
    # List possible variants for precondition columns
    possible_must_have = ['id', 'headline', 'test_description', 'test_desc', 'description', 'test_details']
    must_have = [col for col in possible_must_have if col in df.columns]

    # All other columns except must_have
    other_cols = [col for col in df.columns if col not in must_have]

    for col in must_have:
        val = row.get(col)
        if pd.isna(val) or str(val).strip() == '':
            return False

    for col in other_cols:
        val = row.get(col)
        if pd.notna(val) and str(val).strip() != '':
            return False

    return True


def validate_and_summarize(df):
    expected_col = get_column(df, "expected")
    results_col = get_column(df, "results")
    bug_col = get_column(df, "bug")
    comment_col = get_column(df, "comment")

    df[results_col] = df[results_col].astype(str).str.strip()
    df[comment_col] = df[comment_col].astype(str).str.strip()
    df[expected_col] = df[expected_col].astype(str).str.strip()
    df.loc[df[expected_col] == '', expected_col] = pd.NA

    rule2_mask = df[results_col].ne("") & df[expected_col].isna()
    print(f"Rule2 candidates before filter: {rule2_mask.sum()}")

    precondition_mask = df.apply(lambda row: is_precondition_row(row, df), axis=1)
    print(f"Precondition rows detected: {precondition_mask.sum()}")

    rule2_mask &= ~precondition_mask
    print(f"Rule2 candidates after filter: {rule2_mask.sum()}")

    rules = {
        "Rule1": df[df[results_col].eq("") & df[expected_col].notna()],
        "Rule2": df[rule2_mask],
        "Rule3": df[df[bug_col].notna() & df[results_col].str.lower().eq("pass")],
        "Rule4": df[df[bug_col].isna() & df[results_col].str.lower().eq("fail")],
        "Rule5": df[
            df[expected_col].notna() &
            ~df[results_col].str.lower().eq("pass") &
            df[comment_col].eq("")
            ]
    }

    for rule_name, v_df in rules.items():
        if v_df.empty:
            print(f"{rule_name}: PASS — no violations found.")
        else:
            cols_to_show = [c for c in ('id', 'headline', 'test_id', 'title') if c in v_df.columns]
            print(f"{rule_name}: FAIL — {len(v_df)} violation(s) found:")
            print(v_df[cols_to_show].head(10).to_string(index=False))
        print("-" * 40)

    return rules


if __name__ == "__main__":
    excel_path = "Book1.xlsx"

    # Bug to test mapping using your existing function
    bug_map = get_bug_to_tests_map(excel_path)
    print(bug_map)

    # Load STD and normalize columns
    df = pd.read_excel(excel_path)
    df = normalize_columns(df)

    # Validate baseline and print summary
    violations = validate_and_summarize(df)
