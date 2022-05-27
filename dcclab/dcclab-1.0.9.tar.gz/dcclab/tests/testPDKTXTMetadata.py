from dcclab import PDKTXTMetadata as pdkMtdt
import unittest
import env
import os


class TestPDKTXTMetadata(env.DCCLabTestCase):
    def setUp(self) -> None:
        self.iniPath = os.path.join(str(self.dataDir), '20190101_12_12_12_900nm_16x_512x1024_1000f_8dpf_XYT.ini')
        with open(self.iniPath, 'w') as file:
            file.write('[_]\nTest_File = This is a test file\nno.of.channels = 1.000000000000\nblank_line = blank\n'
                       'frame.count = 1000.000000000000\n\nx.pixels = 1024.000000000000\ny.pixels = 512.000000000000\n'
                       'x.voltage = 5.000000000000\ny.voltage = 1.250000000000\n\nwrong.line = bleh\n'
                       'pixel.resolution = 5.000000000000\nLaser.Power = 21.500000000000\n')

    def tearDown(self) -> None:
        os.remove(self.iniPath)

    def testReadFile(self):
        metadata = pdkMtdt(self.iniPath)
        self.assertTrue(metadata.readFile())

    def testAsDict(self):
        metadata = pdkMtdt(self.iniPath)
        self.assertEqual(
            {'Laser_Power': '21.500000000000', 'frame_count': '1000.000000000000', 'no_of_channels': '1.000000000000',
             'pixel_resolution': '5.000000000000', 'x_pixels': '1024.000000000000', 'x_voltage': '5.000000000000',
             'y_pixels': '512.000000000000', 'y_voltage': '1.250000000000'}, metadata.asDict)

    def testKeys(self):
        metadata = pdkMtdt(self.iniPath)
        self.assertEqual(
            {'Laser_Power': 'REAL', 'frame_count': 'INTEGER', 'no_of_channels': 'INTEGER', 'pixel_resolution': 'REAL',
             'x_pixels': 'INTEGER', 'x_voltage': 'REAL', 'y_pixels': 'INTEGER', 'y_voltage': 'REAL'}, metadata.keys)


if __name__ == '__maine__':
    unittest.main()
