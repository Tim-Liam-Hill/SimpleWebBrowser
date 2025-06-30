from src.Draw.Commands import DrawOutline, DrawLine, DrawText, DrawRect, Rect
import logging
logger = logging.getLogger(__name__)
CHROME_DEFAULT_FONT_SIZE = 14
import tkinter
import tkinter.font

class Chrome: 
    '''Responsible for the search bar and tab display for a given window'''
    
    def __init__(self, browser):
        self.browser = browser
        self.focus = None
        self.address_bar = ""
        self.address_bar_index = 0 # 0 is before the first char, len()+1 is after the last char

        #TODO: clean up this init (may need to cleanup Rect Classes n such first)
        self.font = tkinter.font.Font(size=CHROME_DEFAULT_FONT_SIZE, weight="normal",slant="roman", family="Courier")
        self.font_height = self.font.metrics("linespace")
        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2*self.padding
        plus_width = self.font.measure("+") + 2*self.padding
        self.newtab_rect = Rect(
           self.padding, self.padding,
           self.padding + plus_width,
           self.padding + self.font_height)
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + \
            self.font_height + 2*self.padding
        self.bottom = self.urlbar_bottom

        back_width = self.font.measure("<") + 2*self.padding
        self.back_rect = Rect(
            self.padding,
            self.urlbar_top + self.padding,
            self.padding + back_width,
            self.urlbar_bottom - self.padding)
    
    def getHeight(self):

        return self.bottom

    def tab_rect(self, i, text, offset):
        tabs_start = offset + self.padding
        tab_width = self.calculateTabWidth(text)
        return Rect(
            tabs_start, self.tabbar_top,
            tabs_start + tab_width, self.tabbar_bottom)
    
    def calculateTabWidth(self, text):
        return self.font.measure(text) + 2*self.padding

    def paint(self):
        cmds = [] 

        #TODO: we can clean this a bit more
        cmds.append(DrawRect(
            0, 0, self.browser.window_width, self.bottom,
            "white"))
        cmds.append(DrawLine(
            0, self.bottom, self.browser.window_width,
            self.bottom, "black", 1))

        cmds.append(DrawOutline(self.newtab_rect, "black", 1))
        cmds.append(DrawText(
            self.newtab_rect.left + self.padding,
            self.newtab_rect.top,
            "+", self.font, "black"))
        
        offset = self.newtab_rect.right
        for i, tab in enumerate(self.browser.tabs):
            cmdsTemp, newOffset = self.paintTab(i, tab, offset)
            cmds += cmdsTemp
            offset = newOffset
        
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(DrawText(
            self.back_rect.left + self.padding,
            self.back_rect.top,
            "<", self.font, "black"))
        
        address_rect = self.calculateAddressRect()
        cmds.append(DrawOutline(address_rect, "black", 1))
        url = self.getAddressBarContents()
        cmds.append(DrawText(
            address_rect.left + self.padding,
            address_rect.top,
            url, self.font, "black"))

        if self.focus == "address bar":
            cmds += self.paintCursor(address_rect)

        return cmds
    
    def paintCursor(self, address_rect):
        width = self.font.measure(self.address_bar)
        ave_w = width/max(len(self.address_bar),1)
        w = self.address_bar_index * ave_w
        return [DrawLine(
            address_rect.left + self.padding + w,
            address_rect.top,
            address_rect.left + self.padding + w,
            address_rect.bottom,
            "red", 1)]

    def paintTab(self, i, tab, offset):
        '''Given a tab and the index it appears in the tab list, returns the commands to render it on the canvas. Further returns the offset for next tab to start'''

        cmds = []
        title = tab.getTitle()
        bounds = self.tab_rect(i,title, offset)
        cmds.append(DrawLine(
            bounds.left, 0, bounds.left, bounds.bottom,
            "black", 1))
        cmds.append(DrawLine(
            bounds.right, 0, bounds.right, bounds.bottom,
            "black", 1))
        cmds.append(DrawText(
            bounds.left + self.padding, bounds.top + self.padding,
            title, self.font, "black"))
        if tab == self.browser.active_tab:
            cmds.append(DrawLine(
                0, bounds.bottom, bounds.left, bounds.bottom,
                "black", 1))
            cmds.append(DrawLine(
                bounds.right, bounds.bottom, self.browser.window_width, bounds.bottom,
                "black", 1))

        return cmds, offset + self.calculateTabWidth(title)

    def getAddressBarContents(self):
        '''Returns what should be displayed in the address bar (based on whether chrome is focused)'''
        return self.address_bar if self.focus == "address bar" else str(self.browser.active_tab.curr_url)
        
    def calculateAddressRect(self):
        '''Calcualtes and returns a Rect that will hold address bar contents. Needs to be dynamic to handle resize'''
        
        return Rect(
            self.back_rect.top + self.padding,
            self.urlbar_top + self.padding,
            self.browser.window_width - self.padding,
            self.urlbar_bottom - self.padding)

    def click(self, x, y):
        self.focus = None
        if self.newtab_rect.contains_point(x, y):
            self.browser.new_tab("https://browser.engineering/")
            return True
        elif self.back_rect.contains_point(x, y):
            self.browser.active_tab.go_back()
            return True
        elif self.calculateAddressRect().contains_point(x,y):
            self.focus = "address bar"
            self.address_bar = ""
            self.address_bar_index = 0
            logger.warning(self.focus)
            return True
        else:
            offset = self.newtab_rect.right
            for i, tab in enumerate(self.browser.tabs):
                if self.tab_rect(i, tab.getTitle(),offset).contains_point(x, y):
                    self.browser.active_tab = tab
                    return True
                offset += self.calculateTabWidth(tab.getTitle())
                

        return False
    
    def keypress(self,char):
        if self.focus == "address bar":
            if self.address_bar_index == 0:
                self.address_bar += char
            else: 
                self.address_bar = self.address_bar[:self.address_bar_index] + char + self.address_bar[self.address_bar_index:]
            self.address_bar_index += 1

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(self.address_bar)
            self.focus = None

    def arrowRight(self):
        if self.address_bar_index < len(self.address_bar):
            self.address_bar_index += 1
    
    def arrowLeft(self):
        if self.address_bar_index > 0:
            self.address_bar_index -= 1
    
    def backSpace(self):
        if self.focus == "address bar":
            if self.address_bar_index > 0 and len(self.address_bar) > 0:
                self.address_bar = self.address_bar[:self.address_bar_index-1] + self.address_bar[self.address_bar_index:]
                self.address_bar_index -=1

    def middleClick(self, x, y): 
        '''Deletes the clicked tab if more than one tab open'''

        if len(self.browser.tabs) == 1: #don't delete the only tab we have
            return False 

        offset = self.newtab_rect.right
        for i, tab in enumerate(self.browser.tabs):
            title = tab.getTitle()
            bounds = self.tab_rect(i,title, offset)
            if y > bounds.bottom:
                return False 
            if x < bounds.right and x > bounds.left: 
                newTabs = [t for t in self.browser.tabs if t != tab]
                if tab == self.browser.active_tab:
                    self.browser.active_tab = newTabs[0]
                self.browser.tabs = newTabs
                return True

            offset += self.calculateTabWidth(title)

        return False