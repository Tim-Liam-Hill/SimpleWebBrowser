from src.CSS.SelectorParser import SelectorParser, UniversalSelector, TagSelector, ClassSelector, IDSelector
import unittest


class TestSelector(unittest.TestCase):
    '''Ensure that a sequence of one or more selectors not separated by whitespace is parsed correctly'''


    def test_getBase(self):
        sp = SelectorParser()


        '''Universal'''
        self.assertEqual(sp.getBase("*"), UniversalSelector(None))

        '''Class'''
        self.assertEqual(sp.getBase(".mrMeowMeowmeopw"), ClassSelector("mrMeowMeowmeopw", None))
        self.assertEqual(sp.getBase(".m"), ClassSelector("m", None))
        with self.assertRaises(IndexError):
            sp.getBase('.')

        '''ID'''
        self.assertEqual(sp.getBase("#mrMeowMeowmeopw"), IDSelector("mrMeowMeowmeopw", None))
        self.assertEqual(sp.getBase("#m"), IDSelector("m", None))
        with self.assertRaises(IndexError):
            sp.getBase('#')

        '''Tag'''
        self.assertEqual(sp.getBase("div"), TagSelector("div", None))
        self.assertEqual(sp.getBase("d"), TagSelector("d", None))
        with self.assertRaises(ValueError):
            sp.getBase('')
