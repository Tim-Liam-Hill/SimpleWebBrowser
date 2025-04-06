from layouts.Layout import Layout
from layouts.LayoutConstants import LayoutTypes, DrawRect, VSTEP
from layouts.InlineLayout import InlineLayout
from HTMLParser import Element

class BlockLayout(Layout):
    '''The implementation for "block" css display property'''
    
    def __init__(self, node, parent, previous):
        super().__init__(node,parent,previous)

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
        height = max([child.getHeight() + child.getY() for child in self.children] + [0]) #TODO: should this ever be 0??? 
        height -= self.y
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

        if self.node.tag == "p": 
            initial += VSTEP

        return initial

    #TODO: content width calcs and width calcs are confusing me rn.
    def layout(self):
        '''Forces this Layout Object to create all of its layout children'''

        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        
        if self.previous:
            if self.previous.getLayoutMode().value == LayoutTypes.Inline.value:
                self.y = self.previous.getHeight() + self.previous.getY() #TODO: this logic may need to change.
            else: 
                self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getYStart() #TODO: same here
        self.width = self.calculateWidth()
        self.content_width = self.calculateContentWidth()

        prev = None
        for child in self.node.children:
            if isinstance(child, Element) and child.tag in ["head"]:
                continue
            next = self.createChild(child,prev)
            self.children.append(next)
            prev = next
        
        for child in self.children:
            child.layout()

    def paint(self): #TODO:Should this be abstract or can we make this generic? 
        cmds = []

        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.getHeight()
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)
        
        return cmds


    def getLayoutMode(self):
        
        return LayoutTypes.Block

    def createChild(self, node, previous):
        """Creates and returns a new node based on its display property. Default is InlineLayout if no display property"""

        if "display" in node.style and self.node.style.get("display") in ["block", "inline"]:
            match node.style.get("display"):
                case "block": return BlockLayout(node, self, previous)
                case "inline": return InlineLayout(node, self, previous)
        else: 
            return InlineLayout(node, self, previous)

    def __repr__(self):
        return "BlockLayout: tag={} x={} y={} width={} height={}".format(self.node.tag, self.x, self.y, self.width,self.getHeight())
