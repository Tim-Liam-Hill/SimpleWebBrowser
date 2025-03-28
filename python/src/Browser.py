import tkinter
import tkinter.font
from Layout import DocumentLayout, HSTEP, VSTEP, paint_tree, style
from URL import URL
from HTMLParser import HTMLParser
import sys
from CSS.CSSParser import CSSParser
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
DEFAULT_CSS_PATH = './browser.css'

#TODO: this gonna need a rework to support mutliple pages but that's okay.
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
        self.document = None #textbook gives the var this name but I don't like that. Still, keeping it as is for now

        #event handlers
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mouseWheelScroll)
        self.window.bind("<Button-4>", self.linuxWheelScroll)
        self.window.bind("<Button-5>", self.linuxWheelScroll)
        self.window.bind("<Configure>", self.resize)
        #--------------------------------------

        #css
        logger.info("Loading default Browser CSS")
        try:
            self.defaultCSS = CSSParser(open(DEFAULT_CSS_PATH).read()).parse()
        except ValueError:
            logger.error("Could not open default browser css file")
        #--------------------------------------

    #We will consider the load function to be the start of everything. the passed in url
    #is the base url that everything else is relative to. 
    def load(self, url):
        content = self.urlHandler.request(url)
        #TODO: need a case for view-source!!!!!???
        self.root_node = HTMLParser(content).parse(self.urlHandler.viewSource)
        style(self.root_node, self.defaultCSS.copy())
        self.createLayout()
        self.draw()

    def createLayout(self):
        logger.info("Creating DOM from HTML Tree")
        self.document = DocumentLayout(self.root_node, self.widthForContent())
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.doc_height = self.document.height

    def widthForContent(self):
        return self.window_width - SCROLLBAR_WIDTH

    def draw(self):

        self.canvas.delete("all")

        for cmd in self.display_list:
            if cmd.top > self.scroll + self.window_height: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)
        
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
        logger.debug("Configure Event")
        if e.height == self.window_height and e.width == self.window_width:
            logger.debug("No change in proportions, returning")
            return
        self.window_height = e.height
        self.window_width = e.width
        if self.doc_height > self.window_height:
            self.scroll = min(self.scroll, self.doc_height - self.window_height)
        else: self.scroll = 0
        #Don't re-lex tokens, there is no change in the dom if we resize!!!! (at least, not at this stage, maybe with advanced CSS there would be)
        self.createLayout()
        self.draw()




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    b = Browser()

    if(len(sys.argv) != 2):
        b.load("file:///home/tim/Documents/Projects/SimpleBrowser/SimpleWebBrowser/static-html/chpt3-test.html")
    else: b.load(sys.argv[1])
    tkinter.mainloop()
    