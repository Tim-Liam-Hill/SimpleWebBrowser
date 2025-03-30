import sys
import tkinter
import tkinter.font
from URLHandler import URLHandler, Text, lex
from HTMLParser import Text, Element
from CSS.CSSParser import CSSParser
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
        layoutProps = LayoutDisplayProperties()
        child = BlockLayout(self.node, self, None, layoutProps)
        self.children.append(child)
        child.layout()
        self.height = child.height
    
    def paint(self):
        return []

#Stores properties used to implement font style, weight etc
#TODO: this possibly needs a rework once CSS is implemented but oh whale
class LayoutDisplayProperties:
    def __init__(self):
            self.fontSize = DEFAULT_FONT_SIZE
            self.weight = "normal"
            self.style = "roman"
            self.leading = DEFAULT_LEADING
            self.superscript = False
            self.small_caps = False
            self.family = DEFAULT_FONT_FAMILY
            self.activeTags = []
            self.list_indent = 0
            self.bullet = False

class BlockLayout:
    def __init__(self, node, parent, previous, layoutProps):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.display_list = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.layoutProps = layoutProps

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

        if(isinstance(self.node, Element)):
            self.handleOpenTag(self.node.tag)

        mode = self.layout_mode()
        if mode == "block":
            
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous, self.layoutProps)
                self.children.append(next)
                previous = next
        else:
            self.display_list = []
            self.line = []
            self.cursor_x = 0
            self.cursor_y = 0

            self.recurse(self.node)
            self.flush()
            
        for child in self.children:
            child.layout()
        if(isinstance(self.node, Element)):
            self.handleCloseTag(self.node.tag)
        
        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else: self.height = self.cursor_y
    
    #According to the book, can block elements not draw 
    #TODO: what did I mean by the above???
    def paint(self):
        cmds = []

        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))

        return cmds
    
    def recurse(self, node): 
        
        if isinstance(node, Text):
            if self.layoutProps.bullet:
                if self.layoutProps.list_indent == 1:
                    self.word("• ")
                elif self.layoutProps.list_indent == 2:
                    self.word("◦ ")
                else: 
                    self.word("‣ ")
            for word in node.text.split():
                self.word(word)
        elif node.tag not in ["script","style"]: #TODO: make this a global var somewhere
            self.handleOpenTag(node.tag)
            for child in node.children:
                self.recurse(child)
            self.handleCloseTag(node.tag)

    def word(self, word):

        font = get_font(self.layoutProps.fontSize, self.layoutProps.weight, self.layoutProps.style, self.layoutProps.family)

        if self.layoutProps.small_caps:
            word = word.upper()        

        w = font.measure(word)
        if self.cursor_x + w >= self.width - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font, self.layoutProps.superscript))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return 
        metrics = [font.metrics() for x, word, font, isSuperscript in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y +  self.layoutProps.leading * max_ascent
        for rel_x, word, font, isSuperscript in self.line:
            x = self.x + rel_x
            y =  self.y + baseline - font.metrics("ascent") if not isSuperscript else self.y + baseline - 1.8*font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = 0
        self.line = []

    def handleOpenTag(self, tag):
        if tag == "i":
            self.layoutProps.style = "italic"
        elif tag == "b":
            self.layoutProps.weight = "bold"
        elif tag == "small":
            self.layoutProps.fontSize -= 2
        elif tag == "big":
            self.layoutProps.fontSize += 4
        elif tag == "sup":
            self.layoutProps.fontSize /=2
            self.layoutProps.superscript = True
        elif tag == "abbr":
            self.layoutProps.small_caps = True 
            self.layoutProps.family = "Courier"
            self.layoutProps.fontSize *= 0.75
            self.layoutProps.weight = "bold"
        elif tag == "br":
            #self.flush()
            self.y += VSTEP
        elif tag == 'ul' or tag == 'ol': #going to treat ordered and unordered lists the same
            self.layoutProps.list_indent += 1
        elif tag == 'li':
            self.layoutProps.bullet = True

    def handleCloseTag(self, tag):
        if tag == "i":
            self.layoutProps.style = "roman"
        elif tag == "b":
            self.layoutProps.weight = "normal"
        elif tag == "small":
            self.layoutProps.fontSize += 2
        elif tag == "big":
            self.layoutProps.fontSize -=4
        elif tag == "sup":
            self.layoutProps.fontSize *=2
            self.layoutProps.superscript = False
        elif tag == "abbr":
            self.layoutProps.small_caps = False
            self.layoutProps.family = DEFAULT_FONT_FAMILY
            self.layoutProps.fontSize /= 0.75
            self.layoutProps.weight = "normal"
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == 'ul' or tag == 'ol': #going to treat ordered and unordered lists the same
            self.layoutProps.list_indent -= 1
        elif tag == 'li':
            self.layoutProps.bullet = False

def style(node, rules):
    node.style = {}

    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value
    #style attributes should override stylesheets apparently 
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    for child in node.children:
        style(child, rules)

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
    url = URLHandler()

