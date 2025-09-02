import os
import pandas as pd


def export_combined_html(violations, results, report_title="STD Validation + Automation Results",
                         filename="std_combined_results.html"):
    """
    Combined HTML report:
      • Section 1: STD Excel Validation Summary (per-rule tables)
      • Section 2: Automation Results (single table)
    Accepts `violations` as either:
      - dict: {"Rule1": [row_dict, ...], "Rule2": [...], ...}
      - list of dicts: [{"rule": <name or key>, "count": <int>, "df": <DataFrame> or "rows": <list>}, ...]
      - list of tuples: [(<rule_key>, <rows_list>), ...]
    """

    RULE_NAMES = {
        "Rule1": "Expected Result is not empty AND Test Results Empty",
        "Rule2": "Test Results is not empty AND Expected Result is Empty",
        "Rule3": "Bug not empty AND Test Results = Pass",
        "Rule4": "Bug Empty AND Results = Fail"
    }

    TABLE_STYLE_VALIDATION = """
        <style>
          body { font-family: 'Segoe UI', Arial, sans-serif; background: #262a34; color: #f1f1fa; padding: 20px; }
          h1, h2 { text-align: center; }
          table { border-collapse: collapse; width: 45%; margin: 16px auto; background: #424242; border-radius: 8px; }
          th, td { padding: 12px; border: 1px solid #5c5c5c; text-align: left; }
          th { background: #6155a6; color: #fff; text-align: center;}
          tr:nth-child(even) { background: #313131; }
          tr:hover { background: #444444; transition: background .15s; }
          .success { color: #50fa7b; font-weight: bold; text-align: center; }
        </style>
    """

    TABLE_STYLE_BUGS = """
        <style>
          body { font-family: 'Segoe UI', Arial, sans-serif; background: #262a34; color: #f1f1fa; padding: 20px; }
          h1, h2 { text-align: center; }
          table { border-collapse: collapse; width: 90%; margin: 16px auto; background: #32364a; border-radius: 10px; }
          th, td { padding: 10px 12px; border: 1px solid #424758; text-align: left; }
          th { background: linear-gradient(90deg, #4e59c2 0%, #9755e4 100%); color: #fff; font-weight: bold;
           text-align: center;}
          tr:nth-child(even) { background: #373d52; }
          tr:hover { background: #44476b; transition: background .12s; }
          .success { color: #3ff7b6; font-weight: 600; text-align: center; }
        </style>
    """

    # ---- helpers -------------------------------------------------------------

    def normalize_violations(vio):
        """
        Return list of dicts: [{"rule_key": str, "rule_name": str, "rows": list[dict], "df": DataFrame}, ...]
        """
        normalized = []

        # Case A: dict {"Rule1": [rows], ...}
        if isinstance(vio, dict):
            items = list(vio.items())
        # Case B: list
        elif isinstance(vio, list):
            # If already [{"rule":..., ...}, ...]
            if len(vio) and isinstance(vio[0], dict) and ("rule" in vio[0] or "rule_key" in vio[0]):
                for elem in vio:
                    rule_key = elem.get("rule_key") or elem.get("rule")
                    rows = elem.get("rows")
                    df = elem.get("df")
                    if rows is None and isinstance(df, pd.DataFrame):
                        rows = df.to_dict(orient="records")
                    normalized.append({
                        "rule_key": rule_key,
                        "rule_name": RULE_NAMES.get(rule_key, str(rule_key)),
                        "rows": rows or []
                    })
                return normalized
            # If list of tuples
            elif len(vio) and isinstance(vio[0], tuple) and len(vio[0]) == 2:
                items = vio
            else:
                # Unknown list shape -> treat as single unnamed bucket
                items = [("Uncategorized", vio)]
        else:
            # Unsupported -> wrap as one bucket
            items = [("Uncategorized", [])]

        for rule_key, rows in items:
            normalized.append({
                "rule_key": rule_key,
                "rule_name": RULE_NAMES.get(rule_key, str(rule_key)),
                "rows": rows or []
            })
        return normalized

    # Preferable keys for each semantic column
    ID_KEYS = ["id", "test_id"]

    def first_nonempty(row, keys):
        for k in keys:
            if k in row and row[k] is not None and str(row[k]).strip() != "":
                return row[k]
        return "—"

    def rows_to_df_combined(norm_vio):
        """
        Generate a single DataFrame with one row per Rule.
        Each row contains:
          - Rule Name (column: "Rule")
          - Comma-separated Test Case IDs (column: "Test Case IDs")
        """
        data = []
        for bucket in norm_vio:
            rule_name = bucket["rule_name"]
            rows = bucket["rows"] or []

            # Get all test case IDs as a comma-separated string
            test_case_ids = ", ".join(
                str(first_nonempty(r, ID_KEYS)) for r in rows if str(first_nonempty(r, ID_KEYS)) != "✅")

            # Add the row for this rule
            data.append({
                "Rule": rule_name,
                "Test Case IDs": f"{test_case_ids}" if test_case_ids else "✅"  # Handle empty IDs
            })

        if not data:  # Handle case when there are no violations
            data = [{"Rule": "—", "Test Case IDs": "—"}]

        return pd.DataFrame(data)

    # ---- build HTML ----------------------------------------------------------

    html_parts = [f"<html><head><meta charset='UTF-8'>{TABLE_STYLE_VALIDATION}</head><body>",
                  "<h2>STD Excel Validation Summary</h2>"]

    # Section 1: STD Excel Validation Summary (Custom Style for this table)
    norm_vio = normalize_violations(violations)
    if not norm_vio:
        html_parts.append("<p class='success'>No violations found ✅</p>")
    else:
        combined_df = rows_to_df_combined(norm_vio)
        html_parts.append(combined_df.to_html(index=False, escape=False))

    # Change style head for Section 2
    html_parts.append(f"<style>{TABLE_STYLE_BUGS}</style>")

    # Section 2: Automation Results
    html_parts.append("<h2>Automation Results</h2>")
    if results:
        df_res = pd.DataFrame(results)
        html_parts.append(df_res.to_html(index=False, escape=False))
    else:
        html_parts.append(
            '<p style="text-align: center; font-size: 24px; font-weight: bold;">All clear! No bugs found ✅</p>')

    html_parts.append("</body></html>")
    report_html = "\n".join(html_parts)

    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_html)

    try:
        os.startfile(path)  # Windows only; safe to ignore on non-Windows
    except Exception:
        pass

    print(f"✅ Combined report generated: {path}")
