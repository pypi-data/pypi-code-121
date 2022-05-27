import env
from dcclab import CZIFilter as fltr
from dcclab import CZIMetadata as mtdt
import xml.etree.ElementTree as ET
import unittest
import os

class TestFilter(env.DCCLabTestCase):
    def setUp(self):
        self.directory = str(self.dataDir)
        self.testPath = os.path.join(self.directory, 'testCziFile.czi')
        self.missingEntriesPath = os.path.join(self.directory, 'MissingEntries.xml')
        self.meta = mtdt(self.testPath)

    def testSetFilterSetIdAndTypeExpectedValues(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.setFilterSetIdAndFilterType(), ('FilterSet:1', 'Excitation'))

    def testSetFilterSetIdAndTypeMissingKeys(self):
        filter = fltr('', self.meta.root)
        self.assertIsNone(filter.setFilterSetIdAndFilterType()[0])

    def testSetFilterSetIdAndTypeMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        filter = fltr('Filter:1', root)
        self.assertIsNone(filter.setFilterSetIdAndFilterType()[0])

    def testSetChannelIdExpectedValue(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.setChannelId(), 'Channel:0')

    def testSetChannelIdMissingKeys(self):
        filter = fltr('', self.meta.root)
        self.assertIsNone(filter.setChannelId())

    def testSetChannelIdMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        filter = fltr('Filter:1', root)
        self.assertIsNone(filter.setChannelId())

    def testSetDichroicIdExpectedValue(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.setDichroicId(), 'Dichroic:1')

    def testSetDichroicIdMissingKeys(self):
        filter = fltr('', self.meta.root)
        self.assertIsNone(filter.setDichroicId())

    def testSetDichroicIdMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        filter = fltr('Filter:1', root)
        self.assertIsNone(filter.setDichroicId())

    def testSetDichroicExpectedValue(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.setDichroic(), 495)

    def testSetDichroicMissingKeys(self):
        filter = fltr('', self.meta.root)
        self.assertIsNone(filter.setDichroic())

    def testSetDichroicMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        filter = fltr('Filter:1', root)
        self.assertIsNone(filter.setDichroic())

    def testGetTypeExpectedValue(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.getType(), 'Excitation')

    def testGetTypeNoneValue(self):
        filter = fltr('', self.meta.root)
        self.assertIsNone(filter.getType())

    def testGetChannelIdExpectedValue(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.getChannelId(), 'Channel:0')

    def testGetChannelIdNoneValue(self):
        filter = fltr('', self.meta.root)
        self.assertIsNone(filter.getChannelId())

    def testGetFilterRangeExpectedValue(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.getFilterRange(), '450-490')

    def testGetFilterRangeNoneValues(self):
        filter = fltr('', self.meta.root)
        self.assertEqual(filter.getFilterRange(), 'None-None')

    def testGetDichroicExpectedValue(self):
        filter = fltr('Filter:1', self.meta.root)
        self.assertEqual(filter.getDichroic(), 495)

    def testGetDichroicNoneValue(self):
        filter = fltr('', self.meta.root)
        self.assertIsNone(filter.getDichroic())


if __name__ == '__main__':
    unittest.main()