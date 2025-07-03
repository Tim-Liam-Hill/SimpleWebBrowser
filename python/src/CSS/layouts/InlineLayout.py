from src.HTML.HTMLParser import Element, Text
import logging
from dataclasses import dataclass
from src.CSS.layouts.LayoutConstants import layoutType, getFont
from src.CSS.layouts.Layout import Layout
import re
from src.CSS.layouts.LineLayout import LineLayout, RectLayout
from src.CSS.layouts.TextLayout import TextLayout
from src.CSS.CSSConstants import DEFAULT_LEADING

#from src.CSS.layouts.Line import TextBox, Box, Line
logger = logging.getLogger(__name__)


class InlineLayout(Layout):
    '''Holds and displays a sequence/tree of HTML elements with display inline.
    
    This class functions similar to a LineBox but simplified.
    '''
    
    def __init__(self, nodes,parent,previous):
        super().__init__(parent,previous)
        self.nodes = nodes
        self.lines = [] 
        self.y = self.parent.getYStart()
        self.x = self.parent.getXStart()

        self.curr_line = LineLayout(self, None)
        self.curr_line.y = self.parent.getYStart()
        self.curr_line.x = self.parent.getXStart()
        #does layout need its own display_list array? I think it can just get it from its children. 
    
    def getWidth(self):
        if self.width == None:
            self.width = self.parent.getContentWidth()

        return self.width
    
    def getContentWidth(self):
        if self.contentWidth == None:
            self.contentWidth = self.parent.getContentWidth()

        return self.contentWidth
  
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

        for node in self.nodes:
            self.recurse(node)

        #Remember to handle the last line!
        self.getNextLine() 
        
    def setCoordinates(self):
        self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
        if self.previous:
            self.y = self.previous.getYStart() #TODO: here aswell
        else: 
            self.y = self.parent.getY() #TODO: same here
        
    def recurse(self, node): #x start is always 0 since line's always start at leftmost edge in an inline display.
        '''Recurses through each child and creates lines of TextBoxes and Boxes 
        
        Each call returns cursor_x, start_y and lines index where:
        - cursor_x = the relative x position of text to begin laying out new text
        - start_y = the y value which the line ad lines_index starts
        - lines_index = tracks the last line which has not been flushed
        '''
        if isinstance(node, Text):
            return self.handleText(node)
        elif layoutType(node) == "inline": #TODO: handle inline-block and type input
            return self.handleInline(node)
        else: 
            return self.handleBlock(node)
        
    def getNextLine(self):
        '''Flushes the contents of the current line, appends it to lines and returns a new line to serve as the current line'''
        self.curr_line.flush()
        self.lines.append(self.curr_line)
        next = LineLayout(self, self.curr_line)
        next.x = self.x
        next.y = self.curr_line.getYStart()
        self.curr_line = next #just in case
        return next

    def handleText(self, node):
        no_newlines = re.sub(r'\t|\n','',node.text)
        squash_spaces = re.sub(r' +', ' ', no_newlines)
        words = squash_spaces.split(" ")
        font = getFont(node)
        curr_sentence = "" #create as few textboxes as possible, put lot's of words into a text box
        curr_w = 0
        cursor_x = self.curr_line.getWidth()
        for i in range(len(words)):
            word = words[i] if i == len(curr_sentence) == 0 else " {}".format(words[i]) #TODO: last word might be followed by a space
            w = font.measure(word)
            if curr_w + w + cursor_x < self.getContentWidth():
                curr_sentence += word 
                curr_w += w
            else:
                prev = self.curr_line.layoutFragments[-1] if len(self.curr_line.layoutFragments) > 0 else None
                t = TextLayout(self,prev,curr_sentence,font, node)
                self.curr_line.layoutFragments.append(t)
                self.curr_line = self.getNextLine()
                
                curr_sentence = words[i]
                curr_w = font.measure(word)
                cursor_x = 0

        if curr_sentence != "":
            prev = self.curr_line.layoutFragments[-1] if len(self.curr_line.layoutFragments) > 0 else None
            t = TextLayout(self,prev,curr_sentence,font, node)
            self.curr_line.layoutFragments.append(t)

            #TODO: check if we need an extra flush here to prevent text going off of screen.

        return 

    def handleInline(self,node):

        index = len(self.lines)
        curr_cursor_x = self.curr_line.getWidth()
        for child in node.children:
            self.recurse(child)

        if self.needsRect(node):
            #rect height is based on the font height for this node
            font = getFont(node)
            metrics = font.metrics()
            h = DEFAULT_LEADING * (metrics["descent"]+metrics["ascent"])

            from src.CSS.layouts.BlockLayout import BlockLayout
            for i in range(index, len(self.lines)): 
                if isinstance(self.lines[i], BlockLayout): #we could have interleaved BlockLayouts
                    y = self.lines[i].getYStart() if i < len(self.lines) else self.y
                    rect = RectLayout(self.x + curr_cursor_x,y,self.curr_line.getContentWidth()-curr_cursor_x,i == index, False ,node, h)
                    self.lines[i].rects.append(rect)
                    curr_cursor_x = 0

            #subtract curr_cursor_x since we may only have one line and we don't start that line
            y = self.lines[-1].getYStart() if len(self.lines) > 0 else self.y
            rect = RectLayout(self.x + curr_cursor_x,y,self.curr_line.getContentWidth()-curr_cursor_x,len(self.lines) == index, True,node, h)
            self.curr_line.rects.append(rect)
        return 

    def handleBlock(self,node):
        self.curr_line = self.getNextLine()
        from src.CSS.layouts.BlockLayout import BlockLayout #Python let's you do this and I hate it
        block = BlockLayout(node,self,self.lines[-1])
        block.layout()
        self.lines.append(block)

        return 

    def needsRect(self,node):
        '''Given a node, determines if it needs a surrounding rect for background color, border etc'''
        
        return isinstance(node, Element) and "background-color" in node.style and node.style["background-color"] != "transparent"

    def word(self, word, node):

        font = getFont(node)
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

    def paint(self): 
        cmds = []

        for line in self.lines:
                cmds.extend(line.paint())
            
        return cmds

    def __repr__(self):

        return "InlineLayout: x={} y={} width={} height={} num_nodes={}".format(self.x, self.y, self.getWidth(),self.getHeight(),len(self.nodes))

    def print(self, indent):
        print("-" * indent + "InlineLayout: width {} height {}".format(self.getWidth(), self.getHeight()))
        for line in self.lines:
            line.print(indent + 1)

    def click(self,x,y):
        '''Returns a list of one or more elements that bound the given x and y coordinates (document coordinates, NOT canvas coordinates)'''

        elems = []
        #TODO: more testing to verify clicking on InlineLayouts is correct
        # if self.getX() <= x < self.getX() + self.getWidth() and \
        #     self.getY() <= y < self.getY() + self.getHeight():
        #     elems.append(self.node)
        if self.y > y:
            return elems 
        for child in self.lines:
            elems.extend(child.click(x,y))

        return elems

