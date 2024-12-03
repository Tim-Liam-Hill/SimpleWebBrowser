import sys
import tkinter
import tkinter.font
from URL import URL, Text, lex
from HTMLParser import Text, Element
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
BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
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

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)

#TODO: when we get to adding CSS, this is gonna need a big overhaul. We need to think carefully about how to let CSS adjust properties. 
class DocumentLayout:
    def __init__(self, node, max_width):
        self.node = node
        self.parent = None
        self.children = []
        self.max_width = max_width

    def layout(self):
        self.width = self.max_width
        self.x = HSTEP
        self.y = 0
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()
        self.height = child.height
    
    def paint(self):
        return []

class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.display_list = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"
        
    def layout(self):
        self.x = self.parent.x
        self.width = self.parent.width

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.display_list = []
            self.line = []
            self.cursor_x = 0
            self.cursor_y = 0

            #TODO: move to global/reference variable of sometype.
            self.fontSize = DEFAULT_FONT_SIZE
            self.weight = "normal"
            self.style = "roman"
            self.leading = DEFAULT_LEADING
            self.superscript = False
            self.small_caps = False
            self.family = DEFAULT_FONT_FAMILY
            self.activeTags = []


            self.recurse(self.node)
            self.flush()
            
        for child in self.children:
            child.layout()
        
        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else: self.height = self.cursor_y
    
    #According to the book, can block elements not draw 
    def paint(self):
        cmds = []

        if isinstance(self.node, Element) and self.node.tag == "code":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, "gray")
            cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))



        return cmds
    
    def recurse(self, node): 
        
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(word)
        elif node.tag not in ["script","style"]: #TODO: make this a global var somewhere
            self.handleOpenTag(node.tag)
            for child in node.children:
                self.recurse(child)
            self.handleCloseTag(node.tag)

    def word(self, word):

        font = get_font(self.fontSize, self.weight, self.style, self.family)

        if self.small_caps:
            word = word.upper()

        w = font.measure(word)
        if self.cursor_x + w >= self.width - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font, self.superscript))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return 
        metrics = [font.metrics() for x, word, font, isSuperscript in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y +  self.leading * max_ascent
        for rel_x, word, font, isSuperscript in self.line:
            x = self.x + rel_x
            y =  self.y + baseline - font.metrics("ascent") if not isSuperscript else baseline - 1.8*font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = 0
        self.line = []

    def handleOpenTag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.fontSize -= 2
        elif tag == "big":
            self.fontSize += 4
        elif tag == "sup":
            self.fontSize /=2
            self.superscript = True
        elif tag == "abbr":
            self.small_caps = True 
            self.family = "Courier"
            self.fontSize *= 0.75
            self.weight = "bold"
        elif tag == "br":
            self.flush()
            self.cursor_y += VSTEP

    def handleCloseTag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.fontSize += 2
        elif tag == "big":
            self.fontSize -=4
        elif tag == "sup":
            self.fontSize *=2
            self.superscript = False
        elif tag == "abbr":
            self.small_caps = False
            self.family = DEFAULT_FONT_FAMILY
            self.fontSize /= 0.75
            self.weight = "normal"
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP


class DrawText:
    def __init__(self, x1, y1, text, font):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            anchor='nw')
    
class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color
    
    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=0,
            fill=self.color)

if __name__ == "__main__": 
    logging.basicConfig(level=logging.DEBUG)
    window = tkinter.Tk()
    url = URL()

