import json
from debug_log import log

SETTINGS_FILE_NAME = "settings.json"

DEFAULT_STOP_ID = "740032188" # Campus Gräsvik Id
DEFAULT_TRANSPORT = "All"

# Settings Management (REQ#3.4 and REQ#3.5)
class UserSettings:
    def __init__(self):
        # Default Settings
        self.current_stop_id = DEFAULT_STOP_ID
        self.current_transport = DEFAULT_TRANSPORT

    @staticmethod
    def reload():
        try:
            with open(SETTINGS_FILE_NAME, "r", encoding="UTF8") as f:
                data = json.load(f)

                settings = UserSettings()
                settings.current_stop_id = data.get("stop_id", settings.current_stop_id)
                settings.current_transport = data.get("transport", settings.current_transport)

                log("User Settings loaded.")
                return settings
        except FileNotFoundError:
            log("No User Settings saved, using Default Settings.")
            return UserSettings()
        except Exception as err:
            log("Error loading User Settings (%r), using Default Settings." % (err,))
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