# from src.HTML.HTMLParser import Element, Text
# import logging
# from dataclasses import dataclass
# from src.CSS.layouts.LayoutConstants import layoutType, getFont
# from src.CSS.layouts.Layout import Layout
# import re
# from src.CSS.layouts.Line import TextBox, Box, Line
# logger = logging.getLogger(__name__)

# class InlineLayout(Layout):
#     '''Holds and displays a sequence/tree of HTML elements with display inline.
    
#     This class functions similar to a LineBox but simplified.
#     '''
    
#     def __init__(self, nodes,parent,previous):
#         super().__init__(parent,previous)
#         self.nodes = nodes
#         self.lines = [] 
#         self.curr_line = Line() 
#         #does layout need its own display_list array? I think it can just get it from its children. 
    
#     def getWidth(self):
#         if self.width == None:
#             self.width = self.parent.getContentWidth()

#         return self.width
    
#     def getContentWidth(self):
#         if self.contentWidth == None:
#             self.contentWidth = self.parent.getContentWidth()

#         return self.contentWidth
  
#     #TODO: implement CSS
#     def getHeight(self):

#         if len(self.lines) == 0:
#             return 0
        
#         return sum([line.getHeight() for line in self.lines ])
    
#     def getX(self):

#         return self.x

#     def getY(self):

