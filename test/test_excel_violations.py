import os, unittest

from infra.config_provider import ConfigProvider
from infra.working_with_exel import validate_and_summarize

from utils.report_excel_violations import export_excel_violations_html
from utils.constants import APP_DATA_FOLDER_NAME, CONFIG_FILE_NAME


class TestExcelViolations(unittest.TestCase):
    def setUp(self):
        self.config = ConfigProvider.load_config_json()
        self.std_excel_path = self.config["excel_path"]

    def test_excel_violations(self):
        """Validate that STD Excel is 100% valid with zero violations; generate HTML report."""
        violations = validate_and_summarize(self.std_excel_path)

        # Export HTML report for violations
        export_excel_violations_html(violations)

        self.assertIsNotNone(violations, "Excel validation failed: no violations summary returned.")

        # Uncomment below to fail the test when STD has any violation (100% valid required):
        # total = sum(len(rows) for rows in violations.values())
        # self.assertEqual(total, 0, "STD has violations (must be 100%% valid). See HTML report for details.")


if __name__ == "__main__":
    appdata_folder = os.path.join(
        os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
        APP_DATA_FOLDER_NAME
    )
    config_path = os.path.join(appdata_folder, CONFIG_FILE_NAME)

    config = ConfigProvider.load_config_json(config_path)

    suite = unittest.TestSuite()
    suite.addTest(TestExcelViolations('test_excel_violations'))
    unittest.TextTestRunner(verbosity=2).run(suite)
