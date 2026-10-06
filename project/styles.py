import lvgl as lv

screen_default = lv.style_t()
screen_default.set_bg_color(lv.color_hex(0x1e1f22))
screen_default.set_bg_opa(lv.OPA.COVER)

text_title = lv.style_t()
text_title.set_text_color(lv.color_hex(0x23a55a))
text_title.set_text_font(lv.font_montserrat_28)

text_sub_title = lv.style_t()
text_sub_title.set_text_color(lv.color_hex(0x888888))

text = lv.style_t()
text.set_text_color(lv.color_hex(0xFFFFFF))
