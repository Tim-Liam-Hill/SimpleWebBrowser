import tkinter
from src.HTMLParser import Element, Text
import tkinter.font
import logging
from dataclasses import dataclass
from src.layouts.LayoutConstants import LayoutTypes, get_font
from src.layouts.Layout import Layout
import re
from src.layouts.Box import TextBox, Box, Line
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
        self.lines = [] 
        self.curr_line = Line() 
        #does layout need its own display_list array? I think it can just get it from its children. 
    
    def getWidth(self):

        return self.width
    
    def getContentWidth(self):
        '''If this is resource intensive with calculations mayhaps cache??'''

        return self.content_width
  
    def calculateContentWidth(self):

        return self.parent.getContentWidth()

    def calculateWidth(self):

        return self.parent.getContentWidth()
    
    #TODO: implement CSS
    def getHeight(self):

        if len(self.lines) == 0:
            return 0
        
        return sum([line.getHeight() for line in self.lines ])
    
    def getX(self):

        return self.x

    def getY(self):

        return self.y
    
    def getXStart(self):

        return self.x
    
    def getYStart(self):

        return self.y + self.getHeight()

    #TODO: css to change initial values
    #TODO: content width calcs and width calcs are confusing me rn.

    def layout(self):
        logger.debug("laying our InlineLayout with {} children".format(len(self.children)))
        self.setCoordinates()
        self.content_width = self.calculateContentWidth()

        #2 pass algorithm: the first pass we make sure all lines have the text that fits on them and the 
        #boxes for backgrounds and such. Second pass we set the height for every Line. 

        cursor_x = 0
        start_y = self.getYStart()
        lines_index = 0
        for node in self.nodes:
            cursor_x, start_y, lines_index = self.recurse(node,cursor_x, start_y, lines_index)

        self.flush(lines_index,start_y)
        #flush once we are done!!!
        #then we go through and populate the starting y and height for each element
        
    def setCoordinates(self):
        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here
        
    def recurse(self, node, cursor_x,  start_y, lines_index): #x start is always 0 since line's always start at leftmost edge in an inline display.
        '''Recurses through each child and creates lines of TextBoxes and Boxes 
        
        Each call returns cursor_x, start_y and lines index where:
        - cursor_x = the relative x position of text to begin laying out new text
        - start_y = the y value which the line ad lines_index starts
        - lines_index = tracks the last line which has not been flushed
        '''
        #TODO: break these up into individual functions
        #TODO: test an empty span <span></span> and make sure we don't die if this is what we have. 
        if isinstance(node, Text):
            no_newlines = re.sub(r'\t|\n','',node.text)
            squash_spaces = re.sub(r' +', ' ', no_newlines)
            words = squash_spaces.split(" ")
            font = self.getFont(node)
            curr_sentence = "" #create as few textboxes as possible, put lot's of words into a text box
            curr_w = 0
            for i in range(len(words)):
                word = words[i] if i == len(curr_sentence) == 0 else " {}".format(words[i]) #TODO: last word might be followed by a space
                w = font.measure(word)
                if curr_w + w + cursor_x < self.getContentWidth():
                    curr_sentence += word 
                    curr_w += w
                else:
                    self.curr_line.addText(TextBox(curr_sentence,font,cursor_x,curr_w,node))
                    self.lines.append(self.curr_line)
                    curr_sentence = words[i]
                    curr_w = font.measure(word)
                    self.curr_line = Line()
                    cursor_x = 0
            if curr_sentence != "":
                self.curr_line.addText(TextBox(curr_sentence,font,cursor_x,curr_w,node))

            cursor_x += curr_w    

        elif Layout.layoutType(node) == "inline":
            index = len(self.lines)
            curr_cursor_x = cursor_x #that's a mouthful
            for child in node.children:
                cursor_x, start_y, lines_index = self.recurse(child, cursor_x,start_y,lines_index)

            if self.needsBox(node):
                for i in range(index, len(self.lines)): 
                    if not isinstance(self.lines[i], Line): #we could have interleaved BlockLayouts
                        break
                    box = Box(curr_cursor_x, self.getContentWidth()-curr_cursor_x,i == index, False ,node) #boxes should go all the way to the end if they go onto multiple lines
                    self.lines[i].addBox(box)
                    curr_cursor_x = 0
                #subtract curr_cursor_x since we may only have one line and we don't start that line
                box = Box(curr_cursor_x, self.curr_line.getTextWidth() - curr_cursor_x,len(self.lines) == index, True ,node) #last box only goes up until content inside of it
                self.curr_line.addBox(box)
        elif Layout.layoutType(node) == "none":
            pass
        else: 
            self.flush(lines_index,start_y)
            from src.layouts.BlockLayout import BlockLayout #hopefully this don't cause no circular dependencies but we will see
            block = BlockLayout(node,self,self.lines[-1])
            block.layout()
            self.lines.append(block)
            start_y += block.getHeight()
            lines_index = len(self.lines)
            cursor_x = 0

        return cursor_x, start_y, lines_index

    def needsBox(self,node):
        '''Given a node, determines if it needs a surrounding box for background color, border etc'''
        
        return isinstance(node, Element) and "background-color" in node.style and node.style["background-color"] != "transparent"

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
        try:
            size = int(float(node.style["font-size"][:-2]) * .75)
        except:
            size = 26

        if node.style.get('font-size', " ")[-1] == "%": #TODO: expand and ensure this works. 
            size *= 1/float(node.style.get('font-size'))

        return get_font(size, weight, style, family)

    def flush(self, lines_index, start_y):
        '''Adds current line to lines, then starting with line at line_index, calculates baselines, height and sets y position for each line'''

        self.lines.append(self.curr_line)
        self.curr_line = Line()
        for i in range(lines_index, len(self.lines)):
            self.lines[i].flush(start_y)
            start_y += self.lines[i].getHeight()
        return start_y

    def paint(self): 
        cmds = []

        for line in self.lines:
            if isinstance(line, Line):
                cmds.extend(line.paint(self.x))
            else:
                cmds.extend(line.paint())
            
        
        return cmds

    def getLayoutMode(self):

        return LayoutTypes.Inline

    def __repr__(self):

        return "InlineLayout: x={} y={} width={} height={} num_nodes={}".format(self.x, self.y, self.width,self.getHeight(),len(self.nodes))

    def print(self, indent):
        print("-" * indent + "InlineLayout: width {} height {}".format(self.width, self.getHeight()))
        for line in self.lines:
            line.print(indent + 1)


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