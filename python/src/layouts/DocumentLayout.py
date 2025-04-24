from src.layouts.BlockLayout import BlockLayout
import logging
logger = logging.getLogger(__name__)


class DocumentLayout: #edge case that doesn't need to inherit everything from Layout
    '''The root element of all HTMLElement trees
    
    There should be exactly one such element in every tree. It's responsibility is simply
    to kick off the process of laying out child elements.
    '''
    
    def __init__(self, node, max_width):
        self.node = node
        self.parent = None
        self.children = []
        self.max_width = max_width

    def layout(self):
        self.width = self.max_width
        self.x = 0
        self.y = 0

        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()
        self.height = child.getHeight()
    
    def getXStart(self):
        return 0

    def getY(self):
        return 0

    def getContentWidth(self):
        return self.max_width

    def paint(self):
        return []

    def __repr__(self):
        return "DocumentLayout: max_width {}".format(self.max_width)

    def print(self):

        print("Document Layout: width {} and height {}".format(self.width,self.height))
        self.child.print(1)