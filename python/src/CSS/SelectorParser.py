from abc import ABC, abstractmethod
from src.HTMLParser import Element
from enum import Enum, unique
import logging
logger = logging.getLogger(__name__)

@unique
class States(Enum):
    '''Represents all valid states for DFA of selector parser'''

    START = "start"
    BAD_START = "bad start symbol"

    BASE = "base"

    UNIVERSAL = "universal"
    UNIVERSAL_BAD_FOLLOW = "universal element should only be 1 char long"

    ATTRIBUTE = "attribute" #not sure to what extent I will support these but will throw them in anyway
    ATTRIBUTE_QUOTE1 = "attribute_quote1"
    ATTRIBUTE_QUOTE2 = "attribute_quote2"

    PSEUDO_CLASS_START = "pseudo_class_start"
    PSEUDO_CLASS = "pseudo_class"
    PSEUDO_ELEMENT_START = "pseudo_element_start"
    PSEUDO_ELEMENT = "pseudo_element" #pseudo_elephant lol

    PSEUDO_BAD_BRACKET = "Cannot have [ immediately after :"
    PSEUDO_ELEMENT_EXTRA_COLON = "Cannot have a sequence of 3 colons"


DEFAULT_TRANSITION = "default"
ACCEPT ="accept"
NEXT = "next"

DFA = {
    "start": States.START,
    "states": {
        States.START: { "@":{ACCEPT:States.BAD_START}, ":":{ACCEPT:States.PSEUDO_CLASS_START}, 
                "[": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION:{NEXT:States.BASE},
                "]": {ACCEPT: States.BAD_START}, "*": {NEXT: States.UNIVERSAL}
                }, 

        States.UNIVERSAL:{ ".": {ACCEPT: States.UNIVERSAL, NEXT: States.BASE}, "#":{ACCEPT: States.UNIVERSAL, NEXT: States.BASE}, "[": {ACCEPT: States.UNIVERSAL, NEXT: States.ATTRIBUTE},
            ":": {ACCEPT: States.UNIVERSAL,NEXT: States.PSEUDO_CLASS_START}, DEFAULT_TRANSITION: {ACCEPT: States.UNIVERSAL_BAD_FOLLOW}, },

        States.BASE: {DEFAULT_TRANSITION:{NEXT:States.BASE}, ":":{NEXT:States.PSEUDO_CLASS_START},"[": {NEXT: States.ATTRIBUTE}},
    
        States.ATTRIBUTE: {"]": {ACCEPT: States.ATTRIBUTE, NEXT: States.START},"\"":{NEXT:States.ATTRIBUTE_QUOTE1}, "'":{NEXT:States.ATTRIBUTE_QUOTE2},
                             DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE}},
        States.ATTRIBUTE_QUOTE1: {"\"": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE_QUOTE1}},
        States.ATTRIBUTE_QUOTE2: {"'": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE_QUOTE2}},
    
        States.PSEUDO_CLASS_START:{":":{NEXT: States.PSEUDO_ELEMENT_START},DEFAULT_TRANSITION:{NEXT:States.PSEUDO_CLASS}, "]": {ACCEPT: States.PSEUDO_BAD_BRACKET}},
        States.PSEUDO_CLASS: {":":{ACCEPT: States.PSEUDO_CLASS, NEXT: States.PSEUDO_CLASS_START},"[":{ACCEPT: States.PSEUDO_CLASS,NEXT:States.ATTRIBUTE},
                              DEFAULT_TRANSITION: {NEXT:States.PSEUDO_CLASS}, ".":{ACCEPT:States.PSEUDO_CLASS, NEXT: States.BASE},"#":{ACCEPT:States.PSEUDO_CLASS, NEXT: States.BASE}},
        States.PSEUDO_ELEMENT_START: {":":{ACCEPT: States.PSEUDO_ELEMENT_EXTRA_COLON},"[":{ACCEPT: States.PSEUDO_BAD_BRACKET},DEFAULT_TRANSITION: {States.PSEUDO_ELEMENT}},
        States.PSEUDO_ELEMENT: {":":{ACCEPT: States.PSEUDO_ELEMENT, NEXT: States.PSEUDO_CLASS_START},"[":{ACCEPT: States.PSEUDO_ELEMENT,NEXT:States.ATTRIBUTE},
                                DEFAULT_TRANSITION: {NEXT: States.PSEUDO_ELEMENT},".":{ACCEPT:States.PSEUDO_ELEMENT, NEXT: States.BASE},"#":{ACCEPT:States.PSEUDO_ELEMENT, NEXT: States.BASE}},
    }
}

