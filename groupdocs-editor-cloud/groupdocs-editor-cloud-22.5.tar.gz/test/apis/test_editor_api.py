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

class TestEditorApi(TestContext):
    """EditorApi unit tests"""

    def test_OpenSaveDocx(self):
        # Load
        file = TestFile.four_pages_docx()
        loadOptions = LoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSaveDocxProtected(self):
        # Load
        file = TestFile.password_protected_docx()
        loadOptions = LoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)        

    def test_OpenSaveDocxWithOptions(self):
        # Load
        file = TestFile.password_protected_docx()
        loadOptions = WordProcessingLoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path
        loadOptions.enable_pagination = True
        loadOptions.font_extraction = "ExtractAll"        

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = WordProcessingSaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name
        saveOptions.enable_pagination = True
        saveOptions.format = "Docx"
        saveOptions.password = file.password
        saveOptions.protection_password = file.password
        saveOptions.protection_type = "AllowOnlyComments"         

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path) 

    def test_OpenSaveXlsx(self):
        # Load
        file = TestFile.four_sheets_xlsx()
        loadOptions = LoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSaveXlsxProtected(self):
        # Load
        file = TestFile.password_protected_xlsx()
        loadOptions = LoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSaveXlsxWithOptions(self):
        # Load
        file = TestFile.password_protected_xlsx()
        loadOptions = SpreadsheetLoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path
        loadOptions.exclude_hidden_worksheets = True

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SpreadsheetSaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 
        saveOptions.format = "xlsx"
        saveOptions.password = file.password
        saveOptions.protection_password = file.password
        saveOptions.protection_type = "All"

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSaveTsv(self):
        # Load
        file = TestFile.sample_tsv()
        loadOptions = LoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSaveTsvWithOptions(self):
        # Load
        file = TestFile.sample_tsv()
        loadOptions = DelimitedTextLoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path
        loadOptions.separator = "\t"
        loadOptions.convert_numeric_data = True
        loadOptions.treat_consecutive_delimiters_as_one = True

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = DelimitedTextSaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 
        saveOptions.encoding = "UTF-8"
        saveOptions.format = "tsv"
        saveOptions.keep_separators_for_blank_row = True

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSaveText(self):
        # Load
        file = TestFile.document_txt()
        loadOptions = LoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSaveTextWithOptions(self):
        # Load
        file = TestFile.document_txt()
        loadOptions = TextLoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path
        loadOptions.enable_pagination = True
        loadOptions.leading_spaces = "Trim"
        loadOptions.recognize_lists = True

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = TextSaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 
        saveOptions.add_bidi_marks = True
        saveOptions.encoding = "UTF-8"
        saveOptions.format = "txt"
        saveOptions.preserve_table_layout = True

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSavePresentation(self):
        # Load
        file = TestFile.presentation()
        loadOptions = LoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = SaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name 

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)

    def test_OpenSavePresentationWithOptions(self):
        # Load
        file = TestFile.presentation_with_widden_slide()
        loadOptions = PresentationLoadOptions()
        loadOptions.file_info = file.ToFileInfo()
        loadOptions.output_path = self.output_path
        loadOptions.show_hidden_slides = True
        loadOptions.slide_number = 0        

        loadResult = self.edit_api.load(LoadRequest(loadOptions))
        self.assertTrue(loadResult.html_path)
        self.assertTrue(loadResult.resources_path)

        # Save
        saveOptions = PresentationSaveOptions()
        saveOptions.file_info = file.ToFileInfo()
        saveOptions.html_path = loadResult.html_path
        saveOptions.resources_path = loadResult.resources_path
        saveOptions.output_path = self.output_path  + "/" +  file.file_name
        saveOptions.password = "password"

        saveResult = self.edit_api.save(SaveRequest(saveOptions))
        self.assertEqual(saveOptions.output_path, saveResult.path)        

if __name__ == '__main__':
    unittest.main()
