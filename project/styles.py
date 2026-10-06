import lvgl as lv

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
