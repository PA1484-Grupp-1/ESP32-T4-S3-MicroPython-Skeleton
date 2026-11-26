import fonts

# MicroPython's str.upper() only handles ASCII letters
def upper(text):
    pairs = (("å", "Å"), ("ä", "Ä"), ("ö", "Ö"), ("æ", "Æ"), ("ø", "Ø"),
             ("é", "É"), ("ü", "Ü"))
    for small, big in pairs:
        text = text.replace(small, big)
    return text.upper()


# Shortens text with "..." so a table cell never wraps to more lines
def fit(text, width):
    font = fonts.normal

    def text_width(t):
        return sum(font.get_glyph_width(ord(c), 0) for c in t)

    if text_width(text) <= width:
        return text
    while text and text_width(text + "...") > width:
        text = text[:-1]
    return text.rstrip() + "..."