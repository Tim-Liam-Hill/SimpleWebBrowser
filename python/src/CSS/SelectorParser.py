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
    ATTRIBUTE_AFTER = "attribute_after"

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
        States.START: { "@":{ACCEPT:States.BAD_START}, ":":{NEXT:States.PSEUDO_CLASS_START}, 
                "[": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION:{NEXT:States.BASE},
                "]": {ACCEPT: States.BAD_START}, "*": {NEXT: States.UNIVERSAL}
                }, 

        States.UNIVERSAL:{ ".": {ACCEPT: States.UNIVERSAL, NEXT: States.BASE}, "#":{ACCEPT: States.UNIVERSAL, NEXT: States.BASE}, "[": {ACCEPT: States.UNIVERSAL, NEXT: States.ATTRIBUTE},
            ":": {ACCEPT: States.UNIVERSAL,NEXT: States.PSEUDO_CLASS_START}, DEFAULT_TRANSITION: {ACCEPT: States.UNIVERSAL_BAD_FOLLOW}, },

        States.BASE: {".": {ACCEPT: States.BASE, NEXT: States.BASE}, "#": {ACCEPT: States.BASE, NEXT: States.BASE}, DEFAULT_TRANSITION:{NEXT:States.BASE}, ":":{ACCEPT: States.BASE,NEXT:States.PSEUDO_CLASS_START},"[": {ACCEPT: States.BASE,NEXT: States.ATTRIBUTE}},
    
        States.ATTRIBUTE: {"]": {NEXT: States.ATTRIBUTE_AFTER},"\"":{NEXT:States.ATTRIBUTE_QUOTE1}, "'":{NEXT:States.ATTRIBUTE_QUOTE2},
                             DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE}},
        States.ATTRIBUTE_AFTER: { "@":{ACCEPT:States.BAD_START}, ":":{ACCEPT:States.ATTRIBUTE_AFTER,NEXT:States.PSEUDO_CLASS_START}, 
                "[": {ACCEPT:States.ATTRIBUTE_AFTER,NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION:{ACCEPT:States.ATTRIBUTE_AFTER,NEXT:States.BASE},
                "]": {ACCEPT: States.BAD_START}, "*": {ACCEPT:States.ATTRIBUTE_AFTER,NEXT: States.UNIVERSAL}
                },
        States.ATTRIBUTE_QUOTE1: {"\"": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE_QUOTE1}},
        States.ATTRIBUTE_QUOTE2: {"'": {NEXT: States.ATTRIBUTE}, DEFAULT_TRANSITION: {NEXT: States.ATTRIBUTE_QUOTE2}},
    
        States.PSEUDO_CLASS_START:{":":{NEXT: States.PSEUDO_ELEMENT_START},DEFAULT_TRANSITION:{NEXT:States.PSEUDO_CLASS}, "]": {ACCEPT: States.PSEUDO_BAD_BRACKET}},
        States.PSEUDO_CLASS: {":":{ACCEPT: States.PSEUDO_CLASS, NEXT: States.PSEUDO_CLASS_START},"[":{ACCEPT: States.PSEUDO_CLASS,NEXT:States.ATTRIBUTE},
                              DEFAULT_TRANSITION: {NEXT:States.PSEUDO_CLASS}, ".":{ACCEPT:States.PSEUDO_CLASS, NEXT: States.BASE},"#":{ACCEPT:States.PSEUDO_CLASS, NEXT: States.BASE}},
        States.PSEUDO_ELEMENT_START: {":":{ACCEPT: States.PSEUDO_ELEMENT_EXTRA_COLON},"[":{ACCEPT: States.PSEUDO_BAD_BRACKET},DEFAULT_TRANSITION: {NEXT:States.PSEUDO_ELEMENT}},
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

        if len(s) == 0:
            raise ValueError("selector cannot have length 0")

        for char in s: 
            if char in states[state]:
                if ACCEPT in states[state][char]:
                    elem= self.handleAccept(text, states[state][char][ACCEPT], elem)
                    text = ""
                text += char 
                state = states[state][char][NEXT]
            else: 
                text += char 
                state = states[state][DEFAULT_TRANSITION][NEXT]

        
        #Accept one last time to ensure we don't 'lose' a selector. Also helps throw additional errors as needed
        #if the state we end on doesn't have an Accept state then that is a sign something has gone wrong. 
        return self.handleAccept(text, state, elem)
    

    def getBase(self,text, child):
        '''Given a string representing some simple selector, determines if this selector is a tag, class or ID selector and returns an object of the appropriate class'''
        logger.debug("Creating base case from string {}".format(text))

        if len(text) == 0:
            raise ValueError("Cannot have an empty string for base selector")
        
        match text[0]:
            case "*":
                return UniversalSelector(child)
            case "#":
                return IDSelector(text[1:], child)
            case ".":
                return ClassSelector(text[1:], child)
            case _:
                return TagSelector(text,child)

    def handleAccept(self,text, state, elem):
        '''Given the state to be accepted, returns the new node to be created and new text value or throws the appropriate error message
        
        The created node will have its child elem set correctly already.
        '''

        logger.debug("Accepting state {} with text: {} and child: ".format(state,text, elem))


        match state:
            case States.UNIVERSAL | States.BASE:
                return self.getBase(text, elem)
            case States.ATTRIBUTE_AFTER: #if ending on attribute we would be in state attribute after, so need to accept that
                return AttributeSelector(text[1:len(text)-1], elem)
            case States.PSEUDO_CLASS:
                return PseudoClassSelector(text[1:], elem)
            case States.PSEUDO_ELEMENT:
                return PseudoElementSelector(text[2:], elem)
            case _:
                raise ValueError(state)
            

        

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
        return "TagSelector: {} Child ({})".format(self.tag, self.child)
    
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
        return "ClassSelector: {} Child ({})".format(self.val, self.child)
    
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
        return "IDSelector: {} Child ({})".format(self.val, self.child)
    
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
        return "Universal Seletor Child ({})".format(self.child)
    
    def __eq__(self, value):
        return isinstance(value, UniversalSelector) and self.child == value.child and self.getPrio() == value.getPrio()

    def getPrio(self):
        return self.child.getPrio() if self.child != None else (0,0,0,0)