#         return self.y
    
#     def getXStart(self):

#         return self.x
    
#     def getYStart(self):

#         return self.y + self.getHeight()

#     #TODO: css to change initial values
#     #TODO: content width calcs and width calcs are confusing me rn.

#     def layout(self):
#         logger.debug("laying our InlineLayout with {} children".format(len(self.children)))
#         self.setCoordinates()

#         cursor_x = 0
#         start_y = self.getYStart()
#         lines_index = 0
#         for node in self.nodes:
#             cursor_x, start_y, lines_index = self.recurse(node,cursor_x, start_y, lines_index)

#         self.flush(lines_index,start_y)
#         #flush once we are done!!!
        
#     def setCoordinates(self):
#         self.x = self.parent.getXStart() #TODO: calculate x offset based on CSS (generic function will do for this)
#         if self.previous:
#             self.y = self.previous.getYStart() #TODO: here aswell
#         else: 
#             self.y = self.parent.getY() #TODO: same here
        
#     def recurse(self, node, cursor_x,  start_y, lines_index): #x start is always 0 since line's always start at leftmost edge in an inline display.
#         '''Recurses through each child and creates lines of TextBoxes and Boxes 
        
#         Each call returns cursor_x, start_y and lines index where:
#         - cursor_x = the relative x position of text to begin laying out new text
#         - start_y = the y value which the line ad lines_index starts
#         - lines_index = tracks the last line which has not been flushed
#         '''
#         if isinstance(node, Text):
#             return self.handleText(node,cursor_x), start_y, lines_index  
#         elif layoutType(node) == "inline":
#             return self.handleInline(node,cursor_x,start_y,lines_index)
#         else: 
#             return self.handleBlock(node,cursor_x,start_y,lines_index)

#     def handleText(self, node, cursor_x):
#         no_newlines = re.sub(r'\t|\n','',node.text)
#         squash_spaces = re.sub(r' +', ' ', no_newlines)
#         words = squash_spaces.split(" ")
#         font = getFont(node)
#         curr_sentence = "" #create as few textboxes as possible, put lot's of words into a text box
#         curr_w = 0
#         for i in range(len(words)):
#             word = words[i] if i == len(curr_sentence) == 0 else " {}".format(words[i]) #TODO: last word might be followed by a space
#             w = font.measure(word)
#             if curr_w + w + cursor_x < self.getContentWidth():
#                 curr_sentence += word 
#                 curr_w += w
#             else:
#                 self.curr_line.addText(TextBox(curr_sentence,font,cursor_x,curr_w,node))
#                 self.lines.append(self.curr_line)
#                 curr_sentence = words[i]
#                 curr_w = font.measure(word)
#                 self.curr_line = Line()
#                 cursor_x = 0
#         if curr_sentence != "":
#             self.curr_line.addText(TextBox(curr_sentence,font,cursor_x,curr_w,node))

#         cursor_x += curr_w    
#         return cursor_x

#     def handleInline(self,node,cursor_x,start_y,lines_index):

#         index = len(self.lines)
#         curr_cursor_x = cursor_x #that's a mouthful
#         for child in node.children:
#             cursor_x, start_y, lines_index = self.recurse(child, cursor_x,start_y,lines_index)

