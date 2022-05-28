import env
from dcclab import CZIChannel as chnnl
from dcclab import CZIMetadata as mtdt
import xml.etree.ElementTree as ET
import unittest
import os


class TestCziChannel(env.DCCLabTestCase):
    def setUp(self):
        self.directory = str(self.dataDir)
        self.testPath = os.path.join(self.directory, 'testCziFile.czi')
        self.missingEntriesPath = os.path.join(self.directory, 'MissingEntries.xml')
        self.missingKeysPath = os.path.join(self.directory, 'MissingKeys.xml')
        self.meta = mtdt(self.testPath, 'testCziFile.czi')

    def testSetExWavelengthFilterExpectedValue(self):
        channel = chnnl(['Channel:1', 'DAPI', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.exWavelengthFilter, '335-383')

    def testSetExWavelengthFilterNotFound(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.exWavelengthFilter)

    def testSetExWavelengthFilterEmptyFilterList(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], [], self.meta.root)
        self.assertIsNone(channel.exWavelengthFilter)

    def testSetExWavelengthFilterNotFilterList(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], [1, 2, 3], self.meta.root)
        self.assertIsNone(channel.exWavelengthFilter)

    def testSetEmWavelengthFilterExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.emWavelengthFilter, '500-550')

    def testSetEmWavelengthFilterNotFound(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.emWavelengthFilter)

    def testSetEmWavelengthFilterNoFilters(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], [], self.meta.root)
        self.assertIsNone(channel.emWavelengthFilter)

    def testSetBeamsplitterExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.beamSplitter, 495)

    def testSetBeamsplitterNotFound(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.beamSplitter)

    def testSetBeamsplitterNoFilters(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], [], self.meta.root)
        self.assertIsNone(channel.beamSplitter)

    def testSetReflectorExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setReflector(), '38 HE Green Fluorescent Prot')

    def testSetReflectorMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setReflector())

    def testSetReflectorMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setReflector())

    def testSetContrastMethodExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setContrastMethod(), 'Fluorescence')

    def testSetContrastMethodMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setContrastMethod())

    def testSetContrastMethodMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setContrastMethod())

    def testSetLightSourceExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setLightSource(), 'HXP 120 V')

    def testSetLightSourceMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setLightSource())

    def testSetLightSourceMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setLightSource())

    def testSetLightSourceIntensityExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setLightSourceIntensity(), 58.32)

    def testSetLightSourceIntensityMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setLightSourceIntensity())

    def testSetLightSourceIntensityMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setLightSourceIntensity())

    def testSetDyeNameExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setDyeName(), 'EGFP')

    def testSetDyeNameMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setDyeName())

    def testSetDyeNameMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setDyeName())

    def testSetChannelColorExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setChannelColor(), '#FF00FF5B')

    def testSetChannelColorMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setChannelColor())

    def testSetChannelColorMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setChannelColor())

    def testSetExWavelengthExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setExWavelength(), 488)

    def testSetExWavelengthMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setExWavelength())

    def testSetExWavelengthMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setExWavelength())

    def testSetEmWavelengthExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setEmWavelength(), 509)

    def testSetEmWavelengthMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setEmWavelength())

    def testSetEmWavelengthMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setEmWavelength())

    def testSetExposureTimeExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setExposureTime(), 950.0)

    def testSetExposureTimeMissingKeys(self):
        channel = chnnl(['', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertIsNone(channel.setExposureTime())

    def testSetExposureTimeMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setExposureTime())

    def testSetEffectiveNAExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setEffectiveNA(), 0.15)

    def testSetEffectiveNAMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setEffectiveNA())

    def testSetImagingDeviceExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setImagingDevice(), 'Axiocam 503')

    def testSetImagingDeviceMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setImagingDevice())

    def testSetImagingDeviceMissingKeys(self):
        tree = ET.parse(self.missingKeysPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setImagingDevice())

    def testSetCameraAdapterExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setCameraAdapter(), '1x Camera Adapter')

    def testSetCameraAdapterMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setCameraAdapter())

    def testSetBinningModeExpectedValue(self):
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, self.meta.root)
        self.assertEqual(channel.setCameraAdapter(), '1x Camera Adapter')

    def testSetBinningModeMissingEntries(self):
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        channel = chnnl(['Channel:0', 'EGFP', 'testCziFile.czi'], self.meta.filters, root)
        self.assertIsNone(channel.setCameraAdapter())


if __name__ == '__main__':
    unittest.main()