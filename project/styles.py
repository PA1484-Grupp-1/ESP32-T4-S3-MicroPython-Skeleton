# Shared fonts, colours and widget styles
import fs_driver
import lvgl as lv

from debug_log import log

# REQ#1.2: The built-in fonts have no å, ä or ö. fonts/sv_*.bin add those letters
# (made with lv_font_conv from Montserrat Medium, see fonts/OFL.txt)
font_normal = lv.font_montserrat_14
font_row = lv.font_montserrat_16
font_title = lv.font_montserrat_28

COLOR_BACKGROUND = 0x1e1f22
COLOR_PANEL = 0x2b2d31
COLOR_PANEL_ALT = 0x25272b
COLOR_BORDER = 0x3f4147
COLOR_TEXT = 0xffffff
COLOR_MUTED = 0x9a9ca3
COLOR_ACCENT = 0x23a55a
COLOR_DANGER = 0xa12d2f

# Departure status colours (REQ#1.2)
COLOR_ON_TIME = 0x3ba55d
COLOR_DELAYED = 0xf0b232
COLOR_EARLY = 0x5ab0ff
COLOR_CANCELLED = 0xf23f43

# Line badge colours per transport type (REQ#1.2)
LINE_COLORS = {"BUS": 0x1f8a4c, "TRAIN": 0x2f6feb, "BOAT": 0x0e8a8a}
COLOR_LINE_OTHER = 0x5c5f66

_fs_drv = None  # LVGL keeps using the driver, so it must stay referenced


def load_font(path, builtin):
    try:
        font = lv.binfont_create(path)
    except Exception as err:
        log("Failed to load font %s: %r" % (path, err))
        return builtin

    if font is None:
        log("Failed to load font " + path)
        return builtin

    font.fallback = builtin
    # Without this, g, j and y get clipped
    font.line_height = builtin.line_height
    font.base_line = builtin.base_line
    return font


# Must run after the board is started
def init_fonts():
    global font_normal, font_row, font_title, _fs_drv

    _fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(_fs_drv, "S")

    font_normal = load_font("S:/fonts/sv_14.bin", lv.font_montserrat_14)
    font_row = load_font("S:/fonts/sv_16.bin", lv.font_montserrat_16)
    font_title = load_font("S:/fonts/sv_28.bin", lv.font_montserrat_28)
    text_title.set_text_font(font_title)
    # The theme sets a font on the tiles, not just the screen
    screen_default.set_text_font(font_normal)


def style_button(button, color):
    button.set_style_bg_color(lv.color_hex(color), 0)
    button.set_style_radius(8, 0)
    button.set_style_shadow_width(0, 0)


# Shared look for the dropdowns (REQ#3.2, REQ#3.3)
def style_dropdown(dropdown):
    dropdown.set_style_bg_color(lv.color_hex(COLOR_PANEL), 0)
    dropdown.set_style_text_color(lv.color_hex(COLOR_TEXT), 0)
    dropdown.set_style_text_font(font_row, 0)
    dropdown.set_style_border_color(lv.color_hex(COLOR_BORDER), 0)
    dropdown.set_style_border_width(1, 0)
    dropdown.set_style_radius(8, 0)

    # The list that opens, with extra line spacing so it is easy to tap
    options = dropdown.get_list()
    options.set_style_bg_color(lv.color_hex(COLOR_PANEL), 0)
    options.set_style_text_color(lv.color_hex(COLOR_TEXT), 0)
    options.set_style_text_font(font_row, 0)
    options.set_style_text_line_space(18, 0)
    options.set_style_border_color(lv.color_hex(COLOR_BORDER), 0)
    options.set_style_border_width(1, 0)
    options.set_style_radius(8, 0)
    options.set_style_max_height(290, 0)
    for state in (0, lv.STATE.CHECKED, lv.STATE.PRESSED):
        options.set_style_bg_color(lv.color_hex(COLOR_ACCENT), lv.PART.SELECTED | state)


def new_style() -> lv.style_t:
    style = lv.style_t()
    style.init()
    return style


screen_default = new_style()
screen_default.set_bg_color(lv.color_hex(COLOR_BACKGROUND))
screen_default.set_bg_opa(lv.OPA.COVER)

text_title = new_style()
text_title.set_text_color(lv.color_hex(COLOR_ACCENT))
text_title.set_text_font(lv.font_montserrat_28)

text_sub_title = new_style()
text_sub_title.set_text_color(lv.color_hex(COLOR_MUTED))

text = new_style()
text.set_text_color(lv.color_hex(COLOR_TEXT))
