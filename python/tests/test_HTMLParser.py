from src.HTML.HTMLParser import HTMLParser
import unittest
import os

print("Testing HTML Parsing")

class TestHTMLParser(unittest.TestCase):
    HTML_RELATIVE_DIR = './htmlparser_test_cases'

    def test_validHtml(self):
        '''Ensure that we don't fail to parse a suite of valid html'''

        test_dir = '{}/{}'.format(os.path.dirname(os.path.abspath(__file__)), TestHTMLParser.HTML_RELATIVE_DIR)
        file_list = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f))]

        for file_name in file_list:
            file_path = os.path.join(test_dir, file_name)
            #print('Testing {}'.format(file_name))
            with open(file_path, 'r') as file:
                content = file.read()
                HTMLParser(content).parse()


