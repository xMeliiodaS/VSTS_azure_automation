import json


class ConfigProvider:
    """
    Class for loading configuration from a JSON file.
    """

    @staticmethod
    def load_config_json():
        """
        Load the configuration from the specified JSON file.

        :return: The loaded configuration as a dictionary.
        """
        try:
            with open("../config.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found. Starting with an empty library.")
