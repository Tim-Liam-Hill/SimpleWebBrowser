from src.HTML.HTMLLayout import style
from src.HTML.HTMLParser import Element, HTMLParser
from src.CSS.CSSParser import CSSParser, cascade_priority
import logging
from src.Utils import tree_to_list
from src.CSS.layouts.DocumentLayout import DocumentLayout
logger = logging.getLogger(__name__)

SCROLL_STEP = 100
SCROLLBAR_WIDTH = 24
INNER_SCROLLBAR_WIDTH = 18
INNER_SCROLLBAR_HEIGHT = 40
SCROLLBAR_COLOR = 'deep sky blue'
INNER_SCROLLBAR_COLOR = 'sky blue'

class Tab:
    def __init__(self, defaultCSS, urlHandler):
        # Initialize instance variables--------
        self.urlHandler = urlHandler
        self.display_list = []
        self.scroll = 0
        self.document = None #textbook gives the var this name but I don't like that. Still, keeping it as is for now
        self.css_parser = CSSParser()
        self.curr_url = ""
        self.defaultCSS = defaultCSS
        self.history = []
        
    #We will consider the load function to be the start of everything. the passed in url
    #is the base url that everything else is relative to. 
    def load(self, url):
        self.curr_url = url
        content = self.urlHandler.request(url)

        self.root_node = HTMLParser(content).parse(self.urlHandler.isViewSource(url))
        rules = self.getCSSRules(self.root_node,url)
        style(self.root_node, sorted(rules, key=cascade_priority))
        self.scroll = 0 #if you navigate from another page we shouldn't preserve scroll
        self.history.append(url)
        # self.createLayout(window_width) #for now, Browser will call createLayout.
        #TODO: implement better algorithm/performance for creating layout.
        # print_tree(self.root_node)
        # print('############')
        # print_tree(self.document)
        #print(self.display_list)
    
    #TODO: we should consider having a cache for computed stylesheets if computing them becomes too slow
    def getCSSRules(self, root_node, base_url):
        logger.info("Determining CSS rules for page")
        node_list = tree_to_list(root_node, [])
        links = [node.attributes["href"]
            for node in node_list
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes]
    
        rules = self.defaultCSS.copy()

        for link in links: #TODO: multithreading here to spead up fetching of resources
            
            try:
                style_url = self.urlHandler.resolve(link, base_url)
                body = self.urlHandler.request(style_url)
            except ValueError as e:
                logger.info(e)
                logger.info("Skipping retrieving CSS for malformed URL")
                continue
            rules.extend(self.css_parser.parse(body))

        #Internal css
        style_nodes = [n for n in node_list 
                       if isinstance(n, Element) and n.tag == "style"]
        
        for node in style_nodes:
            if len(node.children) == 1: #just a sanity check, it is possible there are no children (empty style tag). Should never be more than one
                rules.extend(self.css_parser.parse(node.children[0].text))
        
        return rules

    def createLayout(self, window_width, y_start):
        logger.info("Creating DOM from HTML Tree")
        self.document = DocumentLayout(self.root_node, self.widthForContent(window_width), y_start)
        self.document.layout()
        self.display_list = self.document.paint()
        #self.document.print()
        #print(self.display_list)

    def widthForContent(self, window_width):
        return window_width - SCROLLBAR_WIDTH

    def draw(self, window_width, window_height, start_y, canvas):

        canvas.delete("all")

        for cmd in self.display_list: 
            if cmd.top > self.scroll + window_height: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, canvas)
        
        #scrollbar
        if self.document.getHeight() > window_height - start_y:
            canvas.create_rectangle(self.widthForContent(window_width),  start_y, window_width, window_height, fill=SCROLLBAR_COLOR)
            #start y can go to maximum of self.window_height - INNER_SCROLL_HEIGHT
            proportionScrolled = (self.scroll )/(self.document.getHeight() - window_height - start_y)
            
            start = min( proportionScrolled * (window_height-INNER_SCROLLBAR_HEIGHT-start_y), window_height-INNER_SCROLLBAR_HEIGHT) + start_y
            canvas.create_rectangle(window_width -  INNER_SCROLLBAR_WIDTH - (SCROLLBAR_WIDTH - INNER_SCROLLBAR_WIDTH)/2,  start, window_width - (SCROLLBAR_WIDTH - INNER_SCROLLBAR_WIDTH), start + INNER_SCROLLBAR_HEIGHT, fill=INNER_SCROLLBAR_COLOR)

    def scrollClick(self, y, window_height,start_y):
        '''Allows for faster scrolling'''
        self.scroll = ((y-start_y)/(window_height- start_y)) * self.document.getHeight()

    def click(self, x, y, window_width, window_height, start_y):
        '''Handles changes to the page based on a click event. Returns whether a re-render is needed.'''

        if x >= window_width - SCROLLBAR_WIDTH and y > start_y: 
            self.scrollClick(y, window_height,start_y)
            return True

        logger.debug("Canvas clicked at x '{}' y '{}'".format(x,y))
        y += self.scroll
        logger.debug("Document coordinates are x '{}' y '{}'".format(x,y))
        elems = self.document.getElementsAt(x,y)
        if len(elems) == 0:
            logger.warning("Empty list of clicked elements, if page is scrollable this is an error")
            return False
        elt = elems[-1]

        while elt:
            if isinstance(elt, Element) and elt.tag == "a" and "href" in elt.attributes:
                try:
                    url = elt.attributes["href"]
                    url = self.urlHandler.resolve(url, self.curr_url)
                    self.load(url)
                    self.createLayout(window_width,start_y)
                    return True
                except Exception as e:
                    logger.info("Could not load clicked link")
                    logger.info(e)
                    return False
                
            elt = elt.parent
        
        return False

    def scrolldown(self, window_height, chrome_height):
        prev = self.scroll
        if self.document.getHeight() > window_height + chrome_height:
            self.scroll = min(self.scroll + SCROLL_STEP, self.document.getHeight() - window_height + chrome_height)
        else: 
            self.scroll = 0
        return prev != self.scroll
        
    def scrollup(self):
        prev = self.scroll
        self.scroll = max(self.scroll - SCROLL_STEP, 0)
        return prev != self.scroll
    
    def resize(self, window_height):
        if self.document.getHeight() > window_height:
            self.scroll = min(self.scroll, self.document.getHeight() - window_height)
        else: self.scroll = 0

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    pass 