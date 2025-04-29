from src.CSS.layouts.BlockLayout import BlockLayout
from src.CSS.layouts.DocumentLayout import DocumentLayout
from src.HTML.HTMLParser import Element, Text
import unittest
import logging

print("Testing Layout functionality")

class TestHTMLParser(unittest.TestCase):
    '''Tests the functionality of The various layout types implemented
    
    Specifically ensures that heights, widths, x values, y values and display lists
    are computed correctly relative to different tags and CSS properties.
    '''

    def test_basicTrees(self):
        '''Tests whether basic cases of Inline and Block elements produce the expected tree'''
        
        pass

    def test_X(self):
        '''Tests whether x values for children are computed correctly based on parents and CSS'''

        pass

    def test_Y(self):
        '''Tests whether y values for children are computed correctly based on parents and CSS'''

        pass

    def test_Height(self):
        '''Tests whether height values for children are computed correctly based on parents and CSS'''

        pass

    def test_Width(self):
        '''Tests whether width values for children are computed correctly based on parents and CSS'''

        pass

    def test_Block(self):
        '''Tests whether a block layout object will correctly createblock and inline children'''

        logging.basicConfig(level=logging.DEBUG)
        p = Element("div",{"display":"block"},None)
        c1 = Element("span",{"display":"inline"}, p)
        c2 = Text("mr meow meow",p)
        c1c1 = Text("inside span",c1)
        c1.children = [c1c1]
        p.children= [c1,c2]
        block = BlockLayout(p,DocumentLayout(None,700),None)
        block.layout()
        block.print(0)

#Test blocklayout in an inlinelayout

#Adding some test cases here for later:
'''
<!DOCTYPE html>
<html lang="en-US" xml:lang="en-US">
<head>

</head>

<body class="main">

<p>Web browsers are ubiquitous, but how do they work? This book
explains, building a basic but complete web browser, from networking to
JavaScript, in a couple thousand lines of Python.</p>
<div class="wide-ad">
<div>First div inside div</div>
<span>Second span inside div</span>
</div>
</body>
</html>

The above should ensure that the first child of the second div (which itself is also a blocklayout object) inherits the correct starting point

'''