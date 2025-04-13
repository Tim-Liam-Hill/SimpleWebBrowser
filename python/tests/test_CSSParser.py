from src.CSS.CSSParser import CSSParser, TagSelector, ClassSelector
from src.HTMLParser import Element
import unittest


class TestCSSParser(unittest.TestCase):
    '''Ensure that we parse CSS files correctly according to the subset of CSS we wish to support
    
    These tests are limited to CSS parsing and application to nodes, NOT to the actual functionality of how CSS 
    values affect a layout object (see layout tests for this). Tests are of 2 types: 1 is whether we extract values
    correctly and 2 is whether we apply values correctly.
    '''

        #TESTS RELATED TO CSS PARSING/EXTRACTING

    def test_extract(self):
        '''Tests whether the CSSParser can extract the expected set of rules for various selectors'''

        # #Empty Stylesheet
        # css = ""
        # css_rules = []
        # self.assertEqual(CSSParser(css).parse(), css_rules)

        # #Empty body
        # css = "body {}"
        # css_rules = [(TagSelector("body"), {})]
        # self.assertEqual(CSSParser(css).parse(), css_rules)
        
        # #Simple Tag Selector
        # css = "div {width: 100px;}"
        # css_rules = [(TagSelector("div"), {'width':'100px'})]
        # self.assertEqual(CSSParser(css).parse(), css_rules)

        # #Rule not ending in a semicolon
        # css = "div {width: 100px}"
        # css_rules = [(TagSelector("div"), {'width':'100px'})]
        # self.assertEqual(CSSParser(css).parse(), css_rules)

        # #CSS comments shouldn't impact code
        # css = "div {width: 100px}\n\\*I am a comment*\\ p {background-color: red}"
        # css_rules = [(TagSelector("div"), {'width':'100px'}), (TagSelector("p"),{'background-color':'red'})]
        # self.assertEqual(CSSParser(css).parse(), css_rules)

        # #Consecutive semicolons
        # css = "div {;;;;}"
        # self.assertEqual(CSSParser(css).parse(), [(TagSelector("div"), {})])

    def test_malformed(self):
        '''Tests whether the CSSParser can function if given malformed input'''

        #Missing closing brace
        css = "div {width: 100px;"
        css_rules = []
        self.assertEqual(CSSParser(css).parse(), css_rules)

        #Missing opening brace
        css = "div width: 100px;}"
        css_rules = []
        self.assertEqual(CSSParser(css).parse(), css_rules)



    #TESTS RELATED TO SELECTORS

    def test_classSelector(self):
        '''Ensure that a class selector matches nodes correctly'''

        #no class attribute
        self.assertFalse(ClassSelector("myClass", 1).matches(Element("",{},None)))

        #class attribute not matching 
        self.assertFalse(ClassSelector("myClass", 1).matches(Element("",{"class":"notMyClass"},None)))

        #class attribute matching
        self.assertTrue(ClassSelector("myClass", 1).matches(Element("",{"class":"myClass"},None)))

        #many classes none matching 
        self.assertFalse(ClassSelector("myClass", 1).matches(Element("",{"class":"beans toast coffee"},None)))

        #many classes 1 matching
        self.assertTrue(ClassSelector("myClass", 1).matches(Element("",{"class":"beans myClass coffee"},None)))

        #many classes, ensure substring does not match
        self.assertFalse(ClassSelector("myClass", 1).matches(Element("",{"class":"beans myClassLonger coffee"},None)))

        #test whitespaces don't cause non-matching
        self.assertTrue(ClassSelector("myClass", 1).matches(Element("",{"class":" \n beans \n  myClass  \t coffee"},None)))

    def test_tagSelector(self):
        pass 

    def test_IDSelector(self):
        pass 

    def test_universalSelector(self):
        pass 

    def test_descendantSelector(self):
        pass

    #TESTS RELATED TO PRIORITIES


        pass