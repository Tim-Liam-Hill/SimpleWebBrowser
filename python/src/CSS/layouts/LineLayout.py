from src.CSS.CSSConstants import DEFAULT_LEADING
from src.CSS.layouts.Layout import Layout
from src.Draw.Commands import DrawRect
from src.CSS.layouts.TextLayout import TextLayout

class LineLayout(Layout):
    '''Holds all of the boxes that make up a single line within an Inline Formatting context'''

    def __init__(self, parent, previous):
        super().__init__(parent,previous)

        self.layoutFragments = []
        self.rects = []

    def getWidth(self):

        return sum([e.getWidth() for e in self.layoutFragments])
        
   

    def getContentWidth(self):
        '''Content width and width of a line are synonymous'''

        return self.getWidth()

    def getHeight(self):

        #TODO: cache height
        height = max([child.getHeight() for child in self.layoutFragments] + [0])

        return height

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getXStart(self):
        return self.x + self.getWidth()

    def getYStart(self):

        return self.y + self.getHeight()
    
    def flush(self):
        '''Flushes the line such that all text nodes are given the correct y and baseline coordinates
        
        The maximum height is first used to determine line height, after which baseline is made to be the midpoint.
        TextNodes use their own vert-align to determine their layout from their on.

        To determine max height, the max height for text nodes and max height for non-text nodes is determined and compared.
        The maximum height for text nodes is based on the descent and ascent of all textnodes, after which leading is taken into account.
        '''

        textFrags = [t for t in self.layoutFragments if isinstance(t,TextLayout)]
        metrics = [child.font.metrics() for child in textFrags]
        maxAscent = max([metric["ascent"] for metric in metrics] + [0])
        maxDescent = max([metric["descent"] for metric in metrics] + [0])
        fontMaxHeight = (DEFAULT_LEADING * (maxAscent+maxDescent))

        layoutFrags = [t for t in self.layoutFragments if not isinstance(t,TextLayout)]
        layoutMaxHeight = max([child.getHeight() for child in layoutFrags] + [0])

        #Set baseline for every text node
        #for now we won't worry about anything too elaborate regarding
        #keeping the baseline for text fragments in line with that for lines
        #of the potential block layouts. Later on this can be done but it will
        #require a line keeping track of its own baseline so that parents
        # can iterate down the tree to determine childs baseline
        baseline = DEFAULT_LEADING * maxAscent
        if layoutMaxHeight > fontMaxHeight:
            baseline = fontMaxHeight - (DEFAULT_LEADING * maxDescent)

        cursorX = self.x
        for child in self.layoutFragments:
            if isinstance(child, TextLayout):
                child.baseline = baseline
                child.y = self.y 
                child.x = cursorX
            cursorX += child.getWidth()
    
    def layout(self):

        for child in self.layoutFragments:
            child.layout() #ensures any inline block or block elements get laid out correctly
    
    def paint(self):

        cmds = []
        for r in self.rects:
            cmds.extend(r.paint())
        
        for obj in self.layoutFragments:
            cmds.extend(obj.paint())

        return cmds

    def click(self,x,y):

        elems = []
        if self.y > y:
            return elems 
        for child in self.layoutFragments:
            elems.extend(child.click(x,y))

        return elems
    
    def print(self,indent):
        print("-" * indent + "LineLayout at ({},{}) with width {} and height {}".format(self.x,self.y,self.getWidth(),self.getHeight()))
        for f in self.layoutFragments:
            f.print(indent+1)

        for r in self.rects:
            r.print(indent+1)  


class RectLayout: 

    def __init__(self,x,y, width,isStart,isEnd,node,height):
        self.x = x
        self.y = y
        self.width = width 
        self.isStart = isStart
        self.isEnd = isEnd
        self.node = node 
        self.height = height


    def paint(self):
        cmds = []
        xEnd = self.x+self.width
        yEnd = self.y + self.height
        cmds.append(DrawRect(self.x, self.y, xEnd, yEnd, self.node.style["background-color"])) 
        return cmds
    
    def print(self, indent):
        print("-" * indent + "RectLayout at ({},{}) with width {} and height {}".format(self.x,self.y,self.width,self.height))