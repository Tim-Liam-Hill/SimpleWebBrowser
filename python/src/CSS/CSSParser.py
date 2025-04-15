import logging
logger = logging.getLogger(__name__)
from python.src.CSS.SelectorParser import DescendantSelector, TagSelector
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
