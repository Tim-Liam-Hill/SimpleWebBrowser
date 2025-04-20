from src.Browser import Browser
import sys
import logging
import os 
import tkinter
logger = logging.getLogger(__name__)

DEFAULT_FILE_PATH = '../tests/htmlparser_test_cases/test.html' #path from this file's directory to default file we show
CURR_FILEPATH = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    b = Browser()

    if(len(sys.argv) != 2):
        b.load(f'file://{CURR_FILEPATH}/{DEFAULT_FILE_PATH}')
    else: b.load(sys.argv[1])
    tkinter.mainloop()
    