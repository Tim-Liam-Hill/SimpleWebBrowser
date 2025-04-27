import logging
logger = logging.getLogger(__name__)
from src.CSS.SelectorsParser import SelectorsParser
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
    SELECTOR_COMMENT_START = "selector_comment_start"
    SELECTOR_COMMENT_BODY = "selector_comment_body"
    SELECTOR_COMMENT_END = "selector_comment_END"

    PROPERTY = "property"
    PROPERTY_COMMENT_START = "property_comment_start"
    PROPERTY_COMMENT_BODY = "property_comment_body"
    PROPERTY_COMMENT_END = "property_comment_end"

    VALUE = "value"
    VALUE_COMMENT_START = "value_comment_start"
    VALUE_COMMENT_BODY = "value_comment_body"
    VALUE_COMMENT_END = "value_comment_end"

    RULE = "rule"
    VALUE_RULE = "value_rule" #handles the case where a value is followed by closing brace with no semi-colon

    INVALID_BRACE_OPEN = "invalid opening brace"
    INVALID_BRACE_CLOSE = "invalid closing brace"

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
                 "/":{ACCEPT:States.DISCARD,NEXT:States.COMMENT_START},DEFAULT_TRANSITION:{ACCEPT:States.DISCARD,NEXT:States.SELECTOR},
                "{":{ACCEPT:States.INVALID_BRACE_OPEN, NEXT: States.OPEN},"}":{ACCEPT:States.INVALID_BRACE_CLOSE, NEXT: States.OPEN}},
        States.COMMENT_START: {"*":{NEXT:States.COMMENT_BODY},DEFAULT_TRANSITION:{ACCEPT:States.DISCARD,NEXT:States.OPEN}},
        States.COMMENT_BODY: {"*":{NEXT:States.COMMENT_END}, DEFAULT_TRANSITION:{NEXT:States.COMMENT_BODY}},
        States.COMMENT_END: {"/":{ACCEPT:States.DISCARD, NEXT:States.OPEN},DEFAULT_TRANSITION:{NEXT:States.COMMENT_BODY}},

        States.SELECTOR: {"{": {ACCEPT: States.SELECTOR,NEXT:States.PROPERTY}, "}":{ACCEPT:States.INVALID_BRACE_CLOSE, NEXT: States.OPEN}, DEFAULT_TRANSITION: {NEXT: States.SELECTOR},
                          "/":{NEXT: States.SELECTOR_COMMENT_START}},
        States.SELECTOR_COMMENT_START: {"*": {NEXT:States.SELECTOR_COMMENT_BODY},DEFAULT_TRANSITION: {NEXT:States.SELECTOR}},
        States.SELECTOR_COMMENT_BODY: {"*": {NEXT:States.SELECTOR_COMMENT_END},DEFAULT_TRANSITION: {NEXT:States.SELECTOR_COMMENT_BODY}},
        States.SELECTOR_COMMENT_END: {"/": {ACCEPT: States.SELECTOR_COMMENT_END,NEXT:States.SELECTOR},DEFAULT_TRANSITION: {NEXT:States.SELECTOR_COMMENT_BODY}},

        States.PROPERTY: {";":{ACCEPT: States.DISCARD, NEXT: States.PROPERTY}, ":":{ACCEPT:States.PROPERTY,NEXT:States.VALUE},
                          "}":{ACCEPT:States.RULE,NEXT: States.OPEN},  DEFAULT_TRANSITION:{NEXT:States.PROPERTY}, "/":{NEXT:States.PROPERTY_COMMENT_START}},
        States.PROPERTY_COMMENT_START: {"*": {NEXT:States.PROPERTY_COMMENT_BODY}, DEFAULT_TRANSITION: {NEXT: States.PROPERTY}},
        States.PROPERTY_COMMENT_BODY: {"*": {NEXT:States.PROPERTY_COMMENT_END}, DEFAULT_TRANSITION: {NEXT: States.PROPERTY_COMMENT_BODY}},
        States.PROPERTY_COMMENT_END: {"/": {ACCEPT: States.PROPERTY_COMMENT_END, NEXT:States.PROPERTY}, DEFAULT_TRANSITION: {NEXT: States.PROPERTY_COMMENT_BODY}},

        States.VALUE: {";":{ACCEPT: States.VALUE, NEXT: States.PROPERTY},"}":{ACCEPT:States.VALUE_RULE, NEXT: States.OPEN}, 
                       DEFAULT_TRANSITION: {NEXT:States.VALUE}, "/": {NEXT: States.VALUE_COMMENT_START}},
        States.VALUE_COMMENT_START: {"*": {NEXT: States.VALUE_COMMENT_BODY}, DEFAULT_TRANSITION: {NEXT: States.VALUE}},
        States.VALUE_COMMENT_BODY: {"*": {NEXT: States.VALUE_COMMENT_END}, DEFAULT_TRANSITION: {NEXT: States.VALUE_COMMENT_BODY}},
        States.VALUE_COMMENT_END: {"/": {ACCEPT: States.VALUE_COMMENT_END, NEXT: States.VALUE},DEFAULT_TRANSITION: {NEXT:States.VALUE_COMMENT_BODY}},

    }
}

