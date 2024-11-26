import json
import os
from models.config import Config


def fetch_config() -> Config:
    """
    Fetches the configuration from a file named config.json in the parent directory of this file.

    Returns
    -------
    Config
        The configuration object.

    Raises
    ------
    FileNotFoundError
        If the config file is not found at the expected location.

    ValueError
        If the config file is not valid JSON.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "../config/config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r") as config_file:
        try:
            config = json.load(config_file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Config file is not valid JSON: {e}")

    return Config(config)
