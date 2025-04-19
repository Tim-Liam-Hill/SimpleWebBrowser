from enum import Enum, unique

@unique
class States(Enum):
    '''Represents all valid states for DFA of selectors parser'''

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

    UNSUPPORTED_SYMBOL = "unsupported symbol"

DEFAULT_TRANSITION = "default"
ACCEPT ="accept"
NEXT = "next"

DFA = {
    "start": States.START,
    "states": {
        States.START: { "@":{ACCEPT:States.BAD_START}, ":":{ACCEPT:States.BAD_START}, ">":{ACCEPT:States.BAD_START},
                         "+":{ACCEPT:States.BAD_START}, "~":{ACCEPT:States.BAD_START}, ",":{ACCEPT:States.BAD_START},
                         "[": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION:{NEXT:States.BASE}}, #we want rules to be at least 1 char in length, hence why we have bad start condition
    
        States.DESCENDANT: {},



        States.SEQUENCE: {DEFAULT_TRANSITION:{NEXT: States.SEQUENCE}, ".":{ACCEPT:States.SEQUENCE_BASE, NEXT: States.SEQUENCE}, "#":{ACCEPT:States.SEQUENCE_BASE, NEXT: States.SEQUENCE},
                            ":":{NEXT:States.SEQUENCE_PSEUDO_CLASS_START},  },


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