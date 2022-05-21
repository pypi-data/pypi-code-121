"""
unittest for markdown_text_decorator
"""
import unittest
from markdown import Markdown

MARKDOWN_EXTENSIONS = [
    "markdown_text_decorator"
]

class MarkdownTextDecoratorTestCase(unittest.TestCase):
    """ test class for markdown_text_decorator
    """

    def setUp(self):
        self.__md2html = Markdown(extensions=MARKDOWN_EXTENSIONS)

    def test_strikethrough(self):
        """test for strikethrough
        """
        markdown_input = "~~This is~~ strikethrough ~~line.~~"
        expected_output = "<p><s>This is</s> strikethrough <s>line.</s></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_insert(self):
        """test for insert
        """
        markdown_input = "++This is++ insert ++line.++"
        expected_output = "<p><ins>This is</ins> insert <ins>line.</ins></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_delete(self):
        """test for delete
        """
        markdown_input = "--This is-- delete --line.--"
        expected_output = "<p><del>This is</del> delete <del>line.</del></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_superscript(self):
        """test for superscript
        """
        markdown_input = "^^This is^^ superscript ^^line^^"
        expected_output = "<p><sup>This is</sup> superscript <sup>line</sup></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_subscript(self):
        """test for subscript
        """
        markdown_input = "^This is^ subscript ^line^"
        expected_output = "<p><sub>This is</sub> subscript <sub>line</sub></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_mark(self):
        """test for mark
        """
        markdown_input = "!!This is!! mark !!line!!"
        expected_output = "<p><mark>This is</mark> mark <mark>line</mark></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_ruby(self):
        """test for ruby
        """
        markdown_input = "{ Markdown Text Decorator : mɑ́ːkdàun tékst dékərèitər }"
        expected_output = "<p><ruby>Markdown Text Decorator<rt>mɑ́ːkdàun tékst dékərèitər</rt></ruby></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

if __name__ == '__main__':
    print("")
    print("MarkdownTextDecoratorTestCase")
    print("-" * 70)
    unittest.main(argv=[__file__, "-v"])
