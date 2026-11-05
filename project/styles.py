import fs_driver
import lvgl as lv

from debug_log import log

# The built-in Montserrat fonts have no å, ä or ö. fonts/sv_*.bin contain only
# the extra letters and fall back to the built-in font for everything else.
# Generated from Montserrat Medium (see fonts/OFL.txt) with lv_font_conv:
#   lv_font_conv --font Montserrat_500Medium.ttf --size 14 --bpp 4 --format bin
#     --no-compress --no-prefilter -o sv_14.bin
#     -r 0xC4,0xC5,0xC6,0xC9,0xD6,0xD8,0xDC,0xE4,0xE5,0xE6,0xE9,0xF6,0xF8,0xFC
font_normal = lv.font_montserrat_14
font_title = lv.font_montserrat_28

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
    # The extra letters alone give the wrong metrics, which would clip g, j and y
    font.line_height = builtin.line_height
    font.base_line = builtin.base_line
    return font

# Must run after the board is started
def init_fonts():
    global font_normal, font_title, _fs_drv

    _fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(_fs_drv, "S")

    font_normal = load_font("S:/fonts/sv_14.bin", lv.font_montserrat_14)
    font_title = load_font("S:/fonts/sv_28.bin", lv.font_montserrat_28)
    text_title.set_text_font(font_title)
    # The theme sets a font on the tiles, so setting it on the screen is not enough
    screen_default.set_text_font(font_normal)

def new_style() -> lv.style_t:
    style = lv.style_t()
    style.init()
    return style

screen_default = new_style()
screen_default.set_bg_color(lv.color_hex(0x1e1f22))
screen_default.set_bg_opa(lv.OPA.COVER)

text_title = new_style()
text_title.set_text_color(lv.color_hex(0x23a55a))
text_title.set_text_font(lv.font_montserrat_28)

text_sub_title = new_style()
text_sub_title.set_text_color(lv.color_hex(0x888888))

text = new_style()
text.set_text_color(lv.color_hex(0xFFFFFF))
