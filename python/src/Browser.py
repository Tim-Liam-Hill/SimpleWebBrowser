import tkinter
from URL import URL, lex
import sys
import logging
logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
NEWLINE_STEP_FACTOR = 1.2
SCROLL_STEP = 100

class Browser:
    def __init__(self):
        # Initialize instance variables--------
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.urlHandler = URL()
        self.display_list = []
        self.scroll = 0
        self.doc_height = HEIGHT #keeps track of the height of the document

        #event handlers
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mouseWheelScroll)
        self.window.bind("<Button-4>", self.linuxWheelScroll)
        self.window.bind("<Button-5>", self.linuxWheelScroll)
        #--------------------------------------

    def load(self, url):
        body = self.urlHandler.request(url)
        text = lex(body, self.urlHandler.viewSource)
        self.display_list, self.doc_height = layout(text)
        logger.info(self.doc_height)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y- self.scroll, text=c)

    #TODO: make sure we don't go beyond content
    def scrolldown(self, e):
        logger.debug("Scrolling down")
        self.scroll = min(self.scroll + SCROLL_STEP, self.doc_height - HEIGHT)
        self.draw()
    
    def scrollup(self, e):
        logger.debug("Scrolling up")
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        self.draw()
    
    def mouseWheelScroll(self, e):
        #TODO: implement for Windows and Mac since they have differences
        print(e)
        logger.info(e)
    
    def linuxWheelScroll(self, e):
        if e.num == 5: #scroll down
            self.scrolldown(e)
        elif e.num == 4: #scroll up
            self.scrollup(e)
        

def layout(text):
    display_list = []    
    cursor_x, cursor_y = HSTEP, VSTEP
   
    for c in text:
        if c == '\n':
            cursor_y += NEWLINE_STEP_FACTOR * VSTEP
            cursor_x = HSTEP
            continue
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP

    return display_list, cursor_y

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    Browser().load(sys.argv[1])
    tkinter.mainloop()