import tkinter
from src.HTMLParser import Element, Text
import tkinter.font
import logging
from dataclasses import dataclass
from src.layouts.LayoutConstants import LayoutTypes, DrawRect, DrawText, VSTEP, HSTEP, get_font,DEFAULT_LEADING
from src.layouts.Layout import Layout
logger = logging.getLogger(__name__)

@dataclass 
class InlineTextInfo:
    def __init__(self, x, y, word, font, color):
        self.x = x 
        self.y = y 
        self.word = word 
        self.font = font 
        self.color = color

@dataclass
class InlineRectInfo: 
    def __init__(self, x,y,x2,y2,color): #this may need to hold css properties instead of color eventually?
        self.x = x 
        self.y = y 
        self.background_color = color
        self.x2 = x2 
        self.y2 = y2


class InlineLayout(Layout):
    '''Holds and displays a sequence/tree of HTML elements with display inline.
    
    This class functions similar to a LineBox but simplified.
    '''
    
    def __init__(self, nodes,parent,previous):
        super().__init__(parent,previous)
        self.nodes = nodes
        self.lines = [] #2d array
        #does layout need its own display_list array? I think it can just get it from its children. 
    
    def getWidth(self):

        return self.width
    
    def getContentWidth(self):

        return self.content_width
  
    def calculateContentWidth(self):

        return self.parent.getContentWidth()

    def calculateWidth(self):

        return self.parent.getContentWidth()
    
    #TODO: implement CSS
    def getHeight(self):

        return self.cursor_y
    
    def getX(self):

        return self.x

    def getY(self):

        return self.y
    
    def getXStart(self):

        return self.cont_x
    
    def getYStart(self):

        return self.cont_y

    #TODO: css to change initial values
    #TODO: content width calcs and width calcs are confusing me rn.

    def layout(self):
        logger.debug("laying our InlineLayout with {} children".format(len(self.children)))
        self.setCoordinates()
        self.content_width = self.calculateContentWidth()

        #2 pass algorithm: the first pass we make sure all lines have the text that fits on them and the 
        #boxes for backgrounds and such. Second pass we set the height for every Line. 

        cursor_x, x_cont, y_cont, lines_index = 0
        for node in self.nodes:
            cursor_x, x_cont, y_cont, lines_index = self.recurse(node,0, self.getYStart(), 0)

        #flush once we are done!!!
        #then we go through and populate the starting y and height for each element
        
    def setCoordinates(self):
        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here
        
    def recurse(self, node, cursor_x,  start_y, lines_index): #x start is always 0 since line's always start at leftmost edge in an inline display.
        ''''''

        #DON'T CHANGE THE CSS PROPS OBJECT!! IT WILL BE (potentially) SHARED
        #any extra data related to css should be applied to a different dict (which I will get to eventually)

        #start with my node
        #if is text, starts splitting by word, create boxes for each word 
        #if cursor_x + width greater than width, flush 
        #flush handles setting the ascent and such
        #if we encounter non-text node, recurse that node so things are saved on stack
        # if we encounter block element, flush, add it to its own line then update 
        #coordinates to continue from. 

        '''* anytime you finish a line, you prepend your border commands to the lines array
* this way, the parent will keep track of whether to show a border on left/right and childrens borders will also still show in correct order (they will be drawn after parent's border)
* could also do background colors like this I suppose. Yeah, this is exactly how we will do things. '''


        #TODO: test an empty span <span></span> and make sure we don't die if this is what we have. 
        if isinstance(node, Text):
            words = node.text.split(" ")
            font = self.getFont(node)
            for i in range(len(words)):
                pass

        elif Layout.layoutType(node) == "inline":
            #record start x and y here for any background rects we need to add (also lines_index)
            #get index within current line.
            for node in self.nodes:
                cursor_x = self.recurse(node, cursor_x)
            #once we are done recursing through our children we need to come back and put in the boxes 
            #for background color and such. For the line we were initially on we can find the length of 
            #any boxes by taking the x value of the last element and adding its width
            #then for every line between our lines_index and last line index, add a box. Don't worry about height at this stage.
        else: #technically this is an error on author's part, inline element shouldn't have block child. 
            # finish laying out all lines laid out till this point
            # lay out the block element
            # record the new x and y start and index of lines to continue laying out 

            pass 

        return cursor_x, start_y, lines_index

    def word(self, word, node):

        font = self.getFont(node)
        w = font.measure(word)
        if self.cursor_x + w >= self.getContentWidth(): #TODO: what if overflow set? Also: do we still need HSTEP?
            if not self.line and self.previous: 
                #this will only happen if we are an inline following on another inline
                #unless browser page is far too small in which case oops
                self.y = self.previous.getY() + self.previous.getHeight()
                self.cursor_y = 0
                self.cursor_x = 0
            else: 
                self.flush()
            
        vert_align = 1
        match node.style.get('vertical-align', ""):
            case "super":
                vert_align = 1.5
            case "sub":
                vert_align = -1.5
            case _:
                vert_align = 1
        
        css_props = {
            "vert_align": vert_align,
            "color": node.style["color"]
        }
            
        self.line.append((self.cursor_x, word, font, css_props))
        self.cursor_x += w + font.measure(" ")

    def getFont(self, node):
        '''Used to create the font needed to render text, taking into account css properties'''

        weight = node.style["font-weight"]
        style = node.style["font-style"]
        family = node.style["font-family"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)

        if node.style.get('font-size', " ")[-1] == "%": #TODO: expand and ensure this works. 
            size *= 1/float(node.style.get('font-size'))

        return get_font(size, weight, style, family)

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font, css_props in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y +  DEFAULT_LEADING * max_ascent
        text_display_list = []

        for rel_x, word, font, css_props in self.line:
            x = self.x + rel_x
            y =  self.y + baseline - (css_props["vert_align"] * font.metrics("ascent"))
            text_display_list.append(InlineTextInfo(x, y, word, font,css_props["color"]))
        max_descent = max([metric["descent"] for metric in metrics])
        
        if self.node.style.get("background-color") != "transparent": #TODO: adjust offsets once we have padding etc
            self.display_list.append(InlineRectInfo(self.line_start_x, self.y + self.cursor_y,  self.cursor_x, self.y + self.cursor_y + DEFAULT_LEADING*max_descent +  max_ascent,self.node.style.get("background-color")))

        #Rects must be rendered before text otherwise text gets covered 
        self.display_list = self.display_list + text_display_list

        self.cursor_y = baseline + DEFAULT_LEADING * max_descent
        self.cursor_x = 0
        self.line_start_x = self.x 

        self.line = []

        def paint(self): 
            cmds = []
            
            return cmds

    def getLayoutMode(self):

        return LayoutTypes.Inline

    def __repr__(self):

        return "InlineLayout: x={} y={} width={} height={} num_nodes={}".format(self.x, self.y, self.width,self.getHeight(),len(self.nodes))

    def print(self, indent):
        print("-" * indent + "InlineLayout: width {} height {}".format(self.width, self.getHeight()))


