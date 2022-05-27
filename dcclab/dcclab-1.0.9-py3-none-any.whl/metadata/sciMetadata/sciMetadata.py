from ..txtMetadata.pdkTXTMetadata import PDKTXTMetadata
import re
import os
import datetime


class sciMetadata:
    def __init__(self, sciPath):
        self.sciPath = sciPath
        self.rawPath, self.iniPath, self.xmlPath = self.confirmFolderHasScientificaFiles()
        self.fileName = self.__fileName()
        self.date = self.__date()

        # Processing .ini file :
        self.iniDict, self.iniKeys = self.extractDataFromIniFile()

        # Processing .xml file :
        #self.xmlPath = self.__xmlPath()
        #self.xmlRoot = self.readXmlFile()

    def confirmFolderHasScientificaFiles(self):
        rawPath, iniPath, xmlPath = None, None, None
        files = os.listdir(self.sciPath)
        for file in files:
            if rawPath is None and re.search('.raw$', file, re.IGNORECASE):
                rawPath = os.path.join(self.sciPath, file)
            elif iniPath is None and re.search('.ini$', file, re.IGNORECASE):
                iniPath = os.path.join(self.sciPath, file)
            elif xmlPath is None and re.search('.xml$', file, re.IGNORECASE):
                xmlPath = os.path.join(self.sciPath, file)

        if rawPath is None or iniPath is None or xmlPath is None:
            raise FileNotFoundError("The Scientifica folder is missing essential file types.")

        return rawPath, iniPath, xmlPath

    def __fileName(self):
        file = os.path.basename(self.sciPath)
        return os.path.splitext(file)[0]

    def __date(self):
        fileName = self.fileName.split('_')[0:4]
        fileName = str.join('_', fileName)
        date = datetime.datetime.strptime(fileName, '%Y%m%d_%H_%M_%S')
        return '{} {}'.format(date.date(), date.time())

    def extractDataFromIniFile(self):
        mtdt = PDKTXTMetadata(self.iniPath)
        return mtdt.asDict, mtdt.keys

    # FixMe Currently, we do not know if .xml files associated with .raw files have any valuable metadata.
    #def __xmlPath(self):
    #    return re.sub('XYT\.lineshifted\.raw|XYT.raw', 'OME.xml', self.rawPath, re.IGNORECASE)

    # FixMe Currently, we do not know if .xml files associated with .raw files have any valuable metadata.
    #def readXmlFile(self):
    #    tree = et.parse(self.xmlPath)
    #    return tree.getroot()

    @property
    def keys(self):
        keys = {'path': 'TEXT PRIMARY KEY', 'raw_path': 'TEXT', 'ini_path': 'TEXT', 'xml_path': 'TEXT', **self.iniKeys}
        return {'ZebraFishRAW': keys}

    @property
    def asDict(self):
        dictio = {'path': self.sciPath, 'raw_path': self.rawPath, 'ini_path': self.iniPath, 'xml_path': self.xmlPath}
        return {**dictio, **self.iniDict}

