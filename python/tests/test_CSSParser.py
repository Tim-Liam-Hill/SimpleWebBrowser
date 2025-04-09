from src.CSS.CSSParser import CSSParser, TagSelector
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

        #Empty Stylesheet
        css = ""
        css_rules = []
        self.assertEqual(CSSParser(css).parse(), css_rules)

        #Empty body
        css = "body {}"
        css_rules = [(TagSelector("body"), {})]
        self.assertEqual(CSSParser(css).parse(), css_rules)
        
        
        #Simple Tag Selector
        css = "div {width: 100px;}"
        css_rules = [(TagSelector("div"), {'width':'100px'})]
        self.assertEqual(CSSParser(css).parse(), css_rules)



        #Rule not ending in a semicolon
        css = "div {width: 100px}"
        css_rules = [(TagSelector("div"), {'width':'100px'})]
        self.assertEqual(CSSParser(css).parse(), css_rules)


    
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

    #TESTS RELATED TO APPLICATION OF CSS STYLES

    def test_tag(self):
        pass 

    def test_class(self):
        pass 

    def test_id(self):
        pass 

    def test_universal(self):
        pass