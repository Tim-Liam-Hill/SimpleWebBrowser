from abc import ABC, abstractmethod

class Layout(ABC):
    '''The base class that all LayoutTypes inherit'''

    def __init__(self, parent, previous):
        self.x = 0 
        self.y = 0 
        
        '''Width of entire element including margin, padding and borders'''
        self.width = 0
        
        '''Width available for inner text and other elements'''
        self.content_width = 0
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
    def calculateContentWidth(self):
        '''Calculates the width of this element available for inner content'''

        pass 

    @abstractmethod
    def calculateWidth(self):
        '''Calculates the entire width of this element, css and content included'''

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
        
        NOTE: it seems like this should only be used for siblings, NOT children. That is to say: if an element has a previous element it should call this, if not it 
        should just call the getY. TODO: check this. 
        '''

        pass
    
    # def getXContinue(self):
    #     '''Determines where on the current ystart line text content should continue
        
    #     This method has the default behaviour of starting text at the beginning of the content rectangle
    #     and is overridden as necessary eg: by inline class.
    #     '''

    #     return self.getXStart()

    @abstractmethod
    def layout(self):
        '''Forces this Layout Object to create all of its layout children'''

        pass 
    
    @abstractmethod
    def paint(self): #TODO:Should this be abstract or can we make this generic? 
        '''Returns the display list of draw commands necessary for this element to render its content on a canvas'''

        pass

    #TODO: do we even need this method?? 
    @abstractmethod
    def getLayoutMode(self):
        '''Returns this objects CSS display property'''
        pass 

    def layoutType(node):
        '''Given an html element node, determines its layout type'''

        if "display" in node.style and node.style.get("display") in ["block"]:
            return node.style.get("display")

        return "inline"