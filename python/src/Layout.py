import tkinter
import tkinter.font
from URLHandler import URLHandler, Text
from HTMLParser import Text, Element
from CSS.CSSParser import CSSParser
import math
import logging
logger = logging.getLogger(__name__)

HSTEP, VSTEP = 13, 18
DEFAULT_LEADING = 1.25 #do we need different leadings? TODO: later on might get this from CSS.
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
    "background-color": "white" # text book doesn't have this as inherited but I believe it should be based on what my browser does
}

#TODO: support more fonts. Also set up a more sophisticated cache at some point??
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

class DocumentLayout:
    def __init__(self, node, max_width):
        self.node = node
        self.parent = None
        self.children = []
        self.max_width = max_width

    def layout(self):
        self.width = self.max_width
        self.x = 0
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
            self.leading = DEFAULT_LEADING #TODO: this will become padding?? Actually probably not
            self.superscript = False
            self.small_caps = False
            self.list_indent = 0
            self.bullet = False

#Kind of a weird class to be honest. It's called block layout which would lead us to think that all elements
# of this class would have display: block, but how the book uses this class this isn't the case.
# Maybe at some point its worth a rework??
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

    #TODO: support more than block/inline
    def layout_mode(self): #TODO: enum for display vals

        if "display" in self.node.style and self.node.style.get("display") in ["block", "inline"]:
            return self.node.style.get("display")
        else: return "inline"

    def layout(self):

        self.x = self.parent.x
        self.width = self.parent.width #TODO: determine width and height here. 

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

    def paint(self):
        cmds = []

        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font, color in self.display_list:
                cmds.append(DrawText(x, y, word, font, color))

        return cmds

    def recurse(self, node):

        if isinstance(node, Text):
            if self.layoutProps.bullet and self.parent.node.tag == "li": #TODO: there is a better implementation for this
                if self.layoutProps.list_indent == 1:
                    self.word("• ", node)
                elif self.layoutProps.list_indent == 2:
                    self.word("◦ ", node)
                else:
                    self.word("‣ ", node)
            for word in node.text.split():
                self.word(word, node)
        elif node.tag not in ["script","style"]: #TODO: make this a global var somewhere
            self.handleOpenTag(node.tag)
            for child in node.children:
                self.recurse(child)
            self.handleCloseTag(node.tag)

    def word(self, word, node):
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        family = node.style["font-family"]
        color = node.style["color"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)
        font = get_font(size, weight, style, family)

        if self.layoutProps.small_caps:
            word = word.upper()

        w = font.measure(word)
        if self.cursor_x + w >= self.width - HSTEP: #TODO: what if overflow set? 
            self.flush()
        self.line.append((self.cursor_x, word, font, self.layoutProps.superscript, color))
        self.cursor_x += w + font.measure(" ")

    def flush(self): #TODO: use a single object in line to hold vars so we don't need such verbose lines
        if not self.line: return
        metrics = [font.metrics() for x, word, font, isSuperscript, color in self.line] #like this
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y +  self.layoutProps.leading * max_ascent
        for rel_x, word, font, isSuperscript, color in self.line:
            x = self.x + rel_x
            y =  self.y + baseline - font.metrics("ascent") if not isSuperscript else self.y + baseline - 1.8*font.metrics("ascent")
            self.display_list.append((x, y, word, font, color))
        max_descent = max([metric["descent"] for metric in metrics])
        
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = 0

        self.line = []

    def handleOpenTag(self, tag):
        if tag == "sup":
            # self.layoutProps.fontSize /=2
            self.layoutProps.superscript = True
        elif tag == "abbr":
            self.layoutProps.small_caps = True
        elif tag == "br":
            self.y += VSTEP
        elif tag == 'ul' or tag == 'ol': #going to treat ordered and unordered lists the same
            self.layoutProps.list_indent += 1
        elif tag == 'li':
            self.layoutProps.bullet = True

    def handleCloseTag(self, tag):

        if tag == "sup":
        #    self.layoutProps.fontSize *=2
            self.layoutProps.superscript = False
        elif tag == "abbr":
            self.layoutProps.small_caps = False
        elif tag == 'ul' or tag == 'ol': #going to treat ordered and unordered lists the same
            self.layoutProps.list_indent -= 1
        elif tag == 'li':
            self.layoutProps.bullet = False

def style(node, rules):

    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value
    #style attributes should override stylesheets apparently
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"

    for child in node.children:
        style(child, rules)

class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
        self.color = color

    def execute(self, scroll, canvas):
        #TODO: create react around text so we can have background colors for non-block elements
        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            anchor='nw',
            fill=self.color)

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

