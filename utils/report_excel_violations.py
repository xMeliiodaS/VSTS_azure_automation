import os
import pandas as pd

from utils.utils import save_report_copy
from utils.constants import ExcelRules, ReportConfig, Status, REPORTS_FOLDER_NAME

TABLE_STYLE_VALIDATION = """
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #262a34; color: #f1f1fa; padding: 20px; }
  h1, h2 { text-align: center; }
  table { border-collapse: collapse; width: 45%; margin: 16px auto; background: #32364a; border-radius: 8px; }
  th, td { padding: 12px; border: 1px solid #424758; text-align: left; }
  th { background: linear-gradient(90deg, #4e59c2 0%, #9755e4 100%); color: #fff; font-weight: bold; text-align: center;}
  tr:nth-child(even) { background: #373d52; }
  tr:hover { background: #44476b; transition: background .15s; }
  .success { color: #3ff7b6; font-weight: 600; text-align: center; }
</style>
"""

def export_excel_violations_html(violations, filename=ReportConfig.VIOLATIONS_REPORT_FILENAME):
    """
    Generates HTML report for Excel validation only.
    """

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
                        "rule_name": ExcelRules.RULE_NAMES.get(rule_key, str(rule_key)),
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
                "rule_name": ExcelRules.RULE_NAMES.get(rule_key, str(rule_key)),
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
            test_case_ids = ", ".join(
                str(first_nonempty(r, ID_KEYS)) for r in rows if first_nonempty(r, ID_KEYS) != Status.SUCCESS)
            data.append({ExcelRules.RULE_COLUMN_NAME: rule_name, ExcelRules.TC_ID_COLUMN_NAME: test_case_ids or Status.SUCCESS})
        return pd.DataFrame(data) if data else pd.DataFrame([{ExcelRules.RULE_COLUMN_NAME: "—", ExcelRules.TC_ID_COLUMN_NAME: "—"}])

    norm_vio = normalize_violations(violations)
    html_parts = [
        f"<html><head><meta charset='UTF-8'>{TABLE_STYLE_VALIDATION}</head><body><h2>STD Excel Validation Summary</h2>"
    ]

    if not norm_vio:
        html_parts.append(f"<p class='success'>{ReportConfig.NO_VIOLATIONS_MESSAGE}</p>")
    else:
        df = rows_to_df(norm_vio)
        html_parts.append(df.to_html(index=False, escape=False))

    html_parts.append("</body></html>")

    os.makedirs(REPORTS_FOLDER_NAME, exist_ok=True)
    path = os.path.join(REPORTS_FOLDER_NAME, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    # ✅ unified save
    save_report_copy(path)

    try:
        os.startfile(path)
    except Exception:
        pass

    print(f"✅ Violations report generated: {path}")
