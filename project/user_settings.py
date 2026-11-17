import json
from debug_log import log

SETTINGS_FILE_NAME = "settings.json"

DEFAULT_STOP_ID = "740032188"  # Campus Gräsvik
DEFAULT_TRANSPORT = "All"

# US3.4 and US3.5: Settings saved in settings.json on the device


class UserSettings:
    def __init__(self):
        self.current_stop_id = DEFAULT_STOP_ID
        self.current_transport = DEFAULT_TRANSPORT

    @staticmethod
    def reload():
        try:
            with open(SETTINGS_FILE_NAME, "r", encoding="UTF8") as f:
                data = json.load(f)

                settings = UserSettings()
                settings.current_stop_id = data.get(
                    "stop_id", settings.current_stop_id)
                settings.current_transport = data.get(
                    "transport", settings.current_transport)

                log("User Settings loaded.")
                return settings
        except Exception as err:
            log("Error loading User Settings (%r), using Default Settings."
                % (err,))
            return UserSettings()

    def save(self):
        try:
            with open(SETTINGS_FILE_NAME, "w") as f:
                data = {
                    "stop_id": self.current_stop_id,
                    "transport": self.current_transport,
                }

                json.dump(data, f)

                log("User Settings saved.")
        except Exception as err:
            log("Failed to save settings: %r" % (err,))
