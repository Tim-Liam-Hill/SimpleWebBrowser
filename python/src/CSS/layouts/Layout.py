from abc import ABC, abstractmethod

class Layout(ABC):
    '''The base class that all LayoutTypes inherit'''

    def __init__(self, parent, previous):
        self.x = 0 
        self.y = 0 
        
        '''Width of entire element including margin, padding and borders'''
        self.width = None
        
        '''Width available for inner text and other elements'''
        self.contentWidth = None
        self.parent = parent 
        self.previous = previous
        self.children = []
        
    @abstractmethod
    def getWidth(self):
        '''Returns the width of the layout object, taking into account CSS properties as necessary'''

        pass 

    @abstractmethod
    def getContentWidth(self):
        '''Returns the width available inside this element for content
        
        This is used as the width for child classes (to be adjusted by CSS as necessary)
        '''

        pass
    
    @abstractmethod
    def getHeight(self):
        '''Returns the height of the layout object, taking into account CSS properties as necessary
        
        Note that this height is inclusive of margin. 
        '''

        pass 

    @abstractmethod
    def getX(self):
        '''Returns the left hand start co-ordinate layout object, taking into account CSS properties as necessary
        
        This value will be for where the bounding rectangle starts and so is 'outside' any padding or border
        '''

        pass 

    @abstractmethod
    def getY(self):
        '''Returns the vertical start co-ordinate layout object, taking into account CSS properties as necessary
        
        This value will be for where the bounding rectangle starts and so is 'outside' any padding or border
        '''

        pass
    
    @abstractmethod
    def getXStart(self):
        '''Returns the abolute x value for where the next text/element should be displayed.
        
        This is used to determine the top left hand corner of the rectangle containing the next element,
        NOT the relative position of the cursor within the line. 
        '''
        pass
    
    @abstractmethod
    def getYStart(self):
        '''Returns absolute y value for where next text/element should be displayed
        
        '''

        pass
    
    @abstractmethod
    def layout(self):
        '''Forces this Layout Object to create all of its layout children'''

        pass 
    
    @abstractmethod
    def paint(self):
        '''Returns the display list of draw commands necessary for this element to render its content on a canvas'''

        pass
    
    @abstractmethod
    def click(self,x,y):
        '''Returns a list of one or more elements that bound the given x and y coordinates (document coordinates, NOT canvas coordinates).
        
        Returned elements are html elements, not Layout elements
        '''
        
        pass 