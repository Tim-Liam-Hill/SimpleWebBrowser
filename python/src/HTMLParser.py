from dataclasses import dataclass
from URL import URL
import logging
logger = logging.getLogger(__name__)

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]

#if a state has an 'accept' flag, we don't consume current char and instead
#push the type of element determined by the accept flag, then transition as normal
#if state has a 'trailing_tag' flag, the following happens when accept:
#- there is a trailing </script or </style (or whatever tag name) tag appended to the data that should be 
#- broken into a closing tag
#- only ever trailing_tag flag if accept state set to data (but not always present if this is the case)
#NOTE: technically a tag such as <scri' > will be accepted (and the quote won't be interpreted as creating a string)
#this could be catered for but I highly doubt we need this at present. Can add it if I really want
#we would just need to have another subsection for tags, script and style that ensures that the very first word following <
#consists only of ascii chars (which we require either adding a huge amount of chars to the DFA or changing its core functionality)
DFA = {
    "start": "data",
    "default_transition_key": "**", #needs to be 2 chars to ensure it doesn't overlap with chars in language
    "states": {
        "data": {"<":{"accept":"data", "next":"pre_tag"}, "**":{"next": "data"}},
        "pre_tag":{">":{"accept":"tag", "next":"data"}, "s":{"next":"scriptstyle1"}, "**":{"next":"in_tag"}},
        "in_tag": {">":{"accept":"tag", "next":"data"},"'":{"next":"quote1"}, "\"": {"next":"quote2"}, "**":{"next":"in_tag"}},
        "quote1":{"'":{"next":"in_tag"},"**":{"next":"quote1"}},
        "quote2":{"\"":{"next":"in_tag"}, "**":{"next":"quote2"}},
        "scriptstyle1":{"c":{"next":"script2"},"t":{"next":"style2"},"**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "style2":{"y":{"next":"style3"},"**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "style3":{"l":{"next":"style4"},"**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "style4":{"e":{"next":"style_tag_body"}, "**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "style_tag_body":{">":{"accept":"tag","next":"style_body"},"'":{"next":"style_tag_quote1"},"\"":{"next":"style_tag_quote2"},"**":{"next":"style_tag_body"}}, 
        "style_tag_quote1":{"'":{"next":"style_tag_body"},"**":{"next":"style_tag_quote1"}},
        "style_tag_quote2":{"\"":{"next":"style_tag_body"},"**":{"next":"style_tag_quote2"}},
        "style_body":{"<":{"next":"style_close1"}, "'":{"next":"style_quote1"},"\"":{"next":"style_quote2"}, "**":{"next":"style_body"}},
        "style_quote1":{"'":{"next":"style_body"}, "**":{"next":"style_quote1"}},
        "style_quote2":{"\"":{"next":"style_body"}, "**":{"next":"style_quote2"}},
        "style_close1":{"/":{"next":"style_close2"},"**":{"next":"style_body"}},
        "style_close2":{"s":{"next":"style_close3"}, "**":{"next":"style_body"}},
        "style_close3":{"t":{"next":"style_close4"}, "**":{"next":"style_body"}},
        "style_close4":{"y":{"next":"style_close5"}, "**":{"next":"style_body"}},
        "style_close5":{"l":{"next":"style_close6"}, "**":{"next":"style_body"}},
        "style_close6":{"e":{"next":"style_close7"}, "**":{"next":"style_body"}},
        "style_close7":{">":{"next":"data", "accept":"data", "trailing_tag":"style"}, "**":{"next":"style_body"}},
        "script2":{"r":{"next":"script3"},"**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "script3":{"i":{"next":"script4"},"**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "script4":{"p":{"next":"script5"},"**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "script5":{"t":{"next":"script_tag_body"},"**": {"next":"in_tag"} ,">":{"accept":"tag", "next":"data"}},
        "script_tag_body":{">":{"accept":"tag","next":"script_body"},"'":{"next":"script_tag_quote1"}, "\"":{"next":"script_tag_quote2"},"**":{"next":"script_tag_body"}},
        "script_tag_quote1":{"'":{"next":"style_tag_body"},"**":{"next":"script_tag_quote1"}},
        "script_tag_quote2":{"\"":{"next":"style_tag_body"},"**":{"next":"script_tag_quote2"}},
        "script_body":{"<":{"next":"script_close1"}, "'":{"next":"script_quote1"},"\"":{"next":"script_quote2"}, "**":{"next":"script_body"}},
        "script_quote1":{"'":{"next":"script_body"},"**":{"next":"script_quote1"}},
        "script_quote2":{"\"":{"next":"script_body"}, "**":{"next":"script_quote2"}},
        "script_close1":{"/":{"next":"script_close2"},"**":{"next":"script_body"}},
        "script_close2":{"s":{"next":"script_close3"},"**":{"next":"script_body"}},
        "script_close3":{"c":{"next":"script_close4"},"**":{"next":"script_body"}},
        "script_close4":{"r":{"next":"script_close5"},"**":{"next":"script_body"}},
        "script_close5":{"i":{"next":"script_close6"},"**":{"next":"script_body"}},
        "script_close6":{"p":{"next":"script_close7"},"**":{"next":"script_body"}},
        "script_close7":{"t":{"next":"script_close8"},"**":{"next":"script_body"}},
        "script_close8":{">":{"accept":"data","next":"data", "trailing_tag":"script"},"**":{"next":"script_body"}},

    }
}

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

    #better version of parse that uses a DFA (albeit a simple one)
    #it doesn't freak out when encountering quotes inside tag bodies (nor does it freak out if there are closing tags in those quotes)
    def parse(self,viewSource = False):
        if viewSource: #TODO: format the text with newlines and such. Maybe just use a subclass of HTMLParser
            return Text(self.body, None) #TODO: check if we need anything else for this, like a div parent

        text = ""
        state = DFA["start"]
        i = 0

        for i in self.body:
            logger.debug("In state %s: ", state)
            if i in DFA["states"][state]:
                if "accept" in DFA["states"][state][i] and DFA["states"][state][i]["accept"] == "tag":
                    self.add_tag(text)
                    text = ""
                elif "accept" in DFA["states"][state][i] and DFA["states"][state][i]["accept"] == "data":
                    possible_tag = ""
                    
                    if "trailing_tag" in DFA["states"][state][i]:
                        possible_tag_len = len(DFA["states"][state][i]["trailing_tag"]) #excludes implicit </
                        if len(text) >= possible_tag_len + 2 and text[-possible_tag_len-2:] == "</" + DFA["states"][state][i]["trailing_tag"]: #use I know, verbose if statements are gross
                            possible_tag = "/" + DFA["states"][state][i]["trailing_tag"]
                            text = text[0:len(text)-possible_tag_len-2]
                        else: 
                            logger.error("This state should never be reached. We have a DFA state that should only be closed when it encounters the trailing tag yet the trailing tag cannot be extracted")
                            logger.error("String is: %s", text)
                            logger.error("Trailing tag is %s", "</" + DFA["states"][state][i]["trailing_tag"])
                            
                    self.add_text(text)
                    self.add_tag(possible_tag) #if tag == "" then it will be ignored
                    text = ""
                else: text += i
                state = DFA["states"][state][i]["next"]
            else:
                text += i 
                state = DFA["states"][state]["**"]["next"]
            

        if state == "data" and text != "":
            self.add_text(text)
        return self.finish()

    #could be more elegant
    #TODO: support <pre> here with another switch case (maybe even code)

    #I should really just be writing DFAs for this,but its a lot more work than what I think I need right now
    #TODO: seriously need to replace this with a DFA and stop being lazy. 
    def parse_old(self, viewSource = False):

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
        if text.isspace() or len(text) == 0: return

        logger.debug("Adding text: %s", text)
        AMP_REMAPS = { #TODO: there is almost certainly a better way of doing this that is more performant (eh)
            "&quot;": "\"", #it would use a DFA that iterates through and replaces as strings are encountered
            "&copy;":"©",   #actually somewhat trivial to implement, will get to it when the need for performance arises
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
        
        if tag.startswith("!") or tag=="": return #we realistically shouldn't encounter empty tags, and technically I don't think we need to remove them 
        logger.debug("Adding tag: %s", tag)       

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
