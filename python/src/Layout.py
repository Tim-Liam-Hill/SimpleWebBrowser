import tkinter
import tkinter.font
from URL import Text

DEFAULT_FONT_SIZE = 16 #TODO: dedicated text class 
HSTEP, VSTEP = 13, 18
DEFAULT_LEADING = 1.25 #do we need different leadings? TODO: later on might get this from CSS.

FONTS = {}

#TODO: support more fonts 
def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
            slant=style)
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
        
        #TODO: pre formatted code (after html parser I guess?)
        #font = tkinter.font.Font() #TODO: support passed in fonts (somehow, once we move away from tkinter)
        for tok in tokens:
            self.token(tok, width)
        self.flush()

    def token(self,tok, width):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word, width)
        else: self.handleTag(tok.tag)

    def word(self, word, width):
        font = get_font(self.fontSize, self.weight, self.style)
        
        w = font.measure(word)
        if self.cursor_x + w >= width - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return 
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y +  self.leading * max_ascent
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
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
        elif tag == "br":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == "/p":
            self.flush()
            self.cursor_y += VSTEP

        