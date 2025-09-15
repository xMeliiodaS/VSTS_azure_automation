import os, unittest

from infra.config_provider import ConfigProvider
from infra.working_with_exel import validate_and_summarize

from utils.report_excel_violations import export_excel_violations_html


class TestExcelViolations(unittest.TestCase):
    def setUp(self):
        self.config = ConfigProvider.load_config_json()
        self.std_excel_path = self.config["excel_path"]

    def test_excel_violations(self):
        """Validate that Excel is consistent and generate violations HTML report."""
        violations = validate_and_summarize(self.std_excel_path)

        # Export HTML report for violations
        export_excel_violations_html(violations)

        self.assertIsNotNone(violations, "Excel validation failed: no violations summary returned.")


if __name__ == "__main__":
    appdata_folder = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
        'AT_baseline_verifier'
    )
    config_path = os.path.join(appdata_folder, 'config.json')

    config = ConfigProvider.load_config_json(config_path)

    suite = unittest.TestSuite()
    suite.addTest(TestExcelViolations('test_excel_violations'))
    unittest.TextTestRunner(verbosity=2).run(suite)
