import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
#the above makes sure that we can import every module from src normally AND that any module we import
#can import the modules they depend on (I think)
import src

if __name__=='__main__':
    unittest.main()
