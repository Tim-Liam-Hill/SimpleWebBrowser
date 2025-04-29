import tkinter
from src.chrome.Chrome import Chrome
from src.chrome.Tab import Tab
from src.HTTP.URLHandler import URLHandler
from src.CSS.CSSParser import CSSParser
import sys
import logging
import os 
logger = logging.getLogger(__name__)

INIT_WIDTH, INIT_HEIGHT = 800, 600
DEFAULT_CSS_PATH = 'CSS/browser.css'
DEFAULT_FILE_PATH = '../tests/htmlparser_test_cases/test.html' #path from this file's directory to default file we show
CURR_FILEPATH = os.path.dirname(os.path.abspath(__file__))

#TODO: this gonna need a rework to support mutliple pages but that's okay.
class Browser:
    def __init__(self):
        # Initialize instance variables--------
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=INIT_WIDTH,
            height=INIT_HEIGHT,
            bg="white"
        )
        self.canvas.pack(fill="both", expand=1)
        self.urlHandler = URLHandler()
        self.window_height = INIT_HEIGHT #height of rendered window
        self.window_width = INIT_WIDTH
        self.tabs = [] 
        self.active_tab = None
        self.chrome = Chrome(self)

        #event handlers
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mouseWheelScroll)
        self.window.bind("<Button-4>", self.linuxWheelScroll)
        self.window.bind("<Button-5>", self.linuxWheelScroll)
        self.window.bind("<Configure>", self.resize)
        self.window.bind("<Button-1>",self.click)
        #--------------------------------------

        #css
        logger.info("Loading default Browser CSS")
        
        try:
            self.defaultCSS = CSSParser().parse(open(f'{CURR_FILEPATH}/{DEFAULT_CSS_PATH}').read())
        except ValueError:
            logger.error("Could not open default browser css file")
            self.defaultCSS = []
        #--------------------------------------

    #We will consider the load function to be the start of everything. the passed in url
    #is the base url that everything else is relative to. 
    def load(self, url):
        self.active_tab.load(url)

    def new_tab(self, url):
        new_tab = Tab(self.defaultCSS, self.urlHandler)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.layout()
        self.draw()

    def layout(self):
        self.active_tab.createLayout(self.window_width)

    def draw(self):
        self.active_tab.draw(self.window_width, self.window_height, self.canvas)
        for cmd in self.chrome.paint():
            cmd.execute(0, self.canvas)


    def scrolldown(self, e):
        logger.debug("Scrolling down")
        if self.active_tab.scrolldown(self.window_height):
            self.draw()
    
    def scrollup(self, e):
        logger.debug("Scrolling up")
        if self.active_tab.scrollup():
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
        if self.active_tab.resize(self.window_height):
            self.layout()
            self.draw()

    def click(self, e):
        if self.active_tab.click(e.x,e.y):
            self.layout()
            self.draw()

        

# from src.layouts.BlockLayout import BlockLayout
# from src.layouts.DocumentLayout import DocumentLayout
# from src.HTMLParser import Element, Text

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    b = Browser()
    

    if(len(sys.argv) != 2):
        b.new_tab(f'file://{CURR_FILEPATH}/{DEFAULT_FILE_PATH}')
    else: b.new_tab(sys.argv[1])
    tkinter.mainloop()
    # style = {
    #     "font-size": "26px",
    #     "font-style": "normal",
    #     "font-weight": "normal",
    #     "color": "black",
    #     "font-family": 'Times',
    # }
    
    # logging.basicConfig(level=logging.DEBUG)
    # p = Element("div",{},None)
    # p.style = {"display":"block"}
    # c1 = Element("span",{"display":"inline"}, p)
    # c2 = Text("mr meow meow",p)
    # c2.style = style
    # c1.style = {"background-color":"red"}
    # c1c1 = Text("inside span",c1)
    # c1c1.style = style

    # c1c2 = Element("div",{"display":"block"},c1)
    # c1c2.style = {}
    # c1c2.style["display"] = "block"
    # c1c2c1 = Text("ooooo",c1c2)
    # c1c2c1.style = style
    # c1c2.children = [c1c2c1]
    # c1c3 = Text("eeee",c1)
    # c1c3.style = style
    # c1.children = [c1c1,c1c2,c1c3]
    # p.children= [c1,c2]
    # block = BlockLayout(p,DocumentLayout(None,500),None)
    # block.layout()
    # block.print(0)
    # print(block.paint())