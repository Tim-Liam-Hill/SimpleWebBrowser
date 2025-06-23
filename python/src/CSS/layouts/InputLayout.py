from src.CSS.layouts.LayoutConstants import LayoutTypes, get_font
from src.CSS.layouts.Layout import Layout

DEFAULT_WIDTH_PX = 200

class InputLayout(Layout):
    def __init__(self, node, parent, previous):
        super().__init__(parent,previous)
        self.node = node

    def getWidth(self):
        #TODO: extract css and apply
        return DEFAULT_WIDTH_PX
        
    def getContentWidth(self):

        pass

 
    def calculateContentWidth(self):

        pass 


    def calculateWidth(self):

        pass 
    

    def getHeight(self):

        pass 

    def getX(self):


        pass 


    def getY(self):


        pass
    

    def getXStart(self):

        pass
    
    def getYStart(self):
  
        pass
    
    def layout(self):

        pass 
    
    def paint(self): 

        pass

    def getLayoutMode(self):
        '''Returns this objects CSS display property'''
        pass 


    def getElementsAt(self,x,y):

        pass 