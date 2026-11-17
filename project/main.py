import json
import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets_env import WIFI_SSID, WIFI_PASSWORD

import styles
import departures_service as dep_service
from user_settings import UserSettings, DEFAULT_STOP_ID
from stations import stations

<<<<<<< Updated upstream
# stations.py is the complete pool of selectable stops: [id, name]
STATIONS = sorted(stations, key=lambda s: s[1])

=======
SETTINGS_FILE = "settings.json"
DEFAULT_STOP_ID = "740032188"  # Campus Gräsvik
DEFAULT_TRANSPORT = "All"
TRANSPORT_TYPES = ["All", "Bus", "Train", "Ferry"]

# All stops, sorted by name: [id, name]
STATIONS = sorted(stations, key=lambda s: s[1])


# str.upper() does not change å, ä and ö in MicroPython
def upper_sv(text):
    text = text.replace("å", "Å").replace("ä", "Ä").replace("ö", "Ö")
    return text.upper()


>>>>>>> Stashed changes
class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()
        styles.init_fonts()

<<<<<<< Updated upstream
        # User Settings
        # REQ#3.4: Load Saved User Settings at Startup
        self.settings = UserSettings.reload()
        self.current_station = None
=======
        # Factory defaults
        self.current_stop_id = DEFAULT_STOP_ID
        self.current_station = None
        self.current_transport = DEFAULT_TRANSPORT

        # REQ#3.4: Load saved settings at startup
        self.load_settings()
>>>>>>> Stashed changes

        log("Connecting to Wifi..")
        self.connect_wifi()

        # Updates current_station data
        self.set_current_stop_id(self.settings.current_stop_id)

        self.create_ui()

        log("student application ready - starting at startup tile (0, 0)")
<<<<<<< Updated upstream
=======

    # REQ#3.4 and REQ#3.5: Settings
    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                self.current_stop_id = data.get("stop", DEFAULT_STOP_ID)
                self.current_transport = data.get("transport",
                                                  DEFAULT_TRANSPORT)
                log("Settings loaded from flash")
        except Exception:
            self.current_stop_id = DEFAULT_STOP_ID
            self.current_transport = DEFAULT_TRANSPORT
            log("No settings found, using factory default")

        if self.current_transport not in TRANSPORT_TYPES:
            self.current_transport = DEFAULT_TRANSPORT

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({"stop": self.current_stop_id,
                           "transport": self.current_transport}, f)
            log("Settings saved to flash")
        except Exception as err:
            log("Failed to save settings: %r" % (err,))
