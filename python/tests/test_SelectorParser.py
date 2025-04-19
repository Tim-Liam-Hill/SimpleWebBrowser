from src.CSS.SelectorParser import SelectorParser, UniversalSelector, TagSelector, ClassSelector, IDSelector, PseudoClassSelector, PseudoElementSelector, AttributeSelector
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

        
        '''Compound casese'''
        self.assertEqual(PseudoElementSelector("first-letter",PseudoClassSelector("hover",UniversalSelector(None))).getPrio(),(0,0,1,1))
        self.assertEqual(PseudoElementSelector("first-letter",PseudoClassSelector("hover",TagSelector("div",None))).getPrio(),(0,0,1,2))
        self.assertEqual(AttributeSelector("attr",AttributeSelector("value='1'",IDSelector("id",TagSelector("span",None)))).getPrio(),(0,1,2,1) )


