import pandas as pd
import os

def export_combined_html(violations, results, report_title="STD Validation + Automation Results", filename="std_combined_results.html"):
    """
    Export a combined HTML report with:
      1. STD Excel Validation summary & details (violations)
      2. Automation Results (results)
    """

    TABLE_STYLE = """
        <style>
          body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #262a34;
            color: #f1f1fa;
            padding: 20px;
          }
          h1, h2 {
            color: #61dafb;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
          }
          th, td {
            border: 1px solid #444;
            padding: 8px;
            text-align: left;
          }
          th {
            background-color: #333;
          }
          tr:nth-child(even) {
            background-color: #2e323d;
          }
          .success {
            color: #4caf50;
            font-weight: bold;
          }
          .fail {
            color: #ff5252;
            font-weight: bold;
          }
        </style>
    """

    html_parts = [f"<html><head>{TABLE_STYLE}</head><body>"]
    html_parts.append(f"<h1>{report_title}</h1>")

    # --- Violations Section ---
    html_parts.append("<h2>STD Excel Validation Summary</h2>")

    if not violations:
        html_parts.append("<p class='success'>No violations found ✅</p>")
    else:
        # violations is a LIST of dicts (rule_name, count, df)
        for v in violations:
            rule_name = v["rule"]
            count = v["count"]
            df = v["df"]

            html_parts.append(f"<h3>{rule_name} ({count} violation(s))</h3>")
            if count == 0 or df.empty:
                html_parts.append("<p>No violations found ✅</p>")
            else:
                html_parts.append(df.to_html(index=False, escape=False))

    # --- Automation Results Section ---
    html_parts.append("<h2>Automation Results</h2>")

    if not results:
        html_parts.append("<p>No automation results available.</p>")
    else:
        df_results = pd.DataFrame(results)
        if not df_results.empty:
            html_parts.append(df_results.to_html(index=False, escape=False))
        else:
            html_parts.append("<p>No automation results found.</p>")

    # close HTML
    html_parts.append("</body></html>")

    report_html = "\n".join(html_parts)

    # save to file
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_html)

    print(f"[INFO] Combined report generated at: {path}")
