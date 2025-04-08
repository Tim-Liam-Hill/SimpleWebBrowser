from src.CSS.CSSParser import CSSParser, TagSelector
import unittest


class TestCSSParser(unittest.TestCase):
    '''Ensure that we parse CSS files correctly according to the subset of CSS we wish to support
    
    These tests are limited to CSS parsing and application to nodes, NOT to the actual functionality of how CSS 
    values affect a layout object (see layout tests for this). Tests are of 2 types: 1 is whether we extract values
    correctly and 2 is whether we apply values correctly.
    '''

    def test_extract(self):
        

        css1 = "div {width: 100px;}"
        css1_rules = [(TagSelector("div"), {'width':'100px'})]

        self.assertEqual(CSSParser(css1).parse(), css1_rules)

    def test_tag(self):
        pass 

    def test_class(self):
        pass 

    def test_id(self):
        pass 

    def test_universal(self):
        pass