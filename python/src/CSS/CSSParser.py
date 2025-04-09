import logging
logger = logging.getLogger(__name__)
from HTMLParser import Element

class CSSParser:
    '''Parses CSS rules from an input stylesheet string'''

    def __init__(self, s):
        self.s = s
        self.i = 0

    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    #TODO: need to improve to handle more cases. Will get back to at end of chapter. 
    #I will likely split this into 2 functions: one for the name of the property and one for the value. 
    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("Attempted to extract CSS word of length 0")
        return self.s[start:self.i]

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Expected " + literal + " but instead got " + self.s[self.i])
        self.i += 1

    #TODO: create functions 'property' and 'value' and then replace word with those. 
    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return prop.casefold(), val
    
    def body(self):
        pairs = {}
        while self.i < len(self.s):
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                logger.debug("Encountered malformed css rule, skipping")
                why = self.ignore_until([";","}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return pairs

    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None

    def selector(self):
        out = TagSelector(self.word().casefold())
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out
    
    def parse(self):
        rules = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception as e:
                logger.info("An exception occurred when parsing a selector, skipping")
                logger.info(e)
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules

class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    def matches(self, node):
        return isinstance(node, Element) and self.tag == node.tag
    
    def __repr__(self):
        return "TagSelector: {}".format(self.tag)
    
    def __eq__(self, value):
        if not isinstance(value, TagSelector):
            return False 
        return self.tag == value.tag and self.priority == value.priority
            
    
class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority

    def matches(self, node):
        if not self.descendant.matches(node): return False
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent
    
    def __repr__(self):
        return "DescendantSelector"
    
    def __eq__(self, value):
        if not isinstance(value, DescendantSelector):
            return False 
        return self.ancestor == value.ancestor and self.descendant == value.descendant and self.priority == value.priority

#TODO: class selectors and ID selectors 

def cascade_priority(rule):
    selector, body = rule 
    return selector.priority

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
