from src.URL import URL 
import unittest

class TestURL(unittest.TestCase):
    
    def test_extractScheme(self):
        '''Test URL Scheme extraction'''
        #cases:
        #- one for each scheme at least
        #- include ports
        #- are we making this case sensitive??? 
        url = URL("http://google.com")
        self.assertEqual(url.extractScheme("http://google.com"),("http","google.com"))
        


if __name__=='__main__':
    unittest.main()