class SelectorParser:
    '''Parses a string representing one selector (that could have attributes/pseudo elements or pseudo classes)'''

    def __init__(self):
        pass 

    def parse(self,s):
        '''Given a string representing a single selector, parses the selector and returns the non-None selector.
        
        If the selector is invalid, a ValueError will be thrown to be handled higher up. If multiple selectors present it will reselt in a Linked-List like structure.
        '''
        text = ""
        elem = None
        state = DFA["start"]
        states = DFA["states"] #less typing needed when doing this

        for char in s: 
            if char in states[state]:
                if ACCEPT in states[state][char]:
                    elem = self.handleAccept(text, states[state][char][ACCEPT], elem)
                text += char 
                state = states[state][char][NEXT]
            else: 
                text += char 
                states = states[state][DEFAULT_TRANSITION][NEXT]

        
        #Accept one last time to ensure we don't 'lose' a selector. Also helps throw additional errors as needed
        #if the state we end on doesn't have an Accept state then that is a sign something has gone wrong. 
        return self.handleAccept(text, state, elem)

    def getBase(self,text):
        '''Given a string representing some simple selector, determines if this selector is a tag, class or ID selector and returns an object of the appropriate class'''
        logger.debug("Creating base case from string {}".format(text))

        if len(text) == 0:
            raise ValueError("Cannot have an empty string for base selector")
        
        match text[0]:
            case "*":
                return UniversalSelector(None)
            case "#":
                return IDSelector(text[1:], None)
            case ".":
                return ClassSelector(text[1:], None)
            case _:
                return TagSelector(text,None)

    def handleAccept(self,text, state, elem):
        '''Given the state to be accepted, returns the new node to be created or throws the appropriate error message
        
        The created node will have its child elem set correctly already.
        '''

        pass 

class Selector(ABC):
    '''The base class all Selectors inherit'''

    def __init__(self):
        '''Base constructor doesn't need anything'''

        pass 

    @abstractmethod
    def matches(self, node):
        '''Given an HTML Node (either Element or Text) determines if this node should be style by the rules associated with this selector'''

        pass 
    
    @abstractmethod
    def getPrio(self):
        '''Returns a thruple representing this selector's specificity
        
        Base classes containing other selectors will recursively use their children to calculate values.
        '''

        pass 

    @abstractmethod
    def __repr__(self):
        '''Print's selectors class type followed by what they want to match'''

        pass
    
    @abstractmethod
    def __eq__(self, value):
        '''Determines if two selectors have same prio and match the same thing'''

        return True
    
# Simple Selectors

class TagSelector(Selector):
    def __init__(self, tag, child):
        self.tag = tag
        self.child = child

    def matches(self, node):

        if(isinstance(node, Element) and self.tag == node.tag):
            if(self.child != None):
                return self.child.matches(node)
            else: 
                return True 
        return False
    
    def __repr__(self):
        return "TagSelector: {} Child: {}".format(self.tag, self.child)
    
    def __eq__(self, value):
        if not isinstance(value, TagSelector):
            return False 
        return self.tag == value.tag and self.getPrio() == value.getPrio() and self.child == value.child

    def getPrio(self):
        t = list(self.child.getPrio() if self.child != None else (0,0,0,0))
        t[3] += 1
        return tuple(t)

