from src.CSS.SelectorsParser import *
from src.CSS.SelectorParser import *
import unittest

print("Testing Selectors Parsing")

class TestSelectorsParser(unittest.TestCase):
    '''Ensure that a sequence of one or more seelctors separated by combinators is parsed correctly'''

    def test_parse(self):
        '''Ensures that the correct array of selectors is returned for a given string'''

        sp = SelectorsParser()
        '''simple cases: array length 1'''
        self.assertEqual(sp.parse("div.class"),[ClassSelector("class",TagSelector("div",None))])
        self.assertEqual(sp.parse("div.class#id"),[IDSelector("id",ClassSelector("class",TagSelector("div",None)))])
        self.assertEqual(sp.parse("div.class:hover#id[attr]"),[AttributeSelector("attr",IDSelector("id",PseudoClassSelector("hover", ClassSelector("class",TagSelector("div",None)))))])

        self.assertEqual(sp.parse(":hover"), [PseudoClassSelector("hover", None)])
        self.assertEqual(sp.parse("::first-child"), [PseudoElementSelector("first-child", None)])
        self.assertEqual(sp.parse("[val='meow']"), [AttributeSelector("val='meow'", None)])

        '''combinators included'''
        self.assertEqual(sp.parse("span.happy div.sad>#id"),[ChildSelector(DescendantSelector(ClassSelector("happy",TagSelector("span",None)),ClassSelector("sad",TagSelector("div",None))),IDSelector("id",None))])
        #make sure spaces don't mess things up
        self.assertEqual(sp.parse("span     div"),[DescendantSelector(TagSelector("span",None),TagSelector("div",None))])
        self.assertEqual(sp.parse("span  >   div"),[ChildSelector(TagSelector("span",None),TagSelector("div",None))])
        self.assertEqual(sp.parse("  span  +   div  "),[NextSiblingSelector(TagSelector("span",None),TagSelector("div",None))])
        self.assertEqual(sp.parse("  span     ~div  "),[SubsequentSiblingSelector(TagSelector("span",None),TagSelector("div",None))])

        '''multiple selectors'''
        self.assertEqual(sp.parse("span,div,#id"),[TagSelector("span",None),TagSelector("div",None),IDSelector("id",None)])
        self.assertEqual(sp.parse(" span ,div  ,#id   "),[TagSelector("span",None),TagSelector("div",None),IDSelector("id",None)])
        self.assertEqual(sp.parse("span.c,div[attr],#id"),[ClassSelector("c",TagSelector("span",None)),AttributeSelector("attr",TagSelector("div",None)),IDSelector("id",None)])

        '''everything'''
        self.assertEqual(sp.parse("span.happy div.sad>#id, *[count=3][a=b]:has().class#id"),[ChildSelector(DescendantSelector(ClassSelector("happy",TagSelector("span",None)),ClassSelector("sad",TagSelector("div",None))),IDSelector("id",None)),IDSelector("id",ClassSelector("class",PseudoClassSelector("has()",AttributeSelector("a=b",AttributeSelector("count=3",UniversalSelector(None))))))])

        '''error cases'''
        #don't really care what exactly the exception is, just care that it is thrown
        with self.assertRaises(Exception):
            sp.parse(",")

        with self.assertRaises(Exception):
            sp.parse("div,")

        with self.assertRaises(Exception):
            sp.parse(">div")
        
        with self.assertRaises(Exception):
            sp.parse("div, +div")
        
        with self.assertRaises(Exception):
            sp.parse("div,,div")

    def test_squash(self):
        '''Ensures that a list of base selectors with combinator selectors between them is amalgamated into the correct result'''

        sp = SelectorsParser()

        '''Valid cases'''
        l = [TagSelector("div",None),ChildSelector(None,None),ClassSelector("class",None)]
        self.assertEqual(sp.squashCombinators(l), ChildSelector(TagSelector("div",None),ClassSelector("class",None)))
        l = [TagSelector("div",None),DescendantSelector(None,None),ClassSelector("class",None)]
        self.assertEqual(sp.squashCombinators(l), DescendantSelector(TagSelector("div",None),ClassSelector("class",None)))
        l = [TagSelector("div",None),SubsequentSiblingSelector(None,None),ClassSelector("class",None)]
        self.assertEqual(sp.squashCombinators(l), SubsequentSiblingSelector(TagSelector("div",None),ClassSelector("class",None)))
        l = [TagSelector("div",None),NextSiblingSelector(None,None),ClassSelector("class",None)]
        self.assertEqual(sp.squashCombinators(l), NextSiblingSelector(TagSelector("div",None),ClassSelector("class",None)))

        l = [IDSelector("id",ClassSelector("div",None)),ChildSelector(None,None),AttributeSelector("val",None),NextSiblingSelector(None,None),PseudoElementSelector("hover",None)]
        self.assertEqual(sp.squashCombinators(l), NextSiblingSelector(ChildSelector(IDSelector("id",ClassSelector("div",None)),AttributeSelector("val",None)),PseudoElementSelector("hover",None)))

        '''Error Cases'''
        l = []
        with self.assertRaises(ValueError):
            sp.squashCombinators(l)

        l = [ChildSelector(None,None),IDSelector("a",None)]
        with self.assertRaises(ValueError):
            sp.squashCombinators(l)

        l = [ChildSelector(None,None),ChildSelector(None,None)]
        with self.assertRaises(ValueError):
            sp.squashCombinators(l)
        
        l = [IDSelector("a",None),IDSelector("a",None)]
        with self.assertRaises(ValueError):
            sp.squashCombinators(l)
