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

class DrawText:
    '''Represents the command needed to render text onto a Tkinter canvas'''

    def __init__(self, x1, y1, text, font, color):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
        self.color = color

    def execute(self, scroll, canvas):

        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            anchor='nw',
            fill=self.color)

    def __repr__(self):
        return "DrawText: x '{}' y '{}-{}' color '{}' text '{}'".format(self.left,self.top,self.bottom,self.color, self.text)

class DrawRect:
    ''''''

    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    #TODO: borders
    def execute(self, scroll, canvas):
        '''Represents the command needed to render rectangle onto a Tkinter canvas'''

        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=0,
            fill=self.color)

    def __repr__(self):
        return "DrawRect: x '{}->{}' y '{}-{}' color '{}'".format(self.left,self.right,self.top,self.bottom,self.color)