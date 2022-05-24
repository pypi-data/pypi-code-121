import logging
from jlogger import j_logger
import unittest


class TestRotatingFileLog(unittest.TestCase):
    def setUp(self):
        j_logger.set_logger("rotate_logger_unittest.log", max_size=2048)
        self.logger=logging.getLogger(__name__)

    def test_wrap(self):
        assert self.logger.hasHandlers()
        for i in range(200):
            self.logger.info(f"Testing wrap and rotate. {i} ")

    def test_formatter_change(self):
        self.logger.info(f"Test test_formatter_change starts.")
        fmtter = self.logger.root.handlers[0].formatter
        new_fmtter = logging.Formatter("%(asctime)s — myname — %(funcName)s:%(lineno)d — %(levelname)s — %(message)s")
        self.logger.root.handlers[0].setFormatter(new_fmtter)
        self.logger.info(f"after changing formatter.")        
        self.logger.root.handlers[0].setFormatter(fmtter)
        self.logger.info(f"restore formatter.")        



if __name__ == '__main__':
    unittest.main()
