import tkinter
import tkinter.font
from URLHandler import URLHandler, Text
from HTMLParser import Text, Element
from CSS.CSSParser import CSSParser
import math
import logging
from dataclasses import dataclass
logger = logging.getLogger(__name__)

@dataclass 
class InlineTextInfo:
    def __init__(self, x, y, word, font, color):
        self.x = x 
        self.y = y 
        self.word = word 
        self.font = font 
        self.color = color

@dataclass
class InlineRectInfo: 
    def __init__(self, x,y,x2,y2,color): #this may need to hold css properties instead of color eventually?
        self.x = x 
        self.y = y 
        self.background_color = color
        self.x2 = x2 
        self.y2 = y2

def InlineLayout():
    
    def __init__():
        pass


def __init__():

    pass 