#         if self.needsBox(node):
#             for i in range(index, len(self.lines)): 
#                 if not isinstance(self.lines[i], Line): #we could have interleaved BlockLayouts
#                     break
#                 box = Box(curr_cursor_x, self.getContentWidth()-curr_cursor_x,i == index, False ,node) #boxes should go all the way to the end if they go onto multiple lines
#                 self.lines[i].addBox(box)
#                 curr_cursor_x = 0
#             #subtract curr_cursor_x since we may only have one line and we don't start that line
#             box = Box(curr_cursor_x, self.curr_line.getTextWidth() - curr_cursor_x,len(self.lines) == index, True ,node) #last box only goes up until content inside of it
#             self.curr_line.addBox(box)
#         return cursor_x, start_y, lines_index

#     def handleBlock(self,node,cursor_x, start_y,lines_index):
#         self.flush(lines_index,start_y)
#         from src.CSS.layouts.BlockLayout import BlockLayout #Python let's you do this and I hate it
#         block = BlockLayout(node,self,self.lines[-1])
#         block.layout()
#         self.lines.append(block)
#         start_y += block.getHeight()
#         lines_index = len(self.lines)
#         cursor_x = 0

#         return cursor_x, start_y, lines_index

#     def needsBox(self,node):
#         '''Given a node, determines if it needs a surrounding box for background color, border etc'''
        
#         return isinstance(node, Element) and "background-color" in node.style and node.style["background-color"] != "transparent"

#     def word(self, word, node):

#         font = getFont(node)
#         w = font.measure(word)
#         if self.cursor_x + w >= self.getContentWidth(): #TODO: what if overflow set? Also: do we still need HSTEP?
#             if not self.line and self.previous: 
#                 #this will only happen if we are an inline following on another inline
#                 #unless browser page is far too small in which case oops
#                 self.y = self.previous.getY() + self.previous.getHeight()
#                 self.cursor_y = 0
#                 self.cursor_x = 0
#             else: 
#                 self.flush()
            
#         vert_align = 1
#         match node.style.get('vertical-align', ""):
#             case "super":
#                 vert_align = 1.5
#             case "sub":
#                 vert_align = -1.5
#             case _:
#                 vert_align = 1
        
#         css_props = {
#             "vert_align": vert_align,
#             "color": node.style["color"]
#         }
            
#         self.line.append((self.cursor_x, word, font, css_props))
#         self.cursor_x += w + font.measure(" ")

#     def flush(self, lines_index, start_y):
#         '''Adds current line to lines, then starting with line at line_index, calculates baselines, height and sets y position for each line'''

#         self.lines.append(self.curr_line)
#         self.curr_line = Line()
#         for i in range(lines_index, len(self.lines)):
#             self.lines[i].flush(start_y)
#             start_y += self.lines[i].getHeight()
#         return start_y

#     def paint(self): 
#         cmds = []

#         for line in self.lines:
#             if isinstance(line, Line):
#                 cmds.extend(line.paint(self.x))
#             else:
#                 cmds.extend(line.paint())
            
        
#         return cmds

#     def __repr__(self):

#         return "InlineLayout: x={} y={} width={} height={} num_nodes={}".format(self.x, self.y, self.getWidth(),self.getHeight(),len(self.nodes))

#     def print(self, indent):
#         print("-" * indent + "InlineLayout: width {} height {}".format(self.getWidth(), self.getHeight()))
#         for line in self.lines:
#             line.print(indent + 1)

#     def click(self,x,y):
#         '''Returns a list of one or more elements that bound the given x and y coordinates (document coordinates, NOT canvas coordinates)'''

#         elems = []
#         #TODO: more testing to verify clicking on InlineLayouts is correct
#         # if self.getX() <= x < self.getX() + self.getWidth() and \
#         #     self.getY() <= y < self.getY() + self.getHeight():
#         #     elems.append(self.node)
#         if self.y > y:
#             return elems 
#         for child in self.lines:
#             if isinstance(child, Line):
#                 elems.extend(child.click(x,y, self.x))
#             else: 
#                 elems.extend(child.click(x,y))

#         return elems
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