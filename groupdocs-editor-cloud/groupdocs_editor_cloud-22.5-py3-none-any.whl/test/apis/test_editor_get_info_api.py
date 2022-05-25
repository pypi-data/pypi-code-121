# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd">
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

import unittest
import datetime
from groupdocs_editor_cloud import *
from test.test_context import TestContext
from test.test_file import TestFile

class TestEditorGetInfoApi(TestContext):
    """EditorApi unit tests"""

    def test_get_info_returns_file_not_found(self):
        request = GetInfoRequest(TestFile.not_exist().ToFileInfo())
        with self.assertRaises(ApiException) as context:
            self.info_api.get_info(request)
        self.assertEqual("Can't find file located at 'somefolder\\not-exist.docx'.", context.exception.message)

    def test_get_info(self):
        request = GetInfoRequest(TestFile.password_protected_docx().ToFileInfo())
        data = self.info_api.get_info(request)
        self.assertEqual(4, data.page_count)

if __name__ == '__main__':
    unittest.main()
