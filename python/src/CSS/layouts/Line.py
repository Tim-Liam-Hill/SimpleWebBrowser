from src.CSS.CSSConstants import DEFAULT_LEADING
from src.Draw.Commands import DrawText, DrawRect
from src.CSS.layouts.Layout import Layout

class LineLayout(Layout):

    def __init__(self, parent, previous):
        super().__init__(parent,previous)

        self.layoutFragments = []
        self.rects = []

    def getWidth(self):
        pass

    def getContentWidth(self):
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

    def click(self,x,y):

        pass 

class TextLayout(Layout):

    def __init__(self, parent, previous):
        super().__init__(parent,previous)
    
    def getWidth(self):
        '''Returns the width of the layout object, taking into account CSS properties as necessary'''

        pass 


    def getContentWidth(self):
        '''Returns the width available inside this element for content
        
        This is used as the width for child classes (to be adjusted by CSS as necessary)
        '''

        pass
    
    def getHeight(self):
        '''Returns the height of the layout object, taking into account CSS properties as necessary
        
        Note that this height is inclusive of margin. 
        '''

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
        
        This is used to determine the top left hand corner of the rectangle containing the next element,
        NOT the relative position of the cursor within the line. 
        '''
        pass
    
    def getYStart(self):
        '''Returns absolute y value for where next text/element should be displayed
        
        NOTE: it seems like this should only be used for siblings, NOT children. That is to say: if an element has a previous element it should call this, if not it 
        should just call the getY. TODO: check this. 
        '''

        pass
    
    def layout(self):
        '''Forces this Layout Object to create all of its layout children'''

        pass 
    
    def paint(self):
        '''Returns the display list of draw commands necessary for this element to render its content on a canvas'''

        pass
    
    def click(self,x,y):
        '''Returns a list of one or more elements that bound the given x and y coordinates (document coordinates, NOT canvas coordinates).
        
        Returned elements are html elements, not Layout elements
        '''
        
        pass 

#TODO: should we inherit from layout?? 
class Line:
    '''A line is a collection of TextBoxes and Boxes that make up the content to be shown on a specific line within some inline block'''

    def __init__(self):
        self.text_boxes = [] 
        self.boxes = [] 
        self.height = 0 #children won't have vertical padding/margin affecting them per what chrome shows
        self.baseline = 0
        self.y = 0

    def addText(self, textBox):
        '''Append a text box to the list'''

        self.text_boxes.append(textBox)
    
    def addBox(self,box):
        '''Boxes are prepended since parents only add their boxes after their children but these should be displayed first'''

        self.boxes.insert(0,box)
    
    def getHeight(self):
        '''Determines the height of this line relative to all different font sizes present
        
        NOTE: this will only return a sensible value once this line has been flushed.
        '''
        #inline elements don't seem to be affected by margin/padding top and bottom so this should 
        #be a static return value right?? 
        return self.height
    
    def getBaseLine(self):
        '''Determines the baseline to use for displaying text based on the different font sizes present in text_boxes
        
        NOTE: this will only return a sensible value once this line has been flushed.
        '''

        return self.baseline

    def getTextWidth(self):
        '''Returns the relative x coordinate of the last textbox's right hand side which can be used to calculate the width of the CURRENT text elements of this line.'''
        if len(self.text_boxes) == 0:
            return 0
        return self.text_boxes[-1].rel_x + self.text_boxes[-1].width

    def getYStart(self):
        '''Only needed since a blocklayout might call this'''

        return self.y + self.height
    
    def getY(self):
        ''''''
        return self.y

    def flush(self, y):
        '''Given a starting y position, determines the baseline for each text node.'''
        self.y = y
        if len(self.text_boxes) == 0: 
            return 
        metrics = [tbox.font.metrics() for tbox in self.text_boxes]
        max_ascent = max([metric["ascent"] for metric in metrics])
        self.baseline = DEFAULT_LEADING * max_ascent
        max_descent = max([metric["descent"] for metric in metrics])
        self.height = (DEFAULT_LEADING * (max_ascent+max_descent))

    def paint(self,x):
        cmds = [] 

        #commands for boxes go first so we don't paint over text 
        for box in self.boxes:
            cmds.extend(box.paint(x, self.y, self.height))
        for text_box in self.text_boxes:
            cmds.extend(text_box.paint(x,self.y, self.baseline))
        return cmds

    def __eq__(self, value):
        if not isinstance(value, Line):
            return False 
        
        return self.text_boxes == value.text_boxes and self.boxes == value.boxes
    
    def __repr__(self):
        return "Line: height '{}' boxes '{}' text_boxes '{}'".format(self.getHeight(),len(self.boxes), len(self.text_boxes))
    
    def print(self, indent):
        print("-" * indent + self.__repr__())
        for b in self.boxes:
            print(" "*(indent) + "-" + b.__repr__())
        for b in self.text_boxes:
            print(" "*(indent) + "-" + b.__repr__())
    
    def click(self,x,y, parent_x):
        
        elems = [] 
        if self.y > y or self.y + self.getHeight() < y:
            return elems 
        
        for box in self.boxes:
            temp_x = box.getX() + parent_x
            if  temp_x < x and temp_x + box.getWidth() > x:
                elems.append(box.getNode())
        for text_box in self.text_boxes: 
            temp_x = text_box.getX() + parent_x
            if  temp_x < x and temp_x + text_box.getWidth() > x:
                elems.append(text_box.getNode())

        return elems 

