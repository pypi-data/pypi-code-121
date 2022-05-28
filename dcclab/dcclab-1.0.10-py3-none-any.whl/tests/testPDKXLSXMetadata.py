from dcclab import PDKXLSXMetadata as mtdt
import xlrd
import xlwt
import env
import unittest
import os


class TestPDKXLSXMetadata(env.DCCLabTestCase):
    def setUp(self) -> None:
        self.filePath = os.path.join(str(self.dataDir), 'unittest.xlsx')
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('test_1')
        sheet.write(0, 0, 'test_column_1')
        sheet.write(0, 1, 'test_column_2')
        sheet.write(0, 2, 'file_path')
        sheet.write(1, 0, 'abcd')
        sheet.write(1, 1, '1234')
        sheet.write(1, 2, '\\test\\testing\\testerinoo')
        sheet = workbook.add_sheet('test_2')
        sheet.write(0, 0, 'test_id_1')
        sheet.write(0, 1, 'file_path')
        sheet.write(1, 0, '01')
        sheet.write(1, 1, '\\test\\01')
        sheet.write(2, 0, '02')
        sheet.write(2, 1, '\\test\\02')
        workbook.save(self.filePath)

    def tearDown(self) -> None:
        os.remove(self.filePath)

    def testFilename(self):
        metadata = mtdt(self.filePath)
        self.assertEqual('unittest', metadata.fileName())

    def testGetWorkbook(self):
        metadata = mtdt(self.filePath)
        self.assertTrue(type(metadata.getWorkbook()) == xlrd.book.Book)

    def testGetWorksheets(self):
        metadata = mtdt(self.filePath)
        sheets = metadata.getWorksheets()
        for sheet in sheets:
            self.assertTrue(type(sheet), xlrd.sheet.Sheet)

    def testKeys(self):
        metadata = mtdt(self.filePath)
        keys = metadata.keys
        self.assertTrue(keys)

    def testAsDict(self):
        metadata = mtdt(self.filePath)
        self.assertTrue(metadata.asDict)


if __name__ == '__main__':
    unittest.main()
