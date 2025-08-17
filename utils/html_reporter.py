# logic/html_reporter.py

import pandas as pd
import os


def export_combined_html(results, rules_dict,
                         report_title="📝 Automation Dashboard",
                         filename='std_full_report.html'):

    TABLE_STYLE = '''
        <style>
          body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #262a34;
            color: #f1f1fa;
          }
          table {
            border-collapse: collapse;
            width: 80%;
            margin: 24px auto;
            background: #32364a;
            box-shadow: 0 2px 16px #22263a44;
            border-radius: 10px;
            overflow: hidden;
          }
          th, td {
            padding: 12px 15px;
            border: 1px solid #424758;
            text-align: left;
          }
          th {
            background: linear-gradient(90deg, #4e59c2 0%, #9755e4 100%);
            color: #fff;
            font-weight: 600;
            letter-spacing: .02em;
            border: none;
          }
          tr {
            background: #32364a;
          }
          tr:nth-child(even) {
            background: #373d52;
          }
          tr:hover {
            background: #44476b;
            transition: background 0.12s;
          }
          td:last-child {
            font-style: italic;
            color: #bab8ea;
          }
          .pass {
            color: #3ff7b6;
            font-weight: bold;
          }
          .fail {
            color: #ff6584;
            font-weight: bold;
          }
        </style>
    '''

    RULE_NAMES = {
        "Rule1": "Expected Result is not empty AND Test Results Empty",
        "Rule2": "Test Results is not empty AND Expected Result is Empty",
        "Rule3": "Bug not empty AND Test Results = Pass",
        "Rule4": "Bug Empty AND Results = Fail"
    }

    html_parts = [
        "<meta charset='UTF-8'>",
        f"<h1 style='text-align:center;'>{report_title}</h1>",
        TABLE_STYLE
    ]

    # ----------------------
    # Section 1: STD ID CHECK RESULTS
    # ----------------------
    df = pd.DataFrame(results)

    def row_style(row):
        if "✅" in row.Status:
            return ['color: #3ff7b6; font-weight: bold;'] * len(row)
        if "❌" in row.Status:
            return ['color: #ff6584; font-weight: bold;'] * len(row)
        return [''] * len(row)

    styled = df.style.apply(row_style, axis=1)

    html_parts.append("<h2 style='text-align:center;'>STD ID Check Results</h2>")
    html_parts.append(styled.hide(axis='index').to_html())

    # ----------------------
    # Section 2: STD VALIDATION SUMMARY
    # ----------------------
    html_parts.append("<h2 style='text-align:center;'>Validation Summary</h2>")

    for rule_key, rows in rules_dict.items():
        rule_name = RULE_NAMES.get(rule_key, rule_key)
        html_parts.append(f"<h3 style='text-align:center;'>{rule_name} ({len(rows)} violation(s))</h3>")

        columns = ["id", "headline"]

        if rows:
            data_for_df = [{col: r.get(col, "") for col in columns} for r in rows]
            df = pd.DataFrame(data_for_df)
        else:
            df = pd.DataFrame([{col: "—" for col in columns}])

        html_parts.append(df.to_html(index=False, escape=False))

    # ----------------------
    # Write combined HTML
    # ----------------------
    html_content = "\n".join(html_parts)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
        os.startfile(filename)

    print(f"✅ Combined HTML dashboard generated: {filename}")