#Honestly, this and the other 2 selector related parses could have just been static classes. Still, there is no problem with 
#instantiating them
class CSSParser:
    '''Parses CSS rules from an input stylesheet string'''

    def __init__(self):
        self.sp = SelectorsParser()
    
    def parse(self, s):
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
                            rules += self.acceptRule(curr_selector,curr_rule)
                            curr_selector = None 
                            curr_rule = None
                        case States.VALUE_RULE: 
                            curr_rule[curr_property] = text.strip()
                            curr_property = None
                            rules += self.acceptRule(curr_selector,curr_rule)
                            curr_selector = None 
                            curr_rule = None
                        case States.SELECTOR_COMMENT_END | States.PROPERTY_COMMENT_END | States.VALUE_COMMENT_END:
                            text += "/" #we haven't added last char yet
                            text = text[0:text.index("/*")] + text[text.index("*/")+2:]
                            state = DFA["states"][state][char][NEXT]
                            continue #skip usual flow.
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
        logger.debug("Creating new rule/s for selectorString {} with rule {}".format(selectorString,rule))
        rules = []
        try:
            selectors = self.sp.parse(selectorString)
            for s in selectors: 
                rules.append((s,rule))
        except Exception as e:
            logger.info("Error when parsing selector {}".format(selectorString))
            logger.debug(e)
            logger.info("Excluding its rule")

        return rules
    
    def parseStyleBody(self,s):
        '''Used to parse contents of a style attribute string when present in a node.
        
        The regular parse function expects a fully formatted css file ie: property-value pairs must only follow a valid 
        selector. This isn't the case for style attribute of a node so we handle that subset of parsing here. 
        '''
        logger.info("Parsing explicit style attribute string {}".format(s))
        rule = {}
        text = "" 
        curr_property = None
        state = States.PROPERTY

        for char in s: 
            if char in DFA["states"][state]:
                if ACCEPT in DFA["states"][state][char]:
                    accept_type = DFA["states"][state][char][ACCEPT]
                    logger.debug("Accepting str: '{}' type: '{}'".format(text.strip(), accept_type))
                    match accept_type:
                        case States.PROPERTY:
                            curr_property = text.strip()
                            rule[curr_property] = ""
                        case States.VALUE:
                            rule[curr_property] = text.strip()
                            curr_property = None
                        case _: #Here I think we should be throwing errors.
                            logger.warning("Unexpected accept state: only expected property value pairs")
                            logger.warning("skipping parsing this rule")
                            return rule
                    text = ""
                else: 
                    text += char 
                state = DFA["states"][state][char][NEXT]
            else: 
                text += char 
                state = DFA["states"][state][DEFAULT_TRANSITION][NEXT]

        if curr_property != None:
            rule[curr_property] = text.strip() #in case we don't end with a semi-colon

        return rule

def cascade_priority(rule):
    selector, body = rule 
    return selector.getPrio()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = CSSParser()
    path = ""

    print(parser.parse("div {width/*I am a comment*/: 100px }\n p {background-color: red}"))

    # if(len(sys.argv) != 2):
    #     path = "{}/../browser.css".format(os.path.dirname(os.path.abspath(__file__)))
    # else: 
    #     path = sys.argv[1]

    # with open(path, "r") as f:
    #     print(parser.parse(f.read()))
