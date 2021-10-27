import unittest
import pybundle.main

class TestTotoStdout(unittest.TestCase):

    def test_toto_stdout(self):
      print(pybundle.main)

if __name__ == '__main__':
    unittest.main()
