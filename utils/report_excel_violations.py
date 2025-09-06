import os
import pandas as pd

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

def export_excel_violations_html(violations, filename="violations_report.html"):
    """Generates HTML report for Excel validation only."""

    def normalize_violations(vio):
        normalized = []
        if isinstance(vio, dict):
            items = list(vio.items())
        elif isinstance(vio, list):
            if len(vio) and isinstance(vio[0], dict) and ("rule" in vio[0] or "rule_key" in vio[0]):
                for elem in vio:
                    rule_key = elem.get("rule_key") or elem.get("rule")
                    rows = elem.get("rows") or []
                    normalized.append({
                        "rule_key": rule_key,
                        "rule_name": RULE_NAMES.get(rule_key, str(rule_key)),
                        "rows": rows
                    })
                return normalized
            elif len(vio) and isinstance(vio[0], tuple):
                items = vio
            else:
                items = [("Uncategorized", vio)]
        else:
            items = [("Uncategorized", [])]

        for rule_key, rows in items:
            normalized.append({
                "rule_key": rule_key,
                "rule_name": RULE_NAMES.get(rule_key, str(rule_key)),
                "rows": rows or []
            })
        return normalized

    def rows_to_df(norm_vio):
        ID_KEYS = ["id", "test_id"]
        def first_nonempty(row, keys):
            for k in keys:
                if k in row and row[k] not in (None, ""):
                    return row[k]
            return "—"

        data = []
        for bucket in norm_vio:
            rule_name = bucket["rule_name"]
            rows = bucket["rows"]
            test_case_ids = ", ".join(str(first_nonempty(r, ID_KEYS)) for r in rows if first_nonempty(r, ID_KEYS) != "✅")
            data.append({"Rule": rule_name, "Test Case IDs": test_case_ids or "✅"})
        return pd.DataFrame(data) if data else pd.DataFrame([{"Rule": "—", "Test Case IDs": "—"}])

    norm_vio = normalize_violations(violations)
    html_parts = [f"<html><head><meta charset='UTF-8'>{TABLE_STYLE_VALIDATION}</head><body><h2>STD Excel Validation Summary</h2>"]

    if not norm_vio:
        html_parts.append("<p class='success'>No violations found ✅</p>")
    else:
        df = rows_to_df(norm_vio)
        html_parts.append(df.to_html(index=False, escape=False))

    html_parts.append("</body></html>")
    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    try:
        os.startfile(path)
    except Exception:
        pass
    print(f"✅ Violations report generated: {path}")
