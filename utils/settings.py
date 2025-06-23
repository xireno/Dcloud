import json
import os

# Define a default configuration path if not provided
CONFIG_PATH = "./data/user_settings.json"

async def load_user_settings(user_id, config_path=CONFIG_PATH):
    """
    Load user settings or provide defaults if none exist.
    """
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_settings = json.load(f)
        # Return user-specific settings or default ones
        return user_settings.get(str(user_id), {
            "encrypt": False,
            "compress": False,
            "chunk_size": 8 * 1024 * 1024  # Default chunk size 8MB
        })
    else:
        # Create default settings file if it does not exist
        default_settings = {
            str(user_id): {
                "encrypt": False,
                "compress": False,
                "chunk_size": 8 * 1024 * 1024  # Default chunk size 8MB
            }
        }
        with open(config_path, "w") as f:
            json.dump(default_settings, f, indent=4)
        return default_settings[str(user_id)]

async def save_user_settings(user_id, settings, config_path=CONFIG_PATH):
    """
    Save user settings to the configuration file.
    """
    # Load existing settings or initialize an empty dictionary
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            user_settings = json.load(f)
    else:
        user_settings = {}

    # Update settings for the given user_id
    user_settings[str(user_id)] = settings

    # Save the updated settings back to the file
    with open(config_path, "w") as f:
        json.dump(user_settings, f, indent=4)
