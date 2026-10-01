import sys
import time

import lvgl as lv
import network

from board_lvgl import start_board
from debug_log import log

from secrets import WIFI_SSID, WIFI_PASSWORD


class Application:
    def __init__(self):
        self.display, self.touch, self.handler = start_board()
        self.tile2_dark = False

        self.create_ui()
        log("student application ready - starting at startup tile (0, 0)")

    @staticmethod
    def apply_tile_colors(tile, label, dark):
        tile.set_style_bg_opa(lv.OPA.COVER, 0)
        tile.set_style_bg_color(lv.color_hex(0x000000 if dark else 0xFFFFFF), 0)
        label.set_style_text_color(lv.color_hex(0xFFFFFF if dark else 0x000000), 0)

    def on_tile2_clicked(self, _event):
        self.tile2_dark = not self.tile2_dark
        self.apply_tile_colors(self.tile2, self.tile2_label, self.tile2_dark)

    def create_ui(self):
        # Gemensam tileview för hela skärmen
        self.tileview = lv.tileview(lv.screen_active())
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        # 1. STARTSKÄRMEN: Tile (0, 0) - Ligger överst
        # Tillåter enbart att man sveper nedåt till huvudskärmen
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

        # 2. HUVUDSKÄRM 1: Tile (0, 1) - Ligger rakt under startskärmen
        # Tillåter svep uppåt (till start) och åt höger (till tile 2)
        self.tile1 = self.tileview.add_tile(0, 1, lv.DIR.TOP | lv.DIR.RIGHT)
        self.tile1_label = lv.label(self.tile1)
        self.tile1_label.set_text("Hello grupp 1")
        self.tile1_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile1_label.center()
        self.apply_tile_colors(self.tile1, self.tile1_label, False)

        # 3. HUVUDSKÄRM 2: Tile (1, 1) - Ligger till höger om skärm 1
        # Tillåter svep åt vänster (tillbaka till tile 1)
        self.tile2 = self.tileview.add_tile(1, 1, lv.DIR.LEFT)
        self.tile2_label = lv.label(self.tile2)
        self.tile2_label.set_text("Welcome to the workshop")
        self.tile2_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile2_label.center()
        self.apply_tile_colors(self.tile2, self.tile2_label, False)
        self.tile2.add_flag(lv.obj.FLAG.CLICKABLE)
        self.tile2.add_event_cb(self.on_tile2_clicked, lv.EVENT.CLICKED, None)

        # Lås startpositionen till den översta rutan direkt vid boot
        self.tileview.set_tile(self.tile_startup, lv.ANIM.OFF)

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