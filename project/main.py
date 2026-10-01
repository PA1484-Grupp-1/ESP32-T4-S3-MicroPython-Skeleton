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
        self.transitioned = False

        #Skapa och visa startskärmen direkt
        self.create_startup_screen()

        #Timer på 5 sekunder (5000 ms)
        self.fade_timer = lv.timer_create(self.on_timer_trigger, 15000, None)
        self.fade_timer.set_repeat_count(1)

        log("student application ready - waiting 5s or touch")

    #REQ#1.1: Startskärm
    def create_startup_screen(self):
        self.scr_startup = lv.obj()
        self.scr_startup.set_size(600, 450)
        self.scr_startup.set_style_bg_color(lv.color_hex(0x000000), 0)
        self.scr_startup.set_style_bg_opa(lv.OPA.COVER, 0)

        # Projektnamn
        self.lbl_title = lv.label(self.scr_startup)
        self.lbl_title.set_text("TRAFFIC SYSTEM")
        self.lbl_title.set_style_text_color(lv.color_hex(0x00E5FF), 0)
        self.lbl_title.set_style_text_font(lv.font_montserrat_28, 0)
        self.lbl_title.align(lv.ALIGN.TOP_MID, 0, 40)

        # Version
        self.lbl_ver = lv.label(self.scr_startup)
        self.lbl_ver.set_text("Version: 0.1.1")
        self.lbl_ver.set_style_text_color(lv.color_hex(0x888888), 0)
        self.lbl_ver.align(lv.ALIGN.TOP_MID, 0, 85)

        # Gruppnummer
        self.lbl_group = lv.label(self.scr_startup)
        self.lbl_group.set_text("Grupp 1")
        self.lbl_group.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.lbl_group.set_style_text_font(lv.font_montserrat_28, 0)
        self.lbl_group.align(lv.ALIGN.CENTER, 0, -20)

        # Medlemmar
        self.lbl_members = lv.label(self.scr_startup)
        self.lbl_members.set_text("Medlemmar: Ragnar, Anton, Filip, Axel, Jonathan")
        self.lbl_members.set_style_text_color(lv.color_hex(0xDDDDDD), 0)
        self.lbl_members.align(lv.ALIGN.BOTTOM_MID, 0, -40)

        # Osynligt klickbart lager som täcker hela displayen
        self.touch_layer = lv.obj(self.scr_startup)
        self.touch_layer.set_size(600, 450)
        self.touch_layer.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.touch_layer.set_style_border_width(0, 0)
        self.touch_layer.add_flag(lv.obj.FLAG.CLICKABLE)
        self.touch_layer.add_event_cb(self.on_startup_clicked, lv.EVENT.CLICKED, None)

        # Visa startskärmen
        lv.screen_load(self.scr_startup)

    def on_startup_clicked(self, _event):
        log("EVENT: Skärmen tryckt, byter skärm...")
        self.fade_to_main()

    def on_timer_trigger(self, _timer):
        log("EVENT: 5 sekunder har gått, byter skärm...")
        self.fade_to_main()

    def fade_to_main(self):
        if self.transitioned:
            return
        self.transitioned = True

        if self.fade_timer:
            try:
                self.fade_timer._del()
            except Exception:
                pass
            self.fade_timer = None

        # Skapa nästa skärm
        self.scr_main = lv.obj()
        self.scr_main.set_size(600, 450)
        self.create_ui(parent=self.scr_main)

        # Försök köra fade-animering, backa till direkt laddning om det felar
        try:
            lv.screen_load_anim(self.scr_main, lv.SCR_LOAD_ANIM.FADE_ON, 400, 0, True)
        except Exception:
            lv.screen_load(self.scr_main)

    # --- Befintlig UI ---
    @staticmethod
    def apply_tile_colors(tile, label, dark):
        tile.set_style_bg_opa(lv.OPA.COVER, 0)
        tile.set_style_bg_color(lv.color_hex(0x000000 if dark else 0xFFFFFF), 0)
        label.set_style_text_color(lv.color_hex(0xFFFFFF if dark else 0x000000), 0)

    def on_tile2_clicked(self, _event):
        self.tile2_dark = not self.tile2_dark
        self.apply_tile_colors(self.tile2, self.tile2_label, self.tile2_dark)

    def create_ui(self, parent=None):
        if parent is None:
            parent = lv.screen_active()
        self.tileview = lv.tileview(parent)
        self.tileview.set_size(600, 450)
        self.tileview.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

        self.tile1 = self.tileview.add_tile(0, 0, lv.DIR.RIGHT)
        self.tile2 = self.tileview.add_tile(1, 0, lv.DIR.LEFT)

        self.tile1_label = lv.label(self.tile1)
        self.tile1_label.set_text("Hello grupp 1")
        self.tile1_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile1_label.center()
        self.apply_tile_colors(self.tile1, self.tile1_label, False)

        self.tile2_label = lv.label(self.tile2)
        self.tile2_label.set_text("Welcome to the workshop")
        self.tile2_label.set_style_text_font(lv.font_montserrat_28, 0)
        self.tile2_label.center()
        self.apply_tile_colors(self.tile2, self.tile2_label, False)
        self.tile2.add_flag(lv.obj.FLAG.CLICKABLE)
        self.tile2.add_event_cb(self.on_tile2_clicked, lv.EVENT.CLICKED, None)

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