import tkinter
import tkinter.font
from URL import Text

DEFAULT_FONT_SIZE = 16 #TODO: dedicated text class 
HSTEP, VSTEP = 13, 18

class Layout:
    def __init__(self, tokens, width):
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        
        #TODO: pre formatted code (after html parser I guess?)
        #font = tkinter.font.Font() #TODO: support passed in fonts (somehow, once we move away from tkinter)
        for tok in tokens:
            self.token(tok, width)

        # for tok in tokens:
        #     if isinstance(tok, Text):
        #         for word in tok.text.split(): #TODO: if a word is longer than the full window length we will have a weird empty line
        #             font = tkinter.font.Font(
        #                 size=DEFAULT_FONT_SIZE,
        #                 weight=weight,
        #                 slant=style,
        #             )
                    
        #             w = font.measure(word)
        #             if cursor_x + w >= width - HSTEP:
        #                 cursor_y += font.metrics("linespace") * 1.25
        #                 cursor_x = HSTEP
        #             self.display_list.append((cursor_x, cursor_y, word, font))
        #             cursor_x += w + font.measure(" ")
        #         else:
        #             weight, style = switchFontDetails(tok.tag, weight, style)

    def token(self,tok, width):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word, width)
        else: self.switchFontDetails(tok.tag)

    def word(self, word, width):
        font = tkinter.font.Font(
            size=DEFAULT_FONT_SIZE,
            weight=self.weight,
            slant=self.style,
        )
        
        w = font.measure(word)
        if self.cursor_x + w >= width - HSTEP:
            self.cursor_y += font.metrics("linespace") * 1.25
            self.cursor_x = HSTEP
        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.cursor_x += w + font.measure(" ")


    def switchFontDetails(self,tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "/i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "/b":
            self.weight = "normal"

        