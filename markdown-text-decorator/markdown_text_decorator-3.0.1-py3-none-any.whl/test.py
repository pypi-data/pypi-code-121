"""
Markdown Text Decorator Extension
========================================

This is a [Python-Markdown](https://pypi.org/project/Markdown/) Text Decorator extension package.

Copyright 2022 Silver Bullet Software All rigths reserved.

License: MIT see) file:LICENSE

"""
import unittest
from markdown import Markdown
import markdown_text_decorator.sample

MARKDOWN_EXTENSIONS = [
    "markdown_text_decorator"
]

TEST_SAMPLE_EXPECT_RESULT = '''<h1>Markdown Text Decoration</h1>
<p><s>This is</s> strikethrough <s>line</s></p>
<p><ins>This is</ins> insert <ins>line</ins> </p>
<p><del>This is</del> delete <del>line</del></p>
<p><sup>This is</sup> superscript <sup>line</sup></p>
<p><sub>This is</sub> subscript <sub>line</sub></p>
<p><mark>This is</mark> mark <mark>line</mark></p>
<p><span class="underline" style="text-decoration: underline">This is</span> underline <span class="underline" style="text-decoration: underline">line</span></p>
<p><span class="underoverline" style="text-decoration: underline overline">This is</span> underoverline <span class="underoverline" style="text-decoration: underline overline">line</span></p>
<p><span class="overline" style="text-decoration: overline">This is</span> overline <span class="overline" style="text-decoration: overline">line</span></p>
<p><ruby>Markdown Text Decorator<rt>mɑ́ːkdàun tékst dékərèitər</rt></ruby></p>
<p><ruby>日本語<rt><mark>Japanese</mark></rt></ruby> <ruby>英語<rt><mark>English</mark></rt></ruby></p>'''


class MarkdownTextDecoratorTestCase(unittest.TestCase):
    """ test class for markdown_text_decorator
    """

    def setUp(self):
        self.__md2html = Markdown(extensions=MARKDOWN_EXTENSIONS)

    def test_strikethrough(self):
        """test for strikethrough
        """
        markdown_input = "~~This is~~ strikethrough ~~line~~"
        expected_output = "<p><s>This is</s> strikethrough <s>line</s></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_insert(self):
        """test for insert
        """
        markdown_input = "++This is++ insert ++line++"
        expected_output = "<p><ins>This is</ins> insert <ins>line</ins></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_delete(self):
        """test for delete
        """
        markdown_input = "--This is-- delete --line--"
        expected_output = "<p><del>This is</del> delete <del>line</del></p>"
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

    def test_underline(self):
        """test for underline
        """
        markdown_input = "=This is= underline =text="
        expected_output = '<p><span class="underline" style="text-decoration: underline">This is</span> underline <span class="underline" style="text-decoration: underline">text</span></p>'
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_underoverline(self):
        """test for underoverline
        """
        markdown_input = "==This is== underoverline ==text=="
        expected_output = '<p><span class="underoverline" style="text-decoration: underline overline">This is</span> underoverline <span class="underoverline" style="text-decoration: underline overline">text</span></p>'
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_overline(self):
        """test for overline
        """
        markdown_input = "===This is=== overline ===text==="
        expected_output = '<p><span class="overline" style="text-decoration: overline">This is</span> overline <span class="overline" style="text-decoration: overline">text</span></p>'
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_all(self):
        """test for all at once
        """
        expected_output = TEST_SAMPLE_EXPECT_RESULT
        html_output = markdown_text_decorator.sample.run()
        self.assertTrue(expected_output == html_output)

class MarkdownTextDecoratorIsNotDestructiveTestCase(unittest.TestCase):
    """ test class for checking exist expression works properly.
    """

    def setUp(self):
        self.__md2html = Markdown(extensions=MARKDOWN_EXTENSIONS)

    def test_normal(self):
        """test for normal
        """
        markdown_input = "This is normal line"
        expected_output = "<p>This is normal line</p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_bold_p1(self):
        """test for bold pattern 1
        """
        markdown_input = "**This is** bold pattern 1 **line**"
        expected_output = "<p><strong>This is</strong> bold pattern 1 <strong>line</strong></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_bold_p2(self):
        """test for bold pattern 2
        """
        markdown_input = "__This is__ bold pattern 2 __line__"
        expected_output = "<p><strong>This is</strong> bold pattern 2 <strong>line</strong></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_italic_p1(self):
        """test for italic pattern 1
        """
        markdown_input = "*This is* italic pattern 1 *line*"
        expected_output = "<p><em>This is</em> italic pattern 1 <em>line</em></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_italic_p2(self):
        """test for italic pattern 2
        """
        markdown_input = "_This is_ italic pattern 2 _line_"
        expected_output = "<p><em>This is</em> italic pattern 2 <em>line</em></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_bold_italic_p1(self):
        """test for bold_italic pattern 1
        """
        markdown_input = "**_This is_** bold italic pattern 1 **_line_**"
        expected_output = "<p><strong><em>This is</em></strong> bold italic pattern 1 <strong><em>line</em></strong></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_bold_italic_p2(self):
        """test for bold_italic pattern 2
        """
        markdown_input = "***This is*** bold italic pattern 2 ***line***"
        expected_output = "<p><strong><em>This is</em></strong> bold italic pattern 2 <strong><em>line</em></strong></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)

    def test_bold_italic_p3(self):
        """test for bold_italic pattern 3
        """
        markdown_input = "___This is___ bold italic pattern 3 ___line___"
        expected_output = "<p><strong><em>This is</em></strong> bold italic pattern 3 <strong><em>line</em></strong></p>"
        html_output = self.__md2html.convert(markdown_input)
        self.assertTrue(expected_output == html_output)


if __name__ == '__main__':
    print("")
    print("MarkdownTextDecoratorTest")
    print("-" * 70)
    unittest.main(argv=[__file__, "-v"])
