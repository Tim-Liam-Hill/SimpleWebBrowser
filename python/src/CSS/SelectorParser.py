from abc import ABC, abstractmethod
from src.HTMLParser import Element

class SelectorParser:
    '''Parses a string representing one selector (that could have attributes/pseudo elements or pseudo classes)'''

    def __init__(self):
        pass 

    def parse(self,s):
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

class ClassSelector(Selector):
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

class IDSelector(Selector):

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

class UniversalSelector(Selector):

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

class SequenceSelector(Selector): #TODO: test me
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
