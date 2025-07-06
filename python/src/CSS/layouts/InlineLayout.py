from src.HTML.HTMLParser import Element, Text
import logging
from dataclasses import dataclass
from src.CSS.layouts.LayoutConstants import layoutType, getFont
from src.CSS.layouts.Layout import Layout
import re
from src.CSS.layouts.LineLayout import LineLayout, RectLayout
from src.CSS.layouts.TextLayout import TextLayout
from src.CSS.CSSConstants import DEFAULT_LEADING

#from src.CSS.layouts.Line import TextBox, Box, Line
logger = logging.getLogger(__name__)


class InlineLayout(Layout):
    '''Holds and displays a sequence/tree of HTML elements with display inline.
    
    This class functions similar to a LineBox but simplified.
    '''
    
    def __init__(self, nodes,parent,previous):
        super().__init__(parent,previous)
        self.nodes = nodes
        self.lines = [] 
        self.y = self.parent.getYStart()
        self.x = self.parent.getXStart()

        self.curr_line = LineLayout(self, None)
        self.curr_line.y = self.parent.getYStart()
        self.curr_line.x = self.parent.getXStart()
        #does layout need its own display_list array? I think it can just get it from its children. 
    
    def getWidth(self):
        if self.width == None:
            self.width = self.parent.getContentWidth()

        return self.width
    
    def getContentWidth(self):
        if self.contentWidth == None:
            self.contentWidth = self.parent.getContentWidth()

        return self.contentWidth
  
    #TODO: implement CSS
    def getHeight(self):

        if len(self.lines) == 0:
            return 0
        
        return sum([line.getHeight() for line in self.lines ])
    
    def getX(self):

        return self.x

    def getY(self):

        return self.y
    
    def getXStart(self):

        return self.x
    
    def getYStart(self):

        return self.y + self.getHeight()

    #TODO: css to change initial values
    #TODO: content width calcs and width calcs are confusing me rn.

    def layout(self):
        logger.debug("laying our InlineLayout with {} children".format(len(self.children)))
        self.setCoordinates()

        for node in self.nodes:
            self.recurse(node)

        #Remember to handle the last line, but ONLY if it isn't empty
        #If you flush a non-empty line then the child that comes after it will not have the correct
        #start Y value, leading to overlapping text
        #I think, haven't actually seen this in practice. Still, best to be safe.
        if len(self.curr_line.layoutFragments) != 0 or len(self.curr_line.rects) != 0: #I don't think second condition will be true if first isn't
            self.getNextLine() 
        
    def setCoordinates(self):
        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here
        
    def recurse(self, node): #x start is always 0 since line's always start at leftmost edge in an inline display.
        '''Recurses through each child and creates lines of TextBoxes and Boxes 
        
        Each call returns cursor_x, start_y and lines index where:
        - cursor_x = the relative x position of text to begin laying out new text
        - start_y = the y value which the line ad lines_index starts
        - lines_index = tracks the last line which has not been flushed
        '''
        if isinstance(node, Text):
            return self.handleText(node)
        elif layoutType(node) == "inline": #TODO: handle inline-block and type input
            return self.handleInline(node)
        else: 
            return self.handleBlock(node)
        
    def getNextLine(self):
        '''Flushes the contents of the current line, appends it to lines and returns a new line to serve as the current line'''
        self.curr_line.flush()
        self.lines.append(self.curr_line)
        next = LineLayout(self, self.curr_line)
        next.x = self.x
        next.y = self.curr_line.getYStart()
        self.curr_line = next #just in case
        return next

    def handleText(self, node):
        no_newlines = re.sub(r'\t|\n','',node.text)
        squash_spaces = re.sub(r' +', ' ', no_newlines)
        words = squash_spaces.split(" ")
        font = getFont(node)
        curr_sentence = "" #create as few textboxes as possible, put lot's of words into a text box
        curr_w = 0
        cursor_x = self.curr_line.getWidth()
        for i in range(len(words)):
            word = "{} ".format(words[i]) #TODO: try and ensure we don't add extra spaces.
            w = font.measure(word)
            if curr_w + w + cursor_x < self.getContentWidth():
                curr_sentence += word 
                curr_w += w
            else:
                prev = self.curr_line.layoutFragments[-1] if len(self.curr_line.layoutFragments) > 0 else None
                t = TextLayout(self,prev,curr_sentence,font, node)
                self.curr_line.layoutFragments.append(t)
                self.curr_line = self.getNextLine()
                
                curr_sentence = words[i]
                curr_w = font.measure(word)
                cursor_x = 0

        if curr_sentence != "":
            prev = self.curr_line.layoutFragments[-1] if len(self.curr_line.layoutFragments) > 0 else None
            t = TextLayout(self,prev,curr_sentence,font, node)
            self.curr_line.layoutFragments.append(t)

            #TODO: check if we need an extra flush here to prevent text going off of screen.

        return 

    def handleInline(self,node):

        index = len(self.lines)
        curr_cursor_x = self.curr_line.getWidth()
        for child in node.children:
            self.recurse(child)

        if self.needsRect(node):
            #rect height is based on the font height for this node
            font = getFont(node)
            metrics = font.metrics()
            h = DEFAULT_LEADING * (metrics["descent"]+metrics["ascent"])

            from src.CSS.layouts.BlockLayout import BlockLayout
            for i in range(index, len(self.lines)): 
                if isinstance(self.lines[i], BlockLayout): #we could have interleaved BlockLayouts
                    y = self.lines[i].getYStart() if i < len(self.lines) else self.y
                    rect = RectLayout(self.x + curr_cursor_x,y,self.curr_line.getWidth()-curr_cursor_x,i == index, False ,node, h)
                    self.lines[i].rects.append(rect)
                    curr_cursor_x = 0

            #subtract curr_cursor_x since we may only have one line and we don't start that line
            y = self.lines[-1].getYStart() if len(self.lines) > 0 else self.y
            rect = RectLayout(self.x + curr_cursor_x,y,self.curr_line.getWidth()-curr_cursor_x,len(self.lines) == index, True,node, h)
            self.curr_line.rects.append(rect)
        return 

    def handleBlock(self,node):
        
        from src.CSS.layouts.BlockLayout import BlockLayout #Python let's you do this and I hate it
        block = BlockLayout(node,self,self.lines[-1] if len(self.lines) > 0 else None)
        block.layout()
        self.curr_line = self.getNextLine()
        self.lines.append(block)

        return 

    def needsRect(self,node):
        '''Given a node, determines if it needs a surrounding rect for background color, border etc'''
        
        return isinstance(node, Element) and "background-color" in node.style and node.style["background-color"] != "transparent"

    def paint(self): 
        cmds = []

        for line in self.lines:
                cmds.extend(line.paint())
            
        return cmds

    def __repr__(self):

        return "InlineLayout: x={} y={} width={} height={} num_nodes={}".format(self.x, self.y, self.getWidth(),self.getHeight(),len(self.nodes))

    def print(self, indent):
        print("-" * indent + "InlineLayout at ({},{}) with width {} height {}".format(self.x, self.y,self.getWidth(), self.getHeight()))
        for line in self.lines:
            line.print(indent + 1)

    def click(self,x,y):
        '''Returns a list of one or more elements that bound the given x and y coordinates (document coordinates, NOT canvas coordinates)'''

        elems = []
        #TODO: more testing to verify clicking on InlineLayouts is correct
        # if self.getX() <= x < self.getX() + self.getWidth() and \
        #     self.getY() <= y < self.getY() + self.getHeight():
        #     elems.append(self.node)
        if self.y > y:
            return elems 
        for child in self.lines:
            elems.extend(child.click(x,y))

        return elems
