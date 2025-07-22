import pandas as pd
from collections import defaultdict

def get_bug_to_tests_map(excel_path):
    df = pd.read_excel(excel_path)
    with_bugs = df[df["Bugs No. V8"].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]

    bug_to_tests = defaultdict(list)
    for _, row in with_bugs.iterrows():
        bug_id = str(int(round(row["Bugs No. V8"])))  # Make bug_id a string/key
        test_id = row["ID"]
        bug_to_tests[bug_id].append(test_id)
    return dict(bug_to_tests)  # Convert to regular dict if needed

# Example usage:
bug_map = get_bug_to_tests_map("Escort - CARTOSOUND 4D - Clinical WF.xlsx")
print(bug_map)
