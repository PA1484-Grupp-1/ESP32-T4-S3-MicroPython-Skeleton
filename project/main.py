import json
import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets import WIFI_SSID, WIFI_PASSWORD

SETTINGS_FILE = "settings.json"
FACTORY_STOP = "Campus Grasvik"
FACTORY_TRANSPORT = "All"

# Lista med alla 7 hållplatser i poolen (REQ#1.2 och REQ#3.2)
AVAILABLE_STOPS = [
    "Campus Grasvik",
    "Karlskrona C",
    "Kungsmarken",
    "Ronneby Station",
    "Bastasjo",
    "Nattraby centrum",
    "Emmaboda Station"
]


class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()

        # Fabriksinställningar
        self.current_stop = FACTORY_STOP
        self.current_transport = FACTORY_TRANSPORT

        # REQ#3.4: Läs in sparade standardinställningar vid boot
        self.load_settings()

        # Demo-data för alla 7 hållplatser i poolen (REQ#1.2 och REQ#3.2)
        self.stop_data = {
            "Campus Grasvik": [
                ("Buss 1", "Kungsmarken", "2 min"),
                ("Buss 5", "Karlskrona C", "6 min"),
                ("Buss 1", "Lyckeby", "12 min"),
                ("Buss 7", "Nattraby centrum", "15 min"),
                ("Buss 2", "Ronneby Station", "21 min"),
                ("Buss 1", "Bastasjo", "27 min"),
                ("Buss 5", "Bergasa station", "34 min")
            ],
            "Karlskrona C": [
                ("Tag 10", "Kopenhamn H", "4 min"),
                ("Buss 1", "Campus Grasvik", "7 min"),
                ("Tag 85", "Emmaboda Station", "11 min"),
                ("Buss 3", "Bastasjo", "16 min"),
                ("Tag 10", "Malmo C", "22 min"),
                ("Buss 2", "Ronneby Station", "28 min"),
                ("Tag 85", "Alvesta Station", "35 min")
            ],
            "Kungsmarken": [
                ("Buss 1", "Campus Grasvik", "3 min"),
                ("Buss 1", "Karlskrona C", "9 min"),
                ("Buss 5", "Ronneby Station", "16 min"),
                ("Buss 7", "Bastasjo", "22 min"),
                ("Buss 1", "Lyckeby", "28 min"),
                ("Buss 2", "Bergasa station", "33 min"),
                ("Buss 7", "Nattraby centrum", "41 min")
            ],
            "Ronneby Station": [
                ("Tag 10", "Karlskrona C", "5 min"),
                ("Tag 10", "Malmo C", "14 min"),
                ("Buss 2", "Campus Grasvik", "19 min"),
                ("Buss 2", "Kungsmarken", "25 min"),
                ("Tag 85", "Emmaboda Station", "31 min"),
                ("Buss 7", "Nattraby centrum", "38 min"),
                ("Tag 10", "Kopenhamn H", "46 min")
            ],
            "Bastasjo": [
                ("Buss 1", "Campus Grasvik", "4 min"),
                ("Buss 3", "Karlskrona C", "10 min"),
                ("Buss 1", "Kungsmarken", "18 min"),
                ("Buss 7", "Ronneby Station", "24 min"),
                ("Buss 3", "Bergasa station", "30 min"),
                ("Buss 1", "Lyckeby", "37 min"),
                ("Buss 7", "Nattraby centrum", "44 min")
            ],
            "Nattraby centrum": [
                ("Buss 7", "Karlskrona C", "6 min"),
                ("Buss 7", "Campus Grasvik", "13 min"),
                ("Buss 2", "Ronneby Station", "20 min"),
                ("Buss 7", "Kungsmarken", "27 min"),
                ("Buss 1", "Bastasjo", "33 min"),
                ("Tag 10", "Malmo C", "42 min"),
                ("Tag 85", "Emmaboda Station", "50 min")
            ],
            "Emmaboda Station": [
                ("Tag 85", "Karlskrona C", "2 min"),
                ("Tag 85", "Alvesta Station", "12 min"),
                ("Tag 85", "Kalmar C", "20 min"),
                ("Tag 10", "Malmo C", "33 min"),
                ("Buss 2", "Ronneby Station", "40 min"),
                ("Buss 1", "Campus Grasvik", "48 min"),
                ("Tag 10", "Kopenhamn H", "57 min")
            ]
        }

        self.create_ui()

        log("student application ready - starting at startup tile (0, 0)")

    #Inställningshantering (REQ#3.4 och REQ#3.5)
    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                saved_stop = data.get("stop", FACTORY_STOP)
                self.current_stop = saved_stop if saved_stop in AVAILABLE_STOPS else FACTORY_STOP
                self.current_transport = data.get("transport", FACTORY_TRANSPORT)
                log("Settings loaded from flash")
        except Exception:
            self.current_stop = FACTORY_STOP
            self.current_transport = FACTORY_TRANSPORT
            log("No settings found, using factory default")

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({"stop": self.current_stop, "transport": self.current_transport}, f)
            log("Settings saved to flash")
        except Exception as err:
            log("Failed to save settings: %r" % (err,))

    def update_departure_table(self):
        # Uppdatera rubriken på tabellen
        title = "DEPARTURES: " + self.current_stop.upper()
        if self.current_transport != "All":
            title += " (" + self.current_transport.upper() + ")"
        self.lbl_dept_title.set_text(title)

        departures = self.stop_data.get(self.current_stop, [])

        # Filtrera baserat på transporttyp (REQ#3.3)
        if self.current_transport != "All":
            filtered = [row for row in departures if row[0].startswith(self.current_transport)]
        else:
            filtered = departures

        # Rensa gamla rader
        for r in range(1, 8):
            self.table.set_cell_value(r, 0, "")
            self.table.set_cell_value(r, 1, "")
            self.table.set_cell_value(r, 2, "")

        # Fyll tabellen med de filtrerade avgångarna
        for row_idx, (line, dest, dep_time) in enumerate(filtered, start=1):
            if row_idx > 7:
                break
            self.table.set_cell_value(row_idx, 0, line)
            self.table.set_cell_value(row_idx, 1, dest)
            self.table.set_cell_value(row_idx, 2, dep_time)

    def on_stop_changed(self, event):
        idx = event.get_target_obj().get_selected()
        if 0 <= idx < len(AVAILABLE_STOPS):
            self.current_stop = AVAILABLE_STOPS[idx]
            self.update_departure_table()

    def on_transport_changed(self, event):
        idx = event.get_target_obj().get_selected()
        if idx == 0:
            self.current_transport = "All"
        elif idx == 1:
            self.current_transport = "Buss"
        elif idx == 2:
            self.current_transport = "Tag"
        self.update_departure_table()

    def on_save_clicked(self, _event):
        self.save_settings()
        self.lbl_status.set_text("Settings saved as default!")

    def on_reset_clicked(self, _event):
        self.current_stop = FACTORY_STOP
        self.current_transport = FACTORY_TRANSPORT
        self.dd_stops.set_selected(AVAILABLE_STOPS.index(FACTORY_STOP))
        self.dd_transport.set_selected(0)
        self.save_settings()
        self.update_departure_table()
        self.lbl_status.set_text("Factory defaults restored!")

    def create_ui(self):
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        # Startskärm: Tile (0, 0) - Startar alltid här vid boot
        # Tillåter enbart svep nedåt till Huvudskärm
        self.tile_startup = self.tileview.add_tile(0, 0, lv.DIR.BOTTOM)
        self.tile_startup.set_style_bg_color(lv.color_hex(0x000000), 0)
        self.tile_startup.set_style_bg_opa(lv.OPA.COVER, 0)

        self.lbl_title = lv.label(self.tile_startup)
        self.lbl_title.set_text("TRAFFIC SYSTEM")
        self.lbl_title.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_title.set_style_text_font(lv.font_montserrat_28, 0)
        self.lbl_title.align(lv.ALIGN.TOP_MID, 0, 40)

        self.lbl_ver = lv.label(self.tile_startup)
        self.lbl_ver.set_text("Version: 0.1.1")
        self.lbl_ver.set_style_text_color(lv.color_hex(0x888888), 0)
        self.lbl_ver.align(lv.ALIGN.TOP_MID, 0, 85)

        self.lbl_group = lv.label(self.tile_startup)
        self.lbl_group.set_text("Grupp 1")
        self.lbl_group.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.lbl_group.set_style_text_font(lv.font_montserrat_28, 0)
        self.lbl_group.align(lv.ALIGN.CENTER, 0, -20)

        self.lbl_members = lv.label(self.tile_startup)
        self.lbl_members.set_text("Medlemmar: Ragnar, Anton, Filip, Axel, Jonathan")
        self.lbl_members.set_style_text_color(lv.color_hex(0xDDDDDD), 0)
        self.lbl_members.align(lv.ALIGN.BOTTOM_MID, 0, -40)

        # Huvudskärm: Tile (0, 1) - Demotabell för kollektivtrafik
        # Tillåter svep uppåt (Start) och höger (Inställningar)
        self.tile_main = self.tileview.add_tile(0, 1, lv.DIR.TOP | lv.DIR.RIGHT)
        self.tile_main.set_style_bg_color(lv.color_hex(0x101010), 0)
        self.tile_main.set_style_bg_opa(lv.OPA.COVER, 0)

        self.lbl_dept_title = lv.label(self.tile_main)
        self.lbl_dept_title.set_text("DEPARTURES")
        self.lbl_dept_title.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_dept_title.set_style_text_font(lv.font_montserrat_20, 0)
        self.lbl_dept_title.align(lv.ALIGN.TOP_MID, 0, 15)

        self.table = lv.table(self.tile_main)
        self.table.set_size(540, 360)
        self.table.align(lv.ALIGN.TOP_MID, 0, 50)
        self.table.set_style_bg_color(lv.color_hex(0x1E1E1E), 0)
        self.table.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.table.set_style_border_width(1, 0)
        self.table.set_style_border_color(lv.color_hex(0x333333), 0)

        self.table.set_column_width(0, 90)
        self.table.set_column_width(1, 350)
        self.table.set_column_width(2, 100)

        self.table.set_cell_value(0, 0, "Linje")
        self.table.set_cell_value(0, 1, "Destination")
        self.table.set_cell_value(0, 2, "Tid")

        self.update_departure_table()

        # Inställningar: Tile (1, 1) - REQ#3.1 till REQ#3.5
        # Till höger om Huvudskärm, svep vänster tillbaka
        self.tile_settings = self.tileview.add_tile(1, 1, lv.DIR.LEFT)
        self.tile_settings.set_style_bg_color(lv.color_hex(0x181818), 0)
        self.tile_settings.set_style_bg_opa(lv.OPA.COVER, 0)

        self.lbl_settings_title = lv.label(self.tile_settings)
        self.lbl_settings_title.set_text("SETTINGS")
        self.lbl_settings_title.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_settings_title.set_style_text_font(lv.font_montserrat_28, 0)
        self.lbl_settings_title.align(lv.ALIGN.TOP_MID, 0, 15)

        # REQ#3.2: Dropdown med alla 7 hållplatser
        self.lbl_stop = lv.label(self.tile_settings)
        self.lbl_stop.set_text("Departure Stop:")
        self.lbl_stop.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.lbl_stop.align(lv.ALIGN.TOP_LEFT, 50, 65)

        self.dd_stops = lv.dropdown(self.tile_settings)
        self.dd_stops.set_options("\n".join(AVAILABLE_STOPS))
        self.dd_stops.set_size(220, 40)
        self.dd_stops.align(lv.ALIGN.TOP_LEFT, 50, 90)
        if self.current_stop in AVAILABLE_STOPS:
            self.dd_stops.set_selected(AVAILABLE_STOPS.index(self.current_stop))
        self.dd_stops.add_event_cb(self.on_stop_changed, lv.EVENT.VALUE_CHANGED, None)

        # REQ#3.3: Dropdown för transporttyp
        self.lbl_transport = lv.label(self.tile_settings)
        self.lbl_transport.set_text("Transport Type:")
        self.lbl_transport.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.lbl_transport.align(lv.ALIGN.TOP_RIGHT, -120, 65)

        self.dd_transport = lv.dropdown(self.tile_settings)
        self.dd_transport.set_options("All\nBuss\nTag")
        self.dd_transport.set_size(220, 40)
        self.dd_transport.align(lv.ALIGN.TOP_RIGHT, -50, 90)
        if self.current_transport == "Buss":
            self.dd_transport.set_selected(1)
        elif self.current_transport == "Tag":
            self.dd_transport.set_selected(2)
        self.dd_transport.add_event_cb(self.on_transport_changed, lv.EVENT.VALUE_CHANGED, None)

        # REQ#3.4: Spara som standardknapp
        self.btn_save = lv.button(self.tile_settings)
        self.btn_save.set_size(220, 45)
        self.btn_save.align(lv.ALIGN.TOP_LEFT, 50, 160)
        self.btn_save.set_style_bg_color(lv.color_hex(0x008800), 0)
        self.btn_save.add_event_cb(self.on_save_clicked, lv.EVENT.CLICKED, None)

        self.lbl_btn_save = lv.label(self.btn_save)
        self.lbl_btn_save.set_text("Save Default")
        self.lbl_btn_save.center()

        # REQ#3.5: Återställ till fabriksinställningar-knapp
        self.btn_reset = lv.button(self.tile_settings)
        self.btn_reset.set_size(220, 45)
        self.btn_reset.align(lv.ALIGN.TOP_RIGHT, -50, 160)
        self.btn_reset.set_style_bg_color(lv.color_hex(0x880000), 0)
        self.btn_reset.add_event_cb(self.on_reset_clicked, lv.EVENT.CLICKED, None)

        self.lbl_btn_reset = lv.label(self.btn_reset)
        self.lbl_btn_reset.set_text("Factory Reset")
        self.lbl_btn_reset.center()

        # Statusmeddelande
        self.lbl_status = lv.label(self.tile_settings)
        self.lbl_status.set_text("")
        self.lbl_status.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_status.align(lv.ALIGN.BOTTOM_MID, 0, -30)

    @staticmethod
    def connect_wifi():
        log("connecting to Wi-Fi SSID: " + WIFI_SSID)
        station = network.WLAN(network.STA_IF)
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