# logic/html_reporter.py

import pandas as pd


def export_html_report(results, report_title="📝 Automation Results for STD_ID Validation",
                       filename='std_id_check_results.html'):
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

    df = pd.DataFrame(results)

    def row_style(row):
        if "✅" in row.Status:
            return ['color: #388e3c; font-weight: bold;'] * len(row)
        if "❌" in row.Status:
            return ['color: #c62828; font-weight: bold;'] * len(row)
        return [''] * len(row)

    styled = df.style.apply(row_style, axis=1)

    html_output = (
            "<meta charset='UTF-8'>"
            f"<h2 style='text-align:center;'>{report_title}</h2>"
            + TABLE_STYLE
            + styled.hide(axis='index').to_html()
    )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"✅ Fancy HTML report generated: {filename}")
