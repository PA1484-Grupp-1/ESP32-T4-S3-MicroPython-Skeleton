import json
import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets_env import WIFI_SSID, WIFI_PASSWORD

import styles
import departure_list
import departures_service as dep_service
from stations import stations

# Settings file and factory defaults (REQ#3.4, REQ#3.5)
SETTINGS_FILE = "settings.json"
DEFAULT_STOP_ID = "740032188"  # Campus Gräsvik Id
DEFAULT_TRANSPORT = "All"
REFRESH_INTERVAL_MS = 60_000  # REQ#4.1

# Dropdown name and the matching Trafiklab transport_mode (REQ#3.3)
TRANSPORT_MODES = (("All", None), ("Bus", "BUS"), ("Train", "TRAIN"), ("Ferry", "BOAT"))

# stations.py is the complete pool of selectable stops: [id, name] (REQ#3.2)
STATIONS = sorted(stations, key=lambda s: s[1])


# MicroPython's str.upper() only converts ASCII letters (REQ#1.2)
def upper_sv(text):
    for lower, upper in (("å", "Å"), ("ä", "Ä"), ("ö", "Ö"), ("é", "É"),
                         ("ü", "Ü"), ("æ", "Æ"), ("ø", "Ø")):
        text = text.replace(lower, upper)
    return text.upper()


# Dropdown position of a transport type (REQ#3.3)
def transport_index(name):
    for index, mode in enumerate(TRANSPORT_MODES):
        if mode[0] == name:
            return index
    return 0


# "2026-11-05T14:30:00" -> "14:30" (REQ#1.2)
def format_time(timestamp):
    if timestamp is None:
        return ""
    return timestamp[11:16] if len(timestamp) >= 16 else timestamp


