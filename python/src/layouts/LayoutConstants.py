"""Defines layout types and constants needed for display classes"""

from enum import Enum, unique

@unique
class LayoutTypes(Enum):
    Block = "block"
    Inline = "inline"
    #TODO: none, hidden

"""The amount by which to advance horizontally and vertically by default"""
HSTEP, VSTEP = 13, 18

""""""
DEFAULT_LEADING = 1.25 #do we need different leadings? TODO: later on might get this from CSS.

"""Font Cache"""
FONTS = {}

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]

INHERITED_PROPERTIES = {
    "font-size": "26px", #TODO: need a better idea on how to make font-sizes look lekker
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
    "font-family": 'Times',
    #"background-color": "transparent" # text book doesn't have this as inherited but I believe it should be based on what my browser does
    #having this inherited caused problems so oops
}

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
