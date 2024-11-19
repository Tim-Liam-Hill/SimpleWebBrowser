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

    #could be more elegant
    #TODO: support <pre> here with another switch case (maybe even code)
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
                text = ""
            elif i < len(self.body) -3 and self.body[i:i+3] == "&lt":
                text += "<"
                i+= 3
                continue
            elif i < len(self.body) -3 and self.body[i:i+3] == "&gt":
                text = ">"
                i+= 3
                continue
            else:
                text += self.body[i]
            i+=1

        if not in_tag and text:
            self.add_text(text)
        return self.finish()

    def add_text(self, text):
        if text.isspace(): return
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
        return self.unfinished.pop()
    
    #TODO: expand on this so that later we can do a bit more css and such. 
    #basically only split on the first space to get tag. For the rest of the body
    #we need to iterate through and make sure that we aren't splitting on a space that is in
    #between quotes (eg: imagine you have class="dark flex background-grey". Splitting this by spaces
    #would be incorrect)
    def get_attributes(self,text):
        logging.debug(text)
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
