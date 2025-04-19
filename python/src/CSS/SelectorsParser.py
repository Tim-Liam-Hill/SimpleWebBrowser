from src.CSS.SelectorParser import SelectorParser, DescendantSelector,ChildSelector,NextSiblingSelector,SubsequentSiblingSelector
from enum import Enum, unique
import logging
logger = logging.getLogger(__name__)

@unique
class States(Enum):
    '''Represents all valid states for DFA of selectors parser'''

    SELECTOR = "selector"
    DESCENDANT = "descendant"
    CHILD = "child"
    CHILD_INVALID = "invalid '>'"
    NEXT_SIB = "next"
    NEXT_SIB_INVALID ="invalid '+'"
    SUBSEQUENT_SIB = "subsequent"
    SUBSEQUENT_SIB_INVALID ="invalid '~'"

    MULTI = "multi"
    MULTI_INVALID ="invalid ','"
    POST_MULTI = "post multi"


DEFAULT_TRANSITION = "default"
ACCEPT ="accept"
NEXT = "next"

#TODO: consider making a DFA class from which our dfas inherit and implement
DFA = {
    "start": States.SELECTOR,
    "states": {
        States.SELECTOR: {DEFAULT_TRANSITION: {NEXT:States.SELECTOR}, " ":{ACCEPT:States.SELECTOR, NEXT:States.DESCENDANT},
                        ">":{ACCEPT:States.SELECTOR, NEXT:States.CHILD}, "~":{ACCEPT:States.SELECTOR, NEXT:States.SUBSEQUENT_SIB},
                           "+":{ACCEPT:States.SELECTOR, NEXT:States.NEXT_SIB},",":{ACCEPT:States.MULTI, NEXT:States.POST_MULTI}},
        States.POST_MULTI: {" ":{NEXT:States.POST_MULTI},">":{ACCEPT:States.CHILD_INVALID}, "~":{ACCEPT:States.SUBSEQUENT_SIB_INVALID},
                           "+":{ACCEPT:States.NEXT_SIB_INVALID},",":{ACCEPT:States.MULTI_INVALID}, DEFAULT_TRANSITION: {ACCEPT: States.POST_MULTI, NEXT: States.SELECTOR}},
        States.DESCENDANT: {" ":{NEXT:States.DESCENDANT},">":{NEXT:States.CHILD}, "~":{NEXT:States.SUBSEQUENT_SIB},
                           "+":{NEXT:States.NEXT_SIB},",":{ACCEPT:States.MULTI,NEXT:States.POST_MULTI}, DEFAULT_TRANSITION: {ACCEPT: States.DESCENDANT, NEXT: States.SELECTOR}},
        States.CHILD: {" ":{NEXT:States.CHILD},">":{ACCEPT:States.CHILD_INVALID}, "~":{ACCEPT:States.SUBSEQUENT_SIB_INVALID},
                           "+":{ACCEPT:States.NEXT_SIB_INVALID},",":{ACCEPT:States.MULTI_INVALID}, DEFAULT_TRANSITION: {ACCEPT: States.CHILD, NEXT: States.SELECTOR}},
        States.NEXT_SIB: {" ":{NEXT:States.NEXT_SIB},">":{ACCEPT:States.CHILD_INVALID}, "~":{ACCEPT:States.SUBSEQUENT_SIB_INVALID},
                           "+":{ACCEPT:States.NEXT_SIB_INVALID},",":{ACCEPT:States.MULTI_INVALID}, DEFAULT_TRANSITION: {ACCEPT: States.NEXT_SIB, NEXT: States.SELECTOR}},
        States.SUBSEQUENT_SIB: {" ":{NEXT:States.SUBSEQUENT_SIB},">":{ACCEPT:States.CHILD_INVALID}, "~":{ACCEPT:States.SUBSEQUENT_SIB_INVALID},
                           "+":{ACCEPT:States.NEXT_SIB_INVALID},",":{ACCEPT:States.MULTI_INVALID}, DEFAULT_TRANSITION: {ACCEPT: States.SUBSEQUENT_SIB, NEXT: States.SELECTOR}},
     } 
}   

class SelectorsParser:
    '''Parses string representing one or more selectors for a rule'''

    def __init__(self):
        self.selectorParser = SelectorParser()

    def parse(self, selector):
        '''Given a string representing one or more selectors, returns a matching array of selector objects'''
        
        selector = selector.strip()
        selectors = []
        queue = []
        text = ""
        state = DFA["start"]
        states = DFA["states"]

        if len(selector) == 0:
            raise ValueError("selector cannot have length 0")

        #REMEMBER TO HANDLE COMMAS NICELY
        for char in selector: 
            if char in states[state]:
                if ACCEPT in states[state][char]:
                    selectors, queue = self.handleAccept(text,state,queue,selectors)
                    text = ""
                text += char 
                state = states[state][char][NEXT]
            else:
                if ACCEPT in states[state][DEFAULT_TRANSITION]:
                    selectors, queue = self.handleAccept(text,state,queue,selectors)
                    text = ""
                text += char 
                state = states[state][DEFAULT_TRANSITION][NEXT]

        selectors,queue = self.handleAccept(text,state,queue,selectors)

        return selectors +  [self.squashCombinators(queue)]
    
    def handleAccept(self,text,state,queue,selectors):
        '''Determines which selector (if any) to create given an accept state. Joins combinators to base selectors if necessay'''

        logger.debug("Accepting state {} with text {}".format(state,text))
        match state:
            case States.SELECTOR:
                queue.append(self.selectorParser.parse(text))
                return selectors, queue
            case States.DESCENDANT:
                queue.append(DescendantSelector(None,None))
                return selectors, queue
            case States.CHILD:
                queue.append(ChildSelector(None,None))
                return selectors, queue
            case States.NEXT_SIB:
                queue.append(NextSiblingSelector(None,None))
                return selectors, queue
            case States.SUBSEQUENT_SIB:
                queue.append(NextSiblingSelector(None,None))
                return selectors, queue
            case States.MULTI:
                selectors.append(self.squashCombinators(queue))
                return selectors, []
            case _:
                raise ValueError("No matching action for state {}".format(state))

    def squashCombinators(self,queue):
        '''Given a queue of base and combinator selectors merges them into a single selector with appropriate parent/child values set
        
        Essentially creates a linked list. 
        '''

        logger.debug("squashing combinators in queue {}".format(queue))
        if len(queue) == 1:
            return queue[0]

        if len(queue) % 2 == 0: 
            raise ValueError("Queue should never be even in length")
        
        index = len(queue) -1

        while index > 0:
            if self.isCombinator(queue[index]):
                raise ValueError("expected base selector, instead found combinator selector")
            if not self.isCombinator(queue[index-1]):
                raise ValueError("expected combinator selector, instead found base selector")
            
            queue[index-1].child = queue[index]
            queue.pop(index)
    
            index -= 2
        
        while(len(queue) != 1):
            queue[1].parent = queue[0]
            queue.pop(0)
        
        return queue[0]
    
    def isCombinator(self,selector):

        return isinstance(selector,DescendantSelector) or isinstance(selector,NextSiblingSelector)\
              or isinstance(selector,ChildSelector) or isinstance(selector,SubsequentSiblingSelector)


if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    sp = SelectorsParser()
    print(sp.parse("div.class > span#id"))