import tkinter
import tkinter.font
from Layout import Layout, HSTEP, VSTEP
from URL import URL, Text, lex
from HTMLParser import HTMLParser
import sys
import logging
logger = logging.getLogger(__name__)

INIT_WIDTH, INIT_HEIGHT = 800, 600
NEWLINE_STEP_FACTOR = 1.2
SCROLL_STEP = 100
SCROLLBAR_WIDTH = 24
INNER_SCROLLBAR_WIDTH = 18
INNER_SCROLLBAR_HEIGHT = 40
SCROLLBAR_COLOR = 'deep sky blue'
INNER_SCROLLBAR_COLOR = 'sky blue'

class Browser:
    def __init__(self):
        # Initialize instance variables--------
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=INIT_WIDTH,
            height=INIT_HEIGHT
        )
        self.canvas.pack(fill="both", expand=1)
        self.urlHandler = URL()
        self.display_list = []
        self.scroll = 0
        self.window_height = INIT_HEIGHT #height of rendered window
        self.window_width = INIT_WIDTH
        self.doc_height = self.window_height #keeps track of the height of the document (DOM, not tkinter window)
        self.tokens = []

        #event handlers
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mouseWheelScroll)
        self.window.bind("<Button-4>", self.linuxWheelScroll)
        self.window.bind("<Button-5>", self.linuxWheelScroll)
        self.window.bind("<Configure>", self.resize)
        #--------------------------------------

    def load(self, url):
        content = self.urlHandler.request(url)
        #TODO: need a case for view-source!!!!!
        self.root_node = HTMLParser(content).parse(self.urlHandler.viewSource)
        layout = Layout(self.root_node, self.widthForContent())
        self.display_list = layout.display_list
        self.doc_height = layout.cursor_y
        self.draw()

    def widthForContent(self):
        return self.window_width - SCROLLBAR_WIDTH

    def draw(self):

        self.canvas.delete("all")
        
        for x, y, word, font in self.display_list:
            if y > self.scroll + self.window_height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y- self.scroll, text=word, font=font, anchor='nw')

        #scrollbar
        if self.doc_height > self.window_height:
            self.canvas.create_rectangle(self.widthForContent(),  0, self.window_width, self.window_height, fill=SCROLLBAR_COLOR)
            #start y can go to maximum of self.window_height - INNER_SCROLL_HEIGHT
            proportionScrolled = (self.scroll )/(self.doc_height- self.window_height)
            
            start_y = min( proportionScrolled * (self.window_height-INNER_SCROLLBAR_HEIGHT), self.window_height-INNER_SCROLLBAR_HEIGHT)
            self.canvas.create_rectangle(self.window_width -  INNER_SCROLLBAR_WIDTH - (SCROLLBAR_WIDTH - INNER_SCROLLBAR_WIDTH)/2,  start_y, self.window_width - (SCROLLBAR_WIDTH - INNER_SCROLLBAR_WIDTH), start_y + INNER_SCROLLBAR_HEIGHT, fill=INNER_SCROLLBAR_COLOR)


    #TODO: make sure we don't go beyond content
    def scrolldown(self, e):
        logger.debug("Scrolling down")
        if self.doc_height > self.window_height:
            self.scroll = min(self.scroll + SCROLL_STEP, self.doc_height - self.window_height)
        else: self.scroll = 0
        self.draw()
    
    def scrollup(self, e):
        logger.debug("Scrolling up")
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        self.draw()
    
    def mouseWheelScroll(self, e):
        #TODO: implement for Windows and Mac since they have differences
        logger.info(e)
    
    def linuxWheelScroll(self, e):
        if e.num == 5: #scroll down
            self.scrolldown(e)
        elif e.num == 4: #scroll up
            self.scrollup(e)

    def resize(self, e):
        logger.info("Configure Event")
        self.window_height = e.height
        self.window_width = e.width
        if self.doc_height > self.window_height:
            self.scroll = min(self.scroll, self.doc_height - self.window_height)
        else: self.scroll = 0
        #Don't re-lex tokens, there is no change in the dom if we resize!!!! (at least, not at this stage, maybe with advanced CSS there would be)
        layout = Layout(self.root_node, self.widthForContent())
        self.display_list = layout.display_list
        self.doc_height = layout.cursor_y
        self.draw()




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    b = Browser()

    if(len(sys.argv) != 2):
        b.load("file:///home/tim/Documents/Projects/SimpleBrowser/SimpleWebBrowser/python/src/static-html/chpt3-test.html")
    else: b.load(sys.argv[1])
    tkinter.mainloop()
    