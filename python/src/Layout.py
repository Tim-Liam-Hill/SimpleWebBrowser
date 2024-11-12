import sys
import tkinter
import tkinter.font
from URL import URL, Text, lex
import math
import logging
logger = logging.getLogger(__name__)

DEFAULT_FONT_SIZE = 16 #TODO: dedicated text class 
HSTEP, VSTEP = 13, 18
DEFAULT_LEADING = 1.25 #do we need different leadings? TODO: later on might get this from CSS.
DEFAULT_FONT_FAMILY = "Times"
FONTS = {}
SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]

#TODO: support more fonts 
def get_font(size, weight, style, family):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=math.floor(size), weight=weight,
            slant=style, family=family)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]

#TODO: test cases. Lol
class Layout:
    def __init__(self, tokens, width):
        self.display_list = []
        self.line = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.fontSize = DEFAULT_FONT_SIZE
        self.weight = "normal"
        self.style = "roman"
        self.leading = DEFAULT_LEADING
        self.superscript = False
        self.small_caps = False
        self.family = DEFAULT_FONT_FAMILY
        self.activeTags = []
        logger.info(tkinter.font.families())
        
        #TODO: pre formatted code (after html parser I guess?)
        #font = tkinter.font.Font() #TODO: support passed in fonts (somehow, once we move away from tkinter)
        for tok in tokens:
            self.token(tok, width)
        self.flush()

    def token(self,tok, width):
    
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word, width)
        else: 
            #TODO: this will need a big rework once dom is implemented. 
            #I want to have some sort of decorator pattern where we 
            #Setup defaults and then have decorators that edit the defaults
            #as we go down. 
            self.handleTag(tok.tag)

    def word(self, word, width):

        font = get_font(self.fontSize, self.weight, self.style, self.family)

        if self.small_caps:
            word = word.upper()

        w = font.measure(word)
        if self.cursor_x + w >= width - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font, self.superscript))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return 
        metrics = [font.metrics() for x, word, font, isSuperscript in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y +  self.leading * max_ascent
        for x, word, font, isSuperscript in self.line:
            y = baseline - font.metrics("ascent") if not isSuperscript else baseline - 1.8*font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []

    def handleTag(self,tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "/i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "/b":
            self.weight = "normal"
        elif tag == "small":
            self.fontSize -= 2
        elif tag == "/small":
            self.fontSize += 2
        elif tag == "big":
            self.fontSize += 4
        elif tag == "/big":
            self.fontSize -=4
        elif tag == "sup":
            self.fontSize /=2
            self.superscript = True 
        elif tag == "/sup":
            self.fontSize *=2
            self.superscript = False
        elif tag == "abbr":
            self.small_caps = True 
            self.family = "Courier"
            self.fontSize *= 0.75
            self.weight = "bold"
        elif tag == "/abbr":
            self.small_caps = False
            self.family = DEFAULT_FONT_FAMILY
            self.fontSize /= 0.75
            self.weight = "normal"
        elif tag == "br":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == "/p":
            self.flush()
            self.cursor_y += VSTEP

if __name__ == "__main__": 
    logging.basicConfig(level=logging.DEBUG)
    window = tkinter.Tk()
    url = URL()
    content = url.request(sys.argv[1])
    tokens = lex(content, url.viewSource)
    layout = Layout(tokens, 800)
