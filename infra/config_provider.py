import os
import json


class ConfigProvider:
    """
    Class for loading configuration from a per-user JSON file in AppData.
    """

    @staticmethod
    def load_config_json():
        """
        Load the configuration from the user's JSON file.

        :return: The loaded configuration as a dictionary.
        """
        # --- Determine per-user AppData path ---
        appdata = os.getenv('APPDATA')
        user_config_folder = os.path.join(appdata, 'AT_baseline_verifier')
        os.makedirs(user_config_folder, exist_ok=True)

        config_path = os.path.join(user_config_folder, 'config.json')

        # --- If config is missing, optionally copy default from exe folder ---
        if not os.path.exists(config_path):
            default_config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(default_config_path):
                import shutil
                shutil.copy(default_config_path, config_path)
            else:
                print(f"Default config.json not found. Creating empty config.")
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)

        # --- Load and return JSON ---
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading config.json: {e}")
            return {}
