import logging
logger = logging.getLogger(__name__)
from src.HTMLParser import Element
from enum import Enum, unique
import sys
import os

#TODO: might be worthwhile spliting things up into more classes (eg: one specifically for selectors). 

@unique
class States(Enum):
    '''Represents all valid state transitions for the parser DFA
    
    States are given concrete values to aid in debugging. Note that this enum.
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

@unique
class S_States(Enum):
    '''Represents all valid states for DFA of selector parser'''

    START = "start"
    BASE = "base"
    BAD_START = "bad start symbol"
    DESCENDANT = "descendant" #if we see a space, we assume descendant until proven otherwise
    CHILD = "child"
    NEXT_SIBLING = "sibling"
    SUB_SIBLING = "sub_sibling"
    MULTI_TAGS = "multiple_tags"

    SEQUENCE = "sequence" 
    SEQUENCE_BASE = "sequence_base"

    PSEUDO_CLASS_START = "pseudo_class_start"
    PSEUDO_CLASS = "pseudo_class"
    PSEUDO_ELEMENT = "pseudo_element" #pseudo_elephant lol

    ATTRIBUTE = "attribute" #not sure to what extent I will support these but will throw them in anyway
    ATTRIBUTE_QUOTE1 = "attribute_quote1"
    ATTRIBUTE_QUOTE2 = "attribute_quote2"
    ATTRIBUTE_AFTER = "after_attribute" #needed since attribute selector doesn't immediately know which transition to make
    BAD_ATTRIBUTE_AFTER = "bad symbol after attribute selector"


SelectorDFA = {
    "start": S_States.START,
    "states": {
        S_States.START: { "@":{ACCEPT:S_States.BAD_START}, ":":{ACCEPT:S_States.BAD_START}, ">":{ACCEPT:S_States.BAD_START},
                         "+":{ACCEPT:S_States.BAD_START}, "~":{ACCEPT:S_States.BAD_START}, ",":{ACCEPT:S_States.BAD_START},
                         "[": {NEXT: S_States.ATTRIBUTE}, DEFAULT_TRANSITION:{NEXT:S_States.BASE}}, #we want rules to be at least 1 char in length, hence why we have bad start condition
        S_States.BASE: {DEFAULT_TRANSITION:{NEXT:S_States.BASE}, " ": {ACCEPT:S_States.BASE, NEXT: S_States.DESCENDANT}, ",": {ACCEPT: S_States.BASE, NEXT: S_States.MULTI_TAGS},
                        ">":{ACCEPT:S_States.BASE,NEXT:S_States.CHILD},"+":{ACCEPT:S_States.BASE,NEXT:S_States.NEXT_SIBLING},"~":{ACCEPT:S_States.BASE,NEXT:S_States.SUB_SIBLING},
                        ":":{NEXT:S_States.PSEUDO_CLASS_START},"[": {NEXT: S_States.ATTRIBUTE}, ".": {ACCEPT: S_States.SEQUENCE, NEXT: S_States.SEQUENCE}}, 
                        "#": {ACCEPT: S_States.SEQUENCE, NEXT: S_States.SEQUENCE}},
        S_States.DESCENDANT: {},

        S_States.PSEUDO_CLASS_START:{},
        S_States.PSEUDO_CLASS: {},
        S_States.PSEUDO_ELEMENT: {},

        S_States.SEQUENCE: {DEFAULT_TRANSITION:{NEXT: S_States.SEQUENCE}, ".":{ACCEPT:S_States.SEQUENCE_BASE, NEXT: S_States.SEQUENCE}, "#":{ACCEPT:S_States.SEQUENCE_BASE, NEXT: S_States.SEQUENCE}
                            ""},

        S_States.ATTRIBUTE: {"]": {ACCEPT: S_States.ATTRIBUTE, NEXT: S_States.ATTRIBUTE_AFTER},"\"":{NEXT:S_States.ATTRIBUTE_QUOTE1}, "'":{NEXT:S_States.ATTRIBUTE_QUOTE2},
                             DEFAULT_TRANSITION: {NEXT: S_States.ATTRIBUTE}},
        S_States.ATTRIBUTE_QUOTE1: {"\"": {NEXT: S_States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: S_States.ATTRIBUTE_QUOTE1}},
        S_States.ATTRIBUTE_QUOTE2: {"'": {NEXT: S_States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: S_States.ATTRIBUTE_QUOTE2}},
        S_States.ATTRIBUTE_AFTER: {DEFAULT_TRANSITION: {}}
    
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
        curr_selector = None
        curr_property = None
        curr_rule = None

        for char in s: 
            if char in DFA["states"][state]:
                if ACCEPT in DFA["states"][state][char]:
                    accept_type = DFA["states"][state][char][ACCEPT]
                    logger.debug("Accepting str: '{}' type: '{}'".format(text.strip(), accept_type))

                    match accept_type: #wanted this to be its own function but it was getting complicated
                        case States.SELECTOR: 
                            curr_selector = text.strip() #there will almost certainly be leading/trailing whitespace
                            curr_rule = {}
                        case States.PROPERTY:
                            curr_property = text.strip()
                            curr_rule[curr_property] = ""
                        case States.VALUE:
                            curr_rule[curr_property] = text.strip()
                            curr_property = None
                        case States.RULE:
                            self.acceptRule(curr_selector,curr_rule)
                            curr_selector = None 
                            curr_rule = None
                        case _: #discard by default
                            pass #we don't reset any vars here: we might just be ignoring a single property. 
                    text = ""
                else: 
                    text += char 
                state = DFA["states"][state][char][NEXT]
            else: 
                text += char 
                state = DFA["states"][state][DEFAULT_TRANSITION][NEXT]

        return rules 

    def acceptRule(self, selectorString, rule):
        '''Given a selector string, creates an array of SelectorObject RuleObject pairs (ruleobject is just a dict)'''
        rules = []
        try:
            selectors = self.parseSelectorString(selectorString, 0)
        except Exception as e:
            logger.info("Error when parsing selector {}".format(selectorString))
            logger.debug(e)
            logger.info("Excluding its rule")


        return rules


    def parseSelectorString(self, selectorString, i):
        '''Given a string that represents 1 or more selectors, creates a list of Selector objects for a rule will apply.
    
        If the selector cannot be parsed, we will throw and error and discard the rule to which is belongs. Will return an array of Selectors (which will
        be potentially empty if an error is thrown)
        '''

        # Steps:
        #1. Start parsing our value 
        #2. If we hit a :, get current value as tag/class etc, and go onto parsing our pseudo
        #   2.1 We won't parse multiple pseudo class/things to keep things simple.
        #3. If we hit a . or a # we will create the current tag and recurse as a SequenceSelector
        #4. If we hit any of the combinator values we will recurse and handle the child/parent relationshipt
        #based on array of returned values (if , then just flat array I suppose).

        selectors = []
        descendant_type_selectors = []
        value = ""

        while i < len(selectorString):
            pass
        #if no action for the state we are accepting then assume it is an error message and throw it :3
        #remember for sequence selector to consume any spaces before or after the ,
        # remember to check if a descendant selector is actually a different type of selector (like child)
        # for pseudo selectors, we will only get the selector at the end (once we have parsed the portion to the right of : or ::)
        # same thing for attributes
        # Which states will we still allow once we reach the end of the string? 

        return selectors
    

    #Book's method which can now be considered legacy code. 
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

# Simple Selectors

class TagSelector:
    def __init__(self, tag, prio=1):
        self.tag = tag
        self.priority = prio

    def matches(self, node):
        return isinstance(node, Element) and self.tag == node.tag
    
    def __repr__(self):
        return "TagSelector: {}".format(self.tag)
    
    def __eq__(self, value):
        if not isinstance(value, TagSelector):
            return False 
        return self.tag == value.tag and self.priority == value.priority

class ClassSelector:
    def __init__(self,val, prio):
        self.val = val 
        self.prio = prio 
    
    def matches(self,node):
        if isinstance(node,Element):
            if 'class' in node.attributes:
                arr = [val.strip() for val in node.attributes["class"].strip().split(" ")]
                return self.val in arr
        
        return False
    
    def __repr__(self):
        return "ClassSelector: {}".format(self.val)
    
    def __eq__(self, value):
        if not isinstance(value, ClassSelector):
            return False 
        return self.val == value.val and self.priority == value.priority

class IDSelector:

    def __init__(self, val, prio):
        self.val = val 
        self.prio = prio

    def matches(self, node): #Case sensitive match per https://developer.mozilla.org/en-US/docs/Web/CSS/ID_selectors
        if isinstance(node,Element):
            if 'id' in node.attributes:
                return node.attributes['id'] == self.val
        
        return False
    
    def __repr__(self):
        return "IDSelector: {}".format(self.val)
    
    def __eq__(self, value):
        if not isinstance(value, IDSelector):
            return False 
        return self.val == value.val and self.priority == value.priority

class UniversalSelector:

    def __init__(self,  prio):
        self.val = "*"
        self.prio = prio

    def matches(self, node): 
        return isinstance(node,Element)
    
    def __repr__(self):
        return "Universal Seletor"
    
    def __eq__(self, value):
        if not isinstance(value, UniversalSelector):
            return False 
        return self.prio == value.prio

# Combinator Selectors

class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority

    def matches(self, node): #
        if not self.descendant.matches(node): return False
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent
        return False
    
    def __repr__(self):
        return "DescendantSelector with descendant: {}".format(self.descendant)
    
    def __eq__(self, value):
        if not isinstance(value, DescendantSelector):
            return False 
        return self.ancestor == value.ancestor and self.descendant == value.descendant and self.priority == value.priority

class ChildSelector: 
    def __init__(self, ancestor, descendant):
        pass 

    def matches(self,node):
        return False
    
    def __repre__(self):
        return "DirectDescendantSelector: to be implemented"
    
    def __eq__(self, value):
        return isinstance(value, DirectDescendantSelector)

class SequenceSelector: #TODO: test me
    '''Represents a sequence of selectors not separated by any whitespace.'''

    def __init__(self, selectors):
        self.selectors = selectors

    
    def __matches__(self, node):
        if not isinstance(node,Element):
            return False
        for selector in self.selectors:
            if not selector.matches(node):
                return False
        return True
    
    def __repr__(self):
        return "SequenceSelector: {}".format(self.selectors)
    
    def __eq__(self, value):
        if not isinstance(value, SequenceSelector):
            return False 
        if not len(self.selectors) == value.selectors:
            return False
        
        for i in range(len(self.selectors)):
            if not self.selectors[i] == value.selectors[i]:
                return False

        return True

class NextSiblingSelector:
    def __init__(self):
        pass 

class SubsequentSiblingSelector:
    def __init__(self):
        pass 

#Maybe we will support the below. Putting them in so that we can better parse CSS but
#actual implementation will only be later if ever.

class PseudoClassSelector: 
    def __init__(self, val):
        pass 

    def matches(self, node):
        return isinstance(node, PseudoClassSelector)
    
    def __repr__(self):
        return "PsuedoClassSelector"
    
    def __eq__(self, value):
        return isinstance(value, PsuedoClassSelector)

class PseudoElementSelector:
    def __init__(self, val, prio):
        pass 

    def matches(self, node):
        return isinstance(node, PseudoElementSelector)
    
    def __repr__(self):
        return "PsuedoElementSelector"
    
    def __eq__(self, value):
        return isinstance(value, PsuedoElementSelector)

class AttributeSelector: 
    def __init__(self, val):
        pass 

    def matches(self,node):
        return False 
    
    def __repr__(self):
        return "AttributeSelector"
    
    def __eq__(self, value):
        return isinstance(value, AttributeSelector)

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
