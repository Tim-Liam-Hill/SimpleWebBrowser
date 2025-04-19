# from src.CSS.CSSParser import CSSParser, TagSelector, ClassSelector, IDSelector
# from src.HTMLParser import Element
# import unittest


# class TestCSSParser(unittest.TestCase):
#     '''Ensure that we parse CSS files correctly according to the subset of CSS we wish to support
    
#     These tests are limited to CSS parsing and application to nodes, NOT to the actual functionality of how CSS 
#     values affect a layout object (see layout tests for this). Tests are of 2 types: 1 is whether we extract values
#     correctly and 2 is whether we apply values correctly.
#     '''

#         #TESTS RELATED TO CSS PARSING/EXTRACTING

#     def test_extractBasic(self):
#         '''Tests whether the CSSParser can extract the expected set of rules for various selectors'''

#         # #Empty Stylesheet
#         # css = ""
#         # css_rules = []
#         # self.assertEqual(CSSParser(css).parse(), css_rules)

#         # #Empty body
#         # css = "body {}"
#         # css_rules = [(TagSelector("body"), {})]
#         # self.assertEqual(CSSParser(css).parse(), css_rules)
        
#         # #Simple Tag Selector
#         # css = "div {width: 100px;}"
#         # css_rules = [(TagSelector("div"), {'width':'100px'})]
#         # self.assertEqual(CSSParser(css).parse(), css_rules)

#         # #Rule not ending in a semicolon
#         # css = "div {width: 100px}"
#         # css_rules = [(TagSelector("div"), {'width':'100px'})]
#         # self.assertEqual(CSSParser(css).parse(), css_rules)

#         # #CSS comments shouldn't impact code
#         # css = "div {width: 100px}\n\\*I am a comment*\\ p {background-color: red}"
#         # css_rules = [(TagSelector("div"), {'width':'100px'}), (TagSelector("p"),{'background-color':'red'})]
#         # self.assertEqual(CSSParser(css).parse(), css_rules)

#         # #Consecutive semicolons
#         # css = "div {;;;;}"
#         # self.assertEqual(CSSParser(css).parse(), [(TagSelector("div"), {})])

#     def test_extractDescendants(self):
#         '''Ensures that chains of various descendant selectors are extracted correctly'''

#         pass 

#     def test_extractSequence(self):
#         '''Ensures sequences of various tags can be extracted correctly'''

#         pass 

#     def test_extracPseudoSelectors(self):
#         '''Ensures the subset of PseudoSelectors supported are extracted correctly.'''

#         pass

#     def test_extractAttribute(self):
#         pass 

#     def test_complexCases(self):
#         '''Cases with multiple selectors used together'''

#         #div[value='arg'].class::after#id:hover > span {background-color: brown;}

#     def test_malformed(self):
#         '''Tests whether the CSSParser can function if given malformed input'''

#         #Missing closing brace
#         css = "div {width: 100px;"
#         css_rules = []
#         self.assertEqual(CSSParser(css).parse(), css_rules)

#         #Missing opening brace
#         css = "div width: 100px;}"
#         css_rules = []
#         self.assertEqual(CSSParser(css).parse(), css_rules)

#         #TODO: test with > followed by , (same for other non-space combinator symbols)



#     #TESTS RELATED TO SELECTORS

#     def test_classSelector(self):
#         '''Ensure that a class selector matches nodes correctly'''

#         #no class attribute
#         self.assertFalse(ClassSelector("myClass", []).matches(Element("",{},None)))

#         #class attribute not matching 
#         self.assertFalse(ClassSelector("myClass", []).matches(Element("",{"class":"notMyClass"},None)))

#         #class attribute matching
#         self.assertTrue(ClassSelector("myClass", []).matches(Element("",{"class":"myClass"},None)))

#         #many classes none matching 
#         self.assertFalse(ClassSelector("myClass", []).matches(Element("",{"class":"beans toast coffee"},None)))

#         #many classes 1 matching
#         self.assertTrue(ClassSelector("myClass", []).matches(Element("",{"class":"beans myClass coffee"},None)))

#         #many classes, ensure substring does not match
#         self.assertFalse(ClassSelector("myClass", []).matches(Element("",{"class":"beans myClassLonger coffee"},None)))

#         #test whitespaces don't cause non-matching
#         self.assertTrue(ClassSelector("myClass", []).matches(Element("",{"class":" \n beans \n  myClass  \t coffee"},None)))

#     def test_tagSelector(self):
#         pass 

#     def test_IDSelector(self):
        
#         #test no id
#         self.assertFalse(IDSelector("myID",[]).matches(Element("",{},None)))

#         #test id no matches 
#         self.assertFalse(IDSelector("myID",[]).matches(Element("",{"id":"meow"},None)))

#         #test id exact match 
#         self.assertTrue(IDSelector("myID",[]).matches(Element("",{"id":"myID"},None)))

#         #test id doesn't match due to case 
#         self.assertFalse(IDSelector("myID",[]).matches(Element("",{"id":"MyID"},None)))

#         #test id doesn't match due to substring 
#         self.assertFalse(IDSelector("myID",[]).matches(Element("",{"id":"NOTmyID"},None)))

#         #test id does not match when trailing/leading whitespace
#         self.assertFalse(IDSelector("myID",[]).matches(Element("",{"id":"\nmyID"},None)))
#         self.assertFalse(IDSelector("myID",[]).matches(Element("",{"id":" myID"},None)))
#         self.assertFalse(IDSelector("myID",[]).matches(Element("",{"id":"myID\t"},None)))


#     def test_universalSelector(self):
#         pass 

#     def test_descendantSelector(self):
#         pass
    
#     def test_attributeSelector(self):
#         pass 

#     #TESTS RELATED TO PRIORITIES (TODO: populate)