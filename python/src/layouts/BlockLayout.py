'''BlockLayout'''

from Layout import Layout
import LayoutTypes

class BlockLayout(Layout):
    '''The implementation for "block" css display property'''
    
    def __init__(self, node, parent, previous):
        super().__init__(node,parent,previous)

    def getWidth(self):
        '''Returns the width of the layout object, taking into account CSS properties as necessary'''

        pass 
    
    def getHeight(self):
        '''Returns the height of the layout object, taking into account CSS properties as necessary'''

        pass 

    def getX(self):
        '''Returns the left hand start co-ordinate layout object, taking into account CSS properties as necessary
        
        This value will be for where the bounding rectangle starts and so is 'outside' any padding or border
        '''

        pass 

    def getY(self):
        '''Returns the vertical start co-ordinate layout object, taking into account CSS properties as necessary
        
        This value will be for where the bounding rectangle starts and so is 'outside' any padding or border
        '''

        pass

    def getXStart(self):
        '''Returns the abolute x value for where the next text/element should be displayed.
        
        This allows us to handle cases for when text follows on the same line as the previous element for example.
        '''
        pass

    def layout(self):
        '''Forces this Layout Object to create all of its layout children'''

        pass 
    
    def paint(self): #TODO:Should this be abstract or can we make this generic? 
        '''Populates the draw commands in the display list necessary for this element to render its content on a canvas'''

        pass

    def getDisplayList(self):
        '''Returns the display list for this object'''

        pass

    def getLayoutMode(self):
        '''Returns this objects CSS display property'''
        pass 
