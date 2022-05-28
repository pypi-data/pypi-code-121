from dcclab import sciMetadata as mtdt
import env
import unittest
import os


class TestSciMetadata(env.DCCLabTestCase):
    def setUp(self) -> None:
        self.sciDir = os.path.join(str(self.dataDir), '20190101_12_12_12_900nm_16x_512x1024_1000f_8dpf')
        os.mkdir(self.sciDir)

        self.rawPath = os.path.join(self.sciDir, '20190101_12_12_12_900nm_16x_512x1024_1000f_8dpf_XYT.raw')
        with open(self.rawPath, 'w') as file:
            file.write('TEST RAW FILE.')

        self.iniPath = os.path.join(self.sciDir, '20190101_12_12_12_900nm_16x_512x1024_1000f_8dpf_XYT.ini')
        with open(self.iniPath, 'w') as file:
            file.write('[_]\nTest_File = This is a test file\nno.of.channels = 1.000000000000\nblank_line = blank\n'
                       'frame.count = 1000.000000000000\n\nx.pixels = 1024.000000000000\ny.pixels = 512.000000000000\n'
                       'x.voltage = 5.000000000000\ny.voltage = 1.250000000000\n\nwrong.line = bleh\n'
                       'pixel.resolution = 5.000000000000\nLaser.Power = 21.500000000000\n')

        self.xmlPath = os.path.join(self.sciDir, '20190101_12_12_12_900nm_16x_512x1024_1000f_8dpf_OME.xml')
        with open(self.xmlPath, 'w') as file:
            file.write('<TEST>\n')
            file.write('\t<items>\n')
            file.write('\t</items>\n')
            file.write('</TEST>\n')

    def tearDown(self) -> None:
        if os.path.exists(self.rawPath):
            os.remove(self.rawPath)
        if os.path.exists(self.iniPath):
            os.remove(self.iniPath)
        if os.path.exists(self.xmlPath):
            os.remove(self.xmlPath)
        os.rmdir(self.sciDir)

    def testconfirmFolderHasScientificaFilesAllFiles(self):
        metadata = mtdt(self.sciDir)
        testRaw, testIni, testXml = metadata.confirmFolderHasScientificaFiles()
        self.assertEqual(testRaw, self.rawPath)
        self.assertEqual(testIni, self.iniPath)
        self.assertEqual(testXml, self.xmlPath)

    def testconfirmFolderHasScientificaFilesMissingFiles(self):
        metadata = mtdt(self.sciDir)
        os.remove(self.iniPath)
        with self.assertRaises(FileNotFoundError): metadata.confirmFolderHasScientificaFiles()

    def testFileName(self):
        metadata = mtdt(self.sciDir)
        self.assertEqual('20190101_12_12_12_900nm_16x_512x1024_1000f_8dpf', metadata.fileName)

    def testRawPath(self):
        metadata = mtdt(self.sciDir)
        self.assertEqual(self.rawPath, metadata.rawPath)

    def testIniPath(self):
        metadata = mtdt(self.sciDir)
        self.assertEqual(self.iniPath, metadata.iniPath)

    def testXmlPath(self):
        metadata = mtdt(self.sciDir)
        self.assertEqual(self.xmlPath, metadata.xmlPath)

    def testDate(self):
        metadata = mtdt(self.sciDir)
        self.assertEqual('2019-01-01 12:12:12', metadata.date)

    def testExtractDataFromIniFile(self):
        metadata = mtdt(self.sciDir)
        self.assertTrue(metadata.extractDataFromIniFile())

    def testKeys(self):
        metadata = mtdt(self.sciDir)
        self.assertEqual({'ZebraFishRAW': {'Laser_Power': 'REAL', 'frame_count': 'INTEGER', 'ini_path': 'TEXT',
                                           'no_of_channels': 'INTEGER', 'path': 'TEXT PRIMARY KEY',
                                           'pixel_resolution': 'REAL', 'raw_path': 'TEXT', 'x_pixels': 'INTEGER',
                                           'x_voltage': 'REAL', 'xml_path': 'TEXT', 'y_pixels': 'INTEGER',
                                           'y_voltage': 'REAL'}}, metadata.keys)

    def testAsDict(self):
        metadata = mtdt(self.sciDir)
        self.assertEqual(
            {'Laser_Power': '21.500000000000', 'frame_count': '1000.000000000000', 'ini_path': self.iniPath,
             'no_of_channels': '1.000000000000', 'path': self.sciDir, 'pixel_resolution': '5.000000000000',
             'raw_path': self.rawPath, 'x_pixels': '1024.000000000000', 'x_voltage': '5.000000000000',
             'xml_path': self.xmlPath, 'y_pixels': '512.000000000000', 'y_voltage': '1.250000000000'}, metadata.asDict)


if __name__ == '__main__':
    unittest.main()
