from src.CSS.SelectorParser import SelectorParser
from enum import Enum, unique

@unique
class States(Enum):
    '''Represents all valid states for DFA of selectors parser'''

    START = "start"

DEFAULT_TRANSITION = "default"
ACCEPT ="accept"
NEXT = "next"

DFA = {
    "start": States.START,
    "states": {
        States.START: { }
     } 
}   

class SelectorsParser:
    '''Parses string representing one or more selectors for a rule'''

    def __init__(self):
        pass 

    def parse(self, selector):
        '''Given a string representing one or more selectors, returns a matching array of selector objects'''
        pass 
        #REMEMBER TO HANDLE COMMAS NICELY WHORE.
