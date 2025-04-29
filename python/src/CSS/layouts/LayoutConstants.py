"""Defines layout types and constants needed for display classes"""

from enum import Enum, unique
import math
import tkinter
import tkinter.font

@unique
class LayoutTypes(Enum):
    Block = "block"
    Inline = "inline"
    #TODO: none, hidden

"""The amount by which to advance horizontally and vertically by default"""
HSTEP, VSTEP = 13, 18

""""""

"""Font Cache"""
FONTS = {}

#TODO: support more fonts. Also set up a more sophisticated cache at some point??
"""Used to access fonts in the font cache"""
def get_font(size, weight, style, family):

    #TODO: change later once more CSS involved and SKIA involved
    if weight not in ["normal", "bold"]:
        weight = "normal"
    

    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=math.floor(size), weight=weight,
            slant=style, family=family)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]
