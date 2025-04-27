from src.layouts.Layout import Layout
from src.layouts.LayoutConstants import LayoutTypes, DrawRect, VSTEP
from src.layouts.InlineLayout import InlineLayout
from src.HTMLParser import Element
import logging
logger = logging.getLogger(__name__)

class BlockLayout(Layout):
    '''The implementation for "block" css display property'''
    
    def __init__(self, node, parent, previous):
        super().__init__(parent,previous)

        self.node = node 
        self.display_list = []

    def getWidth(self):

        return self.width

    def getContentWidth(self):

        return self.content_width

    #TODO: implement CSS
    def calculateContentWidth(self): 

        return self.parent.getContentWidth()

    #TODO: implement CSS
    def calculateWidth(self):

        return self.parent.getContentWidth()
    
    def getHeight(self):
        '''The height of a block element is dependant on the height of its children'''

        if self.node.tag in ["br", "hr"]:
            return VSTEP
        
        if len(self.children) == 0:
            return 0

        height = max([child.getHeight() + child.getY() for child in self.children] + [0]) #TODO: should this ever be 0??? 
        height -= self.y
        #height = self.y- (self.children[-1].getHeight() + self.children[-1].getY())
        #TODO: add our own borders and padding

        return height

    def getX(self):

        return self.x

    def getY(self):

        return self.y

    def getXStart(self):

        return self.x

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
        self.width = self.calculateWidth()
        self.content_width = self.calculateContentWidth()

        self.createChildren()
        
        for child in self.children:
            child.layout()

    def setCoordinates(self):
        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here. also, NOT Y start here. if we are a block element and our parent was a block element and no previous then we start at their start

    def createChildren(self):
        inline_children = []
        prev = None
        for child in self.node.children: 
            if isinstance(child, Element) and child.tag in ["head","script","style","meta"]:
                continue
            
            if Layout.layoutType(child) == "none":
                continue

            if Layout.layoutType(child) == "inline":
                inline_children.append(child)
                continue

            if len(inline_children) != 0:
                next = InlineLayout(inline_children,self,prev)
                self.children.append(next)
                prev = next
                inline_children = []
            next = BlockLayout(child,self,prev)
            self.children.append(next)
            prev = next

        if len(inline_children) != 0:
            next = InlineLayout(inline_children,self,prev)
            self.children.append(next)
            prev = next
   
    def paint(self):  
        cmds = []

        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.getHeight()
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        for child in self.children:
            cmds.extend(child.paint())
        
        return cmds

    def getLayoutMode(self):
        
        return LayoutTypes.Block

    def __repr__(self):
        return "BlockLayout: tag={} x={} y={} width={} height={}".format(self.node.tag, self.x, self.y, self.width,self.getHeight())

    def print(self, indent):
        print("-" * indent + "BlockLayout: width {} height {}".format(self.width, self.getHeight()))

        for child in self.children:
            child.print(indent + 1)