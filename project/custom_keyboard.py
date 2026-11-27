import lvgl as lv
import fonts

keyboard_upper_map = [ "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "Å", "\n",
                       "A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "\n",
                       lv.SYMBOL.UP, "Z", "X", "C", "V", "B", "N", "M", lv.SYMBOL.BACKSPACE, "\n",
                       lv.SYMBOL.CLOSE, " ", lv.SYMBOL.OK ]

k = lv.buttonmatrix.CTRL.WIDTH_4
k_wide = lv.buttonmatrix.CTRL.WIDTH_6
space = lv.buttonmatrix.CTRL.WIDTH_12
keyboard_upper_format = [ k, k, k, k, k, k, k, k, k, k, k,
                          k, k, k, k, k, k, k, k, k, k, k,
                          k_wide | lv.buttonmatrix.CTRL.CHECKED, k, k, k, k, k, k, k, k_wide,
                          k, space, k ]

keyboard_lower_map = [ "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "å", "\n",
                       "a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "\n",
                       lv.SYMBOL.UP, "z", "x", "c", "v", "b", "n", "m", lv.SYMBOL.BACKSPACE, "\n",
                       lv.SYMBOL.CLOSE, " ", lv.SYMBOL.OK ]

keyboard_lower_format = [ k, k, k, k, k, k, k, k, k, k, k,
                          k, k, k, k, k, k, k, k, k, k, k,
                          k_wide, k, k, k, k, k, k, k, k_wide,
                          k, space, k ]

def is_keyboard_upper(keyboard: lv.keyboard) -> bool:
    return keyboard.get_mode() == lv.keyboard.MODE.USER_1

def set_keyboard_mode(keyboard: lv.keyboard, upper: bool):
    # Required to set map everytime otherwise keyboard won't render correctly
    if upper:
        keyboard.set_map(lv.keyboard.MODE.USER_1, keyboard_upper_map, keyboard_upper_format)
        keyboard.set_mode(lv.keyboard.MODE.USER_1)
    else:
        keyboard.set_map(lv.keyboard.MODE.USER_2, keyboard_lower_map, keyboard_lower_format)
        keyboard.set_mode(lv.keyboard.MODE.USER_2)

def switch_keyboard_mode(event: lv.event_t):
    keyboard: lv.keyboard = event.get_target_obj()

    if lv.SYMBOL.UP != keyboard.get_button_text(keyboard.get_selected_button()):
        return
    
    set_keyboard_mode(keyboard, not is_keyboard_upper(keyboard))
    event.stop_processing() # Dont draw the up arrow to the textarea

def clear_text_area(event: lv.event_t):
    keyboard: lv.keyboard = event.get_target_obj()

    if keyboard.get_textarea() is None:
        return

    text_area: lv.textarea = keyboard.get_textarea()
    text_area.set_text("")

def hide_keyboard(event: lv.event_t):
    keyboard: lv.keyboard = event.get_target_obj()

    keyboard.add_flag(lv.obj.FLAG.HIDDEN)

def custom_keyboard(parent: lv.obj) -> lv.keyboard:
    keyboard = lv.keyboard(parent)
    keyboard.set_style_text_font(fonts.normal, 0)
    keyboard.add_flag(lv.obj.FLAG.HIDDEN)
    
    keyboard.set_map(lv.keyboard.MODE.USER_1, keyboard_upper_map, keyboard_upper_format)
    keyboard.add_event_cb(
        switch_keyboard_mode, lv.EVENT.VALUE_CHANGED | lv.EVENT.PREPROCESS, None)
    keyboard.add_event_cb(
        clear_text_area, lv.EVENT.CANCEL, None)
    keyboard.add_event_cb(
        hide_keyboard, lv.EVENT.READY, None)

    keyboard.set_mode(lv.keyboard.MODE.USER_1)
    return keyboard
