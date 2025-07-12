"""Defines layout types and constants needed for display classes"""

import math
import tkinter
import tkinter.font

def layoutType(node):
    '''Given an html element node, determines its layout type'''

    if "display" in node.style and node.style.get("display") in ["block", "none","list-item","inline-block"]:
        return node.style.get("display")

    return "inline"

"""The amount by which to advance horizontally and vertically by default"""
HSTEP, VSTEP = 13, 18

""""""

"""Font Cache"""
FONTS = {}

#TODO: support more fonts. Also set up a more sophisticated cache at some point??

def getFont(node):
    '''Used to create the font needed to render text, taking into account css properties'''

    weight = node.style["font-weight"]
    style = node.style["font-style"]
    family = node.style["font-family"]
    if style == "normal": style = "roman"
    try:
        size = int(float(node.style["font-size"][:-2]) * .75)
    except:
        size = 26

    if node.style.get('font-size', " ")[-1] == "%": #TODO: expand and ensure this works. 
        size *= 1/float(node.style.get('font-size'))

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
