import tkinter
from HTMLParser import Text
import tkinter.font
import logging
from dataclasses import dataclass
from layouts.LayoutConstants import LayoutTypes, DrawRect, DrawText, VSTEP, HSTEP, get_font,DEFAULT_LEADING
from layouts.Layout import Layout
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


class InlineLayout(Layout):
    '''The implementation for "block" css display property'''
    
    def __init__(self, node,parent,previous):
        super().__init__(node,parent,previous)
        self.cursor_x = 0
        self.cursor_y = 0
        
        self.cont_x = 0
        self.cont_y = 0

        self.line = []
        self.line_start_x = 0
    
    def getWidth(self):

        return self.width

    
    def getContentWidth(self):

        return self.content_width

    
    def calculateContentWidth(self):

        return self.parent.getContentWidth()

    
    def calculateWidth(self):

        return self.parent.getContentWidth()
    
    #TODO: implement CSS
    def getHeight(self):

        return self.cursor_y
    
    def getX(self):

        return self.x

    
    def getY(self):

        return self.y
    
    
    def getXStart(self):

        return self.cont_x
    
    
    def getYStart(self):

        return self.cont_y

    #TODO: css to change initial values
        #TODO: content width calcs and width calcs are confusing me rn.

    def layout(self):
        
        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getYStart() #TODO: same here
        
        self.content_width = self.calculateContentWidth()

        if self.previous:
            self.cursor_x = self.previous.getXContinue()
        else: self.cursor_x = self.parent.getXContinue()
        self.line_start_x = self.cursor_x #so we can draw a rect at the correct starting position if this is a follow on element

        self.recurse(self.node)
        self.cont_x = self.cursor_x 
        self.cont_y = self.cursor_y + self.y

        self.flush()

        for child in self.children:
            child.layout()
    
    def getXContinue(self):

        return self.cont_x
    
    def paint(self): #TODO:Should this be abstract or can we make this generic? 
        cmds = []
        
        for elem in self.display_list:
            if isinstance(elem, InlineTextInfo):
                cmds.append(DrawText(elem.x, elem.y, elem.word, elem.font, elem.color))
            elif isinstance(elem, InlineRectInfo):
                cmds.append(DrawRect(elem.x,elem.y,elem.x2,elem.y2,elem.background_color))

        return cmds

    def recurse(self, node):

        if isinstance(node, Text):
            for word in node.text.split(): #TODO: to stop trailing space isn't as simple as I thought: i need to know if we have a a next after us
                self.word(word, node)
        elif node.tag not in ["script","style", "head", "meta"]: #TODO: make this a global var somewhere
            for child in node.children:
                self.recurse(child)

    def word(self, word, node):

        font = self.getFont(word, node)
        w = font.measure(word)
        if self.cursor_x + w >= self.getContentWidth() - HSTEP: #TODO: what if overflow set?
            self.flush()
            
        vert_align = 1
        match node.style.get('vertical-align', ""):
            case "super":
                vert_align = 1.8
            case "sub":
                vert_align = -1.8
        
        css_props = {
            "vert_align": vert_align,
            "color": node.style["color"]
        }
            
        self.line.append((self.cursor_x, word, font, css_props))
        self.cursor_x += w + font.measure(" ")

    def getFont(self, word, node):
        '''Used to create the font needed to render text, taking into account css properties'''

        weight = node.style["font-weight"]
        style = node.style["font-style"]
        family = node.style["font-family"]
        color = node.style["color"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)

        if node.style.get('font-size', " ")[-1] == "%": #TODO: expand and ensure this works. 
            size *= 1/float(node.style.get('font-size'))

        return get_font(size, weight, style, family)

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font, css_props in self.line] #like this
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y +  DEFAULT_LEADING * max_ascent
        text_display_list = []

        for rel_x, word, font, css_props in self.line:
            x = self.x + rel_x
            y =  self.y + baseline - css_props["vert_align"] * font.metrics("ascent")
            text_display_list.append(InlineTextInfo(x, y, word, font,css_props["color"]))
        max_descent = max([metric["descent"] for metric in metrics])
        
        if self.node.style.get("background-color") != "transparent": #TODO: adjust offsets once we have padding etc
            self.display_list.append(InlineRectInfo(self.line_start_x, self.y + self.cursor_y,  self.cursor_x, self.y + self.cursor_y + 1.25*max_descent +  max_ascent,self.node.style.get("background-color")))

        #Rects must be rendered before text otherwise text gets covered 
        self.display_list = self.display_list + text_display_list

        self.cursor_y = baseline + 1.25 * max_descent #TODO: remind me what that 1.25 is for again?
        self.cursor_x = 0
        self.line_start_x = self.x 

        self.line = []

    def getLayoutMode(self):

        return LayoutTypes.Inline

    def __repr__(self):
        return "InlineLayout: x={} y={} width={} height={}".format(self.x, self.y, self.width,self.getHeight())