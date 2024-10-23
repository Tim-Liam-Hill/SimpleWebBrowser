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
        with self.assertRaises(ValueError):
            url.extractScheme("view-source:view-source:http://google.com")

    
    def test_validateURL(self):
        url = URL("http://google.com")
        #some URLS
        self.assertTrue(url.validateURL('http://google.com'))
        self.assertTrue(url.validateURL('https://google.eu/a/asd'))
        self.assertTrue(url.validateURL('https://meow.google.eu/a/asd?mrmeow=meow'))
        self.assertTrue(url.validateURL('http://localhost:3000/'))
        
        #view-source
        self.assertTrue(url.validateURL('view-source:http://localhost:3000/'))
        self.assertTrue(url.validateURL('view-source:http://google.com'))
        self.assertTrue(url.validateURL('view-source:https://google.eu/a/asd'))
        self.assertTrue(url.validateURL('view-source:https://meow.google.eu/a/asd?mrmeow=meow'))

        #data
        self.assertTrue(url.validateURL('data:,meowmeowmeow#$(*&!)'))
        self.assertTrue(url.validateURL('data:media,meowmeowmeow#$(*&!)'))
        self.assertTrue(url.validateURL('data:media;base64,meowmeowmeow#$(*&!)'))
        self.assertTrue(url.validateURL('data:;base64,meowmeowmeow#$(*&!)'))

        #file paths

        self.assertTrue(url.validateURL('file:///path/file.jpg'))
        self.assertTrue(url.validateURL('file:///path/file e_-/*'))
        self.assertTrue(url.validateURL("file://C:\\users\\tim\\file.jpg"))

        #invalid values

        
#TODO: test URI validation 

if __name__=='__main__':
    unittest.main()

