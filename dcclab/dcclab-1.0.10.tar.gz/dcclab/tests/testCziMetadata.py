import env
from dcclab import CZIMetadata as mtdt
from dcclab import readCziImage
import xml.etree.ElementTree as ET
import unittest
import os


class TestCziMetadata(env.DCCLabTestCase):
    def setUp(self):
        self.directory = str(self.dataDir)
        self.testPath = os.path.join(self.directory, 'testCziFile.czi')
        self.wrongFilePath = os.path.join(self.directory, 'wrongfilename.czi')
        self.wrongFileType = os.path.join(self.directory, 'wrongFile.txt')
        self.missingEntriesPath = os.path.join(self.directory, 'MissingEntries.xml')
        self.missingKeysPath = os.path.join(self.directory, 'MissingKeys.xml')

    def testCziImageObjectFromPathIsCziImageObject(self):
        mdata = mtdt(self.testPath)
        file1 = mdata.cziImageObjectFromPath()
        file2 = readCziImage(self.testPath)
        self.assertIs(type(file1), type(file2))
        file1.close()
        file2.close()

    def testCziImageObjectFromPathFileNotFound(self):
        mdata = mtdt(self.testPath)
        mdata.filePath = self.wrongFilePath
        with self.assertRaises(FileNotFoundError): mdata.cziImageObjectFromPath()

    def testCziFileToCziImageObjectWrongFileType(self):
        mdata = mtdt(self.testPath)
        mdata.filePath = self.wrongFileType
        with self.assertRaises(ValueError): mdata.cziImageObjectFromPath()

    def testXmlFromCziImageObjectReturnsString(self):
        mdata = mtdt(self.testPath)
        cziImageObject = mdata.cziImageObjectFromPath()
        self.assertIs(type(mdata.xmlFromCziImageObject(cziImageObject)), str)
        cziImageObject.close()

    def testXmlFromCziImageObjectWrongTypeOfObject(self):
        mdata = mtdt(self.testPath)
        cziImageObject = 'WrongTypeOfObject'
        with self.assertRaises(AttributeError): mdata.xmlFromCziImageObject(cziImageObject)

    def testCreateElementTreeRootReturnsElement(self):
        mdata = mtdt(self.testPath)
        self.assertIs(type(mdata.createElementTreeRoot()), ET.Element)

    def testSetMicroscopeExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertEqual(mdata.setMicroscope(), 'Axio Observer.Z1 / 7')

    def testSetMicroscopeMissingKey(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingKeysPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setMicroscope())

    def testSetMicroscopeMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setMicroscope())

    def testSetObjectiveExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertEqual(mdata.setObjective(), 'LD A-Plan 5x/0.15 Ph1')

    def testSetObjectiveMissingKey(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingKeysPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setObjective())

    def testSetObjectiveMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setObjective())

    def testSetXScaleExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertEqual(mdata.setXScale(), 9.08E-07)

    def testSetXScaleMissingKey(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingKeysPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setXScale())

    def testSetXScaleMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setXScale())

    def testSetYScaleExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertEqual(mdata.setYScale(), 9.08E-07)

    def testSetYScaleMissingKey(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingKeysPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setYScale())

    def testSetYScaleMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setYScale())

    def testSetXSizeExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertEqual(mdata.setXSize(), 1936)

    def testSetXSizeMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setXSize())

    def testSetYSizeExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertEqual(mdata.setYSize(), 1460)

    def testSetYSizeMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        self.assertIsNone(mdata.setYSize())

    def testXScaledExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertAlmostEqual(mdata.xScaled, 1.757888)

    def testXScaledWrongValue(self):
        mdata = mtdt(self.testPath)
        mdata.xScale = 'abcd'
        self.assertIsNone(mdata.xScaled)

    def testYScaledExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertAlmostEqual(mdata.yScaled, 1.325680)

    def testYScaledWrongValue(self):
        mdata = mtdt(self.testPath)
        mdata.yScale = 'abcd'
        self.assertIsNone(mdata.yScaled)

    def testFindFiltersInRootReturnsListOfFilters(self):
        mdata = mtdt(self.testPath)
        testFilters = ['Filter:1', 'Filter:2', 'Filter:3', 'Filter:4']
        for filter, testFilter in zip(mdata.findFiltersInRoot(), testFilters):
            self.assertEqual(filter.filterId, testFilter)

    def testFindFiltersInRootMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        for filter in mdata.findFiltersInRoot():
            self.assertIsNone(filter.filterType)

    def testFindFiltersInRootMissingKey(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingKeysPath)
        mdata.root = tree.getroot()
        for filter in mdata.findFiltersInRoot():
            self.assertIsNone(filter.channelId)

    def testFindChannelsInRootReturnsListOfChannels(self):
        mdata = mtdt(self.testPath)
        testChannels = [self.testPath + ';Channel:0', self.testPath + ';Channel:1']
        for channel, testChannel in zip(mdata.findChannelsInRoot(), testChannels):
            self.assertEqual(channel.channelId, testChannel)

    def testFindChannelsInRootMissingEntries(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        mdata.root = tree.getroot()
        for channel in mdata.findChannelsInRoot():
            self.assertIsNone(channel)

    def testCheckIfElementHasChildrenHasChildren(self):
        mdata = mtdt(self.testPath)
        root = mdata.root.find('./Metadata/Information/Image/Dimensions/Channels')
        self.assertTrue(mdata.checkIfElementHasChildren(root))

    def testCheckIfElementHasChildrenHasNoChildren(self):
        mdata = mtdt(self.testPath)
        tree = ET.parse(self.missingEntriesPath)
        root = tree.getroot()
        newRoot = root.find('./Metadata/Information/Image/Dimensions/Channels')
        self.assertFalse(mdata.checkIfElementHasChildren(newRoot))

    def testCheckIfElementHasChildrenElementIsNone(self):
        mdata = mtdt(self.testPath)
        self.assertFalse(mdata.checkIfElementHasChildren(None))

    def testAsDictExpectedValue(self):
        mdata = mtdt(self.testPath)
        expectedValue = {'channels': 2, 'file_path': self.testPath,
                         'injection_site': None, 'microscope': 'Axio Observer.Z1 / 7', 'mouse_id': None,
                         'name': 'testCziFile.czi', 'objective': 'LD A-Plan 5x/0.15 Ph1', 'tags': '',
                         'viral_vectors': '', 'x_scale': 9.08e-07, 'x_scaled': 1.757888, 'x_size': 1936,
                         'y_scale': 9.08e-07, 'y_scaled': 1.3256800000000002, 'y_size': 1460}
        self.assertEqual(mdata.asDict()['metadata'], expectedValue)

    def testSetMouseIdUpperCase(self):
        mdata = mtdt(self.testPath, 'S123_test_czi')
        self.assertEqual(mdata.setMouseId(), '123')

    def testSetMouseIdLowerCase(self):
        mdata = mtdt(self.testPath, 's123_test_czi')
        self.assertEqual(mdata.setMouseId(), '123')

    def testSetMouseIdLessDigits(self):
        mdata = mtdt(self.testPath, 's1_test_czi')
        self.assertEqual(mdata.setMouseId(), '1')

    def testSetMouseIdMoreDigits(self):
        mdata = mtdt(self.testPath, 's1234_test_czi')
        self.assertEqual(mdata.setMouseId(), '1234')

    def testSetMouseIdNoIdFound(self):
        mdata = mtdt(self.testPath, 'test_czi')
        self.assertIsNone(mdata.setMouseId())

    def testFindRabVectorsUpperCase(self):
        mdata = mtdt(self.testPath, 'RAB1.2_RABV3.2_czi')
        self.assertEqual(mdata.findRabVectors(), 'RAB1.2;RABV3.2')

    def testFindRabVectorsLowerCase(self):
        mdata = mtdt(self.testPath, 'rab1.2_rabv3.2_czi')
        self.assertEqual(mdata.findRabVectors(), 'rab1.2;rabv3.2')

    def testFindRabVectorsExpectedValues(self):
        mdata = mtdt(self.testPath, 'rab1_rabv1_RAB1.1_rabv1.1_czi')
        self.assertEqual(mdata.findRabVectors(), 'rab1;rabv1;RAB1.1;rabv1.1')

    def testFindRabVectorsNoVectorsFound(self):
        mdata = mtdt(self.testPath, 'test_czi')
        self.assertFalse(mdata.findRabVectors())

    def testFindRabVectorsWrongValue(self):
        mdata = mtdt(self.testPath, 'test_czi')
        mdata.name = 0
        self.assertIsNone(mdata.findRabVectors())

    def testFindAAVVectorsUpperCase(self):
        mdata = mtdt(self.testPath, 'AAV123_czi')
        self.assertEqual(mdata.findAAVVectors(), 'AAV123')

    def testFindAAVVectorsLowerCase(self):
        mdata = mtdt(self.testPath, 'aav112_czi')
        self.assertEqual(mdata.findAAVVectors(), 'aav112')

    def testFindAAVVectorsPlusSeparator(self):
        mdata = mtdt(self.testPath, 'AAV123+456_czi')
        self.assertEqual(mdata.findAAVVectors(), 'AAV123;AAV456')

    def testFindAAVVectorsMinusSeparator(self):
        mdata = mtdt(self.testPath, 'AAV789-101_czi')
        self.assertEqual(mdata.findAAVVectors(), 'AAV789;AAV101')

    def testFindAAVVectorsExpectedValues(self):
        mdata = mtdt(self.testPath, 'AAV123+456_AAV789-101_aav112_czi')
        self.assertEqual(mdata.findAAVVectors(), 'AAV123;AAV456;AAV789;AAV101;aav112')

    def testFindAAVVectorsNoVectorsFound(self):
        mdata = mtdt(self.testPath, 'test_czi')
        self.assertFalse(mdata.findAAVVectors())

    def testFindAAVVectorsWrongValue(self):
        mdata = mtdt(self.testPath, 'test_czi')
        mdata.name = 0
        self.assertIsNone(mdata.findAAVVectors())

    def testSetViralVectorsExpectedValue(self):
        mdata = mtdt(self.testPath, 'AAV123_rab2_test_czi')
        self.assertEqual(mdata.setViralVectors(), 'AAV123;rab2')

    def testSetViralVectorsNoVectorsFound(self):
        mdata = mtdt(self.testPath, 'test_czi')
        self.assertFalse(mdata.setViralVectors())

    def testSetViralVectorsWrongValue(self):
        mdata = mtdt(self.testPath, 'test_czi')
        mdata.name = 0
        self.assertIsNone(mdata.setViralVectors())

    def testSetInjectionSiteUpperCase(self):
        mdata = mtdt(self.testPath, 'AAV425_PATTE_DRG-02.czi')
        self.assertEqual(mdata.setInjectionSite(), 'PATTE')

    def testSetInjectionSiteLowerCase(self):
        mdata = mtdt(self.testPath, 'AAV425_iv_DRG-02.czi')
        self.assertEqual(mdata.setInjectionSite(), 'iv')

    def testSetInjectionSiteNoInjectionSiteFound(self):
        mdata = mtdt(self.testPath, 'AAV425_DRG-02.czi')
        self.assertFalse(mdata.setInjectionSite())

    def testSetInjectionSiteWrongValue(self):
        mdata = mtdt(self.testPath, 'AAV425_DRG-02.czi')
        mdata.name = 0
        self.assertIsNone(mdata.setInjectionSite())

    def testSetTagsUpperCase(self):
        mdata = mtdt(self.testPath, 'AAV425_patte_NEURONES_czi')
        self.assertEqual(mdata.setTags(), 'NEURONES')

    def testSetTagsLowerCase(self):
        mdata = mtdt(self.testPath, 'AAV425_patte_moelle_czi')
        self.assertEqual(mdata.setTags(), 'moelle')

    def testSetTagsWithSpace(self):
        mdata = mtdt(self.testPath, 'AAV400_anti rabbit-03.czi')
        self.assertEqual(mdata.setTags(), 'antirabbit')

    def testSetTagsDuplicates(self):
        mdata = mtdt(self.testPath, 'AAV400_moelle_moelle-03.czi')
        self.assertEqual(mdata.setTags(), 'moelle')

    def testSetTagsExpectedValues(self):
        mdata = mtdt(self.testPath, 'AAV400_cerveau_moelle_neurones_BB-03.czi')
        self.assertEqual(mdata.setTags(), 'moelle;neurones;BB')

    def testSetTagsNoTagsFound(self):
        mdata = mtdt(self.testPath, 'AAV400_cerveau-03.czi')
        self.assertFalse(mdata.setTags())

    def testSetTagsWrongValue(self):
        mdata = mtdt(self.testPath, 'AAV400_cerveau-03.czi')
        mdata.name = 0
        self.assertFalse(mdata.setTags())

    def testNameFromPathExpectedValue(self):
        mdata = mtdt(self.testPath)
        self.assertEqual(mdata.nameFromPath(), 'testCziFile.czi')

    def testNameFromPathNoPath(self):
        mdata = mtdt(self.testPath)
        mdata.filePath = ''
        self.assertEqual(mdata.nameFromPath(), '')

    def testNameFromPathWrongType(self):
        mdata = mtdt(self.testPath)
        mdata.filePath = 0
        self.assertIsNone(mdata.nameFromPath())


if __name__ == '__main__':
    unittest.main()