# Departure status column (REQ#1.2)
def departure_status(departure):
    if departure.get("canceled"):
        return "Cancelled"
    if not departure.get("is_realtime"):
        return "Scheduled"

    delay = departure.get("delay") or 0
    if delay >= 60:
        return "+%d min" % (delay // 60)
    if delay <= -60:
        return "-%d min" % (-delay // 60)
    return "On time"


# Owns the screens, the settings and the live data
class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()
        styles.init_fonts()

        self.current_stop_id = DEFAULT_STOP_ID
        self.current_station = None
        self.current_transport = DEFAULT_TRANSPORT
        self.last_update = None
        self.refresh_timer = None

        # REQ#3.4: Restore saved settings at boot
        self.load_settings()

        log("Connecting to Wifi..")
        self.connect_wifi()

        self.set_current_stop_id(self.current_stop_id)

        self.create_ui()

        log("student application ready - starting at startup tile (0, 0)")

    # Read the saved settings, or factory defaults (REQ#3.4, REQ#3.5)
    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                self.current_stop_id = data.get("stop", DEFAULT_STOP_ID)
                self.current_transport = data.get("transport", DEFAULT_TRANSPORT)
                log("Settings loaded from flash")
        except Exception:
            self.current_stop_id = DEFAULT_STOP_ID
            self.current_transport = DEFAULT_TRANSPORT
            log("No settings found, using factory default")

    # REQ#3.4: Save the current settings as default
    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({"stop": self.current_stop_id, "transport": self.current_transport}, f)
            log("Settings saved to flash")
        except Exception as err:
            log("Failed to save settings: %r" % (err,))

    # REQ#3.2: Select a stop from stations.py
    def set_current_stop_id(self, stop_id):
        for station in STATIONS:
            if station[0] == stop_id:
                self.current_station = station
                self.current_stop_id = stop_id
                return

        # Saved stop is not in stations.py
        log("Unknown stop id %s, using default" % (stop_id,))
        if stop_id != DEFAULT_STOP_ID:
            self.set_current_stop_id(DEFAULT_STOP_ID)

    # REQ#1.2: Fetch and show live departures for the selected stop
    def update_departure_table(self):
        title = "DEPARTURES: " + upper_sv(self.current_station[1])
        if self.current_transport != "All":
            title += " (" + self.current_transport.upper() + ")"
        self.lbl_dept_title.set_text(title)

        # REQ#4.1: Every fetch restarts the 60 second countdown
        self.refresh_timer.reset()

        try:
            response = dep_service.query_departures(self.current_station[0])
            departures = response["departures"]
        except Exception as err:
            log("Failed to query departures: %r" % (err,))
            self.board.show_message("Could not load departures")
            self.update_status(False)
            return

        self.last_update = format_time(response.get("timestamp"))
        self.update_status(True)

        # REQ#3.3: Filter on transport type
        mode = TRANSPORT_MODES[transport_index(self.current_transport)][1]
        if mode is not None:
            filtered = [dep for dep in departures
                        if dep["route"]["transport_mode"].upper() == mode]
        else:
            filtered = departures

        if len(filtered) == 0:
            self.board.show_message("No departures right now")
            return

        # The API sorts by scheduled time, but the board shows the real time
        filtered = sorted(filtered, key=lambda dep: dep["realtime"] or "")

        rows = []
        for dep_data in filtered[:departure_list.ROW_COUNT]:
            route = dep_data["route"]
            rows.append((
                format_time(dep_data["realtime"]),
                route["name"] or route["designation"] or "",
                route["destination"]["name"],
                departure_status(dep_data),
                route["transport_mode"],
            ))
        self.board.show_departures(rows)

    # REQ#4.3: Wi-Fi and live data status on the settings screen
    def update_status(self, data_ok):
        if self.station.isconnected():
            self.lbl_wifi.set_text("Wi-Fi: Connected to " + WIFI_SSID)
        else:
            self.lbl_wifi.set_text("Wi-Fi: Not connected")

        if data_ok:
            self.lbl_live.set_text("Live data: Updated " + self.last_update)
        elif self.last_update is None:
            self.lbl_live.set_text("Live data: Unavailable")
        else:
            self.lbl_live.set_text("Live data: Failed, last update " + self.last_update)

    # REQ#4.1: Automatic update
    def on_refresh_timer(self, _timer):
        try:
            self.update_departure_table()
        except Exception as err:
            log("Automatic refresh failed: %r" % (err,))

    # REQ#4.2: Manual refresh
    def on_refresh_clicked(self, _event):
        self.update_departure_table()

    # REQ#3.2: Show the stop chosen in the dropdown
    def on_stop_changed(self, event):
        idx = event.get_target_obj().get_selected()
        if 0 <= idx < len(STATIONS):
            self.set_current_stop_id(STATIONS[idx][0])
            self.update_departure_table()

    # REQ#3.3: Apply the transport type chosen in the dropdown
    def on_transport_changed(self, event):
        idx = event.get_target_obj().get_selected()
        if 0 <= idx < len(TRANSPORT_MODES):
            self.current_transport = TRANSPORT_MODES[idx][0]
            self.update_departure_table()

    # REQ#3.4: Save Default button
    def on_save_clicked(self, _event):
        self.save_settings()
        self.lbl_status.set_text("Settings saved as default!")

    # REQ#3.5: Go back to the saved defaults, or factory defaults if none are saved
    def on_reset_clicked(self, _event):
        self.load_settings()
        self.set_current_stop_id(self.current_stop_id)
        self.dd_stops.set_selected(STATIONS.index(self.current_station))
        self.dd_transport.set_selected(transport_index(self.current_transport))
        self.update_departure_table()
        self.lbl_status.set_text("Default settings restored!")

    # Builds the three screens, which the user swipes between (REQ#2.1)
    def create_ui(self):
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        # REQ#1.1: Startup tile (0, 0), shown at boot
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
        self.lbl_members.set_text("Members: Ragnar, Anton, Filip, Axel, Jonathan")
        self.lbl_members.set_style_text_color(lv.color_hex(0xDDDDDD), 0)
        self.lbl_members.align(lv.ALIGN.BOTTOM_MID, 0, -40)

        # REQ#1.2: Departures tile (0, 1)
        self.tile_main = self.tileview.add_tile(0, 1, lv.DIR.TOP | lv.DIR.RIGHT)
        self.tile_main.add_style(styles.screen_default, 0)
        self.lbl_dept_title = lv.label(self.tile_main)
        self.lbl_dept_title.set_width(departure_list.BOARD_WIDTH)
        self.lbl_dept_title.set_long_mode(lv.label.LONG_MODE.SCROLL_CIRCULAR)
        self.lbl_dept_title.set_text("DEPARTURES")
        self.lbl_dept_title.add_style(styles.text_title, 0)
        self.lbl_dept_title.set_pos(departure_list.BOARD_X, 12)

        self.board = departure_list.DepartureBoard(self.tile_main)

        # REQ#4.2: Manuell uppdatering
        self.btn_refresh = lv.button(self.tile_main)
        self.btn_refresh.set_size(130, 44)
        self.btn_refresh.align(lv.ALIGN.BOTTOM_RIGHT, -20, -10)
        styles.style_button(self.btn_refresh, styles.COLOR_ACCENT)
        self.btn_refresh.add_event_cb(self.on_refresh_clicked, lv.EVENT.CLICKED, None)

        self.lbl_btn_refresh = lv.label(self.btn_refresh)
        self.lbl_btn_refresh.set_text("Refresh")
        self.lbl_btn_refresh.center()

        # NF3: Attribution required by the Trafiklab CC BY 4.0 licence
        self.lbl_attribution = lv.label(self.tile_main)
        self.lbl_attribution.set_text("Data from Trafiklab.se (CC BY 4.0)")
        self.lbl_attribution.add_style(styles.text_sub_title, 0)
        self.lbl_attribution.align(lv.ALIGN.BOTTOM_LEFT, 20, -24)

        # REQ#3.1: Settings tile (1, 1)
        self.tile_settings = self.tileview.add_tile(1, 1, lv.DIR.LEFT)
        self.tile_settings.add_style(styles.screen_default, 0)

        self.lbl_settings_title = lv.label(self.tile_settings)
        self.lbl_settings_title.set_text("SETTINGS")
        self.lbl_settings_title.add_style(styles.text_title, 0)
        self.lbl_settings_title.align(lv.ALIGN.TOP_MID, 0, 15)

        # REQ#3.2: Stop dropdown
        self.lbl_stop = lv.label(self.tile_settings)
        self.lbl_stop.set_text("Departure Stop:")
        self.lbl_stop.add_style(styles.text_sub_title, 0)
        self.lbl_stop.set_pos(30, 60)

        self.dd_stops = lv.dropdown(self.tile_settings)
        self.dd_stops.set_options("\n".join([station[1] for station in STATIONS]))
        self.dd_stops.set_size(340, 44)
        self.dd_stops.set_pos(30, 82)
        styles.style_dropdown(self.dd_stops)
        self.dd_stops.set_selected(STATIONS.index(self.current_station))
        self.dd_stops.add_event_cb(self.on_stop_changed, lv.EVENT.VALUE_CHANGED, None)

        # REQ#3.3: Transport type dropdown
        self.lbl_transport = lv.label(self.tile_settings)
        self.lbl_transport.set_text("Transport Type:")
        self.lbl_transport.add_style(styles.text_sub_title, 0)
        self.lbl_transport.set_pos(390, 60)

        self.dd_transport = lv.dropdown(self.tile_settings)
        self.dd_transport.set_options("\n".join([mode[0] for mode in TRANSPORT_MODES]))
        self.dd_transport.set_size(180, 44)
        self.dd_transport.set_pos(390, 82)
        styles.style_dropdown(self.dd_transport)
        self.dd_transport.set_selected(transport_index(self.current_transport))
        self.dd_transport.add_event_cb(self.on_transport_changed, lv.EVENT.VALUE_CHANGED, None)

        # REQ#3.4: Save button
        self.btn_save = lv.button(self.tile_settings)
        self.btn_save.set_size(265, 46)
        self.btn_save.set_pos(30, 144)
        styles.style_button(self.btn_save, styles.COLOR_ACCENT)
        self.btn_save.add_event_cb(self.on_save_clicked, lv.EVENT.CLICKED, None)

        self.lbl_btn_save = lv.label(self.btn_save)
        self.lbl_btn_save.set_text("Save Default")
        self.lbl_btn_save.center()

        # REQ#3.5: Reset button
        self.btn_reset = lv.button(self.tile_settings)
        self.btn_reset.set_size(265, 46)
        self.btn_reset.set_pos(305, 144)
        styles.style_button(self.btn_reset, styles.COLOR_DANGER)
        self.btn_reset.add_event_cb(self.on_reset_clicked, lv.EVENT.CLICKED, None)

        self.lbl_btn_reset = lv.label(self.btn_reset)
        self.lbl_btn_reset.set_text("Reset to Default")
        self.lbl_btn_reset.center()

        # REQ#4.3: Status panel
        self.panel_status = departure_list.new_box(self.tile_settings, 30, 208, 540, 84,
                                                   styles.COLOR_PANEL)

        self.lbl_wifi = lv.label(self.panel_status)
        self.lbl_wifi.set_style_text_font(styles.font_row, 0)
        self.lbl_wifi.add_style(styles.text, 0)
        self.lbl_wifi.set_pos(16, 16)

        self.lbl_live = lv.label(self.panel_status)
        self.lbl_live.set_style_text_font(styles.font_row, 0)
        self.lbl_live.add_style(styles.text, 0)
        self.lbl_live.set_pos(16, 46)

        self.lbl_status = lv.label(self.tile_settings)
        self.lbl_status.set_text("")
        self.lbl_status.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_status.set_width(540)
        self.lbl_status.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.lbl_status.set_pos(30, 312)

        # REQ#4.1: Start the automatic update. The first fetch runs here, once all widgets exist
        self.refresh_timer = lv.timer_create(self.on_refresh_timer, REFRESH_INTERVAL_MS, None)
        self.update_departure_table()

    # Connect at boot and give up after 15 seconds (REQ#4.3)
    def connect_wifi(self):
        log("connecting to Wi-Fi SSID: " + WIFI_SSID)
        station = network.WLAN(network.STA_IF)
        self.station = station
        station.active(True)
        station.connect(WIFI_SSID, WIFI_PASSWORD)
        started = time.ticks_ms()
        while not station.isconnected() and time.ticks_diff(time.ticks_ms(), started) < 15_000:
            time.sleep_ms(250)
        log("Wi-Fi connected" if station.isconnected() else "Wi-Fi could not connect (timeout)")


try:
    app = Application()
except Exception as error:
    log("FATAL: %r" % (error,))
    sys.print_exception(error)
    raise
