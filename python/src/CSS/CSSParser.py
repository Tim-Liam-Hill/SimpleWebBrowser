import logging
logger = logging.getLogger(__name__)
from src.HTMLParser import Element
from enum import Enum, unique
import sys
import os

@unique
class States(Enum):
    '''Represents all valid state transitions for the parser DFA
    
    States are given concrete values to aid in debugging. 
    '''

    #Maybe it would be better to separate states for transition and states for accept?

    OPEN = "open"
    DISCARD = "discard"
    COMMENT_START = "comment_start"
    COMMENT_BODY = "comment_body"
    COMMENT_END = "comment_end"
    SELECTOR = "selector"
    PROPERTY = "property"
    VALUE = "value"
    RULE = "rule"
    VALUE_RULE = "value_rule" #handles the case where a value is followed by closing brace with no semi-colon

DEFAULT_TRANSITION = "default"
ACCEPT ="accept"
NEXT = "next"

'''Describes the dfa used to parse CSS strings

It consists of the following main parts:
- open: process whitespace and comments till we get to a tag start
- selector: get contents of selector until we hit the opening brace
- body: inside the body of a selector, whitespace until start rule
- prop_name: processing the name of a pair until :
- prop_value: processing the value of a pair until ; or }
- open_comment: we hit a \\ and need to check if in comment
- close_comment:
and a bunch of error handling. 

If we accept a 'discard' value that means we literally just discard what we encountered since we have no clue how to process it.

This dfa is relatively flexible with respect to what it allows. Further checks will be done at a later stage eg: the DFA
will assume that "8qw.$" is a valid selector value but the later function that determines selector type will reject this.
'''
DFA = {
    "start": States.OPEN,
    "states": {
        States.OPEN: {"\t":{NEXT:States.OPEN},"\n":{NEXT:States.OPEN}," ":{NEXT:States.OPEN}, 
                 "/":{ACCEPT:States.DISCARD,NEXT:States.COMMENT_START},DEFAULT_TRANSITION:{ACCEPT:States.DISCARD,NEXT:States.SELECTOR}},
        States.COMMENT_START: {"*":{NEXT:States.COMMENT_BODY},DEFAULT_TRANSITION:{ACCEPT:States.DISCARD,NEXT:States.OPEN}},
        States.COMMENT_BODY: {"*":{NEXT:States.COMMENT_END}, DEFAULT_TRANSITION:{NEXT:States.COMMENT_BODY}},
        States.COMMENT_END: {"/":{ACCEPT:States.DISCARD, NEXT:States.OPEN},DEFAULT_TRANSITION:{NEXT:States.COMMENT_BODY}},
        States.SELECTOR: {"{": {ACCEPT: States.SELECTOR,NEXT:States.PROPERTY}, DEFAULT_TRANSITION: {NEXT: States.SELECTOR}},
        States.PROPERTY: {";":{ACCEPT: States.DISCARD, NEXT: States.PROPERTY}, ":":{ACCEPT:States.PROPERTY,NEXT:States.VALUE},
                          "}":{ACCEPT:States.RULE,NEXT: States.OPEN},  DEFAULT_TRANSITION:{NEXT:States.PROPERTY}},
        States.VALUE: {";":{ACCEPT: States.VALUE, NEXT: States.PROPERTY},"}":{ACCEPT:States.VALUE_RULE, NEXT: States.OPEN}, 
                       DEFAULT_TRANSITION: {NEXT:States.VALUE}}
    }
}

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
    
    def parse2(self, s):
        '''Uses a custom DFA to parse CSS into selectors and property-value pairs'''

        rules = []
        text = "" 
        state = DFA["start"]


        for char in s: 
            if char in DFA["states"][state]:
                if ACCEPT in DFA["states"][state][char]:
                    self.accept(text,DFA["states"][state][char][ACCEPT])
                    text = ""
                else: 
                    text += char 
                state = DFA["states"][state][char][NEXT]
            else: 
                text += char 
                state = DFA["states"][state][DEFAULT_TRANSITION][NEXT]

        return rules 

    def accept(self, str, acceptType):
        '''Given a string and acceptType, processes the string according to what should be accepted (selector, value etc)'''
        logger.debug("Accepting str: {} type: {}".format(str, acceptType))
        pass

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
    logging.basicConfig(level=logging.DEBUG)

    parser = CSSParser("")
    path = ""

    if(len(sys.argv) != 2):
        path = "{}/../browser.css".format(os.path.dirname(os.path.abspath(__file__)))
    else: 
        path = sys.argv[1]

    with open(path, "r") as f:
        parser.parse2(f.read())
