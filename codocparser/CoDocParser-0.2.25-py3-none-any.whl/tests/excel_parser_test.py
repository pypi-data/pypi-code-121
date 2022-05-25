# Press the green button in the gutter to run the script.
import os
import pytest



class TestExcelDocumentParser:
    """
    测试Excel文档解析器
    """
    def test_text_block_parse(self):
        """
        测试文本块解析
        """

        converter = DocConverterFactory.create('pdf', 'txt')
        output_file = converter.convert(os.getcwd() + "\\files\\zim.pdf",os.getcwd().replace("\\tests","") +"\\output")

        assert output_file is not None

    def test_standard_table_block_parse(self):
        """
        测试标准表格解析
        """

        converter = DocConverterFactory.create('pdf', 'txt')
        output_files = converter.bulk_convert([os.getcwd() + "\\files\\zim.pdf"], os.getcwd().replace("\\tests","") +r"\output")

        assert len(output_files) == 1

    def test_mixed_table_block_parse(self):
        """
        测试混杂模式表格解析
        """

        converter = DocConverterFactory.create('pdf', 'txt')
        output_files = converter.bulk_convert([os.getcwd() + "\\files\\zim.pdf"],
                                              os.getcwd().replace("\\tests", "") + r"\output")

        assert len(output_files) == 1


if __name__ == '__main__':
    pytest.main("-q --html=report.html")
