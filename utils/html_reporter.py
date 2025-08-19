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

    TABLE_STYLE = """
        <style>
          body { font-family: 'Segoe UI', Arial, sans-serif; background: #262a34; color: #f1f1fa; padding: 20px; }
          h1,h2,h3 { text-align: center; }
          table { border-collapse: collapse; width: 90%; margin: 16px auto; background: #32364a; border-radius: 10px; }
          th, td { padding: 10px 12px; border: 1px solid #424758; text-align: left; }
          th { background: linear-gradient(90deg, #4e59c2 0%, #9755e4 100%); color: #fff; font-weight: 600; }
          tr:nth-child(even) { background: #373d52; }
          tr:hover { background: #44476b; transition: background .12s; }
          .success { color: #3ff7b6; font-weight: 600; text-align: center; }
          .fail { color: #ff6584; font-weight: 600; text-align: center; }
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
    HEADLINE_KEYS = ["headline", "title", "summary", "test_name", "test_description", "description"]
    EXPECTED_KEYS = ["expected", "expected_result", "expected_results"]
    RESULTS_KEYS = ["results", "test_results", "test_result"]
    BUG_KEYS = ["bug", "bug_no", "defect_no", "bugs_no", "bug_number"]

    def first_nonempty(row, keys):
        for k in keys:
            if k in row and row[k] is not None and str(row[k]).strip() != "":
                return row[k]
        return "—"

    def rows_to_df(rows):
        # rows: list of dicts (already normalized by your loader)
        data = []
        for r in rows:
            data.append({
                "Test ID": first_nonempty(r, ID_KEYS),
                "Headline": first_nonempty(r, HEADLINE_KEYS),
                "Expected Result": first_nonempty(r, EXPECTED_KEYS),
                "Actual Result": first_nonempty(r, RESULTS_KEYS),
                "Bug": first_nonempty(r, BUG_KEYS),
            })
        if not data:
            data = [{"Test ID": "—", "Headline": "—", "Expected Result": "—", "Actual Result": "—", "Bug": "—"}]
        return pd.DataFrame(data)

    # ---- build HTML ----------------------------------------------------------

    html_parts = [f"<html><head><meta charset='UTF-8'>{TABLE_STYLE}</head><body>"]
    html_parts.append(f"<h1>{report_title}</h1>")

    # Section 1: Violations
    html_parts.append("<h2>STD Excel Validation Summary</h2>")

    norm_vio = normalize_violations(violations)
    if not norm_vio:
        html_parts.append("<p class='success'>No violations found ✅</p>")
    else:
        for bucket in norm_vio:
            rule_name = bucket["rule_name"]
            rows = bucket["rows"] or []
            df = rows_to_df(rows)
            html_parts.append(f"<h3>{rule_name}")
            html_parts.append(df.to_html(index=False, escape=False))

    # Section 2: Automation Results
    html_parts.append("<h2>Automation Results</h2>")
    if results:
        df_res = pd.DataFrame(results)
        # Keep index hidden; rely on keys produced by build_result_record
        html_parts.append(df_res.to_html(index=False, escape=False))
    else:
        html_parts.append("<p>No automation results available.</p>")

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
