import configparser
import os

def get_api_key():
    """
    Reads the Gemini API key from the config.ini file.
    Raises an error if the file or key is not found or is a placeholder.
    """
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    if not os.path.exists(config_file):
        raise FileNotFoundError(
            f"Configuration file '{config_file}' not found. "
            f"Please copy 'config.ini.template' to '{config_file}' and add your API key."
        )

    config.read(config_file)

    if 'gemini' not in config or 'api_key' not in config['gemini']:
        raise ValueError(
            f"API key not found in '{config_file}'. "
            f"Please ensure the file has a [gemini] section with an 'api_key' entry."
        )

    api_key = config['gemini']['api_key']

    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        raise ValueError(
            f"API key in '{config_file}' is missing or is still the placeholder value. "
            f"Please add your actual Gemini API key to the file."
        )

    return api_key

# You can import this variable in other parts of the application.
# Note: This will run on import, so an error will be raised if the config is invalid.
API_KEY = get_api_key()
