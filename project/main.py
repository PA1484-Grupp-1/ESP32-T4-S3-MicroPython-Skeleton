import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets_env import WIFI_SSID, WIFI_PASSWORD

import fonts
import styles
import departures_service as dep_service
from custom_keyboard import custom_keyboard
from search_area import SearchArea
from user_settings import UserSettings, DEFAULT_STOP_ID
from stations import stations
from format_helpers import upper, fit

# US3.2B: All selectable stops, sorted by name
STATIONS = sorted(stations, key=lambda s: s[1])

REFRESH_INTERVAL_MS = 60_000  # US4.1


# Logs errors in callbacks instead of crashing the app
def safe(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except Exception as err:
            log("Error: %r" % (err,))
    return wrapper


class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()

        # US3.4: Load the saved settings at startup
        self.settings = UserSettings.reload()
        self.current_station = None

        log("Connecting to Wifi..")
        self.connect_wifi()

        self.set_current_stop_id(self.settings.current_stop_id)

        self.create_ui()

        # US4.1: Update the departures automatically
        self.refresh_timer = lv.timer_create(
            lambda _t: self.update_departure_table(),
            REFRESH_INTERVAL_MS, None)

        log("student application ready - starting at startup tile (0, 0)")

    def set_current_stop_id(self, stop_id):
        for station in STATIONS:
            if station[0] == stop_id:
                self.current_station = station
                self.settings.current_stop_id = stop_id
                return

        # The saved stop is not in stations.py
        log("Unknown stop id %s, using default" % (stop_id,))
        if stop_id != DEFAULT_STOP_ID:
            self.set_current_stop_id(DEFAULT_STOP_ID)

    @staticmethod
    def format_time(timestamp):
        if timestamp is None:
            return ""
        return timestamp[11:16] if len(timestamp) >= 16 else timestamp

    # US1.2B: Departure status, Trafiklab gives the delay in seconds
    @staticmethod
    def format_status(dep_data):
        if dep_data.get("canceled"):
            return "Cancelled"
        delay_min = (dep_data.get("delay") or 0) // 60
        return "+%d min" % delay_min if delay_min > 0 else "On time"

    # US1.2B: Live departures from Trafiklab for the selected stop
    @safe
    def update_departure_table(self):
        self.lbl_dept_title.set_text(upper(self.current_station[1]))
        transport = self.settings.current_transport
        if transport == "All":
            transport = "All transport"
        self.lbl_dept_subtitle.set_text("Departures · " + transport)

        for r in range(1, 8):
            self.table.set_cell_value(r, 0, "")
            self.table.set_cell_value(r, 1, "")
            self.table.set_cell_value(r, 2, "")
            self.table.set_cell_value(r, 3, "")

        self.update_wifi_icon()

        try:
            departures = dep_service.query_departures(self.current_station[0])
        except Exception as err:
            log("Failed to query departures: %r" % (err,))
            self.table.set_cell_value(1, 1, "Could not load departures")
            self.lbl_live.set_text("Live data: Error")  # US4.3
            return

        self.lbl_live.set_text("Live data: OK")  # US4.3

        # US3.3: Filter on transport type
        if self.settings.current_transport != "All":
            mode = self.settings.current_transport.upper()
            filtered = [
                dep for dep in departures
                if (dep["route"].get("transport_mode") or "").upper() == mode]
        else:
            filtered = departures

        if len(filtered) == 0:
            self.table.set_cell_value(1, 1, "No departures right now")
            return

        for row_idx, dep_data in enumerate(filtered, start=1):
            if row_idx > 7:
                break

            # Line number for buses, train number for trains
            # (the name is the whole route for trains)
            line = dep_data["route"]["designation"]
            if line is None:
                line = dep_data["route"]["name"]

            dest = dep_data["route"]["destination"]["name"]

            dep_time = self.format_time(dep_data["realtime"])

            self.table.set_cell_value(row_idx, 0, fit(line or "", 130 - 33))
            self.table.set_cell_value(row_idx, 1, fit(dest or "", 263 - 33))
            self.table.set_cell_value(row_idx, 2, dep_time)
            self.table.set_cell_value(row_idx, 3, self.format_status(dep_data))

    @staticmethod
    def format_journey_station(station_name):
        index = station_name.find('(')
        if index == -1: return station_name
        return station_name[:index]

    @safe
    def add_journey_step(self, step):
        step_container = lv.obj(self.journey_container)
        step_container.set_size(317, lv.SIZE_CONTENT)
        step_container.align(lv.ALIGN.CENTER, 0, 0)
        step_container.set_style_bg_color(lv.color_hex(0x2B2E33), 0)
        step_container.set_style_radius(8, 0)
        step_container.set_style_pad_left(5, 0)
        step_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        
        detail_line = lv.line(step_container)
        detail_line.set_style_line_color(lv.color_hex(0xFFFFFF), 0)
        detail_line.set_style_line_width(5, 0)
        detail_line.set_style_line_rounded(True, 0)
        points_line = [ lv.point_precise_t({ "x": 10.5, "y": 10.5 }), lv.point_precise_t({ "x": 10.5, "y": 84.5 }) ]
        detail_line.set_points(points_line, len(points_line))
        if step["type"] == "WALK":
            detail_line.set_style_line_dash_width(6, 0)
            detail_line.set_style_line_dash_gap(6, 0)

        detail_circle_origin = lv.obj(step_container)
        detail_circle_origin.set_pos(5, 5)
        detail_circle_origin.set_size(12, 12)
        detail_circle_origin.set_style_border_width(3, 0)
        detail_circle_origin.set_style_border_color(lv.color_hex(0xFFFFFF), 0)
        detail_circle_origin.set_style_bg_color(lv.color_hex(0x2B2E33), 0)
        detail_circle_origin.set_style_radius(16, 0)

        detail_circle_dest = lv.obj(step_container)
        detail_circle_dest.set_pos(5, 78)
        detail_circle_dest.set_size(12, 12)
        detail_circle_dest.set_style_border_width(3, 0)
        detail_circle_dest.set_style_border_color(lv.color_hex(0xFFFFFF), 0)
        detail_circle_dest.set_style_bg_color(lv.color_hex(0x2B2E33), 0)
        detail_circle_dest.set_style_radius(16, 0)

        origin_time = lv.label(step_container)
        origin_time.align(lv.ALIGN.TOP_LEFT, 27, 0)
        origin_time.add_style(styles.text, 0)
        origin_time.set_text(step["Origin"]["time"][:5])
        
        origin_name = lv.label(step_container)
        origin_name.align(lv.ALIGN.TOP_LEFT, 27, 20)
        origin_name.set_text(self.format_journey_station(step["Origin"]["name"]))
        origin_name.add_style(styles.text_sub_title, 0)

        line = step["Product"][0].get("line", None)
        if line is None:
            line = step["Product"][0]["name"]
        else:
            line = "Line " + line
            line += f", Towards: {self.format_journey_station(step["direction"])}"
        
        line_lbl = lv.label(step_container)
        line_lbl.align(lv.ALIGN.TOP_LEFT, 27, 45)
        line_lbl.set_text(line)
        line_lbl.add_style(styles.text_sub_title, 0)
        
        dest_time = lv.label(step_container)
        dest_time.align(lv.ALIGN.TOP_LEFT, 27, 74)
        dest_time.set_text(step["Destination"]["time"][:5])
        dest_time.add_style(styles.text, 0)
        
        dest_name = lv.label(step_container)
        dest_name.align(lv.ALIGN.TOP_LEFT, 27, 74 + 20)
        dest_name.set_text(self.format_journey_station(step["Destination"]["name"]))
        dest_name.add_style(styles.text_sub_title, 0)

    @safe
    def on_search_journey(self, event): # US5.3B
        self.journey_container.clean()
        
        if self.ta_to.get_text() == "" or self.ta_from.get_text() == "":
            return
        
        from_station_id = ""
        to_station_id = ""
        
        for station in STATIONS:
            if upper(station[1]) == upper(self.ta_from.get_text()):
                from_station_id = station[0]
            if upper(station[1]) == upper(self.ta_to.get_text()):
                to_station_id = station[0]

            if from_station_id != "" and to_station_id != "":
                break

        if from_station_id == "" or to_station_id == "":
            return

        if from_station_id == to_station_id:
            return

        journeys = dep_service.query_journeys(from_station_id, to_station_id)
        if len(journeys) == 0:
            return

        for step in journeys[0]["LegList"]["Leg"]:
            self.add_journey_step(step)

    @safe
    def on_stop_changed(self, event):  # US3.2B
        idx = event.get_target_obj().get_selected()
        if 0 <= idx < len(STATIONS):
            self.set_current_stop_id(STATIONS[idx][0])
            self.update_departure_table()

    @safe
    def on_transport_changed(self, event):  # US3.3
        idx = event.get_target_obj().get_selected()
        if idx == 0:
            self.settings.current_transport = "All"
        elif idx == 1:
            self.settings.current_transport = "Bus"
        elif idx == 2:
            self.settings.current_transport = "Train"
        elif idx == 3:
            self.settings.current_transport = "Ferry"
        self.update_departure_table()

    @safe
    def on_save_clicked(self, _event):  # US3.4
        self.settings.save()
        self.lbl_status.set_text("Settings saved as default!")

    # US3.5: Restore the stored default settings
    @safe
    def on_reset_clicked(self, _event):
        self.settings = UserSettings.reload()
        self.set_current_stop_id(self.settings.current_stop_id)
        self.dd_stops.set_selected(STATIONS.index(self.current_station))
        self.select_transport()
        self.update_departure_table()
        self.lbl_status.set_text("Default settings restored!")

    def select_transport(self):
        transports = ["All", "Bus", "Train", "Ferry"]
        if self.settings.current_transport in transports:
            self.dd_transport.set_selected(
                transports.index(self.settings.current_transport))

    # US4.3: Phone-style Wi-Fi icon, on the top layer so it shows on every
    # screen
    def create_wifi_icon(self):
        self.wifi_icon = lv.obj(lv.layer_top())
        self.wifi_icon.remove_style_all()
        self.wifi_icon.set_size(24, 16)
        self.wifi_icon.remove_flag(lv.obj.FLAG.SCROLLABLE)
        self.wifi_icon.remove_flag(lv.obj.FLAG.CLICKABLE)
        self.wifi_icon.align(lv.ALIGN.TOP_RIGHT, -12, 10)
        self.wifi_bars = []
        # Inner wedge, middle arc and outer arc
        for radius, width in ((6, 6), (11, 3), (16, 3)):
            arc = lv.arc(self.wifi_icon)
            arc.set_size(radius * 2, radius * 2)
            arc.align(lv.ALIGN.TOP_MID, 0, 16 - radius)
            arc.set_bg_angles(225, 315)
            arc.remove_style(None, lv.PART.KNOB)
            arc.remove_flag(lv.obj.FLAG.CLICKABLE)
            arc.set_style_arc_width(width, lv.PART.MAIN)
            arc.set_style_arc_rounded(False, lv.PART.MAIN)
            arc.set_style_arc_opa(lv.OPA.TRANSP, lv.PART.INDICATOR)
            self.wifi_bars.append(arc)

    # US4.3: White when connected, grey when not
    def update_wifi_icon(self):
        connected = network.WLAN(network.STA_IF).isconnected()
        for arc in self.wifi_bars:
            color = lv.color_hex(0xFFFFFF if connected else 0x4A4D52)
            arc.set_style_arc_color(color, lv.PART.MAIN)

    def create_ui(self):
        # Fonts with å, ä and ö, see fonts.py
        fonts.load()
        lv.screen_active().set_style_text_font(fonts.normal, 0)
        styles.text_title.set_text_font(fonts.title)
        styles.text_sub_title.set_text_font(fonts.normal)
        styles.text.set_text_font(fonts.normal)

        # Shared Keyboard
        self.shared_kb = custom_keyboard(lv.layer_top())

        # US2.1: The screens are tiles, navigated by swiping
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        # US1.1: Start screen
        self.tile_startup = self.tileview.add_tile(1, 0, lv.DIR.BOTTOM)
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

        # US1.2B: Departure screen
        self.tile_main = self.tileview.add_tile(
            1, 1, lv.DIR.TOP | lv.DIR.LEFT | lv.DIR.RIGHT)
        self.tile_main.add_style(styles.screen_default, 0)
        self.lbl_dept_title = lv.label(self.tile_main)
        self.lbl_dept_title.add_style(styles.text_title, 0)
        # One line, all stop names fit
        self.lbl_dept_title.set_size(520, fonts.title.get_line_height())
        self.lbl_dept_title.set_long_mode(lv.label.LONG_MODE.DOTS)
        self.lbl_dept_title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.lbl_dept_title.align(lv.ALIGN.TOP_MID, 0, 6)

        # US3.3: Shows the selected transport type
        self.lbl_dept_subtitle = lv.label(self.tile_main)
        self.lbl_dept_subtitle.add_style(styles.text_sub_title, 0)
        self.lbl_dept_subtitle.set_style_text_font(fonts.normal, 0)
        self.lbl_dept_subtitle.align(lv.ALIGN.TOP_MID, 0, 40)

        self.table = lv.table(self.tile_main)
        self.table.set_size(580, lv.SIZE_CONTENT)
        self.table.align(lv.ALIGN.TOP_MID, 0, 64)
        self.table.set_style_bg_color(lv.color_hex(0x1E1E1E), 0)
        self.table.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.table.set_style_border_width(1, 0)
        self.table.set_style_border_color(lv.color_hex(0x333333), 0)
        self.table.set_style_text_font(fonts.normal, lv.PART.ITEMS)
        self.table.set_style_pad_top(10, lv.PART.ITEMS)
        self.table.set_style_pad_bottom(10, lv.PART.ITEMS)

        self.table.set_column_count(4)
        # Each column fits its longest text
        self.table.set_column_width(0, 130)
        self.table.set_column_width(1, 263)
        self.table.set_column_width(2, 75)
        self.table.set_column_width(3, 110)

        self.table.set_cell_value(0, 0, "Line")
        self.table.set_cell_value(0, 1, "Destination")
        self.table.set_cell_value(0, 2, "Time")
        self.table.set_cell_value(0, 3, "Status")

        # US4.2: Manual refresh
        self.btn_refresh = lv.button(self.tile_main)
        self.btn_refresh.set_size(130, 36)
        self.btn_refresh.align(lv.ALIGN.BOTTOM_RIGHT, -10, -8)
        self.btn_refresh.set_style_radius(8, 0)
        self.btn_refresh.set_style_bg_color(lv.color_hex(0x2B2E33), 0)
        self.btn_refresh.set_style_bg_color(
            lv.color_hex(0x3A3D42), lv.STATE.PRESSED)
        self.btn_refresh.set_style_border_width(1, 0)
        self.btn_refresh.set_style_border_color(lv.color_hex(0x3A3D42), 0)
        self.btn_refresh.set_style_shadow_width(0, 0)
        self.btn_refresh.add_event_cb(
            lambda _e: self.update_departure_table(), lv.EVENT.CLICKED, None)

        lbl_refresh = lv.label(self.btn_refresh)
        lbl_refresh.set_text(lv.SYMBOL.REFRESH + "  Refresh")
        lbl_refresh.add_style(styles.text, 0)
        lbl_refresh.center()

        # NF3: Trafiklab attribution
        self.lbl_attribution = lv.label(self.tile_main)
        self.lbl_attribution.set_text("Data: Trafiklab.se CC-BY 4.0")
        self.lbl_attribution.add_style(styles.text_sub_title, 0)
        self.lbl_attribution.align_to(
            self.btn_refresh, lv.ALIGN.OUT_LEFT_MID, 0, 0)
        self.lbl_attribution.set_x(10)

        # US5.1: Journey screen
        self.tile_journey = self.tileview.add_tile(0, 1, lv.DIR.RIGHT)
        self.tile_journey.add_style(styles.screen_default, 0)

        self.lbl_journey_title = lv.label(self.tile_journey)
        self.lbl_journey_title.set_text("JOURNEY")
        self.lbl_journey_title.add_style(styles.text_title, 0)
        self.lbl_journey_title.align(lv.ALIGN.TOP_MID, 0, 15)

        # US5.1B: Search Origin and Destination
        self.ta_from = lv.textarea(self.tile_journey)
        self.ta_from.set_style_text_font(fonts.normal, 0)
        self.ta_from.set_size(220, 40)
        self.ta_from.align(lv.ALIGN.TOP_LEFT, 50, 90)
        self.ta_from.set_placeholder_text("Search Stop..")
        self.ta_from.set_one_line(True)

        self.ta_from.add_event_cb(
            self.on_search_journey, lv.EVENT.VALUE_CHANGED, None)
        self.search_from = SearchArea(self.ta_from, self.shared_kb)

        search_stations = [station[1] for station in STATIONS]
        self.search_from.set_options(search_stations)

        self.lbl_from = lv.label(self.tile_journey)
        self.lbl_from.add_style(styles.text, 0)
        self.lbl_from.set_text("From:")
        self.lbl_from.align_to(self.ta_from, lv.ALIGN.OUT_TOP_LEFT, 0, -10)

        self.ta_to = lv.textarea(self.tile_journey)
        self.ta_to.set_style_text_font(fonts.normal, 0)
        self.ta_to.set_size(220, 40)
        self.ta_to.align(lv.ALIGN.TOP_RIGHT, -50, 90)
        self.ta_to.set_placeholder_text("Search Stop..")
        self.ta_to.set_one_line(True)
        self.ta_to.add_event_cb(
            self.on_search_journey, lv.EVENT.VALUE_CHANGED, None)
        self.search_to = SearchArea(self.ta_to, self.shared_kb)

        self.search_to.set_options(search_stations)

        self.lbl_from = lv.label(self.tile_journey)
        self.lbl_from.add_style(styles.text, 0)
        self.lbl_from.set_text("To:")
        self.lbl_from.align_to(self.ta_to, lv.ALIGN.OUT_TOP_LEFT, 0, -10)

        self.journey_container = lv.obj(self.tile_journey)
        self.journey_container.align(lv.ALIGN.CENTER, 0, 60)
        self.journey_container.set_style_bg_color(lv.color_hex(0x16171a), 0)
        self.journey_container.set_style_border_width(0, 0)
        self.journey_container.set_size(350, 220)
        self.journey_container.set_style_radius(8, 0)
        self.journey_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.journey_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)
        self.journey_container.set_scroll_dir(lv.DIR.VER)

        # Manual Refresh
        self.btn_refresh_journey = lv.button(self.tile_journey)
        self.btn_refresh_journey.set_size(130, 36)
        self.btn_refresh_journey.align(lv.ALIGN.BOTTOM_RIGHT, -10, -8)
        self.btn_refresh_journey.set_style_radius(8, 0)
        self.btn_refresh_journey.set_style_bg_color(lv.color_hex(0x2B2E33), 0)
        self.btn_refresh_journey.set_style_bg_color(
            lv.color_hex(0x3A3D42), lv.STATE.PRESSED)
        self.btn_refresh_journey.set_style_border_width(1, 0)
        self.btn_refresh_journey.set_style_border_color(lv.color_hex(0x3A3D42), 0)
        self.btn_refresh_journey.set_style_shadow_width(0, 0)
        self.btn_refresh_journey.add_event_cb(
            self.on_search_journey, lv.EVENT.CLICKED, None)
        
        lbl_refresh_journey = lv.label(self.btn_refresh_journey)
        lbl_refresh_journey.set_text(lv.SYMBOL.REFRESH + "  Refresh")
        lbl_refresh_journey.add_style(styles.text, 0)
        lbl_refresh_journey.center()
        
        # NF3: Trafiklab attribution
        self.lbl_attribution_journey = lv.label(self.tile_journey)
        self.lbl_attribution_journey.set_text("Data: Trafiklab.se CC-BY 4.0")
        self.lbl_attribution_journey.add_style(styles.text_sub_title, 0)
        self.lbl_attribution_journey.align_to(
            self.btn_refresh_journey, lv.ALIGN.OUT_LEFT_MID, 0, 0)
        self.lbl_attribution_journey.set_x(10)

        # US3.1: Settings screen
        self.tile_settings = self.tileview.add_tile(2, 1, lv.DIR.LEFT)
        self.tile_settings.add_style(styles.screen_default, 0)

        self.lbl_settings_title = lv.label(self.tile_settings)
        self.lbl_settings_title.set_text("SETTINGS")
        self.lbl_settings_title.add_style(styles.text_title, 0)
        self.lbl_settings_title.align(lv.ALIGN.TOP_MID, 0, 15)

        # US3.2B: Select stop
        self.lbl_stop = lv.label(self.tile_settings)
        self.lbl_stop.set_text("Departure Stop:")
        self.lbl_stop.add_style(styles.text, 0)
        self.lbl_stop.align(lv.ALIGN.TOP_LEFT, 50, 65)
        
        self.dd_stops = lv.dropdown(self.tile_settings)
        self.dd_stops.set_options(
            "\n".join([station[1] for station in STATIONS]))
        self.dd_stops.set_size(220, 40)
        self.dd_stops.align(lv.ALIGN.TOP_LEFT, 50, 90)
        self.dd_stops.set_style_text_font(fonts.normal, 0)
        self.dd_stops.get_list().set_style_text_font(fonts.normal, 0)
        if self.current_station in STATIONS:
            self.dd_stops.set_selected(STATIONS.index(self.current_station))
        self.dd_stops.add_event_cb(
            self.on_stop_changed, lv.EVENT.VALUE_CHANGED, None)

        # US3.3: Select transport type
        self.lbl_transport = lv.label(self.tile_settings)
        self.lbl_transport.set_text("Transport Type:")
        self.lbl_transport.add_style(styles.text, 0)
        self.lbl_transport.align(lv.ALIGN.TOP_RIGHT, -120, 65)

        self.dd_transport = lv.dropdown(self.tile_settings)
        self.dd_transport.set_options("All\nBus\nTrain\nFerry")
        self.dd_transport.set_size(220, 40)
        self.dd_transport.align(lv.ALIGN.TOP_RIGHT, -50, 90)
        if self.settings.current_transport == "Bus":
            self.dd_transport.set_selected(1)
        elif self.settings.current_transport == "Train":
            self.dd_transport.set_selected(2)
        elif self.settings.current_transport == "Ferry":
            self.dd_transport.set_selected(3)
        self.dd_transport.add_event_cb(
            self.on_transport_changed, lv.EVENT.VALUE_CHANGED, None)

        # US3.4: Save as default
        self.btn_save = lv.button(self.tile_settings)
        self.btn_save.set_size(220, 45)
        self.btn_save.align(lv.ALIGN.TOP_LEFT, 50, 160)
        self.btn_save.set_style_bg_color(lv.color_hex(0x008800), 0)
        self.btn_save.add_event_cb(
            self.on_save_clicked, lv.EVENT.CLICKED, None)

        self.lbl_btn_save = lv.label(self.btn_save)
        self.lbl_btn_save.set_text("Save Default")
        self.lbl_btn_save.center()

        # US3.5: Reset to the stored default
        self.btn_reset = lv.button(self.tile_settings)
        self.btn_reset.set_size(220, 45)
        self.btn_reset.align(lv.ALIGN.TOP_RIGHT, -50, 160)
        self.btn_reset.set_style_bg_color(lv.color_hex(0x880000), 0)
        self.btn_reset.add_event_cb(
            self.on_reset_clicked, lv.EVENT.CLICKED, None)

        self.lbl_btn_reset = lv.label(self.btn_reset)
        self.lbl_btn_reset.set_text("Reset to Default")
        self.lbl_btn_reset.center()

        # US4.3: Live data status
        self.lbl_live = lv.label(self.tile_settings)
        self.lbl_live.add_style(styles.text, 0)
        self.lbl_live.align(lv.ALIGN.TOP_LEFT, 50, 240)

        # Because the startup tile isn't on 0,0 set it as the current tile on startup
        # Before create_wifi_icon() as lvgl starts rendering as soon as its declared
        # This ensures that we are on the startup screen when showing the wifi icons
        self.tileview.set_tile(self.tile_startup, 0)

        self.create_wifi_icon()

        self.lbl_status = lv.label(self.tile_settings)
        self.lbl_status.set_text("")
        self.lbl_status.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_status.align(lv.ALIGN.BOTTOM_MID, 0, -30)

        self.update_departure_table()

    @staticmethod
    def connect_wifi():
        log("connecting to Wi-Fi SSID: " + WIFI_SSID)
        station = network.WLAN(network.STA_IF)
        try:
            station.active(True)
            station.connect(WIFI_SSID, WIFI_PASSWORD)
            started = time.ticks_ms()
            while (not station.isconnected()
                   and time.ticks_diff(time.ticks_ms(), started) < 15_000):
                time.sleep_ms(250)
        except Exception as err:
            log("Wi-Fi error: %r" % (err,))
        if station.isconnected():
            log("Wi-Fi connected")
        else:
            log("Wi-Fi could not connect (timeout)")


try:
    app = Application()
except Exception as error:
    log("FATAL: %r" % (error,))
    sys.print_exception(error)
    raise
