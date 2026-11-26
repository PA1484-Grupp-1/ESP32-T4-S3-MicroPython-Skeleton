import lvgl as lv
from format_helpers import upper

class SearchArea:
    def on_select_option(self, event: lv.event_t):
        options = self.dd.get_options().split("\n")
        
        if self.dd.get_selected() >= len(options):
            return

        self.textarea.set_text(options[self.dd.get_selected()])

        # FIX ME: Only clears the focus visually, for some reason doesn't let you click on it again to regain focus
        self.textarea.remove_state(lv.STATE.FOCUSED | lv.STATE.FOCUS_KEY)
        self.textarea.send_event(lv.EVENT.DEFOCUSED, None)

    def on_click_keyboard(self, event: lv.event_t):
        if not self.dd.is_open():
            return

        self.keyboard.remove_flag(lv.obj.FLAG.HIDDEN)

    def on_focus(self, event: lv.event_t):
        self.dd.open()
        self.keyboard.remove_flag(lv.obj.FLAG.HIDDEN)
        self.keyboard.set_textarea(self.textarea)

    def on_defocus(self, event: lv.event_t):
        self.dd.close()
        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)

    def update_search_options(self, event: lv.event_t):
        search_options = [option for option in self.options if upper(self.textarea.get_text()) in upper(option)]

        is_open = self.dd.is_open()
        if is_open:
            self.dd.close()
            self.dd.clear_options()

        self.dd.set_options("\n".join(search_options))
        self.dd.set_selected(0)
        
        if is_open:
            self.dd.open()

    def __init__(self, textarea: lv.textarea, keyboard: lv.keyboard):
        self.textarea = textarea
        self.keyboard = keyboard
        self.options = []
    
        self.dd = lv.dropdown(self.textarea.get_parent())
        self.dd.set_selected_highlight(False)

        self.dd.set_size(1, 1)
        self.dd.set_symbol(None)
        self.dd.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.dd.set_style_border_width(0, 0)
        self.dd.set_style_shadow_width(0, 0)
        self.dd.set_style_pad_all(0, 0)
        self.dd.set_style_text_opa(lv.OPA.TRANSP, 0)

        self.dd.align_to(self.textarea, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 0)
        self.dd.get_list().set_width(self.textarea.get_width() + 20)
        self.dd.get_list().set_style_min_width(self.textarea.get_width() + 20, 0)
        
        self.dd.add_event_cb(
            self.on_select_option, lv.EVENT.VALUE_CHANGED | lv.EVENT.PREPROCESS, None)
        
        self.textarea.add_event_cb(
            self.on_click_keyboard, lv.EVENT.CLICKED, None)

        self.textarea.add_event_cb(
            self.on_focus, lv.EVENT.FOCUSED, None)

        self.textarea.add_event_cb(
            self.on_defocus, lv.EVENT.DEFOCUSED, None)

        self.textarea.add_event_cb(
            self.update_search_options, lv.EVENT.VALUE_CHANGED, None)
        
    def set_options(self, options: list[str]):
        self.options = options
        self.update_search_options(None)
