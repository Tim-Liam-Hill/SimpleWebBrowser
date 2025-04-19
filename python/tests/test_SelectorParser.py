from src.CSS.SelectorParser import *
from src.HTMLParser import Element
import unittest

print("Testing Selector Parsing")

class TestSelector(unittest.TestCase):
    '''Ensure that a sequence of one or more selectors not separated by whitespace is parsed correctly'''


    def test_getBase(self):
        sp = SelectorParser()


        '''Universal'''
        self.assertEqual(sp.getBase("*", None), UniversalSelector(None))

        '''Class'''
        self.assertEqual(sp.getBase(".mrMeowMeowmeopw", None), ClassSelector("mrMeowMeowmeopw", None))
        self.assertEqual(sp.getBase(".m", None), ClassSelector("m", None))
        with self.assertRaises(IndexError):
            sp.getBase('.', None)

        '''ID'''
        self.assertEqual(sp.getBase("#mrMeowMeowmeopw", None), IDSelector("mrMeowMeowmeopw", None))
        self.assertEqual(sp.getBase("#m", None), IDSelector("m", None))
        with self.assertRaises(IndexError):
            sp.getBase('#', None)

        '''Tag'''
        self.assertEqual(sp.getBase("div", None), TagSelector("div", None))
        self.assertEqual(sp.getBase("d", None), TagSelector("d", None))
        with self.assertRaises(ValueError):
            sp.getBase('', None)

    def testParse(self):

        sp = SelectorParser()

        '''Simple cases: just one selector'''
        self.assertEqual(sp.parse("span"), TagSelector("span",None))
        self.assertEqual(sp.parse(".class"), ClassSelector("class", None))
        self.assertEqual(sp.parse("#id"),IDSelector("id", None))

        '''Base selectors in sequence'''
        self.assertEqual(sp.parse("span.class"), ClassSelector("class",TagSelector("span",None)))
        self.assertEqual(sp.parse("span.class#id"), IDSelector("id",ClassSelector("class",TagSelector("span",None))))
        self.assertEqual(sp.parse("span.class.class2#id.class3"), ClassSelector("class3" ,IDSelector("id" ,ClassSelector("class2",ClassSelector("class",TagSelector("span",None))) )))
        self.assertEqual(sp.parse("#id.class"), ClassSelector("class", IDSelector("id",None))) 

        '''Pseudo and attribute by themselves'''
        self.assertEqual(sp.parse(":hover"), PseudoClassSelector("hover", None))
        self.assertEqual(sp.parse("::first-child"), PseudoElementSelector("first-child", None))
        self.assertEqual(sp.parse("[val='meow']"), AttributeSelector("val='meow'", None))


        '''Base selectors with single pseudo/attribute'''
        self.assertEqual(sp.parse("div:hover"), PseudoClassSelector("hover",TagSelector("div",None)))
        self.assertEqual(sp.parse("*::first-line"), PseudoElementSelector("first-line",UniversalSelector(None)))
        self.assertEqual(sp.parse("#id[nyan|=10]"), AttributeSelector("nyan|=10",IDSelector("id",None)))

        '''Complex examples'''
        self.assertEqual(sp.parse('div:hover.class[attr]::first-line'),PseudoElementSelector("first-line",AttributeSelector("attr",ClassSelector("class",PseudoClassSelector("hover",TagSelector("div",None))))))
        self.assertEqual(sp.parse("*[count=3][a=b]:has().class#id"), IDSelector("id",ClassSelector("class",PseudoClassSelector("has()",AttributeSelector("a=b",AttributeSelector("count=3",UniversalSelector(None)))))))

        '''Errors'''
        with self.assertRaises(ValueError):
            sp.parse("")
        with self.assertRaises(ValueError):
            sp.parse("@div.class")
        with self.assertRaises(IndexError):
            sp.parse("#.class")
        with self.assertRaises(ValueError):
            sp.parse("[insid")
        with self.assertRaises(ValueError):
            sp.parse("[quot']")
        with self.assertRaises(ValueError):
            sp.parse("span:")

    def test_Prios(self):
        '''Explicitly ensure priorities are set correctly'''
        
        '''Simplest cases'''
        self.assertEqual(UniversalSelector(None).getPrio(), (0,0,0,0))
        self.assertEqual(TagSelector("h1",None).getPrio(), (0,0,0,1))
        self.assertEqual(ClassSelector("hello",None).getPrio(), (0,0,1,0))
        self.assertEqual(IDSelector("hello",None).getPrio(), (0,1,0,0))
        self.assertEqual(PseudoClassSelector("hover",None).getPrio(), (0,0,1,0))
        self.assertEqual(PseudoElementSelector("first-line",None).getPrio(), (0,0,0,1))
        self.assertEqual(AttributeSelector("val",None).getPrio(), (0,0,1,0))

        '''Compound cases'''
        self.assertEqual(PseudoElementSelector("first-letter",PseudoClassSelector("hover",UniversalSelector(None))).getPrio(),(0,0,1,1))
        self.assertEqual(PseudoElementSelector("first-letter",PseudoClassSelector("hover",TagSelector("div",None))).getPrio(),(0,0,1,2))
        self.assertEqual(AttributeSelector("attr",AttributeSelector("value='1'",IDSelector("id",TagSelector("span",None)))).getPrio(),(0,1,2,1) )

        '''Combinator cases'''
        self.assertEqual(DescendantSelector(TagSelector("p",None),ClassSelector("a",None)).getPrio(), (0,0,1,1))
        self.assertEqual(ChildSelector(IDSelector("pa",None),ClassSelector("a",None)).getPrio(), (0,1,1,0))
        self.assertEqual(SubsequentSiblingSelector(IDSelector("pa",None),TagSelector("a",None)).getPrio(), (0,1,0,1))
        self.assertEqual(NextSiblingSelector(IDSelector("pa",None),IDSelector("ad",TagSelector("div",None))).getPrio(), (0,2,0,1))
        self.assertEqual(NextSiblingSelector( TagSelector("h1",IDSelector("id",None)) ,AttributeSelector("attr",AttributeSelector("value='1'",IDSelector("id",TagSelector("span",None))))).getPrio(),(0,2,2,2) )




    def test_Matches(self):
        '''Ensure that the subset of CSS we intend to parse will match intended elements
        
        Note that at the time of implementation, PseudoClass, PseudoElements and Attributes do not have matching implemented and return false by default
        '''
        
        '''Simplest cases'''
        self.assertTrue(UniversalSelector(None).matches(Element("div",{}, None)))
        self.assertTrue(TagSelector("div",None).matches(Element("div",{}, None)))
        self.assertTrue(ClassSelector("meow",None).matches(Element("div",{"class":"meow happy"}, None)))
        self.assertTrue(IDSelector("myID",None).matches(Element("div",{"id":"myID"}, None)))

        '''Compound cases'''

        self.assertTrue(ClassSelector("class",TagSelector("div",None)).matches(Element("div",{"class":"big class "}, None)))
        self.assertTrue(IDSelector("myID",ClassSelector("class",TagSelector("div",None))).matches(Element("div",{"class":"big class ","id":"myID"}, None)))

        '''Ensure does not match for certain cases (eg, substrings)'''
        self.assertFalse(ClassSelector("is",None).matches(Element("div",{"class":"homeostasis"},None)))
        self.assertFalse(IDSelector("id",None).matches(Element("div",{"id":"ID"},None)))

        '''Expect false for now'''
        self.assertFalse(PseudoClassSelector("hover",None).matches(Element("div",{"hover":"{}"},None)))
        self.assertFalse(PseudoElementSelector("first-child",None).matches(Element("div",{"first-child":"{}"},None)))
        self.assertFalse(AttributeSelector("val",None).matches(Element("div",{"val":"{}"},None)))

        '''Combinator selectors'''
        #a <p> directly inside a <div>
        p = Element("div",{},None)
        pc = Element("p",{}, p)
        p.children = [pc]
        self.assertTrue(DescendantSelector(TagSelector("div",None),TagSelector("p",None)).matches(pc))
        self.assertTrue(ChildSelector(TagSelector("div",None),TagSelector("p",None)).matches(pc))

        #<div class="myClass"><span><p id="ID"></p></span></div>
        p = Element("div",{"class":"myClass"},None)
        pc = Element("span",{}, p)
        pcc = Element("p", {"id":"ID"}, pc)
        p.children = [pc]
        pc.children = [pcc]
        self.assertTrue(DescendantSelector(TagSelector("div",None),TagSelector("p",None)).matches(pcc))
        self.assertTrue(DescendantSelector(TagSelector("div",None),IDSelector("ID",None)).matches(pcc))
        self.assertTrue(DescendantSelector(ClassSelector("myClass",TagSelector("div",None)),TagSelector("p",None)).matches(pcc))
        self.assertFalse(ChildSelector(TagSelector("div",None),TagSelector("p",None)).matches(pcc))

        #chained together
        p = Element("div",{"class":"highest"},None)
        pc = Element("span",{"class":"1"}, p)
        p.children = [pc]
        pcc = Element("div", {"class":"2"}, pc)
        pc.children = [pcc]
        pccc = Element("div", {},pcc)
        pcc.children = pccc
        pcccc = Element("span", {"class":"3"},pccc)
        pccc.children = [pcccc] 
        #writing these test cases is giving me a headache lol
        self.assertTrue(DescendantSelector(DescendantSelector(TagSelector("div",None),TagSelector("div",None)),TagSelector("span",ClassSelector("3",None))),TagSelector("span",ClassSelector("3", None)).matches(pcccc))
        self.assertTrue(DescendantSelector(ChildSelector(TagSelector("div",ClassSelector("highest",None)),TagSelector("span",None)),TagSelector("span",ClassSelector("3",None))).matches(pcccc))
        self.assertFalse(ChildSelector(DescendantSelector(ClassSelector("highest",None),ClassSelector("2",None)),TagSelector("span",None)).matches(pcccc))


        p = Element("div",{"id":"meow"},None)
        pc1 = Element("span",{"class":"bright"},p)
        pc2 = Element("span",{"class":"dark"},p)
        pc3 = Element("span",{"class":"dull"},p)
        pc4 = Element("span", {"class":"dark"},p)
        p.children = [pc1,pc2,pc3,pc4]

        pc2c = Element("p",{},pc2)
        pc2.children = [pc2c] 

        pc2cc = Element("ul",{},pc2c)
        pc2c.children = [pc2cc]

        self.assertTrue(SubsequentSiblingSelector(ClassSelector("dark",None),ClassSelector("dark",None)).matches(pc4))
        self.assertFalse(NextSiblingSelector(ClassSelector("dark",None),ClassSelector("dark",None)).matches(pc4))
        self.assertTrue(NextSiblingSelector(ClassSelector("dull",None),ClassSelector("dark",None)).matches(pc4))
        self.assertTrue(NextSiblingSelector(ClassSelector("dark",None),ClassSelector("dull",None)).matches(pc3))
        self.assertTrue(NextSiblingSelector(NextSiblingSelector(ClassSelector("dark",None),ClassSelector("dull",None)),ClassSelector("dark",None)).matches(pc4))
        self.assertTrue(NextSiblingSelector(NextSiblingSelector(NextSiblingSelector(ClassSelector("bright",None),ClassSelector("dark",None)),ClassSelector("dull",None)),ClassSelector("dark",None)).matches(pc4))
        self.assertTrue(DescendantSelector(NextSiblingSelector(ClassSelector("bright",None),ClassSelector("dark",None)),TagSelector("ul",None)).matches(pc2cc))
        self.assertFalse(ChildSelector(NextSiblingSelector(ClassSelector("bright",None),ClassSelector("dark",None)),TagSelector("ul",None)).matches(pc2cc))
        self.assertFalse(NextSiblingSelector(ClassSelector("dark",None),TagSelector("p",None)).matches(pc2c))








