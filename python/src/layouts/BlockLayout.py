'''BlockLayout'''

from Layout import Layout
import LayoutConstants as LayoutConstants

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
        
        height = sum([child.getHeight() for child in self.children]) 
        if self.node.tag == "p": 
            height += LayoutConstants.VSTEP

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

        return self.y

    #TODO: content width calcs and width calcs are confusing me rn.
    def layout(self):
        '''Forces this Layout Object to create all of its layout children'''

        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getYStart() #TODO: same here
        self.width = self.calculateWidth()
        self.content_width = self.calculateContentWidth()

        prev = None
        for child in self.node.children:
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
            x2, y2 = self.x + self.width, self.y + self.height
            rect = LayoutConstants.DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)
        
        return cmds


    def getLayoutMode(self):
        
        return LayoutConstants.Block
