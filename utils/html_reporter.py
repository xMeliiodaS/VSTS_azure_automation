# logic/html_reporter.py

import pandas as pd


def export_html_report(results, report_title="📝 Automation Results for STD_ID Validation",
                       filename='std_id_check_results.html'):
    TABLE_STYLE = '''
    <style>
      body { font-family: 'Segoe UI', Arial, sans-serif; }
      table { border-collapse: collapse; width: 98%; margin: 20px auto; background: #f9f9fb; box-shadow: 0 0 10px #ccc;}
      th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
      th { background: #3f51b5; color: white; }
      tr:nth-child(even) { background: #e8eaf6; }
      tr:hover { background: #d1c4e9; }
      td:last-child { font-style: italic; }
      .pass { color: #388e3c; font-weight: bold; }
      .fail { color: #c62828; font-weight: bold; }
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
