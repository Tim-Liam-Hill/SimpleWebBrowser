
#TODO: standardize and cleanup this file: duplicate implementations can be reduced


class DrawText:
    '''Represents the command needed to render text onto a Tkinter canvas'''

    #TODO: is there a more elegant way to handle constant text vs getting text from node?
    def __init__(self, x1, y1, text, font, color, node = None):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
        self.color = color #TODO: do we need this or should we always take in node?
        self.node = node

    def getTextToRender(self):

        #TODO: consider handling placeholder text for input tags
        if self.node:
            v = self.node.attributes.get("value")
            return v if not v == None else ""
        else:
            return self.text

    def execute(self, scroll, canvas):

        t = self.getTextToRender()

        canvas.create_text(
            self.left, self.top - scroll,
            text=t,
            font=self.font,
            anchor='nw',
            fill=self.color)

    def __repr__(self):
        return "DrawText: x '{}' y '{}-{}' color '{}' text '{}'".format(self.left,self.top,self.bottom,self.color, self.text)

class DrawRect:
    ''''''

    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    #TODO: borders
    def execute(self, scroll, canvas):
        '''Represents the command needed to render rectangle onto a Tkinter canvas'''

        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=0,
            fill=self.color)

    def __repr__(self):
        return "DrawRect: x '{}->{}' y '{}-{}' color '{}'".format(self.left,self.right,self.top,self.bottom,self.color)
    
#TODO: document
class DrawOutline:
    def __init__(self, rect, color, thickness):
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            width=self.thickness,
            outline=self.color)
        
class DrawLine:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.rect = Rect(x1, y1, x2, y2)
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_line(
            self.rect.left, self.rect.top - scroll,
            self.rect.right, self.rect.bottom - scroll,
            fill=self.color, width=self.thickness)
        
#TODO: mayhaps a directory for shapes? 
#TODO: standardize the functions used to draw things onto a canvas
class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        
    def contains_point(self, x, y):
        return x >= self.left and x < self.right \
            and y >= self.top and y < self.bottom