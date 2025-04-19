from src.HTMLParser import HTMLParser
import unittest

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