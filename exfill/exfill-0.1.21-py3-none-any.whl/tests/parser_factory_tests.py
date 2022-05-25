from parsers.linkedin_parser import LinkedinParser
from parsers.parser_factory import NoMatchingParserType, ParserFactory
from tests.main import BaseTest


class TestParserFactory(BaseTest):
    def test_parser_factory_type(self):
        self.config = BaseTest.load_test_config(self)

        self.assertIsInstance(
            ParserFactory.create("linkedin", self.config), LinkedinParser
        )

        with self.assertRaises(NoMatchingParserType):
            ParserFactory.create("not_linkedin", self.config)
