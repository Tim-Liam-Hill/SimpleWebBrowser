from dataclasses import dataclass
from URL import URL
import logging
logger = logging.getLogger(__name__)

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]



@dataclass 
class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.text)
    
    def __str__(self):
        return self.text

@dataclass
class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent
    
    def __repr__(self):
        return "<" + self.tag + ">"
    
    def __str__(self):
        return "<" + self.tag + ">"

#TODO: mayhaps do this as a separate project at somepoint? 
#TODO: There is definitely a better/more elegant way to implement a lexer
class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.tokens = []
        self.unfinished = []

    #slightly enhanced version compared to the one in the book. Better handles style and script tags.
    def parse2(self,viewSource = False):
        if viewSource: #TODO: format the text with newlines and such. Maybe just use a subclass of HTMLParser
            return Text(self.body, None) #TODO: check if we need anything else for this, like a div parent

        text = ""

    #could be more elegant
    #TODO: support <pre> here with another switch case (maybe even code)

    #I should really just be writing DFAs for this,but its a lot more work than what I think I need right now
    #TODO: seriously need to replace this with a DFA and stop being lazy. 
    def parse(self, viewSource = False):

        if viewSource:
            return Text(self.body, None) #TODO: check if we need anything else for this, like a div parent

        text = ""
        in_tag = False
        i = 0
        while i < len(self.body):
            if self.body[i] == "<": 
                in_tag = True
                if text: self.add_text(text)
                text = ""
            elif self.body[i] == ">":
                in_tag = False
                self.add_tag(text)
                #we can be sneaky here
                #before we clear text, check what the start of the tag  is
                #if it is script/style, then we jump to a different function 
                #to extract their body, then just return i when done
                #TODO: any other tags here to support? 
                tag = text.split(" ")[0]
                if tag in ["script", "style"]:
                    i, text = self.parseScriptStyle(i + 1, tag) #returns the index of the last char processed (so we don't double iterate)
                else: text = ""
                
            else:
                text += self.body[i]
            i+=1

        if not in_tag and text:
            self.add_text(text)
        return self.finish()

    #NBNBNBNB if for whatever reason a script has a string with contents "...</script..."
    #then that will cause an issue. This shouldn't realistically be the case however (unless that site is doing
    #something weird or shady)
    def parseScriptStyle(self, i, tag):
        logger.debug("Lexing a " + tag + " tag")
        logger.debug("end condition")
        logger.debug(tag)
        text = ""
        #TODO: test this: script at end of document. 
        while i < len(self.body):
            if i < len(self.body) - len(tag) - 3 and self.body[i:i+2+len(tag)] == "</" + tag :
                return i -1, text
            text += self.body[i]
            i += 1
        
        return i, text


    def add_text(self, text):
        if text.isspace(): return
        AMP_REMAPS = { #TODO: there is almost certainly a better way of doing this (eh)
            "&quot;": "\"", 
            "&copy;":"©", 
            "&ndash;":"-", 
            "&amp;":"@",
            "&lt;":"<",
            "&gt;":">",
            "&#124;": "|",
            "&#039;":","
        }
        
        for key, value in AMP_REMAPS.items(): #there is a more efficient way of doing this but its fine
            text = text.replace(key, value)

        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        if tag.startswith("!"): return

        if tag.startswith("/"):
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            tag, attributes = self.get_attributes(tag)
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            tag, attributes = self.get_attributes(tag)
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def finish(self):
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        print_tree(self.unfinished[0])
        return self.unfinished.pop()
    
    #TODO: expand on this so that later we can do a bit more css and such. 
    #basically only split on the first space to get tag. For the rest of the body
    #we need to iterate through and make sure that we aren't splitting on a space that is in
    #between quotes (eg: imagine you have class="dark flex background-grey". Splitting this by spaces
    #would be incorrect)
    def get_attributes_old(self,text):
        
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""
        return tag, attributes
    
    #obtuse but it works 
    #TODO: actually test it more
    def get_attributes(self,text):
        text = text.lstrip()
        parts = text.split()
        tag = parts[0].casefold()
        in_key = True 
        key = ""
        val = ""
        attributes = {}
        i = 0
        while i < len(text):
            if in_key: 
                if text[i] == "=":
                    in_key = False
                elif text[i] == " ":
                    attributes[key] = ""
                    key = ""
                else:
                    key += text[i]
                i += 1
            else:
                stop = " "
                if text[i] == "\"":
                    stop = "\""
                    i += 1
                elif text[i] == "'":
                    stop = "'"
                    i += 1
                while i < len(text) and text[i] != stop:
                    val += text[i] 
                    i+= 1 
                i += 1
                attributes[key] = val 
                key = "" 
                val = ""
                in_key = True 
        attributes[key] = val
                
        return tag, attributes

def print_tree(node, indent=0):
    print(" " * indent, node)
    if(indent >= 6):
        return
    for child in node.children:
        print_tree(child, indent + 2)

if __name__ == "__main__":

    html = """<!Doctype html>
<html>
<body>
<div id="meow">
I am some <h1>Text</h1>
<img src='http://google.com' style="meow:blue" />
</div>
</body>

</html>
"""
    logging.basicConfig(level=logging.DEBUG)
    url = URL()
    content = url.request("https://browser.engineering/html.html")
    p = HTMLParser(content)
    print_tree(p.parse())
