import pandas as pd
from collections import defaultdict
from openpyxl import load_workbook
from collections import defaultdict


def normalize_columns_pandas(df):
    """Normalize column names: lowercase + replace spaces with underscores."""
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df


def get_column_pandas(df, key, required=True):
    """
    Return the first column name in df.columns that matches expected variants.
    If required=False, returns None instead of raising error when missing.
    """
    variants = COLUMN_MAP[key]
    for variant in variants:
        for col in df.columns:
            if variant in col:
                return col
    if required:
        raise ValueError(f"Missing required column for key '{key}': variants {variants}")
    return None


def get_bug_to_tests_map(excel_path):
    """
    Map bug IDs to test case IDs from an STD Excel.
    Handles multiple bug IDs in one cell.
    """
    df = pd.read_excel(excel_path)
    df = normalize_columns_pandas(df)

    bug_col = get_column_pandas(df, "bug")
    id_col = get_column_pandas(df, "id") if "id" in df.columns else None
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


from openpyxl import load_workbook
from collections import defaultdict

COLUMN_MAP = {
    "expected": ["expected_results", "expected_result"],
    "results": ["test_results", "test_result"],
    "bug": ["defect_no", "bug_no", "bugs_no", "bug_number"],
    "comment": ["comment"],
    "id": ["id", "test_id"]
}


def normalize_columns(cols):
    """Normalize column names: lowercase + replace spaces with underscores."""
    return [col.strip().lower().replace(" ", "_") for col in cols]


def get_column(headers, key):
    """Return first header that matches any variant of key."""
    variants = COLUMN_MAP[key]
    for variant in variants:
        for h in headers:
            if variant in h:
                return h
    raise ValueError(f"Missing required column for key '{key}'")


def is_precondition_row(row, headers):
    """Check if row is a precondition row."""
    possible_must_have = ['id', 'headline', 'test_description', 'test_desc', 'description', 'test_details']
    must_have = [h for h in headers if h in possible_must_have]
    other_cols = [h for h in headers if h not in must_have]

    for col in must_have:
        val = row.get(col)
        if val is None or str(val).strip() == '':
            return False

    for col in other_cols:
        val = row.get(col)
        if val is not None and str(val).strip() != '':
            return False

    return True


def validate_and_summarize(file_path):
    """Validate STD rules using openpyxl."""
    wb = load_workbook(filename=file_path, data_only=True)
    ws = wb.active

    headers = normalize_columns([cell.value for cell in ws[1]])
    expected_col = get_column(headers, "expected")
    results_col = get_column(headers, "results")
    bug_col = get_column(headers, "bug")
    comment_col = get_column(headers, "comment")
    id_col = get_column(headers, "id")

    data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_dict = dict(zip(headers, row))
        # Strip strings
        for k, v in row_dict.items():
            if isinstance(v, str):
                row_dict[k] = v.strip()
        data.append(row_dict)

    # Masks for rules
    rule1_rows = []
    rule2_rows = []
    rule3_rows = []
    rule4_rows = []

    for row in data:
        res = str(row.get(results_col) or '').strip()
        res_lower = res.lower()
        exp = row.get(expected_col)
        bug = row.get(bug_col)

        # Rule1: expected filled AND results empty, ignore 'N/A'/'NOT TESTED'
        if exp and (res == '' or res_lower in ['none', 'nan']) and res_lower not in ['n/a', 'not tested']:
            rule1_rows.append(row)

        # Rule2: results filled AND expected empty, excluding precondition
        if (res != '' and exp in [None, '']) and not is_precondition_row(row, headers):
            rule2_rows.append(row)

        # Rule3: bug filled AND results = pass
        if bug and res_lower == 'pass':
            rule3_rows.append(row)

        # Rule4: bug empty AND results = fail
        if not bug and res_lower == 'fail':
            rule4_rows.append(row)

    rules = {
        "Rule1": rule1_rows,
        "Rule2": rule2_rows,
        "Rule3": rule3_rows,
        "Rule4": rule4_rows,
    }

    # Print summary
    for rule_name, rows in rules.items():
        if not rows:
            print(f"{rule_name}: PASS — no violations found.")
        else:
            print(f"{rule_name}: FAIL — {len(rows)} violation(s) found:")
            for r in rows[:10]:
                print(f"  {r.get(id_col)}  {r.get('headline', '')}")
        print("-" * 40)

    return rules


if __name__ == "__main__":
    file_path = "Book1.xlsx"

    bug_map = get_bug_to_tests_map(file_path)
    print(bug_map)


    violations = validate_and_summarize(file_path)
