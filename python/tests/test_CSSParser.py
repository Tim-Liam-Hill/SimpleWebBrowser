from src.CSS.CSSParser import CSSParser
from src.CSS.SelectorParser import * 
import os
import unittest

print("Testing CSS Parsing")

#TODO: get a host of large CSS files from 'the wild', place them in a folder and just make sure we can handle them somewhat
#That is to say, make sure they are the types of files we would want to parse without issue, then ensure no errors are thrown
class TestCSSParser(unittest.TestCase):
    '''Ensure that we parse CSS files correctly according to the subset of CSS we wish to support
    
    These tests are limited to CSS parsing and application to nodes, NOT to the actual functionality of how CSS 
    values affect a layout object (see layout tests for this). Tests are of 2 types: 1 is whether we extract values
    correctly and 2 is whether we apply values correctly.
    '''

    RELATIVE_DIR = './cssparser_test_cases'

    def test_parse(self):
        '''Tests whether the CSSParser can extract the expected set of rules for various selectors'''
        parser = CSSParser()

        #Empty Stylesheet
        self.assertEqual(parser.parse(""), [])

        #Empty body
        self.assertEqual(parser.parse("body {}"), [(TagSelector("body", None), {})])
        
        #Non-EmptyRule
        self.assertEqual(parser.parse("div {width: 100px;}"), [(TagSelector("div",None), {'width':'100px'})])

        # #Rule not ending in a semicolon should still be accepted
        self.assertEqual(parser.parse("div {width: 100px}"), [(TagSelector("div",None), {'width':'100px'})])

        #CSS comments shouldn't impact code
        css = "div {width: 100px}\n/*I am a comment*/ p {background-color: red}"
        rules = [(TagSelector("div",None), {'width':'100px'}), (TagSelector("p",None),{'background-color':'red'})]
        self.assertEqual(parser.parse(css), rules)

        #Consecutive semicolons
        self.assertEqual(parser.parse("div {;;;;}"), [(TagSelector("div",None), {})])

        #spaces/tabs/newlines in between value/property pairs shouldnt reflect in their final values 
        self.assertEqual(parser.parse(" div { width : 100px ; \tcolor\n:\n red;}"), [(TagSelector("div",None), {'width':'100px','color':'red'})])

        #consecutive rules
        self.assertEqual(parser.parse("div {width: 100px;}span{color:red;}"), [(TagSelector("div",None), {'width':'100px'}),(TagSelector("span",None),{'color':'red'})])

        #space separated value
        self.assertEqual(parser.parse("div {border: 1em solid black;}"), [(TagSelector("div",None), {'border':'1em solid black'})])

        #Multiple property value pairs in a rule
        self.assertEqual(parser.parse("#id.class{color: blue;font-size:large}"), [(ClassSelector("class",IDSelector("id",None)), {'color':'blue','font-size': 'large'})])

        #multiple tags for the same rule
        self.assertEqual(parser.parse("div,.class,#id{color:red;}"),[(TagSelector("div",None),{'color':'red'}),(ClassSelector("class",None),{'color':'red'}),(IDSelector("id",None),{'color':'red'})])

        #at least one complex example
        css = '''div{
                    background-color: aqua;
                }span{color:red;}

                /* A comment */

                #meow {
                    font: 1em sans-serif;
                    border: 1em solid black;
                    font-size: large;
                }

                div[attr] > p::after, .container {
                    display: flex;
                    flex-direction: column;
                    flex-wrap: wrap-reverse;
                    justify-content: center;
                }'''
        rules = [(TagSelector("div",None),{"background-color":"aqua"}),\
                 (TagSelector("span",None),{"color":"red"}),\
                 (IDSelector("meow",None),{"font":"1em sans-serif","border":"1em solid black","font-size":"large"}),\
                 (ChildSelector(AttributeSelector("attr",TagSelector("div",None)),PseudoElementSelector("after",TagSelector("p",None))),\
                  {"display":"flex","flex-direction":"column","flex-wrap":"wrap-reverse","justify-content":"center"}),\
                  (ClassSelector("container",None),{"display":"flex","flex-direction":"column","flex-wrap":"wrap-reverse","justify-content":"center"})]
        self.assertEqual(parser.parse(css),rules)

        #Errors -> don't throw Exception
        #As far as possible, the CSSParser should NOT throw errors. At most it should just print out (in debug) that it is 
        #discarding something

        #selector only
        self.assertEqual(parser.parse("div"),[])

        #body only 
        self.assertEqual(parser.parse("{}"),[])

        #second rule malformed 
        self.assertEqual(parser.parse("div {width: 100px;} span{"), [(TagSelector("div",None), {'width':'100px'})])

        #first rule malformed
        self.assertEqual(parser.parse("{} div {width: 100px;}"), [(TagSelector("div",None), {'width':'100px'})])
        self.assertEqual(parser.parse("} div {width: 100px;}"), [(TagSelector("div",None), {'width':'100px'})])
        self.assertEqual(parser.parse("{ div {width: 100px;}"), [(TagSelector("div",None), {'width':'100px'})])

        #missing closing brace. In this scenario we only care that we don't throw an exception
        parser.parse("div{color:red")

        #TODO: add more cases

    def test_gracefulHandle(self):
        '''Reads through a few stylesheets taken from random sites and ensures we don't throw errors'''
        parser = CSSParser()

        test_dir = '{}/{}'.format(os.path.dirname(os.path.abspath(__file__)), TestCSSParser.RELATIVE_DIR)
        file_list = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f))]

        for file_name in file_list:
            file_path = os.path.join(test_dir, file_name)
            #print('Testing {}'.format(file_name))
            with open(file_path, 'r') as file:
                content = file.read()
                parser.parse(content)

        pass 

    def test_parseStyleBody(self):
        '''Tests whether the 'style' attribute string of a node is parsed as expected'''

        parser = CSSParser()

        #empty body
        self.assertEqual(parser.parseStyleBody(""), {})

        #some values
        self.assertEqual(parser.parseStyleBody("prop:val"),{"prop":"val"})
        self.assertEqual(parser.parseStyleBody("prop:val;"),{"prop":"val"})
        self.assertEqual(parser.parseStyleBody("prop:val;width:10px; height : 20em"),{"prop":"val","width":"10px","height":"20em"})

        #don't care about the rest at present
