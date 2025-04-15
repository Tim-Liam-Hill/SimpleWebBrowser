from enum import Enum, unique

@unique
class States(Enum):
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
    SEQUENCE_PSEUDO_ELEMENT = "sequence_pseudo_element"
    SEQUENCE_PSEUDO_CLASS_START = "sequence_pseduo_class_start"
    SEQUENCE_PSEUDO_CLASS = "sequence_pseduo_class"

    PSEUDO_CLASS_START = "pseudo_class_start"
    PSEUDO_CLASS = "pseudo_class"
    PSEUDO_ELEMENT = "pseudo_element" #pseudo_elephant lol

    ATTRIBUTE = "attribute" #not sure to what extent I will support these but will throw them in anyway
    ATTRIBUTE_QUOTE1 = "attribute_quote1"
    ATTRIBUTE_QUOTE2 = "attribute_quote2"
    ATTRIBUTE_AFTER = "after_attribute" #needed since attribute selector doesn't immediately know which transition to make
    BAD_ATTRIBUTE_AFTER = "bad symbol after attribute selector"

    UNSUPPORTED_SYMBOL = "unsupported symbol"

DEFAULT_TRANSITION = "default"
ACCEPT ="accept"
NEXT = "next"

SelectorDFA = {
    "start": States.START,
    "states": {
        States.START: { "@":{ACCEPT:States.BAD_START}, ":":{ACCEPT:States.BAD_START}, ">":{ACCEPT:States.BAD_START},
                         "+":{ACCEPT:States.BAD_START}, "~":{ACCEPT:States.BAD_START}, ",":{ACCEPT:States.BAD_START},
                         "[": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION:{NEXT:States.BASE}}, #we want rules to be at least 1 char in length, hence why we have bad start condition
        States.BASE: {DEFAULT_TRANSITION:{NEXT:States.BASE}, " ": {ACCEPT:States.BASE, NEXT: States.DESCENDANT}, ",": {ACCEPT: States.BASE, NEXT: States.MULTI_TAGS},
                        ">":{ACCEPT:States.BASE,NEXT:States.CHILD},"+":{ACCEPT:States.BASE,NEXT:States.NEXT_SIBLING},"~":{ACCEPT:States.BASE,NEXT:States.SUB_SIBLING},
                        ":":{NEXT:States.PSEUDO_CLASS_START},"[": {NEXT: States.ATTRIBUTE}, ".": {ACCEPT: States.SEQUENCE, NEXT: States.SEQUENCE}}, 
                        "#": {ACCEPT: States.SEQUENCE, NEXT: States.SEQUENCE}},
        States.DESCENDANT: {},

        States.PSEUDO_CLASS_START:{},
        States.PSEUDO_CLASS: {},
        States.PSEUDO_ELEMENT: {},

        States.SEQUENCE: {DEFAULT_TRANSITION:{NEXT: States.SEQUENCE}, ".":{ACCEPT:States.SEQUENCE_BASE, NEXT: States.SEQUENCE}, "#":{ACCEPT:States.SEQUENCE_BASE, NEXT: States.SEQUENCE},
                            ":":{NEXT:States.SEQUENCE_PSEUDO_CLASS_START},  },

        States.ATTRIBUTE: {"]": {ACCEPT: States.ATTRIBUTE, NEXT: States.ATTRIBUTE_AFTER},"\"":{NEXT:States.ATTRIBUTE_QUOTE1}, "'":{NEXT:States.ATTRIBUTE_QUOTE2},
                             DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE}},
        States.ATTRIBUTE_QUOTE1: {"\"": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE_QUOTE1}},
        States.ATTRIBUTE_QUOTE2: {"'": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE_QUOTE2}},
        States.ATTRIBUTE_AFTER: {DEFAULT_TRANSITION: {}}
    
}   

class SelectorsParser:
    '''Parses string representing one or more selectors for a rule'''

    def __init__(self):
        pass 

    def parse(self, selector):
        pass 

    def createBaseSelector(self, s):
        pass 

    def createPseudoElement(self,s):
        pass 

    def createPseudoClass(self,s):
        pass 