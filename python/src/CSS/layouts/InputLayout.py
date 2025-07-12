from src.CSS.layouts.LayoutConstants import getFont
from src.CSS.CSSConstants import DEFAULT_LEADING
from src.CSS.layouts.Layout import Layout
from src.Draw.Commands import DrawRect, DrawText

import logging
logger = logging.getLogger(__name__)
DEFAULT_WIDTH_PX = 200

def createInputLayout(node, parent, previous):
    '''Given a node of tag 'input' returns the appropriate InputLayout object based on the node's "type" attribute'''
    logger.debug("Creating an InputLayout based on node's type")

    #LOL GET PRANKT NERD THERE IS ONLY ONE LAYOUT TYPE SUPPORTED
    #TODO: support more layout types
    return TextInputLayout(node, parent, previous)

class TextInputLayout(Layout):
    '''Implementation of input html tags. NOTE: these tags should never have children (both as a matter of specification and
    how our parser works).'''
    def __init__(self, node, parent, previous):
        super().__init__(parent,previous)
        self.node = node
        self.font = getFont(self.node) #basically caching it

        metrics = self.font.metrics()
        self.baseline = DEFAULT_LEADING * metrics["ascent"]
        self.node.attributes["value"] = "DELETE THIS IN CONSTRUCTOR"

    def getWidth(self):

        '''TODO: css properties'''
        
        return DEFAULT_WIDTH_PX
        
    def getContentWidth(self):

        return self.getWidth()
    

    def getHeight(self):

        ascent = self.font.metrics()["ascent"]
        descent = self.font.metrics()["descent"]

        return DEFAULT_LEADING * (ascent + descent)

    def getX(self):

        return self.x


    def getY(self):

        return self.y
    

    def getXStart(self):
        return self.x + self.getWidth()

    def getYStart(self):

        return self.y + self.getHeight()
    
    def layout(self):

        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        self.y = self.parent.getYStart() #TODO: same here

    def paint(self): 

        cmds = []

        bgcolor = self.node.style.get("background-color","transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.getWidth(), self.y + self.getHeight()
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)
        y1 = self.y + self.baseline - self.font.metrics("ascent")
        cmds.append(DrawText(self.x, y1, "",self.font,self.node.style["color"], self.node))
        return cmds


    def click(self,x,y):

        elems = []
        if self.y < y and self.y + self.getHeight() > y \
            and self.x < x and self.x + self.getWidth() > x:
            elems.append(self.node)

        return elems

    def print(self,indent):
        val = self.node.attributes.get("value")
        t = val if len(val) < 7 else " ".join(val.split(" ")[0:7])
        print("-" * indent + "TextInputLayout at ({},{}) with height {} and text '{}'".format(self.x,self.y,self.getHeight(),t))