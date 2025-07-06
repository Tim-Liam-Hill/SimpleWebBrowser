from src.CSS.layouts.Layout import Layout
from src.CSS.layouts.LayoutConstants import getFont
from src.CSS.CSSConstants import DEFAULT_LEADING
from src.CSS.layouts.InlineLayout import InlineLayout
from src.CSS.layouts.TextLayout import TextLayout
from src.Draw.Commands import DrawRect

import logging
logger = logging.getLogger(__name__)

class ListItemLayout(Layout):

    def __init__(self, node, parent, previous, count):
        super().__init__(parent,previous)
        self.node = node
        self.count = count #in case we are a numbered list item
        self.marker = None 

    def getWidth(self):
        '''Returns sum of parent's padding-inline-start, marker width and child width '''


        w = self.marker.getWidth()
        childW = self.children[0].getWidth()

        return self.getInlinePad() + w + childW

    def getInlinePad(self):
        padInline = 0
        if self.node.parent != None and "padding-inline-start" in self.node.parent.style:
            #TODO: handle ems and other non-px units
            val = self.node.parent.style.get("padding-inline-start")
            if "px" in val:
                padInline = val.split("px")[0]

        return int(padInline)

    def getContentWidth(self):
        '''returns width for non-marker content'''

        return self.parent.getContentWidth() - self.getInlinePad()
    

    def getHeight(self):
        '''Returns height of marker or child, depending on which is larger'''

        return max(self.marker.getHeight(), self.children[0].getHeight() if len(self.children) > 0 else 0)

    def getX(self):

        return self.x

    def getY(self):

        return self.y
    
    def getXStart(self):

        return self.x + self.marker.getWidth() + self.getInlinePad()
    
    def getYStart(self):

        return self.y + self.getHeight()
    
    def layout(self):

        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here

        self.createMarker()
        #I feel like I could also use a block layout here, not really any difference
        #but we will see.
        self.children.append(InlineLayout([self.node], self, self.previous))
        self.children[0].layout()

    def createMarker(self):
        text = ""
        if self.node.parent and self.node.parent.style.get("list-style-type"):
            
            #This should always be the case if not the above
            match self.node.parent.style.get("list-style-type"):
                case "circle":
                    text = "●"
                case "square":
                    text = "■"
                case "disc":
                    text = "○"
                case "decimal":
                    text = "{}.".format(self.count)
                case _:
                    logger.warning("ListItemLayout does not have supported list-style-type,using a default value")
                    text = "●"
            
        else:
            logger.warning("ListItemLayout does not have list-style-type set in style attributes, using a default value")
            text = "●"
        
        font = getFont(self.node)
        metrics = font.metrics()
        h = DEFAULT_LEADING * (metrics["descent"]+metrics["ascent"])
        baseline = h - (DEFAULT_LEADING * metrics["descent"])

        self.marker = TextLayout(self, None,text, font, self.node)
        self.marker.baseline = baseline
        self.marker.x = self.x + self.getInlinePad()
        self.marker.y = self.y

    def paint(self):

        cmds = []
        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.getWidth(), self.y + self.getHeight()
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        cmds.extend(self.marker.paint())
        cmds.extend(self.children[0].paint())

        return cmds
    
    def click(self,x,y):

        elems = []
        if self.getX() <= x < self.getX() + self.getWidth() and \
            self.getY() <= y < self.getY() + self.getHeight():
            elems.append(self.node)
        if self.y > y:
            return elems 
        for child in self.children:
            elems.extend(child.click(x,y))

        return elems

    def print(self, indent):
        print("-" * indent + "ListItemLayout at ({},{}) width {} height {}".format(self.x,self.y,self.getWidth(), self.getHeight()))

        self.marker.print(indent +1)

        for child in self.children:
            child.print(indent + 1)