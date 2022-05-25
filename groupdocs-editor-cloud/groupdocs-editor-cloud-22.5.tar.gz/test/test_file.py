# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="test_file.py">
#   Copyright (c) 2003-2022 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

from __future__ import absolute_import

from groupdocs_editor_cloud import FileInfo

class TestFile:
    """Test file"""

    @classmethod
    def not_exist(cls):
        f = TestFile()
        f.file_name = "not-exist.docx"
        f.folder = "somefolder\\"
        return f

    @classmethod
    def four_pages_docx(cls):
        f = TestFile()
        f.file_name = "four-pages.docx"
        f.folder = "WordProcessing\\"
        return f

    @classmethod
    def password_protected_docx(cls):
        f = TestFile()
        f.file_name = "password-protected.docx"
        f.folder = "WordProcessing\\"
        f.password = "password"
        return f

    @classmethod
    def four_sheets_xlsx(cls):
        f = TestFile()
        f.file_name = "four-sheets.xlsx"
        f.folder = "Spreadsheet\\"
        return f

    @classmethod
    def password_protected_xlsx(cls):
        f = TestFile()
        f.file_name = "four-sheets-protected.xlsx"
        f.folder = "Spreadsheet\\"
        f.password = "password"
        return f

    @classmethod
    def sample_tsv(cls):
        f = TestFile()
        f.file_name = "sample.tsv"
        f.folder = "Spreadsheet\\"
        return f

    @classmethod
    def document_txt(cls):
        f = TestFile()
        f.file_name = "document.txt"
        f.folder = "Text\\"
        return f

    @classmethod
    def presentation(cls):
        f = TestFile()
        f.file_name = "with-notes.pptx"
        f.folder = "Presentation\\"
        return f

    @classmethod
    def presentation_with_widden_slide(cls):
        f = TestFile()
        f.file_name = "with-two-visible-and-one-hidden-slide.odp"
        f.folder = "Presentation\\"
        return f                                

    @classmethod
    def get_test_files(cls):
        return [
            cls.four_pages_docx(),
            cls.password_protected_docx(),
            cls.four_sheets_xlsx(),
            cls.password_protected_xlsx(),
            cls.sample_tsv(),
            cls.document_txt(),
            cls.presentation(),
            cls.presentation_with_widden_slide()
        ]

    def ToFileInfo(self):
        f = FileInfo()
        f.file_path = self.folder + self.file_name
        if hasattr(self, 'password'):
            f.password = self.password
        return f