# Combinator Selectors

class DescendantSelector(Selector):
    def __init__(self, parent, child):
        '''Child represents a non-combinator selector. Parent should never be none'''

        self.parent = parent
        self.child = child

    def matches(self, node): 
        if not self.child.matches(node): return False
        while node.parent:
            if self.parent.matches(node.parent): return True
            node = node.parent
        return False
    
    def __repr__(self):
        return "DescendantSelector Parent: {} Child: {}".format(self.parent,self.child)
    
    def __eq__(self, value):
        if not isinstance(value, DescendantSelector):
            return False 
        return self.parent == value.parent and self.child == value.child and self.getPrio() == value.getPrio()

    def getPrio(self):
        l1 = list(self.parent.getPrio())
        l2 = list(self.child.getPrio())
        return tuple([l1[i] + l2[i] for i in range(len(l2))])

class ChildSelector(Selector): 
    '''Child represents a non-combinator selector. Parent should never be none'''

    def __init__(self, parent, child):
        self.parent = parent 
        self.child = child 

    def matches(self,node):
        if not self.child.matches(node): 
            return False
        if node.parent and self.parent.matches(node.parent): 
            return True
        return False
    
    def __repr__(self):
        return "ChildSelector Parent: {} Child: {}".format(self.parent, self.child)
    
    def __eq__(self, value):
        if not isinstance(value,ChildSelector):
            return False 
        return self.parent == value.parent and self.child == value.child and self.getPrio() == value.getPrio()
    
    def getPrio(self):
        l1 = list(self.parent.getPrio())
        l2 = list(self.child.getPrio())
        return tuple([l1[i] + l2[i] for i in range(len(l2))])