'''
ALGORITHM:

1. Start recursing through your children.
- Each child gets to know the cursor_x, current_y start and current index in lines from where we need to start flushing (ie: last non-flushed line)
- calculating heights from
2. If we have a text node:
    2.1 get font
    2.2 split based on spaces
    2.3 create a text box for each space 
    2.4 while cursor_x is smaller than content width + width, add text_boxes to current line (ie: last line in lines array)
    2.5 if we would go over this line, make a new line
    2.6 Only prepend spaces to words if they aren't the first word in the list
    2.7 Make sure to add css properties 
    2.8 Return the same lines_start index, same y_start index but the updated cursor_x. Child knows where to continue based on latest line in array.
3. If we encounter an inline node:
    3.1 Record the line we are currently at now along with the curr_x value 
    3.2 Recurse through each of our children 
    3.3 Starting at the line before recurse up to and including the current line, add boxes IF background color/border set
        3.3.1 For the first box, set is_start to true 
        3.3.2 For the first box, cursor_x is we saved is start and end is cursor x of last text in the line + its width (plus some padding??)
        3.3.3 For last box set is_start to true 
        3.3.4 For last box, cursor_x that is returned is end x and start x (relative) is 0
4. If we encounter a box layout, flush every line from the line_start index to the last line in the array. 
    4.1 flush each line from line_start index till end of lines
        4.1.1 Get the height of the line by calculating the baseline for all text then adding padding as necessary
        4.1.2 Set this lines y value based on the start y_start
        4.1.3 add y_start to height to get next y_start
        4.1.4 repeat for all lines 
    4.2 Layout the block layout 
    4.3 Get its height
    4.4 Update the line_start index to be the end of the lines array (len(self.lines))
5. Once done, 

'''