"""Departure board shown on the main tile.

lv.table always wraps long text over several lines. These fixed rows keep every
departure on one line instead, and long destinations scroll sideways.
"""

import lvgl as lv

import styles

# REQ#1.2: Number of departures shown at once
ROW_COUNT = 7

BOARD_X = 20
BOARD_WIDTH = 560
HEADER_Y = 50
FIRST_ROW_Y = 72
ROW_HEIGHT = 40
ROW_SPACING = 44

# (x, width) inside a row
COLUMN_TIME = (12, 60)
COLUMN_LINE = (76, 106)
COLUMN_DESTINATION = (194, 262)
COLUMN_STATUS = (462, 88)


def new_box(parent, x, y, width, height, color):
    """Create a plain coloured box that lets touches through to the tile."""
    box = lv.obj(parent)
    box.set_pos(x, y)
    box.set_size(width, height)
    box.set_style_bg_color(lv.color_hex(color), 0)
    box.set_style_bg_opa(lv.OPA.COVER, 0)
    box.set_style_border_width(0, 0)
    box.set_style_pad_all(0, 0)
    box.set_style_radius(8, 0)
    box.remove_flag(lv.obj.FLAG.SCROLLABLE)
    box.remove_flag(lv.obj.FLAG.CLICKABLE)
    return box


def new_cell(parent, column, long_mode, font, color):
    """Create a one-line label in a table column."""
    label = lv.label(parent)
    label.set_width(column[1])
    label.set_long_mode(long_mode)
    label.set_style_text_font(font, 0)
    label.set_style_text_color(lv.color_hex(color), 0)
    label.align(lv.ALIGN.LEFT_MID, column[0], 0)
    label.set_text("")
    return label


def line_color(transport_mode):
    return styles.LINE_COLORS.get(transport_mode, styles.COLOR_LINE_OTHER)


def status_color(status):
    if status == "On time":
        return styles.COLOR_ON_TIME
    if status == "Cancelled":
        return styles.COLOR_CANCELLED
    if status == "Scheduled":
        return styles.COLOR_MUTED
    if status.startswith("-"):
        return styles.COLOR_EARLY
    return styles.COLOR_DELAYED


# One departure: time, line badge, destination and status
class DepartureRow:
    def __init__(self, parent, index):
        color = styles.COLOR_PANEL if index % 2 == 0 else styles.COLOR_PANEL_ALT
        y = FIRST_ROW_Y + index * ROW_SPACING
        self.row = new_box(parent, BOARD_X, y, BOARD_WIDTH, ROW_HEIGHT, color)

        self.time = new_cell(self.row, COLUMN_TIME, lv.label.LONG_MODE.CLIP,
                             styles.font_row, styles.COLOR_TEXT)

        self.badge = new_box(self.row, COLUMN_LINE[0], 7, COLUMN_LINE[1], 26,
                             styles.COLOR_LINE_OTHER)
        self.line = lv.label(self.badge)
        # The fixed height keeps long line names on one line, cut off with dots
        self.line.set_size(COLUMN_LINE[1] - 8, 16)
        self.line.set_long_mode(lv.label.LONG_MODE.DOTS)
        self.line.set_style_text_font(styles.font_normal, 0)
        self.line.set_style_text_color(lv.color_hex(styles.COLOR_TEXT), 0)
        self.line.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.line.center()

        self.destination = new_cell(self.row, COLUMN_DESTINATION,
                                    lv.label.LONG_MODE.SCROLL_CIRCULAR,
                                    styles.font_row, styles.COLOR_TEXT)

        self.status = new_cell(self.row, COLUMN_STATUS, lv.label.LONG_MODE.CLIP,
                               styles.font_normal, styles.COLOR_MUTED)
        self.status.set_style_text_align(lv.TEXT_ALIGN.RIGHT, 0)

        self.hide()

    def show(self, time_text, line, destination, status, transport_mode):
        self.time.set_text(time_text)
        self.line.set_text(line)
        self.badge.set_style_bg_color(lv.color_hex(line_color(transport_mode)), 0)
        self.destination.set_text(destination)
        self.status.set_text(status)
        self.status.set_style_text_color(lv.color_hex(status_color(status)), 0)
        self.row.remove_flag(lv.obj.FLAG.HIDDEN)

    def hide(self):
        self.row.add_flag(lv.obj.FLAG.HIDDEN)


# Column headers, the departure rows and a message for when there is nothing to show
class DepartureBoard:
    def __init__(self, parent):
        for column, text in ((COLUMN_TIME, "Time"), (COLUMN_LINE, "Line"),
                             (COLUMN_DESTINATION, "Destination")):
            self.new_header(parent, column, text, lv.TEXT_ALIGN.LEFT)
        self.new_header(parent, COLUMN_STATUS, "Status", lv.TEXT_ALIGN.RIGHT)

        self.rows = [DepartureRow(parent, index) for index in range(ROW_COUNT)]

        self.message = lv.label(parent)
        self.message.set_style_text_font(styles.font_row, 0)
        self.message.set_style_text_color(lv.color_hex(styles.COLOR_MUTED), 0)
        self.message.align(lv.ALIGN.CENTER, 0, -10)
        self.message.set_text("")

    @staticmethod
    def new_header(parent, column, text, text_align):
        label = lv.label(parent)
        label.set_width(column[1])
        label.set_text(text)
        label.set_style_text_color(lv.color_hex(styles.COLOR_MUTED), 0)
        label.set_style_text_align(text_align, 0)
        label.set_pos(BOARD_X + column[0], HEADER_Y)

    def show_departures(self, departures):
        """Show (time, line, destination, status, transport_mode) tuples."""
        self.message.set_text("")
        for index, row in enumerate(self.rows):
            if index < len(departures):
                row.show(*departures[index])
            else:
                row.hide()

    def show_message(self, text):
        for row in self.rows:
            row.hide()
        self.message.set_text(text)
