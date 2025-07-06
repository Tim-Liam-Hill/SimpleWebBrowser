from src.CSS.CSSConstants import DEFAULT_LEADING
from src.Draw.Commands import DrawText
from src.CSS.layouts.Layout import Layout

class TextLayout(Layout):

    def __init__(self, parent, previous, text, font, node):
        super().__init__(parent,previous)
        self.text = text 
        self.font = font
        self.baseline = None
        self.node = node 

        #X and Y coordinates get set by the parent line once it is flushed.

    def getWidth(self):
        if self.width == None: 
            self.width = self.font.measure(self.text)

        return self.width

    def getContentWidth(self):
        
        return self.getWidth()

    def getHeight(self):
        '''While we could use self.font.metrics()["linespace"] to determine height, instead we make use of ascent descent and DEFAULT_LEADING'''
        
        if self.text == "":
            return 0

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

        return
    
    def paint(self):

        cmds = []
        y1 = self.y + self.baseline - self.font.metrics("ascent")
        #TODO: use vert align
        cmds.append(DrawText(self.x,y1,self.text,self.font,self.node.style["color"]))
        return cmds

    def click(self,x,y):

        elems = []
        if self.y < y and self.y + self.getHeight() > y \
            and self.x < x and self.x + self.getWidth() > x:
            elems.append(self.node)

        return elems
    
    def print(self, indent):
        t = self.text if len(self.text.split(" ")) < 7 else " ".join(self.text.split(" ")[0:7])
        print("-" * indent + "TextLayout at ({},{}) with height {} and text '{}'".format(self.x,self.y,self.getHeight(),t))