class NextSiblingSelector(Selector):
    '''Child represents a non-combinator selector. Parent should never be none'''

    def __init__(self, parent, child):
        self.parent = parent 
        self.child = child  

    def matches(self, node):
        if not self.child.matches(node):
            return False
        
        prev = None 
        c = node.parent.children 
        if c == None or len(c) == 0:
            return False 
        
        for child in c:
            if child is node:
                break 
            else:
                prev = child 

        if prev == None:
            return False

        return self.parent.matches(prev)

    def __eq__(self, value):
        if not isinstance(value,NextSiblingSelector):
            return False 
        return self.parent == value.parent and self.child == value.child and self.getPrio() == value.getPrio()

    def __repr__(self):
        return "NextSiblingSelector Parent: {} Child: {}".format(self.parent, self.child)

    def getPrio(self):
        l1 = list(self.parent.getPrio())
        l2 = list(self.child.getPrio())
        return tuple([l1[i] + l2[i] for i in range(len(l2))])

class SubsequentSiblingSelector(Selector):
    '''Child represents a non-combinator selector. Parent should never be none'''

    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    def matches(self, node):
        if not self.child.matches(node):
            return False
        
        c = node.parent.children 
        if c == None:
            return False 
        
        for child in c:
            if child is node:
                break 
            elif self.parent.matches(child):
                return True


        return False

    def __eq__(self, value):
        if not isinstance(value,SubsequentSiblingSelector):
            return False 
        return self.parent == value.parent and self.child == value.child and self.getPrio() == value.getPrio()
    
    def __repr__(self):
        return "SubsequentSiblingSelector Parent: {} Child: {}".format(self.parent, self.child)

    def getPrio(self):
        l1 = list(self.parent.getPrio())
        l2 = list(self.child.getPrio())
        return tuple([l1[i] + l2[i] for i in range(len(l2))])

#Maybe we will support the below. Putting them in so that we can better parse CSS but
#actual implementation will only be later if ever.

class PseudoClassSelector(Selector): 
    def __init__(self, val, child):
        self.val = val 
        self.child = child

    def matches(self, node):
        return False
    
    def __repr__(self):
        return "PseudoClassSelector: {} Child: ({})".format(self.val, self.child)
    
    def __eq__(self, value):
        return isinstance(value, PseudoClassSelector) and self.val == value.val and self.getPrio() == value.getPrio()

    def getPrio(self):
        t = list(self.child.getPrio() if self.child != None else (0,0,0,0))
        t[2] += 1
        return tuple(t)

class PseudoElementSelector(Selector):
    def __init__(self, val, child):
        self.val = val 
        self.child = child

    def matches(self, node):
        return False
    
    def __repr__(self):
        return "PseudoElementSelector: {} Child: ({})".format(self.val, self.child)
    
    def __eq__(self, value):
        return isinstance(value, PseudoElementSelector) and self.val == value.val and self.getPrio() == value.getPrio()

    def getPrio(self):
        t = list(self.child.getPrio() if self.child != None else (0,0,0,0))
        t[3] += 1
        return tuple(t)

class AttributeSelector(Selector): 
    def __init__(self, val, child):
        self.val = val 
        self.child = child

    def matches(self,node):
        #TODO: implement
        return False 
    
    def __repr__(self):
        return "AttributeSelector: {} Child ({})".format(self.val, self.child)
    
    def __eq__(self, value):
        return isinstance(value, AttributeSelector) and self.val == value.val and self.child == value.child
    
    def getPrio(self):
        t = list(self.child.getPrio() if self.child != None else (0,0,0,0))
        t[2] += 1
        return tuple(t)


if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    sp = SelectorParser()
    #print(sp.parse("div:hover.class[attr]::first-line"))