class TextBox: 
    '''A textbox is essentially the atomic unit that makes up a portion of a line's text.
    
    All textboxes contain non-empty text. All textboxes will have absolute coordinates on which
    they are placed. 
    '''

    def __init__(self, text, font, x, width, node):
        '''Holds the data needed to print a portion of text

        x is relative coordinate to the x position of the line to which this TextBox belongs

        In order to calculate font position, the max_ascent and max_descent of all fonts must
        first be calculated, which can't be done when this box is created
        '''
        #TODO: rename to make clear it is relative coordinates
        self.text = text 
        self.font = font 
        self.rel_x = x  
        self.width = width
        self.node = node #save the parent node for this text in case we can use it for css implementation later (eg: first-word)
        #get css props from node

    def getWidth(self):
        return self.width
    
    def getX(self):
        return self.rel_x
    
    def getNode(self):
        return self.node

    def paint(self, x, y, baseline):
        cmds = []
        y1 = y + baseline - self.font.metrics("ascent")
        cmds.append(DrawText(x+self.rel_x,y1,self.text,self.font,self.node.style["color"]))
        return cmds
    
    def __repr__(self):
        t = self.text if len(self.text.split(" ")) < 7 else " ".join(self.text.split(" ")[0:7])
        return "TextBox: rel_x '{}' width '{}' text '{}'".format(self.rel_x,self.width, t)
    
    def __eq__(self, value):
        if not isinstance(value, Line):
            return False 
        
        return self.text_boxes == value.text_boxes and self.boxes == value.boxes

class Box:
    '''A box is the atomic unit that makes up the portion of a lines background color and borders
    
    
    A Box should never contain any text. Boxes are necessary since text for a given element may be split
    up by its children, but the background color for the parent (and border) should still persist through
    its children (that is, be placed behind).
    '''

    #TODO: rename to make clear it is relative coordinates
    def __init__(self,x,width, is_start, is_end, node):
        self.rel_x = x 
        self.is_start = is_start
        self.is_end = is_end
        self.width = width
        self.node = node 
    
    def getWidth(self):
        return self.width
    
    def getX(self):
        return self.rel_x
    
    def getNode(self):
        return self.node
    
    def paint(self, x, y, height):
        cmds = []
        x_start = x + self.rel_x
        x_end = x_start + self.width
        y_end = y + height
        cmds.append(DrawRect(x_start, y, x_end, y_end, self.node.style["background-color"])) 
        return cmds
    
    def __repr__(self):
        return "Box: rel_x '{}' width '{}' is_start '{}' is_end '{}'".format(self.rel_x,self.width,self.is_start, self.is_end)
