from src.CSS.layouts.Layout import Layout
from src.CSS.layouts.LayoutConstants import VSTEP, layoutType
from src.Draw.Commands import DrawRect
from src.CSS.layouts.InlineLayout import InlineLayout
from src.CSS.layouts.ListItemLayout import ListItemLayout
from src.CSS.layouts.InputLayout import createInputLayout
from src.HTML.HTMLParser import Element
import logging
logger = logging.getLogger(__name__)


class BlockLayout(Layout):
    '''The implementation for "block" css display property. Also implements logic for ul and ol.'''
    
    def __init__(self, node, parent, previous):
        super().__init__(parent,previous)

        self.node = node 
        self.lastLi = None #keeps track of last li element so that children will be in line with its marker

    #TODO: implement CSS
    def getWidth(self):


        return self.parent.getContentWidth()

    #TODO: implement CSS
    def getContentWidth(self):
        if self.contentWidth == None:
            self.contentWidth = self.parent.getContentWidth()

        return self.contentWidth - (self.getXStart() - self.getX())
    
    def getHeight(self):
        '''The height of a block element is dependant on the height of its children
        
        #TODO: implement caching of height calculation.
        '''

        if self.node.tag in ["br", "hr"]:
            return VSTEP
        
        if len(self.children) == 0:
            return 0

        height = sum([child.getHeight() for child in self.children] + [0]) #TODO: should this ever be 0??? 

        #height = self.y- (self.children[-1].getHeight() + self.children[-1].getY())
        #TODO: add our own borders and padding

        return height

    def getX(self):

        return self.x

    def getY(self):

        return self.y

    def getXStart(self):

        padInline = 0
        if  "padding-inline-start" in self.node.style:
            #TODO: handle ems and other non-px units
            val = self.node.style.get("padding-inline-start")
            if "px" in val:
                padInline = val.split("px")[0]

        #If there was a previous marker then we want to be inline with it even though it isn't displayed
        #we ensure marker isn't None since that is the case when we are getting x start for the current li
        markerW = 0 if self.lastLi == None or self.lastLi.marker == None else self.lastLi.marker.getWidth()
        return self.x + int(padInline)  + markerW

    #TODO: padding and margin?? 
    def getYStart(self):

        initial = self.y + self.getHeight()

        if self.node.tag in ["p"]: 
            initial += VSTEP

        return initial

    #TODO: content width calcs and width calcs are confusing me rn.
    def layout(self):
        '''Forces this Layout Object to create all of its layout children'''
        
        self.setCoordinates()
        if self.node.tag == "input":
            c = createInputLayout(self.node,self,self.previous)
            c.layout()
            self.children = [c]
        else: 
            self.createChildren()

    def setCoordinates(self):
        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here. also, NOT Y start here. if we are a block element and our parent was a block element and no previous then we start at their start

    def createChildren(self):
        inline_children = []
        prev = None

        listCount = 1

        for child in self.node.children: 
            if isinstance(child, Element) and child.tag in ["head","script","style","meta"]:
                continue
            
            if layoutType(child) == "none":
                continue

            if layoutType(child) in ["inline", "inline-block"]:
                inline_children.append(child)
                continue

            if child.tag == "br" and len(inline_children) != 0:
                #line breaks look differently when part of an inline context
                inline_children.append(child)
                continue

            if len(inline_children) != 0:
                next = InlineLayout(inline_children,self,prev)
                next.layout()
                self.children.append(next)
                prev = next
                inline_children = []
            
            if layoutType(child) == "list-item":
                next = ListItemLayout(child,self, prev, listCount)
                self.lastLi = next
                listCount += 1
            else:
                next = BlockLayout(child,self,prev)
            self.children.append(next)
            next.layout()
            prev = next

        if len(inline_children) != 0:
            next = InlineLayout(inline_children,self,prev)
            self.children.append(next)
            prev = next
            next.layout()
   
    def paint(self):  
        cmds = []

        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent" and self.node.tag != "input": #don't draw over input!!!!
            x2, y2 = self.x + self.getWidth(), self.y + self.getHeight()
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        for child in self.children:
            cmds.extend(child.paint())
        
        return cmds

    def __repr__(self):
        return "BlockLayout: tag={} x={} y={} width={} height={}".format(self.node.tag, self.x, self.y, self.width,self.getHeight())

    def print(self, indent):
        print("-" * indent + "BlockLayout at ({},{}) width {} height {}".format(self.x,self.y,self.getWidth(), self.getHeight()))

        for child in self.children:
            child.print(indent + 1)
    
    def click(self,x,y):
        '''Returns a list of one or more elements that bound the given x and y coordinates (document coordinates, NOT canvas coordinates)'''

        elems = []
        if self.getX() <= x < self.getX() + self.getWidth() and \
            self.getY() <= y < self.getY() + self.getHeight():
            elems.append(self.node)
        if self.y > y:
            return elems 
        for child in self.children:
            elems.extend(child.click(x,y))

        return elems
