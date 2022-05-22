import __init__
import unittest
from TDhelper.network.http.http_helper import m_http
test_url="http://www.163.com"
H = m_http()

class testHttpHelper(unittest.TestCase):
    def test_post(self):
        result= H.getcontent(test_url)
        print("[INFO]:%s" % result[0])        

if __name__ == "__main__":
    unittest.main()