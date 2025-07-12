from src.CSS.layouts.BlockLayout import BlockLayout

class InlineBlockLayout(BlockLayout):

    def __init__(self,node,parent,previous):
        super().__init__(node,parent,previous)
        self.contentWidth = self.parent.getContentWidth()
   
    def __repr__(self):

        return "InlineBlockLayout: x={} y={} width={} height={} num_nodes={}".format(self.x, self.y, self.getWidth(),self.getHeight(),len(self.nodes))

    def setCoordinates(self):
        self.x = self.previous.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        
        if self.previous:
            self.y = self.previous.getY() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here. also, NOT Y start here. if we are a block element and our parent was a block element and no previous then we start at their start

    def getContentWidth(self):
        return self.contentWidth

    def getWidth(self):

        #TODO: css and such

        if len(self.children[0].lines) > 1:
            return self.getContentWidth()

        return max([child.getWidth() for child in self.children])
    
    def getXStart(self):

        return self.x + self.getWidth()

    def getHeight(self):

        height = sum([child.getHeight() for child in self.children] + [0]) #TODO: should this ever be 0??? 

        #height = self.y- (self.children[-1].getHeight() + self.children[-1].getY())
        #TODO: add our own borders and padding

        return height

    def print(self, indent):
        print("-" * indent + "InlineBlockLayout at ({},{}) with width {} height {}".format(self.x, self.y,self.getWidth(), self.getHeight()))
        for child in self.children:
            child.print(indent + 1)