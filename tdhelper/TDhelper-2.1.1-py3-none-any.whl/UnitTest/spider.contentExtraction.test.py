import __init__
import unittest
from TDhelper.Spider.contentExtraction import lineblock
from TDhelper.network.http.http_helper import m_http


class TestSpider(unittest.TestCase):
    def test_spider_contentExtraction(self):
        spider_http = m_http()
        Extraction_set = lineblock(5, 0.2, 50)
        content, statucode = spider_http.getcontent(
            "https://www.sipwps.com/x/113923.html"
        )
        # content= str(content,"utf-8")
        self.assertEqual((statucode,), (200,))
        result = Extraction_set.getBody(content)
        print("正文", result)


if __name__ == "__main__":
    unittest.main()