class ClassSelector(Selector):
    def __init__(self,val, child):
        self.val = val[1:] if val[0] == "." else val 
        self.child = child

    def matches(self,node): #ugly nesting I know
        if isinstance(node,Element):
            if 'class' in node.attributes:
                arr = [val.strip() for val in node.attributes["class"].strip().split(" ")]
                if(self.val in arr):
                    if(self.child != None):
                        return self.child.matches(node)
                    else: 
                        return True
        
        return False
    
    def __repr__(self):
        return "ClassSelector: {} Child: {}".format(self.val, self.child)
    
    def __eq__(self, value):
        if not isinstance(value, ClassSelector):
            return False 
        return self.val == value.val and self.getPrio() == value.getPrio() and self.child == value.child

    def getPrio(self):
        t = list(self.child.getPrio() if self.child != None else (0,0,0,0))
        t[2] += 1
        return tuple(t)

class IDSelector(Selector):

    def __init__(self, val, child):
        self.val = val[1:] if val[0] == "#" else val 
        self.child = child

    def matches(self, node): #Case sensitive match per https://developer.mozilla.org/en-US/docs/Web/CSS/ID_selectors
        if isinstance(node,Element):
            if 'id' in node.attributes:
                if(self.child != None):
                    return node.attributes['id'] == self.val and self.child.matches(node)
                else: 
                    return node.attributes['id'] == self.val
        
        return False
    
    def __repr__(self):
        return "IDSelector: {} Child: {}".format(self.val, self.child)
    
    def __eq__(self, value):
        if not isinstance(value, IDSelector):
            return False 
        return self.val == value.val and self.child == value.child and self.getPrio() == value.getPrio()

    def getPrio(self):
        t = list(self.child.getPrio() if self.child != None else (0,0,0,0))
        t[1] += 1
        return tuple(t)
class UniversalSelector(Selector):

    def __init__(self,  child):
        self.val = "*"
        self.child = child

    def matches(self, node): 
        if(self.child != None):
            return isinstance(node,Element) and self.child.matches(node)
        return isinstance(node,Element)
    
    def __repr__(self):
        return "Universal Seletor Child: {}".format(self.child)
    
    def __eq__(self, value):
        return isinstance(value, UniversalSelector) and self.child == value.child and self.getPrio() == value.getPrio()

    def getPrio(self):
        return self.child.getPrio() if self.child != None else (0,0,0,0)



# Combinator Selectors

class DescendantSelector(Selector):
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

class ChildSelector(Selector): 
    def __init__(self, ancestor, descendant):
        pass 

    def matches(self,node):
        return False
    
    def __repr__(self):
        return "ChildSelector: to be implemented"
    
    def __eq__(self, value):
        return isinstance(value, ChildSelector)

class NextSiblingSelector(Selector):
    def __init__(self):
        pass 

class SubsequentSiblingSelector(Selector):
    def __init__(self):
        pass 

#Maybe we will support the below. Putting them in so that we can better parse CSS but
#actual implementation will only be later if ever.

class PseudoClassSelector(Selector): 
    def __init__(self, val):
        pass 

    def matches(self, node):
        return isinstance(node, PseudoClassSelector)
    
    def __repr__(self):
        return "PsuedoClassSelector"
    
    def __eq__(self, value):
        return isinstance(value, PseudoClassSelector)

class PseudoElementSelector(Selector):
    def __init__(self, val, prio):
        pass 

    def matches(self, node):
        return isinstance(node, PseudoElementSelector)
    
    def __repr__(self):
        return "PsuedoElementSelector"
    
    def __eq__(self, value):
        return isinstance(value, PseudoElementSelector)

class AttributeSelector(Selector): 
    def __init__(self, val):
        pass 

    def matches(self,node):
        return False 
    
    def __repr__(self):
        return "AttributeSelector"
    
    def __eq__(self, value):
        return isinstance(value, AttributeSelector)


if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
