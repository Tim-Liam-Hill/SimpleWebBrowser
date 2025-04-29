from src.CSS.layouts.BlockLayout import BlockLayout
import logging
logger = logging.getLogger(__name__)


class DocumentLayout: #edge case that doesn't need to inherit everything from Layout
    '''The root element of all HTMLElement trees
    
    There should be exactly one such element in every tree. It's responsibility is simply
    to kick off the process of laying out child elements.
    '''
    
    def __init__(self, node, max_width, y_start):
        self.node = node
        self.parent = None
        self.children = []
        self.max_width = max_width
        self.width = self.max_width
        self.x = 0
        self.y = y_start

    def layout(self):


        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()

    #TODO: could speed this up if needed    
    def getHeight(self):
        return self.children[0].getHeight()

    def getXStart(self):
        return 0

    def getY(self):
        return self.y

    def getContentWidth(self):
        return self.max_width

    def paint(self):
        display_list = []
        for child in self.children:
            display_list.extend(child.paint())
        return display_list

    def __repr__(self):
        return "DocumentLayout: max_width {}".format(self.max_width)

    def print(self):

        print("Document Layout: width {} and height {}".format(self.width,self.getHeight()))
        self.children[0].print(1)
    
    def getElementsAt(self,x,y):

        return self.children[0].getElementsAt(x,y)