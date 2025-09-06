import os
import pandas as pd

TABLE_STYLE_BUGS = """
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #262a34; color: #f1f1fa; padding: 20px; }
  h1, h2 { text-align: center; }
  table { border-collapse: collapse; width: 90%; margin: 16px auto; background: #32364a; border-radius: 10px; }
  th, td { padding: 10px 12px; border: 1px solid #424758; text-align: left; }
  th { background: linear-gradient(90deg, #4e59c2 0%, #9755e4 100%); color: #fff; font-weight: bold; text-align: center;}
  tr:nth-child(even) { background: #373d52; }
  tr:hover { background: #44476b; transition: background .12s; }
  .success { color: #3ff7b6; font-weight: 600; text-align: center; }
</style>
"""

def export_automation_results_html(results, filename="automation_results.html"):
    """
    Generates HTML report for automation results only.
    """
    html_parts = [f"<html><head><meta charset='UTF-8'>{TABLE_STYLE_BUGS}</head><body><h2>Automation Results</h2>"]

    if results:
        df = pd.DataFrame(results)
        html_parts.append(df.to_html(index=False, escape=False))
    else:
        html_parts.append('<p style="text-align:center;font-size:24px;font-weight:bold;">All clear! No bugs found ✅</p>')

    html_parts.append("</body></html>")
    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    try:
        os.startfile(path)
    except Exception:
        pass

    print(f"✅ Automation results report generated: {path}")