>>>>>>> Stashed changes

    def set_current_stop_id(self, stop_id):
        for station in STATIONS:
            if station[0] == stop_id:
                self.current_station = station
                self.settings.current_stop_id = stop_id
                return

        # The stop is not in stations.py
        log("Unknown stop id %s, using default" % (stop_id,))
        if stop_id != DEFAULT_STOP_ID:
            self.set_current_stop_id(DEFAULT_STOP_ID)

    @staticmethod
    def format_time(timestamp):
        # "2026-11-05T14:30:00" -> "14:30"
        if timestamp is None:
            return ""
        return timestamp[11:16] if len(timestamp) >= 16 else timestamp

    # REQ#1.2: Departure status
    @staticmethod
    def departure_status(dep):
        if "canceled" in dep and dep["canceled"]:
            return "Cancelled"
        if "delay" in dep and dep["delay"] is not None:
            if dep["delay"] >= 60:
                return "+%d min" % (dep["delay"] // 60)
        return "On time"

    def update_departure_table(self):
<<<<<<< Updated upstream
        # Uppdatera rubriken på tabellen
        title = "DEPARTURES: " + self.current_station[1].upper()
        if self.settings.current_transport != "All":
            title += " (" + self.settings.current_transport.upper() + ")"
=======
        # Table title
        title = "DEPARTURES: " + upper_sv(self.current_station[1])
        if self.current_transport != "All":
            title += " (" + self.current_transport.upper() + ")"
>>>>>>> Stashed changes
        self.lbl_dept_title.set_text(title)

        # Clear old rows
        for r in range(1, 8):
            for c in range(4):
                self.table.set_cell_value(r, c, "")

        # REQ#4.3: Wi-Fi status
        if self.wlan.isconnected():
            self.lbl_wifi.set_text("Wi-Fi: Connected to " + WIFI_SSID)
        else:
            self.lbl_wifi.set_text("Wi-Fi: Not connected")

        try:
            departures = dep_service.query_departures(
                self.current_station[0])
        except Exception as err:
            log("Failed to query departures: %r" % (err,))
            self.table.set_cell_value(1, 1, "Could not load departures")
            self.lbl_live.set_text("Live data: Failed to load")
            return

<<<<<<< Updated upstream
        # Filtrera baserat på transporttyp (REQ#3.3)
        if self.settings.current_transport != "All":
            filtered = [dep for dep in departures if dep["route"]["transport_mode"].upper() == self.settings.current_transport.upper()]
        else:
            filtered = departures
=======
        # REQ#4.3: Live data status
        self.lbl_live.set_text("Live data: OK")

        # REQ#3.3: Filter on transport type. Trafiklab calls ferries "BOAT".
        mode = self.current_transport.upper()
        if mode == "FERRY":
            mode = "BOAT"

        filtered = []
        for dep in departures:
            if mode == "ALL" or dep["route"]["transport_mode"] == mode:
                filtered.append(dep)
>>>>>>> Stashed changes

        if len(filtered) == 0:
            self.table.set_cell_value(1, 1, "No departures right now")
            return

        # Fill the table
        for row_idx, dep_data in enumerate(filtered, start=1):
            if row_idx > 7:
                break

            line = dep_data["route"]["name"]
            if line is None:
                line = dep_data["route"]["designation"]
            if line is None:
                line = ""

            dest = dep_data["route"]["destination"]["name"]

            # Use the timetable time if there is no live time
            dep_time = self.format_time(dep_data["realtime"])
            if dep_time == "":
                dep_time = self.format_time(dep_data["scheduled"])

            self.table.set_cell_value(row_idx, 0, line)
            self.table.set_cell_value(row_idx, 1, dest)
            self.table.set_cell_value(row_idx, 2, dep_time)
            self.table.set_cell_value(row_idx, 3,
                                      self.departure_status(dep_data))

    # REQ#4.1: Automatic update
    def on_refresh_timer(self, _timer):
        self.update_departure_table()

    # REQ#4.2: Manual update
    def on_refresh_clicked(self, _event):
        self.update_departure_table()

    def on_stop_changed(self, event):
        idx = event.get_target_obj().get_selected()
        if 0 <= idx < len(STATIONS):
            self.set_current_stop_id(STATIONS[idx][0])
            self.update_departure_table()

    def on_transport_changed(self, event):
        idx = event.get_target_obj().get_selected()
<<<<<<< Updated upstream
        if idx == 0:
            self.settings.current_transport = "All"
        elif idx == 1:
            self.settings.current_transport = "Bus"
        elif idx == 2:
            self.settings.current_transport = "Train"
=======
        self.current_transport = TRANSPORT_TYPES[idx]
>>>>>>> Stashed changes
        self.update_departure_table()

    def on_save_clicked(self, _event):
        self.settings.save()
        self.lbl_status.set_text("Settings saved as default!")

    # REQ#3.5: Go back to the saved settings
    def on_reset_clicked(self, _event):
<<<<<<< Updated upstream
        self.settings = UserSettings()
        self.set_current_stop_id(self.settings.current_stop_id)
        self.dd_stops.set_selected(STATIONS.index(self.current_station))
        self.dd_transport.set_selected(0)
        self.settings.save()
=======
        self.load_settings()
        self.set_current_stop_id(self.current_stop_id)
        self.dd_stops.set_selected(STATIONS.index(self.current_station))
        self.dd_transport.set_selected(
            TRANSPORT_TYPES.index(self.current_transport))
>>>>>>> Stashed changes
        self.update_departure_table()
        self.lbl_status.set_text("Default settings restored!")

    def create_ui(self):
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        # Start screen: tile (0, 0), shown at boot. Swipe down only.
        self.tile_startup = self.tileview.add_tile(0, 0, lv.DIR.BOTTOM)
        self.tile_startup.add_style(styles.screen_default, 0)

        self.lbl_title = lv.label(self.tile_startup)
        self.lbl_title.set_text("TRAFFIC SYSTEM")
        self.lbl_title.add_style(styles.text_title, 0)
        self.lbl_title.align(lv.ALIGN.TOP_MID, 0, 40)

        self.lbl_ver = lv.label(self.tile_startup)
        self.lbl_ver.set_text("Version: 0.1.1")
        self.lbl_ver.add_style(styles.text_sub_title, 0)
        self.lbl_ver.align(lv.ALIGN.TOP_MID, 0, 85)

        self.lbl_group = lv.label(self.tile_startup)
        self.lbl_group.set_text("Group 1")
        self.lbl_group.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.lbl_group.set_style_text_font(lv.font_montserrat_28, 0)
        self.lbl_group.align(lv.ALIGN.CENTER, 0, -20)

        self.lbl_members = lv.label(self.tile_startup)
        self.lbl_members.set_text(
            "Members: Ragnar, Anton, Filip, Axel, Jonathan")
        self.lbl_members.set_style_text_color(lv.color_hex(0xDDDDDD), 0)
        self.lbl_members.align(lv.ALIGN.BOTTOM_MID, 0, -40)

        # Departures: tile (0, 1). Swipe up to start, right to settings.
        self.tile_main = self.tileview.add_tile(
            0, 1, lv.DIR.TOP | lv.DIR.RIGHT)
        self.tile_main.add_style(styles.screen_default, 0)
        self.lbl_dept_title = lv.label(self.tile_main)
        self.lbl_dept_title.set_text("DEPARTURES")
        self.lbl_dept_title.add_style(styles.text_title, 0)
        self.lbl_dept_title.align(lv.ALIGN.TOP_MID, 0, 15)

        self.table = lv.table(self.tile_main)
        self.table.set_size(540, 340)
        self.table.align(lv.ALIGN.TOP_MID, 0, 50)
        self.table.set_style_bg_color(lv.color_hex(0x1E1E1E), 0)
        self.table.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.table.set_style_border_width(1, 0)
        self.table.set_style_border_color(lv.color_hex(0x333333), 0)

        self.table.set_column_count(4)
        self.table.set_column_width(0, 80)
        self.table.set_column_width(1, 270)
        self.table.set_column_width(2, 80)
        self.table.set_column_width(3, 110)

        self.table.set_cell_value(0, 0, "Linje")
        self.table.set_cell_value(0, 1, "Destination")
        self.table.set_cell_value(0, 2, "Tid")
        self.table.set_cell_value(0, 3, "Status")

        # REQ#4.2: Refresh button
        self.btn_refresh = lv.button(self.tile_main)
        self.btn_refresh.set_size(120, 40)
        self.btn_refresh.align(lv.ALIGN.BOTTOM_RIGHT, -30, -5)
        self.btn_refresh.add_event_cb(self.on_refresh_clicked,
                                      lv.EVENT.CLICKED, None)

        self.lbl_btn_refresh = lv.label(self.btn_refresh)
        self.lbl_btn_refresh.set_text("Refresh")
        self.lbl_btn_refresh.center()

        # NF3: Trafiklab requires credit for its data (CC BY 4.0)
        self.lbl_attribution = lv.label(self.tile_main)
        self.lbl_attribution.set_text("Data from Trafiklab.se (CC BY 4.0)")
        self.lbl_attribution.add_style(styles.text_sub_title, 0)
        self.lbl_attribution.align(lv.ALIGN.BOTTOM_LEFT, 30, -15)

        # Settings: tile (1, 1). Swipe left to go back.
        self.tile_settings = self.tileview.add_tile(1, 1, lv.DIR.LEFT)
        self.tile_settings.add_style(styles.screen_default, 0)

        self.lbl_settings_title = lv.label(self.tile_settings)
        self.lbl_settings_title.set_text("SETTINGS")
        self.lbl_settings_title.add_style(styles.text_title, 0)
        self.lbl_settings_title.align(lv.ALIGN.TOP_MID, 0, 15)

        # REQ#3.2: Stop dropdown
        self.lbl_stop = lv.label(self.tile_settings)
        self.lbl_stop.set_text("Departure Stop:")
        self.lbl_stop.add_style(styles.text, 0)
        self.lbl_stop.align(lv.ALIGN.TOP_LEFT, 50, 65)

        self.dd_stops = lv.dropdown(self.tile_settings)
        self.dd_stops.set_options(
            "\n".join([station[1] for station in STATIONS]))
        # The open list needs its own font to show å, ä and ö
        self.dd_stops.get_list().set_style_text_font(styles.font_normal, 0)
        self.dd_stops.set_size(220, 40)
        self.dd_stops.align(lv.ALIGN.TOP_LEFT, 50, 90)
        self.dd_stops.set_selected(STATIONS.index(self.current_station))
        self.dd_stops.add_event_cb(self.on_stop_changed,
                                   lv.EVENT.VALUE_CHANGED, None)

        # REQ#3.3: Transport type dropdown
        self.lbl_transport = lv.label(self.tile_settings)
        self.lbl_transport.set_text("Transport Type:")
        self.lbl_transport.add_style(styles.text, 0)
        self.lbl_transport.align(lv.ALIGN.TOP_RIGHT, -120, 65)

        self.dd_transport = lv.dropdown(self.tile_settings)
        self.dd_transport.set_options("\n".join(TRANSPORT_TYPES))
        self.dd_transport.set_size(220, 40)
        self.dd_transport.align(lv.ALIGN.TOP_RIGHT, -50, 90)
<<<<<<< Updated upstream
        if self.settings.current_transport == "Bus":
            self.dd_transport.set_selected(1)
        elif self.settings.current_transport == "Train":
            self.dd_transport.set_selected(2)
        self.dd_transport.add_event_cb(self.on_transport_changed, lv.EVENT.VALUE_CHANGED, None)
=======
        self.dd_transport.set_selected(
            TRANSPORT_TYPES.index(self.current_transport))
        self.dd_transport.add_event_cb(self.on_transport_changed,
                                       lv.EVENT.VALUE_CHANGED, None)
>>>>>>> Stashed changes

        # REQ#3.4: Save button
        self.btn_save = lv.button(self.tile_settings)
        self.btn_save.set_size(220, 45)
        self.btn_save.align(lv.ALIGN.TOP_LEFT, 50, 160)
        self.btn_save.set_style_bg_color(lv.color_hex(0x008800), 0)
        self.btn_save.add_event_cb(self.on_save_clicked,
                                   lv.EVENT.CLICKED, None)

        self.lbl_btn_save = lv.label(self.btn_save)
        self.lbl_btn_save.set_text("Save Default")
        self.lbl_btn_save.center()

        # REQ#3.5: Reset button
        self.btn_reset = lv.button(self.tile_settings)
        self.btn_reset.set_size(220, 45)
        self.btn_reset.align(lv.ALIGN.TOP_RIGHT, -50, 160)
        self.btn_reset.set_style_bg_color(lv.color_hex(0x880000), 0)
        self.btn_reset.add_event_cb(self.on_reset_clicked,
                                    lv.EVENT.CLICKED, None)

        self.lbl_btn_reset = lv.label(self.btn_reset)
        self.lbl_btn_reset.set_text("Reset to Default")
        self.lbl_btn_reset.center()

        # REQ#4.3: Wi-Fi and live data status
        self.lbl_wifi = lv.label(self.tile_settings)
        self.lbl_wifi.add_style(styles.text, 0)
        self.lbl_wifi.align(lv.ALIGN.TOP_LEFT, 50, 240)

        self.lbl_live = lv.label(self.tile_settings)
        self.lbl_live.add_style(styles.text, 0)
        self.lbl_live.align(lv.ALIGN.TOP_LEFT, 50, 270)

        # Message after Save or Reset
        self.lbl_status = lv.label(self.tile_settings)
        self.lbl_status.set_text("")
        self.lbl_status.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_status.align(lv.ALIGN.BOTTOM_MID, 0, -30)

        # REQ#4.1: Update now and then every 60 seconds
        self.update_departure_table()
        self.refresh_timer = lv.timer_create(self.on_refresh_timer,
                                             60_000, None)

    def connect_wifi(self):
        log("connecting to Wi-Fi SSID: " + WIFI_SSID)
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        # Wait at most 15 seconds
        started = time.ticks_ms()
        while (not self.wlan.isconnected()
               and time.ticks_diff(time.ticks_ms(), started) < 15_000):
            time.sleep_ms(250)

        if self.wlan.isconnected():
            log("Wi-Fi connected")
        else:
            log("Wi-Fi could not connect (timeout)")


try:
    app = Application()
except Exception as error:
    log("FATAL: %r" % (error,))
    sys.print_exception(error)
    